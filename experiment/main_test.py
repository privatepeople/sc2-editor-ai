# Python Standard Library imports
import asyncio
import json
import logging
import os
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator, Literal, Optional

# Third-party Library imports
# Password hashing and JWT imports
import bcrypt
import jwt
from jwt import PyJWTError
# FastAPI imports
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# SlowApi imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
# LangChain imports
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

# Custom Library imports
from config import get_settings
from sc2editor.llm import SC2EditorLLM


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
conversations = defaultdict(list)
llm = None
cleanup_task = None
fastapi_settings = get_settings().fastapi

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = fastapi_settings.access_token_expire

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int = Field(description="Time left until JWT token expiration.")


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: bytes


class Message(BaseModel):
    role: Literal['user', 'assistant'] = Field(description="message author.")
    content: str = Field(description="message content.")


class ChatRequest(BaseModel):
    message: str = Field(description="Current prompt.")
    conversation_id: Optional[str] = Field(default=None, description="Identifier of conversation history.")
    history: Optional[list[Message]] = Field(default_factory=list, description="The conversation history up to this point, including the current prompt.")


def get_password_hash(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to be hashed
    
    Returns:
        Bcrypt hashed password
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Verify a plain password against its bcrypt hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against
    
    Returns:
        True if password matches hash, False otherwise
    """
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc , hashed_password=hashed_password)


def get_user(username: str) -> UserInDB | None:
    """
    Retrieve user information from environment variables.
    
    Args:
        username: Username to look up
    
    Returns:
        UserInDB object containing admin account information if username matches, None if user not found
    """
    if username == ADMIN_USERNAME:
        return UserInDB(
            username=ADMIN_USERNAME,
            hashed_password=get_password_hash(ADMIN_PASSWORD)
        )
    return None


def authenticate_user(username: str, password: str) -> bool | UserInDB:
    """
    Authenticate user credentials against stored user data.
    
    Args:
        username: Username to authenticate
        password: Plain text password to verify
    
    Returns:
        UserInDB object if authentication successful, False if authentication fails
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with expiration.
    
    Args:
        data: Data to encode in the JWT payload
        expires_delta: Custom expiration time delta. Defaults to 15 minutes if None
    
    Returns:
        Encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData | None:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
    
    Returns:
        TokenData if token is valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except PyJWTError:
        return None


async def get_current_user_from_token(token: str) -> UserInDB | None:
    """
    Extract and validate current user from JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        Authenticated UserInDB object or None if invalid
    """
    token_data = verify_token(token)
    if not token_data:
        return None
    
    user = get_user(username=token_data.username)
    if user is None:
        return None
    return user


async def get_current_user(
    authorization: Annotated[str, Depends(oauth2_scheme)] = None,
    session_token: Annotated[str, Cookie(alias="session_token")] = None
) -> UserInDB:
    """
    Extract and validate current user from JWT token (either from Authorization header or session cookie).
    
    Args:
        authorization: JWT token from OAuth2 bearer scheme (Authorization header)
        session_token: JWT token from session cookie
    
    Returns:
        Authenticated UserInDB object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try session cookie first, then authorization header
    token = session_token or authorization
    
    if not token:
        raise credentials_exception
    
    user = await get_current_user_from_token(token)
    if not user:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Get current active user (wrapper function for potential future user status checks).
    
    Args:
        current_user: Current authenticated user from get_current_user dependency
    
    Returns:
        Current active User object
    """
    return current_user


async def cleanup_old_conversations(
                                    period: int,
                                    conversation_timeout: int
                                    ):
    """
    Background task to clean up old conversations
    
    Args:
        period: Period to check conversation timeout(seconds)
        conversation_timeout: Grace period from last conversation to deletion(minutes)
    """
    while True:
        try:
            current_time = datetime.now()
            conversations_to_delete = list()
            
            for conversation_id, messages in conversations.items():
                if messages:  # Check if conversation has messages
                    # Get the timestamp of the last message
                    last_message = messages[-1]
                    if 'timestamp' in last_message:
                        last_timestamp = datetime.fromisoformat(last_message['timestamp'])
                        time_diff = current_time - last_timestamp
                        
                        # If more than conversation timeout have passed, mark for deletion
                        if time_diff > timedelta(minutes=conversation_timeout):
                            conversations_to_delete.append(conversation_id)
                            logger.info(f"Marking conversation {conversation_id} for cleanup (last activity: {time_diff} ago)")
                    else:
                        # If no timestamp, consider it old and mark for deletion
                        conversations_to_delete.append(conversation_id)
                        logger.info(f"Marking conversation {conversation_id} for cleanup (no timestamp)")
                else:
                    # Empty conversation, mark for deletion
                    conversations_to_delete.append(conversation_id)
                    logger.info(f"Marking empty conversation {conversation_id} for cleanup")
            
            # Delete marked conversations
            for conversation_id in conversations_to_delete:
                del conversations[conversation_id]
                logger.info(f"Deleted old conversation: {conversation_id}")
            
            if conversations_to_delete:
                logger.info(f"Cleanup completed: {len(conversations_to_delete)} conversations deleted, {len(conversations)} remaining")
            
        except Exception as e:
            logger.error(f"Error during conversation cleanup: {e}")
        
        # Wait for period seconds before next cleanup
        await asyncio.sleep(period)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global llm, cleanup_task

    # Startup
    logger.info("Starting StarCraft 2 Editor AI Backend...")
    
    try:
        llm = SC2EditorLLM()
        logger.info("Gemini LLM initialized successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize Gemini LLM: {e}")
        raise
    
    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_conversations(period=fastapi_settings.conversation_timeout_period, conversation_timeout=fastapi_settings.conversation_timeout))
    logger.info("Background cleanup task started")
    
    yield
    
    # Shutdown
    if llm:
        llm.close()
    logger.info("Shutting down StarCraft 2 Editor AI Backend...")
    
    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            logger.info("Background cleanup task cancelled")


def create_langchain_messages(
                                history: list[Message],
                                current_message: str
                            ) -> list[HumanMessage | AIMessage]:
    """Convert message history to LangChain format
    
    Args:
        history: Conversation history sent by client
        current_message: message entered by client
        
    Returns:
        A list consisting of HumanMessage, AIMessage
    """

    messages = list()
    
    # Add conversation history
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    # Add current message
    messages.append(HumanMessage(content=current_message))

    return messages


async def generate_streaming_response(request: Request, messages: list[HumanMessage | AIMessage], conversation_id: str) -> AsyncGenerator[str, None]:
    """Generate streaming response from Gemini with proper SSE format
    
    Args:
        request: Request object
        messages: A list consisting of HumanMessage, AIMessage
        conversation_id: Conversation history identifier id
        
    Returns:
        AsyncGenerator whose return value is a string
    """
    global llm
    
    try:
        accumulated_response_list = list()
        connection_flags = True
        
        # Send initial connection confirmation
        if await request.is_disconnected():
            raise ConnectionResetError()
        yield f"data: {json.dumps({'conversation_id': conversation_id, 'status': 'connected'}, ensure_ascii=False)}\n\n"
        
        # Add a small delay to ensure connection is established
        await asyncio.sleep(0.1)
        
        # Stream the response
        chunk_count = 0
        async for msg, metadata in llm.astream({'messages': messages}, thread_id=conversation_id):
            if await request.is_disconnected():
                connection_flags = False
                break

            try:
                if metadata['langgraph_node'] in ('answer_node', 'disallow_node'):
                    content = msg.content
                    accumulated_response_list.append(content)
                    chunk_count += 1
                    
                    # Send each chunk as SSE with error handling
                    data = {
                                'content': content,
                                'conversation_id': conversation_id,
                                'chunk_id': chunk_count
                            }
                    
                    # Ensure proper JSON encoding
                    if await request.is_disconnected():
                        connection_flags = False
                        break
                    json_data = json.dumps(data, ensure_ascii=False)
                    yield f"data: {json_data}\n\n"
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.02)
                    
            except Exception as chunk_error:
                logger.error(f"Error processing chunk {chunk_count}: {chunk_error}")
                continue
        
        if not connection_flags:
            raise ConnectionResetError()
        
        accumulated_response = ''.join(accumulated_response_list)

        # Check that the lengths of the request and the conversation history stored in memory are the same
        # This is because the conversation history in memory may have disappeared due to session expiration or other reasons
        if len(messages) != len(conversations[conversation_id]):
            # Initialize the corresponding conversation_id
            if conversation_id in conversations:
                del conversations[conversation_id]
            # Restore past conversation history
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role = "user"
                elif isinstance(msg, AIMessage):
                    role = "assistant"
                else:
                    continue
                
                content = msg.content

                conversations[conversation_id].append(
                                                        {
                                                            "role": role,
                                                            "content": content,
                                                            "timestamp": datetime.now().isoformat()
                                                        }
                                                    )

        # Store the complete conversation
        conversations[conversation_id].append(
                                                {   
                                                    "role": "assistant",
                                                    "content": accumulated_response,
                                                    "timestamp": datetime.now().isoformat()
                                                }
                                            )
        
        logger.info(f"Streaming completed for conversation {conversation_id}, total chunks: {chunk_count}")
        
    except Exception as e:
        # Improved error handling with proper exception type checking
        error_type = type(e).__name__
        error_message = str(e)
        
        # Map common Google API errors to appropriate HTTP codes and messages
        error_mappings = {
                        'InvalidArgument': {
                            'http_code': 400,
                            'message': "The request body is malformed."
                        },
                        'PreconditionFailed': {
                            'http_code': 400,
                            'message': "Gemini API free tier is not available in server country. Please enable billing on your project in Google AI Studio."
                        },
                        'PermissionDenied': {
                            'http_code': 403,
                            'message': "API key doesn't have the required permissions."
                        },
                        'NotFound': {
                            'http_code': 404,
                            'message': "The requested resource wasn't found."
                        },
                        'ResourceExhausted': {
                            'http_code': 429,
                            'message': "The rate limit for the Gemini API free tier has been exceeded. The API is no longer available today. Please try again tomorrow."
                        },
                        'InternalServerError': {
                            'http_code': 500,
                            'message': "An unexpected error occurred on Google's side."
                        },
                        'ServiceUnavailable': {
                            'http_code': 503,
                            'message': "The Gemini API service may be temporarily overloaded or down. Please try again later."
                        },
                        'DeadlineExceeded': {
                            'http_code': 504,
                            'message': "The Gemini API service could not be processed within the deadline."
                        }
                    }
        
        error_info = error_mappings.get(error_type, {
                                                        'http_code': 500,
                                                        'message': "I apologize, but I encountered an error while processing your request. Please try again."
                                                    })
        
        logger.error(f"Error generating streaming response ({error_type}): {error_message}")
        
        content = f"Sorry, an error occurred while processing your request.\n\nHTTP Code {error_info['http_code']}: {error_info['message']}"

        # Send error message
        error_data = {
                        'content': content,
                        'conversation_id': conversation_id,
                        'error': True,
                        'error_message': error_message,
                        'HTTP_CODE': error_info['http_code']
                    }
        
        if not (await request.is_disconnected()):
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    finally:
        # Graph State initialization
        if llm.checkpointer.get({'configurable': {'thread_id': conversation_id}}):
            llm.delete_thread_id(conversation_id)
            logger.info(f"LangGraph State of Conversation ID {conversation_id} has been initialized.")

        # Send completion signal
        if not (await request.is_disconnected()):
            yield "data: [DONE]\n\n"
            logger.info(f"End stream for conversation {conversation_id}")
        else:
            logger.error(f"Connection was closed before sending completion signal for conversation id {conversation_id}.")


# Create FastAPI app
app = FastAPI(
                title="StarCraft 2 Editor AI Backend",
                description="Backend API for StarCraft 2 Editor AI with Gemini integration",
                version="1.0.0",
                lifespan=lifespan
            )

# Configure CORS
app.add_middleware(
                        CORSMiddleware,
                        allow_origins=["*"],  # In production, specify your frontend domain
                        allow_credentials=True,
                        allow_methods=["*"],
                        allow_headers=["*"],
                    )

# Always return same key to share the limit across all clients
global_limiter = Limiter(key_func=lambda request: "global")

app.state.limiter = global_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
                                    response: Response,
                                    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
                                ):
    """Login endpoint to get JWT access token and set session cookie"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    # Set session cookie (httpOnly, secure, sameSite)
    # Session cookie - no max_age means it expires when browser closes
    response.set_cookie(
                        key="session_token",
                        value=access_token,
                        httponly=True,  # Prevent JavaScript access
                        secure=False,   # Set to True in production with HTTPS
                        samesite="lax", # CSRF protection
                    )
    
    logger.info(f"User {user.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer", "expires_in": int(access_token_expires.total_seconds())}


@app.post("/logout")
async def logout(response: Response):
    """Logout endpoint to clear session cookie"""
    response.delete_cookie(key="session_token")
    return {"message": "Successfully logged out"}


# Public endpoints (no authentication required)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.post("/chat/stream")
@global_limiter.limit(f"{fastapi_settings.api_limit}/minute")
async def stream_chat(request: Request, body: ChatRequest):
    """Stream chat response using Gemini"""
    # Generate conversation ID if not provided
    conversation_id = body.conversation_id or str(uuid.uuid4())
    
    try:
        # Store user message
        # Check that the lengths of the body and the conversation history stored in memory are the same
        # This is because the conversation history in memory may have disappeared due to session expiration or other reasons
        
        # Create a copy of history to avoid modifying the original
        history_copy = body.history.copy() if body.history else list()
        
        # Remove the last item if it exists and matches the current message
        if history_copy and history_copy[-1].content == body.message:
            del history_copy[-1]
        
        if len(history_copy) != len(conversations[conversation_id]):
            # Initialize the corresponding conversation_id
            if conversation_id in conversations:
                del conversations[conversation_id]
            # Restore past conversation history
            for msg in history_copy:
                conversations[conversation_id].append(
                                                        {
                                                            "role": msg.role,
                                                            "content": msg.content,
                                                            "timestamp": datetime.now().isoformat()
                                                        }
                                                    )
                
        conversations[conversation_id].append(
                                                {
                                                    "role": "user",
                                                    "content": body.message,
                                                    "timestamp": datetime.now().isoformat()
                                                }
                                            )
        
        messages = create_langchain_messages(history_copy, body.message)
        
        logger.info(f"Start stream for conversation {conversation_id}")
        
        # Return streaming response with proper SSE headers
        return StreamingResponse(
                                    generate_streaming_response(request, messages, conversation_id),
                                    media_type="text/event-stream",
                                    headers={
                                                "Cache-Control": "no-cache",
                                                "Connection": "keep-alive",
                                                "Access-Control-Allow-Origin": "*",
                                                "Access-Control-Allow-Headers": "*", 
                                                "Access-Control-Allow-Methods": "*",
                                                "X-Accel-Buffering": "no",  # Disable nginx buffering
                                                "Transfer-Encoding": "chunked",  # Explicitly set chunked encoding
                                            }
                                )
        
    except Exception as e:
        logger.error(f"Error in stream_chat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Since blocking the delete API with authentication/authorization prevents it from being deleted from memory in a timely manner,
# causing a memory leak, it was changed to public.
@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


# Use events such as refresh or page move/close
# Function to forcefully delete conversation history
# Since the request is made using navigator.sendBeacon on the front side, only the POST method is possible
@app.post("/conversations/delete/{conversation_id}")
async def clear_conversation_forcing(conversation_id: str):
    """Clear conversation history(for sendBeacon compatibility)"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        logger.info(f"Conversation {conversation_id} deleted")
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        # Don't raise error for cleanup calls
        return {"message": f"Conversation {conversation_id} not found"}


# Protected endpoints (authentication required)
@app.get("/health")
async def health_check(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Detailed health check"""
    global llm
    
    health_status = {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                        "services": {
                                        "fastapi": "running",
                                        "gemini_llm": "connected" if llm else "disconnected",
                                        "cleanup_task": "running" if cleanup_task and not cleanup_task.done() else "stopped"
                                    },
                        "active_conversations": len(conversations),
                    }
    
    return health_status


@app.get("/conversations")
async def list_conversations(current_user: Annotated[User, Depends(get_current_active_user)]):
    """List all conversation IDs"""
    return {
                "conversations": list(conversations.keys()),
                "total": len(conversations)
            }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    return {
                "conversation_id": conversation_id,
                "messages": conversations[conversation_id]
            }


if __name__ == "__main__":
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
                    app,
                    host="127.0.0.1",
                    port=8080,
                    reload=False,
                    log_level="info"
                )
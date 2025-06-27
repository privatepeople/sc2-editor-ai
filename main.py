# Python Standard Library imports
import asyncio
import json
import uuid
import logging
from typing import Literal
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

# FastAPI imports
import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

# LangChain imports
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

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
api_limit_state = False  # True when API is limited, False when available
fastapi_settings = get_settings().fastapi


# Pydantic models
class Message(BaseModel):
    role: Literal['user', 'assistant'] = Field(description="message author.")
    content: str = Field(description="message content.")


class ChatRequest(BaseModel):
    message: str = Field(description="message content.")
    conversation_id: Optional[str] = Field(default=None, description="Identifier of conversation history.")
    history: Optional[list[Message]] = Field(default_factory=list, description="The conversation history up to this point, including the current prompt.")


async def cleanup_old_conversations(
                                    period: int,
                                    session_timeout: int
                                    ):
    """
    Background task to clean up old conversations
    
    Args:
        period: Period for checking session_timeout(seconds)
        session_timeout: Grace period from last conversation to deletion(minutes)
    """
    while True:
        try:
            current_time = datetime.now()
            conversations_to_delete = []
            
            for conversation_id, messages in conversations.items():
                if messages:  # Check if conversation has messages
                    # Get the timestamp of the last message
                    last_message = messages[-1]
                    if 'timestamp' in last_message:
                        last_timestamp = datetime.fromisoformat(last_message['timestamp'])
                        time_diff = current_time - last_timestamp
                        
                        # If more than session_timeout have passed, mark for deletion
                        if time_diff > timedelta(minutes=session_timeout):
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


async def api_limit_state_cooldown():
    """API limit cooldown"""
    global api_limit_state, fastapi_settings

    additional_delay_time = 3
    delay = fastapi_settings.api_limit_cooldown + additional_delay_time

    logger.info("API limit cooldown start!")

    await asyncio.sleep(delay)

    api_limit_state = False
    logger.info("API limit reset!")


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
    cleanup_task = asyncio.create_task(cleanup_old_conversations(period=fastapi_settings.session_timeout_check_period, session_timeout=fastapi_settings.session_timeout))
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
                            ) -> list[BaseMessage]:
    """Convert message history to LangChain format
    
    Args:
        history: Conversation history sent by client
        current_message: message entered by client
        
    Returns:
        A list consisting of HumanMessage, AIMessage
    """

    messages = []
    
    # Add conversation history
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    
    # Add current message
    messages.append(HumanMessage(content=current_message))

    return messages


async def generate_streaming_response(messages: list[BaseMessage], conversation_id: str, background_tasks: BackgroundTasks) -> AsyncGenerator[str, None]:
    """Generate streaming response from Gemini with proper SSE format
    
    Args:
        messages: A list consisting of HumanMessage, AIMessage
        conversation_id: Conversation history identifier id
        background_tasks: Tasks to run in the background after response
        
    Returns:
        AsyncGenerator whose return value is a string
    """
    global llm
    
    try:
        accumulated_response_list = []
        
        # Send initial connection confirmation
        yield f"data: {json.dumps({'conversation_id': conversation_id, 'status': 'connected'}, ensure_ascii=False)}\n\n"
        
        # Add a small delay to ensure connection is established
        await asyncio.sleep(0.1)
        
        # Stream the response
        chunk_count = 0
        async for msg, metadata in llm.astream({'messages': messages}, thread_id=conversation_id):
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
                    json_data = json.dumps(data, ensure_ascii=False)
                    yield f"data: {json_data}\n\n"
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.02)
                    
            except Exception as chunk_error:
                logger.error(f"Error processing chunk {chunk_count}: {chunk_error}")
                continue
        
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
        
        # Graph State initialization
        llm.delete_thread_id(conversation_id)
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
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    finally:
        # Start API limit cooldown
        background_tasks.add_task(api_limit_state_cooldown)

        # Send completion signal
        yield "data: [DONE]\n\n"


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

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
                "message": "StarCraft 2 Editor AI Backend is running",
                "status": "healthy",
                "version": "1.0.0"
            }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/health")
async def health_check():
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
                        "active_conversations": len(conversations)
                    }
    
    return health_status


@app.get("/conversations")
async def list_conversations():
    """List all conversation IDs"""
    return {
                "conversations": list(conversations.keys()),
                "total": len(conversations)
            }


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
                "conversation_id": conversation_id,
                "messages": conversations[conversation_id]
            }


@app.post("/chat/stream")
async def stream_chat(request: Request, body: ChatRequest, background_tasks: BackgroundTasks):
    """Stream chat response using Gemini"""
    global llm, api_limit_state, fastapi_settings
    
    if not llm:
        raise HTTPException(
                                status_code=503, 
                                detail="Gemini LLM not initialized. Please check your API key."
                            )
    
    # Check API limit state first
    if api_limit_state:
        logger.warning(f"API usage restrictions")
        raise HTTPException(
                                status_code=429, 
                                detail=f"This API can only be requested {fastapi_settings.api_limit} times per minutes."
                            )
    
    # Set API limit state
    api_limit_state = True
    logger.info(f"API limit activated")
    
    # Generate conversation ID if not provided
    conversation_id = body.conversation_id or str(uuid.uuid4())
    
    try:
        # Store user message
        # Check that the lengths of the body and the conversation history stored in memory are the same
        # This is because the conversation history in memory may have disappeared due to session expiration or other reasons
        
        # Create a copy of history to avoid modifying the original
        history_copy = body.history.copy() if body.history else []
        
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
        
        # Create LangChain messages using the copied history
        messages = create_langchain_messages(history_copy, body.message)
        
        logger.info(f"Starting stream for conversation {conversation_id}")
        
        # Return streaming response with proper SSE headers
        return StreamingResponse(
                                    generate_streaming_response(messages, conversation_id, background_tasks),
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
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


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


if __name__ == "__main__":
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
                    "main:app",
                    host="127.0.0.1",
                    port=8080,
                    reload=False,
                    log_level="info"
                )
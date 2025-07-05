# Python Standard Library imports
import uuid
from datetime import datetime
from typing import Annotated, Any

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject
# FastAPI imports
from fastapi import Depends, APIRouter, Request, Response, HTTPException, status
from fastapi.responses import StreamingResponse

# Custom Library imports
from config import get_settings
from app.logging import ApplicationLogging
from app.containers import Container
from app.models.chat import ChatRequest
from app.services.chat_service import create_langchain_messages, generate_streaming_response
from app.middleware import global_limiter


api_limit = get_settings().fastapi.api_limit

chat_router = APIRouter(prefix="/chat", tags=["Chat"])

@chat_router.post("/stream")
@global_limiter.limit(f"{api_limit}/minute")
@inject
async def stream_chat(
                        request: Request, body: ChatRequest, response: Response,
                        app_logging: Annotated[ApplicationLogging, Depends(Provide[Container.app_logging])],
                        conversations: Annotated[dict[str, list[Any]], Depends(Provide[Container.conversations])],
                        ):
    """
    Stream chat response using Gemini
    
    Args:
        request: FastAPI Request object for accessing request data
        body: ChatRequest containing conversation_id, message, and conversation history
        response: FastAPI Response object to set headers and manage streaming
        app_logging: Application logging instance
        conversations: Dictionary of all conversations from all clients
    """
    logger = app_logging.logger

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
                                    generate_streaming_response(request=request, messages=messages, conversation_id=conversation_id),
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
        logger.critical(f"Error in stream_chat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
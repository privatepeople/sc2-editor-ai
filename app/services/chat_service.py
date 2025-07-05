# Python Standard Library imports
import asyncio
import json
from typing import AsyncGenerator, Any
from datetime import datetime

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject
# LangChain imports
from langchain_core.messages import AIMessage, HumanMessage
# FastAPI imports
from fastapi import Request

# Custom Library imports
from app.models.chat import Message
from app.logging import ApplicationLogging
from app.containers import Container
# StarCraft 2 Editor AI imports
from sc2editor.llm import SC2EditorLLM


def create_langchain_messages(
                                history: list[Message],
                                current_message: str
                            ) -> list[AIMessage | HumanMessage]:
    """Convert message history to LangChain format
    
    Args:
        history: Conversation history sent by client
        current_message: message entered by client
        
    Returns:
        A list consisting of AIMessage, HumanMessage
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


@inject
async def generate_streaming_response(
                                        request: Request,
                                        messages: list[AIMessage | HumanMessage],
                                        conversation_id: str,
                                        app_logging: ApplicationLogging = Provide[Container.app_logging],
                                        llm: SC2EditorLLM = Provide[Container.llm],
                                        conversations: dict[str, list[Any]] = Provide[Container.conversations]
                                        ) -> AsyncGenerator[str, None]:
    """Generate streaming response from Gemini with proper SSE format
    
    Args:
        request: Request object
        messages: A list consisting of AIMessage, HumanMessage
        conversation_id: Conversation history identifier id
        app_logging: Application logging instance
        llm: SC2EditorLLM instance for handling LLM operations
        conversations: Dictionary of all conversations from all clients
        
    Returns:
        AsyncGenerator whose return value is a string
    """
    logger = app_logging.logger
    
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
                logger.critical(f"Critical error processing chunk {chunk_count}: {chunk_error}")
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
        
        logger.critical(f"Error generating streaming response ({error_type}): {error_message}")
        
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
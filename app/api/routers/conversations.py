# Python Standard Library imports
from typing import Annotated, Any

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject

# FastAPI imports
from fastapi import Depends, APIRouter, HTTPException, status

# Custom Library imports
from app.logging import ApplicationLogging
from app.containers import Container
from app.models.user import User
from app.core.auth import get_current_active_user


conversations_router = APIRouter(prefix="/conversations", tags=["Conversations"])


# Since blocking the delete API with authentication/authorization prevents it from being deleted from memory in a timely manner,
# causing a memory leak, it was changed to public.
@conversations_router.delete("/{conversation_id}")
@inject
async def clear_conversation(
    conversation_id: str,
    app_logging: Annotated[ApplicationLogging, Depends(Provide[Container.app_logging])],
    conversations: Annotated[
        dict[str, list[Any]], Depends(Provide[Container.conversations])
    ],
):
    """
    Clear conversation history

    Args:
        conversation_id: ID of the conversation to delete
        app_logging: Application logging instance
        conversations: Dictionary of all conversations from all clients
    """
    logger = app_logging.logger

    if conversation_id in conversations:
        del conversations[conversation_id]
        logger.info(f"Conversation {conversation_id} deleted")
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )


# Use events such as refresh or page move/close
# Function to forcefully delete conversation history
# Since the request is made using navigator.sendBeacon on the front side, only the POST method is possible
@conversations_router.post("/delete/{conversation_id}")
@inject
async def clear_conversation_forcing(
    conversation_id: str,
    app_logging: Annotated[ApplicationLogging, Depends(Provide[Container.app_logging])],
    conversations: Annotated[
        dict[str, list[Any]], Depends(Provide[Container.conversations])
    ],
):
    """
    Clear conversation history(for sendBeacon compatibility)

    Args:
        conversation_id: ID of the conversation to delete
        app_logging: Application logging instance
        conversations: Dictionary of all conversations from all clients
    """
    logger = app_logging.logger

    if conversation_id in conversations:
        del conversations[conversation_id]
        logger.info(f"Conversation {conversation_id} deleted")
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        # Don't raise error for cleanup calls
        return {"message": f"Conversation {conversation_id} not found"}


@conversations_router.get("")
@inject
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    conversations: Annotated[
        dict[str, list[Any]], Depends(Provide[Container.conversations])
    ],
):
    """
    List all conversation IDs

    Args:
        current_user: Current authenticated user
        conversations: Dictionary of all conversations from all clients
    """
    return {"conversations": list(conversations.keys()), "total": len(conversations)}


@conversations_router.get("/{conversation_id}")
@inject
async def get_conversation(
    current_user: Annotated[User, Depends(get_current_active_user)],
    conversation_id: str,
    conversations: Annotated[
        dict[str, list[Any]], Depends(Provide[Container.conversations])
    ],
):
    """
    Get conversation history

    Args:
        current_user: Current authenticated user
        conversation_id: ID of the conversation to retrieve
        conversations: Dictionary of all conversations from all clients
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id],
    }

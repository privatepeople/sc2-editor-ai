# Python Standard Library imports
import asyncio
from datetime import datetime, timedelta
from typing import Any

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject

# Custom Library imports
from app.logging import ApplicationLogging
from app.containers import Container


@inject
async def cleanup_old_conversations(
    app_logging: ApplicationLogging = Provide[Container.app_logging],
    conversations: dict[str, list[Any]] = Provide[Container.conversations],
    period: int = Provide[Container.config.fastapi.conversation_timeout_period],
    conversation_timeout: int = Provide[Container.config.fastapi.conversation_timeout],
):
    """
    Background task to clean up old conversations

    Args:
        app_logging: Application logging instance
        conversations: Dictionary of all conversations from all clients
        period: Period to check conversation timeout(seconds)
        conversation_timeout: Grace period from last conversation to deletion(minutes)
    """
    logger = app_logging.logger

    while True:
        try:
            current_time = datetime.now()
            conversations_to_delete = list()

            for conversation_id, messages in conversations.items():
                if messages:  # Check if conversation has messages
                    # Get the timestamp of the last message
                    last_message = messages[-1]
                    if "timestamp" in last_message:
                        last_timestamp = datetime.fromisoformat(
                            last_message["timestamp"]
                        )
                        time_diff = current_time - last_timestamp

                        # If more than conversation timeout have passed, mark for deletion
                        if time_diff > timedelta(minutes=conversation_timeout):
                            conversations_to_delete.append(conversation_id)
                    else:
                        # If no timestamp, consider it old and mark for deletion
                        conversations_to_delete.append(conversation_id)
                else:
                    # Empty conversation, mark for deletion
                    conversations_to_delete.append(conversation_id)

            # Delete marked conversations
            for conversation_id in conversations_to_delete:
                del conversations[conversation_id]
                logger.info(f"Deleted old conversation: {conversation_id}")

            if conversations_to_delete:
                logger.info(
                    f"Cleanup completed: {len(conversations_to_delete)} conversations deleted, {len(conversations)} remaining"
                )

        except Exception as e:
            logger.critical(f"Error during conversation cleanup: {e}")

        # Wait for period seconds before next cleanup
        await asyncio.sleep(period)

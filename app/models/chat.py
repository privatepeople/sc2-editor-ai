# Python Standard Library imports
from typing import Literal, Optional

# Third-party Library imports
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A model that represents a message in a conversation."""

    role: Literal["user", "assistant"] = Field(description="message author.")
    content: str = Field(description="message content.")


class ChatRequest(BaseModel):
    """A model that represents a chat request."""

    message: str = Field(description="Current prompt.")
    conversation_id: Optional[str] = Field(
        default=None, description="Identifier of conversation history."
    )
    history: Optional[list[Message]] = Field(
        default_factory=list,
        description="The conversation history up to this point, including the current prompt.",
    )

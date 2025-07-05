# Python Standard Library imports
from datetime import datetime
from typing import Annotated, Any

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject
# FastAPI imports
from fastapi import Depends, APIRouter

# Custom Library imports
from app.containers import Container
from app.models.user import User
from app.core.auth import get_current_active_user
# StarCraft 2 Editor AI imports
from sc2editor.llm import SC2EditorLLM


health_router = APIRouter(prefix="/health", tags=["Health"])

@health_router.get("")
@inject
async def health_check(
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        llm: Annotated[SC2EditorLLM, Depends(Provide[Container.llm])],
                        conversations: Annotated[dict[str, list[Any]], Depends(Provide[Container.conversations])]
                        ):
    """
    Detailed health check
    
    Args:
        current_user: Current authenticated user
        llm: SC2EditorLLM instance for handling LLM operations
        conversations: Dictionary of all conversations from all clients
    """
    
    health_status = {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat(),
                        "services": {
                                        "fastapi": "running",
                                        "gemini_llm": "connected" if llm else "disconnected",
                                    },
                        "active_conversations": len(conversations),
                    }
    
    return health_status
# Python Standard Library imports
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

# Third-party Library imports
# Dependency Injection imports
from dependency_injector.wiring import Provide, inject

# FastAPI imports
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# SlowApi imports
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Custom Library imports
from app.logging import ApplicationLogging
from app.containers import Container
from app.utils.conversations import cleanup_old_conversations
from app.api.routers.auth import authentication_router
from app.api.routers.conversations import conversations_router
from app.api.routers.chat import chat_router
from app.api.routers.health import health_router
from app.middleware import SecurityHeadersMiddleware, global_limiter

# StarCraft 2 Editor AI imports
from sc2editor.llm import SC2EditorLLM


@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,
    app_logging: ApplicationLogging = Provide[Container.app_logging],
    llm: SC2EditorLLM = Provide[Container.llm],
):
    """
    Startup and shutdown events

    Args:
        app: FastAPI application instance
        app_logging: Application logging instance
        llm: SC2EditorLLM instance for handling LLM operations
    """

    logger = app_logging.logger
    # Startup
    logger.info("Starting StarCraft 2 Editor AI Backend...")

    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_conversations())
    logger.info("Background cleanup task started")

    yield

    # Shutdown
    llm.close()
    logger.info("Closed SC2EditorLLM resources.")
    logger.info("Shutting down StarCraft 2 Editor AI Backend...")

    # Cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Background cleanup task cancelled")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    container = Container()

    app = FastAPI(
        title="StarCraft 2 Editor AI Backend",
        description="Backend API for StarCraft 2 Editor AI with Gemini integration",
        version="1.0.0",
        lifespan=lifespan,
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )
    app.container = container

    # Configure middleware
    if container.config()["fastapi"]["https_status"]:
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(authentication_router)
    app.include_router(conversations_router)
    app.include_router(chat_router)
    app.include_router(health_router)

    app.state.limiter = global_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Mount static files directory
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    templates_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=templates_dir)

    @app.get("/", response_class=HTMLResponse)
    async def index_page(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/admin", response_class=HTMLResponse)
    async def admin_login_page(request: Request):
        return templates.TemplateResponse("admin_login.html", {"request": request})

    # Public endpoints (no authentication required)
    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return FileResponse(static_dir / "favicon.ico")

    return app

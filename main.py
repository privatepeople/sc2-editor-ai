# Python Standard Library imports
import asyncio

# FastAPI imports
import uvicorn

# Custom Library imports
from config import get_settings
from app.main import create_app


if __name__ == "__main__":
    settings = get_settings()
    host = str(settings.uvicorn_host)
    port = settings.uvicorn_port
    app = create_app()

    import platform

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(app, host=host, port=port, reload=False, log_level="info")

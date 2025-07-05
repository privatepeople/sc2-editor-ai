# Third-party Library imports
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter

# Custom Library imports
from config import get_settings


# Always return same key to share the limit across all clients
global_limiter = Limiter(key_func=lambda request: "global")

settings = get_settings()
protocol = "https" if settings.fastapi.https_status else "http"
host = str(settings.uvicorn_host)
port = settings.uvicorn_port

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            f"connect-src 'self' {protocol}://{host}:{port}; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return response
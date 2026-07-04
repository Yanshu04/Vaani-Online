import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("rate_limit")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 3600):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory store: IP -> list of timestamps
        self.request_history = {}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Limit access to computationally expensive and API-key using endpoints
        if path in ("/chat/stream", "/tts", "/transcribe"):
            # Identify client IP
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            # Clean and filter historical timestamps
            if client_ip not in self.request_history:
                self.request_history[client_ip] = []

            self.request_history[client_ip] = [
                t for t in self.request_history[client_ip]
                if now - t < self.window_seconds
            ]

            logger.info(
                f"Rate Limit Check: IP={client_ip}, path={path}, "
                f"requests={len(self.request_history[client_ip]) + 1}/{self.max_requests}"
            )

            # Check if limit exceeded
            if len(self.request_history[client_ip]) >= self.max_requests:
                logger.warning(f"Rate Limit Exceeded: IP={client_ip}, path={path}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "detail": f"Rate limit exceeded. Maximum of {self.max_requests} requests per hour. Please try again later."
                    }
                )

            # Record timestamp
            self.request_history[client_ip].append(now)

        response = await call_next(request)
        return response

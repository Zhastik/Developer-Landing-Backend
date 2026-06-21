import logging
import time
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id

        started_at = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            if not client_ip and request.client:
                client_ip = request.client.host

            logger.info(
                "request_id=%s client_ip=%s method=%s path=%s status=%s duration_ms=%s",
                request_id,
                client_ip,
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )

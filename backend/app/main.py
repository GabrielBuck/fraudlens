from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app import __version__
from app.api.v1.router import router
from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="FraudLens API",
    summary="API de investigação de anomalias em pagamentos sintéticos",
    description=(
        "Contratos operacionais para investigação humana e endpoints agregados de avaliação "
        "sintética. Scores ordenam prioridade; não estimam probabilidade de fraude."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)
allowed_origins = [settings.frontend_url]
if settings.app_env == "development":
    allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])
allowed_origins = sorted(set(allowed_origins))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "X-Correlation-ID", "X-Admin-Token"],
)
app.include_router(router)
request_windows: dict[str, deque[float]] = defaultdict(deque)


def _secure_response(response: Response, correlation_id: str) -> Response:
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


@app.middleware("http")
async def security_and_observability(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started = time.perf_counter()
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))[:64]
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = request_windows[client]
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= 240:
        return _secure_response(
            JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": "Muitas requisições.",
                        "details": None,
                        "correlation_id": correlation_id,
                    }
                },
            ),
            correlation_id,
        )
    window.append(now)
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    _secure_response(response, correlation_id)
    logger.info(
        "%s %s %s",
        request.method,
        request.url.path,
        response.status_code,
        extra={
            "correlation_id": correlation_id,
            "duration_ms": duration_ms,
            "event": "http_request",
            "method": request.method,
            "route": request.url.path,
            "status": response.status_code,
        },
    )
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))[:64]
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": None,
                "correlation_id": correlation_id,
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))[:64]
    logger.exception(
        "Unhandled application error",
        extra={"correlation_id": correlation_id, "event": "unhandled_error"},
    )
    message = str(exc) if settings.app_env == "development" else "Erro interno inesperado."
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message,
                "details": None,
                "correlation_id": correlation_id,
            }
        },
    )


@app.get("/health", tags=["System"], summary="Service health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "fraudlens-api",
        "version": __version__,
        "timestamp": datetime.now(UTC),
    }

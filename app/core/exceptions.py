import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import (
    APIConnectionError,
    APIStatusError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    def __init__(self, *, limit: int, retry_after: int) -> None:
        self.limit = limit
        self.retry_after = retry_after
        super().__init__("Request rate limit exceeded")


class RateLimitBackendError(Exception):
    pass


def register_exception_handlers(
    app: FastAPI,
) -> None:
    @app.exception_handler(RateLimitExceededError)
    async def local_rate_limit_handler(
        _request: Request,
        exc: RateLimitExceededError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Request rate limit exceeded. Try again later.",
            },
            headers={
                "Retry-After": str(exc.retry_after),
                "X-RateLimit-Limit": str(exc.limit),
            },
        )

    @app.exception_handler(RateLimitBackendError)
    async def rate_limit_backend_handler(
        _request: Request,
        exc: RateLimitBackendError,
    ) -> JSONResponse:
        logger.error(
            "Rate limit backend is unavailable",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Request validation is temporarily unavailable.",
            },
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(
        _request: Request,
        exc: RateLimitError,
    ) -> JSONResponse:
        logger.warning(
            "OpenAI rate limit exceeded: %s",
            exc,
        )

        return JSONResponse(
            status_code=429,
            content={
                "detail": ("AI service rate limit exceeded. Please try again later."),
            },
        )

    @app.exception_handler(APIConnectionError)
    async def connection_handler(
        _request: Request,
        exc: APIConnectionError,
    ) -> JSONResponse:
        logger.warning(
            "Unable to connect to OpenAI: %s",
            exc,
        )

        return JSONResponse(
            status_code=503,
            content={
                "detail": ("AI service is temporarily unavailable."),
            },
        )

    @app.exception_handler(APIStatusError)
    async def api_error_handler(
        _request: Request,
        exc: APIStatusError,
    ) -> JSONResponse:
        logger.warning(
            "OpenAI API error status_code=%s",
            exc.status_code,
        )

        return JSONResponse(
            status_code=502,
            content={
                "detail": ("AI service returned an upstream error."),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled application error",
            exc_info=(
                type(exc),
                exc,
                exc.__traceback__,
            ),
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error.",
            },
        )

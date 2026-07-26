from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APIStatusError, RateLimitError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RateLimitError)
    async def rate_limit_handler(
        request: Request,
        exc: RateLimitError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "OpenAI rate limit exceeded. Please try again later.",
            },
        )

    @app.exception_handler(APIConnectionError)
    async def connection_handler(
        request: Request,
        exc: APIConnectionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Unable to connect to OpenAI.",
            },
        )

    @app.exception_handler(APIStatusError)
    async def api_error_handler(
        request: Request,
        exc: APIStatusError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={
                "detail": "OpenAI API returned an error.",
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error.",
            },
        )
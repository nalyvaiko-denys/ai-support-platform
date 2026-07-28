import logging
import time

from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    RateLimitError,
)

from app.llm.client import BaseLLMClient
from app.schemas.llm import LLMResponse

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        *,
        api_key: str,
        chat_model: str,
        embedding_model: str,
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
        )
        self.chat_model = chat_model
        self.embedding_model = embedding_model

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        started_at = time.perf_counter()

        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.3,
            )
        except RateLimitError:
            logger.exception(
                "OpenAI rate limit exceeded"
            )
            raise
        except APIConnectionError:
            logger.exception(
                "OpenAI connection failed"
            )
            raise
        except APIStatusError:
            logger.exception(
                "OpenAI returned an API error"
            )
            raise

        response_time_ms = int(
            (time.perf_counter() - started_at) * 1000
        )

        usage = response.usage

        result = LLMResponse(
            text=(
                response.choices[0].message.content
                or ""
            ),
            model=response.model,
            prompt_tokens=(
                usage.prompt_tokens
                if usage is not None
                else 0
            ),
            completion_tokens=(
                usage.completion_tokens
                if usage is not None
                else 0
            ),
            total_tokens=(
                usage.total_tokens
                if usage is not None
                else 0
            ),
            response_time_ms=response_time_ms,
        )

        logger.info(
            "OpenAI request completed "
            "model=%s total_tokens=%s duration_ms=%s",
            result.model,
            result.total_tokens,
            result.response_time_ms,
        )

        return result

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.embedding_model,
            )
        except RateLimitError:
            logger.exception(
                "OpenAI embedding rate limit exceeded"
            )
            raise
        except APIConnectionError:
            logger.exception(
                "OpenAI embedding connection failed"
            )
            raise
        except APIStatusError:
            logger.exception(
                "OpenAI embedding API error"
            )
            raise

        return response.data[0].embedding

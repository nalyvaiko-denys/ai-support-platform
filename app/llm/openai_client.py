import logging
import time

from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    RateLimitError,
)

from app.llm.client import BaseLLMClient, EmbeddingProfile
from app.schemas.llm import LLMResponse

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    def __init__(
        self,
        *,
        api_key: str,
        chat_model: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=api_key,
        )
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension

    @property
    def embedding_profile(self) -> EmbeddingProfile:
        return EmbeddingProfile(
            provider="openai",
            model=self.embedding_model,
            dimension=self.embedding_dimension,
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        started_at = time.perf_counter()

        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.2,
            )
        except RateLimitError:
            logger.exception(
                "OpenAI rate limit exceeded",
            )
            raise
        except APIConnectionError:
            logger.exception(
                "OpenAI connection failed",
            )
            raise
        except APIStatusError:
            logger.exception(
                "OpenAI returned an API error",
            )
            raise

        response_time_ms = int((time.perf_counter() - started_at) * 1000)

        usage = response.usage
        text = response.choices[0].message.content or ""

        if not text.strip():
            raise RuntimeError("OpenAI returned an empty response")

        result = LLMResponse(
            text=text,
            model=response.model,
            prompt_tokens=(usage.prompt_tokens if usage is not None else 0),
            completion_tokens=(usage.completion_tokens if usage is not None else 0),
            total_tokens=(usage.total_tokens if usage is not None else 0),
            response_time_ms=response_time_ms,
        )

        logger.info(
            ("OpenAI request completed model=%s total_tokens=%s duration_ms=%s"),
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
                dimensions=self.embedding_dimension,
            )
        except RateLimitError:
            logger.exception(
                "OpenAI embedding rate limit exceeded",
            )
            raise
        except APIConnectionError:
            logger.exception(
                "OpenAI embedding connection failed",
            )
            raise
        except APIStatusError:
            logger.exception(
                "OpenAI embedding API error",
            )
            raise

        if not response.data:
            raise RuntimeError("OpenAI returned no embedding data")

        return response.data[0].embedding

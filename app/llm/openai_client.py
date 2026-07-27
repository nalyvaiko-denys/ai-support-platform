import logging
import time
from typing import Any

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.llm.client import BaseLLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        start = time.perf_counter()

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
            )

        except RateLimitError:
            logger.exception("OpenAI rate limit exceeded")
            raise
        except APIConnectionError:
            logger.exception("OpenAI connection failed")
            raise
        except APIStatusError:
            logger.exception("OpenAI returned API error")
            raise

        elapsed = int((time.perf_counter() - start) * 1000)

        logger.info(
            "OpenAI request completed model=%s total_tokens=%s duration_ms=%s",
            response.model,
            response.usage.total_tokens,
            elapsed,
        )

        return {
            "text": response.choices[0].message.content,
            "model": response.model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "response_time_ms": elapsed,
        }

    # ДОДАНО НОВИЙ МЕТОД:
    async def create_embedding(self, text: str) -> list[float]:
        """Генерує векторне представлення для тексту."""
        try:
            response = await self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"  # Модель, що повертає вектори розміром 1536
            )
            return response.data[0].embedding
        except Exception as e:
            logger.exception("Помилка при створенні ембедингу")
            raise e
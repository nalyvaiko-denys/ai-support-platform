from functools import lru_cache

from app.core.config import LLMProvider, settings
from app.llm.client import BaseLLMClient
from app.llm.mock_client import MockLLMClient
from app.llm.openai_client import OpenAIClient


@lru_cache
def get_llm_client() -> BaseLLMClient:
    if settings.llm_provider is LLMProvider.MOCK:
        return MockLLMClient(
            embedding_dimension=settings.embedding_dimension,
        )

    api_key = settings.openai_api_key

    if api_key is None:
        raise RuntimeError(
            "OpenAI API key is not configured"
        )

    return OpenAIClient(
        api_key=api_key.get_secret_value(),
        chat_model=settings.openai_model,
        embedding_model=settings.openai_embedding_model,
    )

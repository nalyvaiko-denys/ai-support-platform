from enum import StrEnum

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"


class Settings(BaseSettings):
    database_url: str

    llm_provider: LLMProvider = LLMProvider.MOCK
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    retrieval_min_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )
    retrieval_limit: int = Field(
        default=3,
        ge=1,
        le=20,
    )
    cors_origins: list[str] = []
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_openai_configuration(self) -> "Settings":
        if self.llm_provider is LLMProvider.OPENAI:
            api_key = (
                self.openai_api_key.get_secret_value().strip()
                if self.openai_api_key is not None
                else ""
            )

            if not api_key:
                raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        return self


settings = Settings()

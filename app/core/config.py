from enum import StrEnum

from pydantic import SecretStr, model_validator
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
    embedding_dimension: int = 1536

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
                raise ValueError(
                    "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
                )

        if self.embedding_dimension <= 0:
            raise ValueError(
                "EMBEDDING_DIMENSION must be greater than zero"
            )

        return self


settings = Settings()

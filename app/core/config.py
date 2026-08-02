from enum import StrEnum

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"


class AuthMode(StrEnum):
    DISABLED = "disabled"
    JWT = "jwt"


class JWTAlgorithm(StrEnum):
    HS256 = "HS256"
    RS256 = "RS256"


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

    auth_mode: AuthMode = AuthMode.DISABLED
    jwt_algorithm: JWTAlgorithm = JWTAlgorithm.HS256
    jwt_secret: SecretStr | None = None
    jwt_jwks_url: str | None = None
    jwt_issuer: str = "ai-support-platform"
    jwt_audience: str = "ai-support-api"
    jwt_leeway_seconds: int = Field(default=10, ge=0, le=300)

    redis_url: str = "redis://localhost:6379/0"
    rate_limit_requests: int = Field(default=10, ge=1, le=1000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)

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

        if self.auth_mode is AuthMode.JWT:
            secret = (
                self.jwt_secret.get_secret_value().strip()
                if self.jwt_secret is not None
                else ""
            )
            jwks_url = (self.jwt_jwks_url or "").strip()

            if bool(secret) == bool(jwks_url):
                raise ValueError(
                    "Configure exactly one of JWT_SECRET or JWT_JWKS_URL "
                    "when AUTH_MODE=jwt"
                )

            if self.jwt_algorithm is JWTAlgorithm.HS256 and not secret:
                raise ValueError("JWT_SECRET is required for HS256")

            if self.jwt_algorithm is JWTAlgorithm.RS256 and not jwks_url:
                raise ValueError("JWT_JWKS_URL is required for RS256")

        return self


settings = Settings()

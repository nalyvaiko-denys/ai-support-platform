from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.core.auth import JWTAuthenticator
from app.core.config import AuthMode, JWTAlgorithm, LLMProvider, Settings

TEST_SECRET = "test-secret-that-is-long-enough-for-hs256"


def create_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "database_url": "postgresql+asyncpg://test",
        "llm_provider": LLMProvider.MOCK,
        "auth_mode": AuthMode.JWT,
        "jwt_algorithm": JWTAlgorithm.HS256,
        "jwt_secret": TEST_SECRET,
        "jwt_issuer": "test-issuer",
        "jwt_audience": "test-audience",
    }
    values.update(overrides)
    return Settings(**values)


def create_token(**overrides: object) -> str:
    claims: dict[str, object] = {
        "sub": "user-123",
        "iss": "test-issuer",
        "aud": "test-audience",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    claims.update(overrides)
    return jwt.encode(
        claims,
        TEST_SECRET,
        algorithm="HS256",
    )


@pytest.mark.asyncio
async def test_authenticates_valid_token() -> None:
    authenticator = JWTAuthenticator(create_settings())

    user = await authenticator.authenticate(create_token())

    assert user.subject == "user-123"


@pytest.mark.asyncio
async def test_rejects_expired_token() -> None:
    authenticator = JWTAuthenticator(create_settings())
    token = create_token(exp=datetime.now(UTC) - timedelta(minutes=5))

    with pytest.raises(HTTPException) as error:
        await authenticator.authenticate(token)

    assert error.value.status_code == 401
    assert error.value.headers == {
        "WWW-Authenticate": "Bearer",
    }


@pytest.mark.asyncio
async def test_rejects_token_with_wrong_audience() -> None:
    authenticator = JWTAuthenticator(create_settings())

    with pytest.raises(HTTPException) as error:
        await authenticator.authenticate(create_token(aud="another-api"))

    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticates_rs256_token_from_jwks() -> None:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    settings = create_settings(
        jwt_algorithm=JWTAlgorithm.RS256,
        jwt_secret=None,
        jwt_jwks_url="https://identity.example/.well-known/jwks.json",
    )
    authenticator = JWTAuthenticator(settings)
    authenticator.jwks_client = MagicMock()
    authenticator.jwks_client.get_signing_key_from_jwt.return_value = SimpleNamespace(
        key=public_key
    )
    token = jwt.encode(
        {
            "sub": "oidc-user",
            "iss": "test-issuer",
            "aud": "test-audience",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
        headers={
            "kid": "test-key",
        },
    )

    user = await authenticator.authenticate(token)

    assert user.subject == "oidc-user"
    authenticator.jwks_client.get_signing_key_from_jwt.assert_called_once_with(token)


def test_rejects_ambiguous_key_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="Configure exactly one",
    ):
        create_settings(jwt_jwks_url="https://identity.example/.well-known/jwks.json")

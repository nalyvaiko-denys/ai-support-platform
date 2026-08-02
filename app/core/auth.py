import asyncio
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from app.core.config import AuthMode, Settings, settings


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    subject: str


bearer_scheme = HTTPBearer(
    auto_error=False,
    description="JWT access token issued for this API.",
)


class JWTAuthenticator:
    def __init__(self, configuration: Settings) -> None:
        self.configuration = configuration
        self.jwks_client = (
            PyJWKClient(configuration.jwt_jwks_url)
            if configuration.jwt_jwks_url
            else None
        )

    async def authenticate(self, token: str) -> AuthenticatedUser:
        try:
            key = await self._get_signing_key(token)
            claims = jwt.decode(
                token,
                key=key,
                algorithms=[self.configuration.jwt_algorithm.value],
                audience=self.configuration.jwt_audience,
                issuer=self.configuration.jwt_issuer,
                leeway=self.configuration.jwt_leeway_seconds,
                options={
                    "require": ["aud", "exp", "iss", "sub"],
                },
            )
        except (PyJWTError, ValueError) as exc:
            raise _unauthorized() from exc

        subject = claims.get("sub")

        if not isinstance(subject, str) or not subject.strip() or len(subject) > 255:
            raise _unauthorized()

        return AuthenticatedUser(subject=subject.strip())

    async def _get_signing_key(self, token: str) -> object:
        if self.jwks_client is not None:
            signing_key = await asyncio.to_thread(
                self.jwks_client.get_signing_key_from_jwt,
                token,
            )
            return signing_key.key

        secret = self.configuration.jwt_secret

        if secret is None:
            raise ValueError("JWT signing key is not configured")

        return secret.get_secret_value()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing bearer token.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )


@lru_cache
def get_authenticator() -> JWTAuthenticator:
    return JWTAuthenticator(settings)


Credentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


async def get_current_user(
    credentials: Credentials,
) -> AuthenticatedUser:
    if settings.auth_mode is AuthMode.DISABLED:
        return AuthenticatedUser(subject="anonymous")

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    return await get_authenticator().authenticate(credentials.credentials)


CurrentUser = Annotated[
    AuthenticatedUser,
    Depends(get_current_user),
]

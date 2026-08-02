import argparse
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import AuthMode, JWTAlgorithm, settings


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a short-lived JWT for local development.",
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="Value stored in the JWT sub claim.",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=60,
        choices=range(1, 1441),
        metavar="1-1440",
        help="Token lifetime in minutes.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    if settings.auth_mode is not AuthMode.JWT:
        raise RuntimeError("AUTH_MODE must be jwt")

    if settings.jwt_algorithm is not JWTAlgorithm.HS256:
        raise RuntimeError("Development tokens require JWT_ALGORITHM=HS256")

    if settings.jwt_secret is None:
        raise RuntimeError("JWT_SECRET is not configured")

    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": arguments.subject,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "iat": now,
            "exp": now + timedelta(minutes=arguments.minutes),
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm.value,
    )

    print(token)


if __name__ == "__main__":
    main()

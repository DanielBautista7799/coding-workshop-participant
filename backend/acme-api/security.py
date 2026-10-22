"""Password hashing and JWT authentication helpers."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import (
    ACCESS_TOKEN_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET,
    REFRESH_TOKEN_DAYS,
)


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return hashed_password.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Check whether a password matches a stored hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def create_access_token(user_id: int, email: str, role: str) -> str:
    """Create a short-lived access token."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    """Create a longer-lived refresh token."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_DAYS),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str, expected_type: str) -> dict:
    """Decode and validate a JWT."""
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token.") from exc

    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type.")

    return payload


def get_bearer_token(event: dict) -> str:
    """Read a Bearer token from the Authorization header."""
    headers = event.get("headers") or {}

    authorization = (
        headers.get("authorization")
        or headers.get("Authorization")
    )

    if not authorization:
        raise ValueError("Authorization header is required.")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Authorization header must use Bearer authentication.")

    return parts[1]
"""Authentication and user registration logic."""

from psycopg.errors import UniqueViolation

from postgres_service import get_connection
from security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def _validate_email(email: str) -> str:
    email = email.strip().lower()

    if not email.endswith("@acme.inc"):
        raise ValueError("Registration requires an @acme.inc email address.")

    return email


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")


def register_user(data: dict) -> dict:
    """Register a new employee account"""
    full_name = str(data.get("full_name", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))

    if not full_name:
        raise ValueError("Full name is required.")

    if not email:
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    email = _validate_email(email)
    _validate_password(password)

    password_hash = hash_password(password)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    full_name,
                    email,
                    password_hash,
                    role
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id, full_name, email, role, created_at;
                """,
                (
                    full_name,
                    email,
                    password_hash,
                    "EMPLOYEE",
                ),
            )

            user = cursor.fetchone()

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError("An account with that email already exists.") from exc

    return user


def login_user(data: dict) -> dict:
    """Authenticate a user and return JWT tokens."""
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        raise ValueError("Email and password are required.")

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                password_hash,
                role
            FROM users
            WHERE LOWER(email) = %s;
            """,
            (email,),
        )

        user = cursor.fetchone()

    if user is None:
        raise ValueError("Invalid email or password.")

    if not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password.")

    access_token = create_access_token(
        user["id"],
        user["email"],
        user["role"],
    )

    refresh_token = create_refresh_token(user["id"])

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


def refresh_access_token(data: dict) -> dict:
    """Create a new access token from a valid refresh token."""
    refresh_token = str(data.get("refresh_token", "")).strip()

    if not refresh_token:
        raise ValueError("Refresh token is required.")

    payload = decode_token(
        refresh_token,
        expected_type="refresh",
    )

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid refresh token.") from exc

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                email,
                role
            FROM users
            WHERE id = %s;
            """,
            (user_id,),
        )

        user = cursor.fetchone()

    if user is None:
        raise ValueError("User account no longer exists.")

    access_token = create_access_token(
        user["id"],
        user["email"],
        user["role"],
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }
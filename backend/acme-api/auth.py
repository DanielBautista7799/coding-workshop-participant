"""Authentication and user registration logic."""

import re

from psycopg.errors import UniqueViolation

from postgres_service import get_connection
from security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


# Letters (including accented letters), spaces, hyphens, apostrophes, periods.
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' .-]*$")

# Simple local part followed by the company domain.
EMAIL_PATTERN = re.compile(r"^[a-z0-9._%+-]+@acme\.inc$")

NAME_MIN_LENGTH = 2
NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 254
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def _validate_full_name(full_name: str) -> str:
    """Clean up and validate a person's full name."""
    # Collapse repeated spaces: "  Jane   Doe " -> "Jane Doe"
    full_name = " ".join(full_name.split())

    if not full_name:
        raise ValueError("Full name is required.")

    if not NAME_MIN_LENGTH <= len(full_name) <= NAME_MAX_LENGTH:
        raise ValueError(
            f"Full name must be between {NAME_MIN_LENGTH} "
            f"and {NAME_MAX_LENGTH} characters."
        )

    if not NAME_PATTERN.match(full_name):
        raise ValueError(
            "Full name can only contain letters, spaces, "
            "hyphens, apostrophes, and periods."
        )

    return full_name


def _validate_email(email: str) -> str:
    """Validate an ACME company email address."""
    email = email.strip().lower()

    if not email.endswith("@acme.inc"):
        raise ValueError("Registration requires an @acme.inc email address.")

    if len(email) > EMAIL_MAX_LENGTH or not EMAIL_PATTERN.match(email):
        raise ValueError("Enter a valid email address, like name@acme.inc.")

    return email


def _validate_password(password: str) -> None:
    """Check password length and that it mixes letters and numbers."""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError("Password must be at least 8 characters.")

    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError("Password must be at most 128 characters.")

    if not any(character.isalpha() for character in password):
        raise ValueError("Password must include at least one letter.")

    if not any(character.isdigit() for character in password):
        raise ValueError("Password must include at least one number.")


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

    full_name = _validate_full_name(full_name)
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

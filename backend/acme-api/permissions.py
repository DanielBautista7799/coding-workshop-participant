"""authentication and role permission helpers."""

from postgres_service import get_connection
from security import decode_token, get_bearer_token


"""Uses the JWT to identify the user, then checks whether their role allows the action."""


def get_current_user(event: dict) -> dict:
    token = get_bearer_token(event)

    payload = decode_token(
        token,
        expected_type="access",
    )

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid access token.") from exc

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                full_name,
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

    return user


def require_role(user: dict, *allowed_roles: str) -> None:
    """Raise an error when the user does not have an allowed role."""
    if user["role"] not in allowed_roles:
        raise PermissionError("You do not have permission to perform this action.")


def is_admin(user: dict) -> bool:
    """Return True when the user is a Facility Admin."""
    return user["role"] == "FACILITY_ADMIN"


def is_engineer(user: dict) -> bool:
    """Return True when the user is an Engineer."""
    return user["role"] == "ENGINEER"


def is_employee(user: dict) -> bool:
    """Return True when the user is an Employee."""
    return user["role"] == "EMPLOYEE"
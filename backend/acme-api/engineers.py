"""Engineer profile CRUD operations."""

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from permissions import require_role
from postgres_service import get_connection
from security import hash_password


def _require_admin(user: dict) -> None:
    """Only Facility Admins can manage engineers."""
    require_role(user, "FACILITY_ADMIN")


def _required_text(data: dict, field: str) -> str:
    """Return a required text field or raise a validation error."""
    value = str(data.get(field, "")).strip()

    if not value:
        raise ValueError(f"{field.replace('_', ' ').title()} is required.")

    return value


def _validate_email(email: str) -> str:
    """Validate an ACME company email."""
    email = email.strip().lower()

    if not email.endswith("@acme.inc"):
        raise ValueError("Engineer email must use @acme.inc.")

    return email


def list_engineers() -> list:
    """Return all engineer profiles and their current workload."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                engineer_profiles.id,
                users.id AS user_id,
                users.full_name,
                users.email,
                engineer_profiles.specialty,
                engineer_profiles.is_active,
                COUNT(incidents.id) FILTER (
                    WHERE incidents.status IN (
                        'OPEN',
                        'IN_PROGRESS',
                        'BLOCKED'
                    )
                ) AS active_incidents
            FROM engineer_profiles
            JOIN users
                ON users.id = engineer_profiles.user_id
            LEFT JOIN incidents
                ON incidents.engineer_id = engineer_profiles.id
            GROUP BY
                engineer_profiles.id,
                users.id,
                users.full_name,
                users.email,
                engineer_profiles.specialty,
                engineer_profiles.is_active
            ORDER BY users.full_name;
            """
        )

        return cursor.fetchall()


def get_engineer(engineer_id: int) -> dict:
    """Return one engineer profile."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                engineer_profiles.id,
                users.id AS user_id,
                users.full_name,
                users.email,
                engineer_profiles.specialty,
                engineer_profiles.is_active
            FROM engineer_profiles
            JOIN users
                ON users.id = engineer_profiles.user_id
            WHERE engineer_profiles.id = %s;
            """,
            (engineer_id,),
        )

        engineer = cursor.fetchone()

    if engineer is None:
        raise LookupError("Engineer not found.")

    return engineer


def create_engineer(data: dict, user: dict) -> dict:
    """create their login account, then create their engineer profile, then save both."""
    _require_admin(user)

    full_name = _required_text(data, "full_name")
    email = _validate_email(_required_text(data, "email"))
    password = _required_text(data, "password")
    specialty = str(data.get("specialty", "")).strip() or None

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")

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
                RETURNING id;
                """,
                (
                    full_name,
                    email,
                    password_hash,
                    "ENGINEER",
                ),
            )

            new_user = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO engineer_profiles (
                    user_id,
                    specialty,
                    is_active
                )
                VALUES (%s, %s, TRUE)
                RETURNING id;
                """,
                (
                    new_user["id"],
                    specialty,
                ),
            )

            engineer = cursor.fetchone()

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "A user with that email already exists."
        ) from exc

    return get_engineer(engineer["id"])


def update_engineer(
    engineer_id: int,
    data: dict,
    user: dict,
) -> dict:
    """Update an engineer profile."""
    _require_admin(user)

    full_name = _required_text(data, "full_name")
    email = _validate_email(_required_text(data, "email"))
    specialty = str(data.get("specialty", "")).strip() or None
    is_active = data.get("is_active", True)

    if not isinstance(is_active, bool):
        raise ValueError("is_active must be true or false.")

    connection = get_connection()

    engineer = get_engineer(engineer_id)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET full_name = %s,
                    email = %s
                WHERE id = %s;
                """,
                (
                    full_name,
                    email,
                    engineer["user_id"],
                ),
            )

            cursor.execute(
                """
                UPDATE engineer_profiles
                SET specialty = %s,
                    is_active = %s
                WHERE id = %s;
                """,
                (
                    specialty,
                    is_active,
                    engineer_id,
                ),
            )

        connection.commit()

    except UniqueViolation as exc:
        connection.rollback()
        raise ValueError(
            "A user with that email already exists."
        ) from exc

    return get_engineer(engineer_id)


def delete_engineer(engineer_id: int, user: dict) -> None:
    """Delete an engineer when no incidents reference the profile."""
    _require_admin(user)

    engineer = get_engineer(engineer_id)
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM engineer_profiles
                WHERE id = %s;
                """,
                (engineer_id,),
            )

            cursor.execute(
                """
                DELETE FROM users
                WHERE id = %s;
                """,
                (engineer["user_id"],),
            )

        connection.commit()


    
    except ForeignKeyViolation as exc:
        """If the database blocks this because another record still points to it, catch that error."""
        connection.rollback()
        raise ValueError(
            "Engineer cannot be deleted while incidents reference them. "
            "Deactivate the engineer instead."
        ) from exc
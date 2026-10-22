"""Adds demo users, locations, engineers, and incidents for testing and presentation."""

from config import DEMO_PASSWORD
from postgres_service import get_connection
from security import hash_password


def seed_database() -> None:
    """Insert reusable demo data into the database."""
    connection = get_connection()
    password_hash = hash_password(DEMO_PASSWORD)

    try:
        with connection.cursor() as cursor:

            # USERS

            demo_users = [
                (
                    "Facility Admin",
                    "admin@acme.inc",
                    "FACILITY_ADMIN",
                ),
                (
                    "Demo Employee",
                    "employee@acme.inc",
                    "EMPLOYEE",
                ),
                (
                    "Alex Engineer",
                    "engineer@acme.inc",
                    "ENGINEER",
                ),
            ]

            user_ids = {}

            for full_name, email, role in demo_users:
                cursor.execute(
                    """
                    INSERT INTO users (
                        full_name,
                        email,
                        password_hash,
                        role
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email)
                    DO UPDATE SET
                        full_name = EXCLUDED.full_name,
                        password_hash = EXCLUDED.password_hash,
                        role = EXCLUDED.role
                    RETURNING id;
                    """,
                    (
                        full_name,
                        email,
                        password_hash,
                        role,
                    ),
                )

                user_ids[role] = cursor.fetchone()["id"]

            # BUILDING

            cursor.execute(
                """
                INSERT INTO buildings (
                    name,
                    address
                )
                VALUES (
                    'Tampa Operations Center',
                    'Tampa, FL'
                )
                ON CONFLICT (name)
                DO UPDATE SET
                    address = EXCLUDED.address
                RETURNING id;
                """
            )

            building_id = cursor.fetchone()["id"]

            # FLOOR

            cursor.execute(
                """
                INSERT INTO floors (
                    building_id,
                    name
                )
                VALUES (%s, 'Floor 1')
                ON CONFLICT (building_id, name)
                DO UPDATE SET
                    name = EXCLUDED.name
                RETURNING id;
                """,
                (building_id,),
            )

            floor_id = cursor.fetchone()["id"]

            # SEATS

            seat_ids = {}

            for label in ["A-101", "A-102", "A-103"]:
                cursor.execute(
                    """
                    INSERT INTO seats (
                        floor_id,
                        label
                    )
                    VALUES (%s, %s)
                    ON CONFLICT (floor_id, label)
                    DO UPDATE SET
                        label = EXCLUDED.label
                    RETURNING id;
                    """,
                    (
                        floor_id,
                        label,
                    ),
                )

                seat_ids[label] = cursor.fetchone()["id"]

            # ENGINEER PROFILE

            cursor.execute(
                """
                INSERT INTO engineer_profiles (
                    user_id,
                    specialty,
                    is_active
                )
                VALUES (
                    %s,
                    'Hardware and Workplace Technology',
                    TRUE
                )
                ON CONFLICT (user_id)
                DO UPDATE SET
                    specialty = EXCLUDED.specialty,
                    is_active = TRUE
                RETURNING id;
                """,
                (user_ids["ENGINEER"],),
            )

            engineer_id = cursor.fetchone()["id"]

            # SAMPLE INCIDENTS

            incidents = [
                {
                    "title": "Monitor will not power on",
                    "description": "Desk monitor does not turn on.",
                    "category": "Hardware",
                    "priority": "MEDIUM",
                    "status": "OPEN",
                    "seat_id": seat_ids["A-101"],
                    "engineer_id": None,
                    "blocked_reason": None,
                },
                {
                    "title": "Docking station disconnecting",
                    "description": "Laptop repeatedly disconnects from the dock.",
                    "category": "Hardware",
                    "priority": "HIGH",
                    "status": "IN_PROGRESS",
                    "seat_id": seat_ids["A-102"],
                    "engineer_id": engineer_id,
                    "blocked_reason": None,
                },
                {
                    "title": "Replacement keyboard delayed",
                    "description": "Keyboard requires replacement.",
                    "category": "Hardware",
                    "priority": "MEDIUM",
                    "status": "BLOCKED",
                    "seat_id": seat_ids["A-103"],
                    "engineer_id": engineer_id,
                    "blocked_reason": "Waiting for replacement keyboard.",
                },
            ]

            for incident in incidents:

                cursor.execute(
                    """
                    SELECT id
                    FROM incidents
                    WHERE title = %s
                    AND reporter_id = %s;
                    """,
                    (
                        incident["title"],
                        user_ids["EMPLOYEE"],
                    ),
                )

                existing = cursor.fetchone()

                if existing is not None:
                    continue

                cursor.execute(
                    """
                    INSERT INTO incidents (
                        title,
                        description,
                        category,
                        priority,
                        status,
                        reporter_id,
                        seat_id,
                        engineer_id,
                        blocked_reason,
                        created_at,
                        assigned_at,
                        acknowledged_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,

                        NOW() - INTERVAL '60 minutes',

                        CASE
                            WHEN %s::INTEGER IS NOT NULL
                            THEN NOW() - INTERVAL '45 minutes'
                            ELSE NULL
                        END,

                        CASE
                            WHEN %s::TEXT IN (
                                'IN_PROGRESS',
                                'BLOCKED'
                            )
                            THEN NOW() - INTERVAL '30 minutes'
                            ELSE NULL
                        END
                    )
                    RETURNING id;
                    """,
                    (
                        incident["title"],
                        incident["description"],
                        incident["category"],
                        incident["priority"],
                        incident["status"],
                        user_ids["EMPLOYEE"],
                        incident["seat_id"],
                        incident["engineer_id"],
                        incident["blocked_reason"],
                        incident["engineer_id"],
                        incident["status"],
                    ),
                )

                incident_id = cursor.fetchone()["id"]

                cursor.execute(
                    """
                    INSERT INTO status_history (
                        incident_id,
                        changed_by_id,
                        old_status,
                        new_status
                    )
                    VALUES (
                        %s,
                        %s,
                        NULL,
                        %s
                    );
                    """,
                    (
                        incident_id,
                        user_ids["EMPLOYEE"],
                        incident["status"],
                    ),
                )

        connection.commit()

    except Exception:
        connection.rollback()
        raise


if __name__ == "__main__":
    seed_database()

    print("Demo data added successfully.")
    print()
    print("Demo accounts:")
    print(f"Admin:    admin@acme.inc / {DEMO_PASSWORD}")
    print(f"Employee: employee@acme.inc / {DEMO_PASSWORD}")
    print(f"Engineer: engineer@acme.inc / {DEMO_PASSWORD}")
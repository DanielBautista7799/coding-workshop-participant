"""Initialize and seed a fresh workshop Aurora database from inside Lambda.

This module is used only by an IAM-authenticated direct Lambda invocation.
It is not exposed as an HTTP route and will not overwrite a populated database.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any
import bcrypt
import seed_realistic_acme as realistic
from database_setup import initialize_database
from postgres_service import get_connection

LOCK_NAME = "acme-workshop-bootstrap"
CORE_TABLES = ("users", "engineer_profiles", "buildings", "floors", "seats", "incidents")

def _count_rows(connection: Any, table: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT COUNT(*) AS count FROM "{table}";')
        row = cursor.fetchone()
    return int(row["count"] if isinstance(row, dict) else row[0])

def _counts(connection: Any, inspector: realistic.SchemaInspector) -> dict[str, int]:
    result = {}
    for table in (*CORE_TABLES, "skills", "engineer_skills"):
        if inspector.table_exists(table):
            result[table] = _count_rows(connection, table)
    return result

def bootstrap_database() -> dict:
    initialize_database()
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_lock(hashtext(%s));", (LOCK_NAME,))

    try:
        inspector = realistic.SchemaInspector(connection)
        realistic._validate_core_schema(inspector)
        before = _counts(connection, inspector)

        if before.get("users", 0) > 0:
            return {
                "schema": "ready",
                "seeded": False,
                "reason": "existing application data preserved",
                "counts": before,
            }

        partial = {k: v for k, v in before.items() if k != "users" and v > 0}
        if partial:
            raise RuntimeError(
                "Refusing automatic seed because the database contains partial data: "
                f"{partial}"
            )

        realistic.RNG.seed(20261021)

        for table, column in (
            ("users", "role"),
            ("engineer_profiles", "availability"),
            ("incidents", "status"),
            ("incidents", "priority"),
            ("incidents", "escalation_status"),
        ):
            if inspector.table_exists(table) and column in inspector.columns(table):
                inspector.allowed_values(table, column)

        password_hash = bcrypt.hashpw(
            realistic.PASSWORD.encode("utf-8"),
            bcrypt.gensalt(rounds=10),
        ).decode("utf-8")
        now = datetime.now().replace(microsecond=0)

        admins, employees, engineer_users = realistic._seed_users(
            inspector, password_hash, now
        )
        engineers = realistic._seed_engineers(inspector, engineer_users, now)
        realistic._seed_skills(inspector, engineers)
        seats = realistic._seed_facilities(inspector, now)
        incidents = realistic._seed_incidents(
            inspector, employees, engineers, seats, now
        )

        if len(admins) != realistic.ADMIN_COUNT:
            raise RuntimeError("Unexpected administrator seed count.")
        if len(employees) != realistic.EMPLOYEE_COUNT:
            raise RuntimeError("Unexpected employee seed count.")
        if len(engineers) != realistic.ENGINEER_COUNT:
            raise RuntimeError("Unexpected engineer seed count.")
        if len(incidents) != realistic.INCIDENT_COUNT:
            raise RuntimeError("Unexpected incident seed count.")

        connection.commit()
        return {
            "schema": "ready",
            "seeded": True,
            "counts": _counts(connection, realistic.SchemaInspector(connection)),
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT pg_advisory_unlock(hashtext(%s));",
                    (LOCK_NAME,),
                )
            connection.commit()
        except Exception:
            connection.rollback()

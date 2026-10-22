"""Sets up a separate PostgreSQL test database and reusable test helpers."""

import json
import os
import sys
from pathlib import Path

import psycopg
import pytest


SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))


# Make sure tests never use the development database.
os.environ["IS_LOCAL"] = "true"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["POSTGRES_NAME"] = "acme_workplace_test"
os.environ["POSTGRES_USER"] = os.getenv("USER", "postgres")
os.environ["POSTGRES_PASS"] = ""
os.environ["JWT_SECRET"] = "acme-test-secret-key-32-bytes-minimum"
os.environ["DEMO_PASSWORD"] = "AcmeDemo123!"


from database_setup import initialize_database
from postgres_service import close_connection, get_connection
from seed import seed_database


TEST_DATABASE = "acme_workplace_test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create the separate test database and its tables once per test run."""
    admin_connection = psycopg.connect(
        host="localhost",
        port="5432",
        dbname="postgres",
        user=os.getenv("USER", "postgres"),
        password="",
        autocommit=True,
    )

    with admin_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM pg_database
            WHERE datname = %s;
            """,
            (TEST_DATABASE,),
        )

        if cursor.fetchone() is None:
            cursor.execute(
                f"CREATE DATABASE {TEST_DATABASE};"
            )

    admin_connection.close()

    close_connection()
    initialize_database()

    yield

    close_connection()


@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset and reseed the test database before every test."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            TRUNCATE TABLE
                status_history,
                ticket_notes,
                incidents,
                engineer_profiles,
                seats,
                floors,
                buildings,
                users
            RESTART IDENTITY CASCADE;
            """
        )

    connection.commit()

    seed_database()

    yield

    connection.rollback()


def make_event(
    method: str,
    path: str,
    body: dict | None = None,
    token: str | None = None,
    query: dict | None = None,
) -> dict:
    """Create a fake Lambda HTTP event for router tests."""
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if body is not None:
        headers["Content-Type"] = "application/json"

    return {
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": method,
            }
        },
        "headers": headers,
        "queryStringParameters": query,
        "body": json.dumps(body) if body is not None else None,
    }


def get_response_body(response: dict):
    """Convert the router's JSON response body back into Python data."""
    if not response.get("body"):
        return None

    return json.loads(response["body"])
"""Reads schema.sql and creates the PostgreSQL tables for the application."""

from pathlib import Path

from postgres_service import get_connection


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def initialize_database() -> None:
    """Run every SQL statement in schema.sql."""
    connection = get_connection()

    schema_sql = SCHEMA_PATH.read_text()

    try:
        with connection.cursor() as cursor:
            for statement in schema_sql.split(";"):
                statement = statement.strip()

                if statement:
                    cursor.execute(statement)

        connection.commit()

    except Exception:
        connection.rollback()
        raise


if __name__ == "__main__":
    initialize_database()
    print("Database schema created successfully.")
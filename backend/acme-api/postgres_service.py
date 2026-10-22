"""PostgreSQL connection management."""

import psycopg
from psycopg.rows import dict_row

from config import (
    IS_LOCAL,
    POSTGRES_HOST,
    POSTGRES_NAME,
    POSTGRES_PASS,
    POSTGRES_PORT,
    POSTGRES_USER,
)


PG_CONN = None


def get_connection():
    """Return an open postgres connection/ checks if we have a connection"""
    """Like get_session() before, but returns a direct PostgreSQL connection instead of a SQLAlchemy session."""
    global PG_CONN

    if PG_CONN is None or PG_CONN.closed:
        connection_options = {
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "dbname": POSTGRES_NAME,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASS,
            "row_factory": dict_row,
        }

        if not IS_LOCAL:
            connection_options["sslmode"] = "require"

        PG_CONN = psycopg.connect(**connection_options)

    return PG_CONN


def close_connection():
    """close the sql connection if one is open."""
    global PG_CONN

    if PG_CONN is not None and not PG_CONN.closed:
        PG_CONN.close()

    PG_CONN = None
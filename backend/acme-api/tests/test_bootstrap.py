"""Tests the IAM-only cloud database bootstrap path."""
from bootstrap import bootstrap_database
from function import handler
from postgres_service import get_connection

def test_bootstrap_preserves_existing_data() -> None:
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS count FROM users;")
        before = int(cursor.fetchone()["count"])

    result = bootstrap_database()

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS count FROM users;")
        after = int(cursor.fetchone()["count"])

    assert before > 0
    assert result["seeded"] is False
    assert after == before

def test_function_dispatches_direct_bootstrap(monkeypatch) -> None:
    monkeypatch.setattr(
        "function.bootstrap_database",
        lambda: {"schema": "ready", "seeded": True, "counts": {"users": 84}},
    )
    response = handler({"workshop_action": "bootstrap"}, None)
    assert response["status"] == "ok"
    assert response["action"] == "bootstrap"
    assert response["schema"] == "ready"
    assert response["seeded"] is True

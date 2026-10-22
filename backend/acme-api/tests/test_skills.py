"""Tests engineer skill catalog, assignments, validation, and permissions."""

import pytest

import skills


ADMIN = {"id": 1, "role": "FACILITY_ADMIN"}
EMPLOYEE = {"id": 2, "role": "EMPLOYEE"}


class FakeCursor:
    def __init__(
        self,
        *,
        fetchall_batches=None,
        fetchone_values=None,
    ):
        self.fetchall_batches = list(fetchall_batches or [])
        self.fetchone_values = list(fetchone_values or [])
        self.executed = []
        self.executemany_calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def executemany(self, query, params):
        self.executemany_calls.append(
            (query, list(params))
        )

    def fetchall(self):
        if not self.fetchall_batches:
            return []
        return self.fetchall_batches.pop(0)

    def fetchone(self):
        if not self.fetchone_values:
            return None
        return self.fetchone_values.pop(0)


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def _patch_connection(monkeypatch, cursor):
    connection = FakeConnection(cursor)

    monkeypatch.setattr(
        skills,
        "get_connection",
        lambda: connection,
    )

    return connection


def test_list_skills_returns_catalog(monkeypatch):
    """Admins should receive the skill catalog."""
    cursor = FakeCursor(
        fetchall_batches=[
            [
                {"id": 1, "name": "Hardware"},
                {"id": 2, "name": "Networking"},
            ]
        ]
    )
    _patch_connection(monkeypatch, cursor)

    result = skills.list_skills(ADMIN)

    assert result == [
        {"id": 1, "name": "Hardware"},
        {"id": 2, "name": "Networking"},
    ]


def test_list_skills_requires_admin():
    """Employees must not be allowed to manage skill data."""
    with pytest.raises(PermissionError):
        skills.list_skills(EMPLOYEE)


def test_list_engineer_skills_groups_names(monkeypatch):
    """Skill rows should be grouped under each engineer profile."""
    cursor = FakeCursor(
        fetchall_batches=[
            [
                {"engineer_id": 1, "name": "Hardware"},
                {"engineer_id": 1, "name": "Networking"},
                {"engineer_id": 2, "name": None},
            ]
        ]
    )
    _patch_connection(monkeypatch, cursor)

    result = skills.list_engineer_skills(ADMIN)

    assert result == [
        {
            "engineer_id": 1,
            "skills": ["Hardware", "Networking"],
        },
        {
            "engineer_id": 2,
            "skills": [],
        },
    ]


def test_update_engineer_skills_replaces_assignments(monkeypatch):
    """A valid update should replace assignments and commit once."""
    cursor = FakeCursor(
        fetchone_values=[{"id": 1}],
        fetchall_batches=[
            [
                {"id": 10, "name": "Hardware"},
                {"id": 11, "name": "Networking"},
            ]
        ],
    )
    connection = _patch_connection(monkeypatch, cursor)

    result = skills.update_engineer_skills(
        1,
        {
            "skills": [
                " Networking ",
                "Hardware",
                "Hardware",
                "",
            ]
        },
        ADMIN,
    )

    assert result == {
        "engineer_id": 1,
        "skills": ["Hardware", "Networking"],
    }
    assert connection.committed is True
    assert connection.rolled_back is False
    assert len(cursor.executemany_calls) == 1
    assert cursor.executemany_calls[0][1] == [
        (1, 11),
        (1, 10),
    ]


def test_update_engineer_skills_allows_clearing(monkeypatch):
    """An empty skill list should remove all existing assignments."""
    cursor = FakeCursor(
        fetchone_values=[{"id": 1}],
    )
    connection = _patch_connection(monkeypatch, cursor)

    result = skills.update_engineer_skills(
        1,
        {"skills": []},
        ADMIN,
    )

    assert result == {
        "engineer_id": 1,
        "skills": [],
    }
    assert connection.committed is True
    assert cursor.executemany_calls == []


def test_update_engineer_skills_rejects_unknown_skill(monkeypatch):
    """Unknown catalog values should fail and roll back."""
    cursor = FakeCursor(
        fetchone_values=[{"id": 1}],
        fetchall_batches=[
            [{"id": 10, "name": "Hardware"}]
        ],
    )
    connection = _patch_connection(monkeypatch, cursor)

    with pytest.raises(
        ValueError,
        match="Unknown skills: Teleportation",
    ):
        skills.update_engineer_skills(
            1,
            {
                "skills": [
                    "Hardware",
                    "Teleportation",
                ]
            },
            ADMIN,
        )

    assert connection.committed is False
    assert connection.rolled_back is True


def test_update_engineer_skills_rejects_missing_engineer(monkeypatch):
    """Updating a nonexistent engineer should return a lookup error."""
    cursor = FakeCursor(fetchone_values=[None])
    connection = _patch_connection(monkeypatch, cursor)

    with pytest.raises(
        LookupError,
        match="Engineer not found",
    ):
        skills.update_engineer_skills(
            999,
            {"skills": ["Hardware"]},
            ADMIN,
        )

    assert connection.committed is False
    assert connection.rolled_back is True


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            {"skills": "Hardware"},
            "skills must be a list",
        ),
        (
            {"skills": ["Hardware", 123]},
            "Each skill must be a string",
        ),
        (
            {
                "skills": [
                    "Skill 1",
                    "Skill 2",
                    "Skill 3",
                    "Skill 4",
                    "Skill 5",
                    "Skill 6",
                    "Skill 7",
                    "Skill 8",
                    "Skill 9",
                ]
            },
            "at most 8 skills",
        ),
    ],
)
def test_update_engineer_skills_validates_payload(
    payload,
    message,
):
    """Bad skill payloads should be rejected before database work."""
    with pytest.raises(ValueError, match=message):
        skills.update_engineer_skills(
            1,
            payload,
            ADMIN,
        )


def test_update_engineer_skills_requires_admin():
    """Only Facility Admins should be allowed to replace skills."""
    with pytest.raises(PermissionError):
        skills.update_engineer_skills(
            1,
            {"skills": ["Hardware"]},
            EMPLOYEE,
        )

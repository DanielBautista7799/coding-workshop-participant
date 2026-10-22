"""Create a deterministic, realistic ACME workshop demo dataset.

Targets:
- 4 facility admins
- 50 employees
- 30 engineers
- 4 buildings / 12 floors / 180 seats
- 100 incidents
- engineer skills, notes, history, escalations, and realistic timestamps

Run from backend/acme-api with the project virtual environment active:
    python seed_realistic_acme.py --apply

This script intentionally replaces the current demo data in the connected database.
It introspects the live schema so it can tolerate small column differences in the
workshop implementation.
"""

from __future__ import annotations

import argparse
import random
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Any

import bcrypt
from psycopg import sql

from postgres_service import get_connection


RNG = random.Random(20261021)
PASSWORD = "AcmeDemo123!"

ADMIN_COUNT = 4
EMPLOYEE_COUNT = 50
ENGINEER_COUNT = 30
INCIDENT_COUNT = 100

SKILL_NAMES = [
    "Hardware",
    "Networking",
    "AV",
    "Electrical",
    "HVAC",
    "Building Systems",
    "Access Control",
    "Plumbing",
    "Safety Systems",
    "Workstations",
]

BUILDINGS = [
    {
        "name": "Tampa Operations Center",
        "address": "101 Operations Way",
        "city": "Tampa",
        "state": "FL",
        "postal_code": "33610",
    },
    {
        "name": "Jacksonville Technology Center",
        "address": "2400 River Tech Drive",
        "city": "Jacksonville",
        "state": "FL",
        "postal_code": "32202",
    },
    {
        "name": "New York Corporate Office",
        "address": "388 Madison Avenue",
        "city": "New York",
        "state": "NY",
        "postal_code": "10017",
    },
    {
        "name": "Irving Operations Campus",
        "address": "7500 Las Colinas Boulevard",
        "city": "Irving",
        "state": "TX",
        "postal_code": "75039",
    },
]

SPECIALTY_SKILLS = [
    ("IT Support", ["Hardware", "Workstations", "Networking"]),
    ("Network Infrastructure", ["Networking", "Hardware"]),
    ("AV Systems", ["AV", "Hardware", "Workstations"]),
    ("Electrical Systems", ["Electrical", "Safety Systems"]),
    ("HVAC", ["HVAC", "Building Systems"]),
    ("Building Systems", ["Building Systems", "Plumbing", "HVAC"]),
    ("Access Control", ["Access Control", "Safety Systems", "Networking"]),
    ("Workstation Support", ["Workstations", "Hardware"]),
    ("Facilities Technology", ["Building Systems", "Electrical", "AV"]),
    ("Safety Systems", ["Safety Systems", "Access Control", "Electrical"]),
]

CATEGORY_SKILLS = {
    "Hardware": {"Hardware", "Workstations"},
    "Networking": {"Networking"},
    "AV": {"AV", "Hardware"},
    "Electrical": {"Electrical", "Safety Systems"},
    "HVAC": {"HVAC", "Building Systems"},
    "Access Control": {"Access Control", "Safety Systems"},
    "Building Systems": {"Building Systems", "Plumbing", "HVAC"},
    "Workstations": {"Workstations", "Hardware"},
}

INCIDENT_TEMPLATES = {
    "Hardware": [
        ("Docking station not detected", "Employee workstation no longer recognizes the USB-C docking station."),
        ("Conference room monitor has no signal", "Display powers on but does not receive video from the room PC."),
        ("Printer repeatedly jams", "Shared floor printer jams during normal multi-page print jobs."),
        ("Badge printer is offline", "Reception badge printer is powered on but unavailable from the workstation."),
    ],
    "Networking": [
        ("Intermittent wired network connection", "Desk network connection drops several times during the workday."),
        ("Wi-Fi unavailable in meeting area", "Corporate wireless network is not reachable from this section of the floor."),
        ("VoIP phone losing connection", "Desk phone intermittently loses network registration and reconnects."),
        ("Slow network performance", "Users in this area are reporting unusually slow access to internal applications."),
    ],
    "AV": [
        ("Conference room camera unavailable", "Video meeting software cannot detect the installed conference camera."),
        ("Room speakers producing no audio", "Conference room display works but no sound is produced by the room speakers."),
        ("Wireless presentation system offline", "Presentation receiver is not advertising or accepting connections."),
        ("Microphone has heavy static", "Meeting room microphone produces persistent static during calls."),
    ],
    "Electrical": [
        ("Desk power outlets not working", "Multiple outlets at the workstation have stopped supplying power."),
        ("Floor lighting circuit issue", "A section of overhead lighting is flickering and intermittently turning off."),
        ("UPS warning alarm active", "Local UPS unit is showing a persistent warning condition."),
        ("Power strip overheating", "Power strip under the workstation is unusually warm and should be inspected."),
    ],
    "HVAC": [
        ("Workspace temperature too warm", "Temperature in this work area has remained above the normal comfort range."),
        ("Ventilation airflow reduced", "Airflow from nearby vents is significantly lower than adjacent areas."),
        ("HVAC unit making loud noise", "Mechanical noise is coming from the ceiling HVAC equipment."),
        ("Conference room too cold", "Room temperature remains unusually low even when occupied."),
    ],
    "Access Control": [
        ("Badge reader not accepting cards", "Door reader lights up but rejects valid employee access badges."),
        ("Secure door not latching", "Access-controlled door does not consistently latch after closing."),
        ("Turnstile reader intermittent", "Lobby turnstile badge reader works only intermittently."),
        ("Visitor access panel offline", "Front desk visitor access panel is not communicating with the controller."),
    ],
    "Building Systems": [
        ("Ceiling tile leak reported", "Small water stain and moisture are visible above the workstation area."),
        ("Restroom fixture needs repair", "Fixture is leaking slowly and requires facilities attention."),
        ("Automatic door closer failing", "Interior door is no longer closing completely without assistance."),
        ("Water dispenser leaking", "Break-room dispenser has a slow leak around the supply connection."),
    ],
    "Workstations": [
        ("Laptop unable to boot normally", "Employee laptop stops during startup and does not reach the sign-in screen."),
        ("Keyboard input intermittently stops", "USB keyboard randomly stops responding until reconnected."),
        ("Second monitor not recognized", "Operating system detects only one of the two connected monitors."),
        ("Workstation performance degraded", "Desktop applications have become unusually slow during normal use."),
    ],
}

BLOCKED_REASONS = [
    "Replacement part is awaiting delivery.",
    "Vendor access is required before work can continue.",
    "Repair requires an approved maintenance window.",
    "Additional diagnostic equipment is needed.",
    "Area is temporarily inaccessible due to another facilities task.",
]

ESCALATION_REASONS = [
    "Issue is affecting multiple employees in a high-traffic work area.",
    "Repeated incidents at this location are disrupting normal operations.",
    "Business-critical meeting space is unavailable and needs priority attention.",
    "Problem has persisted longer than the expected service window.",
    "Access or safety impact requires additional administrative review.",
]

FIRST_NAMES = [
    "Alex", "Maya", "Jordan", "Taylor", "Chris", "Priya", "Marcus", "Sofia",
    "Ethan", "Avery", "Noah", "Olivia", "Liam", "Emma", "Mateo", "Isabella",
    "Lucas", "Mia", "Elijah", "Amelia", "James", "Harper", "Benjamin", "Evelyn",
    "Henry", "Luna", "Daniel", "Camila", "Jack", "Gianna", "Leo", "Aria",
    "Owen", "Layla", "Julian", "Nora", "Caleb", "Zoe", "Isaac", "Naomi",
    "Adrian", "Elena", "Aaron", "Valeria", "Ryan", "Leah", "Nathan", "Ivy",
    "Dylan", "Alice", "Connor", "Ruby", "Miles", "Grace", "Jason", "Lucy",
    "Kevin", "Claire", "Adam", "Sarah", "Eric", "Jasmine", "Victor", "Anna",
    "Brian", "Natalie", "Justin", "Eva", "Trevor", "Maria", "Colin", "Lily",
    "Sean", "Gabriela", "Ian", "Katherine", "Wesley", "Monica", "Joel", "Diana",
    "Cameron", "Rebecca", "Patrick", "Vanessa", "Blake", "Michelle", "Grant", "Renee",
]

LAST_NAMES = [
    "Johnson", "Patel", "Williams", "Garcia", "Chen", "Brown", "Davis", "Martinez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
    "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres",
    "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall",
    "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans",
    "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart",
]


class SchemaInspector:
    """Read PostgreSQL metadata and provide schema-tolerant inserts."""

    def __init__(self, connection: Any):
        self.connection = connection
        self._columns: dict[str, dict[str, dict[str, Any]]] = {}
        self._allowed_cache: dict[tuple[str, str], list[str]] = {}
        self._token = 0

    @staticmethod
    def _dict_rows(cursor: Any) -> list[dict[str, Any]]:
        rows = cursor.fetchall()
        if not rows:
            return []
        first = rows[0]
        if isinstance(first, dict):
            return [dict(row) for row in rows]
        names = [getattr(desc, "name", desc[0]) for desc in cursor.description]
        return [dict(zip(names, row)) for row in rows]

    def table_exists(self, table: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass(%s);", (table,))
            row = cursor.fetchone()
        value = row.get("to_regclass") if isinstance(row, dict) else row[0]
        return value is not None

    def columns(self, table: str) -> dict[str, dict[str, Any]]:
        if table in self._columns:
            return self._columns[table]
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    column_name,
                    is_nullable,
                    data_type,
                    udt_name,
                    column_default,
                    is_identity,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = %s
                ORDER BY ordinal_position;
                """,
                (table,),
            )
            rows = self._dict_rows(cursor)
        result = {row["column_name"]: row for row in rows}
        self._columns[table] = result
        return result

    def _constraint_values(self, table: str, column: str) -> list[str]:
        values: list[str] = []
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_get_constraintdef(c.oid) AS definition
                FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE n.nspname = current_schema()
                  AND t.relname = %s
                  AND c.contype = 'c';
                """,
                (table,),
            )
            rows = self._dict_rows(cursor)
        for row in rows:
            definition = str(row["definition"])
            if column not in definition:
                continue
            values.extend(
                match.replace("''", "'")
                for match in re.findall(r"'((?:''|[^'])*)'", definition)
            )
        return values

    def _enum_values(self, udt_name: str) -> list[str]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT e.enumlabel
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = %s
                ORDER BY e.enumsortorder;
                """,
                (udt_name,),
            )
            rows = cursor.fetchall()
        if not rows:
            return []
        return [row.get("enumlabel") if isinstance(row, dict) else row[0] for row in rows]

    def _existing_values(self, table: str, column: str) -> list[str]:
        if not self.table_exists(table) or column not in self.columns(table):
            return []
        query = sql.SQL("SELECT DISTINCT {} FROM {} WHERE {} IS NOT NULL;").format(
            sql.Identifier(column), sql.Identifier(table), sql.Identifier(column)
        )
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        result = []
        for row in rows:
            value = row.get(column) if isinstance(row, dict) else row[0]
            if value is not None:
                result.append(str(value))
        return result

    def allowed_values(self, table: str, column: str) -> list[str]:
        key = (table, column)
        if key in self._allowed_cache:
            return self._allowed_cache[key]
        meta = self.columns(table).get(column)
        if not meta:
            return []
        values: list[str] = []
        values.extend(self._enum_values(str(meta["udt_name"])))
        values.extend(self._constraint_values(table, column))
        values.extend(self._existing_values(table, column))
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        self._allowed_cache[key] = deduped
        return deduped

    @staticmethod
    def _normalized(value: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", value.upper())

    def canonical(self, table: str, column: str, preferred: str) -> str:
        meta = self.columns(table).get(column)
        if not meta:
            return preferred

        strict: list[str] = []
        strict.extend(self._enum_values(str(meta["udt_name"])))
        strict.extend(self._constraint_values(table, column))
        strict = list(dict.fromkeys(strict))

        wanted = self._normalized(preferred)
        if strict:
            for value in strict:
                if self._normalized(value) == wanted:
                    return value
            raise RuntimeError(
                f"Cannot map {preferred!r} to allowed {table}.{column} values: {strict}"
            )

        # If the column is plain text with no database-level constraint, existing
        # values help us preserve casing but do not limit what the application can use.
        for value in self.allowed_values(table, column):
            if self._normalized(value) == wanted:
                return value
        return preferred

    def _generic_value(self, table: str, column: str, meta: dict[str, Any]) -> Any:
        self._token += 1
        token = self._token
        data_type = str(meta["data_type"])
        udt_name = str(meta["udt_name"])
        lower = column.lower()

        enum_values = self._enum_values(udt_name)
        if enum_values:
            return enum_values[0]
        if data_type == "boolean":
            return True
        if data_type in {
            "smallint", "integer", "bigint", "numeric", "decimal",
            "real", "double precision",
        }:
            return 1
        if "timestamp" in data_type:
            return datetime.now().replace(microsecond=0)
        if data_type == "date":
            return datetime.now().date()
        if data_type == "time without time zone":
            return datetime.now().time().replace(microsecond=0)
        if data_type == "uuid":
            import uuid
            return uuid.uuid4()
        if "email" in lower:
            value = f"seed{token}@acme.inc"
        elif "role" in lower:
            value = "EMPLOYEE"
        elif "status" in lower:
            allowed = self.allowed_values(table, column)
            value = allowed[0] if allowed else "OPEN"
        else:
            value = f"Seed-{token}"
        max_len = meta.get("character_maximum_length")
        if max_len:
            value = value[: int(max_len)]
        return value

    def insert(self, table: str, desired: dict[str, Any]) -> int | None:
        columns = self.columns(table)
        if not columns:
            raise RuntimeError(f"Table {table!r} does not exist or has no columns.")
        values: dict[str, Any] = {}
        for key, value in desired.items():
            if key in columns:
                values[key] = value

        for column, meta in columns.items():
            if column in values:
                continue
            has_default = meta["column_default"] is not None
            is_identity = str(meta["is_identity"]).upper() == "YES"
            nullable = str(meta["is_nullable"]).upper() == "YES"
            if has_default or is_identity or nullable:
                continue
            if column == "id":
                continue
            values[column] = self._generic_value(table, column, meta)

        names = list(values)
        placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in names)
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(", ").join(sql.Identifier(name) for name in names),
            placeholders,
        )
        if "id" in columns:
            query += sql.SQL(" RETURNING id")

        with self.connection.cursor() as cursor:
            cursor.execute(query, [values[name] for name in names])
            if "id" in columns:
                row = cursor.fetchone()
                return int(row.get("id") if isinstance(row, dict) else row[0])
        return None


def _validate_core_schema(inspector: SchemaInspector) -> None:
    required_tables = [
        "users",
        "engineer_profiles",
        "buildings",
        "floors",
        "seats",
        "incidents",
    ]
    missing = [table for table in required_tables if not inspector.table_exists(table)]
    if missing:
        raise RuntimeError(f"Missing required tables: {', '.join(missing)}")

    required_columns = {
        "users": ["id", "email", "full_name", "role"],
        "engineer_profiles": ["id", "user_id"],
        "buildings": ["id", "name"],
        "floors": ["id", "building_id", "name"],
        "seats": ["id", "floor_id", "label"],
        "incidents": [
            "id", "reporter_id", "seat_id", "title", "description",
            "category", "priority", "status",
        ],
    }
    problems = []
    for table, expected in required_columns.items():
        actual = inspector.columns(table)
        missing_cols = [column for column in expected if column not in actual]
        if missing_cols:
            problems.append(f"{table}: {', '.join(missing_cols)}")
    if problems:
        raise RuntimeError(
            "Core schema differs from the expected ACME implementation: "
            + "; ".join(problems)
        )

    password_columns = inspector.columns("users")
    if not any(name in password_columns for name in ("password_hash", "hashed_password", "password_digest")):
        raise RuntimeError("Could not find the password hash column in users.")


def _truncate_demo_data(connection: Any, inspector: SchemaInspector) -> None:
    candidates = [
        "engineer_skills",
        "skills",
        "ticket_notes",
        "status_history",
        "incidents",
        "engineer_profiles",
        "seats",
        "floors",
        "buildings",
        "users",
    ]
    tables = [table for table in candidates if inspector.table_exists(table)]
    query = sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(
        sql.SQL(", ").join(sql.Identifier(table) for table in tables)
    )
    with connection.cursor() as cursor:
        cursor.execute(query)


def _user_values(
    full_name: str,
    email: str,
    role: str,
    password_hash: str,
    now: datetime,
) -> dict[str, Any]:
    return {
        "full_name": full_name,
        "email": email,
        "role": role,
        "password_hash": password_hash,
        "hashed_password": password_hash,
        "password_digest": password_hash,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }


def _name(index: int, offset: int = 0) -> str:
    first = FIRST_NAMES[(index + offset) % len(FIRST_NAMES)]
    last = LAST_NAMES[((index * 7) + offset) % len(LAST_NAMES)]
    return f"{first} {last}"


def _seed_users(
    inspector: SchemaInspector,
    password_hash: str,
    now: datetime,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    role_admin = inspector.canonical("users", "role", "FACILITY_ADMIN")
    role_employee = inspector.canonical("users", "role", "EMPLOYEE")
    role_engineer = inspector.canonical("users", "role", "ENGINEER")

    admins: list[dict[str, Any]] = []
    employees: list[dict[str, Any]] = []
    engineers: list[dict[str, Any]] = []

    admin_specs = [
        ("Jordan Admin", "admin@acme.inc"),
        ("Morgan Reed", "tampa.admin@acme.inc"),
        ("Casey Morgan", "east.admin@acme.inc"),
        ("Riley Brooks", "central.admin@acme.inc"),
    ]
    for full_name, email in admin_specs:
        user_id = inspector.insert(
            "users",
            _user_values(full_name, email, role_admin, password_hash, now),
        )
        admins.append({"id": user_id, "full_name": full_name, "email": email})

    employee_specs = [("Taylor Employee", "employee@acme.inc")]
    employee_specs.extend(
        (_name(i, 9), f"employee{i + 2:02d}@acme.inc")
        for i in range(EMPLOYEE_COUNT - 1)
    )
    for full_name, email in employee_specs:
        user_id = inspector.insert(
            "users",
            _user_values(full_name, email, role_employee, password_hash, now),
        )
        employees.append({"id": user_id, "full_name": full_name, "email": email})

    engineer_specs = [("Alex Engineer", "engineer@acme.inc")]
    engineer_specs.extend(
        (_name(i, 37), f"engineer{i + 2:02d}@acme.inc")
        for i in range(ENGINEER_COUNT - 1)
    )
    for full_name, email in engineer_specs:
        user_id = inspector.insert(
            "users",
            _user_values(full_name, email, role_engineer, password_hash, now),
        )
        engineers.append({"user_id": user_id, "full_name": full_name, "email": email})

    return admins, employees, engineers


def _availability(inspector: SchemaInspector, preferred: str) -> str:
    if "availability" not in inspector.columns("engineer_profiles"):
        return preferred
    return inspector.canonical("engineer_profiles", "availability", preferred)


def _seed_engineers(
    inspector: SchemaInspector,
    engineers: list[dict[str, Any]],
    now: datetime,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for index, engineer in enumerate(engineers):
        if index == 0:
            specialty = "IT Support"
            skills = ["Hardware", "Networking", "AV"]
            availability = _availability(inspector, "AVAILABLE")
            ticket_limit = 8
            is_active = True
        else:
            specialty, base_skills = SPECIALTY_SKILLS[(index - 1) % len(SPECIALTY_SKILLS)]
            skills = list(base_skills)
            extra = SKILL_NAMES[(index * 3) % len(SKILL_NAMES)]
            if extra not in skills and len(skills) < 4:
                skills.append(extra)
            if index in {14, 29}:
                availability = _availability(inspector, "OFFLINE")
            elif index % 5 == 0:
                availability = _availability(inspector, "BUSY")
            else:
                availability = _availability(inspector, "AVAILABLE")
            ticket_limit = 5 + (index % 4)
            is_active = index != 28

        desired = {
            "user_id": engineer["user_id"],
            "specialty": specialty,
            "availability": availability,
            "ticket_limit": ticket_limit,
            "capacity": ticket_limit,
            "max_tickets": ticket_limit,
            "is_active": is_active,
            "created_at": now,
            "updated_at": now,
        }
        profile_id = inspector.insert("engineer_profiles", desired)
        result.append(
            {
                **engineer,
                "id": profile_id,
                "specialty": specialty,
                "availability": availability,
                "ticket_limit": ticket_limit,
                "is_active": is_active,
                "skills": skills,
                "active_count": 0,
            }
        )

    return result


def _seed_skills(inspector: SchemaInspector, engineers: list[dict[str, Any]]) -> None:
    if not inspector.table_exists("skills") or not inspector.table_exists("engineer_skills"):
        print("Skills tables are not present; skipping skill assignments.")
        return

    skill_ids: dict[str, int] = {}
    for skill in SKILL_NAMES:
        skill_id = inspector.insert("skills", {"name": skill})
        if skill_id is None:
            raise RuntimeError("skills.id is required for engineer skill assignments.")
        skill_ids[skill] = skill_id

    for engineer in engineers:
        for skill in engineer["skills"]:
            inspector.insert(
                "engineer_skills",
                {
                    "engineer_id": engineer["id"],
                    "skill_id": skill_ids[skill],
                },
            )


def _seed_facilities(inspector: SchemaInspector, now: datetime) -> list[dict[str, Any]]:
    seats: list[dict[str, Any]] = []
    floor_letters = ["A", "B", "C"]

    for building_index, spec in enumerate(BUILDINGS):
        building_id = inspector.insert(
            "buildings",
            {
                **spec,
                "code": f"BLD-{building_index + 1:02d}",
                "country": "US",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        )
        for floor_number in range(1, 4):
            floor_name = f"Floor {floor_number}"
            floor_id = inspector.insert(
                "floors",
                {
                    "building_id": building_id,
                    "name": floor_name,
                    "floor_number": floor_number,
                    "number": floor_number,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                },
            )
            letter = floor_letters[floor_number - 1]
            for seat_number in range(1, 16):
                numeric = (floor_number * 100) + seat_number
                label = f"{letter}-{numeric}"
                seat_id = inspector.insert(
                    "seats",
                    {
                        "floor_id": floor_id,
                        "label": label,
                        "name": label,
                        "seat_number": label,
                        "is_active": True,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
                seats.append(
                    {
                        "id": seat_id,
                        "building_id": building_id,
                        "building_name": spec["name"],
                        "floor_id": floor_id,
                        "floor_name": floor_name,
                        "label": label,
                    }
                )

    return seats


def _is_offline(value: str) -> bool:
    return "OFFLINE" in re.sub(r"[^A-Z]", "", str(value).upper())


def _choose_engineer(
    engineers: list[dict[str, Any]],
    category: str,
    active_ticket: bool,
) -> dict[str, Any]:
    required = CATEGORY_SKILLS[category]
    candidates = [
        engineer
        for engineer in engineers
        if engineer["is_active"]
        and not _is_offline(engineer["availability"])
        and required.intersection(engineer["skills"])
        and (
            not active_ticket
            or engineer["active_count"] < engineer["ticket_limit"]
        )
    ]
    if not candidates:
        candidates = [
            engineer
            for engineer in engineers
            if engineer["is_active"]
            and not _is_offline(engineer["availability"])
            and (
                not active_ticket
                or engineer["active_count"] < engineer["ticket_limit"]
            )
        ]
    if not candidates:
        raise RuntimeError("No engineer is available under capacity for incident assignment.")

    candidates.sort(key=lambda item: (item["active_count"], item["id"]))
    lowest = candidates[0]["active_count"]
    pool = [item for item in candidates if item["active_count"] <= lowest + 1]
    chosen = RNG.choice(pool)
    if active_ticket:
        chosen["active_count"] += 1
    return chosen


def _incident_statuses(inspector: SchemaInspector) -> list[str]:
    desired = (
        ["OPEN"] * 25
        + ["IN_PROGRESS"] * 30
        + ["BLOCKED"] * 10
        + ["RESOLVED"] * 20
        + ["CLOSED"] * 15
    )
    values = [inspector.canonical("incidents", "status", value) for value in desired]
    RNG.shuffle(values)
    return values


def _incident_priorities(inspector: SchemaInspector) -> list[str]:
    desired = ["LOW"] * 30 + ["MEDIUM"] * 45 + ["HIGH"] * 25
    values = [inspector.canonical("incidents", "priority", value) for value in desired]
    RNG.shuffle(values)
    return values


def _status_key(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "_", value.upper()).strip("_")


def _seed_status_history(
    inspector: SchemaInspector,
    incident: dict[str, Any],
    reporter_id: int,
    engineer_user_id: int | None,
    created_at: datetime,
    assigned_at: datetime | None,
    acknowledged_at: datetime | None,
    resolved_at: datetime | None,
    closed_at: datetime | None,
) -> None:
    if not inspector.table_exists("status_history"):
        return

    open_value = inspector.canonical("incidents", "status", "OPEN")
    in_progress = inspector.canonical("incidents", "status", "IN_PROGRESS")
    blocked = inspector.canonical("incidents", "status", "BLOCKED")
    resolved = inspector.canonical("incidents", "status", "RESOLVED")
    closed = inspector.canonical("incidents", "status", "CLOSED")
    target = _status_key(str(incident["status"]))

    history_columns = inspector.columns("status_history")
    old_meta = history_columns.get("old_status")
    initial_old = None
    if old_meta and str(old_meta.get("is_nullable", "YES")).upper() != "YES":
        initial_old = open_value

    events: list[tuple[str | None, str, int, datetime, str]] = [
        (initial_old, open_value, reporter_id, created_at, "Incident reported."),
    ]

    actor = engineer_user_id or reporter_id
    if target in {"IN_PROGRESS", "BLOCKED", "RESOLVED", "CLOSED"}:
        events.append(
            (
                open_value,
                in_progress,
                actor,
                acknowledged_at or assigned_at or (created_at + timedelta(minutes=20)),
                "Engineer began investigation.",
            )
        )
    if target == "BLOCKED":
        events.append(
            (
                in_progress,
                blocked,
                actor,
                (acknowledged_at or created_at) + timedelta(hours=2),
                incident["blocked_reason"] or "Work is temporarily blocked.",
            )
        )
    if target in {"RESOLVED", "CLOSED"}:
        events.append(
            (
                in_progress,
                resolved,
                actor,
                resolved_at or (created_at + timedelta(hours=8)),
                "Issue resolved after remediation and verification.",
            )
        )
    if target == "CLOSED":
        events.append(
            (
                resolved,
                closed,
                reporter_id,
                closed_at or (resolved_at or created_at) + timedelta(hours=4),
                "Reporter confirmed resolution and closed the incident.",
            )
        )

    for old_status, new_status, changed_by, event_time, reason in events:
        inspector.insert(
            "status_history",
            {
                "incident_id": incident["id"],
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "changed_by_id": changed_by,
                "changed_by_user_id": changed_by,
                "user_id": changed_by,
                "reason": reason,
                "notes": reason,
                "created_at": event_time,
                "updated_at": event_time,
            },
        )


def _seed_note(
    inspector: SchemaInspector,
    incident_id: int,
    author_id: int,
    text: str,
    created_at: datetime,
) -> None:
    if not inspector.table_exists("ticket_notes"):
        return
    inspector.insert(
        "ticket_notes",
        {
            "incident_id": incident_id,
            "author_id": author_id,
            "author_user_id": author_id,
            "user_id": author_id,
            "created_by": author_id,
            "created_by_id": author_id,
            "content": text,
            "body": text,
            "note": text,
            "note_text": text,
            "message": text,
            "text": text,
            "created_at": created_at,
            "updated_at": created_at,
        },
    )


def _seed_incidents(
    inspector: SchemaInspector,
    employees: list[dict[str, Any]],
    engineers: list[dict[str, Any]],
    seats: list[dict[str, Any]],
    now: datetime,
) -> list[dict[str, Any]]:
    statuses = _incident_statuses(inspector)
    priorities = _incident_priorities(inspector)
    categories = list(CATEGORY_SKILLS)

    none_escalation = inspector.canonical("incidents", "escalation_status", "NONE") \
        if "escalation_status" in inspector.columns("incidents") else "NONE"
    pending_escalation = inspector.canonical("incidents", "escalation_status", "PENDING") \
        if "escalation_status" in inspector.columns("incidents") else "PENDING"
    approved_escalation = inspector.canonical("incidents", "escalation_status", "APPROVED") \
        if "escalation_status" in inspector.columns("incidents") else "APPROVED"
    declined_escalation = inspector.canonical("incidents", "escalation_status", "DECLINED") \
        if "escalation_status" in inspector.columns("incidents") else "DECLINED"

    active_indices = [
        index for index, status in enumerate(statuses)
        if _status_key(status) in {"OPEN", "IN_PROGRESS", "BLOCKED"}
    ]
    RNG.shuffle(active_indices)
    pending_indices = set(active_indices[:4])
    remaining = [index for index in range(INCIDENT_COUNT) if index not in pending_indices]
    RNG.shuffle(remaining)
    approved_indices = set(remaining[:4])
    declined_indices = set(remaining[4:8])

    tampa_hotspot = next(
        seat
        for seat in seats
        if seat["building_name"] == "Tampa Operations Center"
        and seat["floor_name"] == "Floor 1"
        and seat["label"] == "A-101"
    )
    second_hotspot = next(
        seat for seat in seats
        if seat["building_name"] == "New York Corporate Office"
        and seat["floor_name"] == "Floor 2"
        and seat["label"] == "B-205"
    )

    incidents: list[dict[str, Any]] = []

    for index in range(INCIDENT_COUNT):
        status = statuses[index]
        status_key = _status_key(status)
        priority = priorities[index]
        category = categories[index % len(categories)]
        template = INCIDENT_TEMPLATES[category]
        title, description = template[(index // len(categories)) % len(template)]

        if index < 12:
            seat = tampa_hotspot
        elif index < 19:
            seat = second_hotspot
        else:
            seat = RNG.choice(seats)

        reporter = employees[index % len(employees)]
        created_at = now - timedelta(
            days=RNG.randint(0, 89),
            hours=RNG.randint(0, 20),
            minutes=RNG.randint(0, 59),
        )

        should_assign = status_key != "OPEN" or index % 3 != 0
        active_ticket = status_key in {"OPEN", "IN_PROGRESS", "BLOCKED"}
        engineer: dict[str, Any] | None = None
        assigned_at = None
        acknowledged_at = None
        resolved_at = None
        closed_at = None

        if should_assign:
            engineer = _choose_engineer(engineers, category, active_ticket)
            assigned_at = created_at + timedelta(minutes=RNG.randint(8, 95))

        if status_key in {"IN_PROGRESS", "BLOCKED", "RESOLVED", "CLOSED"}:
            acknowledged_at = (assigned_at or created_at) + timedelta(minutes=RNG.randint(5, 35))

        if status_key in {"RESOLVED", "CLOSED"}:
            resolved_at = (acknowledged_at or created_at) + timedelta(hours=RNG.randint(2, 48))

        if status_key == "CLOSED":
            closed_at = (resolved_at or created_at) + timedelta(hours=RNG.randint(1, 30))

        latest_time = closed_at or resolved_at or acknowledged_at or assigned_at or created_at
        if latest_time > now:
            shift = latest_time - now + timedelta(minutes=15)
            created_at -= shift
            if assigned_at:
                assigned_at -= shift
            if acknowledged_at:
                acknowledged_at -= shift
            if resolved_at:
                resolved_at -= shift
            if closed_at:
                closed_at -= shift
            latest_time -= shift

        blocked_reason = RNG.choice(BLOCKED_REASONS) if status_key == "BLOCKED" else None

        if index in pending_indices:
            escalation_status = pending_escalation
        elif index in approved_indices:
            escalation_status = approved_escalation
        elif index in declined_indices:
            escalation_status = declined_escalation
        else:
            escalation_status = none_escalation
        escalation_reason = (
            RNG.choice(ESCALATION_REASONS)
            if index in pending_indices | approved_indices | declined_indices
            else None
        )

        desired = {
            "ticket_reference": f"INC-{index + 1:06d}",
            "reporter_id": reporter["id"],
            "employee_id": reporter["id"],
            "seat_id": seat["id"],
            "engineer_id": engineer["id"] if engineer else None,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": status,
            "blocked_reason": blocked_reason,
            "escalation_status": escalation_status,
            "escalation_reason": escalation_reason,
            "is_escalated": escalation_status != none_escalation,
            "created_at": created_at,
            "updated_at": latest_time,
            "assigned_at": assigned_at,
            "acknowledged_at": acknowledged_at,
            "acknowledged_on": acknowledged_at,
            "resolved_at": resolved_at,
            "closed_at": closed_at,
        }
        incident_id = inspector.insert("incidents", desired)
        if incident_id is None:
            raise RuntimeError("incidents.id is required by the ACME application.")

        incident = {
            "id": incident_id,
            "status": status,
            "category": category,
            "reporter": reporter,
            "engineer": engineer,
            "blocked_reason": blocked_reason,
            "escalation_status": escalation_status,
            "seat": seat,
            "created_at": created_at,
        }
        incidents.append(incident)

        _seed_status_history(
            inspector,
            incident,
            reporter["id"],
            engineer["user_id"] if engineer else None,
            created_at,
            assigned_at,
            acknowledged_at,
            resolved_at,
            closed_at,
        )

        if index % 2 == 0:
            _seed_note(
                inspector,
                incident_id,
                reporter["id"],
                "Issue details confirmed. Please use this ticket for updates.",
                created_at + timedelta(minutes=10),
            )
        if engineer and index % 3 == 0:
            _seed_note(
                inspector,
                incident_id,
                engineer["user_id"],
                "Initial diagnostics completed and remediation is in progress.",
                (acknowledged_at or assigned_at or created_at) + timedelta(minutes=20),
            )
        if status_key == "BLOCKED":
            _seed_note(
                inspector,
                incident_id,
                engineer["user_id"] if engineer else reporter["id"],
                blocked_reason or "Work is temporarily blocked.",
                (acknowledged_at or created_at) + timedelta(hours=2),
            )

    return incidents


def _scalar(connection: Any, query: Any, params: tuple[Any, ...] = ()) -> Any:
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()
    if isinstance(row, dict):
        return next(iter(row.values()))
    return row[0]


def _print_summary(connection: Any, inspector: SchemaInspector) -> None:
    print("\nSeed complete. Database summary:")
    print("-" * 54)
    with connection.cursor() as cursor:
        cursor.execute("SELECT role, COUNT(*) AS count FROM users GROUP BY role ORDER BY role;")
        rows = SchemaInspector._dict_rows(cursor)
    for row in rows:
        print(f"users {row['role']:<18} {row['count']}")

    for table in ("engineer_profiles", "buildings", "floors", "seats", "incidents"):
        count = _scalar(connection, sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(table)))
        print(f"{table:<24} {count}")

    if inspector.table_exists("skills"):
        count = _scalar(connection, "SELECT COUNT(*) FROM skills;")
        print(f"{'skills':<24} {count}")
    if inspector.table_exists("engineer_skills"):
        count = _scalar(connection, "SELECT COUNT(*) FROM engineer_skills;")
        print(f"{'engineer_skills':<24} {count}")

    print("\nIncident statuses:")
    with connection.cursor() as cursor:
        cursor.execute("SELECT status, COUNT(*) AS count FROM incidents GROUP BY status ORDER BY status;")
        rows = SchemaInspector._dict_rows(cursor)
    for row in rows:
        print(f"  {row['status']:<16} {row['count']}")

    print("\nDemo logins (all use AcmeDemo123!):")
    print("  admin@acme.inc")
    print("  employee@acme.inc")
    print("  engineer@acme.inc  (Alex Engineer)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed realistic ACME demo data.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Required because this replaces the current demo data.",
    )
    args = parser.parse_args()

    if not args.apply:
        raise SystemExit(
            "Refusing to modify the database without --apply.\n"
            "Run: python seed_realistic_acme.py --apply"
        )

    connection = get_connection()
    inspector = SchemaInspector(connection)

    database_name = _scalar(connection, "SELECT current_database();")
    print(f"Connected database: {database_name}")
    print(
        "Target dataset: 4 admins, 50 employees, 30 engineers, "
        "4 buildings, 12 floors, 180 seats, 100 incidents"
    )

    _validate_core_schema(inspector)

    # Cache constrained values before existing rows are removed.
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
        PASSWORD.encode("utf-8"),
        bcrypt.gensalt(rounds=10),
    ).decode("utf-8")
    now = datetime.now().replace(microsecond=0)

    try:
        _truncate_demo_data(connection, inspector)
        admins, employees, engineer_users = _seed_users(inspector, password_hash, now)
        engineers = _seed_engineers(inspector, engineer_users, now)
        _seed_skills(inspector, engineers)
        seats = _seed_facilities(inspector, now)
        incidents = _seed_incidents(inspector, employees, engineers, seats, now)

        if len(admins) != ADMIN_COUNT:
            raise RuntimeError(f"Expected {ADMIN_COUNT} admins, created {len(admins)}.")
        if len(employees) != EMPLOYEE_COUNT:
            raise RuntimeError(f"Expected {EMPLOYEE_COUNT} employees, created {len(employees)}.")
        if len(engineers) != ENGINEER_COUNT:
            raise RuntimeError(f"Expected {ENGINEER_COUNT} engineers, created {len(engineers)}.")
        if len(incidents) != INCIDENT_COUNT:
            raise RuntimeError(f"Expected {INCIDENT_COUNT} incidents, created {len(incidents)}.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise

    _print_summary(connection, inspector)


if __name__ == "__main__":
    main()

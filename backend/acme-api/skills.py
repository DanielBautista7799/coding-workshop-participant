from permissions import require_role
from postgres_service import get_connection


MAX_SKILLS_PER_ENGINEER = 8


def list_skills(user):
    """Return the available engineer skill catalog."""
    require_role(user, "FACILITY_ADMIN")

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name
            FROM skills
            ORDER BY name
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def list_engineer_skills(user):
    """Return each engineer profile with its assigned skill names."""
    require_role(user, "FACILITY_ADMIN")

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                ep.id AS engineer_id,
                s.name
            FROM engineer_profiles ep
            LEFT JOIN engineer_skills es
                ON es.engineer_id = ep.id
            LEFT JOIN skills s
                ON s.id = es.skill_id
            ORDER BY ep.id, s.name
            """
        )
        rows = cursor.fetchall()

    grouped = {}

    for row in rows:
        engineer_id = row["engineer_id"]
        grouped.setdefault(engineer_id, [])

        if row["name"]:
            grouped[engineer_id].append(row["name"])

    return [
        {
            "engineer_id": engineer_id,
            "skills": skill_names,
        }
        for engineer_id, skill_names in grouped.items()
    ]


def update_engineer_skills(engineer_id, payload, user):
    """Replace the complete skill set for one engineer."""
    require_role(user, "FACILITY_ADMIN")

    raw_skills = payload.get("skills")

    if not isinstance(raw_skills, list):
        raise ValueError("skills must be a list")

    cleaned = []

    for value in raw_skills:
        if not isinstance(value, str):
            raise ValueError("Each skill must be a string")

        name = value.strip()

        if name and name not in cleaned:
            cleaned.append(name)

    if len(cleaned) > MAX_SKILLS_PER_ENGINEER:
        raise ValueError(
            f"An engineer can have at most "
            f"{MAX_SKILLS_PER_ENGINEER} skills"
        )

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM engineer_profiles
                WHERE id = %s
                """,
                (engineer_id,),
            )

            if cursor.fetchone() is None:
                raise LookupError("Engineer not found")

            skill_ids = {}

            if cleaned:
                cursor.execute(
                    """
                    SELECT id, name
                    FROM skills
                    WHERE name = ANY(%s)
                    """,
                    (cleaned,),
                )

                for row in cursor.fetchall():
                    skill_ids[row["name"]] = row["id"]

                unknown = [
                    name
                    for name in cleaned
                    if name not in skill_ids
                ]

                if unknown:
                    raise ValueError(
                        "Unknown skills: " + ", ".join(unknown)
                    )

            cursor.execute(
                """
                DELETE FROM engineer_skills
                WHERE engineer_id = %s
                """,
                (engineer_id,),
            )

            if cleaned:
                cursor.executemany(
                    """
                    INSERT INTO engineer_skills (
                        engineer_id,
                        skill_id
                    )
                    VALUES (%s, %s)
                    """,
                    [
                        (engineer_id, skill_ids[name])
                        for name in cleaned
                    ],
                )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    return {
        "engineer_id": engineer_id,
        "skills": sorted(cleaned),
    }

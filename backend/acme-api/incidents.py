"""Handles the full incident workflow and permissions: employees create/manage their own incidents,
request escalation, add notes, and close resolved tickets; engineers manage assigned incidents and notes; 
admins can view/manage all incidents, assign engineers, review escalations, and manage notes/history."""

from engineers import get_engineer
from facilities import get_seat
from permissions import is_admin, is_employee, is_engineer
from postgres_service import get_connection


VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}

VALID_STATUSES = {
    "OPEN",
    "IN_PROGRESS",
    "BLOCKED",
    "RESOLVED",
    "CLOSED",
}


STATUS_TRANSITIONS = {
    "OPEN": {"IN_PROGRESS"},
    "IN_PROGRESS": {"BLOCKED", "RESOLVED"},
    "BLOCKED": {"IN_PROGRESS", "RESOLVED"},
    "RESOLVED": {"CLOSED"},
    "CLOSED": set(),
}


def _required_text(data: dict, field: str) -> str:
    """Return a required text value."""
    value = str(data.get(field, "")).strip()

    if not value:
        raise ValueError(
            f"{field.replace('_', ' ').title()} is required."
        )

    return value


def _required_id(data: dict, field: str) -> int:
    """Return a required integer ID."""
    try:
        return int(data.get(field))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Valid {field.replace('_', ' ')} is required."
        ) from exc


def _can_view_incident(user: dict, incident: dict) -> bool:
    """Check whether a user can view an incident."""
    if is_admin(user):
        return True

    if is_employee(user):
        return incident["reporter_id"] == user["id"]

    if is_engineer(user):
        return incident["engineer_user_id"] == user["id"]

    return False


# INCIDENT READ


def list_incidents(
    user: dict,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    search: str | None = None,
) -> list:
    """Return incidents visible to the current user with optional filters."""
    connection = get_connection()

    query = """
        SELECT
            incidents.id,
            'INC-' || LPAD(incidents.id::text, 6, '0')
                AS ticket_reference,
            incidents.title,
            incidents.description,
            incidents.category,
            incidents.priority,
            incidents.status,
            incidents.reporter_id,
            reporter.full_name AS reporter_name,
            incidents.engineer_id,
            engineer_user.id AS engineer_user_id,
            engineer_user.full_name AS engineer_name,
            incidents.seat_id,
            seats.label AS seat_label,
            floors.id AS floor_id,
            floors.name AS floor_name,
            buildings.id AS building_id,
            buildings.name AS building_name,
            incidents.blocked_reason,
            incidents.escalation_status,
            incidents.escalation_reason,
            incidents.created_at,
            incidents.updated_at,
            incidents.assigned_at,
            incidents.acknowledged_at,
            incidents.resolved_at,
            incidents.closed_at
        FROM incidents
        JOIN users AS reporter
            ON reporter.id = incidents.reporter_id
        JOIN seats
            ON seats.id = incidents.seat_id
        JOIN floors
            ON floors.id = seats.floor_id
        JOIN buildings
            ON buildings.id = floors.building_id
        LEFT JOIN engineer_profiles
            ON engineer_profiles.id = incidents.engineer_id
        LEFT JOIN users AS engineer_user
            ON engineer_user.id = engineer_profiles.user_id
        WHERE 1 = 1
    """

    values = []

    if is_employee(user):
        query += " AND incidents.reporter_id = %s"
        values.append(user["id"])

    elif is_engineer(user):
        query += """
            AND incidents.engineer_id = (
                SELECT id
                FROM engineer_profiles
                WHERE user_id = %s
            )
        """
        values.append(user["id"])

    elif not is_admin(user):
        raise PermissionError("You do not have permission to view incidents.")

    if status:
        status = status.upper()

        if status not in VALID_STATUSES:
            raise ValueError("Invalid incident status.")

        query += " AND incidents.status = %s"
        values.append(status)

    if priority:
        priority = priority.upper()

        if priority not in VALID_PRIORITIES:
            raise ValueError("Invalid incident priority.")

        query += " AND incidents.priority = %s"
        values.append(priority)

    if category:
        query += " AND LOWER(incidents.category) = LOWER(%s)"
        values.append(category.strip())

    if search:
        search_value = f"%{search.strip()}%"

        query += """
            AND (
                incidents.title ILIKE %s
                OR incidents.description ILIKE %s
                OR incidents.category ILIKE %s
            )
        """

        values.extend(
            [
                search_value,
                search_value,
                search_value,
            ]
        )

    query += " ORDER BY incidents.created_at DESC;"

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        return cursor.fetchall()


def get_incident(incident_id: int, user: dict) -> dict:
    """Return one incident when the user has access."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                incidents.id,
                'INC-' || LPAD(incidents.id::text, 6, '0')
                    AS ticket_reference,
                incidents.title,
                incidents.description,
                incidents.category,
                incidents.priority,
                incidents.status,
                incidents.reporter_id,
                reporter.full_name AS reporter_name,
                reporter.email AS reporter_email,
                incidents.engineer_id,
                engineer_user.id AS engineer_user_id,
                engineer_user.full_name AS engineer_name,
                engineer_profiles.specialty AS engineer_specialty,
                incidents.seat_id,
                seats.label AS seat_label,
                floors.id AS floor_id,
                floors.name AS floor_name,
                buildings.id AS building_id,
                buildings.name AS building_name,
                incidents.blocked_reason,
                incidents.escalation_status,
                incidents.escalation_reason,
                incidents.created_at,
                incidents.updated_at,
                incidents.assigned_at,
                incidents.acknowledged_at,
                incidents.resolved_at,
                incidents.closed_at
            FROM incidents
            JOIN users AS reporter
                ON reporter.id = incidents.reporter_id
            JOIN seats
                ON seats.id = incidents.seat_id
            JOIN floors
                ON floors.id = seats.floor_id
            JOIN buildings
                ON buildings.id = floors.building_id
            LEFT JOIN engineer_profiles
                ON engineer_profiles.id = incidents.engineer_id
            LEFT JOIN users AS engineer_user
                ON engineer_user.id = engineer_profiles.user_id
            WHERE incidents.id = %s;
            """,
            (incident_id,),
        )

        incident = cursor.fetchone()

    if incident is None:
        raise LookupError("Incident not found.")

    if not _can_view_incident(user, incident):
        raise PermissionError(
            "You do not have permission to view this incident."
        )

    return incident


# INCIDENT CRUD



def create_incident(data: dict, user: dict) -> dict:
    """Create an incident for the logged-in employee."""
    if not is_employee(user):
        raise PermissionError(
            "Only employees can report new incidents."
        )

    title = _required_text(data, "title")
    description = _required_text(data, "description")
    category = _required_text(data, "category")

    priority = _required_text(data, "priority").upper()

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            "Priority must be LOW, MEDIUM, or HIGH."
        )

    seat_id = _required_id(data, "seat_id")

    get_seat(seat_id)

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO incidents (
                title,
                description,
                category,
                priority,
                status,
                reporter_id,
                seat_id
            )
            VALUES (%s, %s, %s, %s, 'OPEN', %s, %s)
            RETURNING id;
            """,
            (
                title,
                description,
                category,
                priority,
                user["id"],
                seat_id,
            ),
        )

        incident = cursor.fetchone()

        cursor.execute(
            """
            INSERT INTO status_history (
                incident_id,
                changed_by_id,
                old_status,
                new_status
            )
            VALUES (%s, %s, NULL, 'OPEN');
            """,
            (
                incident["id"],
                user["id"],
            ),
        )

    connection.commit()

    return get_incident(
        incident["id"],
        user,
    )


def update_incident(
    incident_id: int,
    data: dict,
    user: dict,
) -> dict:
    """Update the basic details of an incident."""
    current = get_incident(
        incident_id,
        user,
    )

    if is_employee(user):
        if current["reporter_id"] != user["id"]:
            raise PermissionError(
                "You can only edit your own incidents."
            )

        if current["status"] != "OPEN":
            raise PermissionError(
                "An employee can only edit an incident while it is open."
            )

    elif not is_admin(user):
        raise PermissionError(
            "You do not have permission to edit this incident."
        )

    title = str(
        data.get("title", current["title"])
    ).strip()

    description = str(
        data.get("description", current["description"])
    ).strip()

    category = str(
        data.get("category", current["category"])
    ).strip()

    priority = str(
        data.get("priority", current["priority"])
    ).strip().upper()

    if not title:
        raise ValueError("Title is required.")

    if not description:
        raise ValueError("Description is required.")

    if not category:
        raise ValueError("Category is required.")

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            "Priority must be LOW, MEDIUM, or HIGH."
        )

    try:
        seat_id = int(
            data.get("seat_id", current["seat_id"])
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Valid seat ID is required.") from exc

    get_seat(seat_id)

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE incidents
            SET title = %s,
                description = %s,
                category = %s,
                priority = %s,
                seat_id = %s,
                updated_at = NOW()
            WHERE id = %s;
            """,
            (
                title,
                description,
                category,
                priority,
                seat_id,
                incident_id,
            ),
        )

    connection.commit()

    return get_incident(
        incident_id,
        user,
    )


def delete_incident(
    incident_id: int,
    user: dict,
) -> None:
    """Delete an incident when the user is allowed."""
    incident = get_incident(
        incident_id,
        user,
    )

    if is_employee(user):
        if incident["reporter_id"] != user["id"]:
            raise PermissionError(
                "You can only delete your own incidents."
            )

        if (
            incident["status"] != "OPEN"
            or incident["engineer_id"] is not None
        ):
            raise PermissionError(
                "An employee can only delete an open, unassigned incident."
            )

    elif not is_admin(user):
        raise PermissionError(
            "You do not have permission to delete this incident."
        )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM incidents
            WHERE id = %s;
            """,
            (incident_id,),
        )

    connection.commit()



# ENGINEER ASSIGNMENT


def assign_engineer(
    incident_id: int,
    engineer_id: int,
    user: dict,
) -> dict:
    """Assign an active engineer to an incident."""
    if not is_admin(user):
        raise PermissionError(
            "Only Facility Admins can assign engineers."
        )

    incident = get_incident(
        incident_id,
        user,
    )

    if incident["status"] == "CLOSED":
        raise ValueError(
            "A closed incident cannot be assigned."
        )

    engineer = get_engineer(engineer_id)

    if not engineer["is_active"]:
        raise ValueError(
            "Inactive engineers cannot receive assignments."
        )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE incidents
            SET engineer_id = %s,
                assigned_at = NOW(),
                updated_at = NOW()
            WHERE id = %s;
            """,
            (
                engineer_id,
                incident_id,
            ),
        )

    connection.commit()

    return get_incident(
        incident_id,
        user,
    )


#
# STATUS WORKFLOW



def update_incident_status(
    incident_id: int,
    new_status: str,
    user: dict,
    blocked_reason: str | None = None,
) -> dict:
    """Move an incident through the allowed status workflow."""
    incident = get_incident(
        incident_id,
        user,
    )

    new_status = new_status.strip().upper()

    if new_status not in VALID_STATUSES:
        raise ValueError("Invalid incident status.")

    current_status = incident["status"]

    # Employees are only allowed to close their own resolved incident.
    if is_employee(user):
        if (
            incident["reporter_id"] != user["id"]
            or current_status != "RESOLVED"
            or new_status != "CLOSED"
        ):
            raise PermissionError(
                "Employees can only close their own resolved incidents."
            )

    else:
        if is_engineer(user):
            if incident["engineer_user_id"] != user["id"]:
                raise PermissionError(
                    "Engineers can only update incidents assigned to them."
                )

        elif not is_admin(user):
            raise PermissionError(
                "You do not have permission to update incident status."
            )

        if new_status not in STATUS_TRANSITIONS[current_status]:
            raise ValueError(
                f"Incident cannot move from "
                f"{current_status} to {new_status}."
            )

    if (
        new_status in {"IN_PROGRESS", "BLOCKED", "RESOLVED"}
        and incident["engineer_id"] is None
    ):
        raise ValueError(
            "Assign an engineer before progressing this incident."
        )

    reason = None

    if new_status == "BLOCKED":
        reason = str(blocked_reason or "").strip()

        if not reason:
            raise ValueError(
                "A blocked reason is required."
            )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE incidents
            SET status = %s,
                blocked_reason = %s,
                updated_at = NOW(),

                acknowledged_at =
                    CASE
                        WHEN %s = 'IN_PROGRESS'
                        THEN COALESCE(acknowledged_at, NOW())
                        ELSE acknowledged_at
                    END,

                resolved_at =
                    CASE
                        WHEN %s = 'RESOLVED'
                        THEN NOW()
                        ELSE resolved_at
                    END,

                closed_at =
                    CASE
                        WHEN %s = 'CLOSED'
                        THEN NOW()
                        ELSE closed_at
                    END

            WHERE id = %s;
            """,
            (
                new_status,
                reason,
                new_status,
                new_status,
                new_status,
                incident_id,
            ),
        )

        cursor.execute(
            """
            INSERT INTO status_history (
                incident_id,
                changed_by_id,
                old_status,
                new_status
            )
            VALUES (%s, %s, %s, %s);
            """,
            (
                incident_id,
                user["id"],
                current_status,
                new_status,
            ),
        )

    connection.commit()

    return get_incident(
        incident_id,
        user,
    )


def get_status_history(
    incident_id: int,
    user: dict,
) -> list:
    """Return the status history for an incident."""
    get_incident(
        incident_id,
        user,
    )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                status_history.id,
                status_history.old_status,
                status_history.new_status,
                status_history.created_at,
                users.id AS changed_by_id,
                users.full_name AS changed_by_name
            FROM status_history
            JOIN users
                ON users.id = status_history.changed_by_id
            WHERE status_history.incident_id = %s
            ORDER BY status_history.created_at;
            """,
            (incident_id,),
        )

        return cursor.fetchall()



# ESCALATION



def request_escalation(
    incident_id: int,
    reason: str,
    user: dict,
) -> dict:
    """Allow an employee to request escalation of their incident."""
    if not is_employee(user):
        raise PermissionError(
            "Only employees can request an escalation."
        )

    incident = get_incident(
        incident_id,
        user,
    )

    if incident["reporter_id"] != user["id"]:
        raise PermissionError(
            "You can only escalate your own incident."
        )

    if incident["status"] == "CLOSED":
        raise ValueError(
            "A closed incident cannot be escalated."
        )

    if incident["escalation_status"] in {
        "PENDING",
        "APPROVED",
    }:
        raise ValueError(
            "This incident already has an active escalation."
        )

    reason = reason.strip()

    if not reason:
        raise ValueError(
            "Escalation reason is required."
        )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE incidents
            SET escalation_status = 'PENDING',
                escalation_reason = %s,
                updated_at = NOW()
            WHERE id = %s;
            """,
            (
                reason,
                incident_id,
            ),
        )

    connection.commit()

    return get_incident(
        incident_id,
        user,
    )


def review_escalation(
    incident_id: int,
    decision: str,
    user: dict,
) -> dict:
    """Allow a Facility Admin to approve or decline an escalation."""
    if not is_admin(user):
        raise PermissionError(
            "Only Facility Admins can review escalations."
        )

    incident = get_incident(
        incident_id,
        user,
    )

    if incident["escalation_status"] != "PENDING":
        raise ValueError(
            "This incident does not have a pending escalation."
        )

    decision = decision.strip().upper()

    if decision not in {"APPROVED", "DECLINED"}:
        raise ValueError(
            "Escalation decision must be APPROVED or DECLINED."
        )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE incidents
            SET escalation_status = %s,
                updated_at = NOW()
            WHERE id = %s;
            """,
            (
                decision,
                incident_id,
            ),
        )

    connection.commit()

    return get_incident(
        incident_id,
        user,
    )


# TICKET NOTES



def list_notes(
    incident_id: int,
    user: dict,
) -> list:
    """Return notes for an incident."""
    get_incident(
        incident_id,
        user,
    )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                ticket_notes.id,
                ticket_notes.incident_id,
                ticket_notes.author_id,
                users.full_name AS author_name,
                users.role AS author_role,
                ticket_notes.body,
                ticket_notes.created_at,
                ticket_notes.updated_at
            FROM ticket_notes
            JOIN users
                ON users.id = ticket_notes.author_id
            WHERE ticket_notes.incident_id = %s
            ORDER BY ticket_notes.created_at;
            """,
            (incident_id,),
        )

        return cursor.fetchall()


def create_note(
    incident_id: int,
    data: dict,
    user: dict,
) -> dict:
    """Add a note to an incident."""
    get_incident(
        incident_id,
        user,
    )

    body = _required_text(
        data,
        "body",
    )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO ticket_notes (
                incident_id,
                author_id,
                body
            )
            VALUES (%s, %s, %s)
            RETURNING
                id,
                incident_id,
                author_id,
                body,
                created_at,
                updated_at;
            """,
            (
                incident_id,
                user["id"],
                body,
            ),
        )

        note = cursor.fetchone()

    connection.commit()

    return note


def _get_note(note_id: int) -> dict:
    """Return a ticket note."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                author_id,
                body,
                created_at,
                updated_at
            FROM ticket_notes
            WHERE id = %s;
            """,
            (note_id,),
        )

        note = cursor.fetchone()

    if note is None:
        raise LookupError("Ticket note not found.")

    return note


def update_note(
    note_id: int,
    data: dict,
    user: dict,
) -> dict:
    """Update a note written by the user or managed by an admin."""
    note = _get_note(note_id)

    get_incident(
        note["incident_id"],
        user,
    )

    if (
        note["author_id"] != user["id"]
        and not is_admin(user)
    ):
        raise PermissionError(
            "You can only edit your own notes."
        )

    body = _required_text(
        data,
        "body",
    )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE ticket_notes
            SET body = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING
                id,
                incident_id,
                author_id,
                body,
                created_at,
                updated_at;
            """,
            (
                body,
                note_id,
            ),
        )

        updated_note = cursor.fetchone()

    connection.commit()

    return updated_note


def delete_note(
    note_id: int,
    user: dict,
) -> None:
    """Delete a user's own note or allow an admin to delete it."""
    note = _get_note(note_id)

    get_incident(
        note["incident_id"],
        user,
    )

    if (
        note["author_id"] != user["id"]
        and not is_admin(user)
    ):
        raise PermissionError(
            "You can only delete your own notes."
        )

    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM ticket_notes
            WHERE id = %s;
            """,
            (note_id,),
        )

    connection.commit()
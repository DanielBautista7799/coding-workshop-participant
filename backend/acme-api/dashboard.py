"""Creates each role's dashboard: employees see their ticket counts, engineers see their assigned workload, 
and admins see overall incident metrics, response times, workload, locations, blocked tickets, and escalations."""
from permissions import is_admin, is_employee, is_engineer
from postgres_service import get_connection


def get_dashboard(user: dict) -> dict:
    """Return the dashboard data that matches the logged-in user's role."""
    if is_admin(user):
        return _get_admin_dashboard()

    if is_engineer(user):
        return _get_engineer_dashboard(user["id"])

    if is_employee(user):
        return _get_employee_dashboard(user["id"])

    raise PermissionError("You do not have permission to view a dashboard.")


# EMPLOYEE DASHBOARD



def _get_employee_dashboard(user_id: int) -> dict:
    """Return incident counts for one employee."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE status = 'OPEN'
                ) AS open,
                COUNT(*) FILTER (
                    WHERE status = 'IN_PROGRESS'
                ) AS in_progress,
                COUNT(*) FILTER (
                    WHERE status = 'BLOCKED'
                ) AS blocked,
                COUNT(*) FILTER (
                    WHERE status = 'RESOLVED'
                ) AS resolved,
                COUNT(*) FILTER (
                    WHERE status = 'CLOSED'
                ) AS closed,
                COUNT(*) FILTER (
                    WHERE escalation_status IN ('PENDING', 'APPROVED')
                ) AS escalated
            FROM incidents
            WHERE reporter_id = %s;
            """,
            (user_id,),
        )

        summary = cursor.fetchone()

    return {
        "role": "EMPLOYEE",
        "summary": summary,
    }



# ENGINEER DASHBOARD



def _get_engineer_dashboard(user_id: int) -> dict:
    """Return workload counts for one engineer."""
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM engineer_profiles
            WHERE user_id = %s;
            """,
            (user_id,),
        )

        engineer = cursor.fetchone()

        if engineer is None:
            raise LookupError("Engineer profile not found.")

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_assigned,
                COUNT(*) FILTER (
                    WHERE status = 'OPEN'
                ) AS open,
                COUNT(*) FILTER (
                    WHERE status = 'IN_PROGRESS'
                ) AS in_progress,
                COUNT(*) FILTER (
                    WHERE status = 'BLOCKED'
                ) AS blocked,
                COUNT(*) FILTER (
                    WHERE status = 'RESOLVED'
                ) AS resolved,
                COUNT(*) FILTER (
                    WHERE status = 'CLOSED'
                ) AS closed,
                COUNT(*) FILTER (
                    WHERE escalation_status IN ('PENDING', 'APPROVED')
                ) AS escalated
            FROM incidents
            WHERE engineer_id = %s;
            """,
            (engineer["id"],),
        )

        summary = cursor.fetchone()

    return {
        "role": "ENGINEER",
        "summary": summary,
    }


# FACILITY ADMIN DASHBOARD


def _get_admin_dashboard() -> dict:
    """Return operational metrics for Facility Admins."""
    connection = get_connection()

    with connection.cursor() as cursor:

        # Overall incident totals
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (
                    WHERE status = 'OPEN'
                ) AS open,
                COUNT(*) FILTER (
                    WHERE status = 'IN_PROGRESS'
                ) AS in_progress,
                COUNT(*) FILTER (
                    WHERE status = 'BLOCKED'
                ) AS blocked,
                COUNT(*) FILTER (
                    WHERE status = 'RESOLVED'
                ) AS resolved,
                COUNT(*) FILTER (
                    WHERE status = 'CLOSED'
                ) AS closed,
                COUNT(*) FILTER (
                    WHERE escalation_status IN ('PENDING', 'APPROVED')
                ) AS escalated
            FROM incidents;
            """
        )

        summary = cursor.fetchone()

        # Average response times in minutes
        cursor.execute(
            """
            SELECT
                ROUND(
                    AVG(
                        EXTRACT(
                            EPOCH FROM (assigned_at - created_at)
                        ) / 60
                    ),
                    2
                ) AS average_assignment_minutes,

                ROUND(
                    AVG(
                        EXTRACT(
                            EPOCH FROM (acknowledged_at - assigned_at)
                        ) / 60
                    ),
                    2
                ) AS average_acknowledgement_minutes,

                ROUND(
                    AVG(
                        EXTRACT(
                            EPOCH FROM (resolved_at - created_at)
                        ) / 60
                    ),
                    2
                ) AS average_resolution_minutes
            FROM incidents;
            """
        )

        response_times = cursor.fetchone()

        # Tickets grouped by status
        cursor.execute(
            """
            SELECT
                status,
                COUNT(*) AS count
            FROM incidents
            GROUP BY status
            ORDER BY status;
            """
        )

        by_status = cursor.fetchall()

        # Tickets grouped by priority
        cursor.execute(
            """
            SELECT
                priority,
                COUNT(*) AS count
            FROM incidents
            GROUP BY priority
            ORDER BY priority;
            """
        )

        by_priority = cursor.fetchall()

        # Tickets grouped by category
        cursor.execute(
            """
            SELECT
                category,
                COUNT(*) AS count
            FROM incidents
            GROUP BY category
            ORDER BY count DESC, category;
            """
        )

        by_category = cursor.fetchall()

        # Current engineer workload
        cursor.execute(
            """
            SELECT
                engineer_profiles.id AS engineer_id,
                users.full_name,
                users.email,
                engineer_profiles.specialty,
                COUNT(incidents.id) FILTER (
                    WHERE incidents.status IN (
                        'OPEN',
                        'IN_PROGRESS',
                        'BLOCKED'
                    )
                ) AS active_incidents
            FROM engineer_profiles
            JOIN users
                ON users.id = engineer_profiles.user_id
            LEFT JOIN incidents
                ON incidents.engineer_id = engineer_profiles.id
            WHERE engineer_profiles.is_active = TRUE
            GROUP BY
                engineer_profiles.id,
                users.full_name,
                users.email,
                engineer_profiles.specialty
            ORDER BY active_incidents DESC, users.full_name;
            """
        )

        engineer_workload = cursor.fetchall()

        # Locations with the most incidents
        cursor.execute(
            """
            SELECT
                buildings.name AS building_name,
                floors.name AS floor_name,
                seats.label AS seat_label,
                COUNT(incidents.id) AS incident_count
            FROM incidents
            JOIN seats
                ON seats.id = incidents.seat_id
            JOIN floors
                ON floors.id = seats.floor_id
            JOIN buildings
                ON buildings.id = floors.building_id
            GROUP BY
                buildings.name,
                floors.name,
                seats.label
            ORDER BY incident_count DESC
            LIMIT 5;
            """
        )

        recurring_locations = cursor.fetchall()

        # Incidents currently blocked
        cursor.execute(
            """
            SELECT
                incidents.id,
                incidents.title,
                incidents.priority,
                incidents.blocked_reason,
                users.full_name AS engineer_name
            FROM incidents
            LEFT JOIN engineer_profiles
                ON engineer_profiles.id = incidents.engineer_id
            LEFT JOIN users
                ON users.id = engineer_profiles.user_id
            WHERE incidents.status = 'BLOCKED'
            ORDER BY incidents.updated_at DESC;
            """
        )

        blocked_incidents = cursor.fetchall()

        # Incidents that requested escalation
        cursor.execute(
            """
            SELECT
                incidents.id,
                incidents.title,
                incidents.priority,
                incidents.status,
                incidents.escalation_status,
                incidents.escalation_reason
            FROM incidents
            WHERE incidents.escalation_status IN (
                'PENDING',
                'APPROVED'
            )
            ORDER BY incidents.updated_at DESC;
            """
        )

        escalated_incidents = cursor.fetchall()

    return {
        "role": "FACILITY_ADMIN",
        "summary": summary,
        "response_times": response_times,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "engineer_workload": engineer_workload,
        "recurring_locations": recurring_locations,
        "blocked_incidents": blocked_incidents,
        "escalated_incidents": escalated_incidents,
    }
"""Reads the request method and path, checks authentication, then sends the request to the correct backend function."""

from auth import (
    login_user,
    refresh_access_token,
    register_user,
)
from dashboard import get_dashboard
from engineers import (
    create_engineer,
    delete_engineer,
    get_engineer,
    list_engineers,
    update_engineer,
)
from facilities import (
    create_building,
    create_floor,
    create_seat,
    delete_building,
    delete_floor,
    delete_seat,
    get_building,
    get_floor,
    get_seat,
    list_buildings,
    list_floors,
    list_seats,
    update_building,
    update_floor,
    update_seat,
)
from http_utils import (
    error_response,
    get_json_body,
    json_response,
)
from incidents import (
    assign_engineer,
    create_incident,
    create_note,
    delete_incident,
    delete_note,
    get_incident,
    get_status_history,
    list_incidents,
    list_notes,
    request_escalation,
    review_escalation,
    update_incident,
    update_incident_status,
    update_note,
)
from permissions import get_current_user
from postgres_service import get_connection
from skills import (
    list_engineer_skills,
    list_skills,
    update_engineer_skills,
)


def _get_method(event: dict) -> str:
    """Get the HTTP method from the Lambda event."""
    request_context = event.get("requestContext") or {}
    http = request_context.get("http") or {}

    return (
        http.get("method")
        or event.get("httpMethod")
        or "GET"
    ).upper()
def _get_path(event: dict) -> str:
    """Get the request path from the Lambda event."""
    path = (
        event.get("rawPath")
        or event.get("path")
        or "/"
    )

    if len(path) > 1:
        path = path.rstrip("/")

    cloudfront_prefix = "/api/acme-api"

    if path == cloudfront_prefix:
        path = "/"

    elif path.startswith(f"{cloudfront_prefix}/"):
        path = path[len(cloudfront_prefix):]

    return path


def _get_query_params(event: dict) -> dict:
    """Return query parameters or an empty dictionary."""
    return event.get("queryStringParameters") or {}


def _get_int(value, field_name: str) -> int:
    """Convert a value to an integer ID."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Valid {field_name} is required."
        ) from exc


def route_request(event: dict) -> dict:
    """Send a Lambda HTTP request to the correct application function."""
    method = _get_method(event)
    path = _get_path(event)
    query = _get_query_params(event)

    
    # PUBLIC ROUTES

    if method == "GET" and path == "/health":
        return json_response(
            200,
            {
                "status": "ok",
                "service": "acme-api",
            },
        )

    if method == "GET" and path == "/ready":
        try:
            conn = get_connection()

            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return json_response(
                200,
                {
                    "status": "ready",
                    "service": "acme-api",
                    "database": "ok",
                },
            )

        except Exception as exc:
            print(
                "Readiness database check failed: "
                f"{type(exc).__name__}"
            )

            return json_response(
                503,
                {
                    "status": "not_ready",
                    "service": "acme-api",
                    "database": "unavailable",
                },
            )

    if method == "POST" and path == "/auth/register":
        try:
            user = register_user(
                get_json_body(event)
            )

            return json_response(
                201,
                user,
            )

        except ValueError as exc:
            return error_response(
                400,
                str(exc),
            )

    if method == "POST" and path == "/auth/login":
        try:
            result = login_user(
                get_json_body(event)
            )

            return json_response(
                200,
                result,
            )

        except ValueError as exc:
            return error_response(
                401,
                str(exc),
            )

    if method == "POST" and path == "/auth/refresh":
        try:
            result = refresh_access_token(
                get_json_body(event)
            )

            return json_response(
                200,
                result,
            )

        except ValueError as exc:
            return error_response(
                401,
                str(exc),
            )

    # Everything below this point requires authentication.
    try:
        user = get_current_user(event)

    except ValueError as exc:
        return error_response(
            401,
            str(exc),
        )

    try:

        # DASHBOARD

        if method == "GET" and path == "/dashboard":
            return json_response(
                200,
                get_dashboard(user),
            )

        # BUILDINGS

        if path == "/buildings":

            if method == "GET":
                return json_response(
                    200,
                    list_buildings(),
                )

            if method == "POST":
                building = create_building(
                    get_json_body(event),
                    user,
                )

                return json_response(
                    201,
                    building,
                )

        if path.startswith("/buildings/"):
            building_id = _get_int(
                path.split("/")[2],
                "building ID",
            )

            if method == "GET":
                return json_response(
                    200,
                    get_building(building_id),
                )

            if method == "PUT":
                building = update_building(
                    building_id,
                    get_json_body(event),
                    user,
                )

                return json_response(
                    200,
                    building,
                )

            if method == "DELETE":
                delete_building(
                    building_id,
                    user,
                )

                return json_response(204)

        # FLOORS

        if path == "/floors":

            if method == "GET":
                building_id = query.get(
                    "building_id"
                )

                if building_id is not None:
                    building_id = _get_int(
                        building_id,
                        "building ID",
                    )

                return json_response(
                    200,
                    list_floors(building_id),
                )

            if method == "POST":
                floor = create_floor(
                    get_json_body(event),
                    user,
                )

                return json_response(
                    201,
                    floor,
                )

        if path.startswith("/floors/"):
            floor_id = _get_int(
                path.split("/")[2],
                "floor ID",
            )

            if method == "GET":
                return json_response(
                    200,
                    get_floor(floor_id),
                )

            if method == "PUT":
                floor = update_floor(
                    floor_id,
                    get_json_body(event),
                    user,
                )

                return json_response(
                    200,
                    floor,
                )

            if method == "DELETE":
                delete_floor(
                    floor_id,
                    user,
                )

                return json_response(204)

        # =========================
        # SEATS
        # =========================

        if path == "/seats":

            if method == "GET":
                floor_id = query.get(
                    "floor_id"
                )

                if floor_id is not None:
                    floor_id = _get_int(
                        floor_id,
                        "floor ID",
                    )

                return json_response(
                    200,
                    list_seats(floor_id),
                )

            if method == "POST":
                seat = create_seat(
                    get_json_body(event),
                    user,
                )

                return json_response(
                    201,
                    seat,
                )

        if path.startswith("/seats/"):
            seat_id = _get_int(
                path.split("/")[2],
                "seat ID",
            )

            if method == "GET":
                return json_response(
                    200,
                    get_seat(seat_id),
                )

            if method == "PUT":
                seat = update_seat(
                    seat_id,
                    get_json_body(event),
                    user,
                )

                return json_response(
                    200,
                    seat,
                )

            if method == "DELETE":
                delete_seat(
                    seat_id,
                    user,
                )

                return json_response(204)

        # =========================
        # ENGINEERS
        # =========================
        if path == "/skills":

            if method == "GET":

                return json_response(

                    200,

                    list_skills(user),

                )


            return error_response(

                405,

                "Method not allowed",

            )


        if path == "/engineer-skills":

            if method == "GET":

                return json_response(

                    200,

                    list_engineer_skills(user),

                )


            return error_response(

                405,

                "Method not allowed",

            )


        if path.startswith("/engineer-skills/"):

            engineer_id = int(

                path.rsplit("/", 1)[-1]

            )


            if method == "PUT":

                result = update_engineer_skills(

                    engineer_id,

                    get_json_body(event),

                    user,

                )


                return json_response(

                    200,

                    result,

                )


            return error_response(

                405,

                "Method not allowed",

            )

        if path == "/engineers":

            if method == "GET":
                return json_response(
                    200,
                    list_engineers(),
                )

            if method == "POST":
                engineer = create_engineer(
                    get_json_body(event),
                    user,
                )

                return json_response(
                    201,
                    engineer,
                )

        if path.startswith("/engineers/"):
            engineer_id = _get_int(
                path.split("/")[2],
                "engineer ID",
            )

            if method == "GET":
                return json_response(
                    200,
                    get_engineer(engineer_id),
                )

            if method == "PUT":
                engineer = update_engineer(
                    engineer_id,
                    get_json_body(event),
                    user,
                )

                return json_response(
                    200,
                    engineer,
                )

            if method == "DELETE":
                delete_engineer(
                    engineer_id,
                    user,
                )

                return json_response(204)

        # =========================
        # INCIDENT COLLECTION
        # =========================

        if path == "/incidents":

            if method == "GET":
                incidents = list_incidents(
                    user=user,
                    status=query.get("status"),
                    priority=query.get("priority"),
                    category=query.get("category"),
                    search=query.get("search"),
                )

                return json_response(
                    200,
                    incidents,
                )

            if method == "POST":
                incident = create_incident(
                    get_json_body(event),
                    user,
                )

                return json_response(
                    201,
                    incident,
                )

        # =========================
        # INDIVIDUAL INCIDENT ROUTES
        # =========================

        if path.startswith("/incidents/"):
            parts = path.strip("/").split("/")

            incident_id = _get_int(
                parts[1],
                "incident ID",
            )

            # /incidents/{id}
            if len(parts) == 2:

                if method == "GET":
                    return json_response(
                        200,
                        get_incident(
                            incident_id,
                            user,
                        ),
                    )

                if method == "PUT":
                    incident = update_incident(
                        incident_id,
                        get_json_body(event),
                        user,
                    )

                    return json_response(
                        200,
                        incident,
                    )

                if method == "DELETE":
                    delete_incident(
                        incident_id,
                        user,
                    )

                    return json_response(204)

            # /incidents/{id}/assignment
            if (
                len(parts) == 3
                and parts[2] == "assignment"
                and method == "PUT"
            ):
                data = get_json_body(event)

                engineer_id = _get_int(
                    data.get("engineer_id"),
                    "engineer ID",
                )

                incident = assign_engineer(
                    incident_id,
                    engineer_id,
                    user,
                )

                return json_response(
                    200,
                    incident,
                )

            # /incidents/{id}/status
            if (
                len(parts) == 3
                and parts[2] == "status"
                and method == "PUT"
            ):
                data = get_json_body(event)

                new_status = str(
                    data.get("status", "")
                ).strip()

                if not new_status:
                    raise ValueError(
                        "Status is required."
                    )

                incident = update_incident_status(
                    incident_id,
                    new_status,
                    user,
                    data.get("blocked_reason"),
                )

                return json_response(
                    200,
                    incident,
                )

            # /incidents/{id}/history
            if (
                len(parts) == 3
                and parts[2] == "history"
                and method == "GET"
            ):
                history = get_status_history(
                    incident_id,
                    user,
                )

                return json_response(
                    200,
                    history,
                )

            # /incidents/{id}/escalation
            if (
                len(parts) == 3
                and parts[2] == "escalation"
            ):
                data = get_json_body(event)

                if method == "POST":
                    incident = request_escalation(
                        incident_id,
                        str(
                            data.get("reason", "")
                        ),
                        user,
                    )

                    return json_response(
                        200,
                        incident,
                    )

                if method == "PUT":
                    incident = review_escalation(
                        incident_id,
                        str(
                            data.get("decision", "")
                        ),
                        user,
                    )

                    return json_response(
                        200,
                        incident,
                    )

            # /incidents/{id}/notes
            if (
                len(parts) == 3
                and parts[2] == "notes"
            ):

                if method == "GET":
                    return json_response(
                        200,
                        list_notes(
                            incident_id,
                            user,
                        ),
                    )

                if method == "POST":
                    note = create_note(
                        incident_id,
                        get_json_body(event),
                        user,
                    )

                    return json_response(
                        201,
                        note,
                    )

        # =========================
        # INDIVIDUAL NOTE ROUTES
        # =========================

        if path.startswith("/notes/"):
            note_id = _get_int(
                path.split("/")[2],
                "note ID",
            )

            if method == "PUT":
                note = update_note(
                    note_id,
                    get_json_body(event),
                    user,
                )

                return json_response(
                    200,
                    note,
                )

            if method == "DELETE":
                delete_note(
                    note_id,
                    user,
                )

                return json_response(204)

        return error_response(
            404,
            "Route not found.",
        )

    except PermissionError as exc:
        return error_response(
            403,
            str(exc),
        )

    except LookupError as exc:
        return error_response(
            404,
            str(exc),
        )

    except ValueError as exc:
        return error_response(
            400,
            str(exc),
        )

    except Exception as exc:
        print(
            f"Unexpected backend error: {exc}"
        )

        return error_response(
            500,
            "An unexpected server error occurred.",
        )
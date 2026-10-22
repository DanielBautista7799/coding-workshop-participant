"""Tests larger CRUD and validation workflows without creating dozens of small tests."""

from conftest import get_response_body, make_event
from router import route_request


def _login(email: str) -> str:
    """Log in a demo user and return an access token."""
    response = route_request(
        make_event(
            "POST",
            "/auth/login",
            body={
                "email": email,
                "password": "AcmeDemo123!",
            },
        )
    )

    return get_response_body(response)["access_token"]


def test_facility_crud_flow() -> None:
    """Admin can manage locations while protected locations cannot be deleted."""
    admin_token = _login("admin@acme.inc")

    # Create building
    response = route_request(
        make_event(
            "POST",
            "/buildings",
            token=admin_token,
            body={
                "name": "Charlotte Office",
                "address": "Charlotte, NC",
            },
        )
    )

    building = get_response_body(response)

    assert response["statusCode"] == 201

    # Update building
    response = route_request(
        make_event(
            "PUT",
            f"/buildings/{building['id']}",
            token=admin_token,
            body={
                "name": "Charlotte Technology Center",
                "address": "Charlotte, NC",
            },
        )
    )

    building = get_response_body(response)

    assert response["statusCode"] == 200
    assert building["name"] == "Charlotte Technology Center"

    # Create floor
    response = route_request(
        make_event(
            "POST",
            "/floors",
            token=admin_token,
            body={
                "building_id": building["id"],
                "name": "Floor 1",
            },
        )
    )

    floor = get_response_body(response)

    assert response["statusCode"] == 201

    # Create seat
    response = route_request(
        make_event(
            "POST",
            "/seats",
            token=admin_token,
            body={
                "floor_id": floor["id"],
                "label": "C-101",
            },
        )
    )

    seat = get_response_body(response)

    assert response["statusCode"] == 201

    # Filter seats by floor
    response = route_request(
        make_event(
            "GET",
            "/seats",
            token=admin_token,
            query={
                "floor_id": str(floor["id"]),
            },
        )
    )

    seats = get_response_body(response)

    assert response["statusCode"] == 200
    assert len(seats) == 1
    assert seats[0]["label"] == "C-101"

    # Seeded building cannot be deleted because it contains floors.
    response = route_request(
        make_event(
            "DELETE",
            "/buildings/1",
            token=admin_token,
        )
    )

    assert response["statusCode"] == 400

    # Clean up the new location.
    assert route_request(
        make_event(
            "DELETE",
            f"/seats/{seat['id']}",
            token=admin_token,
        )
    )["statusCode"] == 204

    assert route_request(
        make_event(
            "DELETE",
            f"/floors/{floor['id']}",
            token=admin_token,
        )
    )["statusCode"] == 204

    assert route_request(
        make_event(
            "DELETE",
            f"/buildings/{building['id']}",
            token=admin_token,
        )
    )["statusCode"] == 204


def test_engineer_management_flow() -> None:
    """Admin can create, update, list, deactivate, and delete an engineer."""
    admin_token = _login("admin@acme.inc")

    # Create engineer
    response = route_request(
        make_event(
            "POST",
            "/engineers",
            token=admin_token,
            body={
                "full_name": "Jordan Engineer",
                "email": "jordan@acme.inc",
                "password": "Password123!",
                "specialty": "Network Support",
            },
        )
    )

    engineer = get_response_body(response)

    assert response["statusCode"] == 201
    assert engineer["email"] == "jordan@acme.inc"

    # Update and deactivate engineer
    response = route_request(
        make_event(
            "PUT",
            f"/engineers/{engineer['id']}",
            token=admin_token,
            body={
                "full_name": "Jordan Engineer",
                "email": "jordan@acme.inc",
                "specialty": "Network and Hardware Support",
                "is_active": False,
            },
        )
    )

    engineer = get_response_body(response)

    assert response["statusCode"] == 200
    assert engineer["is_active"] is False

    # List engineers
    response = route_request(
        make_event(
            "GET",
            "/engineers",
            token=admin_token,
        )
    )

    engineers = get_response_body(response)

    assert response["statusCode"] == 200
    assert any(
        item["email"] == "jordan@acme.inc"
        for item in engineers
    )

    # Inactive engineer cannot be assigned.
    response = route_request(
        make_event(
            "PUT",
            "/incidents/1/assignment",
            token=admin_token,
            body={
                "engineer_id": engineer["id"],
            },
        )
    )

    assert response["statusCode"] == 400

    # Engineer has no incidents, so deletion is allowed.
    response = route_request(
        make_event(
            "DELETE",
            f"/engineers/{engineer['id']}",
            token=admin_token,
        )
    )

    assert response["statusCode"] == 204


def test_incident_crud_filter_and_notes_flow() -> None:
    """Employee can create, edit, search, manage notes, and delete an OPEN incident."""
    employee_token = _login("employee@acme.inc")

    # Create incident
    response = route_request(
        make_event(
            "POST",
            "/incidents",
            token=employee_token,
            body={
                "title": "Conference room mouse broken",
                "description": "Wireless mouse is not responding.",
                "category": "Hardware",
                "priority": "LOW",
                "seat_id": 1,
            },
        )
    )

    incident = get_response_body(response)

    assert response["statusCode"] == 201
    assert incident["status"] == "OPEN"

    # Update incident
    response = route_request(
        make_event(
            "PUT",
            f"/incidents/{incident['id']}",
            token=employee_token,
            body={
                "title": "Conference room mouse not responding",
                "description": "Wireless mouse still does not respond.",
                "category": "Hardware",
                "priority": "MEDIUM",
                "seat_id": 1,
            },
        )
    )

    incident = get_response_body(response)

    assert response["statusCode"] == 200
    assert incident["priority"] == "MEDIUM"

    # Search/filter incidents
    response = route_request(
        make_event(
            "GET",
            "/incidents",
            token=employee_token,
            query={
                "status": "OPEN",
                "priority": "MEDIUM",
                "category": "Hardware",
                "search": "conference",
            },
        )
    )

    incidents = get_response_body(response)

    assert response["statusCode"] == 200
    assert any(
        item["id"] == incident["id"]
        for item in incidents
    )

    # Create note
    response = route_request(
        make_event(
            "POST",
            f"/incidents/{incident['id']}/notes",
            token=employee_token,
            body={
                "body": "I tried replacing the batteries.",
            },
        )
    )

    note = get_response_body(response)

    assert response["statusCode"] == 201

    # Update note
    response = route_request(
        make_event(
            "PUT",
            f"/notes/{note['id']}",
            token=employee_token,
            body={
                "body": "I replaced the batteries but it still does not work.",
            },
        )
    )

    updated_note = get_response_body(response)

    assert response["statusCode"] == 200
    assert "still does not work" in updated_note["body"]

    # Delete note
    response = route_request(
        make_event(
            "DELETE",
            f"/notes/{note['id']}",
            token=employee_token,
        )
    )

    assert response["statusCode"] == 204

    # OPEN and unassigned, so employee can delete their own incident.
    response = route_request(
        make_event(
            "DELETE",
            f"/incidents/{incident['id']}",
            token=employee_token,
        )
    )

    assert response["statusCode"] == 204


def test_important_validation_errors() -> None:
    """Critical invalid requests should be rejected with proper HTTP errors."""
    employee_token = _login("employee@acme.inc")
    engineer_token = _login("engineer@acme.inc")
    admin_token = _login("admin@acme.inc")

    # Invalid seat
    response = route_request(
        make_event(
            "POST",
            "/incidents",
            token=employee_token,
            body={
                "title": "Bad location test",
                "description": "Testing an invalid seat.",
                "category": "Hardware",
                "priority": "LOW",
                "seat_id": 99999,
            },
        )
    )

    assert response["statusCode"] == 404

    # Invalid status transition:
    # seeded incident 2 is IN_PROGRESS, so it cannot go backwards to OPEN.
    response = route_request(
        make_event(
            "PUT",
            "/incidents/2/status",
            token=engineer_token,
            body={
                "status": "OPEN",
            },
        )
    )

    assert response["statusCode"] == 400

    # Duplicate building
    response = route_request(
        make_event(
            "POST",
            "/buildings",
            token=admin_token,
            body={
                "name": "Tampa Operations Center",
                "address": "Another Address",
            },
        )
    )

    assert response["statusCode"] == 400

    # Employee cannot create engineers.
    response = route_request(
        make_event(
            "POST",
            "/engineers",
            token=employee_token,
            body={
                "full_name": "Unauthorized Engineer",
                "email": "unauthorized@acme.inc",
                "password": "Password123!",
                "specialty": "Hardware",
            },
        )
    )

    assert response["statusCode"] == 403



def test_lambda_handler_routes_request() -> None:
    """AWS Lambda handler should pass requests into the application router."""
    from function import handler

    event = make_event(
        "GET",
        "/health",
    )

    response = handler(event, None)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "ok"


def test_remaining_crud_endpoints() -> None:
    """Exercise the remaining CRUD routes not covered by the other workflow tests."""
    admin_token = _login("admin@acme.inc")
    employee_token = _login("employee@acme.inc")

    # GET /buildings
    response = route_request(
        make_event(
            "GET",
            "/buildings",
            token=admin_token,
        )
    )
    assert response["statusCode"] == 200

    # GET /buildings/{id}
    response = route_request(
        make_event(
            "GET",
            "/buildings/1",
            token=admin_token,
        )
    )
    assert response["statusCode"] == 200

    # GET /floors
    response = route_request(
        make_event(
            "GET",
            "/floors",
            token=admin_token,
        )
    )
    assert response["statusCode"] == 200

    # GET /floors/{id}
    response = route_request(
        make_event(
            "GET",
            "/floors/1",
            token=admin_token,
        )
    )
    assert response["statusCode"] == 200

    # PUT /floors/{id}
    response = route_request(
        make_event(
            "PUT",
            "/floors/1",
            token=admin_token,
            body={
                "building_id": 1,
                "name": "Updated Floor 1",
            },
        )
    )
    floor = get_response_body(response)

    assert response["statusCode"] == 200
    assert floor["name"] == "Updated Floor 1"

    # GET /seats/{id}
    response = route_request(
        make_event(
            "GET",
            "/seats/1",
            token=admin_token,
        )
    )
    assert response["statusCode"] == 200

    # PUT /seats/{id}
    response = route_request(
        make_event(
            "PUT",
            "/seats/1",
            token=admin_token,
            body={
                "floor_id": 1,
                "label": "A-101-UPDATED",
            },
        )
    )
    seat = get_response_body(response)

    assert response["statusCode"] == 200
    assert seat["label"] == "A-101-UPDATED"

    # GET /engineers/{id}
    response = route_request(
        make_event(
            "GET",
            "/engineers/1",
            token=admin_token,
        )
    )
    engineer = get_response_body(response)

    assert response["statusCode"] == 200
    assert engineer["email"] == "engineer@acme.inc"

    # Create a note so we can test GET /incidents/{id}/notes
    response = route_request(
        make_event(
            "POST",
            "/incidents/1/notes",
            token=employee_token,
            body={
                "body": "CRUD coverage note.",
            },
        )
    )
    assert response["statusCode"] == 201

    # GET /incidents/{id}/notes
    response = route_request(
        make_event(
            "GET",
            "/incidents/1/notes",
            token=employee_token,
        )
    )
    notes = get_response_body(response)

    assert response["statusCode"] == 200
    assert len(notes) == 1
    assert notes[0]["body"] == "CRUD coverage note."
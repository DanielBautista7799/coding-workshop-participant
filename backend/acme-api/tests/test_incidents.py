"""Tests the full incident workflow, escalation, notes, and history."""

from conftest import get_response_body, make_event
from router import route_request


def _login(email: str) -> str:
    """Log in a demo user and return an access token."""
    event = make_event(
        "POST",
        "/auth/login",
        body={
            "email": email,
            "password": "AcmeDemo123!",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    return body["access_token"]


def test_employee_can_create_incident() -> None:
    """Employees should be able to report a new incident."""
    token = _login("employee@acme.inc")

    event = make_event(
        "POST",
        "/incidents",
        token=token,
        body={
            "title": "Mouse stopped working",
            "description": "USB mouse is no longer responding.",
            "category": "Hardware",
            "priority": "LOW",
            "seat_id": 1,
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 201
    assert body["title"] == "Mouse stopped working"
    assert body["status"] == "OPEN"
    assert body["priority"] == "LOW"


def test_admin_can_assign_engineer() -> None:
    """Facility Admins should be able to assign an active engineer."""
    token = _login("admin@acme.inc")

    event = make_event(
        "PUT",
        "/incidents/1/assignment",
        token=token,
        body={
            "engineer_id": 1,
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["engineer_id"] == 1
    assert body["assigned_at"] is not None


def test_engineer_can_move_assigned_incident_to_in_progress() -> None:
    """An assigned engineer should be able to begin work on an OPEN incident."""
    admin_token = _login("admin@acme.inc")
    engineer_token = _login("engineer@acme.inc")

    assignment_event = make_event(
        "PUT",
        "/incidents/1/assignment",
        token=admin_token,
        body={
            "engineer_id": 1,
        },
    )

    route_request(assignment_event)

    status_event = make_event(
        "PUT",
        "/incidents/1/status",
        token=engineer_token,
        body={
            "status": "IN_PROGRESS",
        },
    )

    response = route_request(status_event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "IN_PROGRESS"
    assert body["acknowledged_at"] is not None


def test_blocked_status_requires_reason() -> None:
    """An engineer cannot block an incident without explaining why."""
    engineer_token = _login("engineer@acme.inc")

    event = make_event(
        "PUT",
        "/incidents/2/status",
        token=engineer_token,
        body={
            "status": "BLOCKED",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 400
    assert "reason" in body["error"].lower()


def test_engineer_can_block_incident_with_reason() -> None:
    """An assigned engineer should be able to block a ticket with a reason."""
    engineer_token = _login("engineer@acme.inc")

    event = make_event(
        "PUT",
        "/incidents/2/status",
        token=engineer_token,
        body={
            "status": "BLOCKED",
            "blocked_reason": "Waiting for replacement hardware.",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "BLOCKED"
    assert body["blocked_reason"] == "Waiting for replacement hardware."


def test_engineer_can_resolve_incident() -> None:
    """An assigned engineer should be able to resolve an active incident."""
    engineer_token = _login("engineer@acme.inc")

    event = make_event(
        "PUT",
        "/incidents/2/status",
        token=engineer_token,
        body={
            "status": "RESOLVED",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "RESOLVED"
    assert body["resolved_at"] is not None


def test_employee_can_close_own_resolved_incident() -> None:
    """The reporting employee should be able to close a resolved incident."""
    engineer_token = _login("engineer@acme.inc")
    employee_token = _login("employee@acme.inc")

    resolve_event = make_event(
        "PUT",
        "/incidents/2/status",
        token=engineer_token,
        body={
            "status": "RESOLVED",
        },
    )

    route_request(resolve_event)

    close_event = make_event(
        "PUT",
        "/incidents/2/status",
        token=employee_token,
        body={
            "status": "CLOSED",
        },
    )

    response = route_request(close_event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "CLOSED"
    assert body["closed_at"] is not None


def test_employee_can_request_escalation() -> None:
    """An employee should be able to request escalation on their own incident."""
    token = _login("employee@acme.inc")

    event = make_event(
        "POST",
        "/incidents/1/escalation",
        token=token,
        body={
            "reason": "This issue is preventing me from working.",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["escalation_status"] == "PENDING"
    assert body["priority"] == "MEDIUM"
    assert body["status"] == "OPEN"


def test_admin_can_approve_escalation() -> None:
    """Facility Admins should be able to approve pending escalations."""
    employee_token = _login("employee@acme.inc")
    admin_token = _login("admin@acme.inc")

    request_event = make_event(
        "POST",
        "/incidents/1/escalation",
        token=employee_token,
        body={
            "reason": "Work is blocked.",
        },
    )

    route_request(request_event)

    review_event = make_event(
        "PUT",
        "/incidents/1/escalation",
        token=admin_token,
        body={
            "decision": "APPROVED",
        },
    )

    response = route_request(review_event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["escalation_status"] == "APPROVED"
    assert body["priority"] == "MEDIUM"


def test_employee_can_create_note() -> None:
    """An employee should be able to add notes to their own incident."""
    token = _login("employee@acme.inc")

    event = make_event(
        "POST",
        "/incidents/1/notes",
        token=token,
        body={
            "body": "Monitor is still not working.",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 201
    assert body["body"] == "Monitor is still not working."


def test_status_history_records_changes() -> None:
    """Status changes should be recorded in incident history."""
    engineer_token = _login("engineer@acme.inc")

    update_event = make_event(
        "PUT",
        "/incidents/2/status",
        token=engineer_token,
        body={
            "status": "RESOLVED",
        },
    )

    route_request(update_event)

    history_event = make_event(
        "GET",
        "/incidents/2/history",
        token=engineer_token,
    )

    response = route_request(history_event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert any(
        item["old_status"] == "IN_PROGRESS"
        and item["new_status"] == "RESOLVED"
        for item in body
    )
"""Tests role-based access for Employees, Engineers, and Facility Admins."""

from conftest import get_response_body, make_event
from router import route_request


def _login(email: str) -> str:
    """Log in a demo user and return their access token."""
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


def test_employee_cannot_create_building() -> None:
    """Employees should not be allowed to manage facilities."""
    token = _login("employee@acme.inc")

    event = make_event(
        "POST",
        "/buildings",
        token=token,
        body={
            "name": "Charlotte Office",
            "address": "Charlotte, NC",
        },
    )

    response = route_request(event)

    assert response["statusCode"] == 403


def test_engineer_cannot_create_building() -> None:
    """Engineers should not be allowed to manage facilities."""
    token = _login("engineer@acme.inc")

    event = make_event(
        "POST",
        "/buildings",
        token=token,
        body={
            "name": "Charlotte Office",
            "address": "Charlotte, NC",
        },
    )

    response = route_request(event)

    assert response["statusCode"] == 403


def test_admin_can_create_building() -> None:
    """Facility Admins should be allowed to create buildings."""
    token = _login("admin@acme.inc")

    event = make_event(
        "POST",
        "/buildings",
        token=token,
        body={
            "name": "Charlotte Office",
            "address": "Charlotte, NC",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 201
    assert body["name"] == "Charlotte Office"


def test_employee_cannot_assign_engineer() -> None:
    """Employees should not be allowed to assign engineers."""
    token = _login("employee@acme.inc")

    event = make_event(
        "PUT",
        "/incidents/1/assignment",
        token=token,
        body={
            "engineer_id": 1,
        },
    )

    response = route_request(event)

    assert response["statusCode"] == 403


def test_engineer_only_sees_assigned_incidents() -> None:
    """Engineers should only see incidents assigned to them."""
    token = _login("engineer@acme.inc")

    event = make_event(
        "GET",
        "/incidents",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    incident_ids = {
        incident["id"]
        for incident in body
    }

    assert response["statusCode"] == 200
    assert incident_ids == {2, 3}


def test_engineer_cannot_view_unassigned_incident() -> None:
    """Engineers should not access incidents assigned to someone else or nobody."""
    token = _login("engineer@acme.inc")

    event = make_event(
        "GET",
        "/incidents/1",
        token=token,
    )

    response = route_request(event)

    assert response["statusCode"] == 403


def test_admin_can_view_all_incidents() -> None:
    """Facility Admins should be able to view every incident."""
    token = _login("admin@acme.inc")

    event = make_event(
        "GET",
        "/incidents",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    incident_ids = {
        incident["id"]
        for incident in body
    }

    assert response["statusCode"] == 200
    assert incident_ids == {1, 2, 3}
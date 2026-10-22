"""Tests the role-specific Employee, Engineer, and Facility Admin dashboards."""

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


def test_employee_dashboard_shows_own_incident_counts() -> None:
    """Employees should receive a summary of their own incidents."""
    token = _login("employee@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["role"] == "EMPLOYEE"

    assert body["summary"]["total"] == 3
    assert body["summary"]["open"] == 1
    assert body["summary"]["in_progress"] == 1
    assert body["summary"]["blocked"] == 1
    assert body["summary"]["resolved"] == 0
    assert body["summary"]["closed"] == 0
    assert body["summary"]["escalated"] == 0


def test_engineer_dashboard_shows_assigned_workload() -> None:
    """Engineers should receive a summary of their assigned work."""
    token = _login("engineer@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["role"] == "ENGINEER"

    assert body["summary"]["total_assigned"] == 2
    assert body["summary"]["open"] == 0
    assert body["summary"]["in_progress"] == 1
    assert body["summary"]["blocked"] == 1
    assert body["summary"]["resolved"] == 0


def test_admin_dashboard_shows_all_incident_counts() -> None:
    """Facility Admins should receive organization-wide incident totals."""
    token = _login("admin@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["role"] == "FACILITY_ADMIN"

    assert body["summary"]["total"] == 3
    assert body["summary"]["open"] == 1
    assert body["summary"]["in_progress"] == 1
    assert body["summary"]["blocked"] == 1


def test_admin_dashboard_contains_reporting_metrics() -> None:
    """The Admin dashboard should contain the required operational reporting data."""
    token = _login("admin@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200

    assert "response_times" in body
    assert "by_status" in body
    assert "by_priority" in body
    assert "by_category" in body
    assert "engineer_workload" in body
    assert "recurring_locations" in body
    assert "blocked_incidents" in body
    assert "escalated_incidents" in body


def test_admin_dashboard_reports_blocked_reason() -> None:
    """Blocked incidents should include the reason work cannot continue."""
    token = _login("admin@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert len(body["blocked_incidents"]) == 1

    blocked = body["blocked_incidents"][0]

    assert blocked["title"] == "Replacement keyboard delayed"
    assert blocked["blocked_reason"] == "Waiting for replacement keyboard."


def test_admin_dashboard_reports_engineer_workload() -> None:
    """Admin reporting should show active incident workload by engineer."""
    token = _login("admin@acme.inc")

    event = make_event(
        "GET",
        "/dashboard",
        token=token,
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert len(body["engineer_workload"]) == 1

    engineer = body["engineer_workload"][0]

    assert engineer["full_name"] == "Alex Engineer"
    assert engineer["active_incidents"] == 2
"""Route-level tests for engineer skill API contracts and errors."""

from conftest import get_response_body, make_event
from router import route_request


DEMO_PASSWORD = "AcmeDemo123!"


def _login(email: str) -> str:
    """Log in a demo user and return its access token."""
    event = make_event(
        "POST",
        "/auth/login",
        body={
            "email": email,
            "password": DEMO_PASSWORD,
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    return body["access_token"]


def test_admin_can_list_skill_catalog() -> None:
    """Facility Admins can read the skill catalog endpoint."""
    token = _login("admin@acme.inc")

    response = route_request(
        make_event(
            "GET",
            "/skills",
            token=token,
        )
    )

    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert isinstance(body, list)


def test_employee_cannot_list_skill_catalog() -> None:
    """Employees cannot access admin-only skill management."""
    token = _login("employee@acme.inc")

    response = route_request(
        make_event(
            "GET",
            "/skills",
            token=token,
        )
    )

    assert response["statusCode"] == 403


def test_skills_route_rejects_unsupported_method() -> None:
    """The skill catalog should reject unsupported HTTP methods."""
    token = _login("admin@acme.inc")

    response = route_request(
        make_event(
            "POST",
            "/skills",
            token=token,
            body={"name": "Test"},
        )
    )

    assert response["statusCode"] == 405


def test_admin_can_list_engineer_skill_assignments() -> None:
    """Facility Admins can read grouped engineer skill assignments."""
    token = _login("admin@acme.inc")

    response = route_request(
        make_event(
            "GET",
            "/engineer-skills",
            token=token,
        )
    )

    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert isinstance(body, list)

    for entry in body:
        assert "engineer_id" in entry
        assert "skills" in entry


def test_admin_can_replace_engineer_skills() -> None:
    """A skill update persists through the public router contract."""
    token = _login("admin@acme.inc")

    assignments_response = route_request(
        make_event(
            "GET",
            "/engineer-skills",
            token=token,
        )
    )
    assignments = get_response_body(assignments_response)

    assert assignments

    engineer = assignments[0]
    engineer_id = engineer["engineer_id"]
    original_skills = list(engineer["skills"])

    try:
        update_response = route_request(
            make_event(
                "PUT",
                f"/engineer-skills/{engineer_id}",
                token=token,
                body={"skills": []},
            )
        )

        update_body = get_response_body(update_response)

        assert update_response["statusCode"] == 200
        assert update_body == {
            "engineer_id": engineer_id,
            "skills": [],
        }

        verify_response = route_request(
            make_event(
                "GET",
                "/engineer-skills",
                token=token,
            )
        )
        verify_body = get_response_body(verify_response)

        updated = next(
            entry
            for entry in verify_body
            if entry["engineer_id"] == engineer_id
        )

        assert updated["skills"] == []

    finally:
        route_request(
            make_event(
                "PUT",
                f"/engineer-skills/{engineer_id}",
                token=token,
                body={"skills": original_skills},
            )
        )


def test_update_engineer_skills_validates_payload() -> None:
    """Invalid skill payloads return a client error."""
    token = _login("admin@acme.inc")

    assignments_response = route_request(
        make_event(
            "GET",
            "/engineer-skills",
            token=token,
        )
    )
    assignments = get_response_body(assignments_response)

    assert assignments

    engineer_id = assignments[0]["engineer_id"]

    response = route_request(
        make_event(
            "PUT",
            f"/engineer-skills/{engineer_id}",
            token=token,
            body={"skills": "Hardware"},
        )
    )

    body = get_response_body(response)

    assert response["statusCode"] == 400
    assert "skills must be a list" in body["error"]


def test_update_missing_engineer_returns_404() -> None:
    """Unknown engineer profiles return a not-found response."""
    token = _login("admin@acme.inc")

    response = route_request(
        make_event(
            "PUT",
            "/engineer-skills/999999",
            token=token,
            body={"skills": []},
        )
    )

    assert response["statusCode"] == 404

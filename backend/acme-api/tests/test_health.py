"""Tests service health and database readiness endpoints."""

from conftest import get_response_body, make_event
from router import route_request


def test_health_endpoint() -> None:
    """Health should report that the API process is running."""
    response = route_request(
        make_event(
            "GET",
            "/health",
        )
    )
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "ok"
    assert body["service"] == "acme-api"

    cloud_response = route_request(
        make_event(
            "GET",
            "/api/acme-api/health",
        )
    )
    cloud_body = get_response_body(cloud_response)

    assert cloud_response["statusCode"] == 200
    assert cloud_body["status"] == "ok"
    assert cloud_body["service"] == "acme-api"


def test_ready_endpoint() -> None:
    """Readiness should verify the PostgreSQL connection."""
    response = route_request(
        make_event(
            "GET",
            "/ready",
        )
    )
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["status"] == "ready"
    assert body["database"] == "ok"

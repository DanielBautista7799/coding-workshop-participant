"""Tests registration, login, JWT protection, refresh tokens, and auth validation."""

from conftest import get_response_body, make_event
from router import route_request


def test_valid_login() -> None:
    """A valid employee login should return access and refresh tokens."""
    event = make_event(
        "POST",
        "/auth/login",
        body={
            "email": "employee@acme.inc",
            "password": "AcmeDemo123!",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 200
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "Bearer"
    assert body["user"]["email"] == "employee@acme.inc"
    assert body["user"]["role"] == "EMPLOYEE"


def test_invalid_password() -> None:
    """A wrong password should return 401."""
    event = make_event(
        "POST",
        "/auth/login",
        body={
            "email": "employee@acme.inc",
            "password": "WrongPassword123!",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 401
    assert "error" in body


def test_registration_requires_acme_email() -> None:
    """Registration should reject email addresses outside @acme.inc."""
    event = make_event(
        "POST",
        "/auth/register",
        body={
            "full_name": "Test Employee",
            "email": "test@gmail.com",
            "password": "Password123!",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 400
    assert "@acme.inc" in body["error"]


def test_public_registration_cannot_choose_admin_role() -> None:
    """Public registration must always create an EMPLOYEE."""
    event = make_event(
        "POST",
        "/auth/register",
        body={
            "full_name": "Sneaky User",
            "email": "sneaky@acme.inc",
            "password": "Password123!",
            "role": "FACILITY_ADMIN",
        },
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 201
    assert body["role"] == "EMPLOYEE"


def test_protected_route_requires_token() -> None:
    """Protected routes should reject requests without a JWT."""
    event = make_event(
        "GET",
        "/incidents",
    )

    response = route_request(event)
    body = get_response_body(response)

    assert response["statusCode"] == 401
    assert "error" in body


def test_refresh_token_creates_new_access_token() -> None:
    """A valid refresh token should create a new access token."""
    login_event = make_event(
        "POST",
        "/auth/login",
        body={
            "email": "employee@acme.inc",
            "password": "AcmeDemo123!",
        },
    )

    login_response = route_request(login_event)
    login_body = get_response_body(login_response)

    refresh_event = make_event(
        "POST",
        "/auth/refresh",
        body={
            "refresh_token": login_body["refresh_token"],
        },
    )

    refresh_response = route_request(refresh_event)
    refresh_body = get_response_body(refresh_response)

    assert refresh_response["statusCode"] == 200
    assert refresh_body["access_token"]
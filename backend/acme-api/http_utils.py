"""HTTP response and request helpers."""

import json


def json_response(status_code: int, data=None) -> dict:
    """Create a JSON response for AWS Lambda."""
    if status_code == 204:
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": "",
        }

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(data, default=str),
    }


def error_response(status_code: int, message: str) -> dict:
    """Create a consistent API error response."""
    return json_response(
        status_code,
        {
            "error": message,
        },
    )


def get_json_body(event: dict) -> dict:
    """Read and validate the JSON body from a Lambda event."""
    body = event.get("body")

    if not body:
        return {}

    if isinstance(body, dict):
        return body

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must contain valid JSON.") from exc
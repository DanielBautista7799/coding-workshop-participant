"""AWS Lambda entry point for HTTP traffic and workshop bootstrap."""
from bootstrap import bootstrap_database
from router import route_request

def handler(event: dict, context) -> dict:
    event = event or {}
    if (
        event.get("workshop_action") == "bootstrap"
        and not event.get("requestContext")
    ):
        return {
            "status": "ok",
            "action": "bootstrap",
            **bootstrap_database(),
        }
    return route_request(event)

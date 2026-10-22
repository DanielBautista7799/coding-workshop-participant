"""Runs the Lambda backend as a local HTTP server for development."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from function import handler


HOST = "localhost"
PORT = 8000


class RequestHandler(BaseHTTPRequestHandler):
    """Convert normal HTTP requests into Lambda events."""

    def _handle_request(self) -> None:
        parsed_url = urlparse(self.path)

        query_params = {
            key: values[0]
            for key, values in parse_qs(parsed_url.query).items()
        }

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = None

        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")

        event = {
            "rawPath": parsed_url.path,
            "requestContext": {
                "http": {
                    "method": self.command,
                }
            },
            "headers": dict(self.headers),
            "queryStringParameters": query_params or None,
            "body": body,
        }

        response = handler(event, None)

        status_code = response.get("statusCode", 500)
        response_body = response.get("body", "")
        response_headers = response.get("headers", {})

        self.send_response(status_code)

        for key, value in response_headers.items():
            self.send_header(key, value)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS",
        )

        self.end_headers()

        if response_body:
            self.wfile.write(
                response_body.encode("utf-8")
            )

    def do_GET(self) -> None:
        self._handle_request()

    def do_POST(self) -> None:
        self._handle_request()

    def do_PUT(self) -> None:
        self._handle_request()

    def do_DELETE(self) -> None:
        self._handle_request()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, OPTIONS",
        )
        self.end_headers()


def run_server() -> None:
    """Start the local development server."""
    server = ThreadingHTTPServer(
        (HOST, PORT),
        RequestHandler,
    )

    print(
        f"ACME API running at http://{HOST}:{PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run_server()
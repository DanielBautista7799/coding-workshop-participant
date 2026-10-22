"""Small dependency-free load test for the ACME API.

Run this only against a local/dev environment, not production.

Examples:
    python performance_test.py
    python performance_test.py --requests 200 --concurrency 20
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_EMAIL = "admin@acme.inc"
DEFAULT_PASSWORD = "AcmeDemo123!"


@dataclass
class RequestResult:
    """Store one timed HTTP result."""

    endpoint: str
    status: int
    elapsed_ms: float
    error: str | None = None


def request_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    body: dict | None = None,
    timeout: float = 10.0,
) -> tuple[int, dict | list | None]:
    """Send one JSON request and return status plus decoded body."""
    headers = {
        "Accept": "application/json",
    }

    data = None

    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
        ) as response:
            raw = response.read().decode("utf-8")
            parsed = json.loads(raw) if raw else None
            return response.status, parsed

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        parsed = json.loads(raw) if raw else None
        return exc.code, parsed


def login(
    base_url: str,
    email: str,
    password: str,
) -> str:
    """Log in once and return an access token."""
    status, body = request_json(
        f"{base_url}/auth/login",
        method="POST",
        body={
            "email": email,
            "password": password,
        },
    )

    if status != 200 or not isinstance(body, dict):
        raise RuntimeError(
            f"Login failed with HTTP {status}: {body}"
        )

    token = body.get("access_token")

    if not token:
        raise RuntimeError(
            "Login response did not contain access_token."
        )

    return str(token)


def timed_get(
    base_url: str,
    endpoint: str,
    token: str,
) -> RequestResult:
    """Time one authenticated GET request."""
    started = time.perf_counter()

    try:
        status, _ = request_json(
            f"{base_url}{endpoint}",
            token=token,
        )

        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000

        return RequestResult(
            endpoint=endpoint,
            status=status,
            elapsed_ms=elapsed_ms,
            error=None if status == 200 else f"HTTP {status}",
        )

    except Exception as exc:
        elapsed_ms = (
            time.perf_counter() - started
        ) * 1000

        return RequestResult(
            endpoint=endpoint,
            status=0,
            elapsed_ms=elapsed_ms,
            error=str(exc),
        )


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    """Return a simple nearest-rank percentile."""
    if not values:
        return 0.0

    ordered = sorted(values)
    index = round(
        (len(ordered) - 1)
        * percentile_value
    )

    return ordered[index]


def print_summary(
    results: list[RequestResult],
    wall_seconds: float,
) -> None:
    """Print aggregate and per-endpoint performance results."""
    successful = [
        result
        for result in results
        if result.status == 200
        and result.error is None
    ]

    failed = [
        result
        for result in results
        if result not in successful
    ]

    latencies = [
        result.elapsed_ms
        for result in successful
    ]

    print()
    print("ACME API performance summary")
    print("-" * 52)
    print(f"Requests attempted : {len(results)}")
    print(f"Successful         : {len(successful)}")
    print(f"Failed             : {len(failed)}")
    print(f"Wall time          : {wall_seconds:.2f} s")

    requests_per_second = (
        len(results) / wall_seconds
        if wall_seconds > 0
        else 0.0
    )

    print(
        f"Throughput         : "
        f"{requests_per_second:.2f} req/s"
    )

    if latencies:
        print(
            f"Mean latency       : "
            f"{statistics.mean(latencies):.2f} ms"
        )
        print(
            f"Median latency     : "
            f"{statistics.median(latencies):.2f} ms"
        )
        print(
            f"P95 latency        : "
            f"{percentile(latencies, 0.95):.2f} ms"
        )
        print(
            f"Min / Max latency  : "
            f"{min(latencies):.2f} / "
            f"{max(latencies):.2f} ms"
        )

    endpoints = sorted(
        {result.endpoint for result in results}
    )

    for endpoint in endpoints:
        endpoint_results = [
            result
            for result in results
            if result.endpoint == endpoint
            and result.status == 200
            and result.error is None
        ]

        endpoint_latencies = [
            result.elapsed_ms
            for result in endpoint_results
        ]

        if not endpoint_latencies:
            continue

        print()
        print(endpoint)
        print(
            f"  successful: {len(endpoint_results)}"
        )
        print(
            f"  mean      : "
            f"{statistics.mean(endpoint_latencies):.2f} ms"
        )
        print(
            f"  p95       : "
            f"{percentile(endpoint_latencies, 0.95):.2f} ms"
        )

    if failed:
        print()
        print("Failures")
        print("-" * 52)

        for result in failed[:10]:
            print(
                f"{result.endpoint}: "
                f"{result.error or result.status}"
            )

        if len(failed) > 10:
            print(
                f"... {len(failed) - 10} more failures"
            )


def main() -> None:
    """Run a concurrent read-only API load test."""
    parser = argparse.ArgumentParser(
        description=(
            "Run a small concurrent load test against "
            "the local ACME API."
        )
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    if args.requests < 1:
        raise SystemExit("--requests must be at least 1")

    if args.concurrency < 1:
        raise SystemExit(
            "--concurrency must be at least 1"
        )

    email = os.getenv(
        "PERF_EMAIL",
        DEFAULT_EMAIL,
    )
    password = os.getenv(
        "PERF_PASSWORD",
        DEFAULT_PASSWORD,
    )

    base_url = args.base_url.rstrip("/")

    print(f"Target      : {base_url}")
    print(f"Requests    : {args.requests}")
    print(f"Concurrency : {args.concurrency}")
    print(f"Login       : {email}")
    print()
    print("Authenticating once before load test...")

    token = login(
        base_url,
        email,
        password,
    )

    print("Authentication successful.")
    print(
        "Testing read-only endpoints: "
        "/dashboard and /incidents"
    )

    endpoints = [
        "/dashboard"
        if index % 2 == 0
        else "/incidents"
        for index in range(args.requests)
    ]

    started = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=args.concurrency,
    ) as executor:
        futures = [
            executor.submit(
                timed_get,
                base_url,
                endpoint,
                token,
            )
            for endpoint in endpoints
        ]

        results = [
            future.result()
            for future in as_completed(futures)
        ]

    wall_seconds = (
        time.perf_counter() - started
    )

    print_summary(
        results,
        wall_seconds,
    )

    failures = [
        result
        for result in results
        if result.status != 200
        or result.error is not None
    ]

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

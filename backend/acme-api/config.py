"""Application settings loaded from environment variables."""

import hashlib
import os


SERVICE_NAME = "acme-api"
APP_NAME = "ACME Workplace Incident Management"

IS_LOCAL = os.getenv("IS_LOCAL", "true").lower() == "true"

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_NAME = os.getenv("POSTGRES_NAME") or "acme_workplace"
POSTGRES_USER = os.getenv("POSTGRES_USER") or os.getenv("USER", "postgres")
POSTGRES_PASS = os.getenv("POSTGRES_PASS", "")

ACCESS_TOKEN_MINUTES = 30
REFRESH_TOKEN_DAYS = 7
JWT_ALGORITHM = "HS256"

secret_source = f"{os.getenv('APP_ID', 'local')}:{POSTGRES_PASS}:acme-workplace"

JWT_SECRET = (
    os.getenv("JWT_SECRET")
    or hashlib.sha256(secret_source.encode()).hexdigest()
)

DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "AcmeDemo123!")
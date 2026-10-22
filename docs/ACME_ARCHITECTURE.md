# ACME Workplace Architecture

## Overview

ACME Workplace is a role-based workplace incident-management application for employees, engineers, and facility administrators.

```text
Browser
  -> React + Material UI
  -> API service layer
  -> AWS Lambda function.handler
  -> router.py
  -> domain modules
  -> psycopg
  -> PostgreSQL
```

Local development uses the same backend logic through `backend/acme-api/local_server.py`.

Cloud target:

```text
CloudFront / S3 -> React frontend
CloudFront API route -> AWS Lambda -> Aurora PostgreSQL
```

## Backend

The backend follows Citi's Lambda architecture rather than FastAPI.

Request flow:

```text
Lambda event
  -> function.handler
  -> router.route_request
  -> domain function
  -> PostgreSQL
```

Domain modules cover authentication, facilities, engineers, incidents, dashboard reporting, and engineer skills.

## Frontend

The React frontend uses Material UI, MUI X DataGrid, MUI X Charts, React Router, reusable components, responsive layouts, loading/error/success feedback, role-aware actions, engineer skill visibility, and a 30-second dashboard refresh.

## Authentication and RBAC

Authentication uses bcrypt password hashing plus JWT access and refresh tokens.

Roles:

- `EMPLOYEE`: report and manage eligible own incidents, notes, escalation, and closure.
- `ENGINEER`: manage assigned work, statuses, blocked reasons, and notes.
- `FACILITY_ADMIN`: manage facilities, engineers, skills, assignments, escalation review, lifecycle, and reporting.

Authorization is enforced in the backend.

## Incident workflow

```text
OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED
           |
           v
        BLOCKED
           |
           +----> IN_PROGRESS or RESOLVED
```

Escalation is tracked independently from workflow status.

## Reporting

The Facility Admin dashboard includes status, priority, category, escalation, response-time metrics, engineer workload, recurring locations, blocked incidents, and escalated incidents.

## Real-time interaction

The dashboard uses 30-second polling, manual refresh, and last-updated feedback. This avoids unnecessary WebSocket/SSE infrastructure while still providing near-real-time operational data.

## PWA support

The production frontend includes a web manifest, 192/512 icons, install metadata, and a production-only service worker for static application-shell caching.

API responses are deliberately not cached.

## Trade-offs

- **AI integration omitted:** no approved provider credentials were supplied, so the app avoids external model dependencies and secret-management risk.
- **No WebSockets/SSE:** polling is sufficient for the workshop use case.
- **No custom infrastructure:** Citi-provided Terraform/Lambda/Aurora/S3/CloudFront are used.
- **No MongoDB/DocumentDB:** PostgreSQL fits the relational domain.
- **No background worker:** current workflows require immediate synchronous feedback.

## Deployment status

Local implementation and validation are complete. AWS deployment is also complete and verified through CloudFront, Lambda, Aurora PostgreSQL, health/readiness checks, authentication, dashboard API access, and CloudWatch Lambda runtime logs.

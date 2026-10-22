# ACME Test and Validation Evidence

## Backend

```bash
cd backend/acme-api
source ../../.venv/bin/activate
python -m pytest --cov=. --cov-config=.coveragerc --cov-report=term-missing
```

Verified:

```text
58 passed in 28.05s
TOTAL 1139 statements
182 missed
84% coverage
```

Notable coverage:

```text
dashboard.py        96%
router.py           93%
postgres_service.py 94%
permissions.py      88%
security.py         84%
incidents.py        84%
engineers.py        82%
auth.py             81%
skills.py          100%
```

## Frontend

```bash
cd frontend
npm test -- --run
```

Verified:

```text
7 test files passed
43 tests passed
```

Coverage:

```bash
npm test -- --run --coverage
```

Verified:

```text
Statements 95.65%
Branches   88.42%
Functions  98.18%
Lines      95.52%
```

## Production build

```bash
npm run build
```

Verified successfully. Vite reports a large-chunk warning, but the build succeeds.

## End-to-end

```bash
npm run e2e
```

Verified:

```text
1 passing
All specs passed
```

Critical workflow:

```text
Employee reports incident
  -> Admin assigns engineer
  -> Engineer moves to IN_PROGRESS
  -> Engineer resolves
  -> Employee closes
```

## Performance

```bash
cd backend/acme-api
python performance_test.py
```

Configuration:

```text
100 requests
10 concurrent workers
/dashboard and /incidents
```

Verified:

```text
Requests attempted : 100
Successful         : 100
Failed             : 0
Wall time          : 0.31 s
Throughput         : 324.74 req/s
Mean latency       : 29.94 ms
Median latency     : 22.97 ms
P95 latency        : 68.34 ms
Min / Max latency  : 7.04 / 113.55 ms
```

Endpoint detail:

```text
/dashboard: 50 successful, 35.03 ms mean, 79.59 ms p95
/incidents: 50 successful, 24.86 ms mean, 60.19 ms p95
```

These are local-development measurements, not AWS production benchmarks.

## Seed validation

```text
EMPLOYEE users         50
ENGINEER users         30
FACILITY_ADMIN users    4
engineer profiles      30
buildings               4
floors                 12
seats                  180
incidents              100
skills                  10
engineer skill links    98
```

Incident status distribution:

```text
BLOCKED      10
CLOSED       15
IN_PROGRESS  30
OPEN         25
RESOLVED     20
```

## Demo accounts

```text
admin@acme.inc
employee@acme.inc
engineer@acme.inc
```

Local demo password:

```text
AcmeDemo123!
```

These are workshop/demo credentials only.

## AWS cloud evidence

Verified in the Citi workshop AWS environment on October 22, 2026.

```text
Frontend CloudFront URL: https://d2sdokoopw4mg4.cloudfront.net
Backend/API path: /api/acme-api
GET /health: status=ok, service=acme-api
GET /ready: status=ready, database=ok
Admin login: verified
Admin dashboard: verified
Aurora seed: 84 users, 30 engineer profiles, 4 buildings, 12 floors, 180 seats, 100 incidents
CloudWatch Lambda runtime logs: verified
```

CloudWatch verification command:

```bash
aws logs tail /aws/lambda/coding-workshop-acme-api-24013543 --region us-east-2 --since 30m --format short
```

The cloud log stream showed successful Lambda START/END/REPORT entries with duration and memory metrics. The full critical workflow remains covered by the passing Cypress E2E test.

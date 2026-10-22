# ACME Requirements Matrix

Status:
- **Covered** - implemented and locally verified
- **Covered / Design Choice** - addressed through a documented pragmatic approach
- **Cloud Verified** - deployed and verified in the Citi AWS workshop environment
- **Not Implemented / Not Required** - deliberately omitted with rationale

## Evaluation competencies

| Area | Status | Evidence |
|---|---|---|
| Implementation | Covered | Full local CRUD application works; AWS CloudFront/Lambda/Aurora deployment verified |
| Design | Covered | Responsive Material UI UI, DataGrid, charts, loading/error/success states, accessibility cleanup |
| Code | Covered | Domain-separated backend modules, reusable React components, validation and centralized routing |
| Testing | Covered | 58 backend tests, 43 frontend tests, Cypress E2E, coverage, load testing |
| Experience | Covered | Reproducible local setup, documented architecture/trade-offs, and verified cloud deployment |

## Data persistence and validation

| Capability | Status |
|---|---|
| Created records persist | Covered |
| Updates persist accurately | Covered |
| Deletes remove data | Covered |
| Retrieval matches stored data | Covered |
| Required fields validated | Covered |
| Types/formats constrained | Covered |
| Entity references verified | Covered |
| Meaningful validation errors | Covered |
| Malformed input handled | Covered |

## REST API

| Capability | Status |
|---|---|
| GET / POST / PUT / DELETE used appropriately | Covered |
| Appropriate status codes | Covered |
| JSON success responses | Covered |
| Consistent error format | Covered |
| Query-parameter filtering | Covered |

## Frontend expected capabilities

| Capability | Status | Evidence |
|---|---|---|
| Responsive/adaptive design | Covered | Desktop DataGrid and responsive/mobile layouts |
| High performance | Covered | Production build plus load test |
| Real-time data interaction | Covered / Design Choice | 30-second dashboard polling + manual refresh |
| Accessibility | Covered | Labels, autocomplete metadata, aria labeling, MUI accessibility |
| State/feedback | Covered | Auth state, loading, success/error alerts, disabled forms |
| PWA | Covered | Manifest, icons, production service worker |
| AI integration | Not Implemented / Not Required | No approved provider credentials supplied |

## Authentication and RBAC

| Capability | Status |
|---|---|
| Secure login | Covered |
| bcrypt password hashing | Covered |
| JWT protected endpoints | Covered |
| Token expiration/refresh | Covered |
| Authentication before CRUD | Covered |
| Clear credential errors | Covered |
| EMPLOYEE / ENGINEER / FACILITY_ADMIN roles | Covered |
| Endpoint restrictions | Covered |
| Unauthorized mutations prevented | Covered |
| Privilege escalation prevented | Covered |
| Consistent 403 responses | Covered |

## ACME workflows

| Workflow | Status |
|---|---|
| Employee registration | Covered |
| Incident creation/tracking | Covered |
| Notes | Covered |
| Escalation request/review | Covered |
| Employee closure | Covered |
| Facility CRUD | Covered |
| Engineer CRUD | Covered |
| Engineer skill management | Covered |
| Engineer assignment | Covered |
| Status lifecycle | Covered |
| Blocked reasons | Covered |
| Dashboard/reporting | Covered |
| Search/filtering | Covered |
| Workflow history | Covered |

## Performance and reliability

| Capability | Status |
|---|---|
| API load test | Covered |
| Response-time metrics | Covered |
| `/health` | Covered |
| `/ready` database readiness | Covered |
| Cloud monitoring | Covered |

## Deliberate omissions

### AI
No approved AI provider credentials were supplied. Core ACME workflows remain provider-independent.

### Async background processing
No current workflow requires delayed/eventual processing; synchronous confirmation is appropriate.

### WebSockets / SSE
Near-real-time polling satisfies the operational need without extra infrastructure.

## Final verification

- AWS deployment: verified
- CloudFront frontend: verified
- Lambda API health/readiness: verified
- Aurora connectivity and seed: verified
- Admin authentication/dashboard: verified
- CloudWatch Lambda runtime logs: verified
- Critical user path: covered by Cypress E2E locally; live browser deployment also verified

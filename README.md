# Coding Workshop

The goal of this coding workshop is to enable and assess the hands-on skills
of participants through development of a practical technical solution that
solves a theoretical business problem.

## Getting Started

Navigate to [Coding Workshop - Main Guide](./docs/README.md) to get started.

## Coding Workshop Example

Coding workshop organizer(s) will provide instructions to follow by email. Here
below is a real example of requirements and expectations for participant(s):

### Requirements: Business Problem

Our company ACME Inc. is going through a massive organizational transformation
to become a more data-driven organization. Information about teams structure
and performance is currently scattered across multiple systems, making it
difficult to get a comprehensive view of team dynamics and achievements.

We are struggling to answer simple questions like:

* Who are the members of each team?
* Where are the teams located?
* What are the key achievements of each team on a monthly basis?
* How many teams have team leader not co-located with team members?
* How many teams have team leader as a non-direct staff?
* How many teams have non-direct staff to employees ratio above 20%?
* How many teams are reporting to an organization leader?

### Requirements: Technical Solution

As part of this transformation, we are looking to build a centralized team
management tool that will allow us to track team members, team locations,
monthly team achievements, as well as individual-level and team-level metadata.
Initial focus is to provide a self-service capability without any integrations
with other tools such as Employee Directory, Project Tracking, or Performance
Management.

The technical solution involves developing a stand-alone web application using
modern technologies. The application will have the following features:

* User authentication and authorization
* Role-based access control
* CRUD operations for individuals, teams, achievements and metadata
* Search and filter functionality
* Responsive design for mobile and desktop usage

### Requirements: Technology Stack

The following technologies are required to build the application:

* Frontend: HTML, CSS, React.js with React Responsive and Material UI Components
* Backend: Python
* Database: PostgreSQL

The following technologies are good to know, as they are used to manage and
deploy code:

* Version Control: Git, GitHub
* Infrastructure: Terraform
* Deployment Mode: Shell Scripts
* Deployment Target: AWS Serverless (e.g. S3, CloudFront, Lambda, RDS)

### Expectations: Value-Based Outcomes

By the end of the workshop, participants will have developed a functional
web application that meets the requirements outlined above. The application
will be deployed to a cloud environment and accessible via a web browser.
Participants will also gain hands-on experience with modern web development
technologies and best practices.

## Contributing

See the [CONTRIBUTING](./CONTRIBUTING.md) resource for more details.

## License

This library is licensed under the MIT-0 License.
See the [LICENSE](./LICENSE) resource for more details.

## Roadmap

See the
[open issues](https://github.com/citi/coding-workshop-participant/issues)
for a list of proposed roadmap features (and known issues).

## Security

See the
[Security Issue Notifications](./CONTRIBUTING.md#security-issue-notifications)
resource for more details.

## Authors

The following people have contributed to this workshop:

* Colin Heilman - [@heilmancs](https://github.com/heilmancs)
* Eugene Istrati - [@eistrati](https://github.com/eistrati)
* Isaiah Cornelius Smith - [@corneliusmith](https://github.com/corneliusmith)
* Juan Arevalo - [@jparevalo27](https://github.com/jparevalo27)
* Michael Annucci - [@michael-annucci](https://github.com/michael-annucci)

## Feedback

We'd love to hear your feedback! Please:

* ⭐ Star the repository if you find it helpful
* 🐛 Report issues on GitHub
* 💡 Suggest improvements
* 📝 Share your experience

<!-- ACME_PROJECT_SECTION_START -->

## ACME Workplace Incident Management

This repository contains the ACME Workplace full-stack implementation for the Citi Coding Workshop.

### Personas

- **Employee** - reports and tracks workplace incidents
- **Engineer** - manages assigned incident work
- **Facility Admin** - manages facilities, engineers, assignments, escalations, and reporting

### Architecture

```text
React + Material UI
        |
        v
Python AWS Lambda application
        |
        v
PostgreSQL
```

Local development uses `backend/acme-api/local_server.py`. Cloud deployment uses Citi-provided Lambda, Aurora/RDS, S3, CloudFront, and Terraform tooling.

### Main capabilities

- JWT authentication and refresh
- bcrypt password hashing
- backend-enforced RBAC
- incident CRUD
- facility hierarchy management
- engineer and skill management
- assignment and workflow transitions
- blocked reasons and escalation
- notes and history
- search/filtering
- responsive DataGrid/mobile UI
- dashboard metrics/charts
- 30-second dashboard refresh
- PWA support
- unit, integration, component, E2E, and load testing

### Local run

Backend:

```bash
cd backend/acme-api
source ../../.venv/bin/activate
python local_server.py
```

Frontend:

```bash
cd frontend
npm run dev
```

### Validation

```bash
# Backend
cd backend/acme-api
python -m pytest --cov=. --cov-config=.coveragerc --cov-report=term-missing

# Frontend
cd ../../frontend
npm test -- --run --coverage
npm run build
npm run e2e
```

Latest verified local evidence:

- Backend: **58 tests passed, 84% coverage**
- Frontend: **43 tests passed**
- Frontend coverage: **95.65% statements**
- Cypress: **1/1 critical workflow passing**
- Performance: **100/100 requests successful**, ~**324.74 req/s**, **29.94 ms mean latency**
- Production build: **passed**

### Documentation

- [`docs/ACME_ARCHITECTURE.md`](docs/ACME_ARCHITECTURE.md)
- [`docs/ACME_REQUIREMENTS_MATRIX.md`](docs/ACME_REQUIREMENTS_MATRIX.md)
- [`docs/ACME_TEST_EVIDENCE.md`](docs/ACME_TEST_EVIDENCE.md)

### Trade-off

AI integration is not enabled because no approved AI provider credentials were supplied. Core incident workflows remain provider-independent.

AWS deployment is complete and verified: the CloudFront frontend, Lambda API, Aurora database readiness, authentication, dashboard integration, and CloudWatch Lambda runtime logs were validated in the Citi workshop environment.

<!-- ACME_PROJECT_SECTION_END -->


## ACME Cloud Deployment

For the Citi workshop AWS deployment procedure, see [`docs/ACME_CLOUD_DEPLOYMENT.md`](docs/ACME_CLOUD_DEPLOYMENT.md).

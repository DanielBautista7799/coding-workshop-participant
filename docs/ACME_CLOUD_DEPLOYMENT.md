# ACME AWS Workshop Deployment

This runbook keeps workshop-specific credentials outside source code and
minimizes work in the Citi workspace.

## Cloud architecture

- Frontend: S3 + CloudFront
- Backend: AWS Lambda
- Database: Aurora PostgreSQL
- API path: `/api/acme-api/*`
- Region for this workshop: `us-east-2`

The application reads `IS_LOCAL` and `POSTGRES_*` from the environment.
No AWS database credentials are hardcoded in application source.

## Before leaving the Mac

```bash
cd ~/coding-workshop-participant
bash -n bin/deploy-acme-workshop.sh
grep -n '"@mui/x-charts"' frontend/package.json frontend/package-lock.json

cd backend/acme-api
pytest -q

cd ../../frontend
npm ci --no-audit --no-fund
npm run build
npm test -- --run
npm run e2e

cd ..
git diff --check
git status --short
```

Commit and push the final version before moving to the workspace.

## In the Citi workspace

```bash
cd ~/coding-workshop-participant
git pull origin main
export AWS_REGION=us-east-2
export TF_VAR_aws_vpc_id=vpc-045fddc9fddda225f
./bin/deploy-acme-workshop.sh
```

The helper prompts for Event ID, Participant ID, and Participant Code.
The Participant Code is entered silently and is not committed.

The helper then:

1. runs `npm ci`,
2. uses Citi's backend/Terraform deployment script,
3. invokes the deployed Lambda directly through AWS IAM to create the
   schema and seed the demo data if the database is empty,
4. uses Citi's frontend deployment script,
5. smoke-tests health, readiness, admin login, and dashboard data.

The bootstrap action is not an HTTP endpoint and will not replace an
already-populated database.

## Demo accounts

Password for all three: `AcmeDemo123!`

- `admin@acme.inc`
- `employee@acme.inc`
- `engineer@acme.inc`

## Presentation flow

Employee reports -> Facility Admin assigns -> Engineer resolves ->
Employee closes.

Use the Facility Admin dashboard afterward to show status/priority/
category reporting, engineer workload, recurring locations, blocked and
escalated incidents, and response-time metrics.

## Verified AWS Deployment

Verified October 22, 2026.

- CloudFront frontend: https://d2sdokoopw4mg4.cloudfront.net
- Lambda: coding-workshop-acme-api-24013543
- Aurora PostgreSQL: available and seeded
- GET /health: verified
- GET /ready: database verified
- Admin authentication: verified
- Dashboard API: verified
- CloudWatch Lambda runtime logs: verified
- Workshop region: us-east-2
- Workshop VPC: vpc-045fddc9fddda225f

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" >/dev/null 2>&1 && pwd -P)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd -P)"
INFRA_DIR="$PROJECT_ROOT/infra"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

export AWS_REGION="${AWS_REGION:-us-east-2}"
export AWS_DEFAULT_REGION="$AWS_REGION"

prompt_if_missing() {
  local name="$1" label="$2" secret="${3:-false}" value="${!1:-}"
  [ -n "$value" ] && return
  if [ "$secret" = "true" ]; then
    read -r -s -p "$label: " value
    echo
  else
    read -r -p "$label: " value
  fi
  [ -n "$value" ] || { echo "ERROR: $label is required."; exit 1; }
  export "$name=$value"
}

prompt_if_missing EVENT_ID "Event ID"
prompt_if_missing PARTICIPANT_ID "Participant ID"
prompt_if_missing PARTICIPANT_CODE "Participant Code" true

echo "========================================="
echo "ACME Workshop AWS Deployment"
echo "========================================="
echo "Region: $AWS_REGION"
echo "Event ID: $EVENT_ID"
echo "Participant ID: $PARTICIPANT_ID"
echo "Participant Code: [hidden]"
echo

cd "$PROJECT_ROOT"
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "ERROR: tracked files have uncommitted changes."
  git status --short
  exit 1
fi

for command in git aws terraform jq curl npm; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "ERROR: missing required command: $command"
    exit 1
  }
done

[ -f "$FRONTEND_DIR/package-lock.json" ] || {
  echo "ERROR: frontend/package-lock.json is missing."
  exit 1
}

echo "Current commit:"
git log -1 --oneline
echo

echo "[1/5] Installing exact frontend dependencies..."
(cd "$FRONTEND_DIR" && npm ci --no-audit --no-fund)

echo "[2/5] Deploying backend/Aurora..."
"$SCRIPT_DIR/deploy-backend.sh" aws

echo "[3/5] Initializing and seeding Aurora through Lambda..."
cd "$INFRA_DIR"
FUNCTION_NAME="$(
  terraform output -json lambda_urls \
  | jq -r 'keys[] | select(contains("-acme-api-"))' \
  | head -n 1
)"
[ -n "$FUNCTION_NAME" ] || {
  echo "ERROR: could not find deployed acme-api Lambda."
  exit 1
}

BOOTSTRAP_RESPONSE="$(mktemp)"
BOOTSTRAP_META="$(mktemp)"
cleanup() { rm -f "$BOOTSTRAP_RESPONSE" "$BOOTSTRAP_META" /tmp/acme-health.json; }
trap cleanup EXIT

aws lambda invoke \
  --region "$AWS_REGION" \
  --function-name "$FUNCTION_NAME" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"workshop_action":"bootstrap"}' \
  "$BOOTSTRAP_RESPONSE" >"$BOOTSTRAP_META"

if jq -e '.FunctionError' "$BOOTSTRAP_META" >/dev/null 2>&1; then
  echo "ERROR: Lambda bootstrap failed:"
  cat "$BOOTSTRAP_RESPONSE"
  echo
  exit 1
fi

jq -e '.status == "ok"' "$BOOTSTRAP_RESPONSE" >/dev/null || {
  echo "ERROR: unexpected bootstrap response:"
  cat "$BOOTSTRAP_RESPONSE"
  echo
  exit 1
}
echo "Bootstrap:"
jq . "$BOOTSTRAP_RESPONSE"

echo "[4/5] Deploying frontend..."
"$SCRIPT_DIR/deploy-frontend.sh" aws

echo "[5/5] Verifying live application..."
cd "$INFRA_DIR"
SITE_URL="$(terraform output -raw website_url)"
HEALTH_URL="$SITE_URL/api/acme-api/health"
READY_URL="$SITE_URL/api/acme-api/ready"

ok=false
for attempt in $(seq 1 18); do
  if curl -fsS "$HEALTH_URL" >/tmp/acme-health.json 2>/dev/null; then
    ok=true
    break
  fi
  echo "CloudFront/API not ready yet ($attempt/18)..."
  sleep 10
done
[ "$ok" = "true" ] || {
  echo "ERROR: live health endpoint did not become available."
  exit 1
}

echo "Health:"
cat /tmp/acme-health.json
echo
echo "Readiness:"
curl -fsS "$READY_URL" | jq .

LOGIN_RESPONSE="$(
  curl -fsS -X POST "$SITE_URL/api/acme-api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@acme.inc","password":"AcmeDemo123!"}'
)"
ACCESS_TOKEN="$(printf '%s' "$LOGIN_RESPONSE" | jq -r '.access_token // empty')"
[ -n "$ACCESS_TOKEN" ] || {
  echo "ERROR: live admin login failed."
  printf '%s\n' "$LOGIN_RESPONSE"
  exit 1
}
echo "Admin login: OK"

DASHBOARD="$(
  curl -fsS "$SITE_URL/api/acme-api/dashboard" \
    -H "Authorization: Bearer $ACCESS_TOKEN"
)"
echo "Dashboard:"
printf '%s' "$DASHBOARD" \
| jq '{role: .role, summary: .summary, response_times: .response_times}'

echo
echo "========================================="
echo "DEPLOYMENT VERIFIED"
echo "========================================="
echo "Live URL: $SITE_URL"
echo "Demo accounts: admin@acme.inc / employee@acme.inc / engineer@acme.inc"
echo "Password: AcmeDemo123!"
echo "Presentation: Employee reports -> Admin assigns -> Engineer resolves -> Employee closes"

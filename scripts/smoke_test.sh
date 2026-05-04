#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"
LOG_FILE="$(mktemp)"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
}
trap cleanup EXIT

unset OPENAI_API_KEY
python app.py >"$LOG_FILE" 2>&1 &
SERVER_PID=$!

for _ in {1..30}; do
  if curl -fsS "$BASE_URL/healthz" >/dev/null; then
    break
  fi
  sleep 1
done

curl -fsS "$BASE_URL/healthz" | grep -q '"status": "ok"'
curl -fsS "$BASE_URL/" >/dev/null
curl -fsS "$BASE_URL/main.js" >/dev/null
curl -fsS "$BASE_URL/api/levels" | grep -q '"levels"'
curl -fsS "$BASE_URL/api/use-cases" | grep -q '"use_cases"'
curl -fsS "$BASE_URL/api/agentic-maturity" | grep -q '"stages"'

for f in web/js/*.js; do
  curl -fsS "$BASE_URL/js/$(basename "$f")" >/dev/null
done

valid_body='{"level":1,"use_case":"uk_year10_teacher","use_case_context":""}'
valid_response="$(mktemp)"
valid_code="$(curl -sS -o "$valid_response" -w '%{http_code}' \
  -X POST "$BASE_URL/api/run" \
  -H 'Content-Type: application/json' \
  -d "$valid_body")"
if [[ "$valid_code" != "200" ]]; then
  echo "Expected HTTP 200 for valid /api/run, got $valid_code"
  cat "$valid_response"
  cat "$LOG_FILE"
  exit 1
fi
grep -q 'AI backend not configured' "$valid_response"

invalid_body='{"level":"bad"}'
invalid_response="$(mktemp)"
invalid_code="$(curl -sS -o "$invalid_response" -w '%{http_code}' \
  -X POST "$BASE_URL/api/run" \
  -H 'Content-Type: application/json' \
  -d "$invalid_body")"
if [[ "$invalid_code" != "400" ]]; then
  echo "Expected HTTP 400 for invalid /api/run payload, got $invalid_code"
  cat "$invalid_response"
  cat "$LOG_FILE"
  exit 1
fi
grep -q '"code": "invalid_field"' "$invalid_response"
grep -q '"request_id"' "$invalid_response"

rm -f "$valid_response" "$invalid_response"
echo "Smoke test passed."

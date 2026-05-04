#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:8000"
LOG_FILE="/tmp/glytch-smoke.log"

unset OPENAI_API_KEY || true

cleanup() {
  if [[ -n "${APP_PID:-}" ]] && kill -0 "$APP_PID" 2>/dev/null; then
    kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

fail_with_log() {
  echo "[smoke] ERROR: $1" >&2
  echo "[smoke] --- server log ($LOG_FILE) ---" >&2
  if [[ -f "$LOG_FILE" ]]; then
    cat "$LOG_FILE" >&2
  else
    echo "(log file not found)" >&2
  fi
  exit 1
}

http_get_check() {
  local path="$1"
  local expect_code="$2"
  local body_file
  body_file=$(mktemp)
  local code
  code=$(curl -sS -o "$body_file" -w '%{http_code}' "$BASE_URL$path") || fail_with_log "curl failed for GET $path"
  if [[ "$code" != "$expect_code" ]]; then
    cat "$body_file" >&2
    rm -f "$body_file"
    fail_with_log "GET $path expected HTTP $expect_code, got $code"
  fi
  cat "$body_file"
  rm -f "$body_file"
}

post_json_check() {
  local path="$1"
  local payload="$2"
  local expect_code="$3"
  local body_file
  body_file=$(mktemp)
  local code
  code=$(curl -sS -o "$body_file" -w '%{http_code}' -X POST "$BASE_URL$path" -H 'Content-Type: application/json' -d "$payload") || fail_with_log "curl failed for POST $path"
  if [[ "$code" != "$expect_code" ]]; then
    cat "$body_file" >&2
    rm -f "$body_file"
    fail_with_log "POST $path expected HTTP $expect_code, got $code"
  fi
  cat "$body_file"
  rm -f "$body_file"
}

python app.py >"$LOG_FILE" 2>&1 &
APP_PID=$!

for _ in $(seq 1 60); do
  if curl -fsS "$BASE_URL/healthz" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

curl -fsS "$BASE_URL/healthz" >/dev/null 2>&1 || fail_with_log "Server did not become ready on $BASE_URL/healthz"

health_body=$(http_get_check "/healthz" "200")
echo "$health_body" | grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' || fail_with_log "/healthz missing status ok"

for endpoint in /api/levels /api/use-cases /api/agentic-maturity; do
  body=$(http_get_check "$endpoint" "200")
  [[ -n "$body" ]] || fail_with_log "$endpoint returned empty body"
  echo "$body" | python -m json.tool >/dev/null 2>&1 || fail_with_log "$endpoint did not return valid JSON"
done

http_get_check "/" "200" >/dev/null
http_get_check "/main.js" "200" >/dev/null

for f in web/js/*.js; do
  module_path="/js/$(basename "$f")"
  http_get_check "$module_path" "200" >/dev/null
done

run_ok_body=$(post_json_check "/api/run" '{"level":1,"use_case":"uk_year10_teacher","use_case_context":""}' "200")
echo "$run_ok_body" | grep -q 'AI backend not configured' || fail_with_log "valid no-key /api/run missing fallback message"
echo "$run_ok_body" | grep -q 'backend' || fail_with_log "valid no-key /api/run missing backend field"
echo "$run_ok_body" | grep -q 'request_id' || fail_with_log "valid no-key /api/run missing request_id"

invalid_payload_body=$(post_json_check "/api/run" '{"level":"bad"}' "400")
echo "$invalid_payload_body" | grep -q 'invalid_field' || fail_with_log "invalid payload missing invalid_field"
echo "$invalid_payload_body" | grep -q 'request_id' || fail_with_log "invalid payload missing request_id"

invalid_level_body=$(post_json_check "/api/run" '{"level":99}' "400")
echo "$invalid_level_body" | grep -q 'invalid_level' || fail_with_log "invalid level missing invalid_level"
echo "$invalid_level_body" | grep -q 'request_id' || fail_with_log "invalid level missing request_id"

wrong_ct_body_file=$(mktemp)
wrong_ct_code=$(curl -sS -o "$wrong_ct_body_file" -w '%{http_code}' -X POST "$BASE_URL/api/run" -H 'Content-Type: text/plain' --data 'hello') || fail_with_log "curl failed for wrong content-type check"
if [[ "$wrong_ct_code" != "400" ]]; then
  cat "$wrong_ct_body_file" >&2
  rm -f "$wrong_ct_body_file"
  fail_with_log "wrong content-type expected HTTP 400, got $wrong_ct_code"
fi
wrong_ct_body=$(cat "$wrong_ct_body_file")
rm -f "$wrong_ct_body_file"
echo "$wrong_ct_body" | grep -q 'invalid_content_type' || fail_with_log "wrong content-type missing invalid_content_type"
echo "$wrong_ct_body" | grep -q 'request_id' || fail_with_log "wrong content-type missing request_id"

echo "[smoke] all checks passed"

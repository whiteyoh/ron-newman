#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   GITHUB_TOKEN=... ./scripts/populate_github_project.sh OWNER PROJECT_NUMBER ./project_tickets.csv
#
# Notes:
# - Requires: curl, jq
# - Creates issues in OWNER/REPO and adds each issue to OWNER's project (v2).
# - Set REPO via env var. Defaults to OWNER's repo named "ron-newman".

OWNER="${1:?Usage: $0 OWNER PROJECT_NUMBER CSV_PATH}"
PROJECT_NUMBER="${2:?Usage: $0 OWNER PROJECT_NUMBER CSV_PATH}"
CSV_PATH="${3:?Usage: $0 OWNER PROJECT_NUMBER CSV_PATH}"
REPO="${REPO:-ron-newman}"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN is required"
  exit 1
fi

for bin in curl jq; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "Missing dependency: $bin"
    exit 1
  fi
done

api_graphql() {
  local query="$1"
  local variables="$2"

  curl -sS \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(jq -cn --arg q "$query" --argjson v "$variables" '{query:$q,variables:$v}')" \
    https://api.github.com/graphql
}

project_query='query($owner:String!, $number:Int!) { user(login:$owner) { projectV2(number:$number) { id } } organization(login:$owner) { projectV2(number:$number) { id } } }'
project_resp="$(api_graphql "$project_query" "$(jq -cn --arg owner "$OWNER" --argjson number "$PROJECT_NUMBER" '{owner:$owner,number:$number}')")"
PROJECT_ID="$(echo "$project_resp" | jq -r '.data.user.projectV2.id // .data.organization.projectV2.id // empty')"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Could not find project #$PROJECT_NUMBER for owner $OWNER"
  echo "$project_resp" | jq .
  exit 1
fi

echo "Using project ID: $PROJECT_ID"

# Read CSV (skip header)
tail -n +2 "$CSV_PATH" | while IFS=, read -r title body status priority estimate; do
  body="${body%\"}"
  body="${body#\"}"

  issue_payload="$(jq -cn --arg t "$title" --arg b "$body" '{title:$t, body:$b}')"
  issue_resp="$(curl -sS \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "Content-Type: application/json" \
    -d "$issue_payload" \
    "https://api.github.com/repos/${OWNER}/${REPO}/issues")"

  issue_node_id="$(echo "$issue_resp" | jq -r '.node_id // empty')"
  issue_url="$(echo "$issue_resp" | jq -r '.html_url // empty')"

  if [[ -z "$issue_node_id" ]]; then
    echo "Failed creating issue for title: $title"
    echo "$issue_resp" | jq .
    continue
  fi

  echo "Created issue: $issue_url"

  add_item_mutation='mutation($project:ID!, $content:ID!) { addProjectV2ItemById(input:{projectId:$project,contentId:$content}) { item { id } } }'
  add_resp="$(api_graphql "$add_item_mutation" "$(jq -cn --arg project "$PROJECT_ID" --arg content "$issue_node_id" '{project:$project,content:$content}')")"

  if [[ "$(echo "$add_resp" | jq -r '.errors | length // 0')" != "0" ]]; then
    echo "Failed to add issue to project: $issue_url"
    echo "$add_resp" | jq .
    continue
  fi

  echo "Added to project: $issue_url"
done

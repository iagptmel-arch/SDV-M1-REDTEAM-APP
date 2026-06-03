#!/usr/bin/env bash
# =============================================================================
# SDV-M1-REDTEAM-APP — GitHub Project Updater
# =============================================================================
# Utilisation :
#   ./scripts/gh-project-updater.sh <commande> [options]
#
# Commandes :
#   add-issue <titre> <phase> <milestone> [<label>]   — Crée une issue + l'ajoute au projet
#   update-status <issue-num> <status>                  — Change le statut (Todo/In Progress/Done)
#   move-phase <issue-num> <phase>                     — Déplace vers une autre phase
#   list-issues [phase]                                 — Liste les issues du projet
#   help                                                — Affiche ce message
#
# Phases disponibles :
#   phase-1, phase-2, phase-3, cross-cutting, infrastructure
#
# Statuts disponibles :
#   Todo, In Progress, Done
#
# Prérequis :
#   - gh CLI installé et authentifié
#   - Token avec scope 'project' et 'repo'
# =============================================================================
set -euo pipefail

PROJECT_NUMBER=1
OWNER="iagptmel-arch"
REPO="iagptmel-arch/SDV-M1-REDTEAM-APP"
GH="/usr/local/bin/gh"

help() {
  head -30 "$0" | tail -28
}

# Récupère l'ID du projet
project_id=$($GH project view $PROJECT_NUMBER --owner $OWNER --format json | $GH api --jq '.id')

# Récupère les IDs de champs
get_field_id() {
  local field_name="$1"
  $GH project field-list $PROJECT_NUMBER --owner $OWNER --format json \
    | $GH api --jq ".fields[] | select(.name == \"$field_name\") | .id"
}

get_single_select_option_id() {
  local field_name="$1"
  local option_name="$2"
  $GH project field-list $PROJECT_NUMBER --owner $OWNER --format json \
    | $GH api --jq ".fields[] | select(.name == \"$field_name\") | .options[] | select(.name == \"$option_name\") | .id"
}

add_issue() {
  local title="$1"
  local phase="$2"
  local milestone_name="$3"
  local labels="${4:-$phase}"

  echo "→ Création de l'issue: $title"
  issue_url=$($GH issue create --repo "$REPO" \
    --title "$title" \
    --label "$labels" \
    --milestone "$milestone_name" \
    --body "Issue créée automatiquement par gh-project-updater.sh" \
    --json url --jq '.url')

  echo "→ Ajout au projet #$PROJECT_NUMBER"
  $GH project item-add $PROJECT_NUMBER --owner $OWNER --url "$issue_url" --format json > /dev/null

  echo "✓ Issue créée: $issue_url"
}

update_status() {
  local issue_num="$1"
  local status="$2"

  local status_field_id=$(get_field_id "Status")
  local status_option_id=$(get_single_select_option_id "Status" "$status")

  # Récupérer l'ID de l'item dans le projet
  local item_id=$($GH project item-list $PROJECT_NUMBER --owner $OWNER --format json \
    | $GH api --jq ".items[] | select(.content.number == $issue_num) | .id")

  if [ -z "$item_id" ]; then
    echo "✗ Issue #$issue_num introuvable dans le projet"
    exit 1
  fi

  $GH project item-edit --project-id "$project_id" --item-id "$item_id" \
    --field-id "$status_field_id" --single-select-option-id "$status_option_id" --format json > /dev/null

  echo "✓ Issue #$issue_num → Status: $status"
}

move_phase() {
  local issue_num="$1"
  local phase="$2"

  local phase_field_id=$(get_field_id "Phase")
  local phase_option_id=$(get_single_select_option_id "Phase" "$phase")

  local item_id=$($GH project item-list $PROJECT_NUMBER --owner $OWNER --format json \
    | $GH api --jq ".items[] | select(.content.number == $issue_num) | .id")

  if [ -z "$item_id" ]; then
    echo "✗ Issue #$issue_num introuvable dans le projet"
    exit 1
  fi

  $GH project item-edit --project-id "$project_id" --item-id "$item_id" \
    --field-id "$phase_field_id" --single-select-option-id "$phase_option_id" --format json > /dev/null

  echo "✓ Issue #$issue_num → Phase: $phase"
}

list_issues() {
  local phase="${1:-}"

  if [ -n "$phase" ]; then
    $GH project item-list $PROJECT_NUMBER --owner $OWNER --format json \
      | $GH api --jq ".items[] | select(.fieldValues[] | select(.field.name == \"Phase\") | .name == \"$phase\") | \"#\(.content.number) - \(.content.title)\""
  else
    $GH project item-list $PROJECT_NUMBER --owner $OWNER --format json \
      | $GH api --jq '.items[] | "#\(.content.number) - \(.content.title) [\(.fieldValues[] | select(.field.name == "Status") | .name // "Todo")]"'
  fi
}

# ── Dispatch ──────────────────────────────────────────────────────────────
case "${1:-help}" in
  add-issue)
    shift
    if [ $# -lt 3 ]; then echo "Usage: $0 add-issue <titre> <phase> <milestone> [label]"; exit 1; fi
    add_issue "$@"
    ;;
  update-status)
    shift
    if [ $# -lt 2 ]; then echo "Usage: $0 update-status <issue-num> <status>"; exit 1; fi
    update_status "$1" "$2"
    ;;
  move-phase)
    shift
    if [ $# -lt 2 ]; then echo "Usage: $0 move-phase <issue-num> <phase>"; exit 1; fi
    move_phase "$1" "$2"
    ;;
  list-issues)
    shift
    list_issues "$@"
    ;;
  help|*)
    help
    ;;
esac

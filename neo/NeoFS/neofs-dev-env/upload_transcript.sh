#!/usr/bin/env bash
set -euo pipefail

# Upload a transcript to NeoFS using wallet auth (with optional non-interactive password).
# Compatible with your CLI (no --attr).
#
# Supports:
#   --text "string"
#   --file path.txt
#   stdin piping
#
# Auth:
#   - Wallet mode only (since your CLI build seems to work with -w)
#   - If NEOFS_WALLET_PASSWORD is SET (even if empty), uses expect.
#   - If not set, runs interactively.

: "${NEOFS_ENDPOINT:?NEOFS_ENDPOINT is not set}"
: "${NEOFS_WALLET:?NEOFS_WALLET is not set}"
: "${NEOFS_CONTAINER_ID:?NEOFS_CONTAINER_ID is not set}"

# --------- Resolve neofs-cli ---------
NEOFS_CLI="${NEOFS_CLI_PATH:-}"
if [[ -z "$NEOFS_CLI" ]]; then
  NEOFS_CLI="$(command -v neofs-cli || true)"
fi
if [[ -z "$NEOFS_CLI" && -x "$HOME/bin/neofs-cli" ]]; then
  NEOFS_CLI="$HOME/bin/neofs-cli"
fi
if [[ -z "$NEOFS_CLI" ]]; then
  echo "❌ neofs-cli not found. Set NEOFS_CLI_PATH or fix PATH."
  exit 127
fi

# --------- Mode selection ---------
MODE="auto"
FILE=""
TEXT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      MODE="file"; FILE="${2:-}"; shift 2;;
    --text)
      MODE="text"; TEXT="${2:-}"; shift 2;;
    -h|--help)
      cat <<'EOF'
Usage:
  ./upload_transcript.sh --text "hello"
  ./upload_transcript.sh --file transcript.txt
  echo "hello" | ./upload_transcript.sh
EOF
      exit 0;;
    *)
      if [[ "$MODE" == "auto" && -z "$FILE" ]]; then
        MODE="file"; FILE="$1"; shift
      else
        echo "❌ Unknown argument: $1"; exit 1
      fi;;
  esac
done

if [[ "$MODE" == "auto" ]]; then
  if [[ ! -t 0 ]]; then
    MODE="stdin"
  else
    MODE="file"; FILE="transcript.txt"
  fi
fi

TMP_FILE=""
cleanup() { [[ -n "${TMP_FILE}" && -f "${TMP_FILE}" ]] && rm -f "${TMP_FILE}"; }
trap cleanup EXIT

case "$MODE" in
  file)
    [[ -z "$FILE" ]] && { echo "❌ --file requires a path"; exit 1; }
    [[ ! -f "$FILE" ]] && { echo "❌ File not found: $FILE"; exit 1; }
    UPLOAD_FILE="$FILE"
    ;;
  text)
    [[ -z "$TEXT" ]] && { echo "❌ --text requires a non-empty string"; exit 1; }
    TMP_FILE="$(mktemp /tmp/neofs_transcript_XXXXXX.txt)"
    printf "%s" "$TEXT" > "$TMP_FILE"
    UPLOAD_FILE="$TMP_FILE"
    ;;
  stdin)
    TMP_FILE="$(mktemp /tmp/neofs_transcript_XXXXXX.txt)"
    cat > "$TMP_FILE"
    [[ ! -s "$TMP_FILE" ]] && { echo "❌ No input received on stdin"; exit 1; }
    UPLOAD_FILE="$TMP_FILE"
    ;;
  *)
    echo "❌ Internal error: unknown mode $MODE"; exit 1;;
esac

echo "----------- NEOFS UPLOAD: RUNNING -----------"
echo "CLI      : $NEOFS_CLI"
echo "Endpoint : $NEOFS_ENDPOINT"
echo "Wallet   : $NEOFS_WALLET"
echo "Container: $NEOFS_CONTAINER_ID"
echo "Mode     : $MODE"
echo "File     : $UPLOAD_FILE"
echo

UPLOAD_CMD=( "$NEOFS_CLI" -r "$NEOFS_ENDPOINT" -w "$NEOFS_WALLET" \
  object put --file "$UPLOAD_FILE" --cid "$NEOFS_CONTAINER_ID" )

# --------- Non-interactive unlock using expect if PASSWORD is SET ---------
# We intentionally check "is the variable defined", not "non-empty".
if [[ "${NEOFS_WALLET_PASSWORD+x}" == "x" ]]; then
  if ! command -v expect >/dev/null 2>&1; then
    echo "❌ NEOFS_WALLET_PASSWORD is set but 'expect' is not installed."
    echo "Install: sudo apt-get install -y expect"
    exit 1
  fi

  # Use expect and propagate the real exit code from neofs-cli
  expect <<EOF
    log_user 1
    set timeout -1

    # Spawn the exact command
    spawn {*}$UPLOAD_CMD

    # When prompted, send password (may be empty) + Enter
    expect {
      "Enter password >" {
        send -- "\$env(NEOFS_WALLET_PASSWORD)\r"
        exp_continue
      }
      eof
    }

    # Extract exit status from spawned process
    catch wait result
    set exit_status [lindex \$result 3]
    exit \$exit_status
EOF

else
  # Interactive fallback
  "${UPLOAD_CMD[@]}"
fi

echo
echo "✅ Upload command finished."


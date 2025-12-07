#!/usr/bin/env bash
set -euo pipefail

# Retrieve a text object from NeoFS.
# Auth automation:
#   1) Prefer key-based if supported.
#   2) Else wallet + expect if password provided.
#   3) Else interactive.
#
# Output flag detection:
#   chooses --out / --file / stdout without noisy errors.

: "${NEOFS_ENDPOINT:?NEOFS_ENDPOINT is not set}"
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

OID="${1:-}"
OUT="${2:-}"

if [[ -z "$OID" ]]; then
  echo "❌ Missing OID."
  echo "Usage: $0 <OID> [output_file]"
  exit 1
fi

TMP_OUT=""
cleanup() { [[ -n "$TMP_OUT" && -f "$TMP_OUT" ]] && rm -f "$TMP_OUT"; }
trap cleanup EXIT

if [[ -z "$OUT" ]]; then
  TMP_OUT="$(mktemp /tmp/neofs_get_XXXXXX.txt)"
  OUT="$TMP_OUT"
fi

echo "----------- NEOFS DOWNLOAD: RUNNING -----------"
echo "CLI      : $NEOFS_CLI"
echo "Endpoint : $NEOFS_ENDPOINT"
echo "Container: $NEOFS_CONTAINER_ID"
echo "OID      : $OID"
echo "Out file : $OUT"
echo

# --------- Auth selection ---------
HELP_GLOBAL="$("$NEOFS_CLI" --help 2>&1 || true)"

AUTH_MODE="wallet"
AUTH_ARGS=()

if [[ -n "${NEOFS_KEY:-}" ]]; then
  if echo "$HELP_GLOBAL" | grep -q -- "--key"; then
    AUTH_MODE="key"
    AUTH_ARGS=(--key "$NEOFS_KEY")
  elif echo "$HELP_GLOBAL" | grep -qE '(^|[[:space:]])-k([,[:space:]]|$)'; then
    AUTH_MODE="key"
    AUTH_ARGS=(-k "$NEOFS_KEY")
  fi
fi

if [[ "$AUTH_MODE" == "wallet" ]]; then
  : "${NEOFS_WALLET:?NEOFS_WALLET is not set}"
  AUTH_ARGS=(-w "$NEOFS_WALLET")
fi

# --------- Output style detection ---------
HELP_GET="$("$NEOFS_CLI" object get --help 2>&1 || true)"

OUTPUT_MODE="stdout"
if echo "$HELP_GET" | grep -q -- "--out"; then
  OUTPUT_MODE="out"
elif echo "$HELP_GET" | grep -q -- "--file"; then
  OUTPUT_MODE="file"
fi

# --------- Build base get command (as string for expect) ---------
BASE_GET=( "$NEOFS_CLI" -r "$NEOFS_ENDPOINT" "${AUTH_ARGS[@]}" object get --cid "$NEOFS_CONTAINER_ID" --oid "$OID" )

if [[ "$OUTPUT_MODE" == "out" ]]; then
  BASE_GET+=( --out "$OUT" )
elif [[ "$OUTPUT_MODE" == "file" ]]; then
  BASE_GET+=( --file "$OUT" )
fi

# --------- Execute download ---------
if [[ "$AUTH_MODE" == "key" ]]; then
  if [[ "$OUTPUT_MODE" == "stdout" ]]; then
    "${BASE_GET[@]}" > "$OUT"
  else
    "${BASE_GET[@]}"
  fi

else
  # Wallet mode: expect if password is provided
  if [[ -n "${NEOFS_WALLET_PASSWORD:-}" && -x "$(command -v expect || true)" ]]; then
    # Build a command string for expect
    CMD_STR=""
    for a in "${BASE_GET[@]}"; do
      # naive quoting-safe-ish for your paths/values
      CMD_STR+="$a "
    done

    if [[ "$OUTPUT_MODE" == "stdout" ]]; then
      # Redirect outside expect
      expect <<EOF
        log_user 1
        set timeout -1
        spawn bash -lc "$CMD_STR"
        expect {
          "Enter password >" {
            send -- "$NEOFS_WALLET_PASSWORD\r"
            exp_continue
          }
          eof
        }
EOF
      # If stdout mode, rerun non-expect but with password won't work.
      # So we just do a safer approach:
      # Use expect with explicit redirection via bash -lc.
      CMD_STR_REDIRECT="$CMD_STR > \"$OUT\""
      expect <<EOF
        log_user 1
        set timeout -1
        spawn bash -lc "$CMD_STR_REDIRECT"
        expect {
          "Enter password >" {
            send -- "$NEOFS_WALLET_PASSWORD\r"
            exp_continue
          }
          eof
        }
EOF
    else
      expect <<EOF
        log_user 1
        set timeout -1
        spawn "${BASE_GET[@]}"
        expect {
          "Enter password >" {
            send -- "$NEOFS_WALLET_PASSWORD\r"
            exp_continue
          }
          eof
        }
EOF
    fi
  else
    # Interactive fallback
    if [[ "$OUTPUT_MODE" == "stdout" ]]; then
      "${BASE_GET[@]}" > "$OUT"
    else
      "${BASE_GET[@]}"
    fi
  fi
fi

echo
echo "✅ Download complete."

if [[ -n "$TMP_OUT" ]]; then
  echo "----------- CONTENT -----------"
  cat "$OUT"
fi



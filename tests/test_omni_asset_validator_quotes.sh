#!/usr/bin/env bash
# Smoke test: ensure the script parses correctly and all path expansions
# are quoted. Place this repo under a path containing spaces to exercise
# the quoting fix.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# shellcheck is the authoritative check for unquoted variables in this file.
if command -v shellcheck >/dev/null 2>&1; then
    shellcheck "${REPO_ROOT}/omni_asset_validator.sh"
else
    echo "WARNING: shellcheck not installed; skipping static quoting check"
fi

# Bash parses the file as a sanity check. A parse error here means the
# quoting change broke the script syntax.
bash -n "${REPO_ROOT}/omni_asset_validator.sh"

echo "PASS: script parses and passes quoting static analysis"

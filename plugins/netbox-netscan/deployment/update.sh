#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [version]" >&2
  exit 2
fi

exec "${SCRIPT_DIR}/deploy.sh" "${1:-}"


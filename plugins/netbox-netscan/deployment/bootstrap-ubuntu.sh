#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NETBOX_DOCKER_DIR="${NETBOX_DOCKER_DIR:-/opt/netbox-docker}"

for command in git docker; do
  if ! command -v "${command}" >/dev/null 2>&1; then
    echo "Required command not found: ${command}" >&2
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "The Docker Compose plugin is required." >&2
  exit 1
fi

if [[ ! -d "${NETBOX_DOCKER_DIR}/.git" ]]; then
  parent_dir="$(dirname -- "${NETBOX_DOCKER_DIR}")"
  sudo mkdir -p "${parent_dir}"
  sudo chown "$(id -u):$(id -g)" "${parent_dir}"
  git clone --branch release --single-branch \
    https://github.com/netbox-community/netbox-docker.git \
    "${NETBOX_DOCKER_DIR}"
fi

install -m 0644 "${SCRIPT_DIR}/configuration.py.example" \
  "${NETBOX_DOCKER_DIR}/configuration/netscan.py"

if [[ ! -f "${NETBOX_DOCKER_DIR}/netscan.env" ]]; then
  install -m 0600 "${SCRIPT_DIR}/deployment.env.example" \
    "${NETBOX_DOCKER_DIR}/netscan.env"
fi

cat <<EOF
Bootstrap completed.

1. Review:
   ${NETBOX_DOCKER_DIR}/configuration/netscan.py
   ${NETBOX_DOCKER_DIR}/netscan.env
   ${NETBOX_DOCKER_DIR}/env/netbox.env

2. If the GHCR package is private, authenticate first:
   docker login ghcr.io --username Guerrito1973

3. Deploy:
   NETBOX_DOCKER_DIR=${NETBOX_DOCKER_DIR} ${SCRIPT_DIR}/deploy.sh
EOF

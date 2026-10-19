#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NETBOX_DOCKER_DIR="${NETBOX_DOCKER_DIR:-/opt/netbox-docker}"
ENV_FILE="${NETSCAN_ENV_FILE:-${NETBOX_DOCKER_DIR}/netscan.env}"
COMPOSE_OVERRIDE="${SCRIPT_DIR}/compose.production.yml"
REQUESTED_VERSION="${1:-}"

if [[ ! -f "${NETBOX_DOCKER_DIR}/docker-compose.yml" ]]; then
  echo "NetBox Docker was not found at ${NETBOX_DOCKER_DIR}. Run bootstrap-ubuntu.sh first." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${SCRIPT_DIR}/deployment.env.example" "${ENV_FILE}"
  echo "Created ${ENV_FILE}. Review it and run this command again." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

if [[ -n "${REQUESTED_VERSION}" ]]; then
  REQUESTED_VERSION="${REQUESTED_VERSION#v}"
  export NETSCAN_IMAGE="ghcr.io/guerrito1973/netbox-netscan:${REQUESTED_VERSION}"
fi

if [[ -z "${NETSCAN_IMAGE:-}" ]]; then
  echo "NETSCAN_IMAGE is not configured in ${ENV_FILE}." >&2
  exit 1
fi

compose() {
  docker compose \
    --project-directory "${NETBOX_DOCKER_DIR}" \
    --env-file "${ENV_FILE}" \
    -f "${NETBOX_DOCKER_DIR}/docker-compose.yml" \
    -f "${COMPOSE_OVERRIDE}" \
    "$@"
}

echo "Validating Compose configuration..."
compose config --quiet

echo "Pulling ${NETSCAN_IMAGE}..."
compose pull netbox netbox-worker netbox-housekeeping

echo "Starting database and Redis services..."
compose up -d postgres redis redis-cache

echo "Applying database migrations..."
compose run --rm netbox \
  /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py migrate --noinput

echo "Starting NetBox with the new image..."
compose up -d --remove-orphans
compose ps

echo "Deployment completed with ${NETSCAN_IMAGE}."


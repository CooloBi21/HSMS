#!/bin/sh
set -eu

flask --app run:app db upgrade

if [ -n "${ADMIN_USERNAME:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  flask --app run:app seed-admin
fi

exec "$@"

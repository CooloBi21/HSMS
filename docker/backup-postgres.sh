#!/bin/sh
set -eu

interval="${BACKUP_INTERVAL_SECONDS:-86400}"
retention_days="${BACKUP_RETENTION_DAYS:-7}"

while true; do
  timestamp="$(date +%Y%m%d_%H%M%S)"
  target="/backups/hsms_${timestamp}.dump"

  pg_dump \
    --host=postgres \
    --port=5432 \
    --username="${POSTGRES_USER}" \
    --dbname="${POSTGRES_DB}" \
    --format=custom \
    --file="${target}"

  find /backups -type f -name "hsms_*.dump" -mtime +"${retention_days}" -delete
  sleep "${interval}"
done

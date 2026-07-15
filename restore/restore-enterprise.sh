#!/usr/bin/env sh
set -eu

: "${BACKUP_DIR:=/backups}"
: "${POSTGRES_HOST:=postgresql}"
: "${POSTGRES_DB:=sentinel}"
: "${POSTGRES_USER:=sentinel}"
: "${POSTGRES_PASSWORD:=sentinel}"
: "${REDIS_HOST:=redis}"
: "${QDRANT_HOST:=qdrant}"
: "${NEO4J_HOST:=neo4j}"
: "${REDIS_DATA_DIR:=/data}"
export PGPASSWORD="$POSTGRES_PASSWORD"

LATEST_PG=$(ls -1t "$BACKUP_DIR"/postgres-*.dump 2>/dev/null | head -n 1)
LATEST_REDIS=$(ls -1t "$BACKUP_DIR"/redis-*.rdb 2>/dev/null | head -n 1)

if [ -n "${LATEST_PG:-}" ]; then
  pg_restore -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "$LATEST_PG"
fi

if [ -n "${LATEST_REDIS:-}" ]; then
  cp "$LATEST_REDIS" "$REDIS_DATA_DIR/dump.rdb"
  redis-cli -h "$REDIS_HOST" FLUSHALL
fi

if [ -f "$BACKUP_DIR/qdrant-snapshot.json" ]; then
  cp "$BACKUP_DIR/qdrant-snapshot.json" "$BACKUP_DIR/qdrant-restore-manifest.json"
fi

if command -v neo4j-admin >/dev/null 2>&1; then
  neo4j-admin database load neo4j --from-path="$BACKUP_DIR" --overwrite-destination=true
else
  printf '%s\n' "neo4j-admin not available in this image; restore the Neo4j volume from storage snapshots." > "$BACKUP_DIR/neo4j-restore-note.txt"
fi

echo "Restore completed"

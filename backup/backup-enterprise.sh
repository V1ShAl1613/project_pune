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
: "${OLLAMA_HOST:=ollama}"

mkdir -p "$BACKUP_DIR"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
export PGPASSWORD="$POSTGRES_PASSWORD"

pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc > "$BACKUP_DIR/postgres-$STAMP.dump"
redis-cli -h "$REDIS_HOST" --rdb "$BACKUP_DIR/redis-$STAMP.rdb"
python3 - "$QDRANT_HOST" "$BACKUP_DIR/qdrant-$STAMP.json" "$STAMP" <<'PY'
import json
import sys
from pathlib import Path
from urllib import request

host = sys.argv[1]
out_file = Path(sys.argv[2])
stamp = sys.argv[3]

with request.urlopen(f"http://{host}:6333/collections") as response:
		collections = json.load(response).get("result", {}).get("collections", [])

snapshot_manifest = {"timestamp": stamp, "collections": []}
for collection in collections:
		name = collection.get("name")
		if not name:
				continue
		snapshot_manifest["collections"].append(name)
		try:
				req = request.Request(f"http://{host}:6333/collections/{name}/snapshots", method="POST")
				with request.urlopen(req) as snapshot_response:
						snapshot_manifest.setdefault("snapshots", []).append(json.load(snapshot_response))
		except Exception as exc:
				snapshot_manifest.setdefault("errors", []).append({"collection": name, "error": str(exc)})

out_file.write_text(json.dumps(snapshot_manifest, indent=2), encoding="utf-8")
PY
if command -v neo4j-admin >/dev/null 2>&1; then
	neo4j-admin database dump neo4j --to-path="$BACKUP_DIR"
else
	printf '%s\n' "neo4j-admin not available in this image; capture a storage snapshot for Neo4j volume recovery." > "$BACKUP_DIR/neo4j-$STAMP.txt"
fi
curl -fsS "http://$OLLAMA_HOST:11434/api/tags" > "$BACKUP_DIR/ollama-$STAMP.json"

echo "Backup completed: $STAMP"

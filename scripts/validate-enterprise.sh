#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

cd "$ROOT_DIR/backend"
python3 -m pytest tests/test_executive_platform.py tests/test_database_models.py -q -p no:langsmith

cd "$ROOT_DIR/frontend"
npm run typecheck

printf '%s\n' "Enterprise validation completed"

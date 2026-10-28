#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if command -v g++ >/dev/null; then make all; else echo 'g++ not found; running Python fallback for scene generator' >&2; fi
if [[ -n "${ORA_SPACE_WEB_DIR:-}" ]]; then WEB="$ORA_SPACE_WEB_DIR";
elif [[ -f ../ORASPACE/web/index.html ]]; then WEB=../ORASPACE/web;
elif [[ -f ../ORASPACE/web/index.html ]]; then WEB=../ORASPACE/web;
else WEB=.; fi
exec python3 -m service.app --host "${ORA_HOST:-127.0.0.1}" --port "${ORA_PORT:-8767}" --db "${ORA_DB:-./data/ora.sqlite3}" --web "$WEB"

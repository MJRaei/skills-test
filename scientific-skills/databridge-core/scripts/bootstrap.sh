#!/usr/bin/env bash
# DataBridge one-time setup.
#
# Creates an isolated Python environment at ~/.databridge/venv with the
# packages DataBridge skill scripts need (pymongo + pandas), writes the
# user's MongoDB URI to ~/.databridge.env, pings the server, and marks
# state.json as setup_complete.
#
# Safe to re-run: existing venv is reused, existing URI is the default
# prompt value, state.json is refreshed.

set -euo pipefail

STATE_DIR="${HOME}/.databridge"
ENV_FILE="${HOME}/.databridge.env"
VENV_DIR="${STATE_DIR}/venv"
DEFAULT_URI="mongodb://localhost:27017/databridge"

# Resolve the directory that contains this script so we can call its siblings.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${STATE_DIR}"

# ----- 1. Locate a Python interpreter ------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "error: python3 not found on PATH. Install Python 3.11+ and re-run." >&2
    exit 1
fi

PY_VER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
# Fail loudly if the interpreter is too old; DataBridge skill scripts target 3.11+.
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
    echo "error: need Python >= 3.11, found ${PY_VER}." >&2
    exit 1
fi

# ----- 2. Create / reuse an isolated venv --------------------------------------
if [[ ! -d "${VENV_DIR}" ]]; then
    echo "Creating isolated environment at ${VENV_DIR} ..."
    python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

echo "Installing pymongo and pandas (quiet) ..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet "pymongo>=4.6" "pandas>=2.0"

# ----- 3. Prompt for MongoDB URI -----------------------------------------------
EXISTING_URI=""
if [[ -f "${ENV_FILE}" ]]; then
    EXISTING_URI="$(grep -E '^MONGO_URI=' "${ENV_FILE}" | head -1 | cut -d= -f2- | sed 's/^"//;s/"$//' || true)"
fi
PROMPT_DEFAULT="${EXISTING_URI:-${DEFAULT_URI}}"

read -r -p "MongoDB URI [${PROMPT_DEFAULT}]: " USER_URI
MONGO_URI="${USER_URI:-${PROMPT_DEFAULT}}"

# ----- 4. Verify the server with a ping ---------------------------------------
echo "Verifying connection ..."
if ! MONGO_URI="${MONGO_URI}" python - <<'PY'
import os, sys
from pymongo import MongoClient
try:
    MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=5000).admin.command("ping")
except Exception as e:
    print(f"ping failed: {e}", file=sys.stderr)
    sys.exit(1)
PY
then
    echo "error: could not reach MongoDB at ${MONGO_URI}." >&2
    echo "       Start the server (brew / docker / atlas) and re-run this script." >&2
    exit 1
fi

# ----- 5. Persist URI and state ------------------------------------------------
umask 077  # keep ~/.databridge.env private (may contain credentials)
cat > "${ENV_FILE}" <<EOF
MONGO_URI=${MONGO_URI}
EOF

# Let doctor.py write the state file so we keep a single source of truth.
python "${SCRIPT_DIR}/doctor.py" >/dev/null

cat <<EOF

DataBridge is ready.

State:      ${STATE_DIR}/state.json
URI file:   ${ENV_FILE}
venv:       ${VENV_DIR}

Next steps:
  - To load a dataset, see its skill's scripts/SOURCE.md.
  - Run: source ${VENV_DIR}/bin/activate  (if you want to run scripts by hand)
EOF

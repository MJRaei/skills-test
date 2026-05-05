"""Shared helpers for DataBridge skill scripts.

All dataset and tool scripts import from this module to get a consistent
MongoDB connection, truncation/error envelope contracts, and read/write
access to the user-level state file at ~/.databridge/state.json.

Targets Python 3.11+. Typing is kept conservative (typing.Optional / Dict
rather than PEP 604 unions, no `from __future__ import annotations`) so
callers can re-exec under the DataBridge venv before importing without
worrying about deferred-annotation evaluation order.
"""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from pymongo import MongoClient
    from pymongo.database import Database
except ImportError as e:
    raise SystemExit(
        "pymongo is not installed. Run databridge-core/scripts/bootstrap.py "
        "once to set up the isolated environment."
    ) from e


STATE_DIR = Path.home() / ".databridge"
STATE_FILE = STATE_DIR / "state.json"
ENV_FILE = Path.home() / ".databridge.env"
DEFAULT_MONGO_URI = "mongodb://localhost:27017/databridge"
DEFAULT_MAX_CHARS = 10_000
SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# Environment + connection
# --------------------------------------------------------------------------- #
def load_env_file(path: Path = ENV_FILE) -> None:
    """Populate os.environ from a KEY=VALUE .env file. No-op if file missing."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_mongo_uri() -> str:
    load_env_file()
    return os.environ.get("MONGO_URI", DEFAULT_MONGO_URI)


def get_db() -> Database:
    """Return the default MongoDB database for DataBridge."""
    client = MongoClient(get_mongo_uri(), serverSelectionTimeoutMS=5000)
    return client.get_default_database()


# --------------------------------------------------------------------------- #
# Output contract (must match every tool script)
# --------------------------------------------------------------------------- #
def truncate_json(payload: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Return payload unchanged, or prefix a [TRUNCATED: ...] marker and clip.

    Matches the envelope used elsewhere in DataBridge so agents can detect
    truncation with a consistent string marker.
    """
    if len(payload) <= max_chars:
        return payload
    marker = (
        f"[TRUNCATED: result was {len(payload)} chars, showing first {max_chars}. "
        "Narrow your query to get complete results.]\n"
    )
    return marker + payload[:max_chars]


def error_envelope(exc: BaseException, hint: Optional[str] = None) -> Dict[str, Any]:
    """Build a structured error dict the agent can parse on exit code 1."""
    payload: Dict[str, Any] = {"error": f"{type(exc).__name__}: {exc}"}
    if hint:
        payload["hint"] = hint
    return payload


# --------------------------------------------------------------------------- #
# State file: atomic read/write + dataset registration
# --------------------------------------------------------------------------- #
def _empty_state() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "setup_complete": False,
        "mongo": {
            "uri_source": str(ENV_FILE),
            "db": None,
            "last_verified_at": None,
        },
        "datasets_loaded": {},
    }


def load_state() -> Dict[str, Any]:
    """Return the current state dict, or an empty skeleton if the file is missing."""
    if not STATE_FILE.exists():
        return _empty_state()
    try:
        return json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return _empty_state()


def save_state(state: Dict[str, Any]) -> None:
    """Atomically write state.json so concurrent readers never see a half-written file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=STATE_DIR, prefix=".state.", suffix=".tmp", delete=False
    ) as tmp:
        json.dump(state, tmp, indent=2, default=str)
        tmp_path = Path(tmp.name)
    tmp_path.replace(STATE_FILE)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def register_dataset(
    skill_name: str,
    collection: str,
    row_count: int,
    checksum: str,
    source: str,
    access: str,
) -> None:
    """Append a dataset entry to state.datasets_loaded and mark setup complete.

    Called by each dataset's ingest.py on successful load. If setup_complete
    was previously False (e.g., user ran ingest.py before bootstrap), this
    flips it to True since we clearly have a working MongoDB connection.
    """
    state = load_state()
    state["setup_complete"] = True
    state["datasets_loaded"][skill_name] = {
        "collection": collection,
        "row_count": row_count,
        "loaded_at": now_iso(),
        "source": source,
        "access": access,
        "checksum": checksum,
    }
    save_state(state)


def mark_setup_complete(mongo_uri: str, db_name: str) -> None:
    """Called by bootstrap.py / doctor.py after a successful ping."""
    state = load_state()
    state["setup_complete"] = True
    state["mongo"]["db"] = db_name
    state["mongo"]["last_verified_at"] = now_iso()
    save_state(state)


# --------------------------------------------------------------------------- #
# Checksum helper
# --------------------------------------------------------------------------- #
def sha256_of_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(chunk_size)
            if not buf:
                break
            h.update(buf)
    return f"sha256:{h.hexdigest()}"

#!/usr/bin/env python3
"""DataBridge health check + state refresher.

Reads ~/.databridge/state.json first. If the state is fresh (last verified
within STALE_AFTER_DAYS), emits it verbatim to stdout. Otherwise pings
MongoDB, reconciles `datasets_loaded` against actual collections, and
rewrites the state file before printing.

Contract (same as query.py):
    stdout = JSON payload
    exit 0 = healthy, stdout = current state
    exit 1 = unhealthy, stdout = {"error": "...", "hint": "..."}
"""

# --- Re-exec under the DataBridge-managed venv -------------------------------
import os
import sys
from pathlib import Path

_VENV_PY = Path.home() / ".databridge" / "venv" / "bin" / "python"
if _VENV_PY.exists() and Path(sys.executable).resolve() != _VENV_PY.resolve():
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

# --- Real imports ------------------------------------------------------------
import json
from datetime import datetime, timedelta, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import (  # noqa: E402
    error_envelope,
    get_db,
    get_mongo_uri,
    load_state,
    now_iso,
    save_state,
)

STALE_AFTER_DAYS = 7


def _is_fresh(state: dict) -> bool:
    mongo = state.get("mongo") or {}
    last = mongo.get("last_verified_at")
    if not last:
        return False
    try:
        when = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return False
    age = datetime.now(timezone.utc) - when
    return age < timedelta(days=STALE_AFTER_DAYS)


def _refresh(state: dict) -> dict:
    """Ping Mongo, drop stale dataset entries, refresh timestamp."""
    db = get_db()
    db.command("ping")

    existing = set(db.list_collection_names())
    loaded = state.get("datasets_loaded") or {}
    state["datasets_loaded"] = {
        name: info
        for name, info in loaded.items()
        if info.get("collection") in existing
    }
    state["setup_complete"] = True
    state["mongo"] = {
        **(state.get("mongo") or {}),
        "uri_source": state.get("mongo", {}).get("uri_source") or "",
        "db": db.name,
        "last_verified_at": now_iso(),
    }
    save_state(state)
    return state


def main() -> None:
    state = load_state()
    try:
        if not _is_fresh(state) or not state.get("setup_complete"):
            state = _refresh(state)
        sys.stdout.write(json.dumps(state, indent=2, default=str))
        sys.stdout.write("\n")
    except Exception as e:
        payload = error_envelope(
            e,
            hint=(
                "MongoDB appears unreachable. Run "
                "databridge-core/scripts/bootstrap.py to (re)configure, "
                f"or confirm the server at {get_mongo_uri()} is running."
            ),
        )
        sys.stdout.write(json.dumps(payload))
        sys.stdout.write("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

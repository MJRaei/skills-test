#!/usr/bin/env python3
"""Ingest SS_rxns_80806_dupremoved.json into MongoDB.

Usage:
    python scripts/ingest.py <path-to-SS_rxns_80806_dupremoved.json>

Behavior:
    - Validates the file exists and is a JSON array whose first record has
      the expected seven fields.
    - Drops any previous `solid_state_synthesis` collection.
    - Inserts records in chunks (default 1,000) after loading the full file.
    - Registers the dataset in ~/.databridge/state.json on success.
"""

# --- Re-exec under the DataBridge-managed venv -------------------------------
import os
import sys
from pathlib import Path

_venv_scripts = "Scripts" if sys.platform == "win32" else "bin"
_venv_exe = "python.exe" if sys.platform == "win32" else "python"
_VENV_PY = Path.home() / ".databridge" / "venv" / _venv_scripts / _venv_exe
if _VENV_PY.exists() and Path(sys.executable).resolve() != _VENV_PY.resolve():
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

# --- Real imports ------------------------------------------------------------
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "databridge-core" / "scripts"))

from lib import (  # noqa: E402
    error_envelope,
    get_db,
    register_dataset,
    sha256_of_file,
)


SKILL_NAME = "solid-state-synthesis"
COLLECTION = "solid_state_synthesis"
SOURCE_PROVIDER = "literature_extraction"
ACCESS_TIER = "direct"
CHUNK_SIZE = 1000

EXPECTED_FIELDS = {
    "DOI",
    "target",
    "precursors",
    "target_reaction",
    "impurity_reaction",
    "conditions_forDOI",
    "impurity_phase",
}


def _fail(exc: BaseException, hint: str = "") -> None:
    sys.stdout.write(json.dumps(error_envelope(exc, hint or None)))
    sys.stdout.write("\n")
    sys.exit(1)


def _load_and_validate(path: Path) -> list:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found at {path}")
    if path.suffix.lower() not in {".json", ".jsonl"}:
        raise ValueError(f"Expected .json or .jsonl, got {path.suffix}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Top-level JSON structure must be an array of records. "
            "See scripts/SOURCE.md for conversion instructions."
        )
    if not data:
        raise ValueError("JSON array is empty; nothing to ingest.")

    sample_keys = set(data[0].keys())
    missing = EXPECTED_FIELDS - sample_keys
    if missing:
        raise ValueError(
            f"First record is missing expected fields: {sorted(missing)}. "
            "Source format may have changed."
        )

    return data


def _ingest(records: list) -> int:
    db = get_db()
    coll = db[COLLECTION]
    coll.drop()

    inserted = 0
    for i in range(0, len(records), CHUNK_SIZE):
        chunk = records[i : i + CHUNK_SIZE]
        coll.insert_many(chunk, ordered=False)
        inserted += len(chunk)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "json_path",
        type=Path,
        help="Path to SS_rxns_80806_dupremoved.json",
    )
    args = parser.parse_args()

    try:
        records = _load_and_validate(args.json_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        _fail(e, hint="See scripts/SOURCE.md for file acquisition and format.")

    try:
        row_count = _ingest(records)
    except Exception as e:
        _fail(
            e,
            hint="Check MongoDB reachability; run databridge-core/scripts/doctor.py.",
        )

    try:
        checksum = sha256_of_file(args.json_path)
        register_dataset(
            skill_name=SKILL_NAME,
            collection=COLLECTION,
            row_count=row_count,
            checksum=checksum,
            source=SOURCE_PROVIDER,
            access=ACCESS_TIER,
        )
    except Exception as e:
        _fail(e, hint="Ingest succeeded but state registration failed; re-run to retry.")

    summary = {
        "ok": True,
        "skill": SKILL_NAME,
        "collection": COLLECTION,
        "row_count": row_count,
        "checksum": checksum,
    }
    sys.stdout.write(json.dumps(summary, indent=2))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()

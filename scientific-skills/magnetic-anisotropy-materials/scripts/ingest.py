#!/usr/bin/env python3
"""Ingest a magnetic_anisotropy_materials.csv export into MongoDB.

Usage:
    python scripts/ingest.py <path-to-magnetic_anisotropy_materials.csv>

Behavior:
    - Validates the file exists and has the expected columns (including
      quirky names like `(BH_Max)` and `Anisotropy Constant K1`).
    - Drops any previous `magnetic_anisotropy_materials` collection.
    - Reads the CSV in chunks with pandas, preserving mixed-type columns.
    - Inserts records into MongoDB (NaN -> None where appropriate, matching
      the databridge CsvParser contract the SKILL.md documents).
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

import pandas as pd  # noqa: E402

from lib import (  # noqa: E402
    error_envelope,
    get_db,
    register_dataset,
    sha256_of_file,
)


SKILL_NAME = "magnetic-anisotropy-materials"
COLLECTION = "magnetic_anisotropy_materials"
SOURCE_PROVIDER = "nemad"
ACCESS_TIER = "gated_registration"
CHUNK_SIZE = 5000

EXPECTED_COLUMNS = {
    "(BH_Max)",
    "Anisotropy Constant K1",
    "Anisotropy Constant K2",
    "Anisotropy_Energy",
    "Anisotropy_Field",
    "Coercivity",
    "Crystal_Structure",
    "Curie(TC)",
    "Curie_Weiss",
    "DOI",
    "Experimental",
    "Intrinsic Coercivity",
    "Lattice_Parameter",
    "Lattice_Structure",
    "Magnet_type",
    "Magnetic_type",
    "Material_Density",
    "Material_Name",
    "Material_Type",
    "Neel(TN)",
    "Remanence_Magnetization",
    "Saturation_Magnetization",
    "Space_Group",
    "Substrate",
    "Thickness",
}


def _fail(exc: BaseException, hint: str = "") -> None:
    sys.stdout.write(json.dumps(error_envelope(exc, hint or None)))
    sys.stdout.write("\n")
    sys.exit(1)


def _validate(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found at {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv file, got {path.suffix}")

    header = pd.read_csv(path, nrows=0).columns
    missing = EXPECTED_COLUMNS - set(header)
    if missing:
        raise ValueError(
            f"CSV is missing expected columns: {sorted(missing)}. "
            "The nemad export format may have changed."
        )


def _ingest(path: Path) -> int:
    db = get_db()
    coll = db[COLLECTION]
    coll.drop()

    inserted = 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        # NaN -> None for object columns, NaN stays for float columns. This
        # matches the existing DataBridge CsvParser and keeps the gotchas
        # section of SKILL.md accurate.
        records = chunk.where(pd.notna(chunk), None).to_dict("records")
        if records:
            coll.insert_many(records, ordered=False)
            inserted += len(records)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path", type=Path, help="Path to magnetic_anisotropy_materials.csv"
    )
    args = parser.parse_args()

    try:
        _validate(args.csv_path)
    except (FileNotFoundError, ValueError) as e:
        _fail(e, hint="See scripts/SOURCE.md for download instructions.")

    try:
        row_count = _ingest(args.csv_path)
    except Exception as e:
        _fail(
            e,
            hint="Check that MongoDB is reachable; run databridge-core/scripts/doctor.py.",
        )

    try:
        checksum = sha256_of_file(args.csv_path)
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

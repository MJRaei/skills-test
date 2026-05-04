#!/usr/bin/env python3
"""DataBridge query tool.

Three subcommands that mirror the internal LangChain tools:

    query.py aggregate --collection <name> --pipeline <json> [--max-chars N]
    query.py records   --collection <name> --filter <json>   [--limit N]
    query.py multi     --spec <json>                         [--max-chars N]

Success: prints a JSON payload to stdout (truncated with a [TRUNCATED: ...]
prefix when it would exceed --max-chars). Exit code 0.

Failure: prints {"error": "...", "hint": "..."} to stdout and exits 1.
"""

# --- Re-exec under the DataBridge-managed venv -------------------------------
# If the user's shell called us with their system Python but a venv exists
# from bootstrap.sh, switch to the venv Python so pymongo/pandas are always
# importable. This block has no imports beyond the stdlib and must stay at
# the top, before any project-level imports.
import os
import sys
from pathlib import Path

_VENV_PY = Path.home() / ".databridge" / "venv" / "bin" / "python"
if _VENV_PY.exists() and Path(sys.executable).resolve() != _VENV_PY.resolve():
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

# --- Real imports ------------------------------------------------------------
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Optional

# Let us import the sibling lib.py regardless of the caller's CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bson import json_util  # noqa: E402  (after sys.path tweak)

from lib import DEFAULT_MAX_CHARS, error_envelope, get_db, truncate_json  # noqa: E402


def _fail(exc: BaseException, hint: Optional[str] = None) -> None:
    sys.stdout.write(json.dumps(error_envelope(exc, hint)))
    sys.stdout.write("\n")
    sys.exit(1)


def _dump(results: Any, max_chars: int) -> None:
    """Serialize Mongo results to extended JSON and print with truncation."""
    payload = json_util.dumps(results, default=str)
    sys.stdout.write(truncate_json(payload, max_chars))
    sys.stdout.write("\n")


def _cmd_aggregate(args: argparse.Namespace) -> None:
    try:
        pipeline = json.loads(args.pipeline)
    except json.JSONDecodeError as e:
        _fail(e, hint="--pipeline must be a JSON array of aggregation stages.")

    try:
        results = list(get_db()[args.collection].aggregate(pipeline))
    except Exception as e:
        _fail(e, hint=f"Aggregation failed against collection '{args.collection}'.")

    _dump(results, args.max_chars)


def _cmd_records(args: argparse.Namespace) -> None:
    try:
        filt = json.loads(args.filter)
    except json.JSONDecodeError as e:
        _fail(e, hint="--filter must be a valid JSON object.")

    try:
        cursor = get_db()[args.collection].find(filt).limit(args.limit)
        results = list(cursor)
    except Exception as e:
        _fail(e, hint=f"Query failed against collection '{args.collection}'.")

    _dump(results, args.max_chars)


def _run_one(spec: dict) -> dict:
    """Worker for --multi. Returns a wrapped result regardless of success/failure."""
    collection = spec.get("collection")
    if not collection:
        return {"ok": False, "error": "spec entry missing 'collection'"}
    try:
        db = get_db()
        if "pipeline" in spec:
            data = list(db[collection].aggregate(spec["pipeline"]))
        else:
            data = list(
                db[collection]
                .find(spec.get("filter", {}))
                .limit(int(spec.get("limit", 10)))
            )
        return {"collection": collection, "ok": True, "result": data}
    except Exception as e:
        return {"collection": collection, "ok": False, "error": f"{type(e).__name__}: {e}"}


def _cmd_multi(args: argparse.Namespace) -> None:
    try:
        specs = json.loads(args.spec)
        if not isinstance(specs, list) or not specs:
            raise ValueError("--spec must be a non-empty JSON array")
    except (json.JSONDecodeError, ValueError) as e:
        _fail(
            e,
            hint='--spec must be a JSON array of {"collection", "pipeline" or "filter", "limit"}',
        )

    # Order-preserving parallel execution.
    results = [None] * len(specs)
    with ThreadPoolExecutor(max_workers=min(len(specs), 8)) as pool:
        futures = {pool.submit(_run_one, s): i for i, s in enumerate(specs)}
        for fut in as_completed(futures):
            results[futures[fut]] = fut.result()

    _dump(results, args.max_chars)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="DataBridge MongoDB query tool.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    agg = sub.add_parser("aggregate", help="Run an aggregation pipeline on one collection.")
    agg.add_argument("--collection", required=True)
    agg.add_argument("--pipeline", required=True, help="JSON array of stages")
    agg.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    agg.set_defaults(fn=_cmd_aggregate)

    rec = sub.add_parser("records", help="Fetch filtered records from one collection.")
    rec.add_argument("--collection", required=True)
    rec.add_argument("--filter", default="{}", help="JSON filter document")
    rec.add_argument("--limit", type=int, default=10)
    rec.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    rec.set_defaults(fn=_cmd_records)

    mul = sub.add_parser("multi", help="Run several queries across collections in parallel.")
    mul.add_argument(
        "--spec",
        required=True,
        help='JSON array of {"collection", "pipeline" or "filter", "limit"}',
    )
    mul.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    mul.set_defaults(fn=_cmd_multi)

    return p


def main() -> None:
    args = _build_parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

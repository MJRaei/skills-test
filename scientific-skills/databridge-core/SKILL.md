---
name: databridge-core
description: Query and ingest orchestration for DataBridge datasets stored in MongoDB. Required prerequisite for every DataBridge dataset skill. Use this skill's decision procedure before running any query, and on first session to verify setup. Trigger phrases: databridge, databridge-core, query dataset, mongodb databridge, run query, dataset health check, databridge setup, databridge doctor.
metadata:
  version: 1.0.0
  requires:
    python: ">=3.11"
    mongodb: ">=7.0"
---

# databridge-core

Orchestration skill for DataBridge. It defines the decision procedure every
DataBridge dataset skill relies on, documents the query tool surface, and
encodes gotchas shared across all datasets.

## First-use setup (one-time per machine)

Users install DataBridge skills via `npx skills add` and then run one command
to provision everything the scripts need:

```bash
bash scripts/bootstrap.sh
```

It creates an isolated Python venv at `~/.databridge/venv`, installs `pymongo`
and `pandas`, prompts for the MongoDB URI (default
`mongodb://localhost:27017/databridge`), pings the server, writes
`~/.databridge.env`, and initializes `~/.databridge/state.json`.

If the agent sees `setup_complete: false` (or the file missing), it should
tell the user to run bootstrap, then stop.

## Fast-path decision procedure

Before answering any databridge question, read `~/.databridge/state.json`
ONCE per session:

```bash
cat ~/.databridge/state.json
```

Then branch:

| Observation | Action |
|---|---|
| File missing OR `setup_complete` is false | Tell user: run `bash scripts/bootstrap.sh`. Stop. |
| Target dataset NOT in `datasets_loaded` | Open that skill's `scripts/SOURCE.md`, relay acquisition steps to the user, wait. Then run `python <skill>/scripts/ingest.py <path>`. |
| Target dataset present | Skip all checks, call `query.py`. |

Only run `scripts/doctor.py` when:

- A `query.py` call fails with a connection error, OR
- `state.mongo.last_verified_at` is older than 7 days.

`doctor.py` auto-refreshes state and reconciles `datasets_loaded` against the
actual collections in Mongo.

## Tool: `scripts/query.py`

Three subcommands. All emit JSON to stdout. On failure they print
`{"error": "...", "hint": "..."}` and exit 1.

### `aggregate` (single-dataset, agent-written pipeline)

```bash
python scripts/query.py aggregate \
    --collection <mongo_collection_name> \
    --pipeline '<json array of aggregation stages>' \
    [--max-chars 10000]
```

Example — count experimental materials with Curie T > 500 K:

```bash
python scripts/query.py aggregate \
    --collection magnetic_materials \
    --pipeline '[{"$match":{"$expr":{"$and":[{"$isNumber":"$Curie"},{"$gt":["$Curie",500]}]},"Experimental":true}},{"$count":"n"}]'
```

### `records` (filter + limit, raw documents)

```bash
python scripts/query.py records \
    --collection <mongo_collection_name> \
    --filter '<json>' \
    [--limit 10] [--max-chars 10000]
```

### `multi` (parallel reads across collections, single shell call)

```bash
python scripts/query.py multi --spec '[
  {"collection": "magnetic_materials",   "pipeline": [{"$count":"n"}]},
  {"collection": "magnetic_anisotropy",  "filter": {"Magnet_type":"Hard"}, "limit": 3}
]'
```

Returns an order-preserved JSON array `[{collection, ok, result|error}, ...]`.
Use when the agent already knows what to ask each dataset and wants parallel
execution without spawning multiple shell calls.

## Truncation contract

When the JSON payload would exceed `--max-chars` (default 10,000), the tool
prepends:

```
[TRUNCATED: result was N chars, showing first M. Narrow your query to get complete results.]
```

If you see this, don't scroll — refine the pipeline (add `$project` to drop
fields, tighten `$match`, or increase selectivity) and run again.

## Error envelope

Failures always look like:

```json
{"error": "TypeName: message", "hint": "actionable suggestion"}
```

Do NOT blindly retry the same command after an error. Read the `hint`; the
most common cases are:

- Invalid JSON in `--pipeline` / `--filter` → fix the quoting (see below).
- Collection name mismatch → check `datasets_loaded[<skill>].collection`.
- Connection error → run `scripts/doctor.py`.

## Shared gotchas (apply to every DataBridge dataset)

### 1. Mixed-type numeric columns

Columns like `Curie`, `Neel`, `(BH_Max)`, etc. store a mix of BSON doubles
and strings (unit-bearing text). `{"$type": "double"}` silently skips the
string values. For numeric comparisons, use `$expr` + `$isNumber`:

```json
{"$match": {"$expr": {"$and": [{"$isNumber": "$Curie"}, {"$gt": ["$Curie", 500]}]}}}
```

For full coverage, also check the sibling string column (e.g. `Curie(Tc)`)
with `$regexFind`.

### 2. Missing values are often NaN doubles, not nulls

`{field: null}` returns 0 on many numeric columns because the missing cells
are BSON NaN doubles. Prefer `$expr` + `$isNumber` (true iff finite) or check
for absence of string content.

### 3. Field names with parentheses, brackets, or spaces

Fields like `(BH_Max)`, `Curie(Tc)`, or `Anisotropy Constant K1` can break
dot-path references inside `$expr`. Use `$getField`:

```json
{"$match": {"$expr": {"$ne": [{"$getField": "(BH_Max)"}, null]}}}
```

### 4. Inconsistent categorical casing and notation

Examples: `FCC` vs `fcc` vs `Face-centered cubic`; `Fd-3m` vs `Fd3m`;
`Semi-Hard` vs `Semi-hard`. Use case-insensitive regex:

```json
{"Space_Group": {"$regex": "^fd[- ]?3m$", "$options": "i"}}
```

### 5. Shell quoting

Nested `$` signs in a pipeline passed via `python -c "..."` lead to
backslash soup. Two reliable patterns:

- Use single quotes around the whole `--pipeline` value (most shells).
- Or write the JSON to a temp file and pass it:
  `--pipeline "$(cat /tmp/pipeline.json)"`

### 6. BSON serialization

Results use `bson.json_util.dumps`, which represents BSON types as extended
JSON:
- `ObjectId` → `{"$oid": "..."}`
- `NaN` → `{"$numberDouble": "NaN"}`
- dates → `{"$date": "..."}`

Don't try to parse these as plain JSON; either read them as strings or feed
them back into `$expr` pipelines directly.

## Permissions summary

- `query.py` — read-only. Safe to auto-run.
- Dataset `ingest.py` scripts — write to MongoDB (NOT to the filesystem).
  Approve once per dataset on first load.
- `bootstrap.sh` — installs Python packages into `~/.databridge/venv` and
  writes `~/.databridge.env` + `~/.databridge/state.json`. Approve once
  at first setup.

## State file: `~/.databridge/state.json`

Single source of truth. Fields:

```json
{
  "schema_version": 1,
  "setup_complete": true,
  "mongo": {
    "uri_source": "/Users/<you>/.databridge.env",
    "db": "databridge",
    "last_verified_at": "2026-05-03T18:00:00Z"
  },
  "datasets_loaded": {
    "<skill-name>": {
      "collection": "<mongo_collection>",
      "row_count": 33668,
      "loaded_at": "2026-05-03T18:15:00Z",
      "source": "<provider>",
      "access": "direct | api_key | gated_registration | manual",
      "checksum": "sha256:..."
    }
  }
}
```

Writers: `bootstrap.sh` creates it, each dataset's `ingest.py` appends its
entry on success (via `lib.register_dataset`), `doctor.py` refreshes on
staleness. Agents should treat it as read-only.

# Acquiring `SS_rxns_80806_dupremoved.json`

**Access tier:** `direct` — the file is a single JSON artifact.

The file was originally produced by literature-scale NLP extraction and
deduplication. If you're working inside the DataBridge monorepo, you may
already have it at:

```
data/magnetic_materials/SS_rxns_80806_dupremoved.json
```

(the path is historical — the file lives under a sibling data folder).

## Steps

1. Locate the JSON. If you don't have it locally, request it from the
   DataBridge maintainer or the paper authors associated with the
   `conditions_forDOI` extraction pipeline.
2. Save or confirm its path, for example:
   ```
   ~/Downloads/SS_rxns_80806_dupremoved.json
   ```
3. Run the ingest:
   ```bash
   python scripts/ingest.py ~/Downloads/SS_rxns_80806_dupremoved.json
   ```

## What to expect

- File size: roughly 250–500 MB (it's a single JSON array with 80,806
  records, each holding nested arrays).
- Top-level shape: `[{record}, {record}, ...]` — a JSON array.
- 7 fields per record: `DOI`, `target`, `precursors`, `target_reaction`,
  `impurity_reaction`, `conditions_forDOI`, `impurity_phase`.
- Memory: the ingest script loads the whole file at once (JSON arrays
  can't be streamed line-by-line without knowing the structure). Budget
  ~2 GB RAM for safety. If this is an issue, ingestion can be adapted to
  use `ijson` — open an issue.

## After ingestion

`ingest.py`:

1. Validates the file shape (top-level list, each record has the 7 fields).
2. Drops any previous `solid_state_synthesis` collection.
3. Inserts the records in chunks of 1,000.
4. Registers the dataset in `~/.databridge/state.json`.

## Troubleshooting

**"Expected a JSON array" / shape error** — the file is probably JSONL
(one record per line). In that case, convert it first:

```bash
jq -s '.' records.jsonl > SS_rxns_80806_dupremoved.json
```

Or, request that ingest.py be extended to handle JSONL (the existing
`JsonParser` in `databridge/catalog/infrastructure/parsers/json_parser.py`
supports both).

**Memory error on large machines** — reduce `CHUNK_SIZE` in `ingest.py`,
or ask for a streaming (`ijson`) variant.

**Connection refused / timeout** — run `databridge-core/scripts/doctor.py`
or re-run `bash databridge-core/scripts/bootstrap.sh`.

## License + attribution

Please cite the original extraction paper and the underlying publications
(the `DOI` column points to each source paper).

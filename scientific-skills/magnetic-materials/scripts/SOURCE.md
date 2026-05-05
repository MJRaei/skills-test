# Acquiring `magnetic_materials.csv`

**Access tier:** `gated_registration` — a free account is required.
**Provider:** nemad — https://nemad.org/

The dataset cannot be downloaded directly; nemad requires sign-in before
exposing the export link. You (the human) complete the download once, then
hand the agent the path.

## Steps

1. Open https://nemad.org/ in your browser.
2. Create a free account if you don't have one, then sign in.
3. Navigate to the magnetic materials table. Export as CSV.
4. Save the file somewhere you can find easily, for example:
   ```
   ~/Downloads/magnetic_materials.csv
   ```
5. Tell the agent (or run directly) the ingest command:
   ```bash
   python scripts/ingest.py ~/Downloads/magnetic_materials.csv
   ```

## What to expect

- File size: roughly 15–25 MB.
- Rows: 33,668 (the skill frontmatter's `source.expected_rows`).
- Columns: 19. If fewer columns are present, the export format has changed
  — see "Troubleshooting" below.

## After ingestion

`ingest.py` does three things:

1. Parses the CSV with dtype preservation so mixed-type columns stay mixed
   (critical for the gotchas this skill documents).
2. Drops any previous `magnetic_materials` collection and loads in chunks.
3. Registers the dataset in `~/.databridge/state.json` so future questions
   skip straight to querying.

Re-running `ingest.py` with a newer export is safe — it replaces the
collection cleanly and updates the row count + checksum in state.json.

## Troubleshooting

**"Column X expected but not found"** — nemad may have renamed or removed a
column in a newer export. Report the issue so we can update the schema in
this SKILL.md.

**"Connection refused on MongoDB"** — run `databridge-core/scripts/doctor.py`
to see the state, or re-run `python databridge-core/scripts/bootstrap.py` if
the URI was wrong.

**Export is JSON/Excel instead of CSV** — the ingest script assumes CSV.
Re-export or convert to CSV before running. The nemad export menu offers
CSV explicitly.

## License + attribution

Please cite nemad and the underlying publications (the `DOI` column points
to each source paper) when using this data.

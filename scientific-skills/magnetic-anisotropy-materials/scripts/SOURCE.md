# Acquiring `magnetic_anisotropy_materials.csv`

**Access tier:** `gated_registration` — a free account is required.
**Provider:** nemad — https://nemad.org/

Same gating as the sibling `magnetic-materials` skill: nemad requires sign-in
before exposing the export. You (the human) complete the download once, then
point the agent at the file.

## Steps

1. Open https://nemad.org/ in your browser.
2. Sign in (or create a free account first).
3. Navigate to the magnetic-anisotropy materials table. Export as CSV.
4. Save it somewhere easy to reference, for example:
   ```
   ~/Downloads/magnetic_anisotropy_materials.csv
   ```
5. Run the ingest:
   ```bash
   python scripts/ingest.py ~/Downloads/magnetic_anisotropy_materials.csv
   ```

## What to expect

- File size: roughly 20–30 MB.
- Rows: 33,916 (`source.expected_rows` in the skill frontmatter).
- Columns: 25.

Some column names contain parentheses or spaces:
`(BH_Max)`, `Anisotropy Constant K1`, `Anisotropy Constant K2`,
`Intrinsic Coercivity`, `Curie(TC)`, `Neel(TN)`. The ingest script preserves
these verbatim so the gotcha section of SKILL.md stays accurate.

## After ingestion

`ingest.py`:

1. Parses the CSV, preserving mixed-type columns as pandas object dtype.
2. Drops any previous `magnetic_anisotropy_materials` collection.
3. Loads the rows in chunks.
4. Registers the dataset (collection, row count, checksum, source tier) in
   `~/.databridge/state.json`.

Re-running with a newer export replaces the collection cleanly.

## Troubleshooting

**"Expected columns missing"** — a nemad schema change. Inspect the CSV
header with `head -1 magnetic_anisotropy_materials.csv` and update
`EXPECTED_COLUMNS` in `ingest.py` (and the Schema table in `SKILL.md`).

**Connection refused / timeout** — run
`databridge-core/scripts/doctor.py`. If it also fails, re-run
`python databridge-core/scripts/bootstrap.py`.

**UnicodeDecodeError** — the nemad export is UTF-8; if the file isn't,
re-export. The µ / Å / θ characters in unit strings require UTF-8.

## License + attribution

Please cite nemad and the underlying publications (the `DOI` column points
to each source paper).

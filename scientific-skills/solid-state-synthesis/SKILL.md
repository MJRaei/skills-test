---
name: solid-state-synthesis
description: Solid-state synthesis dataset with 80,806 deduplicated reaction records extracted from scientific literature. Each record links a target material to its precursors, balanced reaction equations, NLP-extracted synthesis conditions (temperature, time, atmosphere), Materials Project mappings, and any identified impurity phases. Use this dataset to query solid-state synthesis routes, precursor combinations, synthesis conditions, target material formulas, impurity phases, and balanced reaction equations. Trigger phrases: solid-state synthesis, solid state reactions, SS reactions, precursor materials, synthesis conditions, target material, impurity phase, heating conditions, sintering, ball milling, mp_id, mp_eabovehull, conditions_forDOI, target_reaction, impurity_reaction.
source:
  provider: literature_extraction
  url: null
  access: direct
  collection: solid_state_synthesis
  file: SS_rxns_80806_dupremoved.json
  format: json
  expected_rows: 80806
  expected_columns: 7
metadata:
  version: 1.0.0
  generated_date: "2025-01-30"
  requires_skill: databridge-core
---

# solid-state-synthesis

## Overview

80,806 deduplicated solid-state synthesis reaction records extracted from
scientific literature. Each record links a target material to its
precursors, balanced reaction equations, synthesis conditions (NLP-extracted
from paper text), Materials Project mappings, and any identified impurity
phases. The source filename `SS_rxns_80806_dupremoved.json` indicates
duplicates were removed prior to ingestion.

## Source

| Field | Value |
|---|---|
| File | `SS_rxns_80806_dupremoved.json` |
| Format | JSON |
| Records | 80,806 |
| Columns | 7 |
| Tags | reactions, solid-state |
| Access | direct (shipped with repo or downloaded as a single JSON) |

## Loading

If you have the JSON locally:

```bash
python scripts/ingest.py /path/to/SS_rxns_80806_dupremoved.json
```

See `scripts/SOURCE.md` for where to obtain the file. Ingestion is
idempotent — re-running replaces the `solid_state_synthesis` collection.

## Schema

All 7 fields are present in every record. **No top-level nulls**; emptiness
is encoded as empty arrays.

| Column | Type | Empty/Missing | Notes |
|---|---|---|---|
| `DOI` | string | 0.0% | Always present; 57,315 distinct across 80,806 records |
| `target` | array[object] (length 1) | 0.0% | Target material info; `material_formula` null in 12.3%, `mp_id` absent in ~49.4% |
| `precursors` | array[object] | 0.0% | 1–23 per record, mean ≈ 3.08 |
| `target_reaction` | array | 34.9% empty | Balanced equations; empty for records where no equation was computed |
| `impurity_reaction` | array[object] | 94.1% empty | Impurity reactions; rare |
| `conditions_forDOI` | array[object] | 0.6% empty | NLP-extracted synthesis actions; shared across records from the same DOI |
| `impurity_phase` | array[object] | 76.6% empty | Identified impurity phases; max 11 per record |

## Column details

### `DOI`

- 57,315 distinct values; up to 10 records per DOI (one paper, multiple
  reactions). Top: `10.1016/j.intermet.2021.107186` and
  `10.1016/j.jallcom.2005.11.016` with 10 each.

### `target` (length-1 array)

Sub-fields:

- `material_string` — raw string from the paper.
- `material_formula` — parsed formula; **null in 9,914 records (12.3%)** —
  complex composites like `"mullite/SiC whisker/SiC particle multi-composite"`
  couldn't be parsed.
- `additives` — list of species (e.g. dopants).
- `oxygen_deficiency`, `amounts_vars`, `elements_vars`, `composition`.
- `mp_id` — Materials Project ID; **absent in 39,915 records (49.4%)**.
- `mp_eabovehull` — float, present only when `mp_id` exists.

### `precursors` (array, 1–23 elements)

Each object: `material_string`, `material_name`, `material_formula`, `phase`,
`additives`, `oxygen_deficiency`, `is_acronym`, `amounts_vars`,
`elements_vars`, `composition`. No records have an empty precursors array.

### `target_reaction`

Array of tuples: `[target_formula, reaction_dict, null, reaction_string]`.

- `reaction_dict`: `{"left": {reactant: stoich}, "right": {product: stoich}}`.
- `reaction_string`: human-readable equation, e.g. `"1 Nb2O5 + 1 TiO2 == 1 TiNb2O7"`.
- **Empty in 34.9% of records** — no balanced equation computed.

### `impurity_reaction` (array, 0–9)

Mostly empty (94.1% of records). Records with impurity reactions are rare.

### `conditions_forDOI` (array, 0–210, mean ≈ 15.23)

Each object:

- `act_id` (int), `act_type` (enum), `subsent` (char span),
  `subject`, `act_token` (e.g. "sintering", "ball"),
- `temp_values` — list of `{min, max, values, tok_ids, units}`,
- `time_values` — list of `{min, max, values, tok_ids, units}`,
- `env_toks`, `env_ids`, `ref_act` (bool).

`act_type` totals across all records:

| act_type | Count |
|---|---|
| Heating | 373,551 |
| Mixing | 334,360 |
| Starting | 294,810 |
| Purification | 71,956 |
| Shaping | 66,644 |
| Cooling | 61,056 |
| Reaction | 28,281 |

### `impurity_phase` (array, 0–11)

Same object shape as `target` sub-objects. Empty in 76.6% of records.

## Key gotchas

- **No top-level nulls — emptiness is `[]`, not null.** `{field: null}`
  returns 0. Use `{field: {$size: 0}}` or `{"field.0": {$exists: false}}`.
- **`target` is always a length-1 array**, not a plain object. Queries
  must traverse `target.0.<subfield>` or use `$unwind`.
- **`material_formula` is null in 12.3% of targets** — composite materials
  couldn't be parsed. Don't assume every target has a formula.
- **`mp_id` is absent (not null) in ~49.4% of targets.** Use
  `{"target.0.mp_id": {"$exists": true}}` rather than `{"mp_id": {"$ne": null}}`.
- **34.9% of records have no balanced reaction.** Filter with
  `{"target_reaction.0": {"$exists": true}}` before grouping by reaction.
- **`conditions_forDOI` is shared across all reactions from the same DOI.**
  Records with the same DOI will have identical `conditions_forDOI` arrays,
  so aggregating conditions by record over-counts. Deduplicate by DOI first.
- **`temp_values` and `time_values` are deeply nested** inside
  `conditions_forDOI`. Use `$unwind` twice to reach them.
- **Precursor count is wide (1–23).** Outlier high counts may be complex
  systems or NLP extraction artifacts.
- **Impurity reactions are rare (5.9%)** — aggregate statistics over them
  reflect only a small subset.

## Query capabilities

Can answer directly:
- Precursors used to synthesize a given target (by formula or material string).
- Balanced reaction equation for a given synthesis (when present).
- Papers (DOIs) describing synthesis of a specific material.
- Synthesis action types associated with a given reaction.
- Materials Project ID and energy-above-hull for targets that have them.
- Impurity phases reported for a given synthesis.
- Distribution of precursor counts across records.
- Most common synthesis action tokens (e.g., "sintering", "ball milling").

Cannot answer without extra parsing:
- Synthesis temperatures or durations — require traversing nested
  `temp_values` / `time_values` inside `conditions_forDOI`.
- Yield, purity, quantitative phase fractions — not captured.
- Synthesis success/failure labels — not present.
- Crystallographic data (space group, lattice parameters) — not present here.
- Particle size / morphology / microstructure — not present.
- Author, journal, publication year — only DOI is available.

## Example queries

Top 10 most common precursors:

```bash
python query.py aggregate --collection solid_state_synthesis --pipeline '[
  {"$unwind": "$precursors"},
  {"$match": {"precursors.material_formula": {"$ne": null}}},
  {"$group": {"_id": "$precursors.material_formula", "n": {"$sum": 1}}},
  {"$sort": {"n": -1}},
  {"$limit": 10}
]'
```

Lookup all syntheses for a target:

```bash
python query.py records --collection solid_state_synthesis \
    --filter '{"target.0.material_formula": "TiNb2O7"}' --limit 5
```

Count records by target material stability (mp_eabovehull buckets):

```bash
python query.py aggregate --collection solid_state_synthesis --pipeline '[
  {"$match": {"target.0.mp_eabovehull": {"$ne": null}}},
  {"$bucket": {
    "groupBy": "$target.0.mp_eabovehull",
    "boundaries": [0, 0.025, 0.05, 0.1, 0.25, 1.0],
    "default": "above_1_eV",
    "output": {"n": {"$sum": 1}}
  }}
]'
```

Count distinct papers mentioning each synthesis action token:

```bash
python query.py aggregate --collection solid_state_synthesis --pipeline '[
  {"$unwind": "$conditions_forDOI"},
  {"$group": {"_id": "$conditions_forDOI.act_token", "dois": {"$addToSet": "$DOI"}}},
  {"$project": {"token": "$_id", "paper_count": {"$size": "$dois"}, "_id": 0}},
  {"$sort": {"paper_count": -1}},
  {"$limit": 15}
]'
```

Records with a non-empty `impurity_phase`:

```bash
python query.py aggregate --collection solid_state_synthesis --pipeline '[
  {"$match": {"impurity_phase.0": {"$exists": true}}},
  {"$project": {"_id": 0, "DOI": 1, "target": 1, "impurity_phase": 1}},
  {"$limit": 5}
]'
```

## Sample records

```json
[
  {
    "DOI": "10.1002/chem.201905444",
    "target": [{"material_string": "TiNb2O7", "material_formula": "TiNb2O7", "mp_id": "mp-759307", "mp_eabovehull": 0.0068}],
    "precursors": [{"material_string": "TiO2", "material_formula": "TiO2"}, {"material_string": "Nb2O5", "material_formula": "Nb2O5"}],
    "target_reaction": [["TiNb2O7", {"left": {"TiO2": "1", "Nb2O5": "1"}, "right": {"TiNb2O7": "1"}}, null, "1 Nb2O5 + 1 TiO2 == 1 TiNb2O7"]],
    "impurity_reaction": [], "impurity_phase": [],
    "conditions_forDOI": [{"act_id": 8, "act_type": "Starting", "act_token": "fabricated"}]
  },
  {
    "DOI": "10.1039/C5TA02263K",
    "target": [{"material_string": "MoS3", "material_formula": "MoS3", "mp_id": "mp-1239169", "mp_eabovehull": 0.303}],
    "precursors": [{"material_string": "Mo", "material_formula": "Mo"}, {"material_string": "S", "material_formula": "S"}],
    "target_reaction": [], "impurity_reaction": [], "impurity_phase": [],
    "conditions_forDOI": [{"act_id": 11, "act_type": "Starting", "act_token": "prepared"}, {"act_id": 13, "act_type": "Mixing", "act_token": "ball"}]
  },
  {
    "DOI": "10.1016/j.matchar.2022.112001",
    "target": [{"material_string": "Mo5SiB2", "material_formula": "Mo5SiB2", "mp_id": "mp-4984", "mp_eabovehull": 0.009}],
    "precursors": [{"material_string": "Mo", "material_formula": "Mo"}, {"material_string": "Si", "material_formula": "Si"}],
    "target_reaction": [["Mo5SiB2", {"left": {"Mo": "5", "Si": "1", "B": "2"}, "right": {"Mo5SiB2": "1"}}, null, "2 B + 5 Mo + 1 Si == 1 Mo5SiB2"]],
    "impurity_reaction": [],
    "impurity_phase": [{"material_string": "MoB", "material_formula": "MoB", "mp_id": "mp-1890", "mp_eabovehull": 0.0}],
    "conditions_forDOI": [{"act_id": 5, "act_type": "Starting", "act_token": "fabricated"}, {"act_id": 9, "act_type": "Heating", "act_token": "sintering"}]
  },
  {
    "DOI": "10.1111/j.1551-2916.2007.01726.x",
    "target": [{"material_string": "mullite/SiC whisker/SiC particle multi-composite (MS15W10P)", "material_formula": null}],
    "precursors": [{"material_string": "Al2O3", "material_formula": "Al2O3"}, {"material_string": "SiC", "material_formula": "SiC"}],
    "target_reaction": [], "impurity_reaction": [], "impurity_phase": [],
    "conditions_forDOI": [{"act_id": 25, "act_type": "Shaping", "act_token": "pressed"}]
  }
]
```

No external documentation was provided for this dataset. The source file
name indicates duplicates were removed prior to ingestion.

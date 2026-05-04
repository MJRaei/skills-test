---
name: magnetic-materials
description: Magnetic materials dataset from nemad with 33,668 records describing magnetic properties (Curie/Néel/Curie-Weiss temperatures, coercivity, magnetization, remanence, susceptibility, magnetic moment) and crystallographic data (crystal structure, lattice parameters, space group) for chemical formulas extracted from publications. Use when querying magnetic transition temperatures, magnetic property values, crystal/space-group structures, or material formulas. Trigger phrases: magnetic materials, nemad, Curie temperature, Tc, Néel temperature, Tn, Curie-Weiss, θp, coercivity, remanence, magnetization, magnetic moment, susceptibility, space group, crystal structure, lattice parameters.
source:
  provider: nemad
  url: https://nemad.org/
  access: gated_registration
  collection: magnetic_materials
  file: magnetic_materials.csv
  format: csv
  expected_rows: 33668
  expected_columns: 19
metadata:
  version: 1.0.0
  generated_date: 2025-01-22
  requires_skill: databridge-core
---

# magnetic-materials

## Overview

A 33,668-record CSV dataset from `nemad` cataloging magnetic materials with
their measured/reported magnetic properties and crystallographic descriptors.
Each record links a chemical formula (`Material_Name`) to a source publication
(`DOI`) and a heterogeneous mix of magnetic and structural fields. Most
"numeric" columns are actually mixed-type (numeric doubles and unit-bearing
strings coexist) and many fields are sparse.

## Source

| Field | Value |
|---|---|
| File | `magnetic_materials.csv` |
| Format | csv |
| Records | 33,668 |
| Columns | 19 |
| Source | nemad |
| Access | gated_registration (free account) |

## Loading

First-time use requires a free registration at `https://nemad.org/` to export
the CSV. Step-by-step in `scripts/SOURCE.md`. Once the file is on disk:

```bash
python scripts/ingest.py /path/to/magnetic_materials.csv
```

Ingestion is idempotent — re-running replaces the `magnetic_materials`
collection and updates `~/.databridge/state.json`.

## Schema

| Column | Type | Nulls % | Notes |
|---|---|---|---|
| `Coercivity` | string | 86.07 | Free-text with units (kA/m, Oe, kOe, A/m) |
| `Crystal_Structure` | string | 25.45 | Categorical; case-inconsistent labels |
| `Curie` | mixed (double+string) | 36.61 | Numeric Curie T; sibling string col also exists |
| `Curie(Tc)` | string | 36.45 | String Curie T with units (K, °C, ranges) |
| `Curie_Weiss` | string | 76.36 | String Curie-Weiss T; some dict-like entries |
| `Curie_Weiss(θp)` | mixed (double+string) | 82.92 | Numeric θp; large negatives present |
| `DOI` | string | 0.04 | Source publication identifier |
| `Experimental` | bool | 0.00 | True/False flag |
| `Lattice_Parameters` | string | 48.46 | Python-dict-style serialized strings |
| `Lattice_Structure` | string | 51.75 | Mixes structural names and space-group symbols |
| `Magnetic_Moment` | string | 68.14 | Free-text with units (μB, μB/f.u., μB/R) |
| `Magnetization` | string | 79.02 | Free-text with units (emu/g, μB/f.u.) |
| `Material_Name` | string | 0.01 | Chemical formula |
| `Neel` | mixed (double+string) | 67.15 | Numeric Néel T; sibling strings exist |
| `Neel(Tn)` | string | 66.95 | String Néel T with units (K, °C) |
| `New_Column_Concatenated` | string | 20.69 | Element-stoichiometry reordering of `Material_Name` |
| `Remanence` | mixed (double+string) | 94.03 | All numeric doubles are NaN; data lives in 2,009 strings |
| `Space_Group` | string | 56.19 | Crystallographic symbol; notation inconsistent |
| `Susceptibility` | string | 95.60 | Free-text mixing numeric, scientific notation, qualitative |

## Column details

### `Coercivity` — 86.07% null

4,689 string values e.g. `'143 kA/m'`, `'17.8 × 10^3 A/m'`, `'3.7 kOe'`.
Mixed SI + CGS unit systems; no common parsed numeric form.

### `Crystal_Structure` — 25.45% null

Top values: Orthorhombic (3,738), Hexagonal (1,806), Cubic (1,755),
Tetragonal (1,694), Rhombohedral (1,280), Monoclinic (1,060), Amorphous
(852), Spinel (538), Perovskite (403), ThCr2Si2-type (374). Case-inconsistent
(`fcc` vs `FCC`); variant duplicates (`ThMn12` vs `ThMn12-type`). Match with
case-insensitive regex.

### `Curie` — 36.61% null, mixed type

Numeric stats over 16,327 valid doubles: min=−525.0, max=1403.15, mean=322.4.
Another 5,016 cells are strings like `'460 K'`, `'299'`, `'565 K'`. Effective
full range across numeric + parsed strings: −525 to 2316. Sibling string
column: `Curie(Tc)`.

### `Curie(Tc)` — 36.45% null

21,395 strings, e.g. `'336.24 K'`, `'312 K'`, `'118°C'`, `'750-800 K'`.
Mixes Kelvin and Celsius; ranges and uncertainties present.

### `Curie_Weiss` — 76.36% null

7,959 strings, e.g. `'4.1 °C'`, `'334.6 K'`, `'-39.89 K'`. Some entries are
dict-like: `"{'Temperature': {'H_parallel_100': -590, ...}, 'Unit': 'K'}"`.

### `Curie_Weiss(θp)` — 82.92% null, mixed type

Numeric stats over 5,749 doubles: min=−5130.0, max=1651.0. 2,083 additional
string values. Large negative θp indicates antiferromagnetic correlations.

### `DOI` — 0.04% null

11,122 distinct DOIs across 33,668 records — multiple records typically
share a source paper.

### `Experimental` — 0% null

30,706 true (91.2%), 2,962 false (8.8%).

### `Lattice_Parameters` — 48.46% null

17,351 Python-dict-style strings, e.g. `"{'a': '4.662Å', 'c': '12.24 Å'}"`,
sometimes `"{'a': 'NA', 'b': 'NA', 'c': 'NA'}"`. Not parsed into structured
fields.

### `Lattice_Structure` — 51.75% null

Top values: Cubic (2,357), Hexagonal (1,711), Tetragonal (1,201),
Orthorhombic (949), Perovskite (623), Pnma (449), Pbnm (307). Mixes
structural names with space-group symbols. Overlaps semantically with
`Crystal_Structure` and `Space_Group`.

### `Magnetic_Moment` — 68.14% null

10,726 strings, e.g. `'4.95 μB/f.u.'`, `'9.89 μB'`, `'1.3–1.7μB/Co'`.
Often Bohr magnetons per formula unit, atom, or sublattice.

### `Magnetization` — 79.02% null

7,064 strings mixing emu/g and μB/f.u., e.g. `'95 emu/g'`, `'0.43 μB/f.u.'`.

### `Material_Name` — 0.01% null

23,656 distinct chemical formulas. Top entries: Gd (111), La0.7Sr0.3MnO3
(95), La0.7Ca0.3MnO3 (77), Sr2FeMoO6 (68).

### `Neel` — 67.15% null, mixed type

Numeric stats over 7,870 doubles: min=−9.0, max=1073.0, mean=116.7. 3,190
additional strings (some contain multiple temperatures: `'25 K, 19 K'`).
Effective full range: −14 to 2202. Sibling: `Neel(Tn)`.

### `Neel(Tn)` — 66.95% null

11,127 strings, e.g. `'42 K'`, `'320 °C'`. Mixes Kelvin and Celsius.

### `New_Column_Concatenated` — 20.69% null

26,703 strings, e.g. `'O3.0Mn1Sr0.5Nd0.5'`, `'Si11.0Gd3.0Pt23.0'`. Derived
element-stoichiometry form of `Material_Name`.

### `Remanence` — 94.03% null, effectively string-only

**Every numeric double is NaN.** Real data lives in 2,009 strings, e.g.
`'3.75 emu/g'`, `'9%'`, `'4.5 μB'`. Effective range from regex-parsed leading
numbers: 0.0 to 7920.0 over 1,899 parsed values. Mixed units (emu/g, μB, %).

### `Space_Group` — 56.19% null

Top values: Pnma (1,413), I4/mmm (1,049), Pbnm (766), P63/mmc (641),
Fd-3m (485), R-3c (448), Fd3m (407), R-3m (368), P6/mmm (346).
Inconsistent notation: `Fd-3m` vs `Fd3m`, `Fm-3m` vs `Fm3m`, `R-3c` vs
`R3̄c` all appear. Use case-insensitive matching.

### `Susceptibility` — 95.60% null

1,480 strings, heterogeneous: `'-6.3'`, `'2.58 × 10^-4 emu/mol'`,
`'Spin-glass behavior with T_f = 29 K'`. Not directly numeric-parseable.

## Key gotchas

- **Mixed-type numeric columns** (`Curie`, `Curie_Weiss(θp)`, `Neel`,
  `Remanence`) store BSON doubles AND BSON strings. `$type: "double"`
  filters silently skip the strings. Always combine numeric + `$regexFind`
  over strings, or check the sibling string column (`Curie(Tc)`, `Neel(Tn)`).
- **`Remanence` is effectively string-only** — numeric queries return
  nothing. Only the 2,009 strings hold data.
- **Missing values are BSON NaN doubles, not BSON nulls.** `{field: null}`
  returns 0. Use `$expr` + `$isNumber` or test for absent string content.
- **Effective ranges exceed numeric-only stats** (Curie up to 2316 once
  strings are parsed; Néel −14 to 2202). Treat effective ranges as
  authoritative.
- **Unit heterogeneity across rows** — K vs °C; emu/g vs μB/f.u.;
  Oe/kOe/kA/m/A/m for coercivity. Cross-record numeric comparisons require
  unit normalization.
- **Three overlapping crystallographic columns** (`Crystal_Structure`,
  `Lattice_Structure`, `Space_Group`). Choose the right one per query and
  consider checking all three.
- **Inconsistent categorical labels** — case (`FCC`/`fcc`), abbreviation
  (`cub`, `hex`), notation (`Fd-3m`/`Fd3m`, `ThMn12`/`ThMn12-type`).
- **Multiple records per DOI and per `Material_Name`** — don't assume one
  row per material or paper.

## Query capabilities

Can answer directly:
- Filter by chemical formula (`Material_Name`) or element stoichiometry
  (`New_Column_Concatenated`).
- Find materials with Curie / Néel / Curie-Weiss temperatures in a numeric
  range (caveat: also check the sibling string column for completeness).
- Filter by `Crystal_Structure`, `Lattice_Structure`, `Space_Group` with
  case-insensitive regex.
- Filter experimental vs non-experimental via `Experimental`.
- Count records per DOI or per `Material_Name`.
- Inspect raw string values for unit-bearing columns.

Cannot answer without extra parsing:
- Unit-normalized comparisons of coercivity, magnetization, magnetic moment,
  remanence, susceptibility (all unit-bearing text).
- Structured queries on individual lattice parameters a, b, c, α, β, γ
  (stored as Python-dict text).
- Numeric aggregation on `Remanence` directly (all NaN).
- Anisotropy, saturation magnetization at specified field, hysteresis loops —
  not columns here. See `magnetic-anisotropy-materials` instead.

## Example queries

All examples assume the databridge-core query tool is on
`~/.cursor/skills/databridge-core/scripts/query.py` (path differs per host).

Count materials with Curie > 500 K that are experimental:

```bash
python query.py aggregate --collection magnetic_materials --pipeline '[
  {"$match": {"$expr": {"$and": [{"$isNumber": "$Curie"}, {"$gt": ["$Curie", 500]}]}, "Experimental": true}},
  {"$count": "n"}
]'
```

Top 10 most-cited materials (by DOI count):

```bash
python query.py aggregate --collection magnetic_materials --pipeline '[
  {"$match": {"Material_Name": {"$ne": null}}},
  {"$group": {"_id": "$Material_Name", "n": {"$sum": 1}, "dois": {"$addToSet": "$DOI"}}},
  {"$project": {"material": "$_id", "records": "$n", "distinct_dois": {"$size": "$dois"}}},
  {"$sort": {"records": -1}},
  {"$limit": 10}
]'
```

Fetch raw records for a specific formula:

```bash
python query.py records --collection magnetic_materials \
    --filter '{"Material_Name": "Fe3O4"}' --limit 5
```

Find materials with Pnma space group (accepting notation variants):

```bash
python query.py aggregate --collection magnetic_materials --pipeline '[
  {"$match": {"Space_Group": {"$regex": "^pnma$", "$options": "i"}}},
  {"$project": {"_id": 0, "Material_Name": 1, "Curie": 1, "Neel": 1, "DOI": 1}},
  {"$limit": 20}
]'
```

## Sample records

```json
[
  {
    "Crystal_Structure": "Perovskite", "DOI": "10.1016/j.jmmm.2006.10.217",
    "Experimental": true, "Magnetic_Moment": "150μB", "Material_Name": "Nd0.5Sr0.5MnO3",
    "Neel": 50.0, "Neel(Tn)": "50K", "New_Column_Concatenated": "O3.0Mn1Sr0.5Nd0.5"
  },
  {
    "Coercivity": "43-62 Oe", "Crystal_Structure": "Spinel", "Curie": 858.15,
    "Curie(Tc)": "585 °C", "DOI": "10.1016/j.jmmm.2017.05.018", "Experimental": true,
    "Lattice_Structure": "Cubic", "Magnetization": "32-58 emu/g",
    "Material_Name": "Fe3O4", "New_Column_Concatenated": "O4.0Fe3.0"
  },
  {
    "Crystal_Structure": "Face-centered cubic", "Curie": 42.0, "Curie(Tc)": "42±1 K",
    "DOI": "10.1016/j.jmmm.2014.01.010", "Experimental": true,
    "Lattice_Parameters": "{'a': '16.8249(7) Å'}", "Lattice_Structure": "Cubic",
    "Magnetic_Moment": "7.00±0.10 μB/R", "Material_Name": "Gd3Pt23Si11",
    "New_Column_Concatenated": "Si11.0Gd3.0Pt23.0", "Space_Group": "Fm3̄m"
  },
  {
    "Crystal_Structure": "Rhombohedral", "Curie_Weiss": "109 K", "Curie_Weiss(θp)": 109.0,
    "DOI": "10.1016/j.jmmm.2004.09.118", "Experimental": true,
    "Magnetic_Moment": "4.31 μB", "Material_Name": "LaMn0.70Fe0.30O3",
    "New_Column_Concatenated": "O3.0Mn0.7Fe0.3La1", "Space_Group": "R-3c"
  }
]
```

Source attribution: `nemad`. No external documentation was provided with the
original export.

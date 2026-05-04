---
name: magnetic-anisotropy-materials
description: Magnetic anisotropy dataset from nemad with 33,916 records covering magnetic properties (coercivity, saturation magnetization, remanence, anisotropy constants K1/K2, BH_Max, anisotropy field/energy), structural descriptors (crystal structure, lattice parameter, space group), thermal transitions (Curie, Néel, Curie-Weiss), and categorical metadata (magnet type, magnetic type, material type, substrate, thickness) for bulk, thin-film, nanoparticle, and other material forms. Use when querying magnetic anisotropy, hard vs soft magnets, coercivity, saturation magnetization, or thin-film / nanoparticle magnetic data. Trigger phrases: magnetic anisotropy, coercivity, saturation magnetization, remanence, BH_Max, anisotropy constant, anisotropy field, anisotropy energy, Curie temperature, Néel temperature, hard magnet, soft magnet, ferromagnetic, antiferromagnetic, ferrimagnetic, nemad, crystal structure, space group, lattice parameter, thin film magnet, bulk magnet, nanoparticle magnet.
source:
  provider: nemad
  url: https://nemad.org/
  access: gated_registration
  collection: magnetic_anisotropy_materials
  file: magnetic_anisotropy_materials.csv
  format: csv
  expected_rows: 33916
  expected_columns: 25
metadata:
  version: 1.0.0
  generated_date: 2025-07-10
  requires_skill: databridge-core
---

# magnetic-anisotropy-materials

## Overview

33,916 records of magnetic-anisotropy materials from `nemad`, drawn from
19,672 distinct publications and covering 19,336 distinct material names.
Captures coercivity, saturation magnetization, anisotropy constants, crystal
structure, and transition temperatures for bulk / thin-film / nanoparticle /
2D / nanowire forms. 91.9% of records are experimental.

## Source

| Field | Value |
|---|---|
| File | `magnetic_anisotropy_materials.csv` |
| Format | csv |
| Records | 33,916 |
| Columns | 25 |
| Source | nemad |
| Access | gated_registration (free account) |

## Loading

```bash
python scripts/ingest.py /path/to/magnetic_anisotropy_materials.csv
```

Step-by-step acquisition in `scripts/SOURCE.md`. Ingestion is idempotent —
re-running replaces the `magnetic_anisotropy_materials` collection and
updates `~/.databridge/state.json`.

## Schema

| Column | Type | Nulls % | Notes |
|---|---|---|---|
| `(BH_Max)` | mixed (double+string) | 91.50 | Field name has parentheses — use `$getField`. Values are dict-like strings. |
| `Anisotropy Constant K1` | mixed | 78.56 | Space in name. Dict-like strings; may contain multi-measurements. |
| `Anisotropy Constant K2` | mixed | 96.65 | Space in name. Dict-like strings; some `'N/A'`. |
| `Anisotropy_Energy` | mixed | 96.50 | All numeric entries are NaN; data lives in dict-like strings. |
| `Anisotropy_Field` | mixed | 91.52 | Dict-like strings. |
| `Coercivity` | mixed | 50.83 | Most-populated property column. Units vary (A/m, MA/m, T, kOe, Oe, kA/m). |
| `Crystal_Structure` | mixed | 35.75 | Strings; inconsistent naming (FCC vs Face-centered cubic). |
| `Curie(TC)` | mixed | 73.27 | Plain strings with K or °C. |
| `Curie_Weiss` | mixed | 93.20 | Numeric column is all-NaN; strings with unit K. |
| `DOI` | string | 0.00 | Fully populated; 19,672 distinct. |
| `Experimental` | bool | 0.00 | 91.9% true, 8.1% false. |
| `Intrinsic Coercivity` | mixed | 98.43 | Space in name. Very sparse dict-like strings. |
| `Lattice_Parameter` | mixed | 59.81 | Dict-like strings encoding a, b, c. |
| `Lattice_Structure` | mixed | 56.49 | Strings; inconsistent naming. |
| `Magnet_type` | mixed | 14.36 | Soft / Hard / Hard/Soft / Semi-Hard / Semi-hard. |
| `Magnetic_type` | mixed | 0.05 | Nearly complete; top value Ferromagnetic. |
| `Material_Density` | mixed | 88.00 | Strings with units (e.g. `'7.6 g/cm^3'`). |
| `Material_Name` | string | 0.00 | Fully populated; 19,336 distinct. |
| `Material_Type` | mixed | 0.06 | Bulk / Thin Film / 2D Material / Nanoparticle / etc. |
| `Neel(TN)` | mixed | 82.86 | Numeric column all-NaN; strings with unit K. |
| `Remanence_Magnetization` | mixed | 74.72 | Dict-like strings; units T, kG, emu/g. |
| `Saturation_Magnetization` | mixed | 47.22 | Second most-populated property. Units emu/g, Am²/kg; multi-value possible. |
| `Space_Group` | mixed | 64.46 | Inconsistent notation (Fd-3m vs Fd3m). |
| `Substrate` | mixed | 78.38 | Numeric column all-NaN; strings like `'MgO (0 0 1)'`. |
| `Thickness` | mixed | 78.85 | Numeric column all-NaN; strings with units (nm, µm); some ranges. |

## Column details

### `(BH_Max)` — 91.50% null

2,884 non-null dict-like strings, e.g. `{'Value': '36.71', 'Units': 'MGsOe', 'Temperature': 'NA'}`.
**Field name begins with `(`** — this breaks normal `$` operator references.
Use `$getField: "(BH_Max)"` in `$expr`.

### `Anisotropy Constant K1` — 78.56% null

7,272 non-null dict-like strings, e.g.
`{'Value': '840, 832', 'Units': 'J/m^3', 'Type': 'NA', 'Temperature': '20K, 300K'}`.
Multiple values and temperatures can appear in a single cell, separated by
commas. **Field name has a space** — use bracket/getField syntax as needed.

### `Anisotropy Constant K2` — 96.65% null

1,138 non-null dict-like strings. Some entries have `'N/A'` as the value
(the cell is populated but the measurement is absent).

### `Anisotropy_Energy` — 96.50% null

1,187 non-null dict-like strings; many have `'N/A'` as the value. Schema types
this as float64 but all numeric entries are NaN.

### `Anisotropy_Field` — 91.52% null

2,876 non-null dict-like strings, e.g. `{'Value': '8.6', 'Units': 'T', 'Type': 'NA', 'Temperature': 'NA'}`.

### `Coercivity` — 50.83% null

16,675 non-null dict-like strings. Observed units: A/m, MA/m, T, kOe, Oe,
kA/m. **Unit normalization required for numeric comparison.**

### `Crystal_Structure` — 35.75% null

Top values: Cubic (3,560), Hexagonal (3,340), Tetragonal (2,432),
Orthorhombic (1,992), Cubic Spinel (1,738), Spinel (1,274), Monoclinic
(979), Rhombohedral (851), Trigonal (520), Amorphous (517). Inconsistent
naming overlaps with `Lattice_Structure`.

### `Curie(TC)` — 73.27% null

9,065 plain strings with units, e.g. `'580 K'`, `'800 °C'`. Conversion
required for cross-record comparison.

### `Curie_Weiss` — 93.20% null

2,307 non-null strings, e.g. `'360K'`, `'-142 K'`. All numeric entries NaN.

### `DOI` — 0% null

Fully populated; 19,672 distinct. Multiple records per paper common.

### `Experimental` — 0% null

true=31,183 (91.9%), false=2,733 (8.1%).

### `Intrinsic Coercivity` — 98.43% null

532 non-null dict-like strings, e.g. `{'Value': '850', 'Units': 'kA/m'}`.
Some have `'N/A'` values. **Field name has a space.**

### `Lattice_Parameter` — 59.81% null

13,632 non-null dict-like strings, e.g. `{'a': '7.4203', 'b': 'NA', 'c': 'NA'}`.

### `Lattice_Structure` — 56.49% null

Top values: Cubic (4,062), Hexagonal (2,238), Orthorhombic (1,465),
Tetragonal (1,211), Monoclinic (574), Face-centered cubic (484), Trigonal
(401), FCC (330), Spinel (325), Rhombohedral (258). "FCC" and "Face-centered
cubic" appear as separate strings for the same structure.

### `Magnet_type` — 14.36% null

Soft (21,384), Hard (7,453), Hard/Soft (95), Semi-Hard (52), Semi-hard (27).
**"Semi-Hard" and "Semi-hard" are distinct values** — queries must match both.

### `Magnetic_type` — 0.05% null

Ferromagnetic (21,850), Antiferromagnetic (6,689), Ferrimagnetic (3,125),
Superparamagnetic (571), Soft Ferromagnetic (380),
Ferromagnetic/Antiferromagnetic (322), Paramagnetic (140), Helimagnetic (83).

### `Material_Density` — 88% null

4,070 strings with units (e.g. `'7.6 g/cm^3'`). Not parsed numerically.

### `Material_Name` — 0% null

19,336 distinct values.

### `Material_Type` — 0.06% null

Bulk (24,938), Thin Film (7,014), 2D Material (708), Nanoparticle (262),
Nanowire (124), Monolayer (113), Multilayer (95), Superlattice (62),
Single Crystal (56), Ultrathin Film (37).

### `Neel(TN)` — 82.86% null

5,813 plain strings with units (e.g. `'222 K'`, `'227K'`). All numeric
entries NaN.

### `Remanence_Magnetization` — 74.72% null

8,572 dict-like strings, e.g. `{'Value': '0.82', 'Units': 'T', 'Temperature': 'NA'}`.
Units: T, kG, emu/g.

### `Saturation_Magnetization` — 47.22% null

17,901 dict-like strings, e.g. `{'Value': '64, 61', 'Units': 'emu/g', 'Temperature': '20K, 300K'}`.
Units: emu/g, Am²/kg. Multi-value entries common.

### `Space_Group` — 64.46% null

Top values: Fd-3m (1,266), P63/mmc (882), Fd3m (731), Pnma (531), I4/mmm
(506), R-3m (371), Pbnm (334), Fm-3m (282), P6/mmm (268), C2/m (222).
**"Fd-3m" and "Fd3m" represent the same space group** but appear as separate
strings.

### `Substrate` — 78.38% null

7,333 plain strings, e.g. `'MgO (0 0 1)'`, `'Si(100)'`. Numeric column all-NaN.

### `Thickness` — 78.85% null

7,172 plain strings with units (nm, µm). Some encode ranges
(e.g. `'0.5 to 5 µm'`). Numeric column all-NaN.

## Key gotchas

- **`(BH_Max)` field name** — leading `(` breaks `$fieldName` references.
  Use `$getField: "(BH_Max)"` inside `$expr`.
- **Field names with spaces** (`Anisotropy Constant K1/K2`,
  `Intrinsic Coercivity`) — some query environments need
  `{"Anisotropy Constant K1": {...}}` quoted carefully.
- **All float64 columns are entirely NaN** (`Anisotropy_Energy`,
  `Curie_Weiss`, `Neel(TN)`, `Substrate`, `Thickness`). Numeric queries
  return nothing; parse the string values instead.
- **Property values are dict-like strings, not numbers** — `Coercivity`,
  `Saturation_Magnetization`, `Remanence_Magnetization`, K1/K2,
  `Anisotropy_Field`, `Anisotropy_Energy`, `Intrinsic Coercivity`, `(BH_Max)`
  all store `{'Value': ..., 'Units': ..., 'Temperature': ...}` as text.
  Numeric extraction requires string parsing.
- **Heterogeneous units** — Coercivity uses 6+ systems (A/m, MA/m, T, kOe,
  Oe, kA/m); Remanence uses T, kG, emu/g; Saturation uses emu/g, Am²/kg.
- **Temperature units** — `Curie(TC)` mixes K and °C; `Curie_Weiss` uses K.
- **Multiple measurements per cell** — K1 and Saturation often contain
  comma-separated values with matching temperature lists.
- **`'N/A'` string values** — K2, Anisotropy_Energy, Intrinsic Coercivity,
  and Anisotropy_Field may have `'N/A'` as the Value key (the field is
  present but the measurement is absent). Filter these out explicitly.
- **Overlapping structural columns** — `Crystal_Structure` vs
  `Lattice_Structure`; `FCC` vs `Face-centered cubic`; `Fd-3m` vs `Fd3m`.
  Normalize before grouping.
- **`Magnet_type` case** — `Semi-Hard` vs `Semi-hard`. Match case-insensitively.
- **Thickness ranges** — some entries encode `'0.5 to 5 µm'` rather than
  a single value.

## Query capabilities

Can answer directly:
- Magnetic properties (coercivity, saturation magnetization, remanence,
  BH_Max, anisotropy constants) for a named material (as raw strings).
- Filter by `Magnetic_type` (Ferromagnetic, Antiferromagnetic, Ferrimagnetic,
  etc.) or `Magnet_type` (Hard, Soft).
- Crystal structure or space group of a material (with variant-aware regex).
- Records by `Material_Type` (Bulk, Thin Film, Nanoparticle, etc.).
- Substrate and thickness reported for thin-film entries.
- DOI lookups and paper → records fan-out.
- Lattice parameters as raw strings.

Cannot answer without extra parsing:
- Numeric range queries over any property column (dict-like strings must be
  parsed first).
- Unit-normalized comparisons (e.g., "coercivity > 1 T" requires unit
  conversion).
- Temperature-dependent property queries when cells contain multi-value
  pairs.
- `(BH_Max)` queries without field-name-aware operators.
- Reliable deduplication of space groups without normalization.

## Example queries

Count hard magnets that are Ferromagnetic:

```bash
python query.py aggregate --collection magnetic_anisotropy_materials --pipeline '[
  {"$match": {"Magnet_type": "Hard", "Magnetic_type": "Ferromagnetic"}},
  {"$count": "n"}
]'
```

Thin-film materials on Si substrate with coercivity reported:

```bash
python query.py aggregate --collection magnetic_anisotropy_materials --pipeline '[
  {"$match": {
    "Material_Type": "Thin Film",
    "Substrate": {"$regex": "^Si", "$options": "i"},
    "Coercivity": {"$ne": null}
  }},
  {"$project": {"_id": 0, "Material_Name": 1, "Substrate": 1, "Thickness": 1, "Coercivity": 1}},
  {"$limit": 20}
]'
```

Query records with a non-null BH_Max (handles the `(BH_Max)` field name):

```bash
python query.py aggregate --collection magnetic_anisotropy_materials --pipeline '[
  {"$match": {"$expr": {"$ne": [{"$getField": "(BH_Max)"}, null]}}},
  {"$project": {"_id": 0, "Material_Name": 1, "BH": {"$getField": "(BH_Max)"}}},
  {"$limit": 10}
]'
```

Top 15 space groups (normalizing notation variants):

```bash
python query.py aggregate --collection magnetic_anisotropy_materials --pipeline '[
  {"$match": {"Space_Group": {"$ne": null}}},
  {"$addFields": {"sg_norm": {"$toLower": {"$replaceAll": {"input": "$Space_Group", "find": "-", "replacement": ""}}}}},
  {"$group": {"_id": "$sg_norm", "n": {"$sum": 1}}},
  {"$sort": {"n": -1}},
  {"$limit": 15}
]'
```

## Sample records

```json
[
  {
    "(BH_Max)": "{'Value': '8.7', 'Units': 'MGOe', 'Temperature': 'NA'}",
    "Coercivity": "{'Value': '10.3', 'Units': 'kOe', 'Temperature': 'NA'}",
    "DOI": "10.1016/j.jallcom.2009.04.121", "Experimental": true,
    "Magnet_type": "Hard", "Magnetic_type": "Ferromagnetic",
    "Material_Name": "Nd9.5Fe72.5Ti3B15", "Material_Type": "Bulk",
    "Remanence_Magnetization": "{'Value': '6.5', 'Units': 'kG', 'Temperature': 'NA'}"
  },
  {
    "Anisotropy Constant K1": "{'Value': '932.9', 'Units': 'erg/cm^3', 'Type': '', 'Temperature': ''}",
    "Coercivity": "{'Value': '27.40', 'Units': 'Oe', 'Temperature': ''}",
    "Crystal_Structure": "Cubic", "DOI": "10.1016/j.jmmm.2016.09.029",
    "Experimental": true, "Lattice_Parameter": "{'a': '8.381', 'b': '', 'c': ''}",
    "Magnet_type": "Soft", "Magnetic_type": "Ferromagnetic",
    "Material_Density": "5.387 g/cm^3", "Material_Name": "Ni0.3Cu0.2Zn0.5Fe2O4",
    "Material_Type": "Bulk", "Space_Group": "Fd-3m",
    "Saturation_Magnetization": "{'Value': '69.13', 'Units': 'emu/g', 'Temperature': ''}"
  },
  {
    "(BH_Max)": "{'Value': '15', 'Units': 'MGOe', 'Temperature': 'Room Temperature'}",
    "Coercivity": "{'Value': '15.5', 'Units': 'kOe', 'Temperature': 'Room Temperature'}",
    "Curie(TC)": "800 °C", "DOI": "10.1016/j.jmmm.2004.11.383",
    "Experimental": true, "Magnet_type": "Hard", "Magnetic_type": "Ferromagnetic",
    "Material_Name": "SmCo", "Material_Type": "Thin Film",
    "Remanence_Magnetization": "{'Value': '8.5', 'Units': 'kG', 'Temperature': 'Room Temperature'}",
    "Substrate": "Si(100)", "Thickness": "0.5 to 5 µm"
  }
]
```

Source attribution: `nemad`. No external documentation was provided.

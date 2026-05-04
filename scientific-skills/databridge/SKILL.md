---
name: databridge
description: >-
  Top-level overview of the DataBridge scientific-data skill set. A collection
  of curated material-science datasets hosted in the MongoDB, queryable by AI
  agents via helper scripts. Use when the user asks what DataBridge is, what
  data is available, how to set it up, or wants help choosing which dataset
  to query. Trigger phrases: databridge, what is databridge, what datasets do
  you have, available datasets, databridge skills, material science data,
  mongodb dataset catalog, list datasets.
metadata:
  version: 1.0.0
---

# DataBridge

A set of installable Agent Skills for querying curated material-science datasets
that live in the user's own MongoDB. Each dataset skill documents its schema
and gotchas; a shared `databridge-core` skill provides the query and ingest
tools the agent actually calls.

## What you need once

1. **MongoDB 7.0+** running locally, in Docker, or remotely (Atlas).
2. **Python 3.11+** — used only by DataBridge's isolated venv, does not touch
   the user's system packages.
3. **One-time bootstrap:**

   ```bash
   bash databridge-core/scripts/bootstrap.sh
   ```

   Creates `~/.databridge/venv`, prompts for the MongoDB URI, writes
   `~/.databridge.env`, and initializes `~/.databridge/state.json`.

No LLM API key is required — the agent that's already running in your IDE
(Cursor, Claude Code, Codex, Gemini CLI, etc.) handles all reasoning.

## Available datasets

Each entry below is also installed as its own skill — the agent picks the
right one automatically based on what you ask.

| Skill                           | What's in it                                                                                                                         | Records | Source                | Access              |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------- | --------------------- | ------------------- |
| `magnetic-materials`            | Curie / Néel / Curie-Weiss temperatures, crystal structures, space groups, magnetic moments for chemical formulas                    | 33,668  | nemad                 | Registration (free) |
| `magnetic-anisotropy-materials` | Coercivity, saturation magnetization, BH_Max, anisotropy constants, magnet/magnetic type for bulk / thin-film / nanoparticle magnets | 33,916  | nemad                 | Registration (free) |
| `solid-state-synthesis`         | Solid-state reaction records: target + precursors, balanced equations, NLP-extracted synthesis conditions, Materials Project links   | 80,806  | literature extraction | Direct              |

Full schema, gotchas, and example queries live in each dataset's own
`SKILL.md`. Acquisition steps are in each dataset's `scripts/SOURCE.md`.

## How a question becomes an answer

```
User asks → agent picks up the relevant dataset skill based on its
             frontmatter description and trigger phrases
          → agent reads ~/.databridge/state.json
              - missing / setup_complete=false → bootstrap prompt
              - dataset not loaded → show scripts/SOURCE.md, run ingest.py
              - dataset ready → skip checks
          → agent calls databridge-core/scripts/query.py
          → agent parses JSON, answers the user
```

Fine-grained iteration (agent writes a pipeline, sees truncation or error,
refines) happens inside the `query.py` tool loop. The agent iterates in
shell, not through multiple LLM turns of "should I check setup again?".

## Three tiers of query access

All implemented in `databridge-core/scripts/query.py`:

- **`aggregate`** — single dataset, full MongoDB aggregation pipeline.
  The main tool for exploratory questions against one collection.
- **`records`** — filtered raw documents with `--limit`. Quick sample
  fetches, DOI lookups, etc.
- **`multi`** — one call that fans out several queries across collections in
  parallel. Use when the agent already knows what to ask each dataset and
  wants to avoid sequential shell calls.

See `databridge-core/SKILL.md` for concrete invocation examples and the
response / error envelope contract.

## Loading a dataset

For datasets with **direct** access (e.g., solid-state-synthesis): the agent
can run `scripts/ingest.py` directly after confirming with you.

For datasets behind **registration** (e.g., nemad): the agent shows you the
steps from `scripts/SOURCE.md`, you download the file, tell the agent the
path, and it runs `scripts/ingest.py <path>` for you. The dataset is
registered in `state.json` so future questions skip straight to querying.

All ingestion is idempotent — re-running `ingest.py` with a fresh file
drops and reloads the collection cleanly.

## Privacy + data handling

- Your MongoDB URI and any credentials live in `~/.databridge.env` on your
  machine only. Nothing in this skill set ever phones home.
- `~/.databridge/state.json` tracks which datasets you've loaded. It is
  local; no telemetry.
- Dataset contents stay in your MongoDB. Agents query it through
  `query.py`; data leaves your machine only when you paste it into a chat.

## When to extend

To add a new dataset:

1. Create a new skill folder at the top of `scientific-skills/`.
2. Write `SKILL.md` describing the schema and gotchas.
3. Write `scripts/SOURCE.md` explaining how to acquire the raw file.
4. Write `scripts/ingest.py` that loads the file into a named MongoDB
   collection and calls `lib.register_dataset(...)` on success.

`databridge-core` stays unchanged — every new dataset reuses the same
orchestration, tool surface, and state contract.

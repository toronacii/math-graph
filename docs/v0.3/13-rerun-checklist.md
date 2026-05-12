# 13 — Extraction Run Checklist

Operational checklist for executing one extraction run. Walk through this
in order. Do not skip steps.

For terminology (run vs rerun vs extension), see
[`09-rerun-architecture.md`](09-rerun-architecture.md).

## Pre-flight

- [ ] Latest `main` checked out, working tree clean.
- [ ] `uv sync` completed.
- [ ] `uv run mkg-validate` returns 0 against current `data/`
      (or current `data/` is empty).
- [ ] Source PDFs under `sources/<work>/chapters/` present and unmodified
      (verify SHA-256 against `sources/<work>/metadata.yml` if recorded).
- [ ] Schema version in `schema/v03.py` (`SCHEMA_VERSION = "0.3.1"`,
      `SUPPORTED_SCHEMA_VERSIONS = ("0.3.0", "0.3.1")`)
      matches the planned run's schema.
- [ ] Extraction templates are present and unchanged:
      - `schema/v03/templates/statement.template.yml`
      - `schema/v03/templates/proof.template.yml`
      - `schema/v03/templates/EXTRACTION_PROMPT.md`

## Snapshot the previous state

- [ ] `uv run mkg-snapshot --label <previous-run-id-or-baseline>`
- [ ] Verify `MANIFEST.yml` and `hashes.txt` were written under
      `generated/snapshots/<label>/`.

## Plan the run

- [ ] Create `docs/v0.3/reruns/<run_id>.plan.md` listing:
      - in-scope sources;
      - in-scope chapters;
      - extraction template version;
      - any ID merges/splits decided up front;
      - acceptance criteria for the run;
      - run mode: **full** (clear + re-extract everything),
        **rerun** (clear + re-extract from older schema), or
        **extension** (keep existing data, add new chapters/sources).

## Clear (skip for extensions)

- [ ] Move current `data/` under `archive/<previous-run-id>/data/`
      (or rely on the snapshot; the archive is optional).
- [ ] Empty `data/statements/` and `data/proofs/`.

## Extract

For each (source, chapter) in the plan:

### Gather inputs

- [ ] Read the extraction prompt:
      `schema/v03/templates/EXTRACTION_PROMPT.md`
      (this is the system-level guidance for producing v0.3 YAML).
- [ ] Read the frozen policies (minimum reading order):
      - `docs/v0.3/policies/02-domain-vocabulary.md`
      - `docs/v0.3/policies/03-ontology-vocabulary.md`
      - `docs/v0.3/policies/04-edge-role-taxonomy.md`
      - `docs/v0.3/policies/05-id-equivalence-policy.md`
      - `docs/v0.3/policies/06-theorem-granularity-policy.md`
      - `docs/v0.3/policies/07-semantic-freeze.md`
- [ ] Generate the context pack for the chapter:
      ```bash
      uv run mkg-context-pack --source <source-key> --chapter <N>
      ```
      Output: `generated/v0.3/context-packs/<source>-chapter-<NN>.md`
- [ ] **Load the context pack into your working context** (read the
      generated `.md` file). This replaces loading raw YAML files —
      the context pack is a compact summary of the entire graph state
      relevant to this chapter. Do NOT skip this step; extracting
      without the context pack leads to duplicate IDs, missed
      dependencies, and inconsistent domain/ontology tags.

### Produce YAML

- [ ] Use the canonical templates as skeletons:
      - **Statements** (all types: axiom, definition, lemma, proposition,
        theorem, corollary, conjecture):
        `schema/v03/templates/statement.template.yml`
        — select the type via the `type:` field; delete unused optional keys.
      - **Proofs**: `schema/v03/templates/proof.template.yml`
- [ ] Process the chapter section by section. For each section:
      1. Identify every statement.
      2. Write one YAML file per statement → `data/statements/<id>.yml`
         (filename MUST match the `id` field).
      3. Identify proof dependencies and create proof nodes →
         `data/proofs/<id>.yml`.
      4. Wire `proved_by` links from statements to their proofs.
- [ ] Every emitted YAML file MUST carry:
      - `schema_version: "0.3.1"`
      - `provenance.rerun_id: "<run_id>"`
      - `provenance.extracted_by: "llm:<model>"` or `"human:<name>"`
      - `provenance.extracted_at: "<ISO-8601 date>"`
      - `language.original: <source-language>` (e.g. `es` for Stewart 7e Spanish)
      - Exactly one `is_original: true` entry per multilingual block,
        in the language matching `language.original`
      - At least one `sources[]` entry with `work`, `chapter`, and a
        locator (`theorem_label`, `page`, `section`, or `locator`)
      - `status: extracted` (no auto-promotion during extraction)
- [ ] Reclassify entity types per `AGENTS.md` "Entity Classification
      Guide".

## Validate

Validation checks the YAML at six layers (see `09-rerun-architecture.md`
for the full table):

- **L1 Schema**: Pydantic models (`schema/v03.py`) validate structure,
  types, enums, ID patterns, LaTeX consistency, i18n rules. Unknown keys
  are rejected (`extra="forbid"`).
- **L2 References**: All cross-references resolve to existing entities.
- **L3 Symmetry**: `proved_by` <-> `proves` are bidirectionally consistent.
- **L4 Acyclicity**: The derivation graph is a DAG.
- **L5 Lifecycle**: Status promotion gates are respected.
- **L6 Completeness**: Non-fatal warnings for under-specification.

Run:

```bash
uv run mkg-validate
# equivalently: uv run python -m scripts.v03.validate
```

- [ ] Exit code is 0.
- [ ] Inspect warnings; resolve or note each one.

## Build

```bash
uv run mkg-build
# equivalently: uv run python -m scripts.v03.build_db
```

- [ ] Command succeeds without errors.
- [ ] Inspect outputs under `generated/v0.3/`:
      - `math_graph.db` — SQLite database
      - `graph.json` — node-link JSON for visualization
      - `node-details.json` — per-node detail blob
      - `graph.graphml` — GraphML export
- [ ] Verify node + edge counts against the plan's expectations.

## Report

- [ ] Per-chapter statistics, structural analysis, and
      weak-dependency reports under `reports/<run_id>/`.
- [ ] Quality distribution per chapter (per-axis, not flat).
- [ ] Status distribution per chapter.

## Compare (skip for first runs with no baseline)

```bash
uv run python -m scripts.diff_graphs \
  --before <prev-snapshot> \
  --after generated/v0.3 \
  --out reports/migration-<prev>-to-<run_id>.md
```

- [ ] Read the diff. Investigate any unexpected removals.

## Audit-grade review

- [ ] Each entity intended for `status: audited` has all required
      quality axes set.
- [ ] All bundled-definition warnings from the audit log are
      resolved or explicitly deferred.
- [ ] Multi-source merges respect the identity criterion in
      `AGENTS.md` (logical equivalence in full generality).
- [ ] All `implicit: true` proof edges have notes.
- [ ] No `quality.dependency_confidence: high` on any proof whose
      `notes` mentions a concept absent from `uses`.

## Snapshot the result

```bash
uv run mkg-snapshot --label <run_id>
```

- [ ] Verify `generated/snapshots/<run_id>/MANIFEST.yml` was written.
- [ ] Commit `generated/snapshots/<run_id>/MANIFEST.yml` (the
      hashes.txt and contents are gitignored — only the manifest is
      versioned, by convention).

## Promote and publish

- [ ] Promote selected entities from `extracted` toward `validated` /
      `audited`, per [`08-status-lifecycle.md`](08-status-lifecycle.md).
- [ ] Sync visualization:
      ```bash
      cp generated/v0.3/graph.json visualization/web/public/graph.json
      cp generated/v0.3/node-details.json visualization/web/public/node-details.json
      ```
- [ ] Tag the commit: `git tag mkg-<run_id>`.
- [ ] Update `CONTEXT.md`.

## Close

- [ ] Open follow-ups for any deferred items.
- [ ] Mark roadmap items in [`12-roadmap.md`](12-roadmap.md) as done.

# 12 — Implementation Roadmap

A pragmatic, ordered list of what to do to land v0.3 cleanly. Items
marked **done** are already completed by this preparation pass.

## Phase 0 — Architecture (this PR)

- [x] `schema/v03.py` — Pydantic models.
- [x] `schema/v03/templates/` — canonical YAML templates.
- [x] `scripts/v03/loader.py` — v0.3 loader (filters by `schema_version`).
- [x] `scripts/v03/validate.py` — layered validator.
- [x] `scripts/v03/build_db.py` — SQLite + graph outputs under `generated/v0.3/`.
- [x] `scripts/snapshot.py` — frozen snapshot creation.
- [x] `scripts/diff_graphs.py` — snapshot diff.
- [x] `scripts/migrate_v02_to_v03.py` — best-effort skeleton migration.
- [x] `generated/snapshots/v0.2/` — initial freeze of v0.2 artifacts.
- [x] `docs/v0.3/` — full design corpus (00 → 13).
- [x] `tests/v03/test_schema.py` — schema invariants.

## Phase 1 — Confirm the architecture (1 PR)

- [ ] Run `scripts/snapshot.py --label v0.2` to backfill
      `hashes.txt` for the v0.2 baseline.
- [ ] Update `AGENTS.md` to point at `docs/v0.3/` and mark the
      Per-Chapter Pipeline as `v0.2-only`.
- [ ] Update `CONTEXT.md` to document the v0.3 transition.
- [ ] Add `scripts/export_schema.py` support for the v0.3 module
      (write `schema/v03.statement.schema.json` and
      `schema/v03.proof.schema.json`).
- [ ] Add `pyproject.toml` console script aliases:
      `mkg-validate`, `mkg-build`, `mkg-snapshot`, `mkg-diff`.

## Phase 2 — Extraction templates and prompt updates (1–2 PRs)

- [ ] Update extraction prompt templates so extractors emit v0.3 YAML.
      Required outputs:
      - `schema_version: "0.3.1"`
      - `language` block + per-text `is_original`
      - `LatexBlock.status`
      - structured `uses` with `role`
      - `domains`, `ambient`, `ontology`
      - `provenance.rerun_id`, `extracted_by`, `extracted_at`
- [ ] Update [`scripts/make_context_pack.py`](../../scripts/make_context_pack.py)
      OR create `scripts/v03/make_context_pack.py` to:
      - read v0.3 SQLite (`generated/v0.3/math_graph.db`);
      - include `domains` and `ambient` columns in retrieval;
      - prefer `theorem_label` over `section` for locator strings;
      - emit a v0.3 templates section;
      - report quality metrics per axis (not a single number).
- [ ] Bundled-definition policy: extractors must NOT emit nodes whose
      ID lists multiple disjoint concepts. Atomic concepts only.

## Phase 3 — Pilot rerun (1 chapter)

- [ ] Pick a small target (recommend Stewart Ch1 — 30 entities, mostly
      definitions and propositions).
- [ ] Run the full rerun cycle from
      [`13-rerun-checklist.md`](13-rerun-checklist.md).
- [ ] Verify the diff report against `generated/snapshots/v0.2/`.
- [ ] Audit-grade review of the 30 entities. Resolve all open issues
      from the 2026-05-11 audit that touch this scope.
- [ ] Snapshot as `v0.3-pilot-stewart-ch1`.

## Phase 4 — Bundled-definition resolution (audit follow-up)

Targets identified by the audit:

- `definition.neighborhood-limit-point-open-closed`
- `definition.segment-interval-cell-ball`
- `definition.field`
- `definition.separated-connected`

Action:

- [ ] In the pilot rerun's outputs, split these into atomic concepts.
- [ ] Record the v0.2 IDs in `provenance.derived_from` of every new
      atomic concept.
- [ ] Update any v0.3 proofs that previously cited the bundled IDs to
      cite the relevant atomic IDs.
- [ ] Mark the bundled v0.2 IDs as retired in the migration report.

## Phase 5 — Full Rudin + Stewart rerun

- [ ] Apply the pipeline from Phase 3 to all chapters.
- [ ] Special attention to:
      - `theorem.connected-subsets-of-r` — completeness import as
        `role: existence` on `definition.least-upper-bound-property`.
      - `proposition.increasing-decreasing-test` — split into
        Stewart strict version and Rudin non-strict version with a
        `generality.relation: stronger_than` edge.
      - `definition.local-maximum`, `definition.local-minimum` —
        record `ambient.structures` correctly per source variant.
      - `theorem.power-series-convergence` — verify proof coverage
        matches sources cited.
- [ ] Snapshot as `v0.3-2026-MM-DD`.
- [ ] Sync `visualization/web/public/graph.json` from v0.3.

## Phase 6 — v0.2 retirement

- [ ] Once v0.3 carries all expected content and the diff report is
      reviewed, delete `schema/models.py` and `scripts/loader.py` (the
      v0.2 module). Move them under `archive/v0.2-code/` if a
      historical reference is desired.
- [ ] Update CI to invoke v0.3 pipelines only.
- [ ] Move `generated/v0.3/` outputs to `generated/graph/` (or keep
      v0.3 as the live path; either is fine, document the choice).

## Out of scope for v0.3

- Proof AST.
- Symbolic LaTeX comparison.
- Closed ontology vocabularies.
- Multi-version coexistence beyond a single migration window.
- Web viewer redesign (the existing viewer renders v0.3 JSON without
  changes; richer per-node panels can land later).

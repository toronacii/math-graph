# 13 — Rerun Preparation Checklist

Operational checklist for executing one rerun. Walk through this in
order. Do not skip steps.

## Pre-flight

- [ ] Latest `main` checked out, working tree clean.
- [ ] `uv sync` completed.
- [ ] `python -m scripts.v03.validate` returns 0 against current
      `data/` (or current `data/` is empty).
- [ ] Source PDFs under `sources/<work>/` present and unmodified
      (verify SHA-256 against `sources/<work>/metadata.yml` if
      recorded).
- [ ] Schema version in `schema/v03.py` (`SCHEMA_VERSION = "0.3.1"`,
      `SUPPORTED_SCHEMA_VERSIONS = ("0.3.0", "0.3.1")`)
      matches the planned `rerun_id`'s schema.

## Snapshot the previous state

- [ ] `python -m scripts.snapshot --label <previous-rerun-id-or-baseline>`
- [ ] Verify `MANIFEST.yml` and `hashes.txt` were written.

## Plan the rerun

- [ ] Create `docs/v0.3/reruns/<rerun_id>.plan.md` listing:
      - in-scope sources;
      - in-scope chapters;
      - extraction template version;
      - any ID merges/splits decided up front;
      - acceptance criteria for the rerun.

## Clear

- [ ] Move current `data/` under `archive/<previous-rerun-id>/data/`
      (or rely on the snapshot; the archive is optional).
- [ ] Empty `data/statements/` and `data/proofs/`.

## Extract

For each (source, chapter) in the plan:

- [ ] Generate the context pack (`scripts/v03/make_context_pack.py`,
      once Phase 2 of the roadmap lands; until then,
      `scripts/make_context_pack.py` against the v0.2 DB is acceptable
      with the caveat that quality fields will be flat).
- [ ] Run extraction. Every emitted YAML MUST carry
      `schema_version: "0.3.1"` (or `"0.3.0"` for legacy continuation),
      the rerun_id in `provenance`, and an
      `is_original: true` entry in every multilingual block.
- [ ] Reclassify entity types per AGENTS.md "Entity Classification
      Guide".

## Validate

- [ ] `python -m scripts.v03.validate` exits 0.
- [ ] Inspect warnings; resolve or note.

## Build

- [ ] `python -m scripts.v03.build_db` succeeds.
- [ ] Inspect `generated/v0.3/graph.json` node + edge counts against
      the plan.

## Report

- [ ] Per-chapter statistics, structural analysis, and
      weak-dependency reports under `reports/<rerun_id>/`.
- [ ] Quality distribution per chapter (per-axis, not flat).
- [ ] Status distribution per chapter.

## Compare

- [ ] `python -m scripts.diff_graphs --before <prev-snapshot>
      --after generated/v0.3 --out reports/migration-<prev>-to-<rerun_id>.md`
- [ ] Read the diff. Investigate any unexpected removals.

## Audit-grade review

- [ ] Each entity intended for `status: audited` has all required
      quality axes set.
- [ ] All bundled-definition warnings from the audit log are
      resolved or explicitly deferred.
- [ ] Multi-source merges respect the identity criterion in
      AGENTS.md (logical equivalence in full generality).
- [ ] All `implicit: true` proof edges have notes.
- [ ] No `quality.dependency_confidence: high` on any proof whose
      `notes` mentions a concept absent from `uses`.

## Snapshot the result

- [ ] `python -m scripts.snapshot --label <rerun_id>`
- [ ] Commit `generated/snapshots/<rerun_id>/MANIFEST.yml` (the
      hashes.txt and contents are gitignored — only the manifest is
      versioned, by convention).

## Promote and publish

- [ ] Promote selected entities from `extracted` toward `validated` /
      `audited`, per [`08-status-lifecycle.md`](08-status-lifecycle.md).
- [ ] Sync visualization:
      `cp generated/v0.3/graph.json visualization/web/public/graph.json`
      and likewise for `node-details.json`.
- [ ] Tag the commit: `git tag mkg-<rerun_id>`.
- [ ] Update `CONTEXT.md`.

## Close

- [ ] Open follow-ups for any deferred items.
- [ ] Mark roadmap items in [`12-roadmap.md`](12-roadmap.md) as done.

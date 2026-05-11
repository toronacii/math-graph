# 09 — Rerun Architecture

A *rerun* is a deterministic re-extraction of MKG against a chosen set
of sources, using a chosen schema version, producing a new snapshot.

v0.3 makes reruns a first-class operation rather than an ad-hoc event.

## Rerun identity

Every rerun has a `rerun_id` (e.g. `v0.3-2026-06-01`). Every entity
produced by a rerun records that id in `provenance.rerun_id`. A rerun
also produces:

- a frozen snapshot under `generated/snapshots/<rerun_id>/`
- a migration / diff report relative to the previous snapshot
- per-chapter reports
- the live `data/` tree is overwritten only if the rerun is accepted

## Rerun phases

```
0. plan         choose sources, chapters, scope, schema version
1. archive      snapshot the current generated/* and data/*
2. clear        wipe data/ (or branch) and prepare workspace
3. extract      run extractors per source / chapter
4. validate     scripts/v03/validate must pass with no errors
5. report       generate per-chapter reports and audits
6. compare      scripts/diff_graphs against previous snapshot
7. review       human review of the diff and reports
8. snapshot     scripts/snapshot --label <rerun_id>
9. publish      promote selected entities to higher statuses
```

Each phase has explicit inputs/outputs:

| Phase    | Inputs                          | Outputs                                  |
|----------|---------------------------------|------------------------------------------|
| plan     | scope notes                     | `docs/v0.3/reruns/<rerun_id>.plan.md`    |
| archive  | current `generated/`, `data/`   | `generated/snapshots/<prev>/...`         |
| clear    | confirmation                    | empty `data/`                            |
| extract  | sources, context packs          | YAML files in `data/`                    |
| validate | `data/`                         | exit code 0; warnings file               |
| report   | SQLite + YAML                   | `reports/<rerun_id>/...`                 |
| compare  | prev + new snapshots            | `reports/migration-<prev>-to-<new>.md`   |
| review   | reports                         | review notes; possibly more extraction   |
| snapshot | `data/`, `generated/`           | `generated/snapshots/<rerun_id>/`        |
| publish  | review approval                 | status promotions in YAML                |

## ID stability policy

When the same mathematical content reappears in v0.3:

- If the content is identical and the v0.2 ID is well-named, **keep
  the ID**.
- If the content has been split into multiple atomic concepts (e.g.
  bundled definitions), **assign new IDs** and record the v0.2 ID in
  `provenance.derived_from` of every new entity that arose from the
  split.
- If the content has been merged, **choose one canonical ID** and
  record the merged-away IDs in `provenance.derived_from`.
- For each retired ID, the *old* entity (if it survives in any form)
  may set `provenance.redirected_to`. If it does not survive, the
  diff report records it as removed and the migration report links
  to the chosen replacement(s).

## Determinism

A rerun is deterministic with respect to:

- the set of source files (verified via SHA-256 in
  `sources/<work>/metadata.yml`);
- the schema version;
- the extraction prompt templates;
- the rerun configuration file.

LLM nondeterminism is acknowledged but not eliminated. Two runs of the
same plan may produce different YAML; both must validate, and the diff
report makes the divergences explicit.

## Snapshot policy

- Snapshots are immutable.
- Snapshots include `MANIFEST.yml` and `hashes.txt` for tamper
  evidence.
- Snapshots may be deleted only with an explicit RFC; they are part
  of the project's audit trail.

## Live-vs-archived

Only the most recent accepted rerun's `generated/v0.3/` is the *live*
graph used by the visualizer and downstream tooling. All previous
snapshots are read-only.

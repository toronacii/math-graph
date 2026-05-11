# 11 — Archival Strategy

## What is archived

Snapshots are immutable copies of project state at a meaningful moment
(end of a rerun, end of a chapter, before a destructive operation).

A snapshot contains:

- `data/` — full YAML at the snapshot time
- `graph/` — `graph.json`, `node-details.json`, SQLite DB
- `exports/` — GraphML
- `reports/` — chapter reports + audits
- `milestones/` — completion records
- `context-packs/` — extraction packs
- `MANIFEST.yml` — provenance metadata
- `hashes.txt` — SHA-256 of every file

## Where they live

```
generated/snapshots/<label>/
```

`<label>` is either a rerun id (`v0.3-2026-06-01`) or a frozen baseline
label (`v0.2`).

## How they are created

```bash
python -m scripts.snapshot --label <label>
```

The script copies the live state into `generated/snapshots/<label>/`
and writes `MANIFEST.yml` + `hashes.txt`.

## What is NOT archived

- The `.venv/`, `node_modules/`, build caches.
- PDFs of source materials (copyright; tracked under `sources/` only
  via metadata).
- The `generated/snapshots/` directory itself (no recursion).

## Retention

- Every accepted rerun produces a snapshot. **Do not delete.**
- Pre-destructive snapshots (e.g., before a `data/` wipe) may be
  deleted only after a successor rerun snapshot exists and has been
  reviewed.
- The frozen `v0.2` baseline is **never** deleted.

## Verification

`hashes.txt` lets any reviewer verify a snapshot was not modified:

```bash
( cd generated/snapshots/v0.2 && shasum -a 256 -c hashes.txt )
```

Modification of a snapshot file invalidates the snapshot. The fix is
to recreate the snapshot under a new label, not to repair the
original.

## Linking snapshots into the audit trail

Every audit report under `reports/audits/` should reference the
snapshot label(s) it analyzed. This makes audit conclusions
reproducible.

## Migration reports

`scripts/diff_graphs` produces a markdown report at
`reports/migration-<before>-to-<after>.md`. These reports are NOT
snapshots themselves; they live under `reports/` and are versioned
with the repo.

## v0.2 baseline (already archived)

`generated/snapshots/v0.2/` contains the frozen v0.2 prototype. Its
manifest is at `generated/snapshots/v0.2/MANIFEST.yml`. The hash
inventory will be generated when `scripts/snapshot.py --label v0.2`
is re-run; until then, the manifest serves as the metadata anchor.

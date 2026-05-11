# MKG v0.3 — Semantic Hardening & Pre-Rerun Architecture

This directory contains the v0.3 architecture documents. v0.3 is the first
**semantically mature** rerun of MKG. The v0.2 graph (Stewart Ch1–11 + Rudin
Ch1–6) is preserved as a frozen prototype baseline and is *not* used by the
live pipeline.

## Reading order

1. [`00-overview.md`](00-overview.md) — what v0.3 is and is not.
2. [`01-schema.md`](01-schema.md) — full v0.3 schema specification.
3. [`02-i18n.md`](02-i18n.md) — multilingual content & originality.
4. [`03-latex-lifecycle.md`](03-latex-lifecycle.md) — formal-text states.
5. [`04-dependency-edges.md`](04-dependency-edges.md) — `uses` vs `depends_on`.
6. [`05-quality-metadata.md`](05-quality-metadata.md) — split confidence axes.
7. [`06-domains-ambient.md`](06-domains-ambient.md) — domains + ambient context.
8. [`07-ontology-tags.md`](07-ontology-tags.md) — semantic kinds & keywords.
9. [`08-status-lifecycle.md`](08-status-lifecycle.md) — promotion lifecycle.
10. [`09-rerun-architecture.md`](09-rerun-architecture.md) — how a rerun runs.
11. [`10-migration-strategy.md`](10-migration-strategy.md) — v0.2 → v0.3 path.
12. [`11-archival-strategy.md`](11-archival-strategy.md) — snapshots & redirects.
13. [`12-roadmap.md`](12-roadmap.md) — what to do, in what order.
14. [`13-rerun-checklist.md`](13-rerun-checklist.md) — operational checklist.

## Policies (semantic freeze — READ BEFORE EXTRACTING)

The architectural docs above describe the schema and pipeline. The
**policies** in [`policies/`](policies/) describe the binding semantic
decisions that govern how the schema is USED — controlled vocabularies,
ID identity, granularity, edge-role taxonomy. They are FROZEN prior to
the first pilot rerun; changing one requires the procedure in
[`policies/07-semantic-freeze.md`](policies/07-semantic-freeze.md).

Start at [`policies/README.md`](policies/README.md) for the index. At a
minimum, every extractor reads policies 02–06 before writing v0.3 YAML;
every reviewer reads 07 before approving a change.

## Code

- `schema/v03.py` — Pydantic v0.3 models.
- `schema/v03/templates/` — canonical YAML templates.
- `scripts/v03/` — loader, validator, builder.
- `scripts/snapshot.py` — frozen snapshot creation.
- `scripts/diff_graphs.py` — snapshot comparison.
- `scripts/migrate_v02_to_v03.py` — best-effort skeleton migration (non-canonical).

## Coexistence

During the migration window, v0.2 (`schema/models.py`) and v0.3 (`schema/v03.py`)
coexist:

- v0.2 reads files **without** a v0.3 `schema_version` marker.
- v0.3 reads files whose `schema_version` is in
  `SUPPORTED_SCHEMA_VERSIONS` (currently `{"0.3.0", "0.3.1"}`). New
  files SHOULD declare `"0.3.1"`; pilot files written under v0.3.0
  remain valid.
- They use disjoint output directories: `generated/graph/` vs `generated/v0.3/`.

Once `data/` is fully v0.3 and the v0.2 baseline is archived under
`generated/snapshots/v0.2/`, the v0.2 module is retired.

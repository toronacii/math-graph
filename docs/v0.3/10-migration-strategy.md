# 10 — Migration Strategy (v0.2 → v0.3)

## Two valid paths

The project has decided that the v0.2 graph is **regenerable** and need
not be preserved node-by-node. Two migration paths are therefore both
acceptable, with different cost / fidelity tradeoffs.

### Path A — Full rerun (RECOMMENDED)

1. Snapshot v0.2 (`generated/snapshots/v0.2/` already exists).
2. Empty `data/`.
3. Re-extract all in-scope sources against the v0.3 schema using the
   updated extraction templates and context packs.
4. Validate with `scripts/v03/validate`.
5. Snapshot the result with a `rerun_id`.

This produces the highest semantic quality. It is the path the project
is preparing for. The architecture doc, schema, and templates in this
directory are all designed for this path.

### Path B — Skeleton migration (BRIDGE)

A fallback. Use `scripts/migrate_v02_to_v03.py` to generate v0.3
*skeleton* YAML from existing v0.2 YAML. The skeletons:

- preserve IDs, `proved_by`, `proves`, `uses` (as `essential` deps),
  and `sources` (with `theorem_label` inferred from `section` when
  the form `NN.NN` is detected);
- map the single v0.2 `confidence` to `quality.extraction_confidence`;
- mark LaTeX as `present` if a body exists or `missing` / `not_applicable`
  otherwise;
- record `provenance.derived_from = [old_id]` and
  `provenance.rerun_id = "v0.3-migration"`;
- leave `domains`, `ambient`, `ontology`, `generality`,
  `dependency_confidence`, `semantic_confidence`, and review fields
  empty for human fill-in.

Skeletons land under `migrated/`, never directly inside `data/`. A
human reviewer must promote each skeleton.

Path B is **not** sufficient for the v0.3 quality bar by itself. Use it
to bootstrap the rerun's `data/` tree if Path A's per-entity
re-extraction is infeasible at first.

## What changes between v0.2 and v0.3 entities

| Aspect              | v0.2                                | v0.3                                                              |
|---------------------|-------------------------------------|-------------------------------------------------------------------|
| schema marker       | _absent_                            | `schema_version: "0.3.1"` (loader also accepts `"0.3.0"`)        |
| title / natural     | `{lang: text}`                      | `{lang: TranslatedText}` with originality + review                |
| latex               | optional string                     | `LatexBlock` with status + review                                 |
| confidence          | single `low/medium/high`            | `QualityBlock` with 6 axes                                        |
| sources             | flat list                           | flat list + `theorem_label`, `year`, `source_language`            |
| `uses`              | `[statement_id]`                    | `[ProofDependency]` with role / confidence / implicit / locality  |
| definitional deps   | _impossible_                        | `Statement.depends_on` (concept layer)                            |
| ambient context     | _absent_                            | `ambient.structures / logic / foundations`                        |
| domains             | _absent_                            | `domains.primary / secondary`                                     |
| ontology            | _absent_                            | `ontology.semantic_kind / keywords`                               |
| generality          | _absent_                            | `generality[*]` edges                                             |
| status              | `draft/reviewed/published`          | 6-step lifecycle with promotion gates                             |
| provenance          | _absent_                            | `ProvenanceBlock` with rerun id + derived-from                    |
| proof internal      | flat                                | optional `parts[*]` with localized `uses`                         |

## Risk register

| Risk                                                | Mitigation                                                     |
|-----------------------------------------------------|----------------------------------------------------------------|
| Rerun produces semantically different graph         | `scripts/diff_graphs` highlights deltas; review-gate           |
| ID drift breaks visualization links                 | `provenance.redirected_to` + per-rerun snapshot of `graph.json`|
| LLM-written translations marked as approved         | `review_status: unreviewed` is the default; gate at audit      |
| Bundled definitions re-introduced                   | Extraction templates explicitly forbid bundling                |
| Implicit completeness imports remain hidden         | `role: existence` + dep_confidence audit query                 |
| Migration skeletons treated as authoritative        | Skeletons land under `migrated/`, not `data/`                  |

## ID redirect ledger

When a rerun retires an ID, two records are created:

1. The new entity's `provenance.derived_from` lists the old ID.
2. The rerun's migration report (`reports/migration-*.md`) lists the
   redirect.

If the old ID survives in any form (e.g., a bundled definition was
preserved as a coarse hub while atomic concepts were spawned), the old
entity may carry `provenance.redirected_to` to point at the preferred
new entity.

## Visualization handoff

`visualization/web/public/graph.json` is updated at the end of each
rerun by copying `generated/v0.3/graph.json`. The web viewer is
schema-agnostic and renders whatever is shipped, so no viewer changes
are required for the v0.3 transition. Per-node detail pages should
add the new fields incrementally (recommended order: `quality`,
`provenance`, `domains`, `ambient`, `ontology`).

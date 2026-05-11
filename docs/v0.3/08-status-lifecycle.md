# 08 — Status Lifecycle

v0.2 had three statuses (`draft | reviewed | published`) and used
`draft` for everything. v0.3 introduces a six-step lifecycle with
gating rules.

## States

```
extracted → reviewed → validated → audited → stable → canonical
```

| Status      | What it means                                                                |
|-------------|------------------------------------------------------------------------------|
| `extracted` | Raw output of an extraction pass. No human eyes.                             |
| `reviewed`  | A human or audit pass touched the entity. Issues may still be open.          |
| `validated` | Passes structural validation + has source(s) + has LaTeX (or N/A).           |
| `audited`   | A mathematical reviewer signed off on semantic correctness.                  |
| `stable`    | Audited and integrated into a release snapshot.                              |
| `canonical` | The project's blessed formulation. Rarely rewritten. Changes require an RFC. |

## Promotion gates

The validator (`scripts/v03/validate.py`) enforces these gates:

- **`validated`** requires:
  - `sources` is non-empty;
  - `statement.latex.status != "missing"` (statements only).
- **`audited`** requires:
  - `quality.semantic_confidence` is set (statements);
  - `quality.dependency_confidence` is set (proofs).
- **`stable`** and **`canonical`** are administrative; they imply all
  earlier gates. The validator does not reject promotion to these
  statuses, but a snapshot at `stable`/`canonical` is recorded under
  `generated/snapshots/`.

A status may NOT be regressed implicitly. To downgrade a status,
explicit `provenance.rerun_notes` must record the reason.

## Status vs review_status

- Entity `status` is the entity-level lifecycle (the gate above).
- `TranslatedText.review_status` and `LatexBlock.review_status` are
  per-field review states. They contribute to the entity's eligibility
  for higher entity statuses.

For example, a statement with `status: audited` may still have a
`title.es.review_status: unreviewed`. The entity is mathematically
audited; the Spanish title translation has not been verified yet.

## Default behavior

- New v0.3 entities start at `extracted`.
- The migration tool emits everything as `extracted` regardless of
  v0.2 confidence, because the v0.3 axes have not been filled in.

## Reports

Per-chapter reports in v0.3 produce a status-distribution table and
flag entities at high statuses with missing axis data (e.g.,
`audited` entities lacking `semantic_confidence`).

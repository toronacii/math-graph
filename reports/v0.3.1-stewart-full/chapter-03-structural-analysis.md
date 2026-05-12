# Chapter 3 — Differentiation Rules — Structural Analysis

**Rerun:** `v0.3.1-stewart-full`
**Snapshot:** `v0.3.1-stewart-full-ch03`
**Generated:** 2026-05-11
**Cumulative graph (Ch1+Ch2+Ch3):** 173 nodes, 495 edges, 1 connected
component, density 0.0166

---

## 1. What Chapter 3 Adds to the Graph

Chapter 3 is the first chapter that is overwhelmingly *constructive*
rather than *foundational*. Where Ch2 introduced the limit and the
derivative as primitive notions, Ch3 uses those primitives to
mechanize differentiation. The chapter contributes 37 new statements
and 28 new proofs across 11 sections, expanding the cumulative graph
from 108 → 173 nodes (+60%) and 284 → 495 edges (+74%). The edge
growth outpaces node growth, confirming the expected pattern: Ch3
*reuses* Ch1/Ch2 infrastructure intensely instead of inventing new
primitives.

The chapter's central object — `definition.derivative-function` —
moves from a mid-tier hub (in-degree 5 after Ch2) to the second-most
referenced node in the entire graph (combined score 38 after Ch3,
behind only `definition.function`). Every section of Ch3 except §3.7
adds direct dependencies on it.

## 2. Per-Section Topology

| Section | New stmts | New proofs | Local hub | Notes |
|---------|-----------|-----------|-----------|-------|
| 3.1     | 10        | 8         | `theorem.power-rule` | Power, sum/diff, constant-mul, exp basics; defines `e` operationally |
| 3.2     | 2         | 2         | `theorem.product-rule` | Product + quotient |
| 3.3     | 3         | 3         | `theorem.derivatives-of-trigonometric-functions` | Bundled trig; depends on `theorem.special-trig-limit` (§2.3 carryover) |
| 3.4     | 4         | 4         | `theorem.chain-rule` | Becomes the most-referenced theorem of Ch3 |
| 3.5     | 2         | 1         | `proposition.implicit-differentiation` | Schema enabling §3.6 + §3.11 |
| 3.6     | 5         | 5         | `theorem.derivative-of-natural-logarithm` | Closes the power-rule-general loop |
| 3.7     | 0         | 0         | — | Applied interpretations only — no math entities |
| 3.8     | 1         | 1         | `theorem.exponential-growth-decay-solution` | Existence-only proof; uniqueness deferred to §9.4 |
| 3.9     | 1         | 0         | `proposition.related-rates-strategy` | Type-B schema |
| 3.10    | 3         | 0         | `proposition.linear-approximation` | Bridge to Taylor §11.10 |
| 3.11    | 6         | 4         | `definition.hyperbolic-function` | Bundled per trig-bundle policy |

## 3. New Hubs Introduced in Ch3

Three Ch3 nodes have crossed the in-degree-5 threshold and qualify
as graph hubs:

1. **`theorem.chain-rule`** (combined score 17). Used directly in
   the proofs of every inverse-derivative theorem (§3.5 inverse-trig,
   §3.11 inverse-hyperbolic), the implicit-differentiation
   propositions, and the general logarithmic derivative. It will
   continue to dominate Ch4–Ch7.

2. **`definition.hyperbolic-function`** (combined score 13).
   Concentration here is partly an artefact of bundling: a single
   node carries the load of six functions, four derivative formulas,
   four inverse functions, and three log-form identities. The
   chapter `weak-dependencies` report explicitly tracks this as
   Type-A debt.

3. **`proposition.limit-laws`** (combined score 16, up from 4 after
   Ch2). Ch3 derivative-from-definition proofs (`power-rule`,
   `derivative-of-natural-exponential`, `special-trig-limit`)
   reactivate this Ch2 bundle, validating the §2.3 architectural
   choice to keep limit-laws as a single proposition with deferred
   sub-proofs.

## 4. Layering and the Two-Layer Dependency Pattern

The schema's two-layer design (`Statement.depends_on` for conceptual
relationships; `Proof.uses` for inferential dependencies) is now
clearly visible in the graph. Of the 495 edges:

- **281 `depends_on`** edges (conceptual): 95% are `uses_concept`,
  with 6 `extends`, 6 `specializes`, 3 `instance_of`. The very low
  share of generality-style roles confirms that Ch3 builds *on top
  of* Ch2 rather than refining Ch2 statements.

- **172 `uses`** (proof-level): 99 `essential`, 64 `definition`,
  6 `notation`, 2 `background`, 1 `existence`. The 58% essential
  share is healthy — it means most proof dependencies are doing
  real inferential work, not just citing definitions.

- **42 `proves`** edges, one per proof.

This split was unavailable in v0.2 (which collapsed both layers
into a single `uses` field) and is the most important structural
gain of v0.3 visible at the chapter scale.

## 5. Ch1 + Ch2 Carryover Patterns

`definition.function` remains the universal hub (in-degree 53).
`definition.limit-of-function`, `definition.derivative-function`,
and `definition.continuity-at-point` are all heavily reused. No
Ch1 or Ch2 hub became dormant; conversely, several Ch2 leaves
(`theorem.special-trig-limit`, `definition.exponential-function`)
gained 5+ Ch3 inbound edges. This validates the Ch2 architectural
decision to keep `limit-of-function` and `epsilon-delta-limit` as
paired informal/rigorous nodes — the informal node is the one Ch3
overwhelmingly cites.

## 6. Bundled-Node Concentration Analysis

Eight Ch3 statements carry Type-A bundle debt (six trigonometric
derivatives, six inverse-trig derivatives, six hyperbolic functions,
six hyperbolic derivatives, six inverse-hyperbolic functions, six
inverse-hyperbolic derivatives, multiple hyperbolic identities, three
inverse-hyperbolic log forms). Concentration of in-degree on these
nodes inflates their hub scores artificially. If split into atomic
nodes, the trig-derivatives bundle alone would generate ~24 new
nodes (6 statements × 4 inverse forms) and ~30 new edges, increasing
the graph by ~14%. The decision to defer this split is recorded
explicitly in `chapter-03-weak-dependencies.yml` as optional
refinement — splitting is mechanically tractable and can be done in
a future pass without breaking dependents (each splitter would gain
a `specializes` edge to the bundled parent).

## 7. Growth Expectations for Ch4

Ch4 (Aplicaciones de la derivación) will:

- Saturate `definition.differentiable-on-interval` (currently a
  leaf), `definition.acceleration` (leaf), `definition.nth-derivative`
  (leaf, score 1).
- Promote the §3.10 cluster (linearization, differential,
  linear-approximation) from leaves to hubs, as Ch4 §4.1 max/min
  and §4.4 indeterminate forms cite them.
- Generate new hubs around `theorem.mean-value-theorem` (§4.2),
  `theorem.first-derivative-test` (§4.3), and the L'Hôpital
  family (§4.4) — each of which will likely reach in-degree
  ≥5 by chapter end.
- First citations of `theorem.intermediate-value-theorem` (Ch2 leaf)
  expected in §4.1 max/min existence arguments.

## 8. Honest Confidence Distribution

Of 173 nodes, 12 carry `dependency_confidence: medium` — 10 of
which are the bundled-node deferrals listed in §6, and 2 are the
hyperbolic-derivative proofs that explicitly note Stewart's
informal handwave that "the inverse of a differentiable bijection
is differentiable" (Stewart §3.11 page 261). All other nodes are
`high`. No Ch3 entity is `low` — every dependency either traces to
a previously extracted node or is paired with an explicit `notes:`
field documenting the gap.

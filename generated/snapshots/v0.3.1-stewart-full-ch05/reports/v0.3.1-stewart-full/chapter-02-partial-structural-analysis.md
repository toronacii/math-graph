# Chapter 2 (partial: §2.1–§2.3) — Structural Analysis

- **Rerun:** `v0.3.1-stewart-full`
- **Snapshot label:** `v0.3.1-stewart-full-ch2-partial`
- **Source:** Stewart, *Cálculo de una variable: Trascendentes tempranas*, 7th ed. (Spanish), Ch. 2 §2.1–§2.3.
- **Generated:** 2026-05-11
- **Predecessor:** `v0.3.1-stewart-full-ch01`

## Footprint

| Metric | Ch1 closing | This partial | Δ |
|---|---|---|---|
| Statements | 39 | 58 | +19 |
| Proofs | 5 | 7 | +2 |
| Nodes | 44 | 65 | +21 |
| Edges | 88 | 133 | +45 |
| Density | 0.047 | 0.032 | (drops as graph widens) |
| Components | 1 | 1 | — |

All 65 entities at status `extracted`, schema `0.3.1`, rerun
`v0.3.1-stewart-full`, language original `es`. Every Ch2 entity
carries a page locator (a tightening over Ch1, where page
locators were deferred).

## §2.1 — Tangent and velocity problems

Two atomic definitions extracted: `definition.secant-line`
(geometric primitive) and `definition.average-velocity`
(difference quotient over time). The "tangent line" and
"instantaneous velocity" formal definitions are deferred to §2.7
where Stewart actually defines them via limits — extracting them
in §2.1 would be premature semantic invention.

## §2.2 — Limit of a function

Seven entities authored, mirroring Stewart's six numbered
definitions plus the implicit equivalence:

| Stewart | Node | Notes |
|---|---|---|
| Def 1 | `definition.limit-of-function` | informal "intuitive" version |
| Def 2 | `definition.left-hand-limit` | atomic split |
| (paragraph) | `definition.right-hand-limit` | sibling owned by left- |
| Eq 3 | `proposition.limit-exists-iff-one-sided-limits` | restated as Thm 1 in §2.3 — single node, two source locators |
| Def 4 | `definition.infinite-limit` | informal divergence |
| Def 5 | `definition.negative-infinite-limit` | sibling owned by infinite- |
| Def 6 | `definition.vertical-asymptote` | Type-A bundle (6 cases) |

The five informal limit nodes (`limit-of-function`, two one-sided,
two infinite) all carry `latex.status: informal` and
`semantic_confidence: medium` — they are pedagogical, not
rigorous. The rigorous epsilon-delta variants will be SEPARATE
nodes (`definition.epsilon-delta-limit`,
`definition.left-hand-limit-precise`, `definition.infinite-limit-
precise`) authored in §2.4. This honors the audit recommendation
to never collapse rigorous and informal formulations into one
node.

## §2.3 — Calculating limits using limit laws

Ten statements + 2 proofs:

- `proposition.limit-laws` (Type-A bundle of Laws 1–5: sum, diff,
  const-mult, prod, quot). Carried as explicit debt at
  `dependency_confidence: medium`.
- `proposition.limit-power-law` (Law 6) + `proof.limit-power-
  law.stewart` (induction from product law).
- `proposition.limit-of-constant` (Law 7), `proposition.limit-of-
  identity` (Law 8) — both deferred to §2.4 for proof.
- `proposition.limit-power-of-x` (Law 9) + `proof.limit-power-of-
  x.stewart` (two-line: power-law + limit-of-identity).
- `proposition.limit-root-law` (bundles Laws 10+11) — deferred
  proof.
- `proposition.direct-substitution-property` — the
  continuity-precursor for polynomials and rational functions.
- `proposition.limit-equality-near-point` — locality principle.
- `proposition.limit-monotonicity` (Theorem 2) — deferred proof.
- `theorem.squeeze-theorem` (Theorem 3) — deferred proof.

## Hub evolution

`definition.limit-of-function` enters as the second-most-cited
node after a single chapter (in-degree 14, behind only
`definition.function` at 33). This is the expected structural
signature of Ch2: limits are the new universal hub. The five
"informal limit family" nodes will continue to gather incoming
edges through §2.4–§2.8 (continuity, derivatives, limits at
infinity all cite them).

`proposition.direct-substitution-property` is the highest-
out-degree new node (7 outgoing edges) because it explicitly
declares dependencies on polynomial, rational-function, domain,
and three limit-law nodes — making it a "downstream consolidator"
that will become a corollary of continuity in §2.5.

## Edge taxonomy evolution

| Role | Ch1 closing | This partial | Δ |
|---|---|---|---|
| `uses_concept` | 68 | 104 | +36 |
| `instance_of` | 3 | 3 | — |
| `extends` | 0 | 2 | +2 (infinite-limit, negative-infinite-limit extend limit-of-function) |
| `specializes` | 0 | 2 | +2 (left/right-hand-limit specialize limit-of-function) |
| `definition` (Proof.uses) | 8 | 8 | — |
| `essential` (Proof.uses) | 4 | 7 | +3 (two new proofs cite three essential predecessors) |
| `proved_by` | 5 | 7 | +2 |

Two new role categories activate in §2.2: `extends` (used to
mark divergence-extension of the basic limit notion) and
`specializes` (used to mark restriction to one-sided
neighborhoods). These were unused in Ch1.

## Generality edges authored

- `definition.left-hand-limit` ↔ `definition.right-hand-limit`
  (sibling, owned by `left-hand-limit`)
- `definition.infinite-limit` ↔ `definition.negative-infinite-
  limit` (sibling, owned by `infinite-limit`)
- `theorem.squeeze-theorem` `stronger_than` `proposition.limit-
  monotonicity`

All sibling-edge ownership respects policy 04 (alphabetically
earliest id owns).

## Audit-recommendation compliance

| Recommendation | Status |
|---|---|
| Atomic over bundled where natural | ok — left/right and ±∞ split as atoms |
| `Proof.uses[].role` precision | ok — both new proof nodes use `role: essential` exclusively (no flat lists) |
| Honest `dependency_confidence` | ok — 11 new debt-bearing nodes flagged at `medium` |
| Informal vs. rigorous separation | ok — five informal limit nodes flagged with `latex.status: informal`, rigorous ε–δ siblings deferred to §2.4 |
| Semantic confidence faithfulness | ok — informal limits at `semantic_confidence: medium`; precise theorems at `high` |

## What §2.4–§2.8 will deliver

- `definition.epsilon-delta-limit`, `definition.left-hand-limit-
  precise`, `definition.infinite-limit-precise` — rigorous
  siblings of the §2.2 informal nodes (NOT replacements).
- Proofs for `limit-of-constant`, `limit-of-identity`, sum-law
  (`limit-laws`'s first component), and likely `squeeze-theorem`
  + `limit-monotonicity`.
- §2.5 — `definition.continuity-at-point`,
  `definition.continuity-on-interval`, `theorem.intermediate-
  value-theorem`, `theorem.continuity-of-composition`,
  `theorem.continuity-arithmetic-operations`.
- §2.6 — limits at infinity, horizontal asymptotes, end behavior.
- §2.7 — `definition.tangent-line`, `definition.instantaneous-
  velocity`, `definition.derivative-at-point` (closes the loop
  back to §2.1's secant-line and average-velocity).
- §2.8 — `definition.derivative-function`,
  `definition.differentiable`, `theorem.differentiable-implies-
  continuous`.

Roughly +20–25 statements and +5–10 proofs expected to bring Ch2
to ~85 statements and ~12–17 proofs (~100 nodes).

# Chapter 1 (Partial — §1.1 + §1.2) — Structural Analysis

- **Rerun:** `v0.3.1-stewart-full`
- **Snapshot label:** `v0.3.1-stewart-full-ch1-partial`
- **Source:** Stewart, *Cálculo de una variable: Trascendentes tempranas*, 7th ed. (Spanish), Ch. 1 §1.1–§1.2.
- **Generated:** 2026-05-11
- **Status:** partial — §1.3, §1.5, §1.6 deferred to the full Ch1 milestone (`v0.3.1-stewart-full-ch01`).

## Footprint

| Metric | Value |
|---|---|
| Statements | 20 |
| Proofs | 1 |
| Total graph nodes | 21 |
| Edges | 34 |
| Connected components | 1 |
| Density | ≈ 0.081 |

All 21 entities are at status `extracted`, schema `0.3.1`,
`provenance.rerun_id: v0.3.1-stewart-full`, language original `es`.

## Layering

The Ch1 partial graph cleanly forms three semantic layers:

1. **Atomic foundations (layer 0).** `definition.function` is the
   universal hub. It carries no `depends_on` edges and is cited by
   every other entity (in-degree 17). This is by design — `function`
   is an axiomatic atom in Stewart's pedagogy.
2. **Function attributes (layer 1).** `definition.domain`,
   `definition.range`, `definition.graph-of-function`,
   `definition.independent-variable`, `definition.dependent-variable`
   each `uses_concept` `definition.function`. They were authored as
   atomic splits from Stewart's bundled function definition, per the
   audit recommendation against bundled definition hubs.
3. **Properties, criteria, and families (layer 2).**
   `definition.even-function`, `definition.odd-function`,
   `definition.increasing-function`, `definition.decreasing-function`,
   `definition.piecewise-function`, `definition.absolute-value`,
   `proposition.vertical-line-test`, plus the §1.2 function families
   (`linear`, `polynomial`, `power`, `rational`, `algebraic`,
   `trigonometric`) and `definition.mathematical-model`. These depend
   on layer 1 atoms and (for `definition.absolute-value`) layer-2
   peers via `instance_of`.

## Hubs

- **`definition.function`** — in-degree 17. Foundational hub. This is
  expected and correct: it is the universally cited atom.
- **`definition.domain`** — in-degree 7. Secondary hub; cited by
  every function-attribute and family node that needs to discuss
  admissible inputs.
- **`definition.polynomial`** — in-degree 2 (cited by
  `rational-function` and `algebraic-function`). Layer-2 hub for the
  function-family subgraph.

No spurious "definition root" pathology is observed. The two
universal hubs (`function`, `domain`) are real conceptual primitives,
not accidental v0.2-style bundles.

## Edge taxonomy

Of the 34 edges:

- 30 `depends_on` with `role: uses_concept` — concept-layer edges
  expressing "this notion uses that notion."
- 1 `depends_on` with `role: instance_of` —
  `definition.absolute-value` → `definition.piecewise-function`.
- 2 proof-edges with `role: definition` (the v.l.t. proof unfolds
  `definition.function` and `definition.graph-of-function`).
- 1 `proved_by` edge (`proposition.vertical-line-test` →
  `proof.vertical-line-test.stewart`).

Edge-role taxonomy is exercised at three of the eight available roles
(`uses_concept`, `instance_of`, `definition`); other roles
(`essential`, `existence`, `notation`, etc.) will appear once §1.3+
introduce theorems with substantive proofs. The 2026-05-11 audit's
warning against flat / role-less `uses` lists is upheld here — every
edge declares an explicit role.

## Generality edges

Three sibling generality edges authored:

- `definition.even-function` ↔ `definition.odd-function`
- `definition.increasing-function` ↔ `definition.decreasing-function`
- `definition.independent-variable` ↔ `definition.dependent-variable`

Plus one cross-family edge:

- `definition.algebraic-function` `stronger_than`
  `definition.rational-function` (i.e., the algebraic class properly
  contains rational functions).

Sibling edges are owned by the alphabetically-earlier id per
`policies/04-edge-role-taxonomy.md` to prevent double-counting.

## Growth expectations

Once §1.3 (transformations, composition), §1.5 (exponentials), and
§1.6 (inverses, logs, inverse trig) are merged, expect roughly:

- +18–22 statements (transformations as atoms; composition; exp, log,
  one-to-one criterion, horizontal-line test, inverse function,
  inverse-trig family);
- +6–10 proofs (cancellation equations, change-of-base formula,
  laws of logs, vertical-line / horizontal-line test);
- the graph density to drop modestly (more peripheral nodes); and
- `definition.function` to remain the dominant hub.

## Audit-recommendation application

Two of the 2026-05-11 architectural priorities apply at this scale:

1. **Atomic definition nodes.** Stewart's single boxed function
   definition was split into five atoms (`function`, `domain`,
   `range`, `independent-variable`, `dependent-variable`) plus
   `graph-of-function`. The bundled-hub pathology
   (`neighborhood-limit-point-open-closed` style) is not reproduced.
2. **Honest `dependency_confidence`.** The trigonometric-function
   bundle is the one remaining bundle; its
   `dependency_confidence: medium` and a note in `notes` flag it as
   semantic debt to be split before promotion to `validated`.

The completeness/`supremum`/`existence` audit items do not apply at
the Ch1 level — they will become binding from Ch11 (series) onward.

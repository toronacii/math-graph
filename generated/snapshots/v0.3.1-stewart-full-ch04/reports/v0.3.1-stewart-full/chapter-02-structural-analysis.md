# Chapter 2 — Structural Analysis (v0.3.1-stewart-full)

> Stewart, *Cálculo de una variable: Trascendentes tempranas* (7e),
> Capítulo 2 — Límites y derivadas. Full chapter (§2.1–§2.8).
> Status: extracted; semantic-dependency audit pending.

## Snapshot

- 108 nodes (94 statements + 14 proofs); 284 edges; density 0.025;
  1 connected component.
- 55 statements first introduced in Ch2 across all 8 sections; 9 new
  proofs.
- Cumulative since Ch1: definitions dominate (67/94 = 71 %),
  followed by propositions (18) and theorems (9).
- Test suite: 45/45 pass. Validation: clean. Provenance audit: clean.

## Conceptual layering

Ch2 introduces three intertwined hierarchies, each layered roughly
top-down:

1. **Limit hierarchy** (§2.2 → §2.4 → §2.6).
   Informal limits (§2.2) are paired with `equivalent` edges to
   precise ε–δ versions (§2.4) and ε–N versions (§2.6). Each pair
   keeps two nodes — never merged — so that a graph consumer can
   choose between the pedagogical and rigorous formulations without
   losing either. The ε–δ node sits at the bottom of every later
   limit-related proof.

2. **Continuity hierarchy** (§2.5).
   Continuity at a point branches into left/right siblings, lifts
   to continuity on an interval, and then propagates through
   `theorem.continuity-arithmetic` (closure under +, −, ·, /, c·),
   `theorem.continuity-of-polynomials-and-rationals` (instance),
   and `theorem.continuity-of-elementary-functions` (further
   instance). Above them sits IVT (`theorem.intermediate-value-
   theorem`) and the substitution machinery
   (`theorem.limit-through-continuous-function`,
   `theorem.continuity-of-composition`).

3. **Derivative hierarchy** (§2.7 → §2.8).
   `definition.tangent-line` (line-valued) and
   `definition.derivative-at-point` (number-valued) are kept as
   separate atomic nodes and joined by
   `proposition.derivative-as-tangent-slope` + proof. From there
   `definition.derivative-function` (function-valued) abstracts the
   pointwise derivative; `definition.differentiable-at-point` and
   `definition.differentiable-on-interval` formalize existence,
   and `theorem.differentiable-implies-continuous` (with full
   proof) bridges back to the §2.5 hierarchy. The chain extends
   through `definition.second-derivative` and
   `definition.nth-derivative` (recursive), with
   `definition.acceleration` as the kinematic specialization.

## Hubs

- `definition.function` remains the universal substrate (in-deg
  53). Every Ch2 statement that quantifies over real-valued maps
  cites it; this is intentional and matches the textbook's
  pedagogy of "everything is a function".
- `definition.limit-of-function` is the dominant Ch2-native hub
  (in-deg 22). Every section from §2.3 onward depends on it.
- `definition.continuity-at-point` (in-deg 12) is the §2.5 hub and
  the bridge to §2.8.
- `definition.derivative-at-point` (in-deg 5) is the entry point
  for §2.7–§2.8 and will become a top-five hub in Ch3 once
  derivative rules are extracted.

## Edge composition

| Kind                    | Count | Note                                                                |
|-------------------------|------:|---------------------------------------------------------------------|
| `statement_depends_on`  |   202 | Concept-layer edges (no proof participation)                        |
| `proof_uses`            |    39 | Proof-layer edges with explicit `role`                              |
| `statement_generality`  |    29 | Equivalent / stronger_than / sibling / specializes pairs            |
| `statement_proved_by`   |    14 | Statement → Proof; one per proof node                               |

Proof-layer roles are distributed: `essential` (24), `definition`
(12), `notation` (1), `background` (2). Every `proof_uses` row
carries an explicit role per the 2026-05-11 audit policy — no flat
strings.

## Splits and bundles

Per the 2026-05-11 architectural audit, every multi-claim statement
in Ch2 was either split or marked as explicit Type-A bundle debt.
Splits applied (kept as separate atoms):

- left/right-hand-limit, infinite-limit ↔ negative-infinite-limit,
  left/right-continuous, epsilon-delta vs informal limit, epsilon-N
  vs informal limit-at-∞, tangent-line vs derivative-at-point,
  derivative-at-point vs derivative-function, second-derivative vs
  nth-derivative, differentiable-at-point vs differentiable-on-
  interval.

Type-A bundles accepted as debt (carried over and still open):

- `proposition.limit-laws` (5 laws, 1 proven), `theorem.continuity-
  arithmetic` (5 closure laws, 1 proven), `proposition.limit-root-
  law` (Stewart's Laws 10+11), `definition.vertical-asymptote`
  (6 divergence conditions), `definition.infinite-limit-at-
  infinity` (4 cases).

These bundles are flagged via `quality.dependency_confidence:
medium` on the corresponding proof node so a future audit can find
them programmatically.

## Growth expectations for Ch3

- `definition.derivative-at-point` and `definition.derivative-
  function` will pick up large in-degree from every differentiation
  rule (sum, product, quotient, chain).
- The orphan list will shrink substantially as Ch3 rules cite
  `definition.differentiable-on-interval`, `definition.acceleration`,
  `definition.nth-derivative`.
- `theorem.differentiable-implies-continuous` will be cited by every
  proof that converts a differentiability hypothesis into a
  continuity hypothesis (e.g., chain-rule proofs, MVT in Ch4).
- Several Ch1 leaves (transformations, even/odd, inverse-trig)
  will continue to wait for Ch5–7 to gain edges.

## Risk register

- Bundled-proof debt (limit-laws, continuity-arithmetic) is not
  retired; future MVT/limit-comparison work in Ch4 will require
  the multiplicative law to be honestly proven. Plan: split each
  Type-A proof into per-law `parts[]` once §2.4 ε–δ machinery is
  exercised in a worked Ch3 example.
- `proposition.non-differentiability-cases` is a pedagogical
  enumeration, not an exhaustive classification. Flagged via
  `semantic_kind:[criterion,pedagogical]` and
  `semantic_confidence: medium`.
- Two `generality` edges deviate from the alphabetical-ownership
  rule (policy 04) for narrative-clarity reasons; both are
  documented in the corresponding `notes` and listed in the
  statistics report under `deliberate_exceptions`.

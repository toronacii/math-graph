# Chapter 5 — Integrals — Structural Analysis

**Rerun:** `v0.3.1-stewart-full`
**Snapshot:** `v0.3.1-stewart-full-ch05`
**Generated:** 2026-05-11
**Cumulative graph (Ch1–Ch5):** 231 nodes, 704 edges, 1
connected component, density 0.0133

---

## 1. What Chapter 5 Adds to the Graph

Chapter 5 is the pivot chapter of Stewart Calculus: it introduces the
definite integral and proves the Fundamental Theorem of Calculus, which
unifies the two halves of the course (differentiation and integration).
The chapter contributes 16 new statements and 6 new proofs across 5
sections, expanding the cumulative graph from 209 → 231 nodes (+10%) and
636 → 704 edges (+11%).

Unlike Chapter 4, which spread its entities widely across 9 sections,
Ch5 concentrates its mass in three dense cores:

- **§5.2** (5 statements + 1 proof): formal definition of the definite
  integral, integrability theorem, evaluation formula, and two
  comparison-property bundles.
- **§5.3** (2 statements + 2 proofs): TFC1 and TFC2 — the heart of the
  chapter, with proofs that close the differentiation/integration loop.
- **§5.5** (3 statements + 3 proofs): substitution rule (indefinite and
  definite), and integrals of symmetric functions.

The chapter's *spine* is:
> Riemann sum → Definite integral → Integrability → TFC1 → TFC2 →
> (Indefinite integral ← General antiderivative) → Substitution rule →
> Definite substitution → Symmetric integrals

Every theorem in this spine is proved in-chapter except
`theorem.integrability-of-continuous`, which is explicitly deferred to
more advanced courses (requires uniform continuity and completeness of ℝ).

## 2. Per-Section Topology

| Section | New stmts | New proofs | Local hub | Notes |
|---------|-----------|-----------|-----------|-------|
| 5.1 | 2 | 0 | `definition.area-under-curve` | Pedagogical intro: area as limit of Riemann sums for f≥0; superseded by §5.2 definite integral |
| 5.2 | 6 | 1 | `definition.definite-integral` | Formal definition + evaluation formula + comparison properties; integrability deferred |
| 5.3 | 2 | 2 | `theorem.ftc-part-1`, `theorem.ftc-part-2` | TFC1 proved by squeeze; TFC2 proved from TFC1 via corollary |
| 5.4 | 3 | 0 | `definition.indefinite-integral` | Integral notation + 17-row table + Net Change Theorem (TFC2 restatement) |
| 5.5 | 3 | 3 | `theorem.substitution-rule` | Indefinite + definite substitution + symmetric-functions criterion |

## 3. New Hubs Introduced in Ch5

One Ch5 node immediately becomes the dominant new hub of the chapter:

1. **`definition.definite-integral`** (in-degree 9). Referenced by
   `theorem.integrability-of-continuous`, `proposition.integral-evaluation-formula`,
   `proposition.definite-integral-properties`, `proposition.definite-integral-bound`,
   `theorem.ftc-part-1`, `theorem.ftc-part-2`, `definition.indefinite-integral`,
   `theorem.net-change-theorem`, and `proof.definite-integral-bound.from-linearity`.
   This makes it the 9th-most-referenced node in the entire cumulative graph —
   immediately after `definition.continuity-on-interval` (12) — and it will
   continue to accumulate edges through Ch6–Ch8 (integration techniques, area,
   volume).

2. **`theorem.ftc-part-2`** (in-degree 3). Referenced by
   `theorem.net-change-theorem` (generality: equivalent),
   `proof.substitution-rule-definite.from-ftc2`, and
   `proof.ftc-part-2.from-ftc1`. TFC2 will become a major hub as
   integration applications expand.

3. **`definition.continuity-on-interval`** (existing hub, Ch5 escalation).
   Its in-degree grows from ~8 to 11 as TFC1, TFC2, the integrability theorem,
   and the substitution rules each list it as a precondition. It is now the
   8th-ranked node overall.

## 4. Atomicity and Disambiguation Decisions

Three pairs of nodes required explicit keep-separate decisions:

**`definition.area-under-curve` vs `definition.definite-integral`**
Both are introduced in §5.1–5.2, but §5.1's area definition is pedagogical
(restricted to f ≥ 0, right-endpoint Riemann sums) while §5.2's formal
definition is general (arbitrary sample points, signed area). The generality
edge `special_case_of` records the relationship without collapsing the nodes.

**`definition.indefinite-integral` vs `definition.antiderivative`**
Mathematically identical, but §4.9's antiderivative is introduced as "the
reverse derivative" while §5.4's indefinite integral introduces Leibniz
notation ∫ f dx and explicitly connects antiderivatives to TFC2. The
`depends_on: extends` edge records the equivalence; the separate nodes
preserve the distinct pedagogical framing.

**`theorem.net-change-theorem` vs `theorem.ftc-part-2`**
Stewart presents both in a single section (§5.4) as a named theorem ("Teorema
del cambio neto") because the "rate of change → net change" interpretation is
educationally important for physics, chemistry, and economics applications.
The `generality: equivalent` edge records the mathematical identity; separate
nodes preserve the distinct semantic framing.

## 5. Proof Structure

Ch5 proofs use two structural patterns:

**Squeeze-then-continuity** (`proof.ftc-part-1.stewart`): The §5.3 proof of
TFC1 is the canonical squeeze-theorem application — the derivative of g(x)=∫_a^x
f(t)dt is bounded between m and M (EVT), divided by h, and squeezed to f(x)
by continuity. This proof reactivates `theorem.extreme-value-theorem` and
`theorem.squeeze-theorem` (both Ch4 nodes), confirming they were not Ch4 leaves
but rather latent dependencies waiting for Ch5.

**Chain-rule reversal** (`proof.substitution-rule.from-chain-rule`,
`proof.substitution-rule-definite.from-ftc2`): Both substitution proofs
are essentially the same algebraic reversal: recognise the integrand as a
chain-rule derivative and use TFC2 to evaluate. The indefinite version uses
the chain rule directly; the definite version uses TFC2 twice (once on each
side) with the transformed limits.

**TFC1-then-corollary bridge** (`proof.ftc-part-2.from-ftc1`): TFC2 is
proved by combining TFC1 (g is an antiderivative of f) with
`corollary.derivatives-equal-implies-differ-by-constant` (any antiderivative
differs from g by a constant), collapsing the constants on evaluation. This
proof *closes* the Ch4 corollary chain that ran from §4.2 → §4.9.

## 6. Cross-Chapter Dependencies Activated in Ch5

Ch5 proofs activate several pre-existing Ch4 and Ch3 nodes that had been
"dangling" leaves or low-traffic nodes:

| Node reactivated | Prior in-degree | Ch5 use |
|---|---|---|
| `theorem.extreme-value-theorem` | 2 (Ch4 only) | Used by proof.ftc-part-1.stewart |
| `theorem.squeeze-theorem` | ~5 (Ch2) | Used by proof.ftc-part-1.stewart |
| `corollary.derivatives-equal-implies-differ-by-constant` | ~1 (Ch4) | Used by proof.ftc-part-2.from-ftc1 |
| `theorem.chain-rule` | ~17 (Ch3) | Used by both substitution proofs |
| `definition.antiderivative` | ~3 (Ch4) | Used by 3 Ch5 proofs |
| `definition.continuity-on-interval` | ~8 (Ch2–Ch4) | Now 11 — used by 3 Ch5 statements |

## 7. Forward Dependencies

Several Ch5 nodes will become major dependency anchors in future chapters:

- **`definition.definite-integral`**: Ch6 (area between curves, volumes),
  Ch7 (integration techniques), Ch8 (further applications)
- **`theorem.ftc-part-2`**: Every integration problem in Ch6–Ch8 implicitly
  uses TFC2 for evaluation
- **`theorem.substitution-rule`**: Ch7 (integration by parts, trig substitution)
- **`theorem.substitution-rule-definite`**: All definite integral computations
  in Ch6–Ch8 where a substitution is applied
- **`definition.indefinite-integral`**: Foundation for Ch7 (integration techniques)
  and Ch9 (differential equations)

# Milestone: Chapter 2 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 2 — Limits and Derivatives (Limites y derivadas)
- **Sections processed:** 2.1 through 2.8

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Chapter 1 | Chapter 2 | Total |
|----------------------|-----------|-----------|-------|
| Statements           | 39        | 36        | 75    |
| Proofs               | 7         | 13        | 20    |
| Total nodes          | 46        | 49        | 95    |
| Total edges          | 21        | 37        | 58    |
| Definitions          | 32        | 23        | 55    |
| Propositions         | 7         | 2         | 9     |
| Theorems             | 0         | 8         | 8     |
| Corollaries          | 0         | 1         | 1     |
| Lemmas               | 0         | 0         | 0     |
| Axioms               | 0         | 0         | 0     |
| Isolated nodes       | 25        | —         | 36    |
| Connected components | 27        | —         | 42    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 95 entities pass the full validation pipeline.

## Sections Breakdown

### 2.1 — The Tangent and Velocity Problems

4 definitions: secant-line, tangent-line, average-velocity,
instantaneous-velocity.

Motivational section with no theorems. Introduces the two central
problems that lead to the concept of limit and derivative.

### 2.2 — The Limit of a Function

5 definitions: limit-of-function, left-hand-limit, right-hand-limit,
infinite-limit, vertical-asymptote.
1 proposition: limit-exists-iff-one-sided-limits.

### 2.3 — Calculating Limits Using the Limit Laws

4 theorems: limit-laws, limit-power-law, limit-root-law,
squeeze-theorem, limit-sinx-over-x.
1 corollary: limit-cosx-minus-1-over-x.
1 proposition: direct-substitution-property.

Densest section in theorems. The limit laws become the most connected
node in the graph, feeding into multiple downstream proofs.

### 2.4 — The Precise Definition of a Limit

3 definitions: epsilon-delta-limit, left-hand-limit-precise,
infinite-limit-precise.

Provides the rigorous foundation for all limit-based proofs.

### 2.5 — Continuity

4 definitions: continuity-at-point, continuity-on-interval,
removable-discontinuity, jump-discontinuity.
3 theorems: continuity-of-combinations, continuity-of-composition,
intermediate-value-theorem.

### 2.6 — Limits at Infinity; Horizontal Asymptotes

2 definitions: limit-at-infinity, horizontal-asymptote.
1 theorem: limit-one-over-x-at-infinity.

### 2.7 — Derivatives and Rates of Change

2 definitions: derivative-at-point, rate-of-change.

### 2.8 — The Derivative as a Function

3 definitions: derivative-function, differentiable, second-derivative.
1 theorem: differentiable-implies-continuous.

## Reclassifications

One reclassification was performed during review:

- `theorem.limit-cosx-minus-1-over-x` reclassified to
  `corollary.limit-cosx-minus-1-over-x`. Follows almost immediately
  from theorem.limit-sinx-over-x via algebraic manipulation.

## Emerging Dependency Chains

### Chain A — Squeeze theorem cascade (new, depth 3)

```
epsilon-delta-limit → squeeze-theorem → limit-sinx-over-x → corollary.limit-cosx-minus-1-over-x
```

This is the longest chain in the graph (7 nodes including proofs).
It will extend further when derivatives of trigonometric functions
are computed in Chapter 3.

### Chain B — Limit laws fan-out (new, high connectivity)

```
epsilon-delta-limit → theorem.limit-laws
  → theorem.limit-power-law
  → proposition.direct-substitution-property
  → theorem.continuity-of-combinations
  → corollary.limit-cosx-minus-1-over-x
  → theorem.differentiable-implies-continuous
```

The limit laws are the most structurally important node in the graph,
with the highest fan-out among non-definition nodes.

### Chain C — Exponential-logarithmic (from Chapter 1, unchanged)

```
exponential-function → laws-of-exponents → laws-of-logarithms → change-of-base-formula
```

## Observations

1. **First theorems.** Chapter 2 introduces the first 8 theorems and
   1 corollary. The graph transitions from a vocabulary layer to a
   theorem-proof layer.

2. **Cross-chapter activation.** Chapter 2 proofs reference 6 Chapter 1
   definitions: polynomial, rational-function, trigonometric-function,
   composition-of-functions, epsilon-delta-limit uses the concept of
   function from Chapter 1 implicitly.

3. **Proof style diversity.** Chapter 2 introduces epsilon-delta (4),
   geometric (1), and algebraic (1) proof styles alongside direct (6).
   Two proofs remain assumed (IVT, laws-of-exponents from Ch1).

4. **Isolation decreasing.** Isolated nodes dropped from 54% (Ch1 only)
   to 38% (Ch1+Ch2). Still high because many Chapter 1 definitions
   await consumers in Chapters 3-4.

5. **The epsilon-delta definition is the structural keystone.** It feeds
   the limit laws, squeeze theorem, and root law proofs. These cascade
   into continuity theorems and the derivative definition.

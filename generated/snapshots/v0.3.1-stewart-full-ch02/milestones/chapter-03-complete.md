# Milestone: Chapter 3 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 3 — Differentiation Rules (Reglas de derivacion)
- **Sections processed:** 3.1 through 3.6

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Chapter 1 | Chapter 2 | Chapter 3 | Total |
|----------------------|-----------|-----------|-----------|-------|
| Statements           | 39        | 36        | 27        | 102   |
| Proofs               | 7         | 13        | 24        | 44    |
| Total nodes          | 46        | 49        | 51        | 146   |
| Total edges          | 21        | 37        | 88        | 146   |
| Definitions          | 32        | 23        | 3         | 58    |
| Propositions         | 7         | 2         | 0         | 9     |
| Theorems             | 0         | 8         | 22        | 30    |
| Corollaries          | 0         | 1         | 2         | 3     |
| Lemmas               | 0         | 0         | 0         | 0     |
| Axioms               | 0         | 0         | 0         | 0     |
| Isolated nodes       | 25        | —         | —         | 35    |
| Connected components | 27        | —         | —         | 39    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 146 entities pass the full validation pipeline.

## Sections Breakdown

### 3.1 — Derivatives of Polynomials and Exponential Functions

1 definition: number-e.
5 theorems: derivative-constant, power-rule, constant-multiple-rule,
sum-rule, derivative-exponential.
6 proofs.

Establishes the basic differentiation rules. The power rule proof
covers only positive integers here; the general case is completed
in section 3.6 via logarithmic differentiation.

### 3.2 — The Product and Quotient Rules

2 theorems: product-rule, quotient-rule.
2 proofs.

Both proofs use the "add and subtract" technique in the difference
quotient, plus differentiable-implies-continuous from Chapter 2.

### 3.3 — Derivatives of Trigonometric Functions

6 theorems: derivative-sin, derivative-cos, derivative-tan,
derivative-csc, derivative-sec, derivative-cot.
6 proofs.

The sin and cos derivatives are proved from the definition using
the angle addition formulas and the special limits lim sin(h)/h = 1
and lim (cos h - 1)/h = 0. The remaining four follow from the
quotient rule.

### 3.4 — The Chain Rule

1 theorem: chain-rule.
1 corollary: power-rule-combined-chain.
2 proofs.

The chain rule proof uses an increment formulation that avoids
the division-by-zero issue with naive cancellation of Δu.

### 3.5 — Implicit Differentiation

1 definition: implicit-differentiation.
3 theorems: derivative-arcsin, derivative-arccos, derivative-arctan.
3 proofs.

All inverse trig derivatives are derived via implicit differentiation:
apply the chain rule to the defining equation (e.g., sin y = x).

### 3.6 — Derivatives of Logarithmic Functions

1 definition: logarithmic-differentiation.
5 theorems: derivative-ln, derivative-ln-abs, derivative-log-base-a,
derivative-general-exponential, derivative-e-formula.
1 corollary: difference-rule (reclassified from 3.1).
5 proofs.

Closes the exponential-logarithmic derivative cycle. The derivative
of ln x is derived via implicit differentiation of e^y = x. The
general exponential a^x = e^{x ln a} follows by the chain rule.

## Reclassifications

Two reclassifications were performed during review:

- `theorem.difference-rule` reclassified to `corollary.difference-rule`.
  Follows immediately from the sum rule and constant multiple rule
  with c = -1.

- `theorem.power-rule-combined-chain` reclassified to
  `corollary.power-rule-combined-chain`. Direct consequence of
  combining the power rule with the chain rule.

## Emerging Dependency Chains

### Chain A — Extended squeeze-trig-derivative cascade (depth 5)

```
epsilon-delta-limit → squeeze-theorem → limit-sinx-over-x
  → derivative-sin → derivative-tan → derivative-arctan
```

This is now the longest chain in the graph (11 nodes including
proofs, 5 statement hops). It validates the predicted extension
from Chapter 2.

### Chain B — Limit laws mega-fan-out (expanded)

```
theorem.limit-laws (degree 14)
  → power-rule, constant-multiple-rule, sum-rule (Ch3 new)
  → product-rule, quotient-rule (Ch3 new)
  → derivative-sin, derivative-cos (Ch3 new)
  + all Ch2 downstream (unchanged)
```

The limit laws now have degree 14, making them the most connected
node in the entire graph.

### Chain C — Exponential-logarithmic complete cycle

```
exponential-function → laws-of-exponents → laws-of-logarithms
  → change-of-base-formula → derivative-log-base-a
natural-exponential → derivative-exponential
  → derivative-ln → derivative-general-exponential
```

Chapter 3 completed this cycle: exponential and logarithmic
derivatives now form a closed dependency structure.

### Chain D — Inverse trig via implicit differentiation (new)

```
derivative-sin → derivative-arcsin (via chain-rule + inverse-function)
derivative-cos → derivative-arccos
derivative-tan → derivative-arctan
```

## Observations

1. **Theorem explosion.** Chapter 3 added 22 theorems (vs 8 in Ch2),
   making theorems 31% of all statement nodes. The graph has crossed
   the inflection from vocabulary to theorem density.

2. **Massive connectivity.** 88 new edges from 51 nodes — an average
   of 1.73 edges per new node, the highest ratio so far. The largest
   connected component grew from 27 to 100 nodes (+270%).

3. **Cross-chapter activation.** 33 edges cross from Ch1/Ch2 entities
   into Ch3 proofs. definition.derivative-function (10 edges) and
   theorem.limit-laws (8 edges) are the most-consumed earlier entities.

4. **High confidence.** 23 of 24 new proofs are high confidence.
   Only proof.power-rule.stewart is medium (partial proof for
   positive integers only, completed in 3.6).

5. **No new weak dependencies.** No new assumed or low-confidence
   proofs. The epistemic debt from Chapters 1-2 is inherited but
   not expanded.

6. **Isolation continuing to decrease.** 35 isolated nodes (24%),
   down from 38%. Most remaining isolates are Chapter 1 definitions
   that await consumers in Chapters 4-5.

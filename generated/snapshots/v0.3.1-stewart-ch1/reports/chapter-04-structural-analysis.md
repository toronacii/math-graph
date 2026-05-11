# Chapter 4 — Structural Analysis

## 1. Conceptual Density

Chapter 4 produces 24 statements + 13 proofs = 37 nodes across 5
extracted sections (7.4 per section). Sections 4.5-4.8 were skipped
because they contain applications/methodology, not new mathematical
entities.

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 4.1     | 5    | 1     | 2    | 0    | 3      | medium  |
| 4.2     | 0    | 0     | 2    | 2    | 4      | high    |
| 4.3     | 3    | 4     | 0    | 0    | 4      | high    |
| 4.4     | 1    | 0     | 1    | 0    | 1      | medium  |
| 4.9     | 1    | 0     | 1    | 0    | 1      | medium  |

Section 4.2 (MVT) and 4.3 (derivative tests) are the densest.
Section 4.1 is definition-heavy (extrema vocabulary).

## 2. Dependency Growth

| Metric              | After Ch3 | After Ch4 | Change    |
|---------------------|-----------|-----------|-----------|
| Total nodes         | 146       | 183       | +25%      |
| Total edges         | 146       | 194       | +33%      |
| Largest component   | 100       | 144       | +44%      |
| Isolated nodes      | 35        | 36        | +1        |
| Isolation ratio     | 24%       | 20%       | -4pp      |
| Graph density       | 0.0069    | 0.0058    | -16%      |

Density decreased because node growth added many definitions that
are not yet consumed by proofs. The largest component grew from 100
to 144 nodes, absorbing most of Chapter 4's theorem-proof structures.

## 3. Type Distribution

| Type       | Ch3 cumul | Ch4 cumul | Shift                |
|------------|-----------|-----------|----------------------|
| definition | 57%       | 55%       | slight decrease      |
| proposition| 9%        | 11%       | increase (new tests) |
| theorem    | 31%       | 30%       | stable               |
| corollary  | 3%        | 4%        | slight increase      |

The type distribution is stabilizing. Propositions increased due to
the derivative tests (first, second, increasing/decreasing, concavity),
which are practical criteria rather than named theorems.

## 4. Hub Nodes

| Node                              | Degree | Role                    |
|-----------------------------------|--------|-------------------------|
| theorem.limit-laws                | 15     | Central theorem (Ch2)   |
| definition.derivative-function    | 10     | Foundational def (Ch2)  |
| theorem.chain-rule                | 8      | Differentiation key     |
| proof.mean-value-theorem.stewart  | 6      | Critical proof (Ch4)    |
| definition.inverse-function       | 6      | Inverse function key    |
| proof.rolles-theorem.stewart      | 5      | Key lemma proof (Ch4)   |

The Mean Value Theorem proof node has degree 6 — it feeds into
proofs of: zero-derivative-constant, increasing-decreasing test,
L'Hopital's rule, and general antiderivative (via corollaries).

## 5. Key Dependency Chains

### Chain A — MVT cascade (new, deep)

```
extreme-value-theorem + fermat-theorem
  → rolles-theorem
    → mean-value-theorem
      → zero-derivative-constant
        → equal-derivatives-differ-by-constant
          → general-antiderivative
```

This chain is 6 statements deep (12 nodes including proofs).

### Chain B — Derivative test cascade (new)

```
mean-value-theorem
  → increasing-decreasing-test
    → first-derivative-test
    → concavity-test
      → second-derivative-test
```

### Chain C — L'Hopital connection

```
mean-value-theorem → lhopitals-rule
```

L'Hopital's rule depends on the MVT (via the Cauchy MVT variant).

## 6. Cross-Chapter Dependencies

Chapter 4 proofs reference 10 distinct entities from Chapters 1-3:

| Earlier entity                     | Used by Ch4 proofs         |
|------------------------------------|----------------------------|
| definition.continuity-on-interval  | EVT, Rolle's              |
| definition.differentiable          | Rolle's, MVT              |
| definition.derivative-at-point     | Fermat's theorem           |
| definition.left-hand-limit         | Fermat's theorem           |
| definition.right-hand-limit        | Fermat's theorem           |
| definition.increasing-function     | increasing/decreasing test |
| definition.decreasing-function     | increasing/decreasing test |
| definition.second-derivative       | concavity test             |
| theorem.sum-rule                   | MVT proof                 |
| theorem.constant-multiple-rule     | MVT proof                 |
| theorem.limit-laws                 | L'Hopital                 |
| corollary.difference-rule          | equal-derivatives corollary|

## 7. Growth Expectations

### Chapter 5 — Integrals

Expected impact:

- **New definitional layer.** Riemann sums, sigma notation, definite
  integral, indefinite integral, net change.
- **Fundamental Theorem of Calculus (Parts 1 and 2).** Two major
  theorems with proofs referencing continuity, antiderivative, and MVT.
- **Substitution rule.** Connects to chain rule.
- **Estimated: ~15-20 new nodes, ~25-35 new edges.**

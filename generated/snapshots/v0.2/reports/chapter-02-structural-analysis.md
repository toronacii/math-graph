# Chapter 2 — Structural Analysis

## 1. Conceptual Density

Chapter 2 produces 36 statements across 8 sections (4.5 per section),
lower than Chapter 1's 7.8. However, the composition shifted
dramatically:

| Section | Defs | Props | Thms | Cors | Proofs | Density |
|---------|------|-------|------|------|--------|---------|
| 2.1     | 4    | 0     | 0    | 0    | 0      | low     |
| 2.2     | 5    | 1     | 0    | 0    | 1      | medium  |
| 2.3     | 0    | 1     | 4    | 1    | 6      | high    |
| 2.4     | 3    | 0     | 0    | 0    | 0      | low     |
| 2.5     | 4    | 0     | 3    | 0    | 3      | high    |
| 2.6     | 2    | 0     | 1    | 0    | 1      | medium  |
| 2.7     | 2    | 0     | 0    | 0    | 0      | low     |
| 2.8     | 3    | 0     | 1    | 0    | 1      | medium  |

Section 2.3 (limit laws) is the densest in proofs, generating 6 proof
nodes. Sections 2.1, 2.4, and 2.7 are definitional.

## 2. Dependency Growth

Graph density decreased from 0.0101 (Ch1) to 0.0065 (Ch1+Ch2).
This is expected: quadratic growth of possible edges outpaces linear
growth of actual dependencies.

However, the _connected_ subgraph grew substantially:

| Metric              | After Ch1 | After Ch2 | Change    |
|---------------------|-----------|-----------|-----------|
| Largest component   | 12        | 27        | +125%     |
| Isolated nodes      | 25        | 36        | +44%      |
| Isolation ratio     | 54%       | 38%       | -16pp     |

The largest component more than doubled, absorbing nodes from both
chapters. Isolation ratio decreased as Chapter 2 proofs activated
Chapter 1 definitions.

## 3. Type Distribution Shift

| Type       | Ch1 only | Ch1+Ch2 | Shift              |
|------------|----------|---------|---------------------|
| definition | 100%     | 73%     | vocabulary thinning |
| proposition| 18%      | 12%     | relative decrease   |
| theorem    | 0%       | 11%     | first appearance    |
| corollary  | 0%       | 1.3%    | first appearance    |
| proof      | 18%      | 27%     | increasing          |

The graph is transitioning from a vocabulary layer to a theorem-proof
layer. Definitions still dominate (73%) but will continue to decrease
proportionally as future chapters add more theorems.

## 4. Hub Nodes

Nodes with the highest connectivity (degree):

| Node                              | In | Out | Total | Role               |
|-----------------------------------|----|-----|-------|--------------------|
| theorem.limit-laws                | 1  | 5   | 6     | Central theorem    |
| definition.epsilon-delta-limit    | 0  | 4   | 4     | Foundational def   |
| definition.continuity-at-point    | 0  | 3   | 3     | Key definition     |
| theorem.limit-sinx-over-x        | 1  | 1   | 2     | Trigonometric key   |
| definition.graph-of-function      | 0  | 3   | 3     | Geometric tool (Ch1)|

`theorem.limit-laws` is the most connected non-definition node. It
feeds into proofs of: power-law, direct-substitution, cosx-1/x,
continuity-of-combinations, and differentiable-implies-continuous.

`definition.epsilon-delta-limit` is the structural keystone: it
feeds limit-laws, squeeze-theorem, root-law, and
continuity-of-composition directly.

## 5. Proof Topology

Chapter 2 proofs are more diverse than Chapter 1:

| Style          | Count | Description                     |
|----------------|-------|---------------------------------|
| direct         | 11    | Standard logical deduction      |
| epsilon-delta  | 4     | Formal limit proofs             |
| assumed        | 2     | Stated without proof            |
| algebraic      | 1     | Algebraic manipulation          |
| geometric      | 1     | Geometric construction argument |

Average fan-in (uses per proof):

| Chapter | Avg fan-in | Max fan-in |
|---------|-----------|------------|
| Ch1     | 2.0       | 3          |
| Ch2     | 2.0       | 3          |

Fan-in remains moderate. This will increase in Chapter 3 where proofs
like the chain rule combine derivative definition + composition +
limit laws.

## 6. Cross-Chapter Dependencies

Chapter 2 proofs reference these Chapter 1 entities:

| Chapter 1 entity                  | Used by (Ch2)                     |
|-----------------------------------|-----------------------------------|
| definition.polynomial             | proof.direct-substitution         |
| definition.rational-function      | proof.direct-substitution         |
| definition.trigonometric-function | proof.limit-sinx-over-x           |
| definition.composition-of-functions | proof.continuity-of-composition |

These cross-chapter edges are structurally important: they validate
that Chapter 1 definitions serve as reusable foundations.

## 7. Graph Layering

The graph now exhibits four natural layers:

```
Layer 0: Foundational definitions (function, domain, range...)
Layer 1: Structural definitions (limit, continuity, derivative)
Layer 2: Core theorems (limit laws, squeeze, IVT)
Layer 3: Derived results (sinx/x, cosx-1/x, diff→cont)
```

Layer boundaries are not strict — some definitions at Layer 1 also
feed directly into Layer 3 proofs.

## 8. Growth Expectations

### Chapter 3 — Differentiation Rules

Expected impact:

- **High proof density.** Every differentiation rule (power, product,
  quotient, chain) produces a theorem + proof.
- **Massive activation.** definition.polynomial, definition.power-function,
  definition.composition-of-functions, definition.trigonometric-function,
  definition.exponential-function, definition.logarithmic-function
  will all gain edges.
- **sinx/x cascade.** The derivative of sin(x) uses
  theorem.limit-sinx-over-x, extending Chain A.
- **Estimated: ~30 new nodes, ~50 new edges.**

### Chapter 4 — Applications of Differentiation

Expected impact:

- **Theorem-heavy.** Mean Value Theorem, Rolle's Theorem, L'Hopital's
  Rule, optimization theorems.
- **First lemmas likely.** Rolle's Theorem may serve as a lemma for MVT.
- **Deep dependency chains.** Proofs will reference results from
  Chapters 1-3.

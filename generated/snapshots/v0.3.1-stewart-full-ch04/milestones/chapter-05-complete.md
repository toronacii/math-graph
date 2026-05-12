# Milestone: Chapter 5 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 5 — Integrals (Integrales)
- **Sections processed:** 5.1, 5.2, 5.3, 5.4, 5.5

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Ch 1 | Ch 2 | Ch 3 | Ch 4 | Ch 5 | Total |
|----------------------|------|------|------|------|------|-------|
| Statements           | 39   | 36   | 27   | 24   | 13   | 139   |
| Proofs               | 7    | 13   | 24   | 13   | 9    | 66    |
| Total nodes          | 46   | 49   | 51   | 37   | 22   | 205   |
| Total edges          | 21   | 37   | 88   | 48   | 32   | 226   |
| Definitions          | 32   | 23   | 3    | 11   | 4    | 73    |
| Propositions         | 7    | 2    | 0    | 5    | 3    | 17    |
| Theorems             | 0    | 8    | 22   | 6    | 6    | 42    |
| Corollaries          | 0    | 1    | 2    | 2    | 0    | 5     |
| Isolated nodes       | 25   | —    | —    | —    | —    | 37    |
| Connected components | 27   | —    | —    | —    | —    | 39    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 205 entities pass the full validation pipeline.

## Sections Breakdown

### 5.1 — Areas and Distances

2 definitions: sigma-notation, area-under-curve.
0 proofs.

Purely definitional section introducing the notation and concept of
area as a limit of Riemann sums. Sigma notation is isolated (not
referenced by any proof).

### 5.2 — The Definite Integral

1 definition: definite-integral.
1 theorem: integrability-of-continuous-functions.
2 propositions: integral-properties, integral-comparison.
3 proofs.

The definite integral definition generalizes area under a curve to
arbitrary continuous functions. The integrability theorem is stated
without proof (assumed, confidence low — requires uniform continuity).
The two propositions establish basic properties used throughout.

### 5.3 — The Fundamental Theorem of Calculus

2 theorems: ftc-part1, ftc-part2.
2 proofs.

The structural heart of the chapter. FTC Part 1 proves that the
integral function g(x) = integral from a to x of f(t) dt is
differentiable with g'(x) = f(x). FTC Part 2 uses Part 1 and the
equal-derivatives-differ-by-constant corollary from Chapter 4.

### 5.4 — Indefinite Integrals and the Net Change Theorem

1 definition: indefinite-integral.
1 theorem: net-change-theorem.
1 proof.

The indefinite integral is defined as notation for the general
antiderivative. The net change theorem follows directly from FTC Part 2.

### 5.5 — The Substitution Rule

2 theorems: substitution-rule, substitution-rule-definite.
1 proposition: integrals-symmetric-functions.
3 proofs.

The substitution rule for indefinite integrals is proved using the
chain rule and antiderivative definition. The definite integral version
extends it using FTC Part 2. The symmetric functions proposition
applies substitution to even/odd functions.

## Reclassifications

No reclassifications needed. All entity types are correctly classified.

## Key Structural Observations

1. **FTC as the central bridge.** The Fundamental Theorem of Calculus
   connects differentiation (Chapters 2-4) to integration (Chapter 5).
   FTC Part 2 depends on the MVT cascade via equal-derivatives-differ-
   by-constant, creating the longest dependency chain in the graph
   (7+ statement hops from EVT to net-change-theorem).

2. **Chain rule to substitution.** The substitution rule is the
   integration counterpart of the chain rule, creating a direct
   cross-chapter link from Chapter 3 differentiation to Chapter 5
   integration.

3. **New hub node.** The FTC Part 1 proof emerged as a hub node
   (degree 6), drawing on 5 prior entities from Chapters 2-5.

4. **EVT propagation deepened.** The EVT's assumed status now
   propagates to 14 downstream proofs (up from 10), with FTC Part 2
   as the critical new link.

5. **Integrability gap.** The integrability-of-continuous-functions
   theorem is assumed without proof (requires Heine-Cantor theorem).
   This is a secondary epistemic debt alongside the EVT.

6. **Largest component: 165 nodes (80%).** The graph continues to
   become more connected, with 4 out of 5 nodes reachable from the
   core chain.

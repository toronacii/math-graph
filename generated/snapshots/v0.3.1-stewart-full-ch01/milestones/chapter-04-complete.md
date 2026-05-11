# Milestone: Chapter 4 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 4 — Applications of Differentiation (Aplicaciones de la derivada)
- **Sections processed:** 4.1, 4.2, 4.3, 4.4, 4.9
- **Sections skipped:** 4.5 (curve sketching), 4.6 (graphing), 4.7 (optimization), 4.8 (Newton's method)

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Ch 1 | Ch 2 | Ch 3 | Ch 4 | Total |
|----------------------|------|------|------|------|-------|
| Statements           | 39   | 36   | 27   | 24   | 126   |
| Proofs               | 7    | 13   | 24   | 13   | 57    |
| Total nodes          | 46   | 49   | 51   | 37   | 183   |
| Total edges          | 21   | 37   | 88   | 48   | 194   |
| Definitions          | 32   | 23   | 3    | 11   | 69    |
| Propositions         | 7    | 2    | 0    | 5    | 14    |
| Theorems             | 0    | 8    | 22   | 6    | 36    |
| Corollaries          | 0    | 1    | 2    | 2    | 5     |
| Isolated nodes       | 25   | —    | —    | —    | 36    |
| Connected components | 27   | —    | —    | —    | 38    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 183 entities pass the full validation pipeline.

## Sections Breakdown

### 4.1 — Maximum and Minimum Values

5 definitions: absolute-maximum, absolute-minimum, local-maximum,
local-minimum, critical-number, closed-interval-method.
2 theorems: extreme-value-theorem, fermat-theorem.
1 proposition: local-extremum-at-critical.
3 proofs.

The Extreme Value Theorem is stated without proof (assumed, confidence
low). Fermat's theorem is proved and serves as the key lemma for
Rolle's theorem.

### 4.2 — The Mean Value Theorem

2 theorems: rolles-theorem, mean-value-theorem.
2 corollaries: zero-derivative-constant, equal-derivatives-differ-by-constant.
4 proofs.

The structural heart of the chapter. Rolle's is proved via EVT +
Fermat's. MVT is proved by reducing to Rolle's via an auxiliary
function. The two corollaries follow directly from MVT.

### 4.3 — How Derivatives Affect the Shape of a Graph

3 definitions: concave-upward, concave-downward, inflection-point.
4 propositions: increasing-decreasing-test, first-derivative-test,
concavity-test, second-derivative-test.
4 proofs.

All propositions are practical criteria proved using the MVT and
the increasing/decreasing test.

### 4.4 — Indeterminate Forms and L'Hopital's Rule

1 definition: indeterminate-form.
1 theorem: lhopitals-rule.
1 proof.

L'Hopital's rule proved for the 0/0 case using the Cauchy MVT.
The ∞/∞ case stated without complete proof.

### 4.9 — Antiderivatives

1 definition: antiderivative.
1 theorem: general-antiderivative.
1 proof.

The general antiderivative theorem connects to the MVT via the
corollary that functions with equal derivatives differ by a constant.

## Reclassifications

No reclassifications needed. All entity types are correctly classified.

## Key Structural Observations

1. **MVT cascade.** The Mean Value Theorem is the structural backbone
   of Chapter 4, feeding (via corollaries) into the derivative tests,
   L'Hopital's rule, and the antiderivative theorem.

2. **EVT epistemic debt.** The Extreme Value Theorem (assumed, low
   confidence) is the highest-impact weak dependency. Via Rolle's → MVT,
   it propagates to 10+ downstream results.

3. **First propositions in bulk.** Chapter 4 introduced 5 new propositions
   (derivative tests), reflecting the shift from theorem-proving to
   practical criteria.

4. **Antiderivative bridge.** The antiderivative definition and general
   antiderivative theorem form the bridge to Chapter 5 (Integrals) and
   the Fundamental Theorem of Calculus.

5. **Largest component: 144 nodes (79%).** The graph is becoming
   increasingly connected, with most entities reachable from the core
   limit/derivative chain.

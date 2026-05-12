# Milestone: Chapter 7 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 7 — Techniques of Integration (Tecnicas de integracion)
- **Sections processed:** 7.1, 7.8
- **Sections skipped:** 7.2 (trig integrals), 7.3 (trig substitution), 7.4 (partial fractions), 7.5 (strategy), 7.6 (tables/CAS), 7.7 (approximate integration)

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Ch 1 | Ch 2 | Ch 3 | Ch 4 | Ch 5 | Ch 6 | Ch 7 | Total |
|----------------------|------|------|------|------|------|------|------|-------|
| Statements           | 39   | 36   | 27   | 24   | 13   | 6    | 5    | 150   |
| Proofs               | 7    | 13   | 24   | 13   | 9    | 1    | 3    | 70    |
| Total nodes          | 46   | 49   | 51   | 37   | 22   | 7    | 8    | 220   |
| Total edges          | 21   | 37   | 88   | 48   | 32   | 7    | 10   | 243   |
| Definitions          | 32   | 23   | 3    | 11   | 4    | 5    | 2    | 80    |
| Propositions         | 7    | 2    | 0    | 5    | 3    | 0    | 0    | 17    |
| Theorems             | 0    | 8    | 22   | 6    | 6    | 1    | 3    | 46    |
| Corollaries          | 0    | 1    | 2    | 2    | 0    | 0    | 0    | 5     |
| Isolated nodes       | 25   | —    | —    | —    | —    | —    | —    | 41    |
| Connected components | 27   | —    | —    | —    | —    | —    | —    | 43    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 220 entities pass the full validation pipeline.

## Sections Breakdown

### 7.1 — Integration by Parts

2 theorems: integration-by-parts, integration-by-parts-definite.
2 proofs.

Integration by parts is derived from the product rule. The definite
version extends it using FTC Part 2.

### 7.8 — Improper Integrals

2 definitions: improper-integral-type1, improper-integral-type2.
1 theorem: comparison-theorem-integrals.
1 proof.

Two types of improper integrals (infinite intervals, discontinuous
integrands) and the comparison theorem for convergence/divergence.

## Reclassifications

No reclassifications needed.

## Key Structural Observations

1. **Heaviest skip ratio.** 6 of 8 sections skipped — the most of
   any chapter. Techniques of integration is predominantly
   methodology without new mathematical entities.

2. **Product rule → IBP link.** Integration by parts creates a new
   cross-chapter bridge from differentiation (product rule, Ch3) to
   integration, mirroring the chain rule → substitution bridge from Ch5.

3. **Comparison theorem foreshadows Ch11.** The comparison theorem
   for improper integrals introduces a pattern (bound smaller by
   larger convergent) that will recur extensively in the convergence
   tests for series.

4. **No new isolated nodes.** All new entities are connected to the
   main component — unusual for application/technique chapters.

5. **Largest component: 176 nodes (80%).** Steady growth continues.

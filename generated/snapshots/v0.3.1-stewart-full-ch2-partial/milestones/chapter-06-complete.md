# Milestone: Chapter 6 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 6 — Applications of Integration (Aplicaciones de la integral)
- **Sections processed:** 6.1, 6.2, 6.3, 6.5
- **Sections skipped:** 6.4 (Work — physics application)

## Extraction Date

2026-05-10

## Graph Summary (Cumulative)

| Metric               | Ch 1 | Ch 2 | Ch 3 | Ch 4 | Ch 5 | Ch 6 | Total |
|----------------------|------|------|------|------|------|------|-------|
| Statements           | 39   | 36   | 27   | 24   | 13   | 6    | 145   |
| Proofs               | 7    | 13   | 24   | 13   | 9    | 1    | 67    |
| Total nodes          | 46   | 49   | 51   | 37   | 22   | 7    | 212   |
| Total edges          | 21   | 37   | 88   | 48   | 32   | 7    | 233   |
| Definitions          | 32   | 23   | 3    | 11   | 4    | 5    | 78    |
| Propositions         | 7    | 2    | 0    | 5    | 3    | 0    | 17    |
| Theorems             | 0    | 8    | 22   | 6    | 6    | 1    | 43    |
| Corollaries          | 0    | 1    | 2    | 2    | 0    | 0    | 5     |
| Isolated nodes       | 25   | —    | —    | —    | —    | —    | 41    |
| Connected components | 27   | —    | —    | —    | —    | —    | 43    |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 212 entities pass the full validation pipeline.

## Sections Breakdown

### 6.1 — Areas Between Curves

1 definition: area-between-curves.
0 proofs.

Defines the area between two curves as the integral of their
difference. Isolated node (not referenced by any proof).

### 6.2 — Volumes

2 definitions: volume-by-cross-sections, volume-of-revolution.
0 proofs.

General volume formula by cross-sections and the specific disk/washer
method. Both are isolated nodes.

### 6.3 — Volumes by Cylindrical Shells

1 definition: volume-by-cylindrical-shells.
0 proofs.

Shell method formula. Isolated node.

### 6.5 — Average Value of a Function

1 definition: average-value-of-function.
1 theorem: mean-value-theorem-integrals.
1 proof.

The Mean Value Theorem for Integrals is the only theorem in this
chapter. Its proof uses both the EVT and IVT (a first in the graph),
plus integral-comparison.

## Reclassifications

No reclassifications needed. All entity types are correctly classified.

## Key Structural Observations

1. **Lightest chapter.** Only 7 new nodes — the least of any chapter.
   This confirms the prediction that Chapter 6 is primarily applications.

2. **High isolation.** 4 of 5 new definitions are isolated nodes.
   These application formulas (area between curves, volumes) are
   endpoints in the knowledge graph — they consume prior results
   but are not consumed by other proofs.

3. **IVT activated.** The Intermediate Value Theorem, previously
   unused by any proof, now has its first downstream consumer via
   the MVT for Integrals.

4. **EVT + IVT convergence.** The MVT for Integrals proof is the
   first to use both the EVT and IVT, connecting two previously
   independent assumed results.

5. **Largest component: 168 nodes (79%).** Growth slowed but
   connectivity remains stable.

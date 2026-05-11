# Milestone: Chapter 11 Complete — Full Book Extraction Done

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 11 — Infinite Sequences and Series (Sucesiones y series infinitas)
- **Sections processed:** 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.8, 11.9, 11.10
- **Sections skipped:** 11.7 (strategy overview), 11.11 (applications)

## Extraction Date

2026-05-10

## FULL BOOK COMPLETE

All 11 chapters of Stewart's Calculus (Single Variable, Early
Transcendentals, 7th Edition) have been processed.

## Final Graph Summary

| Metric               | Ch 1 | Ch 2 | Ch 3 | Ch 4 | Ch 5 | Ch 6 | Ch 7 | Ch 8 | Ch 9 | Ch 10 | Ch 11 | Total |
|----------------------|------|------|------|------|------|------|------|------|------|-------|-------|-------|
| Statements           | 39   | 36   | 27   | 24   | 13   | 6    | 5    | 2    | 3    | 9     | 18    | 182   |
| Proofs               | 7    | 13   | 24   | 13   | 9    | 1    | 3    | 0    | 1    | 0     | 13    | 84    |
| Total nodes          | 46   | 49   | 51   | 37   | 22   | 7    | 8    | 2    | 4    | 9     | 31    | 266   |
| Total edges          | 21   | 37   | 88   | 48   | 32   | 7    | 10   | 0    | 5    | 0     | 45    | 293   |
| Definitions          | 32   | 23   | 3    | 11   | 4    | 5    | 2    | 2    | 2    | 9     | 5     | 98    |
| Propositions         | 7    | 2    | 0    | 5    | 3    | 0    | 0    | 0    | 1    | 0     | 0     | 18    |
| Theorems             | 0    | 8    | 22   | 6    | 6    | 1    | 3    | 0    | 0    | 0     | 13    | 59    |
| Corollaries          | 0    | 1    | 2    | 2    | 0    | 0    | 0    | 0    | 0    | 0     | 0     | 5     |

## Validation Status

All 266 entities pass the full validation pipeline.

## Chapter Density Ranking

| Rank | Chapter | Nodes | Edges | Description               |
|------|---------|-------|-------|---------------------------|
| 1    | Ch 3    | 51    | 88    | Differentiation Rules     |
| 2    | Ch 2    | 49    | 37    | Limits and Derivatives    |
| 3    | Ch 1    | 46    | 21    | Functions and Models      |
| 4    | Ch 4    | 37    | 48    | Applications of Deriv.    |
| 5    | Ch 11   | 31    | 45    | Sequences and Series      |
| 6    | Ch 5    | 22    | 32    | Integrals                 |
| 7    | Ch 10   | 9     | 0     | Parametric/Polar          |
| 8    | Ch 7    | 8     | 10    | Integration Techniques    |
| 9    | Ch 6    | 7     | 7     | Applications of Integ.    |
| 10   | Ch 9    | 4     | 5     | Differential Equations    |
| 11   | Ch 8    | 2     | 0     | Further Applications      |

## Final Structural Observations

1. **266 nodes, 293 edges.** The graph captures 182 mathematical
   statements and 84 proofs from a complete single-variable calculus
   textbook.

2. **Main component: 210 nodes (79%).** The core mathematical
   knowledge from limits through Taylor series is connected in a
   single component.

3. **53 isolated nodes (20%).** Mostly Chapter 1 foundational
   definitions and Chapter 10 geometric definitions that are
   conceptual vocabulary not consumed by proofs.

4. **Top hub: theorem.limit-laws (degree 17).** The limit laws are
   the most connected entity, feeding into virtually all limit-based
   proofs across the book.

5. **Deepest chain: ~12 hops.** EVT → Rolle's → MVT → zero-deriv →
   equal-deriv → FTC2 → substitution-definite → ... The longest
   dependency chains span 5+ chapters.

6. **Critical epistemic debt: Completeness Axiom.** Three assumed
   theorems (EVT, IVT, MST) all require completeness, collectively
   affecting 23+ downstream proofs. A single axiom node would
   resolve the majority of epistemic debt.

7. **Chapter 3 is the densest.** The differentiation rules chapter
   produced the most edges (88), reflecting the large number of
   derivative formulas each proved from prior rules.

8. **Chapters 6, 8, 10 are application chapters** with few or no
   proofs, adding mostly isolated definitional nodes.

# Rudin Chapter 5 — Differentiation: Structural Analysis

## Overview

Chapter 5 covers differentiation of real functions and its main consequences:
the mean value theorems, L'Hospital's rule, Taylor's theorem, and
differentiation of vector-valued functions.

## Key Characteristics

### High Overlap with Stewart

This chapter has the highest overlap with Stewart of any Rudin chapter so far:
- **9 shared theorems/propositions/corollaries** (added Rudin source + independent proof)
- **4 shared definitions** (added Rudin source)
- Only **6 genuinely new statements** introduced

This makes sense: differentiation on R is essentially the same subject in both
books. The divergence comes in generality (Rudin covers vector-valued
functions) and completeness (Rudin proves L'Hospital's rule rigorously for
both 0/0 and infinity/infinity cases).

### Proof Architecture

Rudin's proof structure differs from Stewart's in several important ways:

1. **No Rolle's theorem** — Rudin goes directly to the generalized MVT (5.9),
   which subsumes both Rolle's theorem and the ordinary MVT. Stewart uses
   Rolle's as an intermediate step.

2. **Generalized MVT as foundation** — Rudin derives MVT (5.10) as a
   corollary of the generalized MVT (5.9), and uses the generalized MVT
   directly to prove L'Hospital's rule (5.13).

3. **Taylor's theorem via repeated MVT** — The proof applies MVT n times
   in succession, a clean inductive argument.

4. **Vector-valued inequality** — Theorem 5.19 provides a substitute for MVT
   in R^k, since the equality form fails (Example 5.17). The proof by Havin
   reduces to the real case via inner products and the Schwarz inequality.

### Hub Nodes

After Ch5, the most connected nodes in the differentiation subgraph:

| Node | Role |
|------|------|
| `definition.derivative-at-point` | Used by 8 proofs in Ch5 |
| `theorem.mean-value-theorem` | Used by 5 proofs (inc/dec, constant, Taylor, vector MVT) |
| `theorem.limit-laws` | Used by 4 proofs (sum, product, quotient, diff⟹cont) |
| `theorem.fermat-theorem` | Used by 3 proofs (gen. MVT, Darboux, itself) |
| `theorem.generalized-mean-value-theorem` | Used by 2 proofs (MVT, L'Hospital) |

### Dependency Chain

The main dependency chain in Ch5:

```
definition.derivative-at-point
  → theorem.differentiable-implies-continuous
  → theorem.fermat-theorem
  → theorem.generalized-mean-value-theorem
    → theorem.mean-value-theorem
      → proposition.increasing-decreasing-test
      → corollary.zero-derivative-constant
      → theorem.taylor-theorem
      → theorem.mean-value-inequality-vector
    → theorem.lhopitals-rule
  → theorem.darboux-theorem
    → corollary.derivative-no-simple-discontinuities
```

### New vs Shared Analysis

| Category | Count | Notes |
|----------|-------|-------|
| Shared definitions | 4 | derivative, local max/min, second derivative |
| Shared theorems | 9 | All core differentiation results |
| New theorems | 5 | gen. MVT, Darboux, Taylor, vector MVT inequality, sum rule |
| New corollaries | 1 | derivative has no simple discontinuities |
| New proofs | 15 | Independent Rudin proofs for all results |

### Growth Expectations

Chapter 6 (Riemann-Stieltjes Integral) will introduce significant new content:
- Riemann-Stieltjes integral definition and properties
- Integration of continuous functions
- Fundamental theorem of calculus (should share with Stewart)
- Integration by parts
- Expected ~40-60 new entities, moderate overlap with Stewart Ch5-6.

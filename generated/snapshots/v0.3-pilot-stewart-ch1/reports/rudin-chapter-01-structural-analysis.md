# Rudin Chapter 1 — Structural Analysis

## 1. Conceptual Density

Chapter 1 of Rudin produces 34 statements and 18 proofs across 33
numbered sections (1.1 through 1.37, skipping some). The chapter
divides into five major conceptual blocks:

| Block                        | Sections    | Definitions | Propositions | Theorems | Proofs |
|------------------------------|-------------|-------------|--------------|----------|--------|
| Introduction & Ordered Sets  | 1.1–1.10    | 7           | 1            | 0        | 1      |
| Fields                       | 1.11–1.18   | 2           | 4            | 1        | 5      |
| The Real Field               | 1.19–1.22   | 0           | 0            | 3+1 cor  | 4      |
| Extended Reals               | 1.23        | 1           | 0            | 0        | 0      |
| Complex Field & Euclidean Rk | 1.24–1.37   | 6           | 0            | 8        | 8      |

The Real Field block (1.19–1.21) is the mathematical core. It
contains the three central theorems: existence of R, archimedean
property / density of Q, and existence of nth roots.

## 2. Dependency Structure

The Rudin Ch1 subgraph has 52 nodes, 65 edges, and density 0.0245.
This is significantly denser than Stewart Ch1 (0.0101) because
Rudin's theorems build on each other in chains rather than standing
in isolation.

Key structural features:

- 3 weakly connected components within the Rudin subgraph.
- The main component contains 47 of 52 nodes (90%).
- Only 3 nodes are fully isolated (set-membership-subset,
  rational-numbers, extended-reals).

## 3. Hub Nodes

The most connected nodes in the Rudin Ch1 subgraph:

| Node                               | Degree | Role                         |
|--------------------------------------|--------|------------------------------|
| definition.field                     | 7      | Referenced by 5 proofs       |
| proof.existence-of-reals.rudin       | 7      | Uses 6 definitions           |
| definition.complex-number            | 5      | Foundation for complex theory |
| proof.existence-of-nth-roots.rudin   | 5      | Uses 4 prior results         |
| proof.lub-implies-glb.rudin          | 5      | Uses 4 definitions           |

`definition.field` is the single most reused definition, serving as a
dependency for proofs across both the field-properties block and the
complex-field block.

## 4. Graph Layering

The Rudin Ch1 graph exhibits a natural four-layer structure:

```
Layer 0 (foundations):   order-relation, ordered-set, upper-bound, supremum,
                         least-upper-bound-property, field, ordered-field,
                         rational-numbers, set-membership-subset
Layer 1 (core theorems): lub-implies-glb, addition-cancellation,
                         multiplication-cancellation, field-zero-product,
                         ordered-field-properties
Layer 2 (R construction): existence-of-reals, archimedean-density,
                          existence-of-nth-roots, nth-root-of-product
Layer 3 (C and Rk):      complex-number, complex-field, conjugate-properties,
                          complex-absolute-value-properties, schwarz-inequality,
                          euclidean-norm-properties
```

This layering reflects Rudin's pedagogical approach: ordered sets and
fields provide the abstract framework, the real field is constructed
from these, and then complex numbers and euclidean spaces are built
on top of R.

## 5. Dependency Chains

The longest dependency chain (statement depth 4):

```
definition.field
  -> proof.addition-cancellation.rudin
    -> proposition.addition-cancellation
      -> proof.field-zero-product.rudin
        -> proposition.field-zero-product
          -> proof.ordered-field-properties.rudin
            -> proposition.ordered-field-properties
              -> proof.existence-of-nth-roots.rudin
                -> theorem.existence-of-nth-roots
```

A second important chain runs through the complex number theory:

```
definition.complex-number
  -> proof.complex-field.rudin
    -> theorem.complex-field
definition.imaginary-unit + theorem.real-subfield-of-complex
  -> proof.complex-algebraic-form.rudin
    -> theorem.complex-algebraic-form
definition.complex-conjugate
  -> proof.conjugate-properties.rudin
    -> theorem.conjugate-properties
      -> proof.complex-absolute-value-properties.rudin
        -> theorem.complex-absolute-value-properties
```

## 6. Cross-Source Connections

Currently there are 0 cross-source edges between Rudin and Stewart
nodes. This is expected: Rudin Ch1 establishes foundational concepts
(fields, ordered sets, completeness) that Stewart assumes without
proof. The key connection points that will emerge in future chapters:

- `definition.least-upper-bound-property` — Stewart's monotonic
  sequence theorem implicitly uses this.
- `theorem.existence-of-reals` — Stewart assumes R exists and is
  complete; Rudin proves it.
- `definition.field` — Stewart uses field properties throughout
  without axiomatizing them.

These connections represent the primary value of integrating Rudin
into the graph: Rudin provides the foundational layer that Stewart
takes for granted.

## 7. Growth Expectations

### Rudin Chapter 2 — Basic Topology

Expected impact:

- **New concepts:** metric space, open/closed sets, compact sets,
  connected sets, perfect sets, Cantor set.
- **Key theorems:** Heine-Borel, Bolzano-Weierstrass, nested
  intervals, Baire category.
- **Dependencies on Ch1:** definition.ordered-set, definition.supremum,
  theorem.archimedean-density, definition.euclidean-k-space.
- **Cross-source:** Rudin's metric space definitions will provide
  the foundation for Stewart's implicit use of distance and
  neighborhoods in limit definitions.

### Rudin Chapter 3 — Numerical Sequences and Series

Expected impact:

- **Convergence, Cauchy sequences, completeness** will create deep
  dependency chains back to Ch1's LUB property.
- **Root and ratio tests** will connect to nth-root existence
  (Theorem 1.21).

## 8. Contrast with Stewart Chapter 1

| Metric                  | Stewart Ch1 | Rudin Ch1 |
|-------------------------|-------------|-----------|
| Total nodes             | 46          | 52        |
| Statements              | 39          | 34        |
| Proofs                  | 7           | 18        |
| Definitions             | 32          | 16        |
| Propositions            | 7           | 5         |
| Theorems                | 0           | 12        |
| Graph density           | 0.0101      | 0.0245    |
| Isolated nodes          | 25 (54%)    | 3 (6%)    |
| Connected components    | 27          | 3         |
| Max dependency depth    | 3           | 4+        |

Key differences:

1. **Rudin is theorem-heavy, Stewart is definition-heavy.** Stewart
   Ch1 introduces vocabulary; Rudin Ch1 proves fundamental results.
2. **Rudin is far more connected.** Only 6% of Rudin nodes are
   isolated vs 54% for Stewart. This reflects the deductive nature
   of analysis vs the descriptive nature of introductory calculus.
3. **Rudin has deeper dependency chains.** The longest chain has
   statement-depth 4 vs 3 for Stewart. Theorems build on each other.
4. **Rudin's proofs are rigorous.** All 18 proofs have confidence:
   high. Stewart has 1 proof with confidence: low (laws of exponents).

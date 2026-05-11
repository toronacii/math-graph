# Chapter 1 — Structural Analysis

## 1. Conceptual Density

Chapter 1 produces 39 statements across 5 sections, averaging 7.8
statements per section. However, the distribution is uneven:

| Section | Statements | Proofs | Density |
|---------|-----------|--------|---------|
| 1.1     | 14        | 1      | high    |
| 1.2     | 8         | 0      | medium  |
| 1.3     | 6         | 0      | medium  |
| 1.4     | 3         | 1      | low     |
| 1.5     | 8         | 5      | high    |

Section 1.1 is the densest in definitions because it establishes the
foundational vocabulary (function, domain, range, symmetry, monotonicity).
Section 1.5 is the densest in propositions because inverse functions
generate multiple testable properties.

## 2. Dependency Sparsity

The graph has a density of 0.0101 (21 edges / 2070 possible edges).
This extreme sparsity is structurally expected. Chapter 1 is a
vocabulary layer: it introduces terminology that later chapters will
reference, but it generates few internal dependencies.

Key sparsity metrics:

- 25 of 46 nodes (54%) are completely isolated.
- 7 of 32 definitions (22%) participate in at least one proof.
- The remaining 25 definitions are dormant roots awaiting consumers.

This sparsity will decrease sharply as Chapter 2 introduces limit
theorems that depend on definitions from Chapter 1.

## 3. Emergence of Reusable Propositions

Two propositions function as reusable intermediate results:

- **proposition.laws-of-exponents** feeds into
  proof.laws-of-logarithms.stewart.
- **proposition.laws-of-logarithms** feeds into
  proof.change-of-base-formula.stewart.

These are the only propositions that act as both targets (proved by a
proof) and sources (used by another proof). This dual role marks them
as structurally important: they are the first reusable mathematical
results in the graph.

The remaining 5 propositions are terminal leaf nodes. They assert facts
but no other proof in Chapter 1 depends on them. This will change in
future chapters (e.g., the vertical line test is foundational for
reasoning about graphs of functions in Chapter 2).

## 4. Proof Topology

All 7 proofs are direct (one-step) proofs, except
proof.laws-of-exponents.stewart which has style: assumed.

Proof fan-in (number of `uses` dependencies per proof):

| Proof                                  | Fan-in |
|----------------------------------------|--------|
| proof.vertical-line-test.stewart       | 2      |
| proof.horizontal-line-test.stewart     | 2      |
| proof.laws-of-exponents.stewart        | 1      |
| proof.cancellation-equations.stewart   | 2      |
| proof.inverse-graph-reflection.stewart | 2      |
| proof.laws-of-logarithms.stewart       | 2      |
| proof.change-of-base-formula.stewart   | 3      |

Average fan-in: 2.0. The proofs in Chapter 1 are shallow, drawing from
1-3 dependencies each. Future chapters will produce proofs with higher
fan-in as theorems combine multiple prior results.

## 5. Graph Layering

The graph exhibits a natural layering:

```
Layer 0 (roots):     32 definitions — no incoming edges
Layer 1 (proofs):     7 proofs      — consume definitions/propositions
Layer 2 (results):    7 propositions — produced by proofs
```

However, two propositions break this clean layering by feeding back into
Layer 1 as inputs to other proofs:

```
Layer 0: definition.exponential-function
Layer 1: proof.laws-of-exponents.stewart
Layer 2: proposition.laws-of-exponents        <-- also feeds Layer 1
Layer 1: proof.laws-of-logarithms.stewart
Layer 2: proposition.laws-of-logarithms       <-- also feeds Layer 1
Layer 1: proof.change-of-base-formula.stewart
Layer 2: proposition.change-of-base-formula
```

This cascading pattern will become the dominant graph structure in later
chapters, where theorems build on theorems through multiple proof layers.

## 6. Chains of Mathematical Reuse

The graph contains one significant dependency chain and one independent
cluster.

**Chain A — Exponential-logarithmic cascade (depth 3):**

```
exponential-function -> laws-of-exponents -> laws-of-logarithms -> change-of-base-formula
```

This chain captures a real mathematical dependency: logarithm properties
derive from exponent properties, and the change of base formula derives
from logarithm properties.

**Cluster B — Function-graph-inverse cluster (4 propositions):**

Four propositions share a common definitional base (function,
graph-of-function, one-to-one-function, inverse-function) but do not
depend on each other. They form a fan-out pattern from shared roots.

## 7. Provisional Roots

All 32 definitions are root nodes. However, some roots are more
structurally significant than others based on their fan-out:

| Root                             | Fan-out | Used by                              |
|----------------------------------|---------|--------------------------------------|
| definition.graph-of-function     | 3       | 3 proofs                             |
| definition.one-to-one-function   | 2       | 2 proofs                             |
| definition.inverse-function      | 2       | 2 proofs                             |
| definition.logarithmic-function  | 2       | 2 proofs                             |
| definition.function              | 1       | 1 proof                              |
| definition.exponential-function  | 1       | 1 proof                              |
| definition.natural-logarithm     | 1       | 1 proof                              |
| (25 others)                      | 0       | dormant — no proof references yet    |

The high fan-out of `definition.graph-of-function` reflects its role as
a shared geometric tool across multiple proofs. It is expected to remain
a high-connectivity node in future chapters.

## 8. Growth Expectations

### Chapter 2 — Limits and Derivatives

Expected impact:

- **New entity types:** First theorems (limit laws, squeeze theorem,
  intermediate value theorem), first lemmas, possible corollaries.
- **Edge growth:** Limit theorems will reference multiple Chapter 1
  definitions (function, domain, composition-of-functions). Many
  currently isolated nodes will gain edges.
- **Proof depth:** Proofs in Chapter 2 are multi-step, often combining
  3-5 prior results. Proof fan-in will increase.
- **Cross-chapter references:** Chapter 2 proofs will reference
  Chapter 1 definitions, creating the first cross-layer dependencies.

### Chapters 3-4 — Differentiation and Applications

Expected impact:

- **Chain rule** will activate definition.composition-of-functions.
- **Derivative of exponential/logarithmic functions** will extend
  Chain A significantly.
- **Power rule** will activate definition.polynomial and
  definition.power-function.
- **Mean Value Theorem** will produce the first deep theorem with
  multiple proof pathways.

### Density projection

| Chapter | Estimated nodes | Estimated edges | Projected density |
|---------|----------------|-----------------|-------------------|
| 1       | 46             | 21              | 0.010             |
| 2       | ~90            | ~80             | ~0.010            |
| 3       | ~130           | ~180            | ~0.011            |
| 4       | ~170           | ~300            | ~0.010            |

Density is expected to remain low (~0.01) because the number of
possible edges grows quadratically while actual mathematical
dependencies grow linearly. The graph will remain sparse but structured.

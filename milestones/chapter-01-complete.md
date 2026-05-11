# Milestone: Chapter 1 Complete

## Source

- **Textbook:** James Stewart — Calculo de una variable: Trascendentes tempranas
- **Edition:** 7th (Septima edicion)
- **Publisher:** Cengage Learning, 2012
- **Language:** Spanish (original), English (translations added)
- **Chapter:** 1 — Functions and Models (Funciones y modelos)
- **Sections processed:** 1.1 through 1.5

## Extraction Date

2026-05-10

## Graph Summary

| Metric            | Value |
|-------------------|-------|
| Total nodes       | 46    |
| Total edges       | 21    |
| Statements        | 39    |
| Proofs            | 7     |
| Definitions       | 32    |
| Propositions      | 7     |
| Theorems          | 0     |
| Lemmas            | 0     |
| Corollaries       | 0     |
| Axioms            | 0     |
| Conjectures       | 0     |
| Isolated nodes    | 25    |
| Connected components | 27 |

## Validation Status

- Schema validation: PASS
- ID uniqueness: PASS
- Reference integrity: PASS
- Symmetry (proved_by <-> proves): PASS
- Acyclicity: PASS

All 46 entities pass the full validation pipeline.

## Sections Breakdown

### 1.1 — Four Ways to Represent a Function

13 definitions: function, domain, range, graph-of-function, even-function,
odd-function, increasing-function, decreasing-function, piecewise-function,
absolute-value, independent-variable, dependent-variable.
1 proposition: vertical-line-test.

### 1.2 — Mathematical Models: A Catalog of Essential Functions

8 definitions: mathematical-model, linear-function, polynomial,
power-function, rational-function, algebraic-function,
trigonometric-function, transcendental-function.

### 1.3 — New Functions from Old Functions

6 definitions: vertical-shift, horizontal-shift,
vertical-stretch-compression, horizontal-stretch-compression, reflection,
composition-of-functions.

### 1.4 — Exponential Functions

2 definitions: exponential-function, natural-exponential-function.
1 proposition: laws-of-exponents.

### 1.5 — Inverse Functions and Logarithms

5 definitions: one-to-one-function, inverse-function,
logarithmic-function, natural-logarithm, horizontal-line-test.
4 propositions: horizontal-line-test, cancellation-equations,
inverse-graph-reflection, laws-of-logarithms, change-of-base-formula.

## Emerging Dependency Chains

The longest dependency chain in the graph traverses three proposition
levels:

```
definition.exponential-function
  -> proof.laws-of-exponents.stewart
    -> proposition.laws-of-exponents
      -> proof.laws-of-logarithms.stewart
        -> proposition.laws-of-logarithms
          -> proof.change-of-base-formula.stewart
            -> proposition.change-of-base-formula
```

This chain (depth 3 at the statement level) demonstrates how
foundational algebra cascades through logarithmic theory. It is expected
to deepen significantly when Chapter 2 introduces limits, as the
exponential and logarithmic functions become central to derivative
computation.

A second independent cluster connects:

```
definition.function + definition.graph-of-function
  -> proposition.vertical-line-test

definition.one-to-one-function + definition.graph-of-function
  -> proposition.horizontal-line-test

definition.inverse-function + definition.one-to-one-function
  -> proposition.cancellation-equations

definition.inverse-function + definition.graph-of-function
  -> proposition.inverse-graph-reflection
```

These four propositions share definitions as common roots, forming a
tightly coupled subgraph around the concepts of function, graph, and
invertibility.

## Observations

1. **Vocabulary-heavy chapter.** Chapter 1 is primarily definitional.
   32 of 39 statements are definitions. This is expected: Stewart uses
   Chapter 1 to establish the conceptual vocabulary before introducing
   theorems with proofs in Chapter 2.

2. **Sparse proof topology.** Only 7 proofs exist, all for propositions.
   No theorems, lemmas, or corollaries appear. Proof density will
   increase sharply in Chapters 2-4.

3. **One weak dependency.** The proof for laws-of-exponents has
   confidence: low and style: assumed. Stewart does not derive exponent
   laws in Chapter 1; he imports them from precalculus. This creates an
   epistemic debt that propagates to laws-of-logarithms and
   change-of-base-formula.

4. **High isolation ratio.** 25 of 46 nodes (54%) are isolated. These
   definitions do not participate in any proof yet. Most will gain edges
   in future chapters (e.g., definition.composition-of-functions is
   essential for the chain rule in Chapter 3).

5. **Reclassification validated.** Two entities (vertical-line-test,
   horizontal-line-test) were reclassified from definition to proposition
   during review. The classification guide has been added to AGENTS.md
   to prevent future misclassifications.

## Architectural Decisions Validated

- **Statement-Proof-Statement model:** The `uses -> proof -> proves`
  architecture works correctly. Edges flow from definitions into proofs
  and from proofs into propositions. No statement-to-statement shortcuts
  exist.

- **Symmetry enforcement:** The `proved_by` field on statements mirrors
  the `proves` field on proofs. The validator catches asymmetries.

- **Confidence tracking:** The `confidence: low` and `style: assumed`
  fields on proof.laws-of-exponents.stewart demonstrate that epistemic
  uncertainty can be tracked without breaking the graph.

- **Reclassification workflow:** Renaming an entity (changing type and
  ID) works cleanly: delete old file, create new file, update references.
  The validator catches dangling references during the process.

- **i18n content:** All 39 statements carry bilingual (en/es) titles and
  natural-language descriptions. The schema enforces at least one
  language entry.

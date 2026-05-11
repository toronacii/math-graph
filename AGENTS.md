# Mathematical Knowledge Graph (MKG)

> **Status (2026-05-11): transitioning from v0.2 → v0.3.**
>
> The full v0.2 prototype graph (Stewart Ch1–11 + Rudin Ch1–6, 527 nodes /
> 687 edges) is **frozen** at `generated/snapshots/v0.2/` as a historical
> baseline. v0.3 is a clean redesign — semantically hardened schema, two-layer
> dependency graph (proof-uses + statement-depends_on), six-axis quality
> assessment, and a snapshot-based rerun architecture.
>
> **Authoritative reference for v0.3:** see `docs/v0.3/` (schema, pipeline,
> migration, archival, rerun checklist).
>
> The schema, classification, multi-source disambiguation and per-chapter
> pipeline sections in this file describe the **v0.2 pipeline only** and are
> retained for historical context. They will be retired once the v0.3 rerun
> completes. New extraction work targets v0.3 — do not author files against
> the v0.2 schema.

## Overview

This repository contains a structured graph representation of mathematical knowledge.

The goal is NOT to fully formalize mathematics in a proof assistant.

The goal is to:

* map mathematical knowledge as a dependency graph,
* identify how theorems emerge from prior statements,
* preserve multiple proof pathways,
* enable historical and structural analysis,
* and eventually support higher-level mathematical heuristics.

The graph is human-readable, machine-readable, and collaboration-oriented.

---

# Core Philosophy

The graph models:

```text
Statement → Proof → Statement
```

A statement is NOT directly connected to another statement.

Instead:

* statements participate in proofs,
* proofs establish statements.

This distinction is fundamental.

---

# Entity Types

Supported entity types:

* axiom
* definition
* lemma
* proposition
* theorem
* corollary
* conjecture
* proof

Additional types may be added later.

---

# Repository Structure

```text
data/
  statements/
  proofs/

sources/
  stewart/
  euclid/
  rudin/

generated/
  graph/
  exports/
```

---

# Statement Rules

Each statement MUST:

* have a globally unique id,
* define a type,
* contain at least one natural-language representation,
* optionally include LaTeX,
* include source metadata,
* avoid proof implementation details.

Statements are conceptual nodes.

They are NOT proof traces.

---

# Proof Rules

Proof nodes describe:

* what statement they prove,
* which statements they use,
* optional metadata about proof style,
* source references.

Proofs DO NOT contain full formal derivations.

The current phase only tracks dependency structure.

---

# Language Rules

## Schema Language

ALL schema keys MUST be written in English.

Examples:

```yml
title:
statement:
sources:
proved_by:
uses:
```

NEVER use Spanish keys.

---

## Human Content Language

Human-readable content supports i18n.

Example:

```yml
title:
  en: Pythagorean Theorem
  es: Teorema de Pitágoras
```

The original language from the source material MUST be preserved.

---

# Mathematical Representation

## Current Standard

Human-readable mathematics MUST use LaTeX.

Example:

```latex
a^2 + b^2 = c^2
```

DO NOT introduce custom mathematical syntaxes.

DO NOT use programming-language syntax as canonical representation.

---

# Current Scope

Current phase goals:

* identify statements,
* identify proof dependencies,
* build graph structure,
* preserve source traceability.

Current phase DOES NOT include:

* semantic ASTs,
* theorem proving,
* proof assistants,
* symbolic execution,
* Lean/Coq formalization,
* step-by-step derivations.

Those may appear in future phases.

---

# Extraction Principles

When extracting from textbooks:

* preserve the author's conceptual hierarchy,
* preserve theorem boundaries,
* preserve explicit dependencies when possible,
* avoid hallucinating hidden dependencies,
* avoid overformalization.

If dependency certainty is unclear:

```yml
confidence: low
```

---

# ID Conventions

IDs MUST be stable and globally unique.

Examples:

```text
theorem.limit-laws
definition.function
lemma.squeeze-theorem
proof.squeeze-theorem.stewart
```

Recommended pattern:

```text
<type>.<normalized-name>
```

Proof IDs:

```text
proof.<statement>.<source-or-style>
```

---

# Minimal Statement Example

```yml
id: theorem.pythagorean-theorem
type: theorem
status: draft

title:
  en: Pythagorean Theorem
  es: Teorema de Pitágoras

statement:
  natural:
    es: >
      En un triángulo rectángulo...

  latex: |
    a^2 + b^2 = c^2

proved_by:
  - proof.pythagorean.similar-triangles

sources:
  - work: Euclid Elements
```

---

# Minimal Proof Example

```yml
id: proof.pythagorean.similar-triangles
type: proof

proves: theorem.pythagorean-theorem

uses:
  - definition.right-triangle
  - definition.similar-triangles
  - theorem.similar-triangles-proportional-sides
```

---

# Human Validation

AI extraction is ASSISTIVE, not authoritative.

All extracted entities should eventually be reviewed by humans.

The repository prioritizes:

* correctness,
* traceability,
* explainability,
* collaborative refinement.

---

# Entity Classification Guide

Classification quality is critical for long-term graph consistency.

## Definition

Use `definition` when:

* a new mathematical object is introduced,
* terminology is established,
* notation is defined,
* a concept is formally described,
* the text explains what something *is*.

Typical patterns:

```text
"A function is..."
"We define..."
"An even function is..."
"The domain of a function is..."
```

Definitions DO NOT assert truth conditions requiring proof.

## Proposition

Use `proposition` when:

* a reusable mathematical fact is stated,
* a criterion or test is introduced,
* a practical result is presented,
* the statement is important but not treated as a major theorem.

Typical patterns:

```text
"A graph represents a function if and only if..."
"The Vertical Line Test states..."
"If f is one-to-one, then..."
```

Many textbook rules, tests, and criteria belong here.

## Theorem

Use `theorem` when:

* the result is mathematically central,
* the book explicitly calls it a theorem,
* the result has broad structural importance.

## Lemma

Use `lemma` when:

* the statement primarily exists to support another theorem,
* the book explicitly calls it a lemma.

## Corollary

Use `corollary` when:

* the statement follows almost immediately from another theorem,
* the book explicitly labels it as a corollary.

## Axiom

Use `axiom` only when:

* the statement is assumed without proof,
* it is foundational to the mathematical system (field axioms, order axioms, etc.).

Do NOT classify ordinary textbook assumptions as axioms.

## Conjecture

Use `conjecture` only when the text explicitly presents a statement as open or unproven.

## Key Distinction: Definition vs Proposition

A definition introduces meaning. A proposition asserts a reusable truth.

```text
"An even function satisfies f(-x) = f(x)."         → definition
"A curve is a function iff no vertical line cuts it twice." → proposition
```

The second establishes a criterion, not a new object.

## Reclassification Rules

When reviewing existing entities:

* keep the current classification if correct,
* replace it with a better type if misclassified,
* DO NOT invent new entities, rewrite content, split, or merge entities,
* only improve classification.

Prioritize: semantic correctness > graph consistency > reusable structure.

---

# Per-Chapter Extraction Pipeline (v0.2 — historical)

> **v0.2 only.** This four-phase pipeline ran the original prototype build
> (Stewart Ch1–11 + Rudin Ch1–6, frozen at `generated/snapshots/v0.2/`).
> v0.3 replaces it with a snapshot-based rerun workflow — see
> `docs/v0.3/04-pipeline.md` and `docs/v0.3/13-rerun-checklist.md`.
> The v0.2 commands below (`scripts.validate`, `scripts.build_graph`,
> `generated/graph/`) target the legacy schema in `schema/models.py` and
> must NOT be used for new v0.3 extraction.

Each chapter follows a fixed four-phase pipeline:

## Phase 1 — Extract

Process the chapter section by section. For each section:

1. Identify every statement (definition, proposition, theorem, lemma, corollary, axiom, conjecture).
2. Create a YAML file per statement in `data/statements/`.
3. Identify proof dependencies and create proof nodes in `data/proofs/`.
4. Wire `proved_by` links from statements to their proofs.

## Phase 2 — Validate

Run the validation script:

```bash
python -m scripts.validate
```

Fix all errors before proceeding.

## Phase 3 — Reclassify

Review every entity extracted in the chapter:

* Check entity type classification against the Entity Classification Guide.
* Fix misclassified types (rename file, update `id`, `type`, and all references).
* Remove stale files after reclassification.

## Phase 4 — Reports & Milestone

1. Rebuild the graph: `python -m scripts.build_graph`
2. Generate three report files:
   - `reports/chapter-NN-statistics.yml` — cumulative node/edge counts, density, components.
   - `reports/chapter-NN-structural-analysis.md` — hub nodes, layering, growth expectations.
   - `reports/chapter-NN-weak-dependencies.yml` — low-confidence proofs, implicit imports, epistemic debt.
3. Create a milestone file: `milestones/chapter-NN-complete.md`.
4. Sync graph data to visualization: `cp generated/graph/graph.json visualization/web/public/graph.json`.

---

# Initial Objective

Initial target:

```text
Stewart Calculus
Chapter 1
Functions and Models
```

The objective is to validate:

* extraction pipeline,
* graph schema,
* dependency granularity,
* proof-node architecture,
* collaborative workflow.

---

# Initial Source Material

Primary initial source:

James Stewart — Cálculo de una variable: Trascendentes tempranas, Séptima edición.

Initial processing target:

```text
Chapter 1 — Functions and Models
```

Future versions of the repository must support multiple textbooks, historical sources, and parallel formulations of mathematical knowledge.

---

# Multi-Source Disambiguation Guide

The graph aspires to represent ALL of human mathematics, not just
one textbook. When integrating a second (or nth) source, disambiguation
is critical.

## Core Principle

A statement node represents a **mathematical truth**, not a page in
a book. Two authors describing the same mathematical fact share one
node with multiple sources. Two authors describing genuinely different
mathematical facts get separate nodes, even if they use the same name.

## Identity Criterion

Two statements from different sources are **the same node** if and
only if they are **logically equivalent** in their full generality.

NOT equivalent restricted to a specific domain (e.g., R).
NOT equivalent "in spirit" or "informally."
Logically equivalent — same hypotheses, same conclusion, same
mathematical objects.

## Decision Procedure

When a new source presents a statement that resembles an existing node:

### Step 1 — Compare Formal Content

Compare the mathematical content (LaTeX / formal statement), ignoring:

* language differences (English vs Spanish vs French),
* notational conventions (f vs φ, x vs t),
* cosmetic phrasing differences.

If the hypotheses and conclusions are identical up to notation:
**same node**. Go to Step 3.

### Step 2 — Check Generality

If the statements differ, determine the relationship:

* **Strictly more general.** The new statement subsumes the existing
  one as a special case. Create a NEW node for the general version.
  The existing node may become a corollary of the new one, or remain
  as-is with a proof that uses the more general result.

  Example:
  ```
  Stewart: "Continuous on [a,b] implies maximum and minimum" (EVT)
  Rudin:   "Continuous image of a compact set is compact"
  ```
  These are DIFFERENT nodes. The EVT becomes a corollary once
  compactness is in the graph.

* **Strictly less general.** The new statement is a special case of
  an existing node. Create a NEW node (likely a corollary) or add
  a proof that derives it from the existing one.

* **Overlapping but incomparable.** Different hypotheses, different
  conclusions, neither subsumes the other. Create a NEW node.

* **Equivalent but differently formulated.** Same mathematical content,
  different presentation. **Same node.** Add the source.

### Step 3 — Merge Sources

When confirmed as the same node:

1. Add the new source to the `sources` list of the existing statement.
2. If the new source provides a different title, add it to `title`
   (under the appropriate language key).
3. If the new source provides a new natural-language formulation,
   add it under `statement.natural` (new language key or improved
   wording).
4. Do NOT change the `id` — it remains stable.

### Step 4 — Add Proofs

Each source's proof is a **separate proof node**, even for the same
statement:

```yaml
proved_by:
  - proof.extreme-value-theorem.stewart    # assumed
  - proof.extreme-value-theorem.rudin      # rigorous, from compactness
```

Different proofs use different dependencies and have different
confidence levels. They are always separate files.

## Disambiguation Markers

When a disambiguation decision is non-trivial, add a `notes` field:

```yaml
notes: >
  Identified as the same statement as Rudin Theorem 4.16.
  Rudin's formulation uses compactness; Stewart restricts to [a,b].
  In R with the standard topology, [a,b] is compact (Heine-Borel),
  so the statements are equivalent in this context. However, Rudin's
  version is strictly more general in arbitrary metric spaces.
  Decision: SEPARATE nodes. Rudin's version is
  theorem.continuous-image-compact; Stewart's EVT becomes a corollary
  via Heine-Borel.
```

## Naming Conflicts

When two sources use the same name for different results, or different
names for the same result:

* The `id` follows the most standard mathematical name, not any
  particular author's convention.
* The `title` field captures all names via i18n or notes.
* If names conflict irreconcilably, prefer the name used by the
  broadest mathematical community.

## Classification Across Sources

When two sources classify the same result differently (e.g., one
calls it a theorem, the other a proposition):

* Use the classification that best fits the Entity Classification
  Guide in this document.
* The classification reflects the result's role in the graph, not
  any single author's editorial choice.
* Document the discrepancy in `notes`.

## Scope

The graph has NO domain restriction. It is designed to eventually
contain all of human mathematics. Disambiguation decisions must be
made with this long-term scope in mind — do not collapse distinct
results into one node just because they coincide in a restricted
context.

# Schema

Pydantic v2 models for MKG entities. JSON Schema files in this folder are generated from the models — do not edit by hand.

## Regenerate

```bash
uv run python scripts/export_schema.py
```

## Entities

- [`Statement`](models.py) — axioms, definitions, lemmas, propositions, theorems, corollaries, conjectures.
- [`Proof`](models.py) — links one statement (`proves`) to its dependencies (`uses`).
- [`Source`](models.py) — bibliographic locator.

## Minimal examples

Statement:

```yaml
id: theorem.pythagorean-theorem
type: theorem
status: draft
title:
  en: Pythagorean Theorem
  es: Teorema de Pitágoras
statement:
  natural:
    es: "En un triángulo rectángulo, el cuadrado de la hipotenusa es la suma de los cuadrados de los catetos."
  latex: |
    a^2 + b^2 = c^2
proved_by:
  - proof.pythagorean-theorem.similar-triangles
sources:
  - work: Euclid Elements
```

Proof:

```yaml
id: proof.pythagorean-theorem.similar-triangles
type: proof
proves: theorem.pythagorean-theorem
uses:
  - definition.right-triangle
  - definition.similar-triangles
  - theorem.similar-triangles-proportional-sides
```

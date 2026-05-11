# 07 — Ontology Tags

A *very lightweight* semantic typing layer. Optional. Used for
retrieval, clustering, navigation, and visualization — not for
inference.

## Shape

```yaml
ontology:
  semantic_kind: [criterion]
  keywords: [continuity, intermediate-value]
```

## `semantic_kind`

Categorical tag(s) describing what the entity *is* at a meta level:

| Kind            | Example                                                          |
|-----------------|------------------------------------------------------------------|
| `object`        | `definition.real-number`, `definition.metric-space`              |
| `property`      | `definition.continuity`, `definition.boundedness`                |
| `relation`      | `definition.subset`, `definition.divides`                        |
| `operator`      | `definition.composition`, `definition.derivative`                |
| `construction`  | `definition.cartesian-product`, `theorem.existence-of-reals`     |
| `criterion`     | `proposition.cauchy-criterion`, `theorem.intermediate-value`     |
| `schema`        | parameterized theorem families                                   |
| `principle`     | `axiom.choice`, `axiom.completeness`                             |

Multiple kinds are allowed (`[property, criterion]`).

## `keywords`

Free-form retrieval keywords. Lowercase, hyphen-separated. Used by the
context-pack generator's topic-based retrieval. They should reflect
the entity's *meaning*, not the words in its statement.

Example:

```yaml
ontology:
  semantic_kind: [property, criterion]
  keywords: [continuity, function, limit, metric-space]
```

## What this is NOT

- Not an inference layer.
- Not a closed vocabulary (validator does not restrict).
- Not the basis for proof discovery.

## Why so minimal

The audit warns explicitly against heavy ontology engines. The current
need is retrieval and visualization clustering. `semantic_kind` and
`keywords` cover both at near-zero schema cost. If a future need
demands richer typing, it should be argued from concrete failure
cases.

## Interaction with reports

A v0.3 report may compute, per chapter:

- distribution of `semantic_kind` (how object-heavy vs criterion-heavy
  is the chapter?);
- top keywords;
- keyword co-occurrence with `domains` and `ambient`.

These are read-only signals. Editing them in YAML is the only way to
change them.

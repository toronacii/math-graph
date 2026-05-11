# 06 — Domains and Ambient Structures

These two blocks are the lightweight context layer. They are NOT a
formal foundation; they are tags that let the graph distinguish
"continuity in R" from "continuity in a metric space" without
inventing a new ontology engine.

## `domains`

Mathematical branch tagging.

```yaml
domains:
  primary:   [real-analysis]
  secondary: [topology]
```

Suggested vocabulary (free-form, not validated):

`real-analysis`, `complex-analysis`, `topology`, `metric-spaces`,
`set-theory`, `linear-algebra`, `abstract-algebra`, `number-theory`,
`combinatorics`, `category-theory`, `mathematical-logic`, `geometry`,
`differential-geometry`, `measure-theory`, `functional-analysis`,
`probability`, `discrete-math`, `numerical-analysis`.

`primary` should contain the principal area; `secondary` may list
bridge domains (a category-theoretic statement used inside topology
might have `primary: [category-theory]`, `secondary: [topology]`).

## `ambient`

The mathematical / logical context within which the statement holds.

```yaml
ambient:
  structures: [metric-space, complete-ordered-field]
  logic: classical-first-order-logic
  foundations: ZFC
```

### `structures`

Suggested vocabulary:

`set`, `ordered-field`, `complete-ordered-field`, `field`, `ring`,
`group`, `vector-space`, `normed-vector-space`, `inner-product-space`,
`metric-space`, `topological-space`, `compact-hausdorff-space`,
`manifold`, `smooth-manifold`, `Riemannian-manifold`, `category`,
`abelian-category`, `monoidal-category`, `topos`, etc.

This is the field that resolves audit issue 5.1: "the architecture
lacks explicit ambient context."

### `logic`

Optional. Defaults are not assumed. If empty, the entity is treated as
ambient-classical for retrieval purposes. Suggested values:

`classical-first-order-logic`, `intuitionistic-logic`, `HoTT`,
`second-order-logic`, `infinitary-logic`.

### `foundations`

Optional. Suggested values:

`ZFC`, `ZF`, `NBG`, `MK`, `ETCS`, `HoTT`, `MLTT`.

## Disambiguation use case

Two `definition.continuity` nodes should be impossible — same ID, two
nodes. Instead, the graph carries:

- `definition.continuity` with `ambient: { structures: [metric-space] }`
- `definition.continuity-topological` with
  `ambient: { structures: [topological-space] }`

and a `generality` edge from the first to the second:

```yaml
# inside definition.continuity
generality:
  - target: definition.continuity-topological
    relation: special_case_of
```

The retrieval layer can then surface both when a user searches for
"continuity", with the `ambient` block as a discriminator.

## Why not enforce a vocabulary

Two reasons:

1. The graph aspires to span all of mathematics. A closed vocabulary
   either fails late (missing terms appear in the Nth chapter we
   integrate) or becomes an ontology bureaucracy.
2. The audit warns against premature ontology engineering.

A future *report* may enumerate observed values and propose
canonicalization. The schema does not block additions.

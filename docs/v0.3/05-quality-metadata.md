# 05 — Quality Metadata

The v0.2 single `confidence` field is overloaded. The audit (issue
3.3) shows that "Rudin proofs are high confidence" can mean any of:

- the extractor parsed the source correctly;
- the dependency list is complete;
- the formulation is mathematically faithful;
- the translations are reliable.

These are independent claims. v0.3 decomposes them.

## Axes

```yaml
quality:
  extraction_confidence:        high     # parser/extractor's own confidence
  dependency_confidence:        medium   # is `uses` / `depends_on` complete?
  semantic_confidence:          high     # is the formulation faithful to the source's mathematical content?
  translation_confidence:       medium   # how reliable are non-original translations?
  latex_confidence:             high     # is the LaTeX representation correct?
  source_alignment_confidence:  high     # does the entity actually match the cited source location?
```

All axes are `low | medium | high | null`. `null` means "not yet
assessed" (preferable to a default `high` that masks ignorance).

## What `null` means

`null` is a strong signal that an audit pass has not touched this axis.
Status promotion rules require certain axes to be non-null:

- `status: validated` requires nothing in particular about `quality`,
  but does require LaTeX status != `missing` and at least one source.
- `status: audited` requires `quality.semantic_confidence` to be set.
- For proofs, `status: audited` requires `quality.dependency_confidence`.

## Per-entity vs per-source

`quality` lives on the entity. When a statement merges two sources,
each source can have its own `Source.notes`, but `quality` is a single
view. If source-specific quality is needed, encode it as a note inside
`Source.notes` and lower the global axis accordingly.

## Why six axes and not three

Three would conflate (a) extraction (b) translation (c) formal
representation. The audit shows we need at least:

- Independent translation confidence (audit issue 1.3, 3.3).
- Independent dependency completeness (audit issue 1.1, 1.4).
- Independent source alignment (audit issue 2.4).

`latex_confidence` is split from `latex.review_status` because the
former is about whether the LaTeX is *mathematically correct*, while
the latter is about whether anyone has looked at it.

## Reports

Per-chapter weak-dependency reports in v0.3 must distinguish weakness
along each axis. A report stating `weak_dependencies: []` is only
valid if `dependency_confidence` is `high` for all proofs in scope —
not merely if all references resolve.

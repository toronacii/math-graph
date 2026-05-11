# 03 — LaTeX Lifecycle

## Problem

In v0.2, `statement.latex` was a free-form optional string. The audit
found 89 statements without LaTeX. There is no way to distinguish:

- "We forgot to add it."
- "It's intentionally informal — this is a definition of a concept that
  has no compact symbolic form."
- "It's present but the math reviewer flagged it."
- "It's present but the auto-extractor is uncertain about the rendering."

## v0.3 model

```yaml
statement:
  natural:
    en: { text: "...", is_original: true, ... }
  latex:
    body: |
      a^2 + b^2 = c^2
    status: present          # present | informal | needs_review | missing | not_applicable
    review_status: unreviewed
```

### Status semantics

| Status            | Meaning                                                                  |
|-------------------|--------------------------------------------------------------------------|
| `present`         | A complete LaTeX representation. Renders standalone.                     |
| `informal`        | Partial / sketch / pseudo-LaTeX. Useful but not authoritative.           |
| `needs_review`    | Present but flagged for math review (typos, ambiguity, etc.).            |
| `missing`         | Should exist; doesn't yet. Will trigger a validation warning.            |
| `not_applicable`  | Conceptual entity; no formal expression is meaningful or expected.       |

### Constraints

- `status: present` requires a non-empty `body`.
- `status: not_applicable` requires no `body`.
- For non-`definition` and non-`axiom` statements, `status: missing`
  produces a validator warning. For definitions and axioms, missing
  LaTeX is acceptable but `not_applicable` should be used when truly
  inapplicable.

### Promotion rules

A statement cannot be promoted to `status: validated` (entity status,
not LaTeX status) while its LaTeX status is `missing`. See
[`08-status-lifecycle.md`](08-status-lifecycle.md).

## Why a separate block

LaTeX has its own review cycle. A theorem's English natural text may be
approved while its LaTeX still needs a typography pass. Bundling them
loses that signal.

## Why no AST

v0.3 does not introduce a LaTeX AST or symbolic checker. The `body`
field is treated as opaque text. Future projects may build comparison
or normalization tooling on top of `body`, but the schema does not
require it.

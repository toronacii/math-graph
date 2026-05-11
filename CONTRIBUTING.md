# Contributing to MKG

Read [AGENTS.md](AGENTS.md) first. The rules below are operational; the philosophy lives there.

## Schema language

- All YAML keys MUST be in English.
- Human-readable content (titles, natural-language statements) is i18n: nest under language codes (`en`, `es`, ...).
- Preserve the original language of the source material.

## IDs

Pattern: `<type>.<normalized-name>` for statements, `proof.<statement-name>.<source-or-style>` for proofs.

- `type` ∈ `{axiom, definition, lemma, proposition, theorem, corollary, conjecture, proof}`.
- `normalized-name`: lowercase, hyphen-separated, ASCII.
- IDs MUST be globally unique across `data/`.

Examples:

```
definition.function
theorem.pythagorean-theorem
proof.pythagorean-theorem.similar-triangles
```

## Mathematical notation

Use LaTeX in `statement.latex`. Do not invent custom syntaxes.

## Dependencies

- `statement.proved_by[]` lists proof IDs that establish this statement.
- `proof.proves` is a single statement ID.
- `proof.uses[]` lists statement IDs the proof depends on.

If a dependency is uncertain, add `confidence: low` and a `notes` field.

## Workflow

1. Add or edit YAML files under `data/statements/` or `data/proofs/`.
2. Run `uv run python scripts/validate.py` — it must exit 0.
3. Run `uv run pytest`.
4. Optionally rebuild the graph: `uv run python scripts/build_graph.py`.
5. Open a PR; CI will re-run validation and publish `graph.json` as an artifact.

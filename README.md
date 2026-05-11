# Mathematical Knowledge Graph (MKG)

Structured graph of mathematical knowledge: statements (axioms, definitions, lemmas, propositions, theorems, corollaries, conjectures) connected through proofs.

The conceptual model, scope and rules are defined in [AGENTS.md](AGENTS.md). Read that first.

## Layout

```
data/
  statements/     # one YAML per statement
  proofs/         # one YAML per proof
sources/          # source-book metadata
schema/           # Pydantic models + generated JSON Schemas
scripts/          # validate.py, build_graph.py
generated/
  graph/          # graph.json (node-link)
  exports/        # graph.graphml
tests/
```

## Quick start

Install [`uv`](https://docs.astral.sh/uv/) and then:

```bash
uv sync
uv run python scripts/validate.py
uv run python scripts/build_graph.py
uv run pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for ID conventions, schema rules and i18n policy.

## License

- Code: MIT — see [LICENSE](LICENSE).
- Data under `data/` and `sources/`: CC-BY-SA 4.0 — see [LICENSE-DATA](LICENSE-DATA).

"""Export Pydantic models to JSON Schema files under schema/.

Emits both the v0.2 (legacy) and v0.3 (canonical) schemas:

- schema/statement.schema.json       v0.2
- schema/proof.schema.json           v0.2
- schema/v03.statement.schema.json   v0.3
- schema/v03.proof.schema.json       v0.3
"""

from __future__ import annotations

import json
from pathlib import Path

from schema.models import proof_json_schema, statement_json_schema
from schema.v03 import (
    proof_json_schema as v03_proof_json_schema,
)
from schema.v03 import (
    statement_json_schema as v03_statement_json_schema,
)

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"


def _write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

    # v0.2 (legacy)
    _write(SCHEMA_DIR / "statement.schema.json", statement_json_schema())
    _write(SCHEMA_DIR / "proof.schema.json", proof_json_schema())

    # v0.3 (canonical)
    _write(SCHEMA_DIR / "v03.statement.schema.json", v03_statement_json_schema())
    _write(SCHEMA_DIR / "v03.proof.schema.json", v03_proof_json_schema())

    print(
        "wrote:\n"
        "  schema/statement.schema.json (v0.2)\n"
        "  schema/proof.schema.json (v0.2)\n"
        "  schema/v03.statement.schema.json (v0.3)\n"
        "  schema/v03.proof.schema.json (v0.3)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

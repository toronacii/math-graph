"""Export Pydantic models to JSON Schema files under schema/."""

from __future__ import annotations

import json
from pathlib import Path

from schema.models import proof_json_schema, statement_json_schema

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"


def main() -> int:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    (SCHEMA_DIR / "statement.schema.json").write_text(
        json.dumps(statement_json_schema(), indent=2) + "\n", encoding="utf-8"
    )
    (SCHEMA_DIR / "proof.schema.json").write_text(
        json.dumps(proof_json_schema(), indent=2) + "\n", encoding="utf-8"
    )
    print("wrote schema/statement.schema.json and schema/proof.schema.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

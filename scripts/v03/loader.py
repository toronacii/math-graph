"""v0.3 YAML loader.

Loads v0.3 YAML entities from a configurable data root (default `data/`).
v0.3 YAML files MUST declare `schema_version` matching one of the
versions in `SUPPORTED_SCHEMA_VERSIONS` (currently `0.3.0` and `0.3.1`).
Files without that marker are ignored with a warning so v0.2 and v0.3
can transiently coexist during migration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from schema.v03 import SUPPORTED_SCHEMA_VERSIONS, Proof, Statement

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"


@dataclass
class LoadError:
    path: Path
    message: str


@dataclass
class Dataset:
    statements: dict[str, Statement] = field(default_factory=dict)
    proofs: dict[str, Proof] = field(default_factory=dict)
    statement_paths: dict[str, Path] = field(default_factory=dict)
    proof_paths: dict[str, Path] = field(default_factory=dict)
    errors: list[LoadError] = field(default_factory=list)
    skipped_legacy: list[Path] = field(default_factory=list)


def _iter_yaml(directory: Path) -> Iterable[Path]:
    if not directory.exists():
        return []
    return sorted(p for p in directory.rglob("*.yml"))


def _load_yaml(path: Path) -> dict | None:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ValueError(f"top-level YAML in {path} must be a mapping")
    return data


def load_dataset(data_dir: Path = DATA_DIR) -> Dataset:
    """Load all v0.3 YAML entities under `data_dir`.

    A file is considered v0.3 iff it declares a `schema_version` in
    `SUPPORTED_SCHEMA_VERSIONS`.
    """
    ds = Dataset()

    for path in _iter_yaml(data_dir / "statements"):
        try:
            raw = _load_yaml(path)
            if raw is None:
                continue
            if raw.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
                ds.skipped_legacy.append(path)
                continue
            stmt = Statement.model_validate(raw)
        except (ValidationError, ValueError, yaml.YAMLError) as exc:
            ds.errors.append(LoadError(path, str(exc)))
            continue
        if stmt.id in ds.statement_paths or stmt.id in ds.proof_paths:
            ds.errors.append(LoadError(path, f"duplicate id {stmt.id!r}"))
            continue
        ds.statements[stmt.id] = stmt
        ds.statement_paths[stmt.id] = path

    for path in _iter_yaml(data_dir / "proofs"):
        try:
            raw = _load_yaml(path)
            if raw is None:
                continue
            if raw.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
                ds.skipped_legacy.append(path)
                continue
            proof = Proof.model_validate(raw)
        except (ValidationError, ValueError, yaml.YAMLError) as exc:
            ds.errors.append(LoadError(path, str(exc)))
            continue
        if proof.id in ds.proof_paths or proof.id in ds.statement_paths:
            ds.errors.append(LoadError(path, f"duplicate id {proof.id!r}"))
            continue
        ds.proofs[proof.id] = proof
        ds.proof_paths[proof.id] = path

    return ds

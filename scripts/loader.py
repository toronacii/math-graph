"""Shared loading utilities for MKG YAML data."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from schema.models import Proof, Statement

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
STATEMENTS_DIR = DATA_DIR / "statements"
PROOFS_DIR = DATA_DIR / "proofs"


@dataclass
class LoadError:
    path: Path
    message: str


@dataclass
class Dataset:
    statements: dict[str, Statement]
    proofs: dict[str, Proof]
    statement_paths: dict[str, Path]
    proof_paths: dict[str, Path]
    errors: list[LoadError]


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
    statements: dict[str, Statement] = {}
    statement_paths: dict[str, Path] = {}
    proofs: dict[str, Proof] = {}
    proof_paths: dict[str, Path] = {}
    errors: list[LoadError] = []

    statements_dir = data_dir / "statements"
    proofs_dir = data_dir / "proofs"

    for path in _iter_yaml(statements_dir):
        try:
            raw = _load_yaml(path)
            if raw is None:
                continue
            stmt = Statement.model_validate(raw)
        except (ValidationError, ValueError, yaml.YAMLError) as exc:
            errors.append(LoadError(path, str(exc)))
            continue
        if stmt.id in statement_paths or stmt.id in proof_paths:
            errors.append(LoadError(path, f"duplicate id {stmt.id!r}"))
            continue
        statements[stmt.id] = stmt
        statement_paths[stmt.id] = path

    for path in _iter_yaml(proofs_dir):
        try:
            raw = _load_yaml(path)
            if raw is None:
                continue
            proof = Proof.model_validate(raw)
        except (ValidationError, ValueError, yaml.YAMLError) as exc:
            errors.append(LoadError(path, str(exc)))
            continue
        if proof.id in proof_paths or proof.id in statement_paths:
            errors.append(LoadError(path, f"duplicate id {proof.id!r}"))
            continue
        proofs[proof.id] = proof
        proof_paths[proof.id] = path

    return Dataset(statements, proofs, statement_paths, proof_paths, errors)

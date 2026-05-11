"""v0.3 validator.

Layered checks (each layer must pass for promotion to the next status):

  L1 schema:                Pydantic model validation (structural).
  L2 references:            All referenced IDs exist.
  L3 symmetry:              proved_by <-> proves consistency.
  L4 acyclicity:            statement -> proof -> statement DAG.
  L5 lifecycle:             status transitions consistent with metadata.
  L6 completeness warnings: non-fatal warnings for likely under-specification.

Errors fail the validator. Warnings are reported but exit code remains 0.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx

from schema.v03 import known_source_works
from scripts.v03.loader import DATA_DIR, Dataset, load_dataset


@dataclass
class Issues:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---- L2 references ---------------------------------------------------------


def _check_references(ds: Dataset, issues: Issues) -> None:
    statement_ids = set(ds.statements)
    proof_ids = set(ds.proofs)

    for sid, stmt in ds.statements.items():
        for ref in stmt.proved_by:
            if ref not in proof_ids:
                issues.errors.append(f"{sid}: proved_by references unknown proof {ref!r}")
        for dep in stmt.depends_on:
            if dep.id not in statement_ids:
                issues.errors.append(
                    f"{sid}: depends_on references unknown statement {dep.id!r}"
                )
        for gen in stmt.generality:
            if gen.target not in statement_ids:
                issues.errors.append(
                    f"{sid}: generality.target references unknown statement {gen.target!r}"
                )

    for pid, proof in ds.proofs.items():
        if proof.proves not in statement_ids:
            issues.errors.append(
                f"{pid}: proves references unknown statement {proof.proves!r}"
            )
        for dep in proof.uses:
            if dep.id not in statement_ids:
                issues.errors.append(
                    f"{pid}: uses references unknown statement {dep.id!r}"
                )
        for part in proof.parts:
            for dep in part.uses:
                if dep.id not in statement_ids:
                    issues.errors.append(
                        f"{pid}/{part.name}: uses references unknown statement {dep.id!r}"
                    )


# ---- L3 symmetry -----------------------------------------------------------


def _check_symmetry(ds: Dataset, issues: Issues) -> None:
    for pid, proof in ds.proofs.items():
        target = ds.statements.get(proof.proves)
        if target is None:
            continue
        if pid not in target.proved_by:
            issues.errors.append(
                f"{pid}: proves {proof.proves!r} but that statement omits it from proved_by"
            )
    for sid, stmt in ds.statements.items():
        for ref in stmt.proved_by:
            proof = ds.proofs.get(ref)
            if proof is None:
                continue
            if proof.proves != sid:
                issues.errors.append(
                    f"{sid}: proved_by lists {ref!r} but that proof proves {proof.proves!r}"
                )


# ---- L4 acyclicity ---------------------------------------------------------


def _check_acyclic(ds: Dataset, issues: Issues) -> None:
    g: nx.DiGraph = nx.DiGraph()
    for sid in ds.statements:
        g.add_node(sid, kind="statement")
    for pid, proof in ds.proofs.items():
        g.add_node(pid, kind="proof")
        for dep in proof.uses:
            g.add_edge(dep.id, pid)
        if proof.proves in ds.statements:
            g.add_edge(pid, proof.proves)

    try:
        cycle = nx.find_cycle(g, orientation="original")
    except nx.NetworkXNoCycle:
        return
    chain = " -> ".join(e[0] for e in cycle) + " -> " + cycle[-1][1]
    issues.errors.append(f"cyclic dependency detected: {chain}")


# ---- L5 lifecycle ----------------------------------------------------------

# Status promotion guards. A status MAY be set at extraction time but stricter
# statuses require the matching quality / metadata to be present.
STATUS_RANK = {
    "extracted": 0,
    "reviewed": 1,
    "validated": 2,
    "audited": 3,
    "stable": 4,
    "canonical": 5,
}


def _rank(status: str) -> int:
    return STATUS_RANK.get(status, -1)


def _check_lifecycle(ds: Dataset, issues: Issues) -> None:
    for sid, stmt in ds.statements.items():
        r = _rank(stmt.status)
        if r >= STATUS_RANK["validated"]:
            if not stmt.sources:
                issues.errors.append(
                    f"{sid}: status>={stmt.status} requires at least one source"
                )
            if stmt.statement.latex.status == "missing":
                issues.errors.append(
                    f"{sid}: status>={stmt.status} requires latex.status != 'missing'"
                )
        if r >= STATUS_RANK["audited"]:
            if not stmt.quality.semantic_confidence:
                issues.errors.append(
                    f"{sid}: status>={stmt.status} requires quality.semantic_confidence"
                )

    for pid, proof in ds.proofs.items():
        r = _rank(proof.status)
        if r >= STATUS_RANK["validated"] and not proof.uses and not proof.parts:
            # axioms/definitions don't have proofs; a proof with zero deps is suspicious
            target = ds.statements.get(proof.proves)
            if target and target.type not in ("axiom", "definition"):
                issues.warnings.append(
                    f"{pid}: validated proof has empty `uses` (target type={target.type})"
                )
        if r >= STATUS_RANK["audited"] and not proof.quality.dependency_confidence:
            issues.errors.append(
                f"{pid}: status>={proof.status} requires quality.dependency_confidence"
            )


# ---- L6 completeness warnings ---------------------------------------------


def _check_warnings(ds: Dataset, issues: Issues) -> None:
    registered_works = known_source_works()

    for sid, stmt in ds.statements.items():
        if stmt.type not in ("definition", "axiom") and stmt.statement.latex.status == "missing":
            issues.warnings.append(f"{sid}: latex.status=missing for non-definition")
        rerun = bool(stmt.provenance and stmt.provenance.rerun_id)
        for src in stmt.sources:
            if registered_works and src.work not in registered_works:
                issues.warnings.append(
                    f"{sid}: source {src.work!r} not in canonical registry "
                    f"(schema/v03/sources.yml)"
                )
            if not src.page and not src.theorem_label and not src.locator:
                msg = (
                    f"{sid}: source {src.work!r} lacks page/theorem_label/locator"
                )
                if rerun:
                    issues.errors.append(msg + " (required when provenance.rerun_id is set)")
                else:
                    issues.warnings.append(msg)

    for pid, proof in ds.proofs.items():
        if not proof.uses and not proof.parts:
            target = ds.statements.get(proof.proves)
            if target and target.type not in ("axiom", "definition"):
                issues.warnings.append(
                    f"{pid}: proof has no dependencies (target type={target.type})"
                )
        rerun = bool(proof.provenance and proof.provenance.rerun_id)
        for src in proof.sources:
            if registered_works and src.work not in registered_works:
                issues.warnings.append(
                    f"{pid}: source {src.work!r} not in canonical registry "
                    f"(schema/v03/sources.yml)"
                )
            if not src.page and not src.theorem_label and not src.locator:
                msg = (
                    f"{pid}: source {src.work!r} lacks page/theorem_label/locator"
                )
                if rerun:
                    issues.errors.append(msg + " (required when provenance.rerun_id is set)")
                else:
                    issues.warnings.append(msg)


# ---- public API ------------------------------------------------------------


def validate(data_dir: Path = DATA_DIR) -> Issues:
    ds = load_dataset(data_dir)
    issues = Issues()
    issues.errors.extend(f"{e.path}: {e.message}" for e in ds.errors)
    if not issues.errors:
        _check_references(ds, issues)
    if not issues.errors:
        _check_symmetry(ds, issues)
        _check_acyclic(ds, issues)
        _check_lifecycle(ds, issues)
        _check_warnings(ds, issues)
    return issues


def main() -> int:
    issues = validate()
    if issues.warnings:
        print(f"WARN — {len(issues.warnings)} warning(s):", file=sys.stderr)
        for w in issues.warnings:
            print(f"  ! {w}", file=sys.stderr)
    if issues.errors:
        print(f"FAIL — {len(issues.errors)} error(s):", file=sys.stderr)
        for e in issues.errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK — all v0.3 entities valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

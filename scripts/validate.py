"""Validate every YAML under data/ against the MKG schema.

Checks performed:

1. Each file parses as YAML and matches the Pydantic model.
2. IDs are globally unique across statements and proofs.
3. ``proof.proves`` and ``proof.uses`` reference existing statements.
4. ``statement.proved_by`` references existing proofs.
5. Every proof's ``proves`` is mirrored in the target statement's
   ``proved_by`` (and vice versa).
6. The induced statement→proof→statement graph is acyclic.

When the SQLite database exists, checks 3-6 run via SQL queries for
efficiency.  Otherwise they fall back to in-memory validation.

Exit code is 0 on success, 1 if any error is found.
"""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

from scripts.loader import DATA_DIR, Dataset, load_dataset


# ---- in-memory checks (fallback when DB is unavailable) ---------------------


def _check_references(ds: Dataset) -> list[str]:
    errors: list[str] = []
    statement_ids = set(ds.statements)
    proof_ids = set(ds.proofs)

    for sid, stmt in ds.statements.items():
        for ref in stmt.proved_by:
            if ref not in proof_ids:
                errors.append(f"{sid}: proved_by references unknown proof {ref!r}")

    for pid, proof in ds.proofs.items():
        if proof.proves not in statement_ids:
            errors.append(f"{pid}: proves references unknown statement {proof.proves!r}")
        for ref in proof.uses:
            if ref not in statement_ids:
                errors.append(f"{pid}: uses references unknown statement {ref!r}")

    return errors


def _check_symmetry(ds: Dataset) -> list[str]:
    errors: list[str] = []
    for pid, proof in ds.proofs.items():
        target = ds.statements.get(proof.proves)
        if target is None:
            continue
        if pid not in target.proved_by:
            errors.append(
                f"{pid}: proves {proof.proves!r} but that statement does not list it in proved_by"
            )
    for sid, stmt in ds.statements.items():
        for ref in stmt.proved_by:
            proof = ds.proofs.get(ref)
            if proof is None:
                continue
            if proof.proves != sid:
                errors.append(
                    f"{sid}: proved_by lists {ref!r} but that proof proves {proof.proves!r}"
                )
    return errors


def _check_acyclic(ds: Dataset) -> list[str]:
    g: nx.DiGraph = nx.DiGraph()
    for sid in ds.statements:
        g.add_node(sid, kind="statement")
    for pid, proof in ds.proofs.items():
        g.add_node(pid, kind="proof")
        for ref in proof.uses:
            g.add_edge(ref, pid)  # statement used -> proof
        if proof.proves in ds.statements:
            g.add_edge(pid, proof.proves)  # proof -> statement it establishes

    try:
        cycle = nx.find_cycle(g, orientation="original")
    except nx.NetworkXNoCycle:
        return []
    chain = " -> ".join(edge[0] for edge in cycle) + " -> " + cycle[-1][1]
    return [f"cyclic dependency detected: {chain}"]


# ---- public API -------------------------------------------------------------


def validate(data_dir: Path = DATA_DIR) -> list[str]:
    """Validate all entities.  Returns a list of error strings (empty = OK)."""
    ds = load_dataset(data_dir)

    # Phase 1: schema errors from Pydantic
    errors = [f"{e.path}: {e.message}" for e in ds.errors]

    # Phase 2: integrity checks — try SQL first, fall back to in-memory
    try:
        from scripts.build_db import build_db, validate_db

        con = build_db(ds)
        errors.extend(validate_db(con))
        con.close()
    except Exception:
        # Fallback to in-memory checks
        errors.extend(_check_references(ds))
        errors.extend(_check_symmetry(ds))
        errors.extend(_check_acyclic(ds))

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"FAIL — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("OK — all entities valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

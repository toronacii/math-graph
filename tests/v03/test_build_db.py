"""Tests for the v0.3 SQLite builder.

Locks in:
  - CHECK constraints derived from schema/v03 enums actually fire on
    out-of-enum inserts (defense-in-depth around external writers).
  - The audit-oriented indexes added in v0.3.1 (proof_uses role + rerun_id)
    are present so the documented query patterns keep their O(log n).
"""

from __future__ import annotations

import sqlite3
from typing import get_args

import pytest

from schema.v03 import (
    ConceptDependencyRole,
    DependencyRole,
    GeneralityRelation,
    SemanticKind,
)
from scripts.v03.build_db import SCHEMA_SQL


@pytest.fixture()
def con() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA_SQL)
    yield c
    c.close()


def _index_names(con: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in con.execute("SELECT name FROM sqlite_master WHERE type='index'")
    }


def test_audit_indexes_present(con: sqlite3.Connection) -> None:
    idx = _index_names(con)
    # v0.3.1 audit-oriented indexes — see build_db.py SCHEMA_SQL footer.
    assert "idx_proof_uses_role" in idx
    assert "idx_stmt_rerun" in idx
    assert "idx_proof_rerun" in idx


def test_query_planner_uses_role_index(con: sqlite3.Connection) -> None:
    plan = con.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM proof_uses WHERE statement_id=? AND role=?",
        ("definition.x", "essential"),
    ).fetchall()
    assert any("idx_proof_uses_role" in row[3] for row in plan), plan


def test_query_planner_uses_rerun_index(con: sqlite3.Connection) -> None:
    plan = con.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM statement_provenance WHERE rerun_id=?",
        ("v0.3-pilot",),
    ).fetchall()
    assert any("idx_stmt_rerun" in row[3] for row in plan), plan


def test_check_proof_uses_role_rejects_unknown(con: sqlite3.Connection) -> None:
    # Need a parent proof+statement first; bypass FK enforcement (off by default).
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    con.execute(
        "INSERT INTO proofs VALUES "
        "('proof.foo.bar','definition.x','extracted','0.3.1',NULL,NULL)"
    )
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        con.execute(
            "INSERT INTO proof_uses VALUES "
            "('proof.foo.bar','definition.x','BOGUS','high',0,'',NULL)"
        )


def test_check_proof_uses_role_accepts_all_enum_values(con: sqlite3.Connection) -> None:
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    con.execute(
        "INSERT INTO proofs VALUES "
        "('proof.foo.bar','definition.x','extracted','0.3.1',NULL,NULL)"
    )
    for role in get_args(DependencyRole):
        con.execute(
            "INSERT INTO proof_uses VALUES (?,?,?,?,?,?,?)",
            ("proof.foo.bar", "definition.x", role, "high", 0, role, None),
        )


def test_check_generality_relation_rejects_unknown(con: sqlite3.Connection) -> None:
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        con.execute(
            "INSERT INTO statement_generality VALUES "
            "('definition.x','definition.y','BOGUS')"
        )


def test_check_generality_relation_accepts_all_enum_values(
    con: sqlite3.Connection,
) -> None:
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    for rel in get_args(GeneralityRelation):
        con.execute(
            "INSERT INTO statement_generality VALUES (?,?,?)",
            ("definition.x", f"definition.target-{rel}", rel),
        )


def test_check_depends_on_role_rejects_unknown(con: sqlite3.Connection) -> None:
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        con.execute(
            "INSERT INTO statement_depends_on VALUES "
            "('definition.x','definition.y','BOGUS','high',NULL)"
        )
    # all canonical roles must be accepted
    for role in get_args(ConceptDependencyRole):
        con.execute(
            "INSERT INTO statement_depends_on VALUES (?,?,?,?,?)",
            ("definition.x", f"definition.target-{role}", role, "high", None),
        )


def test_check_semantic_kind_allows_sentinel_empty(con: sqlite3.Connection) -> None:
    """Ontology rows use '' as a sentinel for keyword-only entries."""
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    # keyword-only row (sentinel '' for semantic_kind)
    con.execute(
        "INSERT INTO statement_ontology VALUES ('definition.x','','some-keyword')"
    )
    # all canonical semantic_kind values accepted
    for k in get_args(SemanticKind):
        con.execute(
            "INSERT INTO statement_ontology VALUES (?,?,?)",
            ("definition.x", k, ""),
        )
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        con.execute(
            "INSERT INTO statement_ontology VALUES ('definition.x','bogus_kind','')"
        )


def test_check_provenance_schema_version_locked(con: sqlite3.Connection) -> None:
    con.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',NULL,"
        "'not_applicable','unreviewed',NULL)"
    )
    with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
        con.execute(
            "INSERT INTO statement_provenance VALUES "
            "('definition.x','9.9.9',NULL,NULL,NULL,NULL)"
        )

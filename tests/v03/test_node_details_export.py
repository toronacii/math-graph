"""Tests for the v0.3 graph & node-details exports.

These lock the contract consumed by the frontend graph explorer
(visualization/web). The Python side promises:

  - graph.json node payloads include summary fields (primary_domain,
    semantic_kinds, latex_status, quality_overall) so filters work
    without a join into node-details.
  - node-details.json carries the rich per-node data (latex, domains,
    ambient, ontology, quality, sources, provenance, proved_by,
    depends_on, generality, parts) when the underlying YAML provides it.
  - Fields are omitted when empty (no empty dicts/lists in the export).
"""

from __future__ import annotations

import sqlite3

import pytest

from scripts.v03.build_db import (
    SCHEMA_SQL,
    _build_graph,
    _node_details,
    _worst_confidence,
)


def _seed(con: sqlite3.Connection) -> None:
    """Minimal but realistic fixture: one statement (with full metadata)
    and one proof that uses it. Mirrors the shape produced by the loader,
    bypassing FK enforcement (off by default in sqlite3).
    """
    cur = con.cursor()
    cur.execute(
        "INSERT INTO statements VALUES "
        "('definition.x','definition','extracted','0.3.1','en',"
        "'X = \\\\{0\\\\}','present','unreviewed','seed note')"
    )
    cur.execute(
        "INSERT INTO statement_titles VALUES "
        "('definition.x','en','X','original','original','approved')"
    )
    cur.execute(
        "INSERT INTO statement_natural VALUES "
        "('definition.x','en','X is the singleton zero.',1,"
        "'original','approved')"
    )
    cur.execute(
        "INSERT INTO statement_quality VALUES "
        "('definition.x','high','medium','high','high','high','low')"
    )
    cur.execute(
        "INSERT INTO statement_provenance VALUES "
        "('definition.x','0.3.1','rerun-test','llm:test','2026-05-11',NULL)"
    )
    cur.execute(
        "INSERT INTO statement_domains VALUES ('definition.x','primary','algebra')"
    )
    cur.execute(
        "INSERT INTO statement_domains VALUES "
        "('definition.x','secondary','set-theory')"
    )
    cur.execute(
        "INSERT INTO statement_ambient VALUES ('definition.x','set')"
    )
    cur.execute(
        "INSERT INTO statement_ontology VALUES ('definition.x','object','')"
    )
    cur.execute(
        "INSERT INTO statement_ontology VALUES ('definition.x','','singleton')"
    )
    cur.execute(
        "INSERT INTO statement_proved_by VALUES "
        "('definition.x','proof.foo.bar')"
    )
    cur.execute(
        "INSERT INTO statement_depends_on VALUES "
        "('definition.x','definition.y','uses_concept','high','because reasons')"
    )
    cur.execute(
        "INSERT INTO statement_generality VALUES "
        "('definition.x','definition.y','stronger_than')"
    )
    cur.execute(
        "INSERT INTO sources VALUES "
        "('definition.x','statement','Test Work','Author','1','2024',"
        "'1','1.1','Theorem 1','42','loc','http://x',NULL)"
    )

    cur.execute(
        "INSERT INTO statements VALUES "
        "('definition.y','definition','extracted','0.3.1','en',"
        "NULL,'not_applicable','unreviewed',NULL)"
    )

    cur.execute(
        "INSERT INTO proofs VALUES "
        "('proof.foo.bar','definition.x','extracted','0.3.1','direct',"
        "'a proof note')"
    )
    cur.execute(
        "INSERT INTO proof_uses VALUES "
        "('proof.foo.bar','definition.y','essential','high',0,'','crit')"
    )
    cur.execute(
        "INSERT INTO proof_parts VALUES "
        "('proof.foo.bar','forward','direction','show =>')"
    )
    cur.execute(
        "INSERT INTO proof_quality VALUES "
        "('proof.foo.bar','high','high','high',NULL,NULL,'medium')"
    )
    cur.execute(
        "INSERT INTO proof_provenance VALUES "
        "('proof.foo.bar','0.3.1','rerun-test','llm:test','2026-05-11',NULL)"
    )
    cur.execute(
        "INSERT INTO sources VALUES "
        "('proof.foo.bar','proof','Test Work',NULL,NULL,NULL,'1','1.1',NULL,"
        "'43',NULL,NULL,'en')"
    )
    con.commit()


@pytest.fixture()
def con() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA_SQL)
    _seed(c)
    yield c
    c.close()


# ---- node-details ---------------------------------------------------------


def test_node_details_statement_carries_full_metadata(con: sqlite3.Connection) -> None:
    out = _node_details(con)
    s = out["definition.x"]

    assert s["kind"] == "statement"
    assert s["type"] == "definition"
    assert s["status"] == "extracted"
    assert s["original_language"] == "en"
    assert s["notes"] == "seed note"

    # i18n
    assert s["title"]["en"]["text"] == "X"
    assert s["title"]["en"]["is_original"] is True
    assert s["natural"]["en"]["text"] == "X is the singleton zero."

    # latex
    assert s["latex"] == {
        "body": "X = \\\\{0\\\\}",
        "status": "present",
        "review_status": "unreviewed",
    }

    # domains / ambient / ontology
    assert s["domains"] == {"primary": ["algebra"], "secondary": ["set-theory"]}
    assert s["ambient_structures"] == ["set"]
    assert s["ontology"] == {
        "semantic_kind": ["object"],
        "keywords": ["singleton"],
    }

    # quality (latex_conf maps to "latex"; source_align to "source_alignment")
    assert s["quality"] == {
        "extraction": "high", "dependency": "medium", "semantic": "high",
        "translation": "high", "latex": "high", "source_alignment": "low",
    }

    # provenance
    assert s["provenance"] == {
        "schema_version": "0.3.1",
        "rerun_id": "rerun-test",
        "extracted_by": "llm:test",
        "extracted_at": "2026-05-11",
    }
    # redirected_to was NULL → omitted
    assert "redirected_to" not in s["provenance"]

    # graph sidebars
    assert s["proved_by"] == ["proof.foo.bar"]
    assert s["depends_on"] == [{
        "id": "definition.y", "role": "uses_concept",
        "confidence": "high", "notes": "because reasons",
    }]
    assert s["generality"] == [
        {"target": "definition.y", "relation": "stronger_than"}
    ]

    # sources
    assert len(s["sources"]) == 1
    src = s["sources"][0]
    assert src["work"] == "Test Work"
    assert src["theorem_label"] == "Theorem 1"
    assert src["page"] == "42"
    assert src["url"] == "http://x"
    # source_language was NULL → omitted
    assert "source_language" not in src


def test_node_details_proof_carries_full_metadata(con: sqlite3.Connection) -> None:
    out = _node_details(con)
    p = out["proof.foo.bar"]

    assert p["kind"] == "proof"
    assert p["type"] == "proof"
    assert p["proves"] == "definition.x"
    assert p["style"] == "direct"
    assert p["notes"] == "a proof note"

    # uses include implicit/locality/notes (notes when present)
    assert p["uses"] == [{
        "id": "definition.y", "role": "essential", "confidence": "high",
        "implicit": False, "notes": "crit",
    }]

    assert p["parts"] == [{
        "name": "forward", "kind": "direction", "description": "show =>",
    }]

    # quality drops None axes
    assert p["quality"] == {
        "extraction": "high", "dependency": "high", "semantic": "high",
        "source_alignment": "medium",
    }

    assert p["provenance"]["rerun_id"] == "rerun-test"
    assert p["sources"][0]["page"] == "43"
    assert p["sources"][0]["source_language"] == "en"


def test_node_details_omits_empty_fields(con: sqlite3.Connection) -> None:
    """definition.y has no titles/natural/quality/sources etc. — these
    fields must be absent from its entry rather than emitted as empty
    structures.
    """
    out = _node_details(con)
    y = out["definition.y"]
    assert y["kind"] == "statement"
    for absent in ("title", "natural", "latex", "domains", "ambient_structures",
                   "ontology", "quality", "provenance", "proved_by",
                   "depends_on", "generality", "sources", "derived_from",
                   "notes"):
        assert absent not in y, f"unexpected empty field: {absent}"


# ---- graph node payload ---------------------------------------------------


def test_graph_node_carries_summary_fields(con: sqlite3.Connection) -> None:
    g = _build_graph(con)
    attrs = g.nodes["definition.x"]
    assert attrs["kind"] == "statement"
    assert attrs["type"] == "definition"
    assert attrs["status"] == "extracted"
    assert attrs["primary_domain"] == "algebra"
    assert attrs["semantic_kinds"] == ["object"]
    assert attrs["latex_status"] == "present"
    # worst-axis wins → low (source_alignment)
    assert attrs["quality_overall"] == "low"


def test_graph_node_omits_summaries_when_absent(con: sqlite3.Connection) -> None:
    g = _build_graph(con)
    # definition.y has no domains/ontology/quality
    attrs = g.nodes["definition.y"]
    assert "primary_domain" not in attrs
    assert "semantic_kinds" not in attrs
    assert "quality_overall" not in attrs
    # latex_status is always present on a statement (NOT NULL column)
    assert attrs["latex_status"] == "not_applicable"


def test_graph_proof_node_carries_quality_overall(con: sqlite3.Connection) -> None:
    g = _build_graph(con)
    attrs = g.nodes["proof.foo.bar"]
    assert attrs["kind"] == "proof"
    assert attrs["style"] == "direct"
    # min(high, high, high, medium) → medium
    assert attrs["quality_overall"] == "medium"


# ---- worst-confidence helper ---------------------------------------------


def test_worst_confidence_picks_lowest_axis() -> None:
    assert _worst_confidence(["high", "medium", "low"]) == "low"
    assert _worst_confidence(["high", None, "medium"]) == "medium"
    assert _worst_confidence([None, None]) is None
    assert _worst_confidence([]) is None
    # unknown values rank below anything → would win, but real data is enum-checked
    assert _worst_confidence(["high"]) == "high"

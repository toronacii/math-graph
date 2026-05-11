"""v0.3 SQLite builder + graph exports.

Schema is wider than v0.2: edges carry role/confidence/locality, sources
carry theorem_label, statements record domains/ambient/ontology/quality.

Outputs (under generated/v0.3/):
  - math_graph.db        SQLite index
  - graph.json           node-link JSON for visualization
  - node-details.json    per-node detail blob
  - graph.graphml        GraphML export
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable, get_args

import networkx as nx

from schema.v03 import (
    SUPPORTED_SCHEMA_VERSIONS,
    ConceptDependencyRole,
    Confidence,
    DependencyRole,
    GeneralityRelation,
    LatexStatus,
    ReviewStatus,
    SemanticKind,
    StatementType,
    Status,
    TranslationOrigin,
)
from scripts.v03.loader import REPO_ROOT, Dataset, load_dataset

OUT_DIR = REPO_ROOT / "generated" / "v0.3"
DB_PATH = OUT_DIR / "math_graph.db"
GRAPH_DIR = OUT_DIR
EXPORT_DIR = OUT_DIR

# ---------------------------------------------------------------------------
# Enum CHECK clause helpers.
#
# These derive SQL CHECK clauses from the canonical Pydantic enums in
# schema/v03.py so the SQLite layer enforces the same value sets as the
# loader. The DB is rebuilt on every `mkg-build`, so adding/changing enum
# values in v03.py automatically flows through; no migration needed.
# ---------------------------------------------------------------------------


def _check_in(
    column: str,
    values: Iterable[str],
    *,
    allow_null: bool = False,
    extra_allowed: Iterable[str] = (),
) -> str:
    """Build a `CHECK (column IN (...))` clause."""
    members = sorted({*values, *extra_allowed})
    quoted = ", ".join(f"'{v}'" for v in members)
    clause = f"{column} IN ({quoted})"
    if allow_null:
        clause = f"({column} IS NULL OR {clause})"
    return f"CHECK ({clause})"


# Canonical enum value tuples derived from schema/v03.py.
_STATEMENT_TYPES = get_args(StatementType)
_STATUS = get_args(Status)
_CONFIDENCE = get_args(Confidence)
_LATEX_STATUS = get_args(LatexStatus)
_REVIEW_STATUS = get_args(ReviewStatus)
_TRANSLATION_ORIGIN = get_args(TranslationOrigin)
_DEP_ROLE = get_args(DependencyRole)
_CONCEPT_ROLE = get_args(ConceptDependencyRole)
_GENERALITY = get_args(GeneralityRelation)
_SEMANTIC_KIND = get_args(SemanticKind)
_PART_KIND = ("direction", "case", "subclaim", "construction", "reduction")

# Pre-built CHECK clauses (kept as strings so SCHEMA_SQL stays a single literal).
_CK_STMT_TYPE   = _check_in("type",   _STATEMENT_TYPES)
_CK_STATUS      = _check_in("status", _STATUS)
_CK_LATEX_ST    = _check_in("latex_status", _LATEX_STATUS)
_CK_LATEX_REV   = _check_in("latex_review", _REVIEW_STATUS)
_CK_TITLE_ORG   = _check_in("origin",        _TRANSLATION_ORIGIN)
_CK_TITLE_REV   = _check_in("review_status", _REVIEW_STATUS)
_CK_CONF_EXTR   = _check_in("extraction",   _CONFIDENCE, allow_null=True)
_CK_CONF_DEP    = _check_in("dependency",   _CONFIDENCE, allow_null=True)
_CK_CONF_SEM    = _check_in("semantic",     _CONFIDENCE, allow_null=True)
_CK_CONF_TRANS  = _check_in("translation",  _CONFIDENCE, allow_null=True)
_CK_CONF_LATEX  = _check_in("latex_conf",   _CONFIDENCE, allow_null=True)
_CK_CONF_SRC    = _check_in("source_align", _CONFIDENCE, allow_null=True)
_CK_PROV_VER    = _check_in("schema_version", SUPPORTED_SCHEMA_VERSIONS)
_CK_DOMAIN_KIND = _check_in("kind", ("primary", "secondary"))
# semantic_kind row uses '' as a sentinel meaning "this row carries a keyword only"
_CK_SEM_KIND    = _check_in("semantic_kind", _SEMANTIC_KIND, extra_allowed=("",))
_CK_DEP_ROLE    = _check_in("role", _CONCEPT_ROLE)
_CK_DEP_CONF    = _check_in("confidence", _CONFIDENCE, allow_null=True)
_CK_GEN_REL     = _check_in("relation", _GENERALITY)
_CK_PROOF_USE_ROLE = _check_in("role",       _DEP_ROLE)
_CK_PROOF_USE_CONF = _check_in("confidence", _CONFIDENCE)
_CK_PART_KIND      = _check_in("kind", _PART_KIND)
_CK_SRC_KIND       = _check_in("entity_kind", ("statement", "proof"))


SCHEMA_SQL = f"""
CREATE TABLE statements (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    status          TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    original_lang   TEXT NOT NULL,
    latex_body      TEXT,
    latex_status    TEXT NOT NULL,
    latex_review    TEXT NOT NULL,
    notes           TEXT,
    {_CK_STMT_TYPE},
    {_CK_STATUS},
    {_check_in("schema_version", SUPPORTED_SCHEMA_VERSIONS)},
    {_CK_LATEX_ST},
    {_CK_LATEX_REV}
);

CREATE TABLE statement_titles (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    lang           TEXT NOT NULL,
    text           TEXT NOT NULL,
    is_original    INTEGER NOT NULL,
    origin         TEXT NOT NULL,
    review_status  TEXT NOT NULL,
    PRIMARY KEY (statement_id, lang),
    {_CK_TITLE_ORG},
    {_CK_TITLE_REV}
);

CREATE TABLE statement_natural (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    lang           TEXT NOT NULL,
    text           TEXT NOT NULL,
    is_original    INTEGER NOT NULL,
    origin         TEXT NOT NULL,
    review_status  TEXT NOT NULL,
    PRIMARY KEY (statement_id, lang),
    {_CK_TITLE_ORG},
    {_CK_TITLE_REV}
);

CREATE TABLE statement_quality (
    statement_id   TEXT PRIMARY KEY REFERENCES statements(id),
    extraction     TEXT,
    dependency     TEXT,
    semantic       TEXT,
    translation    TEXT,
    latex_conf     TEXT,
    source_align   TEXT,
    {_CK_CONF_EXTR},
    {_CK_CONF_DEP},
    {_CK_CONF_SEM},
    {_CK_CONF_TRANS},
    {_CK_CONF_LATEX},
    {_CK_CONF_SRC}
);

CREATE TABLE statement_provenance (
    statement_id   TEXT PRIMARY KEY REFERENCES statements(id),
    schema_version TEXT NOT NULL,
    rerun_id       TEXT,
    extracted_by   TEXT,
    extracted_at   TEXT,
    redirected_to  TEXT,
    {_CK_PROV_VER}
);

CREATE TABLE statement_derived_from (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    prior_id       TEXT NOT NULL,
    PRIMARY KEY (statement_id, prior_id)
);

CREATE TABLE statement_domains (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    kind           TEXT NOT NULL,   -- 'primary' | 'secondary'
    name           TEXT NOT NULL,
    PRIMARY KEY (statement_id, kind, name),
    {_CK_DOMAIN_KIND}
);

CREATE TABLE statement_ambient (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    structure      TEXT NOT NULL,
    PRIMARY KEY (statement_id, structure)
);

CREATE TABLE statement_ontology (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    semantic_kind  TEXT,
    keyword        TEXT,
    PRIMARY KEY (statement_id, semantic_kind, keyword),
    {_CK_SEM_KIND}
);

CREATE TABLE statement_proved_by (
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    proof_id      TEXT NOT NULL,
    PRIMARY KEY (statement_id, proof_id)
);

CREATE TABLE statement_depends_on (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    target_id      TEXT NOT NULL,
    role           TEXT NOT NULL,
    confidence     TEXT,
    notes          TEXT,
    PRIMARY KEY (statement_id, target_id, role),
    {_CK_DEP_ROLE},
    {_CK_DEP_CONF}
);

CREATE TABLE statement_generality (
    statement_id   TEXT NOT NULL REFERENCES statements(id),
    target_id      TEXT NOT NULL,
    relation       TEXT NOT NULL,
    PRIMARY KEY (statement_id, target_id, relation),
    {_CK_GEN_REL}
);

CREATE TABLE proofs (
    id              TEXT PRIMARY KEY,
    proves          TEXT NOT NULL REFERENCES statements(id),
    status          TEXT NOT NULL,
    schema_version  TEXT NOT NULL,
    style           TEXT,
    notes           TEXT,
    {_CK_STATUS},
    {_check_in("schema_version", SUPPORTED_SCHEMA_VERSIONS)}
);

CREATE TABLE proof_uses (
    proof_id      TEXT NOT NULL REFERENCES proofs(id),
    statement_id  TEXT NOT NULL REFERENCES statements(id),
    role          TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    implicit      INTEGER NOT NULL,
    locality      TEXT NOT NULL DEFAULT '',
    notes         TEXT,
    PRIMARY KEY (proof_id, statement_id, role, locality),
    {_CK_PROOF_USE_ROLE},
    {_CK_PROOF_USE_CONF}
);

CREATE TABLE proof_parts (
    proof_id   TEXT NOT NULL REFERENCES proofs(id),
    name       TEXT NOT NULL,
    kind       TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (proof_id, name),
    {_CK_PART_KIND}
);

CREATE TABLE proof_quality (
    proof_id       TEXT PRIMARY KEY REFERENCES proofs(id),
    extraction     TEXT,
    dependency     TEXT,
    semantic       TEXT,
    translation    TEXT,
    latex_conf     TEXT,
    source_align   TEXT,
    {_CK_CONF_EXTR},
    {_CK_CONF_DEP},
    {_CK_CONF_SEM},
    {_CK_CONF_TRANS},
    {_CK_CONF_LATEX},
    {_CK_CONF_SRC}
);

CREATE TABLE proof_provenance (
    proof_id       TEXT PRIMARY KEY REFERENCES proofs(id),
    schema_version TEXT NOT NULL,
    rerun_id       TEXT,
    extracted_by   TEXT,
    extracted_at   TEXT,
    redirected_to  TEXT,
    {_CK_PROV_VER}
);

CREATE TABLE sources (
    entity_id      TEXT NOT NULL,
    entity_kind    TEXT NOT NULL,
    work           TEXT NOT NULL,
    author         TEXT,
    edition        TEXT,
    year           INTEGER,
    chapter        TEXT,
    section        TEXT,
    theorem_label  TEXT,
    page           TEXT,
    locator        TEXT,
    url            TEXT,
    source_language TEXT,
    {_CK_SRC_KIND}
);

CREATE INDEX idx_sources_entity   ON sources(entity_id);
CREATE INDEX idx_sources_work     ON sources(work);
CREATE INDEX idx_sources_chapter  ON sources(chapter);
CREATE INDEX idx_proofs_proves    ON proofs(proves);
CREATE INDEX idx_proof_uses_stmt  ON proof_uses(statement_id);
CREATE INDEX idx_stmt_domain      ON statement_domains(name);
CREATE INDEX idx_stmt_ambient     ON statement_ambient(structure);
CREATE INDEX idx_stmt_ontology    ON statement_ontology(semantic_kind);
CREATE INDEX idx_stmt_keyword     ON statement_ontology(keyword);
CREATE INDEX idx_stmt_type        ON statements(type);
CREATE INDEX idx_stmt_status      ON statements(status);
-- v0.3.1 audit-oriented indexes (see reports/audits/v0.3-pilot-stewart-ch1
-- §1.2 and audit-2026-05-11-rudin §1.2/§4.3): support role-aware queries
-- on proof_uses (e.g. supremum-as-existence vs supremum-as-notation) and
-- rerun-scoped joins on provenance.
CREATE INDEX idx_proof_uses_role  ON proof_uses(statement_id, role);
CREATE INDEX idx_stmt_rerun       ON statement_provenance(rerun_id);
CREATE INDEX idx_proof_rerun      ON proof_provenance(rerun_id);
"""


def _populate(con: sqlite3.Connection, ds: Dataset) -> None:
    cur = con.cursor()
    for sid, s in ds.statements.items():
        cur.execute(
            "INSERT INTO statements VALUES (?,?,?,?,?,?,?,?,?)",
            (
                sid,
                s.type,
                s.status,
                s.schema_version,
                s.language.original,
                s.statement.latex.body,
                s.statement.latex.status,
                s.statement.latex.review_status,
                s.notes,
            ),
        )
        for lang, t in s.title.items():
            cur.execute(
                "INSERT INTO statement_titles VALUES (?,?,?,?,?,?)",
                (sid, lang, t.text, int(t.is_original), t.origin, t.review_status),
            )
        for lang, t in s.statement.natural.items():
            cur.execute(
                "INSERT INTO statement_natural VALUES (?,?,?,?,?,?)",
                (sid, lang, t.text, int(t.is_original), t.origin, t.review_status),
            )
        q = s.quality
        cur.execute(
            "INSERT INTO statement_quality VALUES (?,?,?,?,?,?,?)",
            (
                sid,
                q.extraction_confidence,
                q.dependency_confidence,
                q.semantic_confidence,
                q.translation_confidence,
                q.latex_confidence,
                q.source_alignment_confidence,
            ),
        )
        p = s.provenance
        cur.execute(
            "INSERT INTO statement_provenance VALUES (?,?,?,?,?,?)",
            (sid, p.schema_version, p.rerun_id, p.extracted_by, p.extracted_at, p.redirected_to),
        )
        for prior in p.derived_from:
            cur.execute(
                "INSERT INTO statement_derived_from VALUES (?,?)", (sid, prior)
            )
        for d in s.domains.primary:
            cur.execute(
                "INSERT OR IGNORE INTO statement_domains VALUES (?,?,?)",
                (sid, "primary", d),
            )
        for d in s.domains.secondary:
            cur.execute(
                "INSERT OR IGNORE INTO statement_domains VALUES (?,?,?)",
                (sid, "secondary", d),
            )
        for st in s.ambient.structures:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ambient VALUES (?,?)", (sid, st)
            )
        for k in s.ontology.semantic_kind:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ontology VALUES (?,?,?)",
                (sid, k, ""),
            )
        for kw in s.ontology.keywords:
            cur.execute(
                "INSERT OR IGNORE INTO statement_ontology VALUES (?,?,?)",
                (sid, "", kw),
            )
        for ref in s.proved_by:
            cur.execute(
                "INSERT INTO statement_proved_by VALUES (?,?)", (sid, ref)
            )
        for dep in s.depends_on:
            cur.execute(
                "INSERT INTO statement_depends_on VALUES (?,?,?,?,?)",
                (sid, dep.id, dep.role, dep.confidence, dep.notes),
            )
        for gen in s.generality:
            cur.execute(
                "INSERT INTO statement_generality VALUES (?,?,?)",
                (sid, gen.target, gen.relation),
            )
        for src in s.sources:
            cur.execute(
                "INSERT INTO sources VALUES (?,'statement',?,?,?,?,?,?,?,?,?,?,?)",
                (
                    sid, src.work, src.author, src.edition, src.year, src.chapter,
                    src.section, src.theorem_label, src.page, src.locator, src.url,
                    src.source_language,
                ),
            )

    for pid, pr in ds.proofs.items():
        cur.execute(
            "INSERT INTO proofs VALUES (?,?,?,?,?,?)",
            (pid, pr.proves, pr.status, pr.schema_version, pr.style, pr.notes),
        )
        for dep in pr.uses:
            cur.execute(
                "INSERT OR IGNORE INTO proof_uses VALUES (?,?,?,?,?,?,?)",
                (
                    pid, dep.id, dep.role, dep.confidence, int(dep.implicit),
                    dep.locality or "", dep.notes,
                ),
            )
        for part in pr.parts:
            cur.execute(
                "INSERT INTO proof_parts VALUES (?,?,?,?)",
                (pid, part.name, part.kind, part.description),
            )
            for dep in part.uses:
                cur.execute(
                    "INSERT OR IGNORE INTO proof_uses VALUES (?,?,?,?,?,?,?)",
                    (
                        pid, dep.id, dep.role, dep.confidence, int(dep.implicit),
                        dep.locality or part.name, dep.notes,
                    ),
                )
        q = pr.quality
        cur.execute(
            "INSERT INTO proof_quality VALUES (?,?,?,?,?,?,?)",
            (
                pid,
                q.extraction_confidence,
                q.dependency_confidence,
                q.semantic_confidence,
                q.translation_confidence,
                q.latex_confidence,
                q.source_alignment_confidence,
            ),
        )
        p = pr.provenance
        cur.execute(
            "INSERT INTO proof_provenance VALUES (?,?,?,?,?,?)",
            (pid, p.schema_version, p.rerun_id, p.extracted_by, p.extracted_at, p.redirected_to),
        )
        for src in pr.sources:
            cur.execute(
                "INSERT INTO sources VALUES (?,'proof',?,?,?,?,?,?,?,?,?,?,?)",
                (
                    pid, src.work, src.author, src.edition, src.year, src.chapter,
                    src.section, src.theorem_label, src.page, src.locator, src.url,
                    src.source_language,
                ),
            )
    con.commit()


# Confidence ordering used to compute a single `quality_overall` summary
# field for graph nodes. Lower-confidence axes dominate (worst-axis wins),
# so a node with one `low` axis is reported as `low`. None values ignored.
_CONFIDENCE_RANK = {"high": 2, "medium": 1, "low": 0}


def _worst_confidence(values: Iterable[str | None]) -> str | None:
    present = [v for v in values if v]
    if not present:
        return None
    return min(present, key=lambda v: _CONFIDENCE_RANK.get(v, 99))


def _node_summaries(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """Pre-compute per-node summary fields embedded in the graph payload.

    Filters in the visualization layer use these without a join to
    node-details. Keep payload small: scalars and short string lists only.
    Statements get primary_domain/semantic_kinds/latex_status/quality_overall;
    proofs get quality_overall.
    """
    summaries: dict[str, dict[str, Any]] = {}
    cur = con.cursor()

    # Statements: primary_domain (first primary domain alphabetically),
    # semantic_kinds, latex_status.
    for sid, latex_status in cur.execute(
        "SELECT id, latex_status FROM statements"
    ):
        summaries[sid] = {"latex_status": latex_status}
    for sid, name in cur.execute(
        "SELECT statement_id, name FROM statement_domains "
        "WHERE kind='primary' ORDER BY statement_id, name"
    ):
        summaries[sid].setdefault("primary_domain", name)
    kinds: dict[str, list[str]] = {}
    for sid, k in cur.execute(
        "SELECT statement_id, semantic_kind FROM statement_ontology "
        "WHERE semantic_kind != '' ORDER BY statement_id, semantic_kind"
    ):
        kinds.setdefault(sid, []).append(k)
    for sid, ks in kinds.items():
        summaries[sid]["semantic_kinds"] = ks

    # Statement quality_overall.
    for sid, *axes in cur.execute(
        "SELECT statement_id, extraction, dependency, semantic, "
        "translation, latex_conf, source_align FROM statement_quality"
    ):
        worst = _worst_confidence(axes)
        if worst:
            summaries.setdefault(sid, {})["quality_overall"] = worst

    # Proofs: only quality_overall is summarized at the graph level.
    for pid, *axes in cur.execute(
        "SELECT proof_id, extraction, dependency, semantic, "
        "translation, latex_conf, source_align FROM proof_quality"
    ):
        worst = _worst_confidence(axes)
        if worst:
            summaries.setdefault(pid, {})["quality_overall"] = worst

    return summaries


def _build_graph(con: sqlite3.Connection) -> nx.MultiDiGraph:
    g: nx.MultiDiGraph = nx.MultiDiGraph()
    cur = con.cursor()
    summaries = _node_summaries(con)

    for sid, stype, status in cur.execute("SELECT id, type, status FROM statements"):
        attrs = {"kind": "statement", "type": stype, "status": status}
        attrs.update(summaries.get(sid, {}))
        g.add_node(sid, **attrs)
    for pid, proves, status, style in cur.execute(
        "SELECT id, proves, status, style FROM proofs"
    ):
        attrs = {"kind": "proof", "type": "proof", "status": status,
                 "style": style or ""}
        attrs.update(summaries.get(pid, {}))
        g.add_node(pid, **attrs)
        g.add_edge(pid, proves, relation="proves")
    for pid, sid, role, conf, implicit in cur.execute(
        "SELECT proof_id, statement_id, role, confidence, implicit FROM proof_uses"
    ):
        g.add_edge(
            sid, pid,
            relation="uses", role=role, confidence=conf, implicit=bool(implicit),
        )
    for sid, tid, role in cur.execute(
        "SELECT statement_id, target_id, role FROM statement_depends_on"
    ):
        g.add_edge(sid, tid, relation="depends_on", role=role)
    return g


def _to_node_link(g: nx.MultiDiGraph) -> dict:
    nodes = sorted(({"id": n, **g.nodes[n]} for n in g.nodes), key=lambda d: d["id"])
    links = sorted(
        ({"source": u, "target": v, **data} for u, v, data in g.edges(data=True)),
        key=lambda d: (d["source"], d["target"], d.get("relation", "")),
    )
    return {"directed": True, "multigraph": True, "schema_version": "0.3.1",
            "nodes": nodes, "links": links}


def _quality_dict(row: tuple) -> dict[str, str] | None:
    """Convert a quality row (extraction, dependency, semantic, translation,
    latex_conf, source_align) into a dict, dropping None axes. Returns
    None if every axis is None.
    """
    keys = ("extraction", "dependency", "semantic", "translation",
            "latex", "source_alignment")
    out = {k: v for k, v in zip(keys, row) if v is not None}
    return out or None


def _provenance_dict(row: tuple) -> dict[str, Any] | None:
    """schema_version, rerun_id, extracted_by, extracted_at, redirected_to."""
    keys = ("schema_version", "rerun_id", "extracted_by",
            "extracted_at", "redirected_to")
    out = {k: v for k, v in zip(keys, row) if v is not None}
    return out or None


_SOURCE_KEYS = (
    "work", "author", "edition", "year", "chapter", "section",
    "theorem_label", "page", "locator", "url", "source_language",
)


def _source_rows(sub: sqlite3.Cursor, entity_id: str, entity_kind: str) -> list[dict]:
    out: list[dict] = []
    for row in sub.execute(
        "SELECT work, author, edition, year, chapter, section, theorem_label, "
        "page, locator, url, source_language FROM sources "
        "WHERE entity_id=? AND entity_kind=? ORDER BY work, chapter, section, "
        "theorem_label, page",
        (entity_id, entity_kind),
    ):
        entry = {k: v for k, v in zip(_SOURCE_KEYS, row) if v is not None}
        out.append(entry)
    return out


def _node_details(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    cur = con.cursor()
    sub = con.cursor()
    out: dict[str, dict] = {}

    # ---- statements -------------------------------------------------------
    stmt_rows = cur.execute(
        "SELECT id, type, status, original_lang, latex_body, latex_status, "
        "latex_review, notes FROM statements"
    ).fetchall()
    for (sid, stype, status, original_lang, latex_body, latex_status,
         latex_review, notes) in stmt_rows:
        entry: dict[str, Any] = {
            "id": sid, "kind": "statement", "type": stype, "status": status,
            "original_language": original_lang,
        }
        if notes:
            entry["notes"] = notes

        # i18n title
        titles = {}
        for lang, text, is_orig, origin, review in sub.execute(
            "SELECT lang, text, is_original, origin, review_status "
            "FROM statement_titles WHERE statement_id=?", (sid,),
        ):
            titles[lang] = {
                "text": text, "is_original": bool(is_orig),
                "origin": origin, "review_status": review,
            }
        if titles:
            entry["title"] = titles

        # i18n natural
        natural = {}
        for lang, text, is_orig, origin, review in sub.execute(
            "SELECT lang, text, is_original, origin, review_status "
            "FROM statement_natural WHERE statement_id=?", (sid,),
        ):
            natural[lang] = {
                "text": text, "is_original": bool(is_orig),
                "origin": origin, "review_status": review,
            }
        if natural:
            entry["natural"] = natural

        # latex
        if latex_body is not None or latex_status not in (None, "not_applicable"):
            entry["latex"] = {
                "body": latex_body,
                "status": latex_status,
                "review_status": latex_review,
            }

        # domains
        domains: dict[str, list[str]] = {"primary": [], "secondary": []}
        for kind, name in sub.execute(
            "SELECT kind, name FROM statement_domains WHERE statement_id=? "
            "ORDER BY kind, name", (sid,),
        ):
            domains[kind].append(name)
        if domains["primary"] or domains["secondary"]:
            entry["domains"] = {k: v for k, v in domains.items() if v}

        # ambient
        ambient = [
            r[0] for r in sub.execute(
                "SELECT structure FROM statement_ambient "
                "WHERE statement_id=? ORDER BY structure", (sid,),
            )
        ]
        if ambient:
            entry["ambient_structures"] = ambient

        # ontology — split into semantic_kind list and keywords list.
        semantic_kinds: list[str] = []
        keywords: list[str] = []
        for sk, kw in sub.execute(
            "SELECT semantic_kind, keyword FROM statement_ontology "
            "WHERE statement_id=? ORDER BY semantic_kind, keyword", (sid,),
        ):
            if sk:
                semantic_kinds.append(sk)
            if kw:
                keywords.append(kw)
        if semantic_kinds or keywords:
            ontology: dict[str, list[str]] = {}
            if semantic_kinds:
                ontology["semantic_kind"] = semantic_kinds
            if keywords:
                ontology["keywords"] = keywords
            entry["ontology"] = ontology

        # quality
        q_row = sub.execute(
            "SELECT extraction, dependency, semantic, translation, "
            "latex_conf, source_align FROM statement_quality WHERE statement_id=?",
            (sid,),
        ).fetchone()
        if q_row:
            quality = _quality_dict(q_row)
            if quality:
                entry["quality"] = quality

        # provenance
        p_row = sub.execute(
            "SELECT schema_version, rerun_id, extracted_by, extracted_at, "
            "redirected_to FROM statement_provenance WHERE statement_id=?",
            (sid,),
        ).fetchone()
        if p_row:
            prov = _provenance_dict(p_row)
            if prov:
                entry["provenance"] = prov

        # derived_from
        derived = [
            r[0] for r in sub.execute(
                "SELECT prior_id FROM statement_derived_from "
                "WHERE statement_id=? ORDER BY prior_id", (sid,),
            )
        ]
        if derived:
            entry["derived_from"] = derived

        # proved_by
        proved_by = [
            r[0] for r in sub.execute(
                "SELECT proof_id FROM statement_proved_by "
                "WHERE statement_id=? ORDER BY proof_id", (sid,),
            )
        ]
        if proved_by:
            entry["proved_by"] = proved_by

        # depends_on
        depends_on = []
        for tid, role, conf, dnotes in sub.execute(
            "SELECT target_id, role, confidence, notes FROM statement_depends_on "
            "WHERE statement_id=? ORDER BY target_id, role", (sid,),
        ):
            d = {"id": tid, "role": role}
            if conf is not None:
                d["confidence"] = conf
            if dnotes is not None:
                d["notes"] = dnotes
            depends_on.append(d)
        if depends_on:
            entry["depends_on"] = depends_on

        # generality
        generality = [
            {"target": tid, "relation": rel}
            for tid, rel in sub.execute(
                "SELECT target_id, relation FROM statement_generality "
                "WHERE statement_id=? ORDER BY relation, target_id", (sid,),
            )
        ]
        if generality:
            entry["generality"] = generality

        # sources
        sources = _source_rows(sub, sid, "statement")
        if sources:
            entry["sources"] = sources

        out[sid] = entry

    # ---- proofs -----------------------------------------------------------
    proof_rows = cur.execute(
        "SELECT id, proves, status, style, notes FROM proofs"
    ).fetchall()
    for pid, proves, status, style, notes in proof_rows:
        entry = {
            "id": pid, "kind": "proof", "type": "proof", "status": status,
            "proves": proves, "style": style or "",
        }
        if notes:
            entry["notes"] = notes

        # uses (proof_uses) — full role/confidence/implicit/locality
        uses = []
        for did, role, conf, implicit, locality, unotes in sub.execute(
            "SELECT statement_id, role, confidence, implicit, locality, notes "
            "FROM proof_uses WHERE proof_id=? "
            "ORDER BY statement_id, role, locality",
            (pid,),
        ):
            u: dict[str, Any] = {
                "id": did, "role": role, "confidence": conf,
                "implicit": bool(implicit),
            }
            if locality:
                u["locality"] = locality
            if unotes:
                u["notes"] = unotes
            uses.append(u)
        if uses:
            entry["uses"] = uses

        # parts
        parts = []
        for name, kind, description in sub.execute(
            "SELECT name, kind, description FROM proof_parts "
            "WHERE proof_id=? ORDER BY name", (pid,),
        ):
            part: dict[str, Any] = {"name": name, "kind": kind}
            if description:
                part["description"] = description
            parts.append(part)
        if parts:
            entry["parts"] = parts

        # quality
        q_row = sub.execute(
            "SELECT extraction, dependency, semantic, translation, "
            "latex_conf, source_align FROM proof_quality WHERE proof_id=?",
            (pid,),
        ).fetchone()
        if q_row:
            quality = _quality_dict(q_row)
            if quality:
                entry["quality"] = quality

        # provenance
        p_row = sub.execute(
            "SELECT schema_version, rerun_id, extracted_by, extracted_at, "
            "redirected_to FROM proof_provenance WHERE proof_id=?",
            (pid,),
        ).fetchone()
        if p_row:
            prov = _provenance_dict(p_row)
            if prov:
                entry["provenance"] = prov

        # sources
        sources = _source_rows(sub, pid, "proof")
        if sources:
            entry["sources"] = sources

        out[pid] = entry
    return out


def build_db(ds: Dataset | None = None) -> sqlite3.Connection:
    if ds is None:
        ds = load_dataset()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(str(DB_PATH))
    con.executescript(SCHEMA_SQL)
    _populate(con, ds)
    return con


def _graphml_safe(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Return a copy with list-valued node attributes coerced to comma-
    separated strings. GraphML does not support list types; we only need
    these summaries for visualization/JSON consumers, so flatten for the
    GraphML export instead of dropping data.
    """
    out = g.copy()
    for _, attrs in out.nodes(data=True):
        for k, v in list(attrs.items()):
            if isinstance(v, list):
                attrs[k] = ",".join(v)
    return out


def _write_outputs(con: sqlite3.Connection) -> tuple[int, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    g = _build_graph(con)
    (GRAPH_DIR / "graph.json").write_text(
        json.dumps(_to_node_link(g), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (GRAPH_DIR / "node-details.json").write_text(
        json.dumps(_node_details(con), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    nx.write_graphml(_graphml_safe(g), EXPORT_DIR / "graph.graphml")
    return g.number_of_nodes(), g.number_of_edges()


def main() -> int:
    print("loading v0.3 YAML …")
    ds = load_dataset()
    if ds.skipped_legacy:
        print(f"  skipped {len(ds.skipped_legacy)} non-v0.3 file(s)")
    if ds.errors:
        print(f"FAIL — {len(ds.errors)} schema error(s):", file=sys.stderr)
        for e in ds.errors:
            print(f"  - {e.path}: {e.message}", file=sys.stderr)
        return 1
    print(f"  {len(ds.statements)} statements, {len(ds.proofs)} proofs")
    print("building SQLite …")
    con = build_db(ds)
    print(f"  wrote {DB_PATH.relative_to(REPO_ROOT)}")
    print("writing outputs …")
    n, e = _write_outputs(con)
    print(f"  graph: {n} nodes, {e} edges")
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

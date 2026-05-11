from pathlib import Path

import yaml

from scripts.validate import validate


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _make_dataset(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    _write(
        data / "statements" / "definition.function.yml",
        {
            "id": "definition.function",
            "type": "definition",
            "title": {"en": "Function"},
            "statement": {"natural": {"en": "A function maps each input to one output."}},
        },
    )
    _write(
        data / "statements" / "theorem.foo.yml",
        {
            "id": "theorem.foo",
            "type": "theorem",
            "title": {"en": "Foo"},
            "statement": {"natural": {"en": "Foo holds."}},
            "proved_by": ["proof.theorem-foo.direct"],
        },
    )
    _write(
        data / "proofs" / "proof.theorem-foo.direct.yml",
        {
            "id": "proof.theorem-foo.direct",
            "type": "proof",
            "proves": "theorem.foo",
            "uses": ["definition.function"],
        },
    )
    return data


def test_valid_dataset_passes(tmp_path):
    data = _make_dataset(tmp_path)
    assert validate(data) == []


def test_dangling_proof_reference(tmp_path):
    data = _make_dataset(tmp_path)
    _write(
        data / "statements" / "theorem.bar.yml",
        {
            "id": "theorem.bar",
            "type": "theorem",
            "title": {"en": "Bar"},
            "statement": {"natural": {"en": "Bar holds."}},
            "proved_by": ["proof.does-not-exist.direct"],
        },
    )
    errors = validate(data)
    assert any("unknown proof" in e for e in errors)


def test_proof_uses_unknown_statement(tmp_path):
    data = _make_dataset(tmp_path)
    _write(
        data / "proofs" / "proof.theorem-foo.alt.yml",
        {
            "id": "proof.theorem-foo.alt",
            "type": "proof",
            "proves": "theorem.foo",
            "uses": ["definition.does-not-exist"],
        },
    )
    # also add proved_by mirror to avoid symmetry error masking this one
    foo = data / "statements" / "theorem.foo.yml"
    raw = yaml.safe_load(foo.read_text(encoding="utf-8"))
    raw["proved_by"].append("proof.theorem-foo.alt")
    foo.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
    errors = validate(data)
    assert any("unknown statement" in e for e in errors)


def test_symmetry_required(tmp_path):
    data = _make_dataset(tmp_path)
    foo = data / "statements" / "theorem.foo.yml"
    raw = yaml.safe_load(foo.read_text(encoding="utf-8"))
    raw["proved_by"] = []  # drop the link
    foo.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
    errors = validate(data)
    assert any("does not list it in proved_by" in e for e in errors)


def test_duplicate_id(tmp_path):
    data = _make_dataset(tmp_path)
    _write(
        data / "statements" / "definition.function.duplicate.yml",
        {
            "id": "definition.function",
            "type": "definition",
            "title": {"en": "Function"},
            "statement": {"natural": {"en": "Same id."}},
        },
    )
    errors = validate(data)
    assert any("duplicate id" in e for e in errors)


def test_cycle_detection(tmp_path):
    """A→B→A cycle through proofs."""
    data = tmp_path / "data"
    _write(
        data / "statements" / "theorem.a.yml",
        {
            "id": "theorem.a",
            "type": "theorem",
            "title": {"en": "A"},
            "statement": {"natural": {"en": "A."}},
            "proved_by": ["proof.theorem-a.via-b"],
        },
    )
    _write(
        data / "statements" / "theorem.b.yml",
        {
            "id": "theorem.b",
            "type": "theorem",
            "title": {"en": "B"},
            "statement": {"natural": {"en": "B."}},
            "proved_by": ["proof.theorem-b.via-a"],
        },
    )
    _write(
        data / "proofs" / "proof.theorem-a.via-b.yml",
        {
            "id": "proof.theorem-a.via-b",
            "type": "proof",
            "proves": "theorem.a",
            "uses": ["theorem.b"],
        },
    )
    _write(
        data / "proofs" / "proof.theorem-b.via-a.yml",
        {
            "id": "proof.theorem-b.via-a",
            "type": "proof",
            "proves": "theorem.b",
            "uses": ["theorem.a"],
        },
    )
    errors = validate(data)
    assert any("cyclic dependency" in e for e in errors)


def test_invalid_yaml_in_dataset(tmp_path):
    data = _make_dataset(tmp_path)
    bad = data / "statements" / "broken.yml"
    bad.write_text("id: theorem.broken\ntype: theorem\n  invalid_indent\n", encoding="utf-8")
    errors = validate(data)
    assert any("broken.yml" in e for e in errors)

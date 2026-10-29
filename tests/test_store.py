import json

import pytest

from nave.cli import cmd_ingest
from nave.store import connect, add_indicator, list_indicators, list_audit


def test_insert_and_deduplicate(tmp_path):
    db = tmp_path / "nave.db"
    item = {"type": "domain", "value": "EXAMPLE.ORG", "source": "test", "confidence": 40}
    with connect(db) as con:
        assert add_indicator(con, item) is True
        assert add_indicator(con, item) is False
        rows = list_indicators(con)
    assert len(rows) == 1
    assert rows[0]["normalized_value"] == "example.org"


def test_reject_bad_confidence(tmp_path):
    with connect(tmp_path / "nave.db") as con:
        with pytest.raises(ValueError):
            add_indicator(con, {"type": "domain", "value": "example.org", "source": "test", "confidence": 101})


def test_reject_missing_required_field(tmp_path):
    with connect(tmp_path / "nave.db") as con:
        with pytest.raises(ValueError):
            add_indicator(con, {"type": "domain", "value": "example.org"})


def test_json_import_rolls_back_entire_batch_on_invalid_record(tmp_path, monkeypatch, capsys):
    db = tmp_path / "nave.db"
    source = tmp_path / "import.json"
    source.write_text(json.dumps([
        {
            "type": "domain",
            "value": "first.example",
            "source": "atomic-test",
            "confidence": 50,
        },
        {
            "type": "domain",
            "value": "second.example",
            "source": "atomic-test",
            "confidence": 101,
        },
    ]), encoding="utf-8")
    monkeypatch.setenv("NAVE_DB", str(db))

    result = cmd_ingest(type("Args", (), {"path": str(source)})())

    assert result == 2
    assert "Error en elemento 2" in capsys.readouterr().err
    with connect(db) as con:
        assert list_indicators(con) == []
        assert list_audit(con) == []


def test_json_import_rejects_non_object_and_rolls_back(tmp_path, monkeypatch, capsys):
    db = tmp_path / "nave.db"
    source = tmp_path / "import.json"
    source.write_text(json.dumps([
        {
            "type": "domain",
            "value": "first.example",
            "source": "atomic-test",
            "confidence": 50,
        },
        "not-an-object",
    ]), encoding="utf-8")
    monkeypatch.setenv("NAVE_DB", str(db))

    result = cmd_ingest(type("Args", (), {"path": str(source)})())

    assert result == 2
    assert "se esperaba un objeto" in capsys.readouterr().err
    with connect(db) as con:
        assert list_indicators(con) == []
        assert list_audit(con) == []

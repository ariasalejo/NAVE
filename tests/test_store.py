import json
import sqlite3

import pytest

from nave.store import connect, add_indicator, list_indicators


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
            add_indicator(con, {"type":"domain","value":"example.org","source":"test","confidence":101})


def test_reject_missing_required_field(tmp_path):
    with connect(tmp_path / "nave.db") as con:
        with pytest.raises(ValueError):
            add_indicator(con, {"type":"domain","value":"example.org"})

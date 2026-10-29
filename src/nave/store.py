"""Persistencia local SQLite para el MVP de NAVE."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DB = Path.home() / ".local" / "share" / "nave" / "nave.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def database_path() -> Path:
    return Path(os.environ.get("NAVE_DB", str(DEFAULT_DB))).expanduser()


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    initialize(con)
    return con


def initialize(con: sqlite3.Connection) -> None:
    con.executescript("""
    CREATE TABLE IF NOT EXISTS indicators (
        id INTEGER PRIMARY KEY,
        kind TEXT NOT NULL,
        value TEXT NOT NULL,
        normalized_value TEXT NOT NULL,
        source TEXT NOT NULL,
        confidence INTEGER NOT NULL CHECK(confidence BETWEEN 0 AND 100),
        labels_json TEXT NOT NULL DEFAULT '[]',
        notes TEXT NOT NULL DEFAULT '',
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        content_hash TEXT NOT NULL UNIQUE
    );
    CREATE INDEX IF NOT EXISTS idx_indicators_kind ON indicators(kind);
    CREATE INDEX IF NOT EXISTS idx_indicators_value ON indicators(normalized_value);
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        detail_json TEXT NOT NULL
    );
    """)
    con.commit()


def normalize(kind: str, value: str) -> str:
    value = value.strip()
    if kind in {"domain", "url", "email", "ipv4", "ipv6", "sha256", "md5"}:
        return value.lower()
    return value


def add_indicator(con: sqlite3.Connection, item: dict) -> bool:
    required = ("type", "value", "source")
    if any(not isinstance(item.get(k), str) or not item[k].strip() for k in required):
        raise ValueError("Cada indicador requiere type, value y source como texto no vacío.")
    kind = item["type"].strip().lower()
    value = item["value"].strip()
    source = item["source"].strip()
    confidence = item.get("confidence", 50)
    if not isinstance(confidence, int) or isinstance(confidence, bool) or not 0 <= confidence <= 100:
        raise ValueError("confidence debe ser un entero entre 0 y 100.")
    labels = item.get("labels", [])
    if not isinstance(labels, list) or any(not isinstance(x, str) for x in labels):
        raise ValueError("labels debe ser una lista de textos.")
    notes = item.get("notes", "")
    if not isinstance(notes, str):
        raise ValueError("notes debe ser texto.")
    normalized = normalize(kind, value)
    digest = hashlib.sha256(
        f"{kind}\0{normalized}\0{source}".encode("utf-8")
    ).hexdigest()
    now = utc_now()
    cur = con.execute("""
        INSERT OR IGNORE INTO indicators
        (kind,value,normalized_value,source,confidence,labels_json,notes,
         first_seen,last_seen,content_hash)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (kind, value, normalized, source, confidence,
          json.dumps(labels, ensure_ascii=False), notes, now, now, digest))
    inserted = cur.rowcount == 1
    if inserted:
        log_event(con, "indicator.imported", {"type": kind, "source": source, "hash": digest})
    else:
        con.execute("UPDATE indicators SET last_seen=? WHERE content_hash=?", (now, digest))
        log_event(con, "indicator.duplicate", {"type": kind, "source": source, "hash": digest})
    con.commit()
    return inserted


def log_event(con: sqlite3.Connection, action: str, detail: dict) -> None:
    con.execute(
        "INSERT INTO audit_log(timestamp,action,detail_json) VALUES(?,?,?)",
        (utc_now(), action, json.dumps(detail, ensure_ascii=False, sort_keys=True)),
    )


def list_indicators(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(con.execute(
        "SELECT id,kind,value,source,confidence,labels_json,first_seen,last_seen "
        "FROM indicators ORDER BY id DESC"
    ))


def list_audit(con: sqlite3.Connection, limit: int = 20) -> list[sqlite3.Row]:
    return list(con.execute(
        "SELECT timestamp,action,detail_json FROM audit_log ORDER BY id DESC LIMIT ?",
        (limit,),
    ))

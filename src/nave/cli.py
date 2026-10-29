"""Interfaz de línea de comandos de NAVE."""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import sqlite3
import sys
from pathlib import Path

from . import __version__
from .store import connect, database_path, add_indicator, list_indicators, list_audit


def cmd_doctor(_: argparse.Namespace) -> int:
    print(f"NAVE {__version__} — diagnóstico de solo lectura")
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Sistema: {platform.platform()}")
    print(f"SQLite: {sqlite3.sqlite_version}")
    print(f"Base de datos: {database_path()}")
    print("Herramientas encontradas:")
    for name in ("nmap", "tshark", "wireshark", "lynis", "yara", "zeek",
                 "osqueryi", "clamscan", "docker", "podman", "git"):
        path = shutil.which(name)
        print(f"  {'OK' if path else '--'} {name}: {path or 'no está en PATH'}")
    print("Este diagnóstico no instala, ejecuta ni configura herramientas externas.")
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    source = Path(args.path)
    if not source.is_file():
        print(f"Error: no existe el archivo: {source}", file=sys.stderr)
        return 2
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Error leyendo JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, list):
        print("Error: la raíz del JSON debe ser una lista.", file=sys.stderr)
        return 2

    inserted = duplicates = 0
    try:
        # The connection context commits only if the entire batch succeeds.
        # Any invalid record raises an exception and rolls back the whole batch.
        with connect() as con:
            for number, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    raise ValueError(
                        f"Error en elemento {number}: se esperaba un objeto."
                    )
                try:
                    if add_indicator(con, item):
                        inserted += 1
                    else:
                        duplicates += 1
                except ValueError as exc:
                    raise ValueError(f"Error en elemento {number}: {exc}") from exc
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, sqlite3.Error) as exc:
        print(f"Error de base de datos durante la importación: {exc}", file=sys.stderr)
        return 2

    print(f"Importación terminada: {inserted} nuevos; {duplicates} duplicados.")
    return 0


def cmd_indicators(_: argparse.Namespace) -> int:
    with connect() as con:
        rows = list_indicators(con)
    if not rows:
        print("No hay indicadores. Importa examples/indicators.json.")
        return 0
    for row in rows:
        print(f"#{row['id']} [{row['kind']}] {row['value']} | fuente={row['source']} | confianza={row['confidence']}")
    return 0


def cmd_audit(_: argparse.Namespace) -> int:
    with connect() as con:
        rows = list_audit(con)
    for row in rows:
        print(f"{row['timestamp']} {row['action']} {row['detail_json']}")
    if not rows:
        print("La bitácora está vacía.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    with connect() as con:
        rows = list_indicators(con)
        audit = list_audit(con, 100)
    lines = [
        "# Informe NAVE",
        "",
        f"- Versión: {__version__}",
        f"- Base de datos: `{database_path()}`",
        f"- Indicadores registrados: {len(rows)}",
        "",
        "## Indicadores",
        "",
        "| Tipo | Valor | Fuente | Confianza | Primera observación |",
        "|---|---|---|---:|---|",
    ]
    for row in rows:
        safe_value = str(row["value"]).replace("|", "\\|").replace("\n", " ")
        safe_source = str(row["source"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {row['kind']} | `{safe_value}` | {safe_source} | {row['confidence']} | {row['first_seen']} |")
    lines += ["", "## Bitácora reciente", ""]
    for row in audit:
        lines.append(f"- `{row['timestamp']}` **{row['action']}** — `{row['detail_json']}`")
    lines += ["", "> Este informe refleja únicamente los datos locales importados; no implica que los indicadores hayan sido verificados externamente.", ""]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Informe generado: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nave", description="NAVE — inteligencia y auditoría defensiva local")
    parser.add_argument("--version", action="version", version=f"NAVE {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor", help="diagnóstico de solo lectura")
    p.set_defaults(func=cmd_doctor)
    p = sub.add_parser("ingest-json", help="importar indicadores desde JSON local")
    p.add_argument("path")
    p.set_defaults(func=cmd_ingest)
    p = sub.add_parser("indicators", help="listar indicadores locales")
    p.set_defaults(func=cmd_indicators)
    p = sub.add_parser("audit-log", help="mostrar la bitácora")
    p.set_defaults(func=cmd_audit)
    p = sub.add_parser("report", help="generar informe Markdown")
    p.add_argument("--output", default="reports/nave-report.md")
    p.set_defaults(func=cmd_report)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()

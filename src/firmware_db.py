"""Simple firmware metadata database and export utilities."""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List
import json
import datetime


DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS firmware (
    sha256 TEXT PRIMARY KEY,
    file_name TEXT,
    processor_family TEXT,
    firmware_type TEXT,
    flight_stack TEXT,
    version TEXT,
    confidence REAL,
    board_type TEXT,
    date_analyzed TEXT,
    notes TEXT,
    duplicate_of TEXT,
    added_at TEXT
);
"""


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(DB_SCHEMA)
    conn.commit()
    return conn


def upsert_firmware(conn: sqlite3.Connection, metadata: Dict[str, Any]) -> None:
    now = datetime.datetime.utcnow().isoformat() + "Z"
    conn.execute(
        "INSERT OR REPLACE INTO firmware (sha256, file_name, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of, added_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            metadata.get("sha256"),
            metadata.get("file_name"),
            metadata.get("processor_family"),
            metadata.get("firmware_type"),
            metadata.get("flight_stack"),
            metadata.get("version"),
            metadata.get("confidence"),
            metadata.get("board_type"),
            metadata.get("date_analyzed"),
            metadata.get("notes"),
            metadata.get("duplicate_of"),
            now,
        ),
    )
    conn.commit()


def export_to_dronemaker(conn: sqlite3.Connection, out_path: Path) -> None:
    cur = conn.cursor()
    cur.execute("SELECT sha256, file_name, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of, added_at FROM firmware")
    rows = cur.fetchall()
    entries: List[Dict[str, Any]] = []
    for sha256, file_name, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of, added_at in rows:
        entries.append(
            {
                "firmware_hash": sha256,
                "file_name": file_name,
                "processor_family": processor_family,
                "firmware_type": firmware_type,
                "flight_stack": flight_stack,
                "version": version,
                "confidence": confidence,
                "board_type": board_type,
                "date_analyzed": date_analyzed,
                "notes": notes,
                "duplicate_of": duplicate_of,
                "added_at": added_at,
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump({"firmware": entries}, fh, indent=2)


def export_inventory_json(conn: sqlite3.Connection, out_path: Path) -> None:
    cur = conn.cursor()
    cur.execute("SELECT file_name, sha256, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of FROM firmware")
    rows = cur.fetchall()
    entries: List[Dict[str, Any]] = []
    for file_name, sha256, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of in rows:
        entries.append(
            {
                "file_name": file_name,
                "sha256": sha256,
                "processor_family": processor_family,
                "firmware_type": firmware_type,
                "flight_stack": flight_stack,
                "version": version,
                "confidence": confidence,
                "board_type": board_type,
                "date_analyzed": date_analyzed,
                "notes": notes,
                "duplicate_of": duplicate_of,
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump({"inventory": entries}, fh, indent=2)


def export_inventory_csv(conn: sqlite3.Connection, out_path: Path) -> None:
    import csv

    cur = conn.cursor()
    cur.execute("SELECT file_name, sha256, processor_family, firmware_type, flight_stack, version, confidence, board_type, date_analyzed, notes, duplicate_of FROM firmware")
    rows = cur.fetchall()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["file_name", "sha256", "processor_family", "firmware_type", "flight_stack", "version", "confidence", "board_type", "date_analyzed", "notes", "duplicate_of"])
        for row in rows:
            writer.writerow(row)

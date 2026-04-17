"""
storage.py — SQLite persistence for the BAEL project log.

The database file is created next to this module on first use.
All functions are safe to call concurrently (SQLite WAL mode).
"""

import sqlite3
import json
import os
from pathlib import Path

# ── Database path ──────────────────────────────────────────────────────────────
_DB_PATH = Path(__file__).parent / "bael_projects.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the project_log table if it does not exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS project_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project     TEXT    NOT NULL DEFAULT 'default',
                repere      TEXT,
                type        TEXT,
                nu_mn       REAL,
                section_cm2 REAL,
                stirrup_phi REAL,
                spacing_cm  REAL,
                dimensions  TEXT,
                armatures_a REAL,
                armatures_b REAL,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                extra_json  TEXT
            )
        """)


# ── CRUD helpers ───────────────────────────────────────────────────────────────

def save_entry(entry: dict, project: str = "default") -> None:
    """Persist a design log entry."""
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO project_log
                (project, repere, type, nu_mn, section_cm2,
                 stirrup_phi, spacing_cm, dimensions, armatures_a, armatures_b)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project,
            entry.get("Repère"),
            entry.get("Type"),
            entry.get("Nu (MN)"),
            entry.get("Section Adop. (cm²)"),
            entry.get("Cadres (Φt)"),
            entry.get("Espacement (cm)"),
            entry.get("Dimensions (m)"),
            entry.get("Armatures A (cm²)"),
            entry.get("Armatures B (cm²)"),
        ))


def load_entries(project: str = "default") -> list[dict]:
    """Return all entries for a project as a list of dicts (matching legacy format)."""
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT repere, type, nu_mn, section_cm2,
                   stirrup_phi, spacing_cm, dimensions, armatures_a, armatures_b
            FROM project_log
            WHERE project = ?
            ORDER BY id
        """, (project,)).fetchall()

    return [
        {
            "Repère":              r["repere"],
            "Type":                r["type"],
            "Nu (MN)":             r["nu_mn"],
            "Section Adop. (cm²)": r["section_cm2"],
            "Cadres (Φt)":         r["stirrup_phi"],
            "Espacement (cm)":     r["spacing_cm"],
            "Dimensions (m)":      r["dimensions"],
            "Armatures A (cm²)":   r["armatures_a"],
            "Armatures B (cm²)":   r["armatures_b"],
        }
        for r in rows
    ]


def clear_entries(project: str = "default") -> None:
    """Delete all entries for a project."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM project_log WHERE project = ?", (project,))


def list_projects() -> list[str]:
    """Return all distinct project names."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT project FROM project_log ORDER BY project"
        ).fetchall()
    return [r["project"] for r in rows]

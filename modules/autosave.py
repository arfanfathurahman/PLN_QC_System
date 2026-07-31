"""
Autosave berbasis session_state + SQLite untuk form QC.
Dipakai oleh form_onepost, form_phbtr, form_pmcb.

Cara pakai:
    from modules.autosave import autosave_if_changed

    autosave_if_changed(
        form_key="onepost",
        serial="OP-2026-001",
        payload={"no_sn": ..., "teknisi": ..., ...},
    )

Draft disimpan ke tabel <form_key>_draft (created on first save).
Status autosave ditampilkan via st.toast.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "qc_database.db"


def _conn():
    return sqlite3.connect(str(DB_PATH))


def _ensure_table(table: str):
    """Buat tabel draft jika belum ada. Skema fleksibel (data_json)."""
    with _conn() as c:
        c.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                no_sn TEXT PRIMARY KEY,
                teknisi TEXT,
                status TEXT,
                data_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        c.commit()


def autosave_if_changed(form_key: str, serial: str, payload: dict, teknisi: str = "", status: str = "Draft"):
    """
    Simpan draft hanya jika payload berubah sejak simpanan terakhir.
    Mengembalikan True bila tersimpan, False bila tidak ada perubahan.
    """
    if not serial:
        return False

    table = f"{form_key}_draft"
    _ensure_table(table)

    sig_key = f"_autosave_sig_{form_key}"
    new_sig = json.dumps(payload, sort_keys=True, default=str)

    if st.session_state.get(sig_key) == new_sig:
        return False  # tidak ada perubahan

    try:
        with _conn() as c:
            c.execute(
                f"""
                INSERT INTO {table} (no_sn, teknisi, status, data_json, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(no_sn) DO UPDATE SET
                    teknisi=excluded.teknisi,
                    status=excluded.status,
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
                """,
                (serial, teknisi, status, new_sig, datetime.now().isoformat(timespec="seconds")),
            )
            c.commit()
        st.session_state[sig_key] = new_sig
        st.toast("💾 Autosave: draft tersimpan otomatis", icon="💾")
        return True
    except Exception as exc:
        st.session_state["_autosave_err"] = str(exc)
        return False


def load_draft(form_key: str, serial: str):
    """Muat draft berdasarkan serial number. Mengembalikan dict atau None."""
    if not serial:
        return None
    table = f"{form_key}_draft"
    _ensure_table(table)
    with _conn() as c:
        cur = c.execute(f"SELECT data_json FROM {table} WHERE no_sn=?", (serial,))
        row = cur.fetchone()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return None
    return None


def list_drafts(form_key: str):
    """Daftar serial number draft yang tersimpan (terbaru di atas)."""
    table = f"{form_key}_draft"
    _ensure_table(table)
    with _conn() as c:
        cur = c.execute(f"SELECT no_sn, updated_at FROM {table} ORDER BY updated_at DESC")
        rows = cur.fetchall()
    return [{"no_sn": r[0], "updated_at": r[1]} for r in rows]

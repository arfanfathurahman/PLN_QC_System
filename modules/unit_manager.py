"""
Multi-unit manager + full history autosave untuk form QC.

Fitur:
  - Pengujian lebih dari 1 unit per form (list serial number)
  - Pilih unit aktif untuk diedit
  - Autosave: setiap perubahan widget tersimpan ke history
  - History lengkap: siapa, kapan, apa yang berubah
  - Fleksibel: bisa pindah-pindah unit tanpa kehilangan data

Cara pakai di form:
    from modules.unit_manager import init_units, render_unit_selector, \
        get_active_unit_state, autosave_unit, render_history_panel

    # di Informasi tab:
    init_units("onepost")           # siapkan state
    render_unit_selector("onepost") # UI pilih unit
    unit = get_active_unit_state("onepost")  # ambil data unit aktif

    # di tiap tab pemeriksaan, setelah user isi:
    autosave_unit("onepost", "visual_onepost", hasil_visual)

    # di Summary tab:
    render_history_panel("onepost")
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "qc_database.db"

# Session-state keys per form
_SS_UNITS = "_units_{}"        # list of serial numbers
_SS_ACTIVE = "_active_unit_{}"  # current serial
_SS_DATA = "_unit_data_{}"      # {serial: {state dict}}


def _conn():
    return sqlite3.connect(str(DB_PATH))


def _ensure_table(table: str):
    with _conn() as c:
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                no_sn TEXT NOT NULL,
                form_key TEXT NOT NULL,
                tab_name TEXT,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT DEFAULT 'inspector',
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                snapshot_json TEXT
            )
        """)
        c.commit()


def _form_table(form_key: str) -> str:
    return f"{form_key}_history"


def init_units(form_key: str, default_serials: list = None):
    """Inisialisasi state multi-unit. Dipanggil sekali per form render."""
    units_key = _SS_UNITS.format(form_key)
    active_key = _SS_ACTIVE.format(form_key)
    data_key = _SS_DATA.format(form_key)

    if units_key not in st.session_state:
        if default_serials:
            st.session_state[units_key] = list(default_serials)
        else:
            st.session_state[units_key] = []
    if active_key not in st.session_state:
        st.session_state[active_key] = (
            st.session_state[units_key][0] if st.session_state[units_key] else None
        )
    if data_key not in st.session_state:
        st.session_state[data_key] = {}


def get_units(form_key: str) -> list:
    return st.session_state.get(_SS_UNITS.format(form_key), [])


def get_active_serial(form_key: str) -> str:
    return st.session_state.get(_SS_ACTIVE.format(form_key), None)


def get_active_unit_state(form_key: str) -> dict:
    """Return full state dict for the active unit, or empty dict."""
    serial = get_active_serial(form_key)
    if not serial:
        return {}
    data = st.session_state.get(_SS_DATA.format(form_key), {})
    return data.get(serial, {})


def set_unit_state(form_key: str, serial: str, field: str, value):
    """Set a field on a unit's state and return whether it changed."""
    data_key = _SS_DATA.format(form_key)
    if data_key not in st.session_state:
        st.session_state[data_key] = {}
    unit_data = st.session_state[data_key].setdefault(serial, {})
    old = unit_data.get(field)
    changed = old != value
    unit_data[field] = value
    return changed


def add_unit(form_key: str, serial: str):
    """Add a new unit serial to the list."""
    units_key = _SS_UNITS.format(form_key)
    if units_key not in st.session_state:
        st.session_state[units_key] = []
    if serial and serial not in st.session_state[units_key]:
        st.session_state[units_key].append(serial)
        st.session_state[_SS_ACTIVE.format(form_key)] = serial


def remove_unit(form_key: str, serial: str):
    """Remove a unit serial from the list."""
    units_key = _SS_UNITS.format(form_key)
    data_key = _SS_DATA.format(form_key)
    if units_key in st.session_state and serial in st.session_state[units_key]:
        st.session_state[units_key].remove(serial)
    if data_key in st.session_state and serial in st.session_state[data_key]:
        del st.session_state[data_key][serial]
    active_key = _SS_ACTIVE.format(form_key)
    if st.session_state.get(active_key) == serial:
        st.session_state[active_key] = (
            st.session_state[units_key][0] if st.session_state.get(units_key) else None
        )


def _save_history(form_key: str, serial: str, tab_name: str, field_name: str,
                  old_val, new_val, changed_by="inspector", snapshot=None):
    """Insert a history row."""
    table = _form_table(form_key)
    _ensure_table(table)
    try:
        with _conn() as c:
            c.execute(
                f"""INSERT INTO {table}
                   (no_sn, form_key, tab_name, field_name, old_value, new_value, changed_by, changed_at, snapshot_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    serial, form_key, tab_name, field_name,
                    json.dumps(old_val, default=str) if old_val is not None else None,
                    json.dumps(new_val, default=str) if new_val is not None else None,
                    changed_by,
                    datetime.now().isoformat(timespec="seconds"),
                    json.dumps(snapshot, default=str) if snapshot else None,
                ),
            )
            c.commit()
    except Exception:
        pass  # history is best-effort


def autosave_unit(form_key: str, field_name: str, value, tab_name: str = ""):
    """
    Autosave a field for the active unit. Only writes history if changed.
    Also pushes value to session_state so other tabs can read it.
    """
    serial = get_active_serial(form_key)
    if not serial:
        return

    # Also mirror to st.session_state[field_name] so existing form code works
    st.session_state[field_name] = value

    # Check if changed vs stored state
    data_key = _SS_DATA.format(form_key)
    unit_data = st.session_state.setdefault(data_key, {}).setdefault(serial, {})
    old = unit_data.get(field_name)

    if old != value:
        _save_history(form_key, serial, tab_name, field_name, old, value, snapshot=unit_data)
        unit_data[field_name] = value
        st.toast(f"💾 Tersimpan: {field_name} (unit {serial})", icon="💾")


def render_unit_selector(form_key: str, label_prefix: str = "Unit"):
    """
    Render UI untuk tambah / pilih / hapus unit.
    Returns the active serial.
    """
    units = get_units(form_key)
    active = get_active_serial(form_key)

    st.markdown(
        '<div class="siak-card-title"><i class="bi bi-list-nested"></i> '
        f"Daftar Unit Pengujian ({len(units)} unit)</div>",
        unsafe_allow_html=True,
    )

    # Input untuk tambah unit baru
    c_add, c_btn = st.columns([3, 1])
    with c_add:
        new_serial = st.text_input(
            "Nomor Seri Unit Baru",
            key=f"new_serial_{form_key}",
            placeholder="cth: OP-2026-001",
            label_visibility="collapsed",
        )
    with c_btn:
        if st.button("➕ Tambah", key=f"add_unit_{form_key}", use_container_width=True):
            if new_serial.strip():
                add_unit(form_key, new_serial.strip())
                st.rerun()

    if not units:
        st.info("Belum ada unit. Tambahkan nomor seri unit untuk mulai pengujian.")
        return None

    # Selector unit aktif
    active = st.selectbox(
        f"Pilih unit aktif untuk diedit:",
        units,
        index=units.index(active) if active in units else 0,
        key=f"sel_unit_{form_key}",
    )
    st.session_state[_SS_ACTIVE.format(form_key)] = active

    # Tombol hapus unit
    if st.button("🗑 Hapus unit ini", key=f"del_unit_{form_key}"):
        remove_unit(form_key, active)
        st.rerun()

    return active


def render_history_panel(form_key: str, limit: int = 20):
    """Tampilkan riwayat perubahan untuk unit aktif."""
    serial = get_active_serial(form_key)
    if not serial:
        st.info("Pilih unit untuk melihat riwayat.")
        return

    table = _form_table(form_key)
    _ensure_table(table)

    with _conn() as c:
        cur = c.execute(
            f"SELECT changed_at, tab_name, field_name, old_value, new_value, changed_by "
            f"FROM {table} WHERE no_sn=? ORDER BY changed_at DESC LIMIT ?",
            (serial, limit),
        )
        rows = cur.fetchall()

    st.markdown(
        f'<div class="siak-card-title" style="margin-top:14px;">'
        f'<i class="bi bi-clock-history"></i> Riwayat Perubahan Unit {serial}</div>',
        unsafe_allow_html=True,
    )

    if not rows:
        st.caption("Belum ada perubahan tersimpan untuk unit ini.")
        return

    # Tampilkan sebagai timeline ringkas
    for changed_at, tab_name, field_name, old_val, new_val, changed_by in rows:
        old_str = (old_val[:40] + "...") if old_val and len(old_val) > 40 else (old_val or "-")
        new_str = (new_val[:40] + "...") if new_val and len(new_val) > 40 else (new_val or "-")
        st.markdown(
            f'<div class="history-item">'
            f'<span class="history-time">{changed_at}</span> '
            f'<span class="history-tab">[{tab_name or "-"}]</span> '
            f'<b>{field_name}</b>: '
            f'<span class="history-old">{old_str}</span> → '
            f'<span class="history-new">{new_str}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def get_all_unit_states(form_key: str) -> dict:
    """Return {serial: state_dict} for all units."""
    return st.session_state.get(_SS_DATA.format(form_key), {})


def get_all_units_for_export(form_key: str, info: dict = None) -> list:
    """
    Return list of unit state dicts ready for PDF export.
    Merges info dict into each unit's 'info' key if provided.
    """
    states = get_all_unit_states(form_key)
    units = []
    for serial, state in states.items():
        unit = dict(state)
        if info:
            existing_info = unit.get("info", {})
            existing_info.update(info)
            unit["info"] = existing_info
        if "info" not in unit:
            unit["info"] = {"nomor_seri": serial}
        else:
            unit["info"].setdefault("nomor_seri", serial)
        units.append(unit)
    return units

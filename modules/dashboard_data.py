"""
modules/dashboard_data.py
===========================
Fungsi data untuk halaman "Dashboard" di app.py.

Dipanggil app.py sebagai: total_onepost(), total_phbtr(), total_pmcb(),
ambil_semua_onepost() (dan versi PHBTR/PMCB-nya). Semuanya membaca
langsung dari data/<form_type>_units.json lewat unit_manager — fungsi
yang sama persis dipakai tab Summary di masing-masing form dan oleh
build_..._pdf() saat export. Jadi angka di dashboard, isi PDF, dan tab
Summary selalu konsisten karena sumber datanya satu: file JSON di
folder data/.

Tidak ada query database terpisah, tidak ada cache basi — setiap kali
menu "dashboard" dibuka, fungsi-fungsi ini baca ulang file JSON saat
itu juga.
"""

from __future__ import annotations

import pandas as pd

from modules.unit_manager import get_all_units_for_export

# Nama key "catatan pengesahan" berbeda-beda per form (lihat form_xxx.py)
_CATATAN_KEY = {
    "onepost": "catatan_pengesahan_onepost",
    "phbtr": "catatan_phbtr",
    "pmcb": "catatan_pengesahan_pmcb",
}


def _status_of(unit: dict, form_type: str) -> str:
    """'Diterima' / 'Ditolak' / 'Belum diisi' — dinormalisasi karena tiap
    form kadang menulis 'Diterima', kadang 'diterima'."""
    catatan = unit.get(_CATATAN_KEY[form_type]) or {}
    hasil = str(catatan.get("hasil_pengujian", "")).strip().lower()
    if hasil == "diterima":
        return "Diterima"
    if hasil == "ditolak":
        return "Ditolak"
    return "Belum diisi"


# ── Total unit per form (dipakai untuk metric cards) ───────────────

def total_onepost() -> int:
    return len(get_all_units_for_export("onepost"))


def total_phbtr() -> int:
    return len(get_all_units_for_export("phbtr"))


def total_pmcb() -> int:
    return len(get_all_units_for_export("pmcb"))


# ── Tabel per form (dipakai untuk "Data Inspeksi Terbaru") ─────────
# Diurutkan ASCENDING (lama -> baru) supaya .tail(n) di app.py otomatis
# mengambil n unit yang PALING BARU diupdate.

def ambil_semua_onepost() -> pd.DataFrame:
    rows = []
    for unit in get_all_units_for_export("onepost"):
        info = unit.get("info", {}) or {}
        meta = unit.get("_meta", {}) or {}
        rows.append({
            "Nomor Seri": info.get("nomor_seri", "-"),
            "Nama Produk": info.get("nama_produk", "-"),
            "No AMP": info.get("no_amp", "-"),
            "Status": _status_of(unit, "onepost"),
            "Tab Terakhir": meta.get("last_tab", "-"),
            "Terakhir Diupdate": meta.get("last_updated", "-"),
        })
    cols = ["Nomor Seri", "Nama Produk", "No AMP", "Status", "Tab Terakhir", "Terakhir Diupdate"]
    df = pd.DataFrame(rows, columns=cols)
    return df.sort_values("Terakhir Diupdate") if not df.empty else df


def ambil_semua_phbtr() -> pd.DataFrame:
    rows = []
    for unit in get_all_units_for_export("phbtr"):
        info = unit.get("info", {}) or {}
        meta = unit.get("_meta", {}) or {}
        rows.append({
            "Nomor Seri": info.get("nomor_seri", "-"),
            "Jenis Panel": info.get("jenis_panel", "-"),
            "No AMP": info.get("no_amp", "-"),
            "Status": _status_of(unit, "phbtr"),
            "Tab Terakhir": meta.get("last_tab", "-"),
            "Terakhir Diupdate": meta.get("last_updated", "-"),
        })
    cols = ["Nomor Seri", "Jenis Panel", "No AMP", "Status", "Tab Terakhir", "Terakhir Diupdate"]
    df = pd.DataFrame(rows, columns=cols)
    return df.sort_values("Terakhir Diupdate") if not df.empty else df


def ambil_semua_pmcb() -> pd.DataFrame:
    rows = []
    for unit in get_all_units_for_export("pmcb"):
        info = unit.get("info", {}) or {}
        meta = unit.get("_meta", {}) or {}
        rows.append({
            "Serial VCB": info.get("serial_vcb", "-"),
            "Merk VCB": info.get("merk_vcb", "-"),
            "No AMP": info.get("no_amp", "-"),
            "Status": _status_of(unit, "pmcb"),
            "Tab Terakhir": meta.get("last_tab", "-"),
            "Terakhir Diupdate": meta.get("last_updated", "-"),
        })
    cols = ["Serial VCB", "Merk VCB", "No AMP", "Status", "Tab Terakhir", "Terakhir Diupdate"]
    df = pd.DataFrame(rows, columns=cols)
    return df.sort_values("Terakhir Diupdate") if not df.empty else df
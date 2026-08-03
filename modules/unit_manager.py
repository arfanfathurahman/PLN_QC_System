"""
modules/unit_manager.py
========================
Persistensi lokal untuk data per-unit (per nomor seri) pada form QC.

MASALAH YANG DISELESAIKAN:
st.session_state hanya hidup selama proses Streamlit berjalan. Begitu
app ditutup / server direstart / di-redeploy, semua isi session_state
hilang. File ini menambahkan lapisan penyimpanan ke disk supaya progres
setiap unit tetap ada walau Streamlit-nya mati.

DESAIN:
- Satu file JSON per jenis form: data/<form_type>_units.json
  contoh: data/onepost_units.json, data/phbtr_units.json, data/pmcb_units.json
- Struktur file:
    {
      "<nomor_seri>": {
          "info": {...},
          "visual_onepost": [...],
          "...": ...,
          "_meta": {"last_updated": "...", "last_tab": "..."}
      },
      ...
    }
- session_state dipakai sebagai CACHE di memori (supaya tidak baca file
  berulang setiap rerun Streamlit), tapi setiap autosave_unit() langsung
  ditulis ke disk (atomic write) — jadi walau app tiba-tiba ditutup,
  data yang sempat ter-autosave sebelumnya tetap aman.

CATATAN PENTING SOAL FOTO:
Jangan simpan bytes foto ke JSON ini (lambat & file jadi raksasa).
Pola yang benar sudah dipakai di tab Lampiran form_onepost.py: foto
disimpan sebagai file terpisah di folder uploads/..., dan yang masuk
ke sini hanya path-nya (string). Untuk PHBTR/PMCB, terapkan pola yang
sama (simpan ke uploads/<form_type>/<nomor_seri>/nama_file, lalu
autosave_unit(..., {"foto": [{"path": ..., "keterangan": ...}]})).

BATASAN:
Cocok untuk pemakaian lokal / single-operator (satu orang menjalankan
Streamlit di komputernya sendiri). Kalau nanti dipakai banyak orang
sekaligus mengakses instance yang sama, tulis-menulis file JSON ini
bisa tabrakan (race condition) — saat itu sebaiknya pindah ke SQLite
atau database beneran. Untuk kebutuhan sekarang (progres tidak hilang
saat app ditutup), pendekatan file JSON ini sudah cukup.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

UPLOADS_ROOT = Path(__file__).resolve().parent.parent / "uploads"


# ──────────────────────────────────────────────────────────────────
# Lapisan penyimpanan (disk)
# ──────────────────────────────────────────────────────────────────

def _store_path(form_type: str) -> Path:
    return DATA_DIR / f"{form_type}_units.json"


def _load_store(form_type: str) -> dict:
    path = _store_path(form_type)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # File kosong/korup — jangan sampai bikin app crash, mulai dari kosong.
        # (File lama otomatis tergantikan pada penyimpanan berikutnya.)
        return {}


def _save_store(form_type: str, store: dict) -> None:
    """Atomic write: tulis ke file sementara dulu, baru rename ke nama
    file asli. Ini mencegah file JSON rusak/setengah-tertulis kalau app
    mati tepat di tengah proses penyimpanan.

    Di Windows, os.replace() kadang gagal dengan
    'PermissionError: [WinError 5] Access is denied' kalau file tujuan
    sedang dikunci SESAAT oleh proses lain (paling sering: antivirus/
    Windows Defender yang otomatis men-scan file yang baru ditulis, atau
    folder project disinkron OneDrive/Dropbox). Lock semacam ini normalnya
    lepas dalam hitungan puluhan-ratusan milidetik, jadi di sini kita
    retry beberapa kali dengan jeda singkat sebelum menyerah."""
    path = _store_path(form_type)
    fd, tmp_path = tempfile.mkstemp(dir=str(DATA_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2, default=str)

        last_err = None
        for attempt in range(6):  # ~0+20+40+80+160+320 ms total
            try:
                os.replace(tmp_path, path)
                return
            except PermissionError as e:
                last_err = e
                time.sleep(0.02 * (2 ** attempt))

        # Fallback: rename tetap gagal (biasanya karena antivirus/OneDrive
        # masih memegang handle file tujuan). Tulis langsung ke file asli
        # sebagai upaya terakhir — sedikit kurang "atomic", tapi jauh lebih
        # baik daripada progres pengguna gagal tersimpan sama sekali.
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(store, f, ensure_ascii=False, indent=2, default=str)
        except Exception:
            raise last_err
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        raise


def _cache_key(form_type: str) -> str:
    return f"_unit_store_{form_type}"


def _active_key(form_type: str) -> str:
    return f"_active_serial_{form_type}"


def _get_store(form_type: str) -> dict:
    """Store di-cache di session_state supaya tidak baca disk tiap rerun,
    tapi isi cache-nya SELALU berasal dari file (dimuat sekali per sesi
    lewat init_units)."""
    ck = _cache_key(form_type)
    if ck not in st.session_state:
        st.session_state[ck] = _load_store(form_type)
    return st.session_state[ck]


# ──────────────────────────────────────────────────────────────────
# Public API — dipakai oleh form_onepost.py / form_phbtr.py / form_pmcb.py
# ──────────────────────────────────────────────────────────────────

def init_units(form_type: str) -> None:
    """Panggil di awal setiap form_xxx(). Memuat data tersimpan dari disk
    (sekali per sesi browser) dan menyiapkan unit aktif default."""
    store = _get_store(form_type)
    ak = _active_key(form_type)
    if ak not in st.session_state:
        existing = sorted(store.keys())
        st.session_state[ak] = existing[0] if existing else ""


def render_unit_selector(form_type: str) -> None:
    """UI untuk memilih unit (nomor seri) yang sedang dikerjakan, atau
    membuat unit baru. Setiap unit disimpan terpisah di disk sehingga
    berpindah-pindah unit tidak menghapus progres unit lain."""
    store = _get_store(form_type)
    ak = _active_key(form_type)
    existing = sorted(store.keys())

    NEW_LABEL = "➕ Buat unit / nomor seri baru"
    c1, c2 = st.columns([3, 2])
    with c1:
        options = existing + [NEW_LABEL]
        current = st.session_state.get(ak, "")
        idx = options.index(current) if current in existing else len(options) - 1
        choice = st.selectbox(
            "Unit aktif (nomor seri)", options, index=idx, key=f"_selector_{form_type}"
        )
    with c2:
        if choice == NEW_LABEL:
            new_serial = st.text_input("Nomor seri baru", key=f"_new_serial_{form_type}")
            if new_serial:
                st.session_state[ak] = new_serial
                if new_serial not in store:
                    store[new_serial] = {}
                    _save_store(form_type, store)
        else:
            st.session_state[ak] = choice

    active = st.session_state.get(ak, "")
    if active:
        meta = store.get(active, {}).get("_meta", {})
        last_saved = meta.get("last_updated")
        if last_saved:
            st.caption(f"📌 Unit aktif: **{active}** — terakhir tersimpan {last_saved}")
        else:
            st.caption(f"📌 Unit aktif: **{active}** (belum ada data tersimpan)")


def get_active_serial(form_type: str) -> str:
    return st.session_state.get(_active_key(form_type), "")


def get_active_unit_state(form_type: str) -> dict:
    """Ambil seluruh data unit yang sedang aktif (semua key yang pernah
    di-autosave), langsung dari store yang sudah dimuat dari disk."""
    serial = get_active_serial(form_type)
    store = _get_store(form_type)
    return store.get(serial, {})


def autosave_unit(form_type: str, key: str, data, tab_name: Optional[str] = None) -> None:
    """Simpan `data` di bawah `key` untuk unit yang sedang aktif, dan
    LANGSUNG tulis ke disk (bukan cuma session_state) supaya tidak
    hilang walau Streamlit ditutup sebelum sempat export PDF."""
    serial = get_active_serial(form_type)
    if not serial:
        return
    store = _get_store(form_type)
    unit = store.setdefault(serial, {})
    unit[key] = data
    unit["_meta"] = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_tab": tab_name or key,
    }
    _save_store(form_type, store)


def delete_unit(form_type: str, serial: str) -> bool:
    """Hapus permanen satu unit/project: data JSON-nya (semua tab yang
    pernah di-autosave) DAN folder foto lampirannya di disk
    (uploads/<form_type>/<serial>/...), kalau ada.

    Kalau unit ini yang sedang aktif, unit aktif otomatis dikosongkan
    (form_xxx() akan menampilkan pilihan unit lain / buat baru di
    render_unit_selector berikutnya).

    Return True kalau serial ditemukan & berhasil dihapus dari store,
    False kalau serial kosong atau memang tidak ada di store (tidak ada
    apa-apa untuk dihapus).
    """
    if not serial:
        return False
    store = _get_store(form_type)
    if serial not in store:
        return False

    store.pop(serial, None)
    _save_store(form_type, store)

    if get_active_serial(form_type) == serial:
        st.session_state[_active_key(form_type)] = ""

    # Bersihkan folder foto lampiran unit ini kalau ada. Kegagalan di sini
    # (mis. file lagi dikunci proses lain) TIDAK dianggap fatal — data
    # JSON-nya sudah pasti terhapus di atas, itu yang paling penting.
    unit_uploads_dir = UPLOADS_ROOT / form_type / serial
    if unit_uploads_dir.exists():
        try:
            shutil.rmtree(unit_uploads_dir)
        except OSError:
            pass

    return True


def get_all_units_for_export(form_type: str) -> list:
    """Kembalikan semua unit tersimpan (dari disk) sebagai list dict,
    siap dipakai oleh build_onepost_pdf() / build_phbtr_pdf() / build_pmcb_pdf()."""
    store = _get_store(form_type)
    return list(store.values())


def render_history_panel(form_type: str) -> None:
    """Tabel riwayat unit tersimpan + opsi hapus satu unit."""
    store = _get_store(form_type)
    if not store:
        st.caption("Belum ada unit tersimpan di penyimpanan lokal.")
        return

    st.markdown("#### 🗂 Riwayat unit tersimpan (lokal)")
    rows = []
    for serial, unit in store.items():
        meta = unit.get("_meta", {})
        rows.append({
            "Nomor Seri": serial,
            "Terakhir disimpan": meta.get("last_updated", "-"),
            "Tab terakhir diedit": meta.get("last_tab", "-"),
            "Jumlah bagian terisi": len([k for k in unit.keys() if k != "_meta"]),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(f"📁 Disimpan di: `{_store_path(form_type)}`")

    del_serial = st.selectbox(
        "Hapus unit tersimpan (opsional)",
        [""] + sorted(store.keys()),
        key=f"_delete_select_{form_type}",
    )
    if del_serial:
        confirm = st.checkbox(
            f"Saya yakin ingin menghapus permanen unit '{del_serial}'",
            key=f"_delete_confirm_{form_type}",
        )
        if confirm and st.button(f"🗑 Hapus unit {del_serial}", key=f"_delete_btn_{form_type}"):
            delete_unit(form_type, del_serial)
            st.rerun()
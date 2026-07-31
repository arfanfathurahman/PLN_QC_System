"""
utils/validasi.py
==================
Validasi otomatis + penandaan visual (merah/hijau) untuk nilai hasil ukur
yang berada di luar batas standar — misalnya nilai tarik skun kabel (N),
tahanan isolasi/dielektrik (MΩ), ketebalan coating (μm), tahanan kontinuitas
sirkit protektif (Ω), dsb.

PENTING soal angka batas (THRESHOLDS di bawah):
Beberapa batas sudah eksplisit tertulis di form asli (mis. coating min 80 μm,
sirkit protektif maks 0,1 Ω). Untuk parameter yang di form aslinya masih
berupa isian bebas (mis. batas MΩ dielektrik PHBTR, karena SOP/SPLN yang
dipakai belum saya ketahui pasti), saya beri nilai default yang lazim dipakai
sebagai SANGAT SEMENTARA — WAJIB disesuaikan dengan SOP/SPLN resmi PLN
Pusharlis yang digunakan sebelum dipakai produksi. Cukup ubah angkanya di
dict THRESHOLDS, tidak perlu ubah kode lain.
"""

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# BATAS STANDAR — SESUAIKAN DENGAN SOP / SPLN RESMI SEBELUM DIPAKAI PRODUKSI
# ----------------------------------------------------------------------
THRESHOLDS = {
    "onepost": {
        # gaya tarik skun (N) sudah dibandingkan ke kolom "standar" per baris
        # di form (nilai standar bisa berbeda tiap ukuran kabel), jadi tidak
        # perlu angka tetap di sini.
        "coating_min_um": 80,
    },
    "pmcb": {
        "coating_min_um": 80,
        # toleransi keserempakan antar phasa tahanan kontak: ±20%
        "tahanan_kontak_toleransi_persen": 20,
    },
    "phbtr": {
        # DEFAULT SEMENTARA — ganti sesuai SPLN/SOP resmi yang dipakai.
        "dielektrik_min_mohm": 2.0,
        "sirkit_maks_ohm": 0.1,
        "coating_min_um": 80,
        "baut_toleransi_persen": 10,
    },
}


# ----------------------------------------------------------------------
# HELPER TAMPILAN (badge merah / hijau inline)
# ----------------------------------------------------------------------
def render_flag(value, ok: bool, unit: str = "", label: str = "") -> None:
    """
    Tampilkan satu nilai dengan badge warna: hijau jika ok, MERAH jika di
    luar batas. Dipakai menempel di sebelah st.number_input / st.write yang
    sudah ada, tanpa mengubah struktur kolom form.
    """
    color = "#1a7f37" if ok else "#c92a2a"
    bg = "#e6f4ea" if ok else "#fde8e8"
    icon = "✅" if ok else "🔴"
    text = f"{label + ': ' if label else ''}{value}{(' ' + unit) if unit else ''}"

    st.markdown(
        f"""
        <div style="
            background-color:{bg};
            color:{color};
            border:1px solid {color};
            border-radius:6px;
            padding:2px 8px;
            font-weight:600;
            font-size:0.85rem;
            display:inline-block;
            margin-top:2px;">
            {icon} {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def flag_number_input(
    label: str,
    value: float,
    minimum: float | None = None,
    maximum: float | None = None,
    unit: str = "",
    step: float = 0.1,
    key: str | None = None,
) -> tuple[float, bool]:
    """
    Gabungan st.number_input + badge merah/hijau otomatis berdasarkan
    batas minimum/maximum. Mengembalikan (nilai_input, status_ok).
    Gunakan ini untuk mengganti st.number_input polos pada parameter kritis
    (dielektrik, tarik skun, coating, dll) agar nilai di luar batas langsung
    tertandai merah tanpa perlu logika tambahan di form.
    """
    hasil = st.number_input(label, value=float(value), step=step, key=key)

    ok = True
    if minimum is not None and hasil < minimum:
        ok = False
    if maximum is not None and hasil > maximum:
        ok = False

    batas_text = ""
    if minimum is not None and maximum is not None:
        batas_text = f"(batas: {minimum}–{maximum} {unit})"
    elif minimum is not None:
        batas_text = f"(min: {minimum} {unit})"
    elif maximum is not None:
        batas_text = f"(maks: {maximum} {unit})"

    render_flag(f"{hasil} {unit}".strip(), ok, label=batas_text)

    return hasil, ok


def style_out_of_range(
    df: pd.DataFrame, status_col: str, ok_values=("✓", "Accepted", True, "Sesuai", "Baik")
):
    """
    Kembalikan pandas Styler yang mewarnai MERAH baris-baris di mana
    status_col TIDAK termasuk ok_values — dipakai untuk st.dataframe agar
    hasil di luar batas langsung terlihat merah di tabel rekap.
    """
    def _highlight(row):
        is_ok = row[status_col] in ok_values
        color = "" if is_ok else "background-color:#fde8e8;color:#c92a2a;font-weight:600;"
        return [color] * len(row)

    return df.style.apply(_highlight, axis=1)


def badge_html(ok: bool, text_ok: str = "Sesuai", text_bad: str = "Tidak Sesuai") -> str:
    """String HTML badge kecil, untuk dipakai inline di st.markdown lain."""
    if ok:
        return (
            f'<span style="background:#e6f4ea;color:#1a7f37;border-radius:4px;'
            f'padding:1px 6px;font-size:0.8rem;">✅ {text_ok}</span>'
        )
    return (
        f'<span style="background:#fde8e8;color:#c92a2a;border-radius:4px;'
        f'padding:1px 6px;font-size:0.8rem;font-weight:700;">🔴 {text_bad}</span>'
    )
"""
Tema visual bersama untuk seluruh form QC PLN Pusharlis.
Dipakai oleh: form_onepost, form_phbtr, form_pmcb.

Palet warna PLN:
  - primary deep   : #1B5E6E
  - primary mid    : #14A8BE
  - primary dark   : #14495A
  - accent yellow  : #EAE83A
  - light cyan bg  : #E3F6FB
  - text slate     : #1E293B / #334155 / #64748B
  - surface white  : #FFFFFF
  - border         : #E2E8F0
"""

import streamlit as st

# ======================================================================
# PALET WARNA (konstanta tunggal sumber kebenaran)
# ======================================================================
PRIMARY_DEEP = "#1B5E6E"
PRIMARY_MID = "#14A8BE"
PRIMARY_DARK = "#14495A"
ACCENT_YELLOW = "#EAE83A"
ACCENT_YELLOW_DARK = "#D4D226"
LIGHT_CYAN = "#E3F6FB"
TEXT_DARK = "#1E293B"
TEXT_BODY = "#334155"
TEXT_MUTED = "#64748B"
SURFACE = "#FFFFFF"
BORDER = "#E2E8F0"
BG_APP = "#F8FAFC"
SUCCESS = "#16A34A"
WARNING = "#F59E0B"
ERROR = "#DC2626"

# ======================================================================
# INJECT CSS TEMA FORM
# ======================================================================
THEME_CSS = f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
<style>
    /* ---------- DASAR ---------- */
    .bi {{ vertical-align: -2px; margin-right: 6px; }}

    .stApp {{ background-color: {BG_APP}; }}

    /* ---------- JUDUL FORM ---------- */
    .form-title {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;
        font-weight: 800;
        color: {TEXT_DARK};
        margin: 0 0 4px 0;
        line-height: 1.2;

        padding:22px 24px;
        margin-bottom:20px;

        box-shadow:0 8px 20px rgba(15,23,42,.08);

        font-size:22px;
        font-weight:800;
        color:#1E293B;
        background: linear-gradient(
            135deg,
            #FFFDF2 0%,
            #FFF8D8 70%,
            #FFF4A8 100%
        );

        border:1px solid #EAE83A;

        color:#1E293B;
       
    }}
    .form-title .icon-wrap {{
        background: linear-gradient(135deg, {PRIMARY_DEEP} 0%, {PRIMARY_MID} 100%);
        color: #FFFFFF;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(20, 168, 190, 0.30);
    }}
    .form-subtitle {{
        font-size: 13px;
        color: {TEXT_MUTED};
        font-weight: 500;
        margin: 0 0 18px 0;
    }}

    /* ---------- SECTION TAG ---------- */
    .section-tag {{
        background: {LIGHT_CYAN};
        color: {PRIMARY_MID};
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ---------- INFO CARD ---------- */
    .info-card {{
        display: flex;
                align-items: center;
                gap: 12px;
                font-size: 22px;
                font-weight: 800;
                color: {TEXT_DARK};
                margin: 0 0 4px 0;
                line-height: 1.2;
        
                padding:22px 24px;
                margin-bottom:20px;
        
                box-shadow:0 8px 20px rgba(15,23,42,.08);
        
                font-size:22px;
                font-weight:800;
                color:#1E293B;
                background: linear-gradient(
                    135deg,
                    #FFFDF2 0%,
                    #FFF8D8 70%,
                    #FFF4A8 100%
                );
        
                border:1px solid #EAE83A;
        
                color:#1E293B;
    }}
    .info-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .info-table {{ width: 100%; border-collapse: collapse; }}
    .info-table td {{
        padding: 9px 12px;
        border-bottom: 1px solid #F1F5F9;
        font-size: 13px;
    }}
    .info-table td.label {{
        color: {TEXT_MUTED};
        width: 190px;
        font-weight: 500;
    }}
    .info-table td.value {{
        color: {TEXT_DARK};
        font-weight: 600;
    }}
    -------- PANEL CARD (wrapper tiap tab) ---------- */
    /* Latar kontras: gradasi teal lembut, bukan putih */
    .siak-card {{
        background: linear-gradient(160deg, #EAF6F9 0%, #D7EEF3 100%);
        border: 1px solid #BFE3EC;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 2px 6px rgba(20, 73, 90, 0.08);
        margin-bottom: 20px;
    }}

    .siak-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: {PRIMARY_DEEP};
        margin: 0 0 14px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* inner putih untuk input agar kontras dengan latar teal */
    .siak-card .stTextInput > div > div,
    .siak-card .stNumberInput > div > div,
    .siak-card .stSelectbox > div > div,
    .siak-card .stTextArea > div > div {{
        background-color: {SURFACE} !important;
    }}

    /* ---------- HEADER TABEL MANUAL (st.columns) ---------- */
    .col-hdr {{
        font-size: 12.5px;
        font-weight: 700;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.3px;
        padding-bottom: 6px;
    }}

    /* ---------- ROW ITEM ---------- */
    .row-label {{
        font-size: 13.5px;
        color: {TEXT_BODY};
        font-weight: 500;
        padding-top: 6px;
    }}
    .row-sublabel {{
        font-size: 12px;
        color: {TEXT_MUTED};
        font-weight: 500;
    }}
    .row-no {{
        font-size: 13px;
        color: {PRIMARY_MID};
        font-weight: 700;
        text-align: center;
        padding-top: 6px;
    }}

    /* ---------- STATUS BADGE ---------- */
    .badge {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        white-space: nowrap;
    }}
    .badge-ok {{
        background: #DCFCE7;
        color: #15803D;
    }}
    .badge-warn {{
        background: #FEF3C7;
        color: #B45309;
    }}
    .badge-bad {{
        background: #FEE2E2;
        color: #B91C1C;
    }}

    /* ---------- PROGRESS / METRIC WRAP ---------- */
    .metric-wrap {{
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}

    /* ---------- BANNER HASIL AKHIR ---------- */
    .result-banner {{
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 12px;
        font-weight: 700;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .result-pass {{ background: #DCFCE7; color: #15803D; }}
    .result-review {{ background: #FEF3C7; color: #B45309; }}
    .result-fail {{ background: #FEE2E2; color: #B91C1C; }}

    /* ---------- DIVIDER TIPIS ---------- */
    .thin-divider {{
        height: 1px;
        background: {BORDER};
        margin: 14px 0;
        border: none;
    }}

    /* ---------- KOLOM INPUT GROUP ---------- */
    .field-group-title {{
        font-size: 13px;
        font-weight: 700;
        color: {PRIMARY_DEEP};
        margin: 0 0 4px 0;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}

    /* ---------- VALIDATION STRIP (validasi otomatis) ---------- */
    .validation-strip {{
        display: flex;
        align-items: center;
        gap: 14px;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .vs-pass {{ background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%); border: 1px solid #86EFAC; }}
    .vs-review {{ background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%); border: 1px solid #FCD34D; }}
    .vs-fail {{ background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); border: 1px solid #FCA5A5; }}
    .vs-icon {{
        width: 44px; height: 44px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; color: #FFFFFF; flex-shrink: 0;
    }}
    .vs-pass .vs-icon {{ background: {SUCCESS}; }}
    .vs-review .vs-icon {{ background: {WARNING}; }}
    .vs-fail .vs-icon {{ background: {ERROR}; }}
    .vs-body {{ flex: 1; }}
    .vs-title {{ font-size: 14px; font-weight: 800; color: {TEXT_DARK}; }}
    .vs-msg {{ font-size: 12.5px; font-weight: 600; color: {TEXT_BODY}; margin-top: 2px; }}
    .vs-score {{ font-size: 26px; font-weight: 900; color: {TEXT_DARK}; }}

    /* ---------- DETAIL VALIDASI (bar per item) ---------- */
    .validation-detail {{ margin-top: 8px; }}
    .val-row {{
        display: flex; align-items: center; gap: 10px;
        padding: 8px 10px; border-radius: 8px; margin-bottom: 6px;
        background: {SURFACE}; border: 1px solid {BORDER};
    }}
    .val-name {{ flex: 2; font-size: 12.5px; font-weight: 600; color: {TEXT_DARK}; }}
    .val-bar {{ flex: 3; height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden; }}
    .val-bar-fill {{ height: 100%; background: linear-gradient(90deg, {PRIMARY_MID}, {PRIMARY_DEEP}); border-radius: 4px; }}
    .val-count {{ flex: 1; font-size: 12px; font-weight: 700; color: {TEXT_MUTED}; text-align: center; }}
    .val-persen {{ flex: 1; font-size: 13px; font-weight: 800; color: {PRIMARY_DEEP}; text-align: right; }}

    /* ---------- STATUS STRIP KECIL ---------- */
    .status-pill {{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 20px;
    }}
    .pill-pass {{ background: #DCFCE7; color: #15803D; }}
    .pill-review {{ background: #FEF3C7; color: #B45309; }}
    .pill-fail {{ background: #FEE2E2; color: #B91C1C; }}

    /* ---------- AUTOSAVE INDICATOR ---------- */
    .autosave-indicator {{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 11px; font-weight: 600; color: {PRIMARY_DEEP};
        background: {LIGHT_CYAN}; padding: 4px 10px; border-radius: 6px;
    }}
    .autosave-dot {{ width: 8px; height: 8px; border-radius: 50%; background: {SUCCESS}; animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}

    /* ---------- HISTORY TIMELINE ---------- */
    .history-item {{
        font-size: 12px;
        padding: 6px 10px;
        background: {SURFACE};
        border: 1px solid {BORDER};
        border-left: 3px solid {PRIMARY_MID};
        border-radius: 6px;
        margin-bottom: 4px;
        color: {TEXT_BODY};
    }}
    .history-time {{ color: {TEXT_MUTED}; font-weight: 600; font-size: 11px; }}
    .history-tab {{ color: {PRIMARY_MID}; font-weight: 700; }}
    .history-old {{ color: #B91C1C; text-decoration: line-through; }}
    .history-new {{ color: #15803D; font-weight: 600; }}
    .header-card{{
        display:flex;
        align-items:center;
        gap:18px;
    
        padding:22px 24px;
        margin-bottom:22px;
    
        background:linear-gradient(
            135deg,
            #FFFDF2 0%,
            #FFF8D8 70%,
            #FFF4A8 100%
        );
    
        border:1px solid #EAE83A;
        border-radius:18px;
    
        box-shadow:0 8px 20px rgba(15,23,42,.08);
    }}
    
    .header-icon{{
        width:60px;
        height:60px;
    
        display:flex;
        justify-content:center;
        align-items:center;
    
        border-radius:14px;
    
        background:linear-gradient(
            135deg,
            #1B5E6E,
            #14A8BE
        );
    
        color:white;
        font-size:28px;
    
        box-shadow:0 6px 16px rgba(20,168,190,.30);
    }}
    
    .header-title{{
        font-size:28px;
        font-weight:900;
        color:#1E293B;
    }}
    
    .header-subtitle{{
        margin-top:5px;
        font-size:15px;
        color:#64748B;
    }}
    
</style>
"""
    
def apply_form_theme():
    """Inject CSS tema PLN. Panggil sekali di awal tiap form."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


# ======================================================================
# KOMPONEN UI BERPREDIKAT (helper yang dipakai berulang di form)
# ======================================================================
def form_header(icon: str, title: str, subtitle: str):
    """Banner judul form dengan ikon kotak bergradien."""
    st.markdown(
        f"""
        <div class="form-title">
            <div class="icon-wrap"><i class="bi bi-{icon}"></i></div>
            <div>
                <div>{title}</div>
                <div class="form-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_tag(text: str):
    """Label kecil di atas sebuah blok pemeriksaan."""
    st.markdown(
        f'<span class="section-tag">{text}</span>', unsafe_allow_html=True
    )


def card_begin(extra_class: str = ""):
    """Buka div .siak-card. Pasangkan dengan card_end()."""
    st.markdown(f'<div class="siak-card {extra_class}">', unsafe_allow_html=True)


def card_end():
    """Tutup div .siak-card."""
    st.markdown("</div>", unsafe_allow_html=True)


def col_header(text: str):
    """Header kolom tabel manual (st.columns). Panggil di dalam `with col:` atau via table_headers()."""
    st.markdown(f'<div class="col-hdr">{text}</div>', unsafe_allow_html=True)


def table_headers(cols, labels: list):
    """
    Tulis header tabel dengan benar di setiap kolom.
    cols  : list kolom dari st.columns(...)
    labels: list teks header, urut sesuai cols
    Contoh: table_headers(st.columns([1,3,2]), ["No", "Item", "Status"])
    """
    for col, label in zip(cols, labels):
        with col:
            col_header(label)


def row_no(n):
    """Nomor baris terpusat."""
    st.markdown(f'<div class="row-no">{n}</div>', unsafe_allow_html=True)


def row_label(text: str, sub: str = ""):
    """Label baris (dengan sub-label opsional)."""
    if sub:
        st.markdown(
            f'<div class="row-label">{text}</div>'
            f'<div class="row-sublabel">{sub}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div class="row-label">{text}</div>', unsafe_allow_html=True)


def badge(text: str, kind: str = "ok"):
    """Badge status: ok / warn / bad."""
    st.markdown(
        f'<span class="badge badge-{kind}">{text}</span>',
        unsafe_allow_html=True,
    )


def thin_divider():
    """Pemisah tipis antar blok."""
    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)


def progress_summary(total: int, sesuai: int, label_total="Total", label_ok="Sesuai"):
    """Tampilkan progress bar + 3 metric card di akhir tiap tab pemeriksaan."""
    persen = (sesuai / total * 100) if total else 0.0
    st.progress(persen / 100)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label_total, total)
    with m2:
        st.metric(label_ok, sesuai)
    with m3:
        st.metric("Persentase", f"{persen:.0f}%")
    return persen


def result_status(persen: float, pass_msg: str, review_msg: str = None, fail_msg: str = None):
    """Banner hasil akhir tab: pass / review / fail."""
    if persen == 100:
        kind, msg = "pass", pass_msg
    elif persen >= 90 and review_msg:
        kind, msg = "review", review_msg
    else:
        kind, msg = "fail", fail_msg or review_msg or pass_msg
    icon = {"pass": "check-circle-fill", "review": "exclamation-triangle-fill", "fail": "x-circle-fill"}[kind]
    st.markdown(
        f'<div class="result-banner result-{kind}">'
        f'<i class="bi bi-{icon}"></i> {msg}'
        f"</div>",
        unsafe_allow_html=True,
    )


def qc_score_card(total_pemeriksaan: int, nilai_akhir: float):
    """3 metric card di summary: total / QC score / status akhir."""
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Pemeriksaan", total_pemeriksaan)
    with c2:
        st.metric("QC Score", f"{nilai_akhir:.1f}%")
    with c3:
        if nilai_akhir == 100:
            status_akhir = "🟢 PASS"
        elif nilai_akhir >= 90:
            status_akhir = "🟡 REVIEW"
        else:
            status_akhir = "🔴 FAIL"
        st.metric("Status Akhir", status_akhir)
    st.progress(nilai_akhir / 100)


def autosave_indicator(active: bool = True):
    """Indikator kecil 'Autosave aktif' dengan titik berdenyut."""
    if active:
        st.markdown(
            '<span class="autosave-indicator">'
            '<span class="autosave-dot"></span> Autosave aktif</span>',
            unsafe_allow_html=True,
        )


def status_pill(label: str, kind: str = "pass"):
    """Pill status kecil: pass / review / fail."""
    st.markdown(
        f'<span class="status-pill pill-{kind}">{label}</span>',
        unsafe_allow_html=True,
    )

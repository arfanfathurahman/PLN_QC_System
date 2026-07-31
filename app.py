# ===========================================
# 1. IMPORT LIBRARY
# ===========================================
import os
import glob
import time
import base64
import json
import zipfile
from io import BytesIO
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

# Import modul lokal
from modules.form_onepost import form_onepost
from modules.form_phbtr import form_phbtr
from modules.form_pmcb import form_pmcb 

# Import fungsi database & utils
from database import (
    init_db,
    simpan_onepost,
    ambil_onepost,
    simpan_onepost_log,
    ambil_onepost_by_mode,
    ambil_onepost_by_sn,
    ambil_semua_onepost,
    simpan_phbtr,
    ambil_phbtr,
    simpan_phbtr_draft,      
    ambil_semua_phbtr_draft,
    simpan_pmcb,
    ambil_pmcb,
    total_onepost,
    total_phbtr,
    total_pmcb
)
from utils import (
    convert_df_to_excel,
    export_onepost_excel,
    generate_phbtr_pdf
)

# ===========================================
# 2. PAGE CONFIGURATION
# ===========================================
page_icon_path = "logo_pln.png" if os.path.exists("logo_pln.png") else "⚡"

st.set_page_config(
    page_title="PLN QC System - Pusharlis",
    page_icon=page_icon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi DB
init_db()

# Inisialisasi Session State Data Pengujian OnePost
if 'discharging_data' not in st.session_state:
    st.session_state.discharging_data = pd.DataFrame([
        {"No": "-", "Waktu": "08.00 (start)", "Voltage (V)": 53.50, "Ampere (A)": 46.19, "SOC (%)": 100.0, "Suhu (°C)": 25, "Vavg (V)": 230.0, "Iavg (A)": 9.53},
        {"No": 1, "Waktu": "08.30", "Voltage (V)": 52.80, "Ampere (A)": 45.10, "SOC (%)": 92.0, "Suhu (°C)": 26, "Vavg (V)": 230.0, "Iavg (A)": 9.45},
        {"No": 2, "Waktu": "09.00", "Voltage (V)": 52.40, "Ampere (A)": 44.80, "SOC (%)": 84.0, "Suhu (°C)": 27, "Vavg (V)": 229.5, "Iavg (A)": 9.40},
        {"No": 3, "Waktu": "10.00", "Voltage (V)": 51.90, "Ampere (A)": 44.50, "SOC (%)": 68.0, "Suhu (°C)": 29, "Vavg (V)": 229.0, "Iavg (A)": 9.35},
        {"No": 4, "Waktu": "12.00", "Voltage (V)": 50.80, "Ampere (A)": 43.80, "SOC (%)": 42.0, "Suhu (°C)": 32, "Vavg (V)": 228.0, "Iavg (A)": 9.20},
        {"No": 5, "Waktu": "14.00", "Voltage (V)": 49.50, "Ampere (A)": 43.00, "SOC (%)": 20.0, "Suhu (°C)": 34, "Vavg (V)": 226.5, "Iavg (A)": 9.10},
        {"No": 6, "Waktu": "16.00 (stop)", "Voltage (V)": 48.00, "Ampere (A)": 42.00, "SOC (%)": 5.0, "Suhu (°C)": 35, "Vavg (V)": 224.0, "Iavg (A)": 8.90},
    ])

if 'charging_grid_data' not in st.session_state:
    st.session_state.charging_grid_data = pd.DataFrame([
        {"No": "-", "Waktu": "17.00 (start)", "Voltage (V)": 48.00, "Ampere (A)": -36.99, "SOC (%)": 5.0, "Suhu (°C)": 33, "Vavg (V)": 210.0, "Iavg (A)": 10.2},
        {"No": 1, "Waktu": "18.00", "Voltage (V)": 50.50, "Ampere (A)": -37.20, "SOC (%)": 30.0, "Suhu (°C)": 31, "Vavg (V)": 211.5, "Iavg (A)": 10.1},
        {"No": 2, "Waktu": "20.00", "Voltage (V)": 52.80, "Ampere (A)": -37.00, "SOC (%)": 75.0, "Suhu (°C)": 28, "Vavg (V)": 212.0, "Iavg (A)": 10.0},
        {"No": 3, "Waktu": "22.00 (full)", "Voltage (V)": 54.00, "Ampere (A)": -2.00, "SOC (%)": 100.0, "Suhu (°C)": 26, "Vavg (V)": 215.0, "Iavg (A)": 0.5},
    ])

if 'charging_pv_data' not in st.session_state:
    st.session_state.charging_pv_data = pd.DataFrame([
        {"No": "-", "Waktu": "09.00 (start)", "Voltage (V)": 50.00, "Ampere (A)": 15.00, "SOC (%)": 15.0, "Suhu (°C)": 25, "Vavg (V)": 315.0, "Iavg (A)": 3.50},
        {"No": 1, "Waktu": "11.00", "Voltage (V)": 52.10, "Ampere (A)": 25.00, "SOC (%)": 50.0, "Suhu (°C)": 28, "Vavg (V)": 322.0, "Iavg (A)": 5.10},
        {"No": 2, "Waktu": "13.00", "Voltage (V)": 53.50, "Ampere (A)": 24.50, "SOC (%)": 85.0, "Suhu (°C)": 29, "Vavg (V)": 320.0, "Iavg (A)": 5.00},
        {"No": 3, "Waktu": "15.00 (full)", "Voltage (V)": 54.20, "Ampere (A)": 2.10, "SOC (%)": 100.0, "Suhu (°C)": 27, "Vavg (V)": 318.0, "Iavg (A)": 0.40},
    ])

# ===========================================
# 3. FUNGSI LOGO & BACKGROUND BASE64
# ===========================================
def get_image_base64(keywords):
    files = glob.glob("*") + glob.glob("assets/*")
    for file_path in files:
        file_lower = file_path.lower()
        for kw in keywords:
            if kw.lower() in file_lower and any(file_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                try:
                    with open(file_path, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception:
                    continue
    return ""

logo_pln_b64 = get_image_base64(["logo_pln", "logo", "pln"])
bg_pusharlis_b64 = get_image_base64(["pusharlis", "gedung", "bg", "background", "kantor", "pabrik"])

bg_image_style = f"data:image/jpeg;base64,{bg_pusharlis_b64}" if bg_pusharlis_b64 else "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1600&q=80"

# ===========================================
# 4. CUSTOM STYLING (MODERN SIDEBAR & BANNER - PALET WARNA PLN)
# ===========================================
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
    .bi {{
        vertical-align: -2px;
        margin-right: 6px;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1B5E6E 0%, #14495A 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #E2E8F0 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }}

    .user-profile-box {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-top: 10px;
        margin-bottom: 20px;
    }}

    .user-avatar {{
        background: linear-gradient(135deg, #14A8BE 0%, #0E8497 100%);
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }}

    .sidebar-menu-title {{
        font-size: 11px;
        font-weight: 700;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
        margin-bottom: 8px;
        padding-left: 8px;
    }}

    [data-testid="stSidebar"] div.stButton > button {{
        background-color: transparent !important;
        color: #94A3B8 !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        padding: 11px 16px !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.25s ease-in-out !important;
    }}

    [data-testid="stSidebar"] div.stButton > button:hover {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        transform: translateX(4px);
    }}

    .stApp {{
        background-color: #F8FAFC;
    }}

    .hero-banner {{
        width: 100%;
        min-height: 200px;
        background: linear-gradient(
            90deg, 
            rgba(27, 94, 110, 0.80) 0%, 
            rgba(20, 168, 190, 0.55) 50%, 
            rgba(27, 94, 110, 0.75) 100%
        ), url('{bg_image_style}');
        background-size: cover;
        background-position: center 65%; 
        background-repeat: no-repeat;
        border-radius: 14px;
        padding: 28px 32px;
        color: #FFFFFF;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .banner-left {{
        display: flex;
        align-items: center;
        gap: 20px;
    }}

    .logo-box {{
        background-color: #FFFFFF;
        width: 85px;
        height: 85px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 6px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
        flex-shrink: 0;
    }}

    .logo-box img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }}

    .banner-title {{
        font-size: 26px;
        font-weight: 900;
        color: #FFFFFF;
        margin: 0 0 4px 0;
        line-height: 1.1;
    }}

    .banner-subtitle {{
        font-size: 13px;
        color: #E2E8F0;
        margin: 0;
        font-weight: 500;
    }}

    .info-card {{
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .info-card-title {{
        font-size: 15px;
        font-weight: 700;
        color: #14A8BE;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .info-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .info-table td {{
        padding: 9px 12px;
        border-bottom: 1px solid #F1F5F9;
        font-size: 13px;
    }}
    .info-table td.label {{
        color: #64748B;
        width: 190px;
        font-weight: 500;
    }}
    .info-table td.value {{
        color: #1E293B;
        font-weight: 600;
    }}

    .siak-card {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}
    .section-tag {{
        background: #E3F6FB;
        color: #14A8BE;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
    }}
</style>
""", unsafe_allow_html=True)

# ===========================================
# 5. SESSION STATE MANAGEMENT
# ===========================================
if "menu" not in st.session_state:
    st.session_state.menu = "beranda"

# Daftar menu: key internal <-> label tampilan <-> ikon Bootstrap (satu tema, outline)
MENU_KEYS   = ["beranda", "dashboard", "onepost", "phbtr", "pmcb"]
MENU_LABELS = ["Beranda (Profil)", "Dashboard (Summary)", "Pengujian OnePost", "Pengujian PHB TR", "Pengujian PMCB"]
MENU_ICONS  = ["house-door", "speedometer2", "tools", "lightning-charge", "shield-check"]

def navigate(target_key: str):
    """Pindah halaman + reset state widget sidebar agar ikut sinkron."""
    st.session_state.menu = target_key
    if "sidebar_menu" in st.session_state:
        del st.session_state["sidebar_menu"]
    st.rerun()

# ===========================================
# 6. SIDEBAR KIRI MODERN (HAMBURGER + IKON SATU TEMA)
# ===========================================
with st.sidebar:
    st.markdown("""
        <div style="font-weight: 900; font-size: 16px; color: #A8E6F0 !important; letter-spacing: 0.5px; padding-top: 5px;">
            <i class="bi bi-lightning-charge-fill"></i> PLN PUSHARLIS QC
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="user-profile-box">
            <div class="user-avatar"><i class="bi bi-person-fill" style="font-size: 20px; color: #FFFFFF;"></i></div>
            <div>
                <div style="font-weight: 700; font-size: 13.5px; color: #FFFFFF !important;">PLN PUSHARLIS</div>
                <div style="font-size: 11px; color: #A8E6F0 !important; font-weight: 600;">Teknisi QC Inspector</div>
                <div style="font-size: 10px; color: #94A3B8 !important;">pusharlis@pln.co.id</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    current_index = MENU_KEYS.index(st.session_state.menu) if st.session_state.menu in MENU_KEYS else 0

    selected_label = option_menu(
        menu_title=None,
        options=MENU_LABELS,
        icons=MENU_ICONS,
        menu_icon="list",          # ikon hamburger (garis 3) di header menu
        default_index=current_index,
        key="sidebar_menu",
        styles={
            "container": {
    "padding": "12px",
    "background-color": "#FFF8C8",
    "border-radius": "14px",
    "border": "1px solid #EAE83A",
},
            "icon": {"color": "#A8E6F0", "font-size": "16px"},
            "nav-link": {
                "font-size": "13.5px",
                "font-weight": "600",
                "color": "#94A3B8",
                "text-align": "left",
                "margin": "3px 0",
                "border-radius": "10px",
                "padding": "10px 14px",
                "--hover-color": "rgba(255,255,255,0.10)",
            },
            "nav-link-selected": {
                "background-color": "rgba(255,255,255,0.16)",
                "color": "#FFFFFF",
                "font-weight": "700",
                "border": "1px solid rgba(255,255,255,0.25)",
            },
        },
    )

    selected_key = MENU_KEYS[MENU_LABELS.index(selected_label)]
    if selected_key != st.session_state.menu:
        st.session_state.menu = selected_key
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("© 2026 PT PLN (Persero) Pusharlis")

# ===========================================
# 7. MENU 1: BERANDA
# ===========================================
if st.session_state.menu == "beranda":
    logo_src = f"data:image/png;base64,{logo_pln_b64}" if logo_pln_b64 else "https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_PLN.png"
    
    st.markdown(f"""
        <div class="hero-banner">
            <div class="banner-left">
                <div class="logo-box">
                    <img src="{logo_src}" alt="Logo PLN" />
                </div>
                <div>
                    <div class="banner-title">PLN QUALITY CONTROL SYSTEM</div>
                    <div class="banner-subtitle">
                        PT PLN (Persero) Pusharlis — Mobile Inspection & Testing Management System
                    </div>
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px); padding: 8px 18px; border-radius: 20px; font-weight: 700;">
                ⚡ Pusharlis QC
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_prof1, c_prof2 = st.columns([1.5, 1])
    with c_prof1:
        st.markdown("""
            <div class="info-card">
                <div class="info-card-title"><i class="bi bi-building"></i> Informasi Umum Instansi</div>
                <table class="info-table">
                    <tr><td class="label">Nama Instansi</td><td class="value">PT PLN (Persero) Pusat Pemeliharaan Ketenagalistrikan (Pusharlis)</td></tr>
                    <tr><td class="label">Alamat Kantor Induk</td><td class="value">Jl. Banten No. 10, Kebonwaru, Bandung, Jawa Barat 40272</td></tr>
                    <tr><td class="label">Telepon / Fax</td><td class="value">(022) 7236791 - 3</td></tr>
                    <tr><td class="label">Email Resmi</td><td class="value">pusharlis@pln.co.id</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

    with c_prof2:
        st.markdown("""
            <div class="info-card">
                <div class="info-card-title"><i class="bi bi-bullseye"></i> Visi &amp; Misi Pusharlis</div>
                <p style="font-size: 13px; color: #334155; line-height: 1.6;"><b>Visi:</b> Menjadi pusat keunggulan rekayasa dan pemeliharaan ketenagalistrikan terpercaya bertaraf internasional.</p>
                <p style="font-size: 13px; color: #334155; line-height: 1.6;"><b>Misi:</b> Menyediakan produk manufaktur & pemeliharaan ketenagalistrikan yang berkualitas tinggi.</p>
            </div>
        """, unsafe_allow_html=True)

# ===========================================
# 8. MENU 2: DASHBOARD
# ===========================================
elif st.session_state.menu == "dashboard":
    st.markdown('<div style="font-size: 28px;font-weight: 900;color: #1E293B;line-height: 1.1;border-radius:18px;border:1px solid #EAE83A;padding:24px;color:linear-gradient #FFFDF2 0%, #FFF8D8 70%,#FFF4A8 100%#1E293B; margin-bottom: 4px;"><i class="bi bi-speedometer2"></i> DASHBOARD SUMMARY PENGUJIAN QC</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #64748B; margin-bottom: 20px;">Ringkasan eksekutif, status kepatuhan, dan analitik real-time pengujian peralatan PLN Pusharlis.</div>', unsafe_allow_html=True)
   
    # 1. AMBIL METRIK UTAMA
    op_val = total_onepost() if callable(total_onepost) else 0
    phb_val = total_phbtr() if callable(total_phbtr) else 0
    pmcb_val = total_pmcb() if callable(total_pmcb) else 0
    total_inspeksi = op_val + phb_val + pmcb_val

    # 2. METRIC CARDS OVERVIEW (PALET WARNA PLN)
    st.markdown('<div style="font-size: 15px; font-weight: 700; margin: 10px 0;"><i class="bi bi-pin-angle"></i> Overview Statistik Inspeksi</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B5E6E 0%, #14495A 100%); border-radius: 12px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #FFFFFF; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #CDEBF2; text-transform: uppercase; letter-spacing: 0.5px;"><i class="bi bi-tools"></i> ONEPOST 3500</div>
                <div style="font-size: 30px; font-weight: 800; color: #FFFFFF; margin: 6px 0;">{op_val} <span style="font-size: 14px; font-weight: 500; color: #CDEBF2;">Unit</span></div>
                <div style="font-size: 11px; color: #CDEBF2; font-weight: 600;">● Terdaftar di DB</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Form OnePost ➔", key="btn_dash_op", use_container_width=True):
            navigate("onepost")

    with m2:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #14A8BE 0%, #0E8497 100%); border-radius: 12px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #FFFFFF; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #DFF7FB; text-transform: uppercase; letter-spacing: 0.5px;"><i class="bi bi-lightning-charge"></i> PHB TR</div>
                <div style="font-size: 30px; font-weight: 800; color: #FFFFFF; margin: 6px 0;">{phb_val} <span style="font-size: 14px; font-weight: 500; color: #DFF7FB;">Unit</span></div>
                <div style="font-size: 11px; color: #DFF7FB; font-weight: 600;">● Terdaftar di DB</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Form PHB TR ➔", key="btn_dash_phb", use_container_width=True):
            navigate("phbtr")

    with m3:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #EAE83A 0%, #D4D226 100%); border-radius: 12px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #1B5E6E; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #4A4A00; text-transform: uppercase; letter-spacing: 0.5px;"><i class="bi bi-shield-check"></i> PMCB</div>
                <div style="font-size: 30px; font-weight: 800; color: #1B5E6E; margin: 6px 0;">{pmcb_val} <span style="font-size: 14px; font-weight: 500; color: #4A4A00;">Unit</span></div>
                <div style="font-size: 11px; color: #4A4A00; font-weight: 600;">● Terdaftar di DB</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Form PMCB ➔", key="btn_dash_pmcb", use_container_width=True):
            navigate("pmcb")

    with m4:
        st.markdown(f"""
            <div style="background: #FFFFFF; border: 2px solid #DADADA; border-radius: 12px; padding: 18px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); color: #1B5E6E; margin-bottom: 10px;">
                <div style="font-size: 11px; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px;"><i class="bi bi-clipboard-data"></i> TOTAL INSPEKSI</div>
                <div style="font-size: 30px; font-weight: 800; color: #1B5E6E; margin: 6px 0;">{total_inspeksi} <span style="font-size: 14px; font-weight: 500; color: #6B7280;">Unit</span></div>
                <div style="font-size: 11px; color: #6B7280; font-weight: 500;">Sistem Aktif & Normal</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. GRAFIK DAN ANALITIK VISUAL
    c_dash1, c_dash2 = st.columns([1, 1])

    with c_dash1:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px;">
                <div style="font-size: 11px; font-weight: 700; color: #14A8BE; background: #E3F6FB; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px;">SEBARAN DATA</div>
                <h5 style="margin: 0 0 15px 0; color: #1E293B;"><i class="bi bi-bar-chart-line"></i> Perbandingan Pengujian Peralatan</h5>
        """, unsafe_allow_html=True)
        
        df_dist = pd.DataFrame({
            "Kategori": ["OnePost", "PHB TR", "PMCB"],
            "Jumlah Uji": [op_val, phb_val, pmcb_val]
        }).set_index("Kategori")
        st.bar_chart(df_dist, color="#14A8BE")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_dash2:
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-bottom: 20px;">
                <div style="font-size: 11px; font-weight: 700; color: #1B5E6E; background: #E3F6FB; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px;">TREN PENGUJIAN</div>
                <h5 style="margin: 0 0 15px 0; color: #1E293B;"><i class="bi bi-graph-up"></i> Grafik Aktivitas Inspeksi</h5>
        """, unsafe_allow_html=True)
        
        df_activity = pd.DataFrame({
            "Hari": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"],
            "Aktivitas": [1, 2, 1, 3, total_inspeksi, 0]
        }).set_index("Hari")
        st.line_chart(df_activity, color="#1B5E6E")
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. TABEL MONITORING LIVE
    st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="font-size: 11px; font-weight: 700; color: #14A8BE; background: #E3F6FB; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px;">MONITORING LIVE</div>
            <h5 style="margin: 0 0 15px 0; color: #1E293B;"><i class="bi bi-file-earmark-text"></i> Data Inspeksi Terbaru (OnePost)</h5>
    """, unsafe_allow_html=True)
    
    df_op_dash = ambil_semua_onepost() if callable(ambil_semua_onepost) else pd.DataFrame()
    if not df_op_dash.empty:
        st.dataframe(df_op_dash.tail(5), use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Belum ada riwayat data OnePost tersimpan di database.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================
# 9. MENU 3: FORM PENGUJIAN ONEPOST
# ===========================================
elif st.session_state.menu == "onepost":
    col_back, col_head = st.columns([1.5, 6], vertical_alignment="center")
    with col_back:
        if st.button("⬅ Beranda", key="back_onepost", use_container_width=True):
            navigate("beranda")
    with col_head:
        st.markdown('<h2><i class="bi bi-tools"></i> Form Pengujian &amp; Log Sheet OnePost 3500</h2>', unsafe_allow_html=True)

    st.divider()
    form_onepost()


# ===========================================
# 10. MENU 4: FORM PENGUJIAN PHB TR
# ===========================================
elif st.session_state.menu == "phbtr":
    col_back, col_head = st.columns([1.5, 6], vertical_alignment="center")
    with col_back:
        if st.button("⬅ Beranda", key="back_phbtr", use_container_width=True):
            navigate("beranda")
    with col_head:
        st.markdown('<h2><i class="bi bi-lightning-charge"></i> Form Pengujian PHB TR</h2>', unsafe_allow_html=True)

    st.divider()
    form_phbtr()

    
        

# ===========================================
# 11. MENU 5: FORM PENGUJIAN PMCB
# ===========================================
elif st.session_state.menu == "pmcb":
    col_back, col_head = st.columns([1.5, 6], vertical_alignment="center")
    with col_back:
        if st.button("⬅ Beranda", key="back_pmcb", use_container_width=True):
            navigate("beranda")
    with col_head:
        st.markdown('<h2><i class="bi bi-shield-check"></i> Form Pengujian PMCB</h2>', unsafe_allow_html=True)

    st.divider()
    form_pmcb()
    
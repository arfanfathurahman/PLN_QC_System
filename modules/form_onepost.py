from pathlib import Path
import pandas as pd
import streamlit as st

from modules.theme import (
    apply_form_theme,
    form_header,
    section_tag,
    card_begin,
    card_end,
    table_headers,
    row_no,
    row_label,
    badge,
    thin_divider,
    progress_summary,
    result_status,
    qc_score_card,
    autosave_indicator,
)
from modules.unit_manager import (
    init_units,
    render_unit_selector,
    get_active_serial,
    get_active_unit_state,
    autosave_unit,
    delete_unit,
    render_history_panel,
    get_all_units_for_export,
)
from modules.pdf_export import build_onepost_pdf, pdf_download_button
BASE_DIR = Path(__file__).resolve().parent.parent
gambar_dimensi_onepost = BASE_DIR / "assets" / "onepost_dimensi.png"


def _find_logo_pln():
    """
    Cari file logo PLN di beberapa lokasi & nama file yang umum dipakai,
    supaya tidak gagal cuma karena beda nama file / folder sedikit.
    """
    candidates = [
        BASE_DIR / "assets" / "logo_pln.png",
        BASE_DIR / "assets" / "logo_pln_png.png",
        BASE_DIR / "assets" / "logo_pln.jpg",
        BASE_DIR / "assets" / "logo_pln.jpeg",
        BASE_DIR / "assets" / "logo_PLN.png",
        BASE_DIR / "logo_pln.png",
        BASE_DIR / "logo_pln_png.png",
        Path(__file__).resolve().parent / "assets" / "logo_pln.png",
        Path(__file__).resolve().parent / "logo_pln.png",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _find_dimensi_onepost():
    candidates = [
        BASE_DIR / "assets" / "onepost_dimensi.png",
        BASE_DIR / "assets" / "onepost_dimensi.jpg",
        Path(__file__).resolve().parent / "assets" / "onepost_dimensi.png",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def form_onepost():
    apply_form_theme()
    form_header(
        icon="tools",
        title="FORM QUALITY CONTROL ONEPOST (SUPERSUN 1300VA)",
        subtitle="Pengujian rutin unit Onepost 1300VA — PLN Pusharlis",
    )

    init_units("onepost")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📋 Informasi",
        "👀 Visual",
        "🗄 Selungkup",
        "🔧 Komponen",
        "🔌 Tarik Skun",
        "📏 Dimensi",
        "🖥 Board",
        "⚙ Fungsi",
        "📝 Catatan",
        "📊 Summary",
        "📷 Lampiran"
    ])

    # ==========================================================
    # TAB 1 - INFORMASI PRODUK
    # ==========================================================
    with tab1:
        card_begin()
        section_tag("Informasi Produk")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-info-circle"></i> '
            "Informasi Produk Onepost</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Penugasan Tetap Fabrikasi 6 Set Kompak Daya Berbasis "
            "Baterai 1300VA (Onepost) PLN UID S2JB"
        )

        autosave_indicator(True)
        render_unit_selector("onepost")
        active_serial = get_active_serial("onepost")
        thin_divider()

        c1, c2 = st.columns(2)
        with c1:
            no_amp = st.text_input("No AMP", value="26019301")
            nama_produk = st.text_input(
                "Nama Produk",
                value="SUPERSUN 1300VA",
                key="nama_produk_onepost",
            )
            nomor_seri = st.text_input("Nomor Seri", value=active_serial or "", key="nomor_seri_onepost")
            daya = st.text_input("Daya", value="1300VA")
            tanggal = st.date_input("Tanggal Pengujian")
        with c2:
            tegangan_input = st.text_input(
                "Tegangan Input",
                value="220 VAC ; 24 VDC (Grid) ; 36-90 VDC (PV)",
            )
            tegangan_output = st.text_input("Tegangan Output", value="220-230 VAC")
            inspector = st.text_input("Inspector")
            customer = st.text_input("Customer", value="PT PLN (Persero)")
            status = st.selectbox("Status", ["Draft", "Final"])

        if active_serial:
            autosave_unit("onepost", "info", {
                "no_amp": no_amp, "nama_produk": nama_produk,
                "nomor_seri": nomor_seri, "daya": daya,
                "tanggal": str(tanggal), "tegangan_input": tegangan_input,
                "tegangan_output": tegangan_output, "inspector": inspector,
                "customer": customer, "status": status,
            }, tab_name="Informasi")

        thin_divider()
        if active_serial:
            with st.expander("🗑️ Hapus Project "):
                st.warning(
                    f"Ini akan menghapus permanen semua data project **{active_serial}** "
                    "(seluruh tab yang sudah diisi, termasuk foto lampiran). "
                    "Tindakan ini tidak bisa dibatalkan."
                )
                confirm_delete = st.checkbox(
                    f"Saya yakin ingin menghapus project '{active_serial}' secara permanen",
                    key=f"confirm_delete_onepost_{active_serial}",
                )
                if st.button(
                    "🗑️ Hapus Sekarang",
                    key=f"hapus_btn_onepost_{active_serial}",
                    type="primary",
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_unit("onepost", active_serial)
                    st.success(f"Project '{active_serial}' telah dihapus.")
                    st.rerun()
        st.button("➡ Lanjut ke Visual", key="lanjut_onepost", use_container_width=True)
        card_end()

    # ==========================================================
    # TAB 2 - VISUAL DAN PENANDAAN
    # ==========================================================
    with tab2:
        card_begin()
        section_tag("Visual & Penandaan")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-eye"></i> '
            "Visual dan Penandaan</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan visual sesuai Form Quality Control Onepost")

        visual_items = [
            {"item": "Hasil pengerjaan baik dan kondisi baru"},
            {"item": "Kesesuaian stiker papan nama"},
        ]
        hasil_visual = []

        table_headers(
            st.columns([0.5, 7, 1, 2]),
            ["No", "Jenis Pemeriksaan", "✓", "Hasil"],
        )

        for i, data in enumerate(visual_items, start=1):
            c1, c2, c3, c4 = st.columns([0.5, 7, 1, 2])
            with c1:
                row_no(i)
            with c2:
                row_label(data["item"])
            with c3:
                sesuai = st.checkbox("", value=True, key=f"visual_op_{i}")
            with c4:
                if sesuai:
                    badge("Sesuai", "ok")
                else:
                    badge("Tidak Sesuai", "bad")
            hasil_visual.append({"item": data["item"], "status": sesuai})

        thin_divider()
        jumlah_sesuai = sum(1 for x in hasil_visual if x["status"])
        persen = jumlah_sesuai / len(hasil_visual) * 100
        progress_summary(len(hasil_visual), jumlah_sesuai, "Total Pemeriksaan", "Sesuai")
        result_status(
            persen,
            "🟢 Pemeriksaan Visual LULUS",
            fail_msg="🟡 Masih terdapat ketidaksesuaian",
        )
        card_end()
        st.session_state["visual_onepost"] = hasil_visual
        autosave_unit("onepost", "visual_onepost", hasil_visual, tab_name="Visual")

    # ==========================================================
    # TAB 3 - SELUNGKUP
    # ==========================================================
    with tab3:
        card_begin()
        section_tag("Selungkup")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-box"></i> '
            "Pemeriksaan Selungkup</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan selungkup sesuai Form Quality Control Onepost")

        table_headers(
            st.columns([4, 4, 1, 2]),
            ["Jenis Pemeriksaan", "Spesifikasi / Persyaratan", "✓", "Hasil"],
        )

        selungkup = [
            {"parameter": "Cat powder Coating min 80 μm", "jenis": "coating"},
            {"parameter": "Handle pengangkat supersun", "jenis": "check"},
            {"parameter": "Branding Logo PLN", "jenis": "check"},
        ]
        hasil_selungkup = []

        for i, item in enumerate(selungkup):
            c1, c2, c3, c4 = st.columns([4, 4, 1, 2])
            with c1:
                row_label(item["parameter"])
            with c2:
                if item["jenis"] == "coating":
                    a, b = st.columns(2)
                    with a:
                        tebal = st.number_input("", value=80, step=1, key=f"coat_op_{i}")
                    with b:
                        warna = st.text_input("", value="RAL7032", key=f"warna_op_{i}")
                    nilai = f"{tebal} μm | {warna}"
                else:
                    nilai = "-"
                    st.write("-")
            with c3:
                status_sel = st.selectbox("", ["✓", "✗"], key=f"status_sel_op_{i}")
            with c4:
                if status_sel == "✓":
                    badge("Sesuai", "ok")
                else:
                    badge("Tidak Sesuai", "bad")
            hasil_selungkup.append({
                "parameter": item["parameter"],
                "nilai": nilai,
                "status": status_sel,
            })

        thin_divider()
        sesuai_sel = sum(1 for x in hasil_selungkup if x["status"] == "✓")
        persen = sesuai_sel / len(hasil_selungkup) * 100
        progress_summary(len(hasil_selungkup), sesuai_sel, "Parameter", "Sesuai")
        result_status(
            persen,
            "🟢 Pemeriksaan Selungkup LULUS",
            fail_msg="🟡 Masih terdapat ketidaksesuaian",
        )
        card_end()
        st.session_state["selungkup_onepost"] = hasil_selungkup
        autosave_unit("onepost", "selungkup_onepost", hasil_selungkup, tab_name="Selungkup")

    # ==========================================================
    # TAB 4 - PEMERIKSAAN KOMPONEN
    # ==========================================================
    with tab4:
        card_begin()
        section_tag("Komponen")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-gear"></i> '
            "Pemeriksaan Komponen</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan komponen sesuai Form Quality Control Onepost")

        hasil_komponen = []
        table_headers(
            st.columns([3, 2.3, 2.3, 2.3, 1.3]),
            ["Komponen", "Spesifikasi 1", "Spesifikasi 2", "Spesifikasi 3", "✓ / Hasil"],
        )

        # --- INVERTER ---
        c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
        with c1:
            st.markdown("### Inverter")
        with c2:
            inv_merk = st.text_input("Merk", value="ZAMDON", key="inv_merk")
            inv_vin = st.text_input("Tegangan Input", value="24 VDC", key="inv_vin")
        with c3:
            inv_daya = st.text_input("Daya", value="2000W", key="inv_daya")
            inv_vout = st.text_input("Tegangan Output", value="230 VAC ± 10%", key="inv_vout")
        with c4:
            inv_freq = st.text_input("Frekuensi", value="50 Hz", key="inv_freq")
            inv_out = st.text_input("Output", value="Gelombang sinus murni", key="inv_out")
        with c5:
            status_inv = st.selectbox("", ["✓", "✗"], key="status_inv")
            st.write("Sesuai" if status_inv == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Inverter", "status": status_inv})
        thin_divider()

        # --- MPPT / SCC ---
        c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
        with c1:
            st.markdown("### MPPT / SCC")
        with c2:
            mppt_merk = st.text_input("Merk ", value="ZAMDON", key="mppt_merk")
            mppt_tipe = st.text_input("Tipe ", value="XTRA4215N", key="mppt_tipe")
        with c3:
            mppt_vdc = st.text_input("Tegangan Input DC", value="24 VDC", key="mppt_vdc")
            mppt_vpv = st.text_input("Tegangan Input PV", value="150 VDC", key="mppt_vpv")
        with c4:
            mppt_daya = st.text_input("Daya Pengisi Terkini", value="1040W/24V", key="mppt_daya")
            mppt_arus = st.text_input("Arus Maksimum", value="40 A", key="mppt_arus")
        with c5:
            status_mppt = st.selectbox("", ["✓", "✗"], key="status_mppt")
            st.write("Sesuai" if status_mppt == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "MPPT/SCC", "status": status_mppt})
        thin_divider()

        # --- RCBO ---
        c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
        with c1:
            st.markdown("### RCBO")
        with c2:
            rcbo_merk = st.text_input("Merk  ", value="Chint", key="rcbo_merk")
            rcbo_tipe = st.text_input("Tipe  ", value="NB2LE", key="rcbo_tipe")
        with c3:
            rcbo_arus = st.text_input("Arus Terukur", value="25 A", key="rcbo_arus")
            rcbo_freq = st.text_input("Frekuensi ", value="50 Hz", key="rcbo_freq")
        with c4:
            rcbo_kap = st.text_input("Kapasitas Pemutusan", value="6 kA", key="rcbo_kap")
            rcbo_residu = st.text_input("Arus Residu Terukur", value="30 mA", key="rcbo_residu")
        with c5:
            status_rcbo = st.selectbox("", ["✓", "✗"], key="status_rcbo")
            st.write("Sesuai" if status_rcbo == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "RCBO", "status": status_rcbo})
        thin_divider()

        # --- MCB 1 & MCB 2 ---
        mcb_default = [
            {"arus": "32 A", "key": "mcb1"},
            {"arus": "63 A", "key": "mcb2"},
        ]
        mcb_vals = {}
        for i, mcb in enumerate(mcb_default, start=1):
            c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
            with c1:
                st.markdown(f"### MCB {i}")
            with c2:
                m_merk = st.text_input("Merk   ", value="Suntree", key=f"{mcb['key']}_merk")
                m_tipe = st.text_input("Tipe   ", value="SL7N-63 DC", key=f"{mcb['key']}_tipe")
            with c3:
                m_arus = st.text_input("Arus Terukur ", value=mcb["arus"], key=f"{mcb['key']}_arus")
                m_kutub = st.text_input("Jumlah Kutub", value="1P", key=f"{mcb['key']}_kutub")
            with c4:
                m_std = st.text_input("Standard", value="IEC 60947-2", key=f"{mcb['key']}_std")
                m_kap = st.text_input("Kapasitas Pemutusan ", value="6 kA", key=f"{mcb['key']}_kap")
            with c5:
                status_mcb = st.selectbox("", ["✓", "✗"], key=f"status_{mcb['key']}")
                st.write("Sesuai" if status_mcb == "✓" else "Tidak Sesuai")
            hasil_komponen.append({
                "komponen": f"MCB {i} ({mcb['arus']})",
                "status": status_mcb,
            })
            mcb_vals[mcb["key"]] = {
                "merk": m_merk, "tipe": m_tipe, "arus": m_arus,
                "kutub": m_kutub, "std": m_std, "kap": m_kap,
                "status": status_mcb,
            }
            thin_divider()

        # --- Smart Circuit Breaker ---
        c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
        with c1:
            st.markdown("### Smart Circuit Breaker")
        with c2:
            scb_merk = st.text_input("Merk    ", value="Taxnele", key="scb_merk")
            scb_tipe = st.text_input("Tipe    ", value="TXCB2-VAP", key="scb_tipe")
        with c3:
            scb_arus = st.text_input("Arus Terukur  ", value="10-63 A", key="scb_arus")
            scb_kutub = st.text_input("Jumlah Kutub ", value="1P+N", key="scb_kutub")
        with c4:
            scb_std = st.text_input("Standard ", value="IEC 60947-2", key="scb_std")
            scb_konek = st.text_input("Konektivitas", value="2.4 GHz", key="scb_konek")
        with c5:
            status_scb = st.selectbox("", ["✓", "✗"], key="status_scb")
            st.write("Sesuai" if status_scb == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Smart Circuit Breaker", "status": status_scb})
        thin_divider()

        # --- Baterai ---
        c1, c2, c3, c4, c5 = st.columns([3, 2.3, 2.3, 2.3, 1.3])
        with c1:
            st.markdown("### Baterai")
        with c2:
            bat_merk = st.text_input("Merk     ", value="SUP", key="bat_merk")
            bat_vnom = st.text_input("Tegangan Nominal", value="25,6 V", key="bat_vnom")
        with c3:
            bat_kap = st.text_input("Kapasitas Arus Nominal", value="100 Ah", key="bat_kap")
            bat_vpengisian = st.text_input("Tegangan Pengisian", value="28,8V", key="bat_vpengisian")
        with c4:
            bat_tipe = st.text_input("Tipe Baterai", value="LiFePO4", key="bat_tipe")
            bat_umur = st.text_input("Umur Pakai", value="2500 Cycle", key="bat_umur")
        with c5:
            status_bat = st.selectbox("", ["✓", "✗"], key="status_bat")
            st.write("Sesuai" if status_bat == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Baterai", "status": status_bat})
        thin_divider()

        # --- Item tambahan (busbar, kabel, proteksi) ---
        tambahan = [
            ("Busbar Positif dan Negatif", "180 x 25 x 3 mm"),
            ("Busbar pembumian", "135 x 15 x 3 mm"),
            ("Setting Proteksi kWh Taxnelle", "Rating 4A"),
            ("Kabel instalasi", "NYYHY 2x2.5mm, NYAF 10mm, 6mm, 2.5mm, 0.75mm, AWG 22"),
        ]
        for i, data in enumerate(tambahan):
            c1, c2, c3, c4 = st.columns([3, 5.5, 1, 1.5])
            with c1:
                row_label(data[0])
            with c2:
                nilai_tmb = st.text_input("", value=data[1], key=f"tambahan_op_{i}")
            with c3:
                status_tmb = st.selectbox("", ["✓", "✗"], key=f"status_tambahan_op_{i}")
            with c4:
                st.write("Sesuai" if status_tmb == "✓" else "Tidak Sesuai")
            hasil_komponen.append({
                "komponen": data[0],
                "nilai": nilai_tmb,
                "status": status_tmb,
            })

        thin_divider()
        sesuai_komp = sum(1 for x in hasil_komponen if x["status"] == "✓")
        persen = sesuai_komp / len(hasil_komponen) * 100
        progress_summary(len(hasil_komponen), sesuai_komp, "Total Komponen", "Sesuai")
        result_status(
            persen,
            "🟢 Pemeriksaan Komponen LULUS",
            fail_msg="🟡 Masih terdapat komponen yang perlu diperiksa",
        )
        card_end()
        st.session_state["komponen_onepost"] = hasil_komponen

        # Data terstruktur untuk export PDF (grid spek 2x3 per komponen, persis blangko)
        komponen_detail = {
            "inverter": {"merk": inv_merk, "daya": inv_daya, "vin": inv_vin, "vout": inv_vout, "freq": inv_freq, "out": inv_out, "status": status_inv},
            "mppt": {"merk": mppt_merk, "tipe": mppt_tipe, "vdc": mppt_vdc, "vpv": mppt_vpv, "daya": mppt_daya, "arus": mppt_arus, "status": status_mppt},
            "rcbo": {"merk": rcbo_merk, "tipe": rcbo_tipe, "arus": rcbo_arus, "freq": rcbo_freq, "kap": rcbo_kap, "residu": rcbo_residu, "status": status_rcbo},
            "mcb1": mcb_vals.get("mcb1", {}),
            "mcb2": mcb_vals.get("mcb2", {}),
            "scb": {"merk": scb_merk, "tipe": scb_tipe, "arus": scb_arus, "kutub": scb_kutub, "std": scb_std, "konek": scb_konek, "status": status_scb},
            "baterai": {"merk": bat_merk, "vnom": bat_vnom, "kap": bat_kap, "vpengisian": bat_vpengisian, "tipe": bat_tipe, "umur": bat_umur, "status": status_bat},
        }
        st.session_state["komponen_detail_onepost"] = komponen_detail
        if get_active_serial("onepost"):
            autosave_unit("onepost", "komponen_onepost", hasil_komponen, tab_name="Komponen")
            autosave_unit("onepost", "komponen_detail_onepost", komponen_detail, tab_name="Komponen")

    # ==========================================================
    # TAB 5 - PENGUJIAN TARIK SKUN KABEL
    # ==========================================================
    with tab5:
        card_begin()
        section_tag("Tarik Skun Kabel")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-plug"></i> '
            "Pengujian Tarik Skun Kabel</div>",
            unsafe_allow_html=True,
        )
        st.caption("Ukuran kabel (mm) dan gaya tarik skun (N)")

        ukuran_kabel = [0.75, 2.5, 4, 6, 10]
        standar_default = [45, 150, 240, 360, 600]
        hasil_default = [56.22, 179.2, 273.0, 398.9, 659.6]

        table_headers(
            st.columns([1.5, 2, 2, 1.5]),
            ["Ukuran Kabel (mm)", "Persyaratan Standar (N)", "Hasil Pemeriksaan (N)", "Status"],
        )

        hasil_tarik = []
        for i, ukuran in enumerate(ukuran_kabel):
            c1, c2, c3, c4 = st.columns([1.5, 2, 2, 1.5])
            with c1:
                row_label(f"{ukuran} mm")
            with c2:
                standar_val = st.number_input("", value=float(standar_default[i]), step=1.0, key=f"standar_tarik_{i}")
            with c3:
                hasil_val = st.number_input("", value=float(hasil_default[i]), step=0.1, key=f"hasil_tarik_{i}")
            status_tarik = hasil_val >= standar_val
            with c4:
                if status_tarik:
                    badge("✓ Sesuai", "ok")
                else:
                    badge("✗ Tidak Sesuai", "bad")
            hasil_tarik.append({
                "ukuran": ukuran,
                "standar": standar_val,
                "hasil": hasil_val,
                "status": status_tarik,
            })

        thin_divider()
        sesuai_tarik = sum(1 for x in hasil_tarik if x["status"])
        persen = sesuai_tarik / len(hasil_tarik) * 100
        progress_summary(len(hasil_tarik), sesuai_tarik, "Total Pengujian", "Sesuai")
        result_status(
            persen,
            "🟢 Pengujian Tarik Skun Kabel LULUS",
            fail_msg="🟡 Terdapat hasil di bawah persyaratan standar",
        )
        card_end()
        st.session_state["tarik_skun_onepost"] = hasil_tarik
        autosave_unit("onepost", "tarik_skun_onepost", hasil_tarik, tab_name="Tarik Skun")

    # ==========================================================
    # TAB 6 - PENGUJIAN DIMENSI SELUNGKUP
    # ==========================================================
    with tab6:
        card_begin()
        section_tag("Dimensi Selungkup")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-rulers"></i> '
            "Pengujian Dimensi Selungkup</div>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            dim_img = _find_dimensi_onepost()
            if dim_img:
                st.image(str(dim_img), caption="Gambar Acuan Dimensi Onepost", use_container_width=True)
            else:
                st.info(f"Gambar acuan dimensi belum tersedia. Taruh file di: `{BASE_DIR / 'assets' / 'onepost_dimensi.png'}`")
            thin_divider()
            df = pd.DataFrame({
                "Parameter": ["Persyaratan Standar (mm)", "Hasil Ukur (mm) toleransi 5%"],
                "A": [280, 280], "B": [605, 605], "C": [530, 530], "D": [327.8, 327.8],
                "E": [107, 107], "F": [422.6, 422.6], "G": [400, 400], "H": [160, 160],
            })
            edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed", key="dimensi_editor_onepost")
            thin_divider()
            progress_summary(8, 8, "Total Parameter", "Sesuai")
            result_status(100.0, "🟢 Pengujian Dimensi Memenuhi Persyaratan")
        card_end()
        dimensi_dict = edited.drop(columns=["Parameter"]).to_dict("list")
        st.session_state["dimensi_onepost"] = dimensi_dict
        autosave_unit("onepost", "dimensi_onepost", dimensi_dict, tab_name="Dimensi")

    # ==========================================================
    # TAB 7 - PENGUJIAN BOARD
    # ==========================================================
    with tab7:
        card_begin()
        section_tag("Board Monitoring")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-display"></i> '
            "Pengujian Board</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan board monitoring Onepost")

        board_items = [
            {"item": "ID Board Monitoring", "spek": "ID terdata/terdaftar"},
            {"item": "Power Supply Board", "spek": "Board Menyala"},
            {"item": "Komunikasi", "spek": "Tersambung dengan internet"},
            {"item": "Sensor", "spek": "Sensor terbaca di dashboard"},
        ]

        table_headers(
            st.columns([3, 4, 1, 1.5]),
            ["Item Pengujian", "Spesifikasi Uji", "✓", "Hasil"],
        )

        hasil_board = []
        for i, data in enumerate(board_items):
            c1, c2, c3, c4 = st.columns([3, 4, 1, 1.5])
            with c1:
                row_label(data["item"])
            with c2:
                row_label(data["spek"])
            with c3:
                cek = st.checkbox("", value=True, key=f"board_op_{i}")
            with c4:
                st.write("Baik" if cek else "Tidak Baik")
            hasil_board.append({"item": data["item"], "spek": data["spek"], "status": cek})

        thin_divider()
        sesuai_board = sum(1 for x in hasil_board if x["status"])
        persen = sesuai_board / len(hasil_board) * 100
        progress_summary(len(hasil_board), sesuai_board, "Total Pemeriksaan", "Baik")
        result_status(
            persen,
            "🟢 Pengujian Board LULUS",
            fail_msg="🟡 Masih terdapat item yang belum baik",
        )
        card_end()
        st.session_state["board_onepost"] = hasil_board
        autosave_unit("onepost", "board_onepost", hasil_board, tab_name="Board")

    # ==========================================================
    # TAB 8 - PENGUJIAN FUNGSI
    # ==========================================================
    with tab8:
        card_begin()
        section_tag("Fungsi")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-gear-wide-connected"></i> '
            "Pengujian Fungsi</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan fungsi sistem Onepost")

        hasil_fungsi = []
        table_headers(
            st.columns([2.5, 4, 2, 1, 1.3]),
            ["Jenis Pengujian", "Spesifikasi Uji", "Nilai Pengukuran", "✓", "Hasil"],
        )

        fungsi_check = [
            {"item": "MPPT/SCC", "spek": "Setting SCC melalui dongle"},
            {"item": "PV Input Charging", "spek": "Charging 80-90 VDC, Current Charging 16 ~ 30 A"},
            {"item": "Display Inverter", "spek": "Display ON"},
            {"item": "Indikator Lampu", "spek": "Indikator Baterai, PV, Inv"},
            {"item": "Fan", "spek": "Power ON"},
            {"item": "Limit Switch", "spek": "ON/OFF"},
            {"item": "Load Output 1 & 2", "spek": "Output Load ON, beban 300-800 W"},
        ]
        fungsi_nilai = [
            {"item": "Display BMS Baterai", "spek": "Display ON, Nominal SOC%", "default": 94.0, "satuan": "%"},
            {"item": "DC System Baterai", "spek": "Tegangan Baterai Vo=24~28 VDC", "default": 26.9, "satuan": "VDC"},
            {"item": "AC System Inverter", "spek": "Output Tegangan AC 220-230 V", "default": 220.0, "satuan": "VAC"},
        ]

        for i, data in enumerate(fungsi_check):
            c1, c2, c3, c4, c5 = st.columns([2.5, 4, 2, 1, 1.3])
            with c1:
                row_label(data["item"])
            with c2:
                row_label(data["spek"])
            with c3:
                st.write("-")
            with c4:
                cek = st.checkbox("", value=True, key=f"fungsi_chk_{i}")
            with c5:
                st.write("Baik" if cek else "Tidak Baik")
            hasil_fungsi.append({"item": data["item"], "spek": data["spek"], "status": cek})

        for i, data in enumerate(fungsi_nilai):
            c1, c2, c3, c4, c5 = st.columns([2.5, 4, 2, 1, 1.3])
            with c1:
                row_label(data["item"])
            with c2:
                row_label(data["spek"])
            with c3:
                nilai = st.number_input("", value=data["default"], step=0.1, key=f"fungsi_nilai_{i}")
                st.caption(data["satuan"])
            with c4:
                cek = st.checkbox("", value=True, key=f"fungsi_nilai_chk_{i}")
            with c5:
                st.write("Baik" if cek else "Tidak Baik")
            hasil_fungsi.append({"item": data["item"], "spek": data["spek"], "nilai": nilai, "satuan": data["satuan"], "status": cek})

        thin_divider()
        sesuai_fungsi = sum(1 for x in hasil_fungsi if x["status"])
        persen = sesuai_fungsi / len(hasil_fungsi) * 100
        progress_summary(len(hasil_fungsi), sesuai_fungsi, "Total Pemeriksaan", "Baik")
        result_status(
            persen,
            "🟢 Pengujian Fungsi LULUS",
            fail_msg="🟡 Masih terdapat item yang belum berfungsi baik",
        )
        card_end()
        st.session_state["fungsi_onepost"] = hasil_fungsi
        autosave_unit("onepost", "fungsi_onepost", hasil_fungsi, tab_name="Fungsi")

    # ==========================================================
    # TAB 9 - CATATAN & PENGESAHAN
    # ==========================================================
    with tab9:
        card_begin()
        section_tag("Catatan & Pengesahan")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-pencil"></i> '
            "Catatan & Pengesahan</div>",
            unsafe_allow_html=True,
        )
        hasil_pengujian = st.radio("Hasil Pengujian", ["diterima", "ditolak"], horizontal=True, key="hasil_pengujian_onepost")
        catatan = st.text_area("Catatan", key="catatan_onepost")
        thin_divider()
        c1, c2 = st.columns(2)
        with c1:
            diperiksa_oleh = st.text_input(
                "Diperiksa (Quality Control)",
                placeholder="Contoh: FAUZAN PRATAMA",
                key="diperiksa_onepost",
            )
        with c2:
            tanggal_periksa = st.date_input("Tanggal Pemeriksaan", key="tanggal_periksa_onepost")
        st.session_state["catatan_pengesahan_onepost"] = {
            "hasil_pengujian": hasil_pengujian,
            "catatan": catatan,
            "diperiksa_oleh": diperiksa_oleh,
        }
        autosave_unit("onepost", "catatan_pengesahan_onepost", st.session_state["catatan_pengesahan_onepost"], tab_name="Catatan")
        if hasil_pengujian == "diterima":
            result_status(100.0, "🟢 Hasil Pengujian: DITERIMA")
        else:
            result_status(0.0, "", fail_msg="🔴 Hasil Pengujian: DITOLAK")
        card_end()

    # ==========================================================
    # TAB 10 - SUMMARY ONEPOST
    # ==========================================================
    with tab10:
        card_begin()
        section_tag("Summary")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-clipboard-data"></i> '
            "Summary Quality Control Onepost</div>",
            unsafe_allow_html=True,
        )
        st.caption("Rekap keseluruhan hasil pemeriksaan Onepost (SUPERSUN 1300VA)")

        summary_data = []
        if "visual_onepost" in st.session_state:
            data = st.session_state["visual_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Visual dan Penandaan", total, sesuai, sesuai / total * 100])
        if "selungkup_onepost" in st.session_state:
            data = st.session_state["selungkup_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "✓")
            summary_data.append(["Selungkup", total, sesuai, sesuai / total * 100])
        if "komponen_onepost" in st.session_state:
            data = st.session_state["komponen_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "✓")
            summary_data.append(["Pemeriksaan Komponen", total, sesuai, sesuai / total * 100])
        if "tarik_skun_onepost" in st.session_state:
            data = st.session_state["tarik_skun_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Pengujian Tarik Skun Kabel", total, sesuai, sesuai / total * 100])
        summary_data.append(["Pengujian Dimensi Selungkup", 8, 8, 100])
        if "board_onepost" in st.session_state:
            data = st.session_state["board_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Pengujian Board", total, sesuai, sesuai / total * 100])
        if "fungsi_onepost" in st.session_state:
            data = st.session_state["fungsi_onepost"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Pengujian Fungsi", total, sesuai, sesuai / total * 100])

        if summary_data:
            df_summary = pd.DataFrame(summary_data, columns=["Pemeriksaan", "Jumlah Item", "Sesuai", "Persentase"])
            df_summary["Persentase"] = df_summary["Persentase"].round(1).astype(str) + " %"
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            nilai = [x[3] for x in summary_data]
            nilai_akhir = sum(nilai) / len(nilai)
            thin_divider()
            qc_score_card(len(summary_data), nilai_akhir)
            catatan_state = st.session_state.get("catatan_pengesahan_onepost", {})
            if catatan_state:
                thin_divider()
                st.markdown("### Pengesahan")
                st.write(f"**Hasil Pengujian:** {catatan_state.get('hasil_pengujian', '-')}")
                st.write(f"**Diperiksa (Quality Control):** {catatan_state.get('diperiksa_oleh', '-')}")
                if catatan_state.get("catatan"):
                    st.write(f"**Catatan:** {catatan_state.get('catatan')}")

            thin_divider()
            st.markdown("---")
            st.markdown("### Export PDF Laporan QC")
            export_units = get_all_units_for_export("onepost")
            if not export_units:
                st.info("Tambahkan minimal 1 unit di tab Informasi untuk export PDF.")
            else:
                c_exp1, c_exp2 = st.columns([2, 1])
                with c_exp1:
                    selected_serials = st.multiselect(
                        "Pilih unit untuk diexport:",
                        [u["info"].get("nomor_seri", "?") for u in export_units],
                        default=[u["info"].get("nomor_seri", "?") for u in export_units],
                        key="export_sel_onepost",
                    )
                with c_exp2:
                    st.caption(f"{len(export_units)} unit tersedia")

                units_to_export = [u for u in export_units if u["info"].get("nomor_seri") in selected_serials]

                logo_path = _find_logo_pln()
                dim_img_path = _find_dimensi_onepost()
                if logo_path:
                    st.caption(f"🖼️ Logo PLN terdeteksi: `{logo_path}`")
                else:
                    st.warning(
                        "⚠️ Logo PLN tidak ditemukan. Letterhead PDF akan pakai teks 'PLN' saja. "
                        f"Taruh file di: `{BASE_DIR / 'assets' / 'logo_pln.png'}`"
                    )
                if not dim_img_path:
                    st.warning(
                        "⚠️ Gambar acuan dimensi Onepost tidak ditemukan. "
                        f"Taruh file di: `{BASE_DIR / 'assets' / 'onepost_dimensi.png'}`"
                    )

                if units_to_export and st.button("📄 Generate PDF", key="gen_pdf_onepost", use_container_width=True, type="primary"):
                    pdf_bytes = build_onepost_pdf(
                        units_to_export,
                        logo_path=str(logo_path) if logo_path else None,
                        dimensi_image_path=str(dim_img_path) if dim_img_path else None,
                    )
                    filename = f"QC_Onepost_{'_'.join(selected_serials)}.pdf"
                    pdf_download_button(pdf_bytes, filename=filename, label="⬇ Download PDF Laporan")
                    st.success(f"✅ PDF berhasil dibuat untuk {len(units_to_export)} unit!")
        else:
            st.info("Belum ada data pengujian")

        thin_divider()
        render_history_panel("onepost")
        card_end()

    # ==========================================================
    # TAB 11 - LAMPIRAN DOKUMENTASI
    # ==========================================================
    with tab11:
        card_begin()
        section_tag("Lampiran")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-camera"></i> '
            "Lampiran Dokumentasi</div>",
            unsafe_allow_html=True,
        )
        st.caption("Upload foto dokumentasi unit sesuai Form Quality Control Onepost")

        nama_produk_lampiran = st.session_state.get("nama_produk_onepost", "SUPERSUN 1300VA")
        nomor_seri_lampiran = st.session_state.get("nomor_seri_onepost", "")

        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nama Produk", value=nama_produk_lampiran, disabled=True, key="lampiran_nama_produk_display")
        with c2:
            st.text_input("Nomor Seri", value=nomor_seri_lampiran, disabled=True, key="lampiran_nomor_seri_display")
        thin_divider()

        # Foto yang sudah tersimpan sebelumnya untuk unit ini (dari autosave)
        existing_state = get_active_unit_state("onepost") or {}
        existing_lampiran = (existing_state.get("lampiran_onepost") or {}).get("foto", [])
        existing_valid = [f for f in existing_lampiran if f.get("path") and Path(f["path"]).exists()]

        if existing_valid:
            st.markdown(f"**{len(existing_valid)} foto tersimpan sebelumnya**")
            cols_e = st.columns(3)
            for i, f in enumerate(existing_valid):
                with cols_e[i % 3]:
                    st.image(f["path"], use_container_width=True, caption=f.get("keterangan", f.get("file_name", "")))
            thin_divider()

        uploaded_files = st.file_uploader(
            "Upload Foto Dokumentasi baru (papan nama, label bahaya listrik, kondisi unit, dsb.)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="lampiran_upload_onepost",
        )
        new_lampiran = []
        if uploaded_files:
            unit_dir = BASE_DIR / "uploads" / "onepost" / (nomor_seri_lampiran or "tanpa_nomor_seri")
            unit_dir.mkdir(parents=True, exist_ok=True)
            st.markdown(f"**{len(uploaded_files)} foto baru diunggah**")
            thin_divider()
            cols = st.columns(3)
            for i, file in enumerate(uploaded_files):
                with cols[i % 3]:
                    st.image(file, use_container_width=True)
                    keterangan = st.text_input("Keterangan", value=file.name, key=f"lampiran_keterangan_{i}")
                save_path = unit_dir / file.name
                with open(save_path, "wb") as out_f:
                    file.seek(0)
                    out_f.write(file.getbuffer())
                new_lampiran.append({"file_name": file.name, "keterangan": keterangan, "path": str(save_path)})

        # Gabungkan foto lama + foto baru (nama file sama akan ditimpa versi terbaru)
        merged = {f["file_name"]: f for f in existing_valid}
        for f in new_lampiran:
            merged[f["file_name"]] = f
        hasil_lampiran = list(merged.values())

        if not hasil_lampiran:
            st.info("Belum ada foto yang diunggah")

        st.session_state["lampiran_onepost"] = {
            "nama_produk": nama_produk_lampiran,
            "nomor_seri": nomor_seri_lampiran,
            "foto": hasil_lampiran,
        }
        if get_active_serial("onepost"):
            autosave_unit("onepost", "lampiran_onepost", st.session_state["lampiran_onepost"], tab_name="Lampiran")
        card_end()
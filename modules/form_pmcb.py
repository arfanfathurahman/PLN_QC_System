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
from modules.pdf_export import build_pmcb_pdf, pdf_download_button

BASE_DIR = Path(__file__).resolve().parent.parent

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
def form_pmcb():
    apply_form_theme()
    form_header(
        icon="shield-check",
        title="FORM QUALITY CONTROL PMCB",
        subtitle="Pengujian rutin unit PMCB 4.0 — PLN Pusharlis",
    )

    init_units("pmcb")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "📋 Informasi",
        "⚡ Tahanan Kontak",
        "⏱ Keserempakan",
        "🛡 Relai Pengaman",
        "🧯 Tahanan Isolasi",
        "🔋 Uji HV",
        "⚙ Tes Fungsi",
        "🎨 Ketebalan Coating",
        "📦 Uji IP 55",
        "📷 Dokumentasi",
        "📝 Catatan",
        "📊 Summary"
    ])

    # ==========================================================
    # TAB 1 - INFORMASI
    # ==========================================================
    with tab1:
        card_begin()
        section_tag("Informasi Unit")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-info-circle"></i> '
            "Informasi Unit PMCB</div>",
            unsafe_allow_html=True,
        )
        st.caption("Penugasan Pembuatan 10 Unit PMCB 4.0 UID Jawa Barat")

        autosave_indicator(True)
        render_unit_selector("pmcb")
        active_serial = get_active_serial("pmcb")
        thin_divider()

        c1, c2 = st.columns(2)
        with c1:
            no_amp = st.text_input("No AMP", value="26147301")
            no_produk = st.text_input("No Produk", value="2026-")
            ratio_ct = st.text_input("Ratio CT", value="15/5-5 A")
            ratio_vt = st.text_input("Ratio VT", value="20 / √3 kV : 100 / √3 100/ √3 V")
        with c2:
            serial_vcb = st.text_input("Serial Number VCB", value=active_serial or "371446-38-47-1.15")
            merk_vcb = st.text_input("Merk VCB", value="SUSOL")
            type_vcb = st.text_input("Type VCB", value="SVL-20R25C13")
            arus_pengenal = st.text_input("Arus Pengenal", value="1250 A")
        tanggal = st.date_input("Tanggal Pengujian")
        inspector = st.text_input("Inspector")

        if active_serial:
            autosave_unit("pmcb", "info", {
                "no_amp": no_amp, "no_produk": no_produk,
                "ratio_ct": ratio_ct, "ratio_vt": ratio_vt,
                "serial_vcb": serial_vcb, "merk_vcb": merk_vcb,
                "type_vcb": type_vcb, "arus_pengenal": arus_pengenal,
                "tanggal": str(tanggal), "inspector": inspector,
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
                    key=f"confirm_delete_pmcb_{active_serial}",
                )
                if st.button(
                    "🗑️ Hapus Sekarang",
                    key=f"hapus_btn_pmcb_{active_serial}",
                    type="primary",
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_unit("pmcb", active_serial)
                    st.success(f"Project '{active_serial}' telah dihapus.")
                    st.rerun()
        st.button("➡ Lanjut ke Uji Tahanan Kontak", key="lanjut_pmcb", use_container_width=True)
        card_end()

    # ==========================================================
    # TAB 2 - UJI TAHANAN KONTAK
    # ==========================================================
    with tab2:
        card_begin()
        section_tag("1. Tahanan Kontak")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-lightning"></i> '
            "1. Uji Tahanan Kontak</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            alat_ukur_kontak = st.text_input("Alat Ukur", value="DV Power RMO-H23", key="alat_kontak")
        with c2:
            standar_kontak = st.text_input(
                "Referensi / Standard",
                value="Standar maksimum ±20% antar phase sebelum dan setelah uji high voltage (IEC 62271-200 butir 6.4.1)",
                key="standar_kontak",
            )

        table_headers(
            st.columns([1, 2, 2, 1.5]),
            ["Phasa", "Hasil (µΩ)", "Status", "Hasil"],
        )

        hasil_kontak = []
        phasa_default = [("R", 20.8), ("S", 21.1), ("T", 21.5)]
        for i, (phasa, nilai) in enumerate(phasa_default):
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1.5])
            with c1:
                row_label(phasa)
            with c2:
                hasil = st.number_input("", value=float(nilai), step=0.1, key=f"kontak_{i}")
            with c3:
                status = st.selectbox("", ["Accepted", "Not Accepted"], key=f"status_kontak_{i}")
            with c4:
                if status == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_kontak.append({"phasa": phasa, "nilai": hasil, "status": status})

        thin_divider()
        sesuai_kontak = sum(1 for x in hasil_kontak if x["status"] == "Accepted")
        persen = sesuai_kontak / len(hasil_kontak) * 100
        progress_summary(len(hasil_kontak), sesuai_kontak, "Total Phasa", "Accepted")
        result_status(
            persen,
            "🟢 Uji Tahanan Kontak LULUS",
            fail_msg="🟡 Masih terdapat hasil yang belum diterima",
        )
        card_end()
        st.session_state["tahanan_kontak_pmcb"] = hasil_kontak
        autosave_unit("pmcb", "tahanan_kontak_pmcb", hasil_kontak, tab_name="Tahanan Kontak")

    # ==========================================================
    # TAB 3 - UJI KESEREMPAKAN
    # ==========================================================
    with tab3:
        card_begin()
        section_tag("2. Keserempakan")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-stopwatch"></i> '
            "2. Uji Keserempakan</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            alat_ukur_serempak = st.text_input("Alat Ukur", value="DV Power CAT-P", key="alat_serempak")
        with c2:
            standar_serempak = st.text_input("Standard", value="SKDIR 0520", key="standar_serempak")

        table_headers(
            st.columns([1, 1.5, 1.5, 1.5, 1.5]),
            ["Phasa", "Open Time (ms)", "Open Result", "Close Time (ms)", "Close Result"],
        )

        hasil_serempak = []
        serempak_default = [("R", 13.7, 43.8), ("S", 13.5, 43.9), ("T", 13.7, 43.75)]
        for i, (phasa, open_t, close_t) in enumerate(serempak_default):
            c1, c2, c3, c4, c5 = st.columns([1, 1.5, 1.5, 1.5, 1.5])
            with c1:
                row_label(phasa)
            with c2:
                open_time = st.number_input("", value=float(open_t), step=0.1, key=f"open_t_{i}")
            with c3:
                open_result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"open_r_{i}")
            with c4:
                close_time = st.number_input("", value=float(close_t), step=0.1, key=f"close_t_{i}")
            with c5:
                close_result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"close_r_{i}")
            hasil_serempak.append({
                "phasa": phasa,
                "open_time": open_time,
                "open_result": open_result,
                "close_time": close_time,
                "close_result": close_result,
            })

        thin_divider()
        c1, c2 = st.columns(2)
        with c1:
            imax_open = st.text_input("Imax (Open)", value="9.03 A")
            ipmax_open = st.text_input("Ipmax (Open)", value="6.69 A")
        with c2:
            imax_close = st.text_input("Imax (Close)", value="4.52 A")

        thin_divider()
        total_check = len(hasil_serempak) * 2
        sesuai_serempak = sum(
            1 for x in hasil_serempak for r in [x["open_result"], x["close_result"]] if r == "Accepted"
        )
        persen = sesuai_serempak / total_check * 100
        progress_summary(total_check, sesuai_serempak, "Total Pemeriksaan", "Accepted")
        result_status(
            persen,
            "🟢 Uji Keserempakan LULUS",
            fail_msg="🟡 Masih terdapat hasil yang belum diterima",
        )
        card_end()
        st.session_state["keserempakan_pmcb"] = hasil_serempak
        autosave_unit("pmcb", "keserempakan_pmcb", hasil_serempak, tab_name="Keserempakan")

    # ==========================================================
    # TAB 4 - UJI RELAI PENGAMAN
    # ==========================================================
    with tab4:
        card_begin()
        section_tag("3. Relai Pengaman")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-shield"></i> '
            "3. Uji Relai Pengaman</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            alat_ukur_relai = st.text_input("Alat Ukur", value="Ponovo L336i-441", key="alat_relai")
        with c2:
            standar_relai = st.text_input("Standard", value="IEC 60255", key="standar_relai")

        table_headers(
            st.columns([3, 2, 2]),
            ["Item Uji Relay", "Result", "Hasil"],
        )

        relai_items = ["OCR INS", "OCR", "GFR INS", "GFR", "THERMIC"]
        hasil_relai = []
        for i, item in enumerate(relai_items):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                row_label(item)
            with c2:
                result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"relai_{i}")
            with c3:
                if result == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_relai.append({"item": item, "status": result})

        thin_divider()
        sesuai_relai = sum(1 for x in hasil_relai if x["status"] == "Accepted")
        persen = sesuai_relai / len(hasil_relai) * 100
        progress_summary(len(hasil_relai), sesuai_relai, "Total Item", "Accepted")
        result_status(
            persen,
            "🟢 Uji Relai Pengaman LULUS",
            fail_msg="🟡 Masih terdapat item yang belum diterima",
        )
        card_end()
        st.session_state["relai_pengaman_pmcb"] = hasil_relai
        autosave_unit("pmcb", "relai_pengaman_pmcb", hasil_relai, tab_name="Relai Pengaman")

    # ==========================================================
    # TAB 5 - UJI TAHANAN ISOLASI
    # ==========================================================
    with tab5:
        card_begin()
        section_tag("4. Tahanan Isolasi")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-fire-extinguisher"></i> '
            "4. Uji Tahanan Isolasi</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            alat_ukur_isolasi = st.text_input("Alat Ukur", value="Megger Mi20KVe", key="alat_isolasi")
        with c2:
            standar_isolasi = st.text_input("Standard", value="IEC 62271-200 butir 6.2.6.1", key="standar_isolasi")

        table_headers(
            st.columns([3, 1.5, 1.5, 1.5]),
            ["Phasa Yang Diuji", "Posisi PMT", "Hasil Megger", "Status"],
        )

        isolasi_items = [
            ("IN-OUT + Body", "Open"),
            ("R - S + T + Body", "Close"),
            ("S - R + T + Body", "Close"),
            ("T - R + S + Body", "Close"),
        ]
        hasil_isolasi = []
        for i, (phasa, posisi_default) in enumerate(isolasi_items):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])
            with c1:
                row_label(phasa)
            with c2:
                posisi = st.selectbox("", ["Open", "Close"], index=0 if posisi_default == "Open" else 1, key=f"posisi_isolasi_{i}")
            with c3:
                hasil_megger = st.text_input("", value="∞", key=f"megger_{i}")
            with c4:
                status = st.selectbox("", ["Accepted", "Not Accepted"], key=f"status_isolasi_{i}")
                if status == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_isolasi.append({
                "phasa": phasa,
                "posisi_pmt": posisi,
                "hasil_megger": hasil_megger,
                "status": status,
            })

        thin_divider()
        sesuai_isolasi = sum(1 for x in hasil_isolasi if x["status"] == "Accepted")
        persen = sesuai_isolasi / len(hasil_isolasi) * 100
        progress_summary(len(hasil_isolasi), sesuai_isolasi, "Total Pemeriksaan", "Accepted")
        result_status(
            persen,
            "🟢 Uji Tahanan Isolasi LULUS",
            fail_msg="🟡 Masih terdapat hasil yang belum diterima",
        )
        card_end()
        st.session_state["tahanan_isolasi_pmcb"] = hasil_isolasi
        autosave_unit("pmcb", "tahanan_isolasi_pmcb", hasil_isolasi, tab_name="Tahanan Isolasi")

    # ==========================================================
    # TAB 6 - UJI HV
    # ==========================================================
    with tab6:
        card_begin()
        section_tag("5. Uji HV")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-battery-charging"></i> '
            "5. Uji HV</div>",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            alat_ukur_hv = st.text_input("Alat Ukur", value="Automatic Power Regulator 50kV", key="alat_hv")
        with c2:
            standar_hv = st.text_input("Standard", value="SPLN D3.020-1 2019", key="standar_hv")

        table_headers(
            st.columns([3, 1.5, 1.5]),
            ["Phasa", "Posisi PMT", "Result"],
        )

        hv_items = [
            "IN - OUT + Body",
            "IN + OUT - Body",
            "R - S + T + Body",
            "S - R + T + Body",
            "T - R + S + Body",
        ]
        hasil_hv = []
        for i, phasa in enumerate(hv_items):
            c1, c2, c3 = st.columns([3, 1.5, 1.5])
            with c1:
                row_label(phasa)
            with c2:
                st.write("Close")
            with c3:
                result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"hv_{i}")
                if result == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_hv.append({"phasa": phasa, "posisi_pmt": "Close", "status": result})

        thin_divider()
        sesuai_hv = sum(1 for x in hasil_hv if x["status"] == "Accepted")
        persen = sesuai_hv / len(hasil_hv) * 100
        progress_summary(len(hasil_hv), sesuai_hv, "Total Pemeriksaan", "Accepted")
        result_status(
            persen,
            "🟢 Uji HV LULUS",
            fail_msg="🔴 Terdapat hasil uji HV yang belum diterima",
        )
        card_end()
        st.session_state["uji_hv_pmcb"] = hasil_hv
        autosave_unit("pmcb", "uji_hv_pmcb", hasil_hv, tab_name="Uji HV")

    # ==========================================================
    # TAB 7 - TES FUNGSI
    # ==========================================================
    with tab7:
        card_begin()
        section_tag("6. Tes Fungsi")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-gear"></i> '
            "6. Tes Fungsi</div>",
            unsafe_allow_html=True,
        )

        fungsi_items = [
            "Test Fungsi Wiring",
            "Test Fungsi VCB",
            "Test Fungsi Selector Switch",
            "Test Fungsi Push Button Close",
            "Test Fungsi Push Button Open",
            "Lampu indikator Alarm",
            "Lampu Indikator Tegangan R, S, T",
            "Heater",
            "Battery",
            "Test fungsi Relai Indikator box open",
            "Uji CT VT",
        ]

        table_headers(
            st.columns([0.5, 3.5, 1.7, 2.3]),
            ["No", "Item", "Result", "Ket"],
        )

        hasil_fungsi = []
        for i, item in enumerate(fungsi_items, start=1):
            c1, c2, c3, c4 = st.columns([0.5, 3.5, 1.7, 2.3])
            with c1:
                row_no(i)
            with c2:
                row_label(item)
            with c3:
                result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"fungsi_pmcb_{i}")
            with c4:
                default_ket = "Hasil Terlampir" if item == "Uji CT VT" else ""
                ket = st.text_input("", value=default_ket, key=f"ket_fungsi_pmcb_{i}")
            hasil_fungsi.append({"item": item, "status": result, "keterangan": ket})

        thin_divider()
        paraf = st.text_input("Paraf", key="paraf_fungsi_pmcb")

        thin_divider()
        sesuai_fungsi = sum(1 for x in hasil_fungsi if x["status"] == "Accepted")
        persen = sesuai_fungsi / len(hasil_fungsi) * 100
        progress_summary(len(hasil_fungsi), sesuai_fungsi, "Total Item", "Accepted")
        result_status(
            persen,
            "🟢 Tes Fungsi LULUS",
            fail_msg="🟡 Masih terdapat item yang belum diterima",
        )
        card_end()
        st.session_state["tes_fungsi_pmcb"] = hasil_fungsi
        autosave_unit("pmcb", "tes_fungsi_pmcb", hasil_fungsi, tab_name="Tes Fungsi")

    # ==========================================================
    # TAB 8 - KETEBALAN COATING
    # ==========================================================
    with tab8:
        card_begin()
        section_tag("7. Ketebalan Coating")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-palette"></i> '
            "7. Ketebalan Coating</div>",
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            jenis_coating = st.text_input("Jenis Coating", value="Powder Coating", key="jenis_coating_pmcb")
        with c2:
            spek_coating = st.text_input("Spesifikasi", value="min 80 μm", key="spek_coating_pmcb")
        with c3:
            alat_ukur_coating = st.text_input("Alat Ukur", value="Elcometer FNF 456B", key="alat_coating_pmcb")

        table_headers(
            st.columns([2, 2, 1.5]),
            ["Posisi Uji", "Hasil Uji (μm)", "Result"],
        )

        posisi_default = [
            ("Depan", 137), ("Atas", 117), ("Kiri", 137), ("Kanan", 135), ("Belakang", 125)
        ]
        hasil_coating = []
        for i, (posisi, nilai) in enumerate(posisi_default):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            with c1:
                row_label(posisi)
            with c2:
                hasil = st.number_input("", value=float(nilai), step=1.0, key=f"coating_pmcb_{i}")
            status = "Accepted" if hasil >= 80 else "Not Accepted"
            with c3:
                if status == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_coating.append({"posisi": posisi, "nilai": hasil, "status": status})

        thin_divider()
        sesuai_coating = sum(1 for x in hasil_coating if x["status"] == "Accepted")
        persen = sesuai_coating / len(hasil_coating) * 100
        progress_summary(len(hasil_coating), sesuai_coating, "Total Posisi", "Accepted")
        result_status(
            persen,
            "🟢 Ketebalan Coating LULUS",
            fail_msg="🟡 Terdapat posisi dengan ketebalan di bawah spesifikasi",
        )
        card_end()
        st.session_state["ketebalan_coating_pmcb"] = hasil_coating
        autosave_unit("pmcb", "ketebalan_coating_pmcb", hasil_coating, tab_name="Ketebalan Coating")

    # ==========================================================
    # TAB 9 - UJI IP 55
    # ==========================================================
    with tab9:
        card_begin()
        section_tag("8. Uji IP 55")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-box-seam"></i> '
            "8. Uji IP 55</div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### Box Panel Besar")
        box_besar_items = [
            "Pintu 1 / Depan (Engsel, Sealant, Kunci, Baut)",
            "Pintu 2 / Belakang (Engsel, Sealant, Kunci, Baut)",
            "Pintu 3 / Kanan (Engsel, Sealant, Kunci, Baut)",
            "Pintu 4 / Kiri (Engsel, Shield, Kunci, Baut)",
            "Lubang incoming R",
            "Lubang incoming S",
            "Lubang incoming T",
            "Lubang outgoing R",
            "Lubang outgoing S",
            "Lubang outgoing T",
        ]
        hasil_ip55_besar = []

        table_headers(
            st.columns([0.5, 5, 2]),
            ["No", "Box Panel Besar", "Hasil"],
        )

        for i, item in enumerate(box_besar_items, start=1):
            c1, c2, c3 = st.columns([0.5, 5, 2])
            with c1:
                row_no(i)
            with c2:
                row_label(item)
            with c3:
                result = st.selectbox("", ["Accepted", "Not Accepted"], key=f"ip55_besar_{i}")
                if result == "Accepted":
                    badge("Accepted", "ok")
                else:
                    badge("Not Accepted", "bad")
            hasil_ip55_besar.append({"item": item, "status": result})

        thin_divider()
        st.markdown("#### Box Kontrol")
        table_headers(
            st.columns([0.5, 5, 2]),
            ["No", "Box Kontrol", "Hasil"],
        )

        c1, c2, c3 = st.columns([0.5, 5, 2])
        with c1:
            row_no(1)
        with c2:
            row_label("Pintu / Depan (engsel, Sealant, kunci)")
        with c3:
            result_kontrol = st.selectbox("", ["Accepted", "Not Accepted"], key="ip55_kontrol_1")
            if result_kontrol == "Accepted":
                badge("Accepted", "ok")
            else:
                badge("Not Accepted", "bad")
        hasil_ip55_kontrol = [{"item": "Pintu / Depan (engsel, Sealant, kunci)", "status": result_kontrol}]

        thin_divider()
        hasil_ip55_total = hasil_ip55_besar + hasil_ip55_kontrol
        sesuai_ip55 = sum(1 for x in hasil_ip55_total if x["status"] == "Accepted")
        persen = sesuai_ip55 / len(hasil_ip55_total) * 100
        progress_summary(len(hasil_ip55_total), sesuai_ip55, "Total Pemeriksaan", "Accepted")
        result_status(
            persen,
            "🟢 Uji IP 55 LULUS",
            fail_msg="🟡 Masih terdapat item yang belum diterima",
        )
        card_end()
        st.session_state["uji_ip55_pmcb"] = hasil_ip55_total
        autosave_unit("pmcb", "uji_ip55_pmcb", hasil_ip55_total, tab_name="Uji IP 55")

    # ==========================================================
    # TAB 10 - LAMPIRAN / DOKUMENTASI
    # ==========================================================
    with tab10:
        card_begin()
        section_tag("Dokumentasi")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-camera"></i> '
            "9. Dokumentasi</div>",
            unsafe_allow_html=True,
        )
        st.caption("Upload foto dokumentasi unit PMCB")

        info_state = get_active_unit_state("pmcb") or {}
        nama_produk_lampiran = f"PMCB 4.0 — {info_state.get('info', {}).get('merk_vcb', '')} {info_state.get('info', {}).get('type_vcb', '')}".strip()
        nomor_seri_lampiran = st.session_state.get("serial_vcb", info_state.get("info", {}).get("serial_vcb", ""))

        # Foto yang sudah tersimpan sebelumnya untuk unit ini (dari autosave)
        existing_lampiran = (info_state.get("lampiran_pmcb") or {}).get("foto", [])
        existing_valid = [f for f in existing_lampiran if f.get("path") and Path(f["path"]).exists()]

        if existing_valid:
            st.markdown(f"**{len(existing_valid)} foto tersimpan sebelumnya**")
            cols_e = st.columns(3)
            for i, f in enumerate(existing_valid):
                with cols_e[i % 3]:
                    st.image(f["path"], use_container_width=True, caption=f.get("keterangan", f.get("file_name", "")))
            thin_divider()

        uploaded_files = st.file_uploader(
            "Upload Foto Dokumentasi baru (unit PMCB, label, kondisi panel, dsb.)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="lampiran_upload_pmcb",
        )

        new_lampiran = []
        if uploaded_files:
            unit_dir = BASE_DIR / "uploads" / "pmcb" / (nomor_seri_lampiran or "tanpa_nomor_seri")
            unit_dir.mkdir(parents=True, exist_ok=True)
            st.markdown(f"**{len(uploaded_files)} foto baru diunggah**")
            thin_divider()

            cols = st.columns(3)
            for i, file in enumerate(uploaded_files):
                with cols[i % 3]:
                    st.image(file, use_container_width=True)
                    keterangan = st.text_input(
                        "Keterangan",
                        value=file.name,
                        key=f"lampiran_keterangan_pmcb_{i}"
                    )
                save_path = unit_dir / file.name
                with open(save_path, "wb") as out_f:
                    file.seek(0)
                    out_f.write(file.getbuffer())
                new_lampiran.append({
                    "file_name": file.name,
                    "keterangan": keterangan,
                    "path": str(save_path),
                })

        # Gabungkan foto lama + foto baru (nama file sama akan ditimpa versi terbaru)
        merged = {f["file_name"]: f for f in existing_valid}
        for f in new_lampiran:
            merged[f["file_name"]] = f
        hasil_lampiran = list(merged.values())

        if not hasil_lampiran:
            st.info("Belum ada foto yang diunggah")

        st.session_state["lampiran_pmcb"] = {
            "nama_produk": nama_produk_lampiran,
            "nomor_seri": nomor_seri_lampiran,
            "foto": hasil_lampiran,
        }
        if get_active_serial("pmcb"):
            autosave_unit("pmcb", "lampiran_pmcb", st.session_state["lampiran_pmcb"], tab_name="Dokumentasi")
        card_end()

    # ==========================================================
    # TAB 11 - CATATAN
    # ==========================================================
    with tab11:
        card_begin()
        section_tag("Catatan & Pengesahan")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-pencil"></i> '
            "Catatan & Pengesahan</div>",
            unsafe_allow_html=True,
        )

        hasil_pengujian = st.radio("Hasil Pengujian", ["diterima", "ditolak"], horizontal=True, key="hasil_pengujian_pmcb")
        catatan = st.text_area("Catatan", key="catatan_pmcb")
        thin_divider()
        c1, c2 = st.columns(2)
        with c1:
            diperiksa_oleh = st.text_input(
                "Diperiksa (Quality Control)",
                placeholder="Contoh: FAUZAN PRATAMA",
                key="diperiksa_pmcb",
            )
        with c2:
            tanggal_periksa = st.date_input("Tanggal Pemeriksaan", key="tanggal_periksa_pmcb")
        st.session_state["catatan_pengesahan_pmcb"] = {
            "hasil_pengujian": hasil_pengujian,
            "catatan": catatan,
            "diperiksa_oleh": diperiksa_oleh,
        }
        autosave_unit("pmcb", "catatan_pengesahan_pmcb", st.session_state["catatan_pengesahan_pmcb"], tab_name="Catatan")
        if hasil_pengujian == "diterima":
            result_status(100.0, "🟢 Hasil Pengujian: DITERIMA")
        else:
            result_status(0.0, "", fail_msg="🔴 Hasil Pengujian: DITOLAK")
        card_end()

    # ==========================================================
    # TAB 12 - SUMMARY
    # ==========================================================
    with tab12:
        card_begin()
        section_tag("Summary")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-clipboard-data"></i> '
            "Summary Quality Control PMCB 4.0</div>",
            unsafe_allow_html=True,
        )
        st.caption("Rekap keseluruhan hasil pemeriksaan PMCB 4.0")

        summary_data = []
        if "tahanan_kontak_pmcb" in st.session_state:
            data = st.session_state["tahanan_kontak_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Uji Tahanan Kontak", total, sesuai, sesuai / total * 100])
        if "keserempakan_pmcb" in st.session_state:
            data = st.session_state["keserempakan_pmcb"]
            total = len(data) * 2
            sesuai = sum(1 for x in data for r in [x["open_result"], x["close_result"]] if r == "Accepted")
            summary_data.append(["Uji Keserempakan", total, sesuai, sesuai / total * 100])
        if "relai_pengaman_pmcb" in st.session_state:
            data = st.session_state["relai_pengaman_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Uji Relai Pengaman", total, sesuai, sesuai / total * 100])
        if "tahanan_isolasi_pmcb" in st.session_state:
            data = st.session_state["tahanan_isolasi_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Uji Tahanan Isolasi", total, sesuai, sesuai / total * 100])
        if "uji_hv_pmcb" in st.session_state:
            data = st.session_state["uji_hv_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Uji HV", total, sesuai, sesuai / total * 100])
        if "tes_fungsi_pmcb" in st.session_state:
            data = st.session_state["tes_fungsi_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Tes Fungsi", total, sesuai, sesuai / total * 100])
        if "ketebalan_coating_pmcb" in st.session_state:
            data = st.session_state["ketebalan_coating_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Ketebalan Coating", total, sesuai, sesuai / total * 100])
        if "uji_ip55_pmcb" in st.session_state:
            data = st.session_state["uji_ip55_pmcb"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "Accepted")
            summary_data.append(["Uji IP 55", total, sesuai, sesuai / total * 100])

        if summary_data:
            df_summary = pd.DataFrame(summary_data, columns=["Pemeriksaan", "Jumlah Item", "Accepted", "Persentase"])
            df_summary["Persentase"] = df_summary["Persentase"].round(1).astype(str) + " %"
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            nilai = [x[3] for x in summary_data]
            nilai_akhir = sum(nilai) / len(nilai)
            thin_divider()
            qc_score_card(len(summary_data), nilai_akhir)
            catatan_state = st.session_state.get("catatan_pengesahan_pmcb", {})
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
            export_units = get_all_units_for_export("pmcb")
            if not export_units:
                st.info("Tambahkan minimal 1 unit di tab Informasi untuk export PDF.")
            else:
                c_exp1, c_exp2 = st.columns([2, 1])
                with c_exp1:
                    selected_serials = st.multiselect(
                        "Pilih unit untuk diexport:",
                        [u["info"].get("serial_vcb", u["info"].get("nomor_seri", "?")) for u in export_units],
                        default=[u["info"].get("serial_vcb", u["info"].get("nomor_seri", "?")) for u in export_units],
                        key="export_sel_pmcb",
                    )
                with c_exp2:
                    st.caption(f"{len(export_units)} unit tersedia")

                units_to_export = [u for u in export_units if u["info"].get("serial_vcb", u["info"].get("nomor_seri")) in selected_serials]

                logo_path = _find_logo_pln()
                if logo_path:
                    st.caption(f"🖼️ Logo PLN terdeteksi: `{logo_path}`")
                else:
                    st.warning(
                        "⚠️ Logo PLN tidak ditemukan. Letterhead PDF akan pakai teks 'PLN' saja. "
                        f"Taruh file di: `{BASE_DIR / 'assets' / 'logo_pln.png'}`"
                    )

                if units_to_export and st.button("📄 Generate PDF", key="gen_pdf_pmcb", use_container_width=True, type="primary"):
                    pdf_bytes = build_pmcb_pdf(units_to_export, logo_path=str(logo_path) if logo_path else None)
                    filename = f"QC_PMCB_{'_'.join(selected_serials)}.pdf"
                    pdf_download_button(pdf_bytes, filename=filename, label="⬇ Download PDF Laporan")
                    st.success(f"✅ PDF berhasil dibuat untuk {len(units_to_export)} unit!")
        else:
            st.info("Belum ada data pengujian")

        thin_divider()
        render_history_panel("pmcb")
        card_end()
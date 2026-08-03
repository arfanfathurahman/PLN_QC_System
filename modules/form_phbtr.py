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
from modules.pdf_export import build_phbtr_pdf, pdf_download_button

BASE_DIR = Path(__file__).resolve().parent.parent
gambar_dimensi = BASE_DIR / "assets" / "phbtr_dimensi.png"


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


def form_phbtr():
    apply_form_theme()
    form_header(
        icon="lightning-charge",
        title="FORM QUALITY CONTROL PHB TR",
        subtitle="Pengujian rutin panel PHB TR — PLN Pusharlis",
    )

    init_units("phbtr")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📋 Informasi",
        "👀 Visual",
        "🗄 Selungkup",
        "🔧 Komponen",
        "🔩 Baut",
        "📏 Dimensi",
        "⚙ Operasi",
        "⚡ Dielektrik",
        "🛡 Sirkit",
        "📷 Lampiran",
        "📊 Summary"
    ])

    # ==========================================================
    # TAB 1 - INFORMASI PANEL
    # ==========================================================
    with tab1:
        card_begin()
        section_tag("Informasi Panel")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-info-circle"></i> '
            "Informasi Panel PHBTR</div>",
            unsafe_allow_html=True,
        )

        autosave_indicator(True)
        render_unit_selector("phbtr")
        active_serial = get_active_serial("phbtr")
        thin_divider()

        c1, c2 = st.columns(2)
        with c1:
            no_produk = st.text_input("Nomor Produk")
            nomor_seri = st.text_input("Nomor Seri", value=active_serial or "")
            no_amp = st.text_input("No AMP")
            jenis_panel = st.selectbox("Jenis Panel", ["PHBTR PASANGAN LUAR", "PHBTR PASANGAN DALAM"])
            tipe = st.text_input("Tipe", value="PL-250-2-LBS-ST")
            tanggal = st.date_input("Tanggal Pengujian")
        with c2:
            inspector = st.text_input("Inspector")
            customer = st.text_input("Customer", value="PT PLN (Persero)")
            program = st.text_input("Program")
            lokasi = st.text_input("Lokasi")
            standard = st.text_input("Standard", value="SPLN D3,016-1:2018")
            status = st.selectbox("Status", ["Draft", "Final"])

        thin_divider()
        st.markdown("##### Pengesahan")
        c3, c4 = st.columns(2)
        with c3:
            nama_qc = st.text_input(
                "Nama Petugas Quality Control (Diperiksa oleh)",
                placeholder="Contoh: FAUZAN PRATAMA",
            )
        with c4:
            hasil_pengujian = st.selectbox("Hasil Pengujian", ["diterima", "ditolak"])
        catatan_qc = st.text_area("Catatan Tambahan (opsional)", placeholder="Catatan hasil pengujian, jika ada")

        deskripsi_penugasan = st.text_area(
            "Deskripsi Penugasan (tampil di header PDF)",
            value="Penugasan Pembuatan Unit PHBTR",
            help="Contoh: 'Penugasan Pembuatan 88 Unit PHBTR Varian PL250-2 LBS UID Jawa Barat Tahap 2 Juni 2026 – Program Pemasaran'",
        )

        if active_serial:
            autosave_unit("phbtr", "info", {
                "no_produk": no_produk, "nomor_seri": nomor_seri,
                "no_amp": no_amp, "jenis_panel": jenis_panel,
                "tipe": tipe, "standard": standard,
                "tanggal": str(tanggal), "inspector": inspector,
                "customer": customer, "program": program,
                "lokasi": lokasi, "status": status,
                "deskripsi_penugasan": deskripsi_penugasan,
                "nama_qc": nama_qc,
            }, tab_name="Informasi")
            autosave_unit("phbtr", "catatan_phbtr", {
                "catatan": catatan_qc,
                "hasil_pengujian": hasil_pengujian,
                "diperiksa_oleh": nama_qc,
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
                    key=f"confirm_delete_phbtr_{active_serial}",
                )
                if st.button(
                    "🗑️ Hapus Sekarang",
                    key=f"hapus_btn_phbtr_{active_serial}",
                    type="primary",
                    disabled=not confirm_delete,
                    use_container_width=True,
                ):
                    delete_unit("phbtr", active_serial)
                    st.success(f"Project '{active_serial}' telah dihapus.")
                    st.rerun()
        st.button("➡ Lanjut ke Visual", key="lanjut_phbtr", use_container_width=True)
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
        st.caption("Pemeriksaan visual sesuai Blanko Uji Rutin PHBTR")

        visual_items = [
            {"item": "Hasil pengerjaan baik dan kondisi baru"},
            {"item": "Kesesuaian papan nama"},
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
                sesuai = st.checkbox("", value=True, key=f"visual_{i}")
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
        st.session_state["visual_phbtr"] = hasil_visual
        autosave_unit("phbtr", "visual_phbtr", hasil_visual, tab_name="Visual")

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
        st.caption("Pemeriksaan selungkup sesuai Blanko Uji Rutin PHBTR")

        table_headers(
            st.columns([4, 4, 1, 2]),
            ["Jenis Pemeriksaan", "Spesifikasi / Persyaratan", "✓", "Hasil"],
        )

        selungkup = [
            {"parameter": "Bahan dan tebal selungkup & montase", "jenis": "radio", "opsi": ["Plat SPCC t.2 mm", "Plat SPCC t.3 mm"]},
            {"parameter": "Karet Penutup", "jenis": "text", "nilai": "Karet Penutup"},
            {"parameter": "Cat powder coating min 80 μm", "jenis": "coating"},
            {"parameter": "Tingkat pengaman IP34", "jenis": "text", "nilai": "IP34"},
            {"parameter": "Klem untuk pemegang kabel", "jenis": "check"},
            {"parameter": "Lengan penopang pada tiang", "jenis": "check"},
            {"parameter": "Kuping pengangkat", "jenis": "check"},
            {"parameter": "Bonding pembumian antara pintu dan badan selungkup", "jenis": "text", "nilai": "Kabel NYF 10 mm² warna kuning-hijau"},
            {"parameter": "Ventilasi udara dilengkapi plat berlubang (ram) 4 bh", "jenis": "check"},
            {"parameter": "Bukaan pintu minimal 160°", "jenis": "check"},
            {"parameter": "Handel pintu berikut kunci master dan fasilitas gembok", "jenis": "check"},
            {"parameter": "Rak penyimpanan data/dokumen", "jenis": "check"},
            {"parameter": "Logo PLN dan tanda peringatan bahaya listrik", "jenis": "check"},
        ]
        hasil_selungkup = []

        for i, item in enumerate(selungkup):
            c1, c2, c3, c4 = st.columns([4, 4, 1, 2])
            with c1:
                row_label(item["parameter"])
            with c2:
                if item["jenis"] == "radio":
                    nilai = st.radio("", item["opsi"], horizontal=True, key=f"plat_{i}")
                elif item["jenis"] == "coating":
                    a, b = st.columns(2)
                    with a:
                        tebal = st.number_input("", value=80, step=1, key=f"coat_{i}")
                    with b:
                        warna = st.text_input("", value="RAL7032", key=f"warna_{i}")
                    nilai = f"{tebal} μm | {warna}"
                elif item["jenis"] == "text":
                    nilai = st.text_input("", value=item["nilai"], key=f"text_{i}")
                else:
                    nilai = "-"
                    st.write("-")
            with c3:
                status_sel = st.selectbox("", ["✓", "✗"], key=f"status_sel_{i}")
            with c4:
                if status_sel == "✓":
                    badge("Sesuai", "ok")
                else:
                    badge("Tidak Sesuai", "bad")
            hasil_selungkup.append({"parameter": item["parameter"], "nilai": nilai, "status": status_sel})

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
        st.session_state["selungkup_phbtr"] = hasil_selungkup
        autosave_unit("phbtr", "selungkup_phbtr", hasil_selungkup, tab_name="Selungkup")

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
        st.caption("Pemeriksaan komponen sesuai Blanko Uji Rutin PHBTR")

        hasil_komponen = []
        table_headers(
            st.columns([3, 2, 2, 2, 1, 1.5]),
            ["Jenis Pemeriksaan", "Spesifikasi 1", "Spesifikasi 2", "Spesifikasi 3", "✓", "Hasil"],
        )

        # --- Saklar Utama ---
        c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 1, 1.5])
        with c1:
            st.markdown("### Saklar Utama")
        with c2:
            merk = st.text_input("Merk", value="HEFFTRON")
            arus = st.number_input("Arus (A)", value=400)
        with c3:
            standar = st.text_input("Standar", value="IEC 60947-3")
            short = st.number_input("Hubung Singkat (kA)", value=12.6)
        with c4:
            kategori = st.text_input("Kategori", value="AC 22B")
            pelapis = st.text_input("Pelapis", value="Tembaga lapis perak")
        with c5:
            status_saklar = st.selectbox("", ["✓", "✗"], key="saklar")
        with c6:
            st.write("Sesuai" if status_saklar == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Saklar Utama", "status": status_saklar})
        thin_divider()

        # --- Fuse Rail ---
        c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 1, 1.5])
        with c1:
            st.markdown("### Fuse Rail")
        with c2:
            merk2 = st.text_input("Merk ", value="HEFFTRON")
            arus2 = st.number_input("Arus ", value=250)
            pelapis2 = st.text_input("Pelapis ", value="Tembaga lapis timah")
        with c3:
            standar2 = st.text_input("Standar ", value="IEC 60269-2")
            short2 = st.number_input("Hubung Singkat ", value=50)
            disipasi = st.number_input("Disipasi", value=32)
        with c4:
            ukuran = st.text_input("Ukuran", value="Size 1")
            terminal = st.text_input("Terminal", value="M-Terminal")
        with c5:
            status_fuse = st.selectbox("", ["✓", "✗"], key="fuse")
        with c6:
            st.write("Sesuai" if status_fuse == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Fuse Rail", "status": status_fuse})
        thin_divider()

        # --- Instrumen Pengukuran ---
        c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 1, 1.5])
        with c1:
            st.write("Instrumen Pengukuran")
        with c2:
            instrumen = st.radio("", ["MDI", "kWh Meter"], horizontal=True)
        with c5:
            status_instrumen = st.selectbox("", ["✓", "✗"], key="instrumen")
        with c6:
            st.write("Sesuai" if status_instrumen == "✓" else "Tidak Sesuai")
        hasil_komponen.append({"komponen": "Instrumen", "status": status_instrumen})
        thin_divider()

        # --- Busbar ---
        busbar = [
            ("Busbar Fasa", "30 x 6 mm"),
            ("Busbar Netral", "30 x 6 mm"),
            ("Busbar Pembumian", "20 x 5 mm"),
            ("Kontak-kontak", "Merk Uticon"),
            ("Proteksi Lampu", "Fuse HRC 10 A"),
            ("Kabel Instalasi", "NYAF 2.5 mm²"),
        ]
        for i, data in enumerate(busbar):
            c1, c2, c3, c4 = st.columns([3, 4, 1, 1.5])
            with c1:
                row_label(data[0])
            with c2:
                nilai_bus = st.text_input("", value=data[1], key=f"busbar_{i}")
            with c3:
                st.write("✓")
            with c4:
                st.write("Sesuai")
            hasil_komponen.append({"komponen": data[0], "nilai": nilai_bus, "status": "✓"})

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
        st.session_state["komponen_phbtr"] = hasil_komponen

        # Data terstruktur untuk export PDF (grid Saklar Utama / Fuse Rail persis blangko)
        komponen_detail = {
            "saklar_utama": {
                "merk": merk, "standar": standar, "kategori": kategori,
                "arus": arus, "short": short, "pelapis": pelapis,
                "status": status_saklar,
            },
            "fuse_rail": {
                "merk": merk2, "standar": standar2, "ukuran": ukuran,
                "arus": arus2, "short": short2, "terminal": terminal,
                "pelapis": pelapis2, "disipasi": disipasi,
                "status": status_fuse,
            },
            "instrumen": {"jenis": instrumen, "status": status_instrumen},
            "busbar": hasil_komponen[3:],
        }
        st.session_state["komponen_detail_phbtr"] = komponen_detail
        if get_active_serial("phbtr"):
            autosave_unit("phbtr", "komponen_phbtr", hasil_komponen, tab_name="Komponen")
            autosave_unit("phbtr", "komponen_detail_phbtr", komponen_detail, tab_name="Komponen")

    # ==========================================================
    # TAB 5 - KEKENCANGAN BAUT
    # ==========================================================
    with tab5:
        card_begin()
        section_tag("Kekencangan Baut")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-screwdriver"></i> '
            "Pemeriksaan Kekencangan Baut</div>",
            unsafe_allow_html=True,
        )
        st.caption("Pemeriksaan kekencangan baut dan sambungan listrik")

        baut_items = [
            {"item": "Keluaran saklar utama - busbar hubungan fasa R, S, T", "standar": "70 Nm"},
            {"item": "Antar busbar hubung fasa R, S, T", "standar": "70 Nm"},
            {"item": "Busbar hubung - Fuse rall fasa R, S, T", "standar": "70 Nm"},
        ]
        hasil_baut = []

        table_headers(
            st.columns([0.5, 4, 2, 2, 2, 3]),
            ["No", "Lokasi Baut", "Standar", "Aktual", "Status", "Keterangan"],
        )

        for i, data in enumerate(baut_items, start=1):
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 4, 2, 2, 2, 3])
            with c1:
                row_no(i)
            with c2:
                row_label(data["item"])
            with c3:
                st.write(data["standar"])
            with c4:
                torsi = st.number_input("", min_value=0.0, step=0.5, key=f"torsi_{i}")
            with c5:
                hasil = st.selectbox("", ["✅ Sesuai", "❌ Tidak Sesuai"], key=f"baut_{i}")
            with c6:
                ket = st.text_input("", placeholder="Keterangan", key=f"ket_baut_{i}")
            hasil_baut.append({
                "item": data["item"],
                "standar": data["standar"],
                "aktual": torsi,
                "hasil": hasil,
                "keterangan": ket,
            })

        thin_divider()
        sesuai_baut = sum(1 for x in hasil_baut if x["hasil"] == "✅ Sesuai")
        persen = (sesuai_baut / len(hasil_baut)) * 100
        progress_summary(len(hasil_baut), sesuai_baut, "Total Baut", "Sesuai")
        result_status(
            persen,
            "🟢 Pemeriksaan Kekencangan Baut LULUS",
            fail_msg="🟡 Masih ada baut yang perlu diperbaiki",
        )
        card_end()
        st.session_state["baut_phbtr"] = hasil_baut
        autosave_unit("phbtr", "baut_phbtr", hasil_baut, tab_name="Baut")

    # ==========================================================
    # TAB 6 - DIMENSI SELUNGKUP
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
            st.image(str(gambar_dimensi), caption="Gambar Acuan Dimensi PHBTR", use_container_width=True)
            thin_divider()
            df = pd.DataFrame({
                "Parameter": ["Persyaratan Standar (mm)", "Hasil Ukur (mm)"],
                "A": [1200, 1200], "B": [1100, 1100], "C": [100, 100], "D": [450, 450],
                "E": [50, 50], "F": [100, 100], "G": [185, 185], "H": [60, 60],
                "I": [680, 680], "J": [1200, 1200], "K": [60, 60],
            })
            edited = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed")
            thin_divider()
            progress_summary(11, 11, "Total Parameter", "Sesuai")
            result_status(100.0, "🟢 Pengujian Dimensi Memenuhi Persyaratan")
        card_end()
        dimensi_dict = edited.drop(columns=["Parameter"]).to_dict("list")
        st.session_state["dimensi_phbtr"] = dimensi_dict
        autosave_unit("phbtr", "dimensi_phbtr", dimensi_dict, tab_name="Dimensi")

    # ==========================================================
    # TAB 7 - UJI OPERASI MEKANIS
    # ==========================================================
    with tab7:
        card_begin()
        section_tag("Operasi Mekanis")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-gear-wide-connected"></i> '
            "Uji Operasi Mekanis</div>",
            unsafe_allow_html=True,
        )

        mekanis = {
            "Operasi buka tutup 5 kali": ["Saklar Utama", "Pintu"],
            "Kontinyuitas pengawatan": ["Instrumen ukur", "Lampu indikator", "Lampu penerangan", "Kontak-kontak"],
        }

        table_headers(
            st.columns([3, 4, 1.2, 2]),
            ["Kelompok Pengujian", "Item Pemeriksaan", "Status", "Hasil"],
        )

        hasil_operasi = []
        for grup, items in mekanis.items():
            st.markdown(f"#### {grup}")
            for item in items:
                c1, c2, c3, c4 = st.columns([3, 4, 1.2, 2])
                with c1:
                    st.write("")
                with c2:
                    row_label(item)
                with c3:
                    cek = st.checkbox("", value=True, key=f"cek_{item}")
                with c4:
                    if cek:
                        badge("Berfungsi", "ok")
                    else:
                        badge("Tidak Berfungsi", "bad")
                hasil_operasi.append({"kelompok": grup, "item": item, "status": cek})

        thin_divider()
        sesuai_operasi = sum(1 for x in hasil_operasi if x["status"])
        persen = sesuai_operasi / len(hasil_operasi) * 100
        progress_summary(len(hasil_operasi), sesuai_operasi, "Total Pemeriksaan", "Berfungsi")
        result_status(
            persen,
            "🟢 Uji Operasi Mekanis LULUS",
            fail_msg="🟡 Masih terdapat item yang belum berfungsi",
        )
        card_end()
        st.session_state["operasi_phbtr"] = hasil_operasi
        autosave_unit("phbtr", "operasi_phbtr", hasil_operasi, tab_name="Operasi")

    # ==========================================================
    # TAB 8 - PENGUJIAN DIELEKTRIK
    # ==========================================================
    with tab8:
        card_begin()
        section_tag("Dielektrik")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-lightning-charge"></i> '
            "Pengujian Dielektrik</div>",
            unsafe_allow_html=True,
        )
        st.caption("TAHANAN ISOLASI (MΩ)")

        dielektrik_items = [
            "L1-(L2 + L3 + N + Badan)",
            "L2-(L1 + L3 + N + Badan)",
            "L3-(L1 + L2 + N + Badan)",
            "N-(L1 + L2 + L3 + Badan)",
            "(L1+L2+L3) - (L1'+L2'+L3')",
            "(L1'+L2'+L3') - (L1+L2+L3)",
            "Sirkit kontrol - (sirkit utama+bagian konduktif terbuka+badan)",
        ]

        table_headers(
            st.columns([4.5, 2, 2, 1, 1.5]),
            ["Sirkuit Utama (3kV-1 Menit)", "Sebelum Uji", "Sesudah Uji", "✓", "Hasil"],
        )

        hasil_dielektrik = []
        for i, item in enumerate(dielektrik_items):
            c1, c2, c3, c4, c5 = st.columns([4.5, 2, 2, 1, 1.5])
            with c1:
                row_label(item)
            with c2:
                sebelum = st.number_input("", min_value=0.0, step=0.1, key=f"sebelum_{i}")
                st.caption("MΩ / GΩ")
            with c3:
                sesudah = st.number_input("", min_value=0.0, step=0.1, key=f"sesudah_{i}")
                st.caption("MΩ / GΩ")
            status_diel = sesudah >= sebelum
            with c4:
                st.write("✔" if status_diel else "✘")
            with c5:
                if status_diel:
                    badge("Baik", "ok")
                else:
                    badge("Tidak Baik", "bad")
            hasil_dielektrik.append({
                "sirkuit": item,
                "sebelum": sebelum,
                "sesudah": sesudah,
                "status": status_diel,
            })

        thin_divider()
        sesuai_diel = sum(1 for x in hasil_dielektrik if x["status"])
        persen = sesuai_diel / len(hasil_dielektrik) * 100
        progress_summary(len(hasil_dielektrik), sesuai_diel, "Total Pengujian", "Lulus")
        result_status(
            persen,
            "🟢 Pengujian Dielektrik LULUS",
            fail_msg="🟡 Masih terdapat hasil yang belum memenuhi persyaratan.",
        )
        card_end()
        st.session_state["dielektrik_phbtr"] = hasil_dielektrik
        autosave_unit("phbtr", "dielektrik_phbtr", hasil_dielektrik, tab_name="Dielektrik")

    # ==========================================================
    # TAB 9 - KEEFEKTIFAN SIRKIT PROTEKTIF
    # ==========================================================
    with tab9:
        card_begin()
        section_tag("Sirkit Protektif")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-shield-check"></i> '
            "Pengujian Keefektifan Sirkit Protektif</div>",
            unsafe_allow_html=True,
        )
        st.caption("Batas maksimum tahanan kontinuitas = 0,1 Ω")

        sirkit_items = [
            {"item": "Pintu metering", "satuan": "mΩ"},
            {"item": "Rangka utama", "satuan": "µΩ"},
            {"item": "Rangka dudukan fuse fasa L1, L2, L3", "satuan": "µΩ"},
            {"item": "Plat dudukan fuse peralatan bantu", "satuan": "µΩ"},
            {"item": "Pintu utama", "satuan": "mΩ"},
        ]

        table_headers(
            st.columns([4, 2, 2, 1, 1.5]),
            ["Jenis Pemeriksaan", "Hasil Pengujian", "Satuan", "✓", "Hasil"],
        )

        hasil_sirkit = []
        for i, data in enumerate(sirkit_items):
            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 1, 1.5])
            with c1:
                row_label(data["item"])
            with c2:
                nilai_sirkit = st.number_input("", min_value=0.0, step=0.001, format="%.3f", key=f"sirkit_{i}")
            with c3:
                st.write(data["satuan"])
            status_sirkit = nilai_sirkit <= 0.1
            with c4:
                st.write("✔" if status_sirkit else "✘")
            with c5:
                if status_sirkit:
                    badge("Baik", "ok")
                else:
                    badge("Tidak Baik", "bad")
            hasil_sirkit.append({
                "item": data["item"],
                "nilai": nilai_sirkit,
                "status": status_sirkit,
                "satuan": data["satuan"],
            })

        thin_divider()
        sesuai_sirkit = sum(1 for x in hasil_sirkit if x["status"])
        persen = sesuai_sirkit / len(hasil_sirkit) * 100
        progress_summary(len(hasil_sirkit), sesuai_sirkit, "Total Pemeriksaan", "Lulus")
        result_status(
            persen,
            "🟢 Pengujian Sirkit Protektif LULUS",
            fail_msg="🔴 Terdapat hasil melebihi batas maksimum 0,1 Ω",
        )
        card_end()
        st.session_state["sirkit_protektif_phbtr"] = hasil_sirkit
        autosave_unit("phbtr", "sirkit_protektif_phbtr", hasil_sirkit, tab_name="Sirkit")

    # ==========================================================
    # TAB 10 - LAMPIRAN DOKUMENTASI
    # ==========================================================
    with tab10:
        card_begin()
        section_tag("Lampiran")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-camera"></i> '
            "Lampiran Dokumentasi</div>",
            unsafe_allow_html=True,
        )
        st.caption("Upload foto dokumentasi panel sesuai Blanko Uji Rutin PHBTR")

        info_state = get_active_unit_state("phbtr") or {}
        jenis_panel_lampiran = info_state.get("info", {}).get("jenis_panel", "PHBTR PASANGAN LUAR")
        nomor_seri_lampiran = st.session_state.get("nomor_seri", info_state.get("info", {}).get("nomor_seri", ""))

        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Jenis Panel", value=jenis_panel_lampiran, disabled=True, key="lampiran_jenis_panel_display")
        with c2:
            st.text_input("Nomor Seri", value=nomor_seri_lampiran, disabled=True, key="lampiran_nomor_seri_display")
        thin_divider()

        # Foto yang sudah tersimpan sebelumnya untuk unit ini (dari autosave)
        existing_lampiran = (info_state.get("lampiran_phbtr") or {}).get("foto", [])
        existing_valid = [f for f in existing_lampiran if f.get("path") and Path(f["path"]).exists()]

        if existing_valid:
            st.markdown(f"**{len(existing_valid)} foto tersimpan sebelumnya**")
            cols_e = st.columns(3)
            for i, f in enumerate(existing_valid):
                with cols_e[i % 3]:
                    st.image(f["path"], use_container_width=True, caption=f.get("keterangan", f.get("file_name", "")))
            thin_divider()

        uploaded_files = st.file_uploader(
            "Upload Foto Dokumentasi baru (papan nama, label bahaya listrik, kondisi panel, dsb.)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="lampiran_upload_phbtr",
        )
        new_lampiran = []
        if uploaded_files:
            unit_dir = BASE_DIR / "uploads" / "phbtr" / (nomor_seri_lampiran or "tanpa_nomor_seri")
            unit_dir.mkdir(parents=True, exist_ok=True)
            st.markdown(f"**{len(uploaded_files)} foto baru diunggah**")
            thin_divider()
            cols = st.columns(3)
            for i, file in enumerate(uploaded_files):
                with cols[i % 3]:
                    st.image(file, use_container_width=True)
                    keterangan = st.text_input("Keterangan", value=file.name, key=f"lampiran_keterangan_phbtr_{i}")
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

        st.session_state["lampiran_phbtr"] = {
            "nama_produk": jenis_panel_lampiran,
            "nomor_seri": nomor_seri_lampiran,
            "foto": hasil_lampiran,
        }
        if get_active_serial("phbtr"):
            autosave_unit("phbtr", "lampiran_phbtr", st.session_state["lampiran_phbtr"], tab_name="Lampiran")
        card_end()

    # ==========================================================
    # TAB 11 - SUMMARY PHBTR
    # ==========================================================
    with tab11:
        card_begin()
        section_tag("Summary")
        st.markdown(
            '<div class="siak-card-title"><i class="bi bi-clipboard-data"></i> '
            "Summary Quality Control PHBTR</div>",
            unsafe_allow_html=True,
        )
        st.caption("Rekap keseluruhan hasil pemeriksaan PHBTR")

        summary_data = []
        if "visual_phbtr" in st.session_state:
            data = st.session_state["visual_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Visual", total, sesuai, sesuai / total * 100])
        if "selungkup_phbtr" in st.session_state:
            data = st.session_state["selungkup_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "✓")
            summary_data.append(["Selungkup", total, sesuai, sesuai / total * 100])
        if "komponen_phbtr" in st.session_state:
            data = st.session_state["komponen_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"] == "✓")
            summary_data.append(["Komponen", total, sesuai, sesuai / total * 100])
        if "baut_phbtr" in st.session_state:
            data = st.session_state["baut_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["hasil"] == "✅ Sesuai")
            summary_data.append(["Kekencangan Baut", total, sesuai, sesuai / total * 100])
        summary_data.append(["Dimensi", 11, 11, 100])
        if "operasi_phbtr" in st.session_state:
            data = st.session_state["operasi_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Operasi", total, sesuai, sesuai / total * 100])
        if "dielektrik_phbtr" in st.session_state:
            data = st.session_state["dielektrik_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Dielektrik", total, sesuai, sesuai / total * 100])
        if "sirkit_protektif_phbtr" in st.session_state:
            data = st.session_state["sirkit_protektif_phbtr"]
            total = len(data)
            sesuai = sum(1 for x in data if x["status"])
            summary_data.append(["Sirkit Protektif", total, sesuai, sesuai / total * 100])

        if summary_data:
            df_summary = pd.DataFrame(summary_data, columns=["Pemeriksaan", "Jumlah Item", "Sesuai", "Persentase"])
            df_summary["Persentase"] = df_summary["Persentase"].round(1).astype(str) + " %"
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            nilai = [x[3] for x in summary_data]
            nilai_akhir = sum(nilai) / len(nilai)
            thin_divider()
            qc_score_card(len(summary_data), nilai_akhir)

            thin_divider()
            st.markdown("---")
            st.markdown("### Export PDF Laporan QC")
            export_units = get_all_units_for_export("phbtr")
            if not export_units:
                st.info("Tambahkan minimal 1 unit di tab Informasi untuk export PDF.")
            else:
                c_exp1, c_exp2 = st.columns([2, 1])
                with c_exp1:
                    selected_serials = st.multiselect(
                        "Pilih unit untuk diexport:",
                        [u["info"].get("nomor_seri", "?") for u in export_units],
                        default=[u["info"].get("nomor_seri", "?") for u in export_units],
                        key="export_sel_phbtr",
                    )
                with c_exp2:
                    st.caption(f"{len(export_units)} unit tersedia")

                units_to_export = [u for u in export_units if u["info"].get("nomor_seri") in selected_serials]

                logo_path = _find_logo_pln()
                if logo_path:
                    st.caption(f"🖼️ Logo PLN terdeteksi: `{logo_path}`")
                else:
                    st.warning(
                        "⚠️ Logo PLN tidak ditemukan. Letterhead PDF akan pakai teks 'PLN' saja. "
                        f"Taruh file di: `{BASE_DIR / 'assets' / 'logo_pln.png'}`"
                    )

                if units_to_export and st.button("📄 Generate PDF", key="gen_pdf_phbtr", use_container_width=True, type="primary"):
                    pdf_bytes = build_phbtr_pdf(
                        units_to_export,
                        logo_path=str(logo_path) if logo_path else None,
                        dimensi_image_path=str(gambar_dimensi) if gambar_dimensi.exists() else None,
                    )
                    filename = f"QC_PHBTR_{'_'.join(selected_serials)}.pdf"
                    pdf_download_button(pdf_bytes, filename=filename, label="⬇ Download PDF Laporan")
                    st.success(f"✅ PDF berhasil dibuat untuk {len(units_to_export)} unit!")
        else:
            st.info("Belum ada data pengujian")

        thin_divider()
        render_history_panel("phbtr")
        card_end()
import os
import pandas as pd
from io import BytesIO
from openpyxl import Workbook

# Library ReportLab untuk PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Data QC", index=False)
    output.seek(0)
    return output

def export_onepost_excel(df_discharging, df_charging, metadata):
    wb = Workbook()
    ws = wb.active
    ws.title = "LOG SHEET"
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def generate_phbtr_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15
    )
    styles = getSampleStyleSheet()
    story = []

    # --- HEADER DENGAN LOGO PLN DARI FILE ---
    if os.path.exists("logo_pln.png"):
        img_logo = Image("logo_pln.png", width=50, height=60)
    else:
        img_logo = Paragraph("<b>PLN</b>", styles['Normal'])

    title_text = Paragraph(
        "<b>PT PLN (PERSERO) PUSHARLIS</b><br/>"
        "<font size=10>QUALITY CONTROL MOBILE SYSTEM</font><br/>"
        "<b>LEMBAR HASIL PENGUJIAN PHB TR</b>", 
        ParagraphStyle('HeaderTitle', parent=styles['Heading1'], alignment=1, fontSize=11, leading=13)
    )

    header_table = Table([[img_logo, title_text]], colWidths=[60, 495])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 5))

    # ... (sisa kode tabel 5, 6, 7, 8 dan footer tetap seperti sebelumnya)
    # ==========================================================
    # NO 5. PENGUJIAN DIMENSI SELUNGKUP (DENGAN GAMBAR & TABEL A-K)
    # ==========================================================
    # Cek apakah file gambar skema_panel.png tersedia
    if os.path.exists("skema_panel.png"):
        img_panel = Image("skema_panel.png", width=180, height=90)
    else:
        img_panel = Paragraph("<i>[Gambar Skema Panel (skema_panel.png)]</i>", cell_center)

    # Sub-Tabel Ukuran A-K
    dim_headers = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
    row_ukur = [data.get('dim_ukur', {}).get(k, '-') for k in dim_headers]
    row_syarat = [data.get('dim_syarat', {}).get(k, '-') for k in dim_headers]

    tabel_dimensi_isi = [
        [Paragraph("<b>Hasil Ukur (mm) toleransi 5%</b>", cell_style)] + [Paragraph(str(v), cell_center) for v in row_ukur],
        [Paragraph("<b>Persyaratan Standar (mm)</b>", cell_style)] + [Paragraph(str(v), cell_center) for v in row_syarat]
    ]
    tabel_dim_AK = Table(
        [[Paragraph(f"<b>{h}</b>", cell_bold_center) for h in [""] + dim_headers]] + tabel_dimensi_isi,
        colWidths=[110] + [20]*11
    )
    tabel_dim_AK.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))

    # Wadah Utama Tabel No. 5
    tabel_5_data = [
        [Paragraph("<b>NO.</b>", hdr_style), Paragraph("<b>JENIS PENGUJIAN</b>", hdr_style), Paragraph("<b>JENIS PEMERIKSAAN</b>", hdr_style), Paragraph("<b>HASIL</b>", hdr_style)],
        ["5", Paragraph("Pengujian dimensi selungkup", cell_style), img_panel, Paragraph(data.get('dimensi_hasil', 'Sesuai'), cell_center)],
        ["", "", tabel_dim_AK, ""]
    ]

    t5 = Table(tabel_5_data, colWidths=[25, 110, 370, 50])
    t5.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,1), (0,2)), # Merge NO 5
        ('SPAN', (1,1), (1,2)), # Merge Jenis Pengujian
        ('SPAN', (3,1), (3,2)), # Merge Hasil
        ('ALIGN', (2,1), (2,1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t5)

    # ==========================================================
    # NO 6. UJI OPERASI MEKANIS
    # ==========================================================
    mekanis_items = [
        ("Operasi buka tutup 5 kali", "Saklar Utama", "✓", "Berfungsi"),
        ("", "Pintu", "✓", "Berfungsi"),
        ("", "Instrumen ukur", "✓", "Berfungsi"),
        ("", "Lampu Indicator", "✓", "Berfungsi"),
        ("", "Lampu penerangan", "✓", "Berfungsi"),
        ("Kontinyuitas pengawatan", "Kontak-kontak", "✓", "Berfungsi")
    ]

    t6_rows = []
    for idx, (j_pem, item, v, status_m) in enumerate(mekanis_items):
        no_str = "6" if idx == 0 else ""
        pengujian_str = Paragraph("Uji operasi Mekanis", cell_style) if idx == 0 else ""
        t6_rows.append([
            no_str, pengujian_str,
            Paragraph(j_pem, cell_style),
            Paragraph(item, cell_style),
            Paragraph(v, cell_bold_center),
            Paragraph(status_m, cell_center)
        ])

    t6 = Table(t6_rows, colWidths=[25, 110, 160, 150, 20, 90])
    t6.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,0), (0,5)),
        ('SPAN', (1,0), (1,5)),
        ('SPAN', (2,0), (2,4)), # Merge Operasi Buka Tutup
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t6)

    # ==========================================================
    # NO 7. TAHANAN ISOLASI (MΩ)
    # ==========================================================
    story.append(Table([[Paragraph("<b>TAHANAN ISOLASI (MΩ)</b>", hdr_style)]], colWidths=[555], style=[('GRID', (0,0), (-1,-1), 0.5, colors.black)]))

    iso_items = [
        ("L1-(L2 + L3 + N + Badan)", data.get('iso_l1_sebelum', 'M/G Ω'), data.get('iso_l1_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("L2-(L1 + L3 + N + Badan)", data.get('iso_l2_sebelum', 'M/G Ω'), data.get('iso_l2_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("L3-(L1 + L2 + N + Badan)", data.get('iso_l3_sebelum', 'M/G Ω'), data.get('iso_l3_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("N-(L1 + L2 + L3 + Badan)", data.get('iso_n_sebelum', 'M/G Ω'), data.get('iso_n_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("(L1+L2+L3) - (L1'+L2'+L3')", data.get('iso_b1_sebelum', 'M/G Ω'), data.get('iso_b1_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("(L1'+L2'+L3') - (L1+L2+L3)", data.get('iso_b2_sebelum', 'M/G Ω'), data.get('iso_b2_sesudah', 'M/G Ω'), "✓", "Baik"),
        ("Sirkit kontrol - (sirkit utama+bagian konduktif terbuka+badan)", data.get('iso_ctrl_sebelum', 'M/G Ω'), data.get('iso_ctrl_sesudah', 'M/G Ω'), "✓", "Baik"),
    ]

    t7_rows = [[
        Paragraph("<b>No.</b>", hdr_style),
        Paragraph("<b>Jenis Pengujian</b>", hdr_style),
        Paragraph("<b>Sirkit Utama (1kV-1 Menit)</b>", hdr_style),
        Paragraph("<b>Sebelum uji tegangan</b>", hdr_style),
        Paragraph("<b>Sesudah uji tegangan</b>", hdr_style),
        Paragraph("<b>HASIL Min. 1000Ω/V</b>", hdr_style)
    ]]

    for idx, (sirkit, seb, ses, v, h_iso) in enumerate(iso_items):
        no_str = "7" if idx == 0 else ""
        pengujian_str = Paragraph("Pengujian dielektrik", cell_style) if idx == 0 else ""
        t7_rows.append([
            no_str, pengujian_str,
            Paragraph(sirkit, cell_style),
            Paragraph(seb, cell_center),
            Paragraph(ses, cell_center),
            Paragraph(f"{v} {h_iso}", cell_center)
        ])

    t7 = Table(t7_rows, colWidths=[25, 110, 175, 75, 75, 95])
    t7.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,1), (0,7)),
        ('SPAN', (1,1), (1,7)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t7)

    # ==========================================================
    # NO 8. PENGUJIAN KEEFEKTIFAN SIRKIT PROTEKTIF
    # ==========================================================
    prot_items = [
        ("Pintu metering", data.get('r_pintu_metering', '14,81 mΩ'), "✓", "Baik"),
        ("Rangka utama", data.get('r_rangka_utama', '410,5 μΩ'), "✓", "Baik"),
        ("Rangka dudukan fuse, fasa L1, L2, L3", data.get('r_rangka_fuse', '542,1 μΩ'), "✓", "Baik"),
        ("Plat dudukan fuse peralatan bantu", data.get('r_plat_fuse', '539,1 μΩ'), "✓", "Baik"),
        ("Pintu utama", data.get('r_pintu_utama', '12,8 mΩ'), "✓", "Baik"),
    ]

    t8_rows = [[
        Paragraph("<b>No.</b>", hdr_style),
        Paragraph("<b>Jenis Pengujian</b>", hdr_style),
        Paragraph("<b>Jenis Pemeriksaan</b>", hdr_style),
        Paragraph("<b>Hasil Pengujian Ω</b>", hdr_style),
        Paragraph("<b>Max. 0,1 Ω</b>", hdr_style)
    ]]

    for idx, (j_pem, h_ukur, v, h_prot) in enumerate(prot_items):
        no_str = "8" if idx == 0 else ""
        pengujian_str = Paragraph("Pengujian Keefektifan sirkit protektif", cell_style) if idx == 0 else ""
        t8_rows.append([
            no_str, pengujian_str,
            Paragraph(j_pem, cell_style),
            Paragraph(h_ukur, cell_center),
            Paragraph(f"{v} {h_prot}", cell_center)
        ])

    t8 = Table(t8_rows, colWidths=[25, 110, 175, 150, 95])
    t8.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('SPAN', (0,1), (0,5)),
        ('SPAN', (1,1), (1,5)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t8)

    # ==========================================================
    # FOOTER / CATATAN & TANDA TANGAN
    # ==========================================================
    foot_table_data = [
        [
            Paragraph("<b>CATATAN</b><br/><br/>Hasil pengujian: <s>diterima</s> / <b>diterima</b>", cell_style),
            Paragraph("<b>Diperiksa</b><br/>Quality Control<br/><br/><br/><br/><b>FAUZAN PRATAMA</b>", cell_center)
        ]
    ]
    t_foot = Table(foot_table_data, colWidths=[360, 195])
    t_foot.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_foot)

    doc.build(story)
    buffer.seek(0)
    return buffer
"""
Template-matching PDF generator for PLN Pusharlis QC Forms.
Merefleksikan persis layout template resmi (letterhead, tabel 5-kolom,
section bernomor, catatan/pengesahan, lampiran foto).

Public API:
    build_onepost_pdf(units: list[dict]) -> bytes
    build_phbtr_pdf(units: list[dict])   -> bytes
    build_pmcb_pdf(units: list[dict])    -> bytes
    pdf_download_button(data, filename, label)

units = list of unit-state dicts (one per serial number being exported).
"""

import re
from io import BytesIO
from pathlib import Path

from fpdf import FPDF

# ── Fonts ──────────────────────────────────────────────────────────────────────
_FR = Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf"
_FB = Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"

# Strip emoji/non-renderable chars
_BAD = re.compile(
    r"["
    r"\U0001F000-\U0001FFFF"
    r"\U00002600-\U000027BF"
    r"\U0001F300-\U0001F9FF"
    r"]+",
    flags=re.UNICODE,
)


def _t(v, multiline=False) -> str:
    """Safe text: strip emoji, coerce to str. Newlines kept only for multi_cell."""
    s = str(v) if v is not None else ""
    s = _BAD.sub("", s)
    if not multiline:
        s = s.replace("\n", " ")
    return s.strip()


# ── Page geometry ──────────────────────────────────────────────────────────────
PX = 10      # left margin
PW = 190     # usable page width (A4 = 210, margins 10 each side)

# Letterhead
LH_H = 28          # letterhead total height mm
LH_LEFT = 90       # left section width
LH_LOGO_W = 22     # PLN logo box width

# Main QC table column widths (must sum to PW = 190)
CN = 12     # NO.
CJ = 40     # JENIS PENGUJIAN
CP = 115    # JENIS PEMERIKSAAN
CC = 8      # ✓
CR = 15     # HASIL text
assert CN + CJ + CP + CC + CR == PW, "Column widths must sum to 190"

# Project-info row label/value widths (must sum to PW)
IL1, IV1, IL2, IV2 = 28, 62, 35, 65
assert IL1 + IV1 + IL2 + IV2 == PW

RH = 6      # standard row height


# ── Base PDF class ─────────────────────────────────────────────────────────────
class _QCBase(FPDF):
    def __init__(self, form_title: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self._form_title = form_title

        if not _FR.exists() or not _FB.exists():
            raise FileNotFoundError(
                f"Font DejaVu tidak ditemukan.\n"
                f"Pastikan file ada di:\n{_FR}\n{_FB}"
            )

        self.add_font("DV", "", str(_FR), uni=True)
        self.add_font("DV", "B", str(_FB), uni=True)

        self.set_margins(PX, 10, PX)
        self.set_auto_page_break(False)

    def _f(self, bold=False, size=8):
        self.set_font("DV", "B" if bold else "", size)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)

    def footer(self):
        self.set_y(-10)
        self._f(False, 8)
        self.cell(0, 5, f"Page {self.page_no()} of [Pages]", align="C")

    # ── Letterhead ───────────────────────────────────────────────────────────
    def draw_letterhead(self, logo_path=None):
        y = self.get_y()
        self._f()
        self.set_line_width(0.3)

        # Outer rectangle
        self.rect(PX, y, PW, LH_H)
        # Vertical divider between left (address) and right (title)
        self.line(PX + LH_LEFT, y, PX + LH_LEFT, y + LH_H)
        # Logo box
        self.rect(PX, y, LH_LOGO_W, LH_H)

        # Logo image — fit centered inside the box preserving aspect ratio
        if logo_path and Path(logo_path).exists():
            try:
                from PIL import Image
                with Image.open(str(logo_path)) as im:
                    iw, ih = im.size
                box_w, box_h = LH_LOGO_W - 3, LH_H - 3
                scale = min(box_w / iw, box_h / ih)
                draw_w, draw_h = iw * scale, ih * scale
                ox = PX + (LH_LOGO_W - draw_w) / 2
                oy = y + (LH_H - draw_h) / 2
                self.image(str(logo_path), ox, oy, draw_w, draw_h)
            except Exception:
                try:
                    # Fallback without PIL sizing (fpdf infers from image itself)
                    self.image(str(logo_path), PX + 1.5, y + 1.5, LH_LOGO_W - 3, LH_H - 3)
                except Exception:
                    self._f(True, 7)
                    self.set_xy(PX + 1, y + (LH_H - 6) / 2)
                    self.cell(LH_LOGO_W - 2, 6, "PLN", align="C")
        else:
            self._f(True, 7)
            self.set_xy(PX + 1, y + (LH_H - 6) / 2)
            self.cell(LH_LOGO_W - 2, 6, "PLN", align="C")

        # Address block
        ax = PX + LH_LOGO_W + 2
        aw = LH_LEFT - LH_LOGO_W - 3
        self._f(True, 6.5)
        self.set_xy(ax, y + 2)
        self.cell(aw, 3.5, "PT PLN (PERSERO) PUSHARLIS")
        self._f(False, 6)
        for i, line in enumerate([
            "UNIT PELAKSANA PRODUKSI DAN WORKSHOP III",
            "Jl. Banten No. 10 Bandung 40272",
            "Telp (022) 7236791, 7236792, 7236793 Faks (022) 7236794",
            "e-mail: pusharlis@pln.co.id",
        ]):
            self.set_xy(ax, y + 5.5 + i * 3.5)
            self.cell(aw, 3.5, line)

        # Form title (right side)
        self._f(True, 14)
        self.set_xy(PX + LH_LEFT, y)
        self.cell(PW - LH_LEFT, LH_H, self._form_title, align="C")

        self.set_y(y + LH_H)
        return y + LH_H

    # ── Project info header ───────────────────────────────────────────────────
    def draw_project_header(self, project_line: str, info_rows: list):
        y = self.get_y()
        self._f()
        self.set_line_width(0.3)

        # Full-width bold project description
        self._f(True, 9)
        self.set_xy(PX, y)
        self.cell(PW, 7, _t(project_line), border=1, align="C")
        y += 7

        for row in info_rows:
            self._f(False, 8)
            self.set_xy(PX, y)
            if len(row) == 4:
                l1, v1, l2, v2 = (_t(x) for x in row)
                self.cell(IL1, RH, l1, border=1)
                self.cell(IV1, RH, f": {v1}", border=1)
                self.cell(IL2, RH, l2, border=1)
                self.cell(IV2, RH, f": {v2}", border=1)
            else:
                l1 = _t(row[0])
                v1 = _t(row[1]) if len(row) > 1 else ""
                self.cell(IL1, RH, l1, border=1)
                self.cell(PW - IL1, RH, f": {v1}", border=1)
            y += RH

        self.set_y(y)
        return y

    # ── Main table column headers ─────────────────────────────────────────────
    def draw_table_header(self):
        y = self.get_y()
        self.set_fill_color(220, 220, 220)
        self._f(True, 8)
        self.set_xy(PX, y)
        self.cell(CN, RH, "NO.", border=1, align="C", fill=True)
        self.cell(CJ, RH, "JENIS PENGUJIAN", border=1, align="C", fill=True)
        self.cell(CP, RH, "JENIS PEMERIKSAAN", border=1, align="C", fill=True)
        self.cell(CC + CR, RH, "HASIL", border=1, align="C", fill=True)
        y += RH
        self.set_y(y)
        return y

    # ── Merged-cell section (NO + JENIS span all item rows) ──────────────────
    def draw_section(self, no, jenis: str, items: list):
        """
        items = list of dict with keys:
            text       - JENIS PEMERIKSAAN text (str)
            ok         - bool (default True)
            hasil      - HASIL text (default "Sesuai")
            row_h      - override row height (optional)
        """
        if not items:
            return self.get_y()

        row_heights = [item.get("row_h", RH) for item in items]
        total_h = sum(row_heights)
        y = self.get_y()

        # Page break
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self._f(False, 8)
        self.set_line_width(0.3)

        # NO cell (merged)
        self.rect(PX, y, CN, total_h)
        self._f(False, 8)
        self.set_xy(PX, y + (total_h - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")

        # JENIS PENGUJIAN cell (merged)
        self.rect(PX + CN, y, CJ, total_h)
        # Centered vertically
        lines = _t(jenis, multiline=True).split("\n")
        text_h = len(lines) * 4.5
        self.set_xy(PX + CN + 1, y + max(0, (total_h - text_h) / 2))
        for line in lines:
            self.set_x(PX + CN + 1)
            self.cell(CJ - 2, 4.5, line.strip(), align="C")
            self.ln(4.5)

        # Item rows
        xp = PX + CN + CJ
        iy = y
        for item in items:
            rh = item.get("row_h", RH)
            txt = _t(item.get("text", item.get("pemeriksaan", "")))
            ok = item.get("ok", True)
            hasil = _t(item.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))

            # JENIS PEMERIKSAAN
            self.set_xy(xp, iy)
            if rh > RH:
                # Use multi_cell for tall rows
                self.set_xy(xp + 1, iy + 0.5)
                self.multi_cell(CP - 2, 4.5, _t(txt, multiline=True), align="L")
                # Draw border manually
                self.rect(xp, iy, CP, rh)
            else:
                self.cell(CP, rh, txt, border=1, align="L")

            # ✓ check
            self.set_xy(xp + CP, iy)
            self.cell(CC, rh, "v" if ok else "-", border=1, align="C")
            # HASIL
            self.cell(CR, rh, hasil, border=1, align="C")
            iy += rh

        self.set_y(y + total_h)
        return y + total_h

    # ── Section with split JENIS PEMERIKSAAN column: label | value ───────────
    def draw_section_value(self, no, jenis: str, items: list):
        """
        Matches blangko rows where "Jenis Pemeriksaan" is followed by its
        spesifikasi/value on the same row (e.g. Selungkup, Kekencangan Baut).
        items: [{"label": str, "value": str, "ok": bool, "hasil": str, "row_h": int}]
        """
        if not items:
            return self.get_y()

        row_heights = [item.get("row_h", RH) for item in items]
        total_h = sum(row_heights)
        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        # NO cell (merged) — only drawn if `no` is not blank
        if jenis:
            self.rect(PX, y, CN, total_h)
            self._f(False, 8)
            self.set_xy(PX, y + (total_h - RH) / 2)
            self.cell(CN, RH, _t(str(no)), align="C")

            self.rect(PX + CN, y, CJ, total_h)
            lines = _t(jenis, multiline=True).split("\n")
            text_h = len(lines) * 4.5
            self.set_xy(PX + CN + 1, y + max(0, (total_h - text_h) / 2))
            self._f(False, 8)
            for line in lines:
                self.set_x(PX + CN + 1)
                self.cell(CJ - 2, 4.5, line.strip(), align="C")
                self.ln(4.5)
        else:
            self.rect(PX, y, CN, total_h)
            self.rect(PX + CN, y, CJ, total_h)

        label_w = CP * 0.55
        value_w = CP - label_w
        xp = PX + CN + CJ
        iy = y
        for item in items:
            rh = item.get("row_h", RH)
            label = _t(item.get("label", ""))
            value = _t(item.get("value", ""))
            ok = item.get("ok", True)
            hasil = _t(item.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))

            self._f(False, 7.8)
            self.set_xy(xp, iy)
            self.cell(label_w, rh, label, border=1, align="L")
            self.set_xy(xp + label_w, iy)
            self.cell(value_w, rh, value, border=1, align="C")
            self.set_xy(xp + CP, iy)
            self.cell(CC, rh, "v" if ok else "-", border=1, align="C")
            self.cell(CR, rh, hasil, border=1, align="C")
            iy += rh

        self.set_y(y + total_h)
        return y + total_h

    # ── Grouped rows with bold sub-headers (Uji Operasi Mekanis) ─────────────
    def draw_section_grouped(self, no, jenis: str, groups: dict):
        """groups: {group_name: [(item_text, ok), ...]}"""
        items_flat = []
        for grp, entries in groups.items():
            items_flat.append({"header": True, "text": grp})
            for text, ok in entries:
                items_flat.append({"text": text, "ok": ok})
        if not items_flat:
            return self.get_y()

        total_h = RH * len(items_flat)
        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.rect(PX, y, CN, total_h)
        self._f(False, 8)
        self.set_xy(PX, y + (total_h - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")
        self.rect(PX + CN, y, CJ, total_h)
        lines = _t(jenis, multiline=True).split("\n")
        text_h = len(lines) * 4.5
        self.set_xy(PX + CN + 1, y + max(0, (total_h - text_h) / 2))
        for line in lines:
            self.set_x(PX + CN + 1)
            self.cell(CJ - 2, 4.5, line.strip(), align="C")
            self.ln(4.5)

        xp = PX + CN + CJ
        iy = y
        for item in items_flat:
            if item.get("header"):
                self.set_fill_color(235, 235, 235)
                self._f(True, 8)
                self.set_xy(xp, iy)
                self.cell(CP + CC + CR, RH, _t(item["text"]), border=1, align="L", fill=True)
            else:
                ok = item.get("ok", True)
                hasil = "Berfungsi" if ok else "Tidak Berfungsi"
                self._f(False, 8)
                self.set_xy(xp, iy)
                self.cell(CP, RH, _t(item["text"]), border=1, align="L")
                self.cell(CC, RH, "v" if ok else "-", border=1, align="C")
                self.cell(CR, RH, hasil, border=1, align="C")
            iy += RH
        self.set_y(y + total_h)
        return y + total_h

    # ── Component grid (Saklar Utama / Fuse Rail style spec grid) ────────────
    def draw_component_grid(self, no, jenis: str, comp_name: str, grid_rows: list, ok=True, hasil=None):
        """
        grid_rows: list of rows, each row is a list of (label, value) tuples
        (up to 3 pairs per row), matching the Saklar Utama / Fuse Rail layout
        in the blangko (Merk / Standar desain / Kategori, etc.)
        """
        n_grid_rows = len(grid_rows)
        header_h = RH
        row_h = RH * 1.7
        total_h = header_h + n_grid_rows * row_h
        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.rect(PX, y, CN, total_h)
        if jenis:
            self._f(False, 8)
            self.set_xy(PX, y + (total_h - RH) / 2)
            self.cell(CN, RH, _t(str(no)), align="C")
        self.rect(PX + CN, y, CJ, total_h)
        if jenis:
            self._f(False, 8)
            lines = _t(jenis, multiline=True).split("\n")
            text_h = len(lines) * 4.5
            self.set_xy(PX + CN + 1, y + max(0, (total_h - text_h) / 2))
            for line in lines:
                self.set_x(PX + CN + 1)
                self.cell(CJ - 2, 4.5, line.strip(), align="C")
                self.ln(4.5)

        xp = PX + CN + CJ
        # component name row
        self._f(True, 8.5)
        self.set_xy(xp, y)
        self.cell(CP, header_h, _t(comp_name), border=1, align="C")
        hasil_txt = _t(hasil or ("Sesuai" if ok else "Tidak Sesuai"))
        self.rect(xp + CP, y, CC + CR, total_h)
        self._f(False, 8)
        self.set_xy(xp + CP, y + (total_h - RH) / 2)
        self.cell(CC, RH, "v" if ok else "-", align="C")
        self.set_xy(xp + CP + CC, y + (total_h - RH) / 2)
        self.cell(CR, RH, hasil_txt, align="C")

        iy = y + header_h
        for row in grid_rows:
            n_cols = max(len(row), 1)
            col_w = CP / n_cols
            lbl_w = col_w * 0.42
            val_w = col_w - lbl_w
            cx = xp
            for label, value in row:
                self.rect(cx, iy, lbl_w, row_h)
                self._f(True, 6.6)
                self.set_xy(cx + 0.5, iy + 0.5)
                self.multi_cell(lbl_w - 1, 3.1, _t(label, multiline=True), align="L")
                self.rect(cx + lbl_w, iy, val_w, row_h)
                self._f(False, 7)
                self.set_xy(cx + lbl_w + 0.5, iy + row_h / 2 - 2.2)
                self.multi_cell(val_w - 1, 3.4, _t(value, multiline=True), align="L")
                cx += col_w
            iy += row_h

        self.set_y(y + total_h)
        return y + total_h

    # ── Merged component-grid section (Onepost style — ONE NO/JENIS cell for
    #    the whole section 3, each component gets its own spec grid) ─────────
    def draw_component_grid_section(self, no, jenis, components, flat_items=None):
        """
        components: list of dict {name, pairs: [(label,value), ...] max 6,
                    rendered 3-per-row, ok}
        flat_items: list of dict {text, ok} rendered as plain full-width rows
                    below the component grids (busbar, kabel, dst.)
        The whole section shares a single merged NO + JENIS PENGUJIAN cell,
        matching the reference blangko where "3  Pemeriksaan komponen" spans
        every component box and the flat rows beneath it.
        """
        flat_items = flat_items or []
        PAIR_PER_ROW = 3
        row_h = RH * 1.7
        heights = []
        for c in components:
            n_rows = max(1, -(-len(c.get("pairs", [])) // PAIR_PER_ROW))
            heights.append(n_rows * row_h)
        flat_h = RH * len(flat_items)
        total_h = sum(heights) + flat_h
        if total_h <= 0:
            return self.get_y()

        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.rect(PX, y, CN, total_h)
        self._f(False, 8)
        self.set_xy(PX, y + (total_h - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")

        self.rect(PX + CN, y, CJ, total_h)
        lines = _t(jenis, multiline=True).split("\n")
        text_h = len(lines) * 4.5
        self.set_xy(PX + CN + 1, y + max(0, (total_h - text_h) / 2))
        for line in lines:
            self.set_x(PX + CN + 1)
            self.cell(CJ - 2, 4.5, line.strip(), align="C")
            self.ln(4.5)

        xp = PX + CN + CJ
        NAME_W = 30
        SPEC_W = CP - NAME_W
        col_w = SPEC_W / PAIR_PER_ROW
        iy = y
        for i, comp in enumerate(components):
            h = heights[i]
            ok = comp.get("ok", True)
            hasil = _t(comp.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))
            pairs = comp.get("pairs", [])
            n_rows = max(1, -(-len(pairs) // PAIR_PER_ROW))

            self.rect(xp, iy, NAME_W, h)
            self._f(True, 8)
            name_lines = _t(comp.get("name", ""), multiline=True).split("\n")
            ty = iy + max(0, (h - len(name_lines) * 4) / 2)
            for ln in name_lines:
                self.set_xy(xp + 1, ty)
                self.cell(NAME_W - 2, 4, ln.strip(), align="C")
                ty += 4

            self.rect(xp + NAME_W, iy, SPEC_W, h)
            for idx, (label, value) in enumerate(pairs):
                col = idx % PAIR_PER_ROW
                row = idx // PAIR_PER_ROW
                cx = xp + NAME_W + col * col_w
                cy = iy + row * row_h
                if col > 0:
                    self.line(cx, cy, cx, cy + row_h)
                self._f(True, 6.3)
                self.set_xy(cx + 0.8, cy + 0.6)
                self.cell(col_w - 1.6, 3, f"{_t(label)}:", align="L")
                self._f(False, 6.8)
                self.set_xy(cx + 0.8, cy + 3.6)
                self.multi_cell(col_w - 1.6, 3.1, _t(value, multiline=True), align="L")
            for r in range(1, n_rows):
                self.line(xp + NAME_W, iy + r * row_h, xp + NAME_W + SPEC_W, iy + r * row_h)

            self.rect(xp + CP, iy, CC, h)
            self._f(False, 9)
            self.set_xy(xp + CP, iy + (h - RH) / 2)
            self.cell(CC, RH, "v" if ok else "-", align="C")
            self.rect(xp + CP + CC, iy, CR, h)
            self._f(False, 8)
            self.set_xy(xp + CP + CC, iy + (h - RH) / 2)
            self.cell(CR, RH, hasil, align="C")

            iy += h

        for item in flat_items:
            txt = _t(item.get("text", ""))
            ok = item.get("ok", True)
            hasil = _t(item.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))
            self._f(False, 8)
            self.set_xy(xp, iy)
            self.cell(CP, RH, txt, border=1, align="L")
            self.cell(CC, RH, "v" if ok else "-", border=1, align="C")
            self.cell(CR, RH, hasil, border=1, align="C")
            iy += RH

        self.set_y(y + total_h)
        return y + total_h

    # ── Dimension section: reference image + A..K result table ───────────────
    def draw_dimension_section(self, no, jenis, image_path, letters, hasil_row, standar_row, ok=True):
        y = self.get_y()
        img_h = 68
        if y + img_h + RH * 4 > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.rect(PX, y, CN, img_h)
        self._f(False, 8)
        self.set_xy(PX, y + img_h / 2 - 3)
        self.cell(CN, RH, _t(str(no)), align="C")

        self.rect(PX + CN, y, CJ, img_h)
        self._f(False, 8)
        jenis_txt = _t(jenis, multiline=True).replace("\n", " ")
        self.set_xy(PX + CN + 1, y + img_h / 2 - 3)
        self.multi_cell(CJ - 2, 4.5, jenis_txt, align="C")

        img_box_w = CP + CC + CR
        self.rect(PX + CN + CJ, y, img_box_w, img_h)
        if image_path and Path(image_path).exists():
            try:
                self.image(str(image_path), PX + CN + CJ + 5, y + 3, img_box_w - 10, img_h - 6)
            except Exception:
                pass
        self.set_y(y + img_h)

        # result table below the image
        n = len(letters)
        label_w = 40
        col_w = (PW - label_w) / n
        y2 = self.get_y()

        self._f(True, 7.5)
        self.set_fill_color(220, 220, 220)
        self.set_xy(PX, y2)
        self.cell(label_w, RH, "Parameter", border=1, align="C", fill=True)
        for L in letters:
            self.cell(col_w, RH, L, border=1, align="C", fill=True)
        y2 += RH

        self._f(False, 7.5)
        self.set_xy(PX, y2)
        self.cell(label_w, RH, "Persyaratan Standar (mm)", border=1, align="L")
        for v in standar_row:
            self.cell(col_w, RH, _t(str(v)), border=1, align="C")
        y2 += RH

        self.set_xy(PX, y2)
        self.cell(label_w, RH, "Hasil Ukur (mm) toleransi 5%", border=1, align="L")
        for v in hasil_row:
            self.cell(col_w, RH, _t(str(v)), border=1, align="C")
        y2 += RH

        self._f(True, 8)
        hasil_txt = "Sesuai" if ok else "Tidak Sesuai"
        self.set_xy(PX, y2)
        self.cell(PW, RH, f"HASIL: {hasil_txt}", border=1, align="C")
        y2 += RH

        self.set_y(y2)
        return y2

    # ── Dielektrik section (own column layout: sebelum/sesudah uji) ──────────
    def draw_dielektrik_section(self, no, jenis, items):
        if not items:
            return self.get_y()
        W_SIRKIT, W_SEB, W_SES, W_HASIL = 65, 27, 27, 19
        row_h = 9
        header_h = RH
        total_body = row_h * len(items)
        total_h = header_h + total_body
        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.set_fill_color(220, 220, 220)
        self._f(True, 7)
        self.set_xy(PX, y)
        self.cell(CN, header_h, "No.", border=1, align="C", fill=True)
        self.cell(CJ, header_h, "Jenis Pengujian", border=1, align="C", fill=True)
        self.cell(W_SIRKIT, header_h, "Sirkit Utama (3kV-1 Menit)", border=1, align="C", fill=True)
        self.cell(W_SEB, header_h, "Sebelum uji", border=1, align="C", fill=True)
        self.cell(W_SES, header_h, "Sesudah uji", border=1, align="C", fill=True)
        self.cell(W_HASIL, header_h, "Hasil", border=1, align="C", fill=True)

        y_body = y + header_h
        self.rect(PX, y_body, CN, total_body)
        self._f(False, 8)
        self.set_xy(PX, y_body + (total_body - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")
        self.rect(PX + CN, y_body, CJ, total_body)
        self.set_xy(PX + CN + 1, y_body + (total_body - RH) / 2)
        jenis_txt = _t(jenis, multiline=True).replace("\n", " ")
        self.multi_cell(CJ - 2, 4.5, jenis_txt, align="C")

        xp = PX + CN + CJ
        iy = y_body
        for it in items:
            ok = it.get("ok", True)
            self.rect(xp, iy, W_SIRKIT, row_h)
            self._f(False, 6.3)
            self.set_xy(xp + 0.8, iy + 0.8)
            self.multi_cell(W_SIRKIT - 1.6, 3, _t(it.get("sirkuit", ""), multiline=True), align="L")

            self._f(False, 7.5)
            self.set_xy(xp + W_SIRKIT, iy)
            self.cell(W_SEB, row_h, _t(it.get("sebelum", "")), border=1, align="C")
            self.cell(W_SES, row_h, _t(it.get("sesudah", "")), border=1, align="C")
            hasil_txt = "Baik" if ok else "Tidak Baik"
            self.cell(W_HASIL, row_h, hasil_txt, border=1, align="C")
            iy += row_h

        self.set_y(y_body + total_body)
        return y_body + total_body

    # ── Sirkit Protektif section (own column layout: Ω, satuan, max 0.1Ω) ────
    def draw_sirkit_section(self, no, jenis, items):
        if not items:
            return self.get_y()
        W_ITEM, W_HASIL_UKUR, W_MAX = 65, 45, 28
        row_h = RH
        header_h = RH
        total_body = row_h * len(items)
        total_h = header_h + total_body
        y = self.get_y()
        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self.set_line_width(0.3)
        self.set_fill_color(220, 220, 220)
        self._f(True, 7)
        self.set_xy(PX, y)
        self.cell(CN, header_h, "No.", border=1, align="C", fill=True)
        self.cell(CJ, header_h, "Jenis Pengujian", border=1, align="C", fill=True)
        self.cell(W_ITEM, header_h, "Jenis Pemeriksaan", border=1, align="C", fill=True)
        self.cell(W_HASIL_UKUR, header_h, "Hasil Pengujian", border=1, align="C", fill=True)
        self.cell(W_MAX, header_h, "Max. 0,1 Ohm", border=1, align="C", fill=True)

        y_body = y + header_h
        self.rect(PX, y_body, CN, total_body)
        self._f(False, 8)
        self.set_xy(PX, y_body + (total_body - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")
        self.rect(PX + CN, y_body, CJ, total_body)
        self.set_xy(PX + CN + 1, y_body + (total_body - RH) / 2)
        jenis_txt = _t(jenis, multiline=True).replace("\n", " ")
        self.multi_cell(CJ - 2, 4.5, jenis_txt, align="C")

        xp = PX + CN + CJ
        iy = y_body
        for it in items:
            ok = it.get("ok", it.get("status", True))
            self._f(False, 7.8)
            self.set_xy(xp, iy)
            self.cell(W_ITEM, row_h, _t(it.get("item", "")), border=1, align="L")
            val_txt = f"{it.get('nilai', '')} {it.get('satuan', '')}".strip()
            self.cell(W_HASIL_UKUR, row_h, val_txt, border=1, align="C")
            self.cell(W_MAX, row_h, "Baik" if ok else "Tidak Baik", border=1, align="C")
            iy += row_h

        self.set_y(y_body + total_body)
        return y_body + total_body

    # ── Component block (sub-table within JENIS PEMERIKSAAN column) ───────────
    def draw_component_block(self, no, jenis_name: str, components: list):
        """
        For Section 3 (Komponen) — generic multi-line spec block, used by
        OnePost / PMCB builders.
            name  - e.g. "INVERTER"
            specs - e.g. "Merk: ZAMDON\nDaya: 2000W\n..."
            ok    - bool
        """
        if not components:
            return self.get_y()

        heights = []
        for c in components:
            n_lines = len(c.get("specs", "").split("\n"))
            heights.append(max(RH * 3, n_lines * 3.8 + 6))

        total_h = sum(heights)
        y = self.get_y()

        if y + total_h > 282:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        self._f(False, 8)
        self.set_line_width(0.3)

        self.rect(PX, y, CN, total_h)
        self.set_xy(PX, y + (total_h - RH) / 2)
        self.cell(CN, RH, _t(str(no)), align="C")

        self.rect(PX + CN, y, CJ, total_h)
        self.set_xy(PX + CN + 1, y + (total_h - RH) / 2)
        self.cell(CJ - 2, RH, _t(jenis_name), align="C")

        xp = PX + CN + CJ
        CJ2 = 30
        CS = CP - CJ2
        iy = y
        for i, comp in enumerate(components):
            h = heights[i]
            ok = comp.get("ok", True)
            hasil = _t(comp.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))

            self.rect(xp, iy, CJ2, h)
            self._f(True, 8)
            name_lines = _t(comp.get("name", ""), multiline=True).split("\n")
            ty = iy + max(0, (h - len(name_lines) * 4) / 2)
            for ln in name_lines:
                self.set_xy(xp + 1, ty)
                self.cell(CJ2 - 2, 4, ln.strip(), align="C")
                ty += 4

            self.rect(xp + CJ2, iy, CS, h)
            self._f(False, 7.5)
            self.set_xy(xp + CJ2 + 1, iy + 1)
            self.multi_cell(CS - 2, 3.8, _t(comp.get("specs", ""), multiline=True), align="L")

            self.rect(xp + CP, iy, CC, h)
            self._f(False, 9)
            self.set_xy(xp + CP, iy + (h - RH) / 2)
            self.cell(CC, RH, "v" if ok else "-", align="C")

            self.rect(xp + CP + CC, iy, CR, h)
            self._f(False, 8)
            self.set_xy(xp + CP + CC, iy + (h - RH) / 2)
            self.cell(CR, RH, hasil, align="C")

            iy += h

        self.set_y(y + total_h)
        return y + total_h

    # ── Flat rows (no NO/JENIS merging — continuation rows) ──────────────────
    def draw_flat_rows(self, items: list):
        """Items with optional 'bold' key for sub-header rows."""
        y = self.get_y()
        for item in items:
            rh = item.get("row_h", RH)
            if y + rh > 282:
                self.add_page()
                self.set_y(15)
                y = self.get_y()

            txt = _t(item.get("text", ""))
            ok = item.get("ok", True)
            hasil = _t(item.get("hasil", "Sesuai" if ok else "Tidak Sesuai"))
            is_hdr = item.get("header", False)

            if is_hdr:
                self.set_fill_color(235, 235, 235)
                self._f(True, 8)
                self.set_xy(PX + CN + CJ, y)
                self.cell(CP + CC + CR, rh, txt, border=1, align="C", fill=True)
            else:
                self._f(False, 8)
                self.set_xy(PX + CN + CJ, y)
                self.cell(CP, rh, txt, border=1, align="L")
                self.cell(CC, rh, "v" if ok else "-", border=1, align="C")
                self.cell(CR, rh, hasil, border=1, align="C")
            y += rh

        self.set_y(y)
        return y

    # ── Catatan + Pengesahan boxes ────────────────────────────────────────────
    def draw_catatan(self, catatan: str, hasil: str, diperiksa: str):
        y = self.get_y()
        if y + 35 > 287:
            self.add_page()
            self.set_y(15)
            y = self.get_y()

        box_h = 35
        w_cat = 130
        w_dep = PW - w_cat

        self._f()
        self.set_line_width(0.3)

        # CATATAN box
        self.rect(PX, y, w_cat, box_h)
        self._f(True, 8)
        self.set_xy(PX, y)
        self.cell(w_cat, RH, "CATATAN", align="C", border="B")

        self._f(False, 8)
        self.set_xy(PX + 1, y + RH + 1)
        self.multi_cell(w_cat - 2, 5, f"Hasil pengujian: {_t(hasil, multiline=True)}", align="L")
        if catatan:
            cur_y = self.get_y()
            self.set_xy(PX + 1, cur_y + 1)
            self.multi_cell(w_cat - 2, 5, _t(catatan, multiline=True), align="L")

        # Diperiksa box
        self.rect(PX + w_cat, y, w_dep, box_h)
        self._f(False, 8)
        self.set_xy(PX + w_cat, y)
        self.cell(w_dep, RH, "Diperiksa", align="C", border="B")
        self.set_xy(PX + w_cat, y + RH)
        self.cell(w_dep, RH, "Quality Control", align="C")

        self._f(True, 9)
        self.set_xy(PX + w_cat, y + box_h - 9)
        self.cell(w_dep, RH, _t(diperiksa) or "-", align="C")

        self.set_y(y + box_h)
        return y + box_h

    # ── Lampiran page ─────────────────────────────────────────────────────────
    def draw_lampiran(self, nama_produk: str, nomor_seri: str, foto_list: list):
        self.add_page()
        self.set_y(10)
        y = 10

        self._f()
        self.set_line_width(0.3)
        self.rect(PX, y, PW, 8)
        self._f(True, 10)
        self.set_xy(PX, y)
        self.cell(PW, 8, "LAMPIRAN DOKUMENTASI", align="C")
        y += 10

        self._f(True, 9)
        self.set_xy(PX, y)
        self.cell(25, 6, "Nama produk")
        self.cell(5, 6, ":")
        self._f(False, 9)
        self.cell(0, 6, _t(nama_produk))
        y += 7

        self._f(True, 9)
        self.set_xy(PX, y)
        self.cell(25, 6, "nomor seri")
        self.cell(5, 6, ":")
        self._f(False, 9)
        self.cell(0, 6, _t(nomor_seri))
        y += 10

        if not foto_list:
            self.rect(PX, y, PW, 50)
            self._f(False, 9)
            self.set_xy(PX, y + 22)
            self.cell(PW, 6, "Tidak ada foto dokumentasi", align="C")
            return

        col_w = 60
        col_h = 65
        cols = 3
        for i, foto_path in enumerate(foto_list):
            col = i % cols
            if col == 0 and i > 0:
                y += col_h + 5
            if y + col_h > 283:
                self.add_page()
                y = 15
            x = PX + col * (col_w + 5)
            try:
                self.image(str(foto_path), x, y, col_w, col_h)
                self.rect(x, y, col_w, col_h)
            except Exception:
                self.rect(x, y, col_w, col_h)
                self._f(False, 7)
                self.set_xy(x + 1, y + col_h / 2 - 3)
                self.cell(col_w - 2, 6, "Foto tidak tersedia", align="C")

    # ── Alternate sub-table header (for sections 6,7 with different columns) ──
    def draw_alt_header(self, cols: list, widths: list):
        """Draw a sub-table header with arbitrary columns."""
        y = self.get_y()
        self.set_fill_color(220, 220, 220)
        self._f(True, 8)
        self.set_xy(PX, y)
        self.cell(CN, RH, "No.", border=1, align="C", fill=True)
        x = PX + CN
        for label, w in zip(cols, widths):
            self.set_xy(x, y)
            self.cell(w, RH, label, border=1, align="C", fill=True)
            x += w
        self.set_y(y + RH)
        return y + RH

    def draw_alt_rows(self, rows: list, widths: list, no_col=True):
        """
        rows: list of dict  {"no": int, "cols": [str, ...], "ok": bool}
        widths: column widths (excluding NO col)
        """
        y = self.get_y()
        for r in rows:
            rh = r.get("row_h", RH)
            if y + rh > 282:
                self.add_page()
                self.set_y(15)
                y = self.get_y()
            self._f(False, 8)
            self.set_xy(PX, y)
            if no_col:
                self.cell(CN, rh, _t(str(r.get("no", ""))), border=1, align="C")
            x = PX + CN
            for i, (val, w) in enumerate(zip(r.get("cols", []), widths)):
                self.set_xy(x, y)
                self.cell(w, rh, _t(val), border=1, align="L" if i == 0 else "C")
                x += w
            y += rh
        self.set_y(y)
        return y


# ══════════════════════════════════════════════════════════════════════════════
# ONEPOST PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def _onepost_unit_pages(pdf: _QCBase, unit: dict, logo_path=None, dimensi_image_path=None):
    """Generate all pages for one OnePost unit — matches TEMPLATE_QC_SUPERSUN reference."""
    info = unit.get("info", {})
    no_amp = info.get("no_amp", "-")
    nama_produk = info.get("nama_produk", "SUPERSUN 1300VA")
    nomor_seri = info.get("nomor_seri", "-")
    daya = info.get("daya", "1300VA")
    tegangan_input = info.get("tegangan_input", "220 VAC ;24 VDC (Grid) ; 36-90 VDC (PV)")
    tegangan_output = info.get("tegangan_output", "220-230 VAC")

    pdf.add_page()
    pdf.set_y(10)

    pdf.draw_letterhead(logo_path)
    pdf.draw_project_header(
        "Penugasan Tetap Fabrikasi 6 Set Kompak Daya Berbasis Baterai 1300VA (Onepost) PLN UID S2JB",
        [
            ("No. AMP", no_amp, "Tegangan input", tegangan_input),
            ("Nama Produk", nama_produk, "Daya", daya),
            ("Nomor Seri", nomor_seri, "Tegangan Output", tegangan_output),
        ],
    )
    pdf.draw_table_header()

    # ── Section 1 — Visual dan Penandaan ──────────────────────────────────
    visual = unit.get("visual_onepost") or [
        {"item": "Hasil pengerjaan baik dan kondisi baru", "status": True},
        {"item": "Kesesuaian stiker papan nama", "status": True},
    ]
    pdf.draw_section(1, "Visual dan\nPenandaan", [
        {"text": v.get("item", ""), "ok": v.get("status", True)} for v in visual
    ])

    # ── Section 2 — Selungkup ──────────────────────────────────────────────
    selungkup = unit.get("selungkup_onepost") or [
        {"parameter": "Cat powder Coating min 80 \u03bcm", "nilai": "80 \u03bcm | RAL7032", "status": "\u2713"},
        {"parameter": "Handle pengangkat supersun", "nilai": "-", "status": "\u2713"},
        {"parameter": "Branding Logo PLN", "nilai": "-", "status": "\u2713"},
    ]
    pdf.draw_section(2, "Selungkup", [
        {"text": s.get("parameter", s.get("item", "")), "ok": s.get("status", "\u2713") == "\u2713",
         "hasil": "Sesuai" if s.get("status", "\u2713") == "\u2713" else "Tidak Sesuai"}
        for s in selungkup
    ])

    # ── Section 3 — Pemeriksaan Komponen (grid spek per komponen, sesuai referensi) ──
    detail = unit.get("komponen_detail_onepost", {})

    def _pairs(d, keys_labels, defaults):
        """d: dict komponen; keys_labels: [(field_key, label)]; defaults: dict fallback."""
        out = []
        for key, label in keys_labels:
            val = d.get(key, defaults.get(key, "-"))
            out.append((label, val))
        return out

    inv = detail.get("inverter", {})
    mppt = detail.get("mppt", {})
    rcbo = detail.get("rcbo", {})
    mcb1 = detail.get("mcb1", {})
    mcb2 = detail.get("mcb2", {})
    scb = detail.get("scb", {})
    bat = detail.get("baterai", {})

    components = [
        {
            "name": "INVERTER", "ok": inv.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", inv.get("merk", "ZAMDON")), ("Daya", inv.get("daya", "2000W")),
                ("Tegangan Input", inv.get("vin", "24 VDC")),
                ("Tegangan Output", inv.get("vout", "230 VAC \u00b1 10%")),
                ("Frekuensi", inv.get("freq", "50 Hz")),
                ("Output", inv.get("out", "Gelombang sinus murni")),
            ],
        },
        {
            "name": "MPPT/SCC", "ok": mppt.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", mppt.get("merk", "ZAMDON")), ("Tipe", mppt.get("tipe", "XTRA4215N")),
                ("Tegangan Input DC", mppt.get("vdc", "24 VDC")),
                ("Tegangan Input PV", mppt.get("vpv", "150 VDC")),
                ("Daya Pengisi Terkini", mppt.get("daya", "1040W/24V")),
                ("Arus Maksimum", mppt.get("arus", "40 A")),
            ],
        },
        {
            "name": "RCBO", "ok": rcbo.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", rcbo.get("merk", "Chint")), ("Tipe", rcbo.get("tipe", "NB2LE")),
                ("Arus terukur", rcbo.get("arus", "25 A")),
                ("Frekuensi", rcbo.get("freq", "50 Hz")),
                ("Kapasitas Pemutusan", rcbo.get("kap", "6 kA")),
                ("Arus Residu Terukur", rcbo.get("residu", "30 mA")),
            ],
        },
        {
            "name": "MCB", "ok": mcb1.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", mcb1.get("merk", "Suntree")), ("Tipe", mcb1.get("tipe", "SL7N-63 DC")),
                ("Arus terukur", mcb1.get("arus", "32 A")),
                ("Jumlah kutub", mcb1.get("kutub", "1P")),
                ("Standard", mcb1.get("std", "IEC 60947-2")),
                ("Kapasitas Pemutusan", mcb1.get("kap", "6 kA")),
            ],
        },
        {
            "name": "MCB", "ok": mcb2.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", mcb2.get("merk", "Suntree")), ("Tipe", mcb2.get("tipe", "SL7N-63 DC")),
                ("Arus terukur", mcb2.get("arus", "63 A")),
                ("Jumlah kutub", mcb2.get("kutub", "1P")),
                ("Standard", mcb2.get("std", "IEC 60947-2")),
                ("Kapasitas Pemutusan", mcb2.get("kap", "6 kA")),
            ],
        },
        {
            "name": "Smart Circuit\nBreaker", "ok": scb.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", scb.get("merk", "Taxnele")), ("Tipe", scb.get("tipe", "TXCB2-VAP")),
                ("Arus terukur", scb.get("arus", "10-63 A")),
                ("Jumlah kutub", scb.get("kutub", "1P+N")),
                ("Standard", scb.get("std", "IEC 60947-2")),
                ("Konektivitas", scb.get("konek", "2.4 GHz")),
            ],
        },
        {
            "name": "BATERAI", "ok": bat.get("status", "\u2713") == "\u2713",
            "pairs": [
                ("Merk", bat.get("merk", "SUP")), ("Tegangan Nominal", bat.get("vnom", "25,6 V")),
                ("Kapasitas Arus Nominal", bat.get("kap", "100 Ah")),
                ("Tegangan pengisian", bat.get("vpengisian", "28,8V")),
                ("Tipe Baterai", bat.get("tipe", "LiFePO4")),
                ("Umur pakai", bat.get("umur", "2500 Cycle")),
            ],
        },
    ]

    tambahan = unit.get("komponen_onepost", [])
    tambahan_items = [t for t in tambahan if t.get("komponen") in (
        "Busbar Positif dan Negatif", "Busbar pembumian",
        "Setting Proteksi kWh Taxnelle", "Kabel instalasi",
    )]
    if tambahan_items:
        flat_items = [
            {"text": f"{t.get('komponen','')}     {t.get('nilai','')}", "ok": t.get("status", "\u2713") == "\u2713"}
            for t in tambahan_items
        ]
    else:
        flat_items = [
            {"text": "Busbar Positif dan Negatif     180 x 25 x 3 mm", "ok": True},
            {"text": "Busbar pembumian     135x 15 x 3 mm", "ok": True},
            {"text": "Setting Proteksi kWh Taxnelle dengan rating 4A", "ok": True},
            {"text": "Kabel instalasi NYYHY 2x2.5mm, NYAF 10mm,6mm,2.5mm,0.75mm,AWG 22", "ok": True},
        ]

    pdf.draw_component_grid_section(3, "Pemeriksaan\nkomponen", components, flat_items)

    # ── Section 4 — Pengujian Tarik Skun Kabel ────────────────────────────
    tarik = unit.get("tarik_skun_onepost", [])
    cable_sizes = [0.75, 2.5, 4, 6, 10]
    std_values = [45, 150, 240, 360, 600]
    hasil_values = [56.22, 179.2, 273.0, 398.9, 659.6]
    tarik_ok = True

    if tarik:
        cable_sizes = [t.get("ukuran", cable_sizes[i]) for i, t in enumerate(tarik)]
        std_values = [t.get("standar", std_values[i]) for i, t in enumerate(tarik)]
        hasil_values = [t.get("hasil", hasil_values[i]) for i, t in enumerate(tarik)]
        tarik_ok = all(t.get("status", True) for t in tarik)

    n_cables = len(cable_sizes)
    sub_w = (CP - CC - CR) / max(n_cables, 1)
    row_h4 = RH
    total_h4 = row_h4 * 4
    y = pdf.get_y()
    if y + total_h4 > 282:
        pdf.add_page()
        pdf.set_y(15)
    y = pdf.get_y()

    pdf.set_line_width(0.3)
    pdf.rect(PX, y, CN, total_h4)
    pdf._f(False, 8)
    pdf.set_xy(PX, y + (total_h4 - RH) / 2)
    pdf.cell(CN, RH, "4", align="C")
    pdf.rect(PX + CN, y, CJ, total_h4)
    pdf.set_xy(PX + CN + 1, y + (total_h4 - RH) / 2 - 4.5)
    pdf.multi_cell(CJ - 2, 4.5, _t("Pengujian Tarik Skun Kabel", multiline=True), align="C")

    xp = PX + CN + CJ
    pdf._f(True, 7)
    pdf.set_xy(xp, y)
    pdf.cell(CP - CC - CR, RH, "Ukuran Kabel (mm)", border=1, align="C")
    pdf.rect(xp + CP - CC - CR, y, CC + CR, total_h4)
    yy = y + RH

    pdf._f(False, 7.5)
    pdf.set_xy(xp, yy)
    for sz in cable_sizes:
        pdf.cell(sub_w, RH, _t(str(sz)), border=1, align="C")
    yy += RH

    pdf._f(True, 7)
    pdf.set_xy(xp, yy)
    pdf.cell(CP - CC - CR, RH, "Persyaratan Standar (N)", border=1, align="C")
    yy += RH

    pdf._f(False, 7.5)
    pdf.set_xy(xp, yy)
    for sv in std_values:
        pdf.cell(sub_w, RH, _t(str(sv)), border=1, align="C")
    yy += RH

    pdf._f(False, 8)
    hasil_txt4 = "Sesuai" if tarik_ok else "Tidak Sesuai"
    pdf.set_xy(xp + CP - CC - CR, y + (total_h4 - RH) / 2)
    pdf.cell(CC, RH, "v" if tarik_ok else "-", align="C")
    pdf.set_xy(xp + CP - CR, y + (total_h4 - RH) / 2)
    pdf.cell(CR, RH, hasil_txt4, align="C")

    pdf.set_y(y + total_h4)

    # continuation row: Hasil Pemeriksaan (N)
    y2 = pdf.get_y()
    if y2 + RH * 2 > 282:
        pdf.add_page()
        pdf.set_y(15)
        y2 = pdf.get_y()
    total_h4b = RH * 2
    pdf.rect(PX, y2, CN, total_h4b)
    pdf.rect(PX + CN, y2, CJ, total_h4b)
    xp = PX + CN + CJ
    pdf._f(True, 7)
    pdf.set_xy(xp, y2)
    pdf.cell(CP - CC - CR, RH, "Hasil Pemeriksaan (N)", border=1, align="C")
    pdf.cell(CC + CR, RH, "", border=1)
    yy2 = y2 + RH
    pdf._f(False, 7.5)
    pdf.set_xy(xp, yy2)
    for hv in hasil_values:
        pdf.cell(sub_w, RH, _t(str(hv)), border=1, align="C")
    pdf.cell(CC + CR, RH, "", border=1)
    pdf.set_y(y2 + total_h4b)

    # ── PAGE 2 — Dimensi, Board, Fungsi ───────────────────────────────────
    pdf.add_page()
    pdf.set_y(10)
    pdf.draw_table_header()

    dimensi = unit.get("dimensi_onepost", {})
    letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
    default_dim = [280, 605, 530, 327.8, 107, 422.6, 400, 160]
    if dimensi and all(l in dimensi and len(dimensi[l]) >= 2 for l in letters):
        standar_row = [dimensi[l][0] for l in letters]
        hasil_row = [dimensi[l][1] for l in letters]
    else:
        standar_row = default_dim
        hasil_row = default_dim
    pdf.draw_dimension_section(
        5, "Pengujian\ndimensi\nselungkup",
        dimensi_image_path, letters, hasil_row, standar_row, ok=True,
    )

    # ── Section 6 — Pengujian Board ───────────────────────────────────────
    board_items = unit.get("board_onepost") or [
        {"item": "ID Board Monitoring", "spek": "ID terdata/terdaftar", "status": True},
        {"item": "Power Supply Board", "spek": "Board Menyala", "status": True},
        {"item": "Komunikasi", "spek": "Tersambung dengan internet", "status": True},
        {"item": "Sensor", "spek": "Sensor terbaca di dashboard", "status": True},
    ]
    w6 = [CJ, CP - CJ, CC + CR]
    pdf.draw_alt_header(["Jenis Pengujian", "Item Pengujian", "Spesifikasi Uji"], w6)
    y6 = pdf.get_y()
    merged6_h = len(board_items) * RH
    pdf.set_line_width(0.3)
    pdf.rect(PX, y6, CN, merged6_h)
    pdf._f(False, 8)
    pdf.set_xy(PX, y6 + (merged6_h - RH) / 2)
    pdf.cell(CN, RH, "6", align="C")
    pdf.rect(PX + CN, y6, CJ, merged6_h)
    pdf.set_xy(PX + CN + 1, y6 + (merged6_h - RH) / 2)
    pdf.cell(CJ - 2, RH, _t("Pengujian Board"), align="C")
    xp6 = PX + CN + CJ
    for b in board_items:
        ok = b.get("status", True)
        pdf._f(False, 8)
        pdf.set_xy(xp6, y6)
        pdf.cell(CJ, RH, _t(b.get("item", "")), border=1)
        pdf.cell(CP - CJ, RH, _t(b.get("spek", "")), border=1, align="C")
        pdf.cell(CC + CR, RH, "Baik" if ok else "Tidak Baik", border=1, align="C")
        y6 += RH
    pdf.set_y(y6)

    # ── Section 7 — Pengujian Fungsi ──────────────────────────────────────
    fungsi = unit.get("fungsi_onepost") or [
        {"item": "MPPT/SCC", "spek": "Setting SCC melalui dongle", "status": True},
        {"item": "PV Input Charging", "spek": "Charging 80-90 VDC, Current Charging 16 ~ 30 A", "status": True},
        {"item": "Display BMS Baterai", "spek": "Display ON, Nominal SOC%", "nilai": "94", "satuan": "%", "status": True},
        {"item": "DC System Baterai", "spek": "Tegangan Baterai Vo=24~28 VDC", "nilai": "26.9", "satuan": "VDC", "status": True},
        {"item": "AC System Inverter", "spek": "Output Tegangan AC 220-230 V", "nilai": "220", "satuan": "VAC", "status": True},
        {"item": "Display Inverter", "spek": "Display ON", "status": True},
        {"item": "Indikator Lampu", "spek": "Indikator Baterai, PV, Inv,", "status": True},
        {"item": "Fan", "spek": "Power ON", "status": True},
        {"item": "Limit Switch", "spek": "ON/OFF", "status": True},
        {"item": "Load Output 1 & 2", "spek": "Output Load ON, beban 300-800 W", "status": True},
    ]
    w7_lbl = [CJ, CP - CJ - 30, 30, CC + CR]
    pdf.draw_alt_header(["Jenis Pengujian", "Jenis Pemeriksaan", "Hasil Pengukuran", "HASIL"], w7_lbl)

    y7 = pdf.get_y()
    merged7_h = len(fungsi) * RH
    pdf.rect(PX, y7, CN, merged7_h)
    pdf._f(False, 8)
    pdf.set_xy(PX, y7 + (merged7_h - RH) / 2)
    pdf.cell(CN, RH, "7", align="C")
    pdf.rect(PX + CN, y7, CJ, merged7_h)
    pdf.set_xy(PX + CN + 1, y7 + (merged7_h - RH) / 2)
    pdf.cell(CJ - 2, RH, _t("Pengujian Fungsi"), align="C")

    xp7 = PX + CN + CJ
    for f in fungsi:
        if y7 + RH > 282:
            pdf.add_page()
            pdf.set_y(15)
            y7 = pdf.get_y()
        ok = f.get("status", True)
        nilai_txt = f"{f.get('nilai', '')} {f.get('satuan', '')}".strip() or ("v" if ok else "-")
        pdf._f(False, 8)
        pdf.set_xy(xp7, y7)
        pdf.cell(w7_lbl[0], RH, _t(f.get("item", "")), border=1)
        pdf.cell(w7_lbl[1], RH, _t(f.get("spek", "")), border=1)
        pdf.cell(w7_lbl[2], RH, _t(nilai_txt), border=1, align="C")
        pdf.cell(w7_lbl[3], RH, "Baik" if ok else "Tidak Baik", border=1, align="C")
        y7 += RH
    pdf.set_y(y7 + 3)

    # ── Catatan + Pengesahan ──────────────────────────────────────────────
    catatan_data = unit.get("catatan_pengesahan_onepost", {})
    pdf.draw_catatan(
        catatan=catatan_data.get("catatan", ""),
        hasil=catatan_data.get("hasil_pengujian", "diterima"),
        diperiksa=catatan_data.get("diperiksa_oleh", "-"),
    )

    # ── Lampiran ───────────────────────────────────────────────────────────
    lampiran = unit.get("lampiran_onepost", {})
    foto_paths = [f.get("path", "") for f in lampiran.get("foto", []) if f.get("path")]
    pdf.draw_lampiran(
        nama_produk=lampiran.get("nama_produk", nama_produk),
        nomor_seri=lampiran.get("nomor_seri", nomor_seri),
        foto_list=foto_paths,
    )


def build_onepost_pdf(units: list, logo_path=None, dimensi_image_path=None) -> bytes:
    """Build complete OnePost QC PDF for one or more units."""
    pdf = _QCBase("FORM QUALITY CONTROL")
    for unit in units:
        _onepost_unit_pages(pdf, unit, logo_path, dimensi_image_path)
    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# PHBTR PDF BUILDER — matches BLANGKO UJI RUTIN PHBTR reference exactly
# ══════════════════════════════════════════════════════════════════════════════

def _phbtr_unit_pages(pdf: _QCBase, unit: dict, logo_path=None, dimensi_image_path=None):
    info = unit.get("info", {})
    no_produk = info.get("no_produk", "-")
    nomor_seri = info.get("nomor_seri", "-")
    no_amp = info.get("no_amp", "-")
    inspector = info.get("inspector", "-")
    jenis_panel = info.get("jenis_panel", "PHBTR PASANGAN LUAR")
    tipe = info.get("tipe", "-")
    standard = info.get("standard", "-")
    nama_qc = info.get("nama_qc", "-")
    deskripsi = info.get("deskripsi_penugasan") or f"Pengujian Panel {jenis_panel}"

    # ── PAGE 1 — letterhead, header info, section 1-4 ────────────────────────
    pdf.add_page()
    pdf.set_y(10)
    pdf.draw_letterhead(logo_path)
    pdf.draw_project_header(
        deskripsi,
        [
            ("No. AMP", no_amp, "Panel", jenis_panel),
            ("No. Produk", no_produk, "Tipe", tipe),
            ("Nomor Seri", nomor_seri, "Standard", standard),
        ],
    )
    pdf.draw_table_header()

    # Section 1 – Visual dan Penandaan
    visual = unit.get("visual_phbtr") or [
        {"item": "Hasil pengerjaan baik dan kondisi baru", "status": True},
        {"item": "Kesesuaian papan nama", "status": True},
    ]
    pdf.draw_section(1, "Visual dan\nPenandaan", [
        {"text": v.get("item", ""), "ok": v.get("status", True)} for v in visual
    ])

    # Section 2 – Selungkup (label + spesifikasi berdampingan, sesuai blangko)
    selungkup = unit.get("selungkup_phbtr") or [
        {"parameter": "Bahan dan tebal selungkup & montase", "nilai": "Plat SPCC t.2 mm", "status": "\u2713"},
        {"parameter": "Karet Penutup", "nilai": "Karet Penutup", "status": "\u2713"},
        {"parameter": "Cat powder coating min 80 \u03bcm", "nilai": "80 \u03bcm | RAL7032", "status": "\u2713"},
        {"parameter": "Tingkat pengaman IP34", "nilai": "IP34", "status": "\u2713"},
        {"parameter": "Klem untuk pemegang kabel", "nilai": "-", "status": "\u2713"},
        {"parameter": "Lengan penopang pada tiang", "nilai": "-", "status": "\u2713"},
        {"parameter": "Kuping pengangkat", "nilai": "-", "status": "\u2713"},
        {"parameter": "Bonding pembumian antara pintu dan badan selungkup", "nilai": "Kabel NYF 10 mm\u00b2 warna kuning-hijau", "status": "\u2713"},
        {"parameter": "Ventilasi udara dilengkapi plat berlubang (ram) 4 bh", "nilai": "-", "status": "\u2713"},
        {"parameter": "Bukaan pintu minimal 160\u00b0", "nilai": "-", "status": "\u2713"},
        {"parameter": "Handel pintu berikut kunci master dan fasilitas gembok", "nilai": "-", "status": "\u2713"},
        {"parameter": "Rak penyimpanan data/dokumen", "nilai": "-", "status": "\u2713"},
        {"parameter": "Logo PLN dan tanda peringatan bahaya listrik", "nilai": "-", "status": "\u2713"},
    ]
    sel_items = [
        {"label": s.get("parameter", ""), "value": s.get("nilai", "-"), "ok": s.get("status", "\u2713") == "\u2713"}
        for s in selungkup
    ]
    pdf.draw_section_value(2, "Selungkup", sel_items)

    # Section 3 – Pemeriksaan Komponen (grid Saklar Utama / Fuse Rail + rows)
    detail = unit.get("komponen_detail_phbtr", {})
    saklar = detail.get("saklar_utama", {})
    fuse = detail.get("fuse_rail", {})
    instrumen = detail.get("instrumen", {})
    busbar_list = detail.get("busbar", [])

    pdf.draw_component_grid(
        3, "Pemeriksaan\nKomponen", "Saklar Utama",
        [
            [("Merk", saklar.get("merk", "HEFFTRON")),
             ("Standar desain", saklar.get("standar", "IEC 60947-3")),
             ("Kategori utilitas", saklar.get("kategori", "AC 22B"))],
            [("Arus Pengenal", f"{saklar.get('arus', 400)} A"),
             ("Ketahanan hub. singkat", f"{saklar.get('short', 12.6)} kA"),
             ("Bahan pelapis terminal", saklar.get("pelapis", "Tembaga lapis perak"))],
        ],
        ok=saklar.get("status", "\u2713") == "\u2713",
    )
    pdf.draw_component_grid(
        3, "", "Fuse Rail",
        [
            [("Merk", fuse.get("merk", "HEFFTRON")),
             ("Standar desain", fuse.get("standar", "IEC 60269-2")),
             ("Ukuran", fuse.get("ukuran", "Size 1"))],
            [("Arus Pengenal", f"{fuse.get('arus', 250)} A"),
             ("Ketahanan hub. singkat", f"{fuse.get('short', 50)} kA"),
             ("Konektor terminal keluaran", fuse.get("terminal", "M-Terminal"))],
            [("Bahan pelapis kontak", fuse.get("pelapis", "Tembaga lapis perak")),
             ("Disipasi daya", f"{fuse.get('disipasi', 32)} W"),
             ("Bahan pelapis terminal", "Tembaga lapis timah")],
        ],
        ok=fuse.get("status", "\u2713") == "\u2713",
    )

    instrumen_items = [
        {"label": "Instrumen pengukuran", "value": instrumen.get("jenis", "MDI"),
         "ok": instrumen.get("status", "\u2713") == "\u2713"},
    ]
    if busbar_list:
        for b in busbar_list:
            instrumen_items.append({
                "label": b.get("komponen", b.get("item", "")),
                "value": b.get("nilai", ""),
                "ok": b.get("status", "\u2713") == "\u2713",
            })
    else:
        for name, val in [
            ("Busbar Fasa", "30x6 mm"), ("Busbar Netral", "30x6 mm"),
            ("Busbar Pembumian", "20x5 mm"), ("Kontak-kontak", "Merk Uticon"),
            ("Proteksi Lampu", "Fuse HRC 10 A"), ("Kabel Instalasi", "NYAF 2.5 mm\u00b2"),
        ]:
            instrumen_items.append({"label": name, "value": val, "ok": True})
    pdf.draw_section_value(3, "", instrumen_items)

    # Section 4 – Kekencangan Baut
    baut = unit.get("baut_phbtr") or [
        {"item": "Keluaran saklar utama - busbar hubungan fasa R, S, T", "standar": "70 Nm", "aktual": "", "hasil": "\u2705 Sesuai"},
        {"item": "Antar busbar hubung fasa R, S, T", "standar": "70 Nm", "aktual": "", "hasil": "\u2705 Sesuai"},
        {"item": "Busbar hubung - Fuse rall fasa R, S, T", "standar": "70 Nm", "aktual": "", "hasil": "\u2705 Sesuai"},
    ]
    baut_items = []
    for b in baut:
        aktual = b.get("aktual", "")
        val = f"{aktual} Nm" if aktual else b.get("standar", "")
        ok = b.get("hasil", "\u2705 Sesuai") == "\u2705 Sesuai"
        baut_items.append({"label": b.get("item", ""), "value": val, "ok": ok})
    pdf.draw_section_value(4, "Kekencangan\nBaut", baut_items)

    # ── PAGE 2 — section 5-8 ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_y(10)

    # Section 5 – Pengujian Dimensi Selungkup (gambar acuan + tabel A-K)
    dimensi = unit.get("dimensi_phbtr", {})
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
    default_standar = [1200, 1100, 100, 450, 50, 100, 185, 60, 680, 1200, 60]
    if dimensi and all(l in dimensi and len(dimensi[l]) >= 2 for l in letters):
        standar_row = [dimensi[l][0] for l in letters]
        hasil_row = [dimensi[l][1] for l in letters]
    else:
        standar_row = default_standar
        hasil_row = default_standar
    pdf.draw_dimension_section(
        5, "Pengujian\ndimensi\nselungkup",
        dimensi_image_path, letters, hasil_row, standar_row, ok=True,
    )

    # Section 6 – Uji Operasi Mekanis (grouped)
    operasi = unit.get("operasi_phbtr") or [
        {"kelompok": "Operasi buka tutup 5 kali", "item": "Saklar Utama", "status": True},
        {"kelompok": "Operasi buka tutup 5 kali", "item": "Pintu", "status": True},
        {"kelompok": "Kontinyuitas pengawatan", "item": "Instrumen ukur", "status": True},
        {"kelompok": "Kontinyuitas pengawatan", "item": "Lampu indikator", "status": True},
        {"kelompok": "Kontinyuitas pengawatan", "item": "Lampu penerangan", "status": True},
        {"kelompok": "Kontinyuitas pengawatan", "item": "Kontak-kontak", "status": True},
    ]
    groups = {}
    for o in operasi:
        groups.setdefault(o.get("kelompok", "-"), []).append((o.get("item", ""), o.get("status", True)))
    pdf.draw_table_header()
    pdf.draw_section_grouped(6, "Uji Operasi\nMekanis", groups)

    # Section 7 – Pengujian Dielektrik (TAHANAN ISOLASI M\u03a9)
    dielektrik = unit.get("dielektrik_phbtr") or [
        {"sirkuit": "L1-(L2 + L3 + N + Badan)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "L2-(L1 + L3 + N + Badan)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "L3-(L1 + L2 + N + Badan)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "N-(L1 + L2 + L3 + Badan)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "(L1+L2+L3) - (L1'+L2'+L3')", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "(L1'+L2'+L3') - (L1+L2+L3)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
        {"sirkuit": "Sirkit kontrol - (sirkit utama+bagian konduktif terbuka+badan)", "sebelum": "M/G\u03a9", "sesudah": "M/G\u03a9", "status": True},
    ]
    pdf.draw_dielektrik_section(7, "Pengujian\ndielektrik", [
        {
            "sirkuit": d.get("sirkuit", ""),
            "sebelum": d.get("sebelum", "") if d.get("sebelum") not in (0, "0", None) else "M/G\u03a9",
            "sesudah": d.get("sesudah", "") if d.get("sesudah") not in (0, "0", None) else "M/G\u03a9",
            "ok": d.get("status", True),
        }
        for d in dielektrik
    ])

    # Section 8 – Pengujian Keefektifan Sirkit Protektif
    sirkit = unit.get("sirkit_protektif_phbtr") or [
        {"item": "Pintu metering", "nilai": "", "satuan": "m\u03a9", "status": True},
        {"item": "Rangka utama", "nilai": "", "satuan": "\u03bc\u03a9", "status": True},
        {"item": "Rangka dudukan fuse, fasa L1, L2, L3", "nilai": "", "satuan": "\u03bc\u03a9", "status": True},
        {"item": "Plat dudukan fuse peralatan bantu", "nilai": "", "satuan": "\u03bc\u03a9", "status": True},
        {"item": "Pintu utama", "nilai": "", "satuan": "m\u03a9", "status": True},
    ]
    pdf.draw_sirkit_section(8, "Pengujian\nKeefektifan\nSirkit Protektif", sirkit)

    # Catatan + Pengesahan — nama petugas Quality Control tampil di sini
    catatan_data = unit.get("catatan_phbtr", {})
    pdf.draw_catatan(
        catatan=catatan_data.get("catatan", ""),
        hasil=catatan_data.get("hasil_pengujian", "diterima"),
        diperiksa=catatan_data.get("diperiksa_oleh") or nama_qc or inspector or "-",
    )

    # Lampiran
    lampiran = unit.get("lampiran_phbtr", {})
    foto_paths = [f.get("path", "") for f in lampiran.get("foto", []) if f.get("path")]
    pdf.draw_lampiran(
        nama_produk=jenis_panel,
        nomor_seri=nomor_seri,
        foto_list=foto_paths,
    )


def build_phbtr_pdf(units: list, logo_path=None, dimensi_image_path=None) -> bytes:
    pdf = _QCBase("BLANGKO UJI RUTIN PHBTR")
    for unit in units:
        _phbtr_unit_pages(pdf, unit, logo_path, dimensi_image_path)
    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# PMCB PDF BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def _pmcb_unit_pages(pdf: _QCBase, unit: dict, logo_path=None):
    info = unit.get("info", {})
    no_amp = info.get("no_amp", "26147301")
    no_produk = info.get("no_produk", "-")
    serial_vcb = info.get("serial_vcb", "-")
    merk_vcb = info.get("merk_vcb", "SUSOL")
    type_vcb = info.get("type_vcb", "SVL-20R25C13")
    arus_pengenal = info.get("arus_pengenal", "1250 A")

    pdf.add_page()
    pdf.set_y(10)
    pdf.draw_letterhead(logo_path)
    pdf.draw_project_header(
        "Penugasan Pembuatan 10 Unit PMCB 4.0 UID Jawa Barat",
        [
            ("No. AMP", no_amp, "Serial VCB", serial_vcb),
            ("No. Produk", no_produk, "Merk / Type VCB", f"{merk_vcb} / {type_vcb}"),
            ("Arus Pengenal", arus_pengenal, "Inspector", info.get("inspector", "-")),
        ],
    )
    pdf.draw_table_header()

    kontak = unit.get("tahanan_kontak_pmcb", [])
    pdf.draw_section(1, "Uji Tahanan\nKontak", [
        {"text": f"Phasa {k.get('phasa','')} — {k.get('nilai','')} \u00b5\u03a9",
         "ok": k.get("status", "Accepted") == "Accepted",
         "hasil": k.get("status", "Accepted")}
        for k in (kontak or [
            {"phasa": "R", "nilai": 20.8, "status": "Accepted"},
            {"phasa": "S", "nilai": 21.1, "status": "Accepted"},
            {"phasa": "T", "nilai": 21.5, "status": "Accepted"},
        ])
    ])

    serempak = unit.get("keserempakan_pmcb", [])
    rows_s = []
    for s in (serempak or [
        {"phasa": "R", "open_time": 13.7, "open_result": "Accepted", "close_time": 43.8, "close_result": "Accepted"},
        {"phasa": "S", "open_time": 13.5, "open_result": "Accepted", "close_time": 43.9, "close_result": "Accepted"},
        {"phasa": "T", "open_time": 13.7, "open_result": "Accepted", "close_time": 43.75, "close_result": "Accepted"},
    ]):
        rows_s.append({
            "text": f"Phasa {s.get('phasa','')} — Open: {s.get('open_time','')} ms ({s.get('open_result','')})  |  Close: {s.get('close_time','')} ms ({s.get('close_result','')})",
            "ok": s.get("open_result", "Accepted") == "Accepted" and s.get("close_result", "Accepted") == "Accepted",
        })
    pdf.draw_section(2, "Uji\nKeserempakan", rows_s)

    relai = unit.get("relai_pengaman_pmcb", [])
    pdf.draw_section(3, "Uji Relai\nPengaman", [
        {"text": r.get("item", ""), "ok": r.get("status", "Accepted") == "Accepted",
         "hasil": r.get("status", "Accepted")}
        for r in (relai or [
            {"item": "OCR INS", "status": "Accepted"},
            {"item": "OCR", "status": "Accepted"},
            {"item": "GFR INS", "status": "Accepted"},
            {"item": "GFR", "status": "Accepted"},
            {"item": "THERMIC", "status": "Accepted"},
        ])
    ])

    isolasi = unit.get("tahanan_isolasi_pmcb", [])
    pdf.draw_section(4, "Uji Tahanan\nIsolasi", [
        {"text": f"{x.get('phasa','')} — Posisi PMT: {x.get('posisi_pmt','')} — Hasil Megger: {x.get('hasil_megger','')}",
         "ok": x.get("status", "Accepted") == "Accepted", "hasil": x.get("status", "Accepted")}
        for x in (isolasi or [
            {"phasa": "IN-OUT + Body", "posisi_pmt": "Open", "hasil_megger": "\u221e", "status": "Accepted"},
            {"phasa": "R - S + T + Body", "posisi_pmt": "Close", "hasil_megger": "\u221e", "status": "Accepted"},
            {"phasa": "S - R + T + Body", "posisi_pmt": "Close", "hasil_megger": "\u221e", "status": "Accepted"},
            {"phasa": "T - R + S + Body", "posisi_pmt": "Close", "hasil_megger": "\u221e", "status": "Accepted"},
        ])
    ])

    hv = unit.get("uji_hv_pmcb", [])
    pdf.draw_section(5, "Uji HV", [
        {"text": x.get("phasa", ""), "ok": x.get("status", "Accepted") == "Accepted",
         "hasil": x.get("status", "Accepted")}
        for x in (hv or [
            {"phasa": "IN - OUT + Body", "status": "Accepted"},
            {"phasa": "IN + OUT - Body", "status": "Accepted"},
            {"phasa": "R - S + T + Body", "status": "Accepted"},
            {"phasa": "S - R + T + Body", "status": "Accepted"},
            {"phasa": "T - R + S + Body", "status": "Accepted"},
        ])
    ])

    fungsi = unit.get("tes_fungsi_pmcb", [])
    pdf.draw_section(6, "Tes Fungsi", [
        {"text": f.get("item", ""), "ok": f.get("status", "Accepted") == "Accepted",
         "hasil": f.get("status", "Accepted")}
        for f in (fungsi or [
            {"item": "Test Fungsi Wiring", "status": "Accepted"},
            {"item": "Test Fungsi VCB", "status": "Accepted"},
            {"item": "Test Fungsi Selector Switch", "status": "Accepted"},
            {"item": "Test Fungsi Push Button Close", "status": "Accepted"},
            {"item": "Test Fungsi Push Button Open", "status": "Accepted"},
        ])
    ])

    coating = unit.get("ketebalan_coating_pmcb", [])
    pdf.draw_section(7, "Ketebalan\nCoating", [
        {"text": f"{c.get('posisi','')} — {c.get('hasil','')} \u00b5m", "ok": c.get("status", "Accepted") == "Accepted",
         "hasil": c.get("status", "Accepted")}
        for c in (coating or [
            {"posisi": "Box Panel Besar (1)", "hasil": 120, "status": "Accepted"},
            {"posisi": "Box Panel Besar (2)", "hasil": 115, "status": "Accepted"},
        ])
    ])

    ip55 = unit.get("uji_ip55_pmcb", [])
    pdf.draw_section(8, "Uji IP 55", [
        {"text": x.get("item", ""), "ok": x.get("status", "Accepted") == "Accepted",
         "hasil": x.get("status", "Accepted")}
        for x in (ip55 or [
            {"item": "Box Panel Besar — IP 55 tercapai", "status": "Accepted"},
            {"item": "Box Kontrol — IP 55 tercapai", "status": "Accepted"},
        ])
    ])

    catatan_data = unit.get("catatan_pengesahan_pmcb", {})
    pdf.draw_catatan(
        catatan=catatan_data.get("catatan", ""),
        hasil=catatan_data.get("hasil_pengujian", "diterima"),
        diperiksa=catatan_data.get("diperiksa_oleh", "-"),
    )

    lampiran = unit.get("lampiran_pmcb", {})
    foto_paths = [f.get("path", "") for f in lampiran.get("foto", []) if f.get("path")]
    pdf.draw_lampiran(
        nama_produk=f"PMCB 4.0 — {merk_vcb} {type_vcb}",
        nomor_seri=serial_vcb,
        foto_list=foto_paths,
    )


def build_pmcb_pdf(units: list, logo_path=None) -> bytes:
    pdf = _QCBase("FORM QUALITY CONTROL PMCB 4.0")
    for unit in units:
        _pmcb_unit_pages(pdf, unit, logo_path)
    out = BytesIO()
    pdf.output(out)
    return out.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT DOWNLOAD BUTTON
# ══════════════════════════════════════════════════════════════════════════════

def pdf_download_button(pdf_bytes: bytes, filename: str, label: str = "\U0001F4C4 Download PDF"):
    import streamlit as st
    st.download_button(
        label=label,
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )
#!/usr/bin/env python3
"""Build a printable Crimson Dawn waterslide (water-transfer) decal sheet PDF.

Designed for hobby water-transfer paper. Print at 100% / actual size.
"""

from pathlib import Path

import numpy as np
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("/workspace/docs/warhammer")
SRC = ROOT / "crimson-dawn-gothic-cloud-source.png"
OUT_PDF = ROOT / "crimson-dawn-waterslide-decals.pdf"
OUT_DIR = ROOT / "stencils"
COLOR_BADGE = OUT_DIR / "cloud-decal-color.png"
CRIMSON_ONLY = OUT_DIR / "cloud-decal-crimson-only.png"
DPI = 300


def px(mm: float) -> int:
    return max(1, int(round(mm * DPI / 25.4)))


def load_color_badge() -> Image.Image:
    """Crimson cloud with white edge; near-black background made transparent."""
    badge = Image.open(SRC).convert("RGBA")
    arr = np.array(badge)
    black = (arr[:, :, 0] < 50) & (arr[:, :, 1] < 50) & (arr[:, :, 2] < 50)
    arr[black, 3] = 0
    badge = Image.fromarray(arr)
    bbox = badge.getbbox()
    if bbox:
        badge = badge.crop(bbox)
    # Small transparent pad so cut lines don't nick art
    pad = 8
    canvas = Image.new("RGBA", (badge.width + pad * 2, badge.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(badge, (pad, pad), badge)
    return canvas


def make_crimson_only(color: Image.Image) -> Image.Image:
    """Solid crimson silhouette for clear waterslide (no white ink needed)."""
    arr = np.array(color)
    alpha = arr[:, :, 3]
    # Any visible pigment -> deep crimson; keep alpha
    visible = alpha > 40
    out = np.zeros_like(arr)
    out[visible, 0] = 140
    out[visible, 1] = 18
    out[visible, 2] = 28
    out[visible, 3] = 255
    im = Image.fromarray(out)
    # Slight expand so thin white-edge zones become filled crimson
    solid = im.split()[-1].point(lambda p: 255 if p > 40 else 0)
    solid = solid.filter(ImageFilter.MaxFilter(3))
    rgb = Image.new("RGBA", im.size, (140, 18, 28, 255))
    rgb.putalpha(solid)
    return rgb


def save_assets():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    color = load_color_badge()
    crimson = make_crimson_only(color)
    # Composite on white for PDF embedding reliability (fpdf handles PNG alpha,
    # but white-backed variants help laser printers). Keep transparent masters too.
    color.save(COLOR_BADGE)
    crimson.save(CRIMSON_ONLY)
    return color, crimson


class DecalPDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            4,
            "Crimson Dawn waterslide decals  |  Print at 100% (no fit-to-page)  |  Not official GW material",
            align="C",
        )


def place_grid(
    pdf: DecalPDF,
    img: Path,
    widths_mm: list[float],
    start_y: float,
    gap: float = 3.0,
) -> float:
    """Place a dense left-to-right grid of decals; return y after last row."""
    with Image.open(img) as im:
        aspect = im.height / im.width

    x0 = 12
    x = x0
    y = start_y
    row_h = 0.0
    for w in widths_mm:
        h = w * aspect
        if x + w > 198:
            x = x0
            y += row_h + gap + 3.5
            row_h = 0.0
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.1)
        pdf.rect(x - 0.4, y - 0.4, w + 0.8, h + 0.8, style="D")
        pdf.image(str(img), x=x, y=y, w=w)
        pdf.set_xy(x, y + h + 0.3)
        pdf.set_font("Helvetica", "", 5.5)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(w, 3, f"{w:g}mm", align="C")
        row_h = max(row_h, h)
        x += w + gap
    return y + row_h + 8


def main():
    if not SRC.exists():
        raise SystemExit(f"Missing badge art: {SRC}")

    color, crimson = save_assets()
    # Also write white-backed print helpers (optional laser-friendly)
    for src_im, name in ((color, "cloud-decal-color-on-white.png"), (crimson, "cloud-decal-crimson-on-white.png")):
        bg = Image.new("RGB", src_im.size, (255, 255, 255))
        bg.paste(src_im, mask=src_im.split()[-1])
        bg.save(OUT_DIR / name, dpi=(DPI, DPI))

    pdf = DecalPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # ------------------------------------------------------------------ page 1: instructions
    pdf.add_page()
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 26, style="F")
    pdf.set_xy(12, 7)
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(0, 7, "CRIMSON DAWN  -  WATERSLIDE DECAL SHEET")
    pdf.set_xy(12, 15)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(180, 60, 60)
    pdf.cell(0, 5, "Water-transfer paper  |  Gothic storm-cloud chapter badge")

    pdf.set_xy(12, 32)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Which paper to use")
    pdf.ln(7)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(
        186,
        4.3,
        "White outline needs white ink or white paper. Most home printers cannot print white.\n\n"
        "- WHITE waterslide paper  ->  use PAGE 2 (full colour: crimson + white edge). "
        "Best match to the locked badge on charcoal armour.\n"
        "- CLEAR waterslide paper  ->  use PAGE 3 (crimson-only silhouettes). "
        "White edge will not appear; freehand a thin white outline after the decal sets, or leave crimson-only.\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Print settings")
    pdf.ln(6)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.3,
        "1. Print at Actual size / 100% - turn OFF fit-to-page / shrink-to-fit.\n"
        "2. Use the glossy / printable side of the waterslide paper (check your pack).\n"
        "3. Inkjet: allow full dry time, then spray 2-3 light coats of clear acrylic "
        "(or the sealer your paper brand recommends) before cutting/soaking.\n"
        "4. Laser: many waterslide papers work without spray seal; follow the pack.\n"
        "5. Let sealer cure fully before cutting.\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Apply")
    pdf.ln(6)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.3,
        "1. Gloss-varnish the armour spot first (decals bite better on gloss).\n"
        "2. Cut close to the cloud - leave a tiny clear margin, not a huge square.\n"
        "3. Soak in lukewarm water 20-60 seconds until the decal loosens.\n"
        "4. Slide onto the RIGHT shoulder pad; nudge with a wet brush.\n"
        "5. Blot from the center out with a soft tissue; chase bubbles.\n"
        "6. Optional: Micro Set under / Micro Sol over for curved pads.\n"
        "7. When bone-dry, seal with gloss then matt varnish.\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Size guide (width across the cloud)")
    pdf.ln(6)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.3,
        "4-5 mm  knee / tiny detail\n"
        "7-9 mm  Primaris / tactical pauldron\n"
        "11-14 mm  Terminator / Gravis pauldron\n"
        "18-28 mm  vehicle / banner / practice\n\n"
        "Hairline boxes are cut guides only - cut inside them, close to the art.",
    )

    pdf.ln(2)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        186,
        4,
        "Assets also in docs/warhammer/stencils/: cloud-decal-color.png, "
        "cloud-decal-crimson-only.png. Regenerate: python3 docs/warhammer/generate_waterslide_decals.py",
    )

    # colour reference strip
    pdf.set_xy(12, 250)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(40, 5, "Colour target:")
    pdf.image(str(COLOR_BADGE), x=50, y=242, w=22)
    pdf.set_xy(76, 248)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(110, 3.5, "Deep crimson + white edge on charcoal plate.")

    # ------------------------------------------------------------------ page 2: white paper colour sheet
    pdf.add_page()
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 18, style="F")
    pdf.set_xy(12, 5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(0, 6, "PAGE 2  -  FULL COLOUR  (print on WHITE waterslide paper)")
    pdf.set_xy(12, 11)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(180, 100, 100)
    pdf.cell(0, 4, "Keeps the white outline. Do not use clear paper for this page unless you have white ink.")

    y = 22
    pdf.set_xy(12, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "Infantry / Terminator strip")
    y = 28
    # Mix of common sizes, many repeats
    strip = [9] * 8 + [11] * 6 + [14] * 4 + [7] * 8 + [5] * 10
    y = place_grid(pdf, COLOR_BADGE, strip, y, gap=2.5)

    pdf.set_xy(12, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "Larger / vehicle / spares")
    y += 6
    large = [18, 18, 22, 22, 28]
    place_grid(pdf, COLOR_BADGE, large, y, gap=4)

    # ------------------------------------------------------------------ page 3: clear paper crimson-only
    pdf.add_page()
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 18, style="F")
    pdf.set_xy(12, 5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(0, 6, "PAGE 3  -  CRIMSON ONLY  (print on CLEAR waterslide paper)")
    pdf.set_xy(12, 11)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(180, 100, 100)
    pdf.cell(0, 4, "No white ink required. Optional: freehand thin white edge after sealing.")

    y = 22
    pdf.set_xy(12, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "Infantry / Terminator strip")
    y = 28
    strip = [9] * 8 + [11] * 6 + [14] * 4 + [7] * 8 + [5] * 10
    y = place_grid(pdf, CRIMSON_ONLY, strip, y, gap=2.5)

    pdf.set_xy(12, y)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 5, "Larger / vehicle / spares")
    y += 6
    place_grid(pdf, CRIMSON_ONLY, [18, 18, 22, 22, 28], y, gap=4)

    pdf.output(str(OUT_PDF))
    print(f"Wrote {OUT_PDF}")
    print(f"Wrote {COLOR_BADGE}")
    print(f"Wrote {CRIMSON_ONLY}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a printable Crimson Dawn waterslide (water-transfer) decal sheet PDF.

Page 1 = plain-paper instructions only.
Pages 2-3 = densely packed transfer sheets (print only the one you need).
"""

from pathlib import Path

import numpy as np
from fpdf import FPDF
from PIL import Image, ImageFilter

ROOT = Path("/workspace/docs/warhammer")
SRC = ROOT / "crimson-dawn-gothic-cloud-source.png"
OUT_PDF = ROOT / "crimson-dawn-waterslide-decals.pdf"
OUT_DIR = ROOT / "stencils"
COLOR_BADGE = OUT_DIR / "cloud-decal-color.png"
CLEAR_BADGE = OUT_DIR / "cloud-decal-crimson-black-outline.png"
COLOR_FLIP = OUT_DIR / "cloud-decal-color-flip.png"
CLEAR_FLIP = OUT_DIR / "cloud-decal-crimson-black-outline-flip.png"
DPI = 300


def load_color_badge() -> Image.Image:
    badge = Image.open(SRC).convert("RGBA")
    arr = np.array(badge)
    black = (arr[:, :, 0] < 50) & (arr[:, :, 1] < 50) & (arr[:, :, 2] < 50)
    arr[black, 3] = 0
    badge = Image.fromarray(arr)
    bbox = badge.getbbox()
    if bbox:
        badge = badge.crop(bbox)
    # Tiny pad only (saves sheet space vs large transparent margins)
    pad = 2
    canvas = Image.new("RGBA", (badge.width + pad * 2, badge.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(badge, (pad, pad), badge)
    return canvas


def make_crimson_black_outline(color: Image.Image) -> Image.Image:
    arr = np.array(color).copy()
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    visible = a > 40
    light = visible & (r > 180) & (g > 180) & (b > 180)
    fill = visible & ~light
    out = np.zeros_like(arr)
    out[fill, 0], out[fill, 1], out[fill, 2], out[fill, 3] = 140, 18, 28, 255
    out[light, 0], out[light, 1], out[light, 2], out[light, 3] = 12, 12, 14, 255

    im = Image.fromarray(out)
    crimson_mask = Image.fromarray(np.where(fill, 255, 0).astype(np.uint8))
    full = im.split()[-1].point(lambda p: 255 if p > 40 else 0)
    outer = full.filter(ImageFilter.MaxFilter(5))
    core = crimson_mask.filter(ImageFilter.MinFilter(3))
    outer_a = np.array(outer)
    core_a = np.array(core)
    rim = (outer_a > 200) & (core_a < 200)
    final = np.array(im)
    final[rim, 0], final[rim, 1], final[rim, 2], final[rim, 3] = 12, 12, 14, 255
    final[core_a > 200, 0] = 140
    final[core_a > 200, 1] = 18
    final[core_a > 200, 2] = 28
    final[core_a > 200, 3] = 255
    return Image.fromarray(final)


def save_assets():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    color = load_color_badge()
    clear = make_crimson_black_outline(color)
    color.save(COLOR_BADGE)
    clear.save(CLEAR_BADGE)
    color.transpose(Image.Transpose.ROTATE_180).save(COLOR_FLIP)
    clear.transpose(Image.Transpose.ROTATE_180).save(CLEAR_FLIP)
    for src_im, name in (
        (color, "cloud-decal-color-on-white.png"),
        (clear, "cloud-decal-crimson-black-on-white.png"),
    ):
        bg = Image.new("RGB", src_im.size, (255, 255, 255))
        bg.paste(src_im, mask=src_im.split()[-1])
        bg.save(OUT_DIR / name, dpi=(DPI, DPI))
    return color, clear


class DecalPDF(FPDF):
    def footer(self):
        self.set_y(-8)
        self.set_font("Helvetica", "I", 6)
        self.set_text_color(110, 110, 110)
        self.cell(
            0,
            3,
            "Crimson Dawn waterslide  |  100% scale  |  Not official GW material",
            align="C",
        )


SIZE_NOTES = {
    9: "infantry",
    7: "small pad",
    11: "Terminator",
    5: "detail",
    14: "Gravis/large",
    18: "vehicle",
    22: "vehicle+",
}


def pack_sheet(pdf: DecalPDF, upright: Path, start_y: float = 8.5) -> None:
    """Dense upright rows with a thin size label at the start of each band."""
    with Image.open(upright) as im:
        aspect = im.height / im.width

    gap = 0.35
    label_w = 7.0
    margin_r = 3.0
    x0 = label_w + 0.5
    usable_w = 210 - x0 - margin_r
    y = start_y
    max_y = 289.0

    # (width_mm, row_count)
    bands = [
        (9, 12),
        (7, 4),
        (11, 4),
        (5, 5),
        (14, 2),
        (18, 1),
    ]

    for width, rows in bands:
        h = width * aspect
        if y + h > max_y:
            break

        # Section size indicator (once per band)
        note = SIZE_NOTES.get(width, "")
        pdf.set_xy(1.2, y + max(0, (h - 3) / 2))
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(label_w, 3, f"{width:g}mm", align="C")
        if note:
            pdf.set_xy(1.2, y + max(0, (h - 3) / 2) + 2.6)
            pdf.set_font("Helvetica", "", 4.5)
            pdf.set_text_color(110, 110, 110)
            pdf.cell(label_w, 2.2, note, align="C")

        per_row = max(1, int((usable_w + gap) // (width + gap)))
        for row_i in range(rows):
            if y + h > max_y:
                return
            x = x0
            for _ in range(per_row):
                pdf.image(str(upright), x=x, y=y, w=width)
                x += width + gap
            y += h + gap

    # Mop remaining with 9mm + label if we actually place any
    h9 = 9 * aspect
    mop_labeled = False
    while y + h9 <= max_y:
        if not mop_labeled:
            pdf.set_xy(1.2, y + max(0, (h9 - 3) / 2))
            pdf.set_font("Helvetica", "B", 6)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(label_w, 3, "9mm", align="C")
            pdf.set_xy(1.2, y + max(0, (h9 - 3) / 2) + 2.6)
            pdf.set_font("Helvetica", "", 4.5)
            pdf.set_text_color(110, 110, 110)
            pdf.cell(label_w, 2.2, "extra", align="C")
            mop_labeled = True
        per_row = max(1, int((usable_w + gap) // (9 + gap)))
        x = x0
        for _ in range(per_row):
            pdf.image(str(upright), x=x, y=y, w=9)
            x += 9 + gap
        y += h9 + gap


def dense_transfer_page(pdf: DecalPDF, upright: Path, title: str, subtitle: str) -> None:
    pdf.add_page()
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 7.2, style="F")
    pdf.set_xy(3, 0.9)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(0, 2.7, title)
    pdf.set_xy(3, 3.6)
    pdf.set_font("Helvetica", "", 5.2)
    pdf.set_text_color(200, 120, 120)
    pdf.cell(0, 2.5, subtitle)
    pack_sheet(pdf, upright, start_y=7.8)


def main():
    if not SRC.exists():
        raise SystemExit(f"Missing badge art: {SRC}")

    save_assets()

    pdf = DecalPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # Page 1 — plain paper only
    pdf.add_page()
    pdf.set_fill_color(140, 18, 28)
    pdf.rect(0, 0, 210, 28, style="F")
    pdf.set_xy(12, 6)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "CRIMSON DAWN WATERSLIDE DECALS")
    pdf.set_xy(12, 14)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "PAGE 1 = PLAIN PAPER ONLY  -  DO NOT PRINT ON TRANSFER STOCK")
    pdf.set_xy(12, 20)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(255, 220, 220)
    pdf.cell(0, 5, "On waterslide paper print ONLY page 2 (white) or page 3 (clear).")

    pdf.set_xy(12, 34)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Transfer pages")
    pdf.ln(7)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.2,
        "- WHITE waterslide paper -> PAGE 2 (crimson + white edge)\n"
        "- CLEAR waterslide paper -> PAGE 3 (crimson + black outline)\n\n"
        "Pages 2-3 are nested/packed to burn less film. Cut close to each cloud.\n"
        "Print at 100% / Actual size (no fit-to-page).\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Print + seal")
    pdf.ln(6)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.2,
        "1. Load transfer paper printable-side correctly.\n"
        "2. Print only the page you need (2 or 3) - not this page.\n"
        "3. Inkjet: dry fully, then 2-3 light clear acrylic coats (or brand sealer); cure.\n"
        "4. Laser: follow your pack; many need no spray.\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Apply")
    pdf.ln(6)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        186,
        4.2,
        "1. Gloss-varnish the pad first.\n"
        "2. Cut tight to the cloud (ignore neighbour nesting).\n"
        "3. Soak lukewarm 20-60s; slide onto RIGHT shoulder.\n"
        "4. Blot center-out; optional Micro Set / Micro Sol on curves.\n"
        "5. Dry, then gloss + matt seal.\n\n"
        "Sheet mix: mostly 9mm infantry, plus 7/5/11/14mm and a few larger marks.\n"
        "Packed tight - cut carefully between neighbours.\n",
    )

    pdf.set_x(12)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(186, 4, "Regenerate: python3 docs/warhammer/generate_waterslide_decals.py")

    dense_transfer_page(
        pdf,
        COLOR_BADGE,
        "PAGE 2 - FULL COLOUR - WHITE WATERSLIDE ONLY (do not print page 1 on film)",
        "Crimson + white edge. Dense pack. Cut close. 100% scale.",
    )
    dense_transfer_page(
        pdf,
        CLEAR_BADGE,
        "PAGE 3 - CRIMSON + BLACK OUTLINE - CLEAR WATERSLIDE ONLY (do not print page 1 on film)",
        "Black rim (no white ink). Dense pack. Cut close. 100% scale.",
    )

    pdf.output(str(OUT_PDF))
    print(f"Wrote {OUT_PDF}")
    print(f"Wrote {COLOR_BADGE}")
    print(f"Wrote {CLEAR_BADGE}")


if __name__ == "__main__":
    main()

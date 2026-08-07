#!/usr/bin/env python3
"""Build a printable Crimson Dawn gothic cloud stencil PDF."""

from pathlib import Path

from fpdf import FPDF
from PIL import Image, ImageFilter, ImageOps

ROOT = Path("/workspace/docs/warhammer")
SRC = Path("/opt/cursor/artifacts/assets/crimson-dawn-gothic-cloud-badge.png")
OUT_PDF = ROOT / "crimson-dawn-cloud-stencil.pdf"
OUT_DIR = ROOT / "stencils"
ASSET_COPY = ROOT / "crimson-dawn-gothic-cloud-source.png"


def make_silhouette(src: Path, out: Path, invert: bool = False) -> Path:
    """Extract a high-contrast cloud silhouette for stencil cutting."""
    im = Image.open(src).convert("RGBA")
    # Drop near-black background; keep crimson/white cloud pixels
    pixels = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Keep bright crimson / white / light grey mark; kill dark bg
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            if a < 20 or (r < 50 and g < 50 and b < 50) or lum < 35:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = (0, 0, 0, 255)

    # Tight crop to content
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)

    # Pad and place on white for print/cut
    pad = 24
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (255, 255, 255, 255))
    canvas.paste(im, (pad, pad), im)

    # Slight clean-up
    solid = canvas.convert("L")
    solid = solid.point(lambda p: 0 if p < 200 else 255)
    solid = solid.filter(ImageFilter.MedianFilter(3))
    if invert:
        solid = ImageOps.invert(solid)

    out.parent.mkdir(parents=True, exist_ok=True)
    solid.convert("RGB").save(out, dpi=(300, 300))
    return out


def mm(px_at_300dpi: float) -> float:
    return px_at_300dpi * 25.4 / 300.0


class StencilPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(80, 80, 80)
        self.cell(
            0,
            5,
            "Crimson Dawn - Gothic storm-cloud stencil sheet  |  Not official GW material",
            align="C",
        )


def add_stencil_row(pdf: StencilPDF, img: Path, label: str, widths_mm: list[float], y: float) -> float:
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, label)
    y += 8
    x = 14
    for w in widths_mm:
        # Preserve aspect from image
        with Image.open(img) as im:
            aspect = im.height / im.width
        h = w * aspect
        if x + w > 196:
            x = 14
            y += h + 10
        pdf.image(str(img), x=x, y=y, w=w)
        pdf.set_xy(x, y + h + 1)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(w, 4, f"{w:.0f} mm wide", align="C")
        x += w + 8
    return y + max(w * (Image.open(img).height / Image.open(img).width) for w in widths_mm) + 14


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    ASSET_COPY.write_bytes(SRC.read_bytes())

    fill = make_silhouette(SRC, OUT_DIR / "cloud-stencil-fill.png", invert=False)
    # Mask version: black paper with white hole guide (same as fill for hand-cut;
    # also export a bold filled version already done)

    pdf = StencilPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # Header
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 28, style="F")
    pdf.set_xy(14, 8)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(220, 220, 220)
    pdf.cell(0, 8, "CRIMSON DAWN  -  CLOUD STENCIL SHEET")
    pdf.set_xy(14, 16)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(180, 60, 60)
    pdf.cell(0, 6, "Gothic imperial storm-cloud  |  Print at 100% (no fit-to-page)")

    pdf.set_text_color(30, 30, 30)
    pdf.set_xy(14, 34)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "How to use")
    pdf.ln(7)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    steps = (
        "1. Print this PDF at actual size (100% / turn OFF fit to page).\n"
        "2. Cut out a cloud silhouette with a hobby knife, or load the PNG "
        "from docs/warhammer/stencils/ into a vinyl cutter.\n"
        "3. Apply the mask to the RIGHT shoulder pad (gloss varnish first helps).\n"
        "4. Sponge or stipple deep crimson through the opening; remove mask.\n"
        "5. Freehand a thin white outline around the cloud if desired.\n"
        "6. Seal with matt varnish.\n"
    )
    pdf.multi_cell(182, 4.5, steps)

    pdf.ln(2)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        182,
        4,
        "Tip: Terminator and tactical pauldrons are curved. Cut small relief slits "
        "at the mask edges if needed, or paint in two light passes.",
    )

    y = pdf.get_y() + 4
    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(0.4)
    pdf.line(14, y, 196, y)

    # Reference colour badge (small)
    y += 4
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Colour reference (not a stencil)")
    y += 8
    pdf.image(str(SRC), x=14, y=y, w=32)
    pdf.set_xy(50, y)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(
        140,
        4.5,
        "Target look: deep crimson fill, thin white outline, on charcoal-black armour. "
        "Stencil provides the crimson shape only.",
    )
    y += 36

    pdf.set_draw_color(140, 18, 28)
    pdf.line(14, y, 196, y)
    y += 4

    # Stencil sizes - page 1 tactical / terminator
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Cut stencils - infantry sizes (black = keep mask / cut out interior)")
    y += 8

    # Manual placement for clean layout
    sizes = [
        ("Terminator pauldron (~)", 14),
        ("Terminator small / veteran", 11),
        ("Tactical / Primaris pauldron", 9),
        ("Knee / detail", 6),
    ]
    x = 14
    row_h = 0
    for label, width in sizes:
        with Image.open(fill) as im:
            aspect = im.height / im.width
        height = width * aspect
        if x + width > 196:
            x = 14
            y += row_h + 12
            row_h = 0
        pdf.image(str(fill), x=x, y=y, w=width)
        pdf.set_xy(x, y + height + 1)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(max(width, 28), 3.2, f"{label}\n{width} mm", align="C")
        x += max(width, 28) + 10
        row_h = max(row_h, height)

    # Page 2 - larger sizes + duplicates for a squad
    pdf.add_page()
    pdf.set_fill_color(20, 20, 22)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.set_xy(14, 8)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(220, 220, 220)
    pdf.cell(0, 8, "CRIMSON DAWN  -  EXTRA CUTS / VEHICLE")

    y = 30
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Larger marks (vehicle, banner, practice)")
    y += 10

    large = [22, 28, 36]
    x = 14
    for width in large:
        with Image.open(fill) as im:
            aspect = im.height / im.width
        height = width * aspect
        if y + height > 250:
            break
        if x + width > 196:
            x = 14
            y += 55
        pdf.image(str(fill), x=x, y=y, w=width)
        pdf.set_xy(x, y + height + 1)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(width, 4, f"{width} mm wide", align="C")
        x += width + 10

    y = 120
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, "Squad strip - repeated Terminator size (cut several)")
    y += 8
    x = 14
    for i in range(8):
        width = 12
        with Image.open(fill) as im:
            aspect = im.height / im.width
        height = width * aspect
        if x + width > 196:
            x = 14
            y += height + 10
        pdf.image(str(fill), x=x, y=y, w=width)
        x += width + 6

    y += 40
    pdf.set_xy(14, y)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(
        182,
        4,
        "Source badge and cut-ready PNG also live in docs/warhammer/ "
        "(crimson-dawn-gothic-cloud-source.png and stencils/cloud-stencil-fill.png). "
        "For vinyl cutters, trace the black silhouette.",
    )

    pdf.output(str(OUT_PDF))
    print(f"Wrote {OUT_PDF}")
    print(f"Wrote {fill}")
    print(f"Copied source to {ASSET_COPY}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a Munitorum-style Crimson Dawn markings & heraldry datasheet."""

from pathlib import Path

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/docs/warhammer")
OUT = ROOT / "crimson-dawn-datasheet.pdf"
BADGE = ROOT / "crimson-dawn-gothic-cloud-source.png"
MARINE = ROOT / "stencils" / "munitorum-marine.png"
HELMET = ROOT / "stencils" / "munitorum-helmet.png"
PAD = ROOT / "stencils" / "munitorum-pad.png"
BOLTER = ROOT / "stencils" / "munitorum-bolter.png"


# Palette
CHARCOAL = (32, 32, 34)
CRIMSON = (140, 18, 28)
COLD_GREY = (170, 175, 180)
GUNMETAL = (75, 78, 84)
LENS = (210, 35, 40)
OUTLINE = (20, 20, 22)
PAPER = (245, 240, 230)
TRIM_PAPER = (228, 220, 205)


def draw_marine(path: Path):
    """Front-facing Tacticus-style Marine in Crimson Dawn colours."""
    w, h = 620, 980
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)

    def box(xy, fill, outline=OUTLINE, width=3, radius=18):
        d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    # Boots / greaves
    box((170, 780, 275, 940), CHARCOAL, radius=14)
    box((345, 780, 450, 940), CHARCOAL, radius=14)
    # Kneepads crimson
    box((185, 820, 260, 875), CRIMSON, radius=8)
    box((360, 820, 435, 875), CRIMSON, radius=8)

    # Thighs
    box((175, 640, 285, 790), CHARCOAL, radius=16)
    box((335, 640, 445, 790), CHARCOAL, radius=16)

    # Torso
    box((160, 320, 460, 660), CHARCOAL, radius=28)
    # Struck aquila zone - dark plate with scratched X suggestion
    d.ellipse((250, 380, 370, 480), fill=(45, 45, 48), outline=OUTLINE, width=3)
    d.line((265, 400, 355, 460), fill=CRIMSON, width=4)
    d.line((355, 400, 265, 460), fill=CRIMSON, width=4)

    # Belt / pouch
    box((190, 600, 430, 650), GUNMETAL, radius=8)
    box((400, 610, 455, 700), (90, 70, 50), radius=6)  # pouch

    # Arms
    box((70, 340, 175, 560), CHARCOAL, radius=20)
    box((445, 340, 550, 560), CHARCOAL, radius=20)
    # Bolter
    box((35, 430, 120, 520), GUNMETAL, radius=8)
    box((25, 455, 55, 495), GUNMETAL, radius=4)

    # Pauldrons
    d.ellipse((40, 250, 200, 390), fill=CHARCOAL, outline=OUTLINE, width=4)
    d.ellipse((420, 250, 580, 390), fill=CHARCOAL, outline=OUTLINE, width=4)
    # Crimson trim arcs
    d.arc((40, 250, 200, 390), 210, 330, fill=CRIMSON, width=10)
    d.arc((420, 250, 580, 390), 210, 330, fill=CRIMSON, width=10)
    # Right badge cloud plate
    d.ellipse((85, 290, 155, 345), fill=CRIMSON, outline=(230, 230, 235), width=3)

    # Helmet
    box((230, 110, 390, 280), CHARCOAL, radius=28)
    box((245, 130, 375, 160), CRIMSON, radius=4)  # stripe
    # Lenses
    d.ellipse((255, 185, 300, 225), fill=LENS, outline=OUTLINE, width=2)
    d.ellipse((320, 185, 365, 225), fill=LENS, outline=OUTLINE, width=2)
    # Grill
    for i in range(4):
        y = 235 + i * 8
        d.line((270, y, 350, y), fill=GUNMETAL, width=3)

    # Soft edge highlight suggestion on plate ridges
    d.line((175, 340, 175, 620), fill=COLD_GREY, width=2)
    d.line((445, 340, 445, 620), fill=COLD_GREY, width=2)

    # Labels
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    d.text((20, 20), "MK X TACTICUS ARMOR (ref CD-01)", fill=OUTLINE, font=font_sm)
    d.text((20, 950), "( 0. ) CHAPTER COLOUR SCHEME", fill=OUTLINE, font=font)

    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def draw_helmet(path: Path, variant: str):
    w, h = 220, 220
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 30, 180, 190), radius=28, fill=CHARCOAL, outline=OUTLINE, width=3)
    d.rectangle((55, 48, 165, 72), fill=CRIMSON)
    d.ellipse((60, 95, 100, 130), fill=LENS, outline=OUTLINE, width=2)
    d.ellipse((120, 95, 160, 130), fill=LENS, outline=OUTLINE, width=2)
    for i in range(3):
        y = 145 + i * 7
        d.line((75, y, 145, y), fill=GUNMETAL, width=2)

    if variant == "a":
        pass  # standard
    elif variant == "b":
        # sergeant white laurel suggestion / stripe break
        d.polygon([(110, 20), (125, 45), (95, 45)], fill=(230, 230, 230))
    elif variant == "c":
        # veteran crimson crest
        d.rectangle((100, 18, 120, 50), fill=CRIMSON)
    else:
        # leader unique accent - cold grey band
        d.rectangle((55, 75, 165, 88), fill=COLD_GREY)

    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def draw_pad(path: Path, variant: str):
    w, h = 200, 170
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    d.ellipse((15, 15, 185, 155), fill=CHARCOAL, outline=OUTLINE, width=3)
    d.arc((15, 15, 185, 155), 210, 330, fill=CRIMSON, width=8)

    if variant == "a":
        # chapter cloud
        d.ellipse((70, 55, 130, 100), fill=CRIMSON, outline=(235, 235, 240), width=2)
        d.polygon([(100, 40), (112, 58), (88, 58)], fill=CRIMSON)
        d.polygon([(100, 100), (108, 125), (92, 118)], fill=CRIMSON)
    elif variant == "b":
        # crux/skull honour abstract
        d.ellipse((80, 60, 120, 100), fill=(210, 210, 215), outline=OUTLINE, width=2)
        d.rectangle((95, 100, 105, 125), fill=(210, 210, 215))
    elif variant == "c":
        # tactical arrow
        d.polygon([(100, 45), (130, 110), (70, 110)], outline=OUTLINE, fill=CRIMSON)
    else:
        # leader unique ring mark
        d.ellipse((65, 50, 135, 120), outline=CRIMSON, width=6)
        d.ellipse((85, 70, 115, 100), fill=CRIMSON)

    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


def draw_bolter(path: Path):
    w, h = 420, 160
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    # Body
    d.rounded_rectangle((40, 50, 300, 110), radius=8, fill=GUNMETAL, outline=OUTLINE, width=2)
    # Barrel
    d.rectangle((300, 65, 390, 95), fill=GUNMETAL, outline=OUTLINE, width=2)
    # Mag
    d.rectangle((140, 105, 190, 145), fill=CHARCOAL, outline=OUTLINE, width=2)
    # Scope
    d.rectangle((160, 30, 230, 55), fill=CHARCOAL, outline=OUTLINE, width=2)
    d.ellipse((200, 28, 225, 52), outline=CRIMSON, width=2)
    # Stock
    d.polygon([(40, 55), (15, 45), (15, 115), (40, 105)], fill=CHARCOAL, outline=OUTLINE)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


class FormPDF(FPDF):
    def footer(self):
        pass


def field_box(pdf: FormPDF, x, y, w, h, title: str):
    pdf.set_draw_color(30, 30, 30)
    pdf.set_line_width(0.35)
    pdf.rect(x, y, w, h, style="D")
    pdf.set_xy(x + 1.5, y + 1)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w - 3, 4, title)


def dotted_line_text(pdf: FormPDF, x, y, w, text: str):
    pdf.set_xy(x, y)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(w, 5, text)
    pdf.set_draw_color(120, 120, 120)
    pdf.set_line_width(0.2)
    pdf.line(x, y + 5.5, x + w, y + 5.5)


def main():
    if not BADGE.exists():
        raise SystemExit(f"Missing badge: {BADGE}")

    draw_marine(MARINE)
    for v, name in [("a", "a"), ("b", "b"), ("c", "c"), ("d", "d")]:
        draw_helmet(ROOT / "stencils" / f"munitorum-helmet-{name}.png", v)
        draw_pad(ROOT / "stencils" / f"munitorum-pad-{name}.png", v)
    draw_bolter(BOLTER)

    pdf = FormPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # Parchment background
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_draw_color(40, 40, 40)
    pdf.set_line_width(0.8)
    pdf.rect(8, 8, 194, 281, style="D")
    pdf.set_line_width(0.25)
    pdf.rect(10, 10, 190, 277, style="D")

    # Header
    pdf.set_xy(12, 12)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 7, "ADEPTUS ASTARTES MARKINGS & HERALDRY")
    pdf.set_xy(12, 18)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 40, 40)
    pdf.cell(0, 4, "MUNITORUM FORM REF: CD-UMBRA-01  |  CLASSIFICATION: SEALED / RECOVERY EYES ONLY")

    # Left marine
    pdf.image(str(MARINE), x=12, y=26, h=210)

    # Right column start
    rx, rw = 108, 88

    # (1) Chapter name
    field_box(pdf, rx, 26, rw, 16, "( 1. ) CHAPTER NAME")
    dotted_line_text(pdf, rx + 3, 33, rw - 6, "The Crimson Dawn")

    # (2) Motto
    field_box(pdf, rx, 44, rw, 16, "( 2. ) CHAPTER MOTTO / BATTLE-CRY")
    dotted_line_text(pdf, rx + 3, 51, rw - 6, '"Pain teaches. Dawn follows."')

    # (3a) Symbol
    field_box(pdf, rx, 62, 42, 48, "( 3a. ) CHAPTER SYMBOL")
    pdf.image(str(BADGE), x=rx + 5, y=70, w=32)

    # (3b) Weapon
    field_box(pdf, rx + 44, 62, 44, 48, "( 3b. ) PRIMARY WEAPON")
    pdf.image(str(BOLTER), x=rx + 45, y=78, w=42)
    pdf.set_xy(rx + 46, 100)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(40, 2.8, "Bolt rifle / storm bolter loadout common to Cloud Cells")

    # (4) Helmets
    field_box(pdf, rx, 112, rw, 52, "( 4. ) ALTERNATE HELMET CONFIGURATION")
    hx = rx + 4
    for i, name in enumerate(["a", "b", "c", "d"]):
        img = ROOT / "stencils" / f"munitorum-helmet-{name}.png"
        pdf.image(str(img), x=hx + i * 21, y=120, w=18)
        pdf.set_xy(hx + i * 21, 139)
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(40, 40, 40)
        labels = ["4a line", "4b sgt", "4c vet", "4d lead"]
        pdf.cell(18, 3, labels[i], align="C")
    pdf.set_xy(rx + 3, 145)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        rw - 6,
        3,
        "Crimson stripe + red lenses standard. Leaders add unique accents atop core livery.",
    )

    # (5) Shoulders
    field_box(pdf, rx, 166, rw, 52, "( 5. ) ALTERNATE SHOULDER INSIGNIA")
    sx = rx + 4
    for i, name in enumerate(["a", "b", "c", "d"]):
        img = ROOT / "stencils" / f"munitorum-pad-{name}.png"
        pdf.image(str(img), x=sx + i * 21, y=174, w=18)
        pdf.set_xy(sx + i * 21, 192)
        pdf.set_font("Helvetica", "", 6)
        labels = ["5a ch.", "5b crux", "5c tac", "5d ring"]
        pdf.cell(18, 3, labels[i], align="C")
    pdf.set_xy(rx + 3, 198)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(
        rw - 6,
        3,
        "5a right-pad Chapter cloud. 5b left-pad honour. 5c cell mark. 5d Ring-Bearer.",
    )

    # (6) Additional info
    field_box(pdf, rx, 220, rw, 48, "( 6. ) ADDITIONAL CHAPTER INFORMATION")
    pdf.set_xy(rx + 3, 227)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(25, 25, 25)
    extra = (
        "Former: Umbral Wardens\n"
        "Flagship: Ortus Cruentus (Bloody Dawn)\n"
        "Status: missing / records sealed\n"
        "Gene-seed: unknown (rumours conflict)\n"
        "Livery: charcoal-black; deep crimson accents;\n"
        "white-edged gothic storm-cloud; gunmetal;\n"
        "red lenses; scorched basing."
    )
    pdf.multi_cell(rw - 6, 3.3, extra)

    # Footer Munitorum box
    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(0.7)
    pdf.rect(12, 248, 184, 28, style="D")
    pdf.set_xy(14, 250)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 4, "<<< FOR MUNITORUM / ORDO RECOVERY USE ONLY >>>")
    pdf.set_xy(14, 256)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(
        130,
        3.5,
        '"The casket never should have been opened. It never should have survived. It did both."',
    )
    pdf.set_xy(145, 256)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(80, 40, 40)
    pdf.multi_cell(48, 3, "MUNITORUM REF A:115\nCHAPTER FILE: CRIMSON DAWN\nFORMER: UMBRAL WARDENS")

    # Tiny note under marine
    pdf.set_xy(12, 238)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(90, 3, "Aquila defaced on plate. Right pauldron bears Chapter cloud.")

    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

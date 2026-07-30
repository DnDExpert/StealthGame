#!/usr/bin/env python3
"""Generate the stylized Crimson Dawn chapter-index PDF (lore / livery reference).

Separate from the Munitorum heraldry datasheet — see generate_datasheet.py.
"""

from pathlib import Path

from fpdf import FPDF

ROOT = Path("/workspace/docs/warhammer")
OUT = ROOT / "crimson-dawn-chapter-index.pdf"
BADGE = ROOT / "crimson-dawn-gothic-cloud-source.png"


class DawnSheet(FPDF):
    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 40, 40)
        self.cell(
            0,
            5,
            "Narrative Chapter Index  -  Not official Games Workshop material",
            align="C",
        )


def section_rule(pdf: FPDF, y: float, x1=14, x2=196):
    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(0.4)
    pdf.line(x1, y, x2, y)


def label_value(pdf: FPDF, label: str, value: str, w_label=40):
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(180, 50, 50)
    y = pdf.get_y()
    pdf.cell(w_label, 4.2, label.upper(), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(220, 210, 205)
    pdf.multi_cell(0, 4.2, value)
    pdf.set_y(max(pdf.get_y(), y + 4.2) + 0.3)


def swatch(pdf: FPDF, x: float, y: float, rgb: tuple[int, int, int], name: str, note: str):
    pdf.set_fill_color(*rgb)
    pdf.set_draw_color(90, 30, 30)
    pdf.rect(x, y, 14, 14, style="FD")
    pdf.set_xy(x + 16, y + 1)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(220, 210, 205)
    pdf.cell(40, 4, name)
    pdf.set_xy(x + 16, y + 6)
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(160, 120, 120)
    pdf.cell(40, 4, note)


def page_frame(pdf: FPDF):
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(0, 0, 210, 297, style="F")
    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(1.2)
    pdf.rect(8, 8, 194, 281, style="D")
    pdf.set_line_width(0.3)
    pdf.rect(11, 11, 188, 275, style="D")


def main():
    if not BADGE.exists():
        raise SystemExit(f"Missing badge art: {BADGE}")

    pdf = DawnSheet(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # ------------------------------------------------------------------ page 1
    pdf.add_page()
    page_frame(pdf)

    pdf.set_fill_color(140, 18, 28)
    pdf.rect(11, 11, 188, 16, style="F")
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(13, 13, 184, 12, style="F")

    pdf.set_xy(14, 14)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(182, 7, "THE CRIMSON DAWN", align="C")
    pdf.set_xy(14, 20.5)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(180, 50, 50)
    pdf.cell(
        182,
        3.5,
        "RENEGADE ADEPTUS ASTARTES  -  FLEET-BASED  -  RECORDS SEALED",
        align="C",
    )

    section_rule(pdf, 30)
    pdf.set_xy(14, 32)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(182, 5, "CHAPTER BADGE", align="C")

    # Centered badge
    badge_w = 62
    pdf.image(str(BADGE), x=(210 - badge_w) / 2, y=40, w=badge_w)
    pdf.set_xy(30, 105)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(170, 140, 140)
    pdf.multi_cell(
        150,
        3.8,
        "Gothic storm-cloud, crimson with white edge. Displayed on the RIGHT shoulder.",
        align="C",
    )

    section_rule(pdf, 118)
    pdf.set_xy(14, 120)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 5, "COLOUR SWATCHES")

    swatches = [
        ((28, 28, 30), "Charcoal Black", "Primary armour"),
        ((140, 18, 28), "Deep Crimson", "Trim / badge / stripe"),
        ((210, 210, 215), "Cold Grey", "Edge highlights"),
        ((70, 72, 78), "Dark Gunmetal", "Weapons / metal"),
        ((200, 25, 35), "Lens Red", "Eye lenses"),
        ((55, 45, 40), "Scorched Earth", "Basing"),
    ]
    y = 128
    for i, (rgb, name, note) in enumerate(swatches):
        col = i % 3
        row = i // 3
        swatch(pdf, 14 + col * 62, y + row * 18, rgb, name, note)

    section_rule(pdf, 168)
    pdf.set_xy(14, 170)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 5, "CHAPTER DATA")
    pdf.set_y(176)

    rows = [
        ("Former name", "The Umbral Wardens"),
        ("Status", "Renegade; officially missing / sealed-file"),
        ("Command", "Dawnlord Dolor"),
        ("Flagship", 'Ortus Cruentus ("Bloody Dawn")'),
        ("Battle-cry", '"Pain teaches. Dawn follows."'),
        ("Gene-seed", "Unknown (Imperial rumours conflict wildly)"),
        (
            "Command marks",
            "Squad leaders use unique accents/symbols; core black-crimson retained",
        ),
    ]
    for label, value in rows:
        pdf.set_x(14)
        label_value(pdf, label, value)

    # ------------------------------------------------------------------ page 2
    pdf.add_page()
    page_frame(pdf)

    pdf.set_fill_color(140, 18, 28)
    pdf.rect(11, 11, 188, 14, style="F")
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(13, 13, 184, 10, style="F")
    pdf.set_xy(14, 14)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(182, 8, "DOCTRINE & ORIGIN", align="C")

    pdf.image(str(BADGE), x=168, y=28, w=22)

    y = 30
    section_rule(pdf, y)
    pdf.set_y(y + 3)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "ORIGIN")
    pdf.ln(6)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 210, 205)
    origin = (
        "Once a quiet-war brotherhood tasked with sealed archives and suppression work, "
        "the Umbral Wardens breached a Mechanicus quarantine vault on Mars and recovered "
        "a Terran archaeotech data-casket later classed as memetic contraband. "
        "Librarius reconstruction produced a fragmentary pre-Imperial parable of outcast "
        "cadres who sought peace through shared suffering and decisive force. "
        "Senior command accepted the reading as recovered doctrine. When Mars ordered the "
        "casket destroyed, the Chapter refused, fled Sol custody, and struck the Aquila."
    )
    pdf.multi_cell(182, 4.4, origin)

    pdf.ln(3)
    section_rule(pdf, pdf.get_y())
    pdf.ln(3)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "THE INCOMPLETE SCRIPTURE")
    pdf.ln(6)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 210, 205)
    scripture = (
        "What survives of the casket is badly truncated and biased toward the outcast cadre. "
        "Opposing voices are absent or scrambled. The remaining verses culminate in the "
        "annihilation of a fortified settlement - and then stop. There is no restoration, "
        "no counter-argument, no aftermath. The Dawn read that silence as proof: ruin is "
        "the completed lesson. They hunt further fragments believing the Throne hid the rest."
    )
    pdf.multi_cell(182, 4.4, scripture)

    pdf.ln(3)
    section_rule(pdf, pdf.get_y())
    pdf.ln(3)

    col_y = pdf.get_y()
    pdf.set_xy(14, col_y)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(90, 6, "CREED")
    pdf.set_xy(110, col_y)
    pdf.cell(90, 6, "IMPERIAL STANDING")

    creed_lines = [
        "- Peace bought by ignorance is a lie",
        "- Shared pain ends cycles of war",
        "- Institutions that farm conflict must break",
        "- Settlement-ruin is proof, not tragedy",
        "- The Emperor is rejected as living god",
        "- Skulls honour cost; eagles mark false order",
    ]
    stand_lines = [
        "- Public rolls: missing / records sealed",
        "- Mechanicus: quiet recovery or burn order",
        "- Inquisition: need-to-know black warrants",
        "- No open crusade branding",
        "- Most citizens never hear the name",
        "- Hunters know; sermons do not",
    ]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(220, 210, 205)
    y0 = col_y + 8
    for i, line in enumerate(creed_lines):
        pdf.set_xy(14, y0 + i * 5)
        pdf.cell(90, 5, line)
    for i, line in enumerate(stand_lines):
        pdf.set_xy(110, y0 + i * 5)
        pdf.cell(90, 5, line)

    y = y0 + 6 * 5 + 3
    section_rule(pdf, y)
    pdf.set_y(y + 3)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "STRUCTURE & WARFARE")
    pdf.ln(6)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 210, 205)
    structure = (
        "Codex companies give way to a cell network: Dawnlord above, Ring-Bearers as named "
        "lieutenants, Cloud Cells as independent kill-cadres. Preferred method - sudden "
        "appearance, local overwhelm, symbolic destruction of Imperial command icons, "
        "withdrawal before a crusade can consolidate. They leave parables of pain, not occupations."
    )
    pdf.multi_cell(182, 4.4, structure)

    pdf.ln(8)
    section_rule(pdf, pdf.get_y())
    pdf.ln(6)
    pdf.image(str(BADGE), x=88, y=pdf.get_y(), w=34)
    pdf.ln(38)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(160, 70, 70)
    pdf.multi_cell(
        182,
        4,
        '"The casket never should have been opened. It never should have survived. It did both."',
        align="C",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a stylized one-page Crimson Dawn chapter datasheet PDF."""

from pathlib import Path

from fpdf import FPDF

OUT = Path("/workspace/docs/warhammer/crimson-dawn-datasheet.pdf")


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


def draw_cloud(pdf: FPDF, x: float, y: float, s: float = 1.0):
    """Simple stylized red-cloud mark from overlapping ellipses."""
    pdf.set_fill_color(140, 18, 28)
    pdf.ellipse(x, y + 2 * s, 10 * s, 6 * s, style="F")
    pdf.ellipse(x + 5 * s, y, 12 * s, 8 * s, style="F")
    pdf.ellipse(x + 12 * s, y + 2 * s, 9 * s, 6 * s, style="F")
    pdf.ellipse(x + 3 * s, y + 3 * s, 14 * s, 7 * s, style="F")


def section_rule(pdf: FPDF, y: float):
    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(0.4)
    pdf.line(14, y, 196, y)


def label_value(pdf: FPDF, label: str, value: str, w_label=42):
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(180, 50, 50)
    y = pdf.get_y()
    pdf.cell(w_label, 5, label.upper(), new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 210, 205)
    pdf.multi_cell(0, 5, value)
    pdf.set_y(max(pdf.get_y(), y + 5) + 0.5)


def main():
    pdf = DawnSheet(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    pdf.set_fill_color(12, 10, 12)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_draw_color(140, 18, 28)
    pdf.set_line_width(1.2)
    pdf.rect(8, 8, 194, 281, style="D")
    pdf.set_line_width(0.3)
    pdf.rect(11, 11, 188, 275, style="D")

    pdf.set_fill_color(140, 18, 28)
    pdf.rect(11, 11, 188, 18, style="F")
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(13, 13, 184, 14, style="F")

    draw_cloud(pdf, 16, 14, 0.55)
    draw_cloud(pdf, 178, 14, 0.55)

    pdf.set_xy(14, 15)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(182, 8, "THE CRIMSON DAWN", align="C")
    pdf.set_xy(14, 22)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(180, 50, 50)
    pdf.cell(
        182,
        4,
        "RENEGADE ADEPTUS ASTARTES  -  FLEET-BASED  -  RECORDS SEALED",
        align="C",
    )

    y = 34
    section_rule(pdf, y)
    pdf.set_y(y + 3)

    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "CHAPTER DATA")
    pdf.ln(7)

    rows = [
        ("Former designation", "The Umbral Wardens"),
        ("Present status", "Renegade; officially missing / sealed-file"),
        ("Allegiance", "Independent creed - neither Throne nor Ruin"),
        ("Gene-seed", "Unknown (Imperial theories conflict wildly)"),
        ("Command", "Dawnlord Dolor"),
        ("Flagship", 'Ortus Cruentus  ("Bloody Dawn")'),
        ("Battle-cry", '"Pain teaches. Dawn follows."'),
        (
            "Livery",
            "Charcoal-black armour, crimson accents, white-edged red cloud "
            "heraldry, dark gunmetal weapons and red eye lenses. Squad leaders "
            "bear individualized markings; basing is scorched rock.",
        ),
    ]
    for label, value in rows:
        pdf.set_x(14)
        label_value(pdf, label, value)

    pdf.ln(2)
    section_rule(pdf, pdf.get_y())
    pdf.ln(4)

    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "ORIGIN")
    pdf.ln(7)
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
    pdf.multi_cell(182, 4.5, origin)

    pdf.ln(3)
    section_rule(pdf, pdf.get_y())
    pdf.ln(4)

    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "THE INCOMPLETE SCRIPTURE")
    pdf.ln(7)
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
    pdf.multi_cell(182, 4.5, scripture)

    pdf.ln(3)
    section_rule(pdf, pdf.get_y())
    pdf.ln(4)

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

    y = y0 + len(creed_lines) * 5 + 3
    section_rule(pdf, y)
    pdf.set_y(y + 3)

    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 6, "STRUCTURE & WARFARE")
    pdf.ln(7)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 210, 205)
    structure = (
        "Codex companies give way to a cell network: Dawnlord above, Ring-Bearers as named "
        "lieutenants, Cloud Cells as independent kill-cadres. Preferred method - sudden "
        "appearance, local overwhelm, symbolic destruction of Imperial command icons, "
        "withdrawal before a crusade can consolidate. They leave parables of pain, not occupations."
    )
    pdf.multi_cell(182, 4.5, structure)

    pdf.ln(3)
    section_rule(pdf, pdf.get_y())
    pdf.ln(4)

    draw_cloud(pdf, 90, pdf.get_y(), 0.9)
    pdf.ln(14)
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

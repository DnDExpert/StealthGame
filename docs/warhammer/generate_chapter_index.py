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


def heading(pdf: FPDF, title: str):
    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(140, 18, 28)
    pdf.cell(0, 5.5, title)
    pdf.ln(5.5)


def body(pdf: FPDF, text: str, size=8.5, leading=3.9):
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", size)
    pdf.set_text_color(220, 210, 205)
    pdf.multi_cell(182, leading, text)


def main():
    if not BADGE.exists():
        raise SystemExit(f"Missing badge art: {BADGE}")

    pdf = DawnSheet(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    # ------------------------------------------------------------------ page 1 — identity / livery
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

    # ------------------------------------------------------------------ page 2 — lore
    pdf.add_page()
    page_frame(pdf)

    pdf.set_fill_color(140, 18, 28)
    pdf.rect(11, 11, 188, 14, style="F")
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(13, 13, 184, 10, style="F")
    pdf.set_xy(14, 14)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(182, 8, "LORE & DOCTRINE", align="C")

    pdf.image(str(BADGE), x=172, y=28, w=18)

    section_rule(pdf, 30)
    pdf.set_y(32)
    heading(pdf, "SUMMARY")
    body(
        pdf,
        "Once Loyalist black-ops wardens, they broke with the Imperium after reconstructing "
        "a forbidden Terran archive on Mars and mistaking truncated Akatsuki ideals for "
        "superior truth. They reject God-Emperor worship, deface the Aquila, and wage war "
        "to force peace through necessary pain - operating in secret cells they already "
        "knew how to run.\n\n"
        "To most of the Imperium they barely exist - missing Wardens, sealed files. "
        "To Mechanicus and Inquisition hunters they are a need-to-know recovery/purge target. "
        "To themselves they are the only ones who listened.",
    )

    pdf.ln(2)
    section_rule(pdf, pdf.get_y())
    pdf.ln(2)
    heading(pdf, "ORIGIN")
    body(
        pdf,
        "As the Umbral Wardens they were a quiet-war brotherhood: protectors in public, "
        "Librarius-heavy kill-cells and sealed-archive work in private. Seconded to a "
        "Mechanicus quarantine vault on Mars, they recovered a Terran archaeotech "
        "data-casket later classed as memetic contraband.\n\n"
        "Librarius reconstruction produced a fragmentary pre-Imperial parable of outcast "
        "cadres who sought peace through shared suffering and decisive force. The reading "
        "matched wounds the Chapter already carried - Imperial \"villages\" that farm endless "
        "war. Missing verses were treated as redacted intelligence, not as a warning that "
        "the creed was incomplete.\n\n"
        "Senior commander Dolor accepted the reconstruction, took a tablet glyph read as "
        "\"Pain\" as his name, and made it law. When Mars ordered the casket burned, he "
        "refused. The Wardens fought free of Sol custody, struck the Aquila, and became "
        "the Crimson Dawn aboard the battle-barge Ortus Cruentus (\"Bloody Dawn\").",
    )

    pdf.ln(2)
    section_rule(pdf, pdf.get_y())
    pdf.ln(2)
    heading(pdf, "THE INCOMPLETE SCRIPTURE")
    body(
        pdf,
        "What survives of the casket is badly truncated and biased toward the outcast cadre. "
        "Opposing voices are absent or scrambled. The remaining verses culminate in the "
        "annihilation of a fortified settlement - and then stop. There is no restoration, "
        "no counter-argument, no aftermath.\n\n"
        "The Dawn read that silence as proof: ruin is the completed lesson. They hunt further "
        "shards believing the Throne hid the rest. A fragment showing rebuilding, mercy, or "
        "the outcasts as villains could split the Chapter - or break Dolor's theology. Until "
        "then they act on the ruin already \"proven.\"",
    )

    # ------------------------------------------------------------------ page 3 — creed / structure
    pdf.add_page()
    page_frame(pdf)

    pdf.set_fill_color(140, 18, 28)
    pdf.rect(11, 11, 188, 14, style="F")
    pdf.set_fill_color(12, 10, 12)
    pdf.rect(13, 13, 184, 10, style="F")
    pdf.set_xy(14, 14)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(230, 220, 215)
    pdf.cell(182, 8, "CREED, STANDING & WAR", align="C")

    section_rule(pdf, 30)
    pdf.set_y(32)

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
        "- Completing the scripture is holy work",
    ]
    stand_lines = [
        "- Public rolls: missing / records sealed",
        "- Not an open, advertised crusade war",
        "- Mechanicus: quiet recovery or burn order",
        "- Inquisition: need-to-know black warrants",
        "- Sol failure kept politically buried",
        "- Most citizens never hear either name",
        "- Hunters know; sermons do not",
    ]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(220, 210, 205)
    y0 = col_y + 7
    for i, line in enumerate(creed_lines):
        pdf.set_xy(14, y0 + i * 4.8)
        pdf.cell(90, 4.8, line)
    for i, line in enumerate(stand_lines):
        pdf.set_xy(110, y0 + i * 4.8)
        pdf.cell(90, 4.8, line)

    y = y0 + 7 * 4.8 + 2
    section_rule(pdf, y)
    pdf.set_y(y + 2)
    heading(pdf, "STRUCTURE")
    body(
        pdf,
        "Codex companies give way to a cell network. Dawnlord Dolor keeps tablet doctrine. "
        "Ring-Bearers - Vorago, Ruptura, Nex, Cruor, Fossor, Volumen - lead specialized "
        "Cloud Cells (boarding, siege, decapitation, flame purge, shard recovery, Librarius). "
        "Two rings stay empty: one lost on Mars, one unfilled until another shard is found. "
        "Ash Initiates carry lighter honour marks until proven.",
    )

    pdf.ln(2)
    section_rule(pdf, pdf.get_y())
    pdf.ln(2)
    heading(pdf, "WARFARE")
    body(
        pdf,
        "Appear suddenly; overwhelm locally; smash Imperial command icons, shrines, and "
        "hive authority; withdraw before a crusade response consolidates. Prefer elite "
        "spearheads over grinding occupation. Strategic aim: break a world's will to fight "
        "for the Imperium, enforce Dawn law - or vanish, leaving a parable of pain.\n\n"
        "They are not Chaos by default, not Loyalists with edgy paint, and not aware their "
        "scripture is unfinished fiction. Gene-seed remains unknown; Imperial rumours are "
        "loud and usually wrong.",
    )

    pdf.ln(4)
    section_rule(pdf, pdf.get_y())
    pdf.ln(5)
    pdf.image(str(BADGE), x=88, y=pdf.get_y(), w=34)
    pdf.ln(36)
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

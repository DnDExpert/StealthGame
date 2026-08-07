#!/usr/bin/env python3
"""Fill the official Munitorum heraldry template with correctly placed Crimson Dawn data.

For the narrative chapter-index PDF (livery/doctrine), use generate_chapter_index.py.
"""

from collections import deque
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path("/workspace/docs/warhammer")
BLANK_PDF = ROOT / "templates" / "munitorum-heraldry-blank.pdf"
BADGE = ROOT / "crimson-dawn-gothic-cloud-source.png"
OUT_PNG = ROOT / "crimson-dawn-datasheet.png"
OUT_PDF = ROOT / "crimson-dawn-datasheet.pdf"
PREVIEW = Path("/opt/cursor/artifacts/crimson-dawn-datasheet-preview.png")

SCALE = 3
CHARCOAL = (38, 38, 40)
CRIMSON = (150, 22, 30)
LENS = (215, 36, 42)
WHITE = (250, 250, 252)
INK = (18, 18, 20)

# Coordinates at SCALE=3 (1786 x 1259), measured from blank template ink
SYMBOL_BOX = (938, 250, 1278, 490)

NAME_XY = (1005, 112)
MOTTO_XY = (1085, 163)

# Section 4 helmet centers / section 5 pad centers (slightly different on col 0 & 3)
HELM_CX = (1002, 1212, 1426, 1627)
PAD_CX = (999, 1211, 1424, 1639)
PAD_CY = 875

# Measured eye-socket axis-aligned bounds per helm (L/R)
HELM_EYES = (
    ((953, 600, 985, 614), (1007, 600, 1039, 614)),
    ((1169, 600, 1201, 614), (1223, 600, 1255, 614)),
    ((1385, 600, 1417, 614), (1439, 600, 1471, 614)),
    ((1601, 600, 1633, 614), (1655, 600, 1687, 614)),
)

HELM_LABEL_Y = 712
PAD_LABEL_Y = 942
NOTES_Y0 = 985

# Marine (front view): viewer's left = marine's right shoulder (chapter badge)
# Landmarks measured from blank template ink at SCALE=3
MARINE_BADGE = (255, 278)
MARINE_KNEES = ((308, 832), (649, 833))
MARINE_AQUILA_X = (400, 250, 530, 330)
# Measured Mk X lens cavities on blank (enclosed white sockets)
MARINE_EYE_SEEDS = ((455, 158), (505, 158))
MARINE_EYE_POLYS = (
    # left lens — slanted almond inside measured socket
    [(443, 155), (472, 150), (473, 163), (448, 165)],
    # right lens
    [(496, 150), (522, 155), (520, 165), (495, 163)],
)
# Extra plate seeds so helmet/shins/boots/forearms fill when disconnected.
# Avoid seeds that bridge into page background (e.g. 700,500).
MARINE_EXTRA_SEEDS = (
    (465, 120),  # helm dome
    (456, 175),  # faceplate
    (308, 900),
    (308, 980),
    (308, 1050),
    (649, 900),
    (649, 980),
    (649, 1050),
    (200, 450),
    (180, 550),
    (160, 380),
    (690, 350),  # viewer's-right pauldron / upper arm
    (700, 400),
    (710, 380),
    (740, 450),  # forearm plate
    (750, 480),
)


def render_blank() -> Image.Image:
    doc = fitz.open(BLANK_PDF)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(SCALE, SCALE))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def is_line(rgb, lim=100):
    return rgb[0] < lim and rgb[1] < lim and rgb[2] < lim


def is_fillable(rgb):
    return rgb[0] > 225 and rgb[1] > 225 and rgb[2] > 225


def flood_fillable(im, seed, color, limit=200000):
    px = im.load()
    W, H = im.size
    x0, y0 = seed
    if not (0 <= x0 < W and 0 <= y0 < H and is_fillable(px[x0, y0])):
        return 0
    q = deque([seed])
    seen = {seed}
    n = 0
    while q and n < limit:
        x, y = q.popleft()
        if is_line(px[x, y]) or not is_fillable(px[x, y]):
            continue
        px[x, y] = color
        n += 1
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))
    return n


def interior_seeds(im, bbox):
    x1, y1, x2, y2 = bbox
    px = im.load()
    exterior = set()
    border = deque()
    for x in range(x1, x2):
        for y in (y1, y2 - 1):
            if is_fillable(px[x, y]) and not is_line(px[x, y]):
                exterior.add((x, y))
                border.append((x, y))
    for y in range(y1, y2):
        for x in (x1, x2 - 1):
            if is_fillable(px[x, y]) and not is_line(px[x, y]):
                exterior.add((x, y))
                border.append((x, y))
    while border:
        x, y = border.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if x1 <= nx < x2 and y1 <= ny < y2 and (nx, ny) not in exterior:
                if is_fillable(px[nx, ny]) and not is_line(px[nx, ny]):
                    exterior.add((nx, ny))
                    border.append((nx, ny))
    seeds, visited = [], set(exterior)
    for y in range(y1, y2):
        for x in range(x1, x2):
            if (x, y) in visited:
                continue
            if not (is_fillable(px[x, y]) and not is_line(px[x, y])):
                continue
            seeds.append((x, y))
            q = deque([(x, y)])
            visited.add((x, y))
            while q:
                cx, cy = q.popleft()
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if x1 <= nx < x2 and y1 <= ny < y2 and (nx, ny) not in visited:
                        if is_fillable(px[nx, ny]) and not is_line(px[nx, ny]):
                            visited.add((nx, ny))
                            q.append((nx, ny))
    return seeds


def load_badge(max_size: int) -> Image.Image:
    """Load chapter badge with near-black background made transparent."""
    badge = Image.open(BADGE).convert("RGBA")
    arr = np.array(badge)
    black = (arr[:, :, 0] < 50) & (arr[:, :, 1] < 50) & (arr[:, :, 2] < 50)
    arr[black, 3] = 0
    badge = Image.fromarray(arr)
    badge.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return badge


def colorize_marine(im: Image.Image) -> Image.Image:
    W, H = im.size
    bbox = (55, 55, int(W * 0.46), int(H * 0.95))
    for s in interior_seeds(im, bbox):
        flood_fillable(im, s, CHARCOAL, limit=120000)
    for s in MARINE_EXTRA_SEEDS:
        flood_fillable(im, s, CHARCOAL, limit=80000)

    # Lenses only — no brow bar (it read as forehead blocks on the filled helm)
    d = ImageDraw.Draw(im)
    for poly in MARINE_EYE_POLYS:
        d.polygon(poly, fill=LENS)
    for seed in MARINE_EYE_SEEDS:
        flood_fillable(im, seed, LENS, limit=500)

    for kx, ky in MARINE_KNEES:
        d.ellipse((kx - 36, ky - 34, kx + 36, ky + 34), fill=CRIMSON)
    x1, y1, x2, y2 = MARINE_AQUILA_X
    d.line((x1, y1, x2, y2), fill=CRIMSON, width=4)
    d.line((x2, y1, x1, y2), fill=CRIMSON, width=4)

    badge = load_badge(120)
    base = im.convert("RGBA")
    bx, by = MARINE_BADGE
    base.paste(badge, (bx - badge.width // 2, by - badge.height // 2), badge)
    return base.convert("RGB")


def paste_symbol(im: Image.Image) -> Image.Image:
    x1, y1, x2, y2 = SYMBOL_BOX
    bw, bh = x2 - x1, y2 - y1
    canvas = Image.new("RGBA", (bw, bh), (8, 8, 10, 255))
    badge = load_badge(min(bw, bh) - 28)
    canvas.paste(badge, ((bw - badge.width) // 2, (bh - badge.height) // 2), badge)
    out = im.convert("RGBA")
    out.paste(canvas, (x1, y1), canvas)
    return out.convert("RGB")


def fill_helms_and_pads(im: Image.Image) -> Image.Image:
    """Paint marks into measured template shapes."""
    d = ImageDraw.Draw(im)

    for i, (cx, eyes) in enumerate(zip(HELM_CX, HELM_EYES)):
        # Fill real eye sockets via flood from socket centers
        for x1, y1, x2, y2 in eyes:
            seed = ((x1 + x2) // 2, (y1 + y2) // 2 + 1)
            n = flood_fillable(im, seed, LENS, limit=500)
            if n < 30:
                # Fallback polygon matching slanted Mark VII lens
                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                if mx < cx:  # left eye
                    d.polygon(
                        [(x1 + 1, y1 + 4), (x2 - 1, y1 + 1), (x2 - 2, y2 - 1), (x1 + 2, y2 - 2)],
                        fill=LENS,
                    )
                else:
                    d.polygon(
                        [(x1 + 1, y1 + 1), (x2 - 1, y1 + 4), (x2 - 2, y2 - 2), (x1 + 2, y2 - 1)],
                        fill=LENS,
                    )

        # Rank marks on forehead (above brow), not on lenses
        brow_y = 586
        d.rectangle((cx - 18, brow_y, cx + 18, brow_y + 7), fill=CRIMSON)
        if i == 1:  # sergeant — small chevron
            d.polygon([(cx, 572), (cx + 8, 584), (cx - 8, 584)], fill=CRIMSON)
        if i == 2:  # veteran — second brow bar
            d.rectangle((cx - 18, 578, cx + 18, 583), fill=CRIMSON)
        if i == 3:  # leader — vertical stripe
            d.rectangle((cx - 3, 568, cx + 3, brow_y + 7), fill=CRIMSON)

    # Pads: flood charcoal into measured interiors, then icons
    for cx in PAD_CX:
        flood_fillable(im, (cx, PAD_CY), CHARCOAL, limit=30000)

    out = im.convert("RGBA")
    d = ImageDraw.Draw(out)
    badge = load_badge(84)
    for i, cx in enumerate(PAD_CX):
        cy = PAD_CY
        if i == 0:
            out.paste(badge, (cx - badge.width // 2, cy - badge.height // 2), badge)
        elif i == 1:
            d.ellipse((cx - 14, cy - 16, cx + 14, cy + 12), fill=WHITE, outline=INK, width=2)
        elif i == 2:
            d.polygon([(cx, cy - 22), (cx + 16, cy + 14), (cx - 16, cy + 14)], fill=CRIMSON)
        else:
            d.ellipse((cx - 18, cy - 20, cx + 18, cy + 16), outline=CRIMSON, width=4)
            d.ellipse((cx - 5, cy - 7, cx + 5, cy + 3), fill=CRIMSON)
    return out.convert("RGB")


def draw_text(im: Image.Image) -> Image.Image:
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        font = font_sm = font_tiny = ImageFont.load_default()

    d.text(NAME_XY, "The Crimson Dawn", fill=INK, font=font)
    d.text(MOTTO_XY, "Pain teaches. Dawn follows.", fill=INK, font=font_sm)

    for cx, lab in zip(HELM_CX, ["line", "sergeant", "veteran", "leader"]):
        tw = d.textlength(lab, font=font_tiny)
        d.text((cx - tw / 2, HELM_LABEL_Y), lab, fill=INK, font=font_tiny)
    for cx, lab in zip(PAD_CX, ["chapter", "honour", "cell", "ring"]):
        tw = d.textlength(lab, font=font_tiny)
        d.text((cx - tw / 2, PAD_LABEL_Y), lab, fill=INK, font=font_tiny)

    notes = [
        "Former: Umbral Wardens. Flagship: Ortus Cruentus (Bloody Dawn).",
        "Status: records sealed / quiet Mechanicus-Ordo recovery. Gene-seed: unknown.",
        "Livery: charcoal-black; deep crimson accents; white-edged gothic storm-cloud;",
        "gunmetal weapons; red lenses; scorched basing. Aquila struck.",
    ]
    y = NOTES_Y0
    for line in notes:
        d.text((918, y), line, fill=INK, font=font_tiny)
        y += 22
    return im


def main():
    im = render_blank()
    print("size", im.size)
    im = colorize_marine(im)
    im = paste_symbol(im)
    im = fill_helms_and_pads(im)
    im = draw_text(im)

    im.save(OUT_PNG, dpi=(300, 300))
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_bytes(OUT_PNG.read_bytes())

    doc = fitz.open()
    src = fitz.open(BLANK_PDF)
    page = doc.new_page(width=src[0].rect.width, height=src[0].rect.height)
    page.insert_image(src[0].rect, filename=str(OUT_PNG))
    doc.save(OUT_PDF)
    print("Wrote", OUT_PDF)


if __name__ == "__main__":
    main()

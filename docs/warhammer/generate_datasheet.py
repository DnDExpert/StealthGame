#!/usr/bin/env python3
"""Fill the official GW Munitorum heraldry PDF template with Crimson Dawn data."""

from collections import deque
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/docs/warhammer")
BLANK_PDF = ROOT / "templates" / "munitorum-heraldry-blank.pdf"
BADGE = ROOT / "crimson-dawn-gothic-cloud-source.png"
OUT_PNG = ROOT / "crimson-dawn-datasheet.png"
OUT_PDF = ROOT / "crimson-dawn-datasheet.pdf"
PREVIEW = Path("/opt/cursor/artifacts/crimson-dawn-datasheet-preview.png")

CHARCOAL = (38, 38, 40)
CRIMSON = (150, 22, 30)
LENS = (210, 36, 40)
WHITE = (248, 248, 250)
INK = (18, 18, 20)
SCALE = 3


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


def colorize_marine(im: Image.Image) -> Image.Image:
    W, H = im.size
    # Exclude purity-seal parchment area roughly bottom-center-right of marine
    bbox = (50, 50, int(W * 0.46), int(H * 0.92))
    seeds = interior_seeds(im, bbox)
    print("marine interiors", len(seeds))
    for s in seeds:
        # skip very small later; fill charcoal
        flood_fillable(im, s, CHARCOAL, limit=120000)

    d = ImageDraw.Draw(im)
    # Helmet lenses (drawn, no flood)
    d.polygon([(375, 185), (400, 175), (405, 205), (380, 210)], fill=LENS)
    d.polygon([(425, 175), (450, 185), (445, 210), (420, 205)], fill=LENS)
    # Brow stripe
    d.rectangle((375, 140, 450, 158), fill=CRIMSON)
    # Kneepad discs
    d.ellipse((320, 770, 385, 835), fill=CRIMSON)
    d.ellipse((450, 770, 515, 835), fill=CRIMSON)
    # Pauldron trim hints (rim arcs)
    d.arc((175, 250, 330, 420), 200, 340, fill=CRIMSON, width=8)
    d.arc((500, 250, 655, 420), 200, 340, fill=CRIMSON, width=8)
    # Aquila strike on chest
    d.line((355, 395, 475, 485), fill=CRIMSON, width=5)
    d.line((475, 395, 355, 485), fill=CRIMSON, width=5)

    # Right shoulder chapter badge (viewer right = marine's left in some conventions;
    # scheme says chapter badge on RIGHT shoulder = viewer's left on front view? 
    # Front view: viewer's left = marine's right shoulder. Place badge there.)
    badge = Image.open(BADGE).convert("RGBA")
    badge.thumbnail((100, 100), Image.Resampling.LANCZOS)
    base = im.convert("RGBA")
    # viewer's left pauldron center ~ (250, 330)
    base.paste(badge, (250 - badge.width // 2, 330 - badge.height // 2), badge)
    return base.convert("RGB")


def paste_symbol(im: Image.Image) -> Image.Image:
    box = (928, 252, 1178, 505)
    bw, bh = box[2] - box[0], box[3] - box[1]
    canvas = Image.new("RGBA", (bw, bh), (10, 10, 12, 255))
    badge = Image.open(BADGE).convert("RGBA")
    badge.thumbnail((bw - 18, bh - 18), Image.Resampling.LANCZOS)
    canvas.paste(badge, ((bw - badge.width) // 2, (bh - badge.height) // 2), badge)
    out = im.convert("RGBA")
    out.paste(canvas, (box[0], box[1]), canvas)
    return out.convert("RGB")


def fill_form_icons(im: Image.Image) -> Image.Image:
    d = ImageDraw.Draw(im)
    helm_boxes = [
        (955, 555, 1110, 690),
        (1125, 555, 1280, 690),
        (1295, 555, 1450, 690),
        (1465, 555, 1620, 690),
    ]
    # Pads are open-bottom outlines - paint solid fills instead of flood
    pad_centers = [(1032, 845), (1202, 845), (1372, 845), (1542, 845)]

    for i, box in enumerate(helm_boxes):
        for s in interior_seeds(im, box):
            flood_fillable(im, s, CHARCOAL, limit=30000)
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        d = ImageDraw.Draw(im)
        d.rectangle((cx - 28, y1 + 22, cx + 28, y1 + 36), fill=CRIMSON)
        d.ellipse((cx - 32, y1 + 48, cx - 10, y1 + 68), fill=LENS)
        d.ellipse((cx + 10, y1 + 48, cx + 32, y1 + 68), fill=LENS)
        if i == 1:
            d.polygon([(cx, y1 + 8), (cx + 10, y1 + 24), (cx - 10, y1 + 24)], fill=WHITE)
        if i == 3:
            d.rectangle((cx - 6, y1 + 10, cx + 6, y1 + 40), fill=CRIMSON)

    out = im.convert("RGBA")
    badge = Image.open(BADGE).convert("RGBA")
    d = ImageDraw.Draw(out)
    for i, (cx, cy) in enumerate(pad_centers):
        # solid pad face
        d.ellipse((cx - 55, cy - 60, cx + 55, cy + 40), fill=CHARCOAL, outline=INK, width=2)
        d.rectangle((cx - 55, cy + 28, cx + 55, cy + 42), fill=CHARCOAL, outline=INK, width=2)
        if i == 0:
            b = badge.copy()
            b.thumbnail((70, 70), Image.Resampling.LANCZOS)
            out.paste(b, (cx - b.width // 2, cy - b.height // 2 - 6), b)
        elif i == 1:
            d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=WHITE, outline=INK, width=2)
        elif i == 2:
            d.polygon([(cx, cy - 22), (cx + 20, cy + 18), (cx - 20, cy + 18)], fill=CRIMSON)
        else:
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=CRIMSON, width=5)
            d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=CRIMSON)
    return out.convert("RGB")


def draw_text(im: Image.Image) -> Image.Image:
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font = font_sm = font_tiny = ImageFont.load_default()

    d.text((1000, 86), "The Crimson Dawn", fill=INK, font=font)
    d.text((1080, 166), "Pain teaches. Dawn follows.", fill=INK, font=font_sm)

    for x, lab in zip([978, 1148, 1318, 1488], ["line", "sergeant", "veteran", "leader"]):
        d.text((x, 698), lab, fill=INK, font=font_tiny)
    for x, lab in zip([968, 1148, 1318, 1488], ["chapter", "honour", "cell", "ring"]):
        d.text((x, 918), lab, fill=INK, font=font_tiny)

    notes = [
        "Former: Umbral Wardens. Flagship: Ortus Cruentus (Bloody Dawn).",
        "Status: records sealed / quiet Mechanicus-Ordo recovery. Gene-seed: unknown.",
        "Livery: charcoal-black; deep crimson accents; white-edged gothic storm-cloud;",
        "gunmetal weapons; red lenses; scorched basing. Aquila struck.",
    ]
    y = 978
    for line in notes:
        d.text((915, y), line, fill=INK, font=font_tiny)
        y += 24
    return im


def main():
    im = render_blank()
    print("size", im.size)
    im = colorize_marine(im)
    im = paste_symbol(im)
    im = fill_form_icons(im)
    im = draw_text(im)

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    im.save(OUT_PNG, dpi=(300, 300))
    PREVIEW.write_bytes(OUT_PNG.read_bytes())

    doc = fitz.open()
    src = fitz.open(BLANK_PDF)
    page = doc.new_page(width=src[0].rect.width, height=src[0].rect.height)
    page.insert_image(src[0].rect, filename=str(OUT_PNG))
    doc.save(OUT_PDF)
    print("Wrote", OUT_PDF)


if __name__ == "__main__":
    main()

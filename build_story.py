"""Build Sandor's daily Instagram Story slides (1080x1920 JPEG) in the First Light brand."""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

FONTS = os.environ.get("FONT_DIR", "/home/claude/fonts")
EMERALD, IVORY, ONYX = "#0B3D2E", "#F7F5F0", "#222222"
AURA, SAGE, GREY, HAIR, TILE = "#116248", "#A9C9B8", "#6B6B66", "#E2DED4", "#124A39"
W, H, M = 1080, 1920, 96


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)


def tracked(d, xy, text, f, fill, spacing):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing
    return x


def tracked_width(d, text, f, spacing):
    return sum(d.textlength(c, font=f) + spacing for c in text) - spacing


def wrap(d, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def paragraph(d, x, y, text, f, fill, width, lh):
    for line in wrap(d, text, f, width):
        d.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def horizon(d, x1, x2, y, line, diamond):
    d.line([(x1, y), (x2 - 14, y)], fill=line, width=2)
    s = 10
    d.polygon([(x2 - s, y), (x2, y - s), (x2 + s, y), (x2, y + s)], fill=diamond)


def frame(dark):
    bg, fg = (EMERALD, IVORY) if dark else (IVORY, ONYX)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    acc = SAGE if dark else AURA
    sub = SAGE if dark else GREY
    rule = TILE if dark else HAIR
    # wordmark top
    wm = font("Cormorant-Medium", 34)
    tracked(d, (M, 270), "SANDOR HERNANDEZ", wm, fg, 9)
    horizon(d, M, M + tracked_width(d, "SANDOR HERNANDEZ", wm, 9), 326, rule if not dark else SAGE, acc)
    # footer compliance
    d.line([(M, H - 360), (W - M, H - 360)], fill=rule, width=1)
    ff = font("Montserrat-Regular", 24)
    d.text((M, H - 330), "Sandor Hernandez · Aura Homes · FL Lic. SL3611191", font=ff, fill=sub)
    d.text((M, H - 290), "786.799.2069 · sandorsrealty.com", font=ff, fill=sub)
    return img, d, fg, acc, sub


def cover(s):
    img, d, fg, acc, sub = frame(True)
    lab = font("Montserrat-SemiBold", 28)
    tracked(d, (M, 560), s["label"], lab, acc, 6)
    y = 640
    for line in s["title_lines"]:
        d.text((M, y), line, font=font("Cormorant-Regular", 132), fill=fg); y += 140
    y += 40
    horizon(d, M, M + 300, y, SAGE, SAGE)
    paragraph(d, M, y + 60, s["body"], font("Montserrat-Regular", 38), fg, W - 2 * M, 56)
    d.text((M, H - 430), s.get("source", ""), font=font("Montserrat-Regular", 24), fill=sub)
    return img


def point(s, idx, dark):
    img, d, fg, acc, sub = frame(dark)
    lab = font("Montserrat-SemiBold", 28)
    tracked(d, (M, 470), f"{idx:02d}  ·  {s['label']}", lab, acc, 6)
    hero = font("Cormorant-Regular", 300 if len(s["hero"]) <= 5 else 210)
    d.text((M - 8, 500), s["hero"], font=hero, fill=acc if not dark else SAGE)
    y = d.textbbox((M - 8, 500), s["hero"], font=hero)[3] + 40
    d.text((M, y), s["hero_caption"], font=font("Montserrat-Medium", 32), fill=sub)
    y += 100
    for line in wrap(d, s["headline"], font("Cormorant-Regular", 80), W - 2 * M):
        d.text((M, y), line, font=font("Cormorant-Regular", 80), fill=fg); y += 88
    y += 40
    d.line([(M, y), (M + 120, y)], fill=acc, width=2)
    y += 50
    paragraph(d, M, y, s["body"], font("Montserrat-Regular", 36), fg, W - 2 * M, 54)
    return img


def cta(s):
    img, d, fg, acc, sub = frame(True)
    lab = font("Montserrat-SemiBold", 28)
    tracked(d, (M, 600), s["label"], lab, acc, 6)
    y = 680
    for line in s["title_lines"]:
        d.text((M, y), line, font=font("Cormorant-Regular", 120), fill=fg); y += 130
    y += 60
    # keyword box
    kw = font("Montserrat-SemiBold", 64)
    tw = tracked_width(d, s["keyword"], kw, 14)
    d.rectangle([(M, y), (M + tw + 120, y + 130)], outline=SAGE, width=2)
    tracked(d, (M + 60, y + 30), s["keyword"], kw, SAGE, 14)
    y += 200
    y = paragraph(d, M, y, s["body"], font("Montserrat-Regular", 36), fg, W - 2 * M, 54)
    d.text((M, y + 60), s["signoff"], font=font("Cormorant-Regular", 56), fill=SAGE)
    return img


def main(spec_path, out_dir):
    spec = json.load(open(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    slides = spec["slides"]
    for i, s in enumerate(slides, 1):
        if s["type"] == "cover":
            img = cover(s)
        elif s["type"] == "cta":
            img = cta(s)
        else:
            img = point(s, i - 1, dark=(i % 2 == 1))
        img.save(f"{out_dir}/story-{i:02d}.jpg", "JPEG", quality=92)
        print(f"{out_dir}/story-{i:02d}.jpg")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

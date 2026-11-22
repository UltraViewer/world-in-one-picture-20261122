#!/usr/bin/env python3
"""Compose the make.fun news-image entry for 22 November 2026.

A newspaper front page: masthead, two-line headline, hero summit photo,
two photo stories side by side, and a dark strip with markets + briefs.
All lettering is drawn with PIL, so the text stays crisp; the photos are
AI-generated editorial panels kept in ./panels.
Output: entry.png, 1024x1024, under the 1 MiB cap.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_DIR = os.path.join(HERE, "panels")

PAGE_W, PAGE_H = 1024, 1024
PAPER = (250, 246, 234)
INK = (18, 18, 18)
ACCENT = (176, 30, 42)
MUTED = (96, 92, 82)
CREAM = (250, 246, 234)
STRIP_INK = (232, 228, 216)

FONTS = {
    "mast": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "head": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "cap": "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def load(name, size):
    return ImageFont.truetype(FONTS[name], size)


def fit_crop(img, tw, th):
    """Center-crop the image to the target aspect ratio, then resize."""
    w, h = img.size
    if w / h > tw / th:
        cut = int(h * tw / th)
        left = (w - cut) // 2
        img = img.crop((left, 0, left + cut, h))
    else:
        cut = int(w * th / tw)
        top = (h - cut) // 2
        img = img.crop((0, top, w, top + cut))
    return img.resize((tw, th), Image.LANCZOS)


def wrap_text(draw, text, font, max_width):
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def place_photo(page, draw, filename, x, y, w, h):
    img = Image.open(os.path.join(PANEL_DIR, filename)).convert("RGB")
    img = fit_crop(img, w, h)
    img = ImageEnhance.Color(img).enhance(1.05)
    img = ImageEnhance.Contrast(img).enhance(1.03)
    page.paste(img, (x, y))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def story_column(draw, x, y, width, kicker, subhead, body):
    draw.text((x, y), kicker, font=load("sans_b", 19), fill=ACCENT)
    draw.text((x, y + 24), subhead, font=load("sans_b", 17), fill=INK)
    lines = wrap_text(draw, body, load("sans", 16), width)
    cursor = y + 48
    for line in lines:
        draw.text((x, cursor), line, font=load("sans", 16), fill=INK)
        cursor += 20


def build():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)
    margin = 28
    edge = PAGE_W - margin

    # Masthead.
    draw.text((PAGE_W // 2, 26), "THE WORLD IN ONE PICTURE",
              font=load("mast", 56), fill=INK, anchor="ma")
    draw.line([(margin, 96), (edge, 96)], fill=INK, width=3)
    draw.line([(margin, 102), (edge, 102)], fill=INK, width=1)

    # Dateline row.
    draw.text((margin, 112), "SUNDAY, 22 NOVEMBER 2026",
              font=load("sans_b", 21), fill=ACCENT)
    draw.text((edge, 113), "ONE DAY  \u2022  ONE IMAGE",
              font=load("sans", 19), fill=MUTED, anchor="ra")
    draw.line([(margin, 146), (edge, 146)], fill=INK, width=1)

    # Two-line headline.
    draw.text((PAGE_W // 2, 158), "TRUMP, XI AND PUTIN AGREE",
              font=load("head", 44), fill=INK, anchor="ma")
    draw.text((PAGE_W // 2, 206), "NUCLEAR RISK TALKS",
              font=load("head", 44), fill=INK, anchor="ma")

    # Hero photo: the Shenzhen summit.
    place_photo(page, draw,
                "media-generation-hero-summit-0-99e63138-0863-4293-a611-42153d2e056a.webp",
                margin, 268, edge - margin, 292)

    # Hero caption, two lines.
    caption = ("SHENZHEN \u2014 Trump, Xi and Putin hold the first trilateral summit "
               "in history and agree to open talks on nuclear risk reduction.")
    lines = wrap_text(draw, caption, load("cap", 19), edge - margin)
    cursor = 572
    for line in lines:
        draw.text((margin, cursor), line, font=load("cap", 19), fill=INK)
        cursor += 26

    # Two photo stories side by side.
    gap = 12
    col_w = (edge - margin - gap) // 2
    row_y, img_h = 640, 150
    place_photo(page, draw,
                "media-generation-panel-mexico-0-f7598a5d-1e16-44b7-90c0-1e262a10d1f1.webp",
                margin, row_y, col_w, img_h)
    place_photo(page, draw,
                "media-generation-panel-hormuz-0-4732c55e-11de-4069-8a57-c84c60e67519.webp",
                margin + col_w + gap, row_y, col_w, img_h)
    story_column(draw, margin, row_y + img_h + 10, col_w,
                 "SINALOA, MEXICO", "\u2018El Chapo Isidro\u2019 captured",
                 "Mexican troops seize cartel boss Fausto Isidro Meza "
                 "Flores; 11 killed in the raid.")
    story_column(draw, margin + col_w + gap, row_y + img_h + 10, col_w,
                 "STRAIT OF HORMUZ", "Iran strikes; tankers hit",
                 "Bahrain blames Iran for hitting a civilian site as two "
                 "tankers are attacked near Hormuz.")

    # Dark strip: markets + the day in brief.
    strip_y, strip_h = 904, 76
    draw.rectangle([margin, strip_y, edge, strip_y + strip_h], fill=INK)
    draw.text((margin + 14, strip_y + 10),
              "MARKETS  \u25bc  S&P 500 slides into correction as AI stocks plunge",
              font=load("sans_b", 17), fill=CREAM)
    draw.text((margin + 14, strip_y + 40),
              "COP31 \u2014 Climate talks in overtime  \u2022  PERU \u2014 6.7 quake shakes "
              "Andes  \u2022  INDONESIA \u2014 3 dead, 36 missing in fire",
              font=load("sans", 15), fill=STRIP_INK)

    # Footer.
    draw.text((PAGE_W // 2, 992),
              "Illustrated summary of the world\u2019s news  \u2022  22 November 2026",
              font=load("sans", 13), fill=MUTED, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    page.save(out, "PNG", optimize=True, compress_level=9)
    nbytes = os.path.getsize(out)
    print(f"entry.png: {page.size} {nbytes} bytes "
          f"({nbytes / 1048576:.2f} MiB) limit 1048576")
    if nbytes > 1048576:
        print("OVER LIMIT")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(build())

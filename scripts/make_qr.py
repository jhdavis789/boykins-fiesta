#!/usr/bin/env python3
"""QR poster (PNG + PDF) for Boykin's Fiesta."""
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont

URL = "https://jhdavis789.github.io/boykins-fiesta/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTP = os.path.join(ROOT, "qr")
os.makedirs(OUTP, exist_ok=True)

SKY0, SKY1, EMBER = (18, 10, 42), (92, 31, 56), (224, 123, 57)
CREAM, GOLD, RED = (245, 236, 215), (242, 181, 68), (214, 69, 65)

W, H = 1600, 2200
img = Image.new("RGB", (W, H), SKY0)
d = ImageDraw.Draw(img)
# vertical sunset gradient
for y in range(H):
    t = y / H
    if t < 0.55:
        k = t / 0.55
        c = tuple(int(SKY0[i] + (SKY1[i] - SKY0[i]) * k) for i in range(3))
    else:
        k = (t - 0.55) / 0.45
        c = tuple(int(SKY1[i] + (EMBER[i] - SKY1[i]) * k) for i in range(3))
    d.line([(0, y), (W, y)], fill=c)

def font(size, names):
    for n in names:
        for base in ("/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/", "/Library/Fonts/"):
            p = base + n
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()

f_title = font(150, ["Rockwell.ttc", "Georgia Bold.ttf", "Georgia.ttf"])
f_sub = font(64, ["Futura.ttc", "Avenir Next.ttc", "Helvetica.ttc"])
f_small = font(46, ["Georgia Italic.ttf", "Georgia.ttf"])
f_url = font(40, ["Menlo.ttc", "Courier New.ttf"])

def center(txt, y, f, fill):
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, y), txt, font=f, fill=fill)

import math
def star(cx_, cy_, r, fill):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.42
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx_ + rr * math.cos(a), cy_ + rr * math.sin(a)))
    d.polygon(pts, fill=fill)
for i in range(5):
    star(W / 2 + (i - 2) * 130, 165, 34, GOLD)
center("BOYKIN'S FIESTA", 240, f_title, CREAM)
center("250 BEERS FOR 250 YEARS", 440, f_sub, EMBER)
center("1776 – 2025  ·  America's Semiquincentennial", 560, f_small, CREAM)

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=22, border=2)
qr.add_data(URL)
qr.make(fit=True)
qimg = qr.make_image(fill_color="#241030", back_color="#f5ecd7").convert("RGB")
qs = 1000
qimg = qimg.resize((qs, qs), Image.NEAREST)
# cream card behind QR
pad = 46
d.rounded_rectangle([(W - qs) // 2 - pad, 720 - pad, (W + qs) // 2 + pad, 720 + qs + pad],
                    radius=48, fill=CREAM, outline=GOLD, width=10)
img.paste(qimg, ((W - qs) // 2, 720))

center("SCAN  ·  PICK YOUR YEAR  ·  DRINK ITS BEER", 1860, f_sub, GOLD)
center("Please help us drink all 250 — and learn some history doing it.", 1960, f_small, CREAM)
center(URL, 2060, f_url, CREAM)

png = os.path.join(OUTP, "boykins_fiesta_qr.png")
pdf = os.path.join(OUTP, "boykins_fiesta_qr.pdf")
img.save(png)
img.save(pdf, "PDF", resolution=200)
print(png)
print(pdf)

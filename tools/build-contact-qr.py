#!/usr/bin/env python3
"""Build the printable contact QR code for INTEGRI, offline.

    pip install segno pillow opencv-python-headless
    python3 tools/build-contact-qr.py

Everything is generated locally. Nothing in the printed code depends on a
third-party service that could be deprecated or start charging, which is the
whole reason not to use a Google Charts or shortener URL for something that
gets committed to card stock.

Every file written is decoded back with OpenCV, then rescaled to simulated
print sizes and decoded again, so a variant that does not actually scan cannot
reach the printer. That check is what caught the white-on-black variant.
"""
import os
import sys

import segno
import cv2
import numpy as np
from PIL import Image, ImageDraw

URL = "https://www.integriforensicservices.com/contact"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand-assets", "qr")
CREST = os.path.join(ROOT, "assets", "img", "integri-crest.png")

SCALE = 40      # px per module for the raster exports
BORDER = 4      # quiet zone in modules, the spec minimum
CREST_FRAC = 0.17   # crest width as a fraction of the symbol; ECC H tolerates 30%

os.makedirs(OUT, exist_ok=True)
written = []


def path(name):
    return os.path.join(OUT, name)


# Level H so up to 30 percent can be obscured, which is what lets the crest sit
# in the middle of the branded variant without breaking the read.
qr = segno.make(URL, error="h")
print(f"QR version {qr.version}, {qr.symbol_size(scale=1, border=0)[0]} modules, ECC {qr.error.upper()}")

qr.save(path("integri-contact-qr.svg"), scale=10, border=BORDER,
        dark="#000000", light="#ffffff")
written.append("integri-contact-qr.svg")

qr.save(path("integri-contact-qr.png"), scale=SCALE, border=BORDER,
        dark="#000000", light="#ffffff")
written.append("integri-contact-qr.png")

qr.save(path("integri-contact-qr-black-transparent.png"), scale=SCALE, border=BORDER,
        dark="#000000", light=None)
written.append("integri-contact-qr-black-transparent.png")


def rounded_panel(inner, pad_frac=0.06, radius_frac=0.06):
    """Put the code on a white rounded panel, for placing on the black card.

    Never invert to white-on-black instead. Scanners expect dark modules on a
    light ground; the inverted variant was built, failed to decode, and was
    deleted.
    """
    pad = int(inner.width * pad_frac)
    size = inner.width + pad * 2
    panel = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size - 1, size - 1], radius=int(size * radius_frac), fill=255)
    white = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    panel.paste(white, (0, 0), mask)
    panel.paste(inner, (pad, pad), inner if inner.mode == "RGBA" else None)
    return panel


plain = Image.open(path("integri-contact-qr.png")).convert("RGBA")
rounded_panel(plain).save(path("integri-contact-qr-on-white-panel.png"))
written.append("integri-contact-qr-on-white-panel.png")

if os.path.exists(CREST):
    branded = plain.copy()
    w = int(branded.width * CREST_FRAC)
    crest = Image.open(CREST).convert("RGBA")
    crest.thumbnail((w, w), Image.LANCZOS)

    # White knockout behind the crest so it reads as deliberate rather than as
    # damage, and so the crest never sits half on a dark module.
    knock = int(max(crest.size) * 1.22)
    box = Image.new("RGBA", (knock, knock), (0, 0, 0, 0))
    m = Image.new("L", (knock, knock), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, knock - 1, knock - 1],
                                        radius=int(knock * 0.14), fill=255)
    box.paste(Image.new("RGBA", (knock, knock), (255, 255, 255, 255)), (0, 0), m)
    box.paste(crest, ((knock - crest.width) // 2, (knock - crest.height) // 2), crest)

    branded.alpha_composite(box, ((branded.width - knock) // 2,
                                  (branded.height - knock) // 2))
    branded.save(path("integri-contact-qr-branded.png"))
    written.append("integri-contact-qr-branded.png")
else:
    print(f"note: {CREST} missing, skipping the branded variant")


# ---- verify: decode every raster back, at full size and at print sizes ----
det = cv2.QRCodeDetector()
SIZES_MM = (30, 25, 20, 18, 15, 12)
DPI = 600
failed = []

for name in written:
    if name.endswith(".svg"):
        continue
    img = Image.open(path(name)).convert("RGB")
    # flatten onto white, because a transparent PNG read straight into OpenCV
    # loses the light modules and cannot decode
    flat = Image.new("RGB", img.size, (255, 255, 255))
    flat.paste(Image.open(path(name)).convert("RGBA"), (0, 0),
               Image.open(path(name)).convert("RGBA"))
    gray = cv2.cvtColor(np.array(flat), cv2.COLOR_RGB2GRAY)

    results = []
    if det.detectAndDecode(gray)[0] != URL:
        failed.append(f"{name} @ full size")
        results.append("full:FAIL")
    else:
        results.append("full:OK")

    for mm in SIZES_MM:
        px = max(1, round(mm / 25.4 * DPI))
        small = cv2.resize(gray, (px, px), interpolation=cv2.INTER_AREA)
        ok = det.detectAndDecode(small)[0] == URL
        if not ok:
            failed.append(f"{name} @ {mm}mm")
        results.append(f"{mm}mm:{'OK' if ok else 'FAIL'}")
    print(f"  {name:44s} " + "  ".join(results))

print(f"\nwrote {len(written)} file(s) to {os.path.relpath(OUT, ROOT)}")
if failed:
    print("FAILED to decode: " + ", ".join(failed))
    sys.exit(1)
print("every variant decodes to the exact URL at every tested print size")

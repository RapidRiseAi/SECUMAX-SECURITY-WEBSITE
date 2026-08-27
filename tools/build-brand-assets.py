#!/usr/bin/env python3
"""Build every shipped image asset from the brand library.

    python3 tools/build-brand-assets.py

`assets/brand/` holds twelve supplied variants, named CONTENT-for-BACKGROUND:

    mark-*      the figure alone
    wordmark-*  GREYMAN / PROTECTION alone
    lockup-*    both together

    *-for-dark    transparent, light ink   -> use on a dark ground (this site)
    *-for-light   transparent, dark ink    -> use on a light ground
    *-on-black    baked onto solid black
    *-on-white    baked onto solid white

Pick by the background you are placing it on. Putting a `-for-light` variant on
this site makes it invisible, which is not obvious until someone looks.

The site ships only the two dark-ground transparent variants. The wordmark is
NOT shipped: the site sets the name in type (see `.brand__text` in styles.css),
so the image beside it is the figure alone and the name is never duplicated.

The favicon is built from `mark-on-black`, not from a transparent variant: a
tab strip can be light or dark, and a light-ink transparent mark disappears on
a light one. The crop is a square around the figure, chosen by rendering the
candidates at 32px and looking at them rather than by guessing.
"""
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_DIR = os.path.join(ROOT, "assets", "brand")
IMG = os.path.join(ROOT, "assets", "img")

BLUE = "#0025A8"
LIFT = "#4D7CFF"

os.makedirs(IMG, exist_ok=True)


def out(name):
    return os.path.join(IMG, name)


def brand(name):
    p = os.path.join(BRAND_DIR, name)
    if not os.path.exists(p):
        sys.exit(f"missing brand asset: {p}")
    return Image.open(p)


def trim(im, thresh=8):
    """Crop to the visible content, by alpha when present and by ink when not."""
    rgba = im.convert("RGBA")
    a = np.array(rgba)
    mask = a[:, :, 3] > thresh if a[:, :, 3].min() < 250 else a[:, :, :3].max(axis=2) > 40
    nz = np.argwhere(mask)
    if not len(nz):
        return rgba
    (y0, x0), (y1, x1) = nz.min(0), nz.max(0) + 1
    return rgba.crop((x0, y0, x1, y1))


def pad_square(im, pad_frac=0.05):
    side = int(max(im.size) * (1 + pad_frac * 2))
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(im, ((side - im.width) // 2, (side - im.height) // 2))
    return sq


# ---- 1. the two variants the site actually uses -------------------------
mark = pad_square(trim(brand("mark-for-dark.png")))
mark.save(out("greyman-mark.png"), optimize=True)

lockup = pad_square(trim(brand("lockup-for-dark.png")), pad_frac=0.03)
lockup.save(out("greyman-lockup.png"), optimize=True)

# ---- 2. favicons, from the solid-black mark so they read on any tab -----
solid = brand("mark-on-black.png").convert("RGB")
a = np.array(solid)
nz = np.argwhere(a.max(axis=2) > 40)
(y0, x0), (y1, x1) = nz.min(0), nz.max(0) + 1
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
half = max(x1 - x0, y1 - y0) // 2 + 26
fav = solid.crop((max(0, cx - half), max(0, cy - half),
                  min(solid.width, cx + half), min(solid.height, cy + half)))
if fav.width != fav.height:                      # keep it square after clamping
    side = max(fav.size)
    sq = Image.new("RGB", (side, side), (0, 0, 0))
    sq.paste(fav, ((side - fav.width) // 2, (side - fav.height) // 2))
    fav = sq

for size, name in [(32, "favicon-32.png"), (192, "favicon-192.png"),
                   (512, "favicon-512.png"), (180, "apple-touch-icon.png")]:
    fav.resize((size, size), Image.LANCZOS).save(out(name), optimize=True)

# ---- 3. Open Graph card ------------------------------------------------
# Fonts are embedded as data URIs. A <link> to Google Fonts races the
# screenshot, and the API returns one @font-face per subset with latin NOT
# first, so naively taking the first match embeds a font with no Latin glyphs
# that Chromium loads and silently falls back from. The card then ships in
# Arial and looks almost right.
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def font_face(family, weight, css_name):
    import base64
    import urllib.request
    api = f"https://fonts.googleapis.com/css2?family={family}:wght@{weight}&display=block"
    req = urllib.request.Request(api, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
    try:
        css = urllib.request.urlopen(req, timeout=25).read().decode()
        blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
        chosen = next((b for n, b in blocks if n == "latin"), None)
        if chosen is None:
            chosen = blocks[-1][1] if blocks else css
        url = re.search(r"src:\s*url\((https://[^)]+)\)", chosen).group(1)
        blob = urllib.request.urlopen(url, timeout=25).read()
    except Exception as e:                       # noqa: BLE001
        print(f"note: could not embed {css_name} ({e}); falling back")
        return ""
    fmt = "woff2" if url.endswith(".woff2") else "truetype"
    b64 = base64.b64encode(blob).decode()
    return (f"@font-face{{font-family:'{css_name}';font-weight:{weight};"
            f"font-display:block;src:url(data:font/{fmt};base64,{b64}) format('{fmt}')}}")


faces = font_face("Chakra+Petch", 700, "Chakra Petch") + \
        font_face("Barlow+Condensed", 700, "Barlow Condensed")

# The card sets the name the same way the site does: GREYMAN, then PROTECTION
# centred between two blue rules that fill out to the same width.
STYLE = """
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1200px;height:630px;background:#000;display:flex;align-items:center;
       gap:56px;padding:0 80px;overflow:hidden;position:relative}
  body::after{content:"";position:absolute;inset:0;
       background:radial-gradient(720px 430px at 74% 50%,rgba(0,37,168,.34),transparent 70%)}
  img{width:300px;height:auto;position:relative;z-index:1;flex:none}
  .t{position:relative;z-index:1;display:flex;flex-direction:column;align-items:stretch}
  h1{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:104px;
     line-height:.9;color:#fff;letter-spacing:.06em;margin-right:-.06em}
  .sub{display:flex;align-items:center;gap:16px;margin-top:16px}
  .sub span{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:31px;
            letter-spacing:.42em;margin-right:-.42em;color:#fff;text-transform:uppercase}
  .sub i{flex:1;height:5px;background:BLUEHEX;display:block}
  p{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:19px;
    letter-spacing:.18em;color:#8E8E99;margin-top:30px;white-space:nowrap;
    text-transform:uppercase}
""".replace("BLUEHEX", BLUE)

og_html = os.path.join(BRAND_DIR, "_og.html")
with open(og_html, "w", encoding="utf-8") as f:
    f.write('<!DOCTYPE html><html><head><meta charset="utf-8">\n'
            f"<style>{faces}</style>\n<style>{STYLE}</style></head><body>\n"
            '  <img src="mark-for-dark.png">\n'
            '  <div class="t">\n'
            "    <h1>GREYMAN</h1>\n"
            '    <div class="sub"><i></i><span>Protection</span><i></i></div>\n'
            "    <p>Security &middot; Protection &middot; Intelligence &middot; Control</p>\n"
            "  </div>\n</body></html>")

if os.path.exists(CHROME):
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", "--virtual-time-budget=9000",
                    f"--screenshot={out('og-image.png')}", og_html],
                   check=False, capture_output=True)
    if os.path.exists(out("og-image.png")):
        Image.open(out("og-image.png")).convert("RGB").save(out("og-image.png"), optimize=True)
else:
    print(f"note: no chromium at {CHROME}, skipped og-image.png")
os.remove(og_html)

# ---- 4. retire assets the site no longer references ---------------------
for stale in ("greyman-logo.png",):
    p = out(stale)
    if os.path.exists(p):
        os.remove(p)
        print(f"   removed superseded {stale}")

print("Built:")
for n in ("greyman-mark.png", "greyman-lockup.png", "favicon-32.png",
          "favicon-192.png", "favicon-512.png", "apple-touch-icon.png",
          "og-image.png"):
    p = out(n)
    if os.path.exists(p):
        w, h = Image.open(p).size
        print(f"   {n:22s} {w}x{h}  {os.path.getsize(p)/1024:.1f} KB")

#!/usr/bin/env python3
"""Build every Greyman Protection image asset from the one master logo.

    python3 tools/build-brand-assets.py

Source of truth is assets/brand/greyman-logo-master.png, the 2000x2000 logo
lifted out of the company profile PDF. Everything the site ships is derived
from it here, so there is one place to regenerate from if the logo changes.

The favicon is NOT the full lockup. At 32px the lockup collapses into noise:
the "GREY MAN" wordmark straddles the figure's neck, so any crop containing it
reads as grey mush. The mark used instead is the sword-and-collar, cropped to
avoid both the wordmark underline (ends at y=841) and the small dash element on
the right (starts at x=1245). It is the one part of the logo that survives
being 32 pixels wide.
"""
import os
import re
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "assets", "brand", "greyman-logo-master.png")
IMG = os.path.join(ROOT, "assets", "img")

BLACK = (0, 0, 0)
BLUE = "#0025A8"

# Square crop centred on the sword, clear of the wordmark and the dash.
MARK_BOX = (760, 860, 1240, 1340)

os.makedirs(IMG, exist_ok=True)


def out(name):
    return os.path.join(IMG, name)


if not os.path.exists(MASTER):
    sys.exit(f"missing master logo: {MASTER}")

master = Image.open(MASTER).convert("RGB")
if master.size != (2000, 2000):
    print(f"note: master is {master.size}, crops were derived for 2000x2000")

# ---- 1. full lockup, trimmed to content with a small even margin ----
lockup = master.crop((432 - 40, 270 - 40, 1567 + 40, 1805 + 40))
lockup.save(out("greyman-logo.png"), optimize=True)
lockup.save(os.path.join(ROOT, "assets", "brand", "greyman-logo.png"), optimize=True)

# ---- 2. the square mark ----
mark = master.crop(MARK_BOX)
mark.save(out("greyman-mark.png"), optimize=True)

# ---- 3. favicons and touch icon, all from the mark ----
for size, name in [(32, "favicon-32.png"), (192, "favicon-192.png"),
                   (512, "favicon-512.png"), (180, "apple-touch-icon.png")]:
    mark.resize((size, size), Image.LANCZOS).save(out(name), optimize=True)

# ---- 4. Open Graph card, rendered in Chromium so the type matches the site ----
# The fonts are fetched and embedded as data URIs rather than linked. A <link>
# to Google Fonts races the screenshot: Chromium paints with the fallback face
# and the card silently ships in Arial. Embedding removes the race entirely.
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def font_face(family, weight, css_name):
    """Resolve one Google font to an embedded @font-face block."""
    import base64
    import urllib.request
    api = (f"https://fonts.googleapis.com/css2?family={family}:wght@{weight}"
           "&display=block")
    req = urllib.request.Request(api, headers={
        # without a modern UA the API serves legacy formats
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"})
    try:
        css = urllib.request.urlopen(req, timeout=25).read().decode()
        # The API returns one @font-face per subset, labelled with a preceding
        # /* subset */ comment, and latin is NOT first: for Chakra Petch the
        # first block is thai. Taking the first match embeds a font with no
        # Latin glyphs, which Chromium loads and then silently falls back from,
        # so the card renders in Arial and looks almost right. Pick latin.
        blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{.*?\})",
                            css, re.S)
        chosen = next((b for name, b in blocks if name == "latin"), None)
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
            f"font-display:block;"
            f"src:url(data:font/{fmt};base64,{b64}) format('{fmt}')}}")


faces = "".join([
    font_face("Chakra+Petch", 700, "Chakra Petch"),
    font_face("Barlow+Condensed", 600, "Barlow Condensed"),
])

og_html = os.path.join(ROOT, "assets", "brand", "_og.html")
STYLE = """
  *{margin:0;padding:0;box-sizing:border-box}
  body{width:1200px;height:630px;background:#000;display:flex;align-items:center;
       gap:60px;padding:0 76px;font-family:'Barlow Condensed',sans-serif;
       overflow:hidden;position:relative}
  body::after{content:"";position:absolute;inset:0;
       background:radial-gradient(720px 430px at 76% 50%,rgba(0,37,168,.32),transparent 70%)}
  img{width:280px;height:auto;position:relative;z-index:1;flex:none}
  .t{position:relative;z-index:1;min-width:0}
  h1{font-family:'Chakra Petch',sans-serif;font-weight:700;font-size:76px;
     line-height:.95;color:#fff;letter-spacing:-.5px}
  h1 span{color:#4D7CFF;display:block}
  p{font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:21px;
    letter-spacing:.16em;color:#9A9AA6;margin-top:24px;white-space:nowrap}
  .rule{width:96px;height:4px;background:BLUEHEX;margin-top:24px}
""".replace("BLUEHEX", BLUE)

with open(og_html, "w", encoding="utf-8") as f:
    f.write("<!DOCTYPE html><html><head><meta charset=\"utf-8\">\n"
            f"<style>{faces}</style>\n<style>{STYLE}</style></head><body>\n"
            '  <img src="greyman-logo-master.png">\n'
            "  <div class=\"t\">\n"
            "    <h1>Greyman<span>Protection</span></h1>\n"
            "    <p>SECURITY &middot; PROTECTION &middot; INTELLIGENCE &middot; CONTROL</p>\n"
            '    <div class="rule"></div>\n'
            "  </div>\n</body></html>")

if os.path.exists(CHROME):
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", "--virtual-time-budget=9000",
                    f"--screenshot={out('og-image.png')}", og_html],
                   check=False, capture_output=True)
    if os.path.exists(out("og-image.png")):
        Image.open(out("og-image.png")).convert("RGB").resize((1200, 630)).save(
            out("og-image.png"), optimize=True)
else:
    print(f"note: no chromium at {CHROME}, skipped og-image.png")
os.remove(og_html)

print("Built:")
for n in ("greyman-logo.png", "greyman-mark.png", "favicon-32.png",
          "favicon-192.png", "favicon-512.png", "apple-touch-icon.png",
          "og-image.png"):
    p = out(n)
    if os.path.exists(p):
        w, h = Image.open(p).size
        print(f"   {n:24s} {w}x{h}  {os.path.getsize(p)/1024:.1f} KB")

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
import sys

import numpy as np
from PIL import Image, ImageDraw

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


# ---- 1. the two variants the site actually uses -------------------------
# Trimmed to content and shipped at their NATURAL aspect. Padding these into a
# square canvas was a mistake: the figure is portrait (roughly 3:4), so a square
# file rendered at 42x42 drew it ~31px wide floating in dead space, and every
# consumer then had to guess how much of the box was real. The pages declare the
# true intrinsic size and size on one axis, so the browser keeps the ratio.
mark = trim(brand("mark-for-dark.png"))
mark.save(out("greyman-mark.png"), optimize=True)

# The lockup is brand artwork, not a web asset: the site sets the name in type
# and uses the figure alone for the watermark, so nothing on a page links this.
lockup = trim(brand("lockup-for-dark.png"))
lockup.save(os.path.join(BRAND_DIR, "greyman-lockup.png"), optimize=True)
_stale_lockup = out("greyman-lockup.png")
if os.path.exists(_stale_lockup):
    os.remove(_stale_lockup)

# ---- 2. favicons, from the solid-black mark so they read on any tab -----
solid = brand("mark-on-black.png").convert("RGB")
a = np.array(solid)
nz = np.argwhere(a.max(axis=2) > 40)
(y0, x0), (y1, x1) = nz.min(0), nz.max(0) + 1
cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
half = max(x1 - x0, y1 - y0) // 2 + 26
fav = solid.crop((max(0, cx - half), max(0, cy - half),
                  min(solid.width, cx + half), min(solid.height, cy + half)))
# An icon file has to be square. Get there by padding on black, never by
# resizing a non-square crop to a square, which would squash the figure.
if fav.width != fav.height:
    side = max(fav.size)
    sq = Image.new("RGB", (side, side), (0, 0, 0))
    sq.paste(fav, ((side - fav.width) // 2, (side - fav.height) // 2))
    fav = sq
assert fav.width == fav.height, "favicon source must be square before resizing"

for size, name in [(32, "favicon-32.png"), (192, "favicon-192.png"),
                   (512, "favicon-512.png"), (180, "apple-touch-icon.png")]:
    fav.resize((size, size), Image.LANCZOS).save(out(name), optimize=True)

# favicon.ico at the repo root: still what some crawlers, feed readers and
# older browsers fetch by convention, whatever <link rel="icon"> says.
fav.resize((64, 64), Image.LANCZOS).save(
    os.path.join(ROOT, "favicon.ico"), format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

# ---- 2b. theme-aware SVG favicon ---------------------------------------
# Built from the TRANSPARENT mark, with the ink colour switched by an embedded
# prefers-color-scheme rule, so the figure is dark on a light tab strip and
# light on a dark one. The blue sword is left alone: it reads on both.
#
# The PNG and ICO stay as fallbacks. Chrome and Firefox honour the media query
# inside an SVG favicon; anything that does not simply takes the PNG.
def svg_favicon():
    import potrace

    src = trim(brand("mark-for-dark.png"))
    side = max(src.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.alpha_composite(src, ((side - src.width) // 2, (side - src.height) // 2))
    sq = sq.resize((240, 240), Image.LANCZOS)

    a = np.array(sq).astype(int)
    r, g, b, al = a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3]
    solid = al > 128
    blue = solid & (b - np.maximum(r, g) > 40)
    ink = solid & ~blue

    def trace(mask):
        # bool array, and the complement: see trace-division-icons.py for why
        pth = potrace.Bitmap(np.ascontiguousarray(~mask, dtype=bool)).trace(
            turdsize=8, alphamax=1.0, opticurve=True, opttolerance=0.8)
        sc = 100 / 240
        f = lambda q: f"{q.x * sc:.1f} {q.y * sc:.1f}"          # noqa: E731
        out = []
        for c in pth:
            out.append("M" + f(c.start_point))
            for seg in c:
                out.append("L" + f(seg.c) + "L" + f(seg.end_point) if seg.is_corner
                           else "C" + f(seg.c1) + " " + f(seg.c2) + " " + f(seg.end_point))
            out.append("Z")
        return "".join(out)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
           '<style>.ink{fill:#0B0B0D}'
           '@media (prefers-color-scheme:dark){.ink{fill:#FFFFFF}}</style>'
           f'<path class="ink" d="{trace(ink)}"/>'
           f'<path fill="{BLUE}" d="{trace(blue)}"/>'
           '</svg>')
    with open(out("favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


svg_favicon()

# ---- 3. Open Graph card ------------------------------------------------
# The card is the lockup itself, centred: the figure with GREYMAN / PROTECTION
# beneath it, exactly as the brand artwork draws it. An earlier version set the
# name in type beside the mark, which meant the share image and the logo were
# two different lockups of the same name.
#
# No webfonts are needed now that no type is being set, which also removes the
# Google Fonts round trip from this build.
def og_card():
    W, H = 1200, 630
    card = Image.new("RGBA", (W, H), (0, 0, 0, 255))

    # A soft blue bloom behind the mark so the black ground has some depth.
    # Computed as a smooth radial falloff rather than drawn as concentric
    # ellipses: stepped alpha leaves a visible hard edge where the outermost
    # ring meets the background, which reads as a grey oval rather than a glow.
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W / 2, H * 0.46
    d = np.sqrt(((xx - cx) / (W * 0.42)) ** 2 + ((yy - cy) / (H * 0.62)) ** 2)
    falloff = np.clip(1.0 - d, 0.0, 1.0) ** 2.2
    glow = np.zeros((H, W, 4), dtype=np.uint8)
    glow[:, :, 0], glow[:, :, 1], glow[:, :, 2] = 0, 37, 168
    glow[:, :, 3] = (falloff * 64).astype(np.uint8)
    card.alpha_composite(Image.fromarray(glow, "RGBA"))

    art = trim(brand("lockup-for-dark.png"))
    # fit to the card height with generous margin; the lockup is portrait so
    # height is the binding dimension
    target_h = int(H * 0.74)
    scale = target_h / art.height
    art = art.resize((max(1, int(art.width * scale)), target_h), Image.LANCZOS)
    card.alpha_composite(art, ((W - art.width) // 2, (H - art.height) // 2))

    card.convert("RGB").save(out("og-image.png"), optimize=True)


og_card()

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

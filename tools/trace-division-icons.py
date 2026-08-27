#!/usr/bin/env python3
"""Trace the client's division icons into SVG sprite symbols.

    pip install potracer pillow numpy
    python3 tools/trace-division-icons.py

The six icons were supplied as one flat PNG strip. Redrawing them by hand would
be an approximation of someone else's artwork; tracing keeps the shapes theirs.

Each cell is separated into two masks and traced independently:

    blue  -> the container (ring or shield) and any blue detail in the glyph
    white -> the glyph itself

They are emitted as two filled paths, white first and blue over it, because in
the investigation icon the blue fingerprint sits ON the white magnifier body.
Drawing blue first would bury it.

The blue path is filled with `var(--blue-lift)` rather than the raw brand blue:
these render on a near-black ground where #0025A8 measures 1.73:1 and reads as
a smudge. The glyph takes `var(--ink)` rather than `currentColor`: these icons are
two-tone by design, white glyph on a blue container, so they should not pick up
whatever colour the surrounding component happens to set.

Output goes to tools/_division-icons.svg, which build-site.py inlines.
"""
import os
import sys

import numpy as np
import potrace
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "brand", "division-icons-source.png")
OUT = os.path.join(ROOT, "tools", "_division-icons.svg")

# Cell boundaries measured off the source strip, and the sprite id each becomes.
# The labels on the artwork are the PREVIOUS brand's division names; the ids are
# ours. The mapping is in BRAND.md section 4b.
CELLS = [
    ("d-investigations",   0,  362),   # fingerprint under a magnifier
    ("d-polygraph",      362,  673),   # ECG trace
    ("d-asset",          673,  975),   # padlock in a shield
    ("d-close",          975, 1285),   # suited figure
    ("d-guarding",      1285, 1594),   # three figures in a shield
    ("d-mining",        1594, None),   # ballistic helmet
]

# Trace at this height; higher keeps more detail and costs path bytes. The
# sprite is inlined on every page, so this is a real page-weight decision:
# 300 cost 21.4 KB of path data, 200 costs 12.2 KB and is indistinguishable at
# the sizes these are actually used (96px and below). One decimal place is
# 1/1000 of the icon, far below a pixel.
TRACE_H = 200
VIEW = 100          # symbol coordinate space


def mask_paths(mask, scale, turdsize=10):
    """Trace a boolean mask to an SVG path 'd' string in VIEW coordinates."""
    # MUST be a bool array. potracer thresholds anything else at > 127.5, so a
    # 0/1 uint8 mask reads as entirely background and traces the whole frame as
    # a single rectangle, which looks like a working trace until you render it.
    # and it must be the COMPLEMENT: potracer's Bitmap calls invert() on
    # construction, so passing the mask as-is traces the background and returns
    # a frame with the glyph punched out of it.
    bmp = potrace.Bitmap(np.ascontiguousarray(~mask, dtype=bool))
    path = bmp.trace(turdsize=turdsize, alphamax=1.0, opticurve=True,
                     opttolerance=0.9)
    # potracer yields _Point objects, not tuples
    def pt(p_):
        return f"{p_.x * scale:.1f} {p_.y * scale:.1f}"

    out = []
    for curve in path:
        out.append("M" + pt(curve.start_point))
        for seg in curve:
            if seg.is_corner:
                out.append("L" + pt(seg.c) + "L" + pt(seg.end_point))
            else:
                out.append("C" + pt(seg.c1) + " " + pt(seg.c2)
                           + " " + pt(seg.end_point))
        out.append("Z")
    return "".join(out)


def main():
    if not os.path.exists(SRC):
        sys.exit(f"missing source strip: {SRC}")

    strip = Image.open(SRC).convert("RGB")
    W, H = strip.size
    symbols = []

    for name, x0, x1 in CELLS:
        x1 = x1 if x1 is not None else W
        # inset a few px: the strip has a bright hairline along its edges that
        # would otherwise read as content
        cell = strip.crop((x0 + 8, 3, x1 - 8, H - 3))

        # Crop to the badge itself. The artwork carries a text label underneath
        # which is part of the source image and must not end up in the icon, so
        # take the TALLEST contiguous run of lit rows rather than the first:
        # the first is whatever edge artifact survived the inset, and the label
        # is a shorter run further down.
        a0 = np.array(cell).astype(int)
        lit = a0.max(axis=2) > 60
        rows_lit = lit.sum(axis=1) > 0
        runs, start = [], None
        for y, on in enumerate(rows_lit):
            if on and start is None:
                start = y
            elif not on and start is not None:
                runs.append((start, y)); start = None
        if start is not None:
            runs.append((start, len(rows_lit)))
        if not runs:
            sys.exit(f"{name}: found no content in the cell")
        top, bottom = max(runs, key=lambda r: r[1] - r[0])

        band = lit[top:bottom]
        colmask = band.any(axis=0)
        left = int(np.argmax(colmask))
        right = int(len(colmask) - np.argmax(colmask[::-1]))
        badge = cell.crop((left, top, right, bottom))

        side = max(badge.size)
        sq = Image.new("RGB", (side, side), (0, 0, 0))
        sq.paste(badge, ((side - badge.width) // 2, (side - badge.height) // 2))
        sq = sq.resize((TRACE_H, TRACE_H), Image.LANCZOS)

        a = np.array(sq).astype(int)
        r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        blue = (b - np.maximum(r, g) > 40) & (b > 70)
        white = (np.minimum(np.minimum(r, g), b) > 110)

        scale = VIEW / TRACE_H
        d_white = mask_paths(white, scale)
        d_blue = mask_paths(blue, scale)

        parts = []
        if d_white:
            parts.append(f'<path fill="var(--ink,#fff)" d="{d_white}"/>')
        if d_blue:
            parts.append(f'<path fill="var(--blue-lift)" d="{d_blue}"/>')
        symbols.append(
            f'    <symbol id="{name}" viewBox="0 0 {VIEW} {VIEW}">'
            + "".join(parts) + "</symbol>")
        print(f"   {name:20s} white {len(d_white):6d}B  blue {len(d_blue):6d}B")

    # Training has no icon in the supplied set, so this one is ours. It is
    # drawn rather than traced, to the ring geometry measured off the client's
    # own art (r=47.5, stroke 4 in a 100 unit box) so it sits in the same
    # family instead of merely nearby.
    symbols.append(
        '    <symbol id="d-training" viewBox="0 0 100 100">'
        '<g fill="none" stroke="var(--ink,#fff)" stroke-width="6.5" '
        'stroke-linecap="round">'
        '<circle cx="50" cy="50" r="23"/>'
        '<path d="M50 13.5v9M50 77.5v9M13.5 50h9M77.5 50h9"/></g>'
        '<circle cx="50" cy="50" r="8.5" fill="var(--ink,#fff)"/>'
        '<circle cx="50" cy="50" r="47.5" fill="none" '
        'stroke="var(--blue-lift)" stroke-width="4"/></symbol>')
    print(f"   {'d-training':20s} drawn to match, not traced (not in the source set)")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(symbols) + "\n")
    total = os.path.getsize(OUT)
    print(f"\nwrote {os.path.relpath(OUT, ROOT)}  {total/1024:.1f} KB "
          f"(inlined on every page)")


if __name__ == "__main__":
    main()

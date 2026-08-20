#!/usr/bin/env bash
# Swap the placeholder crest for INTEGRI's real logo file.
#
#   ./tools/use-real-logo.sh ~/Downloads/integri-logo.png
#
# Copies your file into assets/img/ and rewires every reference on every page
# (favicon, apple-touch-icon, og:image, both header/footer marks, hero watermark).
# Re-run it any time the artwork changes.

set -euo pipefail
cd "$(dirname "$0")/.."

SRC="${1:-}"
if [[ -z "$SRC" || ! -f "$SRC" ]]; then
  echo "usage: $0 <path-to-logo-file>   (.png, .svg or .webp — transparent background)" >&2
  exit 1
fi

EXT="${SRC##*.}"
EXT="$(echo "$EXT" | tr '[:upper:]' '[:lower:]')"
case "$EXT" in
  png|svg|webp) ;;
  *) echo "error: expected .png, .svg or .webp, got .$EXT" >&2; exit 1 ;;
esac

DEST="assets/img/integri-crest.$EXT"
cp "$SRC" "$DEST"
echo "copied -> $DEST"

PAGES=(index.html about.html contact.html services/*.html)

# point every reference at the new file
# NB: '#' as the delimiter — '|' would collide with the \| alternation below
sed -i "s#integri-crest\.\(svg\|png\|webp\)#integri-crest.$EXT#g" "${PAGES[@]}"

# the favicon <link> carries an explicit MIME type; keep it honest
case "$EXT" in
  png)  MIME="image/png" ;;
  webp) MIME="image/webp" ;;
  svg)  MIME="image/svg+xml" ;;
esac
sed -i "s|\(rel=\"icon\" href=\"[^\"]*integri-crest\.$EXT\" type=\"\)[^\"]*\"|\1$MIME\"|g" "${PAGES[@]}"

# drop the old placeholder if it is no longer the one in use
if [[ "$EXT" != "svg" && -f assets/img/integri-crest.svg ]]; then
  rm assets/img/integri-crest.svg
  echo "removed the placeholder assets/img/integri-crest.svg"
fi

echo
echo "references now pointing at integri-crest.$EXT:"
grep -c "integri-crest\.$EXT" "${PAGES[@]}"
echo
echo "Done. Review with:  python3 -m http.server 8080"

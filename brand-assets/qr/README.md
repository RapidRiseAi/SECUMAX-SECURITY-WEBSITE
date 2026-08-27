# Greyman Protection QR codes

Two codes. Both generated offline with `segno`, both decoded back and re-tested
at simulated print sizes before being written. Regenerate with:

```
python3 tools/build-contact-qr.py
```

Nothing here depends on a third-party service. A QR is just its payload painted
as squares: once printed it needs no account, no renewal, and nothing anyone
else can deprecate. **Never** put a shortener or a "dynamic QR" service inside a
printed code, because when that service dies every card in every wallet dies
with it, and there is no fixing it.

---

## 1. Contact page code

**Payload:** `https://www.greymanprotection.co.za/contact`

Verified live and returning 200 before these were generated. Version 5, 37
modules, error correction **H** (30% of the symbol can be damaged or covered and
it still reads, which is what lets the crest sit in the middle).

| File | Use it for |
|---|---|
| `greyman-contact-qr.svg` | **Print. Give this to the printer.** Vector, any size. |
| `greyman-contact-qr.png` | Screens, email signatures, slides. |
| `greyman-contact-qr-black-transparent.png` | Placing on a light background of your own. |
| `greyman-contact-qr-on-white-panel.png` | The black business card. |
| `greyman-contact-qr-branded.png` | Crest knocked into the centre. |

Decodes in testing down to 12 mm. **Print it at 20 to 25 mm.**

## 2. vCard code, which depends on no domain at all

**Payload:** a vCard. Scanning it offers to save Greyman Protection to the
reader's contacts: both numbers, the ops address, the office address and the
website. Nothing is fetched, so there is nothing to keep alive.

`greyman-vcard-qr.svg` and `.png`.

A vCard carries far more data than a URL, so the symbol is much denser: version
15, **77 modules** against the URL code's 37. It decoded down to 20 mm in
simulation, but that is perfect ink on perfect paper. **Print this one at 25 to
30 mm minimum**, and scan the physical proof before the full run.

This is the more robust choice for a business card, because it survives a domain
move. The URL code is better if you want people to land on the contact page.

---

## Print rules, both codes

1. **Minimum size as above.** Below it you are relying on the reader's camera
   being better than the print.
2. **Keep the quiet zone.** Four modules of clear space on all four sides. The
   SVG and the white-panel PNG already include it. Do not crop into it and do
   not let text or a rule touch the edge.
3. **Dark on light only. Never invert.** A white-on-black version was built for
   the previous brand, failed to decode, and was deleted. For the black card use
   `greyman-contact-qr-on-white-panel.png`.
4. **Scale uniformly.** No recolouring, stretching, rotated modules or rounded
   corners.
5. **Scan the physical proof before the full run.** Two phones, one iPhone and
   one Android, in dim light.

## If the domain ever changes again

The contact code dies and must be reprinted. The vCard code does not. Update
`URL` in `tools/build-contact-qr.py`, confirm the new address returns 200, and
regenerate: the script refuses to finish if any variant fails to decode.

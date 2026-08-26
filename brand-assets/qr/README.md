# INTEGRI contact QR code

**Encoded URL**

```
https://www.integriforensicservices.com/contact
```

Nothing else is inside the code. No shortener, no redirect service, no tracking
domain. A QR code is just the URL painted as squares, so once it is printed it
depends on exactly one thing staying alive: that URL. No third party can
deprecate it, rate limit it, or start charging for it.

## Files

| File | Use it for |
|---|---|
| `integri-contact-qr.svg` | **Print. Give this to the printer.** Vector, scales to any size with no softening. |
| `integri-contact-qr.png` | Screens, email signatures, slides. 1960 px, black on white. |
| `integri-contact-qr-black-transparent.png` | Placing on a light background of your own. Transparent behind the modules. |
| `integri-contact-qr-on-white-panel.png` | The black business card. White rounded panel with quiet zone built in. |
| `integri-contact-qr-branded.png` | Crest knocked into the centre. Use only if the layout calls for it. |

## Print rules

1. **Minimum printed size 20 mm square.** It decodes down to 10 mm in testing,
   but that is with perfect ink on perfect paper. 20 to 25 mm on a business card
   leaves room for cheap printing, uncoated stock and a shaky hand.
2. **Keep the quiet zone.** Four modules of clear space on all four sides, about
   2 mm at 20 mm size. The SVG and the white panel PNG already include it. Do
   not crop into it and do not let text or a rule run up against the edge.
3. **Dark on light only.** Never invert it to white on black. The white on black
   version was built, tested, and deleted because scanners could not read it.
   For the black card, use `integri-contact-qr-on-white-panel.png`.
4. **Do not recolour, stretch, rotate the modules or round the corners.** Scale
   uniformly, that is all.
5. **Scan the physical proof before the full run.** Two phones, one iPhone and
   one Android, in dim light.

## Technical

- Error correction level **H**, the highest of the four. Up to 30 percent of the
  symbol can be damaged or covered and it still decodes. That is what lets the
  crest sit in the middle of the branded version.
- Version 6, 41 by 41 modules.
- Generated offline with `segno`. Every file was decoded back with OpenCV to
  confirm it returns the exact URL, then rescaled to simulated print sizes from
  30 mm down to 10 mm at 600 dpi and decoded again at each size.

## Why /contact is the right URL to print

Checked against the live site rather than assumed. The production host serves
extensionless URLs and redirects the `.html` form away:

```
/contact        200  serves the page
/contact.html   307  -> /contact
/contact/       307  -> /contact
```

The same pattern holds for every page on the site. So `/contact` is not a
convenience alias, it is the canonical URL, and `/contact.html` is the one that
redirects. Printing `/contact` is correct.

The repository still stores the file as `contact.html`, and internal links
still point at `contact.html`, so the site keeps working on a plain file server
and in local dev. Only the absolute URLs the site declares about itself
(`rel="canonical"` and `og:url`) use the extensionless form, because those have
to match what the host actually serves.

**If the site is ever moved to a host that does not do extensionless URLs, the
printed cards break.** Any replacement host must serve `contact.html` at
`/contact`. That is one line of config on nginx (`try_files $uri $uri.html`) and
the default on Netlify, Vercel, Cloudflare and GitHub Pages, but it is not
automatic everywhere, so it belongs in the handover notes for whoever moves it.

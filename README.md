# INTEGRI Forensic and Protection Services — Website

Marketing site for **INTEGRI Forensic and Protection Services**, a PSIRA-registered South
African firm covering investigation, forensics, polygraph examination, security, protection,
guarding and specialised services.

Static HTML/CSS/JS. No build step, no framework, no runtime dependencies.

---

## Structure

```
index.html              # Home
about.html              # About INTEGRI
contact.html            # Contact + enquiry form
services/
  index.html            # Divisions hub
  investigation.html    # 01
  forensic.html         # 02
  polygraph.html        # 03
  security.html         # 04
  protection.html       # 05
  guarding.html         # 06
  specialized.html      # 07
assets/
  css/styles.css        # complete design system
  js/main.js            # interactions (vanilla JS)
  img/integri-crest.svg # brand crest
BRAND.md                # build contract — read before editing anything
CLIENT-PACK.md          # for the client: 56 services to confirm + documents needed
BUILD-STATUS.md         # for the team: what's done, blocked and queued
tools/use-real-logo.sh  # swap the placeholder crest for the real artwork
```

**This site is not ready to go public.** `BRAND.md` §1 carries a publication gate covering
three unresolved items: PSIRA registration status (asserted in 79 places but not yet confirmed),
director titles that contradict the CIPC record, and 56 sub-services drafted from industry norms
rather than supplied by the client. `CLIENT-PACK.md` is what goes to the client;
`BUILD-STATUS.md` is the internal view.

**`BRAND.md` is the source of truth.** It defines the colour tokens, typography, the exact
contact details, the seven divisions and their sub-services, the CSS class catalogue, and the
rules for adding a page. Read it before making changes.

---

## Design

| | |
|---|---|
| Palette | Black `#000000` · Red `#E01B24` · White |
| Display type | Chakra Petch |
| Body type | Barlow |
| Labels | Barlow Condensed, uppercase, letterspaced |

The site is photography-free by design. Visual weight comes from the SVG crest, red gradient
washes, a technical grid overlay and iconography — so it loads fast and has no image
licensing exposure. Every page shares one inline SVG icon sprite.

Motion (scroll reveals, hero rise, marquee, counters) is disabled automatically under
`prefers-reduced-motion`.

---

## Running locally

```bash
python3 -m http.server 8080
# http://localhost:8080
```

Opening `index.html` from the filesystem also works — all paths are relative.

## Deployment

Publish the repository root to any static host (Netlify, Vercel, Cloudflare Pages,
GitHub Pages). No build command; the output directory is the repo root.

---

## Things to know before you edit

**The crest is a placeholder.** `assets/img/integri-crest.svg` was hand-authored by eye to
match the brand mark, because the real logo was shared in chat and never landed in the
repository. It is not the real artwork. Swap it with one command:

```bash
./tools/use-real-logo.sh ~/Downloads/integri-logo.png
```

That copies the file into `assets/img/`, rewires all 56 references across the 11 pages
(favicon, apple-touch-icon, og:image, header and footer marks, hero watermark), corrects
the favicon MIME type and removes the placeholder. Accepts `.png`, `.svg` or `.webp`.

**The enquiry form has no backend.** It validates in the browser and then hands off to the
visitor's own mail client via `mailto:`, so nothing passes through a third party — but it
also means there is no delivery receipt and no submission log. To capture submissions
server-side, point the `<form>` at a form endpoint (Formspree, Basin, Netlify Forms) or a
serverless function, and remove the `mailto:` branch in `assets/js/main.js`.

**Claims on this site are deliberately limited.** The only accreditation claims made anywhere
are *PSIRA Registered & Compliant* and *Accredited Firearm Training*, because those are the
only ones supplied. There are no client counts, success rates, years-in-business figures,
staff numbers, response-time guarantees or testimonials. If you add any, make sure they are
true and substantiated — see the fabrication ban in `BRAND.md` §1.

**Confirmed and on the site:** registered name *INTEGRI Forensic Services (Pty) Ltd* and CIPC
number *2026/561988/07*, both in the footer of every page.

**Not yet supplied, and therefore absent:** PSIRA registration number, firearm-training
accreditation number, VAT number, business hours beyond "24/7", and social media accounts.

**Deliberately withheld:** the registered office address is also a director's residential
address, so it is not published — that is the client's call to make, not ours. The director's
ID number is not recorded in this repository at all.

---

## Adding a page

1. Copy the closest existing page (a service page, or `about.html` for a root-level page).
2. Fix the relative prefix: root pages use `assets/…`, pages in `services/` use `../assets/…`.
   Icon sprite references are always bare fragments — `<use href="#i-forensic"/>` — never prefixed.
3. Update the `<head>`: title, description, canonical, `og:` tags.
4. Move the `is-active` class onto the right nav item, in both the desktop nav and the mobile drawer.
5. Use only classes from the catalogue in `BRAND.md` §8. If you genuinely need a new component,
   add it to `styles.css` and document it there.

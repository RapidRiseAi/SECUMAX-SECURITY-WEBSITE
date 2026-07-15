# SECUMAX SECURITY — Website

A redesigned, mobile- and desktop-optimised marketing site for **SECUMAX SECURITY**.
Premium black-and-gold theme built around the brand crest, with a distinct blue (`#066aab`)
accent, animated interactions, and genuinely separate mobile and desktop experiences.

## Highlights

- **Brand-matched design** — black + gold (bear crest), `#066aab` blue accent, `Abril Fatface`
  display type + `Space Grotesk` UI type.
- **Distinct mobile vs desktop UI**
  - *Desktop:* full nav bar with active-section tracking, hover-driven service cards,
    a 3D-tilting AI CCTV monitor, multi-column grids.
  - *Mobile:* full-screen slide-in drawer, a sticky **Call / WhatsApp / Quote** action bar,
    single-column layouts, tap-friendly targets.
- **Animation** — page loader, scroll-progress bar, `IntersectionObserver` scroll reveals,
  animated stat counters, hero pan/scan, capability marquee, and a live "Spot-Bot" AI
  detection mockup. All motion respects `prefers-reduced-motion`.
- **Accessible & fast** — semantic HTML, skip link, focus states, lazy-loaded images,
  no build step and no runtime dependencies.
- **Real content** — all copy, services and contact details are taken from the existing
  site (secumaxsecurity.co.za); no placeholder filler.

## Structure

```
index.html            # single-page site
assets/
  css/styles.css      # design system + responsive rules
  js/main.js          # interactions (vanilla JS, no dependencies)
  img/                # brand crest + photography
```

## Running locally

It's a static site — open `index.html` directly, or serve the folder:

```bash
python3 -m http.server 8080
# then visit http://localhost:8080
```

## Deployment

Any static host works (Netlify, Vercel, GitHub Pages, Cloudflare Pages, or the current
host). Just publish the repository root.

## Notes

- The contact form uses a `mailto:` handoff to `info@secumaxsecurity.co.za` so it works with
  no backend. To capture submissions server-side, point the form at a form endpoint
  (e.g. Formspree/Basin) or a serverless function.
- The public phone number shown is the WhatsApp line `+27 63 537 1583`. The old site also
  listed a placeholder `+27123456789`, which has been left off — swap in the correct
  office number if there is one.
- Photography is the company's own imagery, used as darkened atmospheric backgrounds to suit
  the surveillance theme. Higher-resolution originals can be dropped into `assets/img/`.

# Greyman Protection

Static marketing site for Greyman Protection, a specialist security, protection
and investigative company in South Africa.

No framework, no build step for the browser: the deployable output is the repo
root. HTML, one stylesheet, one script.

## Layout

```
index.html  about.html  contact.html      root pages
services/                                 hub + 6 division pages
assets/css/styles.css                     the whole design system
assets/js/main.js                         all interaction
assets/img/                               favicons, OG card, logo
assets/brand/                             master artwork, not shipped to the page
tools/                                    generators and the validator
BRAND.md                                  the contract; read it before changing anything
```

## The pages are generated

Ten pages share a header, mobile drawer, icon sprite, footer, action bar and
to-top button. That chrome is emitted from one source, so **do not hand-edit the
HTML**: the next regenerate overwrites it. Edit the generator instead.

```bash
python3 tools/build-brand-assets.py   # logo, favicons, OG card, from the master logo
python3 tools/build-site.py           # all 10 pages from the taxonomy
python3 tools/validate.py             # must be green before pushing
```

Content and taxonomy live in `DIVISIONS`, `WHY`, `STEPS` and `CLIENTS` at the top
of `tools/build-site.py`.

## Local preview

```bash
python3 -m http.server 8080
# http://localhost:8080
```

Note that the production host serves extensionless URLs (`/contact`, not
`/contact.html`) and redirects the `.html` form away. Internal links keep the
`.html` suffix on purpose so the site also works on a plain file server and in
local dev; only the absolute self-URLs (`rel="canonical"`, `og:url`) use the
extensionless form, because those have to match what the host actually serves.

## What the validator checks

`tools/validate.py` is not decoration. It has caught a dead contact mailbox, a
broken link set on the services hub, and an accessibility violation propagated
across every page. It fails the build on:

- broken internal links, sprite `<use>` ids with no `<symbol>`, CSS classes used
  but never defined
- wrong relative prefixes (`assets/` at the root, `../assets/` under `services/`)
- more or fewer than one `<h1>`, inline `<style>`, stray inline styles
- leftover branding from either previous brand, and the old red palette tokens
- **claims with no paperwork behind them**: PSIRA, a company registration number,
  `24/7`, fabricated volumes or success rates
- any email or phone number outside the approved set
- em dashes, which the site does not use
- canonicals or `og:url` ending in `.html`, which the host redirects away

## Deployment

Publish the repo root to any static host. No build command. The host must serve
extensionless URLs, which Cloudflare, Vercel, Netlify and GitHub Pages do by
default; plain nginx needs `try_files $uri $uri.html`.

## Before this goes public

See BRAND.md §6 and §7. In short: the site currently makes **no PSIRA claim and
no company registration claim**, because the company profile supports neither.
Both were on the previous brand's site and neither transfers. The client needs to
supply the certificates before those go back on.

# Greyman Protection: brand and build contract

Single source of truth for the site. If something here and something in the code
disagree, this file wins and the code is wrong.

---

## 1. Identity

| | |
|---|---|
| Trading name | **Greyman Protection** |
| Tagline | SECURITY · PROTECTION · INTELLIGENCE · CONTROL |
| Positioning | Specialist security, protection and investigative services, South Africa |
| Email | **ops@greymanprotection.co.za** |
| Office | 466 Karel Trichardt Street, Mountainview, Pretoria |
| Directors | Etienne, +27 71 118 3257 · Jacques, +27 67 161 2570 |

The logo wordmark reads "GREY MAN"; the company name is written **Greyman
Protection** as one word, per the company profile. Both are correct in their own
place, so do not "fix" either to match the other.

### Domain

The site publishes on **`greymanprotection.co.za`**, confirmed live and serving
this build before the switch was made. It lives in exactly one place, `DOMAIN`
in `tools/build-site.py`.

The old `integriforensicservices.com` also still resolves to this site. Leaving
canonicals pointed at it told search engines the old domain was authoritative,
which is why they were switched. Point that domain at a 301 to this one when
convenient.

**Two things depend on it and will break silently if it moves again:**

1. Every `rel="canonical"` and `og:url`.
2. The printed contact QR code (`brand-assets/qr/`). It encodes
   `https://www.greymanprotection.co.za/contact`, which was verified live before
   generation. A moved domain means a reprint. The vCard QR beside it carries no
   URL dependency and survives a move.

Note also: the company profile PDF prints `www.greymanprotection.com` while the
working mailbox is `.co.za`. The site follows the mailbox. The PDF should be
corrected.

---

## 2. Colour

| Token | Value | Use |
|---|---|---|
| `--blue` | `#0025A8` | Brand blue, off the logo. **Fills only.** |
| `--blue-lift` | `#4D7CFF` | Type, icons, hairlines, links |
| `--blue-deep` | `#001A73` | Gradient end |
| `--grey` | `#4C4B4C` | Third brand colour, off the logo |
| `--black` / `--black-2` | `#000000` / `#08080A` | Page and section grounds |
| `--ink` / `--body` / `--muted` | `#FFFFFF` / `#C9C9D1` / `#8E8E99` | Text scale |

**The two blues are not interchangeable.** Brand blue on the near-black
background measures **1.73:1**, which is unreadable as text and fine as a fill
behind white (11.5:1). `--blue-lift` measures **5.1 to 5.6:1** on the dark
surfaces and clears WCAG AA.

> Never write `color: var(--blue)`. The validator does not catch this; a human
> reading a diff has to.

Verified: white on every blue fill passes AA, `--blue-lift` passes AA on all four
dark surfaces.

## 3. Typography

Chakra Petch (display) · Barlow (UI) · Barlow Condensed (labels). Unchanged from
the previous build; the rebrand did not change the type system.

### The wordmark is set in type, not shipped as an image

`.brand__text` reproduces the logo's own lockup in CSS: GREYMAN, then
PROTECTION centred between two blue rules that flex out to exactly GREYMAN's
width. The `<img>` beside it is therefore the **figure alone**, never the full
lockup, so the name is never drawn twice.

Two details that look like mistakes and are not: the negative `margin-right` on
both `strong` and the inner `span` cancels the trailing letter-space, so the
rules align to the glyphs instead of to empty space; and the rules carry a
`min-width` so they cannot be crowded to nothing when the word is long.

Any surface showing the name (the OG card included) uses this same treatment.

---

## 3b. Logo library

`assets/brand/` holds twelve supplied variants, named CONTENT-for-BACKGROUND:

| | `mark-` | `wordmark-` | `lockup-` |
|---|---|---|---|
| | the figure alone | GREYMAN / PROTECTION | both together |

| Suffix | What it is | Put it on |
|---|---|---|
| `-for-dark` | transparent, light ink | a dark ground (**this site**) |
| `-for-light` | transparent, dark ink | a light ground |
| `-on-black` | baked onto solid black | anything |
| `-on-white` | baked onto solid white | anything |

**Choose by the background you are placing it on.** A `-for-light` variant on
this site is invisible, and nothing about the filename in a diff makes that
obvious. `tools/validate.py` fails the build if a page references one.

The site ships exactly two: `greyman-mark.png` (the figure, for the header and
the hero watermark) and `greyman-lockup.png`. The wordmark images are never
shipped, because the name is set in type.

The favicon is built from `mark-on-black`, not from a transparent variant: a
browser tab strip can be light or dark, and light ink on transparent disappears
on a light one. The crop was chosen by rendering candidates at 32px and looking
at them.

---

## 3c. Icon system

Two families, deliberately.

**Division badges** (`d-*`) are the client's own artwork, supplied as a flat PNG
strip and **traced**, not redrawn: `tools/trace-division-icons.py` separates each
cell into a blue mask (the ring or shield) and a white mask (the glyph), traces
each with potrace and emits two filled paths. Redrawing them by hand would have
been an approximation of someone else's design.

They are two-tone by construction: the glyph takes `var(--ink)` and the
container `var(--blue-lift)`, so they do not inherit whatever colour the
surrounding component sets. That is why `.svc-card__icon` no longer draws a
tinted chip; the badge already carries its own container and framing it again
was a container inside a container.

**UI icons** (`i-*`) stay the thin stroked set: mail, phone, arrow, and the
sub-service icons inside division pages. Mixing a badge into a row of stroked
icons reads as a mistake, so sub-services keep the stroked family.

| Badge | Source | Used for |
|---|---|---|
| `d-investigations` | fingerprint under a magnifier | Special Investigations |
| `d-asset` | padlock in a shield | Asset Protection |
| `d-close` | suited figure | Executive Close Protection |
| `d-mining` | ballistic helmet | Mining Security |
| `d-guarding` | three figures in a shield | Guarding and Site Security |
| `d-polygraph` | ECG trace | the Polygraph Services sub-service |
| `d-training` | **drawn by us**, not supplied | Training |

The supplied strip is labelled with the *previous* brand's division names, so
the artwork-to-division mapping above is a deliberate reassignment, not a
one-to-one copy. Training had no icon in the set; ours is drawn to the ring
geometry measured off the client's own art (r=47.5, stroke 4 in a 100 unit box)
so it sits in the family rather than merely near it.

Re-tracing is the only step needed to update them:

```
python3 tools/trace-division-icons.py   # writes tools/_division-icons.svg
python3 tools/build-site.py             # inlines it into every page's sprite
```

The sprite is inlined on all 11 pages, so its weight is a real decision: tracing
at 300px cost 21.4 KB of path data, 200px costs 12.2 KB and is indistinguishable
at the sizes these are actually used (96px and below).

---

## 3d. Legal pages

`privacy.html`, `terms.html` and `paia.html`, plus a dismissible privacy notice
in the footer chrome.

They are written against **what this site actually does**, which is unusually
little: it sets no cookies and runs no analytics. It does load Google Fonts,
which is a third-party request, and that is disclosed.

The contact form posts to a Cloudflare Pages Function which relays the enquiry
to the ops mailbox through Resend. Resend is therefore an **operator** under
POPIA and the policy names it. Nothing is written to a database. If that
plumbing changes, the "The contact form" block in `page_privacy()` has to change
with it: the policy is only worth anything while it describes the real thing.

**The notice is not a cookie banner.** With no cookies there is nothing to
consent to, and a consent gate would be theatre. It states the position once and
remembers the dismissal in `localStorage`, which is itself disclosed in the
policy.

Under POPIA the head of a private body is the Information Officer until another
person is formally designated and registered with the Information Regulator, so
the policy names the directors in that role and routes to the ops mailbox. That
is accurate by default. **The client still needs to register an Information
Officer with the Regulator**, and to have these pages reviewed by a lawyer:
they are a plain-language draft, not legal advice.

The Regulator's address `enquiries@inforegulator.org.za` was taken off
inforegulator.org.za rather than from memory, and is whitelisted by name in the
validator's email check.

---

## 4. Services: six divisions

Taken from the company profile. `tools/build-site.py` `DIVISIONS` is the machine
copy; this is the human one.

| # | Division | Sub-services |
|---|---|---|
| 01 | Special Investigations | Track and Trace · Vetting · Polygraph Services · Criminal Record Checks · Extortion Cases · Evictions · Kidnap and Ransom |
| 02 | Asset Protection | Bullion Runs · High-Value Assets in Transit |
| 03 | Executive Close Protection | Corporate Close Protection · Special Event Security · Secure Drivers |
| 04 | Mining Security | Illegal Mining Prevention Teams · Riot and Civil Unrest Control · Dedicated Searches · Incident Investigations · Bullion Runs |
| 05 | Guarding and Site Security | Controlled Access · Patrols · Professional Presence |
| 06 | Training | Corporate · Firearm · Riot Control · Security Training |

Guarding is the one division the profile describes only in the capabilities grid,
not in a section of its own. Its three sub-services are a faithful expansion of
that one line, not new claims. Confirm the wording with the client.

Everything from the previous brand that is not in the list above is gone, not
parked: forensic services, standalone polygraph and security divisions, and the
44 unverified services that build was carrying.

---

## 5. Frozen files

`assets/css/styles.css` and `assets/js/main.js` are shared by every page. Change
them deliberately, never as a side effect of a content edit. New visual
treatments go in the stylesheet with a class name, never inline on a page.

Pages are **generated**. Edit `tools/build-site.py` and re-run it; do not
hand-edit the HTML, because the next regenerate overwrites it.

```
python3 tools/build-brand-assets.py   # logo, favicons, favicon.ico, OG card
python3 tools/build-site.py           # 11 pages + sitemap, robots, redirects, headers
python3 tools/validate.py             # must be green before pushing
node   tools/test-contact-function.mjs   # the enquiry endpoint, Resend stubbed
```

`functions/api/contact.js` is the third shared file. It is the only server-side
code in the project and the only path an enquiry travels, so a change there is a
change to whether the business hears from anyone. It reads its credentials from
`env` and nothing else: **no key, of any provider, is ever committed.** The
validator sweeps every tracked file for key-shaped strings and fails the build
on a hit.

### Generated, not hand-written

`build-site.py` emits these too, from the same page list that builds the pages,
so they cannot drift out of sync with the site:

| File | What it is |
|---|---|
| `sitemap.xml` | The 10 indexable pages. The 404 is deliberately excluded. |
| `robots.txt` | Points at the sitemap; hides `assets/brand/` and `tools/`. |
| `404.html` | Full chrome, `noindex`, routes into the six divisions. |
| `_redirects` | The six retired INTEGRI division URLs, 301 to their nearest survivor. |
| `_headers` | Security headers, plus long immutable caching for images only. |

CSS and JS get a week rather than a year: filenames are not content-hashed, and
a stale stylesheet is a broken page where a stale image is just an old picture.

Structured data (`ProfessionalService` JSON-LD) is emitted on the **home page
only**, so search engines get one description of the entity rather than ten
competing copies. It asserts nothing that is not in the company profile: no
rating, no price range, no opening hours, no accreditation.

### Logo geometry

The supplied art is portrait, roughly 3:4. Ship it at its natural aspect: pages
declare the file's **real** intrinsic `width`/`height` (read from the file at
build time, never typed by hand) and the CSS sizes one axis with the other
`auto`.

An earlier build padded the art into a square canvas, so a 42x42 box drew the
figure ~31px wide floating in dead space. Icon files must be square, and get
there by **padding on black**, never by resizing non-square art to a square.

`tools/validate.py` fails the build when a declared aspect does not match the
file's real one, which is the check that would have caught this.

---

## 6. Publication gate: what may not be claimed

The site may state only what the client's own documents support. Everything below
is currently **absent on purpose**. Adding any of it requires the paperwork
first, not a decision that it sounds right.

| Claim | Status |
|---|---|
| **PSIRA registration** | **Not claimed.** The Greyman profile asserts none. The previous brand's site claimed it on all 11 pages. Needs the certificate and number. |
| **Company registration number** | **Not claimed.** The previous entity's CIPC number belongs to a different name and does not transfer. |
| **Accredited firearm training** | **Not claimed.** "Firearm Training" is offered; the word *accredited* needs the accreditation. |
| **24/7 availability** | **Not claimed.** The profile does not say it. |
| Client counts, years in business, headcount, success rates, response times, testimonials | Never, unless supplied in writing. |

The only numbers on the site are **6** (divisions, countable) and the two phone
numbers. `tools/validate.py` fails the build on PSIRA, on a registration-number
pattern, on `24/7`, and on volume and success-rate phrasings.

### Sensitive services

Kidnap and Ransom, Extortion Cases, Riot Control, Illegal Mining Prevention,
Dedicated Searches, Evictions and Firearm Training are described in the
profile's own terms: support, planning, controlled response, taught to a
standard. Do not escalate that language toward force, apprehension, detention or
guaranteed outcomes. These are regulated activities in South Africa and the copy
should stay narrower than the client's capability, not wider.

---

## 7. Still needed from the client

1. PSIRA registration number and certificate, for the company and for officers.
2. Registered company name and CIPC number for Greyman Protection.
3. Firearm training accreditation, if "accredited" is to appear.
4. Confirmation of the Guarding and Site Security wording.
5. The final domain.
6. Whether `ops@greymanprotection.co.za` is live and monitored: every enquiry is
   delivered there and nowhere else, so an unmonitored mailbox loses all of them.
   Also: `RESEND_API_KEY` set as a secret in Cloudflare, and
   `greymanprotection.co.za` verified as a sending domain in Resend. Until both
   are done the form answers honestly that it is not configured, which is better
   than losing enquiries but is not shippable. See README, "The contact form".
7. Registration of an Information Officer with the Information Regulator, and a
   lawyer's review of the three legal pages before relying on them.

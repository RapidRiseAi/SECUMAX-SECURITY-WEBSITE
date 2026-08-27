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

The site still publishes on `integriforensicservices.com`, the previous brand's
domain, at the client's instruction until they move it. It lives in exactly one
place, `DOMAIN` in `tools/build-site.py`, so the move is a one-line change plus a
regenerate.

**Two things depend on it and will break silently when it moves:**

1. Every `rel="canonical"` and `og:url`.
2. Any printed QR code. The previous brand's codes were deleted rather than
   carried over. Do not print a new one until the domain is final.

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
python3 tools/build-brand-assets.py   # logo, favicons, OG card
python3 tools/build-site.py           # all 10 pages
python3 tools/validate.py             # must be green before pushing
```

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
6. Whether `ops@greymanprotection.co.za` is live and monitored: the contact form
   hands off to it via `mailto:`, so an unmonitored mailbox loses every enquiry.
7. An information officer's name, if a privacy notice is added later.

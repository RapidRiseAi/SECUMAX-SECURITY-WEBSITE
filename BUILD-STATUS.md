# INTEGRI — Build Status (internal)

For the design and development team. **Do not send this to the client** — the client-facing
version is `CLIENT-PACK.md`.

| | |
|---|---|
| Pages | 11 |
| Validator | 0 errors, 0 warnings |
| Total weight | ~464 KB |
| Dependencies | none — static HTML/CSS/JS, no build step |
| Branch | `main` |
| Status | **Not public.** Blocked on client input, not on engineering. |

---

## 1. Complete

- Full rebrand from SECUMAX — black / red `#E01B24` / white, Chakra Petch + Barlow.
- One page expanded to eleven: home, about, contact, services hub, seven division pages.
- All SECUMAX photography removed; K9, anti-poaching and mining lines gone.
- Semantic HTML throughout — one `h1` per page, clean heading order, skip link, keyboard-reachable
  nav, `prefers-reduced-motion` honoured.
- Ruan removed from all contact blocks; Etienne and Jacques remain.
- Registered entity and CIPC number in the footer on all 11 pages.
- Validator covering links, sprite ids, CSS class existence, path prefixes, heading structure,
  brand leftovers, and a whitelist of permitted phone numbers and email addresses.

### Architecture

- **`BRAND.md` is the binding contract** — tokens, contact data, division taxonomy, CSS class
  catalogue, path rules, publication gate. Read before touching anything.
- `assets/css/styles.css` is the complete design system and is treated as frozen. Add components
  there and document them; never inline styles in pages.
- Icons are one inline SVG sprite copied verbatim into every page. References are bare
  fragments — `<use href="#i-forensic"/>` — never path-prefixed.
- Path rule: root pages use `assets/…`, `services/` pages use `../assets/…`. Validator enforces it.
- Deploy = publish the repo root. No build command.

---

## 2. Blocked on client input

### 2.1 PSIRA registration status — hard block

Client says certification is still awaited. The site asserts PSIRA registration in **79 places**:

| Page | Mentions |
|---|---|
| `index.html` | 11 |
| `about.html` | 10 |
| `services/guarding.html` | 9 |
| `services/protection.html` | 9 |
| `services/security.html` | 8 |
| `services/specialized.html` | 7 |
| `services/forensic.html` | 6 |
| `services/investigation.html` | 6 |
| `contact.html` | 5 |
| `services/polygraph.html` | 5 |
| `services/index.html` | 3 |

**If registration is still pending, budget half a day.** This is not a find-and-replace: the
claim appears as hero badges, credential cards, footer text, body copy, two meta descriptions
and an `og:description`. Several sentences need rewriting rather than deleting, and the `.creds`
block on home and about is half PSIRA so it needs re-composing.

The same applies to the **32 "accredited firearm training" mentions** if that accreditation also
turns out to be pending.

### 2.2 Director titles contradict CIPC — hard block

CIPC lists one active director: **Anri Coetser**. The site titles **Etienne** and **Jacques** as
"Director" in `index.html`, `about.html` and `contact.html`. We deliberately have not guessed a
replacement title — inventing one repeats the original failure.

Once confirmed: the `.dir-card__role` line in each of the three `.dir-card` blocks, plus the
directors table in `BRAND.md` §4.

### 2.3 The 56 sub-services are unverified — hard block

Written from industry norms, not supplied by the client. Each division page renders its eight as
`.offer` cards with bespoke copy, and the surrounding prose, the "what this covers" intro and
sometimes the FAQ reference the same capability.

**Budget 15–20 minutes per removed line** including knock-on copy. If a division comes back mostly
struck, that page needs a rewrite rather than an edit.

### 2.4 Logo artwork — waiting on a file

The crest in the repo is a hand-authored SVG approximation. The real artwork has been sent twice
as a chat image, which does not produce a file — there is nothing on disk to commit.

**Fastest route:** upload it through the GitHub web UI — repo → `assets/img` → Add file → Upload
files → Commit. Then:

```bash
./tools/use-real-logo.sh assets/img/integri-logo.png
```

Rewires all 56 references across the 11 pages, corrects the favicon MIME type, deletes the
placeholder. Accepts `.png`, `.svg` or `.webp`. Tested end to end on a scratch copy.

Ask for a **simplified shield-and-eagle variant for the favicon** — the full crest has fingerprint
ridges, an investigator figure and a helmet, all illegible below ~32 px.

### 2.5 Address decision — waiting

The CIPC registered office is also the director's residential address. **Deliberately not
published**, and the ID number on the certificate is not recorded in this repo at all.
Publishing a home address for a protection-services firm is the client's decision.

Knock-on: without an address we cannot add `LocalBusiness` JSON-LD or set up a Google Business
Profile — the main local-search lever for this kind of firm.

### 2.6 POPIA privacy notice — waiting on names

The contact form collects name, email and free text. Needs a privacy notice and a registered
Information Officer. The page is ~2 hours to build in the design system, but needs real answers:
Information Officer name and contact, retention period, and who enquiry data is shared with.

No cookie banner needed as things stand — no cookies, no analytics. That changes the moment GA
or a Meta pixel is added.

---

## 3. Queued, not blocked

| Task | Notes | Size |
|---|---|---|
| **Open Graph image** | `og:image` points at an SVG, which most platforms will not render — link previews break. Needs a 1200 × 630 PNG. Design can produce this without client input. | S |
| `sitemap.xml` + `robots.txt` | 11 static URLs | XS |
| Form backend | Currently `mailto:` handoff, no submission record. Needs a client decision on destination. | S |
| 404 page | Not built; should match the design system | XS |
| Favicon set | Blocked on the logo, but sizes and manifest can be scaffolded now | S |
| Hosting + HTTPS | Any static host, output dir is the repo root | S |
| JSON-LD structured data | Blocked — needs address and confirmed numbers | S |

### Known issues we are carrying

- **Crest illegible at favicon size** — needs a simplified variant.
- **Long email wraps awkwardly** in narrow contact cards (46 characters, breaks mid-token on
  small screens). Cosmetic.
- **No analytics** — deliberate; adding any triggers a cookie-notice requirement.
- **Company is weeks old** (registered 16 July 2026). The fabrication ban in `BRAND.md` §1 forbids
  longevity claims — enforce it.

---

## 4. Do not regress these

Deliberate decisions that are easy to undo by accident:

- **No invented statistics.** No client counts, success rates, years in business, headcounts,
  response-time guarantees or testimonials. Only permitted numbers: `7` (divisions) and `24/7`.
  The validator greps for the common patterns.
- **Polygraph framing must not be softened.** The page states it is a credibility assessment
  requiring written informed consent, producing an examiner's opinion rather than proof, and that
  a result alone does not establish misconduct. Never add an accuracy percentage, a
  court-admissibility claim, or anything implying a failed test justifies dismissal.
- **No licence-outcome promise** on firearm training — the Registrar decides, not INTEGRI.
- **Crowd & labour unrest support** stays framed as lawful, defensive, de-escalation-first.
  Never strike-breaking.
- **No ID numbers or residential addresses** anywhere in the repo or on the site.
- **Only two phone numbers exist** — Etienne and Jacques. The validator fails on any other `+27`
  number or any email that is not `ops@`.

---

## 5. Critical path

1. **Client answers the PSIRA question.** Everything is downstream. If pending, half a day to
   strip and rewrite 79 claims before anything ships.
2. **Logo lands as a real file.** Then one command, and design can produce the OG image and
   favicon set.
3. **Service review comes back.** Then scope the copy edits — the largest unknown remaining.
4. **Titles and Information Officer confirmed.** Unblocks the director cards and the privacy notice.

Nothing on the critical path is engineering work. The build is done; it is waiting on facts.

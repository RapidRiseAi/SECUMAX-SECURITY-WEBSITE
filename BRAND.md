# INTEGRI — Build Contract (SINGLE SOURCE OF TRUTH)

> Every page in this repository MUST conform to this document.
> If something is not defined here, copy the pattern from `index.html`.
> **Do not invent new CSS classes, new colours, or new facts.**

---

## 1. Brand

| Field | Value |
|---|---|
| Legal / display name | **INTEGRI Forensic and Protection Services** |
| Wordmark | `INTEGRI` (uppercase, always) |
| Tagline (under wordmark) | `Forensic and Protection Services` |
| Positioning line | Evidence-led investigation. Uncompromising protection. |
| Country | South Africa |
| Website | `https://www.integriforensicandprotectionservices.com` |

### Credentials — the ONLY accreditation claims permitted
- **PSIRA Registered & Compliant** (Private Security Industry Regulatory Authority)
- **Accredited Firearm Training** — "accredited training for responsible citizens"

### 🚫 FABRICATION BAN — read this twice
Do **NOT** write any of the following anywhere on the site:
- Years in operation / "founded in ####" / "since ####"
- Client counts, case counts, success rates, "500+ clients", "98% conviction rate"
- Staff/officer headcounts ("200 officers")
- Awards, ISO numbers, BEE levels, insurance values, PSIRA registration numbers
- Named client logos or testimonials attributed to real people or companies
- Response-time guarantees in minutes

Permitted, non-numeric trust signals only: `PSIRA Registered & Compliant`,
`Accredited Firearm Training`, `24/7 Operations`, `7 Specialised Divisions`,
`National Coverage`, `Court-Ready Reporting`, `Confidential`, `Chain of Custody`.
Stat counters may ONLY use: `7` (divisions), `24/7` (operations). Nothing else.

---

## 2. Colour tokens (CSS variables — already defined in `styles.css`)

Never hard-code a hex value. Use the variable.

```
--red        #E01B24   primary brand red
--red-bright #FF303B   hover / highlight
--red-deep   #8E0E14   depth, gradients
--red-glow   rgba(224,27,36,.35)

--black      #000000   page background
--black-2    #08080A   alternating section background
--panel      #101014   card background
--panel-2    #17171C   raised card / hover
--line       rgba(255,255,255,.09)
--line-red   rgba(224,27,36,.30)

--ink        #FFFFFF   headings
--body       #C9C9D1   body copy
--muted      #8E8E99   secondary / meta
```

`.grad` = red gradient text treatment. Use on ONE emphasis phrase per heading, never a whole heading.

---

## 3. Typography

Loaded once in `<head>` on every page (copy the block from `index.html`):

- **Display / headings** — `Chakra Petch` (500, 600, 700)
- **Body / UI** — `Barlow` (300, 400, 500, 600, 700)
- **Eyebrows / labels** — `Barlow Condensed` (600, 700), uppercase, letterspaced

---

## 4. Contact data — EXACT, copy character for character

**Primary CTA everywhere is EMAIL.** Phone numbers appear in the contact
section / contact page ONLY — never in the header, hero, or footer CTA.

| Field | Value |
|---|---|
| Email | `ops@integriforensicandprotectionservices.com` |
| Email link | `mailto:ops@integriforensicandprotectionservices.com` |

### Directors — contact page + home contact block only

| Name | Role | Phone (display) | `tel:` href | `wa.me` |
|---|---|---|---|---|
| Etienne | Director | `+27 71 118 3257` | `tel:+27711183257` | `https://wa.me/27711183257` |
| Jacques | Director | `+27 67 161 2570` | `tel:+27671612570` | `https://wa.me/27671612570` |
| Ruan | Director | `+27 66 285 6600` | `tel:+27662856600` | `https://wa.me/27662856600` |

Display numbers use non-breaking spaces: `+27&nbsp;71&nbsp;118&nbsp;3257`.

No physical address and no social media accounts have been supplied — **do not invent
either**. Omit those blocks entirely.

---

## 5. Page inventory & file ownership

| File | Page | Owner |
|---|---|---|
| `index.html` | Home | Orchestrator (DONE — canonical pattern) |
| `assets/css/styles.css` | Design system | Orchestrator — **FROZEN** |
| `assets/js/main.js` | Behaviour | Orchestrator — **FROZEN** |
| `assets/img/integri-crest.svg` | Logo | Orchestrator — **FROZEN** |
| `services/index.html` | Services hub | Agent A |
| `services/investigation.html` | Investigation | Agent A |
| `services/forensic.html` | Forensic | Agent A |
| `services/polygraph.html` | Polygraph | Agent B |
| `services/security.html` | Security | Agent B |
| `services/protection.html` | Protection | Agent C |
| `services/guarding.html` | Guarding | Agent C |
| `services/specialized.html` | Specialized | Agent C |
| `about.html` | About | Agent D |
| `contact.html` | Contact | Agent D |

**You may only create/edit the files assigned to you.** Read any other file freely.

---

## 6. Path rules (most common source of breakage)

Let `{B}` = path prefix to repository root.

- Pages at repo root (`index.html`, `about.html`, `contact.html`) → `{B}` is **empty string**
- Pages in `services/` → `{B}` is **`../`**

Apply `{B}` to every asset and internal link:

| Target | From root page | From `services/` page |
|---|---|---|
| Stylesheet | `assets/css/styles.css` | `../assets/css/styles.css` |
| Script | `assets/js/main.js` | `../assets/js/main.js` |
| Crest | `assets/img/integri-crest.svg` | `../assets/img/integri-crest.svg` |
| Home | `index.html` | `../index.html` |
| About | `about.html` | `../about.html` |
| Contact | `contact.html` | `../contact.html` |
| Services hub | `services/index.html` | `index.html` |
| A service page | `services/forensic.html` | `forensic.html` |

---

## 7. The 7 divisions — canonical names, slugs, icons, copy

Icons come from the inline `<svg class="sprite">` block, which you copy verbatim into
every page. Because the sprite is inlined on the page itself, sprite references take
**no `{B}` prefix** — always a bare fragment:

```html
<svg class="ico" aria-hidden="true"><use href="#i-forensic"/></svg>   <!-- correct -->
<svg class="ico" aria-hidden="true"><use href="../#i-forensic"/></svg> <!-- WRONG -->
```

Available sprite ids (nothing else exists — do not invent one):
`#i-investigation` `#i-forensic` `#i-polygraph` `#i-security` `#i-protection`
`#i-guarding` `#i-specialized` `#i-mail` `#i-phone` `#i-whatsapp` `#i-shield-check`
`#i-target` `#i-clock` `#i-globe` `#i-doc` `#i-eye` `#i-scale` `#i-lock-file`
`#i-arrow-r` `#i-users`

| # | Division | File | Sprite id | Blurb (use verbatim on cards) |
|---|---|---|---|---|
| 01 | Investigation Services | `investigation.html` | `#i-investigation` | Discreet, evidence-led enquiry into fraud, misconduct and loss — documented to a standard that survives scrutiny. |
| 02 | Forensic Services | `forensic.html` | `#i-forensic` | Scene-to-courtroom forensic capability: collection, examination and reporting with an unbroken chain of custody. |
| 03 | Polygraph Services | `polygraph.html` | `#i-polygraph` | Structured credibility assessment for screening, incident resolution and internal integrity programmes. |
| 04 | Security Services | `security.html` | `#i-security` | Risk assessment, access control, surveillance systems and the policy framework that holds them together. |
| 05 | Protection Services | `protection.html` | `#i-protection` | Close protection for principals, families and executives — low-profile, professional, planned around the threat. |
| 06 | Guarding Services | `guarding.html` | `#i-guarding` | Vetted, supervised guarding for sites, estates, retail and industry, with real accountability on shift. |
| 07 | Specialized Services | `specialized.html` | `#i-specialized` | Accredited firearm training, escorts, recovery and bespoke operations for requirements that fall outside the standard scope. |

### Sub-services (use these exact lists — do not add or rename)

**01 Investigation Services**
- Corporate & internal investigations
- Fraud & financial crime enquiry
- Surveillance & counter-surveillance
- Background screening & vetting
- Insurance claim investigation
- Asset tracing & due diligence
- Missing persons tracing
- Matrimonial & domestic enquiry

**02 Forensic Services**
- Crime scene processing & documentation
- Fingerprint collection & comparison
- Questioned document examination
- Digital & mobile device forensics
- Forensic auditing
- Evidence handling & chain of custody
- Expert witness testimony
- Court-ready forensic reporting

**03 Polygraph Services**
- Pre-employment screening examinations
- Periodic integrity testing
- Specific-issue (incident) examinations
- Theft & shrinkage investigations
- Disciplinary hearing support
- Internal integrity programmes
- Structured pre-test interviewing
- Documented examination reporting

**04 Security Services**
- Security risk assessments
- Access control & visitor management
- CCTV design, installation & monitoring
- Alarm systems & response coordination
- Perimeter & physical security design
- Control room & monitoring solutions
- Security policy & SOP development
- Security audits & compliance reviews

**05 Protection Services**
- Close protection officers
- Executive & corporate protection
- Family & residential protection
- Secure chauffeur & transport
- Travel risk management & advance work
- Event & dignitary protection
- Threat & vulnerability assessment
- Female close protection officers

**06 Guarding Services**
- Static & site guarding
- Access control officers
- Residential estate guarding
- Retail & commercial guarding
- Construction & industrial site security
- Mobile patrols & guard monitoring
- Reaction & response officers
- Supervision & control room staffing

**07 Specialized Services**
- Accredited firearm training
- Tactical & refresher training
- Valuable goods & cash escorts
- Asset & vehicle recovery
- Loss prevention programmes
- Undercover operative placement
- Crowd & labour unrest support
- Bespoke risk solutions

---

## 8. CSS class catalogue (the API — nothing outside this list exists)

### Layout
`.wrap` · `.section` · `.section--alt` · `.section--tight` · `.section__head` ·
`.section__head--left` · `.eyebrow` · `.section__title` · `.section__sub` · `.grad`

### Header / nav (copy verbatim from `index.html`)
`.site-header` · `.header__inner` · `.brand` · `.brand__mark` · `.brand__text` ·
`.nav-desktop` · `.nav-drop` · `.nav-drop__panel` · `.nav-drop__link` ·
`.header__cta` · `.hamburger` · `.mobile-menu` · `.mobile-menu__panel` ·
`.mm__num` · `.mobile-menu__foot` · `.action-bar` · `.is-active`

### Buttons
`.btn` + one of `.btn--red` `.btn--outline` `.btn--ghost`
+ optional size `.btn--lg` `.btn--sm` `.btn--block`

### Heroes
Home only: `.hero` · `.hero__bg` · `.hero__inner` · `.hero__badges` · `.hero__badge` ·
`.hero__title` · `.hero__line` · `.hero__line-in` · `.hero__lead` · `.hero__actions` · `.hero__crest`

Interior pages: `.page-hero` · `.page-hero__inner` · `.page-hero__title` ·
`.page-hero__lead` · `.breadcrumb` · `.page-hero__meta`

### Components
- Trust strip — `.trust` · `.trust__inner` · `.trust__item`
- Marquee — `.marquee` · `.marquee__track`
- Division cards — `.svc-grid` · `.svc-card` · `.svc-card__num` · `.svc-card__icon` · `.svc-card__title` · `.svc-card__copy` · `.svc-card__list` · `.svc-card__link`
- Offer grid — `.offer-grid` · `.offer` · `.offer__icon` · `.offer__title` · `.offer__copy`
- Checklist — `.checklist` (on `<ul>`, plain `<li>` children)
- Sidebar — `.aside-card` · `.aside-card__title` · `.aside-card__row`
- Detail layout — `.detail` · `.detail__body` · `.detail__aside` · `.prose`
- Process — `.step-list` · `.step` · `.step__num` · `.step__title` · `.step__copy`
- Stats — `.stats` · `.stat` · `.stat__num` · `.stat__label`
- Credentials — `.creds` · `.cred` · `.cred__icon` · `.cred__title` · `.cred__copy`
- Directors — `.dir-grid` · `.dir-card` · `.dir-card__name` · `.dir-card__role` · `.dir-card__row`
- FAQ — `.faq` · `.faq__item` · `.faq__q` · `.faq__a`
- CTA band — `.cta-band` · `.cta-band__inner` · `.cta-band__title` · `.cta-band__copy`
- Contact — `.contact__grid` · `.contact__form` · `.field` · `.form__note` · `.contact-list` · `.contact-item` · `.contact-item__label` · `.contact-item__value`
- Footer — `.site-footer` · `.footer__grid` · `.footer__col` · `.footer__brand` · `.footer__links` · `.footer__bottom`
- Icons — `.ico` · `.ico--lg`

### Animation (JS-driven, already wired)
Add `.reveal` to any element to fade it up on scroll.
Variants: `.reveal--left` `.reveal--right` `.reveal--scale`.
Stagger with inline `style="--d:.15s"`. **Never add `.in` manually.**

---

## 9. Required page skeleton

Every page follows this order. Header, sprite block and footer are **copied
verbatim** from `index.html` with only `{B}` prefixes and the `.is-active` nav
class changed.

```
<!DOCTYPE html> / <html lang="en">
<head>  … see §10 …  </head>
<body>
  <div class="scroll-progress" id="scrollProgress" aria-hidden="true"></div>
  <a class="skip-link" href="#main">Skip to content</a>
  <svg class="sprite" … >   ← icon sprite, copied verbatim
  <header class="site-header" id="siteHeader"> … </header>
  <div class="mobile-menu" id="mobileMenu" aria-hidden="true"> … </div>
  <main id="main">
     … page content …
     <section class="cta-band"> … </section>   ← last section on every page
  </main>
  <footer class="site-footer"> … </footer>
  <div class="action-bar"> … </div>
  <button class="to-top" id="toTop" …>
  <script src="{B}assets/js/main.js" defer></script>
</body>
```

## 10. `<head>` requirements

Per page you must set: `<title>`, `<meta name="description">`, `og:title`,
`og:description`, `og:url`, and `<link rel="canonical">`.

- Title format: `<Page Name> | INTEGRI Forensic and Protection Services`
  (home is `INTEGRI Forensic and Protection Services | …`)
- Description: 140–160 characters, mentions South Africa and PSIRA where natural.
- Canonical: `https://www.integriforensicandprotectionservices.com/<path>`
- `<meta name="theme-color" content="#000000">`
- Favicon: `<link rel="icon" href="{B}assets/img/integri-crest.svg" type="image/svg+xml">`

Copy the whole block from `index.html` and change only the page-specific values.

---

## 11. Quality bar

- Semantic HTML — one `<h1>` per page, headings in order, real `<section>`/`<nav>`.
- Every `<a>` resolves to a file that exists. Every icon `<use href>` matches a sprite id.
- All interactive controls keyboard reachable; `aria-label` on icon-only controls.
- No inline `<style>` blocks. No inline `style=` except the `--d` stagger variable.
- No external requests except Google Fonts.
- British/South African English: *organised, specialised, programme, licence (noun)*.
  **Exception:** the division is named "Specialized Services" (as per the brand mark) —
  keep that exact spelling for the division name and file name only.
- Copy tone: precise, calm, professional. No hype, no "unleash", no emoji.

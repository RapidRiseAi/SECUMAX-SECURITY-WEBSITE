# INTEGRI — Pre-Launch Checklist

Everything still outstanding before this site should go live publicly.

Two parts: **the images we need**, and **the facts we need to confirm** so that nothing
on the site is a claim INTEGRI cannot stand behind.

> This is a practical checklist written from what is currently on the site. It is not
> legal advice. Before launch, have a South African attorney or compliance consultant
> confirm the regulated claims (PSIRA, firearm training, polygraph, POPIA).

---

# PART 1 — IMAGES NEEDED

## 1.1 Logo files — blocking

The site currently ships a **hand-drawn SVG approximation** of the crest at
`assets/img/integri-crest.svg`. It is not the real artwork. It was built by eye because
the logo files were shared in chat, which does not put a file in the repository — there
was nothing to commit.

**To fix it takes one command.** Put the file anywhere on the machine and run:

```bash
./tools/use-real-logo.sh ~/Downloads/integri-logo.png
```

That copies it into `assets/img/`, rewires all 56 references across the 11 pages
(favicon, apple-touch-icon, og:image, header mark, footer mark, hero watermark), fixes
the favicon MIME type and deletes the placeholder.

| # | Asset | Spec | Used for | Priority |
|---|---|---|---|---|
| 1 | **Crest only**, transparent background | PNG, square, ≥ 1024×1024 | Header, footer, favicon, hero watermark | **Blocking** |
| 2 | **Vector source** if it exists | `.svg`, `.ai` or `.eps` | Sharpest at every size; best possible favicon | **Strongly preferred** |
| 3 | **Full lockup** — crest + INTEGRI + tagline | PNG transparent, ≥ 2000px wide | Documents, proposals, email signatures | High |
| 4 | **Simplified mark for small sizes** | Square, legible at 16 px | Favicon and browser tab | Medium |

The current crest has a lot of fine detail (fingerprint ridges, the investigator, the
helmet). That detail disappears below about 32 px and turns to mush in a browser tab. If
there is a simplified version — the shield and eagle alone, no quadrant icons — it will
look considerably better as the favicon.

## 1.2 Social share image — high priority

When anyone pastes a link to this site into WhatsApp, LinkedIn, Facebook or Slack, the
preview card pulls `og:image`. That currently points at the SVG crest, and **most
platforms do not render SVG for link previews** — so the preview will show a blank box.

| Asset | Spec |
|---|---|
| Open Graph image | **PNG or JPG, exactly 1200 × 630 px** |

Design: black background, crest, "INTEGRI" and the tagline, and possibly
"PSIRA Registered". Keep text well inside the middle 80% — the edges get cropped.

Given how much business in South Africa moves through WhatsApp, this one matters more
than it looks.

## 1.3 Division photography — optional

The site is deliberately photo-free and works well that way. Photographs would add
credibility, but **only real ones**. Stock photos of American SWAT teams do more harm
than good, and the previous SECUMAX images have all been removed.

If INTEGRI wants photography, the useful set is one landscape image per division:

| Division | What the shot should show |
|---|---|
| Investigation | A case file, a surveillance setup, a workstation — not a person in a trench coat |
| Forensic | Gloved hands lifting a print, evidence bags being sealed and labelled |
| Polygraph | The examination room and instrumentation, chairs set up |
| Security | A control room, a monitor wall, an access-control point |
| Protection | A detail working — **faces obscured or angled away** |
| Guarding | An officer in INTEGRI uniform at a gate or site |
| Specialized | The training range, safe handling instruction in progress |

**Rules for these photos:**
- Must be INTEGRI's own, or licensed stock with a commercial licence on file.
- Written consent from every identifiable person, including staff.
- Never show a real client's site, premises, vehicles or signage without written permission.
- Never show anything that identifies a real case, docket or subject.
- Protection and investigation work is confidential by nature — obscure faces.

Specs: landscape 3:2, at least 1600 px wide, JPG. Layouts have image slots ready.

## 1.4 Trust and proof — optional but valuable

| Asset | Notes |
|---|---|
| PSIRA logo | Confirm permitted usage with PSIRA before displaying it |
| Firearm training accreditation logo | Same — only if the accrediting body permits it |
| Director portraits — Etienne, Jacques | Would replace the current initial-letter avatars |
| Uniform / vehicle / branded kit | Shows a real operation rather than a website |

---

# PART 2 — DETAILS NEEDED BEFORE PUBLISHING

## 2.1 ⚠️ The most important item on this page

**The seven divisions are real — they come from INTEGRI's own brand mark. The list of
sub-services underneath each one was written by me.**

There are 56 of them, four to eight per division, and they are the standard offerings of
a South African firm in each field. They were *not* supplied by INTEGRI. Some will be
exactly right. Some may be things INTEGRI does not do, cannot currently staff, or is not
licensed to perform.

**Every one of the 56 has to be confirmed or struck out before launch.** Advertising a
service the business cannot actually deliver is the single largest false-advertising
exposure on this site, and under the Consumer Protection Act 68 of 2008 a misleading
representation about services is actionable regardless of intent.

The full list is in `BRAND.md` §7. Go through it and mark each line **keep / remove /
reword**. Send it back and the pages will be updated to match.

Watch these especially — each implies a specific competence or credential:

| Claim on the site | What has to be true |
|---|---|
| Fingerprint collection & comparison | Someone competent to do comparison work, not just lifting |
| Expert witness testimony | Someone a court would actually accept as an expert |
| Questioned document examination | A trained document examiner |
| Digital & mobile device forensics | Forensic tooling and a defensible acquisition process |
| Forensic auditing | Appropriate financial/audit qualification |
| Polygraph examinations | Trained examiners — see 2.4 |
| CCTV design, installation & monitoring | Installation capability, and any electrical compliance |
| Accredited firearm training | Live accreditation — see 2.3 |
| Undercover operative placement | Capability, and a lawful basis for the deployment |
| Female close protection officers | Actually on the team |

## 2.2 Legal identifiers — currently missing entirely

The site names no legal entity. For a South African security business this is both a
trust problem and a compliance problem.

| Detail | Why it is needed |
|---|---|
| **PSIRA registration number** | The site says "PSIRA Registered & Compliant" with no number. A number makes the claim checkable; without one it is just an assertion. Security providers are required to disclose registration. |
| **Registered company name** | e.g. "Integri Forensic and Protection Services (Pty) Ltd" — the trading name alone is not the legal entity |
| **CIPC company registration number** | Format `20XX/XXXXXX/07`. Belongs in the footer. |
| **VAT number** | If registered for VAT |
| **Registered physical address** | Currently absent. PSIRA-registered businesses have a registered address, and clients look for one. |
| **Postal address** | If different |
| **Directors' full legal names** | The site shows "Etienne" and "Jacques" only |

Are individual officers PSIRA-registered as well as the business? Both matter, and they
are separate registrations.

## 2.3 Firearm training — a regulated claim

The site states **"Accredited firearm training — accredited training for responsible
citizens"**, taken from INTEGRI's own brand mark.

In South Africa firearm competency training is regulated under the Firearms Control Act
60 of 2000, and training providers are accredited through **SAPS** and typically
**SASSETA** against specific unit standards.

Confirm before launch:

- Who the accrediting body is, and the accreditation number
- Which unit standards / competency types are covered — handgun, shotgun, rifle, self-defence, business purposes
- Whether accreditation is current, and its expiry date
- Whether INTEGRI trains only, or also assists with the licence application
- Whether the training is delivered in-house or through an accredited partner

**On the site right now there is no promise that a learner will obtain a licence** — that
decision belongs to the Registrar, not INTEGRI, and it must stay that way. Do not let
anyone add wording that implies a guaranteed licence outcome.

## 2.4 Polygraph — the other regulated claim

The polygraph page was written carefully and deliberately. It states that an examination
is a structured credibility assessment, that it requires written informed consent, that
it produces an examiner's opinion rather than proof, and that a result alone does not
establish misconduct. **That framing should not be softened**, because polygraph evidence
carries very limited weight in South African labour law and CCMA proceedings, and
overstating it creates real exposure for INTEGRI and its clients.

Confirm:

- Examiners' training and qualifications, and any professional association membership
- Instrumentation used
- That the consent process is documented and consent can be withdrawn
- That the site's framing matches how INTEGRI actually presents results to clients

**Never add to this page:** an accuracy percentage, any claim of court admissibility, or
any suggestion that a failed test is grounds for dismissal on its own.

## 2.5 Claims already on the site that need a yes or no

Each of these is currently published. Confirm each one is true, or it comes off.

| Claim | Where | Confirm |
|---|---|---|
| "PSIRA Registered & Compliant" | Every page — badges, footer, credentials | Registration is current and in good standing |
| "24/7 Operations" / "Operational 24 hours a day" | Home, contact, badges | Someone genuinely answers at 03:00 on a Sunday |
| "National coverage" / "across South Africa" | Home, footer, about | INTEGRI can actually service all provinces — if it is really Gauteng plus travel, say that instead |
| "Seven specialised divisions" | Throughout | All seven are staffed and operating today, not aspirational |
| "Court-ready reporting" | Home, forensic, investigation | Reports have actually been produced to that standard |
| "Chain of custody" | Forensic, home | A documented procedure exists |
| Email reaches "the whole operations team" | Contact | `ops@` is a real, monitored mailbox |

Anything not yet true is better phrased as what INTEGRI *does* offer. An honest smaller
claim is worth more than a large one that a client can disprove on the first engagement.

## 2.6 Legally required pages that do not exist yet

The contact form collects a name, an email address and a free-text message. That is
personal information, which brings **POPIA** (Protection of Personal Information Act 4 of
2013) into scope.

| Missing | Why |
|---|---|
| **Privacy / POPIA notice** | Required once personal information is collected. Must state what is collected, why, how long it is kept, who it is shared with, and how someone requests deletion. |
| **Information Officer** | Under POPIA the Information Officer must be registered with the Information Regulator. Usually a director. |
| **Consent line on the form** | A checkbox or a line of text confirming the enquirer agrees to their details being used to respond |
| **Terms of use / terms of engagement** | Standard for a professional services firm |
| **Cookie notice** | Not needed as things stand — the site sets no cookies and runs no analytics. If Google Analytics or a Meta pixel is added later, this becomes required. |

Say the word and these pages get built to match the rest of the site — the privacy notice
needs INTEGRI's answers on retention periods and the Information Officer's name.

## 2.7 Operational details worth adding

| Detail | Value |
|---|---|
| Office hours vs. emergency line | "24/7" is currently unqualified — most firms mean 24/7 emergency, office hours for admin |
| Service areas by province | Better for search than "national" and more honest |
| Professional indemnity / public liability cover | Corporate clients ask before appointing |
| B-BBEE level | Frequently required for tenders and corporate procurement |
| Bank details / payment terms | Not for the website — for the proposal template |
| Individual email addresses | Currently everything routes to `ops@` |
| Social media accounts | None supplied, so none are linked. LinkedIn in particular is worth having. |
| Google Business Profile | Needs a physical address; drives local search |

## 2.8 Technical items before launch

- [ ] Confirm `integriforensicandprotectionservices.com` is registered and controlled by INTEGRI
- [ ] Confirm `ops@integriforensicandprotectionservices.com` exists and is monitored
- [ ] Point the domain at the host and enable HTTPS
- [ ] Decide whether the enquiry form should post to a real endpoint — it currently opens the visitor's own mail client, so there is no record of submissions on INTEGRI's side
- [ ] Add `sitemap.xml` and `robots.txt`
- [ ] Add JSON-LD `LocalBusiness` structured data — needs the address and phone numbers
- [ ] Submit to Google Search Console

---

## What to send back first

Three things unblock the most:

1. **The logo file** — highest impact, takes seconds, fixes the crest and favicon everywhere.
2. **The 56 sub-services in `BRAND.md` §7, marked keep / remove / reword** — this is the false-advertising risk and it is the one thing only INTEGRI can answer.
3. **PSIRA number, registered company name and CIPC number** — turns the compliance claim from an assertion into something a client can verify.

Everything else can follow.

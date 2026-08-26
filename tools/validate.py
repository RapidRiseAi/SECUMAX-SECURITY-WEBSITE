#!/usr/bin/env python3
"""Validate the Greyman Protection static site: links, sprite ids, CSS classes, brand hygiene."""
import os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []
parked_counts = {}

def rel(p): return os.path.relpath(p, ROOT)

# ---------- gather pages ----------
pages = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "assets")]
    for f in filenames:
        if f.endswith(".html"):
            pages.append(os.path.join(dirpath, f))
pages.sort()

# ---------- known CSS classes ----------
css = open(os.path.join(ROOT, "assets/css/styles.css"), encoding="utf-8").read()
css_classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", css))

STATE_CLASSES = {"in", "open", "scrolled", "show", "ok", "err", "is-active", "sprite", "grad"}

for page in pages:
    raw = open(page, encoding="utf-8").read()
    # Services on hold are commented out pending client verification (SERVICE-STATUS.md).
    # Strip comments before checking, so parked markup is not validated as live markup.
    src = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    P = rel(page)
    base = os.path.dirname(page)

    parked = len(re.findall(r"PENDING VERIFICATION", raw))
    if parked:
        parked_counts[P] = parked

    # ---- 1. internal links resolve ----
    for href in re.findall(r'href="([^"]+)"', src):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        resolved = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(resolved):
            errors.append(f"{P}: broken link -> {href}")

    # ---- 2. sprite <use> ids exist on the page ----
    defined = set(re.findall(r'<symbol id="([^"]+)"', src))
    for used in re.findall(r'<use href="([^"]+)"', src):
        if not used.startswith("#"):
            errors.append(f"{P}: sprite ref must be a bare fragment, got {used}")
        elif used[1:] not in defined:
            errors.append(f"{P}: <use {used}> has no matching <symbol>")

    # ---- 3. every class used exists in CSS ----
    for attr in re.findall(r'class="([^"]+)"', src):
        for cls in attr.split():
            if cls in STATE_CLASSES or cls in css_classes:
                continue
            errors.append(f"{P}: class '{cls}' is not defined in styles.css")

    # ---- 4. structure ----
    n_h1 = len(re.findall(r"<h1[ >]", src))
    if n_h1 != 1:
        errors.append(f"{P}: expected exactly 1 <h1>, found {n_h1}")
    if "<style" in src:
        errors.append(f"{P}: contains an inline <style> block")
    for st in re.findall(r'style="([^"]*)"', src):
        if not re.fullmatch(r"\s*(--d\s*:\s*[.\d]+s\s*;?\s*|--i\s*:\s*\d+\s*;?\s*)+", st):
            warnings.append(f"{P}: inline style beyond --d/--i stagger: style=\"{st}\"")

    # ---- 5. required head/chrome ----
    for needle, label in [
        ('rel="canonical"', "canonical link"),
        ('name="description"', "meta description"),
        ('property="og:title"', "og:title"),
        ("assets/css/styles.css", "stylesheet"),
        ("assets/js/main.js", "script"),
        ('id="siteHeader"', "header"),
        ('id="mobileMenu"', "mobile drawer"),
        ("site-footer", "footer"),
        ('class="action-bar"', "mobile action bar"),
        ('id="toTop"', "to-top button"),
        ('class="skip-link"', "skip link"),
    ]:
        if needle not in src:
            errors.append(f"{P}: missing {label} ({needle})")

    # ---- 5b. absolute URLs must match what the host actually serves ----
    # The production host serves extensionless URLs and 307s every .html away
    # (/contact.html -> /contact, verified against the live site). A canonical or
    # og:url ending in .html therefore points at a URL that redirects, which
    # tells crawlers the authoritative page is one the server refuses to serve.
    # Internal relative hrefs are deliberately NOT checked: they stay .html so
    # the repo works on a plain file server and in local dev.
    for attr, url in re.findall(
            r'(rel="canonical" href|property="og:url" content)="([^"]+)"', src):
        label = "canonical" if "canonical" in attr else "og:url"
        if url.endswith(".html"):
            errors.append(f"{P}: {label} ends in .html but the host redirects those -> {url}")
        if not url.startswith("https://www.integriforensicservices.com"):
            errors.append(f"{P}: {label} is not on the canonical host -> {url}")

    # ---- 6. correct relative prefix ----
    depth = 0 if os.path.dirname(page) == ROOT else 1
    if depth == 1:
        if 'href="assets/' in src or 'src="assets/' in src:
            errors.append(f"{P}: uses root-relative 'assets/' but needs '../assets/'")
    else:
        if "../assets/" in src:
            errors.append(f"{P}: uses '../assets/' but is at the repo root")

    # ---- 7. brand hygiene: no leftovers, no fabrication ----
    # The canonical host is still INTEGRI's until the client moves the domain,
    # so strip absolute self-URLs before the brand sweep or every page reports
    # a false leftover.
    src_copy = src.replace("https://www.integriforensicservices.com", "https://SELF")
    for pat, msg in [
        (r"SECUMAX|secumax", "leftover SECUMAX branding"),
        (r"\bINTEGRI\b(?!\w)|Integri(?!ty)", "leftover INTEGRI branding in copy"),
        (r"\bK9\b|\bK-9\b", "leftover K9 reference"),
        (r"anti-poach|Anti-Poach", "leftover anti-poaching reference"),
        (r"#d4af37|#f3ca25|#066aab|#E01B24|#FF303B|\bgold\b", "leftover pre-Greyman brand token"),
        (r"Abril Fatface|Space Grotesk", "leftover SECUMAX font"),
        (r"btn--red|var\(--red", "leftover red palette token"),
        # PSIRA and a company registration number are regulatory claims. The
        # Greyman company profile asserts neither, and INTEGRI's registration
        # does not carry over to a different trading name. Publishing either
        # without the client's paperwork is a false claim, not a copy choice.
        (r"PSIRA", "PSIRA claim with no supporting certificate on file"),
        (r"\b\d{4}/\d{6}/\d{2}\b", "company registration number not verified for Greyman"),
        (r"24/7", "availability claim the company profile does not make"),
        (r"\d+\+\s*(clients|cases|years|officers)", "fabricated volume claim"),
        (r"(?<![/\d])(19|20)\d{2}(?![/\d])", "possible fabricated year"),
        (r"\b\d{1,3}(\.\d+)?%\s*(accura|success|convict)", "fabricated success/accuracy rate"),
        (r"years of (combined )?experience", "fabricated experience claim"),
        (r"lorem ipsum", "placeholder text"),
        (r"greymanprotection\.com\b", "profile says .com but the live mailbox is .co.za"),
    ]:
        for m in re.finditer(pat, src_copy, re.IGNORECASE):
            ctx = src_copy[max(0, m.start() - 45): m.end() + 45].replace("\n", " ")
            # the footer copyright year is legitimate
            if "possible fabricated year" in msg and "data-year" in ctx:
                continue
            warnings.append(f"{P}: {msg} -> …{ctx.strip()}…")

    # ---- 8. contact data exactness ----
    for bad in re.findall(r"\+27[\s\d&nbsp;]{8,}", src):
        digits = re.sub(r"\D", "", bad)
        if digits and digits not in ("27711183257", "27671612570"):
            errors.append(f"{P}: unknown phone number -> {bad.strip()}")
    for mail in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", src):
        if mail != "ops@greymanprotection.co.za":
            errors.append(f"{P}: unknown email address -> {mail}")

# ---------- unreferenced assets ----------
# assets/brand/ holds master artwork, not web assets — excluded.
# The web manifest also references icons, so it counts as a referrer.
referrers = [open(p, encoding="utf-8").read() for p in pages]
manifest = os.path.join(ROOT, "site.webmanifest")
if os.path.exists(manifest):
    referrers.append(open(manifest, encoding="utf-8").read())
all_refs = "\n".join(referrers)
for dirpath, _, filenames in os.walk(os.path.join(ROOT, "assets")):
    if os.path.relpath(dirpath, ROOT).startswith("assets/brand"):
        continue
    for f in filenames:
        if f not in all_refs:
            warnings.append(f"asset never referenced: {rel(os.path.join(dirpath, f))}")

# ---------- shipped assets: CSS and JS are part of the site too ----------
# The domain sweep once missed main.js, leaving the contact form pointing at a
# dead mailbox. Check every shipped file, not just the pages.
for rel_path in ("assets/css/styles.css", "assets/js/main.js", "site.webmanifest"):
    fp = os.path.join(ROOT, rel_path)
    if not os.path.exists(fp):
        continue
    body = open(fp, encoding="utf-8").read()
    if "ops@integriforensicservices" in body:
        errors.append(f"{rel_path}: superseded INTEGRI mailbox, use ops@greymanprotection.co.za")
    if "\u2014" in body:
        errors.append(f"{rel_path}: em dash present ({body.count(chr(8212))}) — the site is em-dash free")

# ---------- no em dashes anywhere in the pages ----------
for page in pages:
    body = open(page, encoding="utf-8").read()
    n = body.count("\u2014")
    if n:
        errors.append(f"{rel(page)}: {n} em dash(es) — the site is em-dash free")

# ---------- report ----------
if parked_counts:
    total = sum(parked_counts.values())
    print(f"Services parked pending verification: {total}")
    for k, v in sorted(parked_counts.items()):
        print(f"   {k}: {v}")
    print()
print(f"Checked {len(pages)} pages:")
for p in pages:
    print(f"  - {rel(p)}")
print()
if errors:
    print(f"❌ {len(errors)} ERROR(S)")
    for e in errors:
        print("   " + e)
else:
    print("✅ no errors")
print()
if warnings:
    print(f"⚠️  {len(warnings)} warning(s)")
    for w in warnings:
        print("   " + w)
else:
    print("✅ no warnings")

sys.exit(1 if errors else 0)

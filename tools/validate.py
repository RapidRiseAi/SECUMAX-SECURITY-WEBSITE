#!/usr/bin/env python3
"""Validate the Greyman Protection static site: links, sprite ids, CSS classes, brand hygiene."""
import json, os, re, sys
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
        if not url.startswith("https://www.greymanprotection.co.za"):
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
    # Strip absolute self-URLs before the brand sweep so the site's own domain
    # never reads as a leftover from a previous brand.
    src_copy = src.replace("https://www.greymanprotection.co.za", "https://SELF")
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
        (r"-for-light\.png|-on-white\.png",
         "light-ground logo variant on a dark site: it will be invisible"),
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
            # A year is only suspicious as an unsupported claim about the
            # business. These are not that: the footer copyright, a statute
            # citation ("...Act, 2013"), and the legal pages' review stamp.
            if "possible fabricated year" in msg and (
                    "data-year" in ctx
                    or re.search(r"Act,\s*(19|20)\d{2}", ctx)
                    or "legal__stamp" in ctx
                    or "Last reviewed" in ctx):
                continue
            warnings.append(f"{P}: {msg} -> …{ctx.strip()}…")

    # ---- 8. contact data exactness ----
    for bad in re.findall(r"\+27[\s\d&nbsp;]{8,}", src):
        digits = re.sub(r"\D", "", bad)
        if digits and digits not in ("27711183257", "27671612570"):
            errors.append(f"{P}: unknown phone number -> {bad.strip()}")
    for mail in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", src):
        # The Information Regulator's published address, verified on
        # inforegulator.org.za. Whitelisted by name rather than by loosening
        # the check, which exists to catch a stale mailbox shipping to prod.
        if mail not in ("ops@greymanprotection.co.za",
                        "enquiries@inforegulator.org.za"):
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
    if "integriforensicservices" in body:
        errors.append(f"{rel_path}: superseded INTEGRI mailbox, use ops@greymanprotection.co.za")
    if "\u2014" in body:
        errors.append(f"{rel_path}: em dash present ({body.count(chr(8212))}) — the site is em-dash free")

# ---------- no em dashes anywhere in the pages ----------
for page in pages:
    body = open(page, encoding="utf-8").read()
    n = body.count("\u2014")
    if n:
        errors.append(f"{rel(page)}: {n} em dash(es) — the site is em-dash free")

# ---------- production files ----------
# sitemap, robots, redirects and icons rot silently: nothing on the page breaks
# when they go stale, so nothing tells you. Check them here.
def _read(rel):
    fp = os.path.join(ROOT, rel)
    return open(fp, encoding="utf-8").read() if os.path.exists(fp) else None


sm = _read("sitemap.xml")
if sm is None:
    errors.append("sitemap.xml is missing")
else:
    listed = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    for page in pages:
        body = open(page, encoding="utf-8").read()
        m = re.search(r'rel="canonical" href="([^"]+)"', body)
        if not m:
            continue
        canon, P = m.group(1), rel(page)
        # 404 must never be advertised for indexing
        if P == "404.html":
            if canon in listed:
                errors.append("sitemap.xml lists the 404 page")
            if 'content="noindex' not in body:
                errors.append("404.html must be noindex")
        elif canon not in listed:
            errors.append(f"sitemap.xml is missing {P} ({canon})")
    for loc in listed:
        if loc.endswith(".html"):
            errors.append(f"sitemap.xml lists a .html URL the host redirects away: {loc}")

rb = _read("robots.txt")
if rb is None:
    errors.append("robots.txt is missing")
elif "sitemap.xml" not in rb.lower():
    errors.append("robots.txt does not point at the sitemap")

rd = _read("_redirects")
if rd is None:
    errors.append("_redirects is missing")
else:
    for line in rd.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            errors.append(f"_redirects: cannot parse -> {line}")
            continue
        src, dest = parts[0], parts[1]
        target = dest.lstrip("/")
        candidates = [target, target + ".html", os.path.join(target, "index.html")]
        if not any(os.path.exists(os.path.join(ROOT, c)) for c in candidates):
            errors.append(f"_redirects: {src} points at a missing page -> {dest}")
        if src.lstrip("/").split("#")[0] in ("", "index.html"):
            errors.append(f"_redirects: refusing to redirect the home page -> {line}")

if _read("_headers") is None:
    errors.append("_headers is missing")
if not os.path.exists(os.path.join(ROOT, "favicon.ico")):
    errors.append("favicon.ico is missing from the repo root")

# every shipped <img> must declare the file's real intrinsic size, or the
# reserved box is the wrong shape and the layout shifts when the art loads
from PIL import Image as _Im
for page in pages:
    body = open(page, encoding="utf-8").read()
    P = rel(page)
    for tag in re.findall(r"<img[^>]*>", body):
        src_m = re.search(r'src="([^"]+)"', tag)
        w_m = re.search(r'width="(\d+)"', tag)
        h_m = re.search(r'height="(\d+)"', tag)
        if not src_m:
            continue
        if not (w_m and h_m):
            errors.append(f"{P}: <img> without width/height -> {src_m.group(1)}")
            continue
        fp = os.path.normpath(os.path.join(os.path.dirname(page), src_m.group(1)))
        if not os.path.exists(fp):
            continue
        rw, rh = _Im.open(fp).size
        dw, dh = int(w_m.group(1)), int(h_m.group(1))
        if abs(dw / dh - rw / rh) > 0.01:
            errors.append(f"{P}: {os.path.basename(fp)} declared {dw}x{dh} "
                          f"(aspect {dw/dh:.3f}) but the file is {rw}x{rh} "
                          f"(aspect {rw/rh:.3f}); the image will be distorted "
                          f"or the reserved box will be wrong")

# ---------- the contact form and its endpoint must agree ----------
# Three files have to say the same thing: the form's action, the function that
# answers it, and the mailbox it delivers to. They live apart, so check them
# together. A form posting at a path with no function behind it looks fine in
# the browser until someone actually sends an enquiry.
FN = os.path.join(ROOT, "worker", "contact.js")
ENTRY = os.path.join(ROOT, "worker", "index.js")
contact_html = os.path.join(ROOT, "contact.html")
if os.path.exists(contact_html):
    body = open(contact_html, encoding="utf-8").read()
    m = re.search(r'<form[^>]*id="contactForm"[^>]*>', body)
    if not m:
        errors.append("contact.html: the enquiry form is gone")
    else:
        tag = m.group(0)
        am = re.search(r'action="([^"]+)"', tag)
        if not am:
            errors.append("contact.html: the form has no action, so it cannot "
                          "post without JavaScript")
        elif am.group(1) != "/api/contact":
            errors.append(f"contact.html: form posts to {am.group(1)} but the "
                          f"function is at /api/contact")
        if 'method="post"' not in tag:
            errors.append("contact.html: the form is not method=post")
        for needle, label in [('name="company"', "honeypot field"),
                              ('id="formTs"', "timestamp field"),
                              ('id="formNote"', "status line"),
                              ('id="formSubmit"', "submit button")]:
            if needle not in body:
                errors.append(f"contact.html: missing {label} ({needle})")

if not os.path.exists(FN):
    errors.append("worker/contact.js is missing: the form would post into the "
                  "404 page")
else:
    fn = open(FN, encoding="utf-8").read()
    if "ops@greymanprotection.co.za" not in fn:
        errors.append("worker/contact.js: does not deliver to the ops mailbox")
    if "env.RESEND_API_KEY" not in fn:
        errors.append("worker/contact.js: the API key must come from env")
    if "—" in fn:
        errors.append("worker/contact.js: em dash present")

# ---------- the platform config must actually mount the handler ----------
# The first version of this endpoint was written as a Pages Function under
# `functions/`. This project is a Cloudflare Worker with static assets, where
# that directory means nothing: the build failed, and had it not failed the
# endpoint would simply never have been reached. The mounting is now explicit,
# so check it rather than trusting a convention that does not apply here.
if os.path.exists(os.path.join(ROOT, "functions")):
    errors.append("a functions/ directory is back. That is a Cloudflare PAGES "
                  "convention and does nothing on this Workers project; routing "
                  "belongs in worker/index.js and wrangler.jsonc.")

WRANGLER = os.path.join(ROOT, "wrangler.jsonc")
if not os.path.exists(WRANGLER):
    errors.append("wrangler.jsonc is missing: `wrangler versions upload` has no "
                  "entry point and the build fails outright")
else:
    # Strip // comments so the JSONC parses. Naive on purpose: no string in this
    # file contains a slash pair, and a parse failure is itself an error worth
    # reporting rather than working around.
    raw = open(WRANGLER, encoding="utf-8").read()
    stripped = re.sub(r"^\s*//.*$", "", raw, flags=re.M)
    try:
        cfg = json.loads(stripped)
    except json.JSONDecodeError as e:
        cfg = None
        errors.append(f"wrangler.jsonc does not parse: {e}")
    if cfg:
        entry = cfg.get("main")
        if not entry:
            errors.append("wrangler.jsonc: no `main`, so the Worker is never built")
        elif not os.path.exists(os.path.join(ROOT, entry)):
            errors.append(f"wrangler.jsonc: main points at {entry}, which does not exist")
        a = cfg.get("assets") or {}
        if a.get("directory") != ".":
            errors.append("wrangler.jsonc: assets.directory must be '.', the repo "
                          f"root is the deployable output (got {a.get('directory')!r})")
        if not a.get("binding"):
            errors.append("wrangler.jsonc: assets needs a binding, or the Worker "
                          "cannot fall back to the static site")
        # The live site serves /contact from contact.html and 307s /contact.html
        # away. Every canonical on the site assumes it.
        if a.get("html_handling") != "auto-trailing-slash":
            errors.append("wrangler.jsonc: html_handling must be "
                          "'auto-trailing-slash' or every URL moves")
        if a.get("not_found_handling") != "404-page":
            errors.append("wrangler.jsonc: not_found_handling must be '404-page', "
                          "or the branded 404.html is built and never served")
        first = a.get("run_worker_first")
        if not (isinstance(first, list) and any(p.startswith("/api") for p in first)):
            errors.append("wrangler.jsonc: run_worker_first must cover /api/*, so "
                          "the enquiry endpoint reaches the Worker")

if not os.path.exists(ENTRY):
    errors.append("worker/index.js is missing: nothing routes /api/contact")
else:
    entry_src = open(ENTRY, encoding="utf-8").read()
    if "/api/contact" not in entry_src:
        errors.append("worker/index.js does not route /api/contact")
    if "env.ASSETS.fetch" not in entry_src:
        errors.append("worker/index.js never falls back to ASSETS, so every page "
                      "on the site would 404")

# ---------- .assetsignore must not exclude anything the site links to ----------
# The asset directory is the repo root, so this file decides what is public. Get
# a pattern slightly wrong and the stylesheet stops being uploaded, which is a
# fully broken site that still builds green everywhere else.
AI = os.path.join(ROOT, ".assetsignore")
if not os.path.exists(AI):
    warnings.append(".assetsignore is missing: the build tools, the brand "
                    "artwork and BRAND.md are all uploaded and publicly served")
else:
    patterns = []
    for line in open(AI, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("/"):
            patterns.append(("dir", line.rstrip("/")))
        elif line.startswith("*."):
            patterns.append(("ext", line[1:]))
        elif "*" not in line and "?" not in line:
            patterns.append(("exact", line))
        else:
            errors.append(f".assetsignore: pattern {line!r} is a shape this check "
                          f"does not understand, so it cannot prove the site "
                          f"still ships. Simplify it or teach validate.py.")

    def excluded(relpath):
        for kind, pat in patterns:
            if kind == "dir" and (relpath == pat or relpath.startswith(pat + "/")):
                return pat + "/"
            if kind == "ext" and relpath.endswith(pat):
                return "*" + pat
            if kind == "exact" and relpath == pat:
                return pat
        return None

    # wrangler walks the asset directory with a plain recursive readdir and
    # excludes only .assetsignore, _headers and _redirects by itself. Dotfiles
    # are not excluded, and the asset directory is the repo root, so without
    # this line the whole git history is uploaded and publicly served.
    if not excluded(".git/config"):
        errors.append(".assetsignore does not exclude .git/. The asset directory "
                      "is the repo root and wrangler does not skip dotfiles, so "
                      "the entire repository history would be served publicly.")

    # Everything a page actually asks the browser to fetch, plus the files the
    # platform and crawlers fetch by convention.
    referenced = {"favicon.ico", "sitemap.xml", "robots.txt", "site.webmanifest",
                  "_headers", "_redirects"}
    for page in pages:
        body = open(page, encoding="utf-8").read()
        base = os.path.dirname(page)
        referenced.add(rel(page))
        for attr in re.findall(r'(?:href|src)="([^"]+)"', body):
            if attr.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            t = attr.split("#")[0].split("?")[0]
            if not t:
                continue
            fp = os.path.normpath(os.path.join(base, t))
            if os.path.exists(fp):
                referenced.add(rel(fp))
    mf = os.path.join(ROOT, "site.webmanifest")
    if os.path.exists(mf):
        for icon in re.findall(r'"src"\s*:\s*"([^"]+)"', open(mf, encoding="utf-8").read()):
            fp = os.path.normpath(os.path.join(ROOT, icon.lstrip("/")))
            if os.path.exists(fp):
                referenced.add(rel(fp))

    for r in sorted(referenced):
        hit = excluded(r)
        if hit:
            errors.append(f".assetsignore: pattern '{hit}' excludes {r}, which the "
                          f"site links to. It would 404 in production.")

# ---------- no credential may ever be committed ----------
# The whole point of reading the key from env is defeated by one paste. Sweep
# every tracked text file for the shapes of the keys this project touches.
SECRET_PATTERNS = [
    (r"\bre_[A-Za-z0-9_-]{16,}", "Resend API key"),
    (r"\b0x[0-9A-Fa-f]{40}\b", "private key material"),
    (r"AIza[0-9A-Za-z_-]{35}", "Google API key"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key block"),
]
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    for f in filenames:
        fp = os.path.join(dirpath, f)
        if os.path.splitext(f)[1].lower() not in (
                ".js", ".json", ".html", ".css", ".py", ".md", ".txt", ".yml",
                ".yaml", ".toml", ".sh", ".xml", ""):
            continue
        try:
            body = open(fp, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for pat, what in SECRET_PATTERNS:
            if re.search(pat, body):
                errors.append(f"{rel(fp)}: looks like a committed {what}. "
                              f"Secrets belong in Cloudflare env vars, never in git.")

# ---------- the printed QR code's target must keep existing ----------
# A QR on a business card cannot be corrected after the print run. This ties the
# build to it: if the page the code points at is renamed or deleted, or the
# domain constant moves away from what was printed, the build fails here rather
# than in someone's wallet.
qr_tool = os.path.join(ROOT, "tools", "build-contact-qr.py")
if os.path.exists(qr_tool):
    tool_src = open(qr_tool, encoding="utf-8").read()
    m = re.search(r'^URL = "([^"]+)"', tool_src, re.M)
    if not m:
        errors.append("build-contact-qr.py: cannot find the URL constant")
    else:
        qr_url = m.group(1)
        # the domain the pages declare must be the domain that was printed
        site_domain = None
        idx = os.path.join(ROOT, "index.html")
        if os.path.exists(idx):
            cm = re.search(r'rel="canonical" href="(https://[^/"]+)',
                           open(idx, encoding="utf-8").read())
            site_domain = cm.group(1) if cm else None
        if site_domain and not qr_url.startswith(site_domain):
            errors.append(
                f"printed QR points at {qr_url} but the site now declares "
                f"{site_domain}: the printed cards would be stranded")
        # and the path itself must still be a real page
        path_part = qr_url.split("://", 1)[-1].split("/", 1)
        rel_path = path_part[1] if len(path_part) > 1 else ""
        rel_path = rel_path.split("#")[0].split("?")[0].strip("/")
        if rel_path:
            candidates = [rel_path, rel_path + ".html",
                          os.path.join(rel_path, "index.html")]
            if not any(os.path.exists(os.path.join(ROOT, c)) for c in candidates):
                errors.append(
                    f"printed QR points at /{rel_path}, which no longer exists "
                    f"as a page: every printed card would 404")

# ---------- cache-busting versions must match the files ----------
# A stale ?v= is worse than none: it pins browsers to an old stylesheet for a
# week while the HTML moves on.
import hashlib
# NB: do not name the loop variable `rel`; that is the path helper defined above.
for asset_rel, pat in (("assets/css/styles.css", r"assets/css/styles\.css\?v=([0-9a-f]+)"),
                       ("assets/js/main.js", r"assets/js/main\.js\?v=([0-9a-f]+)")):
    fp = os.path.join(ROOT, asset_rel)
    if not os.path.exists(fp):
        continue
    want = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:10]
    for page in pages:
        body = open(page, encoding="utf-8").read()
        m = re.search(pat, body)
        if not m:
            errors.append(f"{rel(page)}: {os.path.basename(fp)} has no ?v= "
                          f"cache-busting version")
        elif m.group(1) != want:
            errors.append(f"{rel(page)}: {os.path.basename(fp)} ?v={m.group(1)} "
                          f"is stale, file hashes to {want}")

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

#!/usr/bin/env python3
"""Generate every page of the Greyman Protection site from one taxonomy.

    python3 tools/build-site.py

Ten pages share a header, mobile drawer, icon sprite, footer, action bar and
to-top button. Hand-editing that chrome across ten files is how the last build
ended up with an empty <h4> on every page, so it is emitted from one source
here and the pages carry only their own content.

EVERY claim below traces to the client's company profile. Nothing about
volumes, years, headcount, response times, certifications or accreditations is
invented. In particular this site makes NO PSIRA claim and NO company
registration claim: the Greyman profile asserts neither, and the previous
INTEGRI entity's registration does not transfer to a different trading name.
Add them only when the client supplies the numbers.
"""
import datetime
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def img_size(rel):
    """Intrinsic pixel size of a shipped image, read from the file itself.

    Hard-coding width/height means the attributes drift the moment the art is
    regenerated at a different size, and a wrong pair reserves the wrong box
    and shifts the layout. Read them instead.
    """
    from PIL import Image
    with Image.open(os.path.join(ROOT, rel)) as im:
        return im.size


def division_symbols():
    """The client's own division icons, traced by tools/trace-division-icons.py.

    Read at build time rather than pasted in, so re-tracing the artwork is the
    only step needed to update them.
    """
    fp = os.path.join(ROOT, "tools", "_division-icons.svg")
    if not os.path.exists(fp):
        raise SystemExit("run tools/trace-division-icons.py first: "
                         "_division-icons.svg is missing")
    return open(fp, encoding="utf-8").read().rstrip("\n")


MARK_W, MARK_H = img_size("assets/img/greyman-mark.png")

# The one place the domain lives. Switched to greymanprotection.co.za once that
# host was confirmed live and serving this site: leaving canonicals pointed at
# the old INTEGRI domain told search engines the old one was authoritative.
DOMAIN = "https://www.greymanprotection.co.za"
BRAND = "Greyman Protection"
TAGLINE = "SECURITY &middot; PROTECTION &middot; INTELLIGENCE &middot; CONTROL"
EMAIL = "ops@greymanprotection.co.za"
ADDRESS = "466 Karel Trichardt Street, Mountainview, Pretoria"
DIRECTORS = [
    ("Etienne", "Director", "+27 71 118 3257", "27711183257"),
    ("Jacques", "Director", "+27 67 161 2570", "27671612570"),
]

# ---------------------------------------------------------------------------
# Taxonomy: the six divisions, verbatim in substance from the company profile.
# ---------------------------------------------------------------------------
DIVISIONS = [
    dict(
        slug="investigations", name="Special Investigations", short="Investigations",
        icon="d-investigations",
        blurb="Track and trace, vetting, polygraphs, criminal record checks, extortion and kidnap and ransom support.",
        headline=("Decisions are only as good as", "the facts behind them"),
        intro="Where there is uncertainty, suspected wrongdoing or a person who must be "
              "found, we establish what is actually true: discreetly, methodically and in "
              "a form you can act on.",
        services=[
            ("Track and Trace", "i-eye",
             "Locating individuals or establishing whereabouts through a structured investigative approach."),
            ("Vetting", "i-doc",
             "Background and integrity screening of employees, contractors and partners before trust is extended."),
            ("Polygraph Services", "d-polygraph",
             "Polygraph examinations that support investigations and internal processes where more information is required."),
            ("Criminal Record Checks", "i-lock-file",
             "Additional certainty when evaluating prospective employees, contractors or anyone entering a position of trust."),
            ("Extortion Cases", "i-shield-check",
             "Careful handling of extortion pressure: gathering relevant information and supporting a measured security response."),
            ("Evictions", "i-scale",
             "Security support for eviction operations requiring planning, controlled execution and protection of everyone involved."),
            ("Kidnap and Ransom", "i-protection",
             "Kidnap and ransom situations demand discretion, controlled decision-making and a clear understanding of the risks. "
             "We provide specialist investigative and security support to clients and families through the most sensitive "
             "circumstances they will ever face."),
        ],
    ),
    dict(
        slug="asset-protection", name="Asset Protection", short="Asset Protection",
        icon="d-asset",
        blurb="Bullion runs and high-value assets in transit, planned around exposure points.",
        headline=("High-value movement is", "a plan, not a vehicle"),
        intro="Where theft, interception or loss would be significant, we plan the movement "
              "itself: route, timing, exposure points and the protection required from "
              "origin to destination.",
        services=[
            ("Bullion Runs", "i-asset",
             "Controlled transportation of bullion and exceptionally valuable commodities, with disciplined execution and constant situational awareness."),
            ("High-Value Assets in Transit", "i-lock-file",
             "Protection adapted to the asset, route, operating environment and assessed level of risk, overt or low-profile as required."),
        ],
    ),
    dict(
        slug="close-protection", name="Executive Close Protection", short="Close Protection",
        icon="d-close",
        blurb="Discreet executive and VIP protection, event security and security-trained drivers.",
        headline=("Protection that does", "not interrupt the day"),
        intro="Effective close protection is felt by the threat, not by the client. Our "
              "teams work on preparation and awareness so executives, VIPs and at-risk "
              "individuals carry on with meetings, travel and family life.",
        services=[
            ("Corporate Close Protection", "i-protection",
             "Dedicated protection for executives and key individuals during business activity, travel and movement between locations."),
            ("Special Event Security", "i-users",
             "Access control and personal protection for events involving executives, VIPs and invited guests."),
            ("Secure Drivers", "i-arrow-r",
             "Drivers who bring route awareness and risk thinking to every journey: transport with security built in."),
        ],
    ),
    dict(
        slug="mining-security", name="Mining Security", short="Mining Security",
        icon="d-mining",
        blurb="Illegal mining prevention, unrest control, dedicated searches and incident investigation.",
        headline=("Large sites, valuable material,", "competing interests"),
        intro="Mining environments combine open ground, high-value material, heavy "
              "equipment, contractors and surrounding communities. That mix produces risk "
              "that ordinary guarding does not answer. Our teams work to protect people, "
              "assets and, critically, operational continuity.",
        services=[
            ("Illegal Mining Prevention Teams", "i-specialized",
             "Dedicated teams that identify, deter and respond to illegal mining activity on and around the operation."),
            ("Riot and Civil Unrest Control", "i-users",
             "Support during unrest, demonstrations and disturbances: holding control, limiting escalation and protecting people and infrastructure."),
            ("Dedicated Searches", "i-investigation",
             "Structured searches of areas, buildings, vehicles and other environments where a focused response is required."),
            ("Incident Investigations", "i-doc",
             "Theft, suspicious activity and internal security concerns investigated so management can act on reliable information."),
            ("Bullion Runs", "i-asset",
             "Movement of bullion and other high-value mining commodities, coordinated with the operation's own procedures and shift patterns."),
        ],
        note="Downtime, stolen material and unrest cost more than the security that "
             "prevents them. Our mining work is measured on production days protected, "
             "not on hours billed.",
    ),
    dict(
        slug="guarding", name="Guarding and Site Security", short="Guarding",
        icon="d-guarding",
        blurb="Controlled access, patrols and a professional presence on sites that carry real risk.",
        headline=("A presence that is", "actually watching"),
        intro="Guarding is only worth what the people doing it notice. Controlled access, "
              "patrols and a professional presence on sites that carry real risk, with "
              "teams held to the same standard of awareness and conduct as the rest of "
              "our work.",
        services=[
            ("Controlled Access", "i-security",
             "Managing who enters and leaves a site, and keeping a record that means something afterwards."),
            ("Patrols", "i-eye",
             "Scheduled and irregular patrols that cover a site properly rather than following a predictable pattern."),
            ("Professional Presence", "i-guarding",
             "Officers deployed to sites that carry real risk, briefed on the environment and on what to do when it changes."),
        ],
    ),
    dict(
        slug="training", name="Training", short="Training",
        icon="d-training",
        blurb="Corporate, firearm, riot control and security training for personnel and organisations.",
        headline=("Capability you keep", "after we leave"),
        intro="Security improves permanently when your own people recognise risk, respond "
              "correctly and act with confidence. Our training is practical, "
              "scenario-driven and built for the environment the client actually operates in.",
        services=[
            ("Corporate Training", "i-users",
             "Security awareness adapted to the risks and responsibilities of corporate personnel."),
            ("Firearm Training", "i-target",
             "Safe, responsible and competent firearm handling, taught to a measurable standard."),
            ("Riot Control Training", "i-shield-check",
             "Crowd management and unrest response for personnel who work in high-pressure environments."),
            ("Security Training", "i-guarding",
             "Discipline, procedure and operational capability for security teams already on the ground."),
        ],
        extras=[
            ("Delivery", "On your site or ours, scheduled around shifts and operational demands."),
            ("Group size", "Small groups, so instruction stays hands-on and every candidate is assessed."),
            ("Outcome", "Written feedback on performance, gaps and what to reinforce next."),
        ],
    ),
]

WHY = [
    ("The solution is built around your risk",
     "No two mandates are identical, so we do not sell a standard package. We establish "
     "what needs protecting, what the realistic threats are and what outcome you need, "
     "then match people and measures to that, and nothing more."),
    ("Discretion is the service",
     "Executives, investigations, internal concerns and valuable assets all carry "
     "reputational exposure. Information is compartmentalised, teams are briefed on a "
     "need-to-know basis, and our presence is calibrated to draw as little attention as "
     "the situation allows."),
    ("Prevention before reaction",
     "The best outcome is the incident that never happens. Route planning, vulnerability "
     "assessment, environment study and early threat recognition remove exposure before a "
     "situation develops, which is also the cheapest security you will ever buy."),
    ("Conduct that holds up under pressure",
     "When officers are deployed, their behaviour is your brand. We hold our teams to "
     "discipline, situational awareness, controlled escalation and a professional presence "
     "appropriate to the environment: boardroom, site or crowd."),
    ("One partner across every requirement",
     "An investigation often exposes the need for close protection. A mine may need "
     "prevention teams, investigations and training at once. Because these capabilities sit "
     "in one company, findings move straight into action instead of being handed between "
     "suppliers."),
]

STEPS = [
    ("Understand the requirement",
     "We establish what the client needs, the environment involved and the circumstances surrounding the situation."),
    ("Assess the risk",
     "Threats, vulnerabilities and operational constraints are evaluated before any response is proposed."),
    ("Plan the operation",
     "Personnel, movements, equipment and security measures are coordinated against the assignment, with contingencies built in."),
    ("Execute professionally",
     "The operation runs with the focus on protecting the client, holding control and achieving the required objective."),
    ("Adapt when conditions change",
     "Security situations are rarely static. When circumstances shift, the response shifts with them, and the client is told."),
]

CLIENTS = ["Private individuals", "Corporate executives", "Business owners",
           "Companies and organisations", "Mining operations", "High-value asset owners",
           "Event organisers", "Legal and investigative mandates",
           "Organisations needing training"]

SPRITE = '''  <svg class="sprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
    <symbol id="i-investigation" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/><path d="M8.6 11a2.4 2.4 0 0 1 2.4-2.4"/></symbol>
    <symbol id="i-asset" viewBox="0 0 24 24"><rect x="2.6" y="6.4" width="11.6" height="10.4" rx="1.6"/><path d="M14.2 9.4h3.4l3 3.2v4.2h-6.4"/><circle cx="7" cy="19" r="1.8"/><circle cx="17.2" cy="19" r="1.8"/><path d="M8.4 10.4v3.4"/></symbol>
    <symbol id="i-polygraph" viewBox="0 0 24 24"><path d="M2 12h3.5l2.5-7 4 14 2.5-7H22"/></symbol>
    <symbol id="i-security" viewBox="0 0 24 24"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15.4" r="1.4"/></symbol>
    <symbol id="i-protection" viewBox="0 0 24 24"><path d="M12 2.4l7.4 3.2v5.7c0 4.8-3.1 8.3-7.4 9.9-4.3-1.6-7.4-5.1-7.4-9.9V5.6L12 2.4z"/><circle cx="12" cy="10" r="2.1"/><path d="M8.4 16.4a4 4 0 0 1 7.2 0"/></symbol>
    <symbol id="i-guarding" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.2"/><path d="M2.6 20a6.4 6.4 0 0 1 12.8 0"/><path d="M16.2 5.3a3.2 3.2 0 0 1 0 5.4"/><path d="M17.6 14.3A6.4 6.4 0 0 1 21.4 20"/></symbol>
    <symbol id="i-specialized" viewBox="0 0 24 24"><path d="M3.6 16a8.4 8.4 0 0 1 16.8 0"/><path d="M3.6 16v1a3 3 0 0 0 3 3h1.4"/><path d="M20.4 16v1a3 3 0 0 1-3 3H16"/><path d="M8 20l.9 1.6"/><path d="M16 20l-.9 1.6"/><path d="M8.5 11.4h4"/></symbol>
    <symbol id="i-mail" viewBox="0 0 24 24"><rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="M3.2 6.4L12 12.6l8.8-6.2"/></symbol>
    <symbol id="i-phone" viewBox="0 0 24 24"><path d="M7 3.5h-3a1 1 0 0 0-1 1A16.5 16.5 0 0 0 19.5 21a1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1 11 11 0 0 1-3.5-.6 1 1 0 0 0-1 .25l-1.6 1.6a15 15 0 0 1-6.15-6.15l1.6-1.6a1 1 0 0 0 .25-1A11 11 0 0 1 8 4.5a1 1 0 0 0-1-1z"/></symbol>
    <symbol id="i-whatsapp" viewBox="0 0 24 24"><path d="M20.5 11.7a8.5 8.5 0 0 1-12.7 7.4L3.5 20.5l1.5-4.2A8.5 8.5 0 1 1 20.5 11.7z"/><path d="M9 9.4c.2-.5.5-.5.8-.5h.5l1 2.2-.7.8a6.2 6.2 0 0 0 2.9 2.5l.8-.8 2 1v.6c-.2.6-.9 1-1.6 1a8.6 8.6 0 0 1-5.9-5.7c-.1-.4 0-.8.2-1.1z"/></symbol>
    <symbol id="i-shield-check" viewBox="0 0 24 24"><path d="M12 2.4l7.4 3.2v5.7c0 4.8-3.1 8.3-7.4 9.9-4.3-1.6-7.4-5.1-7.4-9.9V5.6L12 2.4z"/><path d="M8.7 12l2.3 2.3 4.3-4.5"/></symbol>
    <symbol id="i-target" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="3.6"/><path d="M12 1.4v3.2M12 19.4v3.2M1.4 12h3.2M19.4 12h3.2"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><path d="M12 6.8V12l3.2 2"/></symbol>
    <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2"/><path d="M12 3.4c2.3 2.4 3.5 5.4 3.5 8.6S14.3 18.2 12 20.6c-2.3-2.4-3.5-5.4-3.5-8.6S9.7 5.8 12 3.4z"/></symbol>
    <symbol id="i-doc" viewBox="0 0 24 24"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 16.5h4"/></symbol>
    <symbol id="i-eye" viewBox="0 0 24 24"><path d="M2 12s3.7-6.4 10-6.4S22 12 22 12s-3.7 6.4-10 6.4S2 12 2 12z"/><circle cx="12" cy="12" r="2.7"/></symbol>
    <symbol id="i-scale" viewBox="0 0 24 24"><path d="M12 3.5v17"/><path d="M5 7.2h14"/><path d="M7.6 7.2L5 13.4h5.2L7.6 7.2z"/><path d="M16.4 7.2l-2.6 6.2H19l-2.6-6.2z"/><path d="M8 20.5h8"/></symbol>
    <symbol id="i-lock-file" viewBox="0 0 24 24"><rect x="3.5" y="4" width="17" height="16" rx="2"/><path d="M9.5 12.5v-1.2a2.5 2.5 0 0 1 5 0v1.2"/><rect x="8.4" y="12.5" width="7.2" height="5" rx="1"/></symbol>
    <symbol id="i-arrow-r" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
    <symbol id="i-users" viewBox="0 0 24 24"><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="9" cy="8.5" r="3.4"/><path d="M16.5 20a5 5 0 0 0-2-4"/><circle cx="17" cy="9.5" r="2.6"/></symbol>
__DIVISION_SYMBOLS__
  </svg>'''.replace("__DIVISION_SYMBOLS__", division_symbols())

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def ico(name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


JSONLD = """  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "%(brand)s",
    "description": "Specialist security, protection and investigative services for individuals, businesses, mining operations and organisations across South Africa.",
    "url": "%(domain)s/",
    "email": "%(email)s",
    "image": "%(domain)s/assets/img/og-image.png",
    "logo": "%(domain)s/assets/img/greyman-mark.png",
    "telephone": "+27711183257",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "466 Karel Trichardt Street",
      "addressLocality": "Mountainview, Pretoria",
      "addressCountry": "ZA"
    },
    "areaServed": { "@type": "Country", "name": "South Africa" },
    "hasOfferCatalog": {
      "@type": "OfferCatalog",
      "name": "Divisions",
      "itemListElement": [
%(services)s
      ]
    }
  }
  </script>
""" % {
    "brand": BRAND,
    "domain": DOMAIN,
    "email": EMAIL,
    "services": ",\n".join(
        '        { "@type": "Offer", "itemOffered": '
        '{ "@type": "Service", "name": "%s", "description": "%s" } }'
        % (d["name"], d["blurb"]) for d in DIVISIONS),
}


# ---------------------------------------------------------------------------
# Chrome. Class names are the existing design system's, verbatim: the
# stylesheet is frozen (BRAND.md §5) so the markup adapts to it, never the
# other way round.
# ---------------------------------------------------------------------------
def head(p, title, desc, canon, noindex=False):
    robots_tag = ('  <meta name="robots" content="noindex, follow" />\n'
                  if noindex else "")
    # Structured data on the home page only: one page describing the entity,
    # so search engines are not handed ten competing copies of it. Every field
    # traces to the company profile; nothing about ratings, price, hours or
    # accreditation is asserted, because none of it is documented.
    jsonld = JSONLD if canon == "/" else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <meta name="theme-color" content="#000000" />
  <link rel="canonical" href="{DOMAIN}{canon}" />

  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{DOMAIN}{canon}" />
  <meta property="og:image" content="{DOMAIN}/assets/img/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{BRAND}: security, protection, intelligence, control" />
  <meta property="og:site_name" content="{BRAND}" />
  <meta property="og:locale" content="en_ZA" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{desc}" />
  <meta name="twitter:image" content="{DOMAIN}/assets/img/og-image.png" />
  <meta name="twitter:image:alt" content="{BRAND}: security, protection, intelligence, control" />
{robots_tag}
  <link rel="icon" href="{p}favicon.ico" sizes="32x32" />
  <link rel="icon" type="image/svg+xml" href="{p}assets/img/favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="{p}assets/img/favicon-32.png" />
  <link rel="icon" type="image/png" sizes="192x192" href="{p}assets/img/favicon-192.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="{p}assets/img/apple-touch-icon.png" />
  <link rel="manifest" href="{p}site.webmanifest" />
{jsonld}

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@300;400;500;600;700&family=Chakra+Petch:wght@500;600;700&display=swap" rel="stylesheet" />

  <link rel="stylesheet" href="{p}assets/css/styles.css" />
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="scroll-progress" id="scrollProgress"></div>

{SPRITE}

'''


def brand(p):
    # The <img> is the figure alone. The name is set in type, mirroring the
    # logo's own lockup, so it stays crisp at any size and never duplicates
    # the wordmark that would otherwise sit inside the image.
    return (f'      <a href="{p}index.html" class="brand" aria-label="{BRAND} home page">\n'
            f'        <img src="{p}assets/img/greyman-mark.png" alt="" class="brand__mark" width="{MARK_W}" height="{MARK_H}" />\n'
            f'        <span class="brand__text">\n'
            f'          <strong>GREYMAN</strong>\n'
            f'          <em><span>Protection</span></em>\n'
            f'        </span>\n'
            f'      </a>')


def header(p, active=""):
    def a(href, label, key):
        c = ' class="is-active"' if active == key else ""
        return f'        <a href="{p}{href}"{c}>{label}</a>'
    drops = "\n".join(
        f'            <a class="nav-drop__link" role="menuitem" href="{p}services/{d["slug"]}.html">'
        f'{ico(d["icon"])} {d["name"]}</a>' for d in DIVISIONS)
    mm = []
    home_cls = ' class="is-active"' if active == "home" else ""
    mm.append(f'        <a href="{p}index.html"{home_cls} style="--i:0">'
              f'<span class="mm__num">01</span> Home</a>')
    mm.append(f'        <a href="{p}services/index.html" style="--i:1"><span class="mm__num">02</span> All Services</a>')
    for i, d in enumerate(DIVISIONS):
        mm.append(f'        <a href="{p}services/{d["slug"]}.html" style="--i:{i + 2}">'
                  f'<span class="mm__num">{i + 3:02d}</span> {d["short"]}</a>')
    mm.append(f'        <a href="{p}about.html" style="--i:{len(DIVISIONS) + 2}"><span class="mm__num">{len(DIVISIONS) + 3:02d}</span> About</a>')
    mm.append(f'        <a href="{p}contact.html" style="--i:{len(DIVISIONS) + 3}"><span class="mm__num">{len(DIVISIONS) + 4:02d}</span> Contact</a>')

    return f'''  <header class="site-header" id="siteHeader">
    <div class="wrap header__inner">
{brand(p)}

      <nav class="nav-desktop" aria-label="Primary">
{a("index.html", "Home", "home")}

        <div class="nav-drop">
          <button class="nav-drop__toggle" aria-expanded="false" aria-haspopup="true">
            Services
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div class="nav-drop__panel" role="menu">
{drops}
            <a class="nav-drop__link" role="menuitem" href="{p}services/index.html">{ico("i-arrow-r")} All divisions</a>
          </div>
        </div>

{a("about.html", "About", "about")}
{a("contact.html", "Contact", "contact")}
      </nav>

      <div class="header__cta">
        <a class="btn btn--blue btn--sm" href="mailto:{EMAIL}">
          {ico("i-mail")}
          Email us
        </a>
      </div>

      <button class="hamburger" id="hamburger" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <div class="mobile-menu" id="mobileMenu" aria-hidden="true">
    <div class="mobile-menu__panel">
      <nav aria-label="Mobile">
{chr(10).join(mm)}
      </nav>
      <div class="mobile-menu__foot">
        <a class="btn btn--blue btn--block" href="mailto:{EMAIL}">Email us</a>
        <p class="mm-mail">{EMAIL}</p>
      </div>
    </div>
  </div>

'''


def footer(p):
    left, right = DIVISIONS[:3], DIVISIONS[3:]
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer__grid">
        <div class="footer__brand">
{brand(p)}
          <p>Specialist security, protection and investigative services for individuals,
             businesses, mining operations and organisations across South Africa.</p>
        </div>

        <div class="footer__col">
          <h3>Investigation &amp; Assets</h3>
          <div class="footer__links">
{chr(10).join(f'            <a href="{p}services/{d["slug"]}.html">{d["short"]}</a>' for d in left)}
          </div>
        </div>

        <div class="footer__col">
          <h3>Protection &amp; Training</h3>
          <div class="footer__links">
{chr(10).join(f'            <a href="{p}services/{d["slug"]}.html">{d["short"]}</a>' for d in right)}
            <a href="{p}services/index.html">All divisions</a>
          </div>
        </div>

        <div class="footer__col">
          <h3>Company</h3>
          <div class="footer__links">
            <a href="{p}about.html">About {BRAND}</a>
            <a href="{p}contact.html">Contact</a>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
          </div>
        </div>

        <div class="footer__col">
          <h3>Legal</h3>
          <div class="footer__links">
            <a href="{p}privacy.html">Privacy Policy</a>
            <a href="{p}terms.html">Terms of Use</a>
            <a href="{p}paia.html">Access to Information</a>
          </div>
        </div>
      </div>

      <div class="footer__bottom">
        <span>&copy; <span data-year>2026</span> {BRAND}. All rights reserved.</span>
        <span>{ADDRESS}</span>
        <span>{TAGLINE}</span>
      </div>
    </div>
  </footer>

  <div class="action-bar">
    <a class="is-primary" href="mailto:{EMAIL}">
      {ico("i-mail")} Email us
    </a>
    <a href="{p}contact.html">
      {ico("i-phone")} Contact
    </a>
  </div>

  <!-- Not a cookie banner: this site sets no cookies and runs no analytics, so
       there is nothing to consent to. It says so once, then stays dismissed. -->
  <aside class="privacy-note" id="privacyNote" hidden aria-label="Privacy notice">
    <p>This site sets <strong>no cookies</strong> and runs no analytics.
       <a href="{p}privacy.html">How we handle personal information</a>.</p>
    <button type="button" class="privacy-note__ok" id="privacyOk">Got it</button>
  </aside>

  <button class="to-top" id="toTop" aria-label="Scroll back to top">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
  </button>

  <script src="{p}assets/js/main.js" defer></script>
</body>
</html>
'''


def cta_band(p):
    return f'''    <section class="cta-band">
      <div class="wrap cta-band__inner">
        <h2 class="cta-band__title reveal">Tell us what you <span class="grad">need protected.</span></h2>
        <div class="cta-band__copy reveal">
          <p>The first conversation is with the people who will run the mandate.
             Confidential, and no obligation.</p>
          <div class="hero__actions">
            <a class="btn btn--blue btn--lg" href="mailto:{EMAIL}">{ico("i-mail")} Email us</a>
            <a class="btn btn--outline btn--lg" href="{p}contact.html">Contact page {ARROW}</a>
          </div>
        </div>
      </div>
    </section>

'''
# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
# Badges are constrained to claims the company profile actually supports.
# There is no PSIRA badge and no "24/7" badge anywhere on this site: the
# Greyman profile asserts neither, so neither can be published.
BADGES = [("i-users", "Director-led"), ("i-lock-file", "Confidential"),
          ("i-globe", "South Africa")]


def badges(items=None):
    return "\n".join(
        f'          <span class="hero__badge">{ico(n)} {t}</span>'
        for n, t in (items or BADGES))


def svc_card(p, d, n):
    """p is the href prefix to the division pages: "services/" at the root, "" in the hub."""
    subs = "".join(f"<li>{s[0]}</li>" for s in d["services"][:4])
    return f'''        <article class="svc-card reveal" style="--d:.{n}s">
          <span class="svc-card__num">{n + 1:02d}</span>
          <div class="svc-card__icon">{ico(d["icon"], "ico ico--lg")}</div>
          <h3 class="svc-card__title">{d["name"]}</h3>
          <p class="svc-card__copy">{d["blurb"]}</p>
          <ul class="svc-card__list">{subs}</ul>
          <a class="svc-card__link" href="{p}{d["slug"]}.html">Explore division {ARROW}</a>
        </article>'''


def why_blocks():
    return "\n".join(f'''        <div class="step reveal" style="--d:.{i}s">
          <span class="step__num">{i + 1:02d}</span>
          <div class="step__copy">
            <h3 class="step__title">{t}</h3>
            <p>{b}</p>
          </div>
        </div>''' for i, (t, b) in enumerate(WHY))


def step_blocks():
    return "\n".join(f'''        <div class="step reveal" style="--d:.{i}s">
          <span class="step__num">{i + 1:02d}</span>
          <div class="step__copy">
            <h3 class="step__title">{t}</h3>
            <p>{b}</p>
          </div>
        </div>''' for i, (t, b) in enumerate(STEPS))


# ---------------------------------------------------------------------------
def page_home():
    p = ""
    cards = "\n".join(svc_card("services/", d, i) for i, d in enumerate(DIVISIONS))
    marquee = "".join(
        f"<span>{d['short']}</span><i>&#9670;</i>" for d in DIVISIONS) * 2
    return head(p, f"{BRAND} | Security, Protection, Intelligence, Control",
                "Specialist security, protection and investigative services in South Africa. "
                "Close protection, asset protection, special investigations, mining security, "
                "guarding and training.", "/") + header(p, "home") + f'''  <main id="main">

    <section class="hero">
      <div class="hero__bg" aria-hidden="true"></div>

      <div class="wrap hero__inner">
        <div class="hero__copy">
        <div class="hero__badges reveal">
{badges()}
        </div>

        <h1 class="hero__title">
          <span class="hero__line"><span class="hero__line-in" style="--d:.15s">Built around the risk,</span></span>
          <span class="hero__line"><span class="hero__line-in grad" style="--d:.32s">not a package.</span></span>
        </h1>

        <p class="hero__lead reveal" style="--d:.60s">
          {BRAND} is a specialist security, protection and investigative company serving
          individuals, businesses, mining operations and organisations that need more than a
          standard security presence. Protect people. Protect assets. Establish the facts.
          Reduce risk.
        </p>

        <div class="hero__actions reveal" style="--d:.70s">
          <a class="btn btn--blue btn--lg" href="mailto:{EMAIL}">
            Start a confidential enquiry
            {ARROW}
          </a>
          <a class="btn btn--outline btn--lg" href="services/index.html">View our divisions</a>
        </div>

        <p class="hero__mail reveal" style="--d:.80s">
          Every enquiry is treated in confidence, <a href="mailto:{EMAIL}">{EMAIL}</a>
        </p>
        </div>

        <div class="hero__figure reveal" aria-hidden="true" style="--d:.45s">
          <img src="assets/img/greyman-mark.png" alt="" width="{MARK_W}" height="{MARK_H}" />
        </div>
      </div>
    </section>

    <div class="trust">
      <div class="wrap trust__inner">
        <div class="trust__item"><strong><span data-count="6">6</span></strong><span>Specialist divisions</span></div>
        <div class="trust__item"><strong>Director</strong><span>Led on every mandate</span></div>
        <div class="trust__item"><strong>SA</strong><span>South Africa</span></div>
        <div class="trust__item"><strong>Discreet</strong><span>Compartmentalised by default</span></div>
      </div>
    </div>

    <div class="marquee" aria-hidden="true">
      <div class="marquee__track">
        {marquee}
      </div>
    </div>

    <section class="section section--alt" id="about">
      <div class="wrap">
        <div class="section__head section__head--left">
          <span class="eyebrow">Who we are</span>
          <h2 class="section__title reveal">Security built around the risk, <span class="grad">not a package.</span></h2>
        </div>

        <div class="detail">
          <div class="detail__body prose reveal">
            <p>A corporate executive moving between locations does not face the same risk as a
               mining operation dealing with illegal activity. A bullion movement is not an
               investigation. We treat them differently.</p>
            <p>Every assignment starts with understanding the situation: what must be protected,
               what can go wrong, and what outcome the client needs. Only then do we deploy the
               people, resources and measures suited to it.</p>
            <p>Directors are personally involved in every mandate. Clients deal with
               decision-makers, not a call centre, and sensitive information stays inside a small,
               accountable team.</p>
            <p>Real security is not someone standing nearby. It is knowing what to look for,
               what could go wrong, how to reduce the risk and how to respond when the
               situation changes.</p>
            <div class="pullquote">
              Protect people. Protect assets. Establish the facts. Reduce risk.
            </div>
          </div>

          <aside class="detail__aside">
            <div class="aside-card reveal">
              <h3 class="aside-card__title">How we work</h3>
              <div class="aside-card__row">{ico("i-target")} The solution is built around your risk, not a catalogue</div>
              <div class="aside-card__row">{ico("i-lock-file")} Information compartmentalised, teams briefed need-to-know</div>
              <div class="aside-card__row">{ico("i-eye")} Prevention before reaction, because the cheapest incident never happens</div>
              <div class="aside-card__row">{ico("i-users")} Six capabilities in one company, so findings move straight into action</div>
            </div>

            <div class="aside-card reveal" style="--d:.1s">
              <h3 class="aside-card__title">Talk to us</h3>
              <div class="aside-card__row">{ico("i-mail")} <a href="mailto:{EMAIL}">{EMAIL}</a></div>
              <div class="aside-card__row">{ico("i-globe")} {ADDRESS}</div>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class="section" id="services">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">Capabilities</span>
          <h2 class="section__title reveal">Six divisions. <span class="grad">One accountable team.</span></h2>
          <p class="section__sub reveal">An investigation often exposes the need for close protection.
             A mine may need prevention teams, investigations and training at once. Because these
             capabilities sit in one company, findings move straight into action.</p>
        </div>

        <div class="svc-grid">
{cards}
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">Why {BRAND}</span>
          <h2 class="section__title reveal">Five reasons clients hand us <span class="grad">the difficult work.</span></h2>
        </div>
        <div class="step-list">
{why_blocks()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">How we work</span>
          <h2 class="section__title reveal">Five steps from first call <span class="grad">to standing guard.</span></h2>
        </div>
        <div class="step-list">
{step_blocks()}
        </div>
      </div>
    </section>

{cta_band(p)}  </main>

''' + footer(p)


# ---------------------------------------------------------------------------
def page_about():
    p = ""
    clients = "\n".join(
        f'''          <div class="offer reveal" style="--d:.{i % 6}s">
            <div class="offer__icon">{ico("i-shield-check")}</div>
            <div class="offer__copy"><h3 class="offer__title">{c}</h3></div>
          </div>''' for i, c in enumerate(CLIENTS))
    return head(p, f"About | {BRAND}",
                f"{BRAND} is a specialist security, protection and investigative company in "
                "South Africa. Director-led mandates, compartmentalised information and a "
                "response matched to the actual risk.", "/about") + header(p, "about") + f'''  <main id="main">

    <section class="page-hero">
      <div class="wrap page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="index.html">Home</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <span aria-current="page">About</span>
        </nav>

        <span class="eyebrow">Who we are</span>
        <h1 class="page-hero__title reveal">More than a <span class="grad">standard security presence.</span></h1>
        <p class="page-hero__lead reveal" style="--d:.08s">
          {BRAND} is a specialist security, protection and investigative company serving
          individuals, businesses, mining operations and organisations that need more than a
          standard security presence.
        </p>

        <div class="page-hero__meta reveal" style="--d:.16s">
{badges()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="detail">
          <div class="detail__body prose reveal">
            <h2 class="section__title section__title--sm">Protect people. Protect assets. Establish the facts. Reduce risk.</h2>
            <p>A corporate executive moving between locations does not face the same risk as a
               mining operation dealing with illegal activity. A bullion movement is not an
               investigation. We treat them differently.</p>
            <p>Every assignment starts with understanding the situation: what must be protected,
               what can go wrong, and what outcome the client needs. Only then do we deploy the
               people, resources and measures suited to it.</p>
            <p>Directors are personally involved in every mandate. Clients deal with
               decision-makers, not a call centre, and sensitive information stays inside a small,
               accountable team.</p>
            <p>Real security is not someone standing nearby. It is knowing what to look for, what
               could go wrong, how to reduce the risk and how to respond when the situation
               changes. That is the standard {BRAND} works to, on an executive detail, a bullion
               run, a serious investigation or a mine under pressure.</p>
          </div>

          <aside class="detail__aside">
            <div class="aside-card reveal">
              <h3 class="aside-card__title">Talk to us</h3>
              <div class="aside-card__row">{ico("i-mail")} <a href="mailto:{EMAIL}">{EMAIL}</a></div>
              <div class="aside-card__row">{ico("i-globe")} {ADDRESS}</div>
              <a class="btn btn--blue btn--block" href="contact.html">Contact page</a>
            </div>
          </aside>
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">Why {BRAND}</span>
          <h2 class="section__title reveal">Five reasons clients hand us <span class="grad">the difficult work.</span></h2>
        </div>
        <div class="step-list">
{why_blocks()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">How we work</span>
          <h2 class="section__title reveal">Five steps from first call <span class="grad">to standing guard.</span></h2>
        </div>
        <div class="step-list">
{step_blocks()}
        </div>
      </div>
    </section>

    <section class="section section--alt">
      <div class="wrap">
        <div class="section__head section__head--mid">
          <span class="eyebrow">Who we work with</span>
          <h2 class="section__title reveal">The mandates that <span class="grad">come to us.</span></h2>
        </div>
        <div class="offer-grid">
{clients}
        </div>
      </div>
    </section>

{cta_band(p)}  </main>

''' + footer(p)


# ---------------------------------------------------------------------------
def page_contact():
    p = ""
    dirs = "\n".join(f'''          <article class="dir-card reveal" style="--d:.{i}s">
            <div class="dir-card__avatar">{ico("i-users", "ico ico--lg")}</div>
            <h3 class="dir-card__name">{n}</h3>
            <p class="dir-card__role">{role}</p>
            <a class="dir-card__row" href="tel:+{digits}">{ico("i-phone")} {tel}</a>
            <a class="dir-card__row" href="mailto:{EMAIL}">{ico("i-mail")} {EMAIL}</a>
          </article>''' for i, (n, role, tel, digits) in enumerate(DIRECTORS))
    opts = "\n".join(f'              <option>{d["name"]}</option>' for d in DIVISIONS)
    return head(p, f"Contact | {BRAND}",
                f"Contact {BRAND} in South Africa. Email is the preferred first contact and every "
                "enquiry is confidential. Speak directly to a director.",
                "/contact") + header(p, "contact") + f'''  <main id="main">

    <section class="page-hero">
      <div class="wrap page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="index.html">Home</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <span aria-current="page">Contact</span>
        </nav>

        <span class="eyebrow">Contact</span>
        <h1 class="page-hero__title reveal">Speak directly to <span class="grad">a director.</span></h1>
        <p class="page-hero__lead reveal" style="--d:.08s">
          Whether you need ongoing security support or help with one specific situation, the
          first conversation is with the people who will run the mandate. Confidential, and no
          obligation.
        </p>

        <div class="page-hero__meta reveal" style="--d:.16s">
{badges()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="contact__grid">
          <div class="contact-list reveal">
            <a class="contact-item" href="mailto:{EMAIL}">
              {ico("i-mail")}
              <span>
                <span class="contact-item__label">Email, preferred</span>
                <span class="contact-item__value">{EMAIL}</span>
              </span>
            </a>
{chr(10).join(f"""            <a class="contact-item" href="tel:+{digits}">
              {ico("i-phone")}
              <span>
                <span class="contact-item__label">{n}, {role}</span>
                <span class="contact-item__value">{tel}</span>
              </span>
            </a>""" for n, role, tel, digits in DIRECTORS)}
            <div class="contact-item">
              {ico("i-globe")}
              <span>
                <span class="contact-item__label">Office</span>
                <span class="contact-item__value">{ADDRESS}</span>
              </span>
            </div>
          </div>

          <div class="contact__form reveal" style="--d:.1s">
            <h2 class="section__title section__title--sm">Send an enquiry</h2>
            <p class="form__hint">Every enquiry is treated in confidence.</p>
            <form id="contactForm" novalidate>
              <div class="field">
                <input type="text" id="name" name="name" placeholder=" " required />
                <label for="name">Your name</label>
              </div>
              <div class="field">
                <input type="email" id="email" name="email" placeholder=" " required />
                <label for="email">Email address</label>
              </div>
              <div class="field">
                <select id="service" name="service">
                  <option value="">Which division?</option>
{opts}
                </select>
              </div>
              <div class="field">
                <textarea id="message" name="message" rows="5" placeholder=" " required></textarea>
                <label for="message">How can we help?</label>
              </div>
              <button type="submit" class="btn btn--blue btn--block btn--lg">Send enquiry</button>
              <p class="form__note" id="formNote" role="status" aria-live="polite"></p>
            </form>
          </div>
        </div>

        <div class="section__block">
          <h2 class="section__title section__title--sm reveal">Our directors</h2>
          <div class="dir-grid">
{dirs}
          </div>
        </div>
      </div>
    </section>

{cta_band(p)}  </main>

''' + footer(p)


# ---------------------------------------------------------------------------
def page_services_index():
    p = "../"
    cards = "\n".join(svc_card("", d, i) for i, d in enumerate(DIVISIONS))
    return head(p, f"Services | {BRAND}",
                "Six specialist divisions: special investigations, asset protection, executive "
                "close protection, mining security, guarding and site security, and training.",
                "/services/") + header(p, "services") + f'''  <main id="main">

    <section class="page-hero">
      <div class="wrap page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="{p}index.html">Home</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <span aria-current="page">Services</span>
        </nav>

        <span class="eyebrow">Capabilities</span>
        <h1 class="page-hero__title reveal">Six divisions. <span class="grad">One accountable team.</span></h1>
        <p class="page-hero__lead reveal" style="--d:.08s">
          An investigation often exposes the need for close protection. A mine may need
          prevention teams, investigations and training at once. Because these capabilities sit
          in one company, findings move straight into action instead of being handed between
          suppliers.
        </p>

        <div class="page-hero__meta reveal" style="--d:.16s">
{badges()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="svc-grid">
{cards}
        </div>
      </div>
    </section>

{cta_band(p)}  </main>

''' + footer(p)


# ---------------------------------------------------------------------------
def page_division(d, n):
    p = "../"
    offers = "\n".join(f'''          <article class="offer reveal" style="--d:.{i % 6}s">
            <div class="offer__icon">{ico(icon)}</div>
            <div class="offer__copy">
              <h3 class="offer__title">{title}</h3>
              <p>{body}</p>
            </div>
          </article>''' for i, (title, icon, body) in enumerate(d["services"]))

    extra = ""
    if d.get("extras"):
        extra = f'''
    <section class="section section--alt">
      <div class="wrap">
        <div class="offer-grid">
{chr(10).join(f"""          <article class="offer reveal" style="--d:.{i}s">
            <div class="offer__icon">{ico("i-doc")}</div>
            <div class="offer__copy">
              <h3 class="offer__title">{t}</h3>
              <p>{b}</p>
            </div>
          </article>""" for i, (t, b) in enumerate(d["extras"]))}
        </div>
      </div>
    </section>
'''
    note = ""
    if d.get("note"):
        note = f'''
    <section class="section section--alt">
      <div class="wrap">
        <div class="aside-card reveal">
          <h2 class="aside-card__title">Worth saying plainly</h2>
          <p>{d["note"]}</p>
        </div>
      </div>
    </section>
'''

    others = "\n".join(
        f'            <a href="{o["slug"]}.html">{o["name"]}</a>'
        for o in DIVISIONS if o["slug"] != d["slug"])

    return head(p, f'{d["name"]} | {BRAND}', d["blurb"],
                f'/services/{d["slug"]}') + header(p, "services") + f'''  <main id="main">

    <section class="page-hero">
      <div class="wrap page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="{p}index.html">Home</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <a href="index.html">Services</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <span aria-current="page">{d["name"]}</span>
        </nav>

        <span class="eyebrow">Division {n + 1:02d}</span>
        <h1 class="page-hero__title reveal">{d["headline"][0]} <span class="grad">{d["headline"][1]}</span></h1>
        <p class="page-hero__lead reveal" style="--d:.08s">{d["intro"]}</p>

        <div class="page-hero__meta reveal" style="--d:.16s">
{badges()}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section__head section__head--left">
          <span class="eyebrow">What this division does</span>
          <h2 class="section__title reveal">{d["name"]}</h2>
        </div>
        <div class="offer-grid">
{offers}
        </div>
      </div>
    </section>
{note}{extra}
    <section class="section">
      <div class="wrap">
        <div class="aside-card reveal">
          <h2 class="aside-card__title">Other divisions</h2>
          <div class="footer__links">
{others}
          </div>
        </div>
      </div>
    </section>

{cta_band(p)}  </main>

''' + footer(p)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------
def page_404():
    """Served by the host for any unmatched route.

    Lives at the repo root, is marked noindex and is deliberately absent from
    the sitemap. It carries the full chrome so someone who lands on a dead link
    still has the nav, and it routes them into the six divisions instead of
    dead-ending. Dead links are likely for a while: this site changed brand and
    its whole URL structure.
    """
    p = ""
    links = "\n".join(
        '          <a class="offer reveal" style="--d:.%ds" href="services/%s.html">\n'
        '            <div class="offer__icon">%s</div>\n'
        '            <div class="offer__copy">\n'
        '              <h3 class="offer__title">%s</h3>\n'
        '              <p>%s</p>\n'
        '            </div>\n'
        '          </a>' % (i, d["slug"], ico(d["icon"]), d["name"], d["blurb"])
        for i, d in enumerate(DIVISIONS))

    body = (
        '  <main id="main">\n\n'
        '    <section class="page-hero">\n'
        '      <div class="wrap page-hero__inner">\n'
        '        <span class="eyebrow">Error 404</span>\n'
        '        <h1 class="page-hero__title reveal">This page <span class="grad">does not exist.</span></h1>\n'
        '        <p class="page-hero__lead reveal" style="--d:.08s">\n'
        '          The link may be out of date, or the page may have moved when we\n'
        '          rebranded. Everything we do is listed below, or write to us and we\n'
        '          will point you at the right person.\n'
        '        </p>\n'
        '        <div class="hero__actions reveal" style="--d:.16s">\n'
        f'          <a class="btn btn--blue btn--lg" href="index.html">Back to the home page {ARROW}</a>\n'
        f'          <a class="btn btn--outline btn--lg" href="mailto:{EMAIL}">{ico("i-mail")} Email us</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>\n\n'
        '    <section class="section">\n'
        '      <div class="wrap">\n'
        '        <div class="section__head section__head--mid">\n'
        '          <span class="eyebrow">Our divisions</span>\n'
        '          <h2 class="section__title reveal">Where do you need <span class="grad">to get to?</span></h2>\n'
        '        </div>\n'
        '        <div class="offer-grid">\n'
        f'{links}\n'
        '        </div>\n'
        '      </div>\n'
        '    </section>\n\n'
        f'{cta_band(p)}  </main>\n\n')

    return head(p, f"Page not found | {BRAND}",
                "That page does not exist. Find the division you need, or contact "
                f"{BRAND} directly.", "/404", noindex=True) + header(p) + body + footer(p)


# ---------------------------------------------------------------------------
# Production files
# ---------------------------------------------------------------------------
def sitemap(entries):
    """Built from the same list the pages are, so the two cannot drift apart."""
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        "  <url>\n"
        f"    <loc>{DOMAIN}{canon}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{prio}</priority>\n"
        "  </url>"
        for canon, freq, prio in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n"
            "</urlset>\n")


def robots():
    return ("User-agent: *\n"
            "Allow: /\n\n"
            "# Generated pages only; the brand library and build tools are not content.\n"
            "Disallow: /assets/brand/\n"
            "Disallow: /tools/\n\n"
            f"Sitemap: {DOMAIN}/sitemap.xml\n")


def redirects():
    """The six INTEGRI-era division pages retired in the rebrand.

    They were live and may still be linked or indexed, so each goes to its
    nearest surviving division rather than to a 404. 301 because the move is
    permanent. Both the extensionless and .html forms are listed: the host
    canonicalises to extensionless, but an old inbound link may carry either.
    """
    moved = [
        ("/services/investigation", "/services/investigations"),
        ("/services/forensic", "/services/investigations"),
        ("/services/polygraph", "/services/investigations"),
        ("/services/protection", "/services/close-protection"),
        ("/services/security", "/services/guarding"),
        ("/services/specialized", "/services/mining-security"),
    ]
    lines = ["# Retired INTEGRI-era division pages. See BRAND.md section 4.",
             "# These URLs were live, so they redirect rather than 404."]
    for old, new in moved:
        lines.append(f"{old:32s} {new:32s} 301")
        lines.append(f"{old + '.html':32s} {new:32s} 301")
    return "\n".join(lines) + "\n"


def headers():
    """Cloudflare Pages / Workers Assets `_headers`.

    The hashed-name trick is not in play here, so the long immutable cache is
    scoped to images only; CSS and JS get a week, because they change with
    content and a stale stylesheet is a broken page rather than a stale picture.
    """
    return (
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: geolocation=(), microphone=(), camera=()\n"
        "  Strict-Transport-Security: max-age=31536000; includeSubDomains\n"
        "\n"
        "/assets/img/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/assets/css/*\n"
        "  Cache-Control: public, max-age=604800\n"
        "\n"
        "/assets/js/*\n"
        "  Cache-Control: public, max-age=604800\n")


# ---------------------------------------------------------------------------
# Legal pages
# ---------------------------------------------------------------------------
# Written against what this site ACTUALLY does, which is unusually little:
#
#   * it sets no cookies and runs no analytics
#   * the contact form is a mailto: handoff, so the message is composed in the
#     visitor's own mail client and this site never receives or stores it
#   * it does load Google Fonts, which is a third-party request
#
# Saying otherwise would be as much a fabrication as an invented certification,
# so the notice describes exactly that and nothing more. It is a plain-language
# draft, not legal advice: the client should have it reviewed before relying on
# it, and BRAND.md section 7 lists what they still owe.
LAST_REVIEWED = "August 2026"
REGULATOR = "enquiries@inforegulator.org.za"


def legal_page(slug, title, desc, eyebrow, h1a, h1b, lead, blocks):
    """One legal page. `blocks` is a list of (heading, [html paragraphs])."""
    p = ""
    body = []
    for heading, paras in blocks:
        body.append(f'        <h2 class="section__title section__title--sm">{heading}</h2>')
        body.extend(f"        <p>{t}</p>" for t in paras)
    return head(p, f"{title} | {BRAND}", desc, f"/{slug}") + header(p) + f'''  <main id="main">

    <section class="page-hero page-hero--short">
      <div class="wrap page-hero__inner">
        <nav class="breadcrumb" aria-label="Breadcrumb">
          <a href="index.html">Home</a>
          <span class="sep" aria-hidden="true">&#9670;</span>
          <span aria-current="page">{title}</span>
        </nav>

        <span class="eyebrow">{eyebrow}</span>
        <h1 class="page-hero__title reveal">{h1a} <span class="grad">{h1b}</span></h1>
        <p class="page-hero__lead reveal" style="--d:.08s">{lead}</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="legal prose reveal">
{chr(10).join(body)}
          <p class="legal__stamp">Last reviewed {LAST_REVIEWED}. This notice describes how
             this website works. It is written in plain language and is not legal advice.</p>
        </div>
      </div>
    </section>

''' + footer(p)


def page_privacy():
    return legal_page(
        "privacy", "Privacy Policy",
        f"How {BRAND} handles personal information, and your rights under POPIA. "
        "This website sets no cookies and runs no analytics.",
        "Privacy", "Privacy and", "personal information.",
        "This notice explains what happens to personal information when you use this "
        "website or contact us, and what your rights are under the Protection of "
        "Personal Information Act, 2013 (POPIA).",
        [
            ("Who is responsible", [
                f"{BRAND} is the responsible party for personal information processed "
                "through this website and through enquiries made to us.",
                f"Address: {ADDRESS}. Email: "
                f'<a href="mailto:{EMAIL}">{EMAIL}</a>.',
                "Under POPIA the head of a private body is the Information Officer "
                "until another person is formally designated and registered with the "
                "Information Regulator. Our directors therefore act as Information "
                f'Officer and can be reached at <a href="mailto:{EMAIL}">{EMAIL}</a>.',
            ]),
            ("What this website collects", [
                "<strong>Nothing automatically, beyond ordinary server logs.</strong> "
                "This site sets no cookies, uses no analytics, no advertising pixels "
                "and no tracking of any kind. Nothing you do here is profiled.",
                "Our hosting provider keeps standard server logs, which include IP "
                "addresses and the pages requested. These are used to keep the site "
                "available and secure, not to identify visitors.",
                "The site loads its typefaces from Google Fonts. That request reaches "
                "Google's servers and, like any web request, exposes your IP address "
                "to them. We receive nothing from it.",
                "A single item may be stored in your browser: if you dismiss the "
                "privacy notice, that dismissal is remembered in your browser's local "
                "storage so it does not reappear. It never leaves your device and we "
                "cannot read it.",
            ]),
            ("The contact form", [
                "<strong>The form on our contact page does not submit anything to this "
                "website.</strong> It assembles what you typed into a message and opens "
                "it in your own email application, for you to send. Until you press "
                "send in your own mail client, nothing has been transmitted, and this "
                "site never receives or stores what you typed.",
                "Once you do email us, we hold what you sent: your name, your email "
                "address, and whatever you chose to tell us. We use it to answer you "
                "and to carry out any work you engage us for.",
            ]),
            ("Information we hold about clients", [
                "Where you engage us, we hold what the mandate requires. That varies by "
                "service and can include the information you give us and the material "
                "produced during the work.",
                "Our work is confidential by nature. Information is compartmentalised, "
                "teams are briefed on a need-to-know basis, and files stay inside a "
                "small, accountable team.",
                "We do not sell personal information, and we do not share it for "
                "marketing.",
            ]),
            ("Why we may share information", [
                "We share personal information only where it is necessary to do the "
                "work you have engaged us for, where you have asked us to, or where the "
                "law requires it. That last case includes a lawful request from a court "
                "or a competent authority.",
            ]),
            ("How long we keep it", [
                "Enquiries that do not become work are kept only as long as they are "
                "useful to answer, then deleted. Records relating to work we have done "
                "are kept for as long as we may be required to account for that work, "
                "and then deleted.",
            ]),
            ("Your rights under POPIA", [
                "You may ask what personal information we hold about you and ask for a "
                "copy of it. You may ask us to correct it, or to delete information we "
                "no longer have grounds to keep. You may object to processing in the "
                "circumstances POPIA allows.",
                f'To exercise any of these, write to <a href="mailto:{EMAIL}">{EMAIL}</a>. '
                "We may need to confirm who you are before we act, precisely because "
                "acting on an unverified request would itself be a breach.",
                "If you are not satisfied with how we have handled your information you "
                "may complain to the Information Regulator of South Africa: "
                f'<a href="mailto:{REGULATOR}">{REGULATOR}</a>, '
                '<a href="https://inforegulator.org.za" rel="noopener noreferrer" '
                'target="_blank">inforegulator.org.za</a>.',
            ]),
            ("Security", [
                "We take reasonable technical and organisational steps to protect "
                "personal information. This site is served over HTTPS.",
                "No system is perfectly secure, and we will not claim otherwise. If a "
                "breach affects your personal information we will notify you and the "
                "Information Regulator as POPIA requires.",
            ]),
            ("Changes", [
                "If this notice changes materially we will update the review date at "
                "the foot of this page.",
            ]),
        ])


def page_terms():
    return legal_page(
        "terms", "Terms of Use",
        f"The terms on which you may use the {BRAND} website.",
        "Terms", "Terms of", "use.",
        "These terms apply to your use of this website. They do not govern any security "
        "work we carry out for you: that is covered by the separate written agreement "
        "for the mandate.",
        [
            ("The website is information, not an offer", [
                "The pages here describe the services we offer. Nothing on this website "
                "is an offer capable of acceptance, a quotation, or a commitment that we "
                "will take on a particular mandate.",
                "Whether we can act, and on what terms, is agreed in writing for each "
                "engagement after we understand the requirement.",
            ]),
            ("No advice", [
                "Nothing on this website is security, legal or risk advice for your "
                "specific circumstances. Security decisions depend on facts we do not "
                "have until we assess them with you. Do not act on general information "
                "here in place of an assessment.",
            ]),
            ("Accuracy", [
                "We take care that these pages are accurate and keep them up to date. "
                "Descriptions of our services are general, and the detail of what we do "
                "on any mandate is set by that mandate.",
            ]),
            ("Your use of the site", [
                "You may read, print and share these pages. You may not attempt to "
                "interfere with the site, gain unauthorised access to it or to any system "
                "connected to it, or use it to send unlawful or abusive material.",
            ]),
            ("Our material", [
                f"The text, layout, logo and artwork on this site belong to {BRAND} or "
                "are used with permission. Do not reproduce the branding or present it "
                "as your own.",
            ]),
            ("Links out", [
                "Where we link to another site, we do not control it and are not "
                "responsible for its content.",
            ]),
            ("Governing law", [
                "These terms are governed by the law of the Republic of South Africa.",
            ]),
        ])


def page_paia():
    return legal_page(
        "paia", "Access to Information",
        f"How to request access to records held by {BRAND} under PAIA.",
        "PAIA", "Access to", "information.",
        "The Promotion of Access to Information Act, 2000 (PAIA) gives you a route to "
        "request records held by a private body. This page explains how to make such a "
        "request to us.",
        [
            ("How to make a request", [
                "Write to our Information Officer at "
                f'<a href="mailto:{EMAIL}">{EMAIL}</a>, or to {ADDRESS}.',
                "Tell us which record you want, in enough detail that we can identify "
                "it; how you would like to receive it; your contact details; and, where "
                "the request is to exercise or protect a right, which right and how the "
                "record is required for it.",
            ]),
            ("What happens next", [
                "We will respond within the period PAIA allows, and tell you whether we "
                "can grant the request. Where a fee is payable under the Act we will "
                "tell you what it is before we proceed.",
                "PAIA permits and in some cases requires a request to be refused, for "
                "example where a record contains someone else's personal information or "
                "would prejudice a third party. Where we refuse, we will tell you the "
                "grounds and how to appeal.",
            ]),
            ("Confidentiality is not a blanket answer", [
                "Our work is confidential, but confidentiality is not by itself a reason "
                "to refuse a PAIA request. Each request is considered against the "
                "grounds the Act sets out.",
            ]),
            ("Our PAIA manual", [
                "Our manual under section 51 of the Act is available on request from "
                f'<a href="mailto:{EMAIL}">{EMAIL}</a>.',
            ]),
            ("The Information Regulator", [
                "PAIA is overseen by the Information Regulator of South Africa: "
                f'<a href="mailto:{REGULATOR}">{REGULATOR}</a>, '
                '<a href="https://inforegulator.org.za" rel="noopener noreferrer" '
                'target="_blank">inforegulator.org.za</a>.',
            ]),
        ])


def main():
    written = []

    def w(relpath, body):
        full = os.path.join(ROOT, relpath)
        if os.path.dirname(full):
            os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(body)
        written.append((relpath, len(body)))

    # one list drives both the pages and the sitemap
    pages = [
        ("index.html", "/", page_home, "monthly", "1.0"),
        ("about.html", "/about", page_about, "yearly", "0.7"),
        ("contact.html", "/contact", page_contact, "yearly", "0.9"),
        ("services/index.html", "/services/", page_services_index, "monthly", "0.9"),
    ]
    for i, d in enumerate(DIVISIONS):
        pages.append((f'services/{d["slug"]}.html', f'/services/{d["slug"]}',
                      (lambda d=d, i=i: page_division(d, i)), "yearly", "0.8"))
    pages += [
        ("privacy.html", "/privacy", page_privacy, "yearly", "0.3"),
        ("terms.html", "/terms", page_terms, "yearly", "0.3"),
        ("paia.html", "/paia", page_paia, "yearly", "0.3"),
    ]

    for relpath, _canon, fn, _freq, _prio in pages:
        w(relpath, fn())

    w("404.html", page_404())          # noindex, and NOT in the sitemap
    w("sitemap.xml", sitemap([(c, f, p) for _r, c, _fn, f, p in pages]))
    w("robots.txt", robots())
    w("_redirects", redirects())
    w("_headers", headers())

    for old in ("investigation", "forensic", "polygraph", "security",
                "protection", "specialized"):
        stale = os.path.join(ROOT, "services", f"{old}.html")
        if os.path.exists(stale):
            os.remove(stale)
            print(f"   removed stale page services/{old}.html")

    print(f"Generated {len(written)} files:")
    for r, n in written:
        print(f"   {r:34s} {n / 1024:7.1f} KB")

    bad = [r for r, _ in written if r.endswith(".html")
           and "—" in open(os.path.join(ROOT, r), encoding="utf-8").read()]
    if bad:
        raise SystemExit("em dash emitted in: " + ", ".join(bad))


if __name__ == "__main__":
    main()

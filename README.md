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
worker/                                   the Worker: routing + the enquiry endpoint
wrangler.jsonc                            Cloudflare config: entry point and assets
.assetsignore                             what is NOT uploaded, i.e. what is not public
tools/                                    generators and the validator
BRAND.md                                  the contract; read it before changing anything
```

## The pages are generated

Ten pages share a header, mobile drawer, icon sprite, footer, action bar and
to-top button. That chrome is emitted from one source, so **do not hand-edit the
HTML**: the next regenerate overwrites it. Edit the generator instead.

```bash
python3 tools/build-brand-assets.py   # logo, favicons, favicon.ico, OG card
python3 tools/build-site.py           # 11 pages + sitemap, robots, _redirects, _headers
python3 tools/validate.py             # must be green before pushing
```

`build-site.py` also emits `sitemap.xml`, `robots.txt`, `404.html`, `_redirects`
and `_headers` from the same page list that builds the pages, so they cannot
drift. Do not hand-edit those either.

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
- an `<img>` whose declared width/height does not match the file's real aspect
- a page missing from `sitemap.xml`, or the 404 wrongly listed in it
- a `_redirects` rule pointing at a page that does not exist
- a missing `robots.txt`, `_headers` or `favicon.ico`
- **a committed API key**, or any string shaped like one
- the contact form's `action` disagreeing with what `worker/index.js` routes
- a `functions/` directory, which is a Pages convention this project cannot use
- `wrangler.jsonc` losing its entry point, or changing `html_handling` or
  `not_found_handling` out from under the site
- `.assetsignore` excluding a file the pages link to, or failing to exclude
  `.git/`

## The contact form

The enquiry form posts to `/api/contact`, handled by the Worker. It validates the
submission, turns it into an email, sends it through [Resend](https://resend.com)
to the ops mailbox, and forgets it. There is no database, no queue and nothing
stored.

It was a `mailto:` handoff before. That only worked for visitors with a desktop
mail client configured: on a phone, or on webmail, pressing send did nothing
while the page still said the message had gone. Enquiries were being lost.

```
contact.html        <form action="/api/contact" method="post">
assets/js/main.js   posts it with fetch and reports what the server said
worker/index.js     routes /api/contact; everything else falls through to ASSETS
worker/contact.js   validates, relays through Resend, answers
```

With JavaScript off the browser posts the form natively and the Worker answers
with a plain confirmation page instead of JSON, so the form still works.

### Configuration (Cloudflare dashboard)

The API key is **never** committed. `tools/validate.py` fails the build if
anything that looks like one appears in a tracked file.

Cloudflare dashboard -> Workers & Pages -> the project -> **Settings** ->
**Variables and secrets** -> Add, for **Production** and **Preview**:

| Name | Type | Value |
|---|---|---|
| `RESEND_API_KEY` | **Secret** | the key from the Resend account |
| `MAIL_FROM` | Text, optional | overrides the default From address |
| `MAIL_TO` | Text, optional | overrides `ops@greymanprotection.co.za` |

Add the key as a **Secret**, not as plaintext: a plaintext variable stays
readable in the dashboard afterwards. Redeploy after adding it, because
variables are bound at deploy time.

Two things must be true in the Resend account or the send is rejected:

1. `greymanprotection.co.za` is a **verified sending domain** (Resend -> Domains,
   then add the DNS records it gives you). Until it is, set `MAIL_FROM` to an
   address on a domain that already is.
2. The key has send permission.

If `RESEND_API_KEY` is absent the endpoint answers `503` and tells the visitor
to email the ops address instead. It never claims to have sent something it did
not send.

### Testing it

```bash
node tools/test-contact-function.mjs   # handler + routing, with Resend stubbed
```

Twenty cases: relay, honeypot, timing trap, rate limit, validation, header
injection, HTML escaping, missing key, provider failure, no-JS HTML response,
and the Worker routing in front of all of it. Nothing leaves the machine and no
real key is needed.

### Abuse

Built in: a honeypot field, a three-second timing trap, a per-isolate IP rate
limit of five in ten minutes, and length caps on every field. The rate limit is
best effort, because it lives in the isolate's memory rather than in KV. If the
form is ever actually abused, add a **WAF rate-limiting rule on `/api/contact`**
in the Cloudflare dashboard: that runs at the edge, before the Worker is
invoked, and needs no code change. Cloudflare Turnstile is the next step after
that, and needs a site key in the page as well as a secret here.

## Deployment

This is a **Cloudflare Worker with static assets**, not a Pages project. The
difference is not cosmetic: on Pages a `functions/` directory becomes routes
automatically, and on Workers it does nothing at all. Routing is explicit, in
`worker/index.js`, and the platform config is `wrangler.jsonc`.

The build runs `npx wrangler versions upload`. Without `wrangler.jsonc` that
command has nothing to upload and fails with *"Missing entry-point to Worker
script or to assets directory"*, which is exactly what happened when the
endpoint was first written as a Pages Function.

```bash
npx wrangler deploy --dry-run    # parses the config and bundles the Worker
python3 tools/validate.py        # must be green before pushing
```

### What actually gets served

`assets.directory` is the repo root, so **`.assetsignore` decides what is
public**. Wrangler walks the directory with a plain recursive readdir and
excludes only `.assetsignore`, `_headers` and `_redirects` on its own: dotfiles
are not excluded, so without an explicit `.git/` line the entire repository
history is uploaded and served. The current list ships 27 files, the pages and
their assets, and nothing else.

Do not trust the `Read N files from the assets directory` line to check this. It
is logged before `.assetsignore` is applied and it counts directories, so it
reads 968 for a 27-file upload. To see the real list:

```bash
WRANGLER_LOG=debug npx wrangler deploy --dry-run 2>&1 | grep "Ignoring asset:"
```

`tools/validate.py` also resolves every file the pages reference against the
ignore patterns, and fails if one of them would be excluded.

### Serving elsewhere

The static site itself is host-agnostic: publish the repo root, no build
command, and the host must serve extensionless URLs (`try_files $uri $uri.html`
on nginx). Only the contact endpoint is Cloudflare-specific, and only in how it
is mounted: `worker/contact.js` is a plain module that takes a `Request` and
returns a `Response`.

Check it after a deploy:

```bash
curl -i https://www.greymanprotection.co.za/api/contact   # expect 405
```

`405` means the Worker is live. `404` means the platform is not running it and
every enquiry is going nowhere.

## Before this goes public

See BRAND.md §6 and §7. In short: the site currently makes **no PSIRA claim and
no company registration claim**, because the company profile supports neither.
Both were on the previous brand's site and neither transfers. The client needs to
supply the certificates before those go back on.

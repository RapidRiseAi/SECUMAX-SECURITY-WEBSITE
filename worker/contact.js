/**
 * POST /api/contact : the enquiry handler.
 *
 * Takes the contact-page form and relays it to the ops mailbox through Resend.
 * Nothing is stored: the request is validated, turned into an email, and
 * dropped. There is no database and no queue, so there is nothing here to leak.
 *
 * Mounted by worker/index.js. It is a plain module that takes a Request and
 * returns a Response, with no platform-specific API in it, which is why it can
 * be exercised under bare Node by tools/test-contact-function.mjs.
 *
 * Configuration lives entirely in Cloudflare environment variables. The API key
 * is NEVER committed:
 *
 *   RESEND_API_KEY   required. Cloudflare dashboard -> Workers & Pages -> the
 *                    project -> Settings -> Variables and Secrets -> add as a
 *                    SECRET, for both Production and Preview. Not a plaintext
 *                    variable: plaintext values stay readable in the dashboard.
 *   MAIL_FROM        optional. Defaults to the value below. Must be on a domain
 *                    verified in the Resend account, or Resend rejects the send.
 *   MAIL_TO          optional. Defaults to the ops mailbox.
 *
 * If RESEND_API_KEY is absent the endpoint answers 503 and says so, rather than
 * pretending to have sent something. A form that silently swallows enquiries is
 * worse than one that is plainly switched off.
 */

const TO_DEFAULT = "ops@greymanprotection.co.za";

// The From address must sit on a domain VERIFIED in the Resend account, or the
// send is rejected outright. This account is shared with the Rapid Rise AI site
// and rapidriseai.com is the verified domain, so that is what sends.
//
// It reads slightly oddly for a Greyman email to come from rapidriseai.com, and
// that is a deliverability constraint rather than a choice: an unverified From
// domain does not fail quietly, it fails completely. The display name carries
// the context, and Reply-To is set to the enquirer below, so hitting reply in
// the ops mailbox still answers the right person.
//
// To move it onto the client's own domain: verify greymanprotection.co.za in
// Resend (Domains, then add the DNS records it gives you), then either change
// this line or set MAIL_FROM in the Cloudflare runtime variables. Do not change
// it before the domain is verified.
const FROM_DEFAULT = "Greyman Protection website <team@rapidriseai.com>";

const SITE = "https://www.greymanprotection.co.za";

const LIMITS = { name: 120, email: 160, phone: 40, service: 80, message: 5000 };

/* ---------------------------------------------------------------------------
 * Rate limiting.
 *
 * Best effort, and worth being honest about what that means: this counter lives
 * in the isolate's memory. Cloudflare runs many isolates across many locations
 * and recycles them freely, so a determined flood from several sources will not
 * all land on the same counter. What it does reliably stop is the common case,
 * one script hammering the endpoint in a loop, and it costs nothing.
 *
 * Durable limiting needs a KV or Durable Object binding. If the form is ever
 * actually abused, add a Cloudflare WAF rate-limiting rule on /api/contact in
 * the dashboard: that runs at the edge, before this function is even invoked.
 * ------------------------------------------------------------------------- */
const WINDOW_MS = 10 * 60 * 1000;
const MAX_PER_WINDOW = 5;
const hits = new Map();

function rateLimited(ip) {
  if (!ip) return false;
  const now = Date.now();
  const seen = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  seen.push(now);
  hits.set(ip, seen);
  // Keep the map from growing without bound in a long-lived isolate.
  if (hits.size > 5000) {
    for (const [k, v] of hits) {
      if (!v.length || now - v[v.length - 1] > WINDOW_MS) hits.delete(k);
    }
  }
  return seen.length > MAX_PER_WINDOW;
}

/* --------------------------------------------------------------------------- */

const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

// Strip CR/LF from anything that goes into a header-like field. Resend takes
// JSON rather than raw SMTP, so this is belt and braces, but a newline in a
// subject or a display name is the classic header-injection route and it costs
// one regex to make it impossible.
const oneLine = (s) => String(s).replace(/[\r\n]+/g, " ").trim();

function wantsJSON(request) {
  const a = request.headers.get("Accept") || "";
  return a.includes("application/json") ||
    request.headers.get("X-Requested-With") === "fetch";
}

function jsonResponse(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

// The no-JavaScript path. A browser that posted the form natively gets a page,
// not a JSON blob. Deliberately self-contained and unstyled beyond the basics:
// it is a fallback, it must never depend on the stylesheet loading.
function htmlResponse(status, heading, body) {
  const page = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>${esc(heading)} | Greyman Protection</title>
<style>
  html{background:#0B0B0D;color:#EDEDF0;font:16px/1.6 system-ui,sans-serif}
  body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px}
  main{max-width:34rem;text-align:center}
  h1{font-size:1.6rem;letter-spacing:.02em;margin:0 0 .6rem}
  p{color:#8E8E99;margin:0 0 1.6rem}
  a{color:#4D7CFF}
</style></head>
<body><main>
<h1>${esc(heading)}</h1>
<p>${body}</p>
<p><a href="${SITE}/contact">Back to the contact page</a></p>
</main></body></html>`;
  return new Response(page, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

function reply(request, status, ok, message, heading) {
  return wantsJSON(request)
    ? jsonResponse(status, { ok, message })
    : htmlResponse(status, heading || (ok ? "Enquiry sent" : "Not sent"), message);
}

/** One handler for every method, dispatching on `request.method` itself. */
export async function handleContact(context) {
  const { request, env } = context;
  if (request.method === "POST") return handlePost(context);
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: { Allow: "POST, OPTIONS" } });
  }
  // Anything else. Answering here rather than falling through keeps a stray GET
  // from returning the site's 404 page, which would look like the endpoint does
  // not exist at all.
  //
  // `config` answers one question that the dashboard cannot: what does the
  // RUNNING Worker actually see? Cloudflare has two separate "Variables and
  // secrets" sections, one under Builds that only the build process can read,
  // and a saved value looks identical in both. `bindings` lists the NAMES of
  // what is bound, never a value, so a key in the wrong section or a mistyped
  // name is visible from outside without anyone reading a secret.
  return jsonResponse(405, {
    ok: false,
    message: "Post the contact form to this endpoint.",
    config: {
      mailConfigured: Boolean(env && env.RESEND_API_KEY),
      bindings: env ? Object.keys(env).sort() : [],
    },
  });
}

async function handlePost({ request, env }) {
  const to = env.MAIL_TO || TO_DEFAULT;
  const from = env.MAIL_FROM || FROM_DEFAULT;

  if (!env.RESEND_API_KEY) {
    return reply(request, 503, false,
      `The enquiry form is not configured yet. Please email <a href="mailto:${to}">${to}</a> directly.`,
      "Form unavailable");
  }

  // Parse either an HTML form post or a JSON body.
  let data;
  try {
    const ct = request.headers.get("Content-Type") || "";
    if (ct.includes("application/json")) {
      data = await request.json();
    } else {
      const fd = await request.formData();
      data = Object.fromEntries(fd.entries());
    }
  } catch {
    return reply(request, 400, false, "We could not read that submission.");
  }

  const get = (k) => oneLine(data[k] == null ? "" : data[k]).slice(0, LIMITS[k] || 200);
  const name = get("name");
  const email = get("email");
  const phone = get("phone");
  const service = get("service");
  const message = String(data.message == null ? "" : data.message)
    .trim().slice(0, LIMITS.message);

  // ---- 1. honeypot. Silently accepted so the bot has nothing to tune against.
  if (oneLine(data.company || "")) {
    return reply(request, 200, true, "Thank you. Your enquiry has been sent.");
  }

  // ---- 2. time trap. `ts` is stamped by the page's script when the form is
  // ready. A real person needs seconds to type; a script posts instantly. With
  // JavaScript off there is no stamp at all, so a missing value must pass.
  const ts = Number(data.ts);
  if (Number.isFinite(ts) && ts > 0 && Date.now() - ts < 3000) {
    return reply(request, 200, true, "Thank you. Your enquiry has been sent.");
  }

  // ---- 3. rate limit.
  const ip = request.headers.get("CF-Connecting-IP") || "";
  if (rateLimited(ip)) {
    return reply(request, 429, false,
      `That is a lot of enquiries in a short time. Please try again shortly, or email <a href="mailto:${to}">${to}</a>.`,
      "Too many requests");
  }

  // ---- 4. validation, matching what the page checks so the two agree.
  if (!name || !email || !message) {
    return reply(request, 400, false,
      "Please complete your name, email address and message.");
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return reply(request, 400, false,
      "That email address does not look right. Please check it.");
  }

  const country = request.headers.get("CF-IPCountry") || "unknown";
  const subject = `Website enquiry${service ? ": " + service : ""} from ${name}`;

  const text = [
    `Name:    ${name}`,
    `Email:   ${email}`,
    phone ? `Phone:   ${phone}` : null,
    service ? `Service: ${service}` : null,
    "",
    message,
    "",
    "--",
    `Sent from the enquiry form at ${SITE}/contact`,
    `Country: ${country}   Received: ${new Date().toISOString()}`,
  ].filter((l) => l !== null).join("\n");

  const html = `<div style="font:15px/1.6 system-ui,sans-serif;color:#111">
<h2 style="margin:0 0 12px;font-size:17px">Website enquiry</h2>
<table cellpadding="0" cellspacing="0" style="border-collapse:collapse">
<tr><td style="padding:2px 14px 2px 0;color:#666">Name</td><td>${esc(name)}</td></tr>
<tr><td style="padding:2px 14px 2px 0;color:#666">Email</td><td><a href="mailto:${esc(email)}">${esc(email)}</a></td></tr>
${phone ? `<tr><td style="padding:2px 14px 2px 0;color:#666">Phone</td><td>${esc(phone)}</td></tr>` : ""}
${service ? `<tr><td style="padding:2px 14px 2px 0;color:#666">Service</td><td>${esc(service)}</td></tr>` : ""}
</table>
<p style="white-space:pre-wrap;margin:18px 0 0">${esc(message)}</p>
<hr style="border:none;border-top:1px solid #ddd;margin:22px 0 10px">
<p style="color:#888;font-size:12px;margin:0">
Sent from the enquiry form at ${SITE}/contact<br>
Country: ${esc(country)} &middot; Received: ${new Date().toISOString()}
</p></div>`;

  let res;
  try {
    res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from,
        to: [to],
        // So hitting reply in the ops mailbox answers the enquirer, not the
        // noreply sender. The display name is stripped of newlines above.
        reply_to: `${name} <${email}>`,
        subject,
        text,
        html,
      }),
    });
  } catch {
    return reply(request, 502, false,
      `We could not send that just now. Please email <a href="mailto:${to}">${to}</a> directly.`,
      "Not sent");
  }

  if (!res.ok) {
    // Log the provider's reason for the Pages tail, but never return it: it can
    // carry configuration detail, and the visitor can do nothing with it.
    let detail = "";
    try { detail = (await res.text()).slice(0, 500); } catch { /* ignore */ }
    console.error("resend failed", res.status, detail);
    return reply(request, 502, false,
      `We could not send that just now. Please email <a href="mailto:${to}">${to}</a> directly.`,
      "Not sent");
  }

  return reply(request, 200, true,
    "Thank you. Your enquiry has been sent and we will come back to you.");
}

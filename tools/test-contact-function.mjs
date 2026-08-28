/**
 * Exercise worker/contact.js without deploying it.
 *
 *     node tools/test-contact-function.mjs
 *
 * The handler is a plain module that takes a Request and returns a Response, so
 * it runs under Node 18+ as-is. `fetch` is stubbed, so nothing leaves the
 * machine and no real key is needed: the stub records what would have been sent
 * to Resend and the assertions check that payload.
 *
 * Exits non-zero on the first failure, so it can gate a commit.
 */
import { handleContact } from "../worker/contact.js";

let sent = null;
let nextResendStatus = 200;
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  if (String(url).startsWith("https://api.resend.com")) {
    sent = { url: String(url), init, body: JSON.parse(init.body) };
    return new Response(JSON.stringify({ id: "stub" }), { status: nextResendStatus });
  }
  return realFetch(url, init);
};

const ENV = { RESEND_API_KEY: "re_stub_key_not_real" };

// Each call gets its own client address unless the test names one. Sharing an
// address across tests silently trips the rate limiter partway through the run,
// which then fails whichever assertions happen to come last.
let ipSeq = 0;
const nextIp = () => `203.0.113.${(ipSeq++ % 250) + 1}`;

function post(fields, { json = true, env = ENV, headers = {} } = {}) {
  const fd = new FormData();
  for (const [k, v] of Object.entries(fields)) fd.set(k, v);
  const h = { "CF-Connecting-IP": nextIp(), "CF-IPCountry": "ZA", ...headers };
  if (json) h["Accept"] = "application/json";
  return handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact", {
      method: "POST", body: fd, headers: h,
    }),
    env,
  });
}

const GOOD = {
  name: "Thandi Mokoena",
  email: "thandi@example.co.za",
  phone: "+27 82 000 0000",
  service: "Special Investigations",
  message: "We need a vetting check on three candidates.",
  company: "",
  ts: String(Date.now() - 30000),
};

let failures = 0;
async function check(label, fn) {
  try {
    await fn();
    console.log(`  ok    ${label}`);
  } catch (e) {
    failures++;
    console.log(`  FAIL  ${label}\n          ${e.message}`);
  }
}
const eq = (got, want, what) => {
  if (got !== want) throw new Error(`${what}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`);
};
const has = (hay, needle, what) => {
  if (!String(hay).includes(needle)) throw new Error(`${what}: ${JSON.stringify(needle)} not found`);
};

console.log("worker/contact.js");

await check("a good submission is relayed to Resend and reports success", async () => {
  sent = null;
  const res = await post(GOOD);
  const body = await res.json();
  eq(res.status, 200, "status");
  eq(body.ok, true, "ok flag");
  if (!sent) throw new Error("Resend was never called");
  eq(sent.body.to[0], "ops@greymanprotection.co.za", "recipient");
  eq(sent.init.headers.Authorization, "Bearer re_stub_key_not_real", "auth header");
  has(sent.body.reply_to, "thandi@example.co.za", "reply-to");
  has(sent.body.subject, "Special Investigations", "subject");
  has(sent.body.text, "We need a vetting check", "text body");
  has(sent.body.text, "+27 82 000 0000", "phone in body");
  has(sent.body.html, "Thandi Mokoena", "html body");
});

await check("the honeypot is dropped silently, and nothing is sent", async () => {
  sent = null;
  const res = await post({ ...GOOD, company: "Acme Ltd" });
  const body = await res.json();
  eq(res.status, 200, "status");           // the bot is told it worked
  eq(body.ok, true, "ok flag");
  if (sent) throw new Error("a honeypot hit reached Resend");
});

await check("an instant submission is dropped as automated", async () => {
  sent = null;
  const res = await post({ ...GOOD, ts: String(Date.now()) });
  eq(res.status, 200, "status");
  if (sent) throw new Error("a sub-3s submission reached Resend");
});

await check("a submission with no timestamp still goes through (no-JS visitor)", async () => {
  sent = null;
  const res = await post({ ...GOOD, ts: "" });
  eq(res.status, 200, "status");
  if (!sent) throw new Error("a no-JS submission was dropped");
});

await check("missing fields are refused", async () => {
  sent = null;
  const res = await post({ ...GOOD, message: "" });
  const body = await res.json();
  eq(res.status, 400, "status");
  eq(body.ok, false, "ok flag");
  if (sent) throw new Error("an incomplete submission reached Resend");
});

await check("a malformed email address is refused", async () => {
  sent = null;
  const res = await post({ ...GOOD, email: "not-an-address" });
  eq(res.status, 400, "status");
  if (sent) throw new Error("a bad address reached Resend");
});

await check("header injection in the name is neutralised", async () => {
  sent = null;
  await post({ ...GOOD, name: "Eve\r\nBcc: victim@example.com" });
  if (!sent) throw new Error("Resend was never called");
  if (/[\r\n]/.test(sent.body.reply_to) || /[\r\n]/.test(sent.body.subject)) {
    throw new Error("CR/LF survived into reply_to or subject");
  }
});

await check("HTML in the message is escaped in the HTML part", async () => {
  sent = null;
  await post({ ...GOOD, message: '<img src=x onerror="alert(1)">' });
  has(sent.body.html, "&lt;img", "escaped tag");
  if (sent.body.html.includes("<img src=x")) throw new Error("raw tag survived into the html part");
});

await check("no key configured means an honest 503, not a fake success", async () => {
  sent = null;
  const res = await post(GOOD, { env: {} });
  const body = await res.json();
  eq(res.status, 503, "status");
  eq(body.ok, false, "ok flag");
  has(body.message, "ops@greymanprotection.co.za", "fallback address");
  if (sent) throw new Error("Resend was called without a key");
});

await check("a Resend failure is reported as a failure", async () => {
  nextResendStatus = 422;
  const res = await post({ ...GOOD, email: "someone.else@example.com" });
  const body = await res.json();
  nextResendStatus = 200;
  eq(res.status, 502, "status");
  eq(body.ok, false, "ok flag");
  has(body.message, "ops@greymanprotection.co.za", "fallback address");
});

await check("the rate limit trips after six sends from one address", async () => {
  const ip = "198.51.100.7";
  let last;
  for (let i = 0; i < 7; i++) {
    last = await post({ ...GOOD, email: `x${i}@example.com` }, { headers: { "CF-Connecting-IP": ip } });
  }
  eq(last.status, 429, "status on the seventh");
});

await check("a browser posting the form natively gets HTML, not JSON", async () => {
  const res = await post({ ...GOOD, email: "html@example.com" }, { json: false });
  eq(res.headers.get("Content-Type"), "text/html; charset=utf-8", "content type");
  const body = await res.text();
  has(body, "<!doctype html>", "doctype");
  has(body, "Enquiry sent", "confirmation heading");
  has(body, "/contact", "link back");
});

await check("GET is answered with 405, not the site 404", async () => {
  const res = await handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact"),
    env: ENV,
  });
  eq(res.status, 405, "status");
});

await check("GET reports whether the running Worker can see a key", async () => {
  const withKey = await (await handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact"),
    env: { RESEND_API_KEY: "re_stub_key_not_real", ASSETS: {} },
  })).json();
  eq(withKey.config.mailConfigured, true, "mailConfigured with a key");
  eq(withKey.config.bindings.join(","), "ASSETS,RESEND_API_KEY", "binding names");

  const without = await (await handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact"),
    env: { ASSETS: {} },
  })).json();
  eq(without.config.mailConfigured, false, "mailConfigured with no key");
});

await check("the diagnostic never returns a secret's value", async () => {
  const body = await (await handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact"),
    env: { RESEND_API_KEY: "re_a_very_secret_value_here", ASSETS: {} },
  })).text();
  if (body.includes("re_a_very_secret_value_here")) {
    throw new Error("the key's VALUE leaked into the diagnostic response");
  }
});

await check("a JSON body is accepted as well as a form post", async () => {
  sent = null;
  const res = await handleContact({
    request: new Request("https://www.greymanprotection.co.za/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json",
                 "CF-Connecting-IP": "192.0.2.55" },
      body: JSON.stringify({ ...GOOD, email: "json@example.com" }),
    }),
    env: ENV,
  });
  eq(res.status, 200, "status");
  if (!sent) throw new Error("a JSON submission never reached Resend");
});

await check("an oversized message is truncated rather than relayed whole", async () => {
  sent = null;
  await post({ ...GOOD, email: "long@example.com", message: "x".repeat(20000) });
  if (sent.body.text.split("\n").find((l) => l.length > 5001)) {
    throw new Error("the message was not capped at 5000 characters");
  }
});

/* ---------------------------------------------------------------------------
 * worker/index.js: the routing in front of the handler.
 *
 * This is the part that was wrong the first time round. The handler was written
 * as a Pages Function under `functions/`, which this project does not use, so it
 * would never have been reached in production however well it worked in
 * isolation. Test the wiring, not just the thing it wires up.
 * ------------------------------------------------------------------------- */
const { default: worker } = await import("../worker/index.js");

console.log("\nworker/index.js");

function envWithAssets() {
  const asked = [];
  return {
    asked,
    RESEND_API_KEY: "re_stub_key_not_real",
    ASSETS: {
      fetch: async (req) => {
        asked.push(new URL(req.url).pathname);
        return new Response("static asset", { status: 200 });
      },
    },
  };
}

await check("a page request is served by the asset layer, not the handler", async () => {
  const env = envWithAssets();
  const res = await worker.fetch(
    new Request("https://www.greymanprotection.co.za/contact"), env, {});
  eq(res.status, 200, "status");
  eq(await res.text(), "static asset", "body came from ASSETS");
  eq(env.asked.join(","), "/contact", "ASSETS was asked for the page");
});

await check("POST /api/contact reaches the handler and is relayed", async () => {
  sent = null;
  const env = envWithAssets();
  const fd = new FormData();
  for (const [k, v] of Object.entries({ ...GOOD, email: "routed@example.com" })) fd.set(k, v);
  const res = await worker.fetch(
    new Request("https://www.greymanprotection.co.za/api/contact", {
      method: "POST", body: fd,
      headers: { Accept: "application/json", "CF-Connecting-IP": "192.0.2.99" },
    }), env, {});
  eq(res.status, 200, "status");
  if (!sent) throw new Error("the request never reached the contact handler");
  eq(sent.body.to[0], "ops@greymanprotection.co.za", "recipient");
  eq(env.asked.length, 0, "the asset layer was not involved");
});

await check("an unknown /api/ path is a JSON 404, not the site's 404 page", async () => {
  const env = envWithAssets();
  const res = await worker.fetch(
    new Request("https://www.greymanprotection.co.za/api/nope"), env, {});
  eq(res.status, 404, "status");
  eq((await res.json()).ok, false, "ok flag");
  eq(env.asked.length, 0, "the asset layer was not involved");
});

await check("the form's action and the worker's route are the same path", async () => {
  const html = await import("node:fs").then((fs) =>
    fs.readFileSync(new URL("../contact.html", import.meta.url), "utf-8"));
  const action = /<form[^>]*id="contactForm"[^>]*action="([^"]+)"/.exec(html);
  if (!action) throw new Error("contact.html has no form action to compare against");
  const src = await import("node:fs").then((fs) =>
    fs.readFileSync(new URL("../worker/index.js", import.meta.url), "utf-8"));
  if (!src.includes(`pathname === "${action[1]}"`)) {
    throw new Error(`the form posts to ${action[1]} but worker/index.js does not route it`);
  }
});

console.log(failures ? `\n${failures} failure(s)` : "\nall passed");
process.exit(failures ? 1 : 0);

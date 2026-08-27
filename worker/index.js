/**
 * Worker entry point.
 *
 * This site is a Cloudflare **Worker with static assets**, not a Pages project.
 * The distinction matters and cost a red build to learn: on Pages a `functions/`
 * directory is compiled into routes automatically, on Workers it means nothing
 * at all. Here the routing is explicit and lives in this file.
 *
 * Almost every request is a static file and never reaches this code: the asset
 * layer serves it directly, which is faster and cheaper than invoking a Worker.
 * Only `/api/*` is declared `run_worker_first` in wrangler.jsonc, so the one
 * dynamic path is the only one that pays for a Worker invocation.
 *
 * The `env.ASSETS.fetch` fallback exists for anything else that misses the
 * asset layer. It applies `not_found_handling`, so a genuinely missing URL
 * comes back as the site's own 404 page rather than an empty response.
 */
import { handleContact } from "./contact.js";

export default {
  async fetch(request, env, ctx) {
    const { pathname } = new URL(request.url);

    if (pathname === "/api/contact") {
      return handleContact({ request, env, ctx });
    }

    // Any other /api/* path: answer here rather than serving the 404 page, so a
    // typo in a fetch URL reads as a wrong endpoint instead of a missing site.
    if (pathname.startsWith("/api/")) {
      return new Response(
        JSON.stringify({ ok: false, message: "No such endpoint." }),
        { status: 404, headers: { "Content-Type": "application/json; charset=utf-8" } },
      );
    }

    return env.ASSETS.fetch(request);
  },
};

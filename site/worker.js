/**
 * The Sales Floor board's Worker.
 *
 * ORIGINALLY WRITTEN AS TWO PAGES FUNCTIONS (functions/api/days/index.js and
 * functions/api/days/[day].js). That is the wrong shape for what got
 * provisioned: `flores-board` is a plain Cloudflare Workers project (Workers
 * Builds, Git-connected), not a Pages project, and Workers has no built-in
 * file-based routing for a functions/ folder -- see Cloudflare's own
 * Pages-to-Workers migration guide, which says a functions/ folder must
 * either be compiled with `wrangler pages functions build` or rewritten as a
 * single Worker script. This repo has no npm/wrangler toolchain otherwise
 * (it is a Python project), so rewriting by hand is simpler than adding a
 * compile step for two small routes. Consolidated here 2026-09-05.
 *
 * ROUTING. `/api/days` and `/api/days/:day` are handled below; everything
 * else falls through to the ASSETS binding, which serves site/public/
 * (index.html, the dashboard).
 *
 * THE DATA IS NOT PUBLIC. Everything this Worker serves under /api/days is
 * customer NPI -- lead names, phone numbers, notes on what coverage someone
 * was quoted. The R2 bucket itself is private (no r2.dev URL, no public
 * custom domain) and the whole site is meant to sit behind Cloudflare Access
 * with the agency's Google Workspace as the identity provider. Access does
 * the authentication; this Worker deliberately does NOT re-check identity --
 * if a request reaches it, Access already allowed it, and a second
 * half-implemented check here would be security theatre that drifts out of
 * sync with the real policy. If this Worker is ever put on a route Access
 * does not cover, that assumption breaks and this comment is the reason why.
 *
 * BINDINGS (wrangler.jsonc): `BOARD` -> the flores-board R2 bucket, `ASSETS`
 * -> site/public.
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);

    if (parts[0] === "api" && parts[1] === "days") {
      if (parts.length === 2) return listDays(env);
      if (parts.length === 3) return getDay(env, parts[2]);
      return json({ error: "not found" }, 404);
    }

    return env.ASSETS.fetch(request);
  },
};

/** GET /api/days -> { days: ["2026-09-04", "2026-09-03", ...] }, newest first.
 *
 * The date picker's list. Keys only -- never object bodies, so this stays
 * cheap however many days accumulate. R2 list is paginated (1000 keys per
 * page, about four years of business days); we follow the cursor rather than
 * assuming one page, because the failure mode of not doing so is the picker
 * silently losing its oldest days years from now, which nobody would connect
 * back to this file.
 */
async function listDays(env) {
  const days = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix: "days/", cursor });
    for (const o of listed.objects) {
      const m = o.key.match(/^days\/(\d{4}-\d{2}-\d{2})\.json$/);
      if (m) days.push(m[1]);
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  days.sort().reverse();
  // A new day lands every weekday at ~7 PM Arizona. Caching this for even a
  // minute means someone refreshing at 7:01 does not see tonight.
  return json({ days });
}

/** GET /api/days/:day -> the day document from R2. */
async function getDay(env, day) {
  // Only ever ISO dates. The bucket key is built from user-supplied path, so
  // this is what stops `../` and friends from reaching another prefix.
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }

  const obj = await env.BOARD.get(`days/${day}.json`);
  if (obj === null) {
    // A day with no document is ordinary -- weekends, holidays, and any day
    // before the board went live. The UI shows "no report for this day"
    // rather than an error.
    return json({ error: "no report for this day", day }, 404);
  }

  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      // Never cache a day document at the edge. Tonight's document is
      // rewritten if the run is re-run, and a stale board that disagrees
      // with the email is exactly the failure this whole migration exists
      // to end.
      "cache-control": "no-store",
    },
  });
}

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

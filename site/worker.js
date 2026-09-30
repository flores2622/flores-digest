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
 * THE DATA IS NOT PUBLIC, AND THIS WORKER FAILS CLOSED. Everything served
 * under /api/days is customer NPI -- lead names, phone numbers, notes on what
 * coverage someone was quoted. The R2 bucket itself is private (no r2.dev
 * URL, no public custom domain) and the site is meant to sit behind
 * Cloudflare Access.
 *
 * An earlier version of this comment said the Worker "deliberately does NOT
 * re-check identity" because Access would already have allowed the request,
 * and that a second check would be security theatre. That was wrong in a way
 * worth recording: it assumed Access was configured. On 2026-09-06 it was
 * not -- the Worker was deployed and reachable on its workers.dev URL with no
 * policy in front of it, and the only reason nothing leaked is that the
 * bucket happened to still be empty. One unticked dashboard box was the whole
 * control.
 *
 * So /api/* now verifies the Access JWT itself, and refuses when it cannot:
 *
 *   - ACCESS_TEAM_DOMAIN or ACCESS_AUD unset -> 503, serve no data at all.
 *     Unconfigured means closed, never open. This is what makes the dangerous
 *     window impossible rather than merely unlikely.
 *   - Header/cookie missing, signature bad, aud wrong, expired -> 403.
 *
 * The static shell (index.html) is still served unauthenticated on purpose:
 * it contains no customer data, and letting it load means a misconfiguration
 * shows up as a visible error in the UI instead of a blank page nobody
 * investigates.
 *
 * This is defence in depth, not a replacement for Access. Turn Access on.
 *
 * BINDINGS (wrangler.jsonc): `BOARD` -> the flores-board R2 bucket, `ASSETS`
 * -> site/public.
 * VARS: `ACCESS_TEAM_DOMAIN` (e.g. "floresinsurance" for
 * floresinsurance.cloudflareaccess.com) and `ACCESS_AUD` (the Access
 * application's Application Audience tag). Set both in the Worker's
 * Settings -> Variables. Until they are set, /api/* returns 503.
 */
import METHODOLOGY_MD from "../coaching/METHODOLOGY.md";
import ROLEPLAY_MD from "../coaching/ROLEPLAY.md";
import TRAINING_MD from "../coaching/TRAINING.md";
import { getLive, scheduledLive } from "./live.js";

export default {
  // Live figures between checkpoints (site/live.js): the cron in
  // wrangler.jsonc keeps R2's live/<day>*.json fresh through the business day.
  async scheduled(event, env, ctx) {
    ctx.waitUntil(scheduledLive(event, env));
  },

  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);

    if (parts[0] === "api") {
      // Fail closed BEFORE any bucket read. Every early return below leaves
      // R2 untouched, so a misconfigured or unauthenticated request cannot
      // even cause a lookup, let alone a response body.
      const gate = await requireAccess(request, env);
      if (gate) return gate;

      if (parts[1] === "days") {
        if (parts.length === 2) return listDays(env);
        if (parts.length === 3) return getDay(env, parts[2]);
      }

      if (parts[1] === "months" && parts.length === 3) {
        return getMonth(env, parts[2]);
      }

      if (parts[1] === "live" && parts.length === 3) {
        return getLive(env, parts[2]);
      }
      if (parts[1] === "intraday" && parts.length === 3) {
        return getIntraday(env, parts[2]);
      }

      if (parts[1] === "service") {
        if (parts.length === 2) return listService(env);
        if (parts.length === 3) return getService(env, parts[2]);
      }

      if (parts[1] === "renewals" && parts.length === 2) {
        return getRenewals(env);
      }

      if (parts[1] === "commercial") {
        // Frank's alone (2026-09-24): a second gate on top of Access.
        const deny = requireCommercial(request, env);
        if (deny) return deny;
        if (parts.length === 2) return listCommercial(env);
        if (parts.length === 3) return getCommercial(env, parts[2]);
      }

      if (parts[1] === "recordings" && parts.length === 4) {
        return getRecording(request, env, parts[2], parts[3]);
      }

      if (parts[1] === "training" && parts.length === 2) {
        return json(trainingDecks());
      }

      if (parts[1] === "leadsources" && parts.length === 2) {
        return getLeadSources(env);
      }

      if (parts[1] === "roleplay") {
        if (parts[2] === "turn" && request.method === "POST") {
          return roleplayTurn(request, env);
        }
        if (parts[2] === "grade" && request.method === "POST") {
          return roleplayGrade(request, env);
        }
        if (parts[2] === "history" && request.method === "GET") {
          return roleplayHistory(request, env, url.searchParams.get("producer"), url.searchParams.get("beta") === "1");
        }
        if (parts[2] === "sessions" && request.method === "GET") {
          return roleplaySessions(request, env, url);
        }
        if (parts[2] === "clip" && request.method === "POST") {
          return roleplayClipUpload(request, env, url);
        }
        if (parts[2] === "audio" && request.method === "GET") {
          return roleplayAudio(request, env, url.searchParams.get("key"));
        }
        if (parts[2] === "session" && request.method === "GET") {
          return roleplaySession(request, env, url.searchParams.get("key"));
        }
        if (parts[2] === "face" && parts[3] && parts.length === 4 && request.method === "GET") {
          return roleplayFace(env, parts[3]);
        }
        if (parts[2] === "speak" && request.method === "GET") {
          return roleplaySpeak(env, url, ctx);
        }
        if (parts[2] === "voice-feedback" && request.method === "POST") {
          return roleplayVoiceFeedback(request, env);
        }
        if (parts[2] === "voices" && request.method === "GET") {
          return roleplayVoiceRatings(request, env);
        }
      }

      if (parts[1] === "saleslog" && parts[2] === "folio" && parts[3] && parts.length === 4
          && request.method === "GET") {
        return getSalesLogFolio(env, parts[3]);
      }

      if (parts[1] === "saleslog" && parts[2] && /^\d{4}-\d{2}-\d{2}$/.test(parts[2])) {
        const day = parts[2];
        if (parts.length === 3 && request.method === "GET") {
          return getSalesLog(env, day);
        }
        if (parts.length === 3 && request.method === "POST") {
          return postSalesLog(request, env, day);
        }
        if (parts.length === 4 && parts[3] === "delete" && request.method === "POST") {
          return deleteSalesLogEntry(request, env, day);
        }
        if (parts.length === 4 && parts[3] === "track" && request.method === "POST") {
          return trackSalesLogEntry(request, env, day);
        }
      }
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

/** GET /api/intraday/:day -> that day's latest intraday snapshot, or 404 if
 * intraday.py hasn't run yet today, or the day has already been finalized
 * and intraday.py refused to touch it (see that script's own guard) --
 * either way the UI's fallback is simply not to show a live panel, same as
 * getDay's "no report for this day". A SEPARATE key from days/<day>.json on
 * purpose: an in-progress snapshot must never be servable from, or mistaken
 * for, the finalized document. */
async function getIntraday(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }
  const obj = await env.BOARD.get(`intraday/${day}.json`);
  if (obj === null) {
    return json({ error: "no intraday snapshot for this day", day }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** GET /api/service -> { days: [...] }, newest first -- every day
 * service_digest.py has published. Same paginated key walk as listDays. */
async function listService(env) {
  const days = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix: "service/", cursor });
    for (const o of listed.objects) {
      const m = o.key.match(/^service\/(\d{4}-\d{2}-\d{2})\.json$/);
      if (m) days.push(m[1]);
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  days.sort().reverse();
  return json({ days });
}

/** GET /api/service/:day -> the Service tab's document for that day. */
async function getService(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }
  const obj = await env.BOARD.get(`service/${day}.json`);
  if (obj === null) {
    return json({ error: "no service report for this day", day }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** GET /api/renewals -> the Renewals tab's rolling report (renewal_report.py),
 * rebuilt every night: the last four weeks' renewals and the next 45 days'. */
async function getRenewals(env) {
  const obj = await env.BOARD.get("renewals/current.json");
  if (obj === null) return json({ error: "no renewal report yet" }, 404);
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** GET /api/commercial -> { days: [...] }, newest first -- every day
 * commercial_digest.py (Cerberus) has published. Same walk as listService. */
async function listCommercial(env) {
  const days = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix: "commercial/", cursor });
    for (const o of listed.objects) {
      const m = o.key.match(/^commercial\/(\d{4}-\d{2}-\d{2})\.json$/);
      if (m) days.push(m[1]);
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  days.sort().reverse();
  return json({ days });
}

/** GET /api/commercial/:day -> the Commercial Center's document for that day. */
async function getCommercial(env, day) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }
  const obj = await env.BOARD.get(`commercial/${day}.json`);
  if (obj === null) {
    return json({ error: "no commercial report for this day", day }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

/** GET /api/recordings/:day/:id -> the raw call recording (audio/mpeg),
 * range-aware so an <audio> element can seek. Reads r2_cache's own
 * cache/<day>/audio/<id>.mp3 objects -- the same ones call_summary.py's
 * transcription stage already downloads and, per that module's own
 * docstring, keeps around without ever deleting them (Frank, 2026-09-14:
 * "can we start uploading the recording or transcript to the coaching
 * card" -- they were already durably in R2, just never served anywhere).
 * `id` is a coaching card's own recording_ids entry (coaching_cards.py),
 * never user-typed in the UI, but still validated here since it reaches
 * an R2 key straight from the URL path. */
async function getRecording(request, env, day, id) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || !/^[A-Za-z0-9_-]{1,80}$/.test(id)) {
    return json({ error: "bad day or recording id" }, 400);
  }
  const object = await env.BOARD.get(`cache/${day}/audio/${id}.mp3`, { range: request.headers });
  if (object === null) {
    return json({ error: "recording not found" }, 404);
  }
  const headers = new Headers();
  headers.set("content-type", "audio/mpeg");
  headers.set("accept-ranges", "bytes");
  // Private per Access, not edge-public -- same customer-NPI posture as
  // every other /api/* route (see this file's own top-of-file notice).
  headers.set("cache-control", "private, max-age=3600");
  let status = 200;
  if (object.range) {
    const offset = object.range.offset || 0;
    const length = object.range.length ?? (object.size - offset);
    headers.set("content-range", `bytes ${offset}-${offset + length - 1}/${object.size}`);
    headers.set("content-length", String(length));
    status = 206;
  } else {
    headers.set("content-length", String(object.size));
  }
  return new Response(object.body, { status, headers });
}

/** GET /api/leadsources -> {sources: [...]}, AgencyZoom's own lead source
 * names -- powers the Sales tab's Lead Source dropdown (Frank, 2026-09-14:
 * "which should be a dropdown with the lead sources from agency zoom", not
 * free text). Written by publish_board.publish_lead_sources(), refreshed
 * every time pull_sources() runs (daily.py's nightly build and every
 * intraday.py checkpoint alike) since that's also when the lead corpus
 * itself gets force-refetched. Empty list, not an error, if nothing has
 * published it yet -- the dropdown just renders with nothing but the
 * placeholder option. */
async function getLeadSources(env) {
  const obj = await env.BOARD.get("leadsources.json");
  if (obj === null) return json({ sources: [] });
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function salesLogKey(day) { return `saleslog/${day}.json`; }

/** GET /api/saleslog/:day -> {day, entries: [...]}, [] if nobody has logged
 * anything for that day yet. */
async function getSalesLog(env, day) {
  const obj = await env.BOARD.get(salesLogKey(day));
  if (obj === null) return json({ day, entries: [] });
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

// Mirrors digest_config.FOLIO_CLOSE_DATES (site/public/index.html has its own
// copy too, for the date picker) -- a folio period doesn't align to calendar
// months, so it can't be derived, only listed. Extend this array the same
// day that file's copy is extended.
const FOLIO_CLOSE_DATES = [
  "2026-01-20", "2026-02-18", "2026-03-18", "2026-04-17",
  "2026-05-19", "2026-06-18", "2026-07-17", "2026-08-19",
  "2026-09-18", "2026-10-19", "2026-11-17", "2026-12-17",
];
function folioEndFor(day) {
  return FOLIO_CLOSE_DATES.find(end => day <= end) || null;
}
function folioStartFor(end) {
  const i = FOLIO_CLOSE_DATES.indexOf(end);
  if (i <= 0) return null;   // first folio on file, or not a real close date
  const d = new Date(FOLIO_CLOSE_DATES[i - 1] + "T00:00:00Z");
  d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}

/** GET /api/saleslog/folio/:end -> every saleslog entry logged within the
 * folio ending on `end`, across every day in it, newest-added first (Frank,
 * 2026-09-14: "I want this folios sales sheet to be displayed, sorted from
 * recently added to oldest added").
 *
 * Computed at request time, not from a pre-built rollup: a sales log entry
 * can be added any moment during the day, so a pre-built rollup would go
 * stale the instant someone logs a sale. A folio is at most ~4 weeks, so
 * this is at most ~28
 * R2 reads per request -- cheap, and nobody is hitting this tab hard enough
 * to matter. Each entry carries its own `day` (which key it came from) since
 * a flat merged list would otherwise lose that. */
async function getSalesLogFolio(env, end) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(end) || !FOLIO_CLOSE_DATES.includes(end)) {
    return json({ error: "bad folio end date" }, 400);
  }
  const start = folioStartFor(end);
  const days = [];
  if (start) {
    for (let d = new Date(start + "T00:00:00Z"), endD = new Date(end + "T00:00:00Z");
         d <= endD; d.setUTCDate(d.getUTCDate() + 1)) {
      days.push(d.toISOString().slice(0, 10));
    }
  } else {
    // Unbounded start (this is the first folio FOLIO_CLOSE_DATES knows about)
    // -- walk back from `end` a generous 45 days rather than the whole R2
    // bucket's history, same spirit as publish_board._policy_streaks' own cap.
    for (let d = new Date(end + "T00:00:00Z"), i = 0; i < 45; i++, d.setUTCDate(d.getUTCDate() - 1)) {
      days.push(d.toISOString().slice(0, 10));
    }
  }

  const entries = [];
  for (const day of days) {
    const obj = await env.BOARD.get(salesLogKey(day));
    if (!obj) continue;
    const doc = JSON.parse(await obj.text());
    for (const e of doc.entries || []) entries.push({ ...e, day });
  }
  entries.sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
  return json({
    folio_start: start,
    folio_end: end,
    entries,
  });
}

// The Docs Signed dropdown's exact options, taken from the real Google
// "Sales" sheet's own column (Frank, 2026-09-14: "use the exact options
// from the dropdown on the sales sheet") -- measured directly off 102 real
// rows across two folios rather than guessed: "Docs + Paperless" (41),
// "Producer 1".."Producer 6" (49 combined -- a real, actively-used part of
// the vocabulary, not a fluke), "Paperless" (5), blank (3, the two producer
// names seen once or twice each look like manual typos into the wrong
// column, not real dropdown values, and are deliberately not carried over
// as options). Blank is the default/unset ("pending") state -- nothing in
// 102 rows ever spelled "Pending" outright, they just left it blank until
// it was one of these.
const DOCS_SIGNED_OPTIONS = ["", "Paperless", "Docs + Paperless",
  "Producer 1", "Producer 2", "Producer 3", "Producer 4", "Producer 5", "Producer 6"];

/** POST /api/saleslog/:day {producer, client_name, lead_source,
 * az_customer_id, policy_number, product, premium, term, date_sold,
 * effective_date, notes, docs_signed, review_sent} -> the created entry.
 *
 * A same-day, self-reported log (Frank, 2026-09-12: "I want a sales tab
 * where they go in and enter their sales for the day") -- explicitly NOT
 * the official Premium Sold figure, which stays AgencyZoom-derived as it
 * already is everywhere else on this board.
 *
 * docs_signed/review_sent mirror two of the real Sales sheet's own
 * tracking columns (Frank, 2026-09-14; AZ Profile, the third, removed
 * 2026-09-15 -- "remove the az profile checkbox"); see
 * updateSalesLogEntry, which is what changes them after creation.
 *
 * No AgencyZoom-reconciliation status on this entry (Frank, 2026-09-15:
 * "i dont need that column, and will start working on something similar
 * anyways, remove it") -- an earlier version carried reconciled/
 * az_policy_number/az_source fields meant to be filled in by a
 * sales_log_reconcile.py that was never actually built, so every entry
 * sat "pending" forever. Removed rather than left as dead scaffolding. */
async function postSalesLog(request, env, day) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const producer = String(body.producer || "").trim();
  const client_name = String(body.client_name || "").trim();
  if (!producer || !client_name) {
    return json({ error: "producer and client_name are required" }, 400);
  }
  const premiumNum = Number(body.premium);
  const docsSigned = String(body.docs_signed || "");
  // date_sold/effective_date are plain YYYY-MM-DD strings, same "typed in
  // if known, blank otherwise" pattern as policy_number/product/term below
  // -- an invalid or missing value is just blank, never a 400, since this
  // is a same-day self-reported log, not a validated record.
  const dateSold = String(body.date_sold || "");
  const effectiveDate = String(body.effective_date || "");
  const entry = {
    id: crypto.randomUUID(),
    producer,
    client_name,
    lead_source: String(body.lead_source || "").trim().slice(0, 100),
    // Typed in if known, same as policy_number below -- AgencyZoom policy
    // records carry no customerId (CLAUDE.md's own money rules), so there
    // is no way to look this up server-side from anything else on the
    // entry; it's how the client name links to the real AgencyZoom
    // customer account (Frank, 2026-09-15: "on the name can you link the
    // agency zoom customer account").
    az_customer_id: String(body.az_customer_id || "").trim().slice(0, 40),
    policy_number: String(body.policy_number || "").trim().slice(0, 60),
    product: String(body.product || "").trim().slice(0, 80),
    premium: Number.isFinite(premiumNum) ? premiumNum : null,
    term: String(body.term || "").trim().slice(0, 20),
    date_sold: /^\d{4}-\d{2}-\d{2}$/.test(dateSold) ? dateSold : "",
    effective_date: /^\d{4}-\d{2}-\d{2}$/.test(effectiveDate) ? effectiveDate : "",
    notes: String(body.notes || "").trim().slice(0, 500),
    created_at: new Date().toISOString(),
    docs_signed: DOCS_SIGNED_OPTIONS.includes(docsSigned) ? docsSigned : "",
    review_sent: Boolean(body.review_sent),
  };
  const key = salesLogKey(day);
  const existing = await env.BOARD.get(key);
  const doc = existing ? JSON.parse(await existing.text()) : { day, entries: [] };
  doc.entries.push(entry);
  await env.BOARD.put(key, JSON.stringify(doc), {
    httpMetadata: { contentType: "application/json" },
  });
  return json({ entry });
}

/** POST /api/saleslog/:day/track {id, docs_signed?, review_sent?} -> the
 * updated entry. Changes ONLY these two tracking fields, never the sale
 * record itself (producer/client/premium/etc) (Frank, 2026-09-14: "it
 * should be able to be interactive... when they get signed later they
 * should be able to change it"). */
async function trackSalesLogEntry(request, env, day) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const id = String(body.id || "");
  const key = salesLogKey(day);
  const existing = await env.BOARD.get(key);
  if (!existing) return json({ error: "no entries for this day" }, 404);
  const doc = JSON.parse(await existing.text());
  const target = doc.entries.find((e) => e.id === id);
  if (!target) return json({ error: "entry not found" }, 404);
  if ("review_sent" in body) target.review_sent = Boolean(body.review_sent);
  if ("docs_signed" in body) {
    const v = String(body.docs_signed || "");
    if (!DOCS_SIGNED_OPTIONS.includes(v)) return json({ error: "bad docs_signed value" }, 400);
    target.docs_signed = v;
  }
  await env.BOARD.put(key, JSON.stringify(doc), {
    httpMetadata: { contentType: "application/json" },
  });
  return json({ entry: target });
}

/** POST /api/saleslog/:day/delete {id} -- removes one entry (e.g. a typo'd
 * duplicate). */
async function deleteSalesLogEntry(request, env, day) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const id = String(body.id || "");
  const key = salesLogKey(day);
  const existing = await env.BOARD.get(key);
  if (!existing) return json({ error: "no entries for this day" }, 404);
  const doc = JSON.parse(await existing.text());
  const target = doc.entries.find((e) => e.id === id);
  if (!target) return json({ error: "entry not found" }, 404);
  doc.entries = doc.entries.filter((e) => e.id !== id);
  await env.BOARD.put(key, JSON.stringify(doc), {
    httpMetadata: { contentType: "application/json" },
  });
  return json({ ok: true });
}

/** Parses coaching/TRAINING.md into [{ name, cards: [{ front, back }] }].
 * Static content bundled with the Worker (no R2 read, no per-request
 * computation beyond this parse) -- `## Deck Name` starts a deck, `### Front
 * text` starts a card, everything until the next `###` or `##` is the back.
 * Prose before the first `## ` (the file's own editorial notes) is skipped
 * on purpose -- it's for whoever edits this file next, not the flashcard UI.
 * Cached at module scope: parsed once per Worker isolate, not per request. */
let _trainingCache = null;
function trainingDecks() {
  if (_trainingCache) return _trainingCache;
  const lines = TRAINING_MD.split("\n");
  const decks = [];
  let deck = null, card = null;
  for (const line of lines) {
    const deckMatch = line.match(/^## (.+)/);
    const cardMatch = line.match(/^### (.+)/);
    if (deckMatch) {
      deck = { name: deckMatch[1].trim(), cards: [] };
      decks.push(deck);
      card = null;
    } else if (cardMatch && deck) {
      card = { front: cardMatch[1].trim(), back: "" };
      deck.cards.push(card);
    } else if (card) {
      card.back += (card.back ? "\n" : "") + line;
    }
  }
  for (const d of decks) {
    for (const c of d.cards) c.back = c.back.trim();
  }
  _trainingCache = { decks };
  return _trainingCache;
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


/* -------------------------------------------------------------------------
   Cloudflare Access verification.

   Returns a Response to REFUSE the request, or null to allow it. Written so
   that every path that is not a fully verified identity returns a Response --
   there is no fall-through that reaches the data.
   ------------------------------------------------------------------------- */

let jwksCache = { keys: null, at: 0 };
// The verified Access payload of each request that passed requireAccess(),
// for the few routes that also care WHO is asking (requireCommercial).
const ACCESS_IDENTITY = new WeakMap();
const JWKS_TTL_MS = 60 * 60 * 1000;   // Access rotates keys ~every 6 weeks

async function requireAccess(request, env) {
  const team = env.ACCESS_TEAM_DOMAIN;
  const aud = env.ACCESS_AUD;

  // UNCONFIGURED MEANS CLOSED. If someone deploys this Worker without the
  // Access vars -- or Access is removed and the vars go with it -- the data
  // endpoints stop working rather than becoming public. A loud outage is the
  // correct failure here; a quiet leak is not.
  if (!team || !aud) {
    return json({
      error: "board is not configured for authenticated access",
      detail: "ACCESS_TEAM_DOMAIN and ACCESS_AUD must be set on this Worker. " +
              "Refusing to serve customer data without them.",
    }, 503);
  }

  const token =
    request.headers.get("Cf-Access-Jwt-Assertion") ||
    cookie(request, "CF_Authorization");
  if (!token) return json({ error: "not authenticated" }, 403);

  try {
    const payload = await verifyJwt(token, team, aud);
    if (!payload) return json({ error: "not authenticated" }, 403);
    ACCESS_IDENTITY.set(request, payload);
  } catch (_) {
    // Never surface the reason: a verification oracle is a gift to whoever is
    // probing. The Worker's own logs carry the detail if it is ever needed.
    return json({ error: "not authenticated" }, 403);
  }
  return null;
}

/* The Commercial Center is Frank's alone (2026-09-24). Only the emails in
   COMMERCIAL_VIEWERS (wrangler.jsonc, comma-separated) get /api/commercial;
   everyone else behind Access gets a 403, and the board keeps the section's
   left-bar entry hidden for them. Unset means nobody -- closed, never open.
   Must run AFTER requireAccess(): the email is the verified token's, never a
   header a client could set. */
function requireCommercial(request, env) {
  const who = String((ACCESS_IDENTITY.get(request) || {}).email || "").toLowerCase();
  const allowed = String(env.COMMERCIAL_VIEWERS || "").toLowerCase()
    .split(",").map((x) => x.trim()).filter(Boolean);
  if (!who || !allowed.includes(who)) return json({ error: "not permitted" }, 403);
  return null;
}

function cookie(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return null;
}

function b64urlToBytes(s) {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/")
               .padEnd(s.length + ((4 - (s.length % 4)) % 4), "=");
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function jwks(team) {
  const now = Date.now();
  if (jwksCache.keys && now - jwksCache.at < JWKS_TTL_MS) return jwksCache.keys;
  const r = await fetch(`https://${team}.cloudflareaccess.com/cdn-cgi/access/certs`);
  if (!r.ok) throw new Error(`jwks ${r.status}`);
  const { keys } = await r.json();
  jwksCache = { keys, at: now };
  return keys;
}

async function verifyJwt(token, team, aud) {
  const [h, p, sig] = token.split(".");
  if (!h || !p || !sig) return null;

  const header = JSON.parse(new TextDecoder().decode(b64urlToBytes(h)));
  const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(p)));

  // Signature must actually be checked -- decoding a JWT proves nothing, and
  // "alg": "none" is the classic way this check gets bypassed.
  if (header.alg !== "RS256") return null;

  const key = (await jwks(team)).find((k) => k.kid === header.kid);
  if (!key) return null;

  const pub = await crypto.subtle.importKey(
    "jwk", key,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["verify"],
  );
  const ok = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5", pub,
    b64urlToBytes(sig),
    new TextEncoder().encode(`${h}.${p}`),
  );
  if (!ok) return null;

  // A valid signature from the right team is not enough: without the aud
  // check, a token minted for ANY other Access application on this account
  // would open the board.
  const auds = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!auds.includes(aud)) return null;
  if (payload.iss !== `https://${team}.cloudflareaccess.com`) return null;

  const now = Math.floor(Date.now() / 1000);
  if (typeof payload.exp !== "number" || payload.exp <= now) return null;
  if (typeof payload.nbf === "number" && payload.nbf > now) return null;

  return payload;
}

/** GET /api/months/:month -> that month's trend rollup, e.g. 2026-09.
 *
 * Served straight from months/<YYYY-MM>.json, which publish_board.py
 * rewrites every night from that month's day documents. This is now ONLY
 * the Trends tab's data source (loadTrend()'s sparkline points) -- the
 * Digest tab's Week/MTD/YTD/Folio/Custom views read full day documents
 * directly instead (mergeDayDocs), so the rollup no longer needs to carry
 * totals/producers, only `trend`. The Worker still doesn't aggregate days
 * itself here: a full month is up to 23 documents at 20-135 KB each, so
 * doing it here would mean megabytes of R2 reads on every page load, for
 * every viewer, growing through the month.
 */
async function getMonth(env, month) {
  if (!/^\d{4}-\d{2}$/.test(month)) {
    return json({ error: "bad month" }, 400);
  }
  const obj = await env.BOARD.get(`months/${month}.json`);
  if (obj === null) {
    return json({ error: "no rollup for this month", month }, 404);
  }
  return new Response(obj.body, {
    headers: {
      "content-type": "application/json; charset=utf-8",
      // Rewritten nightly, and rewritten again by any past-day rebuild.
      "cache-control": "no-store",
    },
  });
}

/* -----------------------------------------------------------------------
   Role Play — an objection/closing practice partner.

   Grounded in Coral's licensed "One Call Close" workbook (Insurance Sales
   Lab): its Closing Objections Workflow is a numbered decision tree --
   "I want to think about it", "I need to talk to my spouse", "your price
   is too high", etc. -- each with the agency's own scripted technique
   (address the REAL concern behind the objection, then immediately
   re-ask for the sale as a direct question, never a soft "would that be
   ok"). That is also exactly the assumptive-vs-permission-seeking
   distinction coaching_cards.py already grades real calls on
   (askq/asks), so the practice partner and the real-call coaching speak
   the same language on purpose.

   THE PERSONA PROMPTS ARE THE ANSWER KEY AND MUST NEVER REACH THE CLIENT.
   They encode which objection(s) the persona raises and what a good
   response looks like, so the model can judge in character whether the
   producer's real reply earns a concession. Sending this to the browser
   would let a producer read the correct answer instead of practicing it --
   it lives only in coaching/ROLEPLAY.md, read at build time (below), never
   served to a client.

   ONE BRAIN, NOT TWO (Frank, 2026-09-10: "I feel like it should all be one
   brain"). Apollo's judgment -- what counts as an objection, an overcome
   attempt, an assumptive close -- is defined exactly once, in
   coaching/METHODOLOGY.md's "Core judgment" section, and reused verbatim
   here for grading Role Play. The persona prompts (the simulated PROSPECT,
   not Apollo) live in coaching/ROLEPLAY.md instead, since they're a
   different concern -- character behavior, not judgment. Both files are
   imported as raw text below (see wrangler.jsonc's `rules` entry for how
   Workers gets a filesystem-free build to treat a .md file as a string) and
   split into named sections by _section(). Change what Apollo considers an
   objection/addressed/overcome/assumptive in METHODOLOGY.md ONLY -- it
   takes effect here automatically. Change a persona's behavior, or Role
   Play's own grading framing (the checklist, the JSON shape), in
   ROLEPLAY.md.

   No streaming yet (v1): the board's frontend is plain script-tag JS
   with no fetch-stream reader wired up. A ~1-3 sentence reply comes back
   fast enough non-streaming that this is a reasonable place to start;
   revisit if replies feel slow in practice.
*/

/** Splits a "brain" markdown file into named sections by exact header text
 * match, e.g. "### Beginner" or "## Grading (Apollo)". A section runs from
 * right after its own header to the next markdown heading of any level (or
 * EOF) -- so sections don't need to be listed together or in order. Throws
 * if the header text isn't found so a renamed/retyped heading fails loudly
 * at Worker startup, rather than silently sending Apollo an empty prompt. */
function _section(md, header) {
  const marker = `\n${header}\n`;
  const start = md.indexOf(marker);
  if (start === -1) throw new Error(`brain file missing section: ${header}`);
  const contentStart = start + marker.length;
  const nextHeading = md.slice(contentStart).search(/\n#{1,6} /);
  const contentEnd = nextHeading === -1 ? md.length : contentStart + nextHeading;
  return md.slice(contentStart, contentEnd).trim();
}

const CORE_JUDGMENT = _section(
  METHODOLOGY_MD,
  "## Core judgment (shared with Role Play grading — do not fork this list)"
);

const PERSONAS = {
  easy: {
    label: "Beginner",
    blurb: "Open to a quote, minimal resistance",
    system: _section(ROLEPLAY_MD, "### Beginner"),
  },
  medium: {
    label: "Medium",
    blurb: "Interested, but raises multiple objections that don't hold much resistance",
    system: _section(ROLEPLAY_MD, "### Medium"),
  },
  hard: {
    label: "Professional",
    blurb: "Skeptical, cycles through objections, doesn't fold easily",
    system: _section(ROLEPLAY_MD, "### Professional"),
  },
};

// Apollo (Frank's name for the coaching brain, 2026-09-10) grading a Role
// Play session: METHODOLOGY.md's shared judgment, prepended to ROLEPLAY.md's
// own grading framing -- see the "ONE BRAIN, NOT TWO" note above.
// Every persona talks as a person first (Frank, 2026-09-30: "more rapport,
// they keep just turning me back to the quote after 1 sentence").
const RP_RAPPORT = _section(ROLEPLAY_MD, "### Rapport");

const GRADE_SYSTEM = CORE_JUDGMENT + "\n\n" + _section(ROLEPLAY_MD, "## Grading (Apollo)");

async function callClaude(env, { system, messages, maxTokens }) {
  if (!env.ANTHROPIC_API_KEY) {
    throw new Error("ANTHROPIC_API_KEY is not configured on this Worker");
  }
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-5",
      max_tokens: maxTokens,
      system,
      messages,
      thinking: { type: "disabled" },
    }),
  });
  if (!r.ok) {
    throw new Error(`Claude API ${r.status}: ${(await r.text()).slice(0, 300)}`);
  }
  const data = await r.json();
  return (data.content || [])
    .filter((b) => b.type === "text")
    .map((b) => b.text)
    .join("");
}

/* The same call, streamed (Frank, 2026-09-30: start the voice on the first
   sentence): returns a plain-text stream of the reply as Claude writes it,
   so the board can hand each finished sentence to the voice while the rest
   is still being written. Same model and settings as callClaude. */
async function callClaudeStream(env, { system, messages, maxTokens }) {
  if (!env.ANTHROPIC_API_KEY) {
    throw new Error("ANTHROPIC_API_KEY is not configured on this Worker");
  }
  // Prompt caching (2026-09-30, "it still takes too long to respond"): the
  // persona and the conversation so far are the same on every turn of a
  // session, so they are marked for caching -- each turn after the first
  // reads them back instead of processing them again, which starts the reply
  // sooner and bills them at a tenth. A prompt under the model's minimum is
  // simply not cached; the reply is the same either way.
  const cached = messages.map((m, i) => i === messages.length - 1 && m.content
    ? { role: m.role, content: [{ type: "text", text: m.content, cache_control: { type: "ephemeral" } }] }
    : m);
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-sonnet-5",
      max_tokens: maxTokens,
      system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
      messages: cached,
      thinking: { type: "disabled" },
      stream: true,
    }),
  });
  if (!r.ok || !r.body) {
    throw new Error(`Claude API ${r.status}: ${(await r.text()).slice(0, 300)}`);
  }
  // Server-sent events in, text deltas out.
  const dec = new TextDecoder(), enc = new TextEncoder();
  let buf = "";
  return r.body.pipeThrough(new TransformStream({
    transform(chunk, ctl) {
      buf += dec.decode(chunk, { stream: true });
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line.startsWith("data:")) continue;
        let ev;
        try { ev = JSON.parse(line.slice(5)); } catch (_) { continue; }
        if (ev.type === "content_block_delta" && ev.delta && ev.delta.type === "text_delta" && ev.delta.text) {
          ctl.enqueue(enc.encode(ev.delta.text));
        }
      }
    },
  }));
}

function roleplaySlug(name) {
  return String(name || "unknown").trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "unknown";
}

/** Appended to a persona's system prompt when the frontend sends
 * focus_objections -- this producer's own real, unresolved objection
 * categories from the trailing 4 completed weeks (site/public/index.html's
 * producerWeakSpots/objectionWindow4wk). Steers WHICH objection the
 * persona reaches for, not how hard it holds -- that's still entirely the
 * difficulty-level text above (Frank, 2026-09-10: "the objections
 * presented to the producer by the AI bot should be based off of what
 * they have been unsuccessful on"). */
function focusObjectionInstruction(categories) {
  if (!categories || !categories.length) return "";
  return `\n\nThis producer's real calls over the last 4 weeks show they have NOT been overcoming these specific objection types: ${categories.join(", ")}. When you raise your closing objection(s) this call, phrase them so they land as one of these categories rather than a generic one from the list above -- everything else about how hard you push stays exactly as described for your difficulty level.`;
}

/** Appended to a persona's system prompt when the frontend sends
 * lead_source -- backstory flavor only (site/public/index.html's
 * LEAD_SOURCES), shown to the producer on the pre-call debrief screen so
 * they know the same context you do (Frank, 2026-09-11: "they should know
 * ... what the lead source is"). This is scene-setting, not the answer
 * key -- it must never change which objections you raise or how hard you
 * hold them, only how you'd naturally react if asked how you were
 * contacted or why you're on the phone. */
function leadSourceInstruction(backstory) {
  if (!backstory) return "";
  return `\n\nBackstory context for how this call came about: ${backstory} If the producer asks how you were contacted or why you're on the phone, answer consistently with this -- but it does not change which objections you raise, how hard you hold them, or anything else about your difficulty level above.`;
}

/** Appended when the frontend sends prospect -- who this prospect IS (Frank,
 * 2026-09-24: scenarios need names, occupations, ages and family status),
 * rolled per scenario on the board and shown to the producer on the debrief.
 * Identity only: it never changes the objections or how hard they hold. */
function prospectInstruction(profile) {
  if (!profile) return "";
  return `\n\nWho you are: ${profile} Answer as this person -- your name, age, job and household are these, and your coverage needs follow from them (a household with kids or a new driver, a business owner's tools, a retiree's fixed income). Share them naturally when the producer asks during discovery, not all at once. None of this changes which objections you raise or how hard you hold them.`;
}

/** Appended when the frontend sends language (Frank, 2026-09-29: "some
 * should be spanish, some english, and some mixed"). Rolled with the
 * prospect on the board; English sends nothing. How the prospect talks,
 * never what they object to. */
function languageInstruction(language) {
  if (language === "es") {
    return "\n\nLanguage: you speak Spanish -- everyday Mexican Spanish, the way a customer in Arizona talks on the phone -- and you are more comfortable in it than in English. Reply only in Spanish, and EVERY word in Spanish: no English words or fillers at all -- not \"okay\", \"yeah\", \"so\", \"insurance\", \"quote\", \"email\" or \"full coverage\". Say seguro, cotización, póliza, cobertura completa, deducible, pago mensual, correo, and write numbers and prices as words or digits, never with English. Only a company's name stays as it is (Progressive, Geico, Farmers). The example objections above are written in English only to describe them -- say them in your own Spanish. If the producer speaks English, ask whether they speak Spanish (\"¿habla español?\") and keep answering in Spanish.";
  }
  if (language === "mix") {
    return "\n\nLanguage: you are bilingual and talk the way many Arizona families do, switching between English and Spanish naturally, sometimes mid-sentence (\"sí, I already have Progressive, pero está muy caro\"). Mix both in most replies, whichever language the producer uses.";
  }
  return "";
}

/** GET /api/roleplay/speak?voice=aura-2-...&text=... -> audio/mpeg
 *
 * The prospect's voice (Frank, 2026-09-29: Deepgram). The board picks the
 * voice from its own catalogue (RP_VOICES in index.html) to fit the
 * prospect's sex, age and language; any Aura-2 English or Spanish voice
 * id is accepted here. A GET so the page can hand the URL straight to an
 * <audio> element and start playing as Deepgram streams it back -- the
 * Access cookie rides along like any same-origin request. With no
 * DEEPGRAM_API_KEY secret the board falls back to the browser's voice. */
/** GET /api/roleplay/face/<sex>-<band>-<look>-<n> -> image/jpeg
 *
 * The prospect's headshot (Frank, 2026-09-29: "headshots of AI generated
 * faces with glow when they are speaking"). A fixed library -- 2 sexes x 3
 * age bands x 4 looks x 4 variants, at most 96 faces -- each drawn ONCE
 * with Workers AI (FLUX.1 [schnell], about $0.0006 a face) the first time
 * a prospect needs it, then kept in R2 under roleplay-faces/ and served
 * from there forever. No seed: the model refuses one ("Additional or
 * unevaluated properties '/seed'", 2026-09-29, though Cloudflare's own
 * example passes it), so a face lost from R2 would be drawn afresh. No AI
 * binding, or a failed draw, is a 503 and the board shows the prospect's
 * initials instead. */
const RP_FACE_AGE = { young: "24-year-old", adult: "40-year-old", mature: "62-year-old" };
const RP_FACE_LOOK = { latino: "Hispanic", white: "white", black: "Black", asian: "Asian American" };
const RP_FACE_DRESS = [
  "wearing a casual button-up shirt", "wearing a plain t-shirt", "wearing a polo shirt", "wearing a sweater",
];
async function roleplayFace(env, key) {
  const m = /^(f|m)-(young|adult|mature)-(latino|white|black|asian)-([0-3])$/.exec(key);
  if (!m) return json({ error: "unknown face" }, 400);
  const r2key = `roleplay-faces/${key}.jpg`;
  const headers = { "content-type": "image/jpeg", "cache-control": "private, max-age=604800" };
  const saved = await env.BOARD.get(r2key);
  if (saved) return new Response(saved.body, { headers });
  if (!env.AI) return json({ error: "no Workers AI binding" }, 503);
  const [, sex, band, look, n] = m;
  const who = sex === "f" ? "woman" : "man";
  const prompt = `Realistic head-and-shoulders portrait photo of an ordinary ${RP_FACE_AGE[band]} ${RP_FACE_LOOK[look]} ${who} `
    + `from Arizona, ${RP_FACE_DRESS[+n]}, relaxed natural expression, looking at the camera, soft daylight, `
    + `plain softly blurred background, sharp focus on the face, natural skin texture. No text, no watermark.`;
  let img;
  try {
    const out = await env.AI.run("@cf/black-forest-labs/flux-1-schnell", { prompt, steps: 6 });
    // A plain loop, not Uint8Array.from(str, fn): the free plan's CPU budget
    // per request is small and the image is a few hundred KB of base64.
    const bin = atob(out.image);
    img = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) img[i] = bin.charCodeAt(i);
  } catch (e) {
    return json({ error: "face could not be drawn", detail: String(e).slice(0, 200) }, 503);
  }
  await env.BOARD.put(r2key, img, { httpMetadata: { contentType: "image/jpeg" } });
  return new Response(img, { headers });
}

/* The prospect talks a little faster than Deepgram's default (Frank,
   2026-09-29: "they talk to slow"), with Deepgram's own speed setting,
   which keeps the voice natural. Deepgram says it is not supported in every
   language yet, so a refused speed is retried at normal speed and this
   Worker stops asking for that language (per isolate). Raised to 1.5 on
   2026-09-30 ("it still talks really slow"): measured 25-38% shorter than
   normal, English and Spanish alike. */
const RP_SPEAK_SPEED = 1.3;   // Frank, 2026-09-30: 1.5 (Deepgram's maximum) was "just a tad bit too fast"; 1.2 barely changed Spanish
const rpSpeedRefused = new Set();   // "en" / "es"
async function deepgramSpeak(env, voice, text) {
  const call = (speed) => fetch(`https://api.deepgram.com/v1/speak?model=${voice}&encoding=mp3${speed ? `&speed=${speed}` : ""}`, {
    method: "POST",
    headers: { Authorization: `Token ${env.DEEPGRAM_API_KEY}`, "content-type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const lang = voice.slice(-2);
  if (rpSpeedRefused.has(lang)) return call(null);
  const r = await call(RP_SPEAK_SPEED);
  if (r.status !== 400) return r;
  const detail = await r.text();
  if (!/speed/i.test(detail)) return new Response(detail, { status: 400 });
  rpSpeedRefused.add(lang);
  return call(null);
}

async function roleplaySpeak(env, url, ctx) {
  if (!env.DEEPGRAM_API_KEY) return json({ error: "DEEPGRAM_API_KEY is not configured on this Worker" }, 503);
  const voice = url.searchParams.get("voice") || "";
  const text = (url.searchParams.get("text") || "").trim();
  if (!/^aura-2-[a-z]+-(en|es)$/.test(voice)) return json({ error: "unknown voice" }, 400);
  if (!text || text.length > 2000) return json({ error: "text must be 1-2000 characters" }, 400);
  const r = await deepgramSpeak(env, voice, text);
  if (!r.ok) return json({ error: `Deepgram ${r.status}`, detail: (await r.text()).slice(0, 300) }, 502);
  // A copy of every line the prospect speaks, so a saved session can be
  // played back (Frank, 2026-09-29: "i want to be able to hear it"). The
  // copy is keyed by voice + text -- the grade finds it from the session's
  // own turns -- and written after the reply is already streaming.
  if (ctx && r.body) {
    const [play, keep] = r.body.tee();
    ctx.waitUntil((async () => {
      try {
        const bytes = await new Response(keep).arrayBuffer();
        await env.BOARD.put(await rpTtsKey(voice, text), bytes, { httpMetadata: { contentType: "audio/mpeg" } });
      } catch (_) {}
    })());
    return new Response(play, { headers: { "content-type": "audio/mpeg", "cache-control": "no-store" } });
  }
  return new Response(r.body, { headers: { "content-type": "audio/mpeg", "cache-control": "no-store" } });
}

async function rpTtsKey(voice, text) {
  const h = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`${voice}\n${text}`));
  return `roleplay-audio/tts/${[...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 40)}.mp3`;
}

/** POST /api/roleplay/clip?producer=X&beta=1 (body: the audio) -> {key}
 *  One producer turn as the browser recorded it. Stored under the
 *  producer's own prefix (beta under beta/), so the same rule that decides
 *  who may open a session decides who may hear it. */
const RP_CLIP_TYPES = { "audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "m4a", "audio/mpeg": "mp3" };
async function roleplayClipUpload(request, env, url) {
  const type = String(request.headers.get("content-type") || "").split(";")[0].trim().toLowerCase();
  const ext = RP_CLIP_TYPES[type];
  if (!ext) return json({ error: "unsupported audio type" }, 400);
  const beta = url.searchParams.get("beta") === "1";
  const producer = String(url.searchParams.get("producer") || "").trim();
  if (!beta && !producer) return json({ error: "producer is required" }, 400);
  const bytes = await request.arrayBuffer();
  if (!bytes.byteLength) return json({ error: "empty clip" }, 400);
  if (bytes.byteLength > 8 * 1024 * 1024) return json({ error: "clip too large" }, 413);
  const id = `${new Date().toISOString().replace(/[:.]/g, "-")}-${crypto.randomUUID().slice(0, 8)}`;
  const key = `roleplay-audio/${beta ? "beta" : roleplaySlug(producer)}/${id}.${ext}`;
  await env.BOARD.put(key, bytes, { httpMetadata: { contentType: type } });
  return json({ key });
}

/** GET /api/roleplay/audio?key=roleplay-audio/... -> the clip, with range
 *  support so the player can seek. The prospect's lines (tts/) are the
 *  machine's voice and open to anyone signed in; a producer's own turns
 *  follow rpScope -- their own, or everyone's for the history viewers. */
async function roleplayAudio(request, env, key) {
  const m = /^roleplay-audio\/([a-z0-9-]+)\/[A-Za-z0-9._-]+\.(mp3|webm|ogg|m4a)$/.exec(key || "");
  if (!m || key.includes("..")) return json({ error: "bad key" }, 400);
  const scope = rpScope(request, env);
  const owner = m[1];
  const ok = owner === "tts" || scope.all || (owner !== "beta" && scope.producer && owner === roleplaySlug(scope.producer));
  if (!ok) return json({ error: "not permitted" }, 403);
  const object = await env.BOARD.get(key, { range: request.headers });
  if (object === null) return json({ error: "not found" }, 404);
  const headers = new Headers();
  headers.set("content-type", (object.httpMetadata && object.httpMetadata.contentType) || "audio/mpeg");
  headers.set("accept-ranges", "bytes");
  headers.set("cache-control", "private, max-age=3600");
  let status = 200;
  if (object.range) {
    const offset = object.range.offset || 0;
    const length = object.range.length ?? (object.size - offset);
    headers.set("content-range", `bytes ${offset}-${offset + length - 1}/${object.size}`);
    headers.set("content-length", String(length));
    status = 206;
  } else {
    headers.set("content-length", String(object.size));
  }
  return new Response(object.body, { status, headers });
}

/** POST /api/roleplay/voice-feedback {key, stars, again, comment} -> {ok}
 *
 * A producer's rating of the prospect's voice (Frank, 2026-09-29), sent
 * from the grade card after a session. Written onto the saved session
 * itself and appended to roleplay-voices/ratings.json, the one file the
 * ratings table reads -- listing every session to add them up would grow
 * without bound. Beta sessions are rated too: a voice rating is not a
 * producer figure. A second rating of the same session replaces the first. */
async function roleplayVoiceFeedback(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const key = String(body.key || "");
  if (!/^roleplay(-beta)?\/[a-z0-9-]+\/[0-9TZ:.-]+\.json$/.test(key)) return json({ error: "bad session key" }, 400);
  const stars = Number(body.stars);
  if (!Number.isInteger(stars) || stars < 1 || stars > 5) return json({ error: "stars must be 1-5" }, 400);
  const obj = await env.BOARD.get(key);
  if (!obj) return json({ error: "session not found" }, 404);
  const session = await obj.json();
  if (!session.voice) return json({ error: "session has no voice to rate" }, 400);
  const feedback = {
    stars,
    again: body.again === true ? true : body.again === false ? false : null,
    comment: String(body.comment || "").trim().slice(0, 500),
    at: new Date().toISOString(),
  };
  session.voice_feedback = feedback;
  await env.BOARD.put(key, JSON.stringify(session), { httpMetadata: { contentType: "application/json" } });

  const idxKey = "roleplay-voices/ratings.json";
  const idxObj = await env.BOARD.get(idxKey);
  const idx = idxObj ? await idxObj.json() : { ratings: [] };
  idx.ratings = (idx.ratings || []).filter((x) => x.key !== key);
  idx.ratings.push({ key, voice: session.voice, language: session.language || "en",
    producer: session.producer, beta: !!session.beta, ...feedback });
  await env.BOARD.put(idxKey, JSON.stringify(idx), { httpMetadata: { contentType: "application/json" } });
  return json({ ok: true });
}

/** GET /api/roleplay/voices -> {ratings: [...]}, for ROLEPLAY_VOICE_VIEWERS
 * only (wrangler.jsonc): the board adds them up per voice. */
async function roleplayVoiceRatings(request, env) {
  const who = String((ACCESS_IDENTITY.get(request) || {}).email || "").toLowerCase();
  const allowed = String(env.ROLEPLAY_VOICE_VIEWERS || "").toLowerCase()
    .split(",").map((x) => x.trim()).filter(Boolean);
  if (!who || !allowed.includes(who)) return json({ error: "not permitted" }, 403);
  const obj = await env.BOARD.get("roleplay-voices/ratings.json");
  return json(obj ? await obj.json() : { ratings: [] });
}

/** POST /api/roleplay/turn {persona, history, focus_objections} -> {reply}
 *
 * `history` is the growing [{role: "producer"|"prospect", content}, ...]
 * transcript the frontend already holds -- the Claude API is stateless, so
 * the full conversation rides on every turn, same as any other multi-turn
 * chat. `focus_objections` (optional, up to 3 category strings) steers
 * which objections the persona reaches for -- see
 * focusObjectionInstruction(). Mapped to the API's user/assistant roles
 * here so the persona
 * prompt above can talk about "producer" and "prospect" in plain English.
 */
async function roleplayTurn(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const persona = PERSONAS[body.persona];
  if (!persona) return json({ error: "unknown persona" }, 400);
  const history = Array.isArray(body.history) ? body.history : [];
  if (!history.length || history[history.length - 1].role !== "producer") {
    return json({ error: "history must end with a producer turn" }, 400);
  }

  const messages = history.map((h) => ({
    role: h.role === "producer" ? "user" : "assistant",
    content: String(h.content || "").slice(0, 4000),
  }));
  const focusObjections = Array.isArray(body.focus_objections)
    ? body.focus_objections.filter((c) => typeof c === "string").slice(0, 3)
    : [];
  const leadSource = typeof body.lead_source === "string" ? body.lead_source.slice(0, 500) : "";
  const prospect = typeof body.prospect === "string" ? body.prospect.slice(0, 300) : "";
  const system = persona.system + "\n\n" + RP_RAPPORT + focusObjectionInstruction(focusObjections) + leadSourceInstruction(leadSource)
    + prospectInstruction(prospect) + languageInstruction(body.language);

  if (body.stream === true) {
    try {
      const text = await callClaudeStream(env, { system, messages, maxTokens: 300 });
      // text/event-stream + no-transform: Cloudflare may hold back and
      // compress a text/plain body, which would deliver the reply in one
      // lump and undo the first-sentence start. The body is still plain
      // reply text, not SSE frames.
      return new Response(text, { headers: { "content-type": "text/event-stream; charset=utf-8", "cache-control": "no-store, no-transform" } });
    } catch (e) {
      return json({ error: "role-play turn failed", detail: String(e).slice(0, 300) }, 502);
    }
  }
  try {
    const reply = await callClaude(env, { system, messages, maxTokens: 300 });
    return json({ reply: reply.trim() });
  } catch (e) {
    return json({ error: "role-play turn failed", detail: String(e).slice(0, 300) }, 502);
  }
}

/** POST /api/roleplay/grade {producer, persona, history} -> {grade}
 *
 * Grades the transcript, then stores the whole session (transcript +
 * grade) under roleplay/<producer-slug>/<iso-timestamp>.json in the same
 * private R2 bucket the day documents live in -- same bucket, new prefix,
 * no new infrastructure. Scores and sessions persist across devices this
 * way, not just in one browser's local storage.
 */
async function roleplayGrade(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ error: "bad request body" }, 400);
  }
  const persona = PERSONAS[body.persona];
  if (!persona) return json({ error: "unknown persona" }, 400);
  const history = Array.isArray(body.history) ? body.history : [];
  if (!history.length) return json({ error: "no transcript to grade" }, 400);
  const producer = String(body.producer || "").trim();
  if (!producer) return json({ error: "producer is required" }, 400);
  // Each turn's sound, for playback (Frank, 2026-09-29): the producer's
  // own clip only if it sits under this session's own prefix, and the
  // prospect's line from the copy /speak kept, if it did.
  const own = `roleplay-audio/${body.beta === true ? "beta" : roleplaySlug(producer)}/`;
  const voiceOk = typeof body.voice === "string" && /^aura-2-[a-z]+-(en|es)$/.test(body.voice);
  for (const h of history) {
    if (!h || typeof h !== "object") continue;
    if (h.role === "producer") {
      if (typeof h.audio !== "string" || !h.audio.startsWith(own) || h.audio.includes("..")) delete h.audio;
    } else {
      // A streamed reply was spoken sentence by sentence (h.parts), each
      // kept on its own; an older one in one piece. `audio` is the first
      // clip, `audios` every clip in order when there is more than one.
      delete h.audio; delete h.audios;
      const parts = Array.isArray(h.parts)
        ? h.parts.filter((x) => typeof x === "string" && x.trim()).slice(0, 20).map((x) => x.slice(0, 2000).trim())
        : [];
      delete h.parts;
      if (parts.length) h.parts = parts;
      if (voiceOk && typeof h.content === "string" && h.content.trim()) {
        const keys = [];
        for (const t of (parts.length ? parts : [h.content.slice(0, 2000).trim()])) {
          try {
            const k = await rpTtsKey(body.voice, t);
            if (await env.BOARD.head(k)) keys.push(k);
          } catch (_) {}
        }
        if (keys.length) h.audio = keys[0];
        if (keys.length > 1) h.audios = keys;
      }
    }
  }

  const transcriptText = history
    .map((h) => `${h.role === "producer" ? "Producer" : "Prospect"}: ${h.content}`)
    .join("\n");

  let grade;
  try {
    const raw = await callClaude(env, {
      system: GRADE_SYSTEM,
      messages: [{ role: "user", content: transcriptText.slice(0, 12000) }],
      maxTokens: 1000,
    });
    const m = raw.match(/\{[\s\S]*\}/);
    grade = m ? JSON.parse(m[0]) : null;
  } catch (e) {
    return json({ error: "grading failed", detail: String(e).slice(0, 300) }, 502);
  }
  if (!grade) return json({ error: "grading returned no parsable result" }, 502);

  // BETA (Frank, 2026-09-24): "Beta / testing" sessions -- anyone trying the
  // system out -- are saved under roleplay-beta/, which nothing that reads a
  // producer's history or weak spots ever lists. Kept apart until Role Play
  // is finalized.
  const beta = body.beta === true;
  const now = new Date();
  const session = {
    ...(beta ? { beta: true } : {}),
    // Whose real weak spots the beta session borrowed.
    ...(beta && typeof body.as_producer === "string" ? { as_producer: body.as_producer.slice(0, 60) } : {}),
    producer,
    persona: body.persona,
    persona_label: persona.label,
    lead_source: typeof body.lead_source === "string" ? body.lead_source.slice(0, 200) : "",
    ...(typeof body.prospect === "string" && body.prospect ? { prospect: body.prospect.slice(0, 300) } : {}),
    // The prospect's voice and language, so the rating after the session
    // lands on the right voice.
    ...(typeof body.voice === "string" && /^aura-2-[a-z]+-(en|es)$/.test(body.voice) ? { voice: body.voice } : {}),
    ...(["en", "es", "mix"].includes(body.language) ? { language: body.language } : {}),
    // The real objection groups the prospect leaned on (the producer's weak
    // spots), so the history can say what each session drilled.
    ...(Array.isArray(body.focus_objections) && body.focus_objections.length
      ? { focus: body.focus_objections.slice(0, 4).map((x) => String(x).slice(0, 80)) } : {}),
    history,
    grade,
    created_at: now.toISOString(),
  };
  const key = beta ? `roleplay-beta/testing/${now.toISOString()}.json`
                   : `roleplay/${roleplaySlug(producer)}/${now.toISOString()}.json`;
  try {
    await env.BOARD.put(key, JSON.stringify(session), {
      httpMetadata: { contentType: "application/json" },
    });
    try { await rpIndexAdd(env, { [key]: rpSummary(key, session) }); } catch (_) {}
  } catch (e) {
    // The producer still gets their grade even if the save failed -- a
    // lost practice record is a much smaller problem than a lost grade.
    return json({ grade, saved: false, save_error: String(e).slice(0, 200) });
  }
  return json({ grade, saved: true, key });
}

/** GET /api/roleplay/history?producer=X -> {sessions: [...]}
 *  GET /api/roleplay/history?beta=1     -> every beta/testing session
 *
 * Most recent first, capped at 25. Without a producer filter, lists
 * across everyone -- small volume expected (practice reps, not a
 * once-a-day batch), so a plain list-then-fetch is fine; no rollup file.
 */
async function roleplayHistory(request, env, producer, beta) {
  // A producer sees only their own sessions (Frank, 2026-09-29); beta and
  // other producers' lists are for ROLEPLAY_HISTORY_VIEWERS.
  const scope = rpScope(request, env);
  if (!scope.all && (beta || !producer || producer !== scope.producer)) return json({ sessions: [] });
  // beta=1 lists every beta session, whoever ran it; never mixed with the
  // producers' own roleplay/ history.
  const prefix = beta ? "roleplay-beta/"
    : producer ? `roleplay/${roleplaySlug(producer)}/` : "roleplay/";
  const keys = [];
  let cursor;
  do {
    const listed = await env.BOARD.list({ prefix, cursor });
    for (const o of listed.objects) keys.push(o.key);
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);
  keys.sort().reverse();

  const sessions = [];
  for (const key of keys.slice(0, 25)) {
    const obj = await env.BOARD.get(key);
    if (obj) sessions.push(await obj.json());
  }
  return json({ sessions });
}


/* ---- Role Play session history (Frank, 2026-09-29: "a full history of role
   play sessions ... producers see their own") ----------------------------

   Who sees what: an email in ROLEPLAY_HISTORY_VIEWERS (wrangler.jsonc) sees
   every producer's sessions and the beta ones; a producer's own email
   (RP_PRODUCER_EMAILS -- the addresses the staff digest goes to,
   digest_config.RECIPIENTS_STAFF) sees only their own; anyone else, none.
   Always from the verified Access token, never a request parameter.

   The list reads roleplay-index.json -- one summary per session (no
   transcript) -- so the page does not fetch every session to draw a table.
   Each graded session is added to it as it is saved, and every list call
   also compares the index with what is actually in R2 and adds any session
   it lacks (up to 40 a call), so a session saved before the index existed,
   or a lost write, heals itself. A session opens in full from its own file. */
const RP_PRODUCER_EMAILS = {
  "crystal@floresinsuranceagency.com": "Crystal Mango",
  "lorena@floresinsuranceagency.com": "Lorena Gonzalez",
  "mike@floresinsuranceagency.com": "Mike Olvera",
  "coral@floresinsuranceagency.com": "Coral Barwick",
  "sarahi@floresinsuranceagency.com": "Sarahi Chin",
};
const RP_INDEX_KEY = "roleplay-index.json";

function rpScope(request, env) {
  const who = String((ACCESS_IDENTITY.get(request) || {}).email || "").toLowerCase();
  const all = String(env.ROLEPLAY_HISTORY_VIEWERS || "").toLowerCase()
    .split(",").map((x) => x.trim()).filter(Boolean);
  return { all: !!who && all.includes(who), producer: RP_PRODUCER_EMAILS[who] || "" };
}

function rpMaySee(scope, key) {
  if (scope.all) return key.startsWith("roleplay/") || key.startsWith("roleplay-beta/");
  return !!scope.producer && key.startsWith(`roleplay/${roleplaySlug(scope.producer)}/`);
}

function rpSummary(key, s) {
  const g = s.grade || {};
  const items = Array.isArray(g.checklist) ? g.checklist : [];
  return {
    key,
    beta: !!s.beta,
    producer: s.producer || "",
    ...(s.as_producer ? { as_producer: s.as_producer } : {}),
    persona: s.persona || "",
    persona_label: s.persona_label || "",
    lead_source: s.lead_source || "",
    ...(s.language ? { language: s.language } : {}),
    ...(s.focus ? { focus: s.focus } : {}),
    created_at: s.created_at || "",
    resolved: g.resolved === true,
    met: items.filter((c) => c && c.met).length,
    of: items.length,
    missed: items.filter((c) => c && !c.met).map((c) => String(c.item || "")),
    turns: Array.isArray(s.history) ? s.history.length : 0,
    summary: String(g.summary || "").slice(0, 400),
  };
}

async function rpIndexRead(env) {
  const obj = await env.BOARD.get(RP_INDEX_KEY);
  if (!obj) return {};
  try { return (await obj.json()).sessions || {}; } catch (_) { return {}; }
}

async function rpIndexAdd(env, add) {
  const idx = await rpIndexRead(env);
  Object.assign(idx, add);
  await env.BOARD.put(RP_INDEX_KEY, JSON.stringify({ sessions: idx }), {
    httpMetadata: { contentType: "application/json" },
  });
  return idx;
}

async function rpAllKeys(env) {
  const keys = [];
  for (const prefix of ["roleplay/", "roleplay-beta/"]) {
    let cursor;
    do {
      const listed = await env.BOARD.list({ prefix, cursor });
      for (const o of listed.objects) if (o.key.endsWith(".json")) keys.push(o.key);
      cursor = listed.truncated ? listed.cursor : undefined;
    } while (cursor);
  }
  return keys;
}

/** GET /api/roleplay/sessions?from=YYYY-MM-DD&to=YYYY-MM-DD&producer=X&beta=1
 *  -> {scope: {all, producer}, sessions: [summary, ...]} newest first. */
async function roleplaySessions(request, env, url) {
  const scope = rpScope(request, env);
  if (!scope.all && !scope.producer) return json({ scope, sessions: [] });
  let idx = await rpIndexRead(env);
  const keys = await rpAllKeys(env);
  const have = new Set(keys);
  const missing = keys.filter((k) => !idx[k]).slice(0, 40);
  const stale = Object.keys(idx).filter((k) => !have.has(k));
  if (missing.length || stale.length) {
    const add = {};
    for (const k of missing) {
      const obj = await env.BOARD.get(k);
      if (!obj) continue;
      try { add[k] = rpSummary(k, await obj.json()); } catch (_) {}
    }
    for (const k of stale) delete idx[k];
    Object.assign(idx, add);
    try {
      await env.BOARD.put(RP_INDEX_KEY, JSON.stringify({ sessions: idx }), {
        httpMetadata: { contentType: "application/json" },
      });
    } catch (_) {}
  }
  const from = url.searchParams.get("from") || "";
  const to = url.searchParams.get("to") || "";
  const beta = url.searchParams.get("beta") === "1";
  const who = url.searchParams.get("producer") || "";
  // Days are Arizona days, like the rest of the board (UTC-7, no DST).
  const azDay = (iso) => new Date(new Date(iso).getTime() - 7 * 3600e3).toISOString().slice(0, 10);
  const sessions = Object.values(idx)
    .filter((x) => rpMaySee(scope, x.key))
    .filter((x) => (beta ? x.beta : !x.beta))
    .filter((x) => !who || x.producer === who)
    .filter((x) => { const d = azDay(x.created_at); return (!from || d >= from) && (!to || d <= to); })
    .sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
  return json({ scope, sessions });
}

/** GET /api/roleplay/session?key=roleplay/... -> the whole saved session. */
async function roleplaySession(request, env, key) {
  const scope = rpScope(request, env);
  if (!key || key.includes("..") || !rpMaySee(scope, key)) return json({ error: "not permitted" }, 403);
  const obj = await env.BOARD.get(key);
  if (!obj) return json({ error: "not found" }, 404);
  return json({ key, session: await obj.json() });
}

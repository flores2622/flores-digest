/**
 * GET /api/days/:day  ->  the day document from R2.
 *
 * This Function is the ONLY reader of the board bucket. The bucket is private:
 * no r2.dev URL, no public custom domain. Everything it serves is customer NPI
 * -- lead names, phone numbers, notes on what coverage someone was quoted -- so
 * the path to it runs through here, and this whole site sits behind Cloudflare
 * Access with the agency's Google Workspace as the identity provider.
 *
 * Access does the authentication. This Function deliberately does NOT re-check
 * identity: if a request reaches it, Access already allowed it, and a second
 * half-implemented check here would be security theatre that drifts out of
 * sync with the real policy. If you ever put this Function on a route Access
 * does not cover, that assumption breaks and this comment is the reason why.
 *
 * Binding: BOARD -> the R2 bucket (Pages project -> Settings -> Functions ->
 * R2 bucket bindings). The binding is configured in the dashboard because this
 * is a Direct Upload project.
 */
export async function onRequestGet(context) {
  const { day } = context.params;

  // Only ever ISO dates. The bucket key is built from user-supplied path, so
  // this is what stops `../` and friends from reaching another prefix.
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) {
    return json({ error: "bad day" }, 400);
  }

  const obj = await context.env.BOARD.get(`days/${day}.json`);
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
      // rewritten if the run is re-run, and a stale board that disagrees with
      // the email is exactly the failure this whole migration exists to end.
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

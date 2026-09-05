/**
 * GET /api/days  ->  { days: ["2026-09-04", "2026-09-03", ...] }
 *
 * The date picker's list. Newest first. Keys only -- never object bodies, so
 * this stays cheap however many days accumulate.
 *
 * R2 list is paginated (1000 keys per page, which is about four years of
 * business days). We follow the cursor rather than assuming one page, because
 * the failure mode of not doing so is the picker silently losing its oldest
 * days years from now, which nobody would connect back to this file.
 */
export async function onRequestGet(context) {
  const days = [];
  let cursor;

  do {
    const listed = await context.env.BOARD.list({ prefix: "days/", cursor });
    for (const o of listed.objects) {
      const m = o.key.match(/^days\/(\d{4}-\d{2}-\d{2})\.json$/);
      if (m) days.push(m[1]);
    }
    cursor = listed.truncated ? listed.cursor : undefined;
  } while (cursor);

  days.sort().reverse();

  return new Response(JSON.stringify({ days }), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      // A new day lands every weekday at ~7 PM Arizona. Caching this for even
      // a minute means someone refreshing at 7:01 does not see tonight.
      "cache-control": "no-store",
    },
  });
}

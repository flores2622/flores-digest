"""A policy entered late reaches the day it was sold on.

Premium Sold and Life Sold are counted by soldDate from the policy list the
nightly run pulls that evening. A policy typed into AgencyZoom AFTER its
day's run never appeared anywhere: the day it was sold on had been built
without it, and no later day counts it (Frank, 2026-10-12: "we do have a
life sale, its alondra, why is it not on the totals" -- Coral's Individual
Life for Alondra Angulo, sold 09-29, entered 09-30, hours after the 09-29
run; then 2026-10-13: "add late policies to premium sold the same way").
Only the week's life figure on later days ever saw it, because `life_week`
recounts the week from the policy list each night.

So each nightly run re-reads the last LOOKBACK published days against its
own fresh policy list and ADDS any real policy a day is missing:

  - a life policy: the producer's and team's count and premium, the Life
    Sold list (`rows.life`) and the week's figure on that day and the later
    published days of its week;
  - any other policy: the producer's and team's Policies and Premium Sold
    (and the cross-sell count), the Sold list (`rows.sold`), the day's
    Policies / Premium Sold / Closing Ratio tiers, the leaderboard re-scored
    from the published values with the new Premium Sold, and the sale
    streak that colours Policies on that day and the later days of the
    window (`publish_board.apply_policy_streak`, which reads the earlier
    days back from R2), plus the month's trend rollup.

It only ever adds: a published day never loses a figure here, a premium
that AgencyZoom changed since is never applied (the Sales sheet flags
those), and nothing else on the page changes. BOB / Rewrite and test leads
are left out by the same rules as the nightly (`cfg.is_real_sale`). Each
page changed is backed up under backups/<today>-late-policies/. The emailed
digest is not re-sent.

    python3 late_policies.py [--day YYYY-MM-DD] [--lookback N] [--dry-run]

By hand it reads the policy and lead lists from data/ when a run left them
that day, else the newest corpus snapshot in R2 at or before --day.
"""
import copy
import datetime as dt
import gzip
import json
import pathlib
import sys

import digest_config as cfg
import digest_rows

ROOT = pathlib.Path(__file__).resolve().parent
LOOKBACK = 14


def _day_policies(day, pol, who, smap, azid, life):
    return [x for x in pol
            if str(x.get("soldDate") or "").startswith(day) and cfg.is_life(x) == life
            and azid.get(x.get("agentId")) == who and cfg.is_real_sale(x, smap)]


def _rescore(doc):
    """The leaderboard re-scored from its own published category values,
    with Premium Sold replaced by the producers' new figure (the same rule
    the quote recount of 2026-10-12 used)."""
    lb, producers = doc.get("leaderboard"), doc.get("producers") or []
    if not lb or not lb.get("categories") or not producers:
        return
    names = [p["name"] for p in producers]
    by = {p["name"]: p for p in producers}
    vals = []
    for c in lb["categories"]:
        v = dict(c.get("values") or {})
        if c.get("label") == "Premium Sold":
            v = {n: by[n].get("ps") or 0 for n in names}
        vals.append(v)
    tie = {n: tuple(by[n].get(k) or 0 for k in ("ps", "hh", "dials")) for n in names}
    per_cat, points, order = cfg.leaderboard_score(vals, names, tie)
    for c, v, pts in zip(lb["categories"], vals, per_cat):
        c["values"], c["points"] = v, pts
    lb["points"], lb["order"] = points, order


def _closing(t, row):
    hh, pq = row.get("hh") or 0, row.get("pq") or 0
    t["closing_hh"] = cfg.tier("closing_ratio_pct", (100 * (row.get("pol") or 0) / hh) if hh else None)
    t["closing_pq"] = cfg.tier("closing_ratio_pct", (100 * (row.get("ps") or 0) / pq) if pq else None)


def plan(docs, pol, smap, azid):
    """docs: {day: published document}. Returns ({day: changed copy},
    {day of a Premium Sold change}). Pure."""
    out, sales_days = {}, set()
    docs = {d: copy.deepcopy(doc) for d, doc in docs.items()}
    for day, doc in sorted(docs.items()):
        changed = sold_changed = False
        rows = doc.get("rows")
        if not isinstance(rows, dict):
            rows = doc["rows"] = {}
        have_life = {r.get("policy") for r in rows.get("life") or []}
        have_sold = {r.get("policy") for r in rows.get("sold") or []}
        life_day = cfg.life_sales(day, pol, smap, azid)
        real_day = cfg.real_sales(day, pol, smap, azid)
        tiers = doc.get("tiers") or {}
        for p in doc.get("producers") or []:
            who = p.get("name")
            # Life: its own stat (Frank, 2026-09-30).
            n, prem = life_day.get(who, (0, 0.0))
            if n > (p.get("life") or 0):
                p["life"], p["life_ps"] = n, round(prem)
                for x in _day_policies(day, pol, who, smap, azid, True):
                    if (x.get("policyNumber") or "") not in have_life:
                        rows.setdefault("life", []).append(digest_rows.policy_row(x, who, smap))
                changed = True
            # The week's life figure, Monday to this day, as daily.py counts it.
            wk, d = 0, dt.date.fromisoformat(cfg.week_start(day))
            while d.isoformat() <= day:
                wk += cfg.life_sales(d.isoformat(), pol, smap, azid).get(who, (0, 0.0))[0]
                d += dt.timedelta(days=1)
            if wk > (p.get("life_week") or 0):
                p["life_week"] = wk
                changed = True
            # Premium Sold (Frank, 2026-10-13): the count and premium follow the
            # list only when a policy was ADDED; a premium changed on a policy
            # already counted is the Sales sheet's flag, never applied here.
            n, prem = real_day.get(who, (0, 0.0))
            if n > (p.get("pol") or 0):
                added = [x for x in _day_policies(day, pol, who, smap, azid, False)
                         if (x.get("policyNumber") or "") not in have_sold]
                p["pol"], p["ps"] = n, round(prem)
                p["cross_sell"] = (p.get("cross_sell") or 0) + sum(1 for x in added if cfg.is_cross_sell(x, smap))
                for x in added:
                    rows.setdefault("sold", []).append(digest_rows.policy_row(x, who, smap))
                t = tiers.setdefault(who, {}) if isinstance(tiers, dict) else {}
                t["pol"] = t["ps"] = "green"          # a sale that day: streak 0
                _closing(t, p)
                changed = sold_changed = True
        if not changed:
            continue
        T = doc.setdefault("totals", {})
        for k in ("life", "life_ps", "life_week"):
            T[k] = sum(p.get(k) or 0 for p in doc.get("producers") or [])
        if sold_changed:
            for k in ("pol", "ps", "cross_sell"):
                T[k] = sum(p.get(k) or 0 for p in doc.get("producers") or [])
            if isinstance(tiers, dict):
                team = tiers.setdefault("team", {})
                team["pol"] = cfg.tier("policy_count", T.get("pol") or 0)
                team["ps"] = "green" if T.get("ps") else team["pol"]
                _closing(team, T)
                doc["tiers"] = tiers
            _rescore(doc)
            sales_days.add(day)
        out[day] = doc
    return out, sales_days


def _lists(day, cli, bucket, log=print):
    """The policy list and lead-source map: this run's own data/ files (pulled
    on `day`), else the newest corpus snapshot in R2 at or before `day` -- a
    container's stale data/ from an earlier day never stands in."""
    pp, lp = ROOT / "data/az_policies_all.json", ROOT / "data/az_leads_all.json"
    fresh = lambda f: f.exists() and dt.datetime.fromtimestamp(f.stat().st_mtime).date().isoformat() >= day
    if fresh(pp) and fresh(lp):
        pol = json.loads(pp.read_text())
        leads = json.loads(lp.read_text())
    else:
        # Day by day back from `day`: a listing of cache/ is cut off by the
        # audio files long before the corpus keys.
        d, base = dt.date.fromisoformat(day), None
        for _ in range(30):
            try:
                cli.head_object(Bucket=bucket, Key=f"cache/{d.isoformat()}/corpus/az_policies_all.json.gz")
                base = f"cache/{d.isoformat()}/corpus/"
                break
            except Exception:
                d -= dt.timedelta(days=1)
        if not base:
            raise RuntimeError("no policy list in data/ and no corpus snapshot in R2 within 30 days")
        log(f"  late policies: policies from r2://{bucket}/{base}")
        pol = json.loads(gzip.decompress(cli.get_object(Bucket=bucket, Key=base + "az_policies_all.json.gz")["Body"].read()))
        leads = json.loads(gzip.decompress(cli.get_object(Bucket=bucket, Key=base + "az_leads_all.json.gz")["Body"].read()))
    return pol, cfg.lead_source_map(leads)


def _describe(doc, before):
    old = {p["name"]: p for p in before.get("producers") or []}
    bits = []
    for p in doc.get("producers") or []:
        o = old.get(p["name"], {})
        s = []
        dl = (p.get("life") or 0) - (o.get("life") or 0)
        dp = (p.get("pol") or 0) - (o.get("pol") or 0)
        if dl:
            s.append(f"+{dl} life")
        if (p.get("life_week") or 0) != (o.get("life_week") or 0):
            s.append(f"{p.get('life_week') or 0} this week")
        if dp:
            s.append(f"+{dp} policy ${(p.get('ps') or 0) - (o.get('ps') or 0):,}")
        if s:
            bits.append(f"{p['name'].split()[0]} " + ", ".join(s))
    return "; ".join(bits)


def run(day, lookback=LOOKBACK, dry_run=False, log=print):
    """Top up the published days of the `lookback` days before `day`.
    Returns the days changed."""
    import publish_board
    cli, bucket = publish_board._client()
    start = (dt.date.fromisoformat(day) - dt.timedelta(days=lookback)).isoformat()
    keys = [o["Key"][5:15] for o in cli.list_objects_v2(Bucket=bucket, Prefix="days/").get("Contents", [])
            if o["Key"].endswith(".json")]
    days = sorted(d for d in keys if start <= d < day)
    if not days:
        return []
    pol, smap = _lists(day, cli, bucket, log=log)
    azid = {v["az_id"]: n for n, v in cfg.PRODUCERS.items()}
    docs = {d: json.loads(cli.get_object(Bucket=bucket, Key=f"days/{d}.json")["Body"].read()) for d in days}
    changed, sales_days = plan(docs, pol, smap, azid)
    stamp = dt.date.today().isoformat()

    def save(d, doc, before, what):
        cli.put_object(Bucket=bucket, Key=f"backups/{stamp}-late-policies/days_{d}.json",
                       Body=json.dumps(before, default=str).encode(), ContentType="application/json")
        cli.put_object(Bucket=bucket, Key=f"days/{d}.json", Body=json.dumps(doc, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        log(f"  late policies: {d} -- {what}")

    written = []
    for d, doc in sorted(changed.items()):
        what = _describe(doc, docs[d])
        if dry_run:
            log(f"  late policies: {d} would change -- {what}")
            continue
        save(d, doc, docs[d], what)
        written.append(d)
    if not changed:
        log(f"  late policies: nothing missing on {days[0]}..{days[-1]}")
    if dry_run or not sales_days:
        return written
    # A sale added to a day shortens the producer's streak on every later
    # published day: recolour Policies there from the pages as they stand now.
    first = min(sales_days)
    for d in days:
        if d < first:
            continue
        doc = changed.get(d) or docs[d]
        before = copy.deepcopy(doc)
        publish_board.apply_policy_streak(doc, cli, bucket, log=log)
        if doc.get("policy_streak") != before.get("policy_streak") or doc.get("tiers") != before.get("tiers"):
            if d in written:
                cli.put_object(Bucket=bucket, Key=f"days/{d}.json", Body=json.dumps(doc, default=str).encode(),
                               ContentType="application/json", CacheControl="no-store")
                log(f"  late policies: {d} -- sale streak recoloured")
            else:
                save(d, doc, before, "sale streak recoloured")
                written.append(d)
    for month in sorted({d[:7] for d in sales_days}):
        publish_board.publish_month(month, cli=cli, bucket=bucket, log=log)
    return sorted(set(written))


def main():
    a = sys.argv[1:]
    day = a[a.index("--day") + 1] if "--day" in a else dt.date.today().isoformat()
    lookback = int(a[a.index("--lookback") + 1]) if "--lookback" in a else LOOKBACK
    run(day, lookback=lookback, dry_run="--dry-run" in a)


if __name__ == "__main__":
    main()

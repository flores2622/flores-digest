"""A life policy entered late reaches the day it was sold on.

Life Sold is counted by soldDate from the policy list the nightly run pulls
that evening. A life policy typed into AgencyZoom AFTER its day's run never
appeared anywhere: the day it was sold on had been built without it, and no
later day counts it (Frank, 2026-10-12: "we do have a life sale, its
alondra, why is it not on the totals" -- Coral's Individual Life for Alondra
Angulo, sold 09-29, entered 09-30 at 6:18 PM AZ's run was long gone). Only
the week's figure on 10-01 and 10-02 saw it, because `life_week` recounts
the week from the policy list each night.

So each nightly run re-reads the last LOOKBACK published days against its own
fresh policy list and ADDS any life policy a day is missing: that producer's
count and premium, the team's, the Life Sold list (`rows.life`) and the
week's figure on that day and the later published days of its week. It only
ever adds -- a published day never loses a figure here -- and nothing else on
the page changes. Premium Sold is not touched: a non-life policy entered late
is the Sales sheet's 14-day sync's business, and the day's sales stay as they
went out. Each page changed is backed up under backups/<today>-life-topup/.

    python3 life_topup.py [--day YYYY-MM-DD] [--lookback N] [--dry-run]

By hand it reads the policy and lead lists from data/ when a run left them,
else the newest corpus snapshot in R2 at or before --day.
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


def plan(docs, pol, smap, azid):
    """docs: {day: published document}. Returns {day: changed copy} for the
    days a late life policy (or the week's figure) was missing from. Pure."""
    out = {}
    docs = {d: copy.deepcopy(doc) for d, doc in docs.items()}
    by_day = {d: cfg.life_sales(d, pol, smap, azid) for d in docs}
    for day, doc in sorted(docs.items()):
        changed = False
        have_rows = {r.get("policy") for r in (doc.get("rows") or {}).get("life") or []}
        for p in doc.get("producers") or []:
            who = p.get("name")
            n, prem = by_day[day].get(who, (0, 0.0))
            if n > (p.get("life") or 0):
                p["life"], p["life_ps"] = n, round(prem)
                for x in pol:
                    if (str(x.get("soldDate") or "").startswith(day) and cfg.is_life(x)
                            and azid.get(x.get("agentId")) == who and cfg.is_real_sale(x, smap)
                            and (x.get("policyNumber") or "") not in have_rows):
                        doc.setdefault("rows", {}).setdefault("life", []).append(digest_rows.policy_row(x, who, smap))
                changed = True
            # The week's figure, Monday to this day, as daily.py counts it.
            wk = 0
            d = dt.date.fromisoformat(cfg.week_start(day))
            while d.isoformat() <= day:
                wk += cfg.life_sales(d.isoformat(), pol, smap, azid).get(who, (0, 0.0))[0]
                d += dt.timedelta(days=1)
            if wk > (p.get("life_week") or 0):
                p["life_week"] = wk
                changed = True
        if changed:
            t = doc.setdefault("totals", {})
            for k in ("life", "life_ps", "life_week"):
                t[k] = sum(p.get(k) or 0 for p in doc.get("producers") or [])
            out[day] = doc
    return out


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
        log(f"  life top-up: policies from r2://{bucket}/{base}")
        pol = json.loads(gzip.decompress(cli.get_object(Bucket=bucket, Key=base + "az_policies_all.json.gz")["Body"].read()))
        leads = json.loads(gzip.decompress(cli.get_object(Bucket=bucket, Key=base + "az_leads_all.json.gz")["Body"].read()))
    return pol, cfg.lead_source_map(leads)


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
    changed = plan(docs, pol, smap, azid)
    stamp = dt.date.today().isoformat()
    for d, doc in sorted(changed.items()):
        who = ", ".join(f"{p['name'].split()[0]} {p.get('life') or 0} ({p.get('life_week') or 0} this week)"
                        for p in doc["producers"] if (p.get("life") or p.get("life_week")))
        if dry_run:
            log(f"  life top-up: {d} would change -- {who}")
            continue
        cli.put_object(Bucket=bucket, Key=f"backups/{stamp}-life-topup/days_{d}.json",
                       Body=json.dumps(docs[d], default=str).encode(), ContentType="application/json")
        cli.put_object(Bucket=bucket, Key=f"days/{d}.json", Body=json.dumps(doc, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        log(f"  life top-up: {d} -- {who}")
    if not changed:
        log(f"  life top-up: nothing missing on {days[0]}..{days[-1]}")
    return sorted(changed)


def main():
    a = sys.argv[1:]
    day = a[a.index("--day") + 1] if "--day" in a else dt.date.today().isoformat()
    lookback = int(a[a.index("--lookback") + 1]) if "--lookback" in a else LOOKBACK
    run(day, lookback=lookback, dry_run="--dry-run" in a)


if __name__ == "__main__":
    main()

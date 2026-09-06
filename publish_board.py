"""Publish one Arizona day to the Sales Floor board's R2 store.

    python3 publish_board.py 2026-09-04          # build + upload that day
    python3 publish_board.py 2026-09-04 --dry-run # build, print, upload nothing

WHY THIS EXISTS. The board used to live in a claude.ai artifact, whose only
write path is `Artifact write_db` -- a Claude tool call, not an HTTP endpoint we
hold a key for. In an unattended run that call stops and waits for a human to
approve it, and nobody is watching at 7 PM. Measured on the real runs: the
2026-09-03 board document was built 2026-09-05 12:28, forty-one hours after its
emails went out, because the approval sat unanswered. The emails were never
affected -- they go out from inside this process through Resend, and nothing in
that path asks anyone anything.

So the rule this module exists to honour:

    ANYTHING THE SCRIPT DOES ITSELF RUNS UNATTENDED.
    ANYTHING THAT HAS TO BE A CLAUDE TOOL CALL CAN STOP AND WAIT.

An S3 PUT with a key we hold is the first kind. That is the whole point.

WHAT THE NIGHTLY RUN DOES. One `put_object` of `days/<day>.json`. No wrangler,
no node, no site deploy, no cache invalidation. The static shell and the
Worker that reads this bucket (site/public/, site/worker.js, wrangler.jsonc)
are deployed separately by the `flores-board` Workers Builds project, which
Cloudflare runs automatically on every push to main that touches those paths
-- there is no manual deploy step and no deploy_site.py. Keeping the nightly
path down to a single HTTP call is deliberate: every additional step is
another thing that can fail at 7 PM while nobody is looking.

THE DATA IS NOT PUBLIC. `days/<day>.json` carries customer names, phone numbers
and notes on what coverage they were quoted -- see `recontact.at_risk[].
lead_name` and `task_audit.rows.*[].phones`. That is customer NPI belonging to
an insurance agency, not a scoreboard. The bucket therefore stays PRIVATE: it is
never given a public r2.dev URL and never a public custom domain. The only
reader is the flores-board Worker, through its binding, and the whole site sits
behind Cloudflare Access. If you are ever tempted to "just make the bucket
public to debug something", don't -- serve it through the Worker or read it
with this module's --dry-run.
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

import board_payload
import secrets_load

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))

# Object layout in the bucket. site/worker.js maps /api/days/<day> onto
# days/<day>.json and lists this prefix for the date picker, so a change here
# is a change there too.
PREFIX = "days"
MONTH_PREFIX = "months"


def _key(day):
    return f"{PREFIX}/{day}.json"


def _month_key(month):
    return f"{MONTH_PREFIX}/{month}.json"


def _client():
    """An S3 client pointed at this account's R2 endpoint.

    R2 speaks the S3 API, so boto3 works unchanged -- no node, no wrangler, and
    nothing to install in the container beyond boto3 itself. `region_name` must
    be "auto"; R2 rejects a real AWS region.
    """
    import boto3
    s = secrets_load.load("CF_ACCOUNT_ID", "R2_ACCESS_KEY_ID",
                          "R2_SECRET_ACCESS_KEY", "R2_BUCKET")
    return boto3.client(
        "s3",
        endpoint_url=f"https://{s['CF_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=s["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=s["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    ), s["R2_BUCKET"]


def build(day):
    """The day document. Identical shape to what the artifact board was fed.

    If `coaching/cards_<day>.py` exists it is used instead, exactly as before:
    it builds the same document plus the authored per-call coaching cards. The
    cards are AUTHORED, never generated -- an invented coaching card is worse
    than an empty tab, because someone will coach a producer on it.
    """
    cards = ROOT / f"coaching/cards_{day}.py"
    if cards.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location(f"cards_{day}", cards)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.build(day)
    return board_payload.build(day)


def publish(day, doc=None, log=print):
    """Upload one day. Returns the key written.

    Callers in the nightly path must not let this raise -- see daily.publish
    for the wrapper. Raising here is correct for a hand run, where a traceback
    is what you want.
    """
    doc = doc if doc is not None else build(day)
    body = json.dumps(doc, default=str).encode()
    cli, bucket = _client()
    cli.put_object(
        Bucket=bucket, Key=_key(day), Body=body,
        ContentType="application/json",
        # The Function is the only reader and it always fetches by exact key,
        # so nothing caches this. Said explicitly so a future custom domain
        # cannot start serving a stale day.
        CacheControl="no-store",
    )
    log(f"  board: {len(body):,} bytes -> r2://{bucket}/{_key(day)}")
    publish_month(day[:7], cli=cli, bucket=bucket, log=log)
    return _key(day)


def publish_month(month, cli=None, bucket=None, log=print):
    """Roll every day of `month` up into months/<YYYY-MM>.json.

    WHY A STORED ROLLUP RATHER THAN AGGREGATING IN THE WORKER. A month is up
    to 23 day documents at 20-135 KB each, so making the dashboard aggregate
    on the fly would mean up to ~3 MB of R2 reads on every page load, growing
    through the month, paid again for every viewer. Rolling it up once a night
    costs one extra listing and turns the dashboard's month view into a single
    small read.

    ALWAYS RECOMPUTED FROM SCRATCH, never incremented. A rebuilt past day
    (`daily.py --day ...`) rewrites its own document, and the next nightly run
    then folds the corrected figures in automatically. An incremental counter
    would silently keep the old numbers, which is the same class of bug as the
    stale-corpus one in CLAUDE.md.

    RATES ARE RECOMPUTED, NEVER AVERAGED. Month contact rate is
    sum(live)/sum(dials) across the month -- averaging five daily percentages
    weights a 15-dial day the same as a 76-dial one. Same for avg talk time,
    which is weighted by live contacts.
    """
    if cli is None:
        cli, bucket = _client()

    days, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": f"{PREFIX}/{month}-"}
        if token:
            kw["ContinuationToken"] = token
        page = cli.list_objects_v2(**kw)
        for o in page.get("Contents", []):
            m = re.match(rf"^{PREFIX}/(\d{{4}}-\d{{2}}-\d{{2}})\.json$", o["Key"])
            if m:
                days.append(m.group(1))
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")

    if not days:
        log(f"  month {month}: no day documents, nothing to roll up")
        return None

    docs = []
    for d in sorted(days):
        body = cli.get_object(Bucket=bucket, Key=_key(d))["Body"].read()
        docs.append(json.loads(body))

    NUM = ("dials", "live", "hh", "pq", "ps", "pol")
    totals = {k: 0 for k in NUM}
    per = {}
    trend = []

    for doc in docs:
        t = doc.get("totals") or {}
        for k in NUM:
            totals[k] += t.get(k) or 0
        trend.append({
            "date": doc.get("date"),
            "dials": t.get("dials") or 0,
            "live": t.get("live") or 0,
            "rate": t.get("rate") or 0,
            "pq": t.get("pq") or 0,
            "ps": t.get("ps") or 0,
        })
        for p in doc.get("producers") or []:
            row = per.setdefault(p["name"], {k: 0 for k in NUM} |
                                 {"name": p["name"], "days": 0, "talk_secs": 0})
            for k in NUM:
                row[k] += p.get(k) or 0
            row["days"] += 1
            # Talk time is an average per live contact, so it re-weights by
            # live contacts rather than by day.
            row["talk_secs"] += (p.get("talk") or 0) * (p.get("live") or 0)

    for row in per.values():
        row["rate"] = round(100 * row["live"] / row["dials"], 1) if row["dials"] else 0.0
        row["talk"] = round(row["talk_secs"] / row["live"]) if row["live"] else 0
        del row["talk_secs"]

    totals["rate"] = (round(100 * totals["live"] / totals["dials"], 1)
                      if totals["dials"] else 0.0)

    doc = {
        "month": month,
        "label": dt.date.fromisoformat(f"{month}-01").strftime("%B %Y"),
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "days": sorted(days),
        "business_days": len(days),
        "totals": totals,
        "producers": sorted(per.values(), key=lambda r: -r["ps"]),
        "trend": trend,
    }
    body = json.dumps(doc, default=str).encode()
    cli.put_object(Bucket=bucket, Key=_month_key(month), Body=body,
                   ContentType="application/json", CacheControl="no-store")
    log(f"  month:  {len(body):,} bytes -> r2://{bucket}/{_month_key(month)} "
        f"({len(days)} day{'' if len(days) == 1 else 's'})")
    return _month_key(month)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("day", nargs="?")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and print the document, upload nothing")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    doc = build(day)
    if a.dry_run:
        json.dump(doc, sys.stdout, indent=1, default=str)
        print()
        return
    publish(day, doc)


if __name__ == "__main__":
    main()

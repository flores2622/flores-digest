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
no node, no site deploy, no cache invalidation. The static shell and the Pages
Function that reads this bucket are deployed ONCE by `deploy_site.py`, and only
again when the UI changes. Keeping the nightly path down to a single HTTP call
is deliberate: every additional step is another thing that can fail at 7 PM
while nobody is looking.

THE DATA IS NOT PUBLIC. `days/<day>.json` carries customer names, phone numbers
and notes on what coverage they were quoted -- see `recontact.at_risk[].
lead_name` and `task_audit.rows.*[].phones`. That is customer NPI belonging to
an insurance agency, not a scoreboard. The bucket therefore stays PRIVATE: it is
never given a public r2.dev URL and never a public custom domain. The only
reader is the Pages Function, through its binding, and the whole site sits
behind Cloudflare Access. If you are ever tempted to "just make the bucket
public to debug something", don't -- serve it through the Function or read it
with this module's --dry-run.
"""
import argparse
import datetime as dt
import json
import pathlib
import sys

import board_payload
import secrets_load

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))

# Object layout in the bucket. The Function maps /api/days/<day> onto
# days/<day>.json and lists this prefix for the date picker, so a change here
# is a change in site/functions/api/days/ too.
PREFIX = "days"


def _key(day):
    return f"{PREFIX}/{day}.json"


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
    return _key(day)


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

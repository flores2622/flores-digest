"""Mirror AgencyZoom into Pantheon's CRM every run (CRM.md, phase 2, step 1).

    python3 crm_sync.py                 sync what the saved data/ files hold
    python3 crm_sync.py --full          resend everything (ignore the state)
    python3 crm_sync.py --dry-run       build and count, send nothing
    python3 crm_sync.py --sqlite out/x.db --state out/state.json
                                        the same run against a local SQLite
                                        (tests; no network, no R2)

While AgencyZoom is still the record, every run of the nightly (daily.py)
and every hourly checkpoint (intraday.py) calls run(): the rows crm_import
builds from the files the run just saved -- leads, households, policies,
tasks, SRs, notes, stage moves, the lookups -- go to the D1 database as
upserts (crm_import.statement, mode "upsert"): a new record is added, an
imported record AgencyZoom changed is updated, a row Pantheon made itself
(az_id NULL) is never touched. The first run is the full load.

Only what changed is sent. The state -- one fingerprint per row, by table
and id -- lives in R2 (cache/crm_sync_state.json, STATE_KEY), since a
scheduled run gets a cold container; it is written back after each batch
that D1 accepted, so a run that dies midway resends only what it had not
yet sent. Rows go over Cloudflare's D1 REST API
(POST /accounts/<CF_ACCOUNT_ID>/d1/database/<id>/query), several literal
statements per request, batched by size (BATCH_BYTES), the database id read
from wrangler.jsonc (or CRM_D1_ID).

It needs CF_API_TOKEN (a Cloudflare API token with D1 edit; CLOUDFLARE_API_TOKEN
is read too) in the cloud environment's variables beside the R2 keys.
Without it, or on any error, run() logs one line and the run carries on:
the CRM sync is a saving, never a step the digest depends on.
"""
import hashlib
import json
import os
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import crm_import   # noqa: E402

STATE_KEY = "cache/crm_sync_state.json"
BATCH_BYTES = 60_000          # SQL text per D1 request (its statement limit is 100 KB)
BATCH_STATEMENTS = 200
API = "https://api.cloudflare.com/client/v4"
TOKEN_NAMES = ("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN")


def token():
    for n in TOKEN_NAMES:
        if os.environ.get(n):
            return os.environ[n]
    return None


def database_id():
    if os.environ.get("CRM_D1_ID"):
        return os.environ["CRM_D1_ID"]
    m = re.search(r'"database_id":\s*"([0-9a-f-]{36})"', (ROOT / "wrangler.jsonc").read_text())
    return m.group(1) if m else None


class D1:
    """The D1 REST API: execute(sql) runs one or more literal statements."""
    def __init__(self, account, dbid, tok):
        import requests
        self.url = f"{API}/accounts/{account}/d1/database/{dbid}/query"
        self.http = requests.Session()
        self.http.headers.update({"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})

    def execute(self, sql):
        for attempt in range(3):
            r = self.http.post(self.url, json={"sql": sql}, timeout=120)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            j = r.json()
            if not j.get("success"):
                raise RuntimeError(f"D1 {r.status_code}: {str(j.get('errors'))[:300]}")
            return j.get("result")
        raise RuntimeError(f"D1 kept answering {r.status_code}")


class Local:
    """The same interface over a SQLite file (tests)."""
    def __init__(self, path):
        import sqlite3
        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.c = sqlite3.connect(p)
        for f in sorted((ROOT / "site" / "crm" / "migrations").glob("*.sql")):
            self.c.executescript(f.read_text())

    def execute(self, sql):
        self.c.executescript(sql)
        self.c.commit()


# ---- the state ------------------------------------------------------------------
def _r2():
    import publish_board
    return publish_board._client()


def load_state(path=None):
    if path:
        p = pathlib.Path(path)
        return json.loads(p.read_text()) if p.exists() else {}
    cli, bucket = _r2()
    try:
        return json.loads(cli.get_object(Bucket=bucket, Key=STATE_KEY)["Body"].read())
    except cli.exceptions.NoSuchKey:
        return {}


def save_state(state, path=None):
    body = json.dumps(state, separators=(",", ":"))
    if path:
        pathlib.Path(path).write_text(body)
        return
    cli, bucket = _r2()
    cli.put_object(Bucket=bucket, Key=STATE_KEY, Body=body.encode(), ContentType="application/json")


def fingerprint(row):
    return hashlib.sha1(json.dumps(row, sort_keys=True, default=str).encode()).hexdigest()[:16]


def row_key(table, row):
    """What identifies a row in the state: its id, or a stage move's note."""
    if row.get("id") is not None:
        return str(row["id"])
    if table == "stage_moves":
        return f"n{row.get('note_id')}"
    return fingerprint(row)


# ---- the run ---------------------------------------------------------------------
def plan(rows, state, full=False):
    """(statements with their state updates) for every row new or changed."""
    out = []
    for table, row in rows.rows:
        k = row_key(table, row)
        fp = fingerprint(row)
        if not full and state.get(table, {}).get(k) == fp:
            continue
        out.append((table, k, fp, crm_import.statement(table, row, "upsert")))
    return out


def batches(items):
    cur, size = [], 0
    for it in items:
        n = len(it[3]) + 1
        if cur and (size + n > BATCH_BYTES or len(cur) >= BATCH_STATEMENTS):
            yield cur
            cur, size = [], 0
        cur.append(it)
        size += n
    if cur:
        yield cur


def sync(db, rows, state, log=print, full=False, dry_run=False, save=lambda s: None):
    todo = plan(rows, state, full)
    if not todo:
        log("  crm sync: nothing new")
        return 0
    by_table = {}
    for t, *_ in todo:
        by_table[t] = by_table.get(t, 0) + 1
    log("  crm sync: " + ", ".join(f"{t} {n:,}" for t, n in sorted(by_table.items())) + (" (dry run)" if dry_run else ""))
    if dry_run:
        return len(todo)
    sent = 0
    for batch in batches(todo):
        db.execute("\n".join(it[3] for it in batch))
        for t, k, fp, _ in batch:
            state.setdefault(t, {})[k] = fp
        sent += len(batch)
        save(state)
    log(f"  crm sync: {sent:,} rows sent")
    return sent


def run(days=None, log=print, full=False, dry_run=False):
    """The nightly's and the checkpoints' call: never raises."""
    try:
        tok = token()
        if not tok:
            log("  crm sync: CF_API_TOKEN not set -- skipped")
            return 0
        dbid = database_id()
        account = os.environ.get("CF_ACCOUNT_ID")
        if not dbid or not account:
            log("  crm sync: no D1 database id (wrangler.jsonc) or CF_ACCOUNT_ID -- skipped")
            return 0
        rows = crm_import.build(crm_import.Rows(), days=days)
        state = load_state()
        return sync(D1(account, dbid, tok), rows, state, log=log, full=full, dry_run=dry_run, save=save_state)
    except (Exception, SystemExit) as e:
        log(f"  crm sync failed ({type(e).__name__}: {str(e)[:200]}) -- carrying on without it")
        return 0


def run_local(sqlite_path, state_path, days=None, log=print, full=False):
    rows = crm_import.build(crm_import.Rows(), days=days)
    state = load_state(state_path)
    return sync(Local(sqlite_path), rows, state, log=log, full=full, save=lambda s: save_state(s, state_path))


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--sqlite" in a:
        n = run_local(a[a.index("--sqlite") + 1], a[a.index("--state") + 1] if "--state" in a else "out/crm_sync_state.json", full="--full" in a)
    else:
        import secrets_load
        try:
            secrets_load.load()
        except SystemExit:
            pass
        n = run(full="--full" in a, dry_run="--dry-run" in a)
    print(f"crm sync: {n:,} rows")

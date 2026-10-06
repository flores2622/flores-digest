"""Mirror AgencyZoom into Pantheon's CRM every run (CRM.md, phase 2, step 1).

    python3 crm_sync.py                 sync what the saved data/ files hold
    python3 crm_sync.py --full          resend everything (ignore the state)
    python3 crm_sync.py --dry-run       build and count, send nothing
    python3 crm_sync.py --from-r2 2026-10-06 [--dry-run]
                                        a load by hand from any machine with
                                        the R2 keys: restore that day's
                                        AgencyZoom corpus, the household map,
                                        the lead sources and the last 30 days'
                                        task and SR files from R2, fetch the
                                        pipelines and SR categories once if
                                        missing, then sync
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
# D1 counts every index entry as a row written (a lead costs ~8), and the free
# tier allows 100,000 a day: the first load tripped it on 2026-10-06. A run
# sends at most this many rows and leaves the rest for the next one, so a
# fingerprint change or a re-import can never spend a whole day's budget at
# once (CRM_SYNC_MAX_ROWS overrides).
MAX_ROWS_PER_RUN = int(os.environ.get("CRM_SYNC_MAX_ROWS") or 25_000)
# The database refusing everything (the daily write limit, a bad token, a
# schema mismatch) is not a bad row: stop the run instead of retrying each row.
REFUSED_ALL = re.compile(r"limit|quota|exceeded|blocked|unauthori|authentication|no such table|no such column", re.I)
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
        fresh = not p.exists() or p.stat().st_size == 0
        self.c = sqlite3.connect(p)
        if fresh:   # the migrations once, like `wrangler d1 migrations apply`
            for f in sorted((ROOT / "site" / "crm" / "migrations").glob("*.sql")):
                self.c.executescript(f.read_text())
        self.c.execute("PRAGMA foreign_keys = ON")   # D1 enforces them; so does this copy

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
    """What identifies a row in the state: its id, or a stage move's note; a
    list entry or a map row by its kind and id (the two tables' keys)."""
    if table == "lists":
        return f"{row.get('kind')}:{row.get('id')}"
    if table == "list_map":
        return f"{row.get('kind')}:{row.get('az_id')}"
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


LISTS_MIGRATION = ROOT / "site" / "crm" / "migrations" / "0004_lists.sql"


def ensure_lists_tables(db, log=print):
    """The lists and list_map tables (migration 0004) exist before their rows
    go: CREATE TABLE IF NOT EXISTS, so a database that has them is untouched
    (no row written). `wrangler d1 migrations apply` is still the formal
    route; this only keeps a deploy that went out before it from failing
    every lists row until someone runs it."""
    try:
        db.execute(LISTS_MIGRATION.read_text())
    except Exception as e:
        log(f"  crm sync: could not check the lists tables ({str(e)[:120]})")


def sync(db, rows, state, log=print, full=False, dry_run=False, save=lambda s: None):
    todo = plan(rows, state, full)
    if not todo:
        log("  crm sync: nothing new")
        return 0
    held = 0
    if len(todo) > MAX_ROWS_PER_RUN:
        held = len(todo) - MAX_ROWS_PER_RUN
        todo = todo[:MAX_ROWS_PER_RUN]
    by_table = {}
    for t, *_ in todo:
        by_table[t] = by_table.get(t, 0) + 1
    log("  crm sync: " + ", ".join(f"{t} {n:,}" for t, n in sorted(by_table.items())) + (" (dry run)" if dry_run else "")
        + (f"; {held:,} more held for the next run" if held else ""))
    if dry_run:
        return len(todo)
    if any(t in ("lists", "list_map") for t, *_ in todo):
        ensure_lists_tables(db, log)
    sent, bad = 0, []
    for batch in batches(todo):
        try:
            db.execute("\n".join(it[3] for it in batch))
            ok = batch
        except Exception as e:
            if REFUSED_ALL.search(str(e)):
                raise RuntimeError(f"the database is refusing writes ({str(e)[:160]}); {sent:,} rows were sent, the rest wait for the next run")
            # One bad row must not stop the load: find it, log it, leave it out
            # of the state so the next run tries it again, and keep the rest.
            ok, errs = [], []
            for it in batch:
                try:
                    db.execute(it[3])
                    ok.append(it)
                except Exception as e1:
                    bad.append((it[0], it[1], str(e1)[:160]))
                    errs.append(str(e1)[:160])
                    if len(errs) >= 3 and not ok and len(set(errs)) == 1:
                        raise RuntimeError(f"the database is refusing every row ({errs[0]}); {sent:,} rows were sent, the rest wait for the next run")
        for t, k, fp, _ in ok:
            state.setdefault(t, {})[k] = fp
        sent += len(ok)
        save(state)
    log(f"  crm sync: {sent:,} rows sent" + (f", {len(bad):,} refused" if bad else ""))
    for t, k, err in bad[:10]:
        log(f"    refused {t} {k}: {err}")
    if len(bad) > 10:
        log(f"    ... and {len(bad) - 10:,} more")
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


RESTORE_DAYS = 30   # how far back a hand run pulls task and SR files


def restore_from_r2(day, log=print):
    """A hand run's inputs, into data/: the day's corpus snapshot, the household
    map and the Worker's lead source names, plus the task and SR files of the
    last RESTORE_DAYS days (a day's completed-SR file is written by the
    nightly, so today's exists only after 5:55 PM; tasks are one file per
    day, merged by id). The pipelines and SR categories come from AgencyZoom
    only when no file holds them (two requests, the same ones daily.py makes
    once per cold container). Returns the set of days whose files are here."""
    import datetime as dt
    import r2_cache
    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    if not r2_cache.load_corpus(day, log=log):
        raise RuntimeError(f"no corpus snapshot in R2 for {day} (cache/{day}/corpus/)")
    cli, bucket = _r2()

    def pull(key, name):
        try:
            (data / name).write_bytes(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
            return True
        except Exception:
            return False
    if not pull("cache/az_household_policies.json", "az_household_policies.json"):
        log("  az_household_policies.json: not in R2 -- policies load without their household")
    pull("worker-private/lead_sources.json", "az_lead_sources.json")
    d0 = dt.date.fromisoformat(day)
    days, got = set(), {"tasks": 0, "live": 0, "done": 0}
    for back in range(RESTORE_DAYS):
        d = (d0 - dt.timedelta(days=back)).isoformat()
        hit = False
        for kind, name in (("tasks", f"az_tasks_{d}.json"), ("live", f"az_service_tickets_{d}.json"), ("done", f"az_service_tickets_done_{d}.json")):
            if pull(f"cache/{d}/{name}", name):
                got[kind] += 1
                hit = True
        if hit:
            days.add(d)
    log(f"  restored from R2: {day}'s corpus, {got['tasks']} days of tasks, {got['live']} live-SR and {got['done']} completed-SR files")
    if not got["done"]:
        log("  no completed-SR file in the window -- the completed SRs load once the nightly writes one")
    if not (data / "az_pipelines.json").exists() or not (data / "az_service_categories.json").exists():
        from az_client import AgencyZoom
        az = AgencyZoom()
        if not (data / "az_pipelines.json").exists():
            (data / "az_pipelines.json").write_text(json.dumps(az.pipelines_and_stages()))
        if not (data / "az_service_categories.json").exists():
            (data / "az_service_categories.json").write_text(json.dumps(az.service_categories()))
    return days or {day}


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
        days = None
        if "--from-r2" in a:
            days = restore_from_r2(a[a.index("--from-r2") + 1])
        if not token():
            print("CF_API_TOKEN (or CLOUDFLARE_API_TOKEN) is not set in this environment; "
                  "names seen that look related: " + ", ".join(sorted(k for k in os.environ if any(
                      w in k.upper() for w in ("TOKEN", "CLOUDFLARE", "CF_", "D1", "CRM")))))
        n = run(days=days, full="--full" in a, dry_run="--dry-run" in a)
    print(f"crm sync: {n:,} rows")

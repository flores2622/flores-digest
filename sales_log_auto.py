"""Auto-populate the Sales Sheet's self-reported log from real AgencyZoom
policies, for producers AND Amanda Torricellas (Frank, 2026-09-15: "i want
automation for the sales sheet for all producers, including amanda. that
is the only place i want her sales included").

SCOPE. Touches ONLY saleslog/<day>.json, the Sales Sheet's own R2
document -- never days/<day>.json or anything else the official Premium
Sold/Policies figures read. Amanda's agentId is deliberately excluded
from those figures everywhere else on the board (daily.py's own `azid`
mapping, built from digest_config.PRODUCERS only) and stays excluded
there; this module builds its OWN, separate id->name mapping (PRODUCERS
plus Amanda) used for nothing but this file. No cost: every input here
is already-fetched REST data (policies/leads/customers), no paid API
call, unlike coaching_cards.py or call_summary.py.

WHAT A POLICY RECORD DOES AND DOESN'T CARRY. policyNumber, premium,
policyTypeName (product), effectiveDate, expiryDate (term is derived
from the two), agentId, soldDate, leadSourceId are all present. NOT
present: customer name, phone, customerId, leadId -- CLAUDE.md's own
note that "policy records carry no name, phone, customerId or leadId" is
correct for those four, just not for the rest.

BEST-EFFORT NAME MATCH, NOT A GUARANTEE. There is no direct policy ->
customer join. The only path is policy -> (best-effort) sold lead ->
lead.convertedHouseholdId -> customer, matched by (soldDate is implied by
both being filtered to `day` already, agentId == lead.assignedTo,
leadSourceId). Measured against a real month: a unique match for about
half of sold policies, zero AMBIGUOUS matches (when it resolves, it
resolves to exactly one lead) -- so this only ever fills in a name it's
actually confident about. When no unique match exists (a renewal, a book
roll, or any sale with no corresponding "sold" lead -- common on
Amanda's book specifically), client_name/az_customer_id are left BLANK,
never guessed at (Frank's own call when asked how to handle this:
"leave client name blank" rather than a placeholder). A producer fills
it in by hand, same as any other blank field on this self-reported
sheet.

IDEMPOTENT ACROSS RERUNS. Every policy's own AgencyZoom `id` is stored
on the entry as az_policy_id -- sync_day() never creates a second entry
for one it already added (checked by az_policy_id), and never
duplicates a sale someone already typed in by hand (checked by a
matching, non-empty policy_number, but ONLY against entries that have no
az_policy_id of their own -- i.e. genuinely hand-typed ones). That second
check is deliberately a frozen snapshot of what existed when sync_day
started, never updated as it adds new entries: real data caught a case
where two DIFFERENT real policy records (distinct az_policy_id, distinct
premium -- one line per vehicle on a multi-vehicle policy) shared one
displayed policyNumber, and mutating the snapshot mid-run would have
silently dropped the second one as a false duplicate of the first. Both
daily.py (nightly) and intraday.py (each checkpoint) call this, guarded
in a try/except exactly like publish_day -- a Cloudflare/R2 hiccup here
must cost this feature alone, never the digest or the rest of the board.
R2 is the only state,
so a rerun this hour or six months from now behaves identically: it
only ever adds what's missing, never edits or removes an existing row
(including one a producer has since hand-corrected).

Entries this module adds carry "source": "auto" (a manually-typed entry
via the Worker's POST has no such key) so the board can flag them
distinctly -- see index.html's card rendering.
"""
import datetime as dt
import json
import pathlib
import re
import uuid

import digest_config as cfg

ROOT = pathlib.Path(__file__).resolve().parent


def _ids():
    """az_id -> canonical display name, for exactly the people this sheet
    should auto-log: the 5 tracked producers plus Amanda -- deliberately
    narrower than "every AgencyZoom agent" (no CSRs, no Frank, no Debbie)."""
    out = {v["az_id"]: k for k, v in cfg.PRODUCERS.items()}
    out[cfg.OTHER_EXT["Amanda Torricellas"]["az_id"]] = "Amanda Torricellas"
    return out


def _date10(s):
    return str(s or "")[:10]


def _term(effective, expiry):
    e, x = _date10(effective), _date10(expiry)
    if not e or not x:
        return ""
    try:
        d1 = dt.date.fromisoformat(e)
        d2 = dt.date.fromisoformat(x)
    except ValueError:
        return ""
    months = round((d2 - d1).days / 30.44)
    return f"{months}mo" if months > 0 else ""


# Product names as the team types them on the sheet ("Farmers-Auto",
# "BW-Auto", "Foremost-MH"), not AgencyZoom's bare policy type (Frank,
# 2026-09-25: the Breakdown showed three auto options -- "Auto" from these
# auto-added rows beside Farmers-Auto and BW-Auto -- "we only have 2 auto
# products"). The carrier decides, read off the policy corpus 2026-09-25:
#   Farmers  484668, 484654, and 1030958 ("Standard Auto" on 9-digit numbers,
#            still sold 2026-08; not Bristol West's G01- numbers)
#   BW       186, 2448054 (every G01- policy number)
#   Foremost 102, 262
# Anything else keeps AgencyZoom's own name.
CARRIER = {484668: "Farmers", 484654: "Farmers", 1030958: "Farmers",
           186: "BW", 2448054: "BW", 102: "Foremost", 262: "Foremost"}
_AUTO_TYPES = re.compile(r"auto", re.I)
_TOY_TYPES = re.compile(r"atv|motorcycle|trailer|boat|watercraft|motor home|\brv\b|golf cart|toy", re.I)


def product_name(p):
    """The sheet's product name for one AgencyZoom policy record."""
    raw = str(p.get("policyTypeName") or "").strip()
    carrier = CARRIER.get(p.get("carrierId"))
    if not carrier or not raw:
        return raw
    if carrier == "BW":
        return "BW-Auto" if _AUTO_TYPES.search(raw) else f"BW-{raw}"
    if _AUTO_TYPES.search(raw):
        return f"{carrier}-Auto"
    if carrier == "Foremost":
        if re.search(r"mobile|manufactured", raw, re.I):
            return "Foremost-MH"
        if re.search(r"landlord|dp\d|dwelling", raw, re.I):
            return "Foremost-Landlord"
        if _TOY_TYPES.search(raw):
            return "Foremost-Toys"
        if re.search(r"vacant", raw, re.I):
            return "Foremost-Vacant"
        if re.search(r"home|ho-?\d", raw, re.I):
            return "Foremost-Home"
    if carrier == "Farmers":
        if re.search(r"homeowner|^home$|ho-?\d", raw, re.I):
            return "Farmers-Home"
        if re.search(r"term|life", raw, re.I):
            return "Farmers-Life"
    return f"{carrier}-{raw}"


def _customer_name(cust):
    return f"{(cust.get('firstname') or '').strip()} {(cust.get('lastname') or '').strip()}".strip()


def build_entries(day, policies, leads, customers, source_map, ids):
    """One dict per genuine sale on `day` by someone in `ids`, ready to
    append to a saleslog document (still missing id/created_at/day/
    docs_signed/review_sent/notes/source, which sync_day fills in at
    write time -- kept out of here so this function stays a pure,
    easily-tested read of the three corpora)."""
    customers_by_id = {c["id"]: c for c in customers if c.get("id") is not None}
    sold_leads = [l for l in leads if str(l.get("soldDate") or "").startswith(day)]

    out = []
    for p in policies:
        if not str(p.get("soldDate") or "").startswith(day):
            continue
        who = ids.get(p.get("agentId"))
        if not who or not cfg.is_real_sale(p, source_map):
            continue

        client_name, az_customer_id = "", ""
        candidates = [l for l in sold_leads
                      if l.get("assignedTo") == p.get("agentId")
                      and l.get("leadSourceId") == p.get("leadSourceId")]
        if len(candidates) == 1:
            hh_id = candidates[0].get("convertedHouseholdId")
            cust = customers_by_id.get(hh_id) if hh_id else None
            if cust:
                client_name = _customer_name(cust)
                az_customer_id = str(cust["id"])

        out.append({
            "producer": who,
            "client_name": client_name,
            "az_customer_id": az_customer_id,
            "lead_source": (source_map.get(p.get("leadSourceId")) or "").strip(),
            "policy_number": str(p.get("policyNumber") or ""),
            "product": product_name(p),
            "premium": float(p["premium"]) if p.get("premium") is not None else None,
            "term": _term(p.get("effectiveDate"), p.get("expiryDate")),
            "date_sold": _date10(p.get("soldDate")),
            "effective_date": _date10(p.get("effectiveDate")),
            "az_policy_id": p.get("id"),
        })
    return out


def sync_day(day, log=print, dry_run=False):
    """Add any missing auto-entries for `day` to saleslog/<day>.json.
    Returns the number of entries added. Never touches an existing entry
    -- only appends new ones, so a producer's hand-edits (docs signed,
    review sent, a corrected name) are never overwritten by a later run.
    """
    policies = json.loads((ROOT / "data/az_policies_all.json").read_text())
    leads = json.loads((ROOT / "data/az_leads_all.json").read_text())
    customers = json.loads((ROOT / "data/az_customers_all.json").read_text())
    source_map = cfg.lead_source_map(leads)
    candidates = build_entries(day, policies, leads, customers, source_map, _ids())
    if not candidates:
        log(f"  sales log auto: no new-business sales found for {day}")
        return 0

    import publish_board
    cli, bucket = publish_board._client()
    key = f"saleslog/{day}.json"
    try:
        body = cli.get_object(Bucket=bucket, Key=key)["Body"].read()
        doc = json.loads(body)
    except Exception:
        doc = {"day": day, "entries": []}

    existing_policy_ids = {e["az_policy_id"] for e in doc["entries"] if e.get("az_policy_id")}
    # Only guards against a policy a human already typed in by hand (no
    # az_policy_id of its own to match on) -- a FROZEN snapshot, never
    # updated as this loop adds new auto entries below. Real data caught
    # why that matters: two genuinely different policy records (different
    # az_policy_id, different premium -- one line per vehicle on a multi-
    # vehicle policy) can share one displayed policyNumber, and mutating
    # this set mid-loop would silently drop the second one as a false
    # "duplicate" of the first.
    existing_manual_policy_numbers = {e["policy_number"] for e in doc["entries"]
                                       if e.get("policy_number") and not e.get("az_policy_id")}

    added = 0
    for c in candidates:
        if c["az_policy_id"] in existing_policy_ids:
            continue
        if c["policy_number"] and c["policy_number"] in existing_manual_policy_numbers:
            continue
        entry = dict(c)
        entry["id"] = str(uuid.uuid4())
        entry["created_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        entry["day"] = day
        entry["docs_signed"] = ""
        entry["review_sent"] = False
        entry["notes"] = "Auto-added from AgencyZoom"
        entry["source"] = "auto"
        doc["entries"].append(entry)
        added += 1
        if c["az_policy_id"]:
            existing_policy_ids.add(c["az_policy_id"])

    if not added:
        log(f"  sales log auto: {len(candidates)} sale(s) found for {day}, all already logged")
        return 0

    log(f"  sales log auto: {added} new sale(s) added for {day}"
        + (" [dry-run, not written]" if dry_run else ""))
    if dry_run:
        return added

    cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc).encode(),
                    ContentType="application/json", CacheControl="no-store")
    return added


def fix_products(log=print, dry_run=False, since=None):
    """One pass over every saleslog/<day>.json (from `since` on, when given):
    an auto-added entry whose
    product is still AgencyZoom's raw policy type gets the sheet's name
    (product_name). An entry someone has since edited, or typed by hand, is
    left alone -- the same never-overwrite-a-person rule as sync_day. Run
    nightly over the last two weeks too, so a sale newer than that night's
    policy snapshot (Amanda's 553727161, sold 09-24) is named once the
    snapshot catches up."""
    import publish_board
    by_id = {p.get("id"): p for p in json.loads((ROOT / "data/az_policies_all.json").read_text())}
    cli, bucket = publish_board._client()
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": "saleslog/"}
        if token:
            kw["ContinuationToken"] = token
        r = cli.list_objects_v2(**kw)
        keys += [o["Key"] for o in r.get("Contents", []) if o["Key"].endswith(".json")
                 and (since is None or o["Key"][9:19] >= since)]
        if not r.get("IsTruncated"):
            break
        token = r["NextContinuationToken"]
    total = 0
    for key in sorted(keys):
        doc = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        n = 0
        for e in doc.get("entries") or []:
            p = by_id.get(e.get("az_policy_id"))
            if e.get("source") != "auto" or p is None:
                continue
            if e.get("product") == str(p.get("policyTypeName") or "") and product_name(p) != e.get("product"):
                log(f"  {key[9:19]} {e.get('policy_number')}: {e.get('product')!r} -> {product_name(p)!r}")
                e["product"] = product_name(p)
                n += 1
        if n and not dry_run:
            cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc).encode(),
                           ContentType="application/json", CacheControl="no-store")
        total += n
    if total or since is None:
        log(f"  sales log products: {total} auto-added entr{'y' if total == 1 else 'ies'} renamed"
            + (" [dry-run, not written]" if dry_run else ""))
    return total


if __name__ == "__main__":
    import sys
    import secrets_load
    secrets_load.load()
    if "--fix-products" in sys.argv:
        fix_products(dry_run="--dry-run" in sys.argv)
        sys.exit(0)
    d = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(
        dt.timezone(dt.timedelta(hours=-7))).date().isoformat()
    sync_day(d, dry_run="--dry-run" in sys.argv)

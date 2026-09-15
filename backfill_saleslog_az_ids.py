"""One-off backfill: fill in az_customer_id on Sales Sheet entries logged
before that field existed (Frank, 2026-09-15: "where is the link on the
sales sheet? i dont see it anywhere" -- checked, 0 of 53 real entries had
it set; "yes, backfill it").

    python3 backfill_saleslog_az_ids.py            # dry run, prints what it would set
    python3 backfill_saleslog_az_ids.py --apply    # actually writes

WHY THIS IS A SEPARATE, ONE-OFF SCRIPT, NOT PART OF sales_log_auto.py.
sales_log_auto.sync_day() only ever APPENDS new entries -- it is
deliberately built to never edit or remove one a producer already logged
by hand (see its own docstring), so it will never touch these old rows no
matter how many times it runs. Filling them in needs a genuinely different
operation (UPDATE an existing entry's one field), which is rare enough
(a single historical cleanup, not a nightly step) that it does not belong
bolted onto the automated sync.

WHY POLICY NUMBER, NOT sales_log_auto.py's LEAD-JOIN. Every one of the 53
real entries checked already has policy_number filled in (producers do
type it in, just not the optional AZ customer ID field next to it) --
a far more precise anchor than sales_log_auto.py's best-effort policy ->
sold-lead join, which exists only because a BRAND NEW auto-detected sale
has no human-typed policy number yet to start from. Here there is one, so
this looks the policy record up directly by policyNumber, then reuses the
exact same policy -> sold lead -> lead.convertedHouseholdId -> customer
join sales_log_auto.py already validated against real data.

MATCHED ON DIGITS, NOT THE EXACT STRING (real data). A plain string ==
found almost nothing: producers typed "84181101" for what AgencyZoom
actually stores as "0084181101" (a leading zero), "7003532690" for
"103-7003532690" (an extra prefix), "G019128762" for "G01 9128762" (a
space instead of nothing). find_policies() strips everything but digits
and matches either being a substring of the other, length-guarded at 6+
digits so a short number can't spuriously match inside an unrelated one.

POLICY NUMBER IS NOT UNIQUE EVEN THEN (real data, this session): Coral
Barwick's two-vehicle ATV sale, az_policy_id 30390981 and 30390977, both
displayed as policyNumber "00842352" with different premiums. So a
policyNumber hit is disambiguated by (agentId, premium) before it's
trusted -- if more than one candidate policy still matches after that,
this leaves the entry alone rather than guessing.

NEVER OVERWRITES. Only fills az_customer_id when it is currently blank,
and only from a match that resolves to exactly one customer. Nothing else
on the entry (client_name the producer typed, premium, dates, notes) is
touched, ever.
"""
import argparse
import json
import pathlib
import re

import digest_config as cfg

ROOT = pathlib.Path(__file__).resolve().parent


def _digits(s):
    return re.sub(r"\D", "", s or "")


def _customer_name(cust):
    return f"{(cust.get('firstname') or '').strip()} {(cust.get('lastname') or '').strip()}".strip()


def _names_overlap(a, b):
    """True if two names share at least one real word (3+ letters) --
    tolerates a household filed under a spouse's name, a middle name
    dropped, or a spelling variant ("Gonzales"/"Gonzalez") as long as SOME
    word still lines up, while still catching a join that landed on a
    completely different person (see the Carl Childress/Francisco
    Zendejas case above, zero words in common)."""
    words = lambda s: {w for w in re.split(r"[^a-zA-Z]+", (s or "").lower()) if len(w) >= 3}
    return bool(words(a) & words(b))


def find_policies(pnum, digit_index):
    """Policies whose own policyNumber matches `pnum` once punctuation and
    spacing are stripped out, in either direction (one a substring of the
    other) -- real data forced this: a producer-typed policy_number like
    "84181101" needed to match the real record's own "0084181101" (a
    leading zero) and "7003532690" needed to match "103-7003532690" (an
    extra prefix), with plain exact-string comparison finding neither.
    Guarded at >=6 digits so a short number can't spuriously match as a
    substring of unrelated ones."""
    dt = _digits(pnum)
    if len(dt) < 6:
        return []
    return [p for d, p in digit_index if d == dt or dt in d or d in dt]


def find_customer_id(entry, doc_day, digit_index, leads, customers_by_id, name_to_agent_id):
    """Best-effort az_customer_id for one existing entry, or None.

    policy_number -> matching policyNumber record(s) (find_policies),
    disambiguated by (agentId, premium) -> the one real policy -> its
    best-effort sold lead (same join sales_log_auto.build_entries already
    validated) -> convertedHouseholdId -> customer.
    """
    pnum = str(entry.get("policy_number") or "").strip()
    if not pnum:
        return None, "no policy_number on this entry"
    cands = find_policies(pnum, digit_index)
    if not cands:
        return None, f"no policy on file matching policyNumber {pnum!r}"

    agent_id = name_to_agent_id.get(entry.get("producer"))
    premium = entry.get("premium")
    exact = [p for p in cands
             if (agent_id is None or p.get("agentId") == agent_id)
             and (premium is None or p.get("premium") is None
                  or abs((p.get("premium") or 0) - premium) < 0.01)]
    if len(exact) != 1:
        if len(cands) == 1:
            exact = cands  # only one policy matches this number at all -- no ambiguity to resolve
        else:
            return None, (f"{len(cands)} policies match policyNumber {pnum!r}, "
                           f"{len(exact)} match this entry's producer/premium -- ambiguous")
    policy = exact[0]

    # These entries predate the date_sold/day fields (a historical Google
    # Sheet import, before this session's schema even existed) -- the
    # saleslog/<day>.json key itself is the only date signal left, and it's
    # exactly the day these sales were organized under to begin with.
    day = entry.get("date_sold") or entry.get("day") or doc_day or ""
    sold_leads = [l for l in leads if str(l.get("soldDate") or "").startswith(day)]
    matches = [l for l in sold_leads
               if l.get("assignedTo") == policy.get("agentId")
               and l.get("leadSourceId") == policy.get("leadSourceId")]
    if len(matches) != 1:
        return None, f"{len(matches)} sold-lead matches for this policy on {day} -- not unique"
    hh_id = matches[0].get("convertedHouseholdId")
    cust = customers_by_id.get(hh_id) if hh_id else None
    if not cust:
        return None, "matched lead has no converted household on file"

    # The (agentId, leadSourceId, day) join is the same one sales_log_auto.py
    # already accepts is only right "for about half of sold policies" --
    # a UNIQUE match on those three fields is not the same as a CORRECT one.
    # Real data proved it here: policy 826221247 (Crystal Mango, $203,
    # 2026-09-09) resolves to exactly one sold lead on that join, and that
    # lead is for Francisco Zendejas -- a real customer, just not the Carl
    # Childress this entry actually names. sales_log_auto.py has no name to
    # check a brand-new sale against, so it can't catch this; this backfill
    # does have one (the producer already typed it), so it must use it: a
    # match only counts if it shares at least one real name-word (3+
    # letters) with what the producer typed, never on faith alone.
    cust_name = _customer_name(cust)
    if not _names_overlap(entry.get("client_name"), cust_name):
        return None, (f"join resolved to {cust_name!r}, which shares no name "
                       f"with {entry.get('client_name')!r} -- rejected, not trusted")
    return str(cust["id"]), cust_name


def run(apply=False, days=None, log=print):
    policies = json.loads((ROOT / "data/az_policies_all.json").read_text())
    leads = json.loads((ROOT / "data/az_leads_all.json").read_text())
    customers = json.loads((ROOT / "data/az_customers_all.json").read_text())
    customers_by_id = {c["id"]: c for c in customers if c.get("id") is not None}
    name_to_agent_id = {name: v["az_id"] for name, v in cfg.PRODUCERS.items()}
    name_to_agent_id["Amanda Torricellas"] = cfg.OTHER_EXT["Amanda Torricellas"]["az_id"]

    digit_index = [(_digits(str(p.get("policyNumber") or "")), p) for p in policies]
    digit_index = [(d, p) for d, p in digit_index if len(d) >= 6]

    import publish_board
    cli, bucket = publish_board._client()
    resp = cli.list_objects_v2(Bucket=bucket, Prefix="saleslog/")
    keys = sorted(o["Key"] for o in resp.get("Contents", []) if o["Key"].endswith(".json"))
    if days:
        keys = [k for k in keys if any(k.endswith(f"{d}.json") for d in days)]

    filled = skipped = already_set = 0
    for key in keys:
        doc_day = key.removeprefix("saleslog/").removesuffix(".json")
        doc = json.loads(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
        changed = False
        for e in doc.get("entries", []):
            if e.get("az_customer_id"):
                already_set += 1
                continue
            cust_id, detail = find_customer_id(e, doc_day, digit_index, leads, customers_by_id, name_to_agent_id)
            if cust_id:
                log(f"  {key}: {e.get('client_name')!r} ({e.get('producer')}) -> "
                    f"customer {cust_id} ({detail!r}){' [DRY RUN]' if not apply else ''}")
                filled += 1
                if apply:
                    e["az_customer_id"] = cust_id
                    changed = True
            else:
                log(f"  {key}: {e.get('client_name')!r} ({e.get('producer')}) -- no match: {detail}")
                skipped += 1
        if changed:
            cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc).encode(),
                            ContentType="application/json", CacheControl="no-store")
            log(f"  {key}: written")

    log(f"\n{filled} filled, {skipped} left blank (no confident match), "
        f"{already_set} already had one" + (" [DRY RUN -- pass --apply to write]" if not apply else ""))
    return filled, skipped


if __name__ == "__main__":
    import secrets_load
    secrets_load.load()
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the matches (default: dry run)")
    ap.add_argument("--day", action="append", help="limit to this saleslog day (YYYY-MM-DD); repeatable")
    a = ap.parse_args()
    run(apply=a.apply, days=a.day)

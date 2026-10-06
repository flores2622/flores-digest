"""The agency's people, read from staff.json -- the one staff list.

Every AgencyZoom id, RingCentral extension, email, role and board permission
the pipeline and the Worker use comes from staff.json. digest_config,
missed_call_tasks, missed_call_audit, service_digest, service_playbook,
claims, commercial, lead_sources, insightful_client and sanity_gate build
their old constants from the helpers here, so their names and shapes are
unchanged; the Worker reads the same file through site/staff_data.js.

The agency itself is `agency`: `name` (the email's header, the page title,
The Flores Post's dateline, Apollo's own instructions), `short_name` (the
menu's brand and the front desk's greeting -- "thank you for calling
Flores"), `carrier` (the greeting's other word and what Apollo is told the
agency is), `carriers_spoken` (the carrier names said on calls, Deepgram's
keyterms), `place` (how Role Play prospects talk -- "the way a customer in
Arizona talks"), `sender` (the nightly email's From) and `contact` (the
address in every API client's User-Agent and send_digest's default
recipient). `UA` and `GREETING_WORDS` below are built from them.

The agency's clock is `agency.timezone` (an IANA name; Arizona's is
America/Phoenix, UTC-7 all year). `TZ` is that zone and every helper below
works in it -- nothing in the pipeline adds or subtracts "7 hours" any more,
so an agency in a zone with daylight saving gets the right day and clock
on both sides of the change. The Worker and the board page do the same
through site/staff.js's localDay / localParts.

A person's `tags` (what they are in the pipeline):
    licensed               may open and work a claim (claims.LICENSED)
    sells_service          a service team member who sells (service_playbook.SELLS)
    hybrid_util            whole-day utilization, shared with sales
    service_only_dials     only dials to service numbers are service work
    zero_dial_exempt       no "no dials by 11" warning (works service mornings)
    training_lead_owner    their leads are left out of Recontact Struggle
    commercial_owner       Cerberus: commercial SRs completed by / assigned to them
    team_util_exclude      left out of the team utilization figure
    insightful_not_tracked holds a licence but produces no attendance rows
    referral_source        their name as a lead source is a Referral
    sales_sheet            a non-producer whose sales go on the Sales sheet
    task_assignee          a missed-call task may be assigned to them
    missed_call_fallback   gets a missed-call task nobody else fits
    english_only           Role Play never gives them a Spanish or mixed prospect
A person's `heard_as` is how a transcript spells their first name
(Sarahi: Sarai, Zarahi) -- `name_forms` and `heard_names` build the
transcript rules from it.
A person's `color` is their badge on the board, `email_dot` the nightly
email's swatch class, `handle` their name on The Flores Feed. `sales_teams`
names a sales team on the Sales tab; `orders` keeps the display orders (the
coaching page, the email's and the board's utilization panels).
A person's `board` keys (what they may open, the Worker's checks):
    commercial, coeus_usage, card_review, roleplay_voices, rotation,
    rotation_edit, scrub, scrub_edit, roleplay_history, commission_all,
    sales_log_all
`digest` is which nightly email they get (ops / staff); `producer` means
their numbers are counted; `service` puts them on the Service Center.

    python3 staff.py --write-js   rewrite site/staff_data.js (the Worker's) and
                                  site/public/staff.js (the board page's) from staff.json
    python3 staff.py --check      fail if either is out of date, or if
                                  wrangler.jsonc's crons do not match the zone
    python3 staff.py --crons      print the Worker's cron lines for the zone
"""
import datetime as dt
import json
import pathlib
import re
import sys
from zoneinfo import ZoneInfo

import agency_files

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = agency_files.path("staff.json")   # PANTHEON_AGENCY picks the agency
JS_PATH = ROOT / "site" / "staff_data.js"
PUBLIC_PATH = ROOT / "site" / "public" / "staff.js"
# What the board page may know: never an email, a phone extension or an
# AgencyZoom / RingCentral id (site/public is served to every signed-in viewer).
PUBLIC_KEYS = ("name", "status", "producer", "digest", "service", "tags", "board",
               "sales_team", "color", "handle")
# ...and of the agency: its names and place, never its addresses.
PUBLIC_AGENCY_KEYS = ("name", "short_name", "carrier", "place", "timezone")

DATA = json.loads(JSON_PATH.read_text())
PEOPLE = DATA["people"]
AGENCY = DATA["agency"]

# --- the agency itself -------------------------------------------------------
AGENCY_NAME = AGENCY["name"]
SHORT_NAME = AGENCY.get("short_name") or AGENCY_NAME.split()[0]
CARRIER = AGENCY.get("carrier") or ""
CARRIERS_SPOKEN = list(AGENCY.get("carriers_spoken") or ([CARRIER] if CARRIER else []))
PLACE = AGENCY.get("place") or ""
CONTACT = AGENCY.get("contact") or AGENCY.get("sender") or ""
# Every API client's User-Agent (AgencyZoom, RingCentral, Insightful, Resend).
UA = f"{SHORT_NAME}Digest/1.0 (+{CONTACT})"
# The words the front desk greets with -- "thank you for calling Farmers" /
# "Flores Insurance, how can I help" -- as a regex alternation, lower-cased.
GREETING_WORDS = "|".join(re.escape(w.lower()) for w in (CARRIER, SHORT_NAME) if w)


def name_forms(first):
    """A regex alternation of how a transcript spells a staff first name --
    the name and the person's `heard_as` spellings (Sarahi / Sarai / Zarahi,
    Crystal / Cristal), lower-cased."""
    first = (first or "").lower()
    for p in PEOPLE:
        if p["name"].split()[0].lower() == first:
            forms = [first] + [h.lower() for h in p.get("heard_as", [])]
            return "|".join(re.escape(f) for f in forms)
    return re.escape(first)


def heard_names():
    """Every active staff first name and `heard_as` spelling, lower-cased ->
    the first name it is (coaching_cards: who a pick-up line names)."""
    out = {}
    for p in active():
        f = p["name"].split()[0].lower()
        out[f] = f
        for h in p.get("heard_as", []):
            out[h.lower()] = f
    return out


# The Worker's live cron (wrangler.jsonc "triggers"): every minute of the
# agency's business hours on weekdays, written in UTC because Cloudflare
# crons are. 8:00 AM to 5:59 PM on the agency's clock.
WORKER_CRON_HOURS = (8, 17)


def worker_crons(year=None):
    """The wrangler.jsonc cron lines for this zone, or None with a reason
    when the zone changes offset through the year (daylight saving), since
    one set of UTC lines cannot follow it."""
    year = year or now().year
    offs = {dt.datetime(year, m, 15, 12, tzinfo=TZ).utcoffset() for m in (1, 7)}
    if len(offs) != 1:
        return None, f"{TZ_NAME} changes its UTC offset through the year; Cloudflare crons are UTC, so the live window drifts an hour half the year -- pick one set and say so"
    off = next(iter(offs)).total_seconds() / 3600
    if off != int(off):
        return None, f"{TZ_NAME} is not a whole-hour offset; write the crons by hand"
    start = (WORKER_CRON_HOURS[0] - int(off)) % 24
    end = (WORKER_CRON_HOURS[1] - int(off)) % 24
    if start <= end:
        return [f"* {start}-{end} * * 1-5"], None
    return [f"* {start}-23 * * 1-5", f"* 0-{end} * * 2-6" if end else "* 0 * * 2-6"], None

# --- the agency's clock -----------------------------------------------------
TZ_NAME = AGENCY.get("timezone") or "America/Phoenix"
TZ = ZoneInfo(TZ_NAME)
UTC = dt.timezone.utc


def now():
    """Right now, on the agency's clock (an aware datetime)."""
    return dt.datetime.now(TZ)


def today():
    """Today's date on the agency's clock, 'YYYY-MM-DD'."""
    return now().date().isoformat()


def day_start(day):
    """Local midnight starting `day` ('YYYY-MM-DD'), aware."""
    return dt.datetime.combine(dt.date.fromisoformat(day), dt.time(), tzinfo=TZ)


def day_start_iso(day):
    """Local midnight starting `day` as an ISO stamp with its offset
    ('2026-10-06T00:00:00-07:00') -- what RingCentral's call log takes."""
    return day_start(day).isoformat()


def day_bounds_iso(day):
    """(start, end) ISO stamps: local midnight starting `day` and the next."""
    nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
    return day_start_iso(day), day_start_iso(nxt)


def local(t):
    """An aware datetime on the agency's clock. A naive `t` is taken as UTC
    (AgencyZoom's and RingCentral's stamps are)."""
    if t.tzinfo is None:
        t = t.replace(tzinfo=UTC)
    return t.astimezone(TZ)


def local_date(t):
    """The agency's calendar date of an instant, 'YYYY-MM-DD' (naive = UTC)."""
    return local(t).date().isoformat()


def utc_text_local_date(stamp):
    """A 'YYYY-MM-DD HH:MM:SS' / ISO stamp in UTC (AgencyZoom's) as the
    agency's date, '' when it does not parse."""
    s = str(stamp or "")[:19].replace("T", " ")
    try:
        return local_date(dt.datetime.fromisoformat(s))
    except ValueError:
        return ""


def utc_naive_to_local_naive(t):
    """A naive UTC datetime as a naive local one (the same instant)."""
    return local(t).replace(tzinfo=None)


def local_naive_to_utc_naive(t):
    """A naive local datetime as a naive UTC one (the same instant)."""
    return t.replace(tzinfo=TZ).astimezone(UTC).replace(tzinfo=None)


def active():
    return [p for p in PEOPLE if p.get("status", "active") == "active"]


def first(p):
    return p["name"].split()[0]


def tagged(tag):
    """Active people carrying `tag`, in staff.json order (former staff only
    for task_assignee, who can still hold an SR or a task)."""
    pool = PEOPLE if tag == "task_assignee" else active()
    return [p for p in pool if tag in p.get("tags", [])]


def producers():
    return [p for p in active() if p.get("producer")]


def digest_recipients(audience):
    return [p["email"] for p in active() if p.get("digest") == audience]


def service_team():
    return sorted((p for p in active() if p.get("service")),
                  key=lambda p: p["service"]["order"])


def with_board(key):
    return [p["email"] for p in active() if key in p.get("board", []) and p.get("email")]


def one(tag):
    hit = tagged(tag)
    if len(hit) != 1:
        raise ValueError(f"staff.json: exactly one person must carry {tag!r}, found {len(hit)}")
    return hit[0]


def order(key):
    return list(DATA["orders"][key])


def email_dot(names):
    """name -> the nightly email's swatch class, for these names."""
    by = {p["name"]: p for p in PEOPLE}
    return {n: by[n]["email_dot"] for n in names if by.get(n, {}).get("email_dot")}


def phone_ids(p):
    out = {k: p[k] for k in ("ext", "rc_id", "az_id") if k in p}
    return out


def _js():
    body = json.dumps(DATA, indent=2, ensure_ascii=False)
    return ("// WRITTEN BY `python3 staff.py --write-js` FROM staff.json -- do not edit.\n"
            "// The agency's people: see staff.py for what each tag and board key means.\n"
            f"export default {body};\n")


def _public_js():
    view = {"agency": {k: AGENCY[k] for k in PUBLIC_AGENCY_KEYS if k in AGENCY},
            "people": [{k: p[k] for k in PUBLIC_KEYS if k in p} for p in PEOPLE],
            "sales_teams": DATA.get("sales_teams", {}), "orders": DATA.get("orders", {})}
    body = json.dumps(view, indent=1, ensure_ascii=False)
    return ("// WRITTEN BY `python3 staff.py --write-js` FROM staff.json -- do not edit.\n"
            "// The board page's copy of the staff list: names, roles, tags, colours and\n"
            "// orders only -- no emails, extensions or ids. A plain script, loaded before\n"
            "// the page's own (window.STAFF).\n"
            f"window.STAFF = {body};\n")


OUTPUTS = ((JS_PATH, _js), (PUBLIC_PATH, _public_js))


def main(argv):
    if "--write-js" in argv:
        for path, make in OUTPUTS:
            path.write_text(make())
            print(f"wrote {path.relative_to(ROOT)}")
        return 0
    if "--crons" in argv:
        lines, why = worker_crons()
        print("\n".join(lines) if lines else f"no fixed cron lines: {why}")
        return 0
    if "--check" in argv:
        stale = [path for path, make in OUTPUTS if not path.exists() or path.read_text() != make()]
        for path in stale:
            print(f"{path.relative_to(ROOT)} is out of date: run python3 staff.py --write-js")
        if not stale:
            print("site/staff_data.js and site/public/staff.js match staff.json")
        bad = len(stale)
        lines, why = worker_crons()
        wr = (ROOT / "wrangler.jsonc").read_text()
        m = re.search(r'"crons":\s*\[([^\]]*)\]', wr)
        have = re.findall(r'"([^"]+)"', m.group(1)) if m else []
        if lines is None:
            print(f"wrangler.jsonc crons not checked: {why}")
        elif have != lines:
            print(f"wrangler.jsonc crons {have} do not match the zone's {lines} ({TZ_NAME}): run python3 staff.py --crons")
            bad += 1
        else:
            print(f"wrangler.jsonc crons match {TZ_NAME}")
        return 1 if bad else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

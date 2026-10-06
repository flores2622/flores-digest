"""The agency's people, read from staff.json -- the one staff list.

Every AgencyZoom id, RingCentral extension, email, role and board permission
the pipeline and the Worker use comes from staff.json. digest_config,
missed_call_tasks, missed_call_audit, service_digest, service_playbook,
claims, commercial, lead_sources, insightful_client and sanity_gate build
their old constants from the helpers here, so their names and shapes are
unchanged; the Worker reads the same file through site/staff_data.js.

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
    python3 staff.py --check      fail if either is out of date
"""
import datetime as dt
import json
import pathlib
import sys
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = ROOT / "staff.json"
JS_PATH = ROOT / "site" / "staff_data.js"
PUBLIC_PATH = ROOT / "site" / "public" / "staff.js"
# What the board page may know: never an email, a phone extension or an
# AgencyZoom / RingCentral id (site/public is served to every signed-in viewer).
PUBLIC_KEYS = ("name", "status", "producer", "digest", "service", "tags", "board",
               "sales_team", "color", "handle")

DATA = json.loads(JSON_PATH.read_text())
PEOPLE = DATA["people"]
AGENCY = DATA["agency"]

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
    view = {"agency": {"timezone": TZ_NAME},
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
    if "--check" in argv:
        stale = [path for path, make in OUTPUTS if not path.exists() or path.read_text() != make()]
        for path in stale:
            print(f"{path.relative_to(ROOT)} is out of date: run python3 staff.py --write-js")
        if not stale:
            print("site/staff_data.js and site/public/staff.js match staff.json")
        return 1 if stale else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

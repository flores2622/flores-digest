"""The agency's people, read from staff.json -- the one staff list.

Every AgencyZoom id, RingCentral extension, email, role and board permission
the pipeline and the Worker use comes from staff.json. digest_config,
missed_call_tasks, missed_call_audit, service_digest, service_playbook,
claims, commercial, lead_sources, insightful_client and sanity_gate build
their old constants from the helpers here, so their names and shapes are
unchanged; the Worker reads the same file through site/staff_data.js.

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
A person's `board` keys (what they may open, the Worker's checks):
    commercial, coeus_usage, card_review, roleplay_voices, rotation,
    rotation_edit, scrub, scrub_edit, roleplay_history, commission_all,
    sales_log_all
`digest` is which nightly email they get (ops / staff); `producer` means
their numbers are counted; `service` puts them on the Service Center.

    python3 staff.py --write-js   rewrite site/staff_data.js from staff.json
    python3 staff.py --check      fail if site/staff_data.js is out of date
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = ROOT / "staff.json"
JS_PATH = ROOT / "site" / "staff_data.js"

DATA = json.loads(JSON_PATH.read_text())
PEOPLE = DATA["people"]
AGENCY = DATA["agency"]


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


def phone_ids(p):
    out = {k: p[k] for k in ("ext", "rc_id", "az_id") if k in p}
    return out


def _js():
    body = json.dumps(DATA, indent=2, ensure_ascii=False)
    return ("// WRITTEN BY `python3 staff.py --write-js` FROM staff.json -- do not edit.\n"
            "// The agency's people: see staff.py for what each tag and board key means.\n"
            f"export default {body};\n")


def main(argv):
    if "--write-js" in argv:
        JS_PATH.write_text(_js())
        print(f"wrote {JS_PATH.relative_to(ROOT)}")
        return 0
    if "--check" in argv:
        if not JS_PATH.exists() or JS_PATH.read_text() != _js():
            print("site/staff_data.js is out of date: run python3 staff.py --write-js")
            return 1
        print("site/staff_data.js matches staff.json")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""What each AgencyZoom lead source means, and what to sell it (Frank, 2026-09-24).

A lead source names the marketing channel a lead came through. It is not a
product and not a household: the same source covers every lead it ever
brought in. This module turns the ~83 raw names into a few GROUPS. Each group
says who the lead is, what we can sell them, and how to work them.

**The names are this agency's, in lead_sources.json** (the one place): each
source name and its group, the product each cross-sell source sells, a
source's own Role Play backstory where its group's is not right, and the
internet sources Speed to Dial times. The GROUPS -- what a group means and
how it is worked -- and every rule (a staff member's name, "Name at
Company", the money rules) stay here. A new agency starts by writing its
own lead_sources.json; `--discover` lists what its corpus holds.

    python3 lead_sources.py --discover   every source in the saved lead corpus,
                                         with its group; unclassified marked
    python3 lead_sources.py --check      validate lead_sources.json and the
                                         Worker's copy
    python3 lead_sources.py --write-js   rewrite site/lead_sources_data.js (the
                                         Worker's: the speed sources, the
                                         cross-sell and not-a-sale names)

It is also the single definition of two money rules that digest_config
imports:
  * NOT_A_SALE      BOB and Rewrite; a policy under either is not a sale.
  * EXISTING_HOUSEHOLD  the cross-sell sources, where AgencyZoom's own label says
                    the household was already a customer.

`approach` is how to work each group; Frank confirmed them on 2026-09-24
(`APPROACH_CONFIRMED`). `roleplay` says whether Role Play may use a group as
a session's lead source. Every lead source is still coached.
"""
import json
import pathlib
import re

import agency_files
import staff

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = agency_files.path("lead_sources.json")   # PANTHEON_AGENCY picks the agency
JS_PATH = ROOT / "site" / "lead_sources_data.js"
DATA = json.loads(JSON_PATH.read_text())

ANY = "any product"

# key -> definition. Order here is the order a breakdown should list them in.
GROUPS = {
    "cross_sell": {
        "label": "Cross-sell",
        "who": "An existing household missing a product. We marketed the gap to them.",
        "products": "the product the source names; for plain Cross Sell, whatever the household is missing",
        "existing_household": True, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You are already a customer of this agency for one policy. The producer is calling about {product} coverage you do not have with them yet.',
        "approach": "They already trust us. Open with the policy they have, then "
                    "the gap: 'we insure your home, who has your autos?' Quote "
                    "the missing line and show the bundle saving.",
    },
    "existing_new_purchase": {
        "label": "Existing client, new purchase",
        "who": "An existing customer who called or walked in because they bought "
               "something new, usually a property. We did not market it.",
        "products": "usually home/landlord for the new property, but " + ANY,
        "existing_household": True, "sale": True, "owner": "apollo",
        "roleplay": False,   # Frank, 2026-09-24: not a Role Play scenario
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You are already a customer of this agency. You just bought something new, most likely a property, and you called in to get it covered.',
        "approach": "They came to us, so the job is speed and completeness. Write "
                    "the new item, then review the household for anything else "
                    "it lacks.",
    },
    "generated": {
        "label": "Generated / purchased",
        "who": "A lead the agency paid for or generated. A stranger who asked "
               "for a quote somewhere.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'A day or two ago you asked for an insurance quote online, on a comparison or quote site, and gave your number. Several agents may be calling you.',
        "approach": "Speed to lead. They have usually asked several agents, so the "
                    "first real conversation wins. Expect price shopping; get "
                    "current carrier and renewal date, then quote to bundle.",
    },
    "winback": {
        "label": "Winback",
        # "Former" or "prior", never "lapsed" -- lapsed means without
        # coverage, and a winback insures elsewhere now (Frank, 2026-09-30).
        "who": "A former (prior) customer who now insures with another company. "
               "We are trying to win them back.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You used to insure with this agency and moved to another company, which insures you now. The producer is calling to win you back.',
        "approach": "Find out why they left before quoting. Lead with what has "
                    "changed since, and quote what they had plus anything missing.",
    },
    "referral": {
        "label": "Referral",
        "who": "A customer's referral, or a source named after a staff member "
               "whose referrals come through them (staff.json's referral_source).",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'Someone you know, a customer of this agency or someone who works there, gave the producer your number and said they would call.',
        "approach": "Name the person who referred them in the first sentence. The "
                    "trust is borrowed, so follow up the way that person would expect.",
    },
    # Frank, 2026-09-24: a staff member's name as the source is that person's
    # own personal network, and each works their own, never each other's.
    # Francisco's name is a Referral (STAFF_REFERRAL, below). Approach
    # confirmed by Frank, 2026-09-24. Never in Role Play (Frank, 2026-09-24):
    # a producer's own network is not something to practise on a stranger.
    "personal_network": {
        "label": "Personal network",
        "who": "A staff member's own personal network (a source named after one "
               "of us, other than {referral_first}). Each person works their own "
               "network, never someone else's.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "roleplay": False,
        "approach": "They know you, not the agency. Lead with the relationship and "
                    "why you are calling, not a pitch: ask what they have and when "
                    "it renews, then quote the whole household in one go so they "
                    "are not passed around. Keep it professional -- a friend with "
                    "a bad experience will not send anyone else.",
    },
    # Instagram and LinkedIn (Frank, 2026-09-24). Facebook is NOT here: its
    # leads are purchased and sit with Generated. No leads yet. Approach and
    # backstory confirmed by Frank, 2026-09-24.
    "social_media": {
        "label": "Social media",
        "who": "Someone who reached the agency through its Instagram or LinkedIn.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You follow or found this agency on Instagram or LinkedIn and sent a message asking about insurance. You have not asked for a formal quote yet.',
        "approach": "They reached out, but lightly: a message or a comment, not a "
                    "quote request. Respond fast, refer back to the post or message "
                    "that brought them in, then move to a phone call and discovery. "
                    "Expect them to know less about what they need than a quote-site lead.",
    },
    "center_of_influence": {
        "label": "Center of influence",
        "who": "A mortgage loan officer or realtor (\"Name at Company\"). They "
               "refer us the home on a purchase, and we deal with them, not "
               "with the client.",
        "products": "home first, then a cross-sell attempt",
        "existing_household": False, "sale": True, "owner": "apollo",
        "roleplay": False,   # Frank, 2026-09-24: we only talk to the referral partner
        "approach": None,
    },
    "inbound": {
        "label": "Call-in / walk-in",
        # Found us (Google, Farmers.com) is part of this group (Frank,
        # 2026-09-24): they looked for an agent and came to us themselves.
        "who": "Someone who came to us on their own: called, walked in, or "
               "found us online and asked an agent to contact them. Not purchased.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You reached out to this agency yourself because you want a quote: you called, or found them on Google or {carrier_site_lc} and asked for a call.',
        "approach": "They are ready now. Answer the question they came with, then "
                    "ask what else they have and who insures it. A Google or "
                    "{carrier_site_lc} request gets called fast.",
    },
    "cold": {
        "label": "Cold / misc",
        "who": "Dug out of the system, or a one-off list.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        "roleplay": False,   # Frank, 2026-09-24: barely used
        "approach": None,
    },
    "one_off": {
        "label": "Other one-offs",
        "who": "Little volume and no set meaning.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        "approach": None,
    },
    "commercial": {
        "label": "Commercial",
        "who": "Commercial lead generators and lists.",
        "products": "commercial lines",
        "existing_household": False, "sale": True, "owner": "cerberus",
        "approach": None,   # Cerberus's, not Apollo's
    },
    "not_a_sale": {
        "label": "Not a sale",
        "who": "BOB: CRM housekeeping for policies that were not sold. Rewrite: "
               "kept for the service department from 2026-09-24 on.",
        "products": None,
        "existing_household": False, "sale": False, "owner": None,
        "approach": None,
    },
    "unclassified": {
        "label": "Unclassified",
        "who": "A source Frank has not defined yet.",
        "products": None,
        "existing_household": False, "sale": True, "owner": "apollo",
        "approach": None,
    },
}

# Whether Role Play may use a group as a session's lead source. False for
# centers of influence and cold / misc (Frank, 2026-09-24: "we barely use
# them and center of influence we dont even talk to the client, only the
# referral partner"), and for every group with no approach: one-offs,
# commercial (Cerberus's), not a sale, unclassified. This is Role Play only:
# calls on these sources are still coached like any other (Frank, 2026-09-24:
# "i want coaching cards still developed for those lead sources").
for _k, _g in GROUPS.items():
    _g.setdefault("roleplay", _g["approach"] is not None)

# An agency's own wording of who a group's leads are, naming its sources
# (lead_sources.json's `group_who`), over the plain line above.
for _k, _w in (DATA.get("group_who") or {}).items():
    GROUPS[_k]["who"] = _w

# The lines name the referral staff member's first name and the carrier's
# website: {referral_first} and {carrier_site_lc}, from staff.json and the
# coaching carrier layer (coaching_text.carrier()).
def _fill_names():
    import coaching_text
    ref = staff.tagged("referral_source")
    first = staff.first(ref[0]) if ref else "the referral staff member"
    site = (coaching_text.carrier().get("website") or (staff.CARRIER + ".com")).lower()
    for g in GROUPS.values():
        for f in ("who", "approach", "backstory"):
            if g.get(f):
                g[f] = g[f].replace("{referral_first}", first).replace("{carrier_site_lc}", site)
_fill_names()

# Frank read every approach line on 2026-09-24: "all looks good. we can keep
# building on that later". A new or rewritten line starts False again.
APPROACH_CONFIRMED = {k: g["approach"] is not None for k, g in GROUPS.items()}

# Normalised name (see norm) -> group: lead_sources.json's `sources`, in its
# order (a key starting with "_" is a comment there). Everything not listed
# is decided by the rules in classify().
SOURCES = {k: v for k, v in DATA["sources"].items() if not k.startswith("_")}

# The product each cross-sell source is selling into the household
# (lead_sources.json's `cross_sell_product`).
CROSS_SELL_PRODUCT = dict(DATA["cross_sell_product"])

# The internet sources Speed to Dial times (daily.speed_rows, the Worker's
# speedToDial): a lead whose source name CONTAINS one of these.
SPEED_SOURCES = tuple(DATA["speed_sources"])

# A lead marked sold on a life source is a life sale, not a household sold
# (digest_config.is_life_lead): the cross-sell sources selling life.
LIFE_SOURCES = {n for n, p in CROSS_SELL_PRODUCT.items() if p == "life"}

# Staff whose name used as a lead source means their own referral or network.
# Current and past team; a new hire's name as a source lands in "unclassified"
# until it is added here. Former staff per Frank, 2026-09-24: Adrian
# Alcantara, Anastasia Perez, Michelle Garcia, Veronica Rodriguez, Maria Medina.
# Everyone in staff.json, past staff and AgencyZoom's Team category included.
STAFF = {p["name"].lower() for p in staff.PEOPLE}

# Francisco's name as a source is a referral, not a personal network (Frank,
# 2026-09-24).
STAFF_REFERRAL = {p["name"].lower() for p in staff.tagged("referral_source")}

# Role Play backstory for one source where its group's own is not right
# (lead_sources.json's `source_backstory`): a Francisco lead is a referral or
# a warm transfer (Frank, 2026-09-24). Home no Auto and Auto no Home say
# which policy the agency already has (Frank, 2026-09-30: "If its Home no
# auto, that means we have the home and not the auto. we are trying to sell
# the auto") -- the group's "one policy" left the prospect saying they
# already had the auto with us.
SOURCE_BACKSTORY = dict(DATA["source_backstory"])

# "Name at Company" / "Name @ Company" is a center of influence.
_COI = re.compile(r"\s(at|@)\s", re.I)


def norm(name):
    """AgencyZoom names carry stray trailing spaces ('Cross Sell ') and one
    duplicate with a '!' ('Arizona Insurance Reports!')."""
    return re.sub(r"\s+", " ", (name or "").strip().rstrip("!").strip()).lower()


def classify(name):
    """Lead source name -> group key. Never raises; unknown -> 'unclassified'."""
    n = norm(name)
    if not n:
        return "unclassified"
    if n in SOURCES:
        return SOURCES[n]
    if n in STAFF_REFERRAL:
        return "referral"
    if n in STAFF:
        return "personal_network"
    if _COI.search(f" {n} "):
        return "center_of_influence"
    return "unclassified"


def group(name):
    return GROUPS[classify(name)]


def prompt_block(name):
    """What Apollo is told about a call's lead source (coaching_cards), or ""
    when the call never resolved to a lead with a source. Plain facts from
    this guide; how to use them is coaching/METHODOLOGY.md's "Lead source"
    section."""
    if not norm(name):
        return ""
    key = classify(name)
    g = GROUPS[key]
    lines = [f"Lead source: {str(name).strip()} (group: {g['label']})",
             f"Who this lead is: {g['who']}"]
    if g["products"]:
        product = cross_sell_product(name)
        lines.append(f"What to sell: {product if product else g['products']}")
    lines.append("How the agency works this lead: "
                 + (g["approach"] if g["approach"] and APPROACH_CONFIRMED.get(key)
                    else "no set approach for this lead source"))
    return "\n".join(lines)


# The Sales tab's "Premium per Lead Source" categories (Frank, 2026-09-24).
# They follow GROUPS one to one -- the chart and Apollo read lead sources
# the same way -- and only rename two labels for the chart.
SALES_CATEGORY = {k: g["label"] for k, g in GROUPS.items()}
SALES_CATEGORY.update({"generated": "Internet leads", "center_of_influence": "Centers of influence"})


def sales_category(name):
    return SALES_CATEGORY[classify(name)]


def board_map(names):
    """{name: group} for the names given, plus the groups themselves, for the
    board (published with the lead-source list; see publish_board)."""
    return {
        # keyed by norm(name); the board normalises the same way
        "source_group": {norm(n): classify(n) for n in names if norm(n)},
        "sales_category": {norm(n): sales_category(n) for n in names if norm(n)},
        "cross_sell_product": {n: p for n, p in CROSS_SELL_PRODUCT.items() if p},
        "source_backstory": SOURCE_BACKSTORY,
        "groups": {k: {"label": g["label"], "who": g["who"], "products": g["products"],
                       "approach": g["approach"], "roleplay": g["roleplay"],
                       "backstory": g.get("backstory")}
                   for k, g in GROUPS.items()},
    }


def cross_sell_product(name):
    return CROSS_SELL_PRODUCT.get(norm(name))


def names_in(group_key):
    return {n for n, g in SOURCES.items() if g == group_key}


# The money rules digest_config reads, in its lower-cased, stripped form.
NOT_A_SALE = names_in("not_a_sale")
EXISTING_HOUSEHOLD = {n for n, g in SOURCES.items() if GROUPS[g]["existing_household"]}


def _js():
    body = json.dumps({"speed_sources": list(SPEED_SOURCES), "not_a_sale": sorted(NOT_A_SALE),
                       "existing_household": sorted(EXISTING_HOUSEHOLD),
                       "cross_sell_product": {n: p for n, p in CROSS_SELL_PRODUCT.items() if p}},
                      indent=2, ensure_ascii=False)
    return ("// WRITTEN BY `python3 lead_sources.py --write-js` FROM lead_sources.json -- do not edit.\n"
            "// The Worker's copy of the agency's lead-source names: see lead_sources.py.\n"
            f"export default {body};\n")


def check(log=print):
    """Validate lead_sources.json against the groups and rules here, and the
    Worker's copy against the file. Returns the problems."""
    bad = []
    for n, g in SOURCES.items():
        if g not in GROUPS:
            bad.append(f"sources: {n!r} -> {g!r} is not a group ({', '.join(GROUPS)})")
        if n != norm(n):
            bad.append(f"sources: {n!r} is not in its normalised form ({norm(n)!r})")
        if n in STAFF:
            bad.append(f"sources: {n!r} is a staff member's name -- staff.json decides it; drop it here")
    for n, p in CROSS_SELL_PRODUCT.items():
        if n not in SOURCES or not GROUPS[SOURCES[n]]["existing_household"]:
            bad.append(f"cross_sell_product: {n!r} is not a cross-sell source")
    for n in SOURCE_BACKSTORY:
        if n not in SOURCES and n not in STAFF:
            bad.append(f"source_backstory: {n!r} is not a listed source or a staff member")
    if not NOT_A_SALE:
        bad.append("sources: no not_a_sale source (BOB-style housekeeping) -- every agency has one")
    if not SPEED_SOURCES:
        bad.append("speed_sources: empty -- Speed to Dial would time no lead")
    if not JS_PATH.exists() or JS_PATH.read_text() != _js():
        bad.append(f"{JS_PATH.relative_to(ROOT)} is out of date: run python3 lead_sources.py --write-js")
    for b in bad:
        log(f"  lead_sources.json: {b}")
    return bad


def discover():
    """Every source in the saved lead corpus (data/az_leads_all.json), by
    group, the unclassified ones first -- what a new agency's file is
    missing. Reads the nightly's own file; no AgencyZoom request."""
    import collections
    path = ROOT / "data/az_leads_all.json"
    if not path.exists():
        print("no data/az_leads_all.json here -- run after a nightly pull")
        return
    leads = json.loads(path.read_text())
    count = collections.Counter(l.get("leadSourceName") for l in leads if l.get("leadSourceName"))
    by = collections.defaultdict(list)
    for name, n in count.items():
        by[classify(name)].append((n, name.strip()))
    for key in ["unclassified"] + [k for k in GROUPS if k != "unclassified"]:
        if not by.get(key):
            continue
        g = GROUPS[key]
        rows = sorted(by[key], reverse=True)
        mark = "  <- NOT IN lead_sources.json: add each, or leave it unclassified on purpose" if key == "unclassified" else ""
        print(f"\n{g['label']}  ({len(rows)} sources, {sum(n for n, _ in rows):,} leads)"
              f"  products: {g['products'] or '-'}  owner: {g['owner'] or '-'}"
              f"  role play: {'yes' if g['roleplay'] else 'no'}{mark}")
        for n, name in rows:
            print(f"   {n:6,d}  {name}")


def main(argv):
    if "--write-js" in argv:
        JS_PATH.write_text(_js())
        print(f"wrote {JS_PATH.relative_to(ROOT)}")
        return 0
    if "--check" in argv:
        bad = check()
        print("lead_sources.json ok" if not bad else f"{len(bad)} problem(s)")
        return 1 if bad else 0
    if "--discover" in argv:
        discover()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))

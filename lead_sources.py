"""What each AgencyZoom lead source means, and what to sell it (Frank, 2026-09-24).

A lead source names the marketing channel a lead came through. It is not a
product and not a household: the same source covers every lead it ever
brought in. This module turns the ~83 raw names into a few GROUPS. Each group
says who the lead is, what we can sell them, and how to work them.

    python3 lead_sources.py      every source in the lead corpus, with its group

It is also the single definition of two money rules that digest_config
imports:
  * NOT_A_SALE      BOB and Rewrite; a policy under either is not a sale.
  * EXISTING_HOUSEHOLD  the cross-sell sources, where AgencyZoom's own label says
                    the household was already a customer.

`approach` is how to work each group; Frank confirmed them on 2026-09-24
(`APPROACH_CONFIRMED`). `coach` says whether a group's calls are coached
and used for Role Play at all.
"""
import re

ANY = "any product"

# key -> definition. Order here is the order a breakdown should list them in.
GROUPS = {
    "cross_sell": {
        "label": "Cross-sell",
        "who": "An existing household missing a product. We marketed the gap to them.",
        "products": "the product the source names (see CROSS_SELL_PRODUCT)",
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
    "found_us": {
        "label": "Found us",
        "who": "Google (an email via Google, or they said they found us there) "
               "and Farmers.com (a form on farmers.com that Farmers passes on). "
               "Not purchased: they looked for an agent.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You found this agency yourself, on Google or through a form on farmers.com, and asked an agent to contact you.',
        "approach": "Warmer than a purchased lead: they chose an agent. Call fast, "
                    "confirm what they asked for, then round out the household.",
    },
    "winback": {
        "label": "Winback",
        "who": "A former customer we are trying to win back.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You used to insure with this agency and moved to another company. The producer is calling to win you back.',
        "approach": "Find out why they left before quoting. Lead with what has "
                    "changed since, and quote what they had plus anything missing.",
    },
    "referral": {
        "label": "Referral",
        "who": "A customer's referral, or a staff member's own referral or "
               "network (a source named after one of us).",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'Someone you know, a customer of this agency or someone who works there, gave the producer your number and said they would call.',
        "approach": "Name the person who referred them in the first sentence. The "
                    "trust is borrowed, so follow up the way that person would expect.",
    },
    "center_of_influence": {
        "label": "Center of influence",
        "who": "A mortgage loan officer or realtor (\"Name at Company\"). They "
               "refer us the home on a purchase, and we deal with them, not "
               "with the client.",
        "products": "home first, then a cross-sell attempt",
        "existing_household": False, "sale": True, "owner": "apollo",
        "coach": False,   # Frank, 2026-09-24: we only talk to the referral partner
        "approach": None,
    },
    "inbound": {
        "label": "Call-in / walk-in",
        "who": "Someone who called or walked in on their own.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You called the agency yourself because you want a quote.',
        "approach": "They are ready now. Answer the question they came with, then "
                    "ask what else they have and who insures it.",
    },
    "cold": {
        "label": "Cold / misc",
        "who": "Dug out of the system, or a one-off list: Cold lead, FIG QNT "
               "(Farmers Quotes Not Taken), Crane Benefit Fair (a booth at a "
               "local school fair), Old MVP Leads (the old CRM).",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        "coach": False,   # Frank, 2026-09-24: barely used
        "approach": None,
    },
    "one_off": {
        "label": "Other one-offs",
        "who": "Hometown Quotes, X, Other lead. Little volume and no set meaning.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        "approach": None,
    },
    "commercial": {
        "label": "Commercial",
        "who": "Commercial lead generators and lists (Leo, Work Comp, District / "
               "Agent Promoter Comm Leads, RCFBH Group Life).",
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
        # A new source still gets coached until someone classifies it, rather
        # than silently dropping out of the coaching figures.
        "coach": True,
        "approach": None,
    },
}

# Whether a group's calls are coached and used for Role Play. False for
# centers of influence and cold / misc (Frank, 2026-09-24: "we barely use
# them and center of influence we dont even talk to the client, only the
# referral partner"), and for every group with no approach: one-offs,
# commercial (Cerberus's), not a sale. Unclassified stays coached.
for _k, _g in GROUPS.items():
    _g.setdefault("coach", _g["approach"] is not None)

# Frank read every approach line on 2026-09-24: "all looks good. we can keep
# building on that later". A new or rewritten line starts False again.
APPROACH_CONFIRMED = {k: g["approach"] is not None for k, g in GROUPS.items()}

# Normalised name (see norm) -> group. Everything not listed here is decided
# by the patterns in classify().
SOURCES = {
    # cross-sell
    "home no auto": "cross_sell", "auto no home": "cross_sell",
    "life cross sell": "cross_sell", "umbrella": "cross_sell",
    "cross sell": "cross_sell",
    "existing client purchased a new": "existing_new_purchase",
    # generated / purchased
    "surequote": "generated", "smart financial": "generated",
    "smart financial live transfer": "generated", "enterprise": "generated",
    "mav ai": "generated", "alpha media": "generated",
    "arizona insurance reports": "generated", "facebook": "generated",
    # Instagram and LinkedIn share AgencyZoom's Social Media category with
    # Facebook. Neither has a lead yet (2026-09-24).
    "instagram": "generated", "linkedin": "generated",
    # found us
    "google": "found_us", "farmers.com": "found_us",
    "found us on google": "found_us",   # the name on some 2026-09 lead records
    # winback
    "winback": "winback", "winback by agencyzoom": "winback",
    # referral
    "existing customer referral": "referral", "referral by agencyzoom": "referral",
    # center of influence without an "at Company" in the name. Mariah Serna is
    # being renamed "Mariah @ MRS" in AgencyZoom (Frank, 2026-09-24); the new
    # name matches the pattern, and the old one stays here for past leads.
    "lender no longer in the industry": "center_of_influence",
    "mariah serna": "center_of_influence",
    # inbound
    "call-in": "inbound", "walk-in": "inbound",
    # cold / misc
    "cold lead": "cold", "fig qnt": "cold", "crane benefit fair": "cold",
    "old mvp leads": "cold",
    "utv expo": "cold",   # an event booth, like Crane; no leads yet
    # other one-offs
    "hometown quotes": "one_off", "x": "one_off", "other lead": "one_off",
    # commercial -> Cerberus
    "leo": "commercial", "work comp": "commercial",
    "district comm leads": "commercial", "agent promoter comm leads": "commercial",
    "rcfbh group life": "commercial",
    "kraft lake": "commercial",   # AgencyZoom's Commercial Leads category; no leads yet
    # not a sale
    "bob": "not_a_sale", "rewrite": "not_a_sale",
}

# The product each cross-sell source is selling into the household.
CROSS_SELL_PRODUCT = {
    "home no auto": "auto", "auto no home": "home",
    "life cross sell": "life", "umbrella": "umbrella", "cross sell": None,
}

# Staff whose name used as a lead source means their own referral or network.
# Current and past team; a new hire's name as a source lands in "unclassified"
# until it is added here. Former staff per Frank, 2026-09-24: Adrian
# Alcantara, Anastasia Perez, Michelle Garcia, Veronica Rodriguez, Maria Medina.
STAFF = {
    "frank flores", "francisco flores", "veronica flores", "amanda torricellas",
    "debbie aguilera", "crystal mango", "lorena gonzalez", "mike olvera",
    "coral barwick", "sarahi chin",
    "adrian alcantara", "anastasia perez", "michelle garcia",
    "veronica rodriguez", "maria medina",
    # in AgencyZoom's Team category, no leads yet
    "eleuterio gutierrez", "tori pletsch",
}

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
    if n in STAFF:
        return "referral"
    if _COI.search(f" {n} "):
        return "center_of_influence"
    return "unclassified"


def group(name):
    return GROUPS[classify(name)]


def coached(name):
    """True when a call on this lead source is coached and can seed Role Play.
    A call with no lead source at all is coached, as it always has been."""
    return not norm(name) or GROUPS[classify(name)]["coach"]


def board_map(names):
    """{name: group} for the names given, plus the groups themselves, for the
    board (published with the lead-source list; see publish_board)."""
    return {
        # keyed by norm(name); the board normalises the same way
        "source_group": {norm(n): classify(n) for n in names if norm(n)},
        "cross_sell_product": {n: p for n, p in CROSS_SELL_PRODUCT.items() if p},
        "groups": {k: {"label": g["label"], "who": g["who"], "products": g["products"],
                       "approach": g["approach"], "coach": g["coach"],
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


def main():
    import collections, json, pathlib
    leads = json.loads((pathlib.Path(__file__).parent / "data/az_leads_all.json").read_text())
    count = collections.Counter(l.get("leadSourceName") for l in leads if l.get("leadSourceName"))
    by = collections.defaultdict(list)
    for name, n in count.items():
        by[classify(name)].append((n, name.strip()))
    for key, g in GROUPS.items():
        if not by.get(key):
            continue
        rows = sorted(by[key], reverse=True)
        print(f"\n{g['label']}  ({len(rows)} sources, {sum(n for n, _ in rows):,} leads)"
              f"  products: {g['products'] or '-'}  owner: {g['owner'] or '-'}"
              f"  coached: {'yes' if g['coach'] else 'no'}")
        for n, name in rows:
            print(f"   {n:6,d}  {name}")


if __name__ == "__main__":
    main()

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
(`APPROACH_CONFIRMED`). `roleplay` says whether Role Play may use a group as
a session's lead source. Every lead source is still coached.
"""
import re

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
        "who": "A customer's referral, or Francisco Flores's (a source named "
               "after him).",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'Someone you know, a customer of this agency or someone who works there, gave the producer your number and said they would call.',
        "approach": "Name the person who referred them in the first sentence. The "
                    "trust is borrowed, so follow up the way that person would expect.",
    },
    # Frank, 2026-09-24: a staff member's name as the source is that person's
    # own personal network, and each works their own, never each other's.
    # Francisco's name stays a Referral (STAFF_REFERRAL). Approach and
    # backstory confirmed by Frank, 2026-09-24.
    "personal_network": {
        "label": "Personal network",
        "who": "A staff member's own personal network (a source named after one "
               "of us, other than Francisco). Each person works their own "
               "network, never someone else's.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You know the producer personally: a friend, relative or someone from their community. They mentioned they work in insurance and offered to look at your coverage.',
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
               "found us on Google or farmers.com (a form Farmers passes on) "
               "and asked an agent to contact them. Not purchased.",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        # Role Play: what the prospect knows about how this call came about.
        "backstory": 'You reached out to this agency yourself because you want a quote: you called, or found them on Google or farmers.com and asked for a call.',
        "approach": "They are ready now. Answer the question they came with, then "
                    "ask what else they have and who insures it. A Google or "
                    "farmers.com request gets called fast.",
    },
    "cold": {
        "label": "Cold / misc",
        "who": "Dug out of the system, or a one-off list: Cold lead, FIG QNT "
               "(Farmers Quotes Not Taken), Crane Benefit Fair (a booth at a "
               "local school fair), Old MVP Leads (the old CRM).",
        "products": ANY,
        "existing_household": False, "sale": True, "owner": "apollo",
        "roleplay": False,   # Frank, 2026-09-24: barely used
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
    # Facebook but are their own group (social_media, below). Neither has a
    # lead yet (2026-09-24).
    "instagram": "social_media", "linkedin": "social_media",
    # found us -> part of call-in / walk-in (Frank, 2026-09-24)
    "google": "inbound", "farmers.com": "inbound",
    "found us on google": "inbound",   # the name on some 2026-09 lead records
    # winback
    "winback": "winback", "winback by agencyzoom": "winback",
    # referral
    "existing customer referral": "referral", "referral by agencyzoom": "referral",
    # centers of influence without an "at Company" in the name (Mariah Serna:
    # Frank, 2026-09-24)
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

# Francisco's name as a source is a referral, not a personal network (Frank,
# 2026-09-24).
STAFF_REFERRAL = {"francisco flores"}

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
              f"  role play: {'yes' if g['roleplay'] else 'no'}")
        for n, name in rows:
            print(f"   {n:6,d}  {name}")


if __name__ == "__main__":
    main()

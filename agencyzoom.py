"""This AgencyZoom account's own numbers, read from agencyzoom.json.

Every agency's AgencyZoom account hands out its own ids for workflows,
service categories, resolutions and carriers, and names its workflows its
own way. agencyzoom.json holds this account's; the modules that used to
carry them as literals (claims, commercial, service_digest,
service_retention, service_notes, sales_log_auto, renewal_report,
digest_config, az_client) build their old constants from here, so their
names and shapes are unchanged. What the pipeline DOES with each id -- which
outcome a resolution counts as, which pipelines are renewals, the Sales
sheet's product names -- stays in those modules.

    workflows.junk                  a lead vendor's broken integration dumps
                                    leads into this pipeline; moves into it
                                    are ignored (digest_config.JUNK_WORKFLOW_ID)
    workflows.claim                 the Claim service workflow (claims.py)
    workflows.commercial_renewals   Cerberus's renewal workflow names
    workflows.service               each Service Center pipeline key -> the
                                    AgencyZoom workflow name(s) it covers
                                    (service_digest.PIPELINES)
    claim_categories                service category id -> the type of claim
    commercial_claim_categories     the categories that are Cerberus's
    resolutions.labels              resolution id -> its name (the fallback
                                    when /v1/api/service-resolutions fails;
                                    deleted ones stay, past SRs carry them)
    resolutions.outcome_by_id       resolution id -> the renewal outcome key
                                    (service_retention.OUTCOMES)
    resolutions.valid_from          an id not to be trusted on SRs completed
                                    before a date (a deletion moved SRs onto it)
    resolutions.trusted_by_pipeline a resolution that says the outcome on its
                                    own for Late Payments / changes /
                                    Contingencies SRs (service_notes)
    carriers                        carrier id -> the short name the Sales
                                    sheet uses (Farmers / BW / Foremost)
    product_names                   the sheet's product name for a policy:
                                    ordered rules on carrier + policy type
                                    (sales_log_auto.product_name, live.js)
    renewal_ff_carriers             the carriers the Personal Renewals
                                    workflow carries (renewal_report)
    test_lead_ids                   lead records that are tests, by id

    python3 agencyzoom.py --check     validate the file against the code's keys
    python3 agencyzoom.py --discover  read the account's current workflows,
                                      categories, resolutions and carriers
                                      from AgencyZoom and say what the file
                                      is missing or has extra
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = ROOT / "agencyzoom.json"
DATA = json.loads(JSON_PATH.read_text())


def _ints(d):
    return {int(k): v for k, v in d.items()}


WORKFLOWS = DATA["workflows"]
JUNK_WORKFLOW_ID = int(WORKFLOWS["junk"]["id"])
JUNK_WORKFLOW_NAME = WORKFLOWS["junk"]["name"]
CLAIM_WORKFLOW_ID = int(WORKFLOWS["claim"]["id"])
CLAIM_WORKFLOWS = set(WORKFLOWS["claim"]["names"])
COMMERCIAL_RENEWAL_WORKFLOWS = set(WORKFLOWS["commercial_renewals"]["names"])
SERVICE_WORKFLOWS = {k: set(v) for k, v in WORKFLOWS["service"].items()}


def service_workflows(key):
    """The AgencyZoom workflow names a Service Center pipeline key covers."""
    return set(SERVICE_WORKFLOWS[key])


CLAIM_TYPES = _ints(DATA["claim_categories"])
COMMERCIAL_CATEGORIES = {int(x) for x in DATA["commercial_claim_categories"]}
RESOLUTION_LABELS = _ints(DATA["resolutions"]["labels"])
RESOLUTION_KEY_BY_ID = _ints(DATA["resolutions"]["outcome_by_id"])
RESOLUTION_VALID_FROM = _ints(DATA["resolutions"]["valid_from"])
TRUSTED_RESOLUTIONS = {k: _ints(v) for k, v in DATA["resolutions"]["trusted_by_pipeline"].items()}
CARRIERS = _ints(DATA["carriers"])
PRODUCT_RULES = [dict(r) for r in DATA["product_names"]["rules"]]
PRODUCT_DEFAULT = DATA["product_names"]["default"]
FF_CARRIERS = {int(x) for x in DATA["renewal_ff_carriers"]}
TEST_LEAD_IDS = {int(x) for x in DATA["test_lead_ids"]}


def check(log=print):
    """Validate the file against what the code expects. Returns the problems."""
    bad = []
    import service_retention
    keys = {k for k, _, _ in service_retention.OUTCOMES}
    for rid, k in RESOLUTION_KEY_BY_ID.items():
        if k not in keys:
            bad.append(f"resolutions.outcome_by_id: {rid} -> {k!r} is not an outcome key ({sorted(keys)})")
    for k in keys:
        if k not in RESOLUTION_KEY_BY_ID.values():
            bad.append(f"resolutions.outcome_by_id: no resolution id for outcome {k!r}")
    for rid in RESOLUTION_KEY_BY_ID:
        if rid not in RESOLUTION_LABELS:
            bad.append(f"resolutions.labels: no name for {rid}")
    import service_digest
    pipes = {k for k, _, _, _ in service_digest.PIPELINES}
    for k in pipes:
        if k not in SERVICE_WORKFLOWS:
            bad.append(f"workflows.service: no workflow names for pipeline {k!r}")
    for k in SERVICE_WORKFLOWS:
        if k not in pipes:
            bad.append(f"workflows.service: {k!r} is not a Service Center pipeline ({sorted(pipes)})")
    for p, m in TRUSTED_RESOLUTIONS.items():
        if p not in pipes:
            bad.append(f"resolutions.trusted_by_pipeline: {p!r} is not a pipeline")
    for c in COMMERCIAL_CATEGORIES:
        if c not in CLAIM_TYPES:
            bad.append(f"commercial_claim_categories: {c} is not in claim_categories")
    for c in FF_CARRIERS:
        if c not in CARRIERS:
            bad.append(f"renewal_ff_carriers: {c} is not in carriers")
    import re
    for i, r in enumerate(PRODUCT_RULES):
        if "name" not in r:
            bad.append(f"product_names.rules[{i}]: no name")
        if r.get("carrier") and r["carrier"] not in CARRIERS.values():
            bad.append(f"product_names.rules[{i}]: carrier {r['carrier']!r} is not a short name in carriers")
        try:
            re.compile(r.get("match") or "")
        except re.error as e:
            bad.append(f"product_names.rules[{i}]: bad match regex ({e})")
    for b in bad:
        log(f"  agencyzoom.json: {b}")
    return bad


def discover(log=print):
    """Read the account's current workflows, service categories, resolutions
    and carriers from AgencyZoom (and the saved policy corpus) and print each
    beside what agencyzoom.json says -- the first step for a new agency, and
    the check that nothing was renamed or deleted on this one. Reads only."""
    import secrets_load
    secrets_load.load()
    from az_client import AgencyZoom
    az = AgencyZoom()

    def section(title, rows, known, label):
        """rows: (id, name) from AgencyZoom; known: id -> what the file says."""
        log(f"\n== {title}")
        seen = set()
        for rid, name in rows:
            seen.add(rid)
            ours = known.get(rid)
            mark = "   " if ours is not None else "NEW"
            note = "" if ours is None or ours == name else f"   (file says {ours!r})"
            log(f"  {mark} {rid:>8}  {name}{note}")
        for rid, ours in known.items():
            if rid not in seen:
                log(f"  GONE {rid:>7}  {ours}   (in the file, not in AgencyZoom)")

    try:
        wfs = az.pipelines_and_stages()
    except Exception as e:
        wfs, _ = [], log(f"  pipelines-and-stages: {type(e).__name__}: {e}")
    rows = []
    for w in wfs:
        wid, name = w.get("id") or w.get("workflowId"), w.get("name") or w.get("workflowName")
        if wid is not None:
            rows.append((int(wid), str(name)))
    named = {JUNK_WORKFLOW_ID: JUNK_WORKFLOW_NAME, CLAIM_WORKFLOW_ID: ", ".join(sorted(CLAIM_WORKFLOWS))}
    section(f"workflows ({label_names()})", rows, named, "workflow")

    try:
        cats = az.get("/v1/api/service-categories") or []
    except Exception as e:
        cats = []
        log(f"  service-categories: {type(e).__name__}: {e}")
    section("service categories (claim_categories)", [(int(c["id"]), str(c.get("name"))) for c in cats if c.get("id") is not None],
            CLAIM_TYPES, "category")

    try:
        res = az.get("/v1/api/service-resolutions") or []
    except Exception as e:
        res = []
        log(f"  service-resolutions: {type(e).__name__}: {e}")
    section("resolutions (resolutions.labels)", [(int(r["id"]), str(r.get("name", "")).strip()) for r in res if r.get("id") is not None],
            RESOLUTION_LABELS, "resolution")

    pol = ROOT / "data/az_policies_all.json"
    rows = []
    if pol.exists():
        import collections
        by = collections.defaultdict(collections.Counter)
        for p in json.loads(pol.read_text()):
            if p.get("carrierId") is not None:
                by[int(p["carrierId"])][str(p.get("carrierName") or p.get("carrier") or "?")] += 1
        rows = [(cid, f"{names.most_common(1)[0][0]} ({sum(names.values())} policies)") for cid, names in sorted(by.items())]
        section("carriers (carriers), from data/az_policies_all.json", rows, CARRIERS, "carrier")
    else:
        log("\n== carriers: no data/az_policies_all.json here -- run after a nightly pull, or read them off the policy corpus")
    log("")


def label_names():
    names = sorted(set().union(*SERVICE_WORKFLOWS.values()) | COMMERCIAL_RENEWAL_WORKFLOWS)
    return "service names in the file: " + ", ".join(names)


def main(argv):
    if "--check" in argv:
        bad = check()
        print("agencyzoom.json ok" if not bad else f"{len(bad)} problem(s)")
        return 1 if bad else 0
    if "--discover" in argv:
        discover()
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

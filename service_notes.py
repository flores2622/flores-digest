"""How a Service Pipeline, Late Payments or Contingencies SR ended, read from
the rep's note (Frank, 2026-09-24: "go based off of the notes for now").

WHY. Every resolution left in AgencyZoom is a renewal outcome, plus
Completed. These three pipelines are closed on Completed (09-01..09-24: 58 of
66 Service Pipeline, 56 of 60 Late Payments), so the note is the only place
the outcome is written down: "paid", "canceled for non pay", "Endorsement
Successful", "documents were signed".

ORDER. The rep's note, read by the model into one of the pipeline's OUTCOMES
below; with no note, the SR's own resolution where it says something for
this pipeline (TRUSTED_RESOLUTIONS); else "No note". These are categories of
ours, not Frank's resolutions -- if he adds resolutions for these pipelines
in AgencyZoom, match them by id first, the way service_retention does.

COST. Paid, like renewal_notes.py: one model call per batch of up to BATCH
notes, each SR's note read once and kept by SR id and note text (data/ plus
an R2 copy). Its own cache, never renewal_note_reads.json. Only an edited
note is read again. Never delete the cache casually.
"""
import json

import renewal_notes as rn

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data/service_note_reads.json"
CACHE_R2_KEY = "cache/service_note_reads.json"
BATCH = 25

# pipeline key (service_digest.PIPELINES) -> (key, board label, counts as,
# what it means for the model). "good" and "bad" make the pipeline's rate
# where it has one (RATE below); "open" sits outside it.
OUTCOMES = {
    "late_payments": (
        ("paid", "Paid", "good",
         "the customer paid (past due, in full, or set up a payment) and the policy stays"),
        ("cancelled_nonpay", "Cancelled for non-pay", "bad",
         "the policy cancelled, or is being let cancel, for non-payment"),
        ("client_cancelled", "Client cancelled / went elsewhere", "bad",
         "the customer cancelled the policy or moved it to another carrier or agent"),
        ("unable_to_contact", "Unable to Contact/No Show", "open",
         "the rep could not reach the customer and the note does not say how it ended"),
        ("other", "Other", "open",
         "anything else: a duplicate SR, a wrong policy, a note about something else"),
    ),
    "changes": (
        ("change_made", "Change made", "open",
         "a change was made to a policy: vehicle, driver, coverage, deductible, "
         "mortgagee or lienholder, named insured or trust, beneficiary, discount, "
         "EFT or payment method; an endorsement confirmation"),
        ("policy_cancelled", "Policy cancelled", "open",
         "a policy was cancelled at the customer's request or by the company"),
        ("other_service", "Other service", "open",
         "service with no change to a policy: a claim started, a letter of experience "
         "or ID cards sent, a question answered, documents sent"),
        ("not_done", "Not done", "open",
         "the change was quoted or looked at but not made: the customer declined, "
         "or the carrier would not allow it"),
        ("unable_to_contact", "Unable to Contact/No Show", "open",
         "the rep could not reach the customer"),
    ),
    "missing_docs": (
        ("cleared", "Contingency cleared", "good",
         "the contingency was cleared: documents signed, uploaded or approved, "
         "proof sent, Signal or the app completed"),
        ("policy_cancelled", "Policy cancelled", "bad",
         "the policy was cancelled (by the customer, or for the contingency)"),
        ("not_cleared", "Closed, not cleared", "open",
         "the SR was closed while the contingency was still pending: waiting on the "
         "customer or the carrier's system"),
        ("unable_to_contact", "Unable to Contact/No Show", "open",
         "the rep could not reach the customer"),
    ),
}
NO_NOTE = ("no_note", "No note", "open")
# Rules for one pipeline, from the 2026-09-24 spot-check of 09-01..09-23.
RULES = {
    "late_payments": [
        "The customer was reached but has not paid yet (\"will call or stop by when "
        "he has it\", \"will contact us when she can make payment\") is other, not "
        "unable_to_contact.",
    ],
    "changes": [
        "An endorsement result -- \"Endorsement Successful\", a confirmation number, "
        "new and prior full term premium -- is change_made.",
        "A discovered or unrated driver resolved by signed documents is change_made.",
    ],
}
# What the rate is called on the board, where a pipeline has one.
RATE = {"late_payments": "saved", "missing_docs": "cleared"}
# With no note, a resolution that already says the outcome. Unable to Contact
# only from 2026-09-24: before it, AgencyZoom's clean-up had moved Shot Clock
# Expired and Unable to Complete onto it (service_retention.RESOLUTION_VALID_FROM).
TRUSTED_RESOLUTIONS = {
    "late_payments": {38304: "unable_to_contact"},
    "changes": {32570: "policy_cancelled", 38304: "unable_to_contact"},
    "missing_docs": {38304: "unable_to_contact"},
}
PIPELINE_NAMES = {"late_payments": "Late Payments", "changes": "Service Pipeline (changes and "
                  "basic service)", "missing_docs": "Contingencies (anything pending on a policy)"}


def outcomes(pipe):
    """[[key, label, kind], ...] for a document, NO_NOTE last."""
    return [[k, l, c] for k, l, c, _ in OUTCOMES[pipe]] + [list(NO_NOTE)]


def _system(pipe):
    return (f"You read the notes an insurance agency's service reps leave when they close "
            f"a {PIPELINE_NAMES[pipe]} service request, and say how each one ended.\n\n"
            "Pick exactly one of these for each note:\n"
            + "\n".join(f"  {k}: {l} -- {m}" for k, l, _, m in OUTCOMES[pipe]) + """

Rules:
- Only what the note says HAPPENED counts, not a plan ("will call back").
- "notes are there" / "notes present" with the change named ("change made, \
notes are there") is what the change says. A note that says only "done" or \
"completed" is the pipeline's first choice.
- Every note gets one choice: when in doubt, the one that fits best.
""" + "".join(f"- {r}\n" for r in RULES.get(pipe, [])) + """
Return ONLY a JSON object mapping each id to one choice, e.g. {"12345": \"""" +
            OUTCOMES[pipe][0][0] + """\"}.""")


def load(log=print):
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=CACHE_R2_KEY)["Body"].read()
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_bytes(body)
        log("  service notes: restored earlier reads from R2")
        return json.loads(body)
    except Exception:
        return {}


def save(cache, log=print):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=CACHE_R2_KEY, Body=CACHE_FILE.read_bytes(),
                       ContentType="application/json")
    except Exception as e:
        log(f"  service notes: R2 copy not saved ({type(e).__name__})")


def _ask(cs, model, pipe, chunk):
    base = {"model": model, "system": _system(pipe),
            "messages": [{"role": "user", "content": json.dumps(chunk, ensure_ascii=False)}]}
    room = 60 * len(chunk) + 200
    try:
        resp = cs._post(dict(base, max_tokens=room, thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = cs._post(dict(base, max_tokens=room * 4))
    got = cs._extract(resp)
    if got is None:
        got = cs._extract(cs._post(dict(base, max_tokens=room * 4)))
    if not isinstance(got, dict):
        raise ValueError("no JSON in response")
    return got


def read(pipe, srs, log=print):
    """{sr id: outcome key} for these SRs of one pipeline, reading only notes
    not already read. An SR missing from the result has no note, or its read
    failed (retried next night) -- never raises."""
    choices = {k for k, *_ in OUTCOMES[pipe]}
    cache = load(log=log)
    want = {}
    for t in srs:
        note = rn.clean(t.get("resolutionDesc"))
        if not note:
            continue
        sid = str(t.get("id"))
        hit = cache.get(sid)
        if hit and hit.get("h") == rn._h(note) and hit.get("pipe") == pipe:
            continue
        subj = (t.get("subject") or "").strip()
        want[sid] = ((f"{subj}: {note}" if subj else note)[:1500], note)
    if want:
        try:
            import call_summary as cs
            if not cs._key():
                raise RuntimeError("ANTHROPIC_API_KEY not set")
            model = cs.pick_model()
        except Exception as e:
            log(f"  service notes: not read ({type(e).__name__}: {str(e)[:160]}) -- "
                f"a later night reads them")
            model = None
        ids, n_read = list(want), 0
        for i in range(0, len(ids) if model else 0, BATCH):
            chunk = {k: want[k][0] for k in ids[i:i + BATCH]}
            try:
                got = _ask(cs, model, pipe, chunk)
            except Exception as e:
                log(f"  service notes: {pipe} batch not read ({type(e).__name__}: {str(e)[:160]})")
                continue
            fallback = "other" if pipe == "late_payments" else OUTCOMES[pipe][0][0]
            for k in chunk:
                v = got.get(k)
                cache[k] = {"h": rn._h(want[k][1]), "pipe": pipe, "model": model,
                            "choice": v if v in choices else fallback}
            n_read += len(chunk)
        if n_read:
            save(cache, log=log)
            log(f"  service notes: read {n_read} new {pipe} note(s) with {model}")
    out = {}
    for t in srs:
        sid, note = str(t.get("id")), rn.clean(t.get("resolutionDesc"))
        hit = cache.get(sid)
        if note and hit and hit.get("h") == rn._h(note) and hit.get("pipe") == pipe:
            out[sid] = hit["choice"]
    return out


def sr_outcome(pipe, t, note_key):
    """(key, source) for one completed SR: the note's read (source "notes"),
    else a resolution that says it ("resolution"), else a note not read yet
    ("unread", shown as No note), else "no_note"."""
    import service_retention as sr
    if note_key:
        return note_key, "notes"
    rid = t.get("resolutionId")
    since = sr.RESOLUTION_VALID_FROM.get(rid)
    key = TRUSTED_RESOLUTIONS.get(pipe, {}).get(rid)
    if key and not (since and sr._d(t.get("completeDate")) < since):
        return key, "resolution"
    if rn.clean(t.get("resolutionDesc")):
        return "no_note", "unread"
    return "no_note", "no_note"

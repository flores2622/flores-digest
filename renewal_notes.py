"""The rep's own note on a renewal SR, read by the model, for SRs closed on a
resolution that is not one of the team's renewal resolutions (Frank,
2026-09-24).

WHY. Before 2026-09-24 nearly every renewal SR was closed "Completed", which
says nothing about the outcome -- 3,431 of them in a year, 3,227 with a note.
The note does: "Low increase, review if needed", "reviewed over the phone, okay
with increase", "added explorer in storage mode", "rewrote into BW". Keyword
rules were tried first and misread too much to use: "possible deductible
options" is not an endorsement, "possible BW rewrite if customer calls" is not
a rewrite, "left vm and autos on noc" is not a cancellation.

ORDER. The SR's own resolution wins; then this read; a note that is missing
or says nothing is Unable to Contact/No Show (Frank, 2026-09-24). Frank's
resolutions are the only outcomes on the board.

COST. The second paid step after call_summary.py: one model call per batch of
up to BATCH notes. Every read is kept by SR id and note text (data/ plus an R2
copy, like the household map), so an SR is paid for once -- only a note that
is edited is read again. Never delete the cache casually.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data/renewal_note_reads.json"
CACHE_R2_KEY = "cache/renewal_note_reads.json"
BATCH = 25

# What the model may answer, and what each means -- the team's own renewal
# resolutions, in Frank's words. "unclear" keeps the policy-record reading.
CHOICES = {
    "renewed_as_is": "Renewed: Accepted as is -- the rep spoke with the customer "
                     "about the renewal and they kept it without changes.",
    "no_action_review": "No action: Review if needed -- the rep looked at the "
                        "renewal (a low increase, no change, a decrease) and did "
                        "not call because the change did not call for it.",
    "renewed_endorsed": "Renewed: Endorsed -- it renewed and a change was ACTUALLY "
                        "made to the policy (vehicle, driver, coverage, deductible).",
    "rewrite_accepted": "Rewrite Accepted -- the policy was ACTUALLY rewritten "
                        "(new policy, another carrier such as Bristol West).",
    "cancelled_rewrite_declined": "Cancelled: Rewrite Declined -- a rewrite was "
                                  "offered and declined, and the policy is cancelling.",
    "cancelled_no_option": "Cancelled, no endorse/rewrite available -- the policy "
                           "is cancelling or has cancelled.",
    "client_cancelled": "Client Cancelled -- the client cancelled mid term, went to "
                        "the carrier directly to cancel, or never gave us the chance "
                        "to review or retain the policy.",
    "cancelled_before_sr": "The policy was ALREADY cancelled before this renewal came "
                           "up -- cancelled last year, home sold, moved to another agent -- "
                           "and the SR is only being closed out.",
    "unable_to_contact": "Unable to Contact/No Show -- the rep tried to reach the "
                         "customer (voicemail, no answer, bad number) or they did "
                         "not show, and it renewed as is.",
    "unclear": "The note does not say what happened to the renewal.",
}

SYSTEM = """You read the notes an insurance agency's service reps leave when \
they close a policy RENEWAL service request, and say how each renewal ended.

Pick exactly one of these for each note:
""" + "\n".join(f"  {k}: {v}" for k, v in CHOICES.items()) + """

Rules:
- Only what the note says HAPPENED counts. An idea for later -- "possible \
deductible options", "possible rewrite if customer calls", "will make sure we \
have a cross-sell lead" -- is not a change; judge the rest of the note.
- "Review if needed" with no conversation is no_action_review. A cross-sell \
or FFR call that also reviewed the renewal and the customer kept it is \
renewed_as_is (or renewed_endorsed if a change was made).
- A policy that had already cancelled before this renewal came up ("cancelled \
in 2025", "sold home", "transferred to another agent") is cancelled_before_sr, \
not unclear.
- A duplicate SR, a wrong policy, or a payment note with nothing about the \
renewal is unclear.
- When in doubt, answer unclear.

Return ONLY a JSON object mapping each id to one choice, e.g. \
{"12345": "no_action_review"}."""


def _h(text):
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def clean(html):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def load(log=print):
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=CACHE_R2_KEY)["Body"].read()
        CACHE_FILE.write_bytes(body)
        log("  renewal notes: restored earlier reads from R2")
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
        log(f"  renewal notes: R2 copy not saved ({type(e).__name__})")


def _ask(cs, model, chunk):
    """One batch, the way call_summary._ask does it: thinking off, and if a
    model rejects that, or the answer is cut off, one retry with more room.
    Raises rather than return nothing, so a failed batch is never cached."""
    base = {"model": model, "system": SYSTEM,
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


def read(srs, log=print):
    """{sr id: choice} for these SRs' notes, "unclear" included, reading only
    notes not already read. An SR missing from the result has no note, or its
    read failed (retried next night) -- never raises."""
    cache = load(log=log)
    want = {}
    for t in srs:
        note = clean(t.get("resolutionDesc"))
        if not note:
            continue
        sid = str(t.get("id"))
        hit = cache.get(sid)
        if hit and hit.get("h") == _h(note):
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
            log(f"  renewal notes: not read ({type(e).__name__}: {str(e)[:160]}) -- "
                f"counted as Unable to Contact/No Show until a later night reads them")
            model = None
        ids, n_read = list(want), 0
        for i in range(0, len(ids) if model else 0, BATCH):
            chunk = {k: want[k][0] for k in ids[i:i + BATCH]}
            try:
                got = _ask(cs, model, chunk)
            except Exception as e:
                log(f"  renewal notes: batch not read ({type(e).__name__}: {str(e)[:160]})")
                continue
            for k in chunk:
                v = got.get(k)
                cache[k] = {"h": _h(want[k][1]), "choice": v if v in CHOICES else "unclear",
                            "model": model}
            n_read += len(chunk)
        if n_read:
            save(cache, log=log)
            log(f"  renewal notes: read {n_read} new note(s) with {model}")
    out = {}
    for t in srs:
        sid, note = str(t.get("id")), clean(t.get("resolutionDesc"))
        hit = cache.get(sid)
        if note and hit and hit.get("h") == _h(note):
            out[sid] = hit["choice"]          # "unclear" included: read, says nothing
    return out


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
import re

ROOT = pathlib.Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data/renewal_note_reads.json"
CACHE_R2_KEY = "cache/renewal_note_reads.json"
BATCH = 25

# What the model may answer, and what each means -- the team's own renewal
# resolutions, in Frank's words. "unclear" is Unable to Contact/No Show.
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
    "client_cancelled": "Client Cancelled -- the client is cancelling at this "
                        "renewal: went to the carrier directly to cancel, or never "
                        "gave us the chance to review or retain the policy.",
    "unable_to_contact": "Unable to Contact/No Show -- the rep tried to reach the "
                         "customer (voicemail, no answer, bad number) or they did "
                         "not show, and it renewed as is.",
    "sold_moved": "Cancelled: Sold/Moved -- the policy is cancelling at this renewal "
                  "because the customer sold the vehicle, home or item, or moved.",
    "cancelled_before_sr": "Mid-term Cancellation -- the policy was already "
                           "cancelled before this renewal SR was generated: "
                           "cancelled mid term or in an earlier year, the home "
                           "sold, moved to another agent.",
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
- "Review if needed" with no conversation is no_action_review. So is a note \
that only says the policy renewed or was reviewed ("renewed", "reviewed", \
"already reviewed") and says nothing about talking to the customer.
- The customer reviewed the renewal with a rep -- in person, by phone, by \
text or email -- and nothing was changed is renewed_as_is, even when changes \
are planned for later. A cross-sell or FFR call that also reviewed the renewal \
and the customer kept it is renewed_as_is (or renewed_endorsed if a change \
was made).
- A customer who cannot be reached -- bad number, bad email, a postcard sent \
instead -- is unable_to_contact, even if the note also says review if needed.
- A policy already cancelled before the SR -- "cancelled in 2025", "policy \
cancelled 1/2026", "home sold last year", "transferred to a different agent" -- \
is cancelled_before_sr. cancelled_no_option is only a policy cancelling at \
THIS renewal.
- A policy cancelling at this renewal because the customer sold it, got rid \
of it or moved ("got rid of the ATV", "sold the car", "moved out of state") \
is sold_moved.
- A duplicate SR, a wrong policy, a policy that does not renew this term, or \
a payment note with nothing about the renewal is unclear.
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


def _ask(cs, model, chunk, system=None):
    """One batch, the way call_summary._ask does it: thinking off, and if a
    model rejects that, or the answer is cut off, one retry with more room.
    Raises rather than return nothing, so a failed batch is never cached."""
    base = {"model": model, "system": system or SYSTEM,
            "messages": [{"role": "user", "content": json.dumps(chunk, ensure_ascii=False)}]}
    room = 60 * len(chunk) + 200
    think = {"thinking": {"type": "disabled"}}
    try:
        resp = cs._post(dict(base, max_tokens=room, **think))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        think = {}
        resp = cs._post(dict(base, max_tokens=room * 4))
    got = cs._extract(resp)
    if got is None:
        # The retry keeps thinking off too, or it thinks into its own budget.
        got = cs._extract(cs._post(dict(base, max_tokens=room * 4, **think)))
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


# ---- the customer's texts, read on their own (Frank, 2026-09-27) -----------
# Read beside the note in ONE prompt, the model let texts about a payment or
# ID cards turn clear notes ("Already reviewed") into "unclear" and No action
# into Unable to Contact (22 of 61 SRs, 09-01..09-25). So the texts get their
# own narrow question, and service_retention.with_texts() combines the two by
# rule: texts can only add what the note cannot know -- the customer leaving,
# or the renewal talked over with them.
TEXT_CHOICES = {
    "leaving": "the customer says they are cancelling, switching companies or already bought "
               "insurance elsewhere, or asks us to leave the policy cancelled",
    "sold_moved": "the customer says the policy is ending because they sold the car/home/item or moved",
    "already_cancelled": "the texts show the policy was already cancelled BEFORE this renewal",
    "discussed_kept": "the customer and a rep talked about THIS renewal (its price, coverage, "
                      "payment dates, whether to keep it) and the customer is keeping it, "
                      "with no change made",
    "discussed_changed": "the customer and a rep talked about this renewal and a change to the "
                         "policy was actually made (vehicle, driver, coverage, deductible)",
    "other": "anything else: texts about a payment, a bill, ID cards, a claim, a quote for "
             "something new, automation with no reply, or the customer did not answer",
}
_CUSTOMER_SAID = {"leaving", "sold_moved", "already_cancelled"}
# The customer's own words have to say it (Kenneth Lansford's "Stop" to a
# bundling text read as leaving; Maria Zavala's name and email as already
# cancelled -- 2026-09-27).
_GONE_WORDS = re.compile(
    r"cancel|switch|another (company|insurance|agent|carrier)|other (company|insurance)|elsewhere|"
    r"geico|progressive|state farm|allstate|usaa|root|sold|selling|got rid|no longer (have|own|need)|"
    r"moved|moving|mov[ií]|mudamos|mud[eé]|vend[ií]|vendimos|otr[ao] (compa|segur|aseguranza)|"
    r"dar de baja|leave (our|my|the) policy|don'?t (want|need) (it|the policy|insurance)", re.I)
_CUSTOMER_LINE = re.compile(r"^\S+ \S+ customer: (.*)$", re.M)


def _guard(choice, lines):
    said = [m.group(1) for m in _CUSTOMER_LINE.finditer(lines)]
    if choice in _CUSTOMER_SAID and not any(_GONE_WORDS.search(x) for x in said):
        return "other"
    if choice in ("discussed_kept", "discussed_changed") and not said:
        return "other"
    return choice
TEXT_SYSTEM = """You read the text messages between an insurance agency and one \
customer while the agency was working that customer's policy RENEWAL, and say \
what the texts show about the renewal. Lines are oldest first; "customer" is \
the customer, a first name is the agency's rep, "(automation)" is an automatic \
reminder, not a person.

Pick exactly one for each item:
""" + "\n".join(f"  {k}: {v}" for k, v in TEXT_CHOICES.items()) + """

Rules:
- Only what the CUSTOMER says, or a rep's reply to them about the renewal, counts.
- A payment, a late bill, ID cards or a claim is "other" even when the customer \
is friendly or thanks the rep -- that is not a talk about the renewal.
- A reminder with no reply, or an "ok" to a reminder, is "other".
- leaving, sold_moved and already_cancelled need the CUSTOMER's own words. A \
rep warning that a policy will cancel for non-payment, or sending payment \
links or a cancellation phone number, is "other".
- Changing an email, phone or address, or sending ID cards, is not a change \
to the policy -- "other" (or discussed_kept if the renewal itself was talked over).
- "Stop" / "unsubscribe" means stop texting, NOT cancel the policy -- "other".
- discussed_changed only when the texts say the change WAS made. Asking about \
a pay plan or options, or a rep offering changes with no answer, is not a \
change (discussed_kept if the customer talked it over, else other).
- When in doubt, answer other.

Return ONLY a JSON object mapping each id to one choice."""


def read_texts(srs, texts, log=print):
    """{sr id: TEXT_CHOICES key} for the SRs in `texts` ({sr id: lines}),
    reading only texts not already read (kept in the same cache, key
    "tx:<id>", by the texts' own hash). Never raises."""
    cache = load(log=log)
    want = {}
    for t in srs:
        sid = str(t.get("id"))
        tx = texts.get(sid)
        if not tx:
            continue
        hit = cache.get("tx:" + sid)
        if hit and hit.get("h") == _h(tx):
            continue
        subj = (t.get("subject") or "").strip()
        want[sid] = (f"Renewal: {subj}\n{tx[-3000:]}", tx)
    if want:
        try:
            import call_summary as cs
            if not cs._key():
                raise RuntimeError("ANTHROPIC_API_KEY not set")
            model = cs.pick_model()
        except Exception as e:
            log(f"  renewal texts: not read ({type(e).__name__}: {str(e)[:160]})")
            model = None
        ids, n_read = list(want), 0
        for i in range(0, len(ids) if model else 0, BATCH):
            chunk = {k: want[k][0] for k in ids[i:i + BATCH]}
            try:
                got = _ask(cs, model, chunk, system=TEXT_SYSTEM)
            except Exception as e:
                log(f"  renewal texts: batch not read ({type(e).__name__}: {str(e)[:160]})")
                continue
            for k in chunk:
                v = got.get(k) if got.get(k) in TEXT_CHOICES else "other"
                v = _guard(v, want[k][1])
                cache["tx:" + k] = {"h": _h(want[k][1]), "choice": v, "model": model}
            n_read += len(chunk)
        if n_read:
            save(cache, log=log)
            log(f"  renewal texts: read {n_read} SR(s) with {model}")
    out = {}
    for t in srs:
        sid = str(t.get("id"))
        tx, hit = texts.get(sid), cache.get("tx:" + str(t.get("id")))
        if tx and hit and hit.get("h") == _h(tx):
            out[sid] = _guard(hit["choice"], tx)
    return out


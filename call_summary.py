"""Per-call summary and objection read for the Call Detail panel.

Frank, 2026-08-25: "instead of the first sentence of the transcript in the call
detail, can you give me a summary of what you transcribed, if the lead gave an
objection or not, if the producer attempted to overcome that objection, and if
they were successful or not".

WHAT THIS NEEDS THAT THE REST OF THE PIPELINE DID NOT
-----------------------------------------------------
transcribe_file reads only the first and last 30 seconds, which is all the
live/voicemail classification ever needed. An objection and its rebuttal live in
the MIDDLE: Allen Lawson's "I told her I didn't want to give somebody all the
same damn information again" sits four minutes into a 393-second call. So this
module drives transcribe.transcribe_full over the whole recording, for LIVE
CONTACTS ONLY -- 58 minutes of audio across 21 calls on 2026-08-24, about ten
minutes of compute, against 75 minutes for every dial.

WHEN THE TRANSCRIPT CANNOT CARRY IT
-----------------------------------
Whisper base int8 is fine on English and collapses on Spanish. Abel Ramos's
201-second call came back as "(speaking in foreign language)" and then the word
"Okay" about two hundred times. Three of 2026-08-24's 21 transcribed live
contacts were Spanish-tagged and one more was an English repetition loop, so
roughly a fifth of the book cannot be summarised from audio at all.

Frank's call: fall back to the producer's own notes rather than print nothing.
`source` on every row says which it was, so a reader always knows whether they
are looking at the recording or at what the producer typed.

WHY A MODEL CALL AND NOT A PATTERN
----------------------------------
"Did the producer attempt to overcome the objection, and did it work" is not a
keyword question. The API key lives in secrets/all.env as ANTHROPIC_API_KEY. If
it is absent the module degrades to producer notes for every row and says so --
the build never fails over this.
"""
import json
import os
import pathlib
import re

import requests

import transcribe as T

ROOT = pathlib.Path(__file__).resolve().parent

# A transcript has to clear all three to be worth sending to the model.
OVERCOME_VALUES = ("yes", "advanced", "no", "unclear")
MIN_CHARS = 120           # under this there is nothing to summarise
MAX_REPEAT_RATIO = 0.35   # one word eating a third of the text is a loop
MAX_FOREIGN_SHARE = 0.25  # mostly "(speaking in foreign language)" is unusable

API_URL = "https://api.anthropic.com/v1/messages"
MODELS_URL = "https://api.anthropic.com/v1/models"
API_VERSION = "2023-06-01"
TIMEOUT = 90



def _key():
    return (os.environ.get("ANTHROPIC_API_KEY") or "").strip()


BRIEF_CALL_SECONDS = 60


def usable(text, seconds=None):
    """(ok, reason) -- can this transcript support a summary?

    Frank, 2026-08-26: a quick hang-up does not deserve a flag. "Transcription
    too short" reads as a fault in the pipeline when the honest answer is that
    a 26-second call had 26 seconds of speech in it. On a SHORT call say so
    plainly; keep the flag for a long call that came back with nothing, which
    is the case where something really did go wrong.
    """
    t = (text or "").strip()
    if len(t) < MIN_CHARS:
        if seconds and seconds <= BRIEF_CALL_SECONDS:
            return False, "brief call"
        return False, "little speech captured"
    foreign = sum(len(m.group(0)) for m in T.FOREIGN.finditer(t))
    if foreign / len(t) > MAX_FOREIGN_SHARE:
        return False, "not transcribable (foreign language)"
    if T.repetition_ratio(t) > MAX_REPEAT_RATIO:
        return False, "transcription broke down (repetition loop)"
    return True, ""


def pick_model():
    """Newest Sonnet the account can see.

    Deliberately discovered rather than hardcoded -- a pinned model id rots, and
    this build runs unattended every weekday. ANTHROPIC_MODEL overrides.
    """
    override = (os.environ.get("ANTHROPIC_MODEL") or "").strip()
    if override:
        return override
    try:
        r = requests.get(MODELS_URL, timeout=30, headers={
            "x-api-key": _key(), "anthropic-version": API_VERSION})
        r.raise_for_status()
        ids = [m["id"] for m in r.json().get("data", [])]
        for want in ("sonnet", "opus", "haiku"):
            hit = [i for i in ids if want in i.lower()]
            if hit:
                return hit[0]
    except Exception:
        pass
    return "claude-sonnet-4-5"


SYSTEM = """You read one sales call from an insurance agency and report what \
happened. You are given a machine transcript that is often noisy: words are \
misheard, speaker turns are not marked, and both sides may be paraphrased badly.

Return ONLY a JSON object, no prose around it, with exactly these keys:

  "summary"     2 sentences max, plain past tense, what the call was about and \
how it ended. Name what the prospect actually said. Do not pad.
  "service_call"  true ONLY if the call was HOUSEKEEPING on a policy already \
in force and no new business was being sought -- a renewal review, a premium \
or payment question, a claim, adding or removing a vehicle or driver, \
cancelling, chasing paperwork on a policy of OURS that is already sold.
  Chasing a document is only service when the policy is ours and already in \
force. Asking a PROSPECT for their current carrier's declarations page, \
renewal notice or current premium is NEW BUSINESS -- that document exists to \
be quoted against, and the whole point of getting it is to win the account.
  It is FALSE whenever the producer is trying to WRITE something, even to a \
long-standing customer and even if the call also touches an existing policy. \
Selling a product the household does not have yet is new business, not \
service: offering auto to a home-only customer because rates dropped, \
re-quoting someone who cancelled, adding a life policy. If the producer is \
pitching, quoting or asking for the chance to quote ANYTHING, answer false. \
When in doubt, answer false -- a service call wrongly marked here is removed \
from the producer\'s day entirely.
  "quote_presented"  true ONLY if the PRODUCER presented OUR price for a \
specific policy they are proposing -- a rated premium, a monthly or six-month \
figure, a down payment -- that the prospect could accept or turn down on this \
call. Count it even if the price was only spoken and never written down \
anywhere. It is FALSE for every other kind of price talk, and prices come up \
constantly on these calls without a quote being presented:
    - what the prospect pays their CURRENT carrier, or what a competitor \
quoted them. That is the prospect's number, not ours, however precise it is.
    - general or ballpark pricing -- "it usually runs around X", "most people \
in your situation pay Y" -- with no rated figure for this prospect.
    - the prospect ASKING what something would cost, when no figure came back \
on this call.
    - a price for a policy already in force that is being reviewed, renewed or \
adjusted. A renewal premium is not a quote.
  If the only figures in the transcript came out of the prospect's mouth, this \
is false.
  "quote_agreed"  true ONLY if no quote was presented on this call AND the \
prospect agreed to be quoted or to a specific next contact for pricing -- a \
named callback time, "send it to me", "text me the quote". false if they \
declined, gave a vague brush-off, or if a quote WAS presented. A prospect who \
could not talk now but set a time to hear pricing is true.
  "objections"  a JSON array, one entry per objection the PROSPECT raised, in \
the order they came up. Empty array if they raised none. At most 3 entries. \
Each entry is an object with exactly these keys:
      "objection"  the objection in your own words, 12 words or fewer
      "addressed"  "yes" if the producer engaged it -- gave a reason, offered \
an alternative, or asked a question to open it back up. "no" if the producer \
acknowledged it and moved on, or ignored it.
      "overcome"   "yes" if the prospect moved on that specific point, \
"advanced" if the objection was NOT resolved but the call carried on \
substantively anyway, "no" if they held it and the call ended on it, "unclear" \
if the transcript does not settle it.

Rules that matter more than being helpful:
- MERGE near-duplicates into one entry before you count. "Too expensive" and \
"can't afford it right now" are ONE objection, not two. So are "I'm with \
State Farm" and "I already have insurance".
- If more than 3 distinct objections survive merging, return the 3 that got \
the most discussion and mention the rest in the summary sentence.
- A noisy transcript is a reason to answer "unclear", not to guess. Being \
wrong here is worse than being uninformative.
- "addressed" is about effort, "overcome" is about result. A producer can \
address an objection well and still lose it. Do not let one answer drag the \
other.
- Decide "overcome" in THIS order: did the call die on it -> "no". Did they \
drop the point -> "yes". Did the call carry on with real selling despite it -> \
"advanced". Only if none of those can be told from the transcript -> \
"unclear". "unclear" is the LAST resort, not the safe default: if the \
transcript shows what happened next, it is not unclear.
- "advanced" is a REAL result, not a softer "unclear". Use it when the producer \
parked the objection and kept selling: the prospect stayed on the line and the \
call moved to quoting, fact-finding, or a scheduled next step. Sarahi's \
2026-08-25 call with the Beltran household is the case -- "I need to ask my \
husband" was never resolved, and the next twelve minutes were coverage limits, \
mortgage details and prior policy dates. That is not a lost objection. Reserve \
"no" for an objection the prospect HELD and the call died on. Judge this by \
what happens AFTER the objection in the transcript, not by whether they bought.
- Never invent a name, price, coverage or date that is not in the input.
- "not interested" with no reason given IS an objection.
- An objection is the prospect WITHHOLDING something -- a demand, a refusal, a
stall, a condition. Background commentary is NOT an objection, even when it
mentions a competitor or a price. "I just got quotes from American Family"
states a fact and asks nothing of the producer; "your price is higher than
American Family" is an objection. If nothing is being asked of the producer and
nothing needs overcoming, leave it out and put it in the summary instead
(Frank, 2026-08-26, Coral's call with Hugo Bojorquez: "idk if i would consider
the first objection as a true objection, it was really just a comment that he
recently got quotes from american family").
- Do not treat the producer's own pitch as something the prospect said.
- Refer to the agency side ONLY as the name given to you as the producer. Never \
take their identity from the transcript: these calls open with the agency \
greeting, which names the agency owner rather than whoever is on the line."""


MAX_OBJECTIONS = 3


def _clean_objections(raw):
    """Normalise and cap whatever the model returned."""
    out = []
    for o in (raw or [])[:MAX_OBJECTIONS]:
        if not isinstance(o, dict):
            continue
        txt = str(o.get("objection") or "").strip()
        if not txt or txt.lower() in ("none", "n/a"):
            continue
        a = str(o.get("addressed") or "").strip().lower()
        oc = str(o.get("overcome") or "").strip().lower()
        out.append({"objection": txt,
                    "addressed": a if a in ("yes", "no") else "no",
                    # "advanced" MUST be in this whitelist. It was added to
                    # the prompt on 2026-08-26 and silently coerced to
                    # "unclear" here, so the state looked like the model was
                    # refusing to use it when the parser was eating it.
                    "overcome": oc if oc in OVERCOME_VALUES else "unclear"})
    return out


def upgrade(d):
    """Read a row written before objections became a list.

    The cache on disk survives a deploy, so old single-objection rows have to
    keep rendering. One scalar objection becomes a one-entry list; "none"
    becomes an empty list, which is exactly how a no-objection call is stored
    now.
    """
    if not isinstance(d, dict) or "objections" in d:
        return d
    d = dict(d)
    obj = str(d.pop("objection", "") or "").strip()
    att = str(d.pop("attempted", "") or "").strip().lower()
    oc = str(d.pop("outcome", "") or "").strip().lower()
    if obj and obj.lower() not in ("none", "n/a", ""):
        d["objections"] = [{"objection": obj,
                            "addressed": "yes" if att == "yes" else "no",
                            "overcome": oc if oc in OVERCOME_VALUES
                            else "no" if oc == "not overcome"
                            else "yes" if oc == "overcome" else "unclear"}]
    else:
        d["objections"] = []
    return d


def _post(body):
    r = requests.post(API_URL, json=body, timeout=TIMEOUT, headers={
        "x-api-key": _key(), "anthropic-version": API_VERSION,
        "content-type": "application/json"})
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} {r.text[:300]}")
    return r.json()


def _extract(resp):
    """Text blocks only, then the JSON object inside them.

    Returns None when the model produced no parsable object -- which on a long
    call usually means it ran out of budget mid-answer, not that it refused.
    """
    text = "".join(b.get("text", "") for b in resp.get("content", [])
                   if b.get("type", "text") == "text")
    m = re.search(r"\{.*\}", text, re.S)   # tolerates ```json fences
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def _ask(model, transcript, notes, seconds, producer="the producer"):
    """One call, one read. Two failure modes are handled, both seen for real.

    1. THINKING ATE THE WHOLE BUDGET. claude-sonnet-5 thinks by default, and on
       Guillermo Lara's 24-minute call it spent all 600 output tokens thinking
       and returned zero text -- the summary came back empty for the longest,
       most interesting call of the day. Thinking is disabled here: this is a
       read-and-report task, not a reasoning one, and disabling it cut output
       from 1,447 tokens to 314 with no loss of quality (same objections, same
       verdicts). If a model ever rejects the parameter, the retry drops it and
       buys a much bigger budget instead.
    2. TRUNCATED MID-OBJECT. Any answer that hits the cap has no closing brace
       and cannot be parsed. Retry once with room to finish.
    """
    msg = [{"role": "user", "content":
            f"Producer on this call: {producer}\n"
            f"Call length: {seconds} seconds\n\n"
            f"Producer's own notes (may be empty):\n{notes or '(none)'}\n\n"
            f"Machine transcript:\n{transcript}"}]
    base = {"model": model, "system": SYSTEM, "messages": msg}

    try:
        resp = _post(dict(base, max_tokens=1000,
                          thinking={"type": "disabled"}))
    except RuntimeError as e:
        if "thinking" not in str(e).lower():
            raise
        resp = _post(dict(base, max_tokens=3000))

    d = _extract(resp)
    if d is None:
        resp = _post(dict(base, max_tokens=3000))
        d = _extract(resp)
    if d is None:
        raise ValueError("no JSON in response")

    return {"quote_agreed": bool(d.get("quote_agreed")),
            "service_call": bool(d.get("service_call")),
            "quote_presented": bool(d.get("quote_presented")),
            "summary": str(d.get("summary") or "").strip(),
            "objections": _clean_objections(d.get("objections"))}


def from_notes(notes, why):
    """No usable audio: show what the producer wrote, and say why."""
    return {"summary": (notes or "").strip(), "objections": [],
            "source": "producer note", "why": why}


def _ck(producer, number):
    """Cache key. JSON has no tuple keys, so the two parts ride in one string."""
    return f"{producer}|{number}"


def _audio_legs(day):
    """(producer, number) -> [(path, seconds, class, direction)], longest first.

    Built from the transcripts file rather than the raw call log, because that
    file now covers BOTH directions and already carries the producer, the
    other party's number and the live/voicemail verdict for each leg. An
    inbound call back therefore lands on exactly the same key as the outbound
    dial it answers, which is what lets one row be summarised from both
    conversations.
    """
    tpath = ROOT / f"data/transcripts_{day}.json"
    tx = json.loads(tpath.read_text()) if tpath.exists() else {}
    out = {}
    for cid, v in tx.items():
        n, who = v.get("to"), v.get("producer")
        if not n or not who:
            continue
        p = ROOT / f"data/audio/{cid}.mp3"
        if p.exists() and p.stat().st_size > 500:
            out.setdefault((who, n), []).append(
                (str(p), v.get("audio_seconds") or v.get("duration") or 0,
                 v.get("class"), v.get("direction") or "outbound",
                 v.get("offset") or 0, bool(v.get("partial"))))
    for legs in out.values():
        legs.sort(key=lambda x: -x[1])
    return out


def _wanted(legs):
    """Which recordings to read for one row.

    Normally the longest leg -- head and tail of one call is all a summary
    needs. But when the prospect CALLED BACK and both halves were real
    conversations, both get read and the summary covers the pair (Frank,
    2026-08-26: "use the total of both times and summary of both calls (if
    there were 2 live conversations, the initial outbound and the lead call
    back)"). A call back to a voicemail is NOT that case -- nobody talked into
    the voicemail, so the call back alone is the conversation.
    """
    if not legs:
        return []
    live = [l for l in legs if l[2] == "live"]
    if len(live) > 1 and len({l[3] for l in live}) > 1:
        return sorted(live, key=lambda l: l[3] != "outbound")   # outbound first
    return [legs[0]]


def build(day, log=print):
    """Summarise every live contact. Rewrites data/metrics_<day>.json in place.

    Both stages cache to disk, so a re-run neither re-transcribes nor re-pays
    for the model: data/fulltx_<day>.json and data/callsum_<day>.json.
    """
    mpath = ROOT / f"data/metrics_{day}.json"
    M = json.loads(mpath.read_text())

    fx_path = ROOT / f"data/fulltx_{day}.json"
    fx = json.loads(fx_path.read_text()) if fx_path.exists() else {}
    sm_path = ROOT / f"data/callsum_{day}.json"
    sm = json.loads(sm_path.read_text()) if sm_path.exists() else {}

    legs = _audio_legs(day)
    rows = [(p, r) for p, v in M["producers"].items() for r in v["call_detail"]]
    todo = [(p, r) for p, r in rows if _ck(p, r["number"]) not in sm]
    if not todo:
        # Everything is cached. Do NOT return here: build_metrics rewrites
        # metrics_<day>.json from scratch on every run, so the summaries have
        # to be merged back in even when nothing new needs transcribing or
        # reading. Returning early is why the first cached re-run silently
        # rendered raw transcripts again.
        log(f"  call summaries: {len(rows)} already cached")

    # --- stage 1: full transcription of anything not already done ---------
    need = [(p, r) for p, r in todo
            if _ck(p, r["number"]) not in fx and legs.get((p, r["number"]))]
    if need:
        secs = sum(sum(l[1] for l in _wanted(legs[(p, r["number"])]))
                   for p, r in need)
        log(f"  full-transcribing {len(need)} live contacts ({secs // 60}m audio)...")
        for i, (p_, r) in enumerate(need, 1):
            want = _wanted(legs[(p_, r["number"])])
            try:
                parts = []
                for path, dur, cls, direction, off, partial in want:
                    t = T.transcribe_full(path, dur, offset=off) or ""
                    if not t:
                        continue
                    if len(want) > 1 or partial:
                        tag = (f"[{direction} call, {dur // 60}m{dur % 60:02d}s"
                               + (" -- ONLY THE OPENING WAS RECORDED; the call "
                                  "continued after a transfer" if partial else "")
                               + "]")
                        parts.append(f"{tag}\n{t}")
                    else:
                        parts.append(t)
                fx[_ck(p_, r["number"])] = "\n\n".join(parts)
            except Exception as e:
                fx[_ck(p_, r["number"])] = ""
                log(f"    {r['lead']}: transcription failed ({type(e).__name__})")
            if i % 5 == 0:
                log(f"    {i}/{len(need)}")
        fx_path.write_text(json.dumps(fx))

    # --- stage 2: the read ------------------------------------------------
    key = _key() if todo else ""
    model = pick_model() if key else None
    if todo and key:
        log(f"  reading {len(todo)} calls with {model}...")
    elif todo:
        log("  ANTHROPIC_API_KEY not set -- falling back to producer notes")

    for p, r in todo:
        ck = _ck(p, r["number"])
        notes = (r.get("note_producer") or "").replace("&middot;", ";").strip()
        text = fx.get(ck, "")
        ok, why = usable(text, r.get("seconds"))
        if not ok:
            sm[ck] = from_notes(notes, why if text else "no recording")
            continue
        if not key:
            sm[ck] = from_notes(notes, "no API key configured")
            continue
        try:
            d = _ask(model, text[:12000], notes, r.get("seconds") or 0,
                     p.split()[0])
            d.update(source="recording", why="")
            sm[ck] = d
        except Exception as e:
            log(f"    {r['lead']}: read failed ({type(e).__name__}) -- using notes")
            sm[ck] = from_notes(notes, "summary unavailable")

    if todo:
        sm_path.write_text(json.dumps(sm, indent=1))

    import finalize
    for p, r in rows:
        d = sm.get(_ck(p, r["number"]))
        if d:
            r["summary"] = upgrade(d)
            # Only a READ can say this -- a producer-note fallback has not
            # looked at anything. AgencyZoom missed Luis Martinez's renewal
            # entirely (no ticket, no task, an invisible customer record) and
            # the audio said it in the first thirty seconds.
            if d.get("service_call") and d.get("source") == "recording":
                finalize.flag_service(M, p, r["number"])
    finalize.apply(M)
    mpath.write_text(json.dumps(M, indent=1, default=str))
    src = sum(1 for _, r in rows if (r.get("summary") or {}).get("source") == "recording")
    log(f"  call summaries: {src} from the recording, "
        f"{len(rows) - src} from producer notes")

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
MIN_CHARS = 120           # under this there is nothing to summarise
MAX_REPEAT_RATIO = 0.35   # one word eating a third of the text is a loop
MAX_FOREIGN_SHARE = 0.25  # mostly "(speaking in foreign language)" is unusable

API_URL = "https://api.anthropic.com/v1/messages"
MODELS_URL = "https://api.anthropic.com/v1/models"
API_VERSION = "2023-06-01"
TIMEOUT = 90



def _key():
    return (os.environ.get("ANTHROPIC_API_KEY") or "").strip()


def usable(text):
    """(ok, reason) -- can this transcript support a summary?"""
    t = (text or "").strip()
    if len(t) < MIN_CHARS:
        return False, "transcript too short"
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
  "objections"  a JSON array, one entry per objection the PROSPECT raised, in \
the order they came up. Empty array if they raised none. At most 3 entries. \
Each entry is an object with exactly these keys:
      "objection"  the objection in your own words, 12 words or fewer
      "addressed"  "yes" if the producer engaged it -- gave a reason, offered \
an alternative, or asked a question to open it back up. "no" if the producer \
acknowledged it and moved on, or ignored it.
      "overcome"   "yes" if the prospect moved on that specific point, "no" if \
they held it, "unclear" if the transcript does not settle it.

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
- Never invent a name, price, coverage or date that is not in the input.
- "not interested" with no reason given IS an objection.
- Do not treat the producer's own pitch as something the prospect said."""


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
                    "overcome": oc if oc in ("yes", "no", "unclear") else "unclear"})
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
                            "overcome": oc if oc in ("yes", "no", "unclear")
                            else "no" if oc == "not overcome"
                            else "yes" if oc == "overcome" else "unclear"}]
    else:
        d["objections"] = []
    return d


def _ask(model, transcript, notes, seconds):
    body = {
        "model": model,
        "max_tokens": 600,
        "system": SYSTEM,
        "messages": [{"role": "user", "content":
                      f"Call length: {seconds} seconds\n\n"
                      f"Producer's own notes (may be empty):\n{notes or '(none)'}\n\n"
                      f"Machine transcript:\n{transcript}"}],
    }
    r = requests.post(API_URL, json=body, timeout=TIMEOUT, headers={
        "x-api-key": _key(), "anthropic-version": API_VERSION,
        "content-type": "application/json"})
    r.raise_for_status()
    text = "".join(b.get("text", "") for b in r.json().get("content", []))
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in response")
    d = json.loads(m.group(0))
    return {"summary": str(d.get("summary") or "").strip(),
            "objections": _clean_objections(d.get("objections"))}


def from_notes(notes, why):
    """No usable audio: show what the producer wrote, and say why."""
    return {"summary": (notes or "").strip(), "objections": [],
            "source": "producer note", "why": why}


def _audio_legs(day):
    """dialled number -> [(recording_path, duration)], longest leg first."""
    raw = json.loads((ROOT / f"data/rc_raw_{day}.json").read_text())
    out = {}
    for r in raw:
        n = (r.get("to") or {}).get("phoneNumber")
        if not n or not r.get("recording"):
            continue
        p = ROOT / f"data/audio/{r['id']}.mp3"
        if p.exists() and p.stat().st_size > 500:
            out.setdefault(n, []).append((str(p), r.get("duration", 0)))
    for legs in out.values():
        legs.sort(key=lambda x: -x[1])
    return out


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
    todo = [(p, r) for p, r in rows if r["number"] not in sm]
    if not todo:
        # Everything is cached. Do NOT return here: build_metrics rewrites
        # metrics_<day>.json from scratch on every run, so the summaries have
        # to be merged back in even when nothing new needs transcribing or
        # reading. Returning early is why the first cached re-run silently
        # rendered raw transcripts again.
        log(f"  call summaries: {len(rows)} already cached")

    # --- stage 1: full transcription of anything not already done ---------
    need = [(p, r) for p, r in todo
            if r["number"] not in fx and legs.get(r["number"])]
    if need:
        secs = sum(legs[r["number"]][0][1] for _, r in need)
        log(f"  full-transcribing {len(need)} live contacts ({secs // 60}m audio)...")
        for i, (_, r) in enumerate(need, 1):
            path, dur = legs[r["number"]][0]
            try:
                fx[r["number"]] = T.transcribe_full(path, dur) or ""
            except Exception as e:
                fx[r["number"]] = ""
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
        num = r["number"]
        notes = (r.get("note_producer") or "").replace("&middot;", ";").strip()
        text = fx.get(num, "")
        ok, why = usable(text)
        if not ok:
            sm[num] = from_notes(notes, why if text else "no recording")
            continue
        if not key:
            sm[num] = from_notes(notes, "no API key configured")
            continue
        try:
            d = _ask(model, text[:12000], notes, r.get("seconds") or 0)
            d.update(source="recording", why="")
            sm[num] = d
        except Exception as e:
            log(f"    {r['lead']}: read failed ({type(e).__name__}) -- using notes")
            sm[num] = from_notes(notes, "summary unavailable")

    if todo:
        sm_path.write_text(json.dumps(sm, indent=1))

    for _, r in rows:
        d = sm.get(r["number"])
        if d:
            r["summary"] = upgrade(d)
    mpath.write_text(json.dumps(M, indent=1, default=str))
    src = sum(1 for _, r in rows if (r.get("summary") or {}).get("source") == "recording")
    log(f"  call summaries: {src} from the recording, "
        f"{len(rows) - src} from producer notes")

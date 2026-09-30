"""Deepgram transcription: whole-call, bilingual, with speakers separated.

WHY (Frank, 2026-09-28: "not only have we not been able to separate the
speakers, a lot of what it transcribes is wrong"). transcribe.py's Whisper
base int8 is the second-smallest Whisper, run in 30-second windows that cut
words at every edge, tries Spanish only when English gives up on a window,
and marks a speaker change only when it happens to emit ">>". Deepgram
Nova-3 with language=multi reads the whole call in one pass, follows
English/Spanish switching inside a call, and labels each turn with a speaker.

RECORDINGS ARE MONO 8 kHz (checked 2026-09-29 on 09-28's 206), so the two
sides are separated by voice (diarize), not by channel. Speakers come back
as 0 / 1 in order of first speech -- WHICH one is the producer is not known
here and is left to the reader of the transcript.

COST. Deepgram bills per audio minute; the agency records ~226 minutes on a
day like 2026-09-28. Every response is cached per recording under
data/deepgram/<call id>.json, so a recording is paid for once however many
times the head/tail and full-call views are cut from it.

Nothing here raises into the build: any failure returns None and the caller
falls back to Whisper. DEEPGRAM_API_KEY comes from the environment or
secrets/*.env.
"""
import json
import os
import pathlib
import re
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent
CACHE = ROOT / "data/deepgram"
URL = "https://api.deepgram.com/v1/listen"
TIMEOUT = 300

PARAMS = {"model": "nova-3", "language": "multi", "diarize": "true",
          "utterances": "true", "smart_format": "true", "punctuate": "true"}

# Words the agency says on every call that a general model mishears. Sent as
# Nova-3 keyterms; if Deepgram refuses them for this language setting the
# request is simply retried without.
KEYTERMS = ["Farmers", "Farmers Insurance", "Bristol West", "Foremost",
            "Flores Insurance", "Crystal", "Lorena", "Mike", "Coral",
            "Sarahi", "Debbie", "Amanda", "Frank", "Francisco", "Veronica"]


def _key():
    k = os.environ.get("DEEPGRAM_API_KEY")
    if not k:
        try:
            import secrets_load
            secrets_load.load()
            k = os.environ.get("DEEPGRAM_API_KEY")
        except (Exception, SystemExit):
            k = None
    return k or None


def available():
    return bool(_key())


def _request(audio, key, keyterms=True):
    params = list(PARAMS.items())
    if keyterms:
        params += [("keyterm", t) for t in KEYTERMS]
    return requests.post(URL, params=params, data=audio, timeout=TIMEOUT,
                         headers={"Authorization": f"Token {key}",
                                  "Content-Type": "audio/mpeg"})


_WARNED_REFUSED = False     # raw() has said Deepgram refused the key


def raw(path, log=None, cached_only=False):
    """Deepgram's response for one recording, cached. None on any failure.
    cached_only: never send the recording -- None unless it was read before."""
    path = pathlib.Path(path)
    global _WARNED_REFUSED
    cf = CACHE / f"{path.stem}.json"
    if cf.exists():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            pass
    if cached_only:
        return None
    key = _key()
    if not key or not path.exists():
        return None
    audio = path.read_bytes()
    keyterms = True
    for attempt in range(4):
        try:
            r = _request(audio, key, keyterms)
        except requests.RequestException as e:
            if log:
                log(f"    deepgram {path.stem}: {type(e).__name__}")
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code == 400 and keyterms:
            keyterms = False               # retry once without keyterms
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code != 200:
            if log:
                log(f"    deepgram {path.stem}: HTTP {r.status_code}")
            # A refused key (401/403) fails EVERY recording, and callers
            # mostly pass no log, so the whole day used to drop to Whisper
            # without a word (2026-09-30). Said once per run.
            if r.status_code in (401, 403) and not _WARNED_REFUSED:
                _WARNED_REFUSED = True
                print(f"  WARNING: Deepgram refused the key (HTTP {r.status_code}) "
                      f"-- transcribing with Whisper instead until it is fixed")
            return None
        d = r.json()
        res = d.get("results") or {}
        keep = {"utterances": [_keep_utt(u) for u in res.get("utterances") or []],
                "languages": sorted({w.get("language") for ch in
                                     res.get("channels") or []
                                     for alt in ch.get("alternatives") or []
                                     for w in alt.get("words") or []
                                     if w.get("language")}),
                "duration": (d.get("metadata") or {}).get("duration"),
                "keyterms": keyterms}
        CACHE.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(keep))
        return keep
    return None


# A tag transcribe.NON_SPEECH already reads as "ringback or hold audio only".
SILENCE = "[silence]"


def _keep_utt(u):
    """One utterance as the cache keeps it. `w` is each word's start, one per
    word of `text` (Frank, 2026-09-30: "highlight the word its on and make it
    playable from there") -- dropped when Deepgram's words don't line up with
    the transcript word for word, so a time never lands on the wrong word.
    Reads cached before 2026-09-30 have no `w`; the board spreads their words
    across the line instead."""
    text = (u.get("transcript") or "").strip()
    out = {"start": u.get("start"), "end": u.get("end"), "speaker": u.get("speaker"), "text": text}
    words = u.get("words") or []
    if words and len(words) == len(text.split()):
        out["w"] = [round(float(w.get("start") or 0), 2) for w in words]
    return out


def _between(utts, lo, hi):
    return [u for u in utts if u["text"] and u["end"] > lo and u["start"] < hi]


def _inline(utts):
    """One line, speaker changes marked ">>" the way transcribe.DIALOGUE
    already reads them."""
    out, last = [], None
    for u in utts:
        if last is not None and u["speaker"] != last:
            out.append(">>")
        out.append(u["text"])
        last = u["speaker"]
    return " ".join(out).strip()


def head_tail(path, duration=None, offset=0, seconds=30, log=None):
    """transcribe.transcribe_file's shape: first and last `seconds` of the
    [offset, offset+duration) leg, joined by " || ". None is a failure
    (caller falls back).

    A leg with no speech at all comes back as SILENCE, not "". Whisper writes
    ringback, hold music and dead air as tags ("[Music]", "[Bell]") that
    transcribe.classify reads as no answer; Deepgram writes nothing for them,
    and classify reads "" on a 5s+ leg as a pickup that said nothing -- live.
    On 09-28 and 09-25 that turned 15 of Whisper's "[Music]" no-answers live
    (compare_stt.py, 2026-09-29). Only an empty WHOLE leg is SILENCE: speech
    anywhere between the two windows still leaves "" to mean what it did."""
    d = raw(path, log=log)
    if d is None:
        return None
    utts = d["utterances"]
    if not _between(utts, offset, offset + duration if duration else float("inf")):
        return SILENCE
    head = _inline(_between(utts, offset, offset + seconds))
    if not duration or duration <= seconds * 1.5:
        return head
    end = offset + duration
    tail = _inline(_between(utts, max(offset, end - seconds), end))
    if not tail or tail == head:
        return head
    return f"{head} || {tail}"


# How each producer's name comes back, for finding who introduced
# themselves. Only the producer's OWN name: a customer says "Hi, Crystal"
# on a call back, and Mike dials customers named Miguel.
NAME_FORMS = {"sarahi": r"sarahi|sarai|zarahi", "crystal": r"crystal|cristal"}
AGENCY = r"(farmers|la aseguranza|la seguranza|insurance)"


# The agency's own greeting on a call-in. A caller never says it, so on a
# call the service team ANSWERED (the call log names who picked up) the voice
# saying it is theirs -- Debbie answers "Thank you for calling Farmers
# Insurance" and rarely her name. Never used for the producers' calls: a
# transferred call-in's recording starts with the front desk's greeting.
ANSWER_GREETING = re.compile(
    r"thank you for calling (farmers|flores)|gracias por (llamar|su llamada)|"
    r"(farmers|flores) insurance,? (this is|how can i help)", re.I)


def producer_speaker(utts, producer, answered=False):
    """Which diarized speaker is the producer, from how they introduce
    themselves: "This is Crystal with Farmers", "Le habla Mike, de la
    aseguranza", "Soy Sarahi", "Coral, calling from Farmers". None when
    nobody does, or when two speakers score the same -- a guess would put
    the customer's words in the producer's mouth for Apollo."""
    first = (producer or "").split()[0].lower() if producer else ""
    if not first:
        return None
    name = NAME_FORMS.get(first, re.escape(first))
    intro = re.compile(
        rf"\b(this is|it'?s|my name is|soy|le habla|te habla|habla|"
        rf"me llamo|mi nombre es)\s+(me\s+|yo\s+)?({name})\b"
        rf"|\b({name})\b[,.]?\s+(with|from|de|calling from|de parte de)\s+"
        rf"(\w+\s+){{0,2}}{AGENCY}", re.I)
    agency = re.compile(rf"\b(this is|soy|le habla|te habla|calling from|"
                        rf"with|from|de parte de)\s+(\w+\s+){{0,2}}{AGENCY}", re.I)
    score = {}
    for u in utts:
        sp = u["speaker"]
        score.setdefault(sp, 0)
        score[sp] += 3 * len(intro.findall(u["text"]))
        score[sp] += len(agency.findall(u["text"]))
    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    if (not ranked or ranked[0][1] < 2 or
            (len(ranked) > 1 and ranked[1][1] == ranked[0][1])):
        if answered:
            for u in utts[:3]:
                if ANSWER_GREETING.search(u["text"]):
                    return u["speaker"]
        return None
    return ranked[0][0]


def _fold(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn").lower()


def _says_name(text, first):
    """`first` appears in `text`, allowing a transcription's or a record's
    spelling of it (Cinthya / Cynthia, Sarahi / Sarai, Brayana / Brianna,
    Merideth / Meredith): same first AND last letter, at most a letter longer
    or shorter, 70% alike. Jessica is not Jesse (Coral, 09-25: "Yes, this is
    Jessica ... I'm not able to reach him either"), and Juan is not Juana nor
    Mario Maria -- a husband and wife on one number."""
    import difflib
    first = _fold(first)
    for w in re.findall(r"[a-z]+", _fold(text)):
        if w == first or (len(first) >= 4 and w[:1] == first[:1] and
                          w[-1:] == first[-1:] and
                          abs(len(w) - len(first)) <= 1 and
                          difflib.SequenceMatcher(None, w, first).ratio() >= 0.7):
            return True
    return False


# The other voice saying the lead is not who is on the phone.
NOT_THE_LEAD = re.compile(
    r"\b(not here|isn'?t here|not home|isn'?t home|just missed (him|her)|"
    r"(he|she)'?s not (here|available|home)|wrong number|"
    r"my (husband|wife|son|daughter|mom|mother|dad|father)|"
    r"(his|her) (wife|husband|son|daughter|mom|mother|dad|father)|"
    r"no (est[aá]|se encuentra)|n[uú]mero equivocado|"
    r"(soy|es) (su|la|el) (esposa|esposo|hija|hijo|mam[aá]|pap[aá])|"
    r"yo soy su)\b", re.I)
GREETED = (r"(hi|hello|hey|hola|good (morning|afternoon|evening)|buenas tardes|"
           r"buenos d[ií]as|buenas|is this|is it|am i speaking with|"
           r"speaking with|hablo con|es|con|habla|for)")
SELF_NAMED = (r"(this is|it'?s|speaking|soy|habla|ella habla|[eé]l habla|me llamo|"
              r"my name is|mi nombre es|hablas? con)")


def lead_speaker(utts, producer_sp, lead):
    """Which diarized speaker is the lead. Only with the producer found, only
    one other voice with anything to say, and only on evidence in the call:
    the producer says the lead's first name, or the other voice gives it
    ("This is Brianna", "Speaking", "Ella habla"). A spouse, a "you just
    missed him" or a wrong number leaves them Speaker N -- Ubaldo's wife
    (Mike, 09-25) answered his phone while he was in surgery."""
    if producer_sp is None or not lead:
        return None
    first = lead.replace(",", " ").split()[0]
    if len(first) < 2:
        return None
    words = {}
    for u in utts:
        if u["speaker"] != producer_sp:
            words[u["speaker"]] = words.get(u["speaker"], "") + " " + u["text"]
    others = [sp for sp, t in words.items() if len(t.split()) >= 3]
    if len(others) != 1:
        return None
    other = others[0]
    theirs = words[other]
    if NOT_THE_LEAD.search(theirs):
        return None
    # The producer GREETING or ASKING FOR the lead by name in the opening
    # ("Hi, Harry", "Is this Carlos?", "Hablo con Maria?"). A name only
    # mentioned is the person being talked ABOUT: Coral asked Jessica about
    # "trying to get a hold of Jesse" (09-25); a parent called about their
    # son Justin's text (Crystal, 09-28).
    mine = " ".join(" ".join(u["text"] for u in utts
                             if u["speaker"] == producer_sp).split()[:40])
    greeted = any(_says_name(m.group("n"), first) for m in re.finditer(
        rf"\b{GREETED}\W+(?=(?P<n>\w+))", mine, re.I))
    head = " ".join(theirs.split()[:40])
    self_named = any(_says_name(m.group("n"), first) for m in
                     re.finditer(rf"\b{SELF_NAMED}\W+(?=(?P<n>\w+))", head, re.I))
    if (greeted or self_named
            or re.search(r"\b(speaking|ella habla|[eé]l habla)\b", head, re.I)):
        return other
    return None


_CUSTOMERS = {}


def customer_names(number):
    """First names on the AgencyZoom customer records for a phone number
    (the last ten digits, az_corpus.e164's rule), from the nightly's own
    data/az_customers_all.json -- no extra AgencyZoom read. A customer record
    is a household, so this is its primary's name; a spouse answering stays
    Speaker N unless the call shows who they are (lead_speaker's rule)."""
    if not number:
        return []
    if not _CUSTOMERS:
        idx = {}
        try:
            rows = json.loads((ROOT / "data/az_customers_all.json").read_text())
        except (OSError, ValueError):
            rows = []
        if isinstance(rows, dict):
            rows = rows.get("data") or rows.get("customers") or []
        for c in rows:
            name = (c.get("firstname") or "").strip()
            for f in ("phone", "secondaryPhone"):
                d = re.sub(r"\D", "", c.get(f) or "")[-10:]
                if len(d) == 10 and name and name not in idx.setdefault(d, []):
                    idx[d].append(name)
        _CUSTOMERS["idx"] = idx
    d = re.sub(r"\D", "", number)[-10:]
    return list(_CUSTOMERS["idx"].get(d, []))


def other_party(utts, producer_sp, lead=None, number=None):
    """(speaker, label) for the other voice: the lead by lead_speaker's rule,
    else a customer on the number's AgencyZoom records by the same rule --
    greeted or asked for by name in the opening, or giving it themselves.
    (None, None) when nothing on the call shows who it is."""
    if lead:
        sp = lead_speaker(utts, producer_sp, lead)
        if sp is not None:
            return sp, lead.replace(",", " ").split()[0].title() + " (lead)"
    for name in customer_names(number):
        sp = lead_speaker(utts, producer_sp, name)
        if sp is not None:
            return sp, name.split()[0].title() + " (customer)"
    return None, None


def turns(path, duration, offset=0, log=None, producer=None, lead=None,
          cached_only=False, number=None, role="producer", answered=False):
    """The leg as timed turns: [{"t": seconds into the recording, "who":
    label, "text"}], consecutive lines from one speaker merged -- what the
    coaching card's player seeks to (Frank, 2026-09-29: "skip to a specific
    part that I am reading"). Labels as full(); `role` names the agency's
    side ("producer", or "service" for the service team's calls);
    `answered` is a call-in the agency side is known to have picked up
    (producer_speaker's greeting rule). None on failure."""
    d = raw(path, log=log, cached_only=cached_only)
    if d is None:
        return None
    utts = _between(d["utterances"], offset,
                    offset + duration if duration else float("inf"))
    who = producer_speaker(utts, producer, answered=answered)
    first = producer.split()[0] if producer else ""
    them, their_label = other_party(utts, who, lead, number)
    out, last = [], None
    for u in utts:
        if u["speaker"] == last:
            prev = out[-1]
            prev["text"] += " " + u["text"]
            prev["e"] = round(float(u["end"] or 0), 1)
            if "w" in prev:
                if u.get("w"):
                    prev["w"] += u["w"]
                else:
                    del prev["w"]
            continue
        if who is not None and u["speaker"] == who:
            label = f"{first} ({role})"
        elif them is not None and u["speaker"] == them:
            label = their_label
        else:
            label = f"Speaker {int(u['speaker'] or 0) + 1}"
        turn = {"t": round(float(u["start"] or 0), 1), "e": round(float(u["end"] or 0), 1),
                "who": label, "text": u["text"]}
        if u.get("w"):
            turn["w"] = list(u["w"])
        out.append(turn)
        last = u["speaker"]
    return out


def stamp(t):
    """Seconds -> "m:ss", the bracketed time each full() line starts with."""
    n = int(max(0, float(t or 0)))
    return f"{n // 60}:{n % 60:02d}"


# One full() line: "[4:32] Mike (producer): ...". The time is optional -- a
# transcript saved before 2026-09-30 has none -- so nothing that reads the
# label may depend on it.
LINE = re.compile(r"^(?:\[(?P<t>\d+:\d\d)\]\s+)?(?P<who>[^:\n\[\]]{1,40}):\s?(?P<text>.*)$")


def full(path, duration, offset=0, log=None, producer=None, lead=None, number=None):
    """The whole leg, one line per turn: "[0:04] Speaker 1: ...", with the
    producer's turns labelled "<First name> (producer)" when producer_speaker
    finds them and the other voice "<First name> (lead)" or "(customer)" when
    other_party finds them. None on failure.

    Each line starts with the turn's REAL start time in brackets (Frank,
    2026-09-30): seconds into the recording, the same `t` turns() gives the
    card's player, so a time Apollo quotes is a line the player can find.
    Before this the text carried no times and Apollo guessed them. Speakers
    are still found on the utterances (producer_speaker), never on this
    text. Transcripts saved before 2026-09-30 keep their old form: a rebuild
    reuses the saved text, it never re-transcribes."""
    ts = turns(path, duration, offset=offset, log=log, producer=producer, lead=lead,
               number=number)
    if ts is None:
        return None
    return "\n".join(f"[{stamp(x['t'])}] {x['who']}: {x['text']}" for x in ts).strip()

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


def raw(path, log=None):
    """Deepgram's response for one recording, cached. None on any failure."""
    path = pathlib.Path(path)
    cf = CACHE / f"{path.stem}.json"
    if cf.exists():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            pass
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
            return None
        d = r.json()
        res = d.get("results") or {}
        keep = {"utterances": [
                    {"start": u.get("start"), "end": u.get("end"),
                     "speaker": u.get("speaker"),
                     "text": (u.get("transcript") or "").strip()}
                    for u in res.get("utterances") or []],
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
    [offset, offset+duration) leg, joined by " || ". "" is silence; None is
    a failure (caller falls back)."""
    d = raw(path, log=log)
    if d is None:
        return None
    utts = d["utterances"]
    head = _inline(_between(utts, offset, offset + seconds))
    if not duration or duration <= seconds * 1.5:
        return head
    end = offset + duration
    tail = _inline(_between(utts, max(offset, end - seconds), end))
    if not tail or tail == head:
        return head
    return f"{head} || {tail}"


def full(path, duration, offset=0, log=None):
    """The whole leg, one line per turn: "Speaker 1: ...". None on failure."""
    d = raw(path, log=log)
    if d is None:
        return None
    utts = _between(d["utterances"], offset,
                    offset + duration if duration else float("inf"))
    lines, last = [], None
    for u in utts:
        if u["speaker"] == last:
            lines[-1] += " " + u["text"]
        else:
            lines.append(f"Speaker {int(u['speaker'] or 0) + 1}: {u['text']}")
            last = u["speaker"]
    return "\n".join(lines).strip()

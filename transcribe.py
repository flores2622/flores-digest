"""Transcribe a day's call recordings and classify what actually happened.

WHY THIS EXISTS. Duration cannot tell a conversation from a voicemail, in
either direction. Measured on 2026-08-13 recordings:

    2.2s  "I'm sorry, the person you were trying to reach has a..."   carrier msg
   71.0s  "Hi, if you record your name and reason for calling..."     voicemail
   77.0s  "Telephone number 7 6 0 ... can't take your call now."      voicemail
   50.0s  "Your call has been forwarded to an automated voice..."     voicemail

A 3-second pickup-and-hangup is a live contact; a 77-second voicemail greeting
is not. Only the audio settles it.

MODEL. sherpa-onnx running Whisper base int8 on CPU. The weights come from the
k2-fsa GitHub release, because huggingface.co is refused by the sandbox gateway
(403 policy denial) while GitHub release assets are reachable.

RATE LIMIT. RingCentral media downloads are throttled hard and answer
CMN-301 "Request rate exceeded" with HTTP 200 and a 161-byte JSON body -- so a
naive fetch silently writes 135 tiny files that look like MP3s and are not.
Always check the payload, never the status code.
"""
import json
import os
import re
import subprocess
import time
import wave

import numpy as np
import requests

MODEL = "models/sherpa-onnx-whisper-base"
AUDIO = "data/audio"
RATE_LIMIT_MARKER = b"CMN-301"

# Machine-answered: carrier messages and voicemail greetings.
MACHINE = re.compile(
    # Carrier and handset greetings.
    # Contractions matter: Whisper renders this as "you're" as often as "you
    # are", and the strict form silently lost the match when a neighbouring
    # cue ("been forwarded") transcribed differently (Reyna Eskenazi, 08-17).
    r"person you.{0,6}trying to reach|forwarded to voice"
    r"|voice ?mail|voice messaging"
    r"|mailbox|at the (tone|beep)|after the (tone|beep)|record your (name|message)"
    r"|leave (your|a|me a) (name|message|brief message|short message)"
    r"|please leave|you have reached|has not been set up|is not available"
    r"|we are not available|can'?t take your call|can'?t come to my phone"
    r"|if i'?m not answering|i'?m sorry (that )?i missed your call"
    r"|missed your call|return your call|i'?ll (get )?back to you"
    r"|no longer in service|has been disconnected|please try your call again"
    r"|been forwarded|automated|call assistant|press \d|more options"
    # Real phrasings seen on 2026-08-17 that the list above walked straight
    # past: a garbled "you have reached", "can't answer the phone right now",
    # and the producer opening a message with "this message is for X".
    r"|you'? ?(have )?reached|can'?t answer (the|my) phone|not able to (take|answer)"
    r"|this message is for|leave your name and (number|phone)"
    # Spanish equivalents.
    r"|para espa|deje su mensaje|no est[aá] disponible|buz[oó]n|despu[eé]s del tono"
    r"|no (puedo|voy a?) contestar|deja(te)? (tu )?(nombre|n[uú]mero|mensaje)"
    r"|deje su (nombre|n[uú]mero)|no se encuentra|vuelva a llamar"
    # Whisper garbles "deja tu mensaje" into "de la tu mensaje" often enough
    # that the verb cannot be relied on (Carlos Bautista, 08-17).
    r"|\b(tu|su) mensaje\b|al tel[eé]fono.{0,20}mensaje"
    # The producer leaving a message is itself proof nobody answered.
    r"|at your earliest convenience|my direct line|give me a call or text"
    # The agency's voicemail script -- but ONLY the closing lines, which are
    # addressed to someone who is NOT on the phone. The body of the script
    # ("the insurance information you had requested", "no obligation") is said
    # to live prospects word for word: matching it flipped Lorna Lawrence, a
    # real conversation containing "Hi, is this Mourna? Yes, it is."
    r"|please give me a call|give me a call back|call me back at"
    r"|feel free to (call|reach|text) (me|us)"
    # Auto-attendants and carrier number read-backs.
    r"|thank you for calling|telephone number \\d|^telephone number",
    re.I)

# Ringback, hold music and empty captures are not conversations. Whisper also
# emits bare bracketed tags -- [no audio], [COUGH], [BLANK_AUDIO] -- which the
# old pattern missed, so they fell through to the "speech means live" default
# and scored as contacts (Cheryle Ro, Linda Bolgos, 2026-08-17).
NON_SPEECH = re.compile(
    r"^\W*(\(|\[)?\s*(music|dramatic music|inaudible|silence|no audio|"
    r"blank_?audio|cough|coughing|noise|background noise|beep|sighs?|breathing)"
    r"\s*(\)|\])?\W*$", re.I)

# A human answering.
HUMAN = re.compile(
    r"\bhello\b|\bhi\b|\bbueno\b|\bal[oó]\b|\bdiga\b|speaking|this is \w+"
    r"|who'?s this|how can i help|good (morning|afternoon|evening)",
    re.I)


def download(recs, token, per_minute=10, log=print):
    """Fetch recordings, honouring the throttle. Returns {call_id: path}."""
    os.makedirs(AUDIO, exist_ok=True)
    gap = 60.0 / per_minute
    out, last = {}, 0.0
    for i, r in enumerate(recs):
        p = f"{AUDIO}/{r['id']}.mp3"
        if os.path.exists(p) and os.path.getsize(p) > 500:
            out[r["id"]] = p
            continue
        for attempt in range(5):
            wait = gap - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            resp = requests.get(r["recording"]["contentUri"],
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=90)
            last = time.time()
            body = resp.content
            if resp.status_code == 200 and RATE_LIMIT_MARKER not in body[:300]:
                open(p, "wb").write(body)
                out[r["id"]] = p
                break
            time.sleep(gap * (attempt + 1))      # backoff and retry
        if (i + 1) % 20 == 0:
            log(f"  {i + 1}/{len(recs)} fetched")
    return out


_rec = {}

# Whisper emits this when it hears speech it will not transcribe in English.
# Untreated it is worse than useless: the word "speaking" matches the HUMAN
# pattern, so every untranscribable Spanish call scored as a live contact.
FOREIGN = re.compile(r"speaking in (a )?foreign language|\[foreign\]", re.I)


def _model(language=None, threads=2):
    """Whisper base is multilingual; the language is simply never passed."""
    key = language or "auto"
    if key not in _rec:
        import sherpa_onnx
        kw = {"language": language, "task": "transcribe"} if language else {}
        _rec[key] = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=f"{MODEL}/base-encoder.int8.onnx",
            decoder=f"{MODEL}/base-decoder.int8.onnx",
            tokens=f"{MODEL}/base-tokens.txt", num_threads=threads, **kw)
    return _rec[key]


def _window(path, start, seconds, language=None):
    """Transcribe one [start, start+seconds) window of a recording."""
    wav_path = path.replace(".mp3", ".wav")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "quiet",
                        "-ss", str(int(start)), "-t", str(int(seconds)),
                        "-i", path, "-ar", "16000", "-ac", "1", wav_path])
    if r.returncode or not os.path.exists(wav_path):
        return None
    with wave.open(wav_path) as w:
        a = (np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
             .astype(np.float32) / 32768)
    if len(a) < 1600:                      # under 0.1s of audio
        return ""
    m = _model(language)
    s = m.create_stream()
    s.accept_waveform(16000, a)
    m.decode_stream(s)
    return s.result.text.strip()


def transcribe_file(path, seconds=30, duration=None):
    """Both ENDS of the call, not just the opening.

    The machine greeting that proves a voicemail is always at the start; what
    actually happened is at the end. Judged on the tail alone a voicemail reads
    as live, because the tail is the producer delivering their pitch into it
    (Robert Valenzuela, 2026-08-17). So take the first window and the last, and
    classify on both.

    A window that comes back as Whisper's foreign-language placeholder is
    retried in Spanish, which is the only other language on this book.
    """
    def one(start):
        t = _window(path, start, seconds)
        if t and FOREIGN.search(t):
            es = _window(path, start, seconds, language="es")
            if es and not FOREIGN.search(es):
                return es
        return t

    head = one(0)
    if head is None:
        return None
    if not duration or duration <= seconds * 1.5:
        return head
    tail = one(max(0, duration - seconds))
    if not tail or tail == head:
        return head
    return f"{head} || {tail}"


def classify(text, duration):
    """('live'|'voicemail'|'no answer'|'unknown', why)."""
    if text is None:
        return "unknown", "recording unreadable"
    t = text.strip()
    if not t:
        # Silence with real connect time is a pickup that said nothing;
        # silence on a very short leg is a ring-out.
        return ("live", "connected, no speech captured") if duration >= 5 \
            else ("no answer", "no audio")
    if NON_SPEECH.match(t):
        return "no answer", "ringback or hold audio only"
    # "Hello? Hello? Hello?" and nothing else is the producer talking into dead
    # air, not a contact (Estella Ojeda, 08-17).
    if re.fullmatch(r"(\W*(hello|hola|bueno|hi)\W*){2,}", t, re.I):
        return "no answer", "repeated greeting, no reply"
    # A window that is nothing but the foreign-language placeholder means the
    # Spanish retry also failed. There is speech, but nothing that says whether
    # it was a person or a greeting -- do NOT let "speaking" score it as live.
    stripped = FOREIGN.sub(" ", t).strip(" -|.")
    if not stripped:
        return "unknown", "speech present, not transcribable"
    t = stripped
    # Machine phrases are checked BEFORE human ones: a voicemail transcript
    # usually contains the producer's own greeting too ("Hi, this is Crystal
    # with Farmers..."), and matching that first labelled voicemails as live.
    if MACHINE.search(t):
        return "voicemail", "machine greeting in transcript"
    if HUMAN.search(t):
        return "live", "human greeting in transcript"
    # Speech that is neither a known machine phrase nor a greeting is a person
    # talking -- e.g. a pickup mid-sentence, or a hang-up after two words.
    return "live", "speech in transcript"


def run(day, recs, token, log=print):
    log(f"downloading {len(recs)} recordings (throttled)...")
    paths = download(recs, token, log=log)
    log(f"got {len(paths)}; transcribing...")
    out = {}
    for cid, p in paths.items():
        txt = transcribe_file(p)
        out[cid] = {"text": txt}
    json.dump(out, open(f"data/transcripts_{day}.json", "w"))
    return out

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
    r"|thank you for calling|telephone number \\d|^telephone number"
    # SCREENERS / answering services (Albert Collier, 2026-08-18). Two dials
    # 24s apart recorded the same message; Whisper wrote "To record your name"
    # on one and "He records your name" on the other, and the strict
    # "record your name" matched only the first. The second fell through to the
    # live default. Tolerate the verb inflection and match the rest of the
    # script, which is stable even when the opening verb is not.
    r"|records? your (name|message)|record (your|the) (name|reason)"
    r"|(see|check) if (this|that) person is (available|there)"
    r"|(review|see) this person available"
    r"|(please )?stay on the line|hold while i (try|connect|transfer)"
    r"|screening (this|your) call|who may i say is calling"
    # Whisper mangles "leave your name" into "leave your man" / "really your
    # name" often enough that the noun cannot carry the match alone.
    r"|leave your (name|man|number|brief)|your name,? (and )?(phone )?number,? "
    r"(and )?(a )?brief"
    # Truncated carrier messages: the 30s window regularly clips these mid
    # sentence, and requiring the final word lost the match entirely.
    r"|person you.{0,6}(were |are )?trying to|your call has been forward"
    r"|i'?m sorry[,.]? (you|the person|this)"
    r"|check(ing)? my (voice ?)?messages?|send me a text"
    # Spanish screener / voicemail phrasings.
    r"|d[ée]je(se|nos|me)? un mensaje|deje un mensaje|un mensaje para"
    r"|no est[aá] (disponible|en este momento)|le comunico",
    re.I)

# Ringback, hold music and empty captures are not conversations. Whisper also
# emits bare bracketed tags -- [no audio], [COUGH], [BLANK_AUDIO] -- which the
# old pattern missed, so they fell through to the "speech means live" default
# and scored as contacts (Cheryle Ro, Linda Bolgos, 2026-08-17).
NON_SPEECH = re.compile(
    r"^\W*(\(|\[)?\s*(music|dramatic music|inaudible|silence|no audio|"
    r"blank_?audio|cough|coughing|noise|background noise|beep|sighs?|breathing)"
    r"\s*(\)|\])?\W*$", re.I)

# Whisper invents new non-speech tags faster than a whitelist can track them:
# "[Band Warms Up]" on three seconds of silence scored as a live contact
# (Arlinda Dos Santos, 2026-08-18), and the 30s window truncates them mid-tag
# ("[Band War"), so the closing bracket cannot be relied on either. Any window
# that is NOTHING but bracketed or parenthesised tags is non-speech, whatever
# the tag happens to say. Real speech is not written inside brackets.
BRACKET_TAG = re.compile(r"[\[(][^\])]*(?:[\])]|$)")


def is_only_tags(t):
    """True when the transcript is bracketed tags and separators only."""
    if not t:
        return False
    return not BRACKET_TAG.sub(" ", t).strip(" -|.,?!")


# The producer talking and nobody talking back. A window whose only content is
# the producer identifying themselves -- "Crystal with Farmers", "habla Mike de
# la Seguranza Farmers" -- with dead air on the other window is a message being
# left, not a contact (Maria Rodriguez, 2026-08-18).
SELF_ID = re.compile(
    r"\b(this is |habla |soy |le habla )?\w+ (with|de la|from) "
    r"(farmers?|f[aá]rmios|seguran[czs]a|partners? insurance|farmer)"
    r"|\b(crystal|lorena|mike|frank|coral|sarahi|debbie) with farmer",
    re.I)

# Two people alternating. Whisper marks speaker changes with ">>" when it hears
# them, and a closing exchange ("okay ... that's okay ... bye-bye") only occurs
# when someone is on the other end. This is what keeps a genuine pickup with no
# greeting from being discarded (Aracely Meza Tapia, 2026-08-18).
DIALOGUE = re.compile(
    r">>|\bbye[- ]?bye\b|\bthat'?s ok(ay)?\b|\bno problem\b"
    r"|\bcall (you|me) back\b|\bh[aá]blame\b|\bhasta luego\b"
    r"|\bnice (talking|speaking) (to|with) you\b",
    re.I)

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
    if NON_SPEECH.match(t) or is_only_tags(t):
        return "no answer", "ringback or hold audio only"
    # "Hello? Hello? Hello?" and nothing else is the producer talking into dead
    # air, not a contact (Estella Ojeda, 08-17).
    # NOTE (unattended run, 2026-08-24): the original pattern was
    # r"(\W*(hello|hola|bueno|hi)\W*){2,}" -- the \W* on BOTH sides of the
    # inner group makes every partition of the separators a distinct path, so a
    # Whisper repetition-loop transcript ("Hello? " x300) that does not fully
    # match backtracks exponentially and never returns. It hung the 08-24 build
    # for 50 minutes on one call. The form below matches the same language
    # (verified equal on 66,666 generated strings) in linear time.
    if re.fullmatch(r"(?:\W*(?:hello|hola|bueno|hi)){2,}\W*", t, re.I):
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
    # The producer identifying themselves with dead air on the other window is
    # a message being left. Checked before HUMAN because "this is Crystal with
    # Farmers" trips the greeting test on its own.
    halves = [h.strip() for h in t.split("||")]
    if SELF_ID.search(t) and any(is_only_tags(h) or not h for h in halves):
        return "voicemail", "producer speaking into dead air"
    if HUMAN.search(t):
        return "live", "human greeting in transcript"
    # A two-party exchange with no greeting -- a pickup mid-sentence, or a
    # hang-up after two words -- is still a contact.
    if DIALOGUE.search(t):
        return "live", "two-party exchange in transcript"
    # ANYTHING ELSE IS NOT A CONTACT. This used to return "live" on the
    # reasoning that speech means a person; in practice it was the single
    # biggest source of false contacts. On 2026-08-18 it produced 18 of the 42
    # live calls and only one of the 18 was real -- a screener, three
    # silences, two voicemails and a Spanish machine greeting among them
    # (Frank, 2026-08-18). We now claim a contact only on positive evidence:
    # a human greeting, a two-party exchange, or the producer's own note.
    #
    # "unclear" is deliberately NOT "unknown". Unknown means we could not read
    # the audio, so is_live() may fall back to duration. Unclear means we read
    # it and found no sign of a person, and duration must not override that.
    return "unclear", "speech present, no contact evidence"


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

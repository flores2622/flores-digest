# HANDOFF 9 — 2026-08-19

One fix, from Frank's review of the 2026-08-18 Call Detail. **Nothing was
re-emailed.** The 08-18 digest that reached the ops and staff lists at 18:34 MST
is the *old* build and its contact rate (12.4%) is overstated. The corrected
figure for that day is **9.6%**. This code takes effect on the next run.

---

## The leak: `classify()` defaulted to "live"

`transcribe.py::classify()` ended with

```python
# Speech that is neither a known machine phrase nor a greeting is a person
# talking -- e.g. a pickup mid-sentence, or a hang-up after two words.
return "live", "speech in transcript"
```

Fail-open. Every transcript the machine and human patterns both missed became a
live contact. On 08-18 that catch-all produced **18 of the 42 live calls, and
exactly one of the 18 was real.**

Frank caught three of them by eye:

**Maria Rodriguez** — one 53s dial. Head window `"Crystal with farmers?"`, tail
window `"[BLANK_AUDIO]"`. The carrier greeting never transcribed, so there was no
machine phrase to match; "Crystal with farmers?" is not a greeting either. The
producer's own voice followed by dead air is the signature of a voicemail and
there was no rule for it.

**Albert Collier** — two dials 24 seconds apart, the same answering service both
times:

| dial | transcript | old verdict |
|---|---|---|
| 21s | "**To record your name** and reason for calling…" | voicemail ✓ |
| 29s | "**He records your name** and reason for calling…" | live ✗ |

`record your (name|message)` needed the literal string. One letter of Whisper
drift and the match failed. The row then showed 50s — both dials summed — so it
read as one long conversation.

**Arlinda Dos Santos** — three dials in 38 seconds, all silence:

| dial | transcript | old verdict |
|---|---|---|
| 14s | `[BLANK_AUDIO]` | no answer ✓ |
| 16s | `[Music]` | no answer ✓ |
| 17s | `[Band Warms Up]` | live ✗ |

`NON_SPEECH` is a hardcoded whitelist. Whisper invents non-speech tags faster
than a whitelist tracks them.

---

## Changes

**`transcribe.py`**

1. **`classify()` no longer defaults to live.** New terminal class `"unclear"`
   — we read the audio and found no sign of a second person. Deliberately *not*
   `"unknown"`, which means the audio was unreadable and where the duration
   fallback still applies.
2. **`is_only_tags()` / `BRACKET_TAG`** — any window that is nothing but
   bracketed or parenthesised tags is non-speech, whatever the tag says. Handles
   `[Band Warms Up]` and the truncated `[Band War` the 30s window produces. Real
   speech is not written inside brackets.
3. **`SELF_ID`** — producer identifying themselves with dead air on the other
   window is a message being left. Checked *before* `HUMAN`, because "this is
   Crystal with Farmers" trips the greeting test on its own.
4. **`DIALOGUE`** — two-party markers (`>>`, "bye-bye", "that's okay", "no
   problem", "call you back"). This is what keeps a genuine pickup with no
   greeting from being discarded; it is the only thing standing between Aracely
   Meza Tapia and the bin.
5. **`MACHINE` widened** — screener scripts ("records/record your name", "see if
   this person is available", "stay on the line", "who may I say is calling"),
   Whisper's manglings of "leave your name" ("leave your **man**", "**really**
   your name, number, brief message"), truncated carrier messages ("person you
   were trying to…", "your call has been forward"), and Spanish screener
   phrasings ("déjese un mensaje", "un mensaje para").

**`live_contact.py::is_live()`** — `"unclear"` returns `False, "recording (no
contact evidence)"`. It must not fall through to the duration rule: a 53-second
voicemail is 53 seconds long.

**`daily.py`** — multi-dial aggregation now ranks by strength of evidence
(`live > voicemail > no answer > unclear > unknown`) instead of last-write-wins.
A real pickup on any dial still means the number was reached; a confident
machine greeting can no longer be overwritten by a later window that merely
failed to find evidence.

**`build_attachments.py`** — methodology paragraph reports the `unclear` count.

---

## Verified against 08-18's cached transcripts

19 of 174 classifications changed. **All 19 are downgrades of false positives;
no genuine conversation was lost.**

| | before | after |
|---|---|---|
| live | 42 | 23 |
| voicemail | 122 | 131 |
| no answer | 10 | 14 |
| unclear | — | 6 |

Counted team contacts:

| producer | live was | live now | rate was | rate now |
|---|---|---|---|---|
| Crystal Mango | 7 | **3** | 12.5% | **5.4%** |
| Lorena Gonzalez | 6 | 6 | 9.4% | 9.4% |
| Mike Olvera | 9 | **8** | 15.8% | **14.0%** |
| **team** | **22** | **17** | **12.4%** | **9.6%** |

Dropped: Maria Rodriguez, Albert Collier, Arlinda Dos Santos, Nichols Lock &
Safe (Crystal); Griselda Alvarado (Mike — Spanish voicemail greeting,
"Por favor, déjese un mensaje para Griselda"). Retained: Aracely Meza Tapia,
an 18-second real exchange with no greeting, held by `DIALOGUE`.

---

## Worth knowing

**Every row logged from a producer note was correct.** All five errors were on
rows scored from the recording alone (`basis=recording`). Mary Heffner's
recording classified as *voicemail*, but Lorena's note — "Mary advised she was
not looking for insurance at this time" — proves a real conversation, and the
note-first ordering from HANDOFF 8 rescued it. That ordering is doing real work;
leave it alone.

**The direction of this fix is down.** The 08-13 note stands — most dials
genuinely reach voicemail, and a low contact rate is not a bug to be fixed. This
change makes the number lower, not higher, by requiring positive evidence before
claiming a contact: a human greeting, a two-party exchange, or the producer's
own note.

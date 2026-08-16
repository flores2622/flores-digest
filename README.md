# Flores Insurance — Daily Sales Digest

Builds and sends the daily operations and staff reports from live data:
RingCentral (calls + recordings), AgencyZoom (leads, tasks, quotes, policies),
Insightful (utilization) and Coach AI (call quality).

## Run

    pip install -r requirements.txt
    python3 daily.py --audience ops       # TODAY, Arizona (ops fires 6:30 PM)
    python3 daily.py --audience staff     # YESTERDAY (staff fires 8:00 AM)
    python3 daily.py --day 2026-08-13 --no-send

**The reporting day is the day the ops email is sent.** Ops goes out at 6:30 PM
Arizona and reports the day that is ending — that is why the send moved to 6:30
and why utilization comes from the Insightful API rather than its next-morning
email. The staff email at 8:00 AM necessarily carries the previous day.

A cold run takes 25–30 minutes. The RingCentral recording download is throttled
to ~12/minute and dominates. Everything caches to `data/`, so a re-run after a
failure resumes rather than restarting.

## Secrets

Create `secrets/*.env` with, between them:

    RC_CLIENT_ID / RC_CLIENT_SECRET / RC_SERVER_URL / RC_JWT
    AZ_USERNAME / AZ_PASSWORD
    INSIGHTFUL_TOKEN
    RESEND_API_KEY

`chmod 600`. Never commit them — `.gitignore` covers `secrets/`.

## Coach AI

Per-user call-quality figures live only in the Coach AI emails, and only in
their HTML part — the plaintext table is empty. A script cannot read the
mailbox, so the caller writes them first:

    data/coach_<day>.json
    {"Crystal Mango": {"calls": 31, "score": 66, "sentiment": 16, "roleplay": 0}, ...}

**Coach AI titles each email with the UTC date at generation, one day ahead of
the Arizona day it describes.** For Arizona Aug 13, read the emails titled
"Aug 14". Verified repeatedly — do not relitigate.

If the file is absent the run still completes, with zeros in that panel.

## What decides a live contact

The call recording, not duration. Every recorded producer call is transcribed
(Whisper base via sherpa-onnx, weights from the k2-fsa GitHub release because
huggingface.co is blocked) and classified as conversation, voicemail or
no-answer from what was actually said. A two-second pickup counts; a 77-second
voicemail greeting does not. Where there is no recording, the producer's own
AgencyZoom note decides, and an explicit "never answered" outranks everything.

## Things that will bite you

- **AgencyZoom pagination**: pages are zero-indexed and `pageSize` caps at 100.
  Both violations return HTTP 400, not an empty list.
- **RingCentral media**: throttled, and answers `CMN-301` with HTTP **200** and
  a 161-byte JSON body. Check the payload, never the status code.
- **Quoted-printable**: lead links are `?id=86771961`, and `=86` is a QP escape.
  Attachments go as PDF and the body runs through `qp_safe()` for this reason.
- **Div balance**: every panel swap is guarded by `assert_div_balance`. One
  stray `</div>` closes the panel and its column early and destroys every panel
  below it.
- **BOB**: a policy whose lead source is BOB is not a sale.

"""Send a built report via Resend.

Cloudflare fronts api.resend.com and rejects Python's default user-agent with
error 1010 -- an explicit User-Agent header is REQUIRED, not optional
(HANDOFF_4 s3).

Gmail clips HTML bodies at ~102,400 bytes and replaces the tail with
"[Message clipped]", silently losing whole panels. This refuses to send at or
over the threshold rather than delivering a truncated report.
"""
import base64
import sys

import requests

import digest_config as cfg
from secrets_load import load

API = "https://api.resend.com/emails"
UA = "FloresDigest/1.0 (+frank@floresinsuranceagency.com)"


def send(subject, html, to, attachments=(), sender=None, binary=False):
    size = len(html.encode())
    if size >= cfg.GMAIL_CLIP_BYTES:
        raise SystemExit(
            f"REFUSING TO SEND: body is {size:,} bytes, at or over Gmail's "
            f"{cfg.GMAIL_CLIP_BYTES:,}-byte clip threshold. Shrink the inline "
            f"recontact list (3 -> 2 -> 1 -> 0 per group) or run minify first.")

    key = load("RESEND_API_KEY")["RESEND_API_KEY"]
    payload = {
        "from": f"Daily Sales Digest <{sender or cfg.SENDER}>",
        "to": list(to),
        "subject": subject,
        "html": html,
    }
    if attachments:
        # content_type is REQUIRED in practice, not optional. Without it Resend
        # sends the part as application/octet-stream; Gmail then refuses to
        # preview the file and hands over a download that opens as raw source
        # or mojibake. Both attachments arrived "unreadable" on TEST 9 for
        # exactly this reason. charset=utf-8 matters too -- these files carry
        # em dashes and curly quotes.
        payload["attachments"] = [
            {"filename": name,
             "content": base64.b64encode(
                 content if isinstance(content, bytes) else content.encode("utf-8")
             ).decode(),
             "content_type": ("application/pdf" if name.lower().endswith(".pdf")
                              else "text/html; charset=utf-8")}
            for name, content in attachments
        ]

    r = requests.post(API, json=payload, timeout=60, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": UA,          # without this, Cloudflare returns error 1010
    })
    if r.status_code >= 300:
        raise SystemExit(f"Resend {r.status_code}: {r.text[:400]}")
    return r.json()


if __name__ == "__main__":
    path, subject = sys.argv[1], sys.argv[2]
    to = sys.argv[3:] or ["frank@floresinsuranceagency.com"]
    body = open(path).read()
    res = send(subject, body, to)
    print(f"sent {len(body.encode()):,} bytes to {', '.join(to)} -> {res}")

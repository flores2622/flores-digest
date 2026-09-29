"""Tell a check-in service how the nightly run went (Frank, 2026-09-29).

A broken night was only ever noticed after the fact -- ffmpeg missing on
09-10 and 09-17, the API key read as empty on 09-22. With HEALTHCHECK_URL
set (a Healthchecks.io check's ping URL, in the cloud environment's
variables), daily.py pings it when the nightly run starts, when it ends and
when it fails, and the service emails/texts Frank if the success ping has not
arrived by the check's schedule plus its grace time -- which also catches a
run that never started or hung. Unset, this does nothing.

Pings are best-effort: a ping that fails never touches the run.
"""
import os

import requests


def ping(kind="", message=""):
    """kind: "start", "fail", or "" for success. `message` rides along as the
    ping body (shown in the check's log), clipped to 10 KB."""
    url = (os.environ.get("HEALTHCHECK_URL") or "").strip().rstrip("/")
    if not url:
        return
    try:
        requests.post(f"{url}/{kind}" if kind else url,
                      data=str(message or "")[-10000:].encode(), timeout=10)
    except Exception:
        pass

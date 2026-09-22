"""Load secrets from ~/flores/secrets/*.env without ever printing them."""
import os
import pathlib

SECRETS_DIR = pathlib.Path(__file__).resolve().parent / "secrets"


def load(*names):
    """Read every .env in secrets/ into os.environ. Returns dict of requested names.

    A blank/placeholder value already sitting in the environment is treated
    as not set, not as an intentional override -- `os.environ.setdefault`
    used to skip loading the real value the moment ANYTHING was already
    bound to the name, blank or not. Found 2026-09-22: every checkpoint
    that day read ANTHROPIC_API_KEY as empty and fell back to producer
    notes all day (0 of 17 live contacts got a real read), while
    secrets/all.env's own key was confirmed valid the whole time -- some
    upstream provisioning step was pre-binding the name to "" before this
    ever ran, and setdefault let that stick for the rest of the process.
    """
    for f in sorted(SECRETS_DIR.glob("*.env")):
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if not os.environ.get(k):
                os.environ[k] = v.strip()
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise SystemExit(f"missing secret(s): {', '.join(missing)}")
    return {n: os.environ[n] for n in names}


def redact(s):
    """Safe display form for a secret."""
    if not s:
        return "<empty>"
    return f"{s[:4]}…{s[-3:]} (len {len(s)})"

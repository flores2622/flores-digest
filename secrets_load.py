"""Load secrets from ~/flores/secrets/*.env without ever printing them."""
import os
import pathlib

SECRETS_DIR = pathlib.Path(__file__).resolve().parent / "secrets"


def load(*names):
    """Read every .env in secrets/ into os.environ. Returns dict of requested names."""
    for f in sorted(SECRETS_DIR.glob("*.env")):
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise SystemExit(f"missing secret(s): {', '.join(missing)}")
    return {n: os.environ[n] for n in names}


def redact(s):
    """Safe display form for a secret."""
    if not s:
        return "<empty>"
    return f"{s[:4]}…{s[-3:]} (len {len(s)})"

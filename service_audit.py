"""Each completed service SR read against Amanda's Service Playbook
(service_playbook.py; Frank, 2026-09-28: "Teach Athena this").

One model read per SR, from its subject, description and the rep's closing
note, answers four things the board needs for each role:

  type      the request, in the playbook's own "Who handles what" table
            (REQUEST_TYPES) -- so the Service Lead's routine work can be
            told from her complex work ("not the default person for every
            service request")
  missing   the parts of the note standard the note leaves out (Who, What,
            Why, Outcome, Next step)
  opp       a sales opportunity in the conversation: "passed" (the note
            says it went to a producer, or a lead was made), "missed" (one
            came up -- a new vehicle, a home purchase -- and the note does not
            say it was passed), or "none"
  escalated the note says it went to the Service Lead or Frank

COST. The third paid read, beside the renewal and service-outcome notes:
one call per BATCH SRs, each SR read once and kept by SR id and note text
(data/service_audit_reads.json + an R2 copy), so only an edited note is read
again. Never delete the cache casually.
"""
import hashlib
import json
import pathlib
import re

import service_playbook as pb

ROOT = pathlib.Path(__file__).resolve().parent
CACHE_FILE = ROOT / "data/service_audit_reads.json"
CACHE_R2_KEY = "cache/service_audit_reads.json"
BATCH = 20
OPP = ("passed", "missed", "none")

SYSTEM = pb.prompt_block() + """

You audit the service requests (SRs) this agency's service team completed.
Each item is one SR: its subject, the client's request, and the rep's closing
note. For EACH item answer:
  type       one of the request types above -- what the client needed
  missing    the note-standard parts the rep's note leaves out, from
             [who, what, why, outcome, next_step]. A resolved request needs no
             separate next step ("no changes made", "sent ID cards" is
             complete). A renewal the rep reviewed without contacting the
             client ("low increase, review if needed") answers who (no one was
             contacted) and why (the stated reason). An empty note is missing
             all five. Judge the NOTE, not the subject line.
  opp        "passed" if the note says a sales opportunity was acted on --
             passed to a producer, a lead made, or quoted by the rep (some reps
             sell); "missed" if the conversation shows one (a new vehicle, a
             home purchase, a new driver, asking about other coverage) and the
             note does not say it was acted on; else "none"
  escalated  true if the note says it went to the Service Lead, a producer or
             Frank for a decision

Return ONLY a JSON object mapping each id to
{"type": "...", "missing": [...], "opp": "...", "escalated": false}."""


def _h(text):
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def load(log=print):
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=CACHE_R2_KEY)["Body"].read()
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_bytes(body)
        return json.loads(body)
    except Exception:
        return {}


def save(cache, log=print):
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))
    try:
        import publish_board
        cli, bucket = publish_board._client()
        cli.put_object(Bucket=bucket, Key=CACHE_R2_KEY, Body=CACHE_FILE.read_bytes(),
                       ContentType="application/json")
    except Exception as e:
        log(f"  service audit: R2 copy not saved ({type(e).__name__})")


def _item(t):
    subj = (t.get("subject") or "").strip()
    desc = clean(t.get("serviceDesc"))[:600]
    note = clean(t.get("resolutionDesc"))[:1200]
    return f"Subject: {subj}\nRequest: {desc or '(none)'}\nRep's note: {note or '(no note)'}"


def _valid(v):
    if not isinstance(v, dict):
        return None
    typ = v.get("type") if v.get("type") in pb.REQUEST_TYPES else "other"
    miss = [m for m in (v.get("missing") or []) if m in pb.NOTE_PARTS]
    opp = v.get("opp") if v.get("opp") in OPP else "none"
    return {"type": typ, "missing": miss, "opp": opp, "escalated": bool(v.get("escalated"))}


def read(srs, log=print):
    """{sr id: audit} for these completed SRs, reading only those not read
    before. An SR missing from the result could not be read this time (retried
    next night) -- never raises."""
    cache = load(log=log)
    want = {}
    for t in srs:
        sid, item = str(t.get("id")), _item(t)
        hit = cache.get(sid)
        if not (hit and hit.get("h") == _h(item)):
            want[sid] = item
    if want:
        try:
            import call_summary as cs
            import renewal_notes as rn
            if not cs._key():
                raise RuntimeError("ANTHROPIC_API_KEY not set")
            model = cs.pick_model()
        except Exception as e:
            log(f"  service audit: not read ({type(e).__name__}: {str(e)[:160]})")
            model = None
        ids, n = list(want), 0
        for i in range(0, len(ids) if model else 0, BATCH):
            chunk = {k: want[k] for k in ids[i:i + BATCH]}
            try:
                got = rn._ask(cs, model, chunk, system=SYSTEM)
            except Exception as e:
                log(f"  service audit: batch not read ({type(e).__name__}: {str(e)[:160]})")
                continue
            for k in chunk:
                v = _valid(got.get(k))
                if v:
                    cache[k] = dict(v, h=_h(want[k]), model=model)
                    n += 1
        if n:
            save(cache, log=log)
            log(f"  service audit: read {n} SR(s) with {model}")
    out = {}
    for t in srs:
        sid = str(t.get("id"))
        hit = cache.get(sid)
        if hit and hit.get("h") == _h(_item(t)):
            out[sid] = {k: hit[k] for k in ("type", "missing", "opp", "escalated")}
    return out


if __name__ == "__main__":
    import sys
    day = sys.argv[1]
    done = json.loads((ROOT / f"data/az_service_tickets_done_{day}.json").read_text())
    srs = [t for t in done if str(t.get("completeDate") or "")[:10] == day][:int(sys.argv[2]) if len(sys.argv) > 2 else None]
    res = read(srs)
    for t in srs:
        a = res.get(str(t.get("id")))
        print(t.get("modifiedBy", "")[:8], (t.get("subject") or "")[:30], "|", clean(t.get("resolutionDesc"))[:60], "|", a)

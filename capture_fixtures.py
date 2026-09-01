"""Freeze the inputs to live_contact.is_live for one day into a committed file.

    python3 capture_fixtures.py 2026-08-31

WHY THIS EXISTS. tests_live_contact.py used to read data/transcripts_<day>.json
and call day_calls.classify() live. data/ is gitignored, so on a fresh clone the
suite died on line 14 before running a single case -- it had never once run on
the nightly server. This writes everything is_live() needs into
fixtures/live_contact_<day>.json, which IS committed, so the suite runs anywhere
with no network and no cached pulls.

Run this on a container that has already built <day>. It costs nothing beyond
lead-note reads, which are cached.
"""
import json, pathlib, sys, collections
import day_calls, live_contact as lc

RANK = {"live": 4, "voicemail": 3, "no answer": 2, "unclear": 1, "unknown": 0}


def capture(day):
    tx = json.loads(pathlib.Path(f"data/transcripts_{day}.json").read_text())
    metrics = json.loads(pathlib.Path(f"data/metrics_{day}.json").read_text())
    bynum, livesecs = {}, {}
    for v in tx.values():
        n = v.get("to")
        if not n:
            continue
        k = (v.get("producer"), n)
        if RANK.get(v["class"], 0) > RANK.get(bynum.get(k), -1):
            bynum[k] = v["class"]
        if v["class"] == "live":
            livesecs[k] = max(livesecs.get(k, 0), int(v.get("duration") or 0))

    rows = day_calls.classify(day)
    out = []
    for who, rs in rows.items():
        for r in rs:
            if r.get("excluded"):
                continue
            k = (who, r["number"])
            ev = lc.evidence(r["lead_id"], day, who)
            got, basis = lc.is_live(ev, r["talk_seconds"], bynum.get(k),
                                    live_seconds=livesecs.get(k, 0))
            out.append({
                "producer": who,
                "lead_name": r.get("lead_name"),
                "lead_id": r.get("lead_id"),
                "number": r.get("number"),
                "talk_seconds": r.get("talk_seconds"),
                "transcript_class": bynum.get(k),
                "live_seconds": livesecs.get(k, 0),
                "evidence": ev,
                # what the code does TODAY -- the regression baseline
                "current": got,
                "current_basis": basis,
                # what it SHOULD do. null = not yet adjudicated; the suite skips
                # those and reports them so nobody mistakes silence for a pass.
                "expected": None,
                "why": "",
            })
    out.sort(key=lambda d: (d["producer"], -(d["talk_seconds"] or 0)))
    return out


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else None
    if not day:
        sys.exit("usage: python3 capture_fixtures.py YYYY-MM-DD")
    rows = capture(day)
    p = pathlib.Path("fixtures"); p.mkdir(exist_ok=True)
    f = p / f"live_contact_{day}.json"
    f.write_text(json.dumps(rows, indent=1, sort_keys=True))
    live = sum(1 for r in rows if r["current"])
    print(f"{f}: {len(rows)} cases, {live} currently live, "
          f"{sum(1 for r in rows if r['expected'] is None)} awaiting adjudication")

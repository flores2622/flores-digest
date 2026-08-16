"""End-to-end daily build. One entrypoint, safe to run in a fresh container.

    python3 daily.py                     # TODAY, Arizona -- ops AND staff
    python3 daily.py --day 2026-08-13 --no-send

Designed for a scheduled task: every step is idempotent and cached to data/, so
a re-run after a failure resumes rather than starting over.

TIMING. A cold run takes roughly 25-30 minutes, dominated by the RingCentral
recording download (throttled to ~12/min) and transcription. The ops task fires
at 6:30 PM Arizona and the email lands around 7:00 PM. Utilization is pulled at
the END of the run, not the start, so it reflects the settled day.
"""
import argparse
import base64
import collections
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys

AZ = dt.timezone(dt.timedelta(hours=-7))
ROOT = pathlib.Path(__file__).resolve().parent
MODEL_URL = ("https://github.com/k2-fsa/sherpa-onnx/releases/download/"
             "asr-models/sherpa-onnx-whisper-base.tar.bz2")


def log(*a):
    print(f"[{dt.datetime.now(AZ):%H:%M:%S}]", *a, flush=True)


def ensure_model():
    """Whisper weights come from the GitHub release; huggingface.co is blocked."""
    d = ROOT / "models" / "sherpa-onnx-whisper-base"
    if (d / "base-encoder.int8.onnx").exists():
        return
    log("fetching Whisper model...")
    (ROOT / "models").mkdir(exist_ok=True)
    tar = ROOT / "models" / "whisper-base.tar.bz2"
    subprocess.run(["curl", "-sSL", "-o", str(tar), MODEL_URL], check=True)
    subprocess.run(["tar", "xjf", str(tar)], cwd=ROOT / "models", check=True)
    tar.unlink(missing_ok=True)


def pull_sources(day):
    """Everything the day needs, cached so a re-run is cheap."""
    import az_corpus
    from az_client import AgencyZoom
    from rc_client import RingCentral

    (ROOT / "data").mkdir(exist_ok=True)
    nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()

    f = ROOT / f"data/rc_raw_{day}.json"
    if not f.exists():
        log("RingCentral call log...")
        recs = RingCentral().call_log(f"{day}T00:00:00-07:00", f"{nxt}T00:00:00-07:00")
        f.write_text(json.dumps(recs))
    log(f"  {len(json.loads(f.read_text()))} call records")

    az = AgencyZoom()
    for name, fn in [("az_leads_all", lambda: az_corpus.fetch()),
                     ("az_customers_all",
                      lambda: az._paged("/v1/api/customers/list", "customers", {})),
                     ("az_policies_all",
                      lambda: az._paged("/v1/api/policies", "policies", {}))]:
        p = ROOT / f"data/{name}.json"
        if not p.exists():
            log(f"{name}...")
            p.write_text(json.dumps(fn()))

    p = ROOT / f"data/az_tasks_{day}.json"
    if not p.exists():
        log("tasks...")
        p.write_text(json.dumps(az.tasks(day, day)))

    p = ROOT / "data/az_stages.json"
    if not p.exists():
        stage = {}
        def walk(o):
            if isinstance(o, dict):
                for s in o.get("stages") or []:
                    stage[s.get("id")] = f"{o.get('name')} | {s.get('name')}"
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(az.pipelines_and_stages())
        p.write_text(json.dumps({str(k): v for k, v in stage.items()}))


def transcribe_day(day):
    import transcribe
    from digest_config import PRODUCERS
    from rc_client import RingCentral, owner_ext_id

    out_f = ROOT / f"data/transcripts_{day}.json"
    names = {v["rc_id"]: k for k, v in PRODUCERS.items()}
    recs = [r for r in json.loads((ROOT / f"data/rc_raw_{day}.json").read_text())
            if r.get("recording") and r.get("direction") == "Outbound"
            and names.get(owner_ext_id(r) or "")]
    done = json.loads(out_f.read_text()) if out_f.exists() else {}
    todo = [r for r in recs if r["id"] not in done]
    if todo:
        log(f"downloading {len(todo)} recordings (throttled)...")
        transcribe.download(todo, RingCentral().token(), per_minute=12, log=log)
        log("transcribing...")
        for i, r in enumerate(todo):
            txt = transcribe.transcribe_file(f"data/audio/{r['id']}.mp3")
            cls, why = transcribe.classify(txt, r.get("duration", 0))
            done[r["id"]] = {"producer": names[owner_ext_id(r)],
                             "to": (r.get("to") or {}).get("phoneNumber"),
                             "duration": r.get("duration"), "text": txt,
                             "class": cls, "why": why}
            if (i + 1) % 25 == 0:
                log(f"  {i + 1}/{len(todo)}")
        out_f.write_text(json.dumps(done))
    c = collections.Counter(v["class"] for v in done.values())
    log(f"  transcripts: {dict(c)}")
    return done


def build_metrics(day):
    import digest_config as cfg
    import day_calls
    import live_contact as lc
    import recontact
    import insightful_util as iu
    import az_tasks
    from az_client import AgencyZoom
    from az_corpus import fetch
    from digest_config import PRODUCERS

    leads = fetch()
    pol = json.loads((ROOT / "data/az_policies_all.json").read_text())
    smap = cfg.lead_source_map(leads)
    azid = {v["az_id"]: k for k, v in PRODUCERS.items()}
    stage = {int(k): v for k, v in
             json.loads((ROOT / "data/az_stages.json").read_text()).items()}
    tx = json.loads((ROOT / f"data/transcripts_{day}.json").read_text())

    bynum, txt = {}, {}
    for v in tx.values():
        n = v.get("to")
        if not n:
            continue
        if bynum.get(n) != "live":
            bynum[n] = v["class"]
        if v["class"] == "live" and v.get("text"):
            txt.setdefault(n, v["text"])

    rows = day_calls.classify(day)
    dials = day_calls.producer_dials(day)
    ids = [r["lead_id"] for rs in rows.values() for r in rs if r["lead_id"]]
    # at-risk pool: post-contact, active, touched in the last 30 days
    cutoff = (dt.date.fromisoformat(day) - dt.timedelta(days=30)).isoformat()
    for l in leads:
        if l.get("assignedTo") in azid and str(l.get("lastActivityDate") or "")[:10] >= cutoff:
            s = stage.get(l.get("workflowStageId"), "")
            if (l.get("status") == 0 and s
                    and recontact.POST_CONTACT.search(s.split("|")[-1])):
                ids.append(l["id"])
            if str(l.get("lastActivityDate") or "").startswith(day):
                ids.append(l["id"])
    log(f"fetching notes for {len(set(ids))} leads...")
    day_calls.fetch_notes(ids)

    az = AgencyZoom()
    QS = re.compile(r"quoted|quotes presented|fsd|pending bind", re.I)
    hh = collections.defaultdict(set)
    for l in leads:
        if str(l.get("quoteDate") or "").startswith(day):
            w = azid.get(l.get("assignedTo"))
            if w:
                hh[w].add(l["id"])
    for f in (ROOT / "data/notes").glob("*.json"):
        for n in json.loads(f.read_text()):
            if n.get("type") != "MOVE_STAGE":
                continue
            if not str(n.get("createDate") or "").startswith(day):
                continue
            if n.get("createdBy") not in PRODUCERS:
                continue
            mv, _ = lc._move_stage_parts(lc._text(n.get("body")))
            dest = mv.split(" to ")[-1] if " to " in mv else mv
            if QS.search(dest):
                hh[n["createdBy"]].add(int(f.stem))

    real = cfg.real_sales(day, pol, smap, azid)
    M = {}
    for who in PRODUCERS:
        counted = [r for r in rows.get(who, []) if not r["excluded"]]
        live, b, detail = [], collections.Counter(), []
        for r in counted:
            ev = (lc.evidence(r["lead_id"], day, who) if r["lead_id"] else
                  {"written": [], "stage_moves": [], "call_notes": [], "negative": False})
            tc = bynum.get(r["number"])
            ok, basis = lc.is_live(ev, r["talk_seconds"], tc)
            b["Live Contact" if ok else
              ("Voicemail" if tc == "voicemail" else
               ("No Answer" if tc == "no answer" else lc.outcome_bucket(ev, ok)))] += 1
            if ok:
                live.append(r)
                detail.append({"lead": r["lead_name"], "lead_id": r["lead_id"],
                               "number": r["number"], "seconds": r["talk_seconds"],
                               "basis": basis,
                               "note": (ev["written"][0][:280] if ev["written"]
                                        else txt.get(r["number"], "")[:280]),
                               "moves": [m["move"] for m in ev["stage_moves"]]})
        talk = sum(r["talk_seconds"] for r in live)
        tot = 0
        for lid in hh.get(who, ()):
            try:
                qs = az.quotes(lid) or []
            except Exception:
                qs = []
            arr = qs.get("quotes") if isinstance(qs, dict) else qs
            tot += sum(float(q.get("premium") or 0) for q in (arr or []))
        n_sold, prem = real.get(who, (0, 0.0))
        M[who] = {"call_volume": len(counted), "live": len(live),
                  "contact_rate": round(len(live) / len(counted) * 100, 1) if counted else 0,
                  "avg_talk": round(talk / len(live)) if live else 0,
                  "outcomes": dict(b),
                  "call_detail": sorted(detail, key=lambda d: -d["seconds"]),
                  "households_quoted": len(hh.get(who, ())),
                  "premium_quoted": round(tot),
                  "policies": n_sold, "premium_sold": round(prem)}

    util, weighted, _ = iu.pull(day)
    tasks = az_tasks.audit(json.loads((ROOT / f"data/az_tasks_{day}.json").read_text()))
    rc = recontact.build(day, leads, stage, dials)
    coach = coach_from_gmail(day)
    s2d = speed_to_dial(day, leads, dials)

    out = {"day": day, "producers": M, "utilization": util,
           "util_weighted": weighted,
           "placeholder_sales": cfg.placeholder_sales(day, pol, smap),
           "tasks": tasks, "coach": coach, "speed_to_dial": s2d,
           "recontact": {k: [{**{kk: vv for kk, vv in x.items() if kk != "lead"},
                              "lead_id": x["lead"].get("id"),
                              "lead_name": f"{x['lead'].get('firstname','')} "
                                           f"{x['lead'].get('lastname','')}".strip()}
                             for x in v] for k, v in rc.items()}}
    (ROOT / f"data/metrics_{day}.json").write_text(json.dumps(out, indent=1, default=str))
    return out


def speed_to_dial(day, leads, dials):
    from az_corpus import e164
    from digest_config import PRODUCERS
    first = {}
    for w, bynum in dials.items():
        for num, calls in bynum.items():
            t = min(c["startTime"] for c in calls)
            first.setdefault(num, (w, t))
    per = collections.defaultdict(list)
    for l in leads:
        src = (l.get("leadSourceName") or "").lower()
        if not any(k in src for k in ("surequote", "mav ai", "mav")):
            continue
        if not str(l.get("createDate") or "").startswith(day):
            continue
        hit = first.get(e164(l.get("phone")))
        if not hit:
            continue
        c = dt.datetime.fromisoformat(str(l["createDate"]).replace(" ", "T")).replace(
            tzinfo=dt.timezone.utc)
        d = dt.datetime.fromisoformat(hit[1].replace("Z", "+00:00"))
        s = (d - c).total_seconds()
        if s > 0:
            per[hit[0]].append(int(s))
    out = {}
    for p in PRODUCERS:
        v = sorted(per.get(p, []))
        out[p] = ({"median": v[len(v) // 2], "n": len(v),
                   "quickest": v[0], "longest": v[-1]} if v else None)
    return out


def coach_from_gmail(day):
    """Coach AI titles each email with the UTC date at generation, ONE DAY AHEAD
    of the Arizona day it describes. Verified repeatedly -- do not relitigate.

    Per-user rows exist only in the HTML part; the plaintext table is empty.
    If the mailbox is unreachable in a headless run, fall back to zeros so the
    report still builds rather than failing outright.
    """
    from digest_config import PRODUCERS
    blank = {p: {"calls": 0, "score": 0, "sentiment": 0, "roleplay": 0}
             for p in PRODUCERS}
    path = ROOT / f"data/coach_{day}.json"
    if path.exists():
        return json.loads(path.read_text())
    log("  coach AI: no cached figures, using zeros "
        "(populate data/coach_<day>.json to override)")
    return blank


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day")
    ap.add_argument("--audience", choices=["ops", "staff", "both"], default="both")
    ap.add_argument("--no-send", action="store_true")
    a = ap.parse_args()

    # THE REPORTING DAY IS THE DAY THE EMAILS ARE SENT (Frank, 2026-08-14).
    # Both go out at 6:30 PM Arizona and report the day that is ending. That is
    # the whole reason the send sits at 6:30 and the reason utilization comes
    # from the Insightful API rather than its next-morning email.
    # Both emails go out together at 6:30 PM Arizona and report TODAY.
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    os.chdir(ROOT)
    log(f"building {day}")

    ensure_model()
    pull_sources(day)
    transcribe_day(day)
    build_metrics(day)

    import build_day
    out, html = build_day.build(day)
    log(f"rendered {out} ({len(html.encode()):,} bytes)")

    import attachments
    notes, rec = make_attachments(day)
    log(f"attachments: {notes}, {rec}")

    if a.no_send:
        log("--no-send, stopping")
        return
    send(day, html, [notes, rec], audience=a.audience)


def make_attachments(day):
    """Both companions, as PDF. HTML attachments arrive corrupted: they carry
    ?id=NNNNNNN lead links and =NN is a quoted-printable escape, so any hop that
    treats the part as text eats two digits from every link.
    """
    import attachments
    import build_attachments
    n_html, r_html = build_attachments.build(day)
    n_pdf = f"out/Notes_and_Methodology_{day}.pdf"
    r_pdf = f"out/Recontact_Detail_{day}.pdf"
    attachments.to_pdf(n_html, n_pdf, landscape=False)
    attachments.to_pdf(r_html, r_pdf, landscape=True)
    for p, must in ((n_pdf, ["Utilization"]), (r_pdf, ["At risk of going cold"])):
        pages, chars, missing = attachments.verify_pdf(p, must)
        if missing:
            raise SystemExit(f"{p} is missing {missing} -- refusing to send")
    return n_pdf, r_pdf


def send(day, ops_html, pdfs, audience="both"):
    import digest_config as cfg
    import send_digest
    from attachments import qp_safe
    label = dt.date.fromisoformat(day).strftime("%b %-d, %Y")
    ops = qp_safe(ops_html)
    i = ops.index('<div id="audit-section"')
    tail = ops[i:]
    staff = (ops[:i] + tail[tail.rindex("</body>"):]).replace(
        "Daily Sales Digest &amp; Call Detail Audit", "Daily Sales Digest")
    atts = [(pathlib.Path(p).name, pathlib.Path(p).read_bytes()) for p in pdfs]
    jobs = []
    if audience in ("ops", "both"):
        jobs.append((f"Daily Sales Digest & Call Detail Audit — {label}", ops,
                     cfg.RECIPIENTS_OPS))
    if audience in ("staff", "both"):
        jobs.append((f"Daily Sales Digest — {label}", staff, cfg.RECIPIENTS_STAFF))
    for subj, body, to in jobs:
        send_digest.send(subj, body, to, attachments=atts, binary=True)
        log(f"sent: {subj} -> {len(to)}")


if __name__ == "__main__":
    main()

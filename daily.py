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
import statistics
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

    # Recontact counts dials from the stage-entry date (up to MAX_STAGE_AGE days
    # back) through today, so the day's log alone cannot answer it -- every
    # "calls since" collapsed to today's dials and read 0. Frank, 2026-08-17:
    # Pamela Rice showed 0 against three real dials on 8/12, 8/13 and 8/14.
    # Day metrics keep using rc_raw_{day}; only recontact reads this window.
    # Fetched ONE DAY AT A TIME on purpose. A single call-log request spanning
    # the whole window comes back capped at 1000 records with totalPages=1, so
    # a 31-day query silently returned only the most recent ~5 days.
    import recontact
    wf = ROOT / f"data/rc_window_{day}.json"
    if not wf.exists():
        rc_api = RingCentral()
        span = recontact.MAX_STAGE_AGE + 1
        start = dt.date.fromisoformat(day) - dt.timedelta(days=span)
        log(f"RingCentral call log {start} -> {day} (recontact window, "
            f"{span + 1} daily chunks)...")
        recs, seen = [], set()
        for i in range(span + 1):
            d0 = (start + dt.timedelta(days=i)).isoformat()
            d1 = (start + dt.timedelta(days=i + 1)).isoformat()
            for r in rc_api.call_log(f"{d0}T00:00:00-07:00", f"{d1}T00:00:00-07:00"):
                if r.get("id") not in seen:
                    seen.add(r.get("id"))
                    recs.append(r)
        wf.write_text(json.dumps(recs))
    _w = json.loads(wf.read_text())
    log(f"  {len(_w)} window call records over "
        f"{len({r['startTime'][:10] for r in _w if r.get('startTime')})} days")

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

    # Day-scoped: this is a snapshot of what is OPEN, so it has to be re-pulled
    # each day. Cached under a bare name it would have frozen on day one and the
    # renewal exclusion would have quietly gone stale.
    p = ROOT / f"data/az_service_tickets_{day}.json"
    if not p.exists():
        log("service tickets...")
        p.write_text(json.dumps(az.service_tickets_live()))

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


def transcribe_day(day, outbound_only=False):
    """Outbound first, then inbound.

    `outbound_only` exists for hourly.py. The inbound branch needs
    day_calls.build_context(), which pulls the whole AgencyZoom corpus and a
    31-day RingCentral window -- about eight minutes, and in a container that
    starts cold every run that price is paid ten times a day to screen roughly
    three calls. The nightly build does inbound itself, so the hourly prefetch
    skips it and still lands the expensive part: the recordings.
    """
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
        transcribe.download(todo, RingCentral().token(), log=log)
        log("transcribing...")
        for i, r in enumerate(todo):
            txt = transcribe.transcribe_file(f"data/audio/{r['id']}.mp3",
                                             duration=r.get("duration", 0))
            cls, why = transcribe.classify(txt, r.get("duration", 0))
            done[r["id"]] = {"producer": names[owner_ext_id(r)],
                             "to": (r.get("to") or {}).get("phoneNumber"),
                             "duration": r.get("duration"), "text": txt,
                             "class": cls, "why": why}
            if (i + 1) % 25 == 0:
                log(f"  {i + 1}/{len(todo)}")
        out_f.write_text(json.dumps(done))

    if not outbound_only:
        # --- inbound -------------------------------------------------------
        # Screened FIRST, so service and renewal call-ins never cost a download
        # (Frank, 2026-08-26). What survives is stored under the CALLER's number
        # against the producer who took it, which is the same key an outbound dial
        # to that number uses -- so a live call back simply outranks the voicemail
        # the producer left, with no special handling anywhere downstream.
        import inbound as ib
        raw_by_id = {r["id"]: r for r in
                     json.loads((ROOT / f"data/rc_raw_{day}.json").read_text())}
        win = json.loads((ROOT / f"data/rc_window_{day}.json").read_text())
        in_rows = ib.screen(ib.link_callbacks(
            ib.answered(day, list(raw_by_id.values())), win, day), day)
        keep = [r for r in in_rows if not r["skip"] and r["recording"]]
        dropped = len(in_rows) - len(keep)
        in_todo = [raw_by_id[r["id"]] for r in keep if r["id"] not in done]
        if in_todo:
            log(f"inbound: {len(in_rows)} reached a producer, "
                f"{dropped} screened out, downloading {len(in_todo)}...")
            transcribe.download(in_todo, RingCentral().token(), log=log)
            by_id = {r["id"]: r for r in keep}
            for r in in_todo:
                meta = by_id[r["id"]]
                # The recording covers the WHOLE call, front desk included. The
                # producer's conversation is the last leg, so skip everything
                # before it -- otherwise the auto-attendant at the top classifies
                # the call as a voicemail.
                path = f"data/audio/{r['id']}.mp3"
                total = r.get("duration") or meta["seconds"]
                leg = meta["seconds"] or 0
                have = transcribe.audio_seconds(path) or total
                # Only offset when the recording is actually long enough to hold
                # the producer's leg. On a parked transfer it is not -- the audio
                # stops at the hand-off -- and offsetting into it reads past the
                # end and returns nothing at all.
                partial = have < leg * 0.8
                off = 0 if partial else max(0, total - leg)
                use = int(have) if partial else leg
                txt = transcribe.transcribe_file(path, duration=use, offset=off)
                cls, why = transcribe.classify(txt, use)
                done[r["id"]] = {"producer": meta["producer"],
                                 "to": meta["e164"] or meta["number"],
                                 "duration": meta["seconds"], "text": txt,
                                 "class": cls, "why": why,
                                 "direction": "inbound", "kind": meta["kind"],
                                 "offset": off, "audio_seconds": use,
                                 "partial": partial,
                                 "callback_day": meta.get("callback_day")}
            out_f.write_text(json.dumps(done))
    c = collections.Counter(v["class"] for v in done.values())
    log(f"  transcripts: {dict(c)}")
    return done



def _one_row_per_lead(detail):
    """Collapse Call Detail rows that are the same lead on two numbers.

    Returns (kept, collapsed). The collapsed rows are the DUPLICATE dials --
    the same human, reached on another of their numbers -- and the caller marks
    them dropped so they leave the contact rate as well as the panel.

    Rows with no lead_id are left alone -- they cannot be shown to be the same
    person. An inbound row is never merged into an outbound one either: they
    are two separate conversations that the report deliberately counts apart.
    """
    best, out = {}, []
    collapsed = []
    for r in detail:
        lid = r.get("lead_id")
        key = (lid, bool(r.get("inbound")))
        if lid is None:
            out.append(r)
            continue
        keep = best.get(key)
        if keep is None:
            best[key] = r
        elif (r.get("seconds") or 0) > (keep.get("seconds") or 0):
            collapsed.append(keep)          # the shorter dial is the duplicate
            best[key] = r
        else:
            collapsed.append(r)
    return out + list(best.values()), collapsed


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

    bynum, txt, all_txt, livesecs = {}, {}, {}, {}
    for v in tx.values():
        n = v.get("to")
        if not n:
            continue
        # Rank by strength of evidence, not by arrival order. A number dialled
        # more than once gets the STRONGEST verdict across its dials: a real
        # pickup on any dial means the number was reached, and a confident
        # machine greeting must not be overwritten by a later window that
        # merely failed to find evidence. Albert Collier was dialled twice 24s
        # apart -- the same screener message transcribed two ways -- and the
        # weaker read used to win the row (Frank, 2026-08-18).
        # KEYED BY (PRODUCER, NUMBER), not by number alone. Taking the
        # strongest verdict across a number is right WITHIN one producer -- it
        # is what Albert Collier needed -- but two producers can work the same
        # number on the same day, and then it hands one of them the other's
        # call. On 2026-08-25 Sarahi reached Juan Rojas at 9:36 (77s, live)
        # while Mike's own 4:15pm dial to him went to voicemail; Mike's row
        # printed Sarahi's live verdict, her transcript and her summary
        # (Frank, 2026-08-26: "how did it get duplicated to Mike?").
        k = (v.get("producer"), n)
        rank = {"live": 4, "voicemail": 3, "no answer": 2,
                "unclear": 1, "unknown": 0}
        if rank.get(v["class"], 0) > rank.get(bynum.get(k), -1):
            bynum[k] = v["class"]
        if v["class"] == "live" and v.get("text"):
            txt.setdefault(k, v["text"])
        # Longest SINGLE live recording on this key. Not the row's talk time,
        # which sums every dial to the number and would let five voicemails add
        # up to a "conversation". is_live uses this to decide whether a
        # recording is substantial enough to overrule a no-contact note written
        # earlier in the day (Ricardo Perea, Jose Garcia, Guadalupe Garcia --
        # Frank, 2026-08-28).
        if v["class"] == "live":
            livesecs[k] = max(livesecs.get(k, 0), int(v.get("duration") or 0))
        if v.get("text"):
            all_txt[k] = (all_txt.get(k, "") + " " + v["text"]).strip()

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
            if not str(n.get("createDate") or "").startswith(day):
                continue
            if n.get("createdBy") not in PRODUCERS:
                continue
            if n.get("type") == "MOVE_STAGE":
                mv, _ = lc._move_stage_parts(lc._text(n.get("body")))
                dest = mv.split(" to ")[-1] if " to " in mv else mv
                # Match the STAGE only, not the pipeline. "1-2 Leads Not Quoted"
                # is the pipeline leads are recycled into when they were never
                # quoted, so matching the full path counted those as quoted.
                dest = dest.split("|")[-1]
                if QS.search(dest):
                    hh[n["createdBy"]].add(int(f.stem))
            elif quote_presented(lc._text(n.get("body"))):
                hh[n["createdBy"]].add(int(f.stem))

    # Task titles due today, per lead -- the primary signal for whether a quote
    # is already out (Frank, 2026-08-25). Built once; lc.quote_state reads it.
    titles_by_lead = collections.defaultdict(list)
    tf = ROOT / f"data/az_tasks_{day}.json"
    if tf.exists():
        for t in json.loads(tf.read_text()):
            if (t.get("customerType") or "").lower() == "lead" and t.get("customerId"):
                titles_by_lead[t["customerId"]].append(t.get("title") or "")

    real = cfg.real_sales(day, pol, smap, azid)
    # Inbound transcripts, grouped by producer. transcribe_day stored them
    # under the caller's number, so they are already keyed like a dial.
    # RE-SCREENED HERE, not just before download. The transcripts file is a
    # cache: once a call has been transcribed it stays, so a call that a later
    # screening rule would have dropped kept appearing in Call Detail on every
    # subsequent build. Armando Alvarez survived the inbound service rule that
    # was written to exclude him purely because his audio was already on disk
    # from the run before it. The screen is pure record logic and costs
    # nothing, so it is the authority at read time too.
    import inbound as _ib
    _raw = {r["id"]: r for r in
            json.loads((ROOT / f"data/rc_raw_{day}.json").read_text())}
    _win = json.loads((ROOT / f"data/rc_window_{day}.json").read_text())
    _screened = _ib.screen(_ib.link_callbacks(
        _ib.answered(day, list(_raw.values())), _win, day), day)
    _allowed = {r["id"] for r in _screened if not r["skip"]}
    inb = collections.defaultdict(list)
    dropped_inbound = 0
    for cid, v in tx.items():
        if v.get("direction") != "inbound":
            continue
        if cid not in _allowed:
            dropped_inbound += 1
            continue
        inb[v["producer"]].append(v)
    if dropped_inbound:
        log(f"  inbound: {dropped_inbound} cached call(s) dropped by screening")
    from az_corpus import phone_index as _pidx
    lead_ix = _pidx(leads)
    _pick = day_calls.pick_lead
    M = {}
    for who in PRODUCERS:
        counted = [r for r in rows.get(who, []) if not r["excluded"]]
        live, b, detail, dials_kept = [], collections.Counter(), [], []
        for r in counted:
            ev = (lc.evidence(r.get("lead_ids") or [r["lead_id"]], day, who)
                  if r["lead_id"] else
                  {"written": [], "stage_moves": [], "call_notes": [],
                   "negative": False, "screener": False})
            tc = bynum.get((who, r["number"]))
            # How many dials to this number went UNRECORDED. Zero means the
            # audio is a complete account of the day and is_live may trust it
            # over anything written -- see the machine_only gate there.
            _calls = (dials.get(who) or {}).get(r["number"]) or []
            _unrec = sum(1 for c in _calls if not c.get("recording"))
            _scr = ev.get("screener") or bool(
                lc.SCREENER.search(all_txt.get((who, r["number"]), "")))
            ok, basis = lc.is_live(ev, r["talk_seconds"], tc,
                                   live_seconds=livesecs.get((who, r["number"]), 0),
                                   unrecorded_dials=_unrec, screener=_scr)
            # Screener is checked ahead of the transcript class on purpose. An
            # AI attendant reads as a machine greeting, so Elsa Aguilera --
            # "call dropped after AI transferred me" -- was being filed as
            # Voicemail and the Screener bucket never filled (Frank,
            # 2026-08-18). A screener is a distinct outcome: the call reached
            # something, just never the prospect.
            screened = ev.get("screener") or bool(
                lc.SCREENER.search(all_txt.get((who, r["number"]), "")))
            bucket = ("Live Contact" if ok else
                      ("Screener" if screened else
                       ("Voicemail" if tc == "voicemail" else
                        ("No Answer" if tc == "no answer"
                         else lc.outcome_bucket(
                             ev, ok,
                             [c.get("result") for c in
                              dials.get(who, {}).get(r["number"], [])])))))
            b[bucket] += 1
            # Everything finalize() needs to re-total this producer once the
            # call read has had its say. Kept per row on purpose: the totals
            # used to be computed here and the rows thrown away, which is why
            # nothing downstream could drop a dial and still report an honest
            # call volume (Frank, 2026-08-26: "can we just not compute the
            # call volume until later?").
            dials_kept.append({
                "number": r["number"], "bucket": bucket, "live": ok,
                "talk_seconds": r["talk_seconds"],
                "attempts": len(dials.get(who, {}).get(r["number"], []) or []),
                "open_lead": r.get("open_lead", False),
            })
            if ok:
                live.append(r)
                detail.append({"lead": r["lead_name"], "lead_id": r["lead_id"],
                               "number": r["number"], "seconds": r["talk_seconds"],
                               "basis": basis,
                               # Kept apart so the report can say which is
                               # which. Merging them printed Mike's typed
                               # notes as "From the call recording" (Frank,
                               # 2026-08-17, Lazaro Rueda).
                               # EVERY note the producer wrote on this lead
                               # today, not just the first. evidence() has
                               # always collected them all, but the panel
                               # printed [0] alone -- on 2026-08-24 five of the
                               # 32 contacts had two or three notes and only one
                               # was shown (Frank, 2026-08-25: "they might add
                               # multiple notes in one day ... are you reading
                               # all the notes?").
                               # De-duplicated: the same text can arrive as
                               # both a comment and a stage-move comment, and
                               # Josefina Chavez printed hers twice.
                               "note_producer": " &middot; ".join(
                                   dict.fromkeys(ev["written"]))[:480],
                               "quote_state": lc.quote_state(
                                   r["lead_id"], day,
                                   titles_by_lead.get(r["lead_id"], ())),
                               "note_recording": txt.get((who, r["number"]), "")[:280],
                               # Carried from day_calls: the lead behind this
                               # number is marked SOLD today. Outranks the
                               # stage moves, which can sit on a duplicate
                               # record the producer killed (Hugo Bojorquez,
                               # 2026-08-25).
                               "sold_today": r.get("sold_today", False),
                               "moves": [m["move"] for m in ev["stage_moves"]]})
        # --- inbound ----------------------------------------------------
        # A call back that arrived the SAME day merges into the dial it
        # answers: one row, both conversations, the times added (Frank,
        # 2026-08-26). Everything else -- a cold call-in, or a call back to a
        # dial from an earlier day -- becomes its own inbound line on the day
        # it happened, because that earlier day's report has already gone out.
        prior_callbacks = 0
        for e in inb.get(who, []):
            same_day = e.get("kind") == "callback" and e.get("callback_day") == day
            if e.get("kind") == "callback" and not same_day:
                # Answers a dial from an earlier day, which is not in today's
                # denominator. Counted beside the bar, never inside it.
                prior_callbacks += 1
            if same_day:
                # Mark the DIAL, whatever its outcome. The bar counts dials, so
                # the call back shows as a candy-cane slice of whichever
                # segment that dial already sits in -- usually Live Contact,
                # because the call back's own transcript is what turned the
                # dial live in the first place.
                for d0 in dials_kept:
                    if d0["number"] == e["to"]:
                        d0["callback"] = True
                        break
            row = next((d for d in detail if d["number"] == e["to"]), None)
            if same_day and row is not None:
                row["seconds"] += e.get("duration") or 0
                row["callback_seconds"] = e.get("duration") or 0
                continue
            lead = _pick(lead_ix.get(e["to"], []))
            detail.append({
                "lead": (f"{(lead.get('firstname') or '').strip()} "
                         f"{(lead.get('lastname') or '').strip()}".strip()
                         if lead else None),
                "lead_id": lead.get("id") if lead else None,
                "number": e["to"], "seconds": e.get("duration") or 0,
                "basis": "recording (inbound)", "inbound": True,
                "kind": e.get("kind"), "callback_of_day": e.get("callback_day"),
                "note_producer": "", "quote_state": "none",
                "note_recording": (e.get("text") or "")[:280],
                "partial": bool(e.get("partial")),
                "tx_class": e.get("class"),
                "sold_today": False, "moves": []})

        tot = 0
        for lid in hh.get(who, ()):
            try:
                qs = az.quotes(lid) or []
            except Exception:
                qs = []
            arr = qs.get("quotes") if isinstance(qs, dict) else qs
            tot += sum(float(q.get("premium") or 0) for q in (arr or []))
        n_sold, prem = real.get(who, (0, 0.0))
        # ONE PERSON, ONE CONTACT. Keying on (producer, number) is right for
        # attribution, but a lead reachable on two numbers becomes two rows for
        # the same conversation. Roger Ryan was dialled on +1 303-847-3747 for
        # 100 seconds and on +1 480-883-8366 for one second; the lead note sat
        # on both, AgencyZoom itself had the record marked "Loss Reason:
        # Duplicate Lead", and Sarahi's contact rate counted him twice
        # (Frank, 2026-08-28: "he was already there"). Keep the longest row --
        # that is the dial the conversation actually happened on.
        # ONE ACCOUNT, ONE EVERYTHING. Frank, 2026-09-01: "can we make a rule
        # for same accounts to not count as a duplicate even if its from
        # another number". Collapsing Call Detail was only half of it -- the
        # live count and the contact rate come off `dials_kept`, which was not
        # collapsed, so one person reached on two of their numbers scored as
        # two contacts. Mike / Nicole Santana on 2026-08-31: 252s on
        # +1 917-804-1091 and 67s on +1 631-276-3801, same lead 42759342, both
        # counted. Same shape as Roger Ryan (Frank, 2026-08-28: "he was already
        # there").
        #
        # The duplicate dial is marked `dropped`, which is the mechanism the
        # service/renewal read already uses: finalize._totals filters dropped
        # dials before it computes ANY figure, so the second number leaves the
        # numerator and the denominator together. It is one attempt at one
        # person, not two attempts -- reaching someone on their mobile after
        # their landline should not read as a 50% contact rate.
        detail, duplicates = _one_row_per_lead(detail)
        # THE ATTEMPT SURVIVES, THE CONTACT DOES NOT. Frank, 2026-09-01:
        # "theres 2 outbounds to 2 numbers. he got a hold on the second one,
        # it 2 dials, one unique number/contact." A first pass dropped the
        # duplicate outright and took its dial with it -- Mike's total_dials
        # fell 57 -> 56, erasing a call he really made.
        #
        # This is exactly how the model already treats one number dialled
        # twice: ONE call_volume entry carrying attempts=2. A second number for
        # the same person is the same thing, so its attempts move onto the
        # surviving row before it is dropped. Result for Nicole Santana:
        # call_volume 53, total_dials 57, one live contact.
        keep_num = {r["lead_id"]: r["number"] for r in detail
                    if not r.get("inbound") and r.get("lead_id") is not None}
        by_number = {d["number"]: d for d in dials_kept}
        for dup in duplicates:
            if dup.get("inbound"):
                continue
            row = by_number.get(dup["number"])
            if row is None:
                continue
            survivor = by_number.get(keep_num.get(dup.get("lead_id")))
            if survivor is not None and survivor is not row:
                survivor["attempts"] = ((survivor.get("attempts") or 0)
                                        + (row.get("attempts") or 0))
            row["dropped"] = "duplicate lead (same person, another number)"
        M[who] = {"dials": dials_kept, "callbacks_prior": prior_callbacks,
                  "call_detail": sorted(detail, key=lambda d: -d["seconds"]),
                  "households_quoted": len(hh.get(who, ())),
                  "premium_quoted": round(tot),
                  "policies": n_sold, "premium_sold": round(prem)}

    util, weighted, _ = iu.pull(day)
    _raw_tasks = json.loads((ROOT / f"data/az_tasks_{day}.json").read_text())
    import task_audit as _ta
    _verdicts = _ta.cancellation_verdicts(
        day, _raw_tasks, {v["az_id"]: k for k, v in PRODUCERS.items()})
    tasks = az_tasks.audit(_raw_tasks, _verdicts)
    # Window dials, not day dials: recontact counts back to the stage-entry date.
    rc = recontact.build(day, leads, stage, day_calls.window_dials(day))
    import task_audit
    t_audit = task_audit.build(
        day, _raw_tasks, dials, leads,
        json.loads((ROOT / "data/az_customers_all.json").read_text()),
        _verdicts)
    coach = coach_from_gmail(day)
    s2d = speed_to_dial(day, leads, dials)

    out = {"day": day, "producers": M, "utilization": util,
           "util_weighted": weighted,
           "placeholder_sales": cfg.placeholder_sales(day, pol, smap),
           "tasks": tasks, "task_audit": t_audit, "coach": coach,
           "speed_to_dial": s2d,
           "recontact": {k: [{**{kk: vv for kk, vv in x.items() if kk != "lead"},
                              "lead_id": x["lead"].get("id"),
                              "lead_name": f"{x['lead'].get('firstname','')} "
                                           f"{x['lead'].get('lastname','')}".strip()}
                             for x in v] for k, v in rc.items()}}
    # Total it once here so metrics_<day>.json is always well-formed for
    # anything that reads it before the call summaries land. main() re-applies
    # after the read, and finalize.apply is idempotent by design.
    import finalize
    finalize.apply(out)
    (ROOT / f"data/metrics_{day}.json").write_text(json.dumps(out, indent=1, default=str))
    return out

# A note counts as a quote ONLY when the quote is delivered in that message.
# The team's outreach is saturated with the word "quote" -- solicitation
# ("are you interested in a quote?", "called to offer new quote, no answer")
# and follow-ups on quotes sent earlier ("the quote I sent you", "I sent you a
# quote over a week ago"). Counting either would credit a day with work that
# did not happen on it, and the follow-up templates repeat daily until the
# customer replies, so one quote would be recounted every day it is chased.
# Frank confirmed this reading against the 2026-08-14 notes.
_PRESENTED = re.compile(
    r"this is (?:a|an|the|your)[^.!?]{0,40}\bquote\b"
    r"|here (?:is|are) (?:a|the|your)[^.!?]{0,40}\bquote\b"
    r"|(?:your |the )?quote is attached"
    r"|attach(?:ed|ing)[^.!?]{0,25}\bquote\b", re.I)
_PAST = re.compile(
    r"sent you|i sent|week ago|haven'?t heard back|chance to review", re.I)


def quote_presented(body):
    """True when the note delivers a quote rather than asking for or chasing one."""
    b = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(body or "")))
    return bool(_PRESENTED.search(b)) and not _PAST.search(b)
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
        # `secs` IS THE POINT: the team card is the median of every lead time
        # pooled, not a statistic over per-producer medians, so the raw list has
        # to survive into metrics_<day>.json. build_day.py used to derive the
        # team figures from the medians alone, which made team `longest`
        # max(medians) -- structurally incapable of exceeding the worst
        # individual longest. On 2026-09-01 it printed 1m58s against a true
        # 20m47s. See REVIEW_2026-09-01.md section 1.
        #
        # statistics.median, not v[len(v)//2]: on an EVEN count the old index
        # took the upper of the two middle values, which is not a median. It
        # inflated Crystal to 1m58s on 09-01 when hers was 1m13s -- and that
        # figure drives the card's colour tier, whose green/yellow line is at
        # 2 minutes, so she was two seconds from being coloured wrong.
        out[p] = ({"median": int(statistics.median(v)), "n": len(v),
                   "quickest": v[0], "longest": v[-1], "secs": v} if v else None)
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
        # Merge OVER the blank template rather than returning the file as-is.
        # This file is hand-written each evening from the Coach AI emails, and a
        # producer with no rows in those emails is simply absent from it. Before
        # 2026-08-24 the roster and the file always matched, so a raw return was
        # safe; with five producers a missing name became a KeyError deep inside
        # the leaderboard. Zeros are the correct reading of "absent" here.
        loaded = json.loads(path.read_text())
        merged = {p: dict(blank[p], **loaded.get(p, {})) for p in blank}
        missing = [p for p in blank if p not in loaded]
        if missing:
            log(f"  coach AI: no rows for {', '.join(missing)} -- using zeros")
        extra = [p for p in loaded if p not in blank]
        if extra:
            log(f"  coach AI: ignoring non-producer rows: {', '.join(extra)}")
        return merged
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
    (ROOT / "out").mkdir(exist_ok=True)
    log(f"building {day}")

    ensure_model()
    pull_sources(day)
    transcribe_day(day)
    build_metrics(day)

    # Full-transcribe and read the live contacts. Runs AFTER build_metrics
    # because it only touches calls that came out as live contacts, and caches
    # both stages, so it costs nothing on a re-run (Frank, 2026-08-25).
    import call_summary
    try:
        call_summary.build(day, log=log)
    except Exception as e:
        log(f"  call summaries failed ({type(e).__name__}) -- "
            f"Call Detail falls back to producer notes")

    # Re-total after the read: it can drop a dial that AgencyZoom had no way
    # to flag as service work (Frank, 2026-08-26).
    import finalize
    M = json.loads((ROOT / f"data/metrics_{day}.json").read_text())
    before = {w: v.get("call_volume") for w, v in M["producers"].items()}
    finalize.apply(M)
    (ROOT / f"data/metrics_{day}.json").write_text(
        json.dumps(M, indent=2, default=str))
    moved = {w: (before[w], M["producers"][w]["call_volume"])
             for w in before if before[w] != M["producers"][w]["call_volume"]}
    if moved:
        for w, (b, a) in moved.items():
            log(f"  {w}: call volume {b} -> {a} (service found in the call)")

    import build_day
    out, html = build_day.build(day)
    log(f"rendered {out} ({len(html.encode()):,} bytes)")

    import attachments
    notes, rec = make_attachments(day)
    log(f"attachments: {notes}, {rec}")
    missed = make_missed_call_audit(day)

    if a.no_send:
        log("--no-send, stopping")
        return
    # A tracked SEND_HOLD file stops the nightly run from emailing while a
    # change is mid-flight. The scheduled task clones main and runs a bare
    # `daily.py`, so there is no flag to pass it and no way to pause it from
    # outside the repo -- on 2026-08-28 both the scheduler pause and a push
    # were blocked, and an unfixed report went to all ten people as a result.
    # A tracked file is the only hold that travels with the code.
    #
    # To hold a send: commit a SEND_HOLD file with a line saying why.
    # To release it: delete the file in the same merge that lands the fix.
    hold = ROOT / "SEND_HOLD"
    if hold.exists():
        log(f"SEND_HOLD present, built but NOT sending -- "
            f"{hold.read_text().strip()[:200]}")
        return
    send(day, html, [notes, rec], audience=a.audience,
         ops_only_pdfs=[missed] if missed else [])
    make_missed_call_tasks(day)


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


def make_missed_call_audit(day):
    """The missed-call audit, ops only. Read-only -- creates nothing.

    A PDF attachment rather than a panel on purpose. The body is already inside
    two hard Gmail limits (a ~16 KB stylesheet cap and a 102 KB body cap, see
    render_report.prune_css and overflow.relieve) and a new panel is the fastest
    way back to an unstyled email.

    NEVER let this stop the digest. It is a companion report; if it fails the
    day's numbers still have to go out.
    """
    import attachments
    import missed_call_audit as mca
    try:
        rows = mca.build(day, refresh=False)
        html_p = ROOT / f"out/Missed_Call_Audit_{day}.html"
        html_p.write_text(mca.render(day, rows))
        pdf = f"out/Missed_Call_Audit_{day}.pdf"
        attachments.to_pdf(str(html_p), pdf, landscape=False)
        pages, chars, missing = attachments.verify_pdf(pdf, ["Missed Call Audit"])
        if missing:
            log(f"missed-call audit PDF is missing {missing} -- skipping it")
            return None
        waiting = sum(1 for r in rows if r["back_in"] is None)
        log(f"missed-call audit: {len(rows)} callers, {waiting} still waiting")
        return pdf
    except Exception as e:
        log(f"missed-call audit failed ({type(e).__name__}: {e}) -- "
            f"sending the digest without it")
        return None


def send(day, ops_html, pdfs, audience="both", ops_only_pdfs=()):
    import digest_config as cfg
    import send_digest
    from attachments import qp_safe
    label = dt.date.fromisoformat(day).strftime("%b %-d, %Y")
    ops = qp_safe(ops_html)

    # Staff used to lose the whole audit section, which cut Call Detail along with
    # it. Frank, 2026-08-24: staff should see the live call detail. So the staff
    # body now keeps the audit section and drops only the Task Completion Audit
    # panel, and its heading is retitled to match what is actually left in it.
    # Removing one panel by depth walk keeps the section wrapper balanced, which
    # cutting at the section boundary did by brute force.
    import render_report as rr
    staff = rr.drop_panel(ops, "Task Completion Audit &middot;")
    staff = (staff
             .replace("Call Detail &amp; Task Completion Audit", "Call Detail")
             .replace("Daily Sales Digest &amp; Call Detail Audit",
                      "Daily Sales Digest"))
    # Prune the stylesheet LAST, per audience, after shedding -- a shed panel's
    # rules are dead weight in the body that remains, and Gmail throws away any
    # <style> block over ~16 KB (see render_report.prune_css).
    ops = rr.prune_css(ops, log=log)
    staff = rr.prune_css(staff, log=log)
    def load(paths):
        return [(pathlib.Path(p).name, pathlib.Path(p).read_bytes())
                for p in paths if p]
    atts = load(pdfs)
    # The missed-call audit goes to ops alone. It is a management view of
    # volume and response time while the rules are being watched; staff get
    # real tasks once the feature is switched on, not a rehearsal document.
    ops_atts = atts + load(ops_only_pdfs)
    jobs = []
    if audience in ("ops", "both"):
        jobs.append((f"Daily Sales Digest & Call Detail Audit — {label}", ops,
                     cfg.RECIPIENTS_OPS, ops_atts))
    if audience in ("staff", "both"):
        jobs.append((f"Daily Sales Digest — {label}", staff,
                     cfg.RECIPIENTS_STAFF, atts))
    # On a heavy day the body can pass Gmail's clip threshold. Rather than
    # refuse the whole send -- which cost BOTH audiences their report -- shed
    # panels into a PDF attachment and say so at the top of the email (Frank,
    # 2026-08-25). Each audience is measured on its own: the staff body is
    # already lighter by one panel, so it can still fit when ops does not.
    import overflow
    for subj, body, to, base_atts in jobs:
        body, extra = overflow.relieve(day, body, log=log)
        a = list(base_atts)
        if extra:
            a.append((pathlib.Path(extra).name,
                      pathlib.Path(extra).read_bytes()))
        send_digest.send(subj, body, to, attachments=a, binary=True)
        log(f"sent: {subj} -> {len(to)}")


def make_missed_call_tasks(day):
    """Create the missed-call tasks in AgencyZoom (missed_call_tasks.run, live).

    Runs AFTER send(): the digest emails have already gone out by this point,
    so nothing here may ever raise -- a failure creating tasks must not be
    allowed to look like a failure to send the day's numbers.
    """
    import missed_call_tasks
    try:
        made, skipped = missed_call_tasks.run(day, live=True)
        log(f"missed-call tasks: {len(made)} created, {len(skipped)} skipped")
    except Exception as e:
        log(f"missed-call tasks failed ({type(e).__name__}: {e}) -- "
            f"the digest already sent, so nothing else is affected")


if __name__ == "__main__":
    main()

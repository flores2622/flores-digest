"""Athena's texts and emails: what the service team sends customers, what
comes back, and how fast they answer it (Frank, 2026-09-27: mirror the
Sales Center's Texts & Emails, messages.py, on the service side).

TEXTS COME FROM RINGCENTRAL, not AgencyZoom. RingCentral's message store has
every text on each person's own line, both directions, however it was sent
(the RingCentral app, a phone, or AgencyZoom -- AgencyZoom sends through these
same lines). AgencyZoom's own TEXT notes only exist where the customer still
has a lead record, so they are never read here: reading both would count
each text twice.

  Debbie   ext 103   Amanda   ext 102 (two lines)   Crystal  ext 106

EMAILS COME FROM AGENCYZOOM. RingCentral carries no email. AgencyZoom logs an
email on the lead record a customer came in on, so a customer with no lead
record, and anything sent from Outlook outside AgencyZoom, is not seen.

AUTOMATION. RingCentral's record of an AgencyZoom automation text is identical
to a typed one -- no field tells them apart. So, like messages.py's template
emails: a text whose body, with the greeting's name and every number taken
out, one person sent to TEMPLATE_NUMBERS or more different numbers over the
last LEARN_DAYS days is automation ("Just a quick reminder that your Auto
insurance policy..." went to 132 numbers in September). A text with a
picture or PDF (ID cards) is always typed. A canned message typed by hand to
five people reads as automation too -- the store cannot tell them apart.

WHOSE IT IS. Only a number that routes to service counts, by the same rule
as the missed-call audit and call backs (missed_call_audit.route): a
customer, or anyone with an open SR. An open or closed lead is sales
(messages.py, Apollo's); a commercial-only household is Cerberus's; a number
AgencyZoom does not know at all (family, vendors) is counted, never listed,
and its words are never stored.

A customer's text belongs to whoever's line it came in on. It is answered by
the next typed text to that number from any service line, a call back
(RingCentral's call log), or a call they were on for 30s+ that was still
going when the text arrived -- messages.py's rules. The day's window is the
same: from the office's close the business day before to 5:30 PM, the clock
starting at 8:30 for a text that came in closed. "ok" / "thanks" and STOP are
counted, never waiting. Rows, never medians.
"""
import collections
import datetime as dt
import json
import pathlib
import re

import messages as msg
from missed_call_audit import norm

ROOT = pathlib.Path(__file__).resolve().parent
AZ = msg.AZ
LEARN_DAYS = 30
TEMPLATE_NUMBERS = 5
SERVICE_BUCKETS = {"customer", "open SR"}
SAID = 300


# A text that asks for nothing, in more words than messages.ACK takes:
# "Ok muchas grasias", "Si esta bien gracias", "Got it, thank you!".
_ACK_WORDS = {"ok", "okay", "okey", "k", "kk", "thanks", "thank", "thx", "you", "u", "so", "much", "very", "ty",
              "gracias", "grasias", "muchas", "mil", "perfect", "perfecto", "sounds", "good", "great", "si", "sí",
              "yes", "yep", "got", "it", "will", "do", "bien", "está", "esta", "vale", "gotcha", "awesome", "cool",
              "received", "recibido", "listo", "de", "nada", "have", "a", "nice", "day", "buen", "día", "dia",
              "appreciate", "sweet", "alright", "all", "right", "np", "sure", "igualmente", "you're", "welcome"}


_ACK_WORDS |= {"sii", "no", "hay", "problema", "sure", "fine", "that", "is", "that's", "muy", "i'm", "im",
               "awesome", "ya", "ahh", "oh", "wonderful", "excellent", "excelente", "claro", "bueno", "will"}
# A phone's tapback on one of our texts ("Liked “...”", "Le encantó “...”").
_TAPBACK = re.compile(r"^\s*(liked|loved|laughed at|emphasized|disliked|questioned|reacted \S+ to|"
                      r"le gustó|le encantó|le encanto|le gusto|se rió de|enfatizó|destacó)\s*[“\"']", re.I)
_THANKS = re.compile(r"\b(thanks?|thank you|thx|ty|gracias|grasias|appreciate)\b", re.I)


def is_ack(t):
    """Nothing to answer: an ok, a thank-you, a tapback. A thank-you with a
    short sentence and no question ("Thank you! I'll check my email when I
    get home") is one too."""
    t = str(t or "").strip()
    if not t:
        return False
    if _TAPBACK.match(t):
        return True
    words = re.findall(r"[a-záéíóúñ']+", t.lower())
    if "?" in t:
        return False
    return bool(msg.ACK.match(t)) or (0 < len(words) <= 8 and all(w in _ACK_WORDS for w in words)) \
        or (bool(_THANKS.search(t)) and len(words) <= 14)


# A message about a renewal: the reminders ("your Auto policy is scheduled to
# renew soon"), and anything the customer or a rep says about it.
RENEWAL_WORDS = re.compile(r"\brenew|\brenov|\brenuev", re.I)


def log(*a):
    print(*a, flush=True)


def _file(day):
    return ROOT / f"data/rc_texts_{day}.json"


def _norm_body(s):
    """A text with the greeting's name and every number taken out, so one
    template sent to many people reads as one body."""
    s = str(s or "").strip()
    s = re.sub(r"^(hi|hello|hola|hey|good (morning|afternoon|evening)|buen(o|a)s? (d[ií]as|tardes|noches))"
               r"[\s,]+[^\s,!.]+( [A-Z][a-z]+)?[,!.]?\s*", "<hi> ", s, flags=re.I)
    s = re.sub(r"\$?[\d][\d,./:\-]*", "#", s)
    return re.sub(r"\s+", " ", s).lower()[:80]


def _typed_media(r):
    return any((a.get("contentType") or "") != "text/plain" for a in r.get("attachments") or [])


def _slim(r, who):
    inbound = r.get("direction") == "Inbound"
    other = (r.get("from") or {}).get("phoneNumber") if inbound else \
        ((r.get("to") or [{}])[0] or {}).get("phoneNumber")
    return {"id": r.get("id"), "who": who, "in": inbound, "at": r.get("creationTime"),
            "number": norm(other),
            "text": msg.redact(str(r.get("subject") or "").strip()), "media": _typed_media(r),
            "status": r.get("messageStatus")}


def _team():
    import service_digest as sd
    return set(sd.SERVICE_TEAM)


def fetch(day, log=log, refresh=False):
    """The day's texts on the service lines, saved to data/rc_texts_<day>.json:
    everything from the reply window's start to the end of the day, plus the
    template bodies learned from the LEARN_DAYS before. A past day's texts
    do not change, so a saved file is reused."""
    f = _file(day)
    if f.exists() and not refresh:
        # Kept only once the day is over: a copy fetched mid-evening misses
        # what came in after it.
        got = json.loads(f.read_text())
        if str(got.get("fetched_at") or "") > f"{day}T23:59":
            return got
    from rc_client import RingCentral
    rc = RingCentral()
    start, _ = msg.window(day)
    day_end = msg._clock(dt.date.fromisoformat(day), (23, 59)) + dt.timedelta(minutes=1)
    learn_from = start - dt.timedelta(days=LEARN_DAYS)
    z = lambda t: t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    texts, sent_to = [], collections.defaultdict(set)
    names = {eid: v["name"] for eid, v in rc.roster().items()}
    for eid, who in {e: n for e, n in names.items() if n in _team()}.items():
        for r in rc.texts(eid, z(learn_from), z(day_end)):
            s = _slim(r, who)
            if not s["in"] and not s["media"] and s["text"] and s["number"]:
                sent_to[(who, _norm_body(s["text"]))].add(s["number"])
            t = dt.datetime.fromisoformat(str(s["at"]).replace("Z", "+00:00"))
            if t >= start:
                texts.append(s)
    templates = sorted([w, k] for (w, k), nums in sent_to.items() if len(nums) >= TEMPLATE_NUMBERS)
    out = {"day": day, "texts": sorted(texts, key=lambda s: s["at"]), "templates": templates, "names": names,
           "learn_days": LEARN_DAYS, "fetched_at": dt.datetime.now(AZ).isoformat(timespec="seconds")}
    f.parent.mkdir(exist_ok=True)
    f.write_text(json.dumps(out))
    log(f"  service texts: {len(texts)} on the service lines, {len(templates)} automation templates")
    return out


def _calls(day):
    """RingCentral call log for the day (daily.py's rc_raw), or []."""
    f = ROOT / f"data/rc_raw_{day}.json"
    return json.loads(f.read_text()) if f.exists() else []


def customer_leads(idx):
    """Lead ids on the numbers that route to service: where a customer's
    emails are logged."""
    import missed_call_audit as mca
    out = {}
    for n, hit in idx.items():
        if mca.route(hit)[0] in SERVICE_BUCKETS:
            for l in hit["lead"]:
                out[l["id"]] = n
    return out


def fetch_emails(day, lead_ids, since=None, log=log):
    """Make sure the notes of every customer lead active in the window (or
    since `since`, for a backfill) are on disk. Leads daily.py already
    downloaded tonight are skipped."""
    import time
    leads = json.loads((ROOT / "data/az_leads_all.json").read_text())
    want = set(lead_ids)
    if since:
        cut = msg.window(since)[0].astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        ids = [l["id"] for l in leads if l["id"] in want and str(l.get("lastActivityDate") or "") >= cut]
    else:
        ids = msg.active_leads([l for l in leads if l["id"] in want], day)
    msg._fetch_notes_paced(ids, fresh_after=time.time() - 6 * 3600, log=log)


def build(day, idx=None, commercial_only=frozenset(), log=log, download_notes=True):
    """The day's service texts-and-emails section, or None when RingCentral's
    texts could not be read."""
    import commercial
    import missed_call_audit as mca
    import service_digest as sd
    team = set(sd.SERVICE_TEAM)
    try:
        raw = fetch(day, log=log)
    except Exception as e:
        log(f"  service texts: not read ({type(e).__name__}: {str(e)[:160]})")
        return None
    if idx is None:
        idx, *_ = mca.build_index(day)
    start, end = msg.window(day)
    day_end = msg._clock(dt.date.fromisoformat(day), (23, 59))
    opens_at = msg._clock(dt.date.fromisoformat(day), msg.OFFICE_OPEN)
    templates = {tuple(x) for x in raw.get("templates") or []}
    names = raw.get("names") or {}

    def bucket(n):
        hit = idx.get(n)
        if commercial.is_commercial_caller(hit, commercial_only):
            return "commercial"
        return mca.route(hit)[0]

    def link(n):
        hit = idx.get(n) or {}
        cust = (hit.get("cust") or [None])[0]
        lead = (hit.get("lead") or [None])[0] if not cust else None
        return {"name": mca.name_for(hit, None) or mca.pretty(n),
                "link_kind": "customer" if cust else ("lead" if lead else None),
                "link_id": (cust or lead or {}).get("id")}

    events = collections.defaultdict(list)     # number -> [event]
    for s in raw["texts"]:
        if not s["number"]:
            continue
        at = dt.datetime.fromisoformat(str(s["at"]).replace("Z", "+00:00")).astimezone(AZ)
        if s["in"]:
            kind = "in"
        elif s["status"] in ("DeliveryFailed", "SendingFailed"):
            kind = "failed"
        elif not s["media"] and (s["who"], _norm_body(s["text"])) in templates:
            kind = "auto"
        else:
            kind = "sent"
        events[s["number"]].append({"at": at, "kind": kind, "by": s["who"], "type": "TEXT",
                                    "text": s["text"], "media": s["media"]})

    # Emails on the customers' lead records (AgencyZoom notes).
    leads_of = customer_leads(idx)
    if download_notes:
        try:
            fetch_emails(day, leads_of, log=log)
        except Exception as e:
            log(f"  service emails: notes not downloaded ({type(e).__name__}) -- using what is on disk")
    import live_contact as lc
    subj_leads = collections.defaultdict(set)
    email_rows = []
    for lid, n in leads_of.items():
        if not (lc.NOTE_DIR / f"{lid}.json").exists():
            continue
        wrote = []
        notes = [x for x in lc.load_notes(lid) if x.get("type") == "EMAIL"]
        for x in notes:
            at = msg._at(x.get("createDate"))
            if at and msg._inbound(x.get("attr") or {}):
                wrote.append(at)
        for x in notes:
            at = msg._at(x.get("createDate"))
            if at is None or at < start - dt.timedelta(days=LEARN_DAYS):
                continue
            a = x.get("attr") or {}
            by = (x.get("createdBy") or "").strip()
            reply = msg._is_reply_subject(x) and any(w < at for w in wrote)
            key = msg._subject_key(x, None)
            if not msg._inbound(a) and not a.get("attachments") and not reply:
                subj_leads[key].add(lid)
            email_rows.append((n, lid, x, at, a, by, reply, key))
    tmpl = msg.TEMPLATE_SUBJECTS | {k for k, v in subj_leads.items() if k and len(v) >= msg.LEARN_TEMPLATE_LEADS}
    seen = set()
    for n, lid, x, at, a, by, reply, key in email_rows:
        # Duplicate lead records on one number carry the same email; notes
        # have no id, so it is the same email by time, subject and sender.
        dup = (n, x.get("createDate"), str(a.get("emailSubject") or ""), by, msg._inbound(a))
        if at < start or dup in seen:
            continue
        seen.add(dup)
        if msg._inbound(a):
            kind = "in"
        else:
            if by not in team:
                kind = "producer"      # Apollo's; only tells whose thread a reply is
            else:
                kind = "auto" if (key in tmpl and not a.get("attachments") and not reply) else "sent"
        events[n].append({"at": at, "kind": kind, "by": by if not msg._inbound(a) else "", "type": "EMAIL",
                          "text": msg._text(x), "subject": str(a.get("emailSubject") or "").strip(),
                          "bounced": bool(a.get("bounced"))})

    # Calls to and from those numbers, as answers.
    for r in _calls(day):
        d = r.get("direction")
        n = norm(((r.get("to") if d == "Outbound" else r.get("from")) or {}).get("phoneNumber"))
        if not n or n not in events:
            continue
        try:
            at = dt.datetime.fromisoformat(str(r["startTime"]).replace("Z", "+00:00")).astimezone(AZ)
        except (KeyError, ValueError):
            continue
        dur = int(r.get("duration") or 0)
        if d == "Inbound" and dur < msg.CONVERSATION_SECONDS:
            continue
        side = (r.get("from") if d == "Outbound" else r.get("to")) or {}
        who = side.get("name") or names.get(str(side.get("extensionId") or (r.get("extension") or {}).get("id") or "")) or ""
        events[n].append({"at": at, "kind": "call", "by": who, "type": "CALL", "text": "", "dur": dur})

    stats = {p: collections.Counter() for p in sd.SERVICE_TEAM}
    replies, sent_rows = [], []
    for n, evs in events.items():
        evs.sort(key=lambda e: e["at"])
        b = bucket(n)
        mine = b in SERVICE_BUCKETS
        # Renewal business (Frank, 2026-09-27: "everything should be
        # separated"): every SR the customer has open is a renewal SR, or the
        # message itself is about the renewal.
        import service_digest as _sd
        ren_caller = _sd.renewal_caller(idx.get(n))
        who_link = link(n) if mine else None

        # --- what went out today -------------------------------------------
        texted = set()
        for e in evs:
            if e["at"].date().isoformat() != day or e["kind"] not in ("sent", "auto", "failed", "in"):
                continue
            p = e["by"]
            if e["kind"] == "in":
                # Received on whose line; an email has no line, so its thread's owner.
                if e["type"] == "TEXT" and p in stats and mine:
                    stats[p]["texts_in"] += 1
                continue
            if p not in stats:
                continue
            if not mine:
                stats[p]["lead_texts" if b in ("open lead", "closed lead") else "other_texts"] += e["type"] == "TEXT"
                continue
            ch = "texts" if e["type"] == "TEXT" else "emails"
            if e["kind"] == "auto":
                stats[p]["auto_" + ch] += 1
            else:
                stats[p][ch] += 1
                if e["kind"] == "failed" or e.get("bounced"):
                    stats[p]["bad"] += 1
                if (p, n) not in texted:
                    texted.add((p, n))
                    stats[p]["customers"] += 1
            sent_rows.append(dict(who_link, who=p, day=day, at=e["at"].strftime("%H:%M"), number=n,
                                  renewal=ren_caller or bool(RENEWAL_WORDS.search(e.get("subject") or "")
                                                             or RENEWAL_WORDS.search(e["text"] or "")),
                                  channel="text" if e["type"] == "TEXT" else "email",
                                  auto=e["kind"] == "auto", failed=e["kind"] == "failed" or e.get("bounced", False),
                                  media=bool(e.get("media")),
                                  text=(e.get("subject") or e["text"])[:160]))
        if not mine:
            continue

        # --- replies waiting on us ------------------------------------------
        touches = [t for t in evs if t["kind"] in ("sent", "call") and t["at"] <= day_end]
        def ends(t):
            return t["at"] + dt.timedelta(seconds=t.get("dur") or 0)
        i = 0
        while i < len(evs):
            e = evs[i]
            if e["kind"] != "in" or not (start < e["at"] <= end):
                i += 1
                continue
            if e["type"] == "TEXT":
                partner = e["by"]
            else:
                before = [t for t in evs if t["kind"] in ("sent", "auto", "producer") and t["type"] == "EMAIL" and t["at"] < e["at"]]
                partner = before[-1]["by"] if before else None
            ans = next((t for t in touches if ends(t) >= e["at"]), None)
            # Unanswered: every message after it is the same wait.
            stop = (ans["at"] if ans["at"] > e["at"] else e["at"]) if ans else end
            run = [x for x in evs[i:] if x["kind"] == "in" and x["at"] <= max(stop, e["at"]) and x["at"] <= end] or [e]
            i = evs.index(run[-1]) + 1
            if partner not in stats:
                continue
            said = " / ".join(x["text"] or ("(picture)" if x.get("media") else "") for x in run if x["text"] or x.get("media"))[:SAID]
            optout = any(msg.OPT_OUT.match(x["text"] or "") for x in run)
            ack = not optout and all(is_ack(x["text"]) for x in run if x["text"]) and any(x["text"] for x in run)
            # A reply is renewal business when the customer's words are, or
            # it answers a text of ours about the renewal (a reminder).
            last_out = next((t for t in reversed(evs[:evs.index(e)]) if t["kind"] in ("sent", "auto")), None)
            ren = ren_caller or any(RENEWAL_WORDS.search(x["text"] or "") for x in run) or bool(
                last_out and RENEWAL_WORDS.search((last_out.get("subject") or "") + " " + (last_out["text"] or "")))
            row = dict(who_link, who=partner, day=day, number=n, renewal=ren,
                       at=e["at"].strftime("%H:%M") if e["at"].date().isoformat() == day else e["at"].strftime("%m-%d %H:%M"),
                       channel="email" if e["type"] == "EMAIL" else "text", said=said, messages=len(run),
                       optout=optout, ack=ack, answered_by=None, via=None, minutes=None)
            stats[partner]["replies"] += 1
            if optout:
                stats[partner]["optouts"] += 1
            elif ack:
                stats[partner]["acks"] += 1
            elif ans:
                clock = max(e["at"], opens_at)
                row.update(answered_by=ans["by"] or None,
                           via={"TEXT": "text", "EMAIL": "email", "CALL": "call"}.get(ans["type"], ans["type"]),
                           minutes=max(0, int((ans["at"] - clock).total_seconds() // 60)))
                stats[partner]["answered"] += 1
            else:
                stats[partner]["unanswered"] += 1
            replies.append(row)

    replies.sort(key=lambda r: (r["minutes"] is not None, r["day"], r["at"]))
    sent_rows.sort(key=lambda r: r["at"])
    log(f"  service messages: {sum(s['texts'] for s in stats.values())} texts and "
        f"{sum(s['emails'] for s in stats.values())} emails typed to customers, "
        f"{sum(s['replies'] for s in stats.values())} replies "
        f"({sum(s['unanswered'] for s in stats.values())} unanswered)")
    return {"window": [start.isoformat(), end.isoformat()], "people": {p: dict(c) for p, c in stats.items()},
            "replies": replies, "sent": sent_rows}



# ---- the text archive, for renewal outcomes --------------------------------
# Renewal SRs are read with the customer's texts beside the rep's note (Frank,
# 2026-09-27: "i want the texts to be used to help decide"), and a renewal SR
# is open ~45 days, with past days re-read for 120 -- longer than any one
# day's window. So every text on the service lines is kept in one archive
# (data/ + an R2 copy, like the note reads), topped up from RingCentral at
# most every ARCHIVE_STALE_HOURS and trimmed to ARCHIVE_DAYS. Stored redacted.
ARCHIVE_FILE = ROOT / "data/rc_texts_archive.json"
ARCHIVE_R2_KEY = "cache/rc_texts_archive.json"
ARCHIVE_DAYS = 240
ARCHIVE_STALE_HOURS = 12
ARCHIVE_SEED_FROM = "2026-03-01"
TEXT_WINDOW_AFTER = 3        # days after the SR closed that still count


def _z(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_archive(log=log):
    if ARCHIVE_FILE.exists():
        return json.loads(ARCHIVE_FILE.read_text())
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=ARCHIVE_R2_KEY)["Body"].read()
        ARCHIVE_FILE.parent.mkdir(exist_ok=True)
        ARCHIVE_FILE.write_bytes(body)
        return json.loads(body)
    except Exception:
        return {"texts": [], "updated": None}


def update_archive(log=log, force=False):
    """Top the archive up from RingCentral (from the newest text it holds,
    less a day, so late delivery statuses land) and trim it. Never raises:
    a failed pull keeps the archive as it was."""
    arc = load_archive(log=log)
    now = dt.datetime.now(AZ)
    upd = arc.get("updated")
    if not force and upd and now - dt.datetime.fromisoformat(upd) < dt.timedelta(hours=ARCHIVE_STALE_HOURS):
        return arc
    try:
        from rc_client import RingCentral
        rc = RingCentral()
        last = max((t["at"] for t in arc["texts"]), default=None)
        since = (dt.datetime.fromisoformat(last.replace("Z", "+00:00")) - dt.timedelta(days=1)) if last \
            else dt.datetime.fromisoformat(ARCHIVE_SEED_FROM + "T00:00:00-07:00")
        names = {eid: v["name"] for eid, v in rc.roster().items()}
        got = {t["id"]: t for t in arc["texts"]}
        n0 = len(got)
        for eid, who in names.items():
            if who in _team():
                for r in rc.texts(eid, _z(since), _z(now + dt.timedelta(minutes=5))):
                    s = _slim(r, who)
                    got[s["id"]] = s
        cut = _z(now - dt.timedelta(days=ARCHIVE_DAYS))
        arc = {"texts": sorted((t for t in got.values() if t["at"] >= cut), key=lambda t: t["at"]),
               "updated": now.isoformat(timespec="seconds")}
        ARCHIVE_FILE.parent.mkdir(exist_ok=True)
        ARCHIVE_FILE.write_text(json.dumps(arc))
        try:
            import publish_board
            cli, bucket = publish_board._client()
            cli.put_object(Bucket=bucket, Key=ARCHIVE_R2_KEY, Body=ARCHIVE_FILE.read_bytes(),
                           ContentType="application/json")
        except Exception as e:
            log(f"  text archive: R2 copy not saved ({type(e).__name__})")
        log(f"  text archive: {len(arc['texts']) - n0:+d} texts, {len(arc['texts'])} kept")
    except Exception as e:
        log(f"  text archive: not topped up ({type(e).__name__}: {str(e)[:120]}) -- using what it has")
    return arc


def renewal_texts(srs, log=log):
    """{sr id: the customer's texts with the service lines while the SR was
    open (created -> completed + TEXT_WINDOW_AFTER days)}, oldest first, one
    line each, for renewal_notes.read(). Only SRs where the customer wrote
    back or someone typed to them: automation alone is no conversation and
    adds nothing to a read."""
    if not srs:
        return {}
    arc = update_archive(log=log)
    try:
        custs = {str(c["id"]): c for c in json.loads((ROOT / "data/az_customers_all.json").read_text())}
    except Exception:
        return {}
    sent_to = collections.defaultdict(set)
    by_num = collections.defaultdict(list)
    for t in arc["texts"]:
        if not t.get("number"):
            continue
        by_num[t["number"]].append(t)
        if not t["in"] and not t["media"] and t["text"]:
            sent_to[(t["who"], _norm_body(t["text"]))].add(t["number"])
    templates = {k for k, v in sent_to.items() if len(v) >= TEMPLATE_NUMBERS}
    out = {}
    for sr in srs:
        c = custs.get(str(sr.get("householdId")))
        if not c:
            continue
        nums = {norm(c.get("phone")), norm(c.get("secondaryPhone"))} - {None}
        lo = str(sr.get("createDate") or sr.get("completeDate") or "")[:10]
        done = str(sr.get("completeDate") or "")[:10]
        if not (lo and done):
            continue
        hi = (dt.date.fromisoformat(done) + dt.timedelta(days=TEXT_WINDOW_AFTER)).isoformat()
        lines, real = [], False
        for t in sorted((t for n in nums for t in by_num.get(n, ())), key=lambda t: t["at"]):
            at = dt.datetime.fromisoformat(t["at"].replace("Z", "+00:00")).astimezone(AZ)
            if not (lo <= at.date().isoformat() <= hi):
                continue
            body = t["text"] or ("(picture)" if t["media"] else "")
            if not body:
                continue
            if t["in"]:
                who, real = "customer", True
            elif not t["media"] and (t["who"], _norm_body(t["text"])) in templates:
                who = f"{t['who'].split()[0]} (automation)"
            else:
                who, real = t["who"].split()[0], True
            lines.append(f"{at:%m-%d %H:%M} {who}: {body[:300]}")
        if real:
            out[str(sr.get("id"))] = "\n".join(lines[-30:])
    return out


def _saved(cli, bucket, day, name):
    """A day file from data/, else from the R2 day cache (saved there too)."""
    f = ROOT / "data" / name
    if f.exists():
        return True
    import r2_cache
    try:
        f.write_bytes(cli.get_object(Bucket=bucket, Key=r2_cache._key(day, name))["Body"].read())
        return True
    except Exception:
        return False


def backfill(start, end=None, force=False, log=log):
    """Add `messages` to the published Service Center days from `start` to
    `end` (Frank, 2026-09-27: build it back to 9/1). RingCentral keeps every
    text, so a past day reads like tonight; each day's call log and open SRs
    come from its saved files (R2's day cache when not on disk). Emails need
    each customer lead's notes: every one active since `start` is read once,
    paced. Each document is backed up under
    backups/<today>-service-messages-backfill/ and ONLY its `messages` key is
    added -- every other figure stays as it went out. A day that already has
    one is left alone (`force` rebuilds it)."""
    import commercial
    import missed_call_audit as mca
    import publish_board
    import service_digest as sd
    import service_retention
    end = end or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    cli, bucket = publish_board._client()
    days = [d for d in sd._published_days(cli, bucket) if start <= d <= end]
    _, com_only = commercial.households(service_retention.load_household_map(log=log))
    first = True
    stamp = dt.date.today().isoformat()
    done = []
    for day in days:
        key = sd._key(day)
        raw = cli.get_object(Bucket=bucket, Key=key)["Body"].read()
        doc = json.loads(raw)
        if doc.get("messages") and not force:
            log(f"  {day}: already has texts and emails, left as is")
            continue
        _saved(cli, bucket, day, f"rc_raw_{day}.json")
        _saved(cli, bucket, day, f"az_service_tickets_{day}.json")
        idx, *_ = mca.build_index(day)
        if first:
            fetch_emails(day, customer_leads(idx), since=start, log=log)
            first = False
        m = build(day, idx=idx, commercial_only=com_only, log=log, download_notes=False)
        if not m:
            log(f"  {day}: texts not read, left as is")
            continue
        backup = f"backups/{stamp}-service-messages-backfill/{key}"
        try:
            cli.head_object(Bucket=bucket, Key=backup)
        except Exception:
            cli.put_object(Bucket=bucket, Key=backup, Body=raw, ContentType="application/json")
        doc["messages"] = m
        cli.put_object(Bucket=bucket, Key=key, Body=json.dumps(doc, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        done.append(day)
    log(f"  backfilled {len(done)} day(s): {', '.join(done) or 'none'}")
    return done

if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["--backfill"]:
        backfill(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None,
                 force="--force" in sys.argv)
        sys.exit(0)
    d = sys.argv[1] if len(sys.argv) > 1 else dt.date.today().isoformat()
    m = build(d, download_notes="--no-notes" not in sys.argv)
    if not m:
        print("nothing read")
        sys.exit(1)
    for p, s in m["people"].items():
        print(f"{p:20s} {s}")
    print(f"\n{len(m['replies'])} replies, {len(m['sent'])} sent")
    for r in m["replies"][:25]:
        print(" ", r["who"].split()[0], (r["name"] or "")[:22], r["at"], r["channel"], "|", r["said"][:50], "|",
              r["answered_by"], r["via"], r["minutes"], "ack" if r["ack"] else "", "STOP" if r["optout"] else "")

"""What AgencyZoom's automations actually run, rebuilt from the evidence they
leave on the leads (Frank, 2026-10-07: "how do we start building our own
workflows? or display what we currently have so we can adjust or change as
needed").

    python3 az_automations.py --fetch [--days 90]   restore the lead corpus from
                                                    R2 and download the notes of
                                                    every lead active in the last
                                                    N days (paced; a copy under a
                                                    day old is kept)
    python3 az_automations.py --build [--days 90] [--publish]
                                                    rebuild the rules from
                                                    data/notes + the corpus into
                                                    data/az_automations.json;
                                                    --publish writes it to R2 as
                                                    crm/automations.json, which
                                                    /api/crm/automations serves
    python3 az_automations.py --all [--days 90]     fetch, build, publish

AgencyZoom's API gives out the pipelines and stages but NOT its automation
rules (checked against api.agencyzoom.com's OpenAPI spec, 2026-10-06), so
what runs today is read back from what it did:

  * every automated TEXT carries `attr.triggerRuleId` -- the rule that sent
    it: its wording (names, numbers and links blanked), when it fires (the
    stage the lead sat in and how many days after entering it, how many
    days after the lead arrived, the hour), which sources it hits, how many
    leads it reached, how many wrote back within two days, how many opted
    out;
  * every drip EMAIL carries a template subject (messages.TEMPLATE_SUBJECTS,
    plus any subject sent to LEARN_LEADS+ leads with no attachment):
    the same, plus opens and bounces;
  * TASKs that repeat the same wording on LEARN_LEADS+ leads -- the task
    files the nightly saved (title) and the TASK notes on the leads;
  * Smart-Cycle: every move into Smart-Cycle, back into a cycle stage, or to
    Dead, who made it (a staff name is a person; anything else is the
    automation) and how long the lead had sat where it was.

Nothing here writes to AgencyZoom. The read is one note request per lead,
paced like messages.py's backfill (~5,000 leads for 90 days, about half an
hour); run it from the nightly's environment, never from the Worker's
address. The report names no customer: templates are blanked, and only the
counts travel.
"""
import collections
import datetime as dt
import glob
import json
import os
import pathlib
import re
import hashlib
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import staff            # noqa: E402

DATA = pathlib.Path(os.environ.get("CRM_DATA") or ROOT / "data")
OUT = DATA / "az_automations.json"
R2_KEY = "crm/automations.json"
DAYS = 90
LEARN_LEADS = 5          # a wording on this many leads is a template
REPLY_HOURS = 48
EMAIL_REPLY_HOURS = 72
STOP = re.compile(r"^\W*(stop|unsubscribe|quit|end|cancel|remove me|opt ?out)\b", re.I)
CYCLE = re.compile(r"\b(1st|2nd|3rd|first|second|third) cycle\b", re.I)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---- values ----------------------------------------------------------------------
def _local(s):
    """A note's createDate (agency-local 'YYYY-MM-DD HH:MM:SS' or ISO) -> naive local datetime."""
    s = str(s or "").strip()
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("T", " ")[:19])
    except ValueError:
        return None


def _utc_local(s):
    """An AgencyZoom record stamp (UTC) -> naive local datetime."""
    import crm_import
    v = crm_import.local_dt(s)
    return dt.datetime.fromisoformat(v) if v else None


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None


def _top(counter, n=5):
    return [{"name": k, "n": v} for k, v in counter.most_common(n)]


def _hist(xs, edges=(0, 1, 2, 3, 5, 7, 14, 30)):
    """Days -> buckets: 'same day', '1', '2', '3-4', '5-6', '7-13', '14-29', '30+'."""
    labels = ["same day", "1 day", "2 days", "3-4 days", "5-6 days", "7-13 days", "14-29 days", "30+ days"]
    out = collections.Counter()
    for x in xs:
        if x is None:
            continue
        k = len(edges) - 1
        for i in range(len(edges) - 1):
            if x < edges[i + 1]:
                k = i
                break
        out[labels[k]] += 1
    return [{"name": k, "n": v} for k, v in sorted(out.items(), key=lambda kv: labels.index(kv[0]))]


_STAFF_FULL = sorted({p["name"] for p in staff.PEOPLE if p.get("name")}, key=len, reverse=True)
_STAFF_FIRST = sorted({p["name"].split()[0] for p in staff.PEOPLE if p.get("name")}, key=len, reverse=True)
_STAFF_SET = {n.lower() for n in _STAFF_FULL}


def _blank(text, lead=None):
    """A template: the lead's and the staff's names, numbers, links and
    dates blanked, so nothing personal travels and the same rule reads the
    same on every lead."""
    import live_contact as lc
    t = lc._text(text or "")
    for who in _STAFF_FULL:
        t = re.sub(r"\b" + re.escape(who) + r"\b", "{producer}", t, flags=re.I)
    for who in _STAFF_FIRST:
        t = re.sub(r"\b" + re.escape(who) + r"\b", "{producer}", t, flags=re.I)
    if lead:
        for k, tag in (("firstname", "{first}"), ("lastname", "{last}")):
            v = str(lead.get(k) or "").strip()
            if len(v) >= 2:
                t = re.sub(r"\b" + re.escape(v) + r"\b", tag, t, flags=re.I)
    # a signature or a sign-off names whoever's automation it was, past staff
    # included ("~ Erick Gutierrez - Flores Insurance Agency", "Completed by X Y")
    t = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+(?=\s*[,~-]*\s*(with |from |at |-\s*)?(Flores|Farmers|" + re.escape(staff.AGENCY.get("short_name", "Flores")) + r"))", "{producer}", t)
    t = re.sub(r"(?i)(completed by )[A-Z][a-z]+ [A-Z][a-z]+", r"\1{producer}", t)
    t = re.sub(r"https?://\S+|www\.\S+", "{link}", t)
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "{email}", t)
    t = re.sub(r"\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b", "{phone}", t)
    t = re.sub(r"\$\s?\d[\d,]*(\.\d+)?", "{$}", t)
    t = re.sub(r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b", "{date}", t)
    t = re.sub(r"\b\d{4,}\b", "{n}", t)
    return re.sub(r"\s+", " ", t).strip()[:400]


def _hkey(text):
    """A stable short key for a wording (Python's hash() changes per process)."""
    return hashlib.sha1(text.encode()).hexdigest()[:10]


def _actor(move_body):
    """Who made a MOVE_STAGE: the 'by <Name>' in the note; a staff name is a
    person, anything else (AgencyZoom, Automation, Smart Cycle, nobody) is
    the automation."""
    m = re.search(r" by (.+?)(?: Loss Reason:| Comments:|$)", move_body or "")
    who = (m.group(1).strip() if m else "") or "AgencyZoom"
    return who, (who.lower() in _STAFF_SET)


# ---- the inputs ---------------------------------------------------------------------
def restore(log=log):
    """The lead corpus (the newest snapshot in R2), the stage map and the
    lead sources, into data/."""
    import r2_cache
    import publish_board
    DATA.mkdir(exist_ok=True)
    today = staff.today()
    for back in range(10):
        day = (dt.date.fromisoformat(today) - dt.timedelta(days=back)).isoformat()
        if r2_cache.load_corpus(day, log=log):
            log(f"  corpus: {day}'s snapshot")
            break
    else:
        raise RuntimeError("no corpus snapshot in R2 in the last 10 days")
    cli, bucket = publish_board._client()

    def pull(key, name):
        try:
            (DATA / name).write_bytes(cli.get_object(Bucket=bucket, Key=key)["Body"].read())
            return True
        except Exception:
            return False
    pull("worker-private/lead_sources.json", "az_lead_sources.json")
    for back in range(45):
        d = (dt.date.fromisoformat(today) - dt.timedelta(days=back)).isoformat()
        pull(f"cache/{d}/az_tasks_{d}.json", f"az_tasks_{d}.json")
    if not (DATA / "az_pipelines.json").exists():
        from az_client import AgencyZoom
        pipes = AgencyZoom().pipelines_and_stages()
        (DATA / "az_pipelines.json").write_text(json.dumps(pipes))
    if not (DATA / "az_stages.json").exists():
        stages = {}
        for w in json.loads((DATA / "az_pipelines.json").read_text()) or []:
            for st in w.get("stages") or []:
                if st.get("id"):
                    stages[str(st["id"])] = f"{w.get('name')} | {st.get('name')}"
        (DATA / "az_stages.json").write_text(json.dumps(stages))


def leads_active(days):
    leads = json.loads((DATA / "az_leads_all.json").read_text())
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    return leads, [l["id"] for l in leads if str(l.get("lastActivityDate") or "").replace("T", " ") >= since]


def fetch(days=DAYS, log=log):
    import messages
    leads, ids = leads_active(days)
    log(f"  {len(ids):,} leads active in the last {days} days of {len(leads):,}")
    messages._fetch_notes_paced(ids, fresh_after=time.time() - 24 * 3600, log=log)
    return ids


# ---- the rebuild --------------------------------------------------------------------
class Rule:
    def __init__(self, kind, key, title):
        self.kind, self.key, self.title = kind, key, title
        self.fired = 0
        self.leads = set()
        self.bodies = collections.Counter()
        self.sources = collections.Counter()
        self.stages = collections.Counter()
        self.by = collections.Counter()
        self.hours = collections.Counter()
        self.days_in_stage = []
        self.days_since_arrival = []
        self.replied = 0
        self.opted_out = 0
        self.opened = 0
        self.bounced = 0
        self.first = self.last = None

    def hit(self, when, lead, body, source, stage, entered, arrived, by):
        self.fired += 1
        self.leads.add(lead)
        if body:
            self.bodies[body] += 1
        self.sources[source or "(no source)"] += 1
        self.stages[stage or "(unknown)"] += 1
        self.by[by or "(nobody)"] += 1
        if when:
            self.hours[when.hour] += 1
            d = when.strftime("%Y-%m-%d")
            self.first = d if not self.first or d < self.first else self.first
            self.last = d if not self.last or d > self.last else self.last
            if entered:
                self.days_in_stage.append(round((when - entered).total_seconds() / 86400, 1))
            if arrived:
                self.days_since_arrival.append(round((when - arrived).total_seconds() / 86400, 1))

    def out(self):
        n = self.fired or 1
        peak = self.hours.most_common(1)
        return {
            "key": self.key, "kind": self.kind, "title": self.title,
            "template": self.bodies.most_common(1)[0][0] if self.bodies else None,
            "variants": len(self.bodies),
            "fired": self.fired, "leads": len(self.leads),
            "first": self.first, "last": self.last,
            "stages": _top(self.stages), "sources": _top(self.sources), "by": _top(self.by, 3),
            "days_in_stage": {"median": _median(self.days_in_stage), "hist": _hist(self.days_in_stage)},
            "days_since_arrival": {"median": _median(self.days_since_arrival), "hist": _hist(self.days_since_arrival)},
            "peak_hour": peak[0][0] if peak else None,
            "replied": self.replied, "replied_pct": round(100 * self.replied / n),
            "opted_out": self.opted_out,
            "opened": self.opened, "bounced": self.bounced,
        }


def _timeline(notes):
    """[(t, from, to, who, is_person)] oldest first from the MOVE_STAGE notes."""
    import live_contact as lc
    import pipelines
    out = []
    for n in notes:
        if n.get("type") != "MOVE_STAGE":
            continue
        txt = lc._text(n.get("body"))
        move, _ = lc._move_stage_parts(txt)
        m = pipelines.parse_move(move)
        t = _local(n.get("createDate"))
        if m and t:
            who, person = _actor(move)
            out.append((t, m["from"], m["to"], who, person))
    out.sort(key=lambda x: x[0])
    return out


def _where(timeline, t, now_stage, arrived):
    """(stage the lead sat in at t, when it entered it)."""
    before = [m for m in timeline if m[0] <= t]
    if before:
        return before[-1][2], before[-1][0]
    after = [m for m in timeline if m[0] > t]
    if after:
        st = after[0][1]
        return st, (arrived if re.search(r"\| New$", st or "") else None)
    # never moved on record: it has sat where it is since it arrived only if
    # that is an entry stage; a lead in a cycle stage with no move notes got
    # there by a bulk move nobody noted, so when it arrived there is unknown
    return now_stage or "", (arrived if re.search(r"\| New$", now_stage or "") or not now_stage else None)


def build(days=DAYS, log=log):
    import messages
    import live_contact as lc
    leads = {l["id"]: l for l in json.loads((DATA / "az_leads_all.json").read_text())}
    stages = json.loads((DATA / "az_stages.json").read_text()) if (DATA / "az_stages.json").exists() else {}
    src_names = {}
    p = DATA / "az_lead_sources.json"
    if p.exists():
        raw = json.loads(p.read_text())
        names = raw.get("names") if isinstance(raw, dict) else None
        if isinstance(names, dict):
            src_names = {int(k): v for k, v in names.items() if str(k).isdigit()}
        elif isinstance(raw, list):
            src_names = {int(x["id"]): x.get("name") for x in raw if x.get("id")}
    since = dt.datetime.now() - dt.timedelta(days=days)

    texts, emails, tasks = {}, {}, {}
    cycles = {"to_smart_cycle": Rule("cycle", "cycle:park", "Parked in Smart-Cycle"),
              "back_in": Rule("cycle", "cycle:back", "Brought back from Smart-Cycle"),
              "dead": Rule("cycle", "cycle:dead", "Deaded")}
    transitions = collections.Counter()
    actors = collections.Counter()
    parked_days = collections.defaultdict(list)     # target stage -> days parked
    learn = collections.defaultdict(set)
    files = sorted(glob.glob(str(DATA / "notes" / "*.json")))
    read = 0
    per_lead = []
    for f in files:
        try:
            lid = int(pathlib.Path(f).stem)
        except ValueError:
            continue
        lead = leads.get(lid)
        if not lead:
            continue
        try:
            notes = json.loads(pathlib.Path(f).read_text()) or []
        except Exception:
            continue
        read += 1
        per_lead.append((lid, lead, notes))
        first = str(lead.get("firstname") or "").strip()
        for n in notes:
            a = n.get("attr") or {}
            if n.get("type") == "EMAIL" and a.get("outbound") and not a.get("attachments") and not messages._is_reply_subject(n):
                learn[messages._subject_key(n, first)].add(lid)
    templates = set(messages.TEMPLATE_SUBJECTS) | {k for k, v in learn.items() if k and len(v) >= LEARN_LEADS}

    task_bodies = collections.defaultdict(lambda: Rule("task", "", ""))
    for lid, lead, notes in per_lead:
        notes = [n for n in notes if _local(n.get("createDate"))]
        notes.sort(key=lambda n: _local(n.get("createDate")))
        arrived = _utc_local(lead.get("createDate"))
        now_stage = stages.get(str(lead.get("workflowStageId") or ""), "")
        source = lead.get("leadSourceName") or src_names.get(lead.get("leadSourceId")) or ""
        tl = _timeline(notes)
        inbound_texts = [(_local(n["createDate"]), lc._text(n.get("body"))) for n in notes
                         if n.get("type") == "TEXT" and messages._inbound(n.get("attr") or {})]
        inbound_any = inbound_texts + [(_local(n["createDate"]), "") for n in notes
                                       if n.get("type") == "EMAIL" and messages._inbound(n.get("attr") or {})]
        for n in notes:
            t = _local(n.get("createDate"))
            if t < since:
                continue
            a = n.get("attr") or {}
            typ = n.get("type")
            if typ == "TEXT" and a.get("triggerRuleId") and not messages._inbound(a):
                rid = str(a["triggerRuleId"])
                r = texts.setdefault(rid, Rule("text", f"text:{rid}", f"Text rule {rid}"))
                stage, entered = _where(tl, t, now_stage, arrived)
                r.hit(t, lid, _blank(n.get("body"), lead), source, stage, entered, arrived, (n.get("createdBy") or "").strip())
                reps = [b for (rt, b) in inbound_texts if t < rt <= t + dt.timedelta(hours=REPLY_HOURS)]
                if reps:
                    r.replied += 1
                    if any(STOP.match(b or "") for b in reps):
                        r.opted_out += 1
            elif typ == "EMAIL" and a.get("outbound") and not messages._inbound(a):
                key = messages._subject_key(n, str(lead.get("firstname") or "").strip())
                if key in templates and not a.get("attachments") and not messages._is_reply_subject(n):
                    r = emails.setdefault(key, Rule("email", f"email:{_hkey(key)}", _blank(a.get("emailSubject") or key, lead)[:120]))
                    stage, entered = _where(tl, t, now_stage, arrived)
                    r.hit(t, lid, _blank(a.get("emailSnippet") or n.get("body"), lead), source, stage, entered, arrived, (n.get("createdBy") or "").strip())
                    if a.get("lastOpenDate"):
                        r.opened += 1
                    if a.get("bounced"):
                        r.bounced += 1
                    if any(t < rt <= t + dt.timedelta(hours=EMAIL_REPLY_HOURS) for (rt, _) in inbound_any):
                        r.replied += 1
            elif typ == "TASK":
                body = _blank(n.get("body"), lead)
                body = re.sub(r"completed by \{producer\}", "", body, flags=re.I).strip(" .~-")
                if body:
                    r = task_bodies[body]
                    r.key, r.title = "task:" + _hkey(body), body[:90]
                    stage, entered = _where(tl, t, now_stage, arrived)
                    r.hit(t, lid, body, source, stage, entered, arrived, lc.task_note_parts(n.get("body"))[0])
        # Smart-Cycle and the moves
        prev_t = arrived
        for (t, frm, to, who, person) in tl:
            if t >= since:
                transitions[(frm, to, "person" if person else "automation")] += 1
                actors[who] += 1
                stage_days = round((t - prev_t).total_seconds() / 86400, 1) if prev_t else None
                if to == "Smart-Cycle":
                    r = cycles["to_smart_cycle"]
                    r.hit(t, lid, None, source, frm, prev_t, arrived, who)
                elif frm == "Smart-Cycle" or CYCLE.search(to or ""):
                    r = cycles["back_in"]
                    r.hit(t, lid, None, source, to, prev_t, arrived, who)
                    if stage_days is not None:
                        parked_days[to].append(stage_days)
                elif to == "Dead":
                    r = cycles["dead"]
                    r.hit(t, lid, None, source, frm, prev_t, arrived, who)
            prev_t = t

    # the saved task files: titles that repeat
    task_titles = collections.defaultdict(lambda: Rule("task", "", ""))
    seen_tasks = set()
    for f in sorted(glob.glob(str(DATA / "az_tasks_*.json"))):
        try:
            rows = json.loads(pathlib.Path(f).read_text())
        except Exception:
            continue
        for t in (rows.values() if isinstance(rows, dict) else rows or []):
            tid = t.get("id")
            if not tid or tid in seen_tasks:
                continue
            seen_tasks.add(tid)
            title = _blank(t.get("title"))
            if not title:
                continue
            r = task_titles[title]
            r.key, r.title = "tasktitle:" + _hkey(title), title[:90]
            when = _utc_local(t.get("createDate")) or _utc_local(t.get("dueDate"))
            lead = leads.get(t.get("customerId")) if t.get("customerType") == "lead" else None
            arrived = _utc_local(lead.get("createDate")) if lead else None
            assignee = t.get("assigneeId") or ((t.get("assignees") or [{}])[0].get("id") if t.get("assignees") else None)
            who = next((p["name"] for p in staff.PEOPLE if p.get("az_id") == assignee), str(assignee or ""))
            r.hit(when, t.get("customerId") or tid, title, (lead or {}).get("leadSourceName") or "", "", None, arrived, who)

    def rules_out(d, min_fired=1):
        return sorted((r.out() for r in d.values() if r.fired >= min_fired), key=lambda x: -x["fired"])
    report = {
        "built": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "days": days, "since": since.strftime("%Y-%m-%d"),
        "leads_read": read, "leads_in_corpus": len(leads),
        "texts": rules_out(texts),
        "emails": rules_out(emails),
        "tasks": rules_out(task_titles, LEARN_LEADS) + rules_out(task_bodies, LEARN_LEADS),
        "cycles": [r.out() for r in cycles.values()],
        "parked_days": {k: {"median": _median(v), "n": len(v)} for k, v in parked_days.items()},
        "transitions": [{"from": f, "to": t, "who": w, "n": n} for (f, t, w), n in transitions.most_common(40)],
        "actors": _top(actors, 12),
    }
    return report


def publish(report, log=log):
    import publish_board
    cli, bucket = publish_board._client()
    cli.put_object(Bucket=bucket, Key=R2_KEY, Body=json.dumps(report, separators=(",", ":")).encode(), ContentType="application/json")
    log(f"  published to R2 {R2_KEY}")


if __name__ == "__main__":
    a = sys.argv[1:]
    days = int(a[a.index("--days") + 1]) if "--days" in a else DAYS
    if not a or not any(x in a for x in ("--fetch", "--build", "--all")):
        print(__doc__)
        sys.exit(2)
    if "--fetch" in a or "--all" in a:
        import secrets_load
        try:
            secrets_load.load()
        except SystemExit:
            pass
        restore()
        fetch(days)
    if "--build" in a or "--all" in a:
        rep = build(days)
        DATA.mkdir(exist_ok=True)
        OUT.write_text(json.dumps(rep, indent=1))
        log(f"  {OUT}: {len(rep['texts'])} text rules, {len(rep['emails'])} email templates, {len(rep['tasks'])} task templates, "
            f"{sum(c['fired'] for c in rep['cycles'])} cycle moves, from {rep['leads_read']:,} leads' notes")
        if "--publish" in a or "--all" in a:
            publish(rep)

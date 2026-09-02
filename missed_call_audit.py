"""Missed-call audit: who rang and got no answer, where the task would go.

    python3 missed_call_audit.py                 # today, Arizona
    python3 missed_call_audit.py --day 2026-08-28
    python3 missed_call_audit.py --no-refresh    # use the cached call log

Reports only. It creates NOTHING in AgencyZoom. The rules it applies are the
ones settled in HOURLY_RUNS.md sections 1-6; this is the read-only half, so the
routing and the volume can be watched for a while before anything is written.

Writes out/Missed_Call_Audit_<day>.html.

REACHING BACK BY TEXT COUNTS. Frank asked, 2026-09-01. It very nearly did not:
`/v1/api/leads/{id}/notes` on a customer or household id returns only
lifecycle events, no messages, which looked like customers having no
conversation history at all. They do -- it hangs off their LEAD records, and a
customer who converted from a lead still has them. Match the caller's number
against the leads corpus, read the notes on each lead, and the texts are there.

A reachback is an OUTBOUND text, dated after the missed call, with no
`attr.triggerRuleId` -- that field marks automation, which signs the producer's
name and must not count (HOURLY_RUNS.md s5). Measured over the corpus, 73% of
outbound texts are automation.

The gap that remains: a caller with NO lead record on that number has no
reachable message history. On 2026-09-01 that was one of eight.
"""
import argparse
import collections
import datetime as dt
import html
import json
import pathlib
import re

AZ = dt.timezone(dt.timedelta(hours=-7))
ROOT = pathlib.Path(__file__).resolve().parent
WINDOW_SECONDS = 3600          # one task per person per rolling hour
MISSED = ("Missed", "Voicemail")


def log(*a):
    print(f"[{dt.datetime.now(AZ):%H:%M:%S}]", *a, flush=True)


def norm(p):
    d = re.sub(r"\D", "", p or "")
    return d[-10:] if len(d) >= 10 else None


def pretty(n):
    return f"({n[:3]}) {n[3:6]}-{n[6:]}" if n and len(n) == 10 else (n or "—")


def parse(s):
    try:
        return dt.datetime.fromisoformat(
            str(s).replace("Z", "+00:00").replace(" ", "T")).replace(tzinfo=None)
    except Exception:
        return None


def az(t):
    return t - dt.timedelta(hours=7) if t else None


# ---- routing ---------------------------------------------------------------

def build_index(day):
    """Phone -> records, from the cached corpus. Narrow by design.

    The hourly job will query AgencyZoom per number instead of loading all of
    this; the audit runs once and the corpus is already on disk, so it reuses it.
    """
    d = ROOT / "data"
    def load(name):
        p = d / name
        if not p.exists():
            return []
        j = json.loads(p.read_text())
        return j if isinstance(j, list) else (j.get("data") or list(j.values())[0])

    cust, leads = load("az_customers_all.json"), load("az_leads_all.json")
    tix = load(f"az_service_tickets_{day}.json")

    idx = collections.defaultdict(lambda: {"cust": [], "lead": [], "tix": []})
    for c in cust:
        for f in ("phone", "secondaryPhone"):
            n = norm(c.get(f))
            if n:
                idx[n]["cust"].append(c)
    for l in leads:
        for f in ("phone", "secondaryPhone"):
            n = norm(l.get(f))
            if n:
                idx[n]["lead"].append(l)
    for t in tix:
        n = norm(t.get("phone"))
        if n:
            idx[n]["tix"].append(t)
    return idx, len(cust), len(leads), len(tix)


def route(hit):
    """The five buckets from HOURLY_RUNS.md s2, in priority order."""
    if not hit:
        return "no record", "Debbie", "No record at all"
    open_sr = [t for t in hit["tix"] if t.get("status") == 1]
    open_lead = [l for l in hit["lead"] if l.get("status") == 0]
    if open_sr:
        who = open_sr[0].get("csrFirstname") or "the assigned CSR"
        return "open SR", who, "Open service request"
    if open_lead:
        who = open_lead[0].get("assignToFirstname") or "the lead's producer"
        return "open lead", who, "Open lead"
    if hit["cust"]:
        return "customer", "Amanda", "Customer, nothing open"
    if hit["lead"] or hit["tix"]:
        return "closed lead", "Amanda", "Closed lead, not a customer"
    return "no record", "Debbie", "No record at all"


def name_for(hit, cnam):
    for key in ("cust", "lead"):
        for r in (hit or {}).get(key, []):
            nm = " ".join(x for x in (r.get("firstname"), r.get("lastname")) if x)
            if nm.strip():
                return nm.strip()
    return (cnam or "").title() or None


# ---- the audit -------------------------------------------------------------

def collect(day, refresh=True):
    f = ROOT / f"data/rc_raw_{day}.json"
    if refresh:
        from rc_client import RingCentral
        nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
        log("re-pulling today's call log...")
        recs = RingCentral().call_log(f"{day}T00:00:00-07:00",
                                      f"{nxt}T00:00:00-07:00")
        f.write_text(json.dumps(recs))
    return json.loads(f.read_text())


def group(recs):
    """One row per caller per rolling hour (HOURLY_RUNS.md s3)."""
    by = collections.defaultdict(list)
    for r in recs:
        if r.get("direction") != "Inbound" or r.get("result") not in MISSED:
            continue
        n = norm((r.get("from") or {}).get("phoneNumber"))
        if not n:
            continue
        by[n].append(r)
    rows = []
    for n, rs in by.items():
        rs.sort(key=lambda r: r["startTime"])
        cur = [rs[0]]
        for r in rs[1:]:
            gap = (parse(r["startTime"]) - parse(cur[-1]["startTime"])).total_seconds()
            if gap <= WINDOW_SECONDS:
                cur.append(r)
            else:
                rows.append((n, cur))
                cur = [r]
        rows.append((n, cur))
    return rows


def called_after(number, when, recs):
    """Earliest outbound CALL to this number after the missed call."""
    best = None
    for r in recs:
        if r.get("direction") != "Outbound":
            continue
        if norm((r.get("to") or {}).get("phoneNumber")) != number:
            continue
        t = parse(r["startTime"])
        if t and t > when and (best is None or t < best):
            best = t
    return best


_NOTES = {}


def lead_notes(lead_id, az_client):
    if lead_id not in _NOTES:
        try:
            j = az_client.get(f"/v1/api/leads/{lead_id}/notes")
        except Exception:
            j = []
        _NOTES[lead_id] = j if isinstance(j, list) else (j.get("data") or [])
    return _NOTES[lead_id]


def texted_after(hit, when, az_client):
    """Earliest HAND-TYPED outbound text after the missed call.

    attr.triggerRuleId present means automation -- it signs the producer's name,
    so createdBy is useless and this field is the only discriminator.
    """
    best = None
    for l in (hit or {}).get("lead", []):
        for n in lead_notes(l.get("id"), az_client):
            if n.get("type") != "TEXT":
                continue
            a = n.get("attr") or {}
            if not isinstance(a, dict) or not a.get("outbound"):
                continue
            if a.get("triggerRuleId"):
                continue
            t = parse(n.get("createDate"))
            if t and t > when and (best is None or t < best):
                best = t
    return best


def build(day, refresh=True):
    from az_client import AgencyZoom
    azc = AgencyZoom()
    recs = collect(day, refresh)
    idx, nc, nl, nt = build_index(day)
    log(f"corpus: {nc} customers, {nl} leads, {nt} service tickets")
    rows = []
    for n, calls in group(recs):
        first, last = parse(calls[0]["startTime"]), parse(calls[-1]["startTime"])
        hit = idx.get(n)
        bucket, who, label = route(hit)
        cnam = (calls[0].get("from") or {}).get("name") or ""
        rows.append({
            "number": n,
            "name": name_for(hit, cnam if not cnam.isupper() else cnam),
            "cnam": cnam,
            "location": (calls[0].get("from") or {}).get("location") or "",
            "rings": len(calls),
            "vm": any(c.get("result") == "Voicemail" for c in calls),
            "first": az(first), "last": az(last),
            "bucket": bucket, "who": who, "label": label,
        })
        by_call = called_after(n, last, recs)
        # AgencyZoom note timestamps are Arizona local; the RingCentral log is
        # UTC. Compare each against its own clock or every text looks earlier
        # than the call that preceded it by seven hours.
        by_text = texted_after(hit, az(last), azc)
        best, how = None, None
        for t, kind, base in ((by_call, "call", last),
                              (by_text, "text", az(last))):
            if t and (best is None or (t - base) < best[0] - best[1]):
                best, how = (t, base), kind
        rows[-1]["back_in"] = (round((best[0] - best[1]).total_seconds() / 60)
                               if best else None)
        rows[-1]["back_how"] = how
        rows[-1]["reachable"] = bool((hit or {}).get("lead"))
    rows.sort(key=lambda r: r["first"], reverse=True)
    return rows


ORDER = ["open lead", "open SR", "customer", "closed lead", "no record"]
TINT = {"open lead": "lead", "open SR": "sr", "customer": "amanda",
        "closed lead": "former", "no record": "debbie"}


def render(day, rows):
    made = [r for r in rows if r["back_in"] is None]
    done = [r for r in rows if r["back_in"] is not None]
    counts = collections.Counter(r["bucket"] for r in made)
    times = sorted(r["back_in"] for r in done)
    median = times[len(times) // 2] if times else None

    def cells():
        out = []
        for b in ORDER:
            if not counts.get(b):
                continue
            label = next(r["label"] for r in made if r["bucket"] == b)
            who = collections.Counter(r["who"] for r in made if r["bucket"] == b)
            out.append(
                f'<div class="rcell" style="--bar:var(--{TINT[b]})">'
                f'<span class="rcount">{counts[b]}</span>'
                f'<div class="rwho">{html.escape(", ".join(sorted(who)))}</div>'
                f'<div class="rnote">{html.escape(label)}</div></div>')
        out.append(
            f'<div class="rcell"><span class="rcount">{len(done)}</span>'
            f'<div class="rwho">No task</div>'
            f'<div class="rnote">Called back already</div></div>')
        return "".join(out)

    hours = collections.Counter(r["first"].hour for r in rows)
    peak = max(hours, key=lambda h: hours[h]) if hours else None

    def hourstrip():
        if not hours:
            return ""
        top = max(hours.values())
        bars = []
        for h in range(8, 18):
            n = hours.get(h, 0)
            lab = f"{(h - 1) % 12 + 1}"
            hot = " hot" if h == peak and n > 1 else ""
            bars.append(
                f'<div class="hr{hot}"><div class="hbarwrap">'
                f'<div class="hbar" style="height:{max(3, round(n / top * 46))}px">'
                f'</div></div><div class="hn">{n or ""}</div>'
                f'<div class="hl">{lab}</div></div>')
        note = ""
        if peak == 12 and hours[12] > 1:
            note = (f'<p class="lede" style="margin-top:9px">'
                    f'<b>{hours[12]} of {len(rows)} came in during the lunch hour.</b> '
                    f'Nobody is at a desk between 12 and 1, and it shows.</p>')
        return (f'<p class="eyebrow" style="margin-top:30px">When they rang</p>'
                f'<div class="hours">{"".join(bars)}</div>{note}')

    def table(rs, handled):
        trs = []
        for r in rs:
            when = (f'{r["first"]:%-I:%M %p}' if r["rings"] == 1
                    else f'{r["first"]:%-I:%M}–{r["last"]:%-I:%M %p}')
            chips = ""
            if r["rings"] > 1:
                chips += f'<span class="chip">{r["rings"]}&times;</span>'
            if r["vm"]:
                chips += '<span class="chip vm">VM</span>'
            tail = (f'<td class="n good">{r["back_in"]} min'
                    f'<span class="how">{r["back_how"]}</span></td>' if handled
                    else f'<td class="who" style="--c:var(--{TINT[r["bucket"]]})">'
                         f'<span class="dot"></span>{html.escape(r["who"])}</td>')
            trs.append(
                f'<tr><td class="ph">{pretty(r["number"])}</td>'
                f'<td class="nm">{html.escape(r["name"] or "—")}'
                f'<span class="loc">{html.escape(r["location"])}</span></td>'
                f'<td class="when">{when} {chips}</td>{tail}</tr>')
        head = ("Called back in" if handled else "Task would go to")
        return (f'<div class="scroll"><table><thead><tr><th>Number</th>'
                f'<th>Who</th><th>When</th><th{" class=n" if handled else ""}>'
                f'{head}</th></tr></thead><tbody>{"".join(trs)}</tbody>'
                f'</table></div>')

    d = dt.date.fromisoformat(day)
    med = (f'<div class="hcell"><span class="hnum">{median}</span>'
           f'<div class="hlab">median minutes to call back</div></div>'
           if median is not None else "")
    return TEMPLATE.format(
        day=f"{d:%A, %B %-d}", n_made=len(made), n_done=len(done),
        n_total=len(rows), median=med, cells=cells(),
        hourstrip=hourstrip(), made_table=table(made, False),
        done_table=(table(done, True) if done else
                    '<p class="empty">Nobody was called back yet.</p>'),
        stamp=f"{dt.datetime.now(AZ):%-I:%M %p} Arizona")


TEMPLATE = """<title>Missed Call Audit</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Public+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
  :root{{--ground:#f6f7f9;--surface:#fff;--sunk:#eef0f4;--ink:#191c22;--muted:#5d6470;
    --faint:#8a919d;--line:#dfe3e9;--line-strong:#c6ccd6;--lead:#1d4ed8;--sr:#0f766e;
    --amanda:#7c3aed;--former:#b45309;--debbie:#b91c1c;--good:#166534;
    --amber:#9a5b06;--amber-soft:#fdf3e3;--amber-line:#e8c893}}
  @media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
    --ground:#12151a;--surface:#1a1e25;--sunk:#151920;--ink:#e7eaef;--muted:#a0a8b4;
    --faint:#79818e;--line:#2b313a;--line-strong:#3d4550;--lead:#8ab0ff;--sr:#5fd4c4;
    --amanda:#c4a2ff;--former:#f0b45f;--debbie:#ff9494;--good:#6ee7a0;
    --amber:#f0b45f;--amber-soft:#2a2114;--amber-line:#5c4519}}}}
  :root[data-theme="dark"]{{--ground:#12151a;--surface:#1a1e25;--sunk:#151920;
    --ink:#e7eaef;--muted:#a0a8b4;--faint:#79818e;--line:#2b313a;--line-strong:#3d4550;
    --lead:#8ab0ff;--sr:#5fd4c4;--amanda:#c4a2ff;--former:#f0b45f;--debbie:#ff9494;
    --good:#6ee7a0;--amber:#f0b45f;--amber-soft:#2a2114;--amber-line:#5c4519}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--ground);color:var(--ink);font-size:15px;line-height:1.55;
    font-family:'Public Sans',-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif}}
  .wrap{{max-width:940px;margin:0 auto;padding:40px 26px 70px}}
  header{{border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:26px}}
  h1{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:40px;
    line-height:1.1;margin:0 0 6px;letter-spacing:-.01em}}
  h2{{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:23px;
    margin:34px 0 4px}}
  .eyebrow{{font-size:11px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
    color:var(--faint);margin:0 0 9px}}
  .sub{{color:var(--muted);max-width:70ch;margin:0}}
  .lede{{color:var(--muted);font-size:13.5px;max-width:74ch;margin:0 0 12px}}
  .hero{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;
    background:var(--line);border:1px solid var(--line);border-radius:8px;
    overflow:hidden;margin:22px 0 6px}}
  .hcell{{background:var(--surface);padding:15px 17px}}
  .hnum{{font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:500;
    display:block;line-height:1.1;font-variant-numeric:tabular-nums}}
  .hlab{{font-size:12.5px;color:var(--muted);margin-top:4px}}
  .routing{{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:1px;
    background:var(--line);border:1px solid var(--line);border-radius:8px;
    overflow:hidden;margin:8px 0 4px}}
  .rcell{{background:var(--surface);padding:13px 15px;
    border-top:3px solid var(--bar,var(--line-strong))}}
  .rcount{{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:500;
    display:block;line-height:1.2;font-variant-numeric:tabular-nums}}
  .rwho{{font-weight:600;font-size:13px;margin-top:3px}}
  .rnote{{color:var(--muted);font-size:12.5px;margin-top:2px}}
  .scroll{{overflow-x:auto}}
  table{{width:100%;border-collapse:collapse;font-size:13.5px;min-width:620px}}
  th{{text-align:left;font-size:10px;letter-spacing:.06em;text-transform:uppercase;
    color:var(--faint);font-weight:700;padding:0 10px 6px 0;
    border-bottom:1px solid var(--line);white-space:nowrap}}
  th.n,td.n{{text-align:right;font-family:'JetBrains Mono',monospace;
    font-variant-numeric:tabular-nums}}
  td{{padding:8px 10px 8px 0;border-bottom:1px solid var(--line);vertical-align:baseline}}
  tr:last-child td{{border-bottom:none}}
  .ph{{font-family:'JetBrains Mono',monospace;white-space:nowrap}}
  .nm{{font-weight:600}}
  .loc{{display:block;font-weight:400;font-size:11.5px;color:var(--faint)}}
  .when{{color:var(--muted);white-space:nowrap;font-size:12.5px}}
  .who{{white-space:nowrap;font-weight:600}}
  .dot{{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:7px;
    background:var(--c,var(--line-strong))}}
  .good{{color:var(--good);font-weight:600}}
  .how{{display:block;font-size:10.5px;font-weight:400;color:var(--faint);
    text-transform:uppercase;letter-spacing:.05em}}
  .chip{{display:inline-block;font-size:10px;font-weight:700;letter-spacing:.04em;
    padding:1px 5px;border-radius:3px;margin-left:4px;background:var(--amber-soft);
    color:var(--amber);border:1px solid var(--amber-line)}}
  .chip.vm{{background:var(--sunk);color:var(--muted);border-color:var(--line-strong)}}
  .empty{{color:var(--faint);font-size:13.5px}}
  .hours{{display:grid;grid-template-columns:repeat(10,1fr);gap:4px;align-items:end;
    background:var(--surface);border:1px solid var(--line);border-radius:8px;
    padding:12px 14px 9px}}
  .hr{{text-align:center}}
  .hbarwrap{{height:48px;display:flex;align-items:flex-end;justify-content:center}}
  .hbar{{width:70%;background:var(--line-strong);border-radius:2px 2px 0 0}}
  .hr.hot .hbar{{background:var(--debbie)}}
  .hn{{font-family:'JetBrains Mono',monospace;font-size:11.5px;color:var(--muted);
    height:15px}}
  .hl{{font-size:10.5px;color:var(--faint)}}
  footer{{margin-top:36px;padding-top:18px;border-top:1px solid var(--line);
    color:var(--faint);font-size:12.5px;max-width:74ch}}
</style>
<div class="wrap">
  <header>
    <p class="eyebrow">Missed calls &middot; {day} &middot; as of {stamp}</p>
    <h1>Missed Call Audit</h1>
    <p class="sub">Every inbound call nobody picked up, grouped one row per person
      per hour, with where the task would have gone. Nothing was created &mdash;
      this is the read-only rehearsal.</p>
  </header>
  <div class="hero">
    <div class="hcell"><span class="hnum">{n_total}</span>
      <div class="hlab">missed callers</div></div>
    <div class="hcell"><span class="hnum">{n_made}</span>
      <div class="hlab">would have become tasks</div></div>
    <div class="hcell"><span class="hnum">{n_done}</span>
      <div class="hlab">already called back</div></div>
    {median}
  </div>
  <p class="eyebrow">Where those tasks would go</p>
  <div class="routing">{cells}</div>
  {hourstrip}
  <h2>Still waiting on us</h2>
  <p class="lede">These are the ones a task would be created for right now.</p>
  {made_table}
  <h2>Already handled</h2>
  <p class="lede">Somebody rang them back. No task &mdash; the row is the record,
    and the response time is the number worth watching.</p>
  {done_table}
  <footer>
    Missed means RingCentral logged the inbound call as Missed or Voicemail.
    Callers are grouped into one-hour windows, so five rings in forty minutes is
    one row. "Called back" counts an outbound call to that number afterwards
    &mdash; a follow-up sent only by text is not visible for customer records and
    will show here as still waiting.
  </footer>
</div>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default=None)
    ap.add_argument("--no-refresh", action="store_true")
    a = ap.parse_args()
    day = a.day or dt.datetime.now(AZ).date().isoformat()
    rows = build(day, refresh=not a.no_refresh)
    (ROOT / "out").mkdir(exist_ok=True)
    p = ROOT / f"out/Missed_Call_Audit_{day}.html"
    p.write_text(render(day, rows))
    made = sum(1 for r in rows if r["back_in"] is None)
    log(f"{len(rows)} missed callers, {made} would be tasks -> {p}")


if __name__ == "__main__":
    main()

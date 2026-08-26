# Flores digest — change set for Claude Code

Base: `main` at commit `1439bf3`. Everything below was written and verified in a
Cowork session on 2026-08-25 against the real Aug 24 data. Please apply it as-is
rather than re-deriving it — the wording, the regexes and the fallback ordering
were each settled against real calls, and several of them are there to prevent a
specific bug that already happened once.

## What to do

1. Apply the unified diff in section **A** below. It touches seven Python files
   and creates two new ones (`call_summary.py`, `overflow.py`). It does NOT touch the HTML
   template — that is section **B**, a single find-and-replace.
2. Apply section **B**.
3. Run the checks in section **C**.
4. Delete this file (`SPEC.md`) and open a PR.

If a hunk does not apply cleanly, prefer the intent described in the comments
inside the diff over a mechanical fix, and say so in the PR description.

---

## A. Code diff

Save as a file and `git apply` it, or apply by hand. Either is fine.

```diff
diff --git a/az_tasks.py b/az_tasks.py
index c95627b..3832a45 100644
--- a/az_tasks.py
+++ b/az_tasks.py
@@ -48,12 +48,24 @@ def owner(task, az_ids):
     return None
 
 
-def audit(tasks):
-    """Per-producer task completion, plus the excluded-work tally for the notes."""
+def audit(tasks, verdicts=None):
+    """Per-producer task completion, plus the excluded-work tally for the notes.
+
+    `verdicts` is {task_id: 'excluded'|'excused'} from
+    task_audit.cancellation_verdicts (Frank, 2026-08-25):
+
+      excluded -- a duplicate lead's task. Not a real task; leaves the audit
+                  entirely, like service work.
+      excused  -- the producer smart-cycled or killed the lead that day and
+                  AgencyZoom's "cancel all related open tasks" checkbox closed
+                  the task. Counted OUT of the denominator so it does not drag
+                  the rate, but still listed in audit section (d).
+    """
     az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
     per = {n: {"total": 0, "completed": 0, "closed_not_done": 0, "open": 0,
-               "outstanding": []} for n in PRODUCERS}
-    excluded = {"customer record": 0, "title": 0, "body": 0}
+               "excused": 0, "outstanding": []} for n in PRODUCERS}
+    excluded = {"customer record": 0, "title": 0, "body": 0, "duplicate lead": 0}
+    verdicts = verdicts or {}
 
     for t in tasks:
         reason = service_reason(t)
@@ -65,7 +77,15 @@ def audit(tasks):
         who = owner(t, az_ids)
         if not who:
             continue
+        v = verdicts.get(t.get("id"))
+        if v == "excluded":
+            excluded["duplicate lead"] += 1
+            continue
         p = per[who]
+        if v == "excused":
+            # Out of the denominator entirely -- neither a pass nor a fail.
+            p["excused"] += 1
+            continue
         p["total"] += 1
         if t.get("status") == STATUS_COMPLETED:
             p["completed"] += 1
diff --git a/call_summary.py b/call_summary.py
new file mode 100644
index 0000000..b236cd0
--- /dev/null
+++ b/call_summary.py
@@ -0,0 +1,303 @@
+"""Per-call summary and objection read for the Call Detail panel.
+
+Frank, 2026-08-25: "instead of the first sentence of the transcript in the call
+detail, can you give me a summary of what you transcribed, if the lead gave an
+objection or not, if the producer attempted to overcome that objection, and if
+they were successful or not".
+
+WHAT THIS NEEDS THAT THE REST OF THE PIPELINE DID NOT
+-----------------------------------------------------
+transcribe_file reads only the first and last 30 seconds, which is all the
+live/voicemail classification ever needed. An objection and its rebuttal live in
+the MIDDLE: Allen Lawson's "I told her I didn't want to give somebody all the
+same damn information again" sits four minutes into a 393-second call. So this
+module drives transcribe.transcribe_full over the whole recording, for LIVE
+CONTACTS ONLY -- 58 minutes of audio across 21 calls on 2026-08-24, about ten
+minutes of compute, against 75 minutes for every dial.
+
+WHEN THE TRANSCRIPT CANNOT CARRY IT
+-----------------------------------
+Whisper base int8 is fine on English and collapses on Spanish. Abel Ramos's
+201-second call came back as "(speaking in foreign language)" and then the word
+"Okay" about two hundred times. Three of 2026-08-24's 21 transcribed live
+contacts were Spanish-tagged and one more was an English repetition loop, so
+roughly a fifth of the book cannot be summarised from audio at all.
+
+Frank's call: fall back to the producer's own notes rather than print nothing.
+`source` on every row says which it was, so a reader always knows whether they
+are looking at the recording or at what the producer typed.
+
+WHY A MODEL CALL AND NOT A PATTERN
+----------------------------------
+"Did the producer attempt to overcome the objection, and did it work" is not a
+keyword question. The API key lives in secrets/all.env as ANTHROPIC_API_KEY. If
+it is absent the module degrades to producer notes for every row and says so --
+the build never fails over this.
+"""
+import json
+import os
+import pathlib
+import re
+
+import requests
+
+import transcribe as T
+
+ROOT = pathlib.Path(__file__).resolve().parent
+
+# A transcript has to clear all three to be worth sending to the model.
+MIN_CHARS = 120           # under this there is nothing to summarise
+MAX_REPEAT_RATIO = 0.35   # one word eating a third of the text is a loop
+MAX_FOREIGN_SHARE = 0.25  # mostly "(speaking in foreign language)" is unusable
+
+API_URL = "https://api.anthropic.com/v1/messages"
+MODELS_URL = "https://api.anthropic.com/v1/models"
+API_VERSION = "2023-06-01"
+TIMEOUT = 90
+
+
+
+def _key():
+    return (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
+
+
+def usable(text):
+    """(ok, reason) -- can this transcript support a summary?"""
+    t = (text or "").strip()
+    if len(t) < MIN_CHARS:
+        return False, "transcript too short"
+    foreign = sum(len(m.group(0)) for m in T.FOREIGN.finditer(t))
+    if foreign / len(t) > MAX_FOREIGN_SHARE:
+        return False, "not transcribable (foreign language)"
+    if T.repetition_ratio(t) > MAX_REPEAT_RATIO:
+        return False, "transcription broke down (repetition loop)"
+    return True, ""
+
+
+def pick_model():
+    """Newest Sonnet the account can see.
+
+    Deliberately discovered rather than hardcoded -- a pinned model id rots, and
+    this build runs unattended every weekday. ANTHROPIC_MODEL overrides.
+    """
+    override = (os.environ.get("ANTHROPIC_MODEL") or "").strip()
+    if override:
+        return override
+    try:
+        r = requests.get(MODELS_URL, timeout=30, headers={
+            "x-api-key": _key(), "anthropic-version": API_VERSION})
+        r.raise_for_status()
+        ids = [m["id"] for m in r.json().get("data", [])]
+        for want in ("sonnet", "opus", "haiku"):
+            hit = [i for i in ids if want in i.lower()]
+            if hit:
+                return hit[0]
+    except Exception:
+        pass
+    return "claude-sonnet-4-5"
+
+
+SYSTEM = """You read one sales call from an insurance agency and report what \
+happened. You are given a machine transcript that is often noisy: words are \
+misheard, speaker turns are not marked, and both sides may be paraphrased badly.
+
+Return ONLY a JSON object, no prose around it, with exactly these keys:
+
+  "summary"     2 sentences max, plain past tense, what the call was about and \
+how it ended. Name what the prospect actually said. Do not pad.
+  "objections"  a JSON array, one entry per objection the PROSPECT raised, in \
+the order they came up. Empty array if they raised none. At most 3 entries. \
+Each entry is an object with exactly these keys:
+      "objection"  the objection in your own words, 12 words or fewer
+      "addressed"  "yes" if the producer engaged it -- gave a reason, offered \
+an alternative, or asked a question to open it back up. "no" if the producer \
+acknowledged it and moved on, or ignored it.
+      "overcome"   "yes" if the prospect moved on that specific point, "no" if \
+they held it, "unclear" if the transcript does not settle it.
+
+Rules that matter more than being helpful:
+- MERGE near-duplicates into one entry before you count. "Too expensive" and \
+"can't afford it right now" are ONE objection, not two. So are "I'm with \
+State Farm" and "I already have insurance".
+- If more than 3 distinct objections survive merging, return the 3 that got \
+the most discussion and mention the rest in the summary sentence.
+- A noisy transcript is a reason to answer "unclear", not to guess. Being \
+wrong here is worse than being uninformative.
+- "addressed" is about effort, "overcome" is about result. A producer can \
+address an objection well and still lose it. Do not let one answer drag the \
+other.
+- Never invent a name, price, coverage or date that is not in the input.
+- "not interested" with no reason given IS an objection.
+- Do not treat the producer's own pitch as something the prospect said."""
+
+
+MAX_OBJECTIONS = 3
+
+
+def _clean_objections(raw):
+    """Normalise and cap whatever the model returned."""
+    out = []
+    for o in (raw or [])[:MAX_OBJECTIONS]:
+        if not isinstance(o, dict):
+            continue
+        txt = str(o.get("objection") or "").strip()
+        if not txt or txt.lower() in ("none", "n/a"):
+            continue
+        a = str(o.get("addressed") or "").strip().lower()
+        oc = str(o.get("overcome") or "").strip().lower()
+        out.append({"objection": txt,
+                    "addressed": a if a in ("yes", "no") else "no",
+                    "overcome": oc if oc in ("yes", "no", "unclear") else "unclear"})
+    return out
+
+
+def upgrade(d):
+    """Read a row written before objections became a list.
+
+    The cache on disk survives a deploy, so old single-objection rows have to
+    keep rendering. One scalar objection becomes a one-entry list; "none"
+    becomes an empty list, which is exactly how a no-objection call is stored
+    now.
+    """
+    if not isinstance(d, dict) or "objections" in d:
+        return d
+    d = dict(d)
+    obj = str(d.pop("objection", "") or "").strip()
+    att = str(d.pop("attempted", "") or "").strip().lower()
+    oc = str(d.pop("outcome", "") or "").strip().lower()
+    if obj and obj.lower() not in ("none", "n/a", ""):
+        d["objections"] = [{"objection": obj,
+                            "addressed": "yes" if att == "yes" else "no",
+                            "overcome": oc if oc in ("yes", "no", "unclear")
+                            else "no" if oc == "not overcome"
+                            else "yes" if oc == "overcome" else "unclear"}]
+    else:
+        d["objections"] = []
+    return d
+
+
+def _ask(model, transcript, notes, seconds):
+    body = {
+        "model": model,
+        "max_tokens": 600,
+        "system": SYSTEM,
+        "messages": [{"role": "user", "content":
+                      f"Call length: {seconds} seconds\n\n"
+                      f"Producer's own notes (may be empty):\n{notes or '(none)'}\n\n"
+                      f"Machine transcript:\n{transcript}"}],
+    }
+    r = requests.post(API_URL, json=body, timeout=TIMEOUT, headers={
+        "x-api-key": _key(), "anthropic-version": API_VERSION,
+        "content-type": "application/json"})
+    r.raise_for_status()
+    text = "".join(b.get("text", "") for b in r.json().get("content", []))
+    m = re.search(r"\{.*\}", text, re.S)
+    if not m:
+        raise ValueError("no JSON in response")
+    d = json.loads(m.group(0))
+    return {"summary": str(d.get("summary") or "").strip(),
+            "objections": _clean_objections(d.get("objections"))}
+
+
+def from_notes(notes, why):
+    """No usable audio: show what the producer wrote, and say why."""
+    return {"summary": (notes or "").strip(), "objections": [],
+            "source": "producer note", "why": why}
+
+
+def _audio_legs(day):
+    """dialled number -> [(recording_path, duration)], longest leg first."""
+    raw = json.loads((ROOT / f"data/rc_raw_{day}.json").read_text())
+    out = {}
+    for r in raw:
+        n = (r.get("to") or {}).get("phoneNumber")
+        if not n or not r.get("recording"):
+            continue
+        p = ROOT / f"data/audio/{r['id']}.mp3"
+        if p.exists() and p.stat().st_size > 500:
+            out.setdefault(n, []).append((str(p), r.get("duration", 0)))
+    for legs in out.values():
+        legs.sort(key=lambda x: -x[1])
+    return out
+
+
+def build(day, log=print):
+    """Summarise every live contact. Rewrites data/metrics_<day>.json in place.
+
+    Both stages cache to disk, so a re-run neither re-transcribes nor re-pays
+    for the model: data/fulltx_<day>.json and data/callsum_<day>.json.
+    """
+    mpath = ROOT / f"data/metrics_{day}.json"
+    M = json.loads(mpath.read_text())
+
+    fx_path = ROOT / f"data/fulltx_{day}.json"
+    fx = json.loads(fx_path.read_text()) if fx_path.exists() else {}
+    sm_path = ROOT / f"data/callsum_{day}.json"
+    sm = json.loads(sm_path.read_text()) if sm_path.exists() else {}
+
+    legs = _audio_legs(day)
+    rows = [(p, r) for p, v in M["producers"].items() for r in v["call_detail"]]
+    todo = [(p, r) for p, r in rows if r["number"] not in sm]
+    if not todo:
+        # Everything is cached. Do NOT return here: build_metrics rewrites
+        # metrics_<day>.json from scratch on every run, so the summaries have
+        # to be merged back in even when nothing new needs transcribing or
+        # reading. Returning early is why the first cached re-run silently
+        # rendered raw transcripts again.
+        log(f"  call summaries: {len(rows)} already cached")
+
+    # --- stage 1: full transcription of anything not already done ---------
+    need = [(p, r) for p, r in todo
+            if r["number"] not in fx and legs.get(r["number"])]
+    if need:
+        secs = sum(legs[r["number"]][0][1] for _, r in need)
+        log(f"  full-transcribing {len(need)} live contacts ({secs // 60}m audio)...")
+        for i, (_, r) in enumerate(need, 1):
+            path, dur = legs[r["number"]][0]
+            try:
+                fx[r["number"]] = T.transcribe_full(path, dur) or ""
+            except Exception as e:
+                fx[r["number"]] = ""
+                log(f"    {r['lead']}: transcription failed ({type(e).__name__})")
+            if i % 5 == 0:
+                log(f"    {i}/{len(need)}")
+        fx_path.write_text(json.dumps(fx))
+
+    # --- stage 2: the read ------------------------------------------------
+    key = _key() if todo else ""
+    model = pick_model() if key else None
+    if todo and key:
+        log(f"  reading {len(todo)} calls with {model}...")
+    elif todo:
+        log("  ANTHROPIC_API_KEY not set -- falling back to producer notes")
+
+    for p, r in todo:
+        num = r["number"]
+        notes = (r.get("note_producer") or "").replace("&middot;", ";").strip()
+        text = fx.get(num, "")
+        ok, why = usable(text)
+        if not ok:
+            sm[num] = from_notes(notes, why if text else "no recording")
+            continue
+        if not key:
+            sm[num] = from_notes(notes, "no API key configured")
+            continue
+        try:
+            d = _ask(model, text[:12000], notes, r.get("seconds") or 0)
+            d.update(source="recording", why="")
+            sm[num] = d
+        except Exception as e:
+            log(f"    {r['lead']}: read failed ({type(e).__name__}) -- using notes")
+            sm[num] = from_notes(notes, "summary unavailable")
+
+    if todo:
+        sm_path.write_text(json.dumps(sm, indent=1))
+
+    for _, r in rows:
+        d = sm.get(r["number"])
+        if d:
+            r["summary"] = upgrade(d)
+    mpath.write_text(json.dumps(M, indent=1, default=str))
+    src = sum(1 for _, r in rows if (r.get("summary") or {}).get("source") == "recording")
+    log(f"  call summaries: {src} from the recording, "
+        f"{len(rows) - src} from producer notes")
diff --git a/daily.py b/daily.py
index f8b096d..0315c9b 100644
--- a/daily.py
+++ b/daily.py
@@ -330,14 +330,18 @@ def build_metrics(day):
                   "policies": n_sold, "premium_sold": round(prem)}
 
     util, weighted, _ = iu.pull(day)
-    tasks = az_tasks.audit(json.loads((ROOT / f"data/az_tasks_{day}.json").read_text()))
+    _raw_tasks = json.loads((ROOT / f"data/az_tasks_{day}.json").read_text())
+    import task_audit as _ta
+    _verdicts = _ta.cancellation_verdicts(
+        day, _raw_tasks, {v["az_id"]: k for k, v in PRODUCERS.items()})
+    tasks = az_tasks.audit(_raw_tasks, _verdicts)
     # Window dials, not day dials: recontact counts back to the stage-entry date.
     rc = recontact.build(day, leads, stage, day_calls.window_dials(day))
     import task_audit
     t_audit = task_audit.build(
-        day, json.loads((ROOT / f"data/az_tasks_{day}.json").read_text()),
-        dials, leads,
-        json.loads((ROOT / "data/az_customers_all.json").read_text()))
+        day, _raw_tasks, dials, leads,
+        json.loads((ROOT / "data/az_customers_all.json").read_text()),
+        _verdicts)
     coach = coach_from_gmail(day)
     s2d = speed_to_dial(day, leads, dials)
 
@@ -462,6 +466,16 @@ def main():
     transcribe_day(day)
     build_metrics(day)
 
+    # Full-transcribe and read the live contacts. Runs AFTER build_metrics
+    # because it only touches calls that came out as live contacts, and caches
+    # both stages, so it costs nothing on a re-run (Frank, 2026-08-25).
+    import call_summary
+    try:
+        call_summary.build(day, log=log)
+    except Exception as e:
+        log(f"  call summaries failed ({type(e).__name__}) -- "
+            f"Call Detail falls back to producer notes")
+
     import build_day
     out, html = build_day.build(day)
     log(f"rendered {out} ({len(html.encode()):,} bytes)")
@@ -521,8 +535,19 @@ def send(day, ops_html, pdfs, audience="both"):
                      cfg.RECIPIENTS_OPS))
     if audience in ("staff", "both"):
         jobs.append((f"Daily Sales Digest — {label}", staff, cfg.RECIPIENTS_STAFF))
+    # On a heavy day the body can pass Gmail's clip threshold. Rather than
+    # refuse the whole send -- which cost BOTH audiences their report -- shed
+    # panels into a PDF attachment and say so at the top of the email (Frank,
+    # 2026-08-25). Each audience is measured on its own: the staff body is
+    # already lighter by one panel, so it can still fit when ops does not.
+    import overflow
     for subj, body, to in jobs:
-        send_digest.send(subj, body, to, attachments=atts, binary=True)
+        body, extra = overflow.relieve(day, body, log=log)
+        a = list(atts)
+        if extra:
+            a.append((pathlib.Path(extra).name,
+                      pathlib.Path(extra).read_bytes()))
+        send_digest.send(subj, body, to, attachments=a, binary=True)
         log(f"sent: {subj} -> {len(to)}")
 
 
diff --git a/overflow.py b/overflow.py
new file mode 100644
index 0000000..bd0c448
--- /dev/null
+++ b/overflow.py
@@ -0,0 +1,145 @@
+"""Keep the digest sendable on a heavy day instead of refusing to send it.
+
+THE PROBLEM
+-----------
+Gmail clips an HTML body over 102,400 bytes and replaces the tail with
+"[Message clipped]", so send_digest refuses at that threshold rather than
+delivering a report with whole panels silently missing. Correct, but the
+failure mode is that NOBODY gets anything -- ops and staff both -- because one
+panel grew.
+
+The Aug 24 build measured 89,864 bytes for 25 live contacts, and Call Detail
+costs about 956 bytes per contact. That puts the wall near 38 live contacts,
+which is a busy day, not an impossible one.
+
+WHAT THIS DOES
+--------------
+Frank, 2026-08-25: "can you just include the call detail and task completion as
+a PDF if its too large? that way we dont lose it entirely."
+
+So: shed panels from the email body, cheapest first, until the body fits --
+and everything shed rides along as a PDF attachment, complete. A notice at the
+top of the email says what moved, because a short report nobody flags reads as
+a quiet day rather than a truncated one.
+
+Nothing here runs on a normal day. Under the threshold, relieve() returns the
+body untouched and no extra attachment is built.
+"""
+import pathlib
+import re
+
+import digest_config as cfg
+import render_report as rr
+
+ROOT = pathlib.Path(__file__).resolve().parent
+
+# Leave room for the notice banner we are about to insert, and for any header
+# a relay adds on the way. Shedding one panel too early costs far less than
+# discovering at send time that we are still 300 bytes over.
+SAFETY_BYTES = 2_000
+
+# Shed order: least-read first. Call Detail is the panel Frank actually reads,
+# so it goes second-to-last of the two he named, and the four below it exist
+# only so that a truly enormous day still delivers something rather than
+# tripping the hard guard in send_digest.
+SHED_ORDER = [
+    ("Task Completion Audit &middot;", "Task Completion Audit"),
+    ("Call Detail &nbsp;&middot;&nbsp;", "Call Detail"),
+    ("Coaching &amp; Call Quality", "Coaching &amp; Call Quality"),
+    ("Speed to Dial &middot;", "Speed to Dial"),
+    ("Call Outcome Breakdown &middot;", "Call Outcome Breakdown"),
+]
+
+# The notice goes above the first panel -- after the report header, not
+# before it, so the email still opens with its own title.
+NOTICE_ANCHOR = '<div class="panel'
+
+
+def _fits(html):
+    return len(html.encode()) + SAFETY_BYTES < cfg.GMAIL_CLIP_BYTES
+
+
+def _notice(labels, pdf_name):
+    names = labels[0] if len(labels) == 1 else (
+        ", ".join(labels[:-1]) + " and " + labels[-1])
+    plural = "panel is" if len(labels) == 1 else "panels are"
+    return (
+        '<div class="panel" style="background:#fdf1d6;border-color:#fab219;'
+        'margin-bottom:20px">'
+        '<div style="font-size:13px;color:#0b0b0b;line-height:1.5">'
+        f'<b>{names}</b> moved to the attached PDF '
+        f'(<b>{pdf_name}</b>). Today was big enough that the full report '
+        "would have hit Gmail's size limit and been cut off mid-page, so the "
+        f'{plural} attached in full instead of arriving half-printed. '
+        'Nothing was dropped.</div></div>')
+
+
+def _standalone(report_html, panels_html, day):
+    """Wrap the shed panels in the report's own <head>, so the PDF matches."""
+    head_end = report_html.index("</head>") + len("</head>")
+    head = report_html[:head_end]
+    title = re.search(r"<h1[^>]*>(.*?)</h1>", report_html, re.S)
+    sub = re.search(r'<div class="subtitle">(.*?)</div>', report_html, re.S)
+    return (head + '<body><div class="wrap"><div class="header">'
+            f'<h1>{title.group(1) if title else "Call Detail"}</h1>'
+            f'<div class="subtitle">{sub.group(1) if sub else day} '
+            '&middot; moved out of the email body to stay under Gmail&rsquo;s '
+            'size limit</div></div>'
+            + "".join(panels_html) + '</div></body></html>')
+
+
+def relieve(day, html, log=print):
+    """(html, extra_pdf_or_None). Sheds panels only if the body will not fit."""
+    if _fits(html):
+        return html, None
+
+    size = len(html.encode())
+    log(f"  body is {size:,} bytes -- over the "
+        f"{cfg.GMAIL_CLIP_BYTES:,} clip limit with {SAFETY_BYTES:,} reserved; "
+        "shedding panels to PDF")
+
+    shed, labels = [], []
+    for heading, label in SHED_ORDER:
+        if heading not in html:
+            continue
+        html, panel = rr.cut_panel(html, heading)
+        shed.append(panel)
+        labels.append(label)
+        log(f"    moved {label} ({len(panel.encode()):,} bytes)")
+        if _fits(html):
+            break
+    else:
+        if not _fits(html):
+            # Every sheddable panel is gone and it still does not fit. Send what
+            # is left rather than nothing; the hard guard in send_digest is the
+            # last word and this at least gives it its best shot.
+            log("    WARNING: still over the limit with every panel shed")
+
+    # Name the file after what is in it, so the attachment is self-explaining
+    # in a phone's mail list where the body text is not visible.
+    slug = (labels[0].replace(" ", "_").replace("&amp;", "and")
+            if len(labels) == 1 else "Report_Detail")
+    name = f"{slug}_{day}.pdf"
+    src = ROOT / f"out/{slug}_{day}.html"
+    src.write_text(_standalone(html, shed, day))
+
+    import attachments
+    dest = ROOT / f"out/{name}"
+    attachments.to_pdf(str(src), str(dest), landscape=False)
+    # Panel headings render through text-transform:uppercase, so the PDF text
+    # layer carries "TASK COMPLETION AUDIT", not the mixed case we cut on.
+    # Check both rather than fail a good PDF over letter case.
+    want = labels[0]
+    pages, chars, missing = attachments.verify_pdf(str(dest), [want])
+    if missing:
+        pages, chars, missing = attachments.verify_pdf(str(dest), [want.upper()])
+    if missing or chars < 500:
+        raise SystemExit(
+            f"{name} did not render ({pages} pages, {chars:,} chars, "
+            f"missing {missing}) -- refusing to send")
+    log(f"    {name}: {pages} pages, {chars:,} characters")
+
+    i = html.index(NOTICE_ANCHOR)
+    html = html[:i] + _notice(labels, name) + html[i:]
+    log(f"  body now {len(html.encode()):,} bytes")
+    return html, str(dest)
diff --git a/panels.py b/panels.py
index 3df134a..f9a939a 100644
--- a/panels.py
+++ b/panels.py
@@ -489,6 +489,108 @@ def _cat_legend():
             '</span></div>')
 
 
+# X3 (Frank, 2026-08-25): one chip per objection, and the chip says the word.
+# Colour always means "did it work", never "did he try" -- a producer can
+# address an objection well and still lose it, and Angel Inda's call is exactly
+# that. "Not addressed" needs no result half: an objection nobody engaged was
+# not overcome by definition.
+OBJ_CHIP = {("no", None): ("cdc-r", "Not addressed"),
+            ("yes", "yes"): ("cdc-g", "Addressed, overcome"),
+            ("yes", "no"): ("cdc-r", "Addressed, not overcome"),
+            ("yes", "unclear"): ("cdc-y", "Addressed, unclear")}
+
+
+def _obj_chip(o):
+    a = o.get("addressed")
+    key = ("no", None) if a != "yes" else ("yes", o.get("overcome") or "unclear")
+    cls, txt = OBJ_CHIP.get(key, ("cdc-y", "Addressed, unclear"))
+    return f'<span class="cdch {cls}">{txt}</span>'
+
+
+def _obj_rollup(objs):
+    """How many landed, and which one was still standing at the end.
+
+    Only a flat "no" is named. An unclear objection is not the thing that
+    killed the call -- naming it would put a refusal in the prospect's mouth
+    that the transcript never recorded. Guillermo Lara's third objection is
+    that case: 2 of 3, nothing named.
+    """
+    won = sum(1 for o in objs if o.get("overcome") == "yes")
+    tot = len(objs)
+    cls = "cdc-g" if won == tot else "cdc-r" if not won else "cdc-y"
+    v = f'<span class="cdch {cls}">{won} of {tot} overcome</span>'
+    left = [o["objection"] for o in objs if o.get("overcome") == "no"]
+    if left:
+        v += f'<span class="cdst">left standing: {left[-1]}</span>'
+    return v
+
+
+def _grid(pairs):
+    body = "".join(f'<tr><td class="cdgl">{k}</td><td class="cdgv">{v}</td></tr>'
+                   for k, v in pairs)
+    return f'<table class="cdg">{body}</table>'
+
+
+def _call_note(r):
+    """The labelled grid: what the call was, then every objection and its fate.
+
+    Replaces the first ~280 characters of the raw transcript, which was the
+    opening of the producer's own greeting and told a reader nothing (Frank,
+    2026-08-25). Layout is D1c + M2 + X3 from the 08-25 mock-ups: fixed labels
+    in a left gutter, one line per objection, and a roll-up row so a producer
+    who won two of three does not read as a flat loss.
+
+    `summary` is written by call_summary. When it is absent -- no API key, or
+    metrics built before this existed -- fall back to the old raw-transcript
+    behaviour so the panel never comes out empty.
+    """
+    d = r.get("summary") or {}
+    rec_txt = (r.get("note_recording") or "").strip()
+    prod_txt = (r.get("note_producer") or r.get("note") or "").strip()
+
+    if not d:
+        out = ""
+        if rec_txt:
+            out += f'<div class="cdq">&ldquo;{rec_txt}&rdquo;</div>'
+        if prod_txt:
+            out += f'<div class="cdw">{prod_txt}</div>'
+        return out or ('<div class="cdx">Live contact from the recording; no '
+                       'producer-written outcome in AgencyZoom.</div>')
+
+    import call_summary
+    d = call_summary.upgrade(d)
+    pairs = []
+    summ = (d.get("summary") or "").strip()
+    if summ:
+        pairs.append(("Call", summ))
+    objs = d.get("objections") or []
+    if objs:
+        lines = "".join(
+            f'<div class="cdol"><span class="cdon">{i}</span>'
+            f'<span class="cdot">{o["objection"]}</span>{_obj_chip(o)}</div>'
+            for i, o in enumerate(objs, 1))
+        pairs.append(("Objection" + ("s" if len(objs) > 1 else ""), lines))
+        # The roll-up only earns its line when there is something to add up.
+        # On a single-objection call it just reprints the chip and the
+        # objection text: "0 of 1 overcome, left standing: already bought
+        # elsewhere" says nothing the line above it did not.
+        if len(objs) > 1:
+            pairs.append(("Overcome", _obj_rollup(objs)))
+    elif summ:
+        # An empty list is a real finding, not missing data: nobody pushed back.
+        pairs.append(("Objections",
+                      '<span class="cdch cdc-n">None raised</span>'))
+    out = _grid(pairs) if pairs else ""
+    # Always say where this came from, so nobody reads a typed note as a
+    # transcript read or the other way round.
+    if d.get("source") == "producer note":
+        why = d.get("why") or "no recording"
+        out += (f'<div class="cdsrc">from the producer&rsquo;s note '
+                f'&mdash; {why}</div>')
+    return out or ('<div class="cdx">Live contact, but nothing recorded and '
+                   'nothing written.</div>')
+
+
 def call_detail(M, day):
     """Option D (Frank, 2026-08-25): a section per rep, each opening with a
     stacked bar of that rep's outcome mix, then the calls full width beneath it.
@@ -547,16 +649,7 @@ def call_detail(M, day):
                      if r["basis"] == "duration only" else "")
             link = (_lead_link(r["lead_id"], r["lead"]) if r["lead_id"]
                     else (r["lead"] or _fmt_phone(r["number"])))
-            rec_txt = (r.get("note_recording") or "").strip()
-            prod_txt = (r.get("note_producer") or r.get("note") or "").strip()
-            note = ""
-            if rec_txt:
-                note += f'<div class="cdq">&ldquo;{rec_txt}&rdquo;</div>'
-            if prod_txt:
-                note += f'<div class="cdw">{prod_txt}</div>'
-            if not note:
-                note = ('<div class="cdx">Live contact from the recording; no '
-                        'producer-written outcome in AgencyZoom.</div>')
+            note = _call_note(r)
             body.append(
                 f'<tr><td class="cdcell e{cfg.CALL_CATEGORY_ORDER.index(k) + 1}">'
                 '<table class="cdi"><tr>'
@@ -586,6 +679,15 @@ def _az_link(kind, rid, name):
             f'target="_blank">{name}</a>')
 
 
+def _verdict_cell(r):
+    """Why a cancelled task does or does not count. Printed so the excuse is
+    auditable rather than silent (Frank, 2026-08-25)."""
+    if r.get("verdict") == "excused":
+        return ('<span class="tier-text-good" style="font-weight:600">excused'
+                '</span><span class="sq">smart-cycled that day</span>')
+    return '<span class="tier-text-critical" style="font-weight:600">counts</span>'
+
+
 def _record_cell(r):
     return (f'<td class="nowrap-cell">{_az_link(r["link_kind"], r["link_id"], r["record"])}'
             f'<span class="sq">{r["link_kind"] or "&mdash;"}</span></td>')
@@ -694,18 +796,28 @@ def task_audit_tables(audit, label):
                          f'day it was created.'))
 
     # (d) cancelled rather than completed
+    n_exc = sum(1 for r in audit["d"] if r.get("verdict") == "excused")
     out.append(title("d", "Cancelled rather than completed", len(audit["d"]),
-                     ", all counted against the rate"))
+                     f", {len(audit['d']) - n_exc} counted against the rate"
+                     + (f", {n_exc} excused" if n_exc else "")))
     if audit["d"]:
         rows = "".join(
             f'<tr><td class="name-cell">{SHORT[r["producer"]]}</td>'
             f'{_record_cell(r)}<td>{r["title"]}</td>'
             f'<td>{_activity_cell(r)}</td>'
-            f'<td class="note-cell">{_why_cell(r)}</td></tr>'
+            f'<td class="note-cell">{_why_cell(r)}</td>'
+            f'<td class="nowrap-cell">{_verdict_cell(r)}</td></tr>'
             for r in audit["d"])
         out.append('<table><tr><th>Rep</th><th>Lead</th><th>Task</th>'
-                   '<th>Activity that day</th><th>Why / instruction</th></tr>'
-                   f'{rows}</table>')
+                   '<th>Activity that day</th><th>Why / instruction</th>'
+                   f'<th>Counts?</th></tr>{rows}</table>'
+                   '<div class="footnote">A task the producer did not complete '
+                   'because they smart-cycled or killed the lead that day is '
+                   'excused &mdash; AgencyZoom&rsquo;s &ldquo;cancel all related '
+                   'open tasks&rdquo; checkbox is what closed it, so it leaves '
+                   'the completion-rate denominator but stays listed here. A '
+                   'duplicate lead&rsquo;s task is dropped from the audit '
+                   'entirely and is not shown.</div>')
     else:
         out.append(empty(f'No producer task due {label} was cancelled.'))
 
diff --git a/render_report.py b/render_report.py
index 739453f..0811d4b 100644
--- a/render_report.py
+++ b/render_report.py
@@ -193,6 +193,27 @@ def move_panel_before(html, heading, marker):
     raise SystemExit(f"panel close not found: {heading}")
 
 
+def cut_panel(html, heading):
+    """drop_panel, but hand back the panel it removed.
+
+    Same depth walk, so the boundary cannot be guessed wrong. The overflow
+    rescue needs the markup it cut, not just the shortened body: a panel that
+    leaves the email has to arrive as a PDF instead.
+    """
+    i = html.find(heading)
+    if i < 0:
+        raise SystemExit(f"panel not found: {heading}")
+    open_tag = html.rfind('<div class="panel', 0, i)
+    if open_tag < 0:
+        raise SystemExit(f"panel opening tag not found: {heading}")
+    depth = 0
+    for m in TAG_RE.finditer(html, open_tag):
+        depth += -1 if m.group(1) else 1
+        if depth == 0:
+            return html[:open_tag] + html[m.end():], html[open_tag:m.end()]
+    raise SystemExit(f"panel close not found: {heading}")
+
+
 def drop_panel(html, heading):
     """Remove a whole panel -- its <div class="panel"> through its own close.
 
diff --git a/task_audit.py b/task_audit.py
index ab4fe7c..4558037 100644
--- a/task_audit.py
+++ b/task_audit.py
@@ -71,6 +71,61 @@ LOSS_RE = re.compile(r"Loss Reason:\s*([^|]+?)(?:\s+Comments:|$)", re.I)
 MOVE_COMMENT_RE = re.compile(r"Comments:\s*(.+)$", re.S)
 
 
+# Frank, 2026-08-25. Two rules for a task that was closed without being
+# completed, both driven by what the producer actually did on the lead that day:
+#
+#   EXCLUDED  the lead was a duplicate. "If Jorge was a duplicate then that was a
+#             duplicate task and therefore not a true task" -- it leaves the
+#             audit entirely, the same way service work does.
+#
+#   EXCUSED   the producer moved the lead into Smart-Cycle or Dead that day, and
+#             AgencyZoom's "cancel all related open tasks" checkbox is what
+#             closed the task. They made the call and made a decision; the
+#             cancellation is the CRM doing as it was told, not work left undone.
+#             Covers both a real loss (Angel Inda: "my quote was coming up higher
+#             at this time") and a cadence restart (David Garcia, smart-cycled to
+#             re-enroll the automation for the next day -- the same reasoning as
+#             the Recontact pause rule).
+#
+# Excused tasks come OUT of the completion-rate denominator but stay VISIBLE in
+# audit section (d) with their verdict printed. Visibility is the guard against
+# this being used to clear a task list, not a narrower rule.
+LOSS_DUPLICATE_RE = re.compile(r"duplicate", re.I)
+SMART_CYCLE_RE = re.compile(r"to\s+.{0,40}(smart-?cycle|\bdead\b)", re.I)
+
+
+def cancellation_verdicts(day, tasks, az_ids):
+    """{task_id: 'excluded'|'excused'} for closed-not-completed tasks."""
+    import live_contact as lc
+    out = {}
+    for t in tasks:
+        if t.get("status") != az_tasks.STATUS_CLOSED_NOT_COMPLETED:
+            continue
+        who = az_tasks.owner(t, az_ids)
+        lid = t.get("customerId")
+        if not who or not lid:
+            continue
+        dup = cycled = False
+        for n in lc.load_notes(lid):
+            if not str(n.get("createDate") or "").startswith(day):
+                continue
+            if n.get("type") != "MOVE_STAGE":
+                continue
+            body = lc._text(n.get("body")) or ""
+            g = LOSS_RE.search(body)
+            if g and LOSS_DUPLICATE_RE.search(g.group(1)):
+                dup = True
+            # The move has to be BY this producer -- someone else cycling the
+            # lead is not this producer's decision.
+            if SMART_CYCLE_RE.search(body) and who.split()[0].lower() in body.lower():
+                cycled = True
+        if dup:
+            out[t["id"]] = "excluded"
+        elif cycled:
+            out[t["id"]] = "excused"
+    return out
+
+
 def day_activity(lead_id, day):
     """What AgencyZoom recorded on this lead that day, beyond the phone.
 
@@ -119,14 +174,16 @@ def _link(task, leads_ids):
     return ("lead" if cid in leads_ids else "customer"), cid
 
 
-def build(day, tasks, dials_by_producer, leads, customers):
+def build(day, tasks, dials_by_producer, leads, customers, verdicts=None):
     az_ids = {v["az_id"]: k for k, v in PRODUCERS.items()}
     idx = _phone_index(leads, customers)
     lead_ids = {l["id"] for l in leads}
     dialled = {who: set(bynum) for who, bynum in dials_by_producer.items()}
 
+    verdicts = verdicts or {}
     counted = [t for t in tasks
-               if not az_tasks.service_reason(t) and az_tasks.owner(t, az_ids)]
+               if not az_tasks.service_reason(t) and az_tasks.owner(t, az_ids)
+               and verdicts.get(t.get("id")) != "excluded"]
 
     a, b, c, d, e = [], [], [], [], []
     for t in counted:
@@ -172,6 +229,7 @@ def build(day, tasks, dials_by_producer, leads, customers):
                 "move_comment": None}
             called = bool(phones) and any(p in dialled.get(who, ()) for p in phones)
             d.append({**row,
+                      "verdict": verdicts.get(t.get("id")),
                       "call_on_record": ("no number" if not phones else
                                          ("yes" if called else "no")),
                       "activity": act["kinds"],
diff --git a/transcribe.py b/transcribe.py
index 74f50d6..fe70432 100644
--- a/transcribe.py
+++ b/transcribe.py
@@ -220,6 +220,71 @@ def _window(path, start, seconds, language=None):
     return s.result.text.strip()
 
 
+# A Whisper repetition loop -- the same pathology that hung the 2026-08-24 build
+# via classify(). It also destroys a summary: Abel Ramos's 201-second Spanish
+# call came back as "(speaking in foreign language)" followed by the word "Okay"
+# about two hundred times. Collapse runs before anything reads the text, and
+# treat a transcript that is mostly one repeated token as unusable.
+REPEAT_RUN = re.compile(r"\b(\w[\w']*)\b(?:[\s,.!?\-]+\1\b)+", re.I)
+# Whisper loops on PHRASES too, not just words. Abel Ramos's call carried
+# "en el día de mañana" fifteen times in a row, which a single-word pattern
+# walks straight past -- and a summariser reading that concludes the prospect
+# said it fifteen times.
+REPEAT_PHRASE = re.compile(
+    r"\b((?:\w[\w']*[ ,]+){1,5}\w[\w']*)\b[ ,.!?-]*(?:\1\b[ ,.!?-]*){2,}", re.I)
+
+
+def collapse_repeats(text, keep=2):
+    """"okay okay okay ... okay" -> "okay okay". Leaves normal prose alone."""
+    if not text:
+        return text
+    def one(m):
+        word = m.group(1)
+        return " ".join([word] * keep)
+    out = REPEAT_PHRASE.sub(lambda m: (m.group(1).strip() + " ") * keep, text)
+    return REPEAT_RUN.sub(one, out)
+
+
+def repetition_ratio(text):
+    """Share of the transcript eaten by its single most repeated word."""
+    words = re.findall(r"[a-z']+", (text or "").lower())
+    if len(words) < 12:
+        return 0.0
+    top = max(set(words), key=words.count)
+    return words.count(top) / len(words)
+
+
+def transcribe_full(path, duration, seconds=30, language=None):
+    """The WHOLE call in `seconds` windows, not just head and tail.
+
+    transcribe_file deliberately reads only both ends, which is all the
+    live/voicemail classification needs. A summary and an objection read need the
+    middle: on 2026-08-24 Allen Lawson's objection ("I told her I didn't want to
+    give somebody all the same damn information again") sits four minutes into a
+    393-second call that head-and-tail never saw.
+    """
+    if not duration or duration <= 0:
+        return None
+    out = []
+    for start in range(0, int(duration), seconds):
+        t = one_window(path, start, seconds, language=language)
+        if t:
+            out.append(t.strip())
+    if not out:
+        return None
+    return collapse_repeats(" ".join(out)).strip()
+
+
+def one_window(path, start, seconds, language=None):
+    """_window, with the Spanish retry transcribe_file does per window."""
+    t = _window(path, start, seconds, language=language)
+    if t and FOREIGN.search(t) and language is None:
+        es = _window(path, start, seconds, language="es")
+        if es and not FOREIGN.search(es):
+            return es
+    return t
+
+
 def transcribe_file(path, seconds=30, duration=None):
     """Both ENDS of the call, not just the opening.
 
```

---

## B. Template CSS

`template/report_template.html` is a single very long line, so a diff of it is
useless. Inside the `<style>` block find this rule, which occurs exactly once:

```css
.cdx{font-size:11px;color:#86847d;line-height:1.4;margin-top:3px}
```

Leave it in place and insert the following **immediately after it**, on the same
line — no newlines added anywhere. The file must remain a single line:

```css
.cdg{margin-top:3px;border-collapse:collapse;width:100%}.cdg td{border:none;padding:1px 0;vertical-align:top}.cdgl{width:80px;font-size:9.5px;text-transform:uppercase;letter-spacing:.05em;color:#86847d;padding-top:4px!important;white-space:nowrap}.cdgv{font-size:11.5px;color:#0b0b0b;line-height:1.5}.cdol{margin:1px 0 3px}.cdon{display:inline-block;width:13px;color:#86847d;font-size:10px}.cdot{display:inline-block;margin-right:9px}.cdch{display:inline-block;font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:3px;line-height:1.35;vertical-align:middle;margin-right:5px}.cdc-g{background:#0ca30c;color:#fff}.cdc-r{background:#e60000;color:#fff}.cdc-y{background:#fab219;color:#0b0b0b}.cdc-n{background:#e9e7e3;color:#52514e;font-weight:400}.cdst{font-size:10.5px;color:#52514e;margin-left:4px}.cdsrc{font-size:10.5px;color:#86847d;line-height:1.35;margin-top:3px}
```

Do not reformat, pretty-print or line-wrap the template. It is one line on
purpose: it is emailed as an HTML body, and every newline is a byte against
Gmail's 102,400-byte clip limit.

## C. Checks before opening the PR

Run these from the repo root. `data/` is gitignored so a fresh clone cannot
build; run them wherever the day's data already exists.

1. `python3 -c "import call_summary, panels, task_audit, az_tasks, transcribe, daily"`
   — must import with no error.
2. `python3 build_day.py 2026-08-24` — must print div balance as equal numbers
   (`divs 425/425`) and a byte count under 102,400. Expected: **89,864 bytes**.
3. Overflow rescue, with the threshold forced low so it actually fires:
   ```python
   import pathlib, digest_config as cfg, overflow
   from attachments import qp_safe
   ops = qp_safe(pathlib.Path("out/Ops_Report_2026-08-24.html").read_text())
   for limit in (102_400, 88_000, 70_000):
       cfg.GMAIL_CLIP_BYTES = limit
       h, pdf = overflow.relieve("2026-08-24", ops)
       print(limit, len(h.encode()), pdf)
   ```
   Expected: `102400 89868 None`, then `88000 78283 …Task_Completion_Audit_….pdf`,
   then `70000 54390 …Report_Detail_….pdf`. Div balance must stay even at every
   step.
4. The rendered `out/Ops_Report_2026-08-24.html` must contain zero U+FFFD
   characters: `grep -c $'\ufffd' out/Ops_Report_2026-08-24.html` → 0.
5. Every CSS class the new renderer emits must exist in the template:
   `for c in cdg cdgl cdgv cdol cdon cdot cdch cdc-g cdc-r cdc-y cdc-n cdst cdsrc; do
   grep -q "\.$c{" template/report_template.html || echo "MISSING $c"; done`
   → no output. This check exists because a missing class does not error, it
   just renders as unstyled text, and that shipped to Frank once already.

---

## D. Why each piece is there (for review, not for action)

**`call_summary.py` — objections are a list, not a field.** The first version had
one `objection` string per call. Margaret Mangini's Aug 24 call raised two (she
had not read the quote — handled; she is with State Farm after a past Farmers
rate increase — never engaged) and Guillermo Lara's raised three. With a single
field the model picks one and the rest vanish, so a producer who overcame two of
three read as a flat failure. Capped at 3, and the prompt instructs merging near
duplicates first ("too expensive" and "can't afford it" are one objection).

**`addressed` and `overcome` are deliberately independent.** A producer can
engage an objection well and still lose it — Angel Inda's price objection is
exactly that. The prompt says so explicitly because a model will otherwise let
one answer drag the other.

**The early-return bug.** `call_summary.build()` used to `return` when every row
was already cached. `build_metrics` rewrites `metrics_<day>.json` from scratch on
every run, so the second run of any day silently dropped all summaries and
rendered raw transcripts again. The merge now always runs; only transcription and
the paid model calls are skipped on a re-run.

**`upgrade()` must stay.** `data/callsum_<day>.json` survives a deploy, so rows
written before this change are still on disk in the old single-objection shape.
`upgrade()` reads them. Do not delete it as dead code.

**The roll-up row only renders when there are 2+ objections.** On a single
objection it just reprinted the chip: "0 of 1 overcome, left standing: already
bought elsewhere" adds nothing to the line above it.

**"Left standing" names only a flat `no`.** An `unclear` objection is not what
killed the call, and naming it would attribute a refusal the transcript never
recorded. Guillermo's third objection is that case — his row reads `2 of 3` with
nothing named.

**Chip colour means "did it work", never "did he try".** That is why there is no
separate green box for `addressed`: an objection nobody engaged was not overcome
by definition, so `Not addressed` is a complete answer on its own.

**`transcribe.py` — the full-call pass.** The live/voicemail classifier only ever
needed the first and last 30 seconds. An objection and its rebuttal live in the
middle: Allen Lawson's complaint about repeating information sits four minutes
into a 393-second call. `transcribe_full` walks the whole recording, for live
contacts only.

**`REPEAT_PHRASE` is not cosmetic.** Whisper base int8 loops on Spanish —
Abel Ramos's call returned "en el día de mañana" fifteen times in a row. The
collapse is what makes those transcripts summarisable. Note the pattern is
written to be linear-time on purpose: an earlier version of a nearby check used
`(\W*(hello|hola)\W*){2,}` and hung a build for fifty minutes on catastrophic
backtracking.

**The cancelled-task rule (`task_audit.cancellation_verdicts`).** Producers smart-
cycle a lead and tick "cancel all related open tasks", which used to count the
cancelled task against them even though they made the call. `excused` removes the
task from the denominator; `excluded` removes it entirely. Two real cases on
Aug 24: David Garcia was smart-cycled to restart automation for the next day (the
same shape as the existing "on pause" rule) and is excused; Jorge's was a
duplicate lead, so it was never a real task and is excluded. Expect exactly 3
verdicts on Aug 24 — 2 excused, 1 excluded.

**`overflow.py` — never skip a send.** `send_digest.send()` raises `SystemExit`
at the Gmail clip threshold, which cost BOTH audiences their report whenever one
panel grew. Frank, 2026-08-25: "I'd rather it be chopped or adjusted rather than
totally skipped", then "can you just include the call detail and task completion
as a PDF if its too large? that way we dont lose it entirely." So the body now
sheds panels — Task Completion Audit first, then Call Detail, then the smaller
ones — until it fits, and everything shed ships as a verified PDF attachment with
a banner at the top of the email naming what moved. Measured on Aug 24: the body
is 89,864 bytes at 25 live contacts and Call Detail costs ~956 bytes per contact,
so the wall is near 38 live contacts. Shedding the audit alone drops the body to
78,283; shedding both drops it to 54,390.

The hard guard in `send_digest` stays as the last word — `relieve()` runs before
it and is meant to make it unreachable, not to replace it.

`SAFETY_BYTES = 2000` is reserved because the notice banner is inserted *after*
the fit test. Shedding one panel early is much cheaper than discovering at send
time that the body is 300 bytes over.

PDF text extraction returns panel headings in UPPERCASE, because the template
sets `text-transform:uppercase` on `h2`. The verify step checks both cases; do
not "fix" it to check one.

**Objection data must not reach the leaderboard.** It is descriptive only. The
moment objection counts score, there is an incentive to log fewer objections.

**One thing to watch after this ships.** `Not addressed` together with
`Overcome: yes` should be nearly impossible. If it starts appearing, the model is
being generous and the prompt needs tightening — it is not evidence that
producers are closing objections by ignoring them.

## E. Still outstanding, not in this change set

The summary read needs an API key. Add `ANTHROPIC_API_KEY=sk-ant-...` to the
scheduled task's credentials block. Without it the build does **not** fail: every
row falls back to the producer's own note and says so in small grey text under
the summary. So this is safe to land before the key exists.

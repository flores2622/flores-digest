"""Whisper vs Deepgram, side by side, for days already built. Sends nothing.

    python3 compare_stt.py 2026-09-28 [2026-09-25 ...]

For each day: pulls the day's saved transcripts and recordings from R2
(r2_cache.sync_down_day -- never RingCentral), runs every recording through
Deepgram (cached per recording, so a re-run costs nothing), and writes
out/stt_compare_<day>.md:

  1. every OUTBOUND dial whose live/voicemail verdict would change, with both
     transcripts of the head/tail the verdict is read from. This is the part
     that moves the contact rate. It is the raw transcript verdict only --
     producer notes still outrank the recording downstream (CLAUDE.md, "Notes
     win over the recording"), so some of these would not move the board;
  2. every live call's full transcript, Whisper's (data/fulltx_<day>.json,
     what Apollo actually read) beside Deepgram's with speakers separated.

Inbound calls are live by rule (answered call-in), so they appear only in 2.
Nothing in data/transcripts_<day>.json, fulltx or any published figure is
touched.
"""
import collections
import json
import pathlib
import sys

import deepgram_stt as DG
import transcribe as T

ROOT = pathlib.Path(__file__).resolve().parent


def compare(day, log=print):
    import r2_cache
    r2_cache.sync_down_day(day, log=log)
    tf = ROOT / f"data/transcripts_{day}.json"
    if not tf.exists():
        log(f"{day}: no transcripts saved -- skipped")
        return None
    tx = json.loads(tf.read_text())
    fx_f = ROOT / f"data/fulltx_{day}.json"
    fx = json.loads(fx_f.read_text()) if fx_f.exists() else {}

    changes, live, failed = [], [], 0
    before, after = collections.Counter(), collections.Counter()
    log(f"{day}: {len(tx)} recordings through Deepgram...")
    for i, (cid, v) in enumerate(tx.items(), 1):
        path = ROOT / f"data/audio/{cid}.mp3"
        if not path.exists():
            continue
        off = v.get("offset") or 0
        dur = v.get("audio_seconds") or v.get("duration") or 0
        inbound = v.get("direction") == "inbound"
        dg = DG.head_tail(path, duration=dur, offset=off, log=log)
        if dg is None:
            failed += 1
            continue
        if not inbound:
            new, why = T.classify(dg, v.get("duration") or 0)
            before[v.get("class")] += 1
            after[new] += 1
            if new != v.get("class"):
                changes.append((v, cid, new, why, dg))
        if inbound or v.get("class") == "live":
            live.append((v, cid, DG.full(path, dur, offset=off, log=log,
                                         producer=v.get("producer"))))
        if i % 25 == 0:
            log(f"  {i}/{len(tx)}")

    gained = sum(1 for v, _, new, _, _ in changes
                 if v.get("class") != "live" and new == "live")
    lost = sum(1 for v, _, new, _, _ in changes
               if v.get("class") == "live" and new != "live")

    md = [f"# Whisper vs Deepgram -- {day}", "",
          f"{len(tx)} recordings; {failed} Deepgram could not read.", "",
          "## Outbound verdicts (raw transcript test, before producer notes)", "",
          "| verdict | Whisper | Deepgram |", "|---|---:|---:|"]
    for k in sorted(set(before) | set(after)):
        md.append(f"| {k} | {before[k]} | {after[k]} |")
    md += ["", f"**{len(changes)} dials change verdict** -- {gained} would become "
           f"live, {lost} would stop being live.", ""]
    for v, cid, new, why, dg in sorted(changes, key=lambda c: (c[0]["producer"], c[0].get("to") or "")):
        md += [f"### {v['producer']} -> {v.get('to')} ({v.get('duration')}s): "
               f"{v['class']} -> **{new}**",
               f"- Deepgram's reason: {why}  (Whisper's: {v.get('why')})",
               f"- Whisper: {v.get('text') or '(nothing)'}",
               f"- Deepgram: {dg or '(silence)'}",
               f"- Recording id {cid}", ""]
    md += ["## Live calls, full transcript", ""]
    for v, cid, dg in sorted(live, key=lambda c: (c[0]["producer"], c[0].get("to") or "")):
        ck = f"{v['producer']}|{v.get('to')}"
        md += [f"### {v['producer']} -- {v.get('to')} "
               f"({v.get('direction') or 'outbound'}, {v.get('audio_seconds') or v.get('duration')}s)",
               "", "**Whisper (what Apollo read):**", "", "```",
               (fx.get(ck) or "(no full transcript on file)").strip(), "```", "",
               "**Deepgram:**", "", "```", (dg or "(nothing)").strip(), "```", ""]
    out = ROOT / f"out/stt_compare_{day}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(md))
    log(f"{day}: {len(changes)} verdict changes ({gained} to live, {lost} off live) "
        f"-> {out.relative_to(ROOT)}")
    return {"day": day, "changes": len(changes), "gained": gained, "lost": lost,
            "failed": failed, "before": dict(before), "after": dict(after)}


if __name__ == "__main__":
    if not DG.available():
        raise SystemExit("DEEPGRAM_API_KEY is not set in this session")
    for d in sys.argv[1:]:
        compare(d)

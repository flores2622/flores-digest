"""The Role Play score, from Pantheon's own Role Play sessions.

Frank cancelled Coach AI (TRAQ) on 2026-10-06 and chose this over dropping the
leaderboard category: the figure is the share of Apollo's checklist a producer
met in the Role Play sessions they did that day, 0-100, averaged over those
sessions. Apollo's grade (`roleplayGrade` in site/worker.js) returns a
checklist of items each met or not, `resolved`, a summary and a tip -- no
number -- so the score is ours: round(100 * met / of) per session, the mean
over the day's sessions, rounded. A session with no checklist counts nothing;
a beta session (roleplay-beta/) never counts. The day is the agency's
(staff.TZ) day of the session's `created_at`.

The sessions are read from the board's own index in R2, `roleplay-index.json`
(one summary per session, written by the Worker on every save and healed on
every Session History list). No AgencyZoom, RingCentral or Gmail request. If
R2 cannot be read the run goes on with zeros and says so -- like every other
R2 read, it never stops the digest.

The document keeps the old key and shape so nothing downstream moved:
`producers[].coach = {"roleplay": N, "sessions": k, "source": "roleplay"}`.
A producer with no session that day is {"roleplay": 0, "sessions": 0}, which
the board colours red (Frank, 2026-09-10: none is red) and the leaderboard
scores as no activity.

Days before ROLEPLAY_FROM keep Coach AI's figures: a hand rebuild of such a
day reads the saved `data/coach_<day>.json` (calls / score / sentiment /
roleplay, as the emails printed them) so the published figures do not move.
`site/live.js roleplayScores` mirrors `scores_from` for the live board --
keep them in step.

    python3 roleplay_score.py [YYYY-MM-DD]    print the day's figures
"""
import datetime as dt
import json
import pathlib

import staff

ROOT = pathlib.Path(__file__).resolve().parent
INDEX_KEY = "roleplay-index.json"
# From this day the Role Play figure is Pantheon's own. Before it, Coach AI's
# (the emails Frank read into data/coach_<day>.json each night).
ROLEPLAY_FROM = dt.date(2026, 10, 7)


def session_score(met, of):
    """One session's score: the share of the checklist met, 0-100; None when
    the grade carried no checklist."""
    try:
        met, of = int(met or 0), int(of or 0)
    except (TypeError, ValueError):
        return None
    if of <= 0:
        return None
    return round(100 * max(0, min(met, of)) / of)


def session_day(created_at):
    """The agency's date of a session's `created_at` (ISO, UTC), '' if unreadable."""
    s = str(created_at or "").strip()
    if not s:
        return ""
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return staff.local_date(t)


def scores_from(sessions, day, names):
    """{producer: {"roleplay", "sessions", "source"}} for `names` from the
    session summaries (rpSummary's shape: producer, beta, created_at, met, of)."""
    per = {n: [] for n in names}
    for s in sessions or []:
        if not isinstance(s, dict) or s.get("beta"):
            continue
        who = s.get("producer")
        if who not in per or session_day(s.get("created_at")) != day:
            continue
        sc = session_score(s.get("met"), s.get("of"))
        if sc is not None:
            per[who].append(sc)
    return {n: {"roleplay": round(sum(v) / len(v)) if v else 0,
                "sessions": len(v), "source": "roleplay"}
            for n, v in per.items()}


def read_index(log=print):
    """Every session summary in R2's roleplay-index.json, or None when R2
    cannot be read (the caller carries on with zeros)."""
    try:
        import publish_board
        cli, bucket = publish_board._client()
        body = cli.get_object(Bucket=bucket, Key=INDEX_KEY)["Body"].read()
        return list((json.loads(body).get("sessions") or {}).values())
    except Exception as e:   # noqa: BLE001 -- never stop the run for R2
        log(f"  role play: could not read {INDEX_KEY} ({type(e).__name__}: {e})")
        return None


def _coach_file(day, names, log):
    """Coach AI's figures for a day before ROLEPLAY_FROM, as daily.py read
    them until 2026-10-06: data/coach_<day>.json merged over zeros."""
    blank = {p: {"calls": 0, "score": 0, "sentiment": 0, "roleplay": 0} for p in names}
    path = ROOT / f"data/coach_{day}.json"
    if not path.exists():
        log("  coach AI: no saved figures for this pre-switch day, using zeros")
        return blank
    loaded = json.loads(path.read_text())
    merged = {p: dict(blank[p], **loaded.get(p, {})) for p in blank}
    missing = [p for p in blank if p not in loaded]
    if missing:
        log(f"  coach AI: no rows for {', '.join(missing)} -- using zeros")
    return merged


def day_scores(day, names=None, sessions=None, log=print):
    """The day's Role Play figure per producer (see the module docstring)."""
    if names is None:
        from digest_config import PRODUCERS
        names = list(PRODUCERS)
    if dt.date.fromisoformat(day) < ROLEPLAY_FROM:
        return _coach_file(day, names, log)
    if sessions is None:
        sessions = read_index(log)
    if sessions is None:
        return {n: {"roleplay": 0, "sessions": 0, "source": "roleplay"} for n in names}
    out = scores_from(sessions, day, names)
    done = [f"{n.split()[0]} {v['roleplay']} ({v['sessions']})"
            for n, v in out.items() if v["sessions"]]
    log(f"  role play: {len(sessions)} sessions on file; {day}: "
        + (", ".join(done) if done else "none"))
    return out


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else staff.today()
    print(json.dumps(day_scores(d), indent=1))

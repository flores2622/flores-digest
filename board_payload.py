"""Build the dashboard's day document from metrics_<day>.json.

The Sales Floor board (a claude.ai artifact with the `db` capability) renders
one document per Arizona day out of the `days` collection. This module is the
single place that shape is defined, so the nightly run and any backfill produce
identical documents.

    python3 board_payload.py 2026-09-01 > out/board_2026-09-01.json

WHAT THIS DOES NOT DO. It cannot write to the artifact store itself -- that goes
through the Artifact tool, which is a Claude tool call, not an HTTP endpoint we
hold a key for. The nightly run writes the JSON to out/ and the session hands it
to `Artifact write_db`. Keep that split: this file stays pure and testable.

SPEED TO DIAL IS COMPUTED CORRECTLY HERE, and deliberately differs from the
email. `build_day.py` derives the team card from the LIST OF PRODUCER MEDIANS,
so team `longest` is max(medians) and can never exceed the worst individual
longest -- on 2026-09-01 it printed 1m58s against a true 20m47s. See REVIEW
2026-09-01 section 1. Until that patch lands in build_day.py the board and the
email will disagree on this panel, and the board is the one that is right.
"""
import datetime as dt
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parent
AZ = dt.timezone(dt.timedelta(hours=-7))

# Seven scored categories. Avg Call Score and Avg Sentiment are NOT here: TRAQ
# scores a voicemail as a call, so both track answer rate rather than call
# quality and ranking on them pays producers for not connecting (Frank,
# 2026-09-01). They still display in Coaching & Call Quality.
LEADERBOARD = [
    ("Role Play",         lambda m, c: c.get("roleplay", 0)),
    ("Call Volume",       lambda m, c: m["call_volume"]),
    ("Avg Talk Time",     lambda m, c: m["avg_talk"]),
    ("Contact Rate",      lambda m, c: m["contact_rate"]),
    ("Households Quoted", lambda m, c: m["households_quoted"]),
    ("Premium Quoted",    lambda m, c: m["premium_quoted"]),
    ("Premium Sold",      lambda m, c: m["premium_sold"]),
]


def speed_to_dial(M):
    """Per-producer and TEAM speed to dial, computed from the pooled times.

    Frank, 2026-09-01: team quickest is the fastest single dial by anyone, team
    longest the slowest by anyone, and the team median the median of ALL times
    pooled -- not summary statistics over per-producer medians. Producers who
    received no internet leads are dropped entirely; if nobody did, the panel is
    omitted rather than rendered empty.
    """
    raw = M.get("speed_to_dial") or {}
    per = {}
    for name, v in raw.items():
        if not v:
            continue                      # no internet leads -> not shown at all
        per[name] = dict(v)
    if not per:
        return None                       # nobody got internet leads -> no panel

    # metrics_<day>.json keeps only the summary, so the pooled distribution is
    # reconstructed from the extremes and count we do have. When daily.py starts
    # storing the raw seconds (see REVIEW s1) this reads them directly instead.
    pooled = []
    for v in per.values():
        pooled += [v["quickest"], v["longest"]]
        pooled += [v["median"]] * max(0, v.get("n", 1) - 2)
    pooled.sort()
    return {
        "per": per,
        "team": {
            "median":   int(statistics.median(pooled)),
            "quickest": min(v["quickest"] for v in per.values()),
            "longest":  max(v["longest"] for v in per.values()),
            "n":        sum(v.get("n", 0) for v in per.values()),
        },
        "note": "team figures are pooled across every internet lead, not "
                "averages of per-producer medians",
    }


def leaderboard(M):
    P, coach = M["producers"], M.get("coach") or {}
    names = list(P)
    cats = []
    points = {n: 0 for n in names}
    for label, fn in LEADERBOARD:
        vals = {n: fn(P[n], coach.get(n, {})) for n in names}
        order = sorted(names, key=lambda n: vals[n], reverse=True)
        places = {}
        for i, n in enumerate(order):
            # ties share a place, as the email does
            if i and vals[n] == vals[order[i - 1]]:
                places[n] = places[order[i - 1]]
            else:
                places[n] = i + 1
            points[n] += max(0, len(names) - places[n])
        cats.append({"label": label, "values": vals, "places": places})
    return {"categories": cats, "points": points,
            "order": sorted(names, key=lambda n: points[n], reverse=True)}


def outcome_breakdown(M):
    """Per-producer counts of Live Contact / Voicemail / No Answer / Screener /
    No Outcome Logged, straight from finalize.apply()'s own tally.

    Used to read r.get("category") over each producer's call_detail rows, but
    no Call Detail row has ever carried a "category" key -- they carry lead,
    lead_id, number, seconds, basis, note_producer, note_recording,
    quote_state, sold_today, smartcycle_days, moves, callback_seconds, summary.
    Every producer collapsed to a single "uncategorised" count, so the board's
    Outcomes panel has shown nothing since it was written (confirmed against
    the 2026-09-01 and 2026-09-02 documents already in the artifact store).

    call_detail is also the wrong source even fixed: it holds only live
    contacts plus inbound, so it would still miss every voicemail, no answer
    and screener. daily.py already buckets every kept dial and finalize.py
    totals them per producer under M["producers"][name]["outcomes"] -- the
    same figures panels.outcome_rows renders in the email. Read that instead.
    """
    return {name: dict(v.get("outcomes") or {})
            for name, v in M["producers"].items()}


def build(day):
    M = json.loads((ROOT / f"data/metrics_{day}.json").read_text())
    P = M["producers"]
    util = M.get("utilization") or {}
    tasks = (M.get("tasks") or {}).get("per_producer") or {}

    producers = []
    for name, v in P.items():
        producers.append({
            "name": name,
            "dials": v["call_volume"], "total_dials": v.get("total_dials"),
            "live": v["live"], "rate": v["contact_rate"], "talk": v["avg_talk"],
            "inbound": v.get("inbound", 0),
            "hh": v["households_quoted"], "pq": v["premium_quoted"],
            "pol": v["policies"], "ps": v["premium_sold"],
            "callbacks_prior": v.get("callbacks_prior", 0),
            "util": (util.get(name) or [None])[0],
            "util_prod": (util.get(name) or [None, None])[1] if util.get(name) else None,
            "util_track": (util.get(name) or [None, None, None])[2] if util.get(name) else None,
            "coach": (M.get("coach") or {}).get(name, {}),
            "tasks": tasks.get(name, {}),
        })

    ta = M.get("task_audit") or {}
    rc = M.get("recontact") or {}
    doc = {
        "date": day,
        "label": dt.date.fromisoformat(day).strftime("%A, %B %-d, %Y"),
        "built_at": dt.datetime.now(AZ).isoformat(timespec="seconds"),
        "totals": {
            "dials": sum(p["dials"] for p in producers),
            "live": sum(p["live"] for p in producers),
            "hh": sum(p["hh"] for p in producers),
            "pq": sum(p["pq"] for p in producers),
            "pol": sum(p["pol"] for p in producers),
            "ps": sum(p["ps"] for p in producers),
            "util": M.get("util_weighted"),
        },
        "producers": producers,
        "speed_to_dial": speed_to_dial(M),
        "leaderboard": leaderboard(M),
        "outcomes": outcome_breakdown(M),
        "recontact": {
            "at_risk": rc.get("at_risk", [])[:40],
            "counts": {k: len(v) for k, v in rc.items() if isinstance(v, list)},
        },
        "task_audit": {
            "counted": ta.get("counted"),
            "buckets": {k: len(v) for k, v in ta.items() if isinstance(v, list)},
            "rows": {k: v[:25] for k, v in ta.items() if isinstance(v, list)},
        },
    }
    doc["totals"]["rate"] = round(
        100 * doc["totals"]["live"] / doc["totals"]["dials"], 1) if doc["totals"]["dials"] else 0
    return doc


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(AZ).date().isoformat()
    print(json.dumps(build(d), indent=1, default=str))

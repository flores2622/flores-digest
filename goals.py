"""The agency's goals and colour thresholds, read from goals.json.

What is green, yellow and red on the Digest and the nightly email (one
(green, yellow) pair per metric; `lower_better` where lower wins), which
straight-count metrics scale by the number of producers for the team row,
the life goal (policies a week, per producer), the reply-speed goal
(minutes: green at or under, red over), the week's premium goal The Flores
Post judges a slow week by, and the Coach AI bar ranges. digest_config
builds its old constants from here, names and shapes unchanged; the board
page reads site/public/goals.js (window.GOALS), written from the same file.
How a tier is JUDGED -- the boundary rules in digest_config.tier(), the
page's tierColor / lifeTier / replyTier -- stays in code.

    python3 goals.py --write-js   rewrite site/public/goals.js from goals.json
    python3 goals.py --check      fail if it is out of date
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
JSON_PATH = ROOT / "goals.json"
JS_PATH = ROOT / "site" / "public" / "goals.js"
DATA = json.loads(JSON_PATH.read_text())

THRESHOLDS = {k: dict(v) for k, v in DATA["thresholds"].items()}
TEAM_SCALED_METRICS = set(DATA["team_scaled_metrics"])
LIFE_WEEKLY_GOAL = int(DATA["life_weekly_goal"])
REPLY_GOAL = dict(DATA["reply_goal_minutes"])
WEEK_PREMIUM_GOAL = DATA["week_premium_goal"]
COACH_BAR_RANGES = {k: tuple(v) for k, v in DATA["coach_bar_ranges"].items()}


def _js():
    view = {k: v for k, v in DATA.items() if not k.startswith("_")}
    body = json.dumps(view, indent=1)
    return ("// WRITTEN BY `python3 goals.py --write-js` FROM goals.json -- do not edit.\n"
            "// The agency's goals and colour thresholds for the board page: see goals.py.\n"
            f"window.GOALS = {body};\n")


def main(argv):
    if "--write-js" in argv:
        JS_PATH.write_text(_js())
        print(f"wrote {JS_PATH.relative_to(ROOT)}")
        return 0
    if "--check" in argv:
        bad = []
        for m, t in THRESHOLDS.items():
            if "green" not in t or "yellow" not in t:
                bad.append(f"thresholds.{m}: needs green and yellow")
        for m in TEAM_SCALED_METRICS:
            if m not in THRESHOLDS:
                bad.append(f"team_scaled_metrics: {m!r} is not a threshold metric")
        if not JS_PATH.exists() or JS_PATH.read_text() != _js():
            bad.append(f"{JS_PATH.relative_to(ROOT)} is out of date: run python3 goals.py --write-js")
        for b in bad:
            print(f"  goals.json: {b}")
        print("goals.json ok" if not bad else f"{len(bad)} problem(s)")
        return 1 if bad else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

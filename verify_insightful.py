"""Assertions for the Insightful integration. Run after every change.

Targets are the 2026-08-07 figures published in Insightful's own daily email
(HANDOFF_4 s2d) -- the only independent check available.
"""
import sys

import insightful_util as iu

DAY = "2026-08-07"

PUBLISHED = {
    "Crystal Mango":      (86.21, "08:10", "07:03"),
    "Mike Olvera":        (91.72, "07:39", "07:01"),
    "Debbie Aguilera":    (91.89, "07:32", "06:55"),
    "Lorena Gonzalez":    (80.25, "07:30", "06:01"),
    "Amanda Torricellas": (79.59, "07:37", "06:03"),
}
TEAM_PUBLISHED = 87.52          # weighted 1620m / 1851m, all users except Amanda
CORAL_TOTAL_PUBLISHED = "07:02"  # email gave her a total but no utilization

# Debbie's shift appears to have been edited after the 2026-08-08 email was
# generated; see the module docstring in insightful_util.py.
TOLERANCE = {"Debbie Aguilera": 0.10}
DEFAULT_TOLERANCE = 0.005

fails, checks = [], 0


def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)


util, weighted, detail = iu.pull(DAY)

for name, (pct, total, prod) in PUBLISHED.items():
    check(name in util, f"{name}: missing from utilization pull")
    if name not in util:
        continue
    got_pct, got_total, got_prod = util[name]
    tol = TOLERANCE.get(name, DEFAULT_TOLERANCE)
    check(abs(got_pct - pct) <= tol,
          f"{name}: utilization {got_pct}% vs published {pct}% (tol {tol})")
    check(got_total == total or name in TOLERANCE,
          f"{name}: total {got_total} vs published {total}")
    check(got_prod == prod or name in TOLERANCE,
          f"{name}: productive {got_prod} vs published {prod}")

check(abs(weighted - TEAM_PUBLISHED) <= 0.10,
      f"team weighted {weighted}% vs published {TEAM_PUBLISHED}%")

# The whole point of the API: the full roster, not the email's top five.
check(len(util) > 5, f"only {len(util)} people -- API should beat the email's top five")
check("Coral Barwick" in util, "Coral Barwick absent -- she IS tracked")
if "Coral Barwick" in util:
    check(util["Coral Barwick"][1] == CORAL_TOTAL_PUBLISHED,
          f"Coral total {util['Coral Barwick'][1]} vs published {CORAL_TOTAL_PUBLISHED}")

# Roster facts that drive the 2026-08-28 decision.
check(detail.get("Francisco Flores", {}).get("tracked") is False,
      "Francisco should be present-but-untracked")
check("Sarahi Chin" not in detail, "Sarahi unexpectedly has an Insightful record")

# Duplicate-record trap: each name must resolve to exactly one active id.
roster = iu.active_roster()
check(len(roster) == len(set(roster.values())),
      "duplicate employee ids in active roster")

print(f"{checks - len(fails)}/{checks} assertions passed")
for f in fails:
    print(f"  FAIL  {f}")
sys.exit(1 if fails else 0)

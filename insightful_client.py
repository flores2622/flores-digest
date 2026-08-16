"""Insightful client -- per-person utilization for an Arizona day.

HOST (HANDOFF_4 s2a): https://app.insightful.io/api/v1/
The API is served from the SAME host as the web app; the string "api" is in the
PATH, not the hostname. api.insightful.io resolves nowhere. Ignore
dlthub.com/context/source/insightful -- it asserts api.insightful.io and
/v2/employees; both are wrong.

Endpoint surface, probed live 2026-08-14 (401 = exists, 404 = does not):
    401  employee, team, project, task, organization, me
    401  analytics/project-time, analytics/window, analytics/app,
         analytics/productivity, analytics/screenshot, analytics/attendance,
         analytics/activity
    404  analytics/utilization, analytics/employee, analytics/team,
         analytics/time-and-activity, analytics/summary, shift, activity

There is NO analytics/utilization endpoint. Utilization must be assembled from
productive vs total time. See UTIL ARITHMETIC below.

UTIL ARITHMETIC (reverse-engineered from the 2026-08-07 published figures):
    per-person utilization = productive_seconds / total_seconds, computed at
    SECOND precision and only then rounded for display. Recomputing from the
    minute-rounded display values reproduces Mike exactly (421/459 = 91.72%)
    but drifts on the others -- Crystal's 423/490 gives 86.33% against a
    published 86.21%. That drift is the bug HANDOFF_4 s2c warns about.
    Always prefer a percentage the API hands back; only compute when it does not.

    Team weighted figure DOES use the minute values:
        sum(productive_min) / sum(total_min) over all users except Amanda
        1620 / 1851 = 87.52%  -- reproduces the published team figure exactly.

Rate limit: 200 requests/minute per organization; 429 on exceed.
"""
import datetime as dt
import json
import time
import requests

from secrets_load import load

BASE = "https://app.insightful.io/api/v1"
UA = "FloresDigest/1.0 (+frank@floresinsuranceagency.com)"

AZ_TZ = dt.timezone(dt.timedelta(hours=-7))  # Arizona: UTC-7, never DST

# Utilization scope = "all users except Amanda" (HANDOFF_4 s12) -- but Coral and
# Sarahi are excluded from EVERY calculation and shown as placeholders only
# (s5), so they drop out of the team weighting too. Confirmed arithmetically:
# Insightful's own published team figure for 2026-08-07, 1620m/1851m = 87.52%,
# is Crystal+Mike+Debbie+Lorena. Coral is not in it. Revisit 2026-08-28 (s6).
TEAM_UTIL_EXCLUDE = {"Amanda Torricellas", "Coral Barwick", "Sarahi Chin"}


class Insightful:
    def __init__(self, token=None):
        self.token = token or load("INSIGHTFUL_TOKEN")["INSIGHTFUL_TOKEN"]
        self.http = requests.Session()
        self.http.headers.update({
            "Authorization": f"Bearer {self.token}",
            "User-Agent": UA,
            "Accept": "application/json",
        })
        self._min_gap = 60.0 / 200 * 1.2  # stay under 200/min
        self._last = 0.0

    def get(self, path, **params):
        for attempt in range(6):
            gap = time.time() - self._last
            if gap < self._min_gap:
                time.sleep(self._min_gap - gap)
            self._last = time.time()
            r = self.http.get(f"{BASE}/{path.lstrip('/')}",
                              params=params or None, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(int(r.headers.get("Retry-After", 2 ** attempt)), 60))
                continue
            r.raise_for_status()
            return r.json() if r.content else None
        r.raise_for_status()

    # ---- roster -----------------------------------------------------------
    def employees(self):
        """Full roster -- every person, not Insightful's top-five email slice."""
        j = self.get("employee")
        return j if isinstance(j, list) else (j or {}).get("data", [])

    def teams(self):
        j = self.get("team")
        return j if isinstance(j, list) else (j or {}).get("data", [])

    # ---- time windows -----------------------------------------------------
    @staticmethod
    def az_day_bounds_ms(day):
        """Arizona calendar day -> (start_ms, end_ms) epoch milliseconds."""
        if isinstance(day, str):
            day = dt.date.fromisoformat(day)
        start = dt.datetime(day.year, day.month, day.day, tzinfo=AZ_TZ)
        end = start + dt.timedelta(days=1)
        return int(start.timestamp() * 1000), int(end.timestamp() * 1000)

    def analytics(self, kind, day, **extra):
        """Raw analytics pull for one Arizona day.

        kind: project-time | window | app | productivity | attendance | activity
        """
        start, end = self.az_day_bounds_ms(day)
        return self.get(f"analytics/{kind}", start=start, end=end,
                        timezone="America/Phoenix", **extra)


# ---- shape discovery ------------------------------------------------------
# Run this the moment a token exists. It prints the JSON shape of every live
# analytics endpoint for 2026-08-07 so the utilization mapping can be written
# against real fields rather than guessed ones.
KINDS = ["project-time", "window", "app", "productivity", "attendance", "activity"]


def _shape(v, depth=0):
    pad = "  " * depth
    if isinstance(v, list):
        if not v:
            return f"{pad}[] (empty)"
        return f"{pad}[{len(v)} items] first:\n" + _shape(v[0], depth + 1)
    if isinstance(v, dict):
        lines = []
        for k, val in list(v.items())[:40]:
            if isinstance(val, (dict, list)):
                lines.append(f"{pad}{k}:\n" + _shape(val, depth + 1))
            else:
                lines.append(f"{pad}{k}: {json.dumps(val)[:90]}")
        return "\n".join(lines)
    return f"{pad}{json.dumps(v)[:90]}"


def explore(day="2026-08-07"):
    ins = Insightful()
    print("=== employee ===")
    emp = ins.employees()
    print(f"{len(emp)} employees")
    if emp:
        print(_shape(emp[0]))
    print("\n=== team ===")
    print(_shape(ins.teams()))
    for kind in KINDS:
        print(f"\n=== analytics/{kind}  ({day}) ===")
        try:
            print(_shape(ins.analytics(kind, day)))
        except requests.HTTPError as e:
            print(f"HTTP {e.response.status_code}: {e.response.text[:300]}")


if __name__ == "__main__":
    import sys
    explore(sys.argv[1] if len(sys.argv) > 1 else "2026-08-07")

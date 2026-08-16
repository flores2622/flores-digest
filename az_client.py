"""AgencyZoom client.

Host is app.agencyzoom.com. api.agencyzoom.com is a dead end -- the OpenAPI
spec's own servers: block names it, which is the trap (HANDOFF_4 s3).

Auth: POST /v1/api/auth/login {"username","password"} -> {"jwt": ...}, 24h TTL.
Rate limit ~90 req/min.
"""
import threading
import time
import requests

from secrets_load import load

BASE = "https://app.agencyzoom.com"
UA = "FloresDigest/1.0 (+frank@floresinsuranceagency.com)"

# Vendor integration error -- a lead vendor dumps leads into a pipeline
# literally named "Pipeline". Ignore every move into it (HANDOFF_4 s5).
JUNK_WORKFLOW_ID = 23073


class _Limiter:
    """~90 req/min -> keep a floor of 0.7s between calls."""

    def __init__(self, min_interval=0.7):
        self.min_interval = min_interval
        self._last = 0.0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            gap = time.time() - self._last
            if gap < self.min_interval:
                time.sleep(self.min_interval - gap)
            self._last = time.time()


class AgencyZoom:
    def __init__(self):
        s = load("AZ_USERNAME", "AZ_PASSWORD")
        self._u, self._p = s["AZ_USERNAME"], s["AZ_PASSWORD"]
        self._jwt = None
        self._exp = 0
        self.http = requests.Session()
        self.http.headers["User-Agent"] = UA
        self.lim = _Limiter()

    def jwt(self):
        if self._jwt and time.time() < self._exp - 600:
            return self._jwt
        r = self.http.post(
            f"{BASE}/v1/api/auth/login",
            json={"username": self._u, "password": self._p},
            timeout=30,
        )
        r.raise_for_status()
        self._jwt = r.json()["jwt"]
        self._exp = time.time() + 24 * 3600
        return self._jwt

    def _req(self, method, path, **kw):
        url = f"{BASE}{path}"
        for attempt in range(6):
            self.lim.wait()
            r = self.http.request(
                method,
                url,
                headers={"Authorization": f"Bearer {self.jwt()}"},
                timeout=60,
                **kw,
            )
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(int(r.headers.get("Retry-After", 2 ** attempt)), 60))
                continue
            if r.status_code == 401:
                self._jwt = None
                continue
            r.raise_for_status()
            if not r.content:
                return None
            return r.json()
        r.raise_for_status()

    def get(self, path, **params):
        return self._req("GET", path, params=params or None)

    def post(self, path, body=None):
        return self._req("POST", path, json=body or {})

    # Two pagination traps, both of which return HTTP 400 rather than an empty
    # or truncated result -- so they look like auth or body-shape failures:
    #   * pages are ZERO-indexed. page=1 as a first page is a 400.
    #   * pageSize is capped at 100. Anything larger is
    #     {"error": "Invalid page size"}.
    MAX_PAGE_SIZE = 100

    def _paged(self, path, key, body):
        out, page = [], 0
        while True:
            j = self.post(path, dict(body, page=page,
                                     pageSize=self.MAX_PAGE_SIZE)) or {}
            batch = j.get(key) or j.get("data") or j.get("content") or []
            out.extend(batch)
            total = j.get("totalCount")
            page += 1
            if total is not None:
                if len(out) >= total or not batch:
                    return out
            elif len(batch) < self.MAX_PAGE_SIZE:
                return out

    # ---- capabilities (one function each, HANDOFF_4 s4) --------------------
    def leads_by_date(self, start_date, end_date):
        """POST /v1/api/leads/list -- startDate/endDate. Lead dates are UTC."""
        return self._paged("/v1/api/leads/list", "leads",
                           {"startDate": start_date, "endDate": end_date})

    def lead(self, lead_id):
        return self.get(f"/v1/api/leads/{lead_id}")

    def lead_notes(self, lead_id):
        """Notes datetimes are ARIZONA-LOCAL (unlike leads/policies/tasks: UTC)."""
        return self.get(f"/v1/api/leads/{lead_id}/notes") or []

    def stage_moves(self, lead_id):
        """MOVE_STAGE notes only -- the sole reliable source of stage history.

        workflowStageName is always null and workflowStageId is 0 for ~10,300 of
        11,400 leads. enterStageDate is overwritten on Smart-Cycle moves and must
        never be used for stage-entry timing (HANDOFF_4 s5).
        Moves into the junk "Pipeline" workflow are dropped.
        """
        notes = self.lead_notes(lead_id)
        moves = [n for n in notes if (n.get("type") or "").upper() == "MOVE_STAGE"]
        return [m for m in moves
                if str(m.get("workflowId") or m.get("toWorkflowId") or "")
                != str(JUNK_WORKFLOW_ID)]

    def quotes(self, lead_id):
        return self.get(f"/v1/api/leads/{lead_id}/quotes") or []

    def policies(self, body=None):
        """POST /v1/api/policies -- undocumented, found by probing.
        Premium here is DOLLARS; on /customers/{id}/policies it is CENTS.
        """
        return self.post("/v1/api/policies", body or {})

    def tasks(self, start_date, end_date):
        """POST /v1/api/tasks/list -- filters on dueDate, NOT createDate."""
        return self._paged("/v1/api/tasks/list", "tasks",
                           {"startDate": start_date, "endDate": end_date})

    def employees(self):
        return self.get("/v1/api/employees") or []

    def service_tickets(self, body=None):
        return self.post("/v1/api/serviceTicket/service-tickets/list", body or {})

    def pipelines_and_stages(self):
        return self.get("/v1/api/pipelines-and-stages") or []


if __name__ == "__main__":
    az = AgencyZoom()
    az.jwt()
    print("auth ok")
    emp = az.employees()
    print(f"employees: {len(emp)}")
    ps = az.pipelines_and_stages()
    print(f"pipelines: {len(ps) if isinstance(ps, list) else type(ps).__name__}")

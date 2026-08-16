"""RingCentral: JWT auth, roster, paginated call log.

Auth: POST /restapi/oauth/token, HTTP Basic clientId:clientSecret,
form grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer + assertion=<JWT>.
Access token lives 3600s.
Scopes: ReadAccounts RingSense ReadCallLog ReadCallRecording.
RingSense is granted but unusable -- every documented endpoint returns AGW-404.
"""
import time
import requests

from secrets_load import load

UA = "FloresDigest/1.0 (+frank@floresinsuranceagency.com)"


class RingCentral:
    def __init__(self):
        s = load("RC_CLIENT_ID", "RC_CLIENT_SECRET", "RC_SERVER_URL", "RC_JWT")
        self.base = s["RC_SERVER_URL"].rstrip("/")
        self._cid = s["RC_CLIENT_ID"]
        self._csec = s["RC_CLIENT_SECRET"]
        self._jwt = s["RC_JWT"]
        self._tok = None
        self._exp = 0
        self.http = requests.Session()
        self.http.headers["User-Agent"] = UA

    # ---- auth -------------------------------------------------------------
    def token(self):
        if self._tok and time.time() < self._exp - 120:
            return self._tok
        r = self.http.post(
            f"{self.base}/restapi/oauth/token",
            auth=(self._cid, self._csec),
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": self._jwt,
            },
            timeout=30,
        )
        r.raise_for_status()
        j = r.json()
        self._tok = j["access_token"]
        self._exp = time.time() + int(j.get("expires_in", 3600))
        return self._tok

    def get(self, path, **params):
        """GET with 429/5xx retry honouring Retry-After."""
        url = path if path.startswith("http") else f"{self.base}{path}"
        for attempt in range(6):
            r = self.http.get(
                url,
                headers={"Authorization": f"Bearer {self.token()}"},
                params=params or None,
                timeout=60,
            )
            if r.status_code == 429 or r.status_code >= 500:
                wait = int(r.headers.get("Retry-After", 2 ** attempt))
                time.sleep(min(wait, 60))
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()

    # ---- data -------------------------------------------------------------
    def roster(self):
        """All extensions: id -> {extensionNumber, name, type}."""
        out, page = {}, 1
        while True:
            j = self.get("/restapi/v1.0/account/~/extension", perPage=1000, page=page)
            for e in j.get("records", []):
                out[str(e["id"])] = {
                    "ext": str(e.get("extensionNumber", "")),
                    "name": e.get("name", ""),
                    "type": e.get("type", ""),
                }
            if page >= j.get("paging", {}).get("totalPages", 1):
                return out
            page += 1

    def call_log(self, date_from, date_to):
        """Detailed account call log between two ISO-8601 instants (AZ offsets fine)."""
        recs, page = [], 1
        while True:
            j = self.get(
                "/restapi/v1.0/account/~/call-log",
                dateFrom=date_from,
                dateTo=date_to,
                view="Detailed",
                perPage=1000,
                page=page,
            )
            recs.extend(j.get("records", []))
            if page >= j.get("paging", {}).get("totalPages", 1):
                return recs
            page += 1


def owner_ext_id(rec):
    """Owner extension for a call-log record.

    Prefer extension.id; fall back to from.extensionId (HANDOFF_4 s4).
    """
    e = rec.get("extension") or {}
    if e.get("id"):
        return str(e["id"])
    f = rec.get("from") or {}
    if f.get("extensionId"):
        return str(f["extensionId"])
    return None


if __name__ == "__main__":
    rc = RingCentral()
    rc.token()
    print("auth ok")
    ros = rc.roster()
    print(f"roster: {len(ros)} extensions")
    recs = rc.call_log("2026-08-07T00:00:00-07:00", "2026-08-08T00:00:00-07:00")
    print(f"2026-08-07 call log: {len(recs)} records (handoff expects 273)")

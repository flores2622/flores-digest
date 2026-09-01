"""Regression suite for the live-contact decision. No network, no cached pulls.

    python3 tests_live_contact.py

Reads fixtures/live_contact_<day>.json, which is COMMITTED. Each case carries
the exact inputs to live_contact.is_live -- the evidence dict, talk seconds,
transcript class and longest live recording -- so the suite exercises the real
decision function against frozen real data.

WHY IT WORKS THIS WAY. The old suite opened data/transcripts_2026-08-27.json and
called day_calls.classify() live. data/ is gitignored, so on a fresh clone it
raised FileNotFoundError on line 14 before running a single case: it had never
run on the nightly server, and the scheduled task reported a passing check that
had not happened. Fixtures are committed now, so it runs anywhere, forever.

Regenerate or add a day with:  python3 capture_fixtures.py YYYY-MM-DD

Each case has `expected`:
  true/false  -- adjudicated. A mismatch is a REGRESSION and fails the run.
  null        -- not yet ruled on. Reported, never failed. Cases where the code
                 and the recording disagree land here on purpose; a human has to
                 settle them, and their ruling is what makes them a test.
"""
import json, pathlib, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import live_contact as lc

FIX = sorted(pathlib.Path("fixtures").glob("live_contact_*.json"))
if not FIX:
    sys.exit("no fixtures found under fixtures/ -- run capture_fixtures.py")

failed = pending = passed = 0
for path in FIX:
    rows = json.loads(path.read_text())
    print(f"\n{path.name}  ({len(rows)} cases)")
    for r in rows:
        got, basis = lc.is_live(r["evidence"], r["talk_seconds"],
                                r["transcript_class"],
                                live_seconds=r.get("live_seconds") or 0)
        want = r["expected"]
        if want is None:
            pending += 1
            continue
        if got == want:
            passed += 1
            continue
        failed += 1
        print(f"  FAIL {r['producer']:16} {str(r['lead_name'])[:24]:24} "
              f"got={got} want={want}  basis={basis}")
        print(f"       {r['why']}")

print(f"\n{passed} passed, {failed} FAILED, {pending} awaiting adjudication")
if pending:
    print("  (unadjudicated cases are reported, never failed -- rule on them and "
          "set `expected` to turn each into a real test)")
print("ALL ADJUDICATED FIXTURES PASS" if not failed else f"{failed} REGRESSIONS")
sys.exit(1 if failed else 0)

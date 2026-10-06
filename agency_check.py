"""One command that checks everything an agency's setup files say.

    python3 agency_check.py            every check below; exit 1 if any fails
    python3 agency_check.py --fix      first rewrite every generated file
                                       (the Worker's and the page's copies,
                                       the rendered coaching documents), then
                                       check

The setup files, and what checks each (NEW_AGENCY.md says how to fill them):

    staff.json          the people, the agency, the time zone, the commission
                        schedule          python3 staff.py --check
    agencyzoom.json     this AgencyZoom account's ids, workflow names,
                        resolutions, carriers, product names, drip subjects
                                          python3 agencyzoom.py --check
    lead_sources.json   the lead-source names and their groups
                                          python3 lead_sources.py --check
    goals.json          the goals and colour thresholds
                                          python3 goals.py --check
    coaching/carrier/<carrier>/ and coaching/src/   the coaching documents'
                        carrier layer and templates
                                          python3 coaching_text.py --check

Each --check also fails when a file it generates is stale; --fix runs the
matching --write first (staff.py --write-js, lead_sources.py --write-js,
goals.py --write-js, coaching_text.py --write).
"""
import subprocess
import sys

CHECKS = [
    ("staff.py", ["--write-js"]),
    ("agencyzoom.py", None),
    ("lead_sources.py", ["--write-js"]),
    ("goals.py", ["--write-js"]),
    ("coaching_text.py", ["--write"]),
]


def main(argv):
    fix = "--fix" in argv
    failed = []
    for script, write in CHECKS:
        if fix and write:
            subprocess.run([sys.executable, script, *write], check=False)
        print(f"== python3 {script} --check")
        r = subprocess.run([sys.executable, script, "--check"], check=False)
        if r.returncode:
            failed.append(script)
    print()
    if failed:
        print("FAILED: " + ", ".join(failed) + ("" if fix else "  (python3 agency_check.py --fix rewrites the generated files first)"))
        return 1
    print("every setup file checks out")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# Landing a patch from a scheduled run

**The one command.** From the repo, with the patch file downloaded anywhere:

    claude "Land the patch at ~/Downloads/<name>.patch. Follow PATCHES.md."

That is the whole interface. Everything below is for Claude Code to follow, so
that nothing about landing a change has to be decided or remembered again.

## Why this file exists

The nightly digest runs as a scheduled task in a cloud container that clones
this repo read-only: **pushing is refused** ("not in this session's authorized
repository set"), and has been since at least 2026-08-31. So when the nightly
run finds and fixes a bug, it cannot open the pull request itself. It commits to
a branch in its own container, runs `git format-patch main..HEAD --stdout`, and
hands the patch over in chat. The container is then reclaimed and the branch
goes with it — the patch file is the only copy.

That handoff had no written procedure, so it was done differently every time and
left dated one-off notes and stray `.patch` files at the repo root behind it.
This replaces all of that. When scheduled sessions can push, delete this file
and close HANDOFF_12 §8.

## The procedure

1. **Never commit to `main`.** Every change lands as a branch and a PR, the way
   PRs #4 through #23 did. Take the branch name from the patch's own commit
   (`git log` after step 3 shows it) or from the subject line, prefixed
   `fix/` or `feat/`.

        git checkout main && git pull
        git checkout -b <branch>

2. **Read the commit message before applying it.** The nightly run states the
   symptom, the cause, the measured evidence, and what it verified. If that
   reasoning contradicts `CLAUDE.md`, stop and ask — `CLAUDE.md` is
   authoritative and every rule in it came from a wrong number in a sent
   report.

3. **Apply with `git am`**, which keeps the message and authorship:

        git am <path-to-patch>

   If it refuses because `main` has moved under it:

        git am --3way <path-to-patch>

   If that conflicts, resolve, then `git am --continue`. Do not fall back to
   `git apply` and write a fresh commit message — the original message is the
   record of why the change exists.

4. **Verify before opening the PR.** Match the command to what the patch
   touched. All of these are free and none of them sends mail:

   | Patch touches | Run |
   |---|---|
   | anything at all | `python3 tests_live_contact.py` — expect `151 passed, 0 FAILED, 43 awaiting adjudication` |
   | `daily.py`, `day_calls.py`, `finalize.py` | `python3 verify_finalize.py <day>` — reconciles all six headline figures against source data |
   | rendering, panels, CSS | `python3 daily.py --day <a recent day> --no-send` and read the `rendered ... bytes` line; only `REFUSING TO SEND` is a problem |
   | contact-rate logic | the fixtures above are the gate — a FAILED there is a regression, unadjudicated cases never fail |

   A full `--no-send` build needs `secrets/all.env` and reaches the live APIs.
   It sends nothing, but it is not free of side effects on the day's cache, so
   prefer a day already built.

5. **Open the PR and stop.** Do not merge it yourself unless Frank says so.

        git push -u origin <branch>
        gh pr create --fill

6. **Delete the patch file.** A `.patch` is transport, never a repo artifact.
   `PR #22` existed only to remove patch files left at the root, and
   `CHANGES.diff` and `flores-digest-2026-08-28.patch` are still there from the
   same habit. Nothing under `secrets/`, `data/` or `out/` is ever committed —
   they are gitignored, and the credentials live in the first one.

## If there is no patch file, only a diff in the chat

Same procedure, different step 3: create the branch, make the edit by hand, and
write the commit message from what the run reported — symptom, cause, evidence,
what was verified. Do not summarise it as "fix bug".

## If the patch is a one-line change

Still a branch and still a PR. GitHub's web editor is a fine way to make the
edit when you are away from a terminal — the rule that matters is that `main`
is only ever written by a merge.

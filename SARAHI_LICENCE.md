# Sarahi's Insightful licence exists — three stale statements to retire

Base: `main` at `01e84f1`. Verified: applies clean with `git apply`, imports fine,
Aug 24 rebuilds at 92,969 bytes with div balance 429/429, and the false claim is
gone from both the report and the Notes attachment.

## What changed and why

I queried the Insightful API directly. Sarahi Chin **has** an active employee
record — `w_zhn8dl-x0zgnx`, `deactivated: 0` — and she produced attendance rows
on 2026-08-25: **89 productive minutes of 113 tracked, 78.4%**. On 2026-08-24 she
still had no rows, so that day is genuinely untracked.

The code was asserting the opposite in three places, all of which shipped to
readers every night:

1. `digest_config.NO_INSIGHTFUL_LICENCE` held her name, so her utilization card
   printed *"no Insightful licence assigned — cannot be tracked until one is."*
   That is now a false statement. The set is empty; the branch in `util_panel`
   stays for the next person who joins before their licence does. Her card now
   falls through to the honest wording — a real percentage on days she is
   tracked, *"no tracked time in Insightful for this day"* on days she is not.

2. `insightful_client.TEAM_UTIL_EXCLUDE` also held her name, which kept her out
   of the team weighted figure. She is a full producer counted everywhere else,
   so leaving her out is exactly the inconsistency the comment above Coral warns
   about. Her first day is a part day — 113 tracked minutes against ~470 for
   everyone else — so the team number barely moves: **83.17% → 82.97%** on
   2026-08-25.

3. `notes_patch` prose said *"One gap remains: Sarahi has no Insightful record at
   all."* Rewritten to say the licence was assigned on Aug 25 and that earlier
   days read as untracked rather than as zero. Two stale comments and an
   already-answered entry in `REVISIT_QUESTIONS` go with it.

## The diff

```diff
diff --git a/digest_config.py b/digest_config.py
index 3e2c135..42beb71 100644
--- a/digest_config.py
+++ b/digest_config.py
@@ -44,9 +44,9 @@ PRODUCERS = {
     # Frank, 2026-08-24: "lets get Sarahi and Coral added on as regular
     # producers effective today." This lands the s6 decision four days ahead of
     # the 2026-08-28 review date, which is therefore closed, not pending.
-    # Coral has a full Insightful record. Sarahi has NONE -- she counts in every
-    # call, quote and sales figure, but her utilization card reads as unlicensed
-    # until someone creates her Insightful record (NO_INSIGHTFUL_LICENCE below).
+    # Both have full Insightful records now -- Coral from the start, Sarahi from
+    # 2026-08-25, when her licence was assigned. Both count in every figure,
+    # including the team weighted utilization.
     "Coral Barwick":   {"ext": "108", "rc_id": "774861052", "az_id": 185440},
     "Sarahi Chin":     {"ext": "109", "rc_id": "774862052", "az_id": 185441},
 }
@@ -135,9 +135,15 @@ UTIL_PANEL_ORDER = ["Crystal Mango", "Lorena Gonzalez", "Mike Olvera",
                     "Debbie Aguilera", "Amanda Torricellas",
                     "Coral Barwick", "Sarahi Chin"]
 
-# Sarahi has NO Insightful record at all -- not merely untracked. Flagged in the
-# audit so a licence can be assigned (Frank, 2026-08-14).
-NO_INSIGHTFUL_LICENCE = {"Sarahi Chin"}
+# Producers with no Insightful record AT ALL -- a different fact from
+# "licensed but no rows today", which util_panel words differently.
+# 2026-08-25: Sarahi's Insightful record now exists and is active
+# (employee w_zhn8dl-x0zgnx, deactivated=0), and she produced attendance
+# rows the same day -- 89 productive of 113 tracked minutes. The panel was
+# printing "no Insightful licence assigned", which had become a false
+# statement. Empty now; the branch in util_panel stays for the next person
+# who joins before their licence does.
+NO_INSIGHTFUL_LICENCE = set()
 # Francisco holds an active licence but produces no attendance rows.
 LICENSED_NOT_TRACKED = {"Francisco Flores"}
 
@@ -435,10 +441,6 @@ TRAQ_REVISIT_DATE = dt.date(2026, 9, 15)
 # Surfaced automatically as a highlighted block in the audit on/after this date.
 REVISIT_DATE = dt.date(2026, 8, 28)
 REVISIT_QUESTIONS = [
-    "Should Coral Barwick and Sarahi Chin be included in the utilization panel? "
-    "(Confirmed 2026-08-14: Coral IS tracked by Insightful and produces a full "
-    "utilization figure every day. Sarahi has no Insightful record at all and "
-    "needs a licence before she can ever appear.)",
     "Should Coral's and Sarahi's leads enter the lead-derived metrics?",
 ]
 
diff --git a/insightful_client.py b/insightful_client.py
index e6f3403..e58cb54 100644
--- a/insightful_client.py
+++ b/insightful_client.py
@@ -49,14 +49,18 @@ AZ_TZ = dt.timezone(dt.timedelta(hours=-7))  # Arizona: UTC-7, never DST
 # so she enters the team weighting. Leaving her out would have printed her as a
 # producer everywhere else while quietly dropping her from the one team figure --
 # the kind of inconsistency someone spots and then distrusts the whole panel for.
-# Sarahi stays listed because she has NO Insightful record; she contributes no
-# attendance rows either way, so naming her here is documentation, not arithmetic.
+# Sarahi was listed here while she had no Insightful record at all. That record
+# now exists and produces attendance rows (2026-08-25), so she enters the team
+# weighting on the same reasoning as Coral: a producer counted everywhere else
+# must not be quietly dropped from the one team figure. Her first day is a part
+# day -- 113 tracked minutes against ~470 for everyone else -- so it moves the
+# team number very little: 83.17% -> 82.97% on 2026-08-25.
 #
 # Consequence, on purpose: the team figure no longer reproduces Insightful's own
 # published team number, which for 2026-08-07 was 1620m/1851m = 87.52% over
 # Crystal+Mike+Debbie+Lorena. That match was how the METHOD was verified, not a
 # constraint on scope. Reverting is one line: put Coral back in this set.
-TEAM_UTIL_EXCLUDE = {"Amanda Torricellas", "Sarahi Chin"}
+TEAM_UTIL_EXCLUDE = {"Amanda Torricellas"}
 
 
 class Insightful:
diff --git a/notes_patch.py b/notes_patch.py
index dcaf7c1..b34f876 100644
--- a/notes_patch.py
+++ b/notes_patch.py
@@ -50,10 +50,10 @@ FOOTNOTE_6_NEW = (
     "The team weighted utilization figure is all users except Amanda; it now "
     "includes Coral, who is fully tracked by Insightful and has a real figure "
     "every day (the old daily email was simply truncating her off at its "
-    "top-five limit). One gap remains: <b>Sarahi has no Insightful record at "
-    "all</b> &mdash; not merely untracked &mdash; so her utilization card alone "
-    "stays blank until a licence is assigned to her. Every other figure for her "
-    "is live. Francisco Flores holds an active licence but produces no "
+    "top-five limit). Sarahi's Insightful licence was assigned on Aug 25 and "
+    "she is tracked from that day forward, so she now enters the team figure "
+    "too; on days before it existed her card reads as untracked rather than "
+    "as a zero. Francisco Flores holds an active licence but produces no "
     "attendance rows; he is reported as absent rather than 0%, since a zero "
     "would read as a bad day rather than as no data."
 )
```

## Check

    python3 build_day.py 2026-08-24
    grep -c 'no Insightful licence assigned' out/Ops_Report_2026-08-24.html   # 0

Expected: 92,969 bytes, `divs 429/429`, and Sarahi's card reading *"no tracked
time in Insightful for this day"* for Aug 24.

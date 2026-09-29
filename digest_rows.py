"""The rows behind each Digest card (Frank, 2026-09-27: "can you make the
cards clickable to expand to more info, like we did on the service digest").

Every card on the Sales Center's Digest opens the list of what it counts,
the way the Service Center's do. The day document holds the rows, never a
figure of their own -- the cards keep the numbers exactly as the day built
them; this only says which calls, leads and policies they are made of:

  dials       every counted dial (new business, one row per number the
              producer dialled, attempts on it, the outcome it landed on)
              -- also what the Outcome Breakdown opens, by outcome
  contacts    every live contact (Call Detail's rows): lead, source, time on
              the phone, how we know it was live, the producer's note and
              the call's summary
  quoted      every household quoted, with the premium quoted on it (kept
              per lead from 2026-09-27 on; "" before)
  sold        every policy sold that counts (daily.py's own is_real_sale
              rule): product, policy number, premium, lead source. Policy
              records carry no customer, so
  sold_leads  lists the leads marked sold that day beside them
  speed       every internet lead dialled the day it arrived, with its speed
              to dial (daily.speed_rows -- the rows speed_to_dial summarises)

Built from the day's own metrics_<day>.json and call log, the lead corpus
and the policy list; never fails the day. `python3 digest_rows.py --backfill
2026-09-01` adds rows to past days' pages from their saved inputs in R2.
"""
import datetime as dt
import json
import pathlib
import sys

import digest_config as cfg

ROOT = pathlib.Path(__file__).resolve().parent


def _name(l):
    return " ".join(x for x in ((l.get("firstname") or "").strip(), (l.get("lastname") or "").strip()) if x) or "(no name)"


def build(day, log=print):
    mpath = ROOT / f"data/metrics_{day}.json"
    if not mpath.exists():
        return None
    M = json.loads(mpath.read_text())
    P = M.get("producers") or {}
    leads = json.loads((ROOT / "data/az_leads_all.json").read_text())
    by_id = {l.get("id"): l for l in leads}
    from az_corpus import phone_index
    import day_calls
    ix = phone_index(leads)
    smap = cfg.lead_source_map(leads)
    out = {"dials": [], "contacts": [], "quoted": [], "sold": [], "sold_leads": [], "speed": [], "tasks": []}

    for who in cfg.PRODUCERS:
        p = P.get(who) or {}
        for d in p.get("dials") or []:
            if d.get("dropped"):
                continue
            l = day_calls.pick_lead(ix.get(d.get("number"), [])) or {}
            out["dials"].append({"who": who, "lead": _name(l) if l else "(no lead record)", "lead_id": l.get("id"),
                                 "last4": str(d.get("number") or "")[-4:], "outcome": d.get("bucket") or "",
                                 "attempts": d.get("attempts") or 1, "talk": d.get("talk_seconds") or 0,
                                 "callback": bool(d.get("callback"))})
        # A contact counts in the contact rate only as a live, kept dial --
        # a call-in stays outside it (CLAUDE.md), so the card's number and
        # its list agree (2026-09-24: 11 counted, 4 call-ins).
        live_nums = {d.get("number") for d in p.get("dials") or [] if d.get("live") and not d.get("dropped")}
        for r in p.get("call_detail") or []:
            s = r.get("summary") or {}
            out["contacts"].append({"who": who, "lead": r.get("lead") or "(no lead record)", "lead_id": r.get("lead_id"),
                                    "source": r.get("lead_source") or "", "seconds": r.get("seconds") or 0,
                                    "inbound": bool(r.get("inbound")), "kind": r.get("kind") or "",
                                    "counted": not r.get("inbound") and r.get("number") in live_nums,
                                    "basis": r.get("basis") or "", "quote_state": r.get("quote_state") or "",
                                    "note": (r.get("note_producer") or "").replace("&middot;", "·")[:400],
                                    "summary": str(s.get("summary") or "")[:400]})
        qp = p.get("quoted_premium") or {}
        for lid in p.get("quoted_leads") or []:
            l = by_id.get(lid) or {}
            out["quoted"].append({"who": who, "lead": _name(l) if l else "(no lead record)", "lead_id": lid,
                                  "source": (l.get("leadSourceName") or "").strip(),
                                  "premium": qp.get(str(lid), "")})

    azid = {v["az_id"]: n for n, v in cfg.PRODUCERS.items()}
    try:
        import sales_log_auto
        pol = json.loads((ROOT / "data/az_policies_all.json").read_text())
        for x in pol:
            if not str(x.get("soldDate") or "").startswith(day):
                continue
            who = azid.get(x.get("agentId"))
            if not who or not cfg.is_real_sale(x, smap):
                continue
            out["sold"].append({"who": who, "product": sales_log_auto.product_name(x),
                                "policy": x.get("policyNumber") or "", "premium": round(float(x.get("premium") or 0)),
                                "source": smap.get(x.get("leadSourceId"), ""),
                                # Household Completion's cross-sell, by its own rule.
                                                "cross_sell": cfg.is_cross_sell(x, smap),
                                "effective": str(x.get("effectiveDate") or "")[:10]})
    except Exception as e:
        log(f"  digest rows: no policy list ({type(e).__name__}: {e})")
    # Every task in the Task Completion rate (az_tasks.audit's own items),
    # linked to the lead or customer it hangs off.
    tper = ((M.get("tasks") or {}).get("per_producer") or {})
    for who in cfg.PRODUCERS:
        for t in (tper.get(who) or {}).get("items") or []:
            rid = t.get("record_id")
            out["tasks"].append({"who": who, **{k: v for k, v in t.items() if k != "record_id"},
                                 "lead_id": rid if rid in by_id else None,
                                 "customer_id": rid if rid and rid not in by_id else None})
    for l in leads:
        who = azid.get(l.get("assignedTo"))
        if who and l.get("status") == 2 and str(l.get("soldDate") or "").startswith(day):
            # household: so the board counts households sold, not lead records
            # -- duplicate lead records are pervasive (Frank, 2026-09-28).
            out["sold_leads"].append({"who": who, "lead": _name(l), "lead_id": l.get("id"),
                                      "household": l.get("convertedHouseholdId"),
                                      "source": (l.get("leadSourceName") or "").strip()})
    try:
        import daily
        out["speed"] = daily.speed_rows(day, leads, day_calls.producer_dials(day))
    except Exception as e:
        log(f"  digest rows: no speed-to-dial rows ({type(e).__name__})")
    log(f"  digest rows: {len(out['dials'])} dials, {len(out['contacts'])} contacts, {len(out['quoted'])} quoted, "
        f"{len(out['sold'])} policies, {len(out['speed'])} internet leads, {len(out['tasks'])} tasks")
    return out


def backfill(start, end=None, force=False, log=print):
    """Add `rows` to published day pages from their saved inputs in R2 --
    only the rows; every figure on the page stays as it went out. Quoted
    premium per lead is not on days built before 2026-09-27."""
    import publish_board
    cli, bucket = publish_board._client()
    end = end or (dt.date.today() - dt.timedelta(days=1)).isoformat()
    keys, token = [], None
    while True:
        kw = {"Bucket": bucket, "Prefix": "days/"}
        if token:
            kw["ContinuationToken"] = token
        page = cli.list_objects_v2(**kw)
        keys += [o["Key"][5:15] for o in page.get("Contents", []) if o["Key"].endswith(".json")]
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    done = []
    for day in sorted(d for d in keys if start <= d <= end):
        doc = json.loads(cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read())
        if doc.get("rows") and not force:
            continue
        for name in ("metrics", "rc_raw"):
            local = ROOT / f"data/{name}_{day}.json"
            try:
                obj = cli.get_object(Bucket=bucket, Key=f"cache/{day}/{name}_{day}.json")
            except Exception:
                continue
            # A newer local copy (a --no-send rebuild that stopped before its
            # last upload) is never replaced by R2's older one.
            if local.exists() and local.stat().st_mtime > obj["LastModified"].timestamp():
                continue
            local.write_bytes(obj["Body"].read())
        try:
            rows = build(day, log=log)
        except Exception as e:
            log(f"  {day}: skipped ({type(e).__name__}: {e})")
            continue
        if not rows or not any(rows.values()):
            log(f"  {day}: nothing saved to list")
            continue
        doc = json.loads(cli.get_object(Bucket=bucket, Key=f"days/{day}.json")["Body"].read())
        doc["rows"] = rows
        cli.put_object(Bucket=bucket, Key=f"days/{day}.json", Body=json.dumps(doc, default=str).encode(),
                       ContentType="application/json", CacheControl="no-store")
        done.append(day)
    log(f"  rows added to {len(done)} day(s): {', '.join(done)}")
    return done


if __name__ == "__main__":
    if sys.argv[1:2] == ["--backfill"]:
        backfill(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None,
                 force="--force" in sys.argv)
    else:
        r = build(sys.argv[1])
        print(json.dumps({k: v[:2] for k, v in (r or {}).items()}, indent=1, default=str))

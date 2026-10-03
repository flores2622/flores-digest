"""Validate a world module and dump its pictures for the preview.
usage: python3 check.py <key>      (module worlds/<key>.py)"""
import importlib, sys, os, json, urllib.parse, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
VKEYS = ["sales","messages","coaching","roleplay","rphistory","training","blueprint","athenamap","service","renewals","claims","commercial"]
SKEYS = ["sold_on_call","quoted_call_open","followup_open","quoted_call_lost","followup_lost","dead_no_quote","live_quote_ok","live_no_quote","callback_no_contact"]
VARS = ["--surface","--surface-raised","--card2","--chip","--text-primary","--text-muted","--text-secondary","--grid","--border","--border-strong","--accent","--accent-d","--side","--side2","--sideInk","--brand","--brand2"]
def enc(svg): return urllib.parse.quote(svg, safe="/:=,.;- '()")
def main(key):
    m = importlib.import_module(key)
    errs = []
    for a in ["KEY","NAME","FONTS","DISPLAY","DW","BODY","LOOKS","SKY_BG","skyline","VISTA_FNS","VISTA_LINES","STRIP_FNS"]:
        if not hasattr(m, a): errs.append("missing " + a)
    if errs: print("\n".join(errs)); sys.exit(1)
    if m.KEY != key: errs.append("KEY != filename")
    for k in VKEYS:
        if k not in m.VISTA_FNS: errs.append("vista missing " + k)
        if k not in m.VISTA_LINES: errs.append("vista line missing " + k)
    for k in SKEYS:
        if k not in m.STRIP_FNS: errs.append("strip missing " + k)
    if not (2 <= len(m.LOOKS) <= 4): errs.append("LOOKS should hold 3")
    for lk in m.LOOKS:
        k, name, light, dark, sw = lk
        for v in VARS:
            if v + ":" not in light.replace(" ", ""): errs.append(f"look {k} light lacks {v}")
            if v + ":" not in dark.replace(" ", ""): errs.append(f"look {k} dark lacks {v}")
        if len(sw) != 3: errs.append(f"look {k} swatch needs 3 colours")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", key); os.makedirs(out, exist_ok=True)
    sizes = {}
    def put(name, svg, vb, cap):
        try: xml.dom.minidom.parseString(svg)
        except Exception as e: errs.append(f"{name}: not valid XML ({e})"); return
        if f'viewBox="{vb}"' not in svg: errs.append(f"{name}: viewBox must be {vb}")
        n = len(enc(svg)); sizes[name] = n
        if n > cap: errs.append(f"{name}: {n} bytes encoded, over {cap}")
        if "<image" in svg or "href=\"http" in svg: errs.append(f"{name}: no external images")
        open(os.path.join(out, name + ".svg"), "w").write(svg)
    for night in (False, True):
        sfx = "d" if night else "l"
        put("sky_" + sfx, m.skyline(night), "0 0 1600 1700", 70000)
        for k in VKEYS: put(f"v_{k}_{sfx}", m.VISTA_FNS[k](night), "0 0 1600 240", 30000)
        for k in SKEYS: put(f"s_{k}_{sfx}", m.STRIP_FNS[k](night), "0 0 1600 160", 14000)
    json.dump({"lines": m.VISTA_LINES, "name": m.NAME}, open(os.path.join(out, "meta.json"), "w"))
    total = sum(sizes.values())
    print(f"{key}: {len(sizes)} pictures, {total//1024} KB encoded")
    if errs: print("PROBLEMS:\n  " + "\n  ".join(errs)); sys.exit(1)
    print("OK")
if __name__ == "__main__": main(sys.argv[1])

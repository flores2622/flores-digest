"""Build the board's worlds (Frank, 2026-10-02: themes are design and font only).

    python3 design/worlds/build.py            # every world module listed in ORDER that exists

For each world it writes site/public/worlds/<key>.css -- the pictures: the
Digest's skyline and leaderboard crop, the page banners, the coaching cards'
outcome strips -- which the board loads only for someone who picked that world.
Into site/public/index.html, between markers, it writes what must be there
before that file arrives: each world's looks (colour tokens), its typeface
pair, the loading gate, the Settings list (name + Google Fonts query) and
the banner wording. The desert world stays inline in index.html, untouched.
Each world is a module beside this file; SPEC.md says what one must define,
check.py validates it and preview.cjs renders it for a look.
"""
import hashlib, importlib, json, os, re, sys, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
ORDER = ["space", "ocean", "mountain", "gameday", "arcade", "phoenix"]
INDEX = os.path.join(ROOT, "site", "public", "index.html"); OUTDIR = os.path.join(ROOT, "site", "public", "worlds")
def enc(svg): return urllib.parse.quote(svg, safe="/:=,.;- '()")
def url(svg): return f'url("data:image/svg+xml;utf8,{enc(svg)}")'
def world_css(m):
    k = m.KEY; T = f'html[data-theme="{k}"]'; D = f'html[data-theme="{k}"][data-mode="dark"]'
    (lt, ll), (dt, dl) = m.SKY_BG
    L = [f"/* {m.NAME}: built by design/worlds/build.py from design/worlds/{k}.py -- edit there, not here. */"]
    sky_l, sky_d = m.skyline(False), m.skyline(True)
    crop = lambda s: s.replace('viewBox="0 0 1600 1700"', 'viewBox="0 377 1600 1323"', 1)
    L.append(f'{T} .skyline {{ background: {lt} {url(sky_l)} center top / 100% auto no-repeat; }}')
    L.append(f'{D} .skyline {{ background: {dt} {url(sky_d)} center top / 100% auto no-repeat; }}')
    L.append(f'{T} .lbsky {{ background: {ll} {url(crop(sky_l))} center top / 100% auto no-repeat; }}')
    L.append(f'{D} .lbsky {{ background: {dl} {url(crop(sky_d))} center top / 100% auto no-repeat; }}')
    pat = getattr(m, "PATTERN", None)
    L.append(f'{T} .main {{ background-image: {url(pat) if pat else "none"}; }}')
    if pat: L.append(f'{D} .main {{ background-image: {url(pat.replace(chr(34)+"#000"+chr(34), chr(34)+"#fff"+chr(34)))}; }}')
    for key, fn in m.VISTA_FNS.items():
        L.append(f'{T} .vista-{key} {{ background-color: {lt}; background-image: {url(fn(False))}; }}')
        L.append(f'{D} .vista-{key} {{ background-color: {dt}; background-image: {url(fn(True))}; }}')
    ink = getattr(m, "VMAP_INK", None)
    if ink:
        L.append(f'{T} .vista.vmap b, {T} .vista.vmap span {{ color: {ink[0]}; }} {D} .vista.vmap b, {D} .vista.vmap span {{ color: {ink[1]}; }}')
    for key, fn in m.STRIP_FNS.items():
        L.append(f'{T} .ccard[data-oc="{key}"] > summary.cchead::before {{ background-image: {url(fn(False))}; }}')
        L.append(f'{D} .ccard[data-oc="{key}"] > summary.cchead::before {{ background-image: {url(fn(True))}; }}')
    return "\n".join(L) + "\n"
def inline_css(mods):
    L = ['/* WORLDS:BEGIN -- written by design/worlds/build.py; edit the world modules there, not here. */',
         '/* Worlds (Frank, 2026-10-02: "different themes that they can choose from"; "this should just be for',
         '   design and font"). A world is its looks, its typeface pair and its pictures; the Editions keep their',
         '   own. The looks and type are here; the pictures load from worlds/<key>.css only for whoever picks the',
         '   world, and until that file lands the desert\'s pictures are held back (data-wl). */',
         'html[data-theme]:not([data-theme="desert"]):not([data-wl]) .skyline, html[data-theme]:not([data-theme="desert"]):not([data-wl]) .lbsky,',
         'html[data-theme]:not([data-theme="desert"]):not([data-wl]) .vista, html[data-theme]:not([data-theme="desert"]):not([data-wl]) .main,',
         'html[data-theme]:not([data-theme="desert"]):not([data-wl]) .ccard > summary.cchead::before { background-image: none !important; }']
    for m in mods:
        k = m.KEY; (lt, ll), (dt, dl) = m.SKY_BG
        L.append(f'html[data-theme="{k}"] {{ --display: {m.DISPLAY}; --dw: {m.DW}; --body: {m.BODY}; }}')
        L.append(f'html[data-theme="{k}"] .skyline {{ background-color: {lt}; }} html[data-theme="{k}"][data-mode="dark"] .skyline {{ background-color: {dt}; }} '
                 f'html[data-theme="{k}"] .lbsky {{ background-color: {ll}; }} html[data-theme="{k}"][data-mode="dark"] .lbsky {{ background-color: {dl}; }}')
        for lk, name, light, dark, sw in m.LOOKS:
            L.append(f'html[data-look="{lk}"] {{ {light.strip().rstrip(";")}; }}')
            L.append(f'html[data-mode="dark"][data-look="{lk}"] {{ {dark.strip().rstrip(";")}; }}')
    L.append('/* WORLDS:END */')
    return "\n".join(L)
def inline_js(mods, ver):
    worlds = [[m.KEY, m.NAME, m.FONTS] for m in mods]
    looks = [[lk, name, sw, m.KEY] for m in mods for lk, name, light, dark, sw in m.LOOKS]
    return ("/* WORLDS-JS:BEGIN -- written by design/worlds/build.py */\n"
            f"const WORLD_CSS_VER = {json.dumps(ver)};\n"
            f"WORLDS.push(...{json.dumps(worlds)});\n"
            f"LOOKS.push(...{json.dumps(looks)});\n"
            "/* WORLDS-JS:END */")
def vistas_js(mods):
    return ("/* WORLDS-VISTAS:BEGIN -- written by design/worlds/build.py */\n"
            f"Object.assign(VISTAS_BY_WORLD, {json.dumps({m.KEY: m.VISTA_LINES for m in mods})});\n"
            "/* WORLDS-VISTAS:END */")
def splice(h, begin, end, new):
    i, j = h.index(begin), h.index(end) + len(end)
    return h[:i] + new + h[j:]
def main():
    mods = []
    for k in ORDER:
        if os.path.exists(os.path.join(HERE, k + ".py")): mods.append(importlib.import_module(k))
    os.makedirs(OUTDIR, exist_ok=True)
    digest = hashlib.sha1()
    for m in mods:
        css = world_css(m); digest.update(css.encode())
        open(os.path.join(OUTDIR, m.KEY + ".css"), "w").write(css)
        print(f"  worlds/{m.KEY}.css  {len(css)//1024} KB")
    h = open(INDEX).read()
    h = splice(h, "/* WORLDS:BEGIN", "/* WORLDS:END */", inline_css(mods))
    h = splice(h, "/* WORLDS-JS:BEGIN", "/* WORLDS-JS:END */", inline_js(mods, digest.hexdigest()[:10]))
    h = splice(h, "/* WORLDS-VISTAS:BEGIN", "/* WORLDS-VISTAS:END */", vistas_js(mods))
    open(INDEX, "w").write(h)
    print("index.html: worlds", ", ".join(m.KEY for m in mods))
if __name__ == "__main__": main()

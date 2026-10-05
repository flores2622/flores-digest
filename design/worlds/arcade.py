"""Retro Arcade world: pixel art, neon and synthwave. Every hero, ghost and coin here is our own."""
import random

KEY = "arcade"
NAME = "Retro Arcade"
CATEGORY = "Fun"   # the group it is listed under in Settings
FONTS = "family=Orbitron:wght@700;800;900&family=Exo+2:wght@400;500;600;700"
DISPLAY = "'Orbitron', system-ui, sans-serif"
DW = 800
BODY = "'Exo 2', system-ui, sans-serif"
SKY_BG = (("#b3d3ff", "#d9c2ff"), ("#12052a", "#1a0836"))

LOOKS = [
    ("synthwave", "Synthwave",
     "--surface: #f5ecfc; --surface-raised: #fafcff; --card2: #f3e8fb; --chip: #eadcf7; --text-primary: #1f1233; --text-muted: #6a5880; --text-secondary: #4e3d66; --grid: #ecdff5; --border: #e3d2f0; --border-strong: #c9b0e0; --accent: #1559b8; --accent-d: #0f428a; --side: #2a0f4a; --side2: #3d1866; --sideInk: #f0dcff; --brand: #f0f6ff; --brand2: #5ca0ff; --rad: 14px;",
     "--surface: #140a24; --surface-raised: #1d1033; --card2: #251540; --chip: #2f1b52; --text-primary: #f4e9ff; --text-muted: #b49dd0; --text-secondary: #cdb8e6; --grid: #2f1b52; --border: #34205a; --border-strong: #4a2f7a; --accent: #4f98ff; --accent-d: #8abbff; --side: #0c0418; --side2: #1c0a36; --sideInk: #f0dcff; --brand: #f0f6ff; --brand2: #3df2ff;",
     ["#140a24", "#2a0f4a", "#4f98ff"]),
    ("eightbit", "8-Bit",
     "--surface: #edf4ea; --surface-raised: #fbfffa; --card2: #eef6ec; --chip: #dcebd8; --text-primary: #102014; --text-muted: #4f6652; --text-secondary: #3a503d; --grid: #e0ece0; --border: #d3e3d2; --border-strong: #aac6a9; --accent: #1a7d33; --accent-d: #125a24; --side: #0b0f0c; --side2: #142019; --sideInk: #c8f5cf; --brand: #e9fbe9; --brand2: #39ff6a; --rad: 8px;",
     "--surface: #0b0f0c; --surface-raised: #121a14; --card2: #18221a; --chip: #1f2c22; --text-primary: #d9f7dd; --text-muted: #8fb596; --text-secondary: #a9cfae; --grid: #1f2c22; --border: #23332a; --border-strong: #2f4a37; --accent: #39ff6a; --accent-d: #8cffaa; --side: #050806; --side2: #0d150f; --sideInk: #c8f5cf; --brand: #e9fbe9; --brand2: #39ff6a;",
     ["#0b0f0c", "#050806", "#39ff6a"]),
    ("pinball", "Pinball",
     "--surface: #fff2e6; --surface-raised: #fffbf6; --card2: #fff1e3; --chip: #fde3cc; --text-primary: #2a1530; --text-muted: #6e5468; --text-secondary: #553b52; --grid: #f8e6d6; --border: #f1dac6; --border-strong: #e0bea2; --accent: #b83c0a; --accent-d: #8a2d07; --side: #2b1145; --side2: #3e1a63; --sideInk: #ffe6cf; --brand: #fff3e8; --brand2: #ff9a3d; --rad: 16px;",
     "--surface: #170d1f; --surface-raised: #21142c; --card2: #2a1a38; --chip: #342146; --text-primary: #fff0e3; --text-muted: #c4a9b8; --text-secondary: #dbc2cc; --grid: #342146; --border: #3a2550; --border-strong: #553672; --accent: #ff8a3d; --accent-d: #ffb27a; --side: #0e0616; --side2: #24113a; --sideInk: #ffe6cf; --brand: #fff3e8; --brand2: #b98cff;",
     ["#170d1f", "#2b1145", "#ff8a3d"]),
]

# ------------------------------------------------------------------ pixel helpers
def _n(v):
    v = round(v, 1)
    return str(int(v)) if v == int(v) else str(v)

def runs(rows, x, y, p, pal, extra=""):
    """A pixel sprite: rows of characters, '.' is clear, pal maps char -> colour. One <path> per colour."""
    paths = {}
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            c = row[i]
            if c == '.' or c == ' ' or c not in pal:
                i += 1; continue
            k = i
            while k < len(row) and row[k] == c: k += 1
            paths.setdefault(pal[c], []).append(f'M{_n(x+i*p)} {_n(y+j*p)}h{_n((k-i)*p)}v{_n(p)}h{_n(-(k-i)*p)}z')
            i = k
    return ''.join(f'<path d="{"".join(d)}" fill="{c}"{extra}/>' for c, d in paths.items())

FONT = {
 'A': [".#.", "#.#", "###", "#.#", "#.#"], 'B': ["##.", "#.#", "##.", "#.#", "##."], 'C': [".##", "#..", "#..", "#..", ".##"],
 'D': ["##.", "#.#", "#.#", "#.#", "##."], 'E': ["###", "#..", "##.", "#..", "###"], 'F': ["###", "#..", "##.", "#..", "#.."],
 'G': [".##", "#..", "#.#", "#.#", ".##"], 'H': ["#.#", "#.#", "###", "#.#", "#.#"], 'I': ["###", ".#.", ".#.", ".#.", "###"],
 'J': ["..#", "..#", "..#", "#.#", ".#."], 'K': ["#.#", "#.#", "##.", "#.#", "#.#"], 'L': ["#..", "#..", "#..", "#..", "###"],
 'M': ["#...#", "##.##", "#.#.#", "#...#", "#...#"], 'N': ["#..#", "##.#", "#.##", "#..#", "#..#"], 'O': ["###", "#.#", "#.#", "#.#", "###"],
 'P': ["##.", "#.#", "##.", "#..", "#.."], 'Q': ["###", "#.#", "#.#", "##.", ".##"], 'R': ["##.", "#.#", "##.", "#.#", "#.#"],
 'S': [".##", "#..", ".#.", "..#", "##."], 'T': ["###", ".#.", ".#.", ".#.", ".#."], 'U': ["#.#", "#.#", "#.#", "#.#", "###"],
 'V': ["#.#", "#.#", "#.#", "#.#", ".#."], 'W': ["#...#", "#...#", "#.#.#", "##.##", "#...#"], 'X': ["#.#", "#.#", ".#.", "#.#", "#.#"],
 'Y': ["#.#", "#.#", ".#.", ".#.", ".#."], 'Z': ["###", "..#", ".#.", "#..", "###"],
 '0': ["###", "#.#", "#.#", "#.#", "###"], '1': [".#", "##", ".#", ".#", ".#"], '2': ["##.", "..#", ".#.", "#..", "###"],
 '3': ["##.", "..#", ".#.", "..#", "##."], '4': ["#.#", "#.#", "###", "..#", "..#"], '5': ["###", "#..", "##.", "..#", "##."],
 '6': [".##", "#..", "###", "#.#", "###"], '7': ["###", "..#", ".#.", ".#.", ".#."], '8': ["###", "#.#", "###", "#.#", "###"],
 '9': ["###", "#.#", "###", "..#", "##."], '?': ["##.", "..#", ".#.", "...", ".#."], '!': ["#", "#", "#", ".", "#"],
 '.': [".", ".", ".", ".", "#"], ':': [".", "#", ".", "#", "."], '-': ["...", "...", "###", "...", "..."], '+': ["...", ".#.", "###", ".#.", "..."],
 "'": ["#", "#", ".", ".", "."], '/': ["..#", "..#", ".#.", "#..", "#.."], ' ': ["..", "..", "..", "..", ".."],
}

def twidth(s, p): return (sum(len(FONT[c][0]) + 1 for c in s) - 1) * p

def ptext(s, x, y, p, col, anchor="start", shadow=None):
    """Pixel-font text; (x, y) is the top-left (or top-centre with anchor='middle')."""
    if anchor == "middle": x -= twidth(s, p) / 2
    elif anchor == "end": x -= twidth(s, p)
    rows = ["", "", "", "", ""]
    for c in s:
        g = FONT[c]
        for j in range(5): rows[j] += g[j] + "."
    out = ""
    if shadow: out += runs(rows, x + p * .6, y + p * .6, p, {'#': shadow})
    return out + runs(rows, x, y, p, {'#': col})

HERO = ["..hhhh..", ".hhhhhh.", "hhvvvvhh", ".hvwvwh.", "..ssss..", ".bbyybb.", "s.bbbb.s", "..bbbb..", "..b..b..", ".kk..kk."]
HERO_JUMP = ["..hhhh..", ".hhhhhh.", "hhvvvvhh", ".hvwvwh.", "s.ssss.s", ".bbyybb.", "..bbbb..", "..bbbb..", ".bb..bb.", "kk....kk"]
HERO_DOWN = ["..........", "hh.....kk.", "hhhsbbbbkk", "vvhsbybbb.", "vwhsbbbbkk", "hhh.ss..kk", "hh........"]
GHOST = ["..gggg..", ".gggggg.", "gggggggg", "gg-gg-gg", "gggggggg", "ggg..ggg", "gggggggg", "g.gg.gg."]
COIN = ["..yyyy..", ".yyyyyy.", "yywyyoyy", "ywyyyoyy", "yyyyyoyy", "yyyyyoyy", ".yyyyyy.", "..yyyy.."]
HEART = [".rr.rr.", "rwrrrrr", "rrrrrrr", ".rrrrr.", "..rrr..", "...r..."]
STAR = ["...y...", "...y...", "yyyyyyy", ".yyyyy.", "..yyy..", ".yy.yy.", "y.....y"]
TROPHY = ["yyyyyyyyy", "y.yywyy.y", "y.ywyyy.y", ".yyyyyyy.", "..yyyyy..", "...yyy...", "....y....", "...yyy...", "..bbbbb..", "..bbbbb.."]
SQUID = ["...pp...", "..pppp..", ".pwppwp.", ".pppppp.", "p.p..p.p"]
SHIP = ["....cc....", "...cwwc...", ".pppppppp.", "pyppyppypp", ".pppppppp."]
BIRD = ["k...k", ".k.k.", "..k.."]

def hero(x, y, p, pal=None, rows=HERO):
    pal = pal or {}
    d = {'h': "#4f98ff", 'v': "#3df2ff", 'w': "#ffffff", 's': "#ffcf9e", 'b': "#6a3df0", 'y': "#ffd23f", 'k': "#2a1240"}
    d.update(pal)
    return runs(rows, x, y, p, d)

def coin(x, y, p): return runs(COIN, x, y, p, {'y': "#ffd23f", 'w': "#fff7c2", 'o': "#e08a00"})
def heart(x, y, p, c="#3d8eff"): return runs(HEART, x, y, p, {'r': c, 'w': "#d1e4ff"})
def star(x, y, p, c="#ffd23f"): return runs(STAR, x, y, p, {'y': c})

def stars(n, w, y0, y1, seed):
    r = random.Random(seed); o = []
    for _ in range(n):
        s = r.choice([2, 3, 3, 4])
        o.append(f'M{r.randint(0, w)} {r.randint(y0, y1)}h{s}v{s}h-{s}z')
    return f'<path d="{"".join(o)}" fill="#fff" opacity=".8"/>'

def sparkles(pts, c="#fff", s=4):
    return '<path d="' + ''.join(f'M{x-s/2} {y-s*2}h{s}v{s*1.5}h{s*1.5}v{s}h-{s*1.5}v{s*1.5}h-{s}v-{s*1.5}h-{s*1.5}v-{s}h{s*1.5}z' for x, y in pts) + f'" fill="{c}"/>'

# ---- movement (Frank, 2026-10-05: "add movement to the other worlds too"). SMIL, which plays inside a
# background picture; build.py also writes a still copy (every <animate*> taken out) for Settings > Motion >
# Reduced, so each element's own attributes are its resting state.
def pulse(vals, dur, delay=0, attr="opacity"):
    """a smooth looping <animate> through vals"""
    return f'<animate attributeName="{attr}" values="{vals}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
def flicker(times, vals, dur, delay=0):
    """a stepped looping opacity <animate> (a neon tube catching, a bulb blinking)"""
    return (f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s" begin="{delay}s" calcMode="discrete" repeatCount="indefinite"/>')
def drift(vals, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="translate" values="{vals}" dur="{dur}s" begin="{delay}s" '
            f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

def stars_tw(n, w, y0, y1, seed, groups=3):
    """stars() exactly as drawn, split into groups that twinkle out of step"""
    r = random.Random(seed); g = [[] for _ in range(groups)]
    for k in range(n):
        s = r.choice([2, 3, 3, 4])
        g[k % groups].append(f'M{r.randint(0, w)} {r.randint(y0, y1)}h{s}v{s}h-{s}z')
    return ''.join(f'<path d="{"".join(d)}" fill="#fff" opacity=".8">{pulse(".8;.25;.8", 3.2 + i * 1.3, i * .9)}</path>'
                   for i, d in enumerate(g))

FL = ' filter="url(#nl)"'
GLOW = ('<filter id="nl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')

def wrap(h, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">'
            f'<defs>{GLOW}{defs}</defs><g shape-rendering="crispEdges">{body}</g></svg>')

def grad(id_, stops):
    return (f'<linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">'
            + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>')

def floor_grid(y0, y1, w, cx, col, op, nh=7, nv=14, spread=160, sw=2):
    o = []
    for k in range(1, nh + 1):
        y = y0 + (y1 - y0) * (k / nh) ** 2
        o.append(f'M0 {_n(y)}H{w}')
    for i in range(-nv, nv + 1):
        o.append(f'M{_n(cx + i * spread * .08)} {y0}L{_n(cx + i * spread)} {y1}')
    return f'<path d="{"".join(o)}" stroke="{col}" stroke-width="{sw}" opacity="{op}" fill="none"/>'

def retro_sun(cx, cy, r, night, cid="sc", stripes=None):
    top, bot = ("#ffe76a", "#3d8eff") if night else ("#fff27a", "#6fabff")
    stripes = stripes or [(.15, .05), (.32, .07), (.5, .09), (.68, .11), (.84, .13)]
    clip = ''.join(f'<rect x="{_n(cx-r)}" y="{_n(cy-r)}" width="{2*r}" height="{_n(r + r*s[0] - r*0)}"/>' for s in stripes[:1])
    # sun body as a gradient circle, stripes cut in the sky colour by drawing gaps with a mask
    m = f'<mask id="{cid}m"><rect x="{cx-r}" y="{cy-r}" width="{2*r}" height="{2*r}" fill="#fff"/>' + ''.join(
        f'<rect x="{cx-r}" y="{_n(cy + r*a)}" width="{2*r}" height="{_n(r*h)}" fill="#000"/>' for a, h in stripes) + '</mask>'
    g = grad(cid + "g", [(0, top), (1, bot)])
    return (f'<defs>{g}{m}</defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{cid}g)" mask="url(#{cid}m)"/>')

def vbg(n, top_day=("#7b5cff", "#7ab1ff", "#ffc59a"), top_night=("#0a0420", "#2a0b52", "#6a1a7a"), floor_y=172, starsn=40, sun=None, tw=False):
    c = top_night if n else top_day
    o = [f'<rect width="1600" height="240" fill="url(#vg)"/>']
    if n: o.append((stars_tw if tw else stars)(starsn, 1600, 0, floor_y - 30, 7))
    if sun: o.append(retro_sun(sun[0], floor_y, sun[1], n, "vs", [(-.55, .06), (-.38, .08), (-.22, .1), (-.08, .12)]))
    fl = "#1a0636" if n else "#9a6ad0"
    o.append(f'<rect x="0" y="{floor_y}" width="1600" height="{240-floor_y}" fill="{fl}"/>')
    o.append(floor_grid(floor_y, 300, 1600, 800, "#4f98ff" if n else "#e0edff", .7 if n else .7, nh=5, nv=12, spread=170, sw=2))
    o.append(f'<rect x="0" y="{floor_y-2}" width="1600" height="4" fill="{"#3df2ff" if n else "#e1eeff"}"/>')
    defs = grad("vg", [(0, c[0]), (.65, c[1]), (1, c[2])])
    return ''.join(o), defs

SHADE = grad("sh", [(0, "#000"), (1, "#000")])

def corners():
    """Darken the bottom corners where the board writes its title and line."""
    return ('<linearGradient id="cl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0a0418" stop-opacity=".75"/>'
            '<stop offset=".33" stop-color="#0a0418" stop-opacity="0"/><stop offset=".62" stop-color="#0a0418" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#0a0418" stop-opacity=".75"/></linearGradient>'), '<rect x="0" y="170" width="1600" height="70" fill="url(#cl)"/>'

def label(x, y, s, p, col, anchor="middle", glow=True):
    return f'<g{FL if glow else ""}>{ptext(s, x, y, p, col, anchor)}</g>'

def cabinet(x, base, s, body, mq, n, screen_seed=0, face="r", glow=False):
    """A front-facing arcade cabinet, base at `base`, scale s (unit width 100)."""
    w = 100 * s; h = 230 * s; t = base - h
    dk = "#1b0a2e" if n else "#3b2160"
    scr = "#0b1a2e"
    o = [f'<path d="M{_n(x)} {_n(t)}h{_n(w)}v{_n(h)}h{_n(-w)}z" fill="{body}"/>',
         f'<path d="M{_n(x)} {_n(t)}h{_n(w)}v{_n(34*s)}h{_n(-w)}z" fill="{mq}"/>',
         f'<path d="M{_n(x+8*s)} {_n(t+8*s)}h{_n(w-16*s)}v{_n(18*s)}h{_n(-w+16*s)}z" fill="#fff" opacity="{.75 if n else .55}"/>',
         f'<path d="M{_n(x+10*s)} {_n(t+44*s)}h{_n(w-20*s)}v{_n(70*s)}h{_n(-w+20*s)}z" fill="{scr}"/>',
         f'<path d="M{_n(x-6*s)} {_n(t+122*s)}h{_n(w+12*s)}v{_n(22*s)}h{_n(-w-12*s)}z" fill="{dk}"/>',
         f'<path d="M{_n(x+34*s)} {_n(t+170*s)}h{_n(32*s)}v{_n(36*s)}h{_n(-32*s)}z" fill="{dk}"/>',
         f'<path d="M{_n(x+44*s)} {_n(t+180*s)}h{_n(4*s)}v{_n(12*s)}h{_n(-4*s)}z" fill="#ff5a3d"/>']
    r = random.Random(screen_seed)
    cols = ["#3df2ff", "#4f98ff", "#ffd23f", "#39ff6a"]
    pix = ''.join(f'M{_n(x+(14+r.randint(0,60))*s)} {_n(t+(50+r.randint(0,52))*s)}h{_n(6*s)}v{_n(6*s)}h{_n(-6*s)}z' for _ in range(6))
    dur = 3 + (screen_seed % 4) * .9   # the attract-mode pixels blink, each cabinet out of step
    o.append(f'<path d="{pix}" fill="{r.choice(cols)}">' + (flicker(["0", ".45", ".55", ".8"], ["1", ".3", "1", ".6"], dur, screen_seed * .37) if glow else "") + '</path>')
    o.append(f'<path d="M{_n(x+22*s)} {_n(t+127*s)}h{_n(5*s)}v{_n(10*s)}h{_n(-5*s)}z M{_n(x+60*s)} {_n(t+128*s)}h{_n(8*s)}v{_n(8*s)}h{_n(-8*s)}z M{_n(x+74*s)} {_n(t+128*s)}h{_n(8*s)}v{_n(8*s)}h{_n(-8*s)}z" fill="#ffd23f"/>')
    if n:
        o.append(f'<path d="M{_n(x+10*s)} {_n(t+44*s)}h{_n(w-20*s)}v{_n(70*s)}h{_n(-w+20*s)}z" fill="{r.choice(cols)}" opacity=".18">'
                 + (pulse(".18;.34;.18", dur + 1.4, screen_seed * .5) if glow else "") + '</path>')
    return ''.join(o)

# ------------------------------------------------------------------ the Digest picture
W, H, SPLIT = 1600, 1700, 377
HZ = SPLIT + 70   # the horizon: the city's feet run on into the leaderboard (Frank, 2026-10-05: "these dont merge right")

def skyline(night):
    n = night; o = []; a = o.append
    if n:
        sky = grad("sky", [(0, "#07021a"), (.45, "#1c0645"), (.8, "#4a0f6e"), (1, "#1a498a")])
        floor = grad("fl", [(0, "#2a0750"), (.25, "#14042e"), (1, "#0b021c")])
    else:
        sky = grad("sky", [(0, "#8f7bff"), (.35, "#c68cff"), (.7, "#9cc5ff"), (1, "#ffd0a8")])
        floor = grad("fl", [(0, "#c3dcff"), (.3, "#d9b3ff"), (1, "#b79cf0")])
    hz = ('<radialGradient id="hz" cx=".5" cy="0" r=".6"><stop offset="0" stop-color="'
          + ("#4f98ff" if n else "#fff2c8") + '" stop-opacity=".7"/><stop offset="1" stop-color="#4f98ff" stop-opacity="0"/></radialGradient>')
    sg = ('<radialGradient id="sp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6c8" stop-opacity=".55"/><stop offset="1" stop-color="#fff6c8" stop-opacity="0"/></radialGradient>')
    win = ('<pattern id="w1" width="18" height="22" patternUnits="userSpaceOnUse"><rect x="5" y="6" width="7" height="9" fill="'
           + ("#ffd23f" if n else "#fff3c8") + '"/></pattern>'
           '<pattern id="w2" width="18" height="22" patternUnits="userSpaceOnUse"><rect x="5" y="6" width="7" height="9" fill="'
           + ("#3df2ff" if n else "#e9f6ff") + '"/></pattern>'
           '<pattern id="w3" width="18" height="22" patternUnits="userSpaceOnUse"><rect x="5" y="6" width="7" height="9" fill="'
           + ("#7ab1ff" if n else "#e3efff") + '"/></pattern>')
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(f'<defs>{sky}{floor}{hz}{sg}{win}{GLOW}</defs><g shape-rendering="crispEdges">')
    a(f'<rect width="{W}" height="{HZ+2}" fill="url(#sky)"/>')
    # ---- sky: stars / clouds, the striped sun, the moon or birds, a ship
    if n:
        a(stars_tw(70, W, 0, 300, 3))
        a(sparkles([(140, 110), (980, 40), (1270, 22), (560, 150)], "#fff", 3).replace('"/>', f'">{pulse("1;.2;1", 2.6, .4)}</path>'))
    else:
        for i, (cx, cy, s) in enumerate([(120, 120, 1.2), (560, 40, 1), (1180, 150, .9), (1500, 210, 1.1)]):
            d = (30 + i * 8) * (1 if i % 2 else -1)   # the pixel clouds drift a little, each its own way
            cl = runs(["...wwww......", ".wwwwwwwww....", "wwwwwwwwwwwww.", "..ppppppppppp"], cx, cy, 10 * s, {'w': "#f7faff", 'p': "#c6deff"}, ' opacity=".85"')
            a(f'<g>{cl}{drift(f"0 0;{d} 0;0 0", 9 + i * 1.5, i * .8)}</g>')
    a(retro_sun(800, 262, 190, n, "ss", [(-.7, .04), (-.58, .055), (-.45, .07), (-.3, .085), (-.13, .1), (.05, .12), (.25, .14)]))
    if n:
        a(f'<circle cx="800" cy="262" r="300" fill="url(#sp)" opacity=".5"/>')
        a(runs(["..mmmm.", ".mmm...", "mmm....", "mmm....", "mmm....", ".mmm...", "..mmmm."], 1470, 26, 9, {'m': "#fff4d6"}))
        # the ship hovers to and fro over the city, its beam with it, its lights blinking
        a('<g>' + runs(SHIP[:3], 1120, 40, 6, {'c': "#3df2ff", 'w': "#e9ffff", 'p': "#a46bff", 'y': "#ffd23f"})
          + runs(SHIP, 1120, 40, 6, {'y': "#ffd23f"}).replace('"/>', f'">{flicker(["0", ".5"], ["1", ".2"], 1.2)}</path>')
          + runs(SHIP[3:], 1120, 58, 6, {'p': "#a46bff"})
          + '<path d="M1150 70 L1120 160 L1210 160 Z" fill="#3df2ff" opacity=".12">' + pulse(".12;.04;.12", 3.4) + '</path>'
          + drift("0 0;-56 -6;0 0", 10) + '</g>')
    else:
        for i, (bx, by) in enumerate([(1040, 70), (1080, 92), (1010, 100), (300, 40), (330, 60)]):
            dx = 46 if i < 3 else -40   # the two flocks glide back and forth
            a(f'<g>{runs(BIRD, bx, by, 5, {"k": "#4a2a7a"})}{drift(f"0 0;{dx} {-6 + i * 3} ;0 0", 8 if i < 3 else 7, i * .3)}</g>')
    # ---- the city: pixel towers rising into 0..170 between the tiles
    bc = ["#250a4a", "#2f0d5c", "#1c0838"] if n else ["#7a4fc0", "#9a62d6", "#6a44b0"]
    edge = "#4f98ff" if n else "#e1eeff"
    towers = [(10, 150, 120, 0, "w1"), (140, 95, 90, 1, "w2"), (240, 170, 140, 2, "w3"), (380, 105, 140, 0, "w1"),
              (505, 160, 90, 1, "w2"), (1000, 118, 120, 2, "w3"), (1120, 60, 70, 0, "w2"), (1440, 120, 160, 1, "w1"),
              (1530, 80, 70, 2, "w3")]
    for x, top, w, ci, pat in towers:
        a(f'<rect x="{x}" y="{top}" width="{w}" height="{HZ-top}" fill="{bc[ci]}"/>')
        a(f'<rect x="{x+6}" y="{top+16}" width="{w-12}" height="{HZ-top-40}" fill="url(#{pat})" opacity="{.85 if n else .7}"/>')
        # a lit shopfront at street level
        a(f'<rect x="{x+8}" y="{HZ-22}" width="{w-16}" height="18" fill="{"#3df2ff" if ci == 1 else "#ffd23f" if ci == 0 else "#7ab1ff"}" opacity="{.75 if n else .5}"/>')
        a(f'<rect x="{x}" y="{top}" width="{w}" height="5" fill="{edge}"/>')
        # stepped pixel crown
        a(f'<rect x="{x+w*.25:.0f}" y="{top-14}" width="{w*.5:.0f}" height="14" fill="{bc[ci]}"/><rect x="{x+w*.45:.0f}" y="{top-34}" width="6" height="20" fill="{bc[ci]}"/>')
        a(f'<rect x="{x+w*.45-2:.0f}" y="{top-40}" width="10" height="8" fill="{"#3d8eff" if n else "#6fabff"}"/>')
    for x, top, w, ci in [(640, 360, 110, 1), (860, 352, 130, 2), (1300, 330, 140, 0)]:
        a(f'<rect x="{x}" y="{top}" width="{w}" height="{HZ-top}" fill="{bc[ci]}"/><rect x="{x}" y="{top}" width="{w}" height="4" fill="{edge}"/>'
          f'<rect x="{x+6}" y="{top+14}" width="{w-12}" height="{HZ-top-40}" fill="url(#w{ci+1})" opacity="{.85 if n else .7}"/>')
    # the arcade's doors at the head of the lane, light spilling out
    a(f'<rect x="752" y="{HZ-64}" width="116" height="64" fill="{bc[2]}"/><rect x="746" y="{HZ-70}" width="128" height="8" fill="{edge}"/>'
      f'<rect x="782" y="{HZ-46}" width="56" height="46" fill="{"#fff2a8" if n else "#fff8d8"}"/>'
      f'<rect x="782" y="{HZ-46}" width="56" height="46" fill="#ffd23f" opacity=".5">{pulse(".5;.15;.5", 2.4)}</rect>')
    # neon signs on the towers
    def neon(x, y, s, c, p=5, fl=""):
        tw = twidth(s, p)
        bg = "#14042e" if n else "#3b1a6e"
        return (f'<rect x="{x-8}" y="{y-8}" width="{tw+16}" height="{5*p+16}" fill="{bg}" stroke="{c}" stroke-width="3"/>'
                + (f'<g filter="url(#nl)">{ptext(s, x, y, p, c)}{fl}</g>' if n else f'<g>{ptext(s, x, y, p, c)}{fl}</g>'))
    # QUOTE's tube catches now and then; BONUS stutters on its own clock
    a(neon(392, 124, "QUOTE", "#3df2ff", 4, flicker(["0", ".82", ".85", ".88", ".91", "1"], ["1", ".25", "1", ".4", "1", "1"], 7)))
    a(neon(150, 120, "24/7", "#ffd23f", 4))
    a(neon(1022, 136, "BONUS", "#7ab1ff", 4, flicker(["0", ".3", ".34", ".62", ".65"], ["1", ".3", "1", ".2", "1"], 5.5, 1.5)))
    # ---- the HIGH SCORES marquee on its tower
    mx, my, mw, mh = 1150, 48, 380, 92
    a(f'<rect x="{mx+150}" y="{my+mh}" width="18" height="{HZ-my-mh}" fill="{bc[1]}"/><rect x="{mx+212}" y="{my+mh}" width="18" height="{HZ-my-mh}" fill="{bc[1]}"/>')
    a(f'<rect x="{mx}" y="{my}" width="{mw}" height="{mh}" fill="{"#1a0636" if n else "#3b1a6e"}" stroke="{"#4f98ff" if n else "#6fabff"}" stroke-width="6"/>')
    # the marquee's bulbs chase: odd and even ones trade places every half second
    for k in (0, 1):
        bulbs = ''.join(f'M{mx+8+i*24} {my+3}h6v6h-6z M{mx+8+i*24} {my+mh-9}h6v6h-6z' for i in range(k, 16, 2))
        a(f'<path d="{bulbs}" fill="#ffd23f">' + flicker(["0", ".5"], ["1", ".25"] if k == 0 else [".25", "1"], 1) + '</path>')
    hs = ptext("HIGH SCORES", mx + mw / 2, my + 26, 7, "#ffd23f", "middle", shadow="#3d8eff")
    a(f'<g filter="url(#nl)">{hs}</g>' if n else hs)
    # ---- below the horizon: the grid floor
    a(f'<rect x="0" y="{HZ}" width="{W}" height="{H-HZ}" fill="url(#fl)"/>')
    a(f'<rect x="0" y="{HZ}" width="{W}" height="240" fill="url(#hz)"/>')
    gc = "#4f98ff" if n else "#7ab1ff"
    a(floor_grid(HZ, H, W, 810, gc, .8 if n else .55, nh=10, nv=14, spread=260, sw=3))
    if n: a(f'<g filter="url(#nl)" opacity=".7">{floor_grid(HZ, 900, W, 810, "#4f98ff", .6, nh=4, nv=8, spread=260, sw=2)}</g>')
    a(f'<rect x="0" y="{HZ-2}" width="{W}" height="5" fill="{"#3df2ff" if n else "#f6faff"}"/>')
    # the lane to the stage: cyan edges with chevrons
    lc = "#3df2ff" if n else "#ffffff"
    a(f'<path d="M790 {HZ}L700 800M830 {HZ}L920 800" stroke="{lc}" stroke-width="4" fill="none"{FL if n else ""}/>')
    for k, y in enumerate([470, 520, 600, 694]):
        s = 4 + k * 2.5
        a(runs(["#.....#", ".#...#.", "..#.#..", "...#..."], 810 - 3.5 * s, y, s, {'#': "#ffd23f" if n else "#4f98ff"}, ' opacity=".85"'))
    # ---- the winner's stage under the podium
    st = "#2a0b52" if n else "#7a4fc0"; st2 = "#1a0636" if n else "#5a3399"
    a(f'<rect x="560" y="790" width="500" height="22" fill="{st}"/><rect x="540" y="812" width="540" height="40" fill="{st2}"/>')
    a(f'<rect x="560" y="784" width="500" height="6" fill="{"#3df2ff" if n else "#fff"}"/>')
    lights = ''.join(f'M{556+i*30} 826h12v12h-12z' for i in range(18))
    a(f'<path d="{lights}" fill="#ffd23f"{FL if n else ""}/>')
    if n:
        a('<path d="M640 420 L560 790 L700 790 Z M980 420 L920 790 L1060 790 Z" fill="#fff6c8" opacity=".07"/>')
    # coins hovering by the podium
    for cx, cy in [(700, 525), (920, 518), (690, 480), (930, 474)]:
        a(coin(cx, cy, 4))
    a(sparkles([(720, 500), (900, 492), (590, 520), (1030, 520)], "#fff6c8", 4))
    # ---- the back wall of the hall: a far row of cabinets along the horizon, each blinking on its own
    bodies = ["#3a1a6e", "#5a1f7a", "#2a2a7a"] if n else ["#7b4fd6", "#5a92e0", "#4a7be0"]
    mqs = ["#4f98ff", "#3df2ff", "#ffd23f"]
    for i, x in enumerate([18, 70, 122, 174, 226, 278, 330]):
        a(cabinet(x, HZ + 60, .36, bodies[i % 3], mqs[(i + 1) % 3], n, 20 + i, glow=i % 2 == 0))
    for i, x in enumerate([1240, 1292, 1344, 1396, 1448, 1500, 1552]):
        a(cabinet(x, HZ + 60, .36, bodies[(i + 2) % 3], mqs[i % 3], n, 30 + i, glow=i % 2 == 1))
    # ---- arcade cabinets lined up on each side
    for i, (x, base, s) in enumerate([(430, 560, .5), (300, 620, .7), (130, 712, .95), (-60, 830, 1.25)]):
        a(cabinet(x, base, s, bodies[i % 3], mqs[i % 3], n, i, glow=True))
    for i, (x, base, s) in enumerate([(1120, 560, .5), (1230, 620, .7), (1360, 712, .95), (1520, 830, 1.25)]):
        a(cabinet(x, base, s, bodies[(i + 1) % 3], mqs[(i + 2) % 3], n, i + 9, glow=True))
    # players at the cabinets, backs to us, heads bobbing to their games
    hair = ["#2a1608", "#6a3a14", "#111", "#c58a3a"]
    shirt = ["#ff8a3d", "#39ff6a", "#3df2ff", "#ffd23f"]
    BACK = ["..hhhh..", ".hhhhhh.", ".hhhhhh.", "..ssss..", ".bbbbbb.", "bbbbbbbb", "s.bbbb.s", "..kkkk..", "..k..k..", ".kk..kk."]
    def kid(x, y, p, k, bob=0.0):
        pal = {'h': hair[k % 4], 's': "#e0a878" if k % 2 else "#8a5a3a", 'b': shirt[k % 4], 'k': "#2a2a5a"}
        head = runs(BACK[:3], x, y, p, pal)
        body = runs(BACK[3:], x, y + 3 * p, p, pal)
        if bob:
            head = f'<g>{head}{drift(f"0 0;0 {p*.5:.1f};0 0", bob, k * .3)}</g>'
        return body + head
    a(kid(318, 556, 6, 1, 1.4))          # at the mid cabinet on the left
    a(kid(1248, 556, 6, 2, 1.7))         # and on the right
    a(kid(1378, 620, 9, 3, 1.2))         # at the near right cabinet
    # ---- air hockey on the left: a puck flying end to end between two players' mallets
    tc = "#1d5fd6" if n else "#3f86f0"
    a(f'<path d="M262 664h176l20 26h-216z" fill="{tc}"/><path d="M242 690h216v14h-216z" fill="{"#14042e" if n else "#3b1a6e"}"/>'
      f'<path d="M256 704h10v52h-10zM434 704h10v52h-10z" fill="{"#14042e" if n else "#3b1a6e"}"/>'
      f'<path d="M350 664v26" stroke="#ff5a3d" stroke-width="3"/><path d="M268 672h4v12h-4zM428 672h4v12h-4z" fill="#ffd23f"/>')
    a(f'<ellipse cx="290" cy="677" rx="9" ry="5" fill="#111"><animateTransform attributeName="transform" type="translate" values="0 0;124 4;0 -5;124 -2;0 0" dur="2.4s" repeatCount="indefinite"/></ellipse>')
    a(f'<g><ellipse cx="276" cy="676" rx="10" ry="6" fill="#ff5a3d"/><ellipse cx="276" cy="674" rx="4" ry="3" fill="#ffd0c0"/><animateTransform attributeName="transform" type="translate" values="0 0;4 0;0 -4;4 0;0 0" dur="2.4s" repeatCount="indefinite"/></g>')
    a(f'<g><ellipse cx="424" cy="678" rx="10" ry="6" fill="#39ff6a"/><ellipse cx="424" cy="676" rx="4" ry="3" fill="#d8ffe0"/><animateTransform attributeName="transform" type="translate" values="0 0;-4 2;0 0;-4 -2;0 0" dur="2.4s" repeatCount="indefinite"/></g>')
    a(kid(206, 650, 8, 0) + kid(436, 652, 5.5, 2))
    # ---- the dance machine on the right: arrow pads lighting in turn, a dancer jumping on them
    mb = "#2a0b52" if n else "#5a3399"
    a(f'<rect x="1160" y="606" width="150" height="110" fill="{mb}"/><rect x="1166" y="612" width="138" height="20" fill="#3df2ff"/>'
      f'<rect x="1176" y="640" width="118" height="60" fill="#0b1a2e"/>{ptext("DANCE", 1235, 616, 2.4, "#14042e", "middle")}')
    for k, (ax, c) in enumerate([(1186, "#ff8a3d"), (1214, "#3df2ff"), (1242, "#39ff6a"), (1270, "#ffd23f")]):
        a(f'<rect x="{ax}" y="660" width="14" height="14" fill="{c}" opacity=".3">'
          + flicker([f"{k*.25:.2f}", f"{k*.25+.12:.2f}"] if k else ["0", ".12"], ["1", ".3"], 2, 0) + '</rect>')
    a(f'<path d="M1150 772h170l-14 -56h-142z" fill="{"#1a0636" if n else "#4a2a88"}"/>')
    for k, (px, py) in enumerate([(1190, 724), (1252, 724), (1176, 748), (1264, 748)]):
        a(f'<path d="M{px} {py}h34v18h-34z" fill="{["#ff8a3d", "#3df2ff", "#39ff6a", "#ffd23f"][k]}" opacity=".45">'
          + pulse(".45;1;.45", 1, k * .25) + '</path>')
    dpal = {'h': "#3d1a08", 'v': "#3df2ff", 'w': "#fff", 's': "#e0a878", 'b': "#ff8a3d", 'y': "#ffd23f", 'k': "#14042e"}
    a(f'<g>{runs(HERO, 1206, 658, 8, dpal)}<animateTransform attributeName="transform" type="translate" values="0 0;0 -16;0 0;10 -12;0 0" dur="1s" repeatCount="indefinite"/></g>')
    # the 1UP sign and a PLAYER 1 sign
    a(f'<rect x="1025" y="496" width="10" height="44" fill="{st2}"/><rect x="980" y="446" width="100" height="56" fill="#14042e" stroke="#39ff6a" stroke-width="4"/>')
    a(f'<g filter="url(#nl)">{ptext("1UP", 1030, 459, 7, "#39ff6a", "middle")}{flicker(["0", ".6"], ["1", ".15"], 1.6)}</g>')
    a(f'<rect x="585" y="496" width="10" height="44" fill="{st2}"/><rect x="510" y="452" width="160" height="50" fill="#14042e" stroke="#4f98ff" stroke-width="4"/>')
    a(f'<g filter="url(#nl)">{ptext("PLAYER 1", 590, 466, 4, "#7ab1ff", "middle")}</g>')
    a('</g></svg>')
    return ''.join(o)

# ------------------------------------------------------------------ the page banners (1600 x 240)
def scene(n, body_fn, **kw):
    kw.setdefault("tw", True)   # the banners' night stars twinkle
    bg, defs = vbg(n, **kw)
    cd, cr = corners()
    return wrap(240, bg + body_fn() + cr, defs + cd)

# banner movement (Frank, 2026-10-05: "add movement to the new worlds' banners too"): self-closing SMIL only,
# so each element's own attributes are its resting state and build.py's still copy is the drawing as it was.
SPL = 'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"'
def _rep(dur, delay): return f'dur="{dur}s" begin="{-delay}s" repeatCount="indefinite"'
def bob(dx, dy, dur, delay=0):
    return f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" keyTimes="0;.5;1" {SPL} {_rep(dur, delay)}/>'
def rock(a, cx, cy, dur, delay=0):
    return f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};{a} {cx} {cy};0 {cx} {cy}" keyTimes="0;.5;1" {SPL} {_rep(dur, delay)}/>'
def turn(cx, cy, dur):
    return f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" keyTimes="0;1" {_rep(dur, 0)}/>'
def blink(vals, dur, delay=0, attr="opacity"):
    v = vals.split(";"); kt = ";".join(_n(i / (len(v) - 1)) for i in range(len(v)))
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" {_rep(dur, delay)}/>'
def steps(attr, vals, times, dur, delay=0):
    if times.split(";")[-1] != "1": vals += ";" + vals.split(";")[-1]; times += ";1"   # keyTimes always end at 1
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{times}" calcMode="discrete" {_rep(dur, delay)}/>'
def G(body, *anims): return '<g>' + ''.join(anims) + body + '</g>'

def v_sales(n):  # the jackpot
    def b():
        o = []
        x, y = 690, 30
        o.append(f'<rect x="{x}" y="{y}" width="220" height="170" fill="#185fc2"/><rect x="{x+10}" y="{y+10}" width="200" height="34" fill="#14042e"/>')
        o.append(G(label(x + 110, y + 17, "JACKPOT", 3.4, "#ffd23f"), steps("opacity", "1;.25;1;.25;1", "0;.82;.86;.9;.94", 6)))
        o.append(f'<rect x="{x+16}" y="{y+56}" width="188" height="64" fill="#fff8e8"/>')
        for i in range(3):
            o.append(f'<rect x="{x+22+i*62}" y="{y+60}" width="56" height="56" fill="#fff"/>')
            o.append(ptext("7", x + 50 + i * 62, y + 69, 7, "#2070e0", "middle"))
            # the reel spinning: a blur of symbols over the 7 from the pull until it stops, left reel first
            o.append(f'<path d="{"".join(f"M{x+28+i*62} {y+64+k*10}h44v5h-44z" for k in range(5))}" fill="#7ab1ff" opacity="0">'
                     + steps("opacity", "0;1;0", f"0;.1;{.5+i*.1:.1f}", 6) + '</path>'
                     + f'<rect x="{x+22+i*62}" y="{y+60}" width="56" height="56" fill="#fff" opacity="0">'
                     + steps("opacity", "0;.75;0", f"0;.1;{.5+i*.1:.1f}", 6) + '</rect>')
        o.append(f'<rect x="{x+60}" y="{y+132}" width="100" height="16" fill="#14042e"/>')
        lv = f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 44;0 0;0 0" keyTimes="0;.02;.08;.16;1" {_rep(6, 0)}/>'
        o.append(G(f'<rect x="{x+220}" y="{y+40}" width="10" height="70" fill="#9aa0b8"/><rect x="{x+214}" y="{y+22}" width="22" height="22" fill="#3d8eff"/>', lv))
        r = random.Random(4)
        for k in range(16):
            cx = x + 70 + r.randint(-40, 120); cy = 150 + r.randint(0, 60) - (k % 5) * 8
            if k < 6: cx, cy = x + 90 + k * 8 - 20, 168 + (k % 3) * 12
            o.append(G(coin(cx, cy, 3), bob(0, -12, 1.6, k * .27)) if k in (0, 2, 4) else coin(cx, cy, 3))
        for cx, cy in [(560, 160), (600, 176), (1000, 170), (1040, 150), (1080, 178), (480, 120), (1130, 90)]:
            o.append(coin(cx, cy, 3))
        o.append(G(sparkles([(640, 60), (1040, 100)], "#fff6c8", 4), blink("1;.1;1", 2.2)))
        o.append(G(sparkles([(960, 50), (560, 90)], "#fff6c8", 4), blink("1;.1;1", 2.2, 1.1)))
        return ''.join(o)
    return scene(n, b, sun=(1300, 90))

def v_messages(n):  # chat bubbles and a dial-up modem
    def b():
        o = []
        def bubble(x, y, w, txt, c, tail="l"):
            t = (f'M{x+16} {y+40}h12v12h-12z M{x+10} {y+52}h8v8h-8z' if tail == "l" else f'M{x+w-28} {y+40}h12v12h-12z M{x+w-18} {y+52}h8v8h-8z')
            return (f'<path d="M{x+6} {y}h{w-12}v6h6v{28}h-6v6h{-(w-12)}v-6h-6v-28h6z" fill="{c}"/><path d="{t}" fill="{c}"/>'
                    + ptext(txt, x + w / 2, y + 10, 4, "#14042e", "middle"))
        o.append(G(bubble(470, 62, 150, "HI THERE", "#ffffff"), bob(0, -5, 4.4)))
        o.append(G(bubble(640, 46, 150, "QUOTE?", "#3df2ff", "r"), bob(0, -5, 4.4, 1.5)))
        # someone is typing: the three dots light in turn
        o.append(G(bubble(960, 68, 110, "", "#ffd23f") + ''.join(
            f'<rect x="{995+k*16}" y="80" width="8" height="8" fill="#14042e">{blink("1;.2;1;1", 1.5, -k * .25)}</rect>' for k in range(3)), bob(0, -5, 4.4, 3)))
        o.append(G(bubble(1100, 50, 150, "THANKS!", "#7ab1ff", "r"), bob(0, -5, 4.4, 2.2)))
        # the modem
        mx, my = 660, 120
        o.append(f'<rect x="{mx}" y="{my}" width="270" height="44" fill="#e9dfc6"/><rect x="{mx}" y="{my+44}" width="270" height="8" fill="#b9ad93"/><rect x="{mx+10}" y="{my+10}" width="120" height="10" fill="#b9ad93"/>')
        o.append(''.join(f'<path d="M{mx+150+i*20} {my+18}h10v8h-10z" fill="#39ff6a">'
                         + steps("opacity", "1;.25;1;.4;1", "0;.2;.45;.6;.85", 1.3 + i * .37, i * .5) + '</path>' for i in range(5)))
        o.append(f'<path d="M{mx+230} {my+18}h10v8h-10z" fill="#3d8eff"/>')
        o.append(f'<path d="M{mx+270} {my+30} q60 10 60 -40 t70 -30" fill="none" stroke="#2a1240" stroke-width="4"/>')
        o.append(ptext("56K", mx + 16, my + 28, 2.5, "#7a6a50"))
        for k in range(3):
            o.append(f'<path d="M{mx+135-k*14} {my-8-k*14} q{14+k*14} -{14+k*14} {28+k*28} 0" fill="none" stroke="#fff" stroke-width="4" opacity="{.8-.2*k:.1f}">'
                     + blink(f"{.8-.2*k:.1f};.1;{.8-.2*k:.1f}", 1.8, -k * .3) + '</path>')
        return ''.join(o)
    return scene(n, b, top_day=("#5a7bff", "#a98cff", "#b3d3ff"))

def v_coaching(n):  # a PAUSE screen with a replay
    def b():
        o = []
        x, y, w, h = 560, 22, 480, 150
        o.append(f'<rect x="{x-14}" y="{y-12}" width="{w+28}" height="{h+24}" fill="{"#2a1a3e" if n else "#4a3a5e"}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0b0820"/>')
        o.append(hero(x + 60, y + 52, 6, {'b': "#6a3df0"}) + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0b0820" opacity=".45"/>')
        o.append(G(label(x + w / 2, y + 20, "PAUSE", 8, "#ffd23f"), steps("opacity", "1;.15", "0;.6", 1.8)))
        o.append(ptext("CONTINUE", x + w / 2 + 40, y + 78, 4, "#fff", "middle"))
        o.append(ptext("REPLAY CALL", x + w / 2 + 40, y + 102, 4, "#3df2ff", "middle"))
        o.append(G(runs(["#..", "##.", "###", "##.", "#.."], x + w / 2 - 70, y + 100, 4, {'#': "#3df2ff"}), bob(6, 0, 1.2)))
        o.append(f'<path d="{"".join(f"M{x} {y+k*6}h{w}v2h-{w}z" for k in range(0, 25))}" fill="#000" opacity=".25"/>')
        o.append(f'<rect x="{x+20}" y="{y+h-14}" width="{w-40}" height="6" fill="#3a2a5a"/><rect x="{x+20}" y="{y+h-14}" width="{(w-40)*.62:.0f}" height="6" fill="#4f98ff">'
                 f'<animate attributeName="width" values="0;{w-40};{w-40}" keyTimes="0;.9;1" {_rep(10, 6.2)}/></rect>')
        return ''.join(o)
    return scene(n, b, top_day=("#3a2a7a", "#7a4fc0", "#c08ae0"), top_night=("#05020f", "#140a30", "#2a0b52"))

def v_roleplay(n):  # versus screen
    def b():
        o = ['<path d="M0 0H820L760 240H0Z" fill="#4f98ff" opacity=".35"/><path d="M820 0H1600V240H760Z" fill="#3df2ff" opacity=".28"/>']
        o.append('<path d="M820 0L760 240" stroke="#fff" stroke-width="6"/>')
        o.append(G(hero(560, 52, 11), bob(0, -6, 1.4)))
        o.append(G(hero(960, 52, 11, {'h': "#3df2ff", 'b': "#ff7a1a", 'v': "#4f98ff"}), bob(0, -6, 1.4, .7)))
        o.append(G(label(790, 70, "VS", 10, "#ffd23f"), blink("1;.7;1", 2.4)))
        o.append(ptext("PLAYER 1", 400, 112, 5, "#fff", "middle"))
        o.append(f'<g>{ptext("PLAYER 2", 1240, 100, 5, "#fff", "middle")}{G(ptext("READY", 1240, 136, 5, "#ffd23f", "middle"), steps("opacity", "1;0", "0;.55", 1.6))}</g>')
        return ''.join(o)
    return scene(n, b, top_day=("#5a2a9a", "#8a4fd0", "#7aa4e0"), top_night=("#08021a", "#1c0645", "#3a0b62"))

def v_rphistory(n):  # a shelf of cartridges and a replay tape
    def b():
        o = []
        sh = "#5a3a2a" if not n else "#3a2418"
        o.append(f'<rect x="420" y="150" width="760" height="14" fill="{sh}"/><rect x="420" y="164" width="760" height="6" fill="#000" opacity=".3"/>')
        cols = ["#4f98ff", "#3df2ff", "#ffd23f", "#39ff6a", "#a46bff", "#ff7a1a", "#3d8eff"]
        for i in range(9):
            cx = 440 + i * 62; h = 96 + (i * 13) % 20
            c = (f'<rect x="{cx}" y="{150-h}" width="50" height="{h}" fill="#4a4a5a"/><rect x="{cx+6}" y="{150-h+10}" width="38" height="{h-40}" fill="{cols[i%7]}"/>'
                 f'<rect x="{cx+10}" y="{150-26}" width="30" height="6" fill="#2a2a38"/>' + ptext(str(i + 1), cx + 25, 150 - h + 20, 4, "#14042e", "middle"))
            # one cartridge at a time is pulled to be replayed
            o.append(c if i not in (4, 7) else G(c, f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -22;0 -22;0 0;0 0" '
                     f'keyTimes="0;.1;.2;.4;.5;1" {_rep(9, 0 if i == 4 else 4.5)}/>'))
        tx = 1010
        o.append(f'<rect x="{tx}" y="64" width="150" height="86" fill="#1a1a24"/><rect x="{tx+14}" y="80" width="122" height="40" fill="#e9dfc6"/>')
        o.append(f'<circle cx="{tx+46}" cy="100" r="13" fill="#1a1a24"/><circle cx="{tx+104}" cy="100" r="13" fill="#1a1a24"/><rect x="{tx+40}" y="128" width="70" height="10" fill="#3a3a48"/>')
        for rx in (tx + 46, tx + 104):   # the reels' hubs turning
            o.append(G(f'<path d="M{rx-2} 90h4v20h-4z M{rx-10} 98h20v4h-20z" fill="#e9dfc6"/>', turn(rx, 100, 2.4)))
        o.append(G(ptext("REPLAY", tx + 75, 84, 2.4, "#185fc2", "middle"), steps("opacity", "1;.2", "0;.6", 1.6)))
        return ''.join(o)
    return scene(n, b, top_day=("#4a2a7a", "#8a5ac0", "#a0bbe0"), top_night=("#06021a", "#170838", "#3a0f5a"))

def v_training(n):  # the tutorial level
    def b():
        o = []
        pc = "#39b86a"; pd = "#7a4a2a"
        for x, y, w in [(420, 150, 200), (680, 112, 160), (900, 80, 150), (1100, 120, 180)]:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="14" fill="{pc}"/><rect x="{x}" y="{y+14}" width="{w}" height="24" fill="{pd}"/>'
                     f'<path d="{"".join(f"M{x+6+k*20} {y+20}h8v6h-8z" for k in range(w//20))}" fill="#5a3418"/>')
        o.append(hero(520, 108, 4.2, rows=HERO))
        o.append(G(hero(740, 52, 4.2, rows=HERO_JUMP), bob(0, -10, 1.8)))
        o.append(f'<path d="M560 100 Q640 20 740 44" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="8 8"/>')
        for k, x in enumerate([960, 1000, 1150, 1190]): o.append(G(coin(x, 50 if x < 1100 else 90, 3), bob(0, -6, 1.6, k * .4)))
        o.append(G(runs(["..#..", "...#.", "#####", "...#.", "..#.."], 640, 160, 6, {'#': "#ffd23f"}), steps("opacity", "1;.2", "0;.6", 1.4)))
        o.append(f'<rect x="1260" y="40" width="6" height="80" fill="#fff"/><path d="M1266 40L1310 40L1310 54L1266 54Z" fill="#4f98ff">'
                 f'<animate attributeName="d" values="M1266 40L1310 40L1310 54L1266 54Z;M1266 40L1308 46L1308 60L1266 54Z;M1266 40L1310 40L1310 54L1266 54Z" keyTimes="0;.5;1" {SPL} {_rep(1.6, 0)}/></path>')
        o.append(label(250, 96, "TUTORIAL", 5, "#fff", "middle"))
        return ''.join(o)
    return scene(n, b, top_day=("#4aa8ff", "#9ad0ff", "#e0edff"), top_night=("#06021a", "#140a3a", "#2a1a62"))

def v_map(n, athena=False):  # a level-select world map
    route = "#2fd07a" if athena else "#3d8eff"
    def b():
        o = []
        sea = "#2a6ad0" if not n else "#0f1c4a"
        o.append(f'<rect width="1600" height="240" fill="{sea}"/>')
        o.append(f'<path d="{"".join(f"M{x} {y}h18v4h-18z" for x, y in [(80,40),(260,90),(1460,60),(1300,30),(150,150),(1500,150)])}" fill="#fff" opacity=".35">'
                 + bob(12, 0, 6) + '</path>')
        land = "#5fc56a" if not n else "#1f5a3a"; land2 = "#3f9a4a" if not n else "#163f2a"; sand = "#f2d48a" if not n else "#6a5a3a"
        o.append(f'<path d="M300 200 V140 H340 V90 H420 V60 H560 V40 H760 V60 H900 V30 H1080 V50 H1200 V90 H1280 V140 H1320 V200 Z" fill="{sand}"/>')
        o.append(f'<path d="M316 196 V146 H354 V98 H432 V70 H570 V52 H770 V72 H906 V44 H1070 V62 H1190 V100 H1266 V146 H1304 V196 Z" fill="{land}"/>')
        for x, y in [(470, 110), (520, 150), (1010, 150), (1150, 120), (700, 160)]:
            o.append(runs(["..t..", ".ttt.", "ttttt", "..b.."], x, y, 7, {'t': land2, 'b': "#6a3a1a"}))
        pts = [(400, 170), (640, 118), (940, 160), (1200, 112)]
        names = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
        path = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            for k in range(1, 12):
                t = k / 12; path.append(f'M{x1+(x2-x1)*t-4:.0f} {y1+(y2-y1)*t-4:.0f}h8v8h-8z')
        o.append(f'<path d="{"".join(path)}" fill="#fff"/>')
        ink = "#14042e"
        for i, ((x, y), t) in enumerate(zip(pts, names)):
            o.append(f'<rect x="{x-16}" y="{y-16}" width="32" height="32" fill="{route}" stroke="#fff" stroke-width="4"/>'
                     f'<rect x="{x-16}" y="{y-16}" width="32" height="32" fill="#fff" opacity="0">'
                     + steps("opacity", "0;.55;0", f"0;{i*.25:.2f};{i*.25+.12:.2f}", 4, 0) + '</rect>')
            o.append(ptext(str(i + 1), x, y - 7, 3, "#fff", "middle"))
            tw = len(t) * 11 + 18
            o.append(f'<rect x="{x-tw/2:.0f}" y="{y-54}" width="{tw}" height="28" fill="#fffaf0" stroke="{ink}" stroke-width="3"/>'
                     f'<text x="{x}" y="{y-34}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="{ink}">{t}</text>')
        o.append(hero(330, 134, 3.4) if not athena else hero(330, 134, 3.4, {'h': "#2fd07a", 'b': "#1a7d5a"}))
        o.append(G(runs(STAR, 1262, 70, 5, {'y': "#ffd23f"}), bob(0, -6, 2)))
        o.append(ptext("WORLD 1 · " + ("ATHENA" if athena else "APOLLO"), 1400, 196, 3, "#fff", "middle") if False else "")
        return ''.join(o)
    cd, cr = corners()
    return wrap(240, b() + cr, cd)

def v_service(n):  # the repair shop
    def b():
        o = []
        wall = "#3a2a5a" if not n else "#1a0f30"
        o.append(f'<rect width="1600" height="172" fill="{wall}" opacity=".55"/>')
        o.append(f'<rect x="1060" y="56" width="260" height="40" fill="#14042e" stroke="#3df2ff" stroke-width="4"/>')
        o.append(G(label(1190, 67, "REPAIR SHOP", 3.6, "#3df2ff"), steps("opacity", "1;.3;1;.4;1", "0;.7;.73;.78;.81", 5)))
        # an open cabinet: side panel swung open, wires inside
        x, base = 700, 200
        o.append(cabinet(x, base, .58, "#5a1f7a", "#ffd23f", n, 3))
        o.append(f'<rect x="706" y="92" width="46" height="41" fill="#3df2ff" opacity="0">' + steps("opacity", "0;.35;0;.2;0", "0;.3;.38;.6;.66", 2.6) + '</rect>')   # its screen sputtering back
        o.append(f'<path d="M{x+58} {base-133}L{x+108} {base-122}V{base-8}L{x+58} {base}Z" fill="#7a3a9a"/>')
        o.append(f'<path d="M{x+14} {base-60}q20 20 0 40 M{x+24} {base-60}q14 24 18 44" stroke="#3d8eff" stroke-width="3" fill="none"/><path d="M{x+34} {base-62}q-10 20 6 46" stroke="#39ff6a" stroke-width="3" fill="none"/>')
        o.append(hero(860, 112, 6, {'h': "#ffd23f", 'b': "#2a6ad0", 'y': "#ff7a1a"}))
        o.append(G(f'<g transform="rotate(-30 932 140)"><path d="M926 112h10v50h-10z M918 104h26v14h-6v-6h-14v6h-6z" fill="#c9d1dc"/></g>', rock(-22, 920, 156, 1.6)))
        o.append(f'<rect x="1000" y="168" width="90" height="34" fill="#3d8eff"/><rect x="1030" y="158" width="30" height="10" fill="#1a4f9a"/><rect x="1000" y="180" width="90" height="4" fill="#1a4f9a"/>')
        o.append(G(sparkles([(700, 90), (650, 140)], "#ffd23f", 4), blink("1;0;1", 1.6)))
        return ''.join(o)
    return scene(n, b, top_day=("#7a4fc0", "#b07ae0", "#c0daff"))

def v_renewals(n):  # extra lives: 1UP hearts coming back
    def b():
        o = []
        o.append(G(hero(760, 104, 6), f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -14;0 0" keyTimes="0;.6;.8;1" {SPL.replace(".45 0 .55 1;", ".45 0 .55 1;.2 0 .4 1;")} {_rep(2.4, 0)}/>'))
        for k, (x, y, s) in enumerate([(560, 120, 6), (640, 70, 5), (900, 64, 5), (980, 110, 6), (720, 50, 4), (1080, 80, 4)]):
            o.append(G(heart(x, y, s) + f'<path d="M{x+3.5*s} {y+6*s+6}v18" stroke="#fff" stroke-width="3" stroke-dasharray="4 4" opacity=".7"/>', bob(0, -8, 3 + k % 3 * .6, k * .7)))
        o.append(G(label(1160, 60, "+1UP", 5, "#39ff6a"), steps("opacity", "1;.2;1;.2;1", "0;.6;.67;.74;.81", 3)))
        o.append(ptext("EXTRA LIFE", 450, 64, 3.6, "#fff", "middle", shadow="#185fc2"))
        return ''.join(o)
    return scene(n, b, top_day=("#8abbff", "#b3d3ff", "#ffe0c0"), sun=(800, 80))

def v_claims(n):  # after the storm: a glitched screen being fixed
    def b():
        o = []
        cl = "#4a3a6a" if not n else "#2a1a40"
        o.append(runs(["....cccc....", "..cccccccc..", ".cccccccccccc", "cccccccccccccc", ".cccccccccccc."], 300, 30, 12, {'c': cl}))
        o.append(f'<path d="{"".join(f"M{x} {y}h4v12h-4z" for x, y in [(330,100),(370,120),(410,96),(450,114),(490,104)])}" fill="#9ad0ff" opacity=".6">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 -10;0 22" keyTimes="0;1" {_rep(1.6, 0)}/>{blink("0;.6;.6;0", 1.6)}</path>')
        x, y, w, h = 640, 30, 300, 140
        o.append(f'<rect x="{x-12}" y="{y-12}" width="{w+24}" height="{h+24}" fill="#2a1a3e"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0b0820"/>')
        r = random.Random(9)
        bars = []
        for k in range(8):
            yy = y + 6 + k * 16; off = r.randint(-30, 30)
            bars.append(f'<rect x="{max(x, x+40+off)}" y="{yy}" width="{r.randint(60, 200)}" height="10" fill="{r.choice(["#4f98ff", "#3df2ff", "#39ff6a", "#ffd23f"])}" opacity=".85"/>')
        for k in range(2):   # the broken half glitches, rows out of step (the fixed half covers anything that jumps right)
            o.append(G(''.join(bars[k::2]), f'<animateTransform attributeName="transform" type="translate" values="0 0;{10-k*18} 0;{-6+k*10} 0;0 0;0 0" '
                       f'keyTimes="0;.1;.16;.22;1" calcMode="discrete" {_rep(2.6 + k, k * .9)}/>'))
        o.append(f'<rect x="{x+w/2:.0f}" y="{y}" width="{w/2:.0f}" height="{h}" fill="#0b0820"/>')
        o.append(G(ptext("FIXED", x + w * .75, y + 54, 6, "#39ff6a", "middle"), steps("opacity", "1;.2", "0;.65", 1.8)))
        o.append(f'<path d="M{x+w/2} {y}v{h}" stroke="#fff" stroke-width="3" stroke-dasharray="6 6"/>')
        o.append(hero(990, 96, 6, {'h': "#ffd23f", 'b': "#2a6ad0", 'y': "#ff7a1a"}))
        o.append(G(f'<g transform="rotate(35 960 110)"><path d="M954 82h10v50h-10z M946 74h26v14h-6v-6h-14v6h-6z" fill="#c9d1dc"/></g>', rock(18, 980, 140, 1.6)))
        o.append(G(sparkles([(950, 80), (930, 60), (970, 52)], "#ffd23f", 3), blink("1;0;1", 1.6, .8)))
        o.append(sparkles([(1250, 50), (1320, 90)], "#fff", 3))
        return ''.join(o)
    return scene(n, b, top_day=("#6a7ab0", "#a99cd0", "#ffd0c0"), top_night=("#05020f", "#140a30", "#2a1050"))

def v_commercial(n):  # the boss castle
    def b():
        o = []
        cs = "#2a1a40" if n else "#3a1f5c"; win = "#ffd23f"
        o.append('<radialGradient id="lv" cx=".5" cy="1" r=".7"><stop offset="0" stop-color="#ff7a1a" stop-opacity=".7"/><stop offset="1" stop-color="#3d8eff" stop-opacity="0"/></radialGradient>')
        o.append(f'<rect x="440" y="40" width="720" height="140" fill="url(#lv)">{blink("1;.55;1", 3.4)}</rect>')
        o.append(f'<path d="M520 174 V150 H560 V140 H1040 V150 H1080 V174Z" fill="{"#0f213a" if n else "#1a355a"}"/>')
        # walls, towers and battlements in pixel steps
        o.append(f'<path d="M600 140 V84 H612 V74 H628 V84 H644 V74 H660 V84 H676 V60 H690 V50 H706 V60 H720 V40 H736 V30 H752 V40 H768 V30 H784 V40 H800 V24 H816 V40 H832 V30 H848 V40 H864 V30 H880 V40 H896 V60 H910 V50 H926 V60 H940 V84 H956 V74 H972 V84 H988 V74 H1000 V84 V140Z" fill="{cs}"/>')
        o.append(f'<path d="M624 96h14v22h-14z M960 96h14v22h-14z M702 74h14v22h-14z" fill="{win}">' + steps("opacity", "1;.55;1;.7", "0;.3;.45;.8", 2.3) + '</path>'
                 f'<path d="M884 74h14v22h-14z M760 54h14v18h-14z M826 54h14v18h-14z" fill="{win}">' + steps("opacity", "1;.6;1;.5", "0;.2;.55;.7", 1.9, .6) + '</path>')
        o.append('<path d="M772 140 V100 H780 V92 H820 V100 H828 V140Z" fill="#14042e"/>')
        o.append(f'<path d="M774 104h52v4h-52z M774 116h52v4h-52z M774 128h52v4h-52z" fill="#6a5a8a"/>')
        o.append(f'<rect x="806" y="-2" width="4" height="26" fill="{cs}"/><path d="M810 0h56v20h-56z" fill="#3d8eff"/>')
        o.append(ptext("BOSS", 838, 5, 1.8, "#fff", "middle"))
        for x in [560, 640, 960, 1030]:
            o.append(f'<path d="M{x} 150 h8 v-10 h8 v-8 h8 v8 h8 v10 h8 v8 h-40z" fill="#ff7a1a"/><path d="M{x+12} 150 h8 v-10 h8 v10 h8 v8 h-24z" fill="#ffd23f"/>')
        o.append(ptext("BOSS", 1130, 34, 3, "#fff", shadow="#14042e"))
        o.append('<rect x="1130" y="56" width="280" height="18" fill="#14042e" stroke="#fff" stroke-width="3"/><rect x="1136" y="61" width="190" height="8" fill="#3d8eff">'
                 f'<animate attributeName="width" values="190;190;70;70;190" keyTimes="0;.2;.6;.75;1" {_rep(8, 0)}/></rect>')
        # the invaders march: a step at a time, side to side and back
        mv = lambda d, dl: (f'<animateTransform attributeName="transform" type="translate" values="0 0;{d} 0;{2*d} 0;{d} 0;{d} 0" keyTimes="0;.25;.5;.75;1" '
                            f'calcMode="discrete" {_rep(2.4, dl)}/>')
        o.append(G(runs(SQUID, 1220, 100, 8, {'p': "#a46bff", 'w': "#fff"}), mv(16, 0)))
        o.append(G(runs(SQUID, 380, 90, 6, {'p': "#39d07a", 'w': "#fff"}), mv(10, 1.2)))
        return ''.join(o)
    return scene(n, b, top_day=("#4a2a7a", "#4f7ec0", "#ffa070"), top_night=("#05020f", "#1c0630", "#0f2e5a"), starsn=30)

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "jackpot: premium paying out"],
    "messages": ["Texts & Emails", "every message gets a reply"],
    "coaching": ["Coaching", "paused: every call, replayed"],
    "roleplay": ["Role Play", "player 2 ready"],
    "rphistory": ["Session History", "every run, saved to the cartridge"],
    "training": ["Training", "the tutorial level"],
    "blueprint": ["Apollo's Road Map", "level select, in plain words"],
    "athenamap": ["Athena's Road Map", "the service world map, in plain words"],
    "service": ["Service Digest", "the repair shop: keeping the book"],
    "renewals": ["Renewals", "extra lives: what came back"],
    "claims": ["Claims", "after the storm: glitch fixed"],
    "commercial": ["Commercial Center", "the boss castle: Cerberus's book"],
}

# ------------------------------------------------------------------ coaching-card strips (1600 x 160)
def strip(n, body, day=("#5a2a9a", "#9a3fb0"), night=("#0b0420", "#2a0b52"), grid="#4f98ff"):
    c = night if n else day
    defs = grad("sg", [(0, c[0]), (1, c[1])])
    o = [f'<rect width="1600" height="160" fill="url(#sg)"/>']
    if n: o.append(stars(24, 1600, 10, 110, 11))
    o.append(f'<rect x="0" y="118" width="1600" height="42" fill="#000" opacity=".3"/>')
    o.append(floor_grid(118, 200, 1600, 800, grid, .55, nh=3, nv=10, spread=200, sw=2))
    o.append(body)
    return wrap(160, ''.join(o), defs)

def cap(s, col="#fff", sh="#14042e"): return ""   # strips carry no words

def s_sold(n):
    b = [cap("LEVEL CLEARED", "#ffd23f")]
    b.append(runs(TROPHY, 770, 40, 7, {'y': "#ffd23f", 'w': "#fff7c2", 'b': "#7a3a1a"}))
    for x, y in [(640, 60), (700, 40), (900, 44), (960, 66), (1060, 50)]: b.append(star(x, y, 4))
    b.append(sparkles([(740, 40), (870, 100), (600, 100), (1020, 100)], "#fff", 3))
    return strip(n, ''.join(b), day=("#3a6ae0", "#4f85d0"))

def s_open(n):
    b = [cap("CONTINUE?")]
    b.append(f'<rect x="760" y="40" width="80" height="76" fill="#14042e" stroke="#ffd23f" stroke-width="4"/>')
    b.append(hero(640, 44, 7))
    return strip(n, ''.join(b), day=("#7a3aa0", "#6095e0"))

def s_lost(n):
    gp = {'h': "#e4e4ec", 'v': "#2a2a33", 'w': "#2a2a33", 's': "#d8d2ca", 'b': "#3a3a46", 'y': "#c8c8d0", 'k': "#1e1e26"}
    b = [cap("GAME OVER", "#e8e8ee", "#2a2a33")]
    b.append(f'<g transform="translate(-90 -8) rotate(90 792 92)">{hero(760, 52, 8, gp)}</g>')
    b.append('<path d="M640 116h150v6h-150z" fill="#1e1e26" opacity=".5"/>')
    b.append(runs(["..ggg..", ".ggggg.", "ggggggg", "ggrgrgg", "ggggggg", "ggggggg", "ggggggg"], 800, 60, 8, {'g': "#b8b8c4", 'r': "#4a4a56"}))
    return strip(n, ''.join(b), day=("#5a5a66", "#8a8a96"), night=("#0e0e14", "#24242e"), grid="#9a9aa8")

def s_dead(n):
    on = "#ff7a1a"
    b = [cap("INSERT COIN", on)]
    b.append('<rect x="760" y="36" width="90" height="86" fill="#2a1a3e" stroke="#6a5a8a" stroke-width="4"/><rect x="796" y="52" width="18" height="38" fill="#14042e"/>')
    b.append(f'<g filter="url(#nl)"><rect x="788" y="46" width="34" height="50" fill="none" stroke="{on}" stroke-width="4"><animate attributeName="opacity" values="1;.15;1" dur="1.2s" repeatCount="indefinite"/></rect></g>')
    b.append(ptext("25C", 805, 102, 2.5, "#c8b8e0", "middle"))
    b.append(coin(900, 56, 5))
    return strip(n, ''.join(b), day=("#2a456a", "#4a6ea0"), night=("#120418", "#2a0b32"))

def s_reached(n):
    b = [cap("PLAYER 2 JOINED", "#3df2ff")]
    b.append(hero(710, 42, 7))
    b.append(hero(840, 42, 7, {'h': "#3df2ff", 'b': "#ff7a1a", 'v': "#4f98ff"}))
    b.append(sparkles([(814, 60)], "#ffd23f", 5))
    
    return strip(n, ''.join(b), day=("#2a5ad0", "#7a4fd0"))

def s_live_noq(n):
    b = [cap("PAUSED")]
    b.append('<rect x="760" y="40" width="26" height="76" fill="#fff"/><rect x="812" y="40" width="26" height="76" fill="#fff"/>')
    return strip(n, ''.join(b), day=("#4a3a8a", "#7a5ab0"))

def s_vm(n):
    b = [cap("NO ANSWER", "#c8d8ff")]
    b.append(runs(GHOST, 760, 52, 7, {'g': "#e9f0ff", '-': "#2a2a5a"}))
    b.append(runs(["....r", "...rr", "..rrr", ".rrrr", "wwwww"], 774, 24, 7, {'r': "#3d6aff", 'w': "#fff"}))
    b.append(ptext("Z", 840, 50, 3, "#ffd23f") + ptext("Z", 866, 34, 4, "#ffd23f") + ptext("Z", 898, 14, 5, "#ffd23f"))
    return strip(n, ''.join(b), day=("#2a2a6a", "#4a4a9a"), night=("#04020f", "#120a30"), grid="#7a8aff")

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}
# The header's greetings in this world only (Frank, 2026-10-05: "world themed ones that appear only in those worlds"); {n} is the first name.
GREETINGS = ['Player one ready, {n}.', 'Insert coin, {n}.', 'Press start, {n}.', 'New high score incoming, {n}.', 'Level up, {n}.', 'Combo multiplier: bundles, {n}.', 'Extra life unlocked, {n}.', 'The boss level is a renewal, {n}.', 'Ready, player {n}?', 'Power-up: assume the sale, {n}.', 'Game on, {n}.', 'No continues needed today, {n}.', '1UP, {n}.', 'Speedrun the speed to dial, {n}.', 'Loading closes... {n}.']

"""The Phoenix world: the modern Valley -- the camel-shaped mountain, the tower ridge, downtown,
palm-lined boulevards and the light rail. Design and font only."""
import random

KEY = "phoenix"
NAME = "Phoenix"
FONTS = "family=Archivo:wght@500;700;800&family=Inter:wght@400;500;600;700"
DISPLAY = "'Archivo', system-ui, sans-serif"
DW = 800
BODY = "'Inter', system-ui, sans-serif"
SKY_BG = (("#8a3f7a", "#b9858a"), ("#0b0e26", "#141026"))

LOOKS = [
    ("valley", "Valley Sunset",
     "--surface: #f5ece4; --surface-raised: #fffaf5; --card2: #f8efe7; --chip: #efe0d4; --text-primary: #1f1726; --text-muted: #6b5c6e; --text-secondary: #554858; --grid: #eee0d5; --border: #e6d6ca; --border-strong: #cdb6a8; --accent: #c2410c; --accent-d: #9a330a; --side: #2e1d4a; --side2: #43285e; --sideInk: #eadff5; --brand: #f5ece4; --brand2: #ffa45c; --rad: 12px;",
     "--surface: #16111f; --surface-raised: #1f1829; --card2: #271f33; --chip: #30263f; --text-primary: #f3ece6; --text-muted: #b3a6bd; --text-secondary: #c9bdd0; --grid: #2d2439; --border: #33293f; --border-strong: #4a3c5c; --accent: #ff8a4c; --accent-d: #ffab7f; --side: #0e0918; --side2: #1d1330; --sideInk: #eadff5; --brand: #f3ece6; --brand2: #ffa45c;",
     ["#f5ece4", "#2e1d4a", "#c2410c"]),
    ("copper", "Copper",
     "--surface: #f1ece8; --surface-raised: #fbf8f6; --card2: #f4efeb; --chip: #e7ded7; --text-primary: #1d1a19; --text-muted: #675d57; --text-secondary: #514843; --grid: #e6ded8; --border: #ddd3cb; --border-strong: #c2b4a9; --accent: #a5501f; --accent-d: #7e3a14; --side: #232323; --side2: #333131; --sideInk: #e8e2dd; --brand: #f1ece8; --brand2: #e08a52; --rad: 10px;",
     "--surface: #121212; --surface-raised: #1b1a19; --card2: #23211f; --chip: #2c2926; --text-primary: #eee8e3; --text-muted: #a89e96; --text-secondary: #c2b8b0; --grid: #2a2725; --border: #302c29; --border-strong: #47413c; --accent: #e0884e; --accent-d: #f0a878; --side: #0b0b0b; --side2: #1a1918; --sideInk: #e8e2dd; --brand: #eee8e3; --brand2: #e08a52;",
     ["#f1ece8", "#232323", "#a5501f"]),
    ("monsoon", "Monsoon",
     "--surface: #e8edf2; --surface-raised: #f7f9fb; --card2: #edf1f5; --chip: #dde4eb; --text-primary: #131b24; --text-muted: #56657a; --text-secondary: #445367; --grid: #dde4eb; --border: #d3dbe4; --border-strong: #b4c0ce; --accent: #1f5fd6; --accent-d: #164aa8; --side: #2b3a4e; --side2: #3a4c63; --sideInk: #dce5f0; --brand: #e8edf2; --brand2: #6fb6ff; --rad: 14px;",
     "--surface: #0d1219; --surface-raised: #141b25; --card2: #1a2330; --chip: #222d3c; --text-primary: #e6edf5; --text-muted: #98a6b8; --text-secondary: #b1bdcc; --grid: #222d3c; --border: #263243; --border-strong: #35465c; --accent: #4ea8ff; --accent-d: #86c4ff; --side: #080c12; --side2: #152031; --sideInk: #dce5f0; --brand: #e6edf5; --brand2: #6fb6ff;",
     ["#e8edf2", "#2b3a4e", "#1f5fd6"]),
]

# ------------------------------------------------------------------ helpers
def wrap(h, body, aspect="xMidYMid slice", w=1600):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="{aspect}">{body}</svg>'

def smooth(pts, close=True):
    """Catmull-Rom through pts as cubic beziers (ints)."""
    p = pts; o = [f'M{p[0][0]:.0f} {p[0][1]:.0f}']
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[i]; p1 = p[i]; p2 = p[i + 1]; p3 = p[i + 2] if i + 2 < len(p) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        o.append(f'C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]:.0f} {p2[1]:.0f}')
    return ''.join(o) + ('Z' if close else '')

CAMEL = [(0, 1), (.07, .84), (.13, .5), (.18, .3), (.22, .25), (.26, .29), (.3, .42), (.35, .47), (.44, .24),
         (.52, .05), (.57, 0), (.62, .04), (.7, .27), (.8, .55), (.9, .82), (1, 1)]
def camel(x0, base, w, h, fill, extra=''):
    pts = [(x0 + u * w, base - (1 - v) * h) for u, v in CAMEL]
    pts = [(x0, base + 4)] + pts + [(x0 + w, base + 4)]
    return f'<path d="{smooth(pts)}" fill="{fill}"{extra}/>'

def stars(n, w, y0, y1, seed, ops=(.35, .55, .85)):
    r = random.Random(seed); o = []
    for _ in range(n):
        o.append(f'<circle cx="{r.randint(0, w)}" cy="{r.randint(y0, y1)}" r="{r.choice([.8, 1.1, 1.5, 2])}" fill="#fff" opacity="{r.choice(ops)}"/>')
    return ''.join(o)

def lingrad(id_, stops, x2=0, y2=1):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'

def radgrad(id_, col, op=.6):
    return f'<radialGradient id="{id_}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{col}" stop-opacity="{op}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>'

# a palm, base at 0,0, 100 tall; trunk takes `fill`, fronds take `color`
PALM_DEF = ('<g id="palm"><path d="M-3 0Q3 -50 -1 -98L2 -98Q7 -50 3 0Z"/>'
            '<g transform="translate(0 -99)" fill="currentColor">'
            + ''.join(f'<path d="M0 0Q14 -12 32 2Q15 -3 0 3Z" transform="rotate({a})"/>' for a in (-30, 0, 30, 70))
            + ''.join(f'<path d="M0 0Q14 -12 32 2Q15 -3 0 3Z" transform="scale(-1 1) rotate({a})"/>' for a in (-30, 0, 30, 70))
            + '<path d="M0 0Q-4 -14 2 -26Q4 -12 0 0Z"/><circle r="3"/></g></g>')
def palm(x, y, h, trunk, frond, lean=0):
    s = h / 100
    t = f'translate({x:.0f} {y:.0f}) scale({s:.2f})' + (f' skewX({lean})' if lean else '')
    return f'<use href="#palm" transform="{t}" fill="{trunk}" color="{frond}"/>'

def mast(x, base, top, col, lit=False, w=None):
    """A lattice radio mast with a red beacon."""
    w = w or max(8, (base - top) * .07)
    o = [f'<path d="M{x - w:.0f} {base}L{x:.1f} {top}L{x + w:.0f} {base}" fill="none" stroke="{col}" stroke-width="2.4"/>',
         f'<line x1="{x:.1f}" y1="{top - 14}" x2="{x:.1f}" y2="{base}" stroke="{col}" stroke-width="1.6"/>']
    n = int((base - top) / 22)
    for i in range(1, n):
        y = top + i * (base - top) / n; hw = w * (y - top) / (base - top)
        o.append(f'<line x1="{x - hw:.0f}" y1="{y:.0f}" x2="{x + hw:.0f}" y2="{y + 9:.0f}" stroke="{col}" stroke-width="1.2"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{top - 14}" r="3.4" fill="#ff3b3b"/>')
    if lit: o.append(f'<circle cx="{x:.1f}" cy="{top - 14}" r="11" fill="#ff3b3b" opacity=".35"/>')
    return ''.join(o)

def tower(x, top, w, base, col, win, night, crown=0, step=18):
    """An office tower; window bands as dashed lines (lit at night)."""
    o = [f'<rect x="{x}" y="{top}" width="{w}" height="{base - top}" fill="{col}"/>']
    if crown == 1: o.append(f'<path d="M{x} {top}L{x + w / 2:.0f} {top - w * .45:.0f}L{x + w} {top}Z" fill="{col}"/>')
    if crown == 2: o.append(f'<rect x="{x + w / 2 - 2:.0f}" y="{top - 30}" width="4" height="30" fill="{col}"/>')
    if crown == 3: o.append(f'<rect x="{x + 6}" y="{top - 12}" width="{w - 12}" height="12" fill="{col}"/>')
    da = "7 5" if night else "10 4"
    for y in range(top + 10, base - 4, step):
        o.append(f'<line x1="{x + 5}" y1="{y}" x2="{x + w - 4}" y2="{y}" stroke="{win}" stroke-width="{5 if night else 3}" stroke-dasharray="{da}" opacity="{.85 if night else .45}"/>')
    return ''.join(o)

def train(x, y, w, night, stripe="#e8662a", body=None, flip=False, h=44):
    """Light-rail car, side view, rails at y. Nose at the left unless flip."""
    body = body or ("#eef0f2" if not night else "#c9cdd6"); win = "#ffd98a" if night else "#2b3d55"
    o = [f'<g transform="translate({x} {y})' + (f' translate({w} 0) scale(-1 1)' if flip else '') + '">',
         f'<path d="M0 -8L0 -{h - 14}Q2 -{h} 18 -{h}L{w} -{h}L{w} -8Z" fill="{body}"/>',
         f'<rect x="4" y="-{h - 10}" width="{w - 8}" height="14" rx="3" fill="{win}"/>',
         f'<rect x="0" y="-16" width="{w}" height="7" fill="{stripe}"/>',
         f'<path d="M{w * .45:.0f} -{h}l12 -12l14 0l-8 12" fill="none" stroke="#555" stroke-width="2"/>']
    for k in range(1, int(w / 60)):
        o.append(f'<line x1="{k * 60}" y1="-{h - 10}" x2="{k * 60}" y2="-{h - 24}" stroke="{body}" stroke-width="3"/>')
    for k in range(int(w / 120) + 1):
        o.append(f'<rect x="{30 + k * 120}" y="-{h - 28}" width="16" height="22" rx="2" fill="{win}" opacity=".7"/>')
    o.append(f'<circle cx="5" cy="-20" r="3" fill="{"#fff6c8" if night else "#ffe08a"}"/>')
    o.append(f'<rect x="0" y="-8" width="{w}" height="6" fill="#3a3a44"/></g>')
    return ''.join(o)

def person(x, y, s, shirt, skin="#c68a5e", hair="#2a1a14", pants="#2f3b55", arm=0):
    o = f'<g transform="translate({x} {y}) scale({s})">'
    o += f'<rect x="-6" y="-22" width="5" height="22" fill="{pants}"/><rect x="1" y="-22" width="5" height="22" fill="{pants}"/>'
    o += f'<rect x="-8" y="-46" width="16" height="26" rx="5" fill="{shirt}"/>'
    o += f'<rect x="-11" y="-44" width="4" height="18" rx="2" fill="{shirt}" transform="rotate({arm} -9 -44)"/><rect x="7" y="-44" width="4" height="18" rx="2" fill="{shirt}"/>'
    o += f'<circle cx="0" cy="-54" r="7" fill="{skin}"/><path d="M-7 -55a7 7 0 0 1 14 0q-7 -4 -14 0z" fill="{hair}"/></g>'
    return o

def sitter(x, y, s, shirt, skin="#c68a5e", hair="#2a1a14", pants="#2f3b55", flip=False):
    o = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    o += f'<path d="M-6 -20h18v5h-4v15h-5v-15h-9z" fill="{pants}"/>'
    o += f'<rect x="-9" y="-44" width="15" height="26" rx="5" fill="{shirt}"/><rect x="2" y="-40" width="4" height="16" rx="2" fill="{shirt}" transform="rotate(-50 4 -40)"/>'
    o += f'<circle cx="-1" cy="-52" r="7" fill="{skin}"/><path d="M-8 -53a7 7 0 0 1 14 0q-7 -4 -14 0z" fill="{hair}"/></g>'
    return o

def birds(pts, col, s=1):
    return ''.join(f'<path d="M{x - 9 * s:.0f} {y - 4 * s:.0f}q{5 * s:.0f} -2 {9 * s:.0f} {4 * s:.0f}q{4 * s:.0f} -6 {9 * s:.0f} -4" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>' for x, y in pts)

def cloud(x, y, w, col, op):
    return (f'<g fill="{col}" opacity="{op}"><ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="{w / 10:.0f}"/>'
            f'<ellipse cx="{x - w * .12:.0f}" cy="{y - w * .07:.0f}" rx="{w * .22:.0f}" ry="{w * .1:.0f}"/>'
            f'<ellipse cx="{x + w * .14:.0f}" cy="{y - w * .05:.0f}" rx="{w * .18:.0f}" ry="{w * .08:.0f}"/></g>')

def burst(cx, cy, r, col, n=10):
    o = [f'<g stroke="{col}" stroke-width="3" stroke-linecap="round">']
    import math
    for k in range(n):
        a = 2 * math.pi * k / n; x1 = cx + r * .35 * math.cos(a); y1 = cy + r * .35 * math.sin(a)
        x2 = cx + r * math.cos(a); y2 = cy + r * math.sin(a)
        o.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>')
    o.append('</g>')
    for k in range(n):
        a = 2 * math.pi * (k + .5) / n
        o.append(f'<circle cx="{cx + r * 1.08 * math.cos(a):.0f}" cy="{cy + r * 1.08 * math.sin(a):.0f}" r="2.6" fill="{col}"/>')
    return ''.join(o)

# ------------------------------------------------------------------ the Digest picture
W, H, SPLIT = 1600, 1700, 377
def skyline(night):
    o = []; a = o.append
    r = random.Random(7)
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    if night:
        sky = [(0, "#070a1e"), (.45, "#121a3e"), (.8, "#2b2352"), (1, "#5a3462")]
        gnd = [(0, "#2a1d3e"), (.25, "#16112a"), (1, "#120e22")]
    else:
        sky = [(0, "#3b2a6b"), (.32, "#8a3f7a"), (.62, "#e46a5c"), (.84, "#f9a35a"), (1, "#ffd78e")]
        gnd = [(0, "#c98a86"), (.3, "#c79a86"), (1, "#c7a48a")]
    a('<defs>' + lingrad("sky", sky) + lingrad("gnd", gnd) + radgrad("sun", "#fff1b8" if not night else "#fff4d6", .8 if not night else .35)
      + radgrad("glow", "#ffcf7a", .7) + radgrad("hz", "#ff9a4a", .55) + PALM_DEF + '</defs>')
    a(f'<rect width="{W}" height="{SPLIT + 4}" fill="url(#sky)"/>')
    # sun / moon and the sky band
    if night:
        a(stars(46, W, 0, 230, 3))
        for pts in [[(1000, 40), (1040, 62), (1086, 54), (1120, 82)], [(170, 120), (210, 100), (250, 118)]]:
            a('<polyline points="' + ' '.join(f'{x},{y}' for x, y in pts) + '" fill="none" stroke="#fff" stroke-opacity=".22"/>')
            a(''.join(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff"/>' for x, y in pts))
        a('<circle cx="400" cy="78" r="140" fill="url(#sun)"/><circle cx="400" cy="78" r="50" fill="#f6efd8"/>'
          '<circle cx="384" cy="66" r="9" fill="#e4dbc0"/><circle cx="414" cy="94" r="12" fill="#e4dbc0"/><circle cx="420" cy="62" r="5" fill="#e4dbc0"/>')
        a(f'<ellipse cx="800" cy="{SPLIT}" rx="900" ry="120" fill="url(#hz)"/>')
    else:
        a('<circle cx="790" cy="150" r="190" fill="url(#sun)"/><circle cx="790" cy="150" r="56" fill="#ffe7a0"/><circle cx="790" cy="150" r="46" fill="#fff3c4"/>')
        a(cloud(260, 120, 300, "#ffd0a8", .45) + cloud(1120, 70, 360, "#ffc29a", .4) + cloud(560, 40, 220, "#f7b2a6", .35))
        a(birds([(660, 92), (690, 110), (716, 86), (980, 64), (1004, 80)], "#3a2440", 1.2))
    # the camel-shaped mountain (behind) and the tower ridge
    a(camel(40, SPLIT, 920, 372, "#1b1531" if night else "#7b4a7c"))
    a(f'<path d="{smooth([(1100, SPLIT + 4), (1140, 300), (1220, 238), (1320, 226), (1420, 246), (1520, 232), (1600, 250), (1600, SPLIT + 4)])}" fill="{"#171128" if night else "#6c3f6e"}"/>')
    mc = "#3a2c55" if night else "#4a2c50"
    for x, top in [(1236, 70), (1300, 46), (1372, 84), (1452, 58), (1540, 96)]:
        base = 240 if x < 1500 else 236
        a(mast(x, base, top, mc, night))
    # downtown towers
    tc = "#1d1834" if night else "#53315f"; tc2 = "#251e40" if night else "#613a6c"; win = "#ffd27a" if night else "#ffc98a"
    for x, top, w, cr, c in [(930, 128, 46, 0, tc2), (968, 84, 58, 2, tc), (1022, 150, 40, 3, tc2), (1058, 104, 52, 1, tc), (1106, 160, 44, 0, tc2), (1146, 136, 38, 3, tc)]:
        a(tower(x, top, w, SPLIT + 4, c, win, night))
    # tall palms rising into the sky band
    pt = "#120c1e" if night else "#3a2142"
    for x, h, ln in [(56, 240, 0), (112, 205, -3), (872, 300, 2), (1196, 280, -2), (1590, 270, 3)]:
        a(palm(x, SPLIT + 6, h, pt, pt, ln))
    # ---- the ground: the city grid running out to the plaza
    a(f'<rect x="0" y="{SPLIT}" width="{W}" height="{H - SPLIT}" fill="url(#gnd)"/>')
    # near-horizon city blocks
    bc = "#2a2042" if night else "#9a6a84"
    for _ in range(40):
        x = r.randint(-20, 1600); w = r.randint(20, 60); hh = r.randint(5, 18)
        if 760 < x < 840: continue
        a(f'<rect x="{x}" y="{SPLIT - hh + 6}" width="{w}" height="{hh}" fill="{bc}"/>')
    # grid: rows and converging streets
    sc = "#3b2c48" if night else "#a77c86"
    rows = [SPLIT + 10 + int(6 * k ** 1.75) for k in range(1, 15)]
    rows = [y for y in rows if y < 860]
    for y in rows:
        a(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{sc}" stroke-width="{1 + (y - SPLIT) / 140:.1f}"/>')
    vx, vy = 800, SPLIT - 30
    xs = list(range(-1400, 3001, 220))
    for xb in xs:
        a(f'<line x1="{vx + (xb - vx) * 0.064:.0f}" y1="{SPLIT + 2}" x2="{xb}" y2="{vy + 500}" stroke="{sc}" stroke-width="2"/>')
    # rooftops in the blocks (day) / the glittering grid (night)
    if not night:
        for _ in range(70):
            y = r.randint(SPLIT + 14, 840); d = (y - SPLIT) / 470
            x = r.randint(0, W)
            if 520 < x < 1080 and y > 560: continue
            if 700 < x < 900: continue
            if x < 360 and y < 440: continue
            w = 10 + 40 * d; hh = 5 + 16 * d
            a(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{hh:.0f}" fill="{r.choice(["#e9b48c", "#dda080", "#f0c8a0", "#b98ea0"])}"/>')
            if r.random() < .25:
                a(f'<rect x="{x + w + 4:.0f}" y="{y + 2:.0f}" width="{w * .5:.0f}" height="{hh * .6:.0f}" rx="2" fill="#5fb3d6"/>')
    else:
        lights = ["#ffb347", "#fff2c0", "#ff8a3d", "#ffd27a"]
        for y in rows:
            for xb in xs:
                t = (y - (SPLIT + 2)) / (vy + 500 - SPLIT - 2)
                x = vx + (xb - vx) * (0.064 + t * (1 - 0.064))
                if not (0 <= x <= W) or r.random() < .2: continue
                if 520 < x < 1080 and y > 560: continue
                d = (y - SPLIT) / 470
                a(f'<circle cx="{x:.0f}" cy="{y}" r="{1.4 + 2.4 * d:.1f}" fill="{r.choice(lights)}"/>')
        for _ in range(70):
            y = r.randint(SPLIT + 4, 600); x = r.randint(0, W)
            if 740 < x < 860: continue
            a(f'<rect x="{x}" y="{y}" width="{2 + (y - SPLIT) // 50}" height="2" fill="{r.choice(lights)}" opacity=".8"/>')
    # the boulevard
    rd = "#1d1828" if night else "#6e5868"; edge = "#2f2738" if night else "#d9b8a4"
    a(f'<path d="M788 {SPLIT}L812 {SPLIT}L1060 660L540 660Z" fill="{rd}"/>')
    a(f'<path d="M788 {SPLIT}L540 660L560 660L792 {SPLIT}ZM812 {SPLIT}L1060 660L1040 660L808 {SPLIT}Z" fill="{edge}"/>')
    lane = "#ffd27a" if night else "#f4e2c8"
    a(f'<path d="M796 {SPLIT + 6}L720 660M804 {SPLIT + 6}L880 660" stroke="{lane}" stroke-width="2.4" stroke-dasharray="14 16" opacity=".7"/>')
    if night:  # headlights and taillights streaking down the boulevard
        a(f'<path d="M793 {SPLIT + 8}L640 660" stroke="#fff4d0" stroke-width="5" stroke-dasharray="6 26" opacity=".85"/>'
          f'<path d="M807 {SPLIT + 8}L960 660" stroke="#ff4a3a" stroke-width="5" stroke-dasharray="6 30" opacity=".85"/>')
    else:
        for t, side, col in [(.25, -1, "#e8662a"), (.55, 1, "#2f6fb8"), (.72, -1, "#f2f2f2"), (.4, 1, "#d6b13a")]:
            y = SPLIT + t * 283; x = 800 + side * (12 + 120 * t); s = .4 + t
            a(f'<rect x="{x - 9 * s:.0f}" y="{y - 6 * s:.0f}" width="{18 * s:.0f}" height="{11 * s:.0f}" rx="{3 * s:.0f}" fill="{col}"/>')
    # light rail: down the median, then off to the platform on the right
    rail = "#9a8fa8" if night else "#4a3a4a"
    for dx in (-4, 4):
        a(f'<path d="M{800 + dx // 2} {SPLIT + 4}L{800 + dx} 430Q{800 + dx} {520 + dx} {900 + dx} {520 + dx}L1600 {520 + dx}" fill="none" stroke="{rail}" stroke-width="2.4"/>')
    a(f'<line x1="802" y1="440" x2="1600" y2="440" stroke="{rail}" stroke-width="0"/>')
    # overhead wire poles along the line
    for x in range(960, 1600, 130):
        a(f'<rect x="{x}" y="470" width="4" height="54" fill="{rail}"/>')
    a(f'<path d="M900 476L1600 476" stroke="{rail}" stroke-width="1.4"/>')
    # platform beside the plaza: deck, canopy, the train in
    deck = "#3a3048" if night else "#d8c4b4"; deck2 = "#2a2236" if night else "#a88a7e"
    a(f'<rect x="1150" y="528" width="450" height="12" fill="{deck}"/><rect x="1150" y="540" width="450" height="8" fill="{deck2}"/>')
    a(train(1190, 520, 330, night))
    can = "#e8662a" if not night else "#c4511e"
    a(f'<rect x="1170" y="452" width="4" height="76" fill="{deck2}"/><rect x="1536" y="452" width="4" height="76" fill="{deck2}"/>'
      f'<path d="M1150 456L1560 456L1570 446L1160 446Z" fill="{can}"/>')
    a(f'<rect x="1526" y="470" width="44" height="22" rx="3" fill="#1d2a3a"/><text x="1548" y="486" text-anchor="middle" font-family="monospace" font-size="11" fill="#7dff9a">2 MIN</text>')
    if night: a('<ellipse cx="1360" cy="530" rx="260" ry="40" fill="url(#glow)" opacity=".5"/>')
    # boulevard palms
    for t in (.1, .2, .32, .46, .56):
        y = SPLIT + 283 * t; hw = 12 + 248 * t + 14 * t; h = 26 + 250 * t
        for side in (-1, 1):
            a(palm(800 + side * hw, y, h, "#120c1e" if night else "#7a5040", "#0f1a14" if night else "#3f6a3a", side * 2))
    # the plaza and the stage
    pv = "#2a2238" if night else "#e7cdb4"; pv2 = "#211a2e" if night else "#d6b79c"
    a(f'<path d="M440 650L1160 650L1320 860L280 860Z" fill="{pv}"/>')
    for k in range(1, 6):
        y = 650 + k * 38
        a(f'<line x1="{440 - 30 * k}" y1="{y}" x2="{1160 + 30 * k}" y2="{y}" stroke="{pv2}" stroke-width="2"/>')
    if night: a('<ellipse cx="800" cy="740" rx="380" ry="110" fill="url(#glow)" opacity=".7"/>')
    st = "#4a2c5a" if night else "#8a4a5a"; st2 = "#331d40" if night else "#6a3446"; top = "#5a3a6a" if night else "#b5707a"
    a(f'<path d="M590 690L1010 690L1040 806L560 806Z" fill="{top}"/><rect x="560" y="806" width="480" height="26" fill="{st2}"/>'
      f'<path d="M560 806L1040 806" stroke="{st}" stroke-width="3"/>')
    # string lights over the plaza
    pole = "#2a2236" if night else "#4a3440"
    for x in (452, 1158):
        a(f'<rect x="{x - 3}" y="496" width="6" height="200" fill="{pole}"/>')
    bulb = "#ffd27a"
    for (x1, x2, sag) in [(452, 1158, 34), (452, 330, 22)]:
        a(f'<path d="M{x1} 500Q{(x1 + x2) / 2:.0f} {500 + 2 * sag} {x2} 500" fill="none" stroke="{pole}" stroke-width="1.6"/>')
        n = max(4, abs(x2 - x1) // 34)
        for k in range(1, n):
            t = k / n; x = x1 + (x2 - x1) * t; y = 496 + 2 * sag * 2 * t * (1 - t)
            if night: a(f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="9" fill="{bulb}" opacity=".3"/>')
            a(f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="3.6" fill="{bulb if night else "#fff1c0"}"/>')
    a('</svg>')
    return ''.join(o)

# ------------------------------------------------------------------ vistas (1600 x 240)
V = 240
def vsky(night, day, nt, extra=''):
    c = nt if night else day
    stops = [(0, c[0]), (.6, c[1]), (1, c[2])]
    return ('<defs>' + lingrad("g", stops) + radgrad("gl", "#ffd27a", .6) + radgrad("sn", "#fff1b8", .8) + PALM_DEF + extra + '</defs>'
            f'<rect width="1600" height="{V}" fill="url(#g)"/>')
DUSK = ("#4a2c6e", "#e46a5c", "#ffc480"); NITE = ("#070a1e", "#161c42", "#3a2a58")
def shade(h=240):  # darken the two text corners a touch
    return (f'<defs><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient></defs>'
            f'<rect width="1600" height="{h}" fill="url(#sh)"/>')

def v_sales(n):  # the freeway at rush hour, traffic flowing like premium
    o = [vsky(n, DUSK, NITE)]
    o.append(stars(40, 1600, 0, 90, 1) if n else '<circle cx="1180" cy="120" r="110" fill="url(#sn)"/><circle cx="1180" cy="120" r="34" fill="#fff3c4"/>')
    o.append(camel(200, 150, 640, 110, "#1b1531" if n else "#7b4a7c"))
    o.append(f'<path d="M900 152Q1100 110 1300 120T1600 130L1600 152Z" fill="{"#171128" if n else "#6c3f6e"}"/>')
    for x, t in [(1180, 78), (1260, 92), (1420, 70)]: o.append(mast(x, 124, t, "#3a2c55" if n else "#4a2c50", n))
    # the deck of the freeway
    deck = "#2a2236" if n else "#b98a8a"; road = "#17121f" if n else "#5a4656"
    o.append(f'<rect x="0" y="150" width="1600" height="90" fill="{"#120e1c" if n else "#8a5a6a"}"/>')
    # flyover ramp sweeping over
    o.append(f'<path d="M-20 200Q400 60 800 86T1620 150L1620 166Q1200 104 800 104T-20 216Z" fill="{deck}"/>')
    o.append(f'<path d="M-20 196Q400 56 800 82T1620 146" fill="none" stroke="{"#4a3c5c" if n else "#e9cfc4"}" stroke-width="4"/>')
    for x in (300, 700, 1100, 1450):
        y = 140 if x < 500 else 104 if x < 1000 else 128
        o.append(f'<rect x="{x - 9}" y="{y}" width="18" height="{200 - y}" fill="{deck}"/>')
    o.append(f'<rect x="0" y="176" width="1600" height="40" fill="{road}"/><rect x="0" y="174" width="1600" height="4" fill="{"#4a3c5c" if n else "#e9cfc4"}"/>')
    o.append('<line x1="0" y1="196" x2="1600" y2="196" stroke="#f4e2c8" stroke-width="2" stroke-dasharray="20 18" opacity=".5"/>')
    r = random.Random(4)
    if n:  # light trails: white one way, red the other, gold on the ramp like premium
        for y, col in [(186, "#fff4d0"), (190, "#fff4d0"), (202, "#ff4a3a"), (207, "#ff4a3a")]:
            o.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="{col}" stroke-width="3" stroke-dasharray="{r.randint(40, 120)} {r.randint(20, 60)}" opacity=".85"/>')
        o.append('<path d="M-20 192Q400 52 800 78T1620 142" fill="none" stroke="#ffd27a" stroke-width="3" stroke-dasharray="60 30" opacity=".9"/>')
    else:
        cols = ["#e8662a", "#2f6fb8", "#f2f2f2", "#d6b13a", "#3a8a5a", "#c43a4a"]
        for lane_y in (180, 198):
            x = r.randint(0, 60)
            while x < 1600:
                c = r.choice(cols)
                o.append(f'<rect x="{x}" y="{lane_y}" width="34" height="14" rx="4" fill="{c}"/><rect x="{x + 7}" y="{lane_y + 2}" width="16" height="5" rx="2" fill="#2b3d55" opacity=".7"/>')
                x += r.randint(48, 90)
        for x in range(120, 1500, 160):
            t = (x + 20) / 1640
            o.append(f'<rect x="{x}" y="{94 + 60 * (1 - t) ** 2 - 40 * t * (1 - t):.0f}" width="28" height="11" rx="3" fill="{r.choice(cols)}"/>')
    # the overhead sign
    o.append(f'<rect x="596" y="20" width="6" height="66" fill="{deck}"/><rect x="1000" y="20" width="6" height="66" fill="{deck}"/><rect x="590" y="16" width="420" height="6" fill="{deck}"/>')
    o.append('<rect x="640" y="24" width="320" height="54" rx="6" fill="#1f6b3e" stroke="#fff" stroke-width="2"/>'
             '<text x="800" y="48" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#fff">PREMIUM  NEXT EXIT</text>'
             '<text x="800" y="70" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#fff">FLORES BLVD  1/2 MILE</text>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_messages(n):  # the cell towers on the ridge, signal arcs
    o = [vsky(n, ("#3a4a8a", "#e88a6a", "#ffd0a0"), NITE)]
    o.append(stars(50, 1600, 0, 120, 2) if n else cloud(300, 60, 300, "#fff", .3) + cloud(1300, 50, 260, "#fff", .25))
    o.append(f'<path d="{smooth([(0, 244), (0, 190), (220, 170), (420, 150), (640, 160), (820, 140), (1040, 150), (1240, 168), (1440, 160), (1600, 176), (1600, 244)])}" fill="{"#171128" if n else "#6c3f6e"}"/>')
    mc = "#3a2c55" if n else "#3a2242"
    for x, base, top in [(300, 166, 40), (560, 152, 26), (1040, 150, 34), (1290, 166, 52)]:
        o.append(mast(x, base, top, mc, n))
        for k in range(1, 4):
            rr = 18 * k
            op = .8 - .2 * k
            o.append(f'<path d="M{x - rr * .9:.0f} {top - 14 - rr * .45:.0f}A{rr} {rr} 0 0 1 {x + rr * .9:.0f} {top - 14 - rr * .45:.0f}" fill="none" stroke="{"#7dd3ff" if n else "#fff"}" stroke-width="3" opacity="{op:.1f}" stroke-linecap="round"/>')
    # the "palm" that is really a cell tower
    pt = "#120c1e" if n else "#3a2242"
    o.append(palm(800, 148, 130, pt, pt))
    o.append(f'<rect x="784" y="40" width="5" height="12" fill="{mc}"/><rect x="811" y="40" width="5" height="12" fill="{mc}"/><rect x="797" y="34" width="5" height="12" fill="{mc}"/>')
    # message bubbles riding the signal
    for x, y, t in [(420, 60, "quote?"), (930, 52, "yes!"), (1160, 84, "call me")]:
        w = 12 * len(t) + 24
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="12" fill="{"#2f6fe0" if n else "#fff"}" opacity=".95"/><path d="M{x + 14} {y + 26}l-6 10l14 -10z" fill="{"#2f6fe0" if n else "#fff"}"/>'
                 f'<text x="{x + w / 2:.0f}" y="{y + 19}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="15" fill="{"#fff" if n else "#3a2242"}">{t}</text>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_coaching(n):  # a rooftop at night overlooking the lit grid
    o = [vsky(n, ("#2a2058", "#a0507a", "#f2906a"), NITE)]
    o.append(stars(30, 1600, 0, 90, 3) if not n else stars(50, 1600, 0, 100, 3))
    r = random.Random(5)
    # the grid falling away below
    g = "#120e22" if n else "#5a3a5a"
    o.append(f'<rect x="0" y="110" width="1600" height="130" fill="{g}"/>')
    o.append(camel(80, 112, 520, 70, "#1b1531" if n else "#6a3e6c"))
    vx = 800
    for k in range(1, 7):
        y = 110 + int(4 * k ** 1.9)
        o.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="#ffb347" stroke-width="1.4" opacity="{.35 if n else .25}"/>')
    for xb in range(-1600, 3201, 260):
        o.append(f'<line x1="{vx + (xb - vx) * .06:.0f}" y1="110" x2="{xb}" y2="240" stroke="#ffb347" stroke-width="1.4" opacity="{.35 if n else .25}"/>')
    for _ in range(34):
        y = r.randint(112, 200); x = r.randint(0, 1600)
        o.append(f'<circle cx="{x}" cy="{y}" r="{1 + (y - 110) / 40:.1f}" fill="{r.choice(["#ffd27a", "#fff2c0", "#ff8a3d"])}" opacity="{.9 if n else .6}"/>')
    # towers either side
    tc = "#1d1834" if n else "#43284e"
    for x, top, w in [(60, 30, 70), (140, 70, 50), (1380, 40, 64), (1450, 10, 70), (1530, 60, 60)]:
        o.append(tower(x, top, w, 240, tc, "#ffd27a", True))
    # the rooftop deck, railing, two chairs, a table with a phone playing the call back
    deck = "#2a2236" if n else "#3a2a40"
    o.append(f'<rect x="420" y="170" width="760" height="70" fill="{deck}"/>')
    o.append(f'<path d="M420 170L1180 170" stroke="#8a7a9a" stroke-width="3"/>')
    for x in range(430, 1180, 30): o.append(f'<line x1="{x}" y1="140" x2="{x}" y2="170" stroke="#8a7a9a" stroke-width="2"/>')
    o.append('<line x1="420" y1="140" x2="1180" y2="140" stroke="#8a7a9a" stroke-width="3"/>')
    o.append('<path d="M420 96Q800 140 1180 96" fill="none" stroke="#3a2c40" stroke-width="1.5"/>')
    for k in range(1, 16):
        t = k / 16; x = 420 + 760 * t; y = 96 + 44 * 2 * t * (1 - t) * 1.0
        o.append((f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="8" fill="#ffd27a" opacity=".3"/>' if n else '') + f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="3.4" fill="#ffe8a8"/>')
    o.append(sitter(720, 200, 1.4, "#e8662a", flip=False) + sitter(880, 200, 1.4, "#2f8a8a", skin="#8a5a3a", flip=True))
    o.append('<rect x="776" y="170" width="48" height="6" fill="#c9b6a8"/><rect x="796" y="176" width="8" height="24" fill="#c9b6a8"/>'
             '<rect x="788" y="160" width="24" height="12" rx="2" fill="#111"/><path d="M794 163l0 6l6 -3z" fill="#7dff9a"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_roleplay(n):  # a spring-training ballpark
    o = [vsky(n, ("#3f86d6", "#8cc4ec", "#f6e2b8"), NITE)]
    if n: o.append(stars(40, 1600, 0, 60, 4))
    else: o.append(cloud(360, 50, 260, "#fff", .7) + cloud(1200, 40, 300, "#fff", .6))
    o.append(camel(900, 120, 560, 80, "#1b1531" if n else "#a07a9a"))
    pt = "#120c1e" if n else "#6a4a3a"; pf = "#0f1a14" if n else "#3f7a3a"
    for x, h in [(120, 90), (190, 110), (260, 84), (1340, 100), (1420, 120), (1500, 92)]:
        o.append(palm(x, 122, h, pt, pf))
    # berm and outfield wall
    o.append(f'<path d="M0 122L1600 122L1600 140L0 140Z" fill="{"#1c3a24" if n else "#5a9a4a"}"/>')
    o.append(f'<rect x="0" y="118" width="1600" height="10" fill="{"#173a5a" if n else "#1f5a8a"}"/>')
    r = random.Random(6)
    for _ in range(60):
        x = r.randint(0, 1600); y = r.randint(126, 138)
        o.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{r.choice(["#e8662a", "#fff", "#2f6fb8", "#d6b13a", "#c43a4a"])}"/>')
    # the field
    o.append(f'<rect x="0" y="140" width="1600" height="100" fill="{"#1f4a2a" if n else "#4f9a3e"}"/>')
    for k in range(0, 1600, 120): o.append(f'<rect x="{k}" y="140" width="60" height="100" fill="#fff" opacity=".05"/>')
    o.append(f'<path d="M800 250L560 190L800 150L1040 190Z" fill="{"#5a3a2a" if n else "#c98a5a"}"/><path d="M800 238L620 190L800 162L980 190Z" fill="{"#1f4a2a" if n else "#4f9a3e"}"/>')
    o.append('<circle cx="800" cy="194" r="12" fill="#c98a5a"/>')
    for x, y in [(800, 160), (622, 190), (978, 190)]: o.append(f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="#fff" transform="rotate(45 {x} {y})"/>')
    o.append(person(800, 196, 1.1, "#fff", pants="#ddd") + person(700, 186, .9, "#fff", pants="#ddd", skin="#8a5a3a") + person(905, 182, .9, "#fff", pants="#ddd", arm=40))
    # scoreboard and lights
    o.append('<rect x="680" y="34" width="240" height="70" rx="4" fill="#1d2a3a"/><rect x="796" y="104" width="8" height="16" fill="#1d2a3a"/>'
             '<text x="800" y="58" text-anchor="middle" font-family="monospace" font-size="15" fill="#ffd27a">SPRING TRAINING</text>'
             '<text x="800" y="90" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="22" fill="#7dff9a">FLORES 3 · AWAY 2</text>')
    for x in (440, 1160):
        o.append(f'<rect x="{x - 3}" y="40" width="6" height="80" fill="#5a6070"/><rect x="{x - 28}" y="26" width="56" height="18" rx="2" fill="#dfe4ea"/>')
        if n: o.append(f'<path d="M{x - 28} 44L{x - 160} 240L{x + 160} 240L{x + 28} 44Z" fill="#fff6d6" opacity=".14"/><circle cx="{x}" cy="34" r="50" fill="url(#gl)"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_rphistory(n):  # an old neon motel sign, flickering
    o = [vsky(n, ("#3a2a6b", "#c4507a", "#f6a46a"), ("#07071a", "#14123a", "#2a1a4a"),
              '<filter id="nf" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')]
    if n: o.append(stars(60, 1600, 0, 140, 5))
    o.append(camel(980, 170, 520, 80, "#1b1531" if n else "#7b4a7c"))
    # the motel: a long low row of doors
    mb = "#2a2240" if n else "#e8c8a8"; mr = "#1c1630" if n else "#3a7a8a"
    o.append(f'<rect x="760" y="150" width="760" height="70" fill="{mb}"/><rect x="740" y="140" width="800" height="12" fill="{mr}"/>')
    for k in range(10):
        x = 790 + k * 72
        o.append(f'<rect x="{x}" y="170" width="26" height="50" fill="{["#e8662a", "#2f8a8a", "#d6b13a"][k % 3]}"/><rect x="{x + 34}" y="170" width="24" height="20" fill="{"#ffd27a" if (n and k % 3 != 1) else "#5a7a9a"}"/>')
    o.append(f'<rect x="0" y="220" width="1600" height="20" fill="{"#100c1a" if n else "#5a4656"}"/>')
    o.append(palm(1560, 222, 150, "#120c1e" if n else "#6a4a3a", "#0f1a14" if n else "#3f7a3a"))
    # the sign: a pole, a starburst, the REPLAY board and an arrow
    pole = "#3a3048" if n else "#c94a3a"
    o.append(f'<rect x="496" y="40" width="14" height="190" fill="{pole}"/>')
    pink = "#ff4fa8"; teal = "#3ff0e0"; yel = "#ffd23f"
    on = .95 if n else .9
    board = "#14122a" if n else "#21607a"
    o.append(f'<path d="M330 50L660 34L680 120L340 132Z" fill="{board}" stroke="{yel}" stroke-width="4"/>')
    if n: o.append(f'<text x="505" y="108" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="bold" font-size="60" fill="{pink}" filter="url(#nf)" opacity=".9">REPLAY</text>')
    o.append(f'<text x="505" y="108" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="bold" font-size="60" fill="{pink if n else "#ffd6e8"}" stroke="{pink}" stroke-width="{0 if n else 1}" opacity="{on}">REP<tspan opacity="{.35 if n else 1}">L</tspan>AY</text>')
    o.append(f'<rect x="420" y="146" width="170" height="34" rx="4" fill="{board}" stroke="{teal}" stroke-width="3"/>')
    if n: o.append(f'<text x="505" y="171" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="22" fill="{teal}" filter="url(#nf)">VACANCY</text>')
    o.append(f'<text x="505" y="171" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="22" fill="{teal if n else "#d8fffb"}">VACANCY</text>')
    o.append(f'<text x="398" y="171" text-anchor="end" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="#7a5a6a" opacity=".7">NO</text>')
    # the starburst on top
    o.append(f'<g transform="translate(503 30)">' + ''.join(f'<path d="M0 -26L5 -4L0 0L-5 -4Z" fill="{yel}" transform="rotate({k * 45})"/>' for k in range(8)) + '</g>')
    if n: o.append('<circle cx="503" cy="30" r="40" fill="url(#gl)"/>')
    # the arrow pointing at the rooms, a chase of bulbs
    o.append(f'<path d="M640 140L700 140L700 126L740 150L700 174L700 160L640 160Z" fill="{board}" stroke="{pink}" stroke-width="3"/>')
    for k in range(3): o.append(f'<circle cx="{654 + k * 20}" cy="150" r="3.5" fill="{yel}" opacity="{1 if k % 2 == 0 else .35}"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_training(n):  # a hiker on the switchbacks up the camel mountain
    o = [vsky(n, ("#f08a5a", "#ffc48a", "#ffe8c4"), NITE)]
    o.append(stars(50, 1600, 0, 120, 6) if n else '<circle cx="1260" cy="70" r="90" fill="url(#sn)"/><circle cx="1260" cy="70" r="30" fill="#fff3c4"/>')
    if n: o.append('<circle cx="1260" cy="60" r="24" fill="#f6efd8"/>')
    o.append(camel(240, 250, 1100, 240, "#2a2040" if n else "#b5707a"))
    o.append(camel(240, 250, 1100, 240, "#000", ' opacity=".08" transform="translate(30 0)"'))
    # the switchback trail up to the hump
    trail = [(330, 236), (560, 214), (440, 192), (640, 168), (560, 140), (760, 112), (690, 80), (850, 56), (868, 22)]
    o.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in trail)}" fill="none" stroke="{"#c9a8b8" if n else "#ffe2c4"}" stroke-width="5" stroke-linejoin="round" stroke-dasharray="14 8"/>')
    # boulders and creosote along it
    r = random.Random(8)
    for _ in range(26):
        x = r.randint(300, 1250); y = r.randint(60, 236)
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(6, 14)}" ry="{r.randint(3, 7)}" fill="{"#1a1430" if n else "#7a4a5a"}" opacity=".7"/>')
    # a trail sign at the bottom and the hiker mid-way
    hx, hy = 604, 165
    o.append(f'<rect x="{hx - 12}" y="{hy - 46}" width="10" height="20" rx="3" fill="#e8662a"/>')
    o.append(person(hx, hy, .95, "#2f8a8a", pants="#5a4a3a"))
    o.append(f'<line x1="{hx + 12}" y1="{hy - 30}" x2="{hx + 20}" y2="{hy + 2}" stroke="#555" stroke-width="2"/><path d="M{hx - 8} {hy - 60}h16l-2 -5h-12z" fill="#d6b13a"/>')
    o.append('<rect x="858" y="12" width="3" height="20" fill="#eee"/>' if False else '')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_map(n, athena=False):  # a Valley street-grid map with a light-rail route
    paper = "#f4ece0" if not n else "#141226"; ink = "#3a2a3a" if not n else "#d8cfe8"
    route = "#2f9e63" if athena else "#e2552b"; route2 = "#1f7a4a" if athena else "#c0391b"
    o = [f'<rect width="1600" height="{V}" fill="{paper}"/>']
    # parks and a canal
    for x, y, w, h in [(120, 40, 160, 70), (1040, 150, 140, 60), (1380, 30, 120, 80), (520, 150, 110, 50)]:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{"#cfe3b8" if not n else "#1c3a2a"}"/>')
    o.append(f'<path d="M0 110Q300 60 700 120T1600 70" fill="none" stroke="{"#7fc4e8" if not n else "#2a5a8a"}" stroke-width="10" opacity=".8"/>')
    for x in range(0, 1600, 40): o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{V}" stroke="{ink}" stroke-opacity="{.22 if x % 160 == 0 else .07}" stroke-width="{3 if x % 160 == 0 else 1}"/>')
    for y in range(0, V, 40): o.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="{ink}" stroke-opacity="{.22 if y % 160 == 0 else .07}" stroke-width="{3 if y % 160 == 0 else 1}"/>')
    # the camel mountain marked on the map
    o.append(f'<path d="M1240 220l20 -26l12 8l18 -30l24 48z" fill="{ink}" opacity=".25"/><text x="1280" y="236" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="{ink}" opacity=".6">CAMEL MTN</text>')
    # the line: on the grid, so right angles with rounded corners
    path = "M200 200L200 160Q200 140 220 140L540 140Q560 140 560 120L560 80Q560 60 580 60L940 60Q960 60 960 80L960 120Q960 140 980 140L1180 140Q1200 140 1200 120L1200 60Q1200 40 1220 40L1600 40"
    o.append(f'<path d="{path}" fill="none" stroke="{paper}" stroke-width="16"/><path d="{path}" fill="none" stroke="{route}" stroke-width="9" stroke-linejoin="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for (x, y, dy), t in zip([(380, 140, -22), (760, 60, 36), (960, 116, 0), (1200, 92, 0)], steps):
        o.append(f'<circle cx="{x}" cy="{y}" r="12" fill="#fff" stroke="{route2}" stroke-width="5"/>')
        if dy:
            o.append(f'<text x="{x}" y="{y + dy}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="19" fill="{ink}">{t}</text>')
        else:
            o.append(f'<text x="{x + 22}" y="{y + 7}" font-family="Arial, sans-serif" font-weight="bold" font-size="19" fill="{ink}">{t}</text>')
    o.append(f'<rect x="1340" y="96" width="210" height="38" rx="19" fill="{route}"/><text x="1445" y="121" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#fff">{"ATHENA LINE" if athena else "APOLLO LINE"}</text>')
    o.append(f'<g transform="translate(80 70)"><circle r="26" fill="none" stroke="{ink}" stroke-width="2" opacity=".6"/><path d="M0 -24L6 0L0 24L-6 0Z" fill="{route}"/><text y="-30" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="{ink}">N</text></g>')
    o.append(shade())
    return wrap(V, ''.join(o))

def ranch(x, y, w, wall, roof, night, door="#2f8a8a"):
    o = [f'<path d="M{x - 10} {y - 40}L{x + 30} {y - 62}L{x + w - 30} {y - 62}L{x + w + 10} {y - 40}Z" fill="{roof}"/>',
         f'<rect x="{x}" y="{y - 40}" width="{w}" height="40" fill="{wall}"/>',
         f'<rect x="{x + w - 70}" y="{y - 32}" width="58" height="32" fill="{"#3a3048" if night else "#e9e2da"}"/>']
    for k in range(4): o.append(f'<line x1="{x + w - 70}" y1="{y - 24 + k * 8}" x2="{x + w - 12}" y2="{y - 24 + k * 8}" stroke="#000" stroke-opacity=".12"/>')
    o.append(f'<rect x="{x + 20}" y="{y - 30}" width="34" height="18" fill="{"#ffd27a" if night else "#5a7a9a"}"/><rect x="{x + 66}" y="{y - 32}" width="16" height="32" fill="{door}"/>')
    return ''.join(o)

def v_service(n):  # a neighbourhood street: ranch houses, palms, a pool
    o = [vsky(n, ("#3f86d6", "#8cc4ec", "#f6e2b8"), NITE)]
    o.append(stars(40, 1600, 0, 90, 7) if n else cloud(500, 40, 260, "#fff", .7) + cloud(1300, 54, 220, "#fff", .6))
    if n: o.append('<circle cx="1260" cy="50" r="22" fill="#f6efd8"/>')
    o.append(camel(820, 140, 640, 90, "#1b1531" if n else "#a888a8"))
    o.append(f'<rect x="0" y="140" width="1600" height="100" fill="{"#1a2a1e" if n else "#9cc47a"}"/>')
    pt = "#120c1e" if n else "#7a5040"; pf = "#0f1a14" if n else "#3f6a3a"
    houses = [(70, "#f0d8b8", "#b5604a"), (420, "#e8c4a4", "#8a5a4a"), (960, "#f4e4cc", "#a0503a"), (1300, "#e4ccb0", "#b5604a")]
    for x, wall, roof in houses:
        w = 260
        if n: wall = "#3a3048"; roof = "#231c30"
        o.append(ranch(x, 176, w, wall, roof, n))
    # the pool behind the low wall
    o.append(f'<rect x="730" y="150" width="190" height="34" rx="14" fill="{"#1f6a9a" if n else "#5fc4e8"}"/><path d="M750 166q15 -6 30 0t30 0t30 0t30 0" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>')
    if n: o.append('<ellipse cx="825" cy="167" rx="110" ry="30" fill="#5fc4e8" opacity=".25"/>')
    o.append(f'<path d="M760 150l0 -16l12 0M784 150l0 -16" stroke="#ccc" stroke-width="2" fill="none"/><rect x="866" y="140" width="38" height="8" rx="3" fill="#e8662a"/>')
    for x, h in [(380, 150), (700, 170), (930, 140), (1260, 160), (1580, 140)]:
        o.append(palm(x, 186, h, pt, pf))
    o.append(f'<rect x="0" y="186" width="1600" height="12" fill="{"#3a3048" if n else "#e2d6c8"}"/><rect x="0" y="198" width="1600" height="42" fill="{"#17121f" if n else "#5a4f58"}"/>')
    o.append('<line x1="0" y1="220" x2="1600" y2="220" stroke="#f4e2c8" stroke-width="2" stroke-dasharray="26 20" opacity=".5"/>')
    o.append('<rect x="620" y="160" width="4" height="26" fill="#555"/><rect x="608" y="150" width="28" height="14" rx="6" fill="#2f6fb8"/>')
    if n:
        for x in (300, 820, 1340): o.append(f'<rect x="{x}" y="120" width="4" height="66" fill="#3a3048"/><circle cx="{x + 2}" cy="120" r="30" fill="url(#gl)"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_renewals(n):  # orange blossoms in a citrus grove
    o = [vsky(n, ("#7ec0ec", "#c4e2f2", "#fff2d4"), NITE)]
    o.append(stars(50, 1600, 0, 100, 8) + '<circle cx="1180" cy="54" r="26" fill="#f6efd8"/>' if n else '<circle cx="1180" cy="60" r="80" fill="url(#sn)"/><circle cx="1180" cy="60" r="28" fill="#fff3c4"/>')
    o.append(camel(100, 120, 560, 70, "#1b1531" if n else "#b49ab8"))
    o.append(f'<rect x="0" y="118" width="1600" height="122" fill="{"#2a2018" if n else "#c49a6a"}"/>')
    r = random.Random(9)
    leaf = "#173a22" if n else "#2f7a3a"; leaf2 = "#1f4a2a" if n else "#3f9a4a"
    rows = [(128, 40, .7), (186, 60, 1.15)]
    for y, off, s in rows:
        o.append(f'<path d="M0 {y + 12 * s:.0f}L1600 {y + 12 * s:.0f}" stroke="{"#3a2a1e" if n else "#a87a4a"}" stroke-width="{3 * s:.0f}"/>')
        step = int(150 * s)
        for x in range(-off, 1700, step):
            rx = 58 * s; ry = 40 * s
            o.append(f'<rect x="{x - 4 * s:.0f}" y="{y - 4 * s:.0f}" width="{8 * s:.0f}" height="{16 * s:.0f}" fill="#5a3a2a"/>')
            o.append(f'<ellipse cx="{x}" cy="{y - ry * .7:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{leaf}"/><ellipse cx="{x - rx * .25:.0f}" cy="{y - ry * .95:.0f}" rx="{rx * .55:.0f}" ry="{ry * .55:.0f}" fill="{leaf2}"/>')
            for _ in range(int(3 * s) + 2):
                fx = x + r.uniform(-rx * .8, rx * .8); fy = y - ry * .7 + r.uniform(-ry * .7, ry * .6)
                if r.random() < .5:
                    o.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="{5 * s:.1f}" fill="#ff9a1f"/>')
                else:
                    o.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="{3.4 * s:.1f}" fill="#fffaf0"/><circle cx="{fx:.0f}" cy="{fy:.0f}" r="{1.2 * s:.1f}" fill="#ffd23f"/>')
    for x, y in [(560, 60), (620, 84), (940, 50)]:
        o.append(f'<g transform="translate({x} {y})"><ellipse rx="7" ry="5" fill="#ffd23f"/><path d="M-2 -5v10M2 -5v10" stroke="#222" stroke-width="2"/><ellipse cx="-2" cy="-7" rx="5" ry="3" fill="#fff" opacity=".8"/><ellipse cx="3" cy="-7" rx="5" ry="3" fill="#fff" opacity=".8"/></g>')
    o.append(f'<path d="M500 70q30 -20 60 -10t60 14" fill="none" stroke="{"#fff" if n else "#5a3a2a"}" stroke-width="1.6" stroke-dasharray="4 6" opacity=".6"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_claims(n):  # after the storm
    o = [vsky(n, ("#4f9ae0", "#8cc4ec", "#d8e8f0"), NITE,
              lingrad("st", [(0, "#2a3040"), (1, "#4a5266")], 1, 0))]
    if n: o.append(stars(40, 1600, 0, 80, 9))
    else: o.append('<path d="M120 200A360 360 0 0 1 760 120" fill="none" stroke="#ff8a8a" stroke-width="7" opacity=".4"/><path d="M128 210A360 360 0 0 1 768 130" fill="none" stroke="#ffd23f" stroke-width="7" opacity=".4"/><path d="M136 220A360 360 0 0 1 776 140" fill="none" stroke="#7ad07a" stroke-width="7" opacity=".4"/><path d="M144 230A360 360 0 0 1 784 150" fill="none" stroke="#6aa8ff" stroke-width="7" opacity=".4"/>')
    # the storm moving off to the right, still raining there
    sc = "#1e2232" if n else "#4a5266"
    o.append(f'<g fill="{sc}"><ellipse cx="1340" cy="40" rx="320" ry="60"/><ellipse cx="1200" cy="54" rx="160" ry="44"/><ellipse cx="1480" cy="70" rx="200" ry="50"/></g>')
    for x in range(1080, 1600, 26): o.append(f'<line x1="{x}" y1="90" x2="{x - 18}" y2="170" stroke="{"#8a9ab8" if n else "#b8c8dc"}" stroke-width="2" opacity=".55"/>')
    o.append('<path d="M1300 80l-16 30h12l-10 26l26 -36h-12l12 -20z" fill="#ffe680"/>')
    o.append(camel(100, 150, 520, 80, "#1b1531" if n else "#8a6a8a"))
    o.append(f'<rect x="0" y="148" width="1600" height="92" fill="{"#1e1a28" if n else "#b89878"}"/>')
    # the flooded wash across the road
    o.append(f'<path d="M0 190L1600 190L1600 240L0 240Z" fill="{"#17121f" if n else "#5a4f58"}"/>')
    o.append(f'<path d="M1020 186Q1150 174 1300 186L1340 214Q1150 236 980 214Z" fill="{"#4a3a2a" if n else "#a07a50"}"/><path d="M1050 196q30 -6 60 0t60 0t60 0t60 0" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>')
    o.append('<rect x="1370" y="140" width="4" height="56" fill="#888"/><rect x="1336" y="112" width="40" height="40" fill="#ffd23f" transform="rotate(45 1356 132)"/><text x="1356" y="136" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="10" fill="#111">FLOOD</text>')
    # the crew clearing a fallen palm
    pt = "#3a2a2a" if n else "#7a5040"; pf = "#1f3a24" if n else "#3f6a3a"
    o.append(f'<g transform="translate(860 200) rotate(-82)">{palm(0, 0, 230, pt, pf)}</g>')
    o.append(f'<path d="M846 200l-8 -22l16 0l8 22z" fill="{pt}"/><rect x="560" y="190" width="30" height="10" rx="4" fill="#c06a3a"/><rect x="600" y="192" width="24" height="8" rx="4" fill="#c06a3a"/>')
    vest = "#ff8a1f"
    o.append(person(900, 200, 1.0, vest, pants="#2f3b55", arm=-60) + person(960, 200, 1.0, vest, skin="#8a5a3a", pants="#2f3b55", arm=30))
    o.append('<path d="M885 146h30l-4 -8h-22z" fill="#ffd23f"/><path d="M945 146h30l-4 -8h-22z" fill="#ffd23f"/><rect x="914" y="160" width="22" height="10" rx="2" fill="#e8662a"/><rect x="934" y="163" width="18" height="4" fill="#bbb"/>')
    # the crew truck with its light bar
    tk = "#e9edf2" if not n else "#9aa3b5"
    o.append('<g transform="translate(260 0)">' + f'<path d="M180 200L180 160L240 160L260 178L300 178L300 200Z" fill="{tk}"/><rect x="196" y="166" width="34" height="14" fill="#2b3d55"/><circle cx="208" cy="202" r="10" fill="#222"/><circle cx="280" cy="202" r="10" fill="#222"/>'
             '<rect x="194" y="152" width="40" height="8" rx="3" fill="#ff8a1f"/>' + ('<circle cx="214" cy="156" r="30" fill="#ff8a1f" opacity=".3"/>' if n else '') + '</g>')
    for x in (620, 1010): o.append(f'<path d="M{x} 210l10 -26l10 26z" fill="#ff6a1f"/><rect x="{x + 3}" y="196" width="14" height="4" fill="#fff"/>')
    o.append(shade())
    return wrap(V, ''.join(o))

def v_commercial(n):  # downtown towers and offices
    o = [vsky(n, ("#3a4a8a", "#e88a6a", "#ffd0a0"), NITE)]
    o.append(stars(50, 1600, 0, 100, 10) if n else '<circle cx="300" cy="150" r="140" fill="url(#sn)"/><circle cx="300" cy="150" r="40" fill="#fff3c4"/>')
    o.append(camel(0, 200, 600, 120, "#1b1531" if n else "#7b4a7c"))
    tc = ["#1d1834", "#251e40", "#2a2448"] if n else ["#53315f", "#613a6c", "#7a4a7c"]
    win = "#ffd27a" if n else "#ffc98a"
    r = random.Random(11)
    x = 420
    specs = [(40, 80, 0), (90, 64, 2), (30, 90, 1), (60, 70, 3), (110, 56, 0), (20, 84, 2), (70, 72, 1), (50, 60, 3), (100, 70, 0), (36, 90, 2), (80, 64, 1), (120, 70, 0)]
    for top, w, cr in specs:
        o.append(tower(x, top, w, 240, r.choice(tc), win, n, cr, 20))
        x += w + 6
    # a construction crane on a new tower
    cc = "#e8a23a"
    o.append(f'<rect x="1300" y="30" width="8" height="210" fill="{cc}"/><rect x="1180" y="26" width="260" height="8" fill="{cc}"/><line x1="1220" y1="34" x2="1220" y2="96" stroke="#333" stroke-width="2"/><rect x="1208" y="96" width="24" height="12" fill="#2f6fb8"/>')
    o.append(f'<path d="M1304 30L1240 26M1304 30L1420 26" stroke="{cc}" stroke-width="2"/>')
    if n: o.append('<circle cx="1440" cy="26" r="4" fill="#ff3b3b"/><circle cx="1440" cy="26" r="12" fill="#ff3b3b" opacity=".35"/>')
    o.append(f'<rect x="0" y="222" width="1600" height="18" fill="{"#100c1a" if n else "#4a3446"}"/>')
    o.append(f'<text x="800" y="210" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#fff" opacity=".0">.</text>')
    o.append(shade())
    return wrap(V, ''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "rush hour: premium on the move"],
    "messages": ["Texts & Emails", "the tower ridge: every signal answered"],
    "coaching": ["Coaching", "up on the roof: every call, replayed"],
    "roleplay": ["Role Play", "spring training: reps before it counts"],
    "rphistory": ["Session History", "the replay motel: every session kept"],
    "training": ["Training", "one switchback at a time"],
    "blueprint": ["Apollo's Road Map", "the apollo line, in plain words"],
    "athenamap": ["Athena's Road Map", "the athena line, in plain words"],
    "service": ["Service Digest", "the neighborhood: keeping the book"],
    "renewals": ["Renewals", "the grove: what came back"],
    "claims": ["Claims", "after the monsoon: the crew is out"],
    "commercial": ["Commercial Center", "downtown: Cerberus's book"],
}

# ------------------------------------------------------------------ strips (1600 x 160)
S = 160
def ssky(night, day, nt, extra=''):
    c = nt if night else day
    return ('<defs>' + lingrad("g", [(0, c[0]), (.6, c[1]), (1, c[2])]) + radgrad("gl", "#ffd27a", .6) + PALM_DEF + extra + '</defs>'
            f'<rect width="1600" height="{S}" fill="url(#g)"/>')
def cap(t, col="#fff", size=26):
    return f'<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="{size}" fill="{col}">{t}</text>'
def capshade():
    return ('<defs><linearGradient id="cs" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".35"/><stop offset=".35" stop-color="#000" stop-opacity="0"/></linearGradient></defs>'
            f'<rect width="1600" height="{S}" fill="url(#cs)"/>')
def mini_downtown(n, x0=420, base=130, col=None):
    col = col or ("#1d1834" if n else "#3a2448"); o = []; x = x0
    for top, w in [(70, 40), (52, 50), (80, 34), (44, 46), (66, 40), (58, 52), (76, 36), (62, 44)]:
        o.append(f'<rect x="{x}" y="{top}" width="{w}" height="{base - top}" fill="{col}"/>')
        for y in range(top + 8, base - 4, 16):
            o.append(f'<path d="M{x + 4} {y}h{w - 8}" stroke="#ffd27a" stroke-width="3" stroke-dasharray="5 5" opacity=".75"/>')
        x += w + 6
    return ''.join(o)

def s_sold(n):  # FIREWORKS over downtown
    o = [ssky(n, ("#2a1e5a", "#8a3f7a", "#e46a5c"), ("#05071a", "#121a3e", "#2b2352"))]
    o.append(stars(6, 1600, 0, 120, 21))
    for cx, cy, rr, c in [(560, 60, 40, "#ffd23f"), (760, 46, 52, "#ff4fa8"), (960, 64, 40, "#3ff0e0"), (1110, 56, 30, "#ff8a3d")]:
        o.append(burst(cx, cy, rr, c)); o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr * 1.6:.0f}" fill="{c}" opacity=".12"/>')
    o.append('<path d="M760 128Q756 100 760 70M960 128Q964 104 960 82" stroke="#ffd27a" stroke-width="2" stroke-dasharray="3 5" opacity=".7"/>')
    o.append(mini_downtown(n, 560, 136))
    o.append(f'<rect x="0" y="130" width="1600" height="30" fill="{"#0e0a18" if n else "#2a1a36"}"/>')
    o.append(capshade() + cap("FIREWORKS"))
    return wrap(S, ''.join(o))

def s_open(n):  # NEXT TRAIN: a light-rail train arriving, green signal
    o = [ssky(n, ("#4a2c6e", "#e46a5c", "#ffc480"), ("#070a1e", "#161c42", "#2b2352"))]
    if n: o.append(stars(20, 1600, 0, 60, 22))
    o.append(camel(900, 120, 420, 60, "#1b1531" if n else "#7b4a7c"))
    o.append(f'<rect x="0" y="118" width="1600" height="42" fill="{"#17121f" if n else "#6e5868"}"/><rect x="0" y="118" width="1600" height="3" fill="#9a8fa8"/>')
    o.append('<line x1="0" y1="56" x2="1600" y2="56" stroke="#3a2c40" stroke-width="1.5"/>')
    o.append(train(640, 120, 380, n))
    o.append('<path d="M1020 90h120M1030 100h90M1020 110h110" stroke="#fff" stroke-width="2" opacity=".5"/>' if False else '')
    o.append('<path d="M560 84h60M540 96h70M570 108h50" stroke="#fff" stroke-width="2.4" opacity=".55" stroke-linecap="round"/>')
    # signal: green
    o.append('<rect x="486" y="56" width="6" height="64" fill="#444"/><rect x="474" y="30" width="30" height="44" rx="6" fill="#1d2a3a"/><circle cx="489" cy="42" r="6" fill="#3a2a2a"/><circle cx="489" cy="61" r="7" fill="#3dff7a"/><circle cx="489" cy="61" r="16" fill="#3dff7a" opacity=".3"/>')
    o.append(capshade() + cap("NEXT TRAIN"))
    return wrap(S, ''.join(o))

def s_lost(n):  # MISSED THE TRAIN: the train leaving, grey
    o = [ssky(n, ("#6a6e7a", "#9a9ea8", "#c4c6cc"), ("#0a0c14", "#1a1d28", "#2a2d3a"))]
    o.append(camel(920, 120, 420, 60, "#2a2d38" if n else "#80838e"))
    o.append(f'<rect x="0" y="118" width="1600" height="42" fill="{"#15161c" if n else "#6a6c74"}"/><rect x="0" y="118" width="1600" height="3" fill="#9a9ca4"/>')
    o.append(f'<rect x="420" y="112" width="300" height="10" fill="{"#2a2c34" if n else "#8a8c94"}"/>')
    o.append(train(820, 120, 340, n, stripe="#8a8c94", body="#b8bac0" if not n else "#5a5c66", flip=True))
    o.append('<path d="M790 80h-60M800 94h-80M790 108h-50" stroke="#fff" stroke-width="2.4" opacity=".35" stroke-linecap="round"/>')
    o.append(person(600, 112, .95, "#7a7c86", skin="#a8a0a0", pants="#4a4c56", arm=-120))
    o.append('<rect x="596" y="60" width="14" height="18" rx="2" fill="#5a5c66" transform="rotate(-20 600 60)"/>' if False else '')
    o.append('<rect x="486" y="56" width="6" height="64" fill="#444"/><rect x="474" y="30" width="30" height="44" rx="6" fill="#1d2a3a"/><circle cx="489" cy="42" r="7" fill="#ff3b3b"/><circle cx="489" cy="61" r="6" fill="#2a3a2a"/>')
    o.append(capshade() + cap("MISSED THE TRAIN", size=24))
    return wrap(S, ''.join(o))

def s_dead(n):  # HABOOB: a dust wall rolling in
    o = [ssky(n, ("#c48a5a", "#d8a070", "#e8c090"), ("#1a120c", "#2a1c12", "#3a2618"),
              lingrad("du", [(0, "#a8682e"), (1, "#d89a5a")], 0, 1))]
    o.append(mini_downtown(n, 380, 132, "#3a2418" if n else "#6a4028"))
    wall = [(620, 160), (640, 110), (680, 70), (720, 48), (780, 30), (860, 20), (960, 14), (1100, 10), (1300, 8), (1600, 6), (1600, 160)]
    o.append(f'<path d="{smooth(wall)}" fill="{"#5a3a22" if n else "url(#du)"}" opacity=".95"/>')
    for cx, cy, rr in [(690, 80, 30), (740, 54, 34), (810, 36, 30), (900, 28, 34), (1000, 22, 30)]:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{"#6a4a2c" if n else "#c88a50"}" opacity=".9"/>')
    o.append(f'<rect x="0" y="130" width="1600" height="30" fill="{"#2a1c12" if n else "#8a5a34"}"/>')
    for x, y in [(560, 100), (590, 112), (600, 86)]: o.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{"#8a6a4a" if n else "#e8b880"}" opacity=".7"/>')
    o.append(capshade() + cap("HABOOB"))
    return wrap(S, ''.join(o))

def s_porch(n):  # PORCH CHAT: two neighbours on a porch
    o = [ssky(n, ("#f08a5a", "#ffc48a", "#ffe8c4"), ("#070a1e", "#161c42", "#2b2352"))]
    if n: o.append(stars(20, 1600, 0, 60, 23))
    wall = "#3a3048" if n else "#f0d8b8"; roof = "#231c30" if n else "#b5604a"
    o.append(f'<rect x="480" y="56" width="560" height="74" fill="{wall}"/><path d="M450 60L520 36L1000 36L1070 60Z" fill="{roof}"/>')
    o.append(f'<rect x="900" y="74" width="34" height="56" fill="#2f8a8a"/><rect x="540" y="72" width="70" height="34" fill="{"#ffd27a" if n else "#5a7a9a"}"/>')
    o.append(f'<rect x="460" y="128" width="600" height="8" fill="{"#2a2236" if n else "#c9a88a"}"/><rect x="0" y="136" width="1600" height="24" fill="{"#1a2a1e" if n else "#9cc47a"}"/>')
    for x in (500, 1020): o.append(f'<rect x="{x}" y="60" width="8" height="70" fill="{"#2a2236" if n else "#fff"}"/>')
    o.append(f'<rect x="690" y="104" width="34" height="5" fill="#7a5040"/><rect x="800" y="104" width="34" height="5" fill="#7a5040"/>')
    o.append(sitter(712, 128, 1.15, "#e8662a") + sitter(812, 128, 1.15, "#2f6fb8", skin="#8a5a3a", flip=True))
    o.append('<rect x="752" y="112" width="20" height="16" fill="#c9a88a"/><rect x="756" y="104" width="8" height="10" rx="2" fill="#ffd23f"/>')
    o.append(f'<rect x="700" y="46" width="44" height="22" rx="10" fill="#fff"/><text x="722" y="62" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#3a2242">...</text>'
             f'<rect x="784" y="40" width="44" height="22" rx="10" fill="#fff"/><text x="806" y="56" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#3a2242">ha!</text>')
    o.append(palm(1120, 140, 120, "#120c1e" if n else "#7a5040", "#0f1a14" if n else "#3f6a3a"))
    if n: o.append('<circle cx="760" cy="70" r="80" fill="url(#gl)"/>')
    o.append(capshade() + cap("PORCH CHAT"))
    return wrap(S, ''.join(o))

def s_stop(n):  # AT THE STOP: waiting under a shade canopy
    o = [ssky(n, ("#3f86d6", "#8cc4ec", "#f6e2b8"), ("#070a1e", "#161c42", "#2b2352"))]
    o.append('<circle cx="1120" cy="40" r="60" fill="#fff1b8" opacity=".5"/><circle cx="1120" cy="40" r="22" fill="#fff3c4"/>' if not n else stars(24, 1600, 0, 60, 24))
    o.append(camel(980, 122, 360, 50, "#1b1531" if n else "#a888a8"))
    o.append(f'<rect x="0" y="120" width="1600" height="40" fill="{"#17121f" if n else "#d8c4b4"}"/><rect x="0" y="130" width="1600" height="3" fill="#8a8a96"/>')
    can = "#e8662a" if not n else "#c4511e"; post = "#5a4a5a"
    o.append(f'<rect x="620" y="52" width="6" height="70" fill="{post}"/><rect x="900" y="52" width="6" height="70" fill="{post}"/><path d="M590 56L940 56L960 40L610 40Z" fill="{can}"/>')
    o.append(f'<path d="M626 122L906 122L940 132L600 132Z" fill="#000" opacity=".12"/>')
    o.append(f'<rect x="680" y="100" width="90" height="6" fill="#7a6a7a"/><rect x="690" y="106" width="4" height="16" fill="#7a6a7a"/><rect x="756" y="106" width="4" height="16" fill="#7a6a7a"/>')
    o.append(sitter(730, 122, 1.0, "#2f8a8a"))
    o.append('<rect x="820" y="70" width="46" height="24" rx="3" fill="#1d2a3a"/><text x="843" y="87" text-anchor="middle" font-family="monospace" font-size="11" fill="#ffd27a">12 MIN</text>')
    o.append(capshade() + cap("AT THE STOP"))
    return wrap(S, ''.join(o))

def s_vm(n):  # a coyote asleep under the moon by the mountain
    o = [ssky(n, ("#2a2058", "#4a3a7a", "#7a5a8a"), ("#04060f", "#0a0f24", "#1a1838"))]
    o.append(stars(40, 1600, 0, 110, 25))
    o.append('<circle cx="1080" cy="48" r="70" fill="#f6efd8" opacity=".12"/><circle cx="1080" cy="48" r="24" fill="#f6efd8"/><circle cx="1070" cy="42" r="5" fill="#e4dbc0"/>')
    o.append(camel(820, 130, 420, 70, "#1b1531" if n else "#2e2448"))
    o.append(f'<rect x="0" y="126" width="1600" height="34" fill="{"#120e1c" if n else "#2a2040"}"/>')
    fur = "#9a7a5a" if not n else "#7a6450"; fur2 = "#c8aa84" if not n else "#a08a70"
    o.append(f'<g transform="translate(700 124)"><path d="M-70 0Q-80 -30 -40 -36Q10 -42 40 -26Q60 -14 50 0Z" fill="{fur}"/>'
             f'<path d="M48 -4Q80 -8 84 -26Q70 -14 50 -14Z" fill="{fur}"/><path d="M80 -24Q86 -30 82 -36Q76 -24 74 -20Z" fill="{fur2}"/>'
             f'<path d="M-62 -8Q-96 -10 -104 -2Q-98 4 -64 2Z" fill="{fur}"/><path d="M-60 -16L-58 -40L-48 -22ZM-74 -18L-78 -40L-64 -24Z" fill="{fur}"/>'
             f'<ellipse cx="-90" cy="-4" rx="6" ry="3" fill="{fur2}"/><path d="M-72 -10q4 3 8 0" stroke="#222" stroke-width="1.6" fill="none"/></g>')
    o.append('<text x="560" y="88" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#ffd27a">z</text><text x="580" y="74" font-family="Arial, sans-serif" font-weight="bold" font-size="26" fill="#ffd27a">z</text><text x="606" y="58" font-family="Arial, sans-serif" font-weight="bold" font-size="32" fill="#ffd27a">z</text>')
    o.append(capshade() + cap("ALL QUIET", size=24))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_porch, "live_no_quote": s_stop,
             "callback_no_contact": s_vm}
# The header's greetings in this world only (Frank, 2026-10-05: "world themed ones that appear only in those worlds"); {n} is the first name.
GREETINGS = ['Rise from the ashes, {n}.', 'Another sunny day in the Valley, {n}.', "It's a dry heat, {n}. The leads aren't.", 'Valley strong, {n}.', 'Monsoon season for premium, {n}.', "Light rail's running, so are the phones, {n}.", 'Up and rising, {n}.', 'Hot day, hot leads, {n}.', 'From the Valley to the summit, {n}.', "Sunset's later than the last close, {n}.", 'Rise and grind, {n}.', 'Haboob of sales incoming, {n}.', "The Valley's waking up, {n}.", 'Fly like a phoenix, {n}.', 'Hydrate and dominate, {n}.']

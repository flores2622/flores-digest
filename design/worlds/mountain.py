"""The Mountain world: a national park. Colour looks, fonts, the Digest picture, page banners, card strips."""
import random, math

KEY = "mountain"
NAME = "Mountain"
CATEGORY = "Outdoors"   # the group it is listed under in Settings
FONTS = "family=Zilla+Slab:wght@600;700&family=Work+Sans:wght@400;500;600;700"
DISPLAY = "'Zilla Slab', Georgia, serif"
DW = 700
BODY = "'Work Sans', system-ui, sans-serif"
SKY_BG = (("#6fa6d6", "#6a9452"), ("#070d1f", "#152536"))

LOOKS = [
    ("evergreen", "Evergreen",
     "--surface: #ecebe0; --surface-raised: #fbf9f1; --card2: #f2efe3; --chip: #e4e0cf; --text-primary: #1d2a22; --text-muted: #5b6658; --text-secondary: #44513f; --grid: #e3dfd0; --border: #d9d4c2; --border-strong: #bdb59d; --accent: #b24a24; --accent-d: #8a3618; --side: #1f3a2b; --side2: #2a4a37; --sideInk: #dfe9df; --brand: #f3efe2; --brand2: #e8a070; --rad: 12px;",
     "--surface: #0f1612; --surface-raised: #16201a; --card2: #1c2820; --chip: #233128; --text-primary: #e6ede4; --text-muted: #9fb0a0; --text-secondary: #b9c6b8; --grid: #233128; --border: #26342b; --border-strong: #34473a; --accent: #e98a5c; --accent-d: #f2ac88; --side: #0a120d; --side2: #13221a; --sideInk: #dfe9df; --brand: #f3efe2; --brand2: #e8a070;",
     ["#ecebe0", "#1f3a2b", "#b24a24"]),
    ("glacier", "Glacier",
     "--surface: #e8edf1; --surface-raised: #f8fafc; --card2: #eef3f6; --chip: #dde6ec; --text-primary: #18242e; --text-muted: #566673; --text-secondary: #43525e; --grid: #dfe6ec; --border: #d4dde4; --border-strong: #b5c3cd; --accent: #2b6f9a; --accent-d: #1d5274; --side: #2e3c48; --side2: #3a4a58; --sideInk: #dbe5ec; --brand: #eef3f6; --brand2: #9fd4f0; --rad: 10px;",
     "--surface: #0e141a; --surface-raised: #151d25; --card2: #1b252f; --chip: #22303b; --text-primary: #e4ecf2; --text-muted: #9aabb8; --text-secondary: #b5c3ce; --grid: #22303b; --border: #25323e; --border-strong: #344553; --accent: #7cc4ea; --accent-d: #a6d8f3; --side: #0a0f14; --side2: #141e27; --sideInk: #dbe5ec; --brand: #eef3f6; --brand2: #9fd4f0;",
     ["#e8edf1", "#2e3c48", "#7cc4ea"]),
    ("aspen", "Aspen",
     "--surface: #f1ebde; --surface-raised: #fdf9f0; --card2: #f6efe0; --chip: #ebe0c8; --text-primary: #2a2016; --text-muted: #6a5b48; --text-secondary: #534533; --grid: #e8dfcc; --border: #e0d5bd; --border-strong: #c6b48f; --accent: #96580a; --accent-d: #74440a; --side: #3b2a1c; --side2: #4a3626; --sideInk: #f0e4d2; --brand: #f6eedd; --brand2: #f2b844; --rad: 14px;",
     "--surface: #15110c; --surface-raised: #1d1812; --card2: #241e16; --chip: #2d251b; --text-primary: #f0e8dc; --text-muted: #b0a28c; --text-secondary: #c8bba6; --grid: #2d251b; --border: #30281e; --border-strong: #43382a; --accent: #f2b844; --accent-d: #f7cd74; --side: #0f0b07; --side2: #1c150e; --sideInk: #f0e4d2; --brand: #f6eedd; --brand2: #f2b844;",
     ["#f1ebde", "#3b2a1c", "#f2b844"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(far="#26324f", main="#33426a", shade="#232e4c", snow="#c9d4ea", snows="#8e9dbd",
                    pine="#0d1f22", pine2="#0a1719", meadow="#1a2c3c", meadow2="#16263a", lake="#13223f",
                    rock="#4a5266", rock2="#353c4e", trail="#4b4c5a", wood="#4a3020", wood2="#33200f",
                    ink="#f3e7cf", log="#5a3a24", win="#ffcf6a")
    return dict(far="#a9bdd3", main="#7890ad", shade="#5e7592", snow="#ffffff", snows="#d6e2ef",
                pine="#285240", pine2="#1d3f30", meadow="#79a35d", meadow2="#6a9452", lake="#4e8fc0",
                rock="#c2bdb2", rock2="#9c968a", trail="#dcc79c", wood="#7a4a26", wood2="#5a3418",
                ink="#fbefd4", log="#8a5a32", win="#a9d0e4")

def stars(n, x0, x1, y0, y1, seed, op=(0.35, 0.55, 0.85)):
    r = random.Random(seed); o = []
    for _ in range(n):
        o.append(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([0.7, 1, 1.3, 1.8])}" fill="#fff" opacity="{r.choice(op)}"/>')
    return ''.join(o)

def pine(x, b, h, c, tc=None):
    w = h * .42; top = b - h; n = 4; R = []
    for i in range(1, n + 1):
        y = top + h * .86 * i / n; hw = w / 2 * (.38 + .62 * i / n)
        R += [(x + hw, y), (x + hw * .45, y)] if i < n else [(x + hw, y)]
    pts = [(x, top)] + R + [(2 * x - px, py) for px, py in reversed(R)]
    d = 'M' + 'L'.join(f'{px:.0f} {py:.0f}' for px, py in pts) + 'Z'
    t = f'<rect x="{x - h * .035:.0f}" y="{top + h * .85:.0f}" width="{max(2, h * .07):.0f}" height="{h * .15:.0f}" fill="{tc}"/>' if tc else ''
    return t + f'<path d="{d}" fill="{c}"/>'

def forest(x0, x1, b, hmin, hmax, c, seed, step=26):
    r = random.Random(seed); o = []
    x = x0
    while x < x1:
        o.append(pine(x, b + r.randint(-4, 6), r.randint(hmin, hmax), c)); x += r.randint(step - 8, step + 8)
    return ''.join(o)

def peak(ax, ay, lx, rx, b, p, f=.3, seed=1):
    o = [f'<path d="M{lx} {b} L{ax} {ay} L{rx} {b} Z" fill="{p["main"]}"/>']
    sx = ax + (rx - lx) * .07
    o.append(f'<path d="M{ax} {ay} L{rx} {b} L{sx:.0f} {b} Z" fill="{p["shade"]}"/>')
    Lx, Ly = ax + (lx - ax) * f, ay + (b - ay) * f
    Rx, Ry = ax + (rx - ax) * f, ay + (b - ay) * f
    r = random.Random(seed); pts = [(Rx, Ry)]; k = 6
    for i in range(1, k):
        t = i / k
        pts.append((Rx + (Lx - Rx) * t, Ry + (Ly - Ry) * t + (r.uniform(.25, .5) if i % 2 else -r.uniform(0, .1)) * (b - ay) * f))
    pts.append((Lx, Ly))
    o.append(f'<path d="M{ax} {ay} ' + ' '.join(f'L{x:.0f} {y:.0f}' for x, y in pts) + 'Z" fill="' + p["snow"] + '"/>')
    j = pts[1]; dx = ax + (sx - ax) * ((j[1] - ay) / (b - ay))
    o.append(f'<path d="M{ax} {ay} L{Rx:.0f} {Ry:.0f} L{j[0]:.0f} {j[1]:.0f} L{dx:.0f} {j[1]:.0f}Z" fill="{p["snows"]}"/>')
    return ''.join(o)

def ridge(pts, b, c):
    return f'<path d="M{pts[0][0]} {b} ' + ' '.join(f'L{x} {y}' for x, y in pts) + f' L{pts[-1][0]} {b}Z" fill="{c}"/>'

def moon(x, y, r, glow=True):
    g = f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".08"/><circle cx="{x}" cy="{y}" r="{r * 1.8}" fill="#e9eefc" opacity=".12"/>' if glow else ''
    return g + f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4efdc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#ddd6bd"/><circle cx="{x + r * .3:.0f}" cy="{y + r * .3:.0f}" r="{r * .12:.0f}" fill="#ddd6bd"/>'

def sun(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r * 2.6}" fill="#fff4cf" opacity=".25"/><circle cx="{x}" cy="{y}" r="{r * 1.6}" fill="#fff4cf" opacity=".35"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fff7dc"/>'

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s} {y - 3 * s} Q{x - 5 * s} {y - 7 * s} {x} {y} Q{x + 5 * s} {y - 7 * s} {x + 10 * s} {y - 3 * s}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

def eagle(x, y, s, c, head="#fff"):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 0 Q-20 -14 -52 -10 L-40 -4 L-50 0 L-36 2 L-44 8 Q-18 6 0 6 Q18 6 44 8 L36 2 L50 0 L40 -4 L52 -10 Q20 -14 0 0Z" fill="{c}"/>'
            f'<path d="M-4 4 L4 4 L2 16 L-2 16Z" fill="{c}"/><circle cx="0" cy="-1" r="4" fill="{head}"/></g>')

def smoke(x, y, n, op=.5, c="#e8ecef"):
    return ''.join(f'<circle cx="{x + i * 9 + (i % 2) * 6}" cy="{y - i * 16}" r="{6 + i * 3}" fill="{c}" opacity="{op * (1 - i / (n + 1)):.2f}"/>' for i in range(n))

def fire(x, y, s, n):
    o = []
    if n: o.append(f'<circle cx="{x}" cy="{y - 8 * s}" r="{70 * s}" fill="url(#glow)"/>')
    o.append(f'<path d="M{x - 22 * s} {y} L{x + 22 * s} {y - 8 * s}" stroke="#5a3a24" stroke-width="{7 * s}" stroke-linecap="round"/><path d="M{x - 22 * s} {y - 8 * s} L{x + 22 * s} {y}" stroke="#6a4428" stroke-width="{7 * s}" stroke-linecap="round"/>')
    o.append(f'<path d="M{x - 13 * s} {y - 4 * s} Q{x - 14 * s} {y - 26 * s} {x} {y - 44 * s} Q{x + 4 * s} {y - 26 * s} {x + 13 * s} {y - 4 * s}Z" fill="#f2762e"/>'
             f'<path d="M{x - 7 * s} {y - 4 * s} Q{x - 6 * s} {y - 18 * s} {x + 1 * s} {y - 28 * s} Q{x + 4 * s} {y - 16 * s} {x + 7 * s} {y - 4 * s}Z" fill="#ffd36a"/>')
    return ''.join(o)

def hiker(x, y, s, c="#c8552b", pack="#3b5a3a", flip=False, stick=True):
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    return (g + '<path d="M-6 0 L-2 -26 L4 -26 L9 0" stroke="#3a3a46" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<rect x="-19" y="-52" width="12" height="26" rx="4" fill="{pack}"/><rect x="-9" y="-54" width="18" height="30" rx="7" fill="{c}"/>'
            '<circle cx="1" cy="-63" r="8.5" fill="#e3b48c"/><path d="M-11 -65 h24 l-4 -7 h-15z" fill="#6a4426"/>'
            + ('<path d="M7 -42 L16 -36 L20 0" stroke="#7a5a3a" stroke-width="3" fill="none" stroke-linecap="round"/>' if stick else '') + '</g>')

def tent(x, b, w, h, c, door):
    return (f'<path d="M{x - w / 2} {b} L{x} {b - h} L{x + w / 2} {b}Z" fill="{c}"/><path d="M{x} {b - h} L{x + w / 2} {b} L{x + w * .3} {b}Z" fill="#000" opacity=".15"/>'
            f'<path d="M{x} {b - h * .62} L{x + w * .16} {b} L{x - w * .16} {b}Z" fill="{door}"/>')

def sign(x, y, w, h, text, p, fs=20, posts=60, sub=None):
    o = [f'<rect x="{x - w * .38:.0f}" y="{y}" width="8" height="{h + posts}" fill="{p["wood2"]}"/><rect x="{x + w * .38 - 8:.0f}" y="{y}" width="8" height="{h + posts}" fill="{p["wood2"]}"/>',
         f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{h}" rx="5" fill="{p["wood"]}" stroke="{p["wood2"]}" stroke-width="4"/>',
         f'<text x="{x}" y="{y + h / 2 + fs * .36 - (fs * .5 if sub else 0):.0f}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["ink"]}" letter-spacing="1">{text}</text>']
    if sub: o.append(f'<text x="{x}" y="{y + h / 2 + fs * .75:.0f}" text-anchor="middle" font-family="Georgia, serif" font-size="{fs * .62:.0f}" fill="{p["ink"]}" opacity=".85">{sub}</text>')
    return ''.join(o)

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc35a" stop-opacity=".6"/><stop offset="1" stop-color="#ffc35a" stop-opacity="0"/></radialGradient>'
            + extra + '</defs>')

def skyg(h, n, day=("#3f7fc4", "#8cc0e6", "#f3e2c4"), nt=("#050a1a", "#0f1d3d", "#27375e"), id="g"):
    c = nt if n else day
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/><stop offset=".6" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

AUR = ('<filter id="bl" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="14"/></filter><linearGradient id="au" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5dffb0" stop-opacity="0"/><stop offset=".6" stop-color="#5dffb0" stop-opacity=".45"/><stop offset="1" stop-color="#5dffb0" stop-opacity="0"/></linearGradient>')

def aurora(x0, x1, y, amp, th):
    w = x1 - x0
    return (f'<path d="M{x0} {y} C{x0 + w * .25} {y - amp} {x0 + w * .45} {y + amp} {x0 + w * .7} {y - amp * .6} S{x1 - w * .05} {y + amp * .3} {x1} {y - amp * .4} '
            f'L{x1} {y - amp * .4 + th} C{x1 - w * .2} {y + th} {x0 + w * .55} {y + amp + th * .6} {x0 + w * .35} {y + th} S{x0 + w * .1} {y - amp * .2 + th} {x0} {y + th}Z" fill="url(#au)"/>')

SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(240, body + SHADE)
def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    # the horizon sits below the split, so the peaks' feet, the treeline and the lake's far shore
    # run on into the leaderboard's top (Frank, 2026-10-05: "one background on 2 cards that flow into each other")
    HZ = SPLIT + 62
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(defs(skyg(1, n, day=("#3d7ec4", "#93c4e8", "#f6e3c2"), nt=("#040817", "#0d1a3a", "#25365e"), id="sky") + AUR +
           '<radialGradient id="mg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'))
    a(f'<rect width="{W}" height="{HZ + 30}" fill="url(#sky)"/>')
    if n:
        a('<g filter="url(#bl)" opacity=".8">' + aurora(-50, 1100, 70, 40, 70) + aurora(300, 1650, 120, 30, 50) + '</g>')
        a(stars(90, 0, W, 0, 300, 3))
        for pts in [[(420, 40), (460, 60), (505, 52), (540, 80), (590, 70)], [(1040, 30), (1080, 54), (1120, 44), (1150, 72)]]:
            a('<polyline points="' + ' '.join(f'{x},{y}' for x, y in pts) + '" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1"/>')
            for x, y in pts: a(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#fff" opacity=".9"/>')
        a(moon(1290, 82, 34))
    else:
        a(sun(1300, 92, 36))
        for x, y, w in [(520, 120, 240), (1080, 70, 200), (180, 150, 180)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="11" fill="#fff" opacity=".5"/><ellipse cx="{x + 30}" cy="{y - 9}" rx="{w // 3}" ry="10" fill="#fff" opacity=".45"/>')
        a(eagle(640, 62, 1.15, "#4a3424")); a(bird(720, 96, 1, "#4a5a6a")); a(bird(748, 84, .8, "#4a5a6a"))
    # far range
    a(ridge([(0, 250), (120, 196), (230, 236), (420, 168), (560, 222), (700, 186), (860, 230), (1100, 150), (1300, 224), (1450, 178), (1600, 230)], HZ, p["far"]))
    # the main peaks
    a(peak(900, 34, 560, 1260, HZ, p, .3, 4))
    a(peak(600, 98, 330, 860, HZ, p, .3, 5))
    a(peak(1230, 86, 1000, 1500, HZ, p, .3, 6))
    a(peak(310, 140, 70, 560, HZ, p, .28, 7))
    if n: a('<ellipse cx="1290" cy="90" rx="260" ry="120" fill="url(#mg)"/>')
    # treeline at the horizon
    a(forest(-10, 1610, HZ + 4, 26, 58, p["pine2"], 2, 22))
    # tall pines rising into the sky band, at both edges
    for x, b, h in [(130, 455, 300), (40, 475, 410), (1440, 450, 300), (1540, 485, 430)]:
        a(pine(x, b, h, p["pine"], p["wood2"]))
    # ---------------- below the horizon
    a(f'<rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="{p["meadow"]}"/>')
    # the lake, far right, against the treeline
    a(f'<path d="M860 {HZ} L1600 {HZ} L1600 {HZ + 120} Q1300 {HZ + 132} 1080 {HZ + 84} Q940 {HZ + 54} 860 {HZ} Z" fill="{p["lake"]}"/>')
    a(f'<path d="M1080 {HZ + 84} Q1300 {HZ + 132} 1600 {HZ + 120} L1600 {HZ + 132} Q1300 {HZ + 146} 1070 {HZ + 92}Z" fill="{"#d9cba6" if not n else "#3a4252"}"/>')
    # reflections of the peaks in the lake
    a(f'<path d="M1000 {HZ} L1230 {HZ + 70} L1460 {HZ}Z" fill="{p["main"]}" opacity=".35"/>')
    for i, (x, y, w) in enumerate([(1000, 457, 120), (1180, 474, 160), (1380, 466, 110), (1300, 502, 140), (1500, 494, 70), (1120, 500, 60)]):
        a(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="#fff" opacity="{.45 if not n else .22}"/>')
    if n: a(f'<path d="M1270 {HZ + 4} L1310 {HZ + 4} L1330 {HZ + 110} L1250 {HZ + 110}Z" fill="#f4efdc" opacity=".16"/>')
    # a red canoe on the lake
    a(f'<path d="M1200 {HZ + 52} Q1250 {HZ + 66} 1300 {HZ + 52} Q1250 {HZ + 58} 1200 {HZ + 52}Z" fill="#c2452a"/><path d="M1200 {HZ + 52} Q1250 {HZ + 70} 1300 {HZ + 52}" fill="none" stroke="#7a2a18" stroke-width="2"/>'
      f'<line x1="1236" y1="{HZ + 36}" x2="1262" y2="{HZ + 66}" stroke="{p["wood2"]}" stroke-width="3"/>')
    # rolling meadow tones
    a(f'<path d="M0 {SPLIT + 150} Q400 {SPLIT + 110} 820 {SPLIT + 170} T1600 {SPLIT + 190} L1600 {H} L0 {H}Z" fill="{p["meadow2"]}"/>')
    r = random.Random(11); sc = "#5d8a4a" if not n else "#12212f"
    for _ in range(30):
        x = r.randint(0, W); y = r.randint(SPLIT + 160, 880)
        if 450 < x < 1160 and y > 520: continue
        a(f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(10, 24)}" ry="{r.randint(4, 8)}" fill="{sc}"/>')
    if not n:
        for _ in range(26):
            x = r.randint(20, W - 20); y = r.randint(SPLIT + 170, 860)
            if 450 < x < 1160 and y > 520: continue
            a(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{r.choice(["#f2d14a", "#e86a8a", "#f7f3e8", "#9b7fe0"])}"/>')
    # ranger cabin, left
    cx, cb = 210, 640
    a(f'<rect x="{cx + 60}" y="{cb - 150}" width="26" height="70" fill="{"#8a8378" if not n else "#3a3a44"}"/>')
    a(smoke(cx + 74, cb - 168, 5, .55 if not n else .25, "#eef1f3" if not n else "#9aa4b8"))
    a(f'<rect x="{cx - 110}" y="{cb - 92}" width="220" height="92" fill="{p["log"]}"/>')
    for y in range(cb - 84, cb, 14): a(f'<line x1="{cx - 110}" y1="{y}" x2="{cx + 110}" y2="{y}" stroke="{p["wood2"]}" stroke-width="2" opacity=".6"/>')
    a(f'<path d="M{cx - 136} {cb - 86} L{cx} {cb - 170} L{cx + 136} {cb - 86} L{cx + 120} {cb - 78} L{cx} {cb - 150} L{cx - 120} {cb - 78}Z" fill="{"#4a3424" if not n else "#241912"}"/>')
    a(f'<path d="M{cx - 120} {cb - 78} L{cx} {cb - 150} L{cx + 120} {cb - 78}Z" fill="{p["log"]}"/>')
    a(f'<rect x="{cx - 18}" y="{cb - 56}" width="36" height="56" fill="{p["wood2"]}"/><circle cx="{cx + 10}" cy="{cb - 28}" r="2.5" fill="#d8b46a"/>')
    for wx in (cx - 82, cx + 42):
        if n: a(f'<circle cx="{wx + 20}" cy="{cb - 44}" r="44" fill="url(#glow)"/>')
        a(f'<rect x="{wx}" y="{cb - 62}" width="40" height="34" fill="{p["win"]}" stroke="{p["wood2"]}" stroke-width="4"/><line x1="{wx + 20}" y1="{cb - 62}" x2="{wx + 20}" y2="{cb - 28}" stroke="{p["wood2"]}" stroke-width="3"/>')
    a(f'<rect x="{cx - 52}" y="{cb - 128}" width="104" height="22" rx="3" fill="{p["wood2"]}"/><text x="{cx}" y="{cb - 112}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{p["ink"]}" letter-spacing="1">RANGER</text>')
    if n: a(f'<circle cx="{cx + 34}" cy="{cb - 66}" r="5" fill="#ffd27a"/><circle cx="{cx + 34}" cy="{cb - 66}" r="20" fill="url(#glow)"/>')
    # woodpile
    for i in range(6):
        a(f'<circle cx="{cx + 132 + (i % 3) * 16 + (i // 3) * 8}" cy="{cb - 8 - (i // 3) * 15}" r="8" fill="{p["log"]}" stroke="{p["wood2"]}" stroke-width="2"/>')
    # campfire with log seats
    fx, fy = 335, 744
    a(f'<ellipse cx="{fx}" cy="{fy}" rx="44" ry="12" fill="{p["rock2"]}"/>')
    a(fire(fx, fy, 1.15, n))
    if n: a(f'<circle cx="{fx}" cy="{fy - 10}" r="190" fill="url(#glow)" opacity=".7"/>')
    a(f'<rect x="{fx - 112}" y="{fy - 4}" width="52" height="16" rx="8" fill="{p["log"]}"/><rect x="{fx + 64}" y="{fy - 2}" width="52" height="16" rx="8" fill="{p["log"]}"/>')
    # the trail: winding from the treeline down to the summit clearing
    L, R = [], []
    for i in range(41):
        t = i / 40; y = HZ + 10 + t * (775 - HZ - 10)
        x = 800 + 120 * math.sin(t * math.pi * 2.1) * (1 - t * .7)
        hw = 5 + 42 * t ** 1.3
        L.append((x - hw, y)); R.append((x + hw, y))
    a('<path d="M' + 'L'.join(f'{x:.0f} {y:.0f}' for x, y in L + R[::-1]) + f'Z" fill="{p["trail"]}"/>')
    if n:
        for i in range(6, 40, 6):
            x, y = R[i]; a(f'<circle cx="{x + 8:.0f}" cy="{y:.0f}" r="3" fill="#ffd27a"/><circle cx="{x + 8:.0f}" cy="{y:.0f}" r="12" fill="#ffd27a" opacity=".25"/>')
    # trailhead sign by the trail
    a(sign(690, 452, 170, 58, "TRAILHEAD", p, 20, 30, "SUMMIT 0.3 MI"))
    # boulders
    for x, y, r in [(1010, 500, 30), (1046, 510, 20), (1240, 560, 36), (1282, 574, 22)]:
        a(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * .66:.0f}" fill="{p["rock2"]}"/><ellipse cx="{x - r * .2:.0f}" cy="{y - r * .18:.0f}" rx="{r * .7:.0f}" ry="{r * .42:.0f}" fill="{p["rock"]}"/>')
    # the summit clearing: a flat granite slab for the podium
    a(f'<ellipse cx="805" cy="818" rx="345" ry="62" fill="{p["rock2"]}"/><ellipse cx="805" cy="802" rx="338" ry="58" fill="{p["rock"]}"/>')
    a(f'<path d="M600 790 l40 10 l30 -6 M960 784 l-34 14 l-30 -4 M760 830 l26 -8" fill="none" stroke="{p["rock2"]}" stroke-width="3"/>')
    # a cairn on the slab
    for i, (w, h) in enumerate([(40, 16), (32, 14), (24, 12), (16, 10)]):
        a(f'<ellipse cx="{1152 + (i % 2) * 3}" cy="{786 - sum(hh for _, hh in [(40, 16), (32, 14), (24, 12), (16, 10)][:i]) * 1.0:.0f}" rx="{w / 2}" ry="{h / 2}" fill="{p["rock2"] if i % 2 else "#8a857c" if not n else "#5a6276"}"/>')
    # the carved SUMMIT REGISTER sign
    a(sign(1330, 676, 290, 56, "SUMMIT REGISTER", p, 22, 112))
    a(f'<rect x="1392" y="742" width="44" height="34" rx="3" fill="{p["wood2"]}"/><rect x="1396" y="746" width="36" height="8" fill="{p["wood"]}"/>')
    if n:
        a(f'<circle cx="1330" cy="704" r="120" fill="url(#mg)"/>')
    # foreground pines
    for x, b, h in [(70, 900, 330), (1520, 920, 380), (240, 880, 200), (1640, 900, 300)]:
        a(pine(x, b, h, p["pine"], p["wood2"]))
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def base(n, sky=None, nt=None, star=60):
    return defs(skyg(1, n, **({"day": sky} if sky else {}), **({"nt": nt} if nt else {})) + AUR) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 150, 7) if n else '')

def foot(p, y=196):
    return f'<path d="M0 {y} Q400 {y - 14} 800 {y} T1600 {y - 6} L1600 240 L0 240Z" fill="{p["pine2"]}"/>'

def v_sales(n):  # the waterfall running full
    p = P(n); o = [base(n)]
    o.append(moon(1320, 60, 22) if n else sun(1320, 60, 22))
    o.append(ridge([(0, 150), (200, 90), (380, 140), (560, 70), (700, 110)], 200, p["far"]))
    o.append(ridge([(900, 110), (1080, 60), (1260, 130), (1420, 80), (1600, 130)], 200, p["far"]))
    rk = "#6f6a62" if not n else "#2c3040"; rk2 = "#57534c" if not n else "#20232f"
    o.append(f'<path d="M580 240 L600 60 L700 40 L760 52 L760 240Z M840 240 L840 50 L920 36 L1000 66 L1020 240Z" fill="{rk}"/>')
    o.append(f'<path d="M640 240 L660 90 L700 80 L720 240Z M930 240 L920 80 L960 90 L980 240Z" fill="{rk2}"/>')
    wt = "#dff2fb" if not n else "#9fb8d8"; wt2 = "#a9d6ee" if not n else "#5c7aa6"
    o.append(f'<path d="M752 52 L848 52 L860 190 L740 190Z" fill="{wt2}"/>')
    for x in range(760, 846, 14): o.append(f'<path d="M{x} 56 L{x + 4} 186" stroke="{wt}" stroke-width="5" opacity=".85"/>')
    o.append(f'<ellipse cx="800" cy="192" rx="140" ry="26" fill="{wt}" opacity=".7"/><ellipse cx="740" cy="182" rx="60" ry="18" fill="#fff" opacity=".45"/><ellipse cx="870" cy="184" rx="66" ry="18" fill="#fff" opacity=".45"/>')
    o.append(f'<path d="M560 240 Q700 196 800 200 Q920 204 1060 240Z" fill="{p["lake"]}"/>')
    for x, y in [(700, 214), (820, 222), (920, 230)]: o.append(f'<path d="M{x} {y} q20 -6 40 0" stroke="#fff" stroke-opacity=".5" stroke-width="2" fill="none"/>')
    o.append(forest(0, 560, 210, 50, 110, p["pine"], 3, 34)); o.append(forest(1040, 1610, 210, 50, 110, p["pine"], 4, 34))
    if not n: o.append(bird(1100, 50, 1.2, "#3a4a5a") + bird(1130, 40, .9, "#3a4a5a"))
    return vwrap(''.join(o))

def v_messages(n):  # the fire lookout tower with its radio
    p = P(n); o = [base(n, sky=("#3b5d9c", "#e59a6a", "#f8d4a0"))]
    o.append(ridge([(0, 160), (240, 120), (460, 150), (700, 100), (900, 140), (1200, 96), (1400, 140), (1600, 110)], V, p["far"]))
    o.append(ridge([(0, 210), (300, 180), (600, 150), (800, 128), (1000, 150), (1300, 186), (1600, 200)], V, p["main"]))
    lc = "#5a3a20" if not n else "#2a1c12"
    o.append(f'<path d="M760 140 L776 70 M840 140 L824 70 M768 110 L832 110 M772 90 L828 90 M762 140 L828 90 M838 140 L772 90" stroke="{lc}" stroke-width="5" fill="none"/>')
    if n: o.append('<circle cx="800" cy="52" r="90" fill="url(#glow)"/>')
    o.append(f'<rect x="762" y="38" width="76" height="34" fill="{"#e8dcc0" if not n else "#3a3024"}"/><rect x="770" y="44" width="60" height="18" fill="{p["win"] if n else "#8fc4e0"}"/><path d="M752 40 L800 18 L848 40Z" fill="{"#8a3a22" if not n else "#4a2014"}"/>')
    o.append(f'<line x1="836" y1="22" x2="836" y2="-4" stroke="{lc}" stroke-width="3"/><circle cx="836" cy="-2" r="4" fill="#ff5a3a"/>')
    for k in range(1, 4): o.append(f'<path d="M{850 + 12 * k} {10 - 10 * k} A{16 * k} {16 * k} 0 0 1 {850 + 12 * k} {30 + 10 * k}" fill="none" stroke="#fff" stroke-opacity="{.75 - .18 * k:.2f}" stroke-width="3"/>')
    for k in range(1, 4): o.append(f'<path d="M{822 - 12 * k} {10 - 10 * k} A{16 * k} {16 * k} 0 0 0 {822 - 12 * k} {30 + 10 * k}" fill="none" stroke="#fff" stroke-opacity="{.75 - .18 * k:.2f}" stroke-width="3"/>')
    o.append(forest(0, 1610, 236, 40, 90, p["pine"], 5, 30))
    if not n: o.append(bird(500, 60, 1, "#5a3a4a") + bird(530, 48, .8, "#5a3a4a"))
    return vwrap(''.join(o))

def v_coaching(n):  # the trailhead map board under a lamp
    p = P(n); o = [base(n, sky=("#5f97c9", "#a8d0ea", "#e6efe2"))]
    o.append(peak(800, 20, 480, 1120, 200, p, .3, 9))
    o.append(forest(0, 1610, 210, 60, 130, p["pine"], 6, 30))
    o.append(foot(p, 210))
    o.append(f'<rect x="640" y="60" width="12" height="170" fill="{p["wood2"]}"/><rect x="948" y="60" width="12" height="170" fill="{p["wood2"]}"/>')
    o.append(f'<path d="M610 64 L800 22 L990 64Z" fill="{"#5a3a22" if not n else "#2a1c12"}"/>')
    o.append(f'<rect x="660" y="72" width="280" height="130" fill="{p["wood"]}"/><rect x="672" y="82" width="256" height="110" fill="{"#efe4c6" if not n else "#b7aa8a"}"/>')
    for k in range(4): o.append(f'<ellipse cx="760" cy="140" rx="{70 - k * 16}" ry="{40 - k * 9}" fill="none" stroke="#9a8a62" stroke-width="1.5"/>')
    o.append('<path d="M690 180 Q740 150 760 140 T860 110 T910 96" fill="none" stroke="#b5452a" stroke-width="3" stroke-dasharray="7 5"/><circle cx="910" cy="96" r="5" fill="#b5452a"/><text x="900" y="186" text-anchor="end" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="#5a3a22">YOU ARE HERE</text><circle cx="690" cy="180" r="5" fill="#2f7d4a"/>')
    o.append(f'<rect x="1040" y="40" width="8" height="190" fill="{"#3a3a40" if not n else "#20222a"}"/><path d="M1044 44 L1010 44 L1010 52" fill="none" stroke="{"#3a3a40" if not n else "#20222a"}" stroke-width="5"/>')
    o.append(f'<path d="M996 52 L1024 52 L1018 66 L1002 66Z" fill="{"#3a3a40" if not n else "#20222a"}"/><circle cx="1010" cy="68" r="6" fill="{"#fff1c0" if n else "#e8e2cc"}"/>')
    if n: o.append('<path d="M1002 68 L860 230 L1160 230 L1018 68Z" fill="#ffe7a0" opacity=".16"/><circle cx="1010" cy="70" r="60" fill="url(#glow)"/>')
    return vwrap(''.join(o))

def v_roleplay(n):  # the climbing wall and ropes
    p = P(n); o = [base(n, sky=("#4f8ac4", "#9cc8e6", "#e8eedc"))]
    o.append(ridge([(0, 150), (300, 110), (500, 140)], V, p["far"])); o.append(ridge([(1100, 140), (1300, 100), (1600, 130)], V, p["far"]))
    rk = "#9c968a" if not n else "#3a4052"; rk2 = "#7f796e" if not n else "#2a2f3e"
    o.append(f'<path d="M520 240 L540 40 L620 18 L760 30 L880 14 L1000 34 L1060 60 L1080 240Z" fill="{rk}"/>')
    for d in ["M600 40 L590 240", "M760 30 L770 120 L740 240", "M900 20 L930 150", "M1000 40 L980 240"]: o.append(f'<path d="{d}" stroke="{rk2}" stroke-width="4" fill="none"/>')
    r = random.Random(3)
    for _ in range(26): o.append(f'<circle cx="{r.randint(560, 1040)}" cy="{r.randint(40, 210)}" r="{r.choice([5, 6, 7])}" fill="{r.choice(["#e2552b", "#f2c230", "#3aa070", "#4a7fd0", "#c04a9a"])}"/>')
    o.append(f'<circle cx="700" cy="24" r="6" fill="#ccc"/><circle cx="900" cy="18" r="6" fill="#ccc"/>')
    o.append('<path d="M700 24 L700 112 M700 112 Q690 180 660 240" stroke="#e8c23a" stroke-width="3" fill="none"/><path d="M900 18 L900 150 M900 150 Q920 200 940 240" stroke="#e2552b" stroke-width="3" fill="none"/>')
    o.append(hiker(700, 168, .95, "#4a7fd0", "#e2552b", stick=False)); o.append(hiker(900, 206, .95, "#3aa070", "#f2c230", flip=True, stick=False))
    o.append(forest(0, 520, 236, 50, 100, p["pine"], 7, 32)); o.append(forest(1090, 1610, 236, 50, 100, p["pine"], 8, 32))
    return vwrap(''.join(o))

def v_rphistory(n):  # the trail journal, photos pinned
    o = [defs()]
    wd = "#8a5a34" if not n else "#2c1d12"; wd2 = "#744a28" if not n else "#22160d"
    o.append(f'<rect width="1600" height="{V}" fill="{wd}"/>')
    for y in range(0, V, 40): o.append(f'<rect x="0" y="{y}" width="1600" height="3" fill="{wd2}"/>')
    pg = "#f3e9d0" if not n else "#b8ad92"; ln = "#c9b994" if not n else "#8f8670"
    o.append(f'<path d="M420 30 Q610 16 800 34 L800 226 Q610 210 420 222Z" fill="{pg}"/><path d="M800 34 Q990 16 1180 30 L1180 222 Q990 210 800 226Z" fill="{pg}"/><line x1="800" y1="34" x2="800" y2="226" stroke="{ln}" stroke-width="3"/>')
    for y in range(70, 210, 18):
        o.append(f'<line x1="450" y1="{y}" x2="770" y2="{y}" stroke="{ln}" stroke-width="1.2"/><line x1="830" y1="{y}" x2="1150" y2="{y}" stroke="{ln}" stroke-width="1.2"/>')
    o.append('<text x="450" y="62" font-family="Georgia, serif" font-style="italic" font-size="20" fill="#5a3a22">Day 14 - made the ridge by noon</text>')
    for x, y, rot, c in [(500, 92, -6, "#7fb2d8"), (640, 118, 5, "#9cc07a"), (850, 70, -4, "#e2a35a"), (1010, 108, 7, "#8fa6c4")]:
        o.append(f'<g transform="rotate({rot} {x + 50} {y + 45})"><rect x="{x}" y="{y}" width="100" height="92" fill="#fff"/><rect x="{x + 7}" y="{y + 7}" width="86" height="64" fill="{c}"/>'
                 f'<path d="M{x + 7} {y + 71} L{x + 40} {y + 28} L{x + 58} {y + 50} L{x + 70} {y + 38} L{x + 93} {y + 71}Z" fill="#4a5a6e"/><path d="M{x + 40} {y + 28} L{x + 32} {y + 40} L{x + 48} {y + 40}Z" fill="#fff"/>'
                 f'<circle cx="{x + 50}" cy="{y + 4}" r="5" fill="#c2452a"/></g>')
    o.append('<path d="M1100 180 q20 -30 40 -10 q-10 20 -40 10z" fill="#c26a2a"/><line x1="1100" y1="180" x2="1150" y2="160" stroke="#7a3a1a" stroke-width="2"/>')
    o.append('<path d="M1200 40 L1220 230" stroke="#c2452a" stroke-width="10"/>')
    if n: o.append('<circle cx="800" cy="120" r="420" fill="url(#glow)" opacity=".5"/>')
    o.append(f'<rect x="0" y="190" width="420" height="50" fill="{wd2}" opacity=".6"/><rect x="1180" y="190" width="420" height="50" fill="{wd2}" opacity=".6"/>')
    return vwrap(''.join(o))

def v_training(n):  # base camp, tents and a ropes course
    p = P(n); o = [base(n)]
    o.append(moon(260, 50, 20) if n else sun(260, 50, 20))
    o.append(peak(1000, 14, 700, 1300, 170, p, .32, 11)); o.append(peak(720, 54, 480, 960, 170, p, .3, 12)); o.append(peak(1300, 50, 1080, 1560, 170, p, .3, 13))
    o.append(forest(0, 1610, 176, 30, 60, p["pine2"], 9, 22))
    o.append(f'<rect x="0" y="170" width="1600" height="70" fill="{p["meadow"]}"/>')
    lc = p["wood2"]
    o.append(f'<rect x="980" y="110" width="10" height="100" fill="{lc}"/><rect x="1150" y="100" width="10" height="110" fill="{lc}"/><rect x="1320" y="116" width="10" height="94" fill="{lc}"/>')
    o.append('<path d="M985 120 Q1070 140 1155 110 M1155 110 Q1240 136 1325 124" stroke="#e8c23a" stroke-width="3" fill="none"/><path d="M985 160 L1155 150 L1325 162" stroke="#d8cfb8" stroke-width="5" fill="none"/>')
    o.append(hiker(1100, 152, .7, "#e2552b", "#2f6a4a", stick=False))
    door = "#ffcf6a" if n else "#3a2a1a"
    o.append(tent(560, 214, 130, 80, "#e2552b", door)); o.append(tent(700, 208, 110, 66, "#f2b230", door)); o.append(tent(820, 214, 120, 74, "#3a8a5a", door))
    o.append(fire(640, 226, .7, n))
    o.append('<path d="M480 120 L480 214" stroke="#ddd" stroke-width="3"/><path d="M482 122 l36 10 l-36 10z" fill="#c2452a"/>')
    o.append(f'<rect x="0" y="210" width="1600" height="30" fill="{p["pine2"]}" opacity=".7"/>')
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the topographic trail map
    paper = "#efe6cc" if not n else "#151d2c"; ink = "#5a4a30" if not n else "#cbd6e8"; topo = "#b8a272" if not n else "#3e4c66"
    route = ("#2f7d4a" if not n else "#5cc98a") if athena else ("#b5452a" if not n else "#ff8a5c")
    o = [f'<rect width="1600" height="{V}" fill="{paper}"/>']
    for cx, cy, k0, seed in [(300, 100, 6, 1), (1000, 150, 7, 2), (1450, 60, 5, 3), (700, 40, 4, 4)]:
        r = random.Random(seed)
        for k in range(k0):
            rx = 30 + k * 26; ry = 18 + k * 15
            pts = []
            for i in range(18):
                ang = i / 18 * 2 * math.pi; j = 1 + r.uniform(-.12, .12)
                pts.append((cx + rx * j * math.cos(ang), cy + ry * j * math.sin(ang)))
            o.append('<path d="M' + 'L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + f'Z" fill="none" stroke="{topo}" stroke-width="{2 if k % 3 == 0 else 1.2}"/>')
    o.append(f'<path d="M0 200 Q300 170 600 210 T1200 180 T1600 200" fill="none" stroke="{"#7fb2d8" if not n else "#3e6a9a"}" stroke-width="5"/>')
    for x, y in [(300, 100), (1000, 150), (1450, 60)]: o.append(f'<path d="M{x - 10} {y + 8} L{x} {y - 10} L{x + 10} {y + 8}Z" fill="{ink}"/>')
    pts = [(470, 150), (690, 70), (960, 120), (1230, 52)]
    d = f'M380 196 C420 176 440 160 {pts[0][0]} {pts[0][1]} S620 60 {pts[1][0]} {pts[1][1]} S880 140 {pts[2][0]} {pts[2][1]} S1160 50 {pts[3][0]} {pts[3][1]} S1300 30 1330 40'
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="5" stroke-dasharray="3 11" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        ty = y - 22 if i % 2 == 0 else y + 38
        o.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{route}" stroke="{paper}" stroke-width="4"/><text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="{paper}">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="{ink}" stroke="{paper}" stroke-width="5" paint-order="stroke">{t}</text>')
    o.append(f'<g transform="translate(1440 150)"><circle r="34" fill="none" stroke="{ink}" stroke-width="2"/><path d="M0 -30 L7 0 L0 30 L-7 0Z" fill="{ink}"/><path d="M0 -30 L7 0 L-7 0Z" fill="{route}"/><text y="-38" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{ink}">N</text></g>')
    o.append(f'<rect x="0" y="0" width="1600" height="{V}" fill="none" stroke="{ink}" stroke-width="8" opacity=".35"/>')
    o.append(f'<rect x="0" y="186" width="440" height="54" fill="{"#3e3222" if not n else "#0a0f18"}" opacity=".35"/><rect x="1060" y="196" width="540" height="44" fill="{"#3e3222" if not n else "#0a0f18"}" opacity=".35"/>')
    return vwrap(''.join(o))

def v_service(n):  # the ranger cabin, woodpile and smoke
    p = P(n); o = [base(n, sky=("#5f97c9", "#a8d0ea", "#efe6d2"))]
    o.append(moon(1260, 56, 20) if n else sun(1260, 56, 20))
    o.append(peak(560, 30, 260, 880, 190, p, .3, 21)); o.append(peak(1050, 60, 800, 1320, 190, p, .3, 22))
    o.append(forest(0, 1610, 200, 40, 90, p["pine2"], 10, 26))
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{p["meadow2"]}"/>')
    cx, cb = 800, 206
    o.append(f'<rect x="{cx + 54}" y="{cb - 140}" width="22" height="60" fill="{"#8a8378" if not n else "#3a3a44"}"/>' + smoke(cx + 64, cb - 152, 5, .6 if not n else .3, "#f2f4f6" if not n else "#9aa4b8"))
    o.append(f'<rect x="{cx - 120}" y="{cb - 84}" width="240" height="84" fill="{p["log"]}"/>')
    for y in range(cb - 76, cb, 12): o.append(f'<line x1="{cx - 120}" y1="{y}" x2="{cx + 120}" y2="{y}" stroke="{p["wood2"]}" stroke-width="2" opacity=".6"/>')
    o.append(f'<path d="M{cx - 146} {cb - 80} L{cx} {cb - 156} L{cx + 146} {cb - 80}Z" fill="{"#4a3424" if not n else "#241912"}"/><path d="M{cx - 124} {cb - 80} L{cx} {cb - 138} L{cx + 124} {cb - 80}Z" fill="{p["log"]}"/>')
    o.append(f'<rect x="{cx - 16}" y="{cb - 52}" width="32" height="52" fill="{p["wood2"]}"/>')
    for wx in (cx - 92, cx + 50):
        if n: o.append(f'<circle cx="{wx + 21}" cy="{cb - 40}" r="46" fill="url(#glow)"/>')
        o.append(f'<rect x="{wx}" y="{cb - 58}" width="42" height="32" fill="{p["win"]}" stroke="{p["wood2"]}" stroke-width="4"/>')
    o.append(f'<text x="{cx}" y="{cb - 98}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="15" fill="{p["ink"]}" letter-spacing="2">RANGER STATION</text>')
    for i in range(12): o.append(f'<circle cx="{cx + 150 + (i % 6) * 15 + (i // 6) * 7}" cy="{cb - 8 - (i // 6) * 14}" r="7.5" fill="{p["log"]}" stroke="{p["wood2"]}" stroke-width="2"/>')
    o.append(f'<rect x="{cx - 220}" y="{cb - 20}" width="30" height="20" fill="{p["wood2"]}"/><path d="M{cx - 205} {cb - 20} L{cx - 196} {cb - 52}" stroke="#7a7a80" stroke-width="4"/>')
    o.append(f'<rect x="1200" y="150" width="6" height="56" fill="#ddd"/><path d="M1206 152 l40 8 l-40 8z" fill="#2f7d4a"/>')
    return vwrap(''.join(o))

def v_renewals(n):  # the spring thaw
    p = P(n); o = [base(n, sky=("#6aa6d8", "#b8dcf0", "#f2f3dc"))]
    o.append(moon(1340, 56, 20) if n else sun(1340, 56, 20))
    pp = dict(p);
    o.append(peak(820, 24, 500, 1140, 160, pp, .18, 31)); o.append(peak(1200, 60, 980, 1440, 160, pp, .16, 32))
    # snow patches melting low down
    for x, y, w in [(640, 140, 60), (980, 132, 50), (1300, 150, 40)]: o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="{p["snow"]}" opacity=".85"/>')
    o.append(forest(0, 1610, 168, 30, 64, p["pine2"], 12, 30))
    o.append(f'<rect x="0" y="164" width="1600" height="76" fill="{"#8cbc66" if not n else p["meadow"]}"/>')
    o.append(f'<path d="M760 164 Q820 180 780 196 Q700 214 820 240 L900 240 Q790 214 860 196 Q900 180 800 164Z" fill="{p["lake"]}"/>')
    o.append('<path d="M800 180 q10 4 0 8 M810 214 q14 6 0 10" stroke="#fff" stroke-opacity=".6" stroke-width="2" fill="none"/>')
    r = random.Random(5)
    for _ in range(70):
        x = r.randint(420, 1240); y = r.randint(176, 236)
        if 740 < x < 900: continue
        c = r.choice(["#f2d14a", "#e86a8a", "#9b7fe0", "#ffffff", "#f28a3a"])
        o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 8}" stroke="#4a7a3a" stroke-width="2"/><circle cx="{x}" cy="{y}" r="{r.choice([3, 4, 5])}" fill="{c}" opacity="{.9 if not n else .6}"/>')
    o.append(bird(1000, 70, 1, "#3a4a5a" if not n else "#cfd8e8"))
    o.append(f'<rect x="0" y="200" width="420" height="40" fill="{p["pine2"]}" opacity=".7"/><rect x="1030" y="200" width="570" height="40" fill="{p["pine2"]}" opacity=".8"/>')
    return vwrap(''.join(o))

def v_claims(n):  # after the storm: a fallen tree across the trail, a crew with a saw
    p = P(n)
    o = [base(n, sky=("#5a6a80", "#9cb4cc", "#e8e4d4"), nt=("#060a16", "#111a30", "#2a3450"))]
    if n: o.append(moon(1180, 54, 20))
    else: o.append('<path d="M1050 0 L1250 0 L1500 240 L1160 240Z" fill="#fff6d0" opacity=".22"/>' + sun(1150, 30, 18))
    for x, y, w in [(200, 40, 300), (520, 30, 260), (1450, 46, 240)]:
        cc = "#7a8494" if not n else "#2a3248"
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="26" fill="{cc}"/><ellipse cx="{x + 40}" cy="{y - 16}" rx="{w // 3}" ry="22" fill="{cc}"/>')
    o.append(ridge([(0, 150), (300, 110), (600, 140), (900, 96), (1200, 130), (1600, 104)], V, p["far"]))
    o.append(forest(0, 1610, 186, 50, 100, p["pine"], 13, 32))
    o.append(f'<rect x="0" y="180" width="1600" height="60" fill="{p["meadow2"]}"/><path d="M640 240 L740 180 L860 180 L960 240Z" fill="{p["trail"]}"/>')
    o.append(f'<ellipse cx="700" cy="226" rx="40" ry="5" fill="{"#a9cbe0" if not n else "#3e5a80"}"/>')
    # the fallen tree
    o.append(f'<path d="M520 196 L1060 170 L1062 186 L522 214Z" fill="{p["log"]}"/><circle cx="1061" cy="178" r="10" fill="#d8b47a" stroke="{p["wood2"]}" stroke-width="3"/>')
    o.append(f'<path d="M500 190 L470 160 L440 196 L470 210Z" fill="{p["wood2"]}"/>' + pine(470, 220, 70, p["pine"]).replace('<path', '<path transform="rotate(-80 470 200)"'))
    o.append('<path d="M810 152 L870 150" stroke="#b8bcc4" stroke-width="5"/><path d="M812 154 l4 5 l4 -5 l4 5 l4 -5 l4 5 l4 -5 l4 5 l4 -5 l4 5 l4 -5 l4 5 l4 -5" stroke="#8a8e96" stroke-width="2" fill="none"/>')
    o.append(hiker(790, 176, .8, "#f2b230", "#c2452a", stick=False)); o.append(hiker(900, 174, .8, "#f2b230", "#2f6a4a", flip=True, stick=False))
    o.append(f'<rect x="0" y="210" width="440" height="30" fill="{p["pine2"]}" opacity=".6"/><rect x="1030" y="204" width="570" height="36" fill="{p["pine2"]}" opacity=".7"/>')
    return vwrap(''.join(o))

def v_commercial(n):  # the grand old lodge
    p = P(n); o = [base(n, sky=("#4f8ac4", "#a8d0ea", "#f2e2c4"))]
    o.append(moon(1400, 50, 20) if n else sun(1400, 50, 20))
    o.append(peak(300, 30, 0, 640, 180, p, .3, 41)); o.append(peak(1250, 40, 960, 1600, 180, p, .3, 42))
    o.append(forest(0, 1610, 190, 40, 80, p["pine2"], 14, 26))
    o.append(f'<rect x="0" y="190" width="1600" height="50" fill="{p["meadow2"]}"/>')
    st = "#8a8378" if not n else "#3a3a44"; st2 = "#6a645a" if not n else "#2a2a32"; rf = "#3a5a40" if not n else "#18261c"
    o.append(f'<rect x="460" y="170" width="680" height="40" fill="{st}"/>')
    for x in range(470, 1130, 34): o.append(f'<rect x="{x}" y="{176 + (x // 34) % 2 * 14}" width="26" height="10" rx="3" fill="{st2}"/>')
    o.append(f'<rect x="480" y="90" width="640" height="80" fill="{p["log"]}"/>')
    o.append(f'<path d="M450 96 L560 46 L1040 46 L1150 96Z" fill="{rf}"/>')
    for gx, gw, gy in [(800, 150, 6), (560, 90, 40), (1040, 90, 40)]:
        o.append(f'<path d="M{gx - gw} {96 if gx != 800 else 100} L{gx} {gy} L{gx + gw} {96 if gx != 800 else 100}Z" fill="{rf}"/><path d="M{gx - gw * .7:.0f} 96 L{gx} {gy + 26} L{gx + gw * .7:.0f} 96Z" fill="{p["log"]}"/>')
    o.append(f'<rect x="690" y="60" width="16" height="40" fill="{st}"/><rect x="900" y="56" width="16" height="44" fill="{st}"/>')
    o.append(smoke(698, 50, 4, .5 if not n else .25, "#eef1f3" if not n else "#9aa4b8"))
    for x in list(range(500, 760, 44)) + list(range(860, 1110, 44)):
        if n: o.append(f'<circle cx="{x + 13}" cy="132" r="26" fill="url(#glow)"/>')
        o.append(f'<rect x="{x}" y="112" width="26" height="36" fill="{p["win"]}" stroke="{p["wood2"]}" stroke-width="3"/>')
    o.append(f'<rect x="770" y="128" width="60" height="62" fill="{p["wood2"]}"/><path d="M760 128 L800 104 L840 128Z" fill="{rf}"/>')
    o.append(f'<rect x="700" y="72" width="200" height="22" rx="3" fill="{p["wood2"]}"/><text x="800" y="89" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="16" fill="{p["ink"]}" letter-spacing="3">SUMMIT LODGE</text>')
    o.append(f'<line x1="800" y1="6" x2="800" y2="-30" stroke="#ccc" stroke-width="3"/>')
    o.append(f'<rect x="1188" y="60" width="5" height="130" fill="#ccc"/><path d="M1193 62 l50 10 l-50 10z" fill="#8f5be8"/>')
    o.append(f'<rect x="0" y="206" width="440" height="34" fill="{p["pine2"]}" opacity=".6"/><rect x="1160" y="206" width="440" height="34" fill="{p["pine2"]}" opacity=".6"/>')
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the falls: premium running full"],
    "messages": ["Texts & Emails", "the lookout: every signal answered"],
    "coaching": ["Coaching", "the trailhead board: every call, mapped"],
    "roleplay": ["Role Play", "the climbing wall: practice on the rope"],
    "rphistory": ["Session History", "the trail journal: every climb, written down"],
    "training": ["Training", "base camp: learn the ropes"],
    "blueprint": ["Apollo's Road Map", "the trail map, in plain words"],
    "athenamap": ["Athena's Road Map", "the service trail, in plain words"],
    "service": ["Service Digest", "the ranger station: keeping the book"],
    "renewals": ["Renewals", "the spring thaw: what came back"],
    "claims": ["Claims", "the trail crew: after the storm"],
    "commercial": ["Commercial Center", "the grand lodge: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=40):
    return defs(skyg(1, n, day=day, nt=nt) + '<radialGradient id="sb" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2b0" stop-opacity=".8"/><stop offset="1" stop-color="#fff2b0" stop-opacity="0"/></radialGradient>') + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 100, 21) if n else '')

def cap(t, c="#fff"):
    return f'<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="26" fill="{c}" stroke="#000" stroke-opacity=".35" stroke-width="4" paint-order="stroke" letter-spacing="2">{t}</text>'

def s_sold(n):  # SUMMIT: a flag on the peak, sunburst
    p = P(n); o = [sbase(n, ("#d9822b", "#f2b85a", "#fde3a0"), ("#0a1030", "#1a2858", "#3a3a6a"))]
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        o.append(f'<path d="M760 74 L{760 + 700 * math.cos(ang):.0f} {74 + 700 * math.sin(ang):.0f} L{760 + 700 * math.cos(ang + .12):.0f} {74 + 700 * math.sin(ang + .12):.0f}Z" fill="#fff" opacity="{.18 if not n else .08}"/>')
    o.append('<circle cx="760" cy="74" r="120" fill="url(#sb)"/>')
    o.append(peak(760, 82, 520, 1000, 180, p, .3, 51))
    o.append('<line x1="760" y1="84" x2="760" y2="44" stroke="#3a2a1a" stroke-width="4"/><path d="M762 46 L806 55 L762 64Z" fill="#c2452a"/>')
    o.append(ridge([(0, 130), (300, 110), (460, 140)], S, p["far"])); o.append(ridge([(1060, 140), (1300, 112), (1600, 130)], S, p["far"]))
    r = random.Random(5)
    for _ in range(26): o.append(f'<rect x="{r.randint(420, 1120)}" y="{r.randint(20, 120)}" width="6" height="10" fill="{r.choice(["#ffd27a", "#5ec97a", "#e2552b", "#7fb2e8"])}" transform="rotate({r.randint(0, 90)} {r.randint(420, 1120)} 70)"/>')
    o.append(cap("SUMMIT"))
    return wrap(S, ''.join(o))

def s_open(n):  # STILL CLIMBING: a switchback trail, a hiker partway
    p = P(n); o = [sbase(n, ("#4f8ac4", "#9cc8e6", "#e6efe2"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(peak(980, 10, 560, 1400, 170, p, .22, 52))
    o.append('<path d="M640 150 L900 132 L700 112 L960 92 L780 74 L980 54" fill="none" stroke="' + p["trail"] + '" stroke-width="5" stroke-linejoin="round" stroke-dasharray="10 6"/>')
    o.append(hiker(836, 103, .62, "#e2552b", "#2f6a4a"))
    o.append(forest(380, 640, 160, 40, 80, p["pine"], 15, 26))
    o.append(cap("STILL CLIMBING"))
    return wrap(S, ''.join(o))

def s_lost(n):  # TRAIL WASHED OUT: grey, a broken bridge
    p = P(n); o = [sbase(n, ("#6a6e78", "#9a9ea6", "#c4c6ca"), ("#0a0c14", "#1a1d28", "#2a2d3a"), 10)]
    for x in (300, 700, 1150): o.append(f'<ellipse cx="{x}" cy="30" rx="200" ry="22" fill="{"#7a7e88" if not n else "#20232e"}"/>')
    o.append(f'<path d="M0 100 L560 92 L590 160 L0 160Z M1600 100 L960 92 L930 160 L1600 160Z" fill="{"#6a6560" if not n else "#252630"}"/>')
    o.append(f'<path d="M572 126 L948 126 L940 160 L580 160Z" fill="{"#7f97a8" if not n else "#26344a"}"/>')
    for x in (650, 760, 860): o.append(f'<path d="M{x} 136 q16 -6 32 0" stroke="#fff" stroke-opacity=".4" stroke-width="2" fill="none"/>')
    bw = "#5a4a3a" if not n else "#3a3028"
    o.append(f'<path d="M560 90 L700 84 L708 92 L560 100Z" fill="{bw}"/><path d="M700 84 L730 120 L722 126 L692 90Z" fill="{bw}"/>')
    o.append(f'<path d="M960 90 L840 84 L834 92 L960 100Z" fill="{bw}"/><path d="M840 84 L812 112 L820 118 L846 90Z" fill="{bw}"/>')
    o.append(f'<path d="M600 92 L700 84 M960 92 L840 84" stroke="#3a3028" stroke-width="2"/><path d="M700 84 Q720 110 712 140" fill="none" stroke="#3a3028" stroke-width="2"/>')
    o.append(forest(0, 520, 96, 30, 60, "#4a5050" if not n else "#151a1e", 16, 28))
    o.append(cap("TRAIL WASHED OUT", "#f2f2f2"))
    return wrap(S, ''.join(o))

def s_dead(n):  # TRAIL CLOSED: fog, a barrier sign
    p = P(n); o = [sbase(n, ("#8a8e94", "#b4b8bc", "#d4d6d8"), ("#0c0e14", "#1c1f28", "#30333e"), 6)]
    o.append(forest(380, 1200, 150, 50, 110, "#6a7470" if not n else "#1a2226", 17, 34))
    for y, op in [(70, .55), (100, .6), (130, .5)]: o.append(f'<rect x="0" y="{y}" width="1600" height="24" rx="12" fill="{"#e4e6e8" if not n else "#4a4e5c"}" opacity="{op}"/>')
    o.append('<rect x="680" y="90" width="8" height="60" fill="#4a4a4a"/><rect x="900" y="90" width="8" height="60" fill="#4a4a4a"/>')
    o.append('<rect x="650" y="84" width="290" height="22" fill="#fff"/>')
    for x in range(650, 940, 36): o.append(f'<path d="M{x} 84 L{x + 18} 84 L{x + 6} 106 L{x - 12} 106Z" fill="#d8402a"/>')
    o.append('<rect x="730" y="42" width="130" height="38" rx="4" fill="#c2452a" stroke="#fff" stroke-width="3"/><text x="795" y="68" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#fff">CLOSED</text>')
    o.append(cap("TRAIL CLOSED"))
    return wrap(S, ''.join(o))

def s_reached(n):  # AT THE TRAILHEAD: two hikers chatting at a sign
    p = P(n); o = [sbase(n, ("#5f97c9", "#a8d0ea", "#eef0dc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(peak(1100, 20, 820, 1380, 140, p, .3, 53)); o.append(peak(460, 40, 240, 700, 140, p, .3, 54))
    o.append(forest(0, 1610, 140, 30, 60, p["pine2"], 18, 44))
    o.append(f'<rect x="0" y="130" width="1600" height="30" fill="{p["meadow2"]}"/>')
    o.append(sign(800, 64, 150, 34, "TRAILHEAD", p, 16, 50))
    o.append(hiker(680, 140, .8, "#e2552b", "#2f6a4a")); o.append(hiker(920, 140, .8, "#4a7fd0", "#c2452a", flip=True))
    o.append('<g transform="translate(0 14)"><path d="M700 50 q8 -14 24 -14 h20 q16 0 16 14 q0 12 -16 12 h-24 l-10 8z" fill="#fff" opacity=".92"/><path d="M900 44 q-8 -14 -24 -14 h-20 q-16 0 -16 14 q0 12 16 12 h24 l10 8z" fill="#fff" opacity=".92"/>')
    for x in (716, 730, 744): o.append(f'<circle cx="{x}" cy="49" r="2.6" fill="#5a4a3a"/>')
    for x in (856, 870, 884): o.append(f'<circle cx="{x}" cy="43" r="2.6" fill="#5a4a3a"/>')
    o.append('</g>')
    o.append(cap("AT THE TRAILHEAD"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # AT BASE CAMP: a tent, resting
    p = P(n); o = [sbase(n, ("#d98a4a", "#f2c27a", "#fbe6b8"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(peak(980, 20, 700, 1260, 140, p, .3, 55))
    o.append(forest(0, 1610, 136, 30, 56, p["pine2"], 19, 44))
    o.append(f'<rect x="0" y="126" width="1600" height="34" fill="{p["meadow2"]}"/>')
    o.append(tent(700, 130, 150, 84, "#e2552b", "#ffcf6a" if n else "#3a2a1a"))
    o.append(fire(860, 130, .7, n))
    o.append(f'<rect x="900" y="118" width="70" height="14" rx="7" fill="{p["log"]}"/><g transform="translate(936 116) rotate(-12)"><rect x="-26" y="-14" width="40" height="14" rx="6" fill="#4a7fd0"/><circle cx="20" cy="-10" r="8" fill="#e3b48c"/><path d="M12 -14 h18 l-3 -6 h-12z" fill="#6a4426"/></g>')
    o.append('<text x="980" y="78" font-family="Georgia, serif" font-weight="bold" font-size="18" fill="#fff" opacity=".85">~</text>')
    o.append(cap("AT BASE CAMP"))
    return wrap(S, ''.join(o))

def s_vm(n):  # HIBERNATING: a bear asleep in its den, moon
    o = [sbase(n, ("#2a3a6a", "#4a5a8a", "#7a7aa0"), ("#04060f", "#0a0f24", "#141a38"), 60)]
    if not n: o.append(stars(30, 0, 1600, 0, 90, 22))
    o.append(moon(560, 62, 20))
    rk = "#5a5a6a" if not n else "#2a2c3a"
    o.append('<g transform="translate(0 -30)">')
    o.append(f'<path d="M640 160 Q660 40 820 30 Q980 40 1000 160Z" fill="{rk}"/><path d="M700 160 Q720 76 820 72 Q920 76 940 160Z" fill="#141420"/>')
    o.append(f'<path d="M640 160 Q620 140 600 160Z M0 150 L1600 150 L1600 190 L0 190Z" fill="{"#e6ecf4" if not n else "#8a96b0"}"/>')
    o.append('<ellipse cx="820" cy="134" rx="76" ry="26" fill="#6a4426"/><circle cx="884" cy="128" r="20" fill="#6a4426"/><circle cx="876" cy="110" r="7" fill="#6a4426"/><ellipse cx="900" cy="134" rx="9" ry="7" fill="#a8784a"/><circle cx="906" cy="132" r="3" fill="#1a1a1a"/><path d="M878 124 q5 4 10 0" stroke="#1a1a1a" stroke-width="2.4" fill="none"/>')
    o.append('<text x="930" y="96" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="#ffd27a">z</text><text x="950" y="80" font-family="Arial, sans-serif" font-weight="bold" font-size="24" fill="#ffd27a">z</text><text x="976" y="60" font-family="Arial, sans-serif" font-weight="bold" font-size="30" fill="#ffd27a">z</text>')
    o.append('</g>')
    o.append(pine(1100, 126, 90, "#1a2c30") + pine(1160, 126, 70, "#1a2c30") + pine(500, 126, 80, "#1a2c30"))
    o.append(cap("HIBERNATING"))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}
# The header's greetings in this world only (Frank, 2026-10-05: "world themed ones that appear only in those worlds"); {n} is the first name.
GREETINGS = ['Summit day, {n}.', "Lace up, {n}. Trail's open.", 'One switchback at a time, {n}.', "The view's better from the top of the board, {n}.", 'Fresh air, fresh leads, {n}.', 'Base camp is ready, {n}.', 'Climb on, {n}.', 'Pack light, quote heavy, {n}.', 'The peak is just past the next call, {n}.', "Trail's clear, {n}. Let's hike.", 'Every summit starts with one step, {n}.', 'Altitude, attitude, {n}.', 'Pine trees and premiums, {n}.', 'Keep climbing, {n}.', "Rope up, {n}. Let's go."]

"""The Dinosaurs world: one lush prehistoric valley at golden hour. Colour looks, fonts, the Digest picture,
page banners, card strips. Every creature is friendly: round eyes, a smile, nobody hunting anybody."""
import random, math

KEY = "dinosaurs"
NAME = "Dinosaurs"
CATEGORY = "Fun"   # the group it is listed under in Settings
FONTS = "family=Fredoka:wght@500;600;700&family=Nunito:wght@400;500;600;700"
DISPLAY = "'Fredoka', 'Trebuchet MS', sans-serif"
DW = 700
BODY = "'Nunito', system-ui, sans-serif"
SKY_BG = (("#f0c07c", "#86ad58"), ("#0a1028", "#15281f"))

LOOKS = [
    ("fern", "Fern",
     "--surface: #edefe2; --surface-raised: #fbfcf5; --card2: #f2f4e8; --chip: #e2e7d3; --text-primary: #1a2618; --text-muted: #566152; --text-secondary: #404c3c; --grid: #e1e6d4; --border: #d6dcc6; --border-strong: #b6c0a2; --accent: #2e6b30; --accent-d: #1f5022; --side: #1f3a22; --side2: #2a4a2d; --sideInk: #e2eddc; --brand: #f4f6ea; --brand2: #f0c27a; --rad: 16px;",
     "--surface: #0e140e; --surface-raised: #151e15; --card2: #1b261b; --chip: #223022; --text-primary: #e5eedf; --text-muted: #9db098; --text-secondary: #b8c7b2; --grid: #223022; --border: #25342a; --border-strong: #344a36; --accent: #8fd06a; --accent-d: #b0e094; --side: #090f09; --side2: #132013; --sideInk: #e2eddc; --brand: #f4f6ea; --brand2: #f0c27a;",
     ["#edefe2", "#1f3a22", "#f0c27a"]),
    ("lava", "Lava",
     "--surface: #f1e9e4; --surface-raised: #fdf8f5; --card2: #f6eeea; --chip: #ebdfd8; --text-primary: #241a18; --text-muted: #67554f; --text-secondary: #4f3f3a; --grid: #e9ddd6; --border: #e0d2ca; --border-strong: #c6afa3; --accent: #b0301e; --accent-d: #8a2414; --side: #2a2224; --side2: #3a2e30; --sideInk: #efe2dc; --brand: #f6eee9; --brand2: #ff8a4a; --rad: 14px;",
     "--surface: #141010; --surface-raised: #1c1716; --card2: #241d1c; --chip: #2e2524; --text-primary: #f1e6e2; --text-muted: #b3a29c; --text-secondary: #cbbcb6; --grid: #2e2524; --border: #322827; --border-strong: #463836; --accent: #ff7a4a; --accent-d: #ffa07c; --side: #0d0a0a; --side2: #1c1515; --sideInk: #efe2dc; --brand: #f6eee9; --brand2: #ff8a4a;",
     ["#f1e9e4", "#2a2224", "#e2552b"]),
    ("amber", "Amber",
     "--surface: #f3ead6; --surface-raised: #fdf8ec; --card2: #f7efdc; --chip: #ede0c2; --text-primary: #2a1f12; --text-muted: #6a5a42; --text-secondary: #52432e; --grid: #e9ddc2; --border: #e2d4b6; --border-strong: #c8b388; --accent: #8a5410; --accent-d: #6a3f0a; --side: #3a2814; --side2: #4a341c; --sideInk: #f2e6cf; --brand: #f8efdc; --brand2: #f5b83a; --rad: 18px;",
     "--surface: #15110a; --surface-raised: #1d1810; --card2: #251e14; --chip: #2e261a; --text-primary: #f2e9d8; --text-muted: #b2a387; --text-secondary: #cabca2; --grid: #2e261a; --border: #31291c; --border-strong: #463a28; --accent: #f5b83a; --accent-d: #f8cd6e; --side: #0e0b06; --side2: #1c160d; --sideInk: #f2e6cf; --brand: #f8efdc; --brand2: #f5b83a;",
     ["#f3ead6", "#3a2814", "#f5b83a"]),
]

TOUR = {"k": "Field journal", "next": "Next fossil", "back": "Back", "done": "Roar!", "skip": "Back to camp"}

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(far="#252b4a", far2="#1e2440", volc="#2a2238", volc2="#211b2e", jung="#10241f", jung2="#0c1c18",
                    ground="#182c22", ground2="#14261d", leaf="#11281e", leaf2="#0b1c15", trunk="#2a1c16",
                    rock="#4a3a46", rock2="#3a2e38", rock3="#2c232b", ledge="#55404c", ledge2="#3e2e3a", ledge3="#4a3844",
                    trail="#3e3640", water="#16294c", water2="#3d5e90", foam="#9fb6d8",
                    sau="#3d6262", sau2="#2e4c4c", saub="#55786e", tri="#73503e", tri2="#5a3c2e", frill="#743e3e", horn="#c2b6a2",
                    thr="#30566c", thr2="#244458", thrb="#557684", pte="#6a4048", pte2="#523038",
                    egg="#d4ccb8", egg2="#a8b4a6", nest="#3e2a1c", nest2="#2c1c12", eye="#e8e8e2", pup="#141414",
                    blush="#c06a6a", lava="#ff6a22", lava2="#ffc64a", ink="#e8dcc4", stone="#55545a", stone2="#3e3d44",
                    flower="#9a6a86", smoke="#4a4658")
    return dict(far="#c39a9a", far2="#ae8a92", volc="#8b6a74", volc2="#735864", jung="#4f7d48", jung2="#3f6c3c",
                ground="#8ab45a", ground2="#7aa44c", leaf="#3e7a3a", leaf2="#2c602e", trunk="#7a5232",
                rock="#dca46e", rock2="#c28758", rock3="#a46c44", ledge="#e4aa7c", ledge2="#bd7c50", ledge3="#d2966a",
                trail="#e8cf98", water="#5aa6cc", water2="#b0e0f2", foam="#ffffff",
                sau="#7cb48c", sau2="#5e9672", saub="#c2e0b0", tri="#e39c56", tri2="#c47c3e", frill="#cc624c", horn="#f8eed6",
                thr="#5aa6c4", thr2="#3f88a6", thrb="#c4e6ee", pte="#d0745c", pte2="#ac584a",
                egg="#f8efd8", egg2="#9cc6a2", nest="#8a5a32", nest2="#6a4222", eye="#ffffff", pup="#2a2a2a",
                blush="#f2867a", lava="#ff7a2a", lava2="#ffd05a", ink="#fbf2d8", stone="#a8a296", stone2="#8a8478",
                flower="#f2a2c0", smoke="#efe6dc")

DAYSKY = ("#6c9ec8", "#f4c27c", "#fbe0a6")
NIGHTSKY = ("#050a1c", "#13204a", "#2c3a66")

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb04a" stop-opacity=".7"/><stop offset="1" stop-color="#ff7a2a" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="ff" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#f6ff9a" stop-opacity=".95"/><stop offset="1" stop-color="#d8ff5a" stop-opacity="0"/></radialGradient>'
            + extra + '</defs>')

def skyg(n, day=DAYSKY, nt=NIGHTSKY, id="g"):
    c = nt if n else day
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/><stop offset=".6" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

def stars(k, x0, x1, y0, y1, seed, op=(0.35, 0.55, 0.85)):
    r = random.Random(seed); o = []
    for _ in range(k):
        o.append(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([0.7, 1, 1.3, 1.8])}" fill="#fff" opacity="{r.choice(op)}"/>')
    return ''.join(o)

def moon(x, y, r, glow=True):
    g = f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#f3ecd2" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.8}" fill="#f3ecd2" opacity=".12"/>' if glow else ''
    return g + (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6efd8"/><circle cx="{x - r * .32:.0f}" cy="{y - r * .22:.0f}" r="{r * .2:.0f}" fill="#e2d9bc"/>'
                f'<circle cx="{x + r * .3:.0f}" cy="{y + r * .32:.0f}" r="{r * .13:.0f}" fill="#e2d9bc"/><circle cx="{x + r * .36:.0f}" cy="{y - r * .3:.0f}" r="{r * .09:.0f}" fill="#e2d9bc"/>')

def sun(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r * 2.8}" fill="#fff0c0" opacity=".22"/><circle cx="{x}" cy="{y}" r="{r * 1.7}" fill="#fff0c0" opacity=".35"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fff4d2"/>'

def cloud(x, y, w, op=.5, c="#fff"):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="9" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .12:.0f}" cy="{y - 8}" rx="{w * .28:.0f}" ry="9" fill="{c}" opacity="{op * .85:.2f}"/>')

def hills(pts, b, c):
    d = f'M{pts[0][0]} {b} L{pts[0][0]} {pts[0][1]}'
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2; my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f' Q{pts[i][0]} {pts[i][1]} {mx:.0f} {my:.0f}'
    d += f' L{pts[-1][0]} {pts[-1][1]} L{pts[-1][0]} {b}Z'
    return f'<path d="{d}" fill="{c}"/>'

def canopy(x0, x1, b, rmin, rmax, c, seed, step=34):
    r = random.Random(seed); o = []; x = x0
    while x < x1:
        rr = r.randint(rmin, rmax); o.append(f'<circle cx="{x}" cy="{b - rr * .6:.0f}" r="{rr}" fill="{c}"/>'); x += r.randint(step - 10, step + 10)
    return f'<rect x="{x0}" y="{b - rmin}" width="{x1 - x0}" height="{rmin + 2}" fill="{c}"/>' + ''.join(o)

# ---- movement. SMIL, which plays inside a background picture; build.py also writes a still copy (every
# <animate*> taken out) for Settings > Motion > Reduced, so each element's own attributes are its resting state.
def show(times, vals, dur, attr="opacity", begin=0):
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s" begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>')
def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="0 {x} {b};{deg} {x} {b};0 {x} {b};{-deg} {x} {b};0 {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>')
SP2 = ".45 0 .55 1;.45 0 .55 1"
def bob(dy, dur, delay=0, dx=0):
    """a step or a peek: out to (dx, -dy) and back"""
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {-dy};0 0" keyTimes="0;.5;1" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines="{SP2}"/>')
def pulse(hi, lo, dur, delay=0, attr="opacity"):
    return (f'<animate attributeName="{attr}" values="{hi};{lo};{hi}" keyTimes="0;.5;1" dur="{dur}s" begin="{delay}s" '
            f'repeatCount="indefinite" calcMode="spline" keySplines="{SP2}"/>')
def rise(x, y, r, c, dx, dy, dur, begin, op=.8):
    """a puff that shows only mid-loop: rises off (x, y) and fades"""
    return (f'<g opacity="0">{puff(x, y, r, c, op)}<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy}" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" keyTimes="0;.3;1" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')
def fireflies(k, x0, x1, y0, y1, seed):
    r = random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="5" fill="url(#ff)" opacity=".9"><animate attributeName="opacity" '
                   f'values=".9;.1;.9" dur="{3 + r.random() * 3:.1f}s" begin="{r.random() * 3:.1f}s" repeatCount="indefinite"/></circle>' for _ in range(k))
def twinkle(seed):
    """a few brighter stars right of the title, blinking in two sets"""
    r = random.Random(seed); o = []
    for i in range(2):
        st = ''.join(f'<circle cx="{r.randint(480, 1580)}" cy="{r.randint(8, 110)}" r="1.8" fill="#fff"/>' for _ in range(3))
        o.append(f'<g>{st}{pulse(1, .2, 4, i * 2)}</g>')
    return ''.join(o)

# ----------------------------------------------------------------- plants
def tube(p0, c1, c2, p3, w0, w1, N=16):
    """a tapering limb (neck, tail) along a cubic spine, as one closed path"""
    L, R = [], []
    for i in range(N + 1):
        t = i / N; m = 1 - t
        x = m ** 3 * p0[0] + 3 * m * m * t * c1[0] + 3 * m * t * t * c2[0] + t ** 3 * p3[0]
        y = m ** 3 * p0[1] + 3 * m * m * t * c1[1] + 3 * m * t * t * c2[1] + t ** 3 * p3[1]
        dx = 3 * m * m * (c1[0] - p0[0]) + 6 * m * t * (c2[0] - c1[0]) + 3 * t * t * (p3[0] - c2[0])
        dy = 3 * m * m * (c1[1] - p0[1]) + 6 * m * t * (c2[1] - c1[1]) + 3 * t * t * (p3[1] - c2[1])
        l = math.hypot(dx, dy) or 1; nx, ny = -dy / l, dx / l; w = (w0 + (w1 - w0) * t) / 2
        L.append(f'{x + nx * w:.0f} {y + ny * w:.0f}'); R.append(f'{x - nx * w:.0f} {y - ny * w:.0f}')
    return 'M' + ' L'.join(L) + ' L' + ' L'.join(reversed(R)) + 'Z'

def frond(x0, y0, ang, L, c, w=16, droop=.35):
    """a fern frond: a curved comb of leaflets on a midrib"""
    a = math.radians(ang)
    x1 = x0 + L * .55 * math.cos(a); y1 = y0 + L * .55 * math.sin(a) - L * .08
    x2 = x0 + L * math.cos(a); y2 = y0 + L * math.sin(a) + L * droop
    d = f'M{x0:.0f} {y0:.0f} Q{x1:.0f} {y1:.0f} {x2:.0f} {y2:.0f}'
    return (f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-dasharray="{w * .28:.1f} {w * .16:.1f}"/>'
            f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{max(2, w * .2):.1f}" stroke-linecap="round"/>')

def treefern(x, b, h, p, c=None, anim=''):
    """a giant tree fern: a slim, slightly bent trunk and a crown of arching fronds"""
    c = c or p["leaf"]; top = b - h
    o = [f'<path d="M{x} {b} Q{x + h * .05:.0f} {b - h * .5:.0f} {x} {top}" fill="none" stroke="{p["trunk"]}" stroke-width="{max(5, h * .045):.0f}" stroke-linecap="round"/>']
    L = h * .36; cr = []
    for ang, k in [(-170, .9), (-145, 1), (-118, .9), (-90, .75), (-62, .9), (-35, 1), (-10, .9), (160, .7), (20, .7)]:
        cr.append(frond(x, top, ang, L * k, c if ang not in (160, 20) else p["leaf2"], max(10, h * .06)))
    o.append(f'<g>{"".join(cr)}{anim}</g>')
    return ''.join(o)

def cycad(x, b, s, p, c=None):
    """a stout cycad: a scaly barrel trunk and a stiff fan of fronds"""
    c = c or p["leaf"]
    o = [f'<g transform="translate({x} {b}) scale({s})">',
         f'<path d="M-14 0 L-12 -40 Q0 -46 12 -40 L14 0Z" fill="{p["trunk"]}"/>',
         f'<path d="M-12 -10 L12 -18 M-12 -22 L12 -30 M-12 -32 L10 -40 M12 -10 L-12 -18 M12 -22 L-12 -30" stroke="{p["nest2"]}" stroke-width="1.6" opacity=".6"/>']
    for ang, L in [(-160, 60), (-135, 70), (-110, 64), (-90, 58), (-70, 64), (-45, 70), (-20, 60)]:
        o.append(frond(0, -40, ang, L, c, 12, .12))
    o.append('</g>')
    return ''.join(o)

def araucaria(x, b, top, p):
    """the tall browse tree: a bare trunk and an umbrella of tiered branches"""
    o = [f'<path d="M{x - 7} {b} L{x - 3} {top + 10} L{x + 3} {top + 10} L{x + 7} {b}Z" fill="{p["trunk"]}"/>']
    tiers = [(0, 60), (30, 100), (62, 124), (94, 112), (124, 84)]
    for i, (dy, w) in enumerate(tiers):
        y = top + dy
        o.append(f'<path d="M{x - w} {y + 6} Q{x - w * .5:.0f} {y + 16} {x} {y + 10} Q{x + w * .5:.0f} {y + 16} {x + w} {y + 6}" fill="none" stroke="{p["trunk"]}" stroke-width="4"/>')
        for k in (-1, 0, 1):
            cx = x + w * k; cy = y + (4 if abs(k) == 1 else 10)
            o.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{30 if abs(k) < 1 else 24}" ry="13" fill="{p["leaf2"] if i % 2 else p["leaf"]}"/>')
        o.append(f'<ellipse cx="{x}" cy="{y + 2}" rx="{w * .7:.0f}" ry="10" fill="{p["leaf"]}"/>')
    return ''.join(o)

def volcano(cx, peak, b, half, p, n, glow=True, halo=True):
    """a broad cone with a notched crater; at night the lava lights it"""
    w = half; cw = 42
    d = (f'M{cx - w} {b} C{cx - w * .55:.0f} {b - (b - peak) * .35:.0f} {cx - cw * 1.6:.0f} {peak + 30} {cx - cw} {peak} '
         f'L{cx - cw * .4:.0f} {peak + 8} L{cx + cw * .2:.0f} {peak + 2} L{cx + cw} {peak - 4} '
         f'C{cx + cw * 1.6:.0f} {peak + 30} {cx + w * .55:.0f} {b - (b - peak) * .35:.0f} {cx + w} {b}Z')
    o = [f'<path d="{d}" fill="{p["volc"]}"/>',
         f'<path d="M{cx + cw * .2:.0f} {peak + 2} L{cx + cw} {peak - 4} C{cx + cw * 1.6:.0f} {peak + 30} {cx + w * .55:.0f} {b - (b - peak) * .35:.0f} {cx + w} {b} L{cx + w * .2:.0f} {b} C{cx + w * .1:.0f} {b - (b - peak) * .4:.0f} {cx + cw * .6:.0f} {peak + 60} {cx + cw * .2:.0f} {peak + 2}Z" fill="{p["volc2"]}"/>']
    if glow:
        o.append(f'<ellipse cx="{cx}" cy="{peak + 2}" rx="{cw * .9:.0f}" ry="7" fill="{p["lava"]}" opacity="{.95 if n else .7}"/>')
        if n and halo:
            o.append(f'<circle cx="{cx}" cy="{peak}" r="{cw * 2.6:.0f}" fill="url(#glow)"/>')
            o.append(f'<path d="M{cx - 8} {peak + 6} Q{cx - 18} {peak + 60} {cx - 40} {peak + 120} Q{cx - 52} {peak + 170} {cx - 70} {peak + 230}" fill="none" stroke="{p["lava"]}" stroke-width="6" stroke-linecap="round"/>'
                     f'<path d="M{cx + 12} {peak + 4} Q{cx + 30} {peak + 70} {cx + 60} {peak + 150}" fill="none" stroke="{p["lava"]}" stroke-width="5" stroke-linecap="round" opacity=".85"/>'
                     f'<path d="M{cx - 8} {peak + 6} Q{cx - 18} {peak + 60} {cx - 40} {peak + 120}" fill="none" stroke="{p["lava2"]}" stroke-width="2" stroke-linecap="round"/>')
    return ''.join(o)

def puff(x, y, r, c, op=.8):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity="{op}"/><circle cx="{x - r * .7:.0f}" cy="{y + r * .3:.0f}" r="{r * .7:.0f}" fill="{c}" opacity="{op}"/>'
            f'<circle cx="{x + r * .75:.0f}" cy="{y + r * .25:.0f}" r="{r * .65:.0f}" fill="{c}" opacity="{op}"/>')

# ----------------------------------------------------------------- the creatures (all face right at scale 1, feet at 0)
def eye(x, y, r, p, look=1):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{p["eye"]}"/><circle cx="{x + r * .3 * look:.1f}" cy="{y}" r="{r * .55:.1f}" fill="{p["pup"]}"/>'
            f'<circle cx="{x + r * .5 * look:.1f}" cy="{y - r * .3:.1f}" r="{r * .2:.1f}" fill="#fff"/>')

def shut_eye(x, y, r, c):
    return f'<path d="M{x - r} {y} Q{x} {y + r * .9:.1f} {x + r} {y}" fill="none" stroke="{c}" stroke-width="{max(1.6, r * .4):.1f}" stroke-linecap="round"/>'

def sauro_head(hx, hy, p, sleep=False, leaf=False):
    c, c2 = p["sau"], p["sau2"]
    o = [f'<ellipse cx="{hx + 8}" cy="{hy}" rx="26" ry="16" fill="{c}"/><ellipse cx="{hx + 28}" cy="{hy + 4}" rx="14" ry="11" fill="{c}"/>',
         f'<circle cx="{hx + 36}" cy="{hy - 1}" r="1.8" fill="{c2}"/>',
         shut_eye(hx + 10, hy - 4, 5, p["pup"]) if sleep else eye(hx + 10, hy - 4, 6, p),
         f'<path d="M{hx + 24} {hy + 8} q8 5 16 -1" fill="none" stroke="{c2}" stroke-width="2.4" stroke-linecap="round"/>',
         f'<circle cx="{hx + 20}" cy="{hy + 6}" r="4" fill="{p["blush"]}" opacity=".45"/>']
    if leaf: o.append(f'<path d="M{hx + 38} {hy + 8} q14 -2 22 8 q-12 4 -22 -8Z M{hx + 40} {hy + 9} q10 8 8 20 q-8 -6 -8 -20Z" fill="{p["leaf"]}"/>')
    return ''.join(o)

def sauropod(x, b, s, p, head=(150, -250), c1=None, c2=None, flip=False, neck_anim='', tail_anim='', leaf=False, sleep=False):
    """a long-necked browser; head is where the head sits in local units, the neck bends to reach it"""
    c, cd, bel = p["sau"], p["sau2"], p["saub"]
    hx, hy = head
    c1 = c1 or (118, -150 + (hy + 112) * .25); c2 = c2 or (hx - 30, hy + 70)
    o = [f'<g transform="translate({x} {b}) scale({-s if flip else s} {s})">',
         f'<rect x="-98" y="-64" width="28" height="64" rx="10" fill="{cd}"/><rect x="42" y="-64" width="28" height="64" rx="10" fill="{cd}"/>',
         f'<g><path d="M-100 -100 C-170 -98 -240 -70 -310 -30 Q-300 -22 -288 -28 C-220 -56 -160 -64 -104 -62Z" fill="{c}"/>{tail_anim}</g>',
         f'<path d="M-118 -80 C-118 -132 -40 -146 20 -142 C84 -138 124 -112 128 -80 C132 -54 108 -46 86 -46 L-92 -46 C-116 -46 -118 -62 -118 -80Z" fill="{c}"/>',
         f'<path d="M-90 -50 C-40 -40 40 -40 92 -50 C70 -66 -70 -66 -90 -50Z" fill="{bel}"/>',
         f'<circle cx="-40" cy="-122" r="9" fill="{cd}" opacity=".55"/><circle cx="-10" cy="-130" r="7" fill="{cd}" opacity=".55"/><circle cx="-70" cy="-108" r="6" fill="{cd}" opacity=".55"/><circle cx="20" cy="-124" r="6" fill="{cd}" opacity=".55"/>',
         f'<rect x="-76" y="-66" width="32" height="66" rx="11" fill="{c}"/><rect x="66" y="-66" width="32" height="66" rx="11" fill="{c}"/>',
         ''.join(f'<ellipse cx="{lx + k * 8}" cy="-2" rx="3" ry="2.4" fill="{p["horn"]}"/>' for lx in (-68, 74) for k in range(3)),
         f'<g><path d="{tube((96, -112), c1, c2, (hx, hy), 52, 24)}" fill="{c}"/>{sauro_head(hx, hy, p, sleep, leaf)}{neck_anim}</g>',
         '</g>']
    return ''.join(o)

def trike(x, b, s, p, flip=False, graze=0, head_anim='', specs=False):
    """the three-horned grazer: frill, two brow horns and a nose horn, a beak and a smile"""
    c, cd, fr, hn = p["tri"], p["tri2"], p["frill"], p["horn"]
    o = [f'<g transform="translate({x} {b}) scale({-s if flip else s} {s})">',
         f'<rect x="-58" y="-34" width="22" height="34" rx="8" fill="{cd}"/><rect x="22" y="-34" width="22" height="34" rx="8" fill="{cd}"/>',
         f'<path d="M-70 -46 Q-112 -40 -130 -22 Q-100 -24 -66 -28Z" fill="{c}"/>',
         f'<ellipse cx="-8" cy="-48" rx="72" ry="36" fill="{c}"/>',
         f'<path d="M-66 -34 Q-8 -14 56 -34 Q-8 -24 -66 -34Z" fill="{cd}" opacity=".35"/>',
         f'<circle cx="-30" cy="-68" r="8" fill="{cd}" opacity=".45"/><circle cx="-2" cy="-74" r="6" fill="{cd}" opacity=".45"/><circle cx="-52" cy="-56" r="5" fill="{cd}" opacity=".45"/>',
         f'<rect x="-44" y="-36" width="26" height="36" rx="9" fill="{c}"/><rect x="34" y="-36" width="26" height="36" rx="9" fill="{c}"/>',
         ''.join(f'<ellipse cx="{lx + k * 7}" cy="-2" rx="2.6" ry="2" fill="{hn}"/>' for lx in (-38, 40) for k in range(3)),
         f'<g transform="rotate({graze} 46 -50)"><g>',
         f'<circle cx="50" cy="-62" r="34" fill="{fr}"/><circle cx="50" cy="-62" r="31" fill="none" stroke="{hn}" stroke-width="5" stroke-dasharray="3 7" opacity=".9"/>',
         f'<path d="M58 -64 Q72 -92 110 -98 Q84 -80 74 -58Z" fill="{cd}"/>',
         f'<ellipse cx="80" cy="-46" rx="30" ry="20" fill="{c}"/>',
         f'<path d="M100 -56 Q122 -46 110 -30 L98 -34Z" fill="{cd}"/>',
         f'<path d="M66 -60 Q82 -90 118 -94 Q92 -76 80 -56Z" fill="{hn}"/>',
         f'<path d="M98 -54 Q104 -68 112 -72 Q110 -60 106 -52Z" fill="{hn}"/>',
         eye(78, -52, 6, p),
         f'<path d="M88 -36 q8 5 16 -2" fill="none" stroke="{cd}" stroke-width="2.4" stroke-linecap="round"/>',
         f'<circle cx="88" cy="-42" r="4" fill="{p["blush"]}" opacity=".45"/>']
    if specs: o.append(f'<circle cx="78" cy="-52" r="9" fill="none" stroke="#3a2a1a" stroke-width="2.4"/><path d="M69 -54 L56 -58" stroke="#3a2a1a" stroke-width="2"/>')
    o.append(f'{head_anim}</g></g></g>')
    return ''.join(o)

def thero(x, b, s, p, flip=False, tail_anim='', pose="stand", c=None, wave=False):
    """the small friendly two-legger: a big round head, big eyes, tiny arms"""
    c = c or p["thr"]; cd = p["thr2"]; bel = p["thrb"]
    o = [f'<g transform="translate({x} {b}) scale({-s if flip else s} {s})">']
    sit = pose == "sit"; dy = 14 if sit else 0
    o.append(f'<g><path d="M-14 {-46 + dy} C-50 {-50 + dy} -84 {-44 + dy} -112 {-26 + dy * .6:.0f} C-84 {-30 + dy} -50 {-28 + dy} -12 {-32 + dy}Z" fill="{c}"/>{tail_anim}</g>')
    if sit:
        o.append(f'<ellipse cx="-2" cy="-6" rx="20" ry="9" fill="{cd}"/><ellipse cx="14" cy="-2" rx="12" ry="4" fill="{cd}"/>')
    else:
        o.append(f'<path d="M-6 -36 L-12 -14 L-6 0" fill="none" stroke="{cd}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/><ellipse cx="-2" cy="-1" rx="9" ry="3.5" fill="{cd}"/>')
    o.append(f'<ellipse cx="0" cy="{-44 + dy}" rx="28" ry="21" fill="{c}"/><ellipse cx="8" cy="{-40 + dy}" rx="16" ry="13" fill="{bel}"/>')
    o.append(f'<path d="M-18 {-58 + dy} q6 -6 10 2 M-4 {-63 + dy} q6 -6 10 2" fill="none" stroke="{cd}" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<path d="M14 {-56 + dy} Q22 {-66 + dy} 24 {-74 + dy} L40 {-70 + dy} Q34 {-56 + dy} 26 {-46 + dy}Z" fill="{c}"/>')
    hy = -82 + dy
    o.append(f'<circle cx="30" cy="{hy}" r="19" fill="{c}"/><ellipse cx="46" cy="{hy + 6}" rx="17" ry="11" fill="{c}"/>')
    if not sit:
        o.append(f'<ellipse cx="-4" cy="-34" rx="13" ry="15" fill="{c}"/><path d="M0 -26 L6 -10 L2 0" fill="none" stroke="{c}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/><ellipse cx="8" cy="-1" rx="9" ry="3.5" fill="{cd}"/>')
    else:
        o.append(f'<ellipse cx="-2" cy="-14" rx="18" ry="12" fill="{c}"/>')
    if wave: o.append(f'<path d="M22 {-48 + dy} Q34 {-58 + dy} 38 {-72 + dy}" fill="none" stroke="{cd}" stroke-width="5" stroke-linecap="round"/>')
    else: o.append(f'<path d="M22 {-48 + dy} Q32 {-46 + dy} 34 {-38 + dy}" fill="none" stroke="{cd}" stroke-width="5" stroke-linecap="round"/>')
    o.append(eye(32, hy - 6, 7, p))
    o.append(f'<path d="M48 {hy + 12} q6 4 13 -1" fill="none" stroke="{cd}" stroke-width="2.5" stroke-linecap="round"/><circle cx="58" cy="{hy + 3}" r="1.6" fill="{cd}"/>')
    o.append(f'<circle cx="42" cy="{hy + 8}" r="4.5" fill="{p["blush"]}" opacity=".45"/></g>')
    return ''.join(o)

def ptero(x, y, s, p, flap=''):
    """a gliding pterosaur: membrane wings out, crest back, beak forward"""
    c, cd = p["pte"], p["pte2"]
    return (f'<g transform="translate({x} {y}) scale({s})"><g><path d="M-4 -2 Q-26 -30 -66 -24 Q-50 -14 -44 -2 Q-26 -8 -6 6Z M4 -2 Q26 -30 66 -24 Q50 -14 44 -2 Q26 -8 6 6Z" fill="{c}"/>'
            f'<path d="M-6 6 Q-26 -8 -44 -2 Q-30 -4 -8 10Z M6 6 Q26 -8 44 -2 Q30 -4 8 10Z" fill="{cd}"/>{flap}</g>'
            f'<ellipse cx="0" cy="2" rx="7" ry="11" fill="{cd}"/>'
            f'<path d="M2 -12 L-16 -22 L0 -6Z" fill="{cd}"/><ellipse cx="6" cy="-10" rx="9" ry="7" fill="{c}"/><path d="M12 -13 L34 -8 L12 -5Z" fill="{p["horn"]}"/>'
            f'<circle cx="7" cy="-11" r="2.6" fill="{p["eye"]}"/><circle cx="8" cy="-11" r="1.4" fill="{p["pup"]}"/></g>')

def egg(x, b, s, p, tilt=0, spots=True):
    o = [f'<g transform="translate({x} {b}) rotate({tilt}) scale({s})"><ellipse cx="0" cy="-21" rx="16" ry="21" fill="{p["egg"]}"/>',
         '<ellipse cx="-5" cy="-28" rx="5" ry="8" fill="#fff" opacity=".35"/>']
    if spots: o.append(f'<circle cx="6" cy="-30" r="3" fill="{p["egg2"]}"/><circle cx="-6" cy="-14" r="2.4" fill="{p["egg2"]}"/><circle cx="8" cy="-12" r="2" fill="{p["egg2"]}"/>')
    o.append('</g>')
    return ''.join(o)

def shell_paths(ex, ey):
    """an egg (rx 16, ry 21, base at ey) split along a zigzag crack into a bottom shell and a top cap"""
    bot = f'M{ex - 16} {ey - 21} L{ex - 10} {ey - 26} L{ex - 4} {ey - 18} L{ex + 3} {ey - 26} L{ex + 9} {ey - 18} L{ex + 16} {ey - 21} A16 21 0 0 1 {ex - 16} {ey - 21}Z'
    cap = f'M{ex - 16} {ey - 21} A16 21 0 0 1 {ex + 16} {ey - 21} L{ex + 9} {ey - 18} L{ex + 3} {ey - 26} L{ex - 4} {ey - 18} L{ex - 10} {ey - 26}Z'
    crack = f'M{ex - 16} {ey - 21} L{ex - 10} {ey - 26} L{ex - 4} {ey - 18} L{ex + 3} {ey - 26} L{ex + 9} {ey - 18} L{ex + 16} {ey - 21}'
    return bot, cap, crack

def baby_head(x, y, r, p, c=None):
    c = c or p["sau"]
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/><ellipse cx="{x + r * .8:.1f}" cy="{y + r * .3:.1f}" rx="{r * .75:.1f}" ry="{r * .55:.1f}" fill="{c}"/>'
            + eye(x + r * .15, y - r * .22, r * .42, p)
            + f'<path d="M{x + r * .9:.1f} {y + r * .55:.1f} q{r * .35:.1f} {r * .2:.1f} {r * .65:.1f} -{r * .1:.1f}" fill="none" stroke="{p["pup"]}" stroke-width="{max(1, r * .12):.1f}" stroke-linecap="round"/>'
            + f'<circle cx="{x + r * .7:.1f}" cy="{y + r * .35:.1f}" r="{r * .22:.1f}" fill="{p["blush"]}" opacity=".5"/>')

def hatchling(x, b, s, p, c=None, tilt=0, anim=''):
    """a baby peeking out of its bottom shell"""
    bot, cap, crack = shell_paths(0, 0)
    hd = baby_head(0, -28, 13, p, c)
    return (f'<g transform="translate({x} {b}) rotate({tilt}) scale({s})">' + (f'<g>{hd}{anim}</g>' if anim else hd)
            + f'<path d="{bot}" fill="{p["egg"]}"/><circle cx="6" cy="-10" r="2.2" fill="{p["egg2"]}"/></g>')

def nest(x, b, w, p, part):
    """part 'back' (the bowl behind the eggs) or 'front' (the rim in front of them)"""
    if part == "back":
        return f'<ellipse cx="{x}" cy="{b - 6}" rx="{w / 2:.0f}" ry="{w * .14:.0f}" fill="{p["nest2"]}"/>'
    o = [f'<path d="M{x - w / 2:.0f} {b - 8} Q{x} {b + w * .16:.0f} {x + w / 2:.0f} {b - 8} Q{x + w * .46:.0f} {b + w * .12:.0f} {x} {b + w * .14:.0f} Q{x - w * .46:.0f} {b + w * .12:.0f} {x - w / 2:.0f} {b - 8}Z" fill="{p["nest"]}"/>']
    r = random.Random(int(x))
    for _ in range(9):
        t = r.uniform(-.45, .45)
        o.append(f'<path d="M{x + w * t - 14:.0f} {b + r.randint(-4, 6)} l{r.randint(20, 34)} {r.randint(-5, 5)}" stroke="{p["nest2"] if r.random() < .5 else p["trunk"]}" stroke-width="2.5" stroke-linecap="round"/>')
    return ''.join(o)

def footprint(x, y, s, c, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><ellipse cx="0" cy="0" rx="4" ry="3.4" fill="{c}"/>'
            f'<path d="M0 -2 L-6 -10 M0 -2 L0 -12 M0 -2 L6 -10" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/></g>')

def sparkle(x, y, r, c="#fff6c0"):
    return f'<path d="M{x} {y - r} Q{x + r * .18:.1f} {y - r * .18:.1f} {x + r} {y} Q{x + r * .18:.1f} {y + r * .18:.1f} {x} {y + r} Q{x - r * .18:.1f} {y + r * .18:.1f} {x - r} {y} Q{x - r * .18:.1f} {y - r * .18:.1f} {x} {y - r}Z" fill="{c}"/>'

def tablet(x, b, w, h, p, lines, fs=14):
    """a carved standing stone"""
    o = [f'<path d="M{x - w / 2:.0f} {b} L{x - w / 2:.0f} {b - h + 14} Q{x - w / 2:.0f} {b - h} {x - w / 2 + 16:.0f} {b - h} L{x + w / 2 - 16:.0f} {b - h} Q{x + w / 2:.0f} {b - h} {x + w / 2:.0f} {b - h + 14} L{x + w / 2:.0f} {b}Z" fill="{p["stone"]}"/>',
         f'<path d="M{x + w / 2 - 10:.0f} {b} L{x + w / 2 - 10:.0f} {b - h + 8} Q{x + w / 2:.0f} {b - h + 4} {x + w / 2:.0f} {b - h + 14} L{x + w / 2:.0f} {b}Z" fill="{p["stone2"]}"/>',
         f'<ellipse cx="{x}" cy="{b}" rx="{w * .6:.0f}" ry="5" fill="#000" opacity=".15"/>']
    for i, t in enumerate(lines):
        y = b - h + 22 + i * (fs + 6)
        o.append(f'<text x="{x - 4}" y="{y}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["stone2"]}" letter-spacing="1.5">{t}</text>'
                 f'<text x="{x - 5}" y="{y - 1}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["ink"] if p["egg"] != "#f8efd8" else "#4a3a2a"}" letter-spacing="1.5">{t}</text>')
    return ''.join(o)

def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(240, body + SHADE)

# ================================================================= the Digest picture
def eruption(p, n):
    """the volcano erupting on an 11 s loop: the crater flares, a fountain of lava bombs, an ash column, lava
    running down the flanks, embers; then back to the gentle smoke. Everything rests hidden (opacity 0)."""
    K = 'dur="11s" repeatCount="indefinite"'
    def op(v, t): return f'<animate attributeName="opacity" values="{v}" keyTimes="{t}" {K}/>'
    def tf(ty, v, t): return f'<animateTransform attributeName="transform" type="{ty}" values="{v}" keyTimes="{t}" {K}/>'
    o = []
    # the ash column: dark puffs stacked over the crater that surge up and spread, lit from below at night
    ash = "#4a4048" if not n else "#2c2630"
    col = puff(0, -28, 22, ash, 1) + puff(6, -72, 32, ash, 1) + puff(-4, -112, 40, ash, 1)
    o.append(f'<g transform="translate(1050 124)"><g opacity="0">{op("0;0;.9;.85;0;0", "0;.12;.22;.45;.68;1")}'
             f'<g>{tf("scale", ".3 .1;.3 .1;1 1;1.5 1.2", "0;.12;.3;1")}{col}</g></g></g>')
    # the crater flaring
    kt = "0;.08;.14;.42;.62;1"
    o.append(f'<circle cx="1050" cy="126" r="{120 if n else 90}" fill="url(#glow)" opacity="{.8 if n else 0}">'
             f'{op((".8;.8;1;1;.8;.8" if n else "0;0;1;.9;0;0"), kt)}'
             f'<animate attributeName="r" values="{"120;120;220;200;120;120" if n else "90;90;170;150;90;90"}" keyTimes="{kt}" {K}/></circle>')
    o.append(f'<ellipse cx="1050" cy="128" rx="38" ry="7" fill="{p["lava2"]}" opacity="0">{op("0;0;1;.5;1;0;0", "0;.08;.14;.2;.26;.5;1")}</ellipse>')
    # lava streaming down both flanks
    o.append(f'<g fill="none" stroke="{p["lava"]}" stroke-width="7" stroke-linecap="round"{"" if n else " stroke-dasharray=\"100 100\""}>')
    for d in ("M1034 132 Q1018 200 992 262 Q974 306 962 360", "M1068 128 Q1088 196 1110 258 Q1126 302 1140 360"):
        # at night they run all the time and swell with the burst; by day they run only with it
        o.append(f'<path d="{d}" pathLength="100" stroke-width="5" opacity=".85">{op(".85;.85;1;1;.85;.85", "0;.16;.18;.6;.8;1")}</path>' if n else
                 f'<path d="{d}" pathLength="100" stroke-dashoffset="100" opacity="0"><animate attributeName="stroke-dashoffset" values="100;100;0;0" keyTimes="0;.16;.5;1" {K}/>'
                 f'{op("0;0;1;1;0;0", "0;.16;.18;.6;.8;1")}</path>')
    o.append('</g>')
    # the fountain: a fan of bombs flung out of the crater, rising then falling back down either side
    bombs = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in [(-60, -80, 7), (-22, -110, 6), (24, -96, 8), (66, -70, 6), (-96, -44, 5), (104, -40, 6)])
    o.append(f'<g fill="{p["lava2"]}" stroke="{p["lava"]}" stroke-width="3">')
    for t0, mir in [(.14, ''), (.22, ' scale(-1 1)')]:
        tm, t1 = t0 + .07, t0 + .2
        kt = f"0;{t0};{tm:.2f};{t1:.2f};1"
        o.append(f'<g transform="translate(1050 124){mir}"><g opacity="0">{op("0;0;1;1;0;0", f"0;{t0};{t0 + .01:.2f};{t1 - .03:.2f};{t1:.2f};1")}'
                 f'<g>{tf("translate", "0 0;0 0;0 -14;0 80;0 80", kt)}<g>{tf("scale", "0;0;1;1.3;1.3", kt)}{bombs}</g></g></g></g>')
    # embers drifting up
    for dx, b in [(-50, .15), (40, .22), (70, .32)]:
        o.append(f'<circle cx="1050" cy="118" r="3" opacity="0" stroke="none">'
                 f'{tf("translate", f"0 0;0 0;{dx} -100;{dx} -100", f"0;{b};{b + .25:.2f};1")}{op("0;0;1;0;0", f"0;{b};{b + .03:.2f};{b + .25:.2f};1")}</circle>')
    o.append('</g>')
    return ''.join(o)

W, H, SPLIT = 1600, 1700, 377
def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    HZ = 452  # the far jungle sits below the split so the valley runs on into the leaderboard
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(defs(skyg(n, id="sky") +
           '<linearGradient id="wf" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="{p["water2"]}"/><stop offset="1" stop-color="{p["water"]}"/></linearGradient>'))
    a(f'<rect width="{W}" height="{HZ + 40}" fill="url(#sky)"/>')
    if n:
        a(stars(8, 0, W, 0, 300, 3))
        a(moon(660, 96, 46))
    else:
        a(sun(660, 104, 36))
        a(cloud(820, 60, 200, .45) + cloud(260, 150, 180, .4) + cloud(1340, 40, 170, .4))
    # far ridges in the haze, then the volcano behind everything else
    a(hills([(0, 290), (180, 236), (420, 284), (640, 250), (820, 290), (1200, 250), (1420, 284), (1600, 240)], HZ, p["far"]))
    a(volcano(1050, 126, HZ, 420, p, n, halo=False))  # its glow is the eruption's
    # its smoke: a standing plume, and puffs that rise off the crater and fade
    sc = p["smoke"]
    a(puff(1062, 98, 20, sc, .75) + puff(1088, 66, 26, sc, .65) + puff(1124, 34, 32, sc, .55) + puff(1170, 4, 38, sc, .45))
    for i in range(3):
        a(f'<g opacity="0">{puff(1056, 112, 16, sc, .9)}'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;40 -70;100 -130" dur="9s" begin="{i * 3}s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0;.85;0" dur="9s" begin="{i * 3}s" repeatCount="indefinite"/></g>')
    a(eruption(p, n))
    a(hills([(0, 380), (260, 350), (520, 390), (800, 362), (1100, 394), (1400, 356), (1600, 380)], HZ, p["far2"]))
    # pterosaurs gliding across the sky, each crossing then coming back round from the far side
    for i, (x, y, s, dur, out, back, k) in enumerate([(300, 112, .9, 12, 1400, -520, .6), (1260, 64, .6, 11, 420, -1400, .3)]):
        flap = (f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 .3;1 1;1 .3;1 1;1 1" '
                f'keyTimes="0;.5;.58;.66;.74;.82;1" dur="4s" begin="{i * 1.3}s" repeatCount="indefinite"/>')
        a(f'<g>{ptero(x, y, s, p, flap)}<animateTransform attributeName="transform" type="translate" '
          f'values="0 0;{out} -24;{back} 18;0 0" keyTimes="0;{k};{k + .0001};1" dur="{dur}s" repeatCount="indefinite"/></g>')
    # the valley floor and the far jungle edge
    a(f'<rect x="0" y="{HZ - 4}" width="{W}" height="{H - HZ}" fill="{p["ground"]}"/>')
    a(canopy(-10, 1610, HZ + 6, 20, 34, p["jung"], 2, 30))
    a(canopy(-10, 1610, HZ + 22, 14, 22, p["jung2"], 5, 44))
    # the cliff on the right, the waterfall off its lip, the pool and the river running out of it
    a(f'<path d="M1176 620 L1182 486 Q1190 424 1236 414 L1294 406 L1350 410 L1420 400 L1520 404 L1600 396 L1600 640 Z" fill="{p["rock"]}"/>')
    a(f'<path d="M1182 486 Q1190 424 1236 414 L1294 406 L1290 620 L1176 620Z" fill="{p["rock2"]}" opacity=".55"/>')
    for y in (448, 488, 530): a(f'<path d="M1186 {y} Q1400 {y - 10} 1600 {y + 4}" fill="none" stroke="{p["rock3"]}" stroke-width="3" opacity=".45"/>')
    a(f'<path d="M1230 412 Q1400 392 1600 392 L1600 404 L1520 408 L1420 404 L1350 414 L1294 410 L1236 418Z" fill="{p["leaf"]}"/>')
    a(f'<rect x="1300" y="406" width="44" height="186" fill="url(#wf)"/>')
    for i, x in enumerate((1306, 1316, 1327, 1337)):
        a(f'<path d="M{x} 410 L{x} 588" stroke="{p["foam"]}" stroke-width="{3 if i % 2 else 2}" stroke-dasharray="30 12" opacity=".4">'
          f'<animate attributeName="stroke-dashoffset" values="0;-114" dur="{3 + i * .3:.1f}s" repeatCount="indefinite"/></path>')
    a(f'<path d="M1216 604 Q1230 576 1322 576 Q1420 578 1440 600 Q1500 618 1600 626 L1600 676 Q1500 672 1440 650 Q1380 632 1300 626 Q1218 624 1216 604Z" fill="{p["water"]}"/>')
    for i, (x, y, w) in enumerate([(1290, 600, 70), (1400, 618, 60), (1500, 646, 70), (1250, 612, 40)]):
        a(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{p["water2"]}" opacity=".8"/>')
    a(f'<ellipse cx="1322" cy="588" rx="44" ry="9" fill="{p["foam"]}" opacity=".8"><animate attributeName="rx" values="44;52;44" dur="3s" repeatCount="indefinite"/></ellipse>')
    # the cliff-top tree ferns, their crowns rising into the sky
    for i, (x, b, h) in enumerate([(1470, 404, 300), (1566, 400, 262), (1236, 418, 170)]):
        a(treefern(x, b, h, p, anim=sway(x, b - h, 1.6, 6 + i, i * .8)))
    for i, t in enumerate(["PREHISTORIC", "PROTECTION"]):
        y = 462 + i * 30
        a(f'<text x="1474" y="{y + 1}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="{p["rock3"]}" letter-spacing="2">{t}</text>'
          f'<text x="1473" y="{y}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="{p["ink"] if n else "#fff3dc"}" opacity="{.55 if n else .8}" letter-spacing="2">{t}</text>')
    # the game trail from the far jungle down to the ledge, with footprints on it
    a(f'<path d="M786 {HZ + 2} L812 {HZ + 2} Q838 510 878 574 L726 574 Q768 510 786 {HZ + 2}Z" fill="{p["trail"]}"/>')
    tc = p["ledge2"] if not n else "#2a2230"
    for i, (x, y, s) in enumerate([(796, 478, .5), (808, 496, .55), (792, 516, .65), (812, 538, .75), (790, 560, .85)]):
        a(footprint(x, y, s, tc, -6 if i % 2 else 6))
    # the browse tree and the sauropod eating from its crown; its neck sways as it chews
    a(araucaria(520, 528, 54, p))
    a(cycad(70, 610, 1.1, p, p["leaf2"]))
    a(sauropod(232, 586, 1.0, p, head=(208, -470), c1=(122, -230), c2=(176, -380), leaf=True,
               neck_anim=sway(96, -112, 1.6, 5),
               tail_anim=sway(-104, -80, 4, 7, 1)))
    a(cycad(392, 606, .9, p) + cycad(160, 636, .8, p, p["leaf2"]))
    # the podium's stage: a flat sandstone ledge
    lt = "M456 650 C462 596 606 570 806 570 C1004 570 1156 596 1164 656 C1172 730 1080 800 816 808 C576 812 448 748 456 650Z"
    a(f'<path d="{lt}" fill="{p["ledge2"]}" transform="translate(0 26)"/>')
    a(f'<path d="M470 700 Q800 800 1150 700" fill="none" stroke="{p["ledge3"]}" stroke-width="3" opacity=".6" transform="translate(0 44)"/>')
    a(f'<path d="{lt}" fill="{p["ledge"]}"/>')
    a(f'<path d="M520 630 C600 596 1000 596 1100 630" fill="none" stroke="#fff" stroke-width="10" opacity="{.12 if not n else .05}" stroke-linecap="round"/>')
    a(f'<path d="M560 720 l40 -8 l18 10 M1040 700 l30 10 l20 -6" fill="none" stroke="{p["ledge3"]}" stroke-width="2.5" stroke-linecap="round"/>')
    for x, y, r in [(470, 708, 10), (452, 676, 7), (1160, 704, 9), (1176, 680, 6)]:
        a(f'<ellipse cx="{x}" cy="{y}" rx="{r * 1.4:.0f}" ry="{r}" fill="{p["ledge2"]}"/>')
    # the nest at the front left, one egg wobbling, cracking and hatching on a 9-second loop
    nx, nb = 316, 772
    a(nest(nx, nb, 150, p, "back"))
    a(egg(nx - 38, nb - 2, 1.0, p, -12) + egg(nx + 40, nb - 2, .95, p, 14))
    ex, ey = nx + 2, nb + 2
    bot, cap, crack = shell_paths(ex, ey)
    wob = (f'<animateTransform attributeName="transform" type="rotate" values="0 {ex} {ey};0 {ex} {ey};8 {ex} {ey};-8 {ex} {ey};6 {ex} {ey};-5 {ex} {ey};0 {ex} {ey};0 {ex} {ey}" '
           f'keyTimes="0;.08;.13;.19;.25;.31;.36;1" dur="9s" repeatCount="indefinite"/>')
    lid = (f'<animateTransform attributeName="transform" type="rotate" values="0 {ex - 16} {ey - 21};0 {ex - 16} {ey - 21};-75 {ex - 16} {ey - 21};-75 {ex - 16} {ey - 21};0 {ex - 16} {ey - 21};0 {ex - 16} {ey - 21}" '
           f'keyTimes="0;.44;.5;.86;.9;1" dur="9s" repeatCount="indefinite"/>')
    a(f'<g><g opacity="0">{baby_head(ex, ey - 30, 12, p, p["thr"])}{show(["0", ".46", ".88"], ["0", "1", "0"], 9)}'
      f'<animateTransform attributeName="transform" type="translate" values="0 12;0 12;0 0;0 0;0 12" keyTimes="0;.46;.52;.86;1" dur="9s" repeatCount="indefinite"/></g>'
      f'<path d="{bot}" fill="{p["egg"]}"/><circle cx="{ex + 6}" cy="{ey - 10}" r="2.2" fill="{p["egg2"]}"/>'
      f'<path d="{crack}" fill="none" stroke="{p["nest2"]}" stroke-width="1.8" stroke-linejoin="round" opacity="0">{show(["0", ".28", ".9"], ["0", "1", "0"], 9)}</path>'
      f'<g><path d="{cap}" fill="{p["egg"]}"/><circle cx="{ex - 4}" cy="{ey - 32}" r="2.6" fill="{p["egg2"]}"/>{lid}</g>{wob}</g>')
    for i, (sx, sy, sr) in enumerate([(ex - 26, ey - 54, 6), (ex + 24, ey - 60, 7), (ex + 4, ey - 72, 5)]):
        a(f'<g opacity="0">{sparkle(sx, sy, sr)}{show(["0", f"{.52 + i * .04:.2f}", ".86"], ["0", "1", "0"], 9)}</g>')
    a(nest(nx, nb, 150, p, "front"))
    # the small friendly theropod keeping an eye on the nest, tail swishing
    a(thero(150, 800, 1.0, p, tail_anim=sway(-12, -40, 7, 3.5)))
    # the three-horned herd grazing on the near bank of the river
    a(trike(1556, 712, .7, p, flip=True, graze=26))
    a(tablet(1222, 676, 128, 62, p, ["NO LAPSE", "LAGOON"], 15))
    a(trike(1430, 778, .86, p, flip=True, graze=22))
    a(trike(1268, 830, .8, p, flip=True, graze=0))
    a(cycad(1570, 840, .9, p, p["leaf2"]))
    # the left edge's tall tree fern frames the picture and rises into the sky
    a(cycad(24, 690, 1.3, p, p["leaf2"]))
    # fireflies at night, blinking over the ferns and the bank
    if n:
        r = random.Random(8)
        for i in range(4):
            x = r.choice([r.randint(40, 440), r.randint(1180, 1580)]); y = r.randint(540, 720)
            a(f'<circle cx="{x}" cy="{y}" r="7" fill="url(#ff)" opacity=".9"><animate attributeName="opacity" values=".9;.1;.9" dur="{3 + r.random() * 3:.1f}s" begin="{r.random() * 3:.1f}s" repeatCount="indefinite"/></circle>')
    # tufts in the grass, kept off the stage
    r = random.Random(11); tg = p["ground2"] if not n else "#0f1f17"
    for _ in range(14):
        x = r.randint(0, W); y = r.randint(HZ + 50, 860)
        if 430 < x < 1190 and y > 520: continue
        if x < 440 and 680 < y < 830: continue
        a(f'<path d="M{x - 6} {y} l3 -9 l3 7 l3 -10 l3 12" stroke="{tg}" stroke-width="2" fill="none"/>')
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def base(n, sky=DAYSKY, nt=NIGHTSKY, star=45, extra=''):
    return defs(skyg(n, day=sky, nt=nt) + extra) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 140, 7) + twinkle(star) if n else '')

def ground(p, y, c=None):
    return f'<path d="M0 {y} Q400 {y - 10} 800 {y} T1600 {y - 4} L1600 240 L0 240Z" fill="{c or p["ground"]}"/>'

def corners(p, n):
    """the dark fern banks the title and line sit on"""
    c = p["leaf2"]; o = [f'<path d="M0 168 Q200 160 470 188 L470 240 L0 240Z" fill="{c}"/>',
                         f'<path d="M1600 174 Q1320 168 1040 196 L1040 240 L1600 240Z" fill="{c}"/>']
    for x, ang in [(60, -60), (150, -120), (250, -70), (1380, -110), (1470, -60), (1550, -130)]:
        o.append(frond(x, 200, ang, 90, c, 14, .3))
    return ''.join(o)

def far_volcano(p, n, cx=300, peak=96, b=176, half=200, smoke=True):
    o = [volcano(cx, peak, b, half, p, n)]
    if smoke: o.append(puff(cx + 10, peak - 22, 14, p["smoke"], .7) + puff(cx + 30, peak - 48, 18, p["smoke"], .55))
    return ''.join(o)

def v_sales(n):  # the herd on the move along the valley trail
    p = P(n); o = [base(n)]
    o.append(moon(1250, 60, 22) if n else sun(1250, 66, 24))
    o.append(hills([(0, 150), (300, 120), (600, 140), (900, 112), (1200, 134), (1600, 120)], 190, p["far"]))
    o.append(far_volcano(p, n, 420, 92, 180, 170))
    o.append(canopy(0, 1600, 176, 12, 22, p["jung"], 4, 26))
    o.append(ground(p, 172))
    o.append(f'<path d="M380 200 Q800 182 1240 194 L1240 208 Q800 196 380 214Z" fill="{p["trail"]}"/>')
    dust = p["trail"] if not n else "#5a5060"
    o.append(f'<g>{"".join(puff(x, 200, 9, dust, .6) for x in (552, 742, 950, 1160))}{pulse(1, .3, 2.4)}</g>')
    o.append(sauropod(560, 204, .55, p, head=(196, -230), neck_anim=sway(96, -112, 2.5, 6)))
    o.append(f'<g>{trike(800, 206, .68, p)}{trike(1200, 202, .56, p)}{bob(2.5, 1.2)}</g><g>{trike(1010, 204, .66, p)}{bob(2.5, 1.2, .6)}</g>')
    o.append(f'<g>{thero(1330, 200, .55, p)}{bob(3, .9, .3)}</g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_messages(n):  # the volcano sending its smoke signals
    p = P(n); o = [base(n, sky=("#6c9ec8", "#f2b874", "#fbd89a"))]
    o.append(moon(1260, 56, 20) if n else sun(1260, 60, 22))
    o.append(hills([(0, 160), (400, 132), (800, 150), (1200, 126), (1600, 150)], 200, p["far"]))
    o.append(volcano(800, 104, 196, 300, p, n))
    if n: o.append(f'<circle cx="800" cy="106" r="80" fill="url(#glow)">{pulse(1, .55, 5)}</circle>')
    for i, (x, y, r) in enumerate([(812, 72, 18), (836, 34, 22)]):
        o.append(puff(x, y, r, p["smoke"], .9))
    o.append(rise(806, 88, 12, p["smoke"], 20, -60, 6, 0) + rise(806, 88, 12, p["smoke"], 20, -60, 6, 3))
    o.append(f'<ellipse cx="868" cy="12" rx="40" ry="14" fill="none" stroke="{p["smoke"]}" stroke-width="10" opacity=".8">{pulse(.8, .45, 4)}{pulse(40, 46, 4, 0, "rx")}</ellipse>')
    o.append(f'<path d="M790 82 q10 -6 20 0" stroke="{p["smoke"]}" stroke-width="3" fill="none" opacity=".6"/>')
    o.append(canopy(0, 1600, 190, 12, 22, p["jung"], 5, 26))
    o.append(ground(p, 186))
    o.append(f'<path d="M1020 206 Q1060 180 1110 186 Q1150 192 1160 210Z" fill="{p["rock2"]}"/>')
    o.append(f'<g>{thero(1084, 196, .8, p, flip=True, pose="sit", wave=True)}{sway(1084, 196, 2.5, 3)}</g>')
    fl = '<animateTransform attributeName="transform" type="scale" values="1 1;1 .35;1 1" keyTimes="0;.5;1" dur="1.6s" repeatCount="indefinite"/>'
    o.append(f'<g>{ptero(560, 84, .7, p, fl)}{ptero(640, 60, .45, p)}{bob(6, 8, 0, 30)}</g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_coaching(n):  # an elder teaching the young ones at the stone
    p = P(n); o = [base(n, sky=("#7aa8cc", "#f4cc8a", "#fbe6b2"))]
    o.append(moon(1290, 58, 20) if n else sun(1290, 62, 22))
    o.append(canopy(0, 1600, 140, 14, 26, p["jung"], 6, 28))
    o.append(ground(p, 136))
    o.append(cycad(1200, 180, 1.1, p, p["leaf2"]))
    # the stone the elder draws on: a dial, a quote, a close
    o.append(f'<path d="M590 200 L596 92 Q600 80 614 80 L746 80 Q760 80 762 92 L768 200Z" fill="{p["stone"]}"/>')
    o.append(f'<path d="M620 120 q30 -26 60 0 q30 26 56 -6" fill="none" stroke="{p["stone2"]}" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M726 106 l12 6 l-10 10" fill="none" stroke="{p["stone2"]}" stroke-width="5" stroke-linecap="round"/>'
             f'<circle cx="640" cy="160" r="12" fill="none" stroke="{p["stone2"]}" stroke-width="5"/><path d="M670 160 h50 M670 176 h36" stroke="{p["stone2"]}" stroke-width="5" stroke-linecap="round"/>')
    o.append(sauropod(520, 206, .52, p, head=(200, -180), c1=(140, -160), c2=(180, -210), neck_anim=sway(96, -112, 2, 6)))
    o.append(thero(870, 208, .7, p, flip=True, pose="sit", tail_anim=sway(-12, -40, 7, 3)))
    o.append(trike(1000, 210, .44, p, flip=True, head_anim=sway(46, -50, 5, 4, .5)))
    o.append(sauropod(1110, 210, .32, p, flip=True, head=(150, -230), neck_anim=sway(96, -112, 3, 5, 1)))
    if n: o.append(fireflies(5, 820, 1500, 150, 210, 21))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_roleplay(n):  # the nest of hatchlings
    p = P(n); o = [base(n, sky=("#7aa8cc", "#f6cc8c", "#fbe8bc"))]
    o.append(moon(1250, 56, 20) if n else sun(1250, 60, 22))
    o.append(canopy(0, 1600, 136, 14, 26, p["jung"], 8, 28))
    o.append(ground(p, 132))
    o.append(cycad(560, 196, 1.2, p) + cycad(1060, 196, 1.3, p, p["leaf2"]))
    o.append(nest(800, 206, 300, p, "back"))
    cols = [p["sau"], p["thr"], p["tri"], p["pte"]]
    for i, (x, b, s, t) in enumerate([(720, 200, 1.4, -10), (790, 196, 1.6, 4), (870, 200, 1.4, 12), (950, 206, 1.1, 18)]):
        o.append(hatchling(x, b, s, p, cols[i], t, bob(5, 2.2 + i * .3, i * .5)))
    o.append(f'<g>{egg(660, 206, 1.1, p, -18)}{sway(660, 206, 4, 2.5)}</g>')
    if n: o.append(fireflies(5, 560, 1500, 140, 200, 22))
    o.append(nest(800, 206, 300, p, "front"))
    o.append(f'<path d="M1000 214 l10 -8 l8 6 l8 -6 l6 8Z" fill="{p["egg"]}"/>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_rphistory(n):  # cave paintings by firelight
    o = [defs()]
    wall = "#7a4e34" if not n else "#2a1a14"; wall2 = "#5e3a26" if not n else "#1c120d"
    o.append(f'<rect width="1600" height="{V}" fill="{wall}"/>')
    o.append(f'<path d="M0 0 L1600 0 L1600 40 Q1200 70 800 46 Q400 24 0 60Z" fill="{wall2}"/>')
    for x, y, rx in [(300, 120, 140), (1250, 110, 160), (760, 160, 300)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="40" fill="{wall2}" opacity=".35"/>')
    o.append(f'<circle cx="800" cy="210" r="420" fill="url(#glow)" opacity=".75">{pulse(.75, .55, 3)}</circle>')
    ochre = "#e8a85a" if not n else "#c88a48"; red = "#c4523a" if not n else "#a8442e"
    # the paintings: a long-neck, the herd, a sun, footprints and a tally
    pp = dict(P(False), sau=ochre, sau2=ochre, saub=ochre, horn=ochre, eye=ochre, pup=ochre, blush=ochre, leaf=ochre)
    o.append(f'<g opacity=".9">{sauropod(560, 150, .38, pp, head=(170, -240))}</g>')
    tp = dict(P(False), tri=red, tri2=red, frill=red, horn=red, eye=red, pup=red, blush=red)
    o.append(f'<g opacity=".85">{trike(900, 132, .36, tp)}{trike(1010, 140, .3, tp)}</g>')
    o.append(f'<circle cx="760" cy="62" r="16" fill="none" stroke="{ochre}" stroke-width="5"/>' +
             ''.join(f'<path d="M{760 + 26 * math.cos(k * math.pi / 4):.0f} {62 + 26 * math.sin(k * math.pi / 4):.0f} L{760 + 36 * math.cos(k * math.pi / 4):.0f} {62 + 36 * math.sin(k * math.pi / 4):.0f}" stroke="{ochre}" stroke-width="4" stroke-linecap="round"/>' for k in range(8)))
    for i in range(5): o.append(footprint(1140 + i * 26, 80 + (i % 2) * 14, .9, red, 80))
    o.append(f'<path d="M640 70 v24 M650 70 v24 M660 70 v24 M670 70 v24 M634 90 l42 -16" stroke="{ochre}" stroke-width="4" stroke-linecap="round"/>')
    # the fire and the little theropod sitting by it
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{wall2}"/>')
    o.append('<path d="M760 210 l70 -10 M770 200 l60 12" stroke="#4a2a18" stroke-width="8" stroke-linecap="round"/>')
    fk = ('<animateTransform attributeName="transform" type="scale" values="1 1;1.05 .9;.96 1.06;1 1" keyTimes="0;.3;.65;1" dur="1.4s" repeatCount="indefinite"/>')
    o.append(f'<g transform="translate(804 204)"><g>{fk}<g transform="translate(-804 -204)"><path d="M780 202 Q770 170 796 140 Q792 168 808 176 Q816 156 812 136 Q842 172 826 204Z" fill="#ff9a3a"/><path d="M792 202 Q786 182 800 166 Q804 184 816 188 Q820 196 814 204Z" fill="#ffe08a"/></g></g></g>')
    for i, (x, dx) in enumerate([(800, -14), (812, 16), (806, 4)]):
        o.append(f'<circle cx="{x}" cy="150" r="2.5" fill="#ffd27a" opacity="0"><animateTransform attributeName="transform" type="translate" values="0 0;{dx} -90" dur="3s" begin="{i}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;.2;1" dur="3s" begin="{i}s" repeatCount="indefinite"/></circle>')
    o.append(thero(940, 206, .5, P(n), flip=True, pose="sit", tail_anim=sway(-12, -40, 7, 3.5)))
    return vwrap(''.join(o))

def v_training(n):  # hatchlings learning to fly off the ledge
    p = P(n); o = [base(n, sky=("#78a8d0", "#f2c886", "#fbe4b0"))]
    o.append(moon(300, 56, 20) if n else sun(300, 60, 22))
    o.append(hills([(0, 170), (400, 150), (800, 168), (1200, 144), (1600, 162)], 220, p["far"]))
    o.append(canopy(0, 1600, 206, 10, 20, p["jung"], 9, 24))
    o.append(f'<path d="M940 240 Q1100 214 1600 224 L1600 240Z" fill="{p["water"]}"/>')
    # the ledge they launch from
    o.append(f'<path d="M380 240 L400 132 Q420 116 470 116 L700 112 Q724 112 730 126 L760 240Z" fill="{p["rock"]}"/>')
    o.append(f'<path d="M700 112 Q724 112 730 126 L760 240 L690 240Z" fill="{p["rock2"]}"/>')
    o.append(f'<path d="M400 128 Q560 106 730 124 L728 116 Q560 98 404 120Z" fill="{p["leaf"]}"/>')
    pt = dict(p)
    for x in (500, 575, 645):
        o.append(f'<g><g transform="translate({x} 120) scale(.85)"><ellipse cx="0" cy="-16" rx="12" ry="16" fill="{p["pte2"]}"/>{baby_head(4, -40, 14, p, p["pte"])}<path d="M10 -40 L34 -36 L10 -32Z" fill="{p["horn"]}"/></g>{bob(4, 1.6, (x - 500) / 120)}</g>')
    o.append(f'<path d="M700 110 Q820 60 960 92 Q1060 116 1130 96" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="4 10" stroke-linecap="round" opacity=".75"/>')
    o.append(f'<g>{ptero(960, 92, .7, pt)}{bob(5, 4)}</g>')
    fl = '<animateTransform attributeName="transform" type="scale" values="1 1;1 .35;1 1" keyTimes="0;.5;1" dur="1.4s" repeatCount="indefinite"/>'
    o.append(f'<g>{ptero(1130, 70, .9, pt, fl)}{bob(7, 6, 0, 24)}</g>')
    o.append(f'<g opacity="0">{ptero(724, 104, .5, pt)}<animateMotion path="M0 0 Q110 -60 236 -10" dur="7s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="7s" repeatCount="indefinite"/></g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the stone tablet with the route carved through four stops
    st = "#a49e92" if not n else "#3e3c40"; st2 = "#8a8478" if not n else "#2e2c32"; cut = "#6a645a" if not n else "#1e1d22"
    route = "#7fd0a0" if athena else "#ff9a4a"
    o = [f'<rect width="1600" height="{V}" fill="{"#5a4636" if not n else "#17120e"}"/>',
         f'<path d="M360 30 Q380 18 420 20 L1180 16 Q1230 18 1240 40 L1250 206 Q1240 228 1200 226 L400 230 Q366 228 358 200Z" fill="{st}"/>',
         f'<path d="M1180 16 Q1230 18 1240 40 L1250 206 Q1240 228 1200 226 L1196 40Z" fill="{st2}"/>']
    r = random.Random(3)
    for _ in range(14):
        x = r.randint(400, 1180); y = r.randint(36, 210)
        o.append(f'<path d="M{x} {y} l{r.randint(6, 16)} {r.randint(-6, 6)}" stroke="{st2}" stroke-width="2" stroke-linecap="round"/>')
    # carved landmarks: the volcano, the river, the ferns, the nest
    o.append(f'<path d="M430 120 L470 60 L486 60 L526 120Z" fill="none" stroke="{cut}" stroke-width="4" stroke-linejoin="round"/><path d="M478 54 q-6 -12 4 -20 q-4 -8 6 -14" fill="none" stroke="{cut}" stroke-width="3"/>')
    o.append(f'<path d="M560 210 Q700 180 820 200 T1100 190" fill="none" stroke="{cut}" stroke-width="4" opacity=".6"/>')
    for x in (1120, 1150): o.append(frond(x, 120, -100, 50, cut, 8, .1))
    o.append(f'<ellipse cx="1150" cy="190" rx="26" ry="8" fill="none" stroke="{cut}" stroke-width="3"/><ellipse cx="1140" cy="182" rx="7" ry="9" fill="{cut}"/><ellipse cx="1158" cy="182" rx="7" ry="9" fill="{cut}"/>')
    pts = [(560, 150), (720, 92), (890, 152), (1060, 92)]
    d = f'M470 170 C500 166 530 160 {pts[0][0]} {pts[0][1]} S660 92 {pts[1][0]} {pts[1][1]} S830 152 {pts[2][0]} {pts[2][1]} S1000 92 {pts[3][0]} {pts[3][1]} S1120 140 1140 180'
    o.append(f'<path d="{d}" fill="none" stroke="{cut}" stroke-width="9" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="4" stroke-dasharray="2 12" stroke-linecap="round"><animate attributeName="stroke-dashoffset" values="0;-28" dur="2s" repeatCount="indefinite"/></path>')
    for i, (x, y) in enumerate(pts):
        o.append(f'<circle cx="{x}" cy="{y}" r="15" fill="none" stroke="{route}" stroke-width="3" opacity="0"><animate attributeName="r" values="15;30" dur="4s" begin="{i}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;.9;0;0" keyTimes="0;.1;.5;1" dur="4s" begin="{i}s" repeatCount="indefinite"/></circle>')
    for i in range(6): o.append(footprint(492 + i * 13, 168 - i * 3, .7, cut, 70))
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        o.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{route}" stroke="{cut}" stroke-width="4"/><text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#2a2018">{i + 1}</text>')
        ty = y - 26 if y < 120 else y + 40
        if y < 120: ty = y + 42
        else: ty = y - 26
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="#fff" stroke="#2a2018" stroke-width="5" paint-order="stroke">{t}</text>')
    o.append(f'<text x="420" y="54" font-family="Georgia, serif" font-style="italic" font-size="15" fill="{cut}">' + ('the service trail' if athena else 'the sales trail') + '</text>')
    return vwrap(''.join(o))

def v_service(n):  # the herd guarding the nest
    p = P(n); o = [base(n, sky=("#78a8d0", "#f2c886", "#fbe4b0"))]
    o.append(moon(1300, 56, 20) if n else sun(1300, 60, 22))
    o.append(canopy(0, 1600, 132, 14, 28, p["jung"], 10, 28))
    o.append(ground(p, 128))
    o.append(sauropod(820, 160, .4, p, head=(90, -270), c1=(130, -200), c2=(40, -290), neck_anim=sway(96, -112, 3, 7)))
    o.append(trike(640, 214, .56, p, flip=True, head_anim=sway(46, -50, 4, 5)))
    o.append(trike(990, 214, .56, p, head_anim=sway(46, -50, 4, 5, 2)))
    o.append(nest(810, 212, 170, p, "back"))
    o.append(egg(776, 210, 1.1, p, -10) + f'<g>{egg(812, 206, 1.2, p)}{sway(812, 206, 5, 3)}</g>' + egg(846, 210, 1.1, p, 12))
    o.append(nest(810, 212, 170, p, "front"))
    if n: o.append(fireflies(5, 500, 1500, 140, 200, 23))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # spring hatching: the meadow in flower and eggs opening
    p = P(n); o = [base(n, sky=("#7ab2da", "#cfe4ea", "#f6eccc"))]
    o.append(moon(1260, 56, 20) if n else sun(1260, 60, 22))
    o.append(hills([(0, 130), (400, 106), (800, 124), (1200, 100), (1600, 124)], 160, p["far"]))
    o.append(canopy(0, 1600, 150, 12, 22, p["jung"], 11, 26))
    o.append(ground(p, 146))
    r = random.Random(14)
    for x, b, s in [(520, 196, 1.2), (1100, 196, 1.3)]:
        o.append(cycad(x, b, s, p))
        for _ in range(7): o.append(f'<circle cx="{x + r.randint(-60, 60)}" cy="{b - 40 * s - r.randint(10, 60)}" r="{r.randint(5, 9)}" fill="{p["flower"]}"/>')
    for x, b, s, c, t in [(700, 206, 1.3, p["sau"], -8), (820, 200, 1.5, p["tri"], 6), (940, 208, 1.3, p["thr"], 10)]:
        o.append(hatchling(x, b, s, p, c, t, bob(4, 2.4, (x - 700) / 200)))
        o.append(f'<g>{sparkle(x - 26, b - 64, 6)}{sparkle(x + 28, b - 70, 5)}{pulse(1, .15, 2, (x - 700) / 240)}</g>')
    for _ in range(40):
        x = r.choice([r.randint(420, 680), r.randint(980, 1220)]); y = r.randint(196, 226)
        o.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{r.choice(["#f2d14a", "#f2a2c0", "#fff6e8", "#b8a0f0"] if not n else ["#a89a5a", "#8a5a6a", "#a8a4b0"])}"/>')
    for i, (x, y) in enumerate([(640, 110), (1000, 90)]):
        o.append(f'<g><g transform="translate({x} {y})"><path d="M0 0 h24" stroke="{p["thr2"]}" stroke-width="3" stroke-linecap="round"/>'
                 f'<ellipse cx="8" cy="-6" rx="10" ry="4" fill="#fff" opacity=".7"/><ellipse cx="8" cy="6" rx="10" ry="4" fill="#fff" opacity=".7">{pulse(4, 1.5, .25, 0, "ry")}</ellipse></g>'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;26 -10;44 6;14 12;0 0" keyTimes="0;.25;.5;.75;1" dur="{6 + i}s" repeatCount="indefinite" calcMode="spline" keySplines="{SP2};{SP2}"/></g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_claims(n):  # after the rockslide: the herd clearing the trail
    p = P(n); o = [base(n, sky=("#8a96a6", "#c8c0b2", "#e8dcc6"), nt=("#06080f", "#141826", "#262a3c"), star=20)]
    for x in (300, 760, 1240): o.append(f'<ellipse cx="{x}" cy="40" rx="220" ry="22" fill="{"#a0a6b2" if not n else "#1c2032"}" opacity=".8"/>')
    # the cliff the rocks came down
    o.append(f'<path d="M360 240 L380 60 Q420 30 520 40 L640 60 Q700 80 700 120 L720 240Z" fill="{p["rock"]}"/>')
    o.append(f'<path d="M560 54 L640 60 Q700 80 700 120 L720 240 L600 240 Q620 150 560 54Z" fill="{p["rock2"]}"/>')
    o.append(f'<path d="M520 44 L580 110 L560 150" fill="none" stroke="{p["rock3"]}" stroke-width="3"/>')
    o.append(canopy(700, 1600, 150, 14, 26, p["jung"], 12, 28))
    o.append(ground(p, 150))
    o.append(f'<path d="M700 214 Q1000 200 1300 210 L1300 222 Q1000 214 700 228Z" fill="{p["trail"]}"/>')
    # the slide across the trail
    for x, y, r in [(760, 196, 26), (800, 182, 22), (720, 206, 18), (842, 200, 20), (780, 210, 16), (870, 212, 12)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{r * 1.2:.0f}" ry="{r}" fill="{p["stone"]}"/><ellipse cx="{x + r * .3:.0f}" cy="{y + r * .3:.0f}" rx="{r * .7:.0f}" ry="{r * .5:.0f}" fill="{p["stone2"]}"/>')
    o.append(f'<g>{puff(760, 150, 18, "#d8cfc0" if not n else "#3a3a44", .5)}{bob(8, 6, 0, 10)}{pulse(1, .4, 6)}</g>')
    # the crew: a trike nosing a boulder off, a long-neck lifting one, a little one carrying a pebble
    nk = 'keyTimes="0;.3;.5;1" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"'
    o.append(f'<ellipse cx="955" cy="204" rx="26" ry="20" fill="{p["stone"]}"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-7 0;0 0" {nk}/></ellipse>')
    o.append(trike(1040, 220, .66, p, flip=True, graze=12, head_anim=f'<animateTransform attributeName="transform" type="rotate" values="0 46 -50;-4 46 -50;6 46 -50;0 46 -50" {nk}/>'))
    o.append(sauropod(1250, 218, .46, p, flip=True, head=(240, -150), c1=(140, -170), c2=(220, -170), tail_anim=sway(-104, -80, 4, 6)))
    o.append(f'<ellipse cx="1150" cy="168" rx="12" ry="9" fill="{p["stone"]}"/>')
    o.append(f'<g>{thero(900, 220, .62, p)}<ellipse cx="928" cy="178" rx="10" ry="8" fill="{p["stone"]}"/>{bob(3, 1)}</g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the great sauropod caravan crossing the valley
    p = P(n); o = [base(n, sky=("#6c9ec8", "#f0a86a", "#f8d494"))]
    o.append(moon(300, 54, 20) if n else sun(300, 58, 26))
    o.append(far_volcano(p, n, 1280, 90, 176, 190))
    o.append(rise(1292, 64, 12, p["smoke"], 24, -50, 7, 0, .7) + rise(1292, 64, 12, p["smoke"], 24, -50, 7, 3.5, .7))
    o.append(hills([(0, 170), (400, 150), (800, 166), (1200, 148), (1600, 168)], 200, p["far2"]))
    o.append(ground(p, 196, p["trail"]))
    o.append(f'<path d="M0 196 Q800 182 1600 196" fill="none" stroke="{p["ground"]}" stroke-width="6"/>')
    for i, (x, s, hd) in enumerate([(470, .3, (190, -330)), (660, .4, (200, -350)), (880, .46, (200, -330)), (1080, .3, (180, -300)), (1180, .18, (170, -300))]):
        o.append(f'<g>{sauropod(x, 208 - s * 10, s, p, head=hd, neck_anim=sway(96, -112, 2, 5 + i % 2, i * .7) if x > 600 else "")}{bob(2, 1.6, i * .4)}</g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the herd on the move: premium down the trail"],
    "messages": ["Texts & Emails", "smoke signals: every reply sent up"],
    "coaching": ["Coaching", "the elders' stone: every call, explained"],
    "roleplay": ["Role Play", "the nest: practice before you hatch"],
    "rphistory": ["Session History", "the cave wall: every session, painted"],
    "training": ["Training", "the ledge: learning to fly"],
    "blueprint": ["Apollo's Road Map", "the stone map, in plain words"],
    "athenamap": ["Athena's Road Map", "the service trail, in plain words"],
    "service": ["Service Digest", "the herd: guarding the nest egg"],
    "renewals": ["Renewals", "spring hatching: what came back"],
    "claims": ["Claims", "after the rockslide: clearing the trail"],
    "commercial": ["Commercial Center", "the great caravan: Cerberus's herd"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=30):
    return (defs(skyg(n, day=day, nt=nt)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 90, 21) if n else ''))

def sground(p, y=112, c=None):
    return f'<path d="M0 {y} Q800 {y - 12} 1600 {y} L1600 160 L0 160Z" fill="{c or p["ground"]}"/>'

def s_sold(n):  # the egg hatches: shell open, the baby out, sparkles all round
    p = P(n); o = [sbase(n, ("#e8a04a", "#f6c86e", "#fde6a8"), ("#0a1030", "#1a2858", "#3a3a6a"))]
    for i in range(14):
        ang = i / 14 * 2 * math.pi
        o.append(f'<path d="M780 90 L{780 + 700 * math.cos(ang):.0f} {90 + 700 * math.sin(ang):.0f} L{780 + 700 * math.cos(ang + .13):.0f} {90 + 700 * math.sin(ang + .13):.0f}Z" fill="#fff" opacity="{.18 if not n else .07}"/>')
    o.append(canopy(0, 1600, 100, 10, 18, p["jung"], 31, 30))
    o.append(sground(p, 104))
    o.append(nest(780, 118, 190, p, "back"))
    o.append(f'<g transform="translate(780 114) scale(1.9)">{baby_head(0, -40, 15, p, p["sau"])}<path d="M-6 -26 q-10 4 -14 -4 M6 -26 q10 4 14 -4" stroke="{p["sau"]}" stroke-width="5" stroke-linecap="round" fill="none"/>'
             f'<path d="{shell_paths(0, 0)[0]}" fill="{p["egg"]}"/></g>')
    cap = shell_paths(0, 0)[1]
    o.append(f'<g transform="translate(846 112) rotate(30) scale(1.3)"><path d="{cap}" fill="{p["egg"]}" transform="translate(0 21)"/></g>')
    o.append(nest(780, 118, 190, p, "front"))
    for x, y, r in [(700, 50, 12), (870, 40, 14), (640, 86, 8), (930, 80, 9), (760, 26, 7), (820, 60, 6)]:
        o.append(sparkle(x, y, r))
    return wrap(S, ''.join(o))

def s_open(n):  # the egg wobbling: still whole, rocking in the nest
    p = P(n); o = [sbase(n, ("#6c9ec8", "#b4d4e4", "#eef0d8"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(canopy(0, 1600, 96, 12, 22, p["jung"], 32, 28))
    o.append(sground(p, 100))
    o.append(nest(800, 118, 160, p, "back"))
    o.append(egg(800, 116, 1.9, p, 14))
    for k in (1, 2):
        o.append(f'<path d="M{742 - k * 12} {66 + k * 4} q-8 14 0 28 M{860 + k * 12} {62 + k * 4} q8 14 0 28" fill="none" stroke="{p["pup"] if not n else "#cfd6e6"}" stroke-width="3" stroke-linecap="round" opacity="{.55 - k * .15:.2f}"/>')
    o.append(nest(800, 118, 160, p, "front"))
    return wrap(S, ''.join(o))

def s_lost(n):  # grey ashfall over the valley
    p = P(n); o = [sbase(n, ("#7a7a80", "#a2a2a6", "#c6c4c2"), ("#0a0b10", "#1a1b22", "#2a2b34"), 6)]
    vp = dict(p, volc="#6a6a70" if not n else "#26262e", volc2="#5a5a62" if not n else "#1e1e26")
    o.append(volcano(820, 40, 110, 280, vp, False, glow=False))
    o.append(puff(830, 22, 30, "#8a8a90" if not n else "#3a3a44", .9) + puff(760, 30, 40, "#8a8a90" if not n else "#3a3a44", .7))
    o.append(sground(p, 104, "#7a8070" if not n else "#1c2220"))
    gp = dict(p, tri="#9a9690" if not n else "#3e3c40", tri2="#86827c" if not n else "#323034", frill="#8a8680" if not n else "#38363a", horn="#c8c4bc" if not n else "#5a585c", blush="#9a9690")
    o.append(trike(620, 130, .75, gp, graze=24))
    r = random.Random(4)
    for _ in range(60):
        o.append(f'<circle cx="{r.randint(420, 1240)}" cy="{r.randint(10, 150)}" r="{r.choice([1.5, 2, 2.6])}" fill="{"#e2e0dc" if not n else "#8a8a94"}" opacity=".8"/>')
    return wrap(S, ''.join(o))

def s_dead(n):  # stuck in the tar pit: up to its tummy, arms up, a little worried
    p = P(n); o = [sbase(n, ("#8aa4b4", "#c4ccc6", "#ece4cc"), ("#0c0e14", "#1c1f28", "#30333e"), 10)]
    o.append(canopy(0, 1600, 86, 12, 22, p["jung"], 34, 28))
    o.append(sground(p, 90))
    o.append(f'<ellipse cx="800" cy="120" rx="250" ry="34" fill="#1a1612"/><ellipse cx="780" cy="112" rx="160" ry="10" fill="#3a332c" opacity=".7"/>')
    o.append(f'<g clip-path="url(#tar)"><defs><clipPath id="tar"><rect x="0" y="0" width="1600" height="116"/></clipPath></defs>{thero(780, 168, 1.35, p, wave=True)}</g>')
    o.append(f'<path d="M700 116 Q780 104 880 116" fill="none" stroke="#1a1612" stroke-width="10" stroke-linecap="round"/>')
    for x, y, r in [(900, 108, 6), (660, 116, 5), (930, 120, 4)]: o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#4a4038" stroke-width="2"/>')
    o.append(f'<path d="M854 36 q6 10 0 16 q-6 -6 0 -16Z" fill="#8fd0f0"/>')
    o.append(cycad(1100, 96, .8, p))
    return wrap(S, ''.join(o))

def s_reached(n):  # two long-necks nuzzling, their necks a heart
    p = P(n); o = [sbase(n, ("#f0a86a", "#f6c88a", "#fbe6bc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(canopy(0, 1600, 104, 12, 22, p["jung"], 35, 28))
    o.append(sground(p, 108))
    o.append(sauropod(650, 150, .5, p, head=(220, -190), c1=(110, -260), c2=(250, -260)))
    o.append(sauropod(950, 150, .5, p, flip=True, head=(220, -190), c1=(110, -260), c2=(250, -260)))
    o.append('<path d="M800 52 q-10 -12 -18 -2 q-6 8 18 22 q24 -14 18 -22 q-8 -10 -18 2Z" fill="#f2867a"/>')
    return wrap(S, ''.join(o))

def s_live_noq(n):  # the little one waiting by the water
    p = P(n); o = [sbase(n, ("#e09a5a", "#f2c27a", "#fbe6b8"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(canopy(0, 1600, 94, 12, 22, p["jung"], 36, 28))
    o.append(sground(p, 98))
    o.append(f'<path d="M820 160 Q840 108 1000 106 Q1200 104 1260 160Z" fill="{p["water"]}"/>')
    for x, y, w in [(900, 122, 60), (1020, 136, 80), (960, 150, 40)]: o.append(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{p["water2"]}" opacity=".8"/>')
    o.append(thero(740, 136, 1.2, p, pose="sit"))
    o.append(cycad(560, 122, .9, p, p["leaf2"]))
    return wrap(S, ''.join(o))

def s_vm(n):  # asleep under the moon, curled up, a z or two
    p = P(True); o = [sbase(True, ("#1a2850", "#2a3a6a", "#4a5a8a"), ("#04060f", "#0a0f24", "#141a38"), 50)]
    o.append(moon(1020, 54, 20))
    o.append(canopy(0, 1600, 98, 12, 24, "#0a1a16", 37, 28))
    o.append(sground(p, 104, "#14281f"))
    o.append(sauropod(760, 138, .5, p, head=(150, -40), c1=(140, -90), c2=(190, -40), sleep=True))
    for x, y, s in [(880, 70, 1), (906, 50, 1.3), (938, 26, 1.6)]:
        o.append(f'<path d="M{x} {y} h{10 * s:.0f} l{-10 * s:.0f} {10 * s:.0f} h{10 * s:.0f}" fill="none" stroke="#dfe6f6" stroke-width="{2.4 * s:.1f}" stroke-linejoin="round" stroke-linecap="round" opacity=".85"/>')
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Roar-some to see you, {n}.", "The herd is waiting, {n}.", "Something's hatching today, {n}.",
             "Stomp out a big one, {n}.", "Prehistoric protection, modern rates, {n}.", "Dino-mite day ahead, {n}.",
             "Keep the nest egg safe, {n}.", "Every lead's a fossil worth digging, {n}.", "No lapse in this lagoon, {n}.",
             "Long neck, long reach, {n}.", "Three horns, zero objections, {n}.", "The volcano's warm and so are the leads, {n}.",
             "Tread big, quote bigger, {n}.", "Don't go extinct on a follow-up, {n}.", "Hatch a household today, {n}."]

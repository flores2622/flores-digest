"""The Tropics world: an island lagoon at sunset (and under the moon).
Digest picture 1600x1700 split at 377; page vistas 1600x240; card strips 1600x160."""
import random, math

KEY = "tropics"
NAME = "Tropics"
CATEGORY = "Scenic"   # the group it is listed under in Settings
FONTS = "family=Pacifico&family=Nunito+Sans:wght@400;500;600;700"
DISPLAY = "'Pacifico', Georgia, cursive"
DW = 400               # Pacifico has one weight, and it is a heavy one
BODY = "'Nunito Sans', system-ui, sans-serif"
SKY_BG = (("#e9906e", "#3fb3b4"), ("#080d26", "#0b2734"))

LOOKS = [
    ("lagoon", "Lagoon",
     "--surface: #eaf2ef; --surface-raised: #fbfdfc; --card2: #f0f6f4; --chip: #dcebe6; --text-primary: #10282b; --text-muted: #4f6668; --text-secondary: #3b5356; --grid: #dde9e5; --border: #d0dfda; --border-strong: #afc6bf; --accent: #0b7177; --accent-d: #07555a; --side: #0c3a44; --side2: #125060; --sideInk: #dff1ef; --brand: #f4faf8; --brand2: #f2c879; --rad: 16px;",
     "--surface: #0b1618; --surface-raised: #112023; --card2: #16292c; --chip: #1c3337; --text-primary: #e2f1ef; --text-muted: #94b1ad; --text-secondary: #b1c9c5; --grid: #1c3337; --border: #1f383c; --border-strong: #2e5056; --accent: #4fd1c8; --accent-d: #8ae3dc; --side: #061012; --side2: #0d2226; --sideInk: #dff1ef; --brand: #f4faf8; --brand2: #f2c879;",
     ["#eaf2ef", "#0c3a44", "#f2c879"]),
    ("sunset", "Sunset",
     "--surface: #f7ece3; --surface-raised: #fffaf5; --card2: #faf0e8; --chip: #f4e0d2; --text-primary: #2b1626; --text-muted: #6e5562; --text-secondary: #573d4d; --grid: #f1e1d5; --border: #e9d5c7; --border-strong: #d2b29e; --accent: #b8402a; --accent-d: #8f2f1d; --side: #3a1838; --side2: #52224c; --sideInk: #f7e4ea; --brand: #fff3ea; --brand2: #ffbf5e; --rad: 16px;",
     "--surface: #170d16; --surface-raised: #20141f; --card2: #291a28; --chip: #342132; --text-primary: #f6e9ee; --text-muted: #bba2b1; --text-secondary: #d3bcc8; --grid: #342132; --border: #3b2639; --border-strong: #553852; --accent: #ff9468; --accent-d: #ffb894; --side: #0d060c; --side2: #200f1f; --sideInk: #f7e4ea; --brand: #fff3ea; --brand2: #ffbf5e;",
     ["#f7ece3", "#3a1838", "#ff9468"]),
    ("palm", "Palm",
     "--surface: #efefe2; --surface-raised: #fdfcf5; --card2: #f4f3e8; --chip: #e6e8d6; --text-primary: #18261a; --text-muted: #56634f; --text-secondary: #404e3b; --grid: #e4e5d4; --border: #d8dac6; --border-strong: #b9bea2; --accent: #2b6a35; --accent-d: #1d4f26; --side: #16361f; --side2: #1f4a2b; --sideInk: #e6efdc; --brand: #f6f6e9; --brand2: #e8d48e; --rad: 14px;",
     "--surface: #0e140e; --surface-raised: #151d15; --card2: #1b251b; --chip: #222e21; --text-primary: #e7eee0; --text-muted: #a0ae99; --text-secondary: #bac6b2; --grid: #222e21; --border: #263325; --border-strong: #364834; --accent: #9fd98c; --accent-d: #c0e8b2; --side: #070c07; --side2: #112012; --sideInk: #e6efdc; --brand: #f6f6e9; --brand2: #e8d48e;",
     ["#efefe2", "#16361f", "#e8d48e"]),
]

TOUR = {"k": "Island guide", "next": "Next wave", "back": "Back", "done": "Aloha!", "skip": "Back to shore"}

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(sea="#0d2347", sea2="#16335e", lag="#0f3d52", lag2="#165266", lag3="#1f6474", foam="#9fb6cc",
                    sand="#3d3b52", sand2="#322f45", wet="#2a2a40", isl="#141a38", isl2="#0f1430", jng="#0b1a1c",
                    jng2="#081312", trunk="#2a2018", trunk2="#1d150f", frond="#0f2a22", frond2="#0b1f19",
                    wood="#4a3426", wood2="#33231a", plank="#57402f", thatch="#4a3c2a", thatch2="#382c1e",
                    wall="#5a4a3e", win="#ffcf6a", ink="#f6e7c8", skin="#b8876a", flame="#ffb23a", flame2="#ffe37a",
                    shadow="#000")
    return dict(sea="#2f6f9c", sea2="#4f8db0", lag="#2bb3b5", lag2="#4fcbc4", lag3="#86e0cf", foam="#ffffff",
                sand="#f4e2b6", sand2="#e4c98e", wet="#d9bf8c", isl="#7a5b86", isl2="#5d4673", jng="#2f5b3a",
                jng2="#234a2d", trunk="#8a6340", trunk2="#6b4a2c", frond="#2f7a3e", frond2="#245f30",
                wood="#9a6a40", wood2="#6e4826", plank="#b07d4e", thatch="#c99a55", thatch2="#a87b3c",
                wall="#f2e3c6", win="#5b8ea4", ink="#fff2d6", skin="#d9a27c", flame="#ff9a2a", flame2="#ffe06a",
                shadow="#3a2a10")

DAYSKY = ("#4a5aa8", "#e8877a", "#ffcf86")
NIGHTSKY = ("#050a22", "#101c48", "#24305e")

def N(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffb84a" stop-opacity=".6"/>'
            '<stop offset="1" stop-color="#ffb84a" stop-opacity="0"/></radialGradient>' + extra + '</defs>')

def skyg(n, day=DAYSKY, nt=NIGHTSKY, id="g", y2=1):
    c = nt if n else day
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="{y2}"><stop offset="0" stop-color="{c[0]}"/>'
            f'<stop offset=".6" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

def stars(k, x0, x1, y0, y1, seed):
    r = random.Random(seed); o = []
    for _ in range(k):
        o.append(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([.7, 1, 1.3, 1.8])}" fill="#fff" opacity="{r.choice([.35, .55, .85])}"/>')
    return ''.join(o)

def moon(x, y, r, glow=True):
    g = f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.8}" fill="#e9eefc" opacity=".12"/>' if glow else ''
    return g + (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6f0da"/><circle cx="{N(x - r * .3)}" cy="{N(y - r * .2)}" r="{N(r * .18)}" fill="#e0d8bc"/>'
                f'<circle cx="{N(x + r * .32)}" cy="{N(y + r * .3)}" r="{N(r * .12)}" fill="#e0d8bc"/>')

def sun(x, y, r, c="#fff2c4"):
    return (f'<circle cx="{x}" cy="{y}" r="{N(r * 3)}" fill="#ffd9a0" opacity=".18"/><circle cx="{x}" cy="{y}" r="{N(r * 1.8)}" fill="#ffe2a8" opacity=".3"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')

def gull(x, y, s=1, c="#3a2f4a", k=1):
    return (f'M{N(x - 12 * s)} {N(y - 3 * s * k)} Q{N(x - 6 * s)} {N(y - 8 * s * k)} {x} {y} Q{N(x + 6 * s)} {N(y - 8 * s * k)} {N(x + 12 * s)} {N(y - 3 * s * k)}')

def gullp(x, y, s, c):
    return f'<path d="{gull(x, y, s)}" fill="none" stroke="{c}" stroke-width="{N(2 * s)}" stroke-linecap="round"/>'

def cloud(x, y, w, c="#fff", op=.5, h=8):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{N(w / 2)}" ry="{h}" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{N(x - w * .12)}" cy="{y - h * .8:.0f}" rx="{N(w * .26)}" ry="{h}" fill="{c}" opacity="{op * .8:.2f}"/>')

# ---- movement: SMIL that plays inside a background picture; build.py writes a still copy with every <animate*>
# taken out, so each element's own attributes are its resting state.
def show(times, vals, dur, attr="opacity", begin=0):
    b = f' begin="{begin}s"' if begin else ''
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s"{b} calcMode="discrete" repeatCount="indefinite"/>')

def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {N(x)} {N(b)};{deg} {N(x)} {N(b)};{-deg} {N(x)} {N(b)}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

# ----------------------------------------------------------------- the pieces
def qpt(p0, c, p1, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])

def pl(pts):
    """a polyline's points, whole units, implicit lineto"""
    return " ".join(f"{a:.0f} {b:.0f}" for a, b in pts)

class Palm:
    """a coconut palm: a curved, tapering, ringed trunk from base (x0, y0) to its crown at (x1, y1)"""
    def __init__(self, x0, y0, x1, y1, bend=0.25, w=26):
        self.b, self.t = (x0, y0), (x1, y1)
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
        self.c = ((x0 + x1) / 2 - dy / L * bend * L * .5, (y0 + y1) / 2 + dx / L * bend * L * .5)
        self.w = w
    def at(self, t): return qpt(self.b, self.c, self.t, t)
    def trunk(self, p, rings=10):
        L, R = [], []
        for i in range(13):
            t = i / 12; x, y = self.at(t); x2, y2 = self.at(min(1, t + .01)); x3, y3 = self.at(max(0, t - .01))
            tx, ty = x2 - x3, y2 - y3; m = math.hypot(tx, ty) or 1; nx, ny = -ty / m, tx / m
            ww = self.w * (1 - .45 * t) / 2
            L.append((x + nx * ww, y + ny * ww)); R.append((x - nx * ww, y - ny * ww))
        pts = L + R[::-1]
        o = [f'<path d="M{pl(pts)}Z" fill="{p["trunk"]}"/>']
        sh = R + [self.at(i / 12) for i in range(12, -1, -1)]
        o.append(f'<path d="M{pl(sh)}Z" fill="{p["trunk2"]}" opacity=".7"/>')
        rr = []
        for i in range(1, rings):
            t = i / rings; a, b = L[round(t * 12)], R[round(t * 12)]
            rr.append(f'M{a[0]:.0f} {a[1]:.0f}L{b[0]:.0f} {b[1]:.0f}')
        o.append(f'<path d="{"".join(rr)}" stroke="{p["trunk2"]}" stroke-width="2" opacity=".8"/>')
        return ''.join(o)
    def crown(self, p, L=150, seed=1, angs=(-168, -142, -116, -88, -60, -34, -10, 14, 152, 196), res=10):
        x, y = self.t; r = random.Random(seed); o = []
        for k, a in enumerate(angs):
            ll = L * r.uniform(.85, 1.05) * (.75 if -110 < a < -70 else 1); ra = math.radians(a)
            dx, dy = math.cos(ra), math.sin(ra)
            droop = ll * .7 * abs(dx) ** 1.5 + (ll * .3 if dy > 0 else 0)
            tip = (x + dx * ll, y + dy * ll * .8 + droop)
            ctrl = (x + dx * ll * .6, y + dy * ll * .6 - ll * .12)
            pts_u, pts_d = [], []
            for i in range(res + 1):
                t = i / res; px, py = qpt((x, y), ctrl, tip, t); qx, qy = qpt((x, y), ctrl, tip, min(1, t + .02))
                tx, ty = qx - px, qy - py; m = math.hypot(tx, ty) or 1; nx, ny = -ty / m, tx / m
                ww = ll * .11 * math.sin(math.pi * min(1, t * 1.15)) * (1 if i % 2 else .45)
                pts_u.append((px + nx * ww, py + ny * ww)); pts_d.append((px - nx * ww * .9, py - ny * ww * .9))
            pts = pts_u + pts_d[::-1]
            col = p["frond"] if k % 2 else p["frond2"]
            o.append(f'<path d="M{pl(pts)}Z" fill="{col}"/>')
        o.append(f'<circle cx="{N(x - 6)}" cy="{N(y + 8)}" r="7" fill="#5a3a1c"/><circle cx="{N(x + 6)}" cy="{N(y + 9)}" r="7" fill="#6b4724"/><circle cx="{x}" cy="{N(y + 15)}" r="6.5" fill="#4a2f16"/>')
        return ''.join(o)

def palm(x0, y0, x1, y1, p, L=120, w=18, bend=.25, seed=1, rustle=0, dur=4, delay=0, res=None):
    pm = Palm(x0, y0, x1, y1, bend, w)
    cr = pm.crown(p, L, seed, res=res or (10 if L > 100 else 6))
    if rustle: cr = f'<g>{cr}{sway(x1, y1, rustle, dur, delay)}</g>'
    return pm.trunk(p) + cr

def torch(x, b, h, p, n, ph=0, anim=True, s=1):
    """a bamboo tiki torch: post in the sand at (x, b), the cup on top and its flame"""
    top = b - h; o = []
    if n: o.append(f'<circle cx="{x}" cy="{N(top - 14 * s)}" r="{N(70 * s)}" fill="url(#glow)"/>')
    o.append(f'<rect x="{N(x - 4 * s)}" y="{top}" width="{N(8 * s)}" height="{h}" fill="{p["wood"]}"/>')
    o.append(''.join(f'<rect x="{N(x - 5 * s)}" y="{N(top + k * h / 5)}" width="{N(10 * s)}" height="{N(3 * s)}" fill="{p["wood2"]}"/>' for k in range(1, 5)))
    o.append(f'<path d="M{N(x - 10 * s)} {N(top - 12 * s)} L{N(x + 10 * s)} {N(top - 12 * s)} L{N(x + 6 * s)} {top} L{N(x - 6 * s)} {top}Z" fill="{p["thatch2"]}"/>')
    def fl(hh, lean, ww):
        return f"M{N(x - ww * s)} {N(top - 12 * s)} Q{N(x - (ww + 3) * s)} {N(top - (12 + hh * .5) * s)} {N(x + lean * s)} {N(top - (12 + hh) * s)} Q{N(x + (ww + 3) * s)} {N(top - (12 + hh * .5) * s)} {N(x + ww * s)} {N(top - 12 * s)}Z"
    d = [fl(30, 0, 8), fl(36, 4, 7), fl(27, -3, 8), fl(33, 2, 8)]
    i = [fl(16, 0, 4), fl(20, 2, 3.5), fl(14, -2, 4), fl(18, 1, 4)]
    a1 = f'<animate attributeName="d" values="{";".join(d + d[:1])}" dur="{.9 + ph * .17:.2f}s" repeatCount="indefinite"/>' if anim else ''
    a2 = f'<animate attributeName="d" values="{";".join(i + i[:1])}" dur="{.9 + ph * .17:.2f}s" repeatCount="indefinite"/>' if anim else ''
    o.append(f'<path d="{d[0]}" fill="{p["flame"]}">{a1}</path><path d="{i[0]}" fill="{p["flame2"]}">{a2}</path>')
    return ''.join(o)

def bungalow_def(p, n):
    """an over-water bungalow in local units: waterline at 0, 80 wide"""
    win = p["win"]
    return (f'<g id="bg"><path d="M-34 0V-30M-12 0V-30M12 0V-30M34 0V-30" stroke="{p["wood2"]}" stroke-width="4"/>'
            f'<rect x="-44" y="-34" width="88" height="7" fill="{p["wood"]}"/>'
            f'<rect x="-32" y="-66" width="64" height="33" fill="{p["wall"]}"/><rect x="-32" y="-66" width="10" height="33" fill="#000" opacity=".12"/>'
            f'<rect x="-6" y="-58" width="14" height="25" fill="{win}"/><rect x="14" y="-58" width="12" height="12" fill="{win}"/>'
            f'<path d="M-48 -62 L0 -104 L48 -62Z" fill="{p["thatch"]}"/><path d="M0 -104 L48 -62 L18 -62Z" fill="{p["thatch2"]}"/>'
            f'<path d="M-36 -70 L-4 -98 M-20 -64 L4 -88 M-2 -64 L10 -78" stroke="{p["thatch2"]}" stroke-width="2"/>'
            f'<path d="M-44 -34 h88" stroke="{p["wood2"]}" stroke-width="2"/></g>')

def canoe(p, n, paddle=True):
    """an outrigger canoe in local units, facing left; two paddlers"""
    hull = "#7a3f1e" if not n else "#2e1c12"; ama = "#c9a06a" if not n else "#4a3a2a"
    sk = p["skin"]; s1, s2 = ("#e2552b", "#f2c230") if not n else ("#7a3a2a", "#7a6a2a")
    o = [f'<path d="M-48 -16 Q0 -13 46 -16" stroke="{ama}" stroke-width="5" stroke-linecap="round" fill="none"/>',
         f'<path d="M-34 -5 L-30 -16 M28 -5 L24 -16" stroke="{p["wood2"]}" stroke-width="3"/>',
         f'<path d="M-74 -10 Q-66 2 -40 2 L54 2 Q66 0 70 -8 L62 -6 L-66 -6Z" fill="{hull}"/>']
    for k, (x, sc) in enumerate([(-24, s1), (22, s2)]):
        o.append(f'<path d="M{x - 6} -6 L{x - 5} -26 Q{x} -30 {x + 5} -26 L{x + 6} -6Z" fill="{sc}"/><circle cx="{x}" cy="-33" r="6" fill="{sk}"/>'
                 f'<path d="M{x - 6} -36 Q{x} -42 {x + 6} -36Z" fill="#2a1a10"/>')
        if paddle:
            o.append(f'<g><path d="M{x} -24 L{x - 14} 2" stroke="{p["wood"]}" stroke-width="3"/><path d="M{x - 18} -2 L{x - 10} 0 L{x - 15} 8Z" fill="{p["wood"]}"/>'
                     f'<animateTransform attributeName="transform" type="rotate" values="0 {x} -24;-28 {x} -24;0 {x} -24" dur="1.4s" begin="{k * .35}s" repeatCount="indefinite"/></g>')
    return ''.join(o)

def sailboat(x, wy, s, p, n, sail=None):
    sail = sail or ("#fff4e6" if not n else "#a9aec4")
    hull = "#f6efe2" if not n else "#7e8296"
    return (f'<g transform="translate({x} {wy}) scale({s})"><path d="M0 -10 L0 -130" stroke="#4a3a30" stroke-width="3"/>'
            f'<path d="M4 -126 Q50 -70 56 -20 L4 -18Z" fill="{sail}"/><path d="M-4 -110 Q-30 -64 -40 -22 L-4 -20Z" fill="{sail}" opacity=".85"/>'
            f'<path d="M-58 -14 L62 -14 L48 2 L-46 2Z" fill="{hull}"/><path d="M-56 -10 L60 -10" stroke="#2f6f9c" stroke-width="3"/>'
            f'<path d="M0 -130 L18 -125 L0 -120Z" fill="#e2552b"/></g>')

def person(x, y, s, pose="stand", shirt="#e2552b", skin="#d9a27c", shorts="#2f4f7a", hair="#2a1a10", flip=False, extra=""):
    g = f'<g transform="translate({N(x)} {N(y)}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{skin}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    arm = f'stroke="{skin}" stroke-width="5" fill="none" stroke-linecap="round"'
    head = lambda hx, hy: f'<circle cx="{hx}" cy="{hy}" r="7" fill="{skin}"/><path d="M{hx - 7} {hy - 1} Q{hx} {hy - 12} {hx + 7} {hy - 1} Q{hx} {hy - 6} {hx - 7} {hy - 1}Z" fill="{hair}"/>'
    if pose == "sit":  # sitting on the ground or a log, knees up, facing right
        b = (f'<path d="M-4 -10 L10 -12 L14 0" {leg}/><path d="M-10 -10 L-6 -36 Q2 -40 8 -34 L8 -10Z" fill="{shirt}"/>'
             f'<path d="M-10 -12 h20" stroke="{shorts}" stroke-width="7"/><path d="M6 -32 L16 -20" {arm}/>' + head(0, -44))
    elif pose == "wave":
        b = (f'<path d="M-5 0 L-3 -24 M5 0 L3 -24" {leg}/><path d="M-8 -26 h16 v8 h-16Z" fill="{shorts}"/>'
             f'<path d="M-9 -48 Q0 -52 9 -48 L8 -24 L-8 -24Z" fill="{shirt}"/><path d="M7 -46 L16 -58 L18 -70 M-7 -46 L-11 -30" {arm}/>' + head(0, -57))
    elif pose == "work":  # bent over, both hands down (hauling, raking)
        b = (f'<path d="M-6 0 L-4 -26 M6 0 L4 -26" {leg}/><path d="M-8 -28 h16 v8 h-16Z" fill="{shorts}"/>'
             f'<path d="M-8 -26 L6 -26 L22 -44 Q14 -52 4 -46Z" fill="{shirt}"/><path d="M18 -44 L24 -24 M12 -44 L16 -24" {arm}/>' + head(26, -50))
    elif pose == "surf":  # crouched on a board, arms out
        b = (f'<path d="M-12 0 L-6 -16 L-2 -26 M12 0 L8 -14 L2 -26" {leg}/><path d="M-7 -28 h14 v6 h-14Z" fill="{shorts}"/>'
             f'<path d="M-7 -48 Q2 -52 9 -46 L6 -26 L-6 -26Z" fill="{shirt}"/><path d="M6 -44 L22 -40 M-6 -44 L-22 -50" {arm}/>' + head(4, -56))
    elif pose == "point":
        b = (f'<path d="M-5 0 L-3 -24 M5 0 L3 -24" {leg}/><path d="M-8 -26 h16 v8 h-16Z" fill="{shorts}"/>'
             f'<path d="M-9 -48 Q0 -52 9 -48 L8 -24 L-8 -24Z" fill="{shirt}"/><path d="M7 -46 L20 -50 L30 -54 M-7 -46 L-10 -28" {arm}/>' + head(0, -57))
    elif pose == "hold":  # both arms forward, holding something at chest height
        b = (f'<path d="M-5 0 L-3 -24 M5 0 L3 -24" {leg}/><path d="M-8 -26 h16 v8 h-16Z" fill="{shorts}"/>'
             f'<path d="M-9 -48 Q0 -52 9 -48 L8 -24 L-8 -24Z" fill="{shirt}"/><path d="M7 -46 L18 -36 M-7 -46 L8 -36" {arm}/>' + head(0, -57))
    else:  # stand
        b = (f'<path d="M-5 0 L-3 -24 M5 0 L3 -24" {leg}/><path d="M-8 -26 h16 v8 h-16Z" fill="{shorts}"/>'
             f'<path d="M-9 -48 Q0 -52 9 -48 L8 -24 L-8 -24Z" fill="{shirt}"/><path d="M7 -46 L11 -26 M-7 -46 L-11 -26" {arm}/>' + head(0, -57))
    return g + b + extra + '</g>'

def sign(x, y, w, h, text, p, fs=16, posts=36, sub=None):
    o = [f'<rect x="{N(x - w * .36)}" y="{y}" width="6" height="{h + posts}" fill="{p["wood2"]}"/><rect x="{N(x + w * .36 - 6)}" y="{y}" width="6" height="{h + posts}" fill="{p["wood2"]}"/>',
         f'<rect x="{N(x - w / 2)}" y="{y}" width="{w}" height="{h}" rx="5" fill="{p["wood"]}" stroke="{p["wood2"]}" stroke-width="3"/>',
         f'<text x="{x}" y="{N(y + h / 2 + fs * .36 - (fs * .5 if sub else 0))}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["ink"]}" letter-spacing="1">{text}</text>']
    if sub: o.append(f'<text x="{x}" y="{N(y + h / 2 + fs * .8)}" text-anchor="middle" font-family="Georgia, serif" font-size="{N(fs * .62)}" fill="{p["ink"]}" opacity=".9">{sub}</text>')
    return ''.join(o)

def ripples(k, x0, x1, y0, y1, seed, c="#fff", op=.35, avoid=None):
    r = random.Random(seed); o = []
    for _ in range(k):
        x = r.randint(x0, x1); y = r.randint(y0, y1)
        if avoid and avoid(x, y): continue
        w = r.randint(8, 20) * (1 + (y - y0) / max(1, y1 - y0))
        o.append(f'M{x} {y}q{N(w / 2)} -3 {N(w)} 0')
    return f'<path d="{"".join(o)}" fill="none" stroke="{c}" stroke-opacity="{op}" stroke-width="2" stroke-linecap="round"/>'

def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(240, body + SHADE)

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
HZ = 408   # the sea's horizon, just under the split so the far islands run on into the leaderboard

def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    lag = (f'<linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["lag"]}"/><stop offset=".55" stop-color="{p["lag2"]}"/>'
           f'<stop offset="1" stop-color="{p["lag3"]}"/></linearGradient>'
           f'<linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["sea"]}"/><stop offset="1" stop-color="{p["sea2"]}"/></linearGradient>'
           '<radialGradient id="sunr" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe7a8" stop-opacity=".55"/><stop offset="1" stop-color="#ffb070" stop-opacity="0"/></radialGradient>'
           '<radialGradient id="mg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    a(defs(skyg(n, id="sky") + lag + bungalow_def(p, n)))
    a(f'<rect width="{W}" height="{HZ + 4}" fill="url(#sky)"/>')
    SX, SY = 800, 112
    if n:
        a(stars(60, 0, W, 0, 330, 3))
        a('<ellipse cx="800" cy="120" rx="320" ry="150" fill="url(#mg)"/>' + moon(SX, SY, 34))
        # a shooting star now and then
        a('<g opacity="0"><path d="M0 0 L-60 22" stroke="#fff" stroke-width="2" stroke-linecap="round"/>'
          '<animateMotion path="M1180 40 L1020 100" dur="9s" keyPoints="0;0;1;1" keyTimes="0;.6;.68;1" calcMode="linear" repeatCount="indefinite"/>'
          + show(["0", ".6", ".68"], ["0", "1", "0"], 9) + '</g>')
    else:
        a(f'<ellipse cx="{SX}" cy="{SY + 40}" rx="520" ry="260" fill="url(#sunr)"/>' + sun(SX, SY, 52))
        # long lit streaks of cloud across the sunset
        for x, y, w in [(520, 150, 300), (1080, 92, 260), (1300, 150, 220), (230, 118, 200)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="7" fill="#ffd2a8" opacity=".55"/><ellipse cx="{x + 30}" cy="{y + 6}" rx="{w // 3}" ry="4" fill="#c86a7a" opacity=".45"/>')
        # gulls gliding past the sun, flapping
        for i, (x, y, sc) in enumerate([(900, 70, 1.3), (930, 56, 1), (1130, 128, 1.1)]):
            flap = f'<animate attributeName="d" values="{gull(x, y, sc)};{gull(x, y, sc, k=-.3)};{gull(x, y, sc)}" dur=".9s" begin="{i * .3:.1f}s" repeatCount="indefinite"/>'
            a(f'<g><path d="{gull(x, y, sc)}" fill="none" stroke="#3a2f4a" stroke-width="{N(2.2 * sc)}" stroke-linecap="round">{flap}</path>'
              f'<animateTransform attributeName="transform" type="translate" values="0 0;{-50 - i * 14} -8;{-100 - i * 26} 4;{-50 - i * 14} 10;0 0" dur="{10 + i * 1.5}s" repeatCount="indefinite"/></g>')
    # the volcano island far off to the left, a wisp of cloud caught on its peak
    vc = p["isl"]; vc2 = p["isl2"]
    a(f'<path d="M40 {HZ} C210 360 300 170 368 76 L384 84 L398 72 L414 80 C470 170 580 350 780 {HZ}Z" fill="{vc}"/>')
    a(f'<path d="M398 72 L414 80 C470 170 580 350 780 {HZ} L560 {HZ} C500 300 440 170 398 72Z" fill="{vc2}" opacity=".7"/>')
    a(f'<path d="M370 84 Q380 120 372 160 M392 82 Q400 130 410 170" stroke="{vc2}" stroke-width="5" fill="none" opacity=".6"/>')
    wc = "#ffe1c8" if not n else "#5a6488"
    a(f'<ellipse cx="452" cy="58" rx="80" ry="9" fill="{wc}" opacity=".7"/><ellipse cx="420" cy="66" rx="42" ry="8" fill="{wc}" opacity=".8"/><ellipse cx="520" cy="50" rx="46" ry="5" fill="{wc}" opacity=".5"/>')
    # a low island on the right horizon
    a(f'<path d="M1060 {HZ} Q1120 {HZ - 26} 1220 {HZ - 30} Q1320 {HZ - 34} 1420 {HZ - 14} L1460 {HZ}Z" fill="{vc}"/>')
    # the open sea out past the reef, the sun's (moon's) path on it
    a(f'<rect x="0" y="{HZ}" width="{W}" height="80" fill="url(#sg)"/>')
    gl = "#ffe6a8" if not n else "#f2eedc"
    r = random.Random(4); gls = []
    for k in range(16):
        y = HZ + 4 + k * 8; w = 40 + k * 7 + r.randint(-10, 10); x = SX + r.randint(-30, 30)
        gls.append(f'M{x - w // 2} {y}h{w}')
    a(f'<path d="{"".join(gls)}" stroke="{gl}" stroke-width="3" opacity="{.75 if not n else .55}" stroke-linecap="round"/>')
    # the reef: a line of white surf breaking across the lagoon's mouth
    RY = 488
    a(f'<path d="M0 {RY - 2} Q400 {RY - 8} 800 {RY - 4} T1600 {RY - 4} L1600 {RY + 12} L0 {RY + 12}Z" fill="{p["lag"]}"/>')
    r = random.Random(7); sf = []
    x = -20
    while x < W:
        w = r.randint(40, 110); sf.append(f'M{x} {RY + r.randint(-3, 3)}q{w // 2} -7 {w} 0'); x += w + r.randint(14, 40)
    a(f'<path d="{"".join(sf)}" stroke="{p["foam"]}" stroke-width="5" fill="none" stroke-linecap="round" opacity=".85"/>')
    # the lagoon inside the reef
    a(f'<rect x="0" y="{RY + 6}" width="{W}" height="180" fill="url(#lg)"/>')
    a(f'<path d="M0 {RY + 30} Q300 {RY + 40} 600 {RY + 30}" stroke="{p["lag"]}" stroke-width="10" opacity=".35" fill="none"/>')
    a(ripples(26, 0, W, RY + 20, 590, 5, op=.3 if not n else .18, avoid=lambda x, y: 470 < x < 1140 and y > 540))
    if n:  # the moon's path carries on across the lagoon (stops short of the stage)
        a(f'<path d="M760 506h80M744 520h112M770 532h60" stroke="{gl}" stroke-width="3" opacity=".35" stroke-linecap="round"/>')
    # the sailboat at anchor on the lagoon, right
    a(sailboat(1238, 548, .9, p, n))
    a(f'<ellipse cx="1240" cy="551" rx="62" ry="4" fill="#000" opacity=".15"/>')
    # a dolphin breaking the surface out past the reef now and then
    dol = "#3a5a7a" if not n else "#5a7090"
    a('<g transform="translate(1000 458)"><g opacity="0">'
      f'<path d="M-20 0 Q-8 -10 12 -5 L22 -3 L12 0 Q-6 5 -20 2 L-28 -4 L-26 2Z M-2 -8 L4 -16 L6 -7Z" fill="{dol}"/>'
      '<animateMotion path="M0 0 Q45 -46 90 0" rotate="auto" dur="9s" keyPoints="0;0;1;1" keyTimes="0;.2;.36;1" calcMode="linear" repeatCount="indefinite"/>'
      + show(["0", ".2", ".36"], ["0", "1", "0"], 9) + '</g>'
      f'<g opacity="0"><ellipse cx="0" cy="2" rx="14" ry="3" fill="none" stroke="{p["foam"]}" stroke-width="2"/><ellipse cx="90" cy="2" rx="14" ry="3" fill="none" stroke="{p["foam"]}" stroke-width="2"/>'
      + show(["0", ".19", ".42"], ["0", "1", "0"], 9) + '</g></g>')
    # the over-water bungalows on stilts, far to near, and the boardwalk that joins them to the deck
    bw = []
    for x, y, s in [(268, 530, .66), (360, 552, .8), (444, 578, .92)]:
        if n: bw.append(f'<path d="M{x - 2} {y + 4} v{N(30 * s)}" stroke="{p["win"]}" stroke-width="{N(10 * s)}" opacity=".25"/>')
        bw.append(f'<use href="#bg" transform="translate({x} {y}) scale({s})"/>')
    walk = "M196 540 L440 594 L540 618"
    a(f'<path d="M220 546v14M290 561v14M360 576v14M430 592v14M490 606v14" stroke="{p["wood2"]}" stroke-width="3"/>')
    a(''.join(bw))
    a(f'<path d="{walk}" stroke="{p["wood2"]}" stroke-width="14" fill="none" stroke-linejoin="round"/><path d="{walk}" stroke="{p["plank"]}" stroke-width="10" fill="none" stroke-linejoin="round"/>')
    a(f'<path d="{walk}" stroke="{p["wood2"]}" stroke-width="10" fill="none" stroke-dasharray="1.5 7" opacity=".7"/>')
    # the outrigger canoe paddling across the lagoon (behind the stage, above it)
    a(f'<g transform="translate(1060 524) scale(1.2)"><g>{canoe(p, n)}'
      '<animateTransform attributeName="transform" type="translate" values="0 0;-330 0" dur="12s" repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="12s" repeatCount="indefinite"/></g></g>')
    # the beach: wet sand at the water's edge, dry sand above it
    shore = "M0 668 C200 650 380 624 560 612 L1040 612 C1220 622 1420 650 1600 664"
    a(f'<path d="{shore} L1600 {H} L0 {H}Z" fill="{p["wet"]}"/>')
    a(f'<path d="M0 684 C200 666 380 640 560 628 L1040 628 C1220 638 1420 666 1600 680 L1600 {H} L0 {H}Z" fill="{p["sand"]}"/>')
    # the waves lapping up the beach on either side of the deck, and running back
    for k, (seg, dur) in enumerate([("M0 668 C200 650 380 624 520 614", 4.5), ("M1080 614 C1220 622 1420 650 1600 664", 5.2)]):
        a(f'<g><path d="{seg}" stroke="{p["foam"]}" stroke-width="5" fill="none" opacity=".85" stroke-linecap="round"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;0 9;0 0" dur="{dur}s" begin="{k * .8}s" repeatCount="indefinite" calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1"/>'
          f'<animate attributeName="opacity" values="1;.4;1" dur="{dur}s" begin="{k * .8}s" repeatCount="indefinite"/></g>')
    r = random.Random(9); dots = []
    for _ in range(46):
        x = r.randint(0, W); y = r.randint(700, 880)
        if 440 < x < 1170: continue
        dots.append(f'M{x} {y}h3')
    a(f'<path d="{"".join(dots)}" stroke="{p["sand2"]}" stroke-width="3" stroke-linecap="round"/>')
    # the deck the podium stands on: planks in perspective, set on the sand at the water's edge
    a(f'<path d="M500 598 L1110 598 L1170 828 L440 828Z" fill="#000" opacity=".12" transform="translate(8 8)"/>')
    a(f'<path d="M500 598 L1110 598 L1170 828 L440 828Z" fill="{p["plank"]}"/>')
    pl = []
    for k in range(1, 12):
        f = (k / 12) ** 1.25; y = 598 + 230 * f; xl = 500 - 60 * f; xr = 1110 + 60 * f
        pl.append(f'M{N(xl)} {N(y)}H{N(xr)}')
    a(f'<path d="{"".join(pl)}" stroke="{p["wood2"]}" stroke-width="2" opacity=".55"/>')
    a(f'<path d="M500 598 L1110 598" stroke="{p["wood2"]}" stroke-width="5"/><path d="M440 828 L1170 828 L1170 842 L440 842Z" fill="{p["wood2"]}"/>')
    a(f'<path d="M500 598 L440 828 M1110 598 L1170 828" stroke="{p["wood2"]}" stroke-width="4"/>')
    if n: a('<ellipse cx="805" cy="700" rx="330" ry="90" fill="#ffb84a" opacity=".07"/>')
    # the sign on the beach, left, below the boardwalk
    a(sign(310, 712, 196, 46, "NO LAPSE LAGOON", p, 16, 34, "PARADISE PROTECTED"))
    # the tiki torches framing the deck, flames on their posts
    for i, (x, b, h, s) in enumerate([(468, 700, 96, .85), (1142, 700, 96, .85), (424, 850, 196, 1.1), (1186, 850, 196, 1.1)]):
        a(torch(x, b, h, p, n, i, s=s))
    # the coconut palms: two leaning out over the left, two framing the right with a hammock slung between them
    a(f'<g>{palm(70, 880, 40, 92, p, 165, 34, -.12, 11, 3, 4.5)}{sway(70, 880, .7, 7)}</g>')
    a(f'<g>{palm(176, 900, 228, 150, p, 140, 30, .14, 12, 3.5, 5, 1)}{sway(176, 900, .6, 8, 1)}</g>')
    pc = Palm(1380, 850, 1302, 124, .16, 32); pd = Palm(1570, 870, 1535, 64, -.12, 34)
    a(pc.trunk(p) + f'<g>{pc.crown(p, 150, 13)}{sway(1302, 124, 3, 4.2, .5)}</g>')
    a(pd.trunk(p) + f'<g>{pd.crown(p, 165, 14)}{sway(1535, 64, 2.5, 5.4, 1.4)}</g>')
    A = pc.at(.25); B = pd.at(.25)
    ax, ay = A; bx, by = B; mx = (ax + bx) / 2
    def bed(dx): return f'M{N(ax)} {N(ay)} Q{N(mx + dx)} {N(max(ay, by) + 96)} {N(bx)} {N(by)}'
    hm = "#e2552b" if not n else "#7a3a3a"; hm2 = "#f2c230" if not n else "#7a6a3a"
    a(f'<path d="{bed(0)}" stroke="{hm}" stroke-width="12" fill="none" stroke-linecap="round">'
      f'<animate attributeName="d" values="{bed(0)};{bed(16)};{bed(0)};{bed(-16)};{bed(0)}" dur="5s" repeatCount="indefinite"/></path>')
    a(f'<g transform="translate({N(mx)} {N(max(ay, by) + 40)}) scale(1.45)"><g>'
      f'<path d="M-46 -2 Q0 12 40 -6" stroke="{p["skin"]}" stroke-width="7" fill="none" stroke-linecap="round"/>'
      f'<path d="M-30 2 Q0 14 18 2 L16 -6 Q0 2 -30 -6Z" fill="#2f8f9a"/><circle cx="-50" cy="-8" r="7" fill="{p["skin"]}"/>'
      f'<path d="M-62 -10 Q-50 -26 -38 -10Z" fill="{p["thatch"]}"/><path d="M-66 -10 h32" stroke="{p["thatch"]}" stroke-width="3"/>'
      f'<animateTransform attributeName="transform" type="translate" values="0 0;8 -2;0 0;-8 -2;0 0" dur="5s" repeatCount="indefinite"/></g></g>')
    a(f'<path d="{bed(0)}" stroke="{hm2}" stroke-width="3" fill="none" stroke-dasharray="6 6" opacity=".9">'
      f'<animate attributeName="d" values="{bed(0)};{bed(16)};{bed(0)};{bed(-16)};{bed(0)}" dur="5s" repeatCount="indefinite"/></path>')
    a(f'<path d="M{N(ax)} {N(ay)} l-4 6 M{N(bx)} {N(by)} l4 6" stroke="{hm}" stroke-width="3"/>')
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def base(n, sky=DAYSKY, nt=NIGHTSKY, star=40):
    return defs(skyg(n, day=sky, nt=nt)) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 150, 7) if n else '')

def sea_band(p, y, n, c=None, op=.3):
    return (f'<rect x="0" y="{y}" width="1600" height="{V - y}" fill="{c or p["sea"]}"/>'
            + ripples(20, 0, 1600, y + 6, min(V, y + 60), 3, op=op if not n else .15))

def corners(p, n, c=None):
    """dark jungle in the corners the title and line sit on"""
    c = c or p["jng2"]
    r = random.Random(2); o = [f'<path d="M0 168 Q220 158 470 190 L470 240 L0 240Z" fill="{c}"/><path d="M1600 174 Q1320 168 1040 198 L1040 240 L1600 240Z" fill="{c}"/>']
    for x0, x1, y in ((0, 440, 182), (1070, 1600, 190)):
        for _ in range(9):
            x = r.randint(x0, x1); rr = r.randint(16, 30)
            if x0 == 0: yy = y - (440 - x) * .03
            else: yy = y - (x - 1070) * .025
            o.append(f'<circle cx="{x}" cy="{N(yy)}" r="{rr}" fill="{c}"/>')
    return ''.join(o)

def edge_palms(p, left=True, right=True, seed=30):
    o = []
    if left: o.append(palm(70, 236, 30, 46, p, 70, 14, -.15, seed, res=5) + palm(160, 240, 210, 70, p, 60, 12, .2, seed + 1, res=5))
    if right: o.append(palm(1520, 240, 1570, 44, p, 72, 14, .15, seed + 2, res=5) + palm(1430, 240, 1388, 80, p, 58, 12, -.2, seed + 3, res=5))
    return ''.join(o)

def v_sales(n):  # surfers riding a big wave
    p = P(n); o = [base(n, sky=("#5162b0", "#ef9a7c", "#ffd88e"))]
    o.append(moon(1250, 62, 22) if n else sun(1250, 70, 26))
    o.append(f'<path d="M1080 150 Q1180 138 1300 146 L1300 152 L1080 152Z" fill="{p["isl"]}"/>')
    o.append(sea_band(p, 150, n, p["sea"]))
    wv = p["lag"]; wv2 = p["lag2"]; fm = p["foam"]
    # the curling wave: its face, the lip pitching over, the white water at its foot
    o.append(f'<path d="M380 240 C440 200 520 120 640 86 C740 58 820 70 860 108 C820 96 780 104 770 128 C820 150 900 176 1100 186 C1200 192 1300 200 1400 240Z" fill="{wv}"/>')
    o.append(f'<path d="M560 230 C600 180 660 120 740 96 C700 130 690 170 720 230Z" fill="{wv2}" opacity=".7"/>')
    o.append(f'<path d="M640 86 C740 58 820 70 860 108 C840 104 820 104 806 110 C780 90 720 84 650 96Z" fill="{fm}"/>')
    o.append(f'<path d="M820 120 q10 -8 22 -2 M836 132 q12 -6 20 0" stroke="{fm}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M380 240 C450 222 520 214 600 226 C680 210 760 222 820 214 L860 240Z" fill="{fm}" opacity=".9"/>')
    # two surfers on the face
    o.append(f'<path d="M846 168 L938 156 Q948 160 940 166 L850 176Z" fill="#f2c230"/>' + person(892, 164, 1.0, "surf", "#e2552b", p["skin"], "#1f3f6a"))
    o.append(f'<path d="M1050 186 L1126 178 Q1134 182 1128 186 L1052 194Z" fill="#fff4e6"/>' + person(1088, 184, .85, "surf", "#2f8f9a", p["skin"], "#7a2a2a", flip=True))
    o.append(f'<path d="M940 166 Q990 170 1040 182" stroke="{fm}" stroke-width="3" fill="none" opacity=".7"/>')
    if not n: o.append(gullp(480, 60, 1.1, "#3a2f4a") + gullp(510, 48, .8, "#3a2f4a"))
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

def v_messages(n):  # the beach shack, its radio on the counter, the aerial on the roof
    p = P(n); o = [base(n)]
    o.append(moon(300, 60, 20) if n else sun(300, 92, 24))
    o.append(sea_band(p, 138, n, p["lag"]))
    o.append(f'<path d="M0 178 Q800 160 1600 176 L1600 240 L0 240Z" fill="{p["sand"]}"/>')
    sx = 640
    # the aerial on the roof, waves going out
    o.append(f'<path d="M{sx + 180} 70 L{sx + 180} 22 M{sx + 170} 34 h20 M{sx + 166} 46 h28" stroke="#4a3a30" stroke-width="3"/>')
    for k, r_ in enumerate((14, 26, 38)):
        o.append(f'<path d="M{sx + 180 - r_} {28 - r_ * .3:.0f} Q{sx + 180} {28 - r_ * 1.1:.0f} {sx + 180 + r_} {28 - r_ * .3:.0f}" stroke="#fff" stroke-width="3" fill="none" opacity="{.8 - k * .2:.1f}"/>')
    # the shack on its posts
    o.append(f'<rect x="{sx}" y="96" width="250" height="100" fill="{p["wood"]}"/>')
    o.append(''.join(f'<rect x="{sx + k * 25}" y="96" width="2" height="100" fill="{p["wood2"]}"/>' for k in range(1, 10)))
    o.append(f'<path d="M{sx - 30} 102 L{sx + 30} 62 L{sx + 220} 62 L{sx + 280} 102Z" fill="{p["thatch"]}"/><path d="M{sx - 30} 102 h310 l-8 10 h-294Z" fill="{p["thatch2"]}"/>')
    if n: o.append(f'<circle cx="{sx + 125}" cy="140" r="90" fill="url(#glow)"/>')
    o.append(f'<rect x="{sx + 24}" y="118" width="202" height="44" fill="{"#3a2a1c" if not n else "#ffcf6a"}"/>')
    o.append(f'<rect x="{sx + 14}" y="160" width="222" height="10" fill="{p["wood2"]}"/>')
    # the radio on the counter, a coconut drink beside it
    o.append(f'<rect x="{sx + 100}" y="136" width="56" height="26" rx="4" fill="#d8402a"/><circle cx="{sx + 114}" cy="149" r="8" fill="#3a2a1c"/><rect x="{sx + 128}" y="142" width="22" height="5" fill="#fff4e6"/>'
             f'<path d="M{sx + 146} 136 L{sx + 160} 112" stroke="#4a3a30" stroke-width="2"/><circle cx="{sx + 190}" cy="154" r="8" fill="#6b4724"/><path d="M{sx + 192} 146 l6 -12" stroke="#f2c230" stroke-width="2"/>')
    o.append(person(sx + 60, 160, .9, "hold", "#2f8f9a", p["skin"]))
    o.append(f'<rect x="{sx + 20}" y="74" width="210" height="20" rx="3" fill="{p["wood2"]}"/><text x="{sx + 125}" y="89" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["ink"]}" letter-spacing="2">SHORE THING COVERAGE</text>')
    o.append(f'<path d="M{sx + 10} 196 v-26 M{sx + 240} 196 v-26" stroke="{p["wood2"]}" stroke-width="6"/>')
    # a surfboard leaning on the shack
    o.append(f'<path d="M{sx + 262} 196 Q{sx + 270} 120 {sx + 290} 104 Q{sx + 300} 130 {sx + 284} 196Z" fill="#f2c230"/><path d="M{sx + 286} 108 L{sx + 276} 196" stroke="#e2552b" stroke-width="3"/>')
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

def v_coaching(n):  # the fire circle on the beach at dusk
    p = P(n); o = [base(n, sky=("#3a3a86", "#c46a7a", "#f2a070"), nt=("#040818", "#0c1638", "#1c2450"))]
    o.append(moon(1260, 56, 20) if n else sun(1260, 118, 22, "#ffd28a"))
    o.append(sea_band(p, 120, n, p["sea"]))
    o.append(f'<path d="M0 150 Q800 136 1600 150 L1600 240 L0 240Z" fill="{p["sand"]}"/>')
    cx, cy = 800, 190
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="220" ry="40" fill="#ffb84a" opacity="{.18 if not n else .25}"/><circle cx="{cx}" cy="{cy - 30}" r="110" fill="url(#glow)"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy + 4}" rx="44" ry="10" fill="#5a5048"/>')
    o.append(f'<path d="M{cx - 34} {cy + 2} L{cx + 30} {cy - 8} M{cx - 30} {cy - 8} L{cx + 34} {cy + 2}" stroke="{p["wood2"]}" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 26} {cy - 2} Q{cx - 30} {cy - 40} {cx - 4} {cy - 74} Q{cx + 2} {cy - 50} {cx + 12} {cy - 64} Q{cx + 32} {cy - 34} {cx + 24} {cy - 2}Z" fill="{p["flame"]}"/>'
             f'<path d="M{cx - 12} {cy - 2} Q{cx - 14} {cy - 26} {cx} {cy - 44} Q{cx + 14} {cy - 26} {cx + 12} {cy - 2}Z" fill="{p["flame2"]}"/>')
    for x, y in [(cx - 6, cy - 92), (cx + 18, cy - 104), (cx - 20, cy - 116)]: o.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#ffd27a"/>')
    # logs as seats, the circle round the fire; the coach on his feet, explaining
    for x0, x1 in ((560, 700), (900, 1040)):
        o.append(f'<rect x="{x0}" y="{cy + 2}" width="{x1 - x0}" height="16" rx="8" fill="{p["wood"]}"/><ellipse cx="{x1}" cy="{cy + 10}" rx="6" ry="8" fill="{p["thatch"]}"/>')
    o.append(person(600, cy + 4, 1.0, "sit", "#e2552b", p["skin"]) + person(660, cy + 4, 1.0, "sit", "#f2c230", p["skin"], hair="#5a3a1c"))
    o.append(person(950, cy + 4, 1.0, "sit", "#2f8f9a", p["skin"], flip=True) + person(1010, cy + 4, 1.0, "sit", "#7a5ab0", p["skin"], flip=True, hair="#8a5a2a"))
    o.append(person(880, cy + 10, 1.25, "point", "#fff4e6", p["skin"], "#2f6a3a", flip=True))
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

def v_roleplay(n):  # the luau stage: a thatched stage, torches, a performer and the crowd
    p = P(n); o = [base(n, sky=("#4a4a9a", "#e47e7a", "#ffc47e"))]
    o.append(moon(320, 58, 20) if n else sun(320, 90, 24))
    o.append(sea_band(p, 130, n, p["sea"]))
    o.append(f'<path d="M0 164 Q800 150 1600 164 L1600 240 L0 240Z" fill="{p["sand"]}"/>')
    x0, x1 = 600, 1000
    o.append(f'<rect x="{x0}" y="168" width="{x1 - x0}" height="22" fill="{p["wood2"]}"/><rect x="{x0}" y="164" width="{x1 - x0}" height="8" fill="{p["plank"]}"/>')
    o.append(f'<path d="M{x0 + 10} 166 V70 M{x1 - 10} 166 V70" stroke="{p["wood"]}" stroke-width="10"/>')
    o.append(f'<path d="M{x0 - 40} 74 L{x0 + 60} 34 L{x1 - 60} 34 L{x1 + 40} 74Z" fill="{p["thatch"]}"/><path d="M{x0 - 40} 74 h{x1 - x0 + 80} l-10 12 h-{x1 - x0 + 60}Z" fill="{p["thatch2"]}"/>')
    o.append(''.join(f'<path d="M{x} 86 v10" stroke="{p["thatch2"]}" stroke-width="4"/>' for x in range(x0 - 26, x1 + 30, 14)))
    # string of lanterns hung under the eave
    o.append(f'<path d="M{x0 + 10} 92 Q800 116 {x1 - 10} 92" stroke="#3a2a1c" stroke-width="2" fill="none"/>')
    for k in range(9):
        t = (k + 1) / 10; x = x0 + 10 + (x1 - x0 - 20) * t; y = 92 + 24 * 4 * t * (1 - t) * .98
        if n: o.append(f'<circle cx="{N(x)}" cy="{N(y + 6)}" r="16" fill="url(#glow)"/>')
        o.append(f'<circle cx="{N(x)}" cy="{N(y + 6)}" r="5" fill="{["#ffcf6a", "#ff8a5a", "#7fe0cf"][k % 3]}"/>')
    o.append(f'<rect x="{x0 + 110}" y="46" width="180" height="20" rx="4" fill="{p["wood2"]}"/><text x="800" y="61" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["ink"]}" letter-spacing="2">OPEN MIC LUAU</text>')
    # the performer with a ukulele, a dancer in a grass skirt
    o.append(person(740, 164, 1.0, "hold", "#e2552b", p["skin"], extra='<ellipse cx="12" cy="-34" rx="8" ry="5" fill="#c9893a"/><path d="M14 -36 L30 -44" stroke="#6b4724" stroke-width="3"/>'))
    o.append(person(860, 164, 1.0, "wave", "#f2c230", p["skin"], "#5aa04a", hair="#2a1a10", extra='<path d="M-10 -26 L-12 -6 M-6 -26 L-6 -6 M-2 -26 L0 -6 M2 -26 L4 -6 M6 -26 L8 -6 M10 -26 L12 -6" stroke="#5aa04a" stroke-width="3"/>'))
    for i, x in enumerate((560, 1040)): o.append(torch(x, 196, 90, p, n, i, anim=False, s=.8))
    # the crowd from behind, heads and shoulders
    for k, x in enumerate(range(520, 1100, 44)):
        o.append(f'<path d="M{x - 18} 240 Q{x - 16} 214 {x} 212 Q{x + 16} 214 {x + 18} 240Z" fill="{["#5a3a5a", "#3a4a6a", "#4a5a3a"][k % 3] if not n else "#14121e"}"/><circle cx="{x}" cy="204" r="10" fill="{"#3a2a20" if not n else "#100c10"}"/>')
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

def v_rphistory(n):  # beach movie night: a screen hung between two palms, the crowd on blankets
    p = P(n); o = [base(n, sky=("#2a3470", "#7a5a8a", "#d48a7a"), nt=("#03061a", "#0a1236", "#18204a"), star=60)]
    if not n: o.append(stars(16, 0, 1600, 0, 80, 8))
    o.append(moon(1300, 50, 18))
    o.append(sea_band(p, 132, n, p["sea"], .15))
    o.append(f'<path d="M0 160 Q800 146 1600 160 L1600 240 L0 240Z" fill="{p["sand"]}"/>')
    pa = Palm(560, 220, 590, 30, .08, 16); pb = Palm(1040, 220, 1010, 30, -.08, 16)
    o.append(pa.trunk(p) + pa.crown(p, 60, 41, res=6) + pb.trunk(p) + pb.crown(p, 60, 42, res=6))
    a1 = pa.at(.75); b1 = pb.at(.75); a2 = pa.at(.28); b2 = pb.at(.28)
    # ropes from the trunks to the screen's corners
    o.append(f'<path d="M{N(a1[0])} {N(a1[1])} L650 66 M{N(b1[0])} {N(b1[1])} L950 66 M{N(a2[0])} {N(a2[1])} L650 162 M{N(b2[0])} {N(b2[1])} L950 162" stroke="#d8c8a8" stroke-width="2"/>')
    o.append(f'<rect x="646" y="62" width="308" height="104" fill="#f4f0e6"/>')
    scr = "#7fd0e8" if not n else "#5aa8c8"
    o.append(f'<rect x="654" y="70" width="292" height="88" fill="{scr}"/><path d="M654 128 C720 100 780 90 820 104 C800 110 790 120 800 134 C860 130 900 136 946 140 V158 H654Z" fill="#2bb3b5"/>')
    o.append(f'<path d="M820 104 C800 110 790 120 800 134" stroke="#fff" stroke-width="3" fill="none"/>' + person(760, 132, .5, "surf", "#e2552b", "#d9a27c"))
    o.append('<path d="M664 80 l12 7 l-12 7z" fill="#fff" opacity=".9"/><rect x="654" y="152" width="292" height="6" fill="#000" opacity=".3"/><rect x="654" y="152" width="170" height="6" fill="#e2552b"/>')
    o.append('<path d="M800 210 L654 72 L946 72Z" fill="#fff" opacity=".05"/><rect x="784" y="206" width="32" height="16" rx="3" fill="#3a3a44"/><circle cx="800" cy="210" r="4" fill="#fff8d8"/>')
    for x, c in [(600, "#c8402a"), (900, "#2f6f9c"), (1100, "#f2c230")]:
        o.append(f'<path d="M{x - 60} 222 L{x + 60} 222 L{x + 76} 240 L{x - 76} 240Z" fill="{c}" opacity="{.85 if not n else .45}"/>')
    for x in (570, 630, 870, 930, 1080):
        o.append(f'<path d="M{x - 14} 236 Q{x - 12} 214 {x} 212 Q{x + 12} 214 {x + 14} 236Z" fill="{"#3a2a3a" if not n else "#12101a"}"/><circle cx="{x}" cy="204" r="9" fill="{"#2a1e20" if not n else "#0e0a0e"}"/>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_training(n):  # snorkelling over the reef: the surface above, the reef and a turtle below
    p = P(n)
    wt = ("#5fd0d0", "#2b98b0", "#16607e") if not n else ("#14506a", "#0c3450", "#06203a")
    o = [defs(f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{wt[0]}"/><stop offset=".5" stop-color="{wt[1]}"/><stop offset="1" stop-color="{wt[2]}"/></linearGradient>')]
    o.append(f'<rect width="1600" height="{V}" fill="url(#g)"/>')
    # sun rays coming down through the water
    o.append(''.join(f'<path d="M{x} 40 L{x + 40} 40 L{x + 140} 240 L{x + 60} 240Z" fill="#fff" opacity="{.08 if not n else .04}"/>' for x in (420, 640, 900, 1120)))
    # the surface, and the snorkellers lying on it, fins and masks
    o.append(f'<path d="M0 40 Q200 34 400 40 T800 40 T1200 40 T1600 40 L1600 0 L0 0Z" fill="{"#f2b07e" if not n else "#101a3a"}"/>')
    o.append(f'<path d="M0 40 Q200 34 400 40 T800 40 T1200 40 T1600 40" stroke="#fff" stroke-width="3" fill="none" opacity=".6"/>')
    for x, sh in ((640, "#e2552b"), (900, "#f2c230")):
        o.append(f'<g transform="translate({x} 52)"><path d="M-50 -4 L30 -6" stroke="{p["skin"]}" stroke-width="12" stroke-linecap="round"/><path d="M-30 -8 L10 -10 L12 2 L-30 4Z" fill="{sh}"/>'
                 f'<path d="M-50 -4 L-74 -12 L-76 4Z" fill="#2f4f7a"/><circle cx="38" cy="-4" r="9" fill="{p["skin"]}"/><rect x="38" y="-2" width="12" height="9" rx="3" fill="#7fe0f0" stroke="#2a2a2a" stroke-width="2"/>'
                 f'<path d="M36 -12 L36 -30" stroke="#f2c230" stroke-width="4" stroke-linecap="round"/><path d="M20 -2 L40 14" stroke="{p["skin"]}" stroke-width="5" stroke-linecap="round"/></g>')
    o.append(''.join(f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="#fff" stroke-width="1.5" opacity=".6"/>' for x, y in [(690, 70), (694, 84), (952, 74), (948, 90)]))
    # the reef
    o.append(reef(p, n, 172, 7))
    # a sea turtle gliding over it
    tc = "#6a8a3a" if not n else "#2e4a2a"
    o.append(f'<g transform="translate(1130 120) rotate(-8)"><ellipse rx="36" ry="22" fill="{tc}"/><path d="M-22 -8 L0 -18 L22 -8 L18 10 L-18 10Z" fill="#8aa84a" opacity="{.8 if not n else .4}"/>'
             f'<ellipse cx="42" cy="-2" rx="11" ry="8" fill="#9aae6a"/><path d="M14 -18 L36 -38 L26 -14Z M14 18 L34 36 L24 14Z M-24 -14 L-40 -26 L-30 -10Z M-24 14 L-40 24 L-30 10Z" fill="#9aae6a"/></g>')
    r = random.Random(3)
    for _ in range(8):
        x = r.randint(480, 1180); y = r.randint(90, 150)
        o.append(f'<g transform="translate({x} {y})"><path d="M-10 0 Q0 -6 10 0 Q0 6 -10 0Z M-10 0 L-16 -5 L-16 5Z" fill="{r.choice(["#ffb23a", "#ff6a4a", "#f2e04a", "#7fd0ff"])}"/></g>')
    o.append(f'<path d="M0 190 Q220 180 470 200 L470 240 L0 240Z M1600 196 Q1320 190 1040 206 L1040 240 L1600 240Z" fill="{"#0c3a4e" if not n else "#041624"}"/>')
    return vwrap(''.join(o))

def reef(p, n, y, seed, bloom=False):
    r = random.Random(seed); o = []
    rock = "#7a6a6a" if not n else "#26283a"
    o.append(f'<path d="M0 {y} Q200 {y - 16} 400 {y - 6} T800 {y - 10} T1200 {y - 4} T1600 {y - 12} L1600 240 L0 240Z" fill="{rock}"/>')
    cols = (["#ff7a8a", "#ffb23a", "#c86ad0", "#ff5a4a", "#f2e04a", "#7fe0cf"] if bloom else ["#e8786a", "#d8a04a", "#9a6ab0", "#c8564a"])
    if n: cols = ["#8a4a5a", "#8a6a3a", "#5a4a7a", "#7a3a3a", "#6a6a3a"]
    for _ in range(26 if bloom else 18):
        x = r.randint(380, 1240); b = y + r.randint(-6, 20); c = r.choice(cols); k = r.random()
        if k < .35:  # branching coral
            h = r.randint(30, 60)
            o.append(f'<path d="M{x} {b} V{b - h} M{x} {b - h * .5:.0f} L{x - 16} {b - h * .8:.0f} M{x} {b - h * .4:.0f} L{x + 18} {b - h * .75:.0f} M{x - 16} {b - h * .8:.0f} V{b - h - 6}" stroke="{c}" stroke-width="7" stroke-linecap="round" fill="none"/>')
        elif k < .6:  # brain coral
            rr = r.randint(14, 26)
            o.append(f'<path d="M{x - rr} {b} A{rr} {rr} 0 0 1 {x + rr} {b}Z" fill="{c}"/><path d="M{x - rr * .6:.0f} {b - 4} q{rr * .3:.0f} -10 {rr * .6:.0f} 0 t{rr * .6:.0f} 0" stroke="#000" stroke-opacity=".15" stroke-width="2" fill="none"/>')
        elif k < .8:  # sea fan
            h = r.randint(36, 64)
            o.append(f'<path d="M{x} {b} Q{x - h * .6:.0f} {b - h * .6:.0f} {x - h * .3:.0f} {b - h} Q{x} {b - h * 1.1:.0f} {x + h * .3:.0f} {b - h} Q{x + h * .6:.0f} {b - h * .6:.0f} {x} {b}Z" fill="{c}" opacity=".85"/>')
        else:  # anemone / kelp
            h = r.randint(26, 50)
            o.append(f'<path d="M{x} {b} q-8 -{h // 2} 2 -{h} M{x + 6} {b} q8 -{h // 2} 0 -{h - 6} M{x - 6} {b} q-10 -{h // 3} -6 -{h - 10}" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    return ''.join(o)

def v_map(n, athena=False):  # the treasure-style island chart, laid out on a dark teak table
    tbl = "#3a2416" if not n else "#140c08"; tbl2 = "#2e1c10" if not n else "#0e0805"
    paper = "#f0dfb4" if not n else "#a8946a"; paper2 = "#d9c08a" if not n else "#8a7650"
    ink = "#5a3a1e" if not n else "#3a2410"; sea = "#a8d2c8" if not n else "#6a8a80"
    land = "#d8c08a" if not n else "#9a8256"; jungle = "#7a9a5a" if not n else "#56683e"
    route = "#c8402a" if not athena else "#2a7a6a"
    o = [f'<rect width="1600" height="{V}" fill="{tbl}"/>']
    o.append(''.join(f'<rect x="0" y="{y}" width="1600" height="3" fill="{tbl2}"/>' for y in range(10, V, 26)))
    if n: o.append('<circle cx="800" cy="120" r="420" fill="#ffcf6a" opacity=".1"/>')
    # the chart: a torn-edged sheet, sea all over it, one island in the middle
    o.append(f'<path d="M372 34 L520 28 L700 36 L900 30 L1080 36 L1232 30 L1238 120 L1230 214 L1060 210 L880 216 L700 210 L520 216 L366 210 L372 120Z" fill="{paper2}" transform="translate(6 6)" opacity=".5"/>')
    o.append(f'<path d="M372 34 L520 28 L700 36 L900 30 L1080 36 L1232 30 L1238 120 L1230 214 L1060 210 L880 216 L700 210 L520 216 L366 210 L372 120Z" fill="{paper}"/>')
    o.append(f'<path d="M390 50 L1214 50 L1214 196 L390 196Z" fill="{sea}" opacity=".55"/>')
    o.append(ripples(16, 400, 1200, 58, 190, 6, c=ink, op=.25))
    isl = "M470 150 C470 96 560 70 660 80 C740 60 820 66 900 76 C1000 70 1110 88 1130 124 C1150 166 1060 186 960 178 C880 190 780 184 700 180 C600 190 470 190 470 150Z"
    o.append(f'<path d="{isl}" fill="{land}" stroke="{ink}" stroke-width="2.5"/>')
    o.append(f'<path d="M560 140 C580 110 640 100 700 108 C760 96 840 100 900 110 C980 100 1040 116 1050 136 C1000 150 900 156 800 150 C700 160 600 160 560 140Z" fill="{jungle}" opacity=".7"/>')
    o.append(f'<path d="M790 116 L814 84 L838 116Z" fill="{paper2}" stroke="{ink}" stroke-width="2"/>')
    for x, y in [(520, 128), (612, 96), (980, 96), (1092, 128)]:
        o.append(f'<path d="M{x} {y + 10} q2 -10 0 -16 M{x} {y - 6} q-8 -2 -12 4 M{x} {y - 6} q8 -2 12 4 M{x} {y - 6} q-4 -8 -10 -8 M{x} {y - 6} q4 -8 10 -8" stroke="{ink}" stroke-width="2" fill="none"/>')
    pts = [(560, 150), (720, 124), (900, 156), (1060, 134)]
    d = f'M{pts[0][0]} {pts[0][1]} C600 150 640 128 {pts[1][0]} {pts[1][1]} S840 170 {pts[2][0]} {pts[2][1]} S1010 130 {pts[3][0]} {pts[3][1]}'
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="4" stroke-dasharray="10 8" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        if i == 3:
            o.append(f'<path d="M{x - 10} {y - 10} L{x + 10} {y + 10} M{x + 10} {y - 10} L{x - 10} {y + 10}" stroke="{route}" stroke-width="5" stroke-linecap="round"/>')
        else:
            o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{route}" stroke="{paper}" stroke-width="3"/>')
        ty = y - 18
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-style="italic" font-size="22" fill="{ink}" stroke="{paper}" stroke-width="4" paint-order="stroke">{t}</text>')
    # the compass rose and a little ship
    o.append(f'<g transform="translate(1160 84)"><circle r="24" fill="none" stroke="{ink}" stroke-width="2"/><path d="M0 -30 L6 0 L0 30 L-6 0Z M-30 0 L0 6 L30 0 L0 -6Z" fill="{ink}" opacity=".85"/>'
             f'<path d="M0 -30 L6 0 L-6 0Z" fill="{route}"/><text y="-34" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="{ink}">N</text></g>')
    o.append(f'<g transform="translate(440 84)" fill="none" stroke="{ink}" stroke-width="2"><path d="M-18 6 L18 6 L12 14 L-12 14Z" fill="{paper2}"/><path d="M0 6 V-22 M2 -20 Q16 -8 14 2 L2 2Z"/></g>')
    o.append(f'<text x="800" y="70" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="14" fill="{ink}" opacity=".8">'
             + ('the service passage' if athena else 'the sales passage') + '</text>')
    return vwrap(''.join(o))

def v_service(n):  # the boat dock crew: tying up, loading, coiling a line
    p = P(n); o = [base(n, sky=("#4f62b0", "#e99a80", "#ffd890"))]
    o.append(moon(1280, 56, 20) if n else sun(1280, 80, 24))
    o.append(sea_band(p, 120, n, p["lag"]))
    # the dock, out from the left, on piles
    o.append(f'<path d="M420 196 L1180 176 L1180 188 L420 210Z" fill="{p["wood2"]}"/><path d="M420 190 L1180 170 L1180 178 L420 198Z" fill="{p["plank"]}"/>')
    o.append(''.join(f'<rect x="{x}" y="{178 - (x - 420) * .026:.0f}" width="8" height="{60:.0f}" fill="{p["wood2"]}"/>' for x in range(450, 1180, 120)))
    o.append(''.join(f'<rect x="{x - 2}" y="{164 - (x - 420) * .026:.0f}" width="12" height="20" rx="3" fill="{p["wood"]}"/>' for x in (560, 860, 1140)))
    # the launch tied alongside
    o.append(f'<path d="M700 150 L1000 144 L980 168 L720 172Z" fill="{"#f6efe2" if not n else "#7e8296"}"/><path d="M704 154 L996 148" stroke="#2f6f9c" stroke-width="4"/>'
             f'<rect x="800" y="118" width="80" height="30" fill="#e8e0d0"/><path d="M790 120 h100 l-6 -14 h-88Z" fill="#2f8f9a"/>')
    o.append(f'<path d="M708 152 Q680 166 666 {170 - 6}" stroke="#e8d8a8" stroke-width="3" fill="none"/>')
    # the crew
    o.append(person(640, 186, 1.0, "work", "#2f8f9a", p["skin"], "#2f4f7a"))
    o.append(person(940, 176, 1.0, "hold", "#f2c230", p["skin"], extra='<rect x="4" y="-46" width="22" height="16" fill="#a8753a"/>'))
    o.append(person(1060, 174, 1.0, "point", "#e2552b", p["skin"], flip=True))
    o.append(f'<rect x="1000" y="160" width="26" height="16" fill="#a8753a"/><rect x="1004" y="146" width="20" height="14" fill="#8a5a2a"/>')
    o.append(f'<ellipse cx="610" cy="186" rx="14" ry="5" fill="none" stroke="#e8d8a8" stroke-width="3"/>')
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # the reef in bloom
    p = P(n)
    wt = ("#7fe0d8", "#36aec4", "#1a6e8e") if not n else ("#14506a", "#0c3450", "#06203a")
    o = [defs(f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{wt[0]}"/><stop offset=".5" stop-color="{wt[1]}"/><stop offset="1" stop-color="{wt[2]}"/></linearGradient>')]
    o.append(f'<rect width="1600" height="{V}" fill="url(#g)"/>')
    o.append(''.join(f'<path d="M{x} 0 L{x + 50} 0 L{x + 170} 240 L{x + 80} 240Z" fill="#fff" opacity="{.1 if not n else .04}"/>' for x in (380, 620, 880, 1120)))
    o.append(reef(p, n, 168, 11, True))
    r = random.Random(5)
    for _ in range(14):
        x = r.randint(460, 1200); y = r.randint(60, 140); s = r.choice([.8, 1, 1.3]); c = r.choice(["#ffb23a", "#ff6a4a", "#f2e04a", "#ffffff", "#7fd0ff"] if not n else ["#8a7a4a", "#7a5a4a", "#6a8aa0"])
        o.append(f'<g transform="translate({x} {y}) scale({s})"><path d="M-10 0 Q0 -7 10 0 Q0 7 -10 0Z M-10 0 L-17 -6 L-17 6Z" fill="{c}"/><circle cx="5" cy="-1" r="1.4" fill="#222"/></g>')
    o.append(''.join(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="none" stroke="#fff" stroke-width="1.5" opacity=".5"/>' for x, y, rr in [(700, 60, 3), (706, 44, 2), (1010, 70, 3), (1004, 52, 2.4)]))
    o.append(f'<path d="M0 190 Q220 180 470 200 L470 240 L0 240Z M1600 196 Q1320 190 1040 206 L1040 240 L1600 240Z" fill="{"#0c3a4e" if not n else "#041624"}"/>')
    return vwrap(''.join(o))

def v_claims(n):  # after the tropical storm: palms bent over, fronds down, the crew clearing
    p = P(n); o = [base(n, sky=("#5a6a84", "#a4aab4", "#e2c8a8"), nt=("#04060f", "#10162a", "#20283e"), star=18)]
    for x in (300, 760, 1240): o.append(f'<ellipse cx="{x}" cy="50" rx="230" ry="26" fill="{"#7a8498" if not n else "#1a2034"}"/>')
    if not n: o.append('<circle cx="1120" cy="96" r="34" fill="#fff2c4" opacity=".55"/><path d="M1060 60 L1100 200 M1140 60 L1170 200" stroke="#fff" stroke-width="30" opacity=".06"/>')
    o.append(sea_band(p, 140, n, "#4a7a90" if not n else "#0c2034", .2))
    o.append(f'<path d="M0 168 Q800 156 1600 168 L1600 240 L0 240Z" fill="{p["sand"]}"/>')
    for x, y, w in [(560, 206, 80), (1000, 214, 70)]: o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="{"#9ab4c8" if not n else "#2a3a5a"}" opacity=".8"/>')
    # the palms, bent hard over by the wind and still leaning
    o.append(palm(640, 190, 830, 78, p, 70, 16, .35, 51))
    o.append(palm(1120, 200, 1260, 96, p, 62, 14, .3, 52))
    # fronds down on the sand, a coconut or two
    fd = p["frond2"]
    for x, y, rot in [(720, 206, -6), (900, 212, 8), (1180, 214, -4)]:
        o.append(f'<g transform="translate({x} {y}) rotate({rot})"><path d="M-50 0 Q0 -10 50 -2" stroke="{p["thatch2"]}" stroke-width="3" fill="none"/>'
                 + ''.join(f'<path d="M{k} {-4 + abs(k) * .04:.0f} l-8 -10 M{k} {-4 + abs(k) * .04:.0f} l-8 8" stroke="{fd}" stroke-width="3"/>' for k in range(-40, 50, 10)) + '</g>')
    o.append('<circle cx="600" cy="212" r="7" fill="#5a3a1c"/><circle cx="614" cy="216" r="6" fill="#6b4724"/>')
    # the crew: one hauling fronds to the barrow, one raking
    o.append(person(960, 212, 1.0, "work", "#e98a2a", p["skin"], "#3a4a3a"))
    o.append(f'<g transform="translate(1040 214)"><path d="M-30 -24 L30 -24 L22 -4 L-22 -4Z" fill="#2f6a8a"/><circle cx="-12" cy="0" r="8" fill="#222"/><path d="M22 -20 L50 -34" stroke="#5a5a5a" stroke-width="4"/>'
             f'<path d="M-24 -24 Q0 -40 26 -24" stroke="{fd}" stroke-width="6" fill="none"/></g>')
    o.append(person(520, 210, 1.0, "hold", "#e98a2a", p["skin"], "#3a4a3a", flip=True))
    o.append(f'<path d="M506 172 L470 212 M462 208 L480 216" stroke="{p["wood"]}" stroke-width="4"/>')
    o.append('<path d="M760 214 L770 188 L780 214Z" fill="#e98a2a"/><rect x="762" y="202" width="16" height="4" fill="#fff"/>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the resort's open-air lobby: a great thatched roof on posts, the desk, the sea beyond
    p = P(n); o = [base(n)]
    o.append(moon(800, 120, 18) if n else sun(800, 132, 22))
    o.append(sea_band(p, 146, n, p["sea"]))
    o.append(f'<rect x="0" y="190" width="1600" height="50" fill="{p["plank"]}"/>' + ''.join(f'<path d="M{x} 190 L{x - (x - 800) * .3:.0f} 240" stroke="{p["wood2"]}" stroke-width="2" opacity=".5"/>' for x in range(420, 1220, 60)))
    # the roof: a tall hipped thatch spanning the lobby, its beams and posts
    o.append(f'<path d="M340 76 L800 18 L1260 76 L1240 90 L360 90Z" fill="{p["thatch"]}"/><path d="M800 18 L1260 76 L1240 90 L1000 90Z" fill="{p["thatch2"]}" opacity=".8"/>')
    o.append(''.join(f'<path d="M{x} 86 v8" stroke="{p["thatch2"]}" stroke-width="4"/>' for x in range(370, 1240, 16)))
    o.append(f'<rect x="360" y="90" width="880" height="8" fill="{p["wood2"]}"/>')
    for x in (430, 620, 980, 1170): o.append(f'<rect x="{x - 7}" y="96" width="14" height="96" fill="{p["wood"]}"/>')
    # ceiling fans and lanterns hung from the beam
    for x in (700, 900):
        o.append(f'<path d="M{x} 98 v12" stroke="#2a2a2a" stroke-width="2"/><ellipse cx="{x}" cy="112" rx="34" ry="3" fill="#3a2a1c"/>')
    for x in (520, 1080):
        if n: o.append(f'<circle cx="{x}" cy="120" r="34" fill="url(#glow)"/>')
        o.append(f'<path d="M{x} 98 v12" stroke="#2a2a2a" stroke-width="2"/><rect x="{x - 7}" y="110" width="14" height="18" rx="3" fill="{"#ffcf6a" if n else "#f2c27a"}" stroke="#3a2a1c" stroke-width="2"/>')
    # the reception desk, the sign over it, a clerk and a guest
    o.append(f'<rect x="680" y="156" width="240" height="38" fill="{p["wood"]}"/><rect x="672" y="150" width="256" height="8" fill="{p["wood2"]}"/>')
    o.append(f'<rect x="680" y="50" width="240" height="20" rx="3" fill="{p["wood2"]}"/><text x="800" y="65" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["ink"]}" letter-spacing="2">PARADISE PROTECTED</text>')
    o.append(person(760, 154, .8, "stand", "#2f8f9a", p["skin"]) + person(980, 192, 1.0, "wave", "#e2552b", p["skin"], flip=True))
    o.append(f'<rect x="1004" y="168" width="26" height="24" rx="4" fill="#4a5a7a"/>')
    # potted palms either side of the desk
    for x in (560, 1120):
        o.append(f'<path d="M{x - 16} 192 L{x + 16} 192 L{x + 12} 170 L{x - 12} 170Z" fill="#c8643a"/>' + palm(x, 170, x + 4, 120, p, 34, 6, .1, x, res=4))
    o.append(edge_palms(p) + corners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "catch the wave: premium riding in"],
    "messages": ["Texts & Emails", "the beach shack: every reply on the air"],
    "coaching": ["Coaching", "the fire circle: every call, talked over"],
    "roleplay": ["Role Play", "the luau stage: practice the pitch"],
    "rphistory": ["Session History", "movie night on the beach: every session, replayed"],
    "training": ["Training", "snorkel the reef: learn what's down there"],
    "blueprint": ["Apollo's Road Map", "the island chart, in plain words"],
    "athenamap": ["Athena's Road Map", "the service chart, in plain words"],
    "service": ["Service Digest", "the dock crew: keeping the fleet afloat"],
    "renewals": ["Renewals", "the reef in bloom: what came back"],
    "claims": ["Claims", "after the storm: clearing the beach"],
    "commercial": ["Commercial Center", "the open-air lobby: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=30):
    return defs(skyg(n, day=day, nt=nt)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 90, 21) if n else '')

def cap(t): return f'<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="24" fill="#fff" stroke="#000" stroke-opacity=".35" stroke-width="3" paint-order="stroke">{t}</text>'

def s_sold(n):  # fireworks over the lagoon
    p = P(True if n else False)
    o = [sbase(n, ("#2a2f6a", "#7a4a7a", "#e2806a"), ("#03061a", "#0c1438", "#1a2250"), 24)]
    o.append(f'<rect x="0" y="104" width="1600" height="56" fill="{"#2a7a90" if not n else "#0c2a40"}"/>')
    o.append(palm(380, 160, 350, 60, p, 50, 10, -.1, 61) + palm(1180, 160, 1210, 66, p, 46, 10, .1, 62))
    for cx, cy, rr, c in [(640, 54, 40, "#ffd27a"), (820, 40, 50, "#ff6a8a"), (990, 60, 38, "#7fe0f0")]:
        rays = ''.join(f'M{N(cx + rr * .3 * math.cos(k * math.pi / 8))} {N(cy + rr * .3 * math.sin(k * math.pi / 8))}L{N(cx + rr * math.cos(k * math.pi / 8))} {N(cy + rr * math.sin(k * math.pi / 8))}' for k in range(16))
        o.append(f'<path d="{rays}" stroke="{c}" stroke-width="3" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="4" fill="#fff"/>')
        o.append(f'<path d="M{cx - 20} {112 + (cy - 40) // 6}h40M{cx - 12} {120 + (cy - 40) // 6}h24" stroke="{c}" stroke-width="3" opacity=".5" stroke-linecap="round"/>')
    o.append('<path d="M700 160 L700 104 M940 160 L940 104" stroke="#000" opacity="0"/>')
    o.append(cap("PARADISE"))
    return wrap(S, ''.join(o))

def s_open(n):  # a sailboat heading out past the reef, wake behind it
    p = P(n); o = [sbase(n, ("#5a6ab0", "#ef9e80", "#ffd890"), NIGHTSKY)]
    o.append(moon(1060, 56, 14) if n else sun(1060, 80, 18))
    o.append(f'<rect x="0" y="88" width="1600" height="72" fill="{p["sea"]}"/>')
    o.append(f'<path d="M0 116 Q400 110 800 114 T1600 114 L1600 160 L0 160Z" fill="{p["lag"]}"/>')
    o.append(ripples(10, 300, 1200, 120, 150, 4, op=.4 if not n else .2))
    o.append(sailboat(840, 104, .55, p, n))
    o.append(f'<path d="M800 106 Q700 112 560 110 M806 104 Q720 104 600 98" stroke="{p["foam"]}" stroke-width="2.5" fill="none" opacity=".7"/>')
    o.append(cap("SETTING SAIL"))
    return wrap(S, ''.join(o))

def s_lost(n):  # a grey squall coming over the lagoon
    p = P(n); o = [sbase(n, ("#5a606c", "#8a909a", "#b4b8bc"), ("#07080e", "#141822", "#22262f"), 6)]
    cl = "#4a505c" if not n else "#181b24"
    for x in (420, 760, 1100): o.append(f'<ellipse cx="{x}" cy="44" rx="230" ry="34" fill="{cl}"/>')
    o.append(f'<path d="{"".join(f"M{x} 60 l-24 60" for x in range(440, 1220, 26))}" stroke="#c8ccd4" stroke-width="2" opacity=".5"/>')
    o.append(f'<rect x="0" y="104" width="1600" height="56" fill="{"#5a7080" if not n else "#101c28"}"/>')
    o.append(ripples(16, 300, 1200, 110, 150, 5, c="#d8dde4", op=.5))
    o.append(palm(1150, 160, 1250, 80, P(n), 46, 10, .35, 63))
    o.append('<path d="M760 60 L742 92 L756 92 L740 120" stroke="#f2f2d8" stroke-width="3" fill="none" opacity=".8"/>')
    o.append(cap("SQUALL"))
    return wrap(S, ''.join(o))

def s_dead(n):  # a canoe beached, its paddle snapped
    p = P(n); o = [sbase(n, ("#8a9aac", "#c4c8cc", "#e8dcc4"), ("#0a0c14", "#1a1d28", "#2c2f3c"), 10)]
    o.append(f'<rect x="0" y="80" width="1600" height="30" fill="{p["sea"]}"/><path d="M0 104 Q800 92 1600 104 L1600 160 L0 160Z" fill="{p["sand"]}"/>')
    o.append(f'<path d="M0 104 Q800 92 1600 104" stroke="{p["foam"]}" stroke-width="3" fill="none" opacity=".7"/>')
    hull = "#7a3f1e" if not n else "#2e1c12"
    o.append(f'<g transform="translate(860 116) rotate(5) scale(1.5)"><path d="M-110 -14 Q-96 4 -60 4 L80 4 Q100 2 106 -10 L92 -8 L-98 -8Z" fill="{hull}"/>'
             f'<path d="M-60 -8 L-56 -34 M50 -8 L46 -34" stroke="{p["wood2"]}" stroke-width="4"/><path d="M-70 -34 Q0 -30 66 -34" stroke="{"#c9a06a" if not n else "#4a3a2a"}" stroke-width="6" fill="none"/></g>')
    o.append(f'<path d="M500 128 L580 112" stroke="{p["wood"]}" stroke-width="7" stroke-linecap="round"/><path d="M580 112 L592 104 L588 118Z" fill="{p["wood"]}"/>'
             f'<path d="M604 120 L650 124" stroke="{p["wood"]}" stroke-width="7" stroke-linecap="round"/><path d="M648 114 L690 120 L676 136 L650 132Z" fill="{p["wood"]}"/>')
    o.append(cap("BEACHED"))
    return wrap(S, ''.join(o))

def hammock_between(p, n, x0, x1, top, sag, who, col="#e2552b"):
    pa = Palm(x0, 160, x0 - 20, top, -.1, 14); pb = Palm(x1, 160, x1 + 20, top, .1, 14)
    a = pa.at(.4); b = pb.at(.4); mx = (a[0] + b[0]) / 2; my = max(a[1], b[1]) + sag
    o = [pa.trunk(p), pb.trunk(p)]
    o.append(f'<path d="M{N(a[0])} {N(a[1])} Q{N(mx)} {N(my + sag * .6)} {N(b[0])} {N(b[1])}" stroke="{col}" stroke-width="9" fill="none" stroke-linecap="round"/>')
    if who:
        o.append(f'<g transform="translate({N(mx)} {N(my)})"><path d="M-40 -8 Q0 4 36 -10" stroke="{p["skin"]}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                 f'<path d="M-24 -4 Q0 6 16 -4 L14 -12 Q0 -4 -24 -12Z" fill="{who}"/><circle cx="-44" cy="-14" r="7" fill="{p["skin"]}"/><path d="M-51 -15 Q-44 -26 -37 -15Z" fill="#2a1a10"/></g>')
    return ''.join(o), (mx, my)

def s_reached(n):  # two people in hammocks, talking
    p = P(n); o = [sbase(n, ("#5f72b8", "#efa88a", "#ffe0a0"), NIGHTSKY)]
    o.append(f'<rect x="0" y="84" width="1600" height="30" fill="{p["lag"]}"/><path d="M0 110 Q800 100 1600 110 L1600 160 L0 160Z" fill="{p["sand"]}"/>')
    h1, m1 = hammock_between(p, n, 520, 720, 40, 22, "#2f8f9a")
    h2, m2 = hammock_between(p, n, 860, 1060, 40, 22, "#f2c230", "#2f8f9a")
    o.append(h1 + h2)
    o.append('<path d="M640 40 q8 -14 24 -14 h24 q16 0 16 14 q0 12 -16 12 h-28 l-10 8z" fill="#fff" opacity=".94"/><path d="M960 36 q-8 -14 -24 -14 h-24 q-16 0 -16 14 q0 12 16 12 h28 l10 8z" fill="#fff" opacity=".94"/>')
    o.append(''.join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#2f6f7a"/>' for x, y in [(658, 39), (672, 39), (686, 39), (914, 35), (928, 35), (942, 35)]))
    o.append(cap("TALK STORY"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # a lone surfer sitting on the board, waiting for a wave on a flat sea
    p = P(n); o = [sbase(n, ("#5162b0", "#ef9a7c", "#ffd88e"), NIGHTSKY)]
    o.append(moon(1000, 52, 14) if n else sun(1000, 84, 20))
    o.append(f'<rect x="0" y="92" width="1600" height="68" fill="{p["sea"]}"/>')
    o.append(ripples(8, 300, 1200, 100, 150, 9, op=.3 if not n else .15))
    o.append(f'<path d="M736 112 L864 108 Q874 110 864 114 L740 118Z" fill="#f2c230"/>')
    o.append(f'<g transform="translate(800 112)"><path d="M-8 0 L-14 -26 Q-6 -32 4 -28 L4 0Z" fill="#e2552b"/><path d="M-6 -2 L10 4 L12 14" stroke="{p["skin"]}" stroke-width="6" fill="none" stroke-linecap="round"/>'
             f'<path d="M0 -24 L14 -8" stroke="{p["skin"]}" stroke-width="5" stroke-linecap="round"/><circle cx="-6" cy="-36" r="7" fill="{p["skin"]}"/><path d="M-13 -37 Q-6 -48 1 -37Z" fill="#2a1a10"/></g>')
    o.append(f'<path d="M730 118 Q800 124 870 116" stroke="{p["foam"]}" stroke-width="2" fill="none" opacity=".6"/>')
    o.append(cap("WAITING"))
    return wrap(S, ''.join(o))

def s_vm(n):  # an empty hammock under the moon
    p = P(True); o = [sbase(True, ("#141c44", "#22306a", "#3a4a80"), ("#03050f", "#0a0f26", "#141a3c"), 50)]
    if not n: o.append(stars(20, 0, 1600, 0, 80, 22))
    o.append(moon(1040, 52, 16))
    o.append(f'<rect x="0" y="86" width="1600" height="28" fill="#0d2347"/><path d="M1000 92h80M990 100h100M1010 108h60" stroke="#f2eedc" stroke-width="2" opacity=".4"/>')
    o.append(f'<path d="M0 110 Q800 100 1600 110 L1600 160 L0 160Z" fill="#2c2a40"/>')
    h, _ = hammock_between(p, True, 660, 900, 40, 26, None, "#6a3a3a")
    o.append(h)
    o.append(cap("NO ANSWER"))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Aloha, {n}.", "Surf's up, {n}. So are the leads.", "Catch the next wave, {n}.", "Island time is quote time, {n}.",
             "Paradise protected, {n}.", "Shore thing, {n}. Let's write some.", "The tide's coming in, {n}.",
             "Sun's out, phones out, {n}.", "Paddle hard today, {n}.", "No lapse in the lagoon, {n}.",
             "Hang loose and close, {n}.", "Every wave's a new lead, {n}.", "Sunscreen on, headset on, {n}.",
             "Bundle the whole island, {n}.", "Clear skies, full coverage, {n}."]

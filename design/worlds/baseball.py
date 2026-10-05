"""The Baseball world: one ballpark at golden hour, and the same park under the lights at night.
Colour looks, fonts, the Digest picture, page banners and card strips. No real teams, leagues, players or
parks -- insurance puns on the wall, the scoreboard and the banners."""
import random, math

KEY = "baseball"
NAME = "Baseball"
CATEGORY = "Sports"   # the group it is listed under in Settings
FONTS = "family=Alfa+Slab+One&family=Barlow:wght@400;500;600;700"
DISPLAY = "'Alfa Slab One', Georgia, serif"
DW = 400               # Alfa Slab One has one weight, and it is already heavy
BODY = "'Barlow', system-ui, sans-serif"
SKY_BG = (("#f0b878", "#5f9d3e"), ("#060b1e", "#2c6a30"))
TOUR = {"k": "Scouting report", "next": "Next pitch", "back": "Back", "done": "Home run!", "skip": "Leave the park"}

LOOKS = [
    ("ballpark", "Ballpark",
     "--surface: #edf1ea; --surface-raised: #fcfdfb; --card2: #f2f6ef; --chip: #e1e9dc; --text-primary: #14231a; --text-muted: #546557; --text-secondary: #3d4f42; --grid: #dfe7da; --border: #d3dccd; --border-strong: #b2c1aa; --accent: #1f6e36; --accent-d: #165428; --side: #163f26; --side2: #1e5032; --sideInk: #e4f0e6; --brand: #f6f8f2; --brand2: #f0c75a; --rad: 12px;",
     "--surface: #0c140f; --surface-raised: #131e17; --card2: #19271e; --chip: #203126; --text-primary: #e6efe7; --text-muted: #9cb1a2; --text-secondary: #b8c8bb; --grid: #203126; --border: #233629; --border-strong: #31493a; --accent: #7fd08f; --accent-d: #a6e0b0; --side: #070e0a; --side2: #102017; --sideInk: #e4f0e6; --brand: #f6f8f2; --brand2: #f0c75a;",
     ["#edf1ea", "#163f26", "#f6f3ea"]),
    ("pinstripe", "Pinstripe",
     "--surface: #eceff4; --surface-raised: #fbfcfe; --card2: #f1f4f8; --chip: #e0e5ee; --text-primary: #121a2c; --text-muted: #586379; --text-secondary: #424d64; --grid: #dfe4ec; --border: #d4dae5; --border-strong: #b3bdce; --accent: #1d3a78; --accent-d: #142a5a; --side: #13203f; --side2: #1c2c52; --sideInk: #e0e6f2; --brand: #f2f4f9; --brand2: #9fb6e6; --rad: 10px;",
     "--surface: #0b0f1a; --surface-raised: #121828; --card2: #182033; --chip: #1f2940; --text-primary: #e7ebf4; --text-muted: #9ba6bd; --text-secondary: #b6bfd2; --grid: #1f2940; --border: #222c45; --border-strong: #31406a; --accent: #8fb0f0; --accent-d: #b3caf6; --side: #060912; --side2: #0f1629; --sideInk: #e0e6f2; --brand: #f2f4f9; --brand2: #9fb6e6;",
     ["#eceff4", "#13203f", "#ffffff"]),
    ("sunday", "Sunday",
     "--surface: #f3ece0; --surface-raised: #fdf9f1; --card2: #f7f1e6; --chip: #ece2d2; --text-primary: #24170f; --text-muted: #6a5848; --text-secondary: #523f30; --grid: #eadfcd; --border: #e0d4c0; --border-strong: #c8b598; --accent: #b0262a; --accent-d: #8a1c1f; --side: #4a1416; --side2: #5e1c1e; --sideInk: #f6e9de; --brand: #fbf3e6; --brand2: #f2c27a; --rad: 14px;",
     "--surface: #140d0c; --surface-raised: #1c1312; --card2: #241918; --chip: #2d201e; --text-primary: #f3e9e2; --text-muted: #b3a196; --text-secondary: #ccbcb0; --grid: #2d201e; --border: #302220; --border-strong: #48322e; --accent: #f08a80; --accent-d: #f6b0a8; --side: #0c0606; --side2: #1e0f0f; --sideInk: #f6e9de; --brand: #fbf3e6; --brand2: #f2c27a;",
     ["#f3ece0", "#4a1416", "#b0262a"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:  # under the lights: a dark sky, the field itself lit bright
        return dict(grass="#3d8a3a", grass2="#4a9a45", foul="#3a8236", dirt="#b4763f", dirt2="#9a6233", track="#8e5a30",
                    chalk="#f4f4ee", wall="#123c29", wall2="#0c2a1c", pad="#1a5236", seat="#16223a", seat2="#1c2a46",
                    row="#0e1626", rail="#3a4658", steel="#5a6272", steel2="#3a4050", lamp="#fffbe6", board="#0f2a1e",
                    board2="#0a1d14", ink="#f6efd6", pole="#f2c230", roof="#2a3242", conc="#4a5262", skin="#c08a66",
                    far="#0d1426", tree="#0c1a14", glass="#ffe7a0")
    return dict(grass="#5e9c3c", grass2="#6dab48", foul="#5a9438", dirt="#c98a52", dirt2="#b3743f", track="#a96f40",
                chalk="#fbf8ee", wall="#1f5238", wall2="#163d29", pad="#256043", seat="#2f5f86", seat2="#376b94",
                row="#244a6a", rail="#d8d4c8", steel="#c7cbd0", steel2="#8a9096", lamp="#f4f1e2", board="#1b4a33",
                board2="#123526", ink="#f6efd6", pole="#f2c230", roof="#d8d2c4", conc="#c9c2b2", skin="#dba67c",
                far="#7f98a8", tree="#3a6a3e", glass="#9cc4dc")

DAYSKY = ("#3f6fb4", "#efb57a", "#fbdcac")
NIGHTSKY = ("#040816", "#0d1736", "#1e2a54")
CROWD = ["#d8402a", "#f2f0e8", "#2f6ab0", "#f2c230", "#3a8a4a", "#e8875a", "#8a4ab0", "#1a2a44"]
CROWD_N = ["#8a3a2e", "#b8b6ae", "#2a4a7a", "#a88a3a", "#2e5a3a", "#9a6a4e", "#5a3a7a", "#121a2a"]

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff2c0" stop-opacity=".75"/>'
            '<stop offset="1" stop-color="#fff2c0" stop-opacity="0"/></radialGradient>' + extra + '</defs>')

def skyg(n, day=DAYSKY, nt=NIGHTSKY, id="g"):
    c = nt if n else day
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/>'
            f'<stop offset=".6" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

def stars(k, x0, x1, y0, y1, seed):
    r = random.Random(seed)
    return '<g fill="#fff">' + ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([.8, 1.1, 1.5])}" opacity="{r.choice([.4, .6, .9])}"/>' for _ in range(k)) + '</g>'

def moon(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.7}" fill="#e9eefc" opacity=".12"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4efdc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#ddd6bd"/>')

def sun(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 2.8}" fill="#fff1c8" opacity=".22"/><circle cx="{x}" cy="{y}" r="{r * 1.7}" fill="#fff1c8" opacity=".35"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff6d8"/>')

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s:.0f} {y - 3 * s:.0f} Q{x - 5 * s:.0f} {y - 7 * s:.0f} {x} {y} Q{x + 5 * s:.0f} {y - 7 * s:.0f} {x + 10 * s:.0f} {y - 3 * s:.0f}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

def cloud(x, y, w, op=.55, c="#fff"):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="9" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .12:.0f}" cy="{y - 8}" rx="{w * .3:.0f}" ry="9" fill="{c}" opacity="{op * .85:.2f}"/>')

def pts(L): return " ".join(f"{x:.0f},{y:.0f}" for x, y in L)
def poly(L, fill, extra=''): return f'<polygon points="{pts(L)}" fill="{fill}"{extra}/>'

# ---- movement: SMIL plays inside a background picture; build.py writes a still copy with every <animate*/> taken
# out, so each element's own attributes are its resting state, and anything seen only mid-loop starts at opacity 0.
def show(times, vals, dur, attr="opacity", begin=0):
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s" begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>')
def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {b};{deg} {x} {b};{-deg} {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
# the banners' movement: an eased loop over evenly spaced values (a transform, or any attribute)
def _ease(vals):
    k = len(vals) - 1
    return (f'values="{";".join(vals)}" keyTimes="{";".join(f"{i / k:g}" for i in range(k + 1))}" '
            f'calcMode="spline" keySplines="{";".join([".45 0 .55 1"] * k)}" repeatCount="indefinite"')
def mv(vals, dur, begin=0, typ="translate"):
    return f'<animateTransform attributeName="transform" type="{typ}" {_ease(vals)} dur="{dur}s" begin="{begin}s"/>'
def am(attr, vals, dur, begin=0):
    return f'<animate attributeName="{attr}" {_ease(vals)} dur="{dur}s" begin="{begin}s"/>'
def bob(body, dy, dur, begin=0, dx=0):
    return f'<g>{body}{mv(["0 0", f"{dx} {-dy}", "0 0"], dur, begin)}</g>'
def rock(body, x, y, deg, dur, begin=0):
    return f'<g>{body}{sway(x, y, deg, dur, begin)}</g>'
def twinkle(k, x0, x1, y0, y1, seed):
    """a few stars that brighten and fade, for the night banners"""
    r = random.Random(seed)
    return '<g fill="#fff">' + ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="1.6" opacity=".3">'
                                       f'{am("opacity", [".3", "1", ".3"], r.choice([2.5, 3.5, 4.5]), r.randint(0, 30) / 10)}</circle>' for _ in range(k)) + '</g>'

# ----------------------------------------------------------------- people
# a player is drawn from a handful of joints (feet at 0, ~64 tall at scale 1, facing right): legs in the pants
# colour, the body a jersey capsule, arms in the jersey colour, a head with a cap whose brim faces forward
POSES = {
    "stand":  dict(hip=(0, -30), sh=(0, -51), hd=(0, -60), lk=(-3, -15), lf=(-4, 0), rk=(3, -15), rf=(5, 0), le=(-5, -41), lh=(-6, -31), re=(5, -41), rh=(6, -31)),
    "ready":  dict(hip=(-3, -27), sh=(5, -45), hd=(9, -53), lk=(-9, -14), lf=(-10, 0), rk=(7, -14), rf=(8, 0), le=(-1, -33), lh=(-6, -17), re=(9, -33), rh=(7, -17)),
    "catch":  dict(hip=(0, -30), sh=(1, -51), hd=(2, -60), lk=(-3, -15), lf=(-5, 0), rk=(4, -15), rf=(6, 0), le=(4, -62), lh=(7, -72), re=(-3, -62), rh=(1, -71)),
    "windup": dict(hip=(0, -31), sh=(-1, -52), hd=(-2, -61), lk=(-1, -16), lf=(-1, 0), rk=(9, -35), rf=(4, -22), le=(6, -44), lh=(4, -47), re=(-5, -43), rh=(2, -48)),
    "throw":  dict(hip=(2, -27), sh=(10, -46), hd=(15, -54), lk=(12, -14), lf=(17, 0), rk=(-7, -14), rf=(-16, -3), le=(5, -38), lh=(2, -33), re=(19, -49), rh=(27, -46)),
    "crouch": dict(hip=(-3, -15), sh=(2, -35), hd=(5, -44), lk=(7, -18), lf=(5, 0), rk=(3, -17), rf=(-6, 0), le=(9, -29), lh=(15, -30), re=(-1, -24), rh=(1, -18)),
    "bat":    dict(hip=(0, -30), sh=(-1, -51), hd=(1, -60), lk=(-7, -15), lf=(-9, 0), rk=(7, -15), rf=(9, 0), le=(-7, -43), lh=(-5, -53), re=(4, -43), rh=(-4, -54)),
    "swing":  dict(hip=(0, -30), sh=(1, -51), hd=(3, -60), lk=(-6, -15), lf=(-9, 0), rk=(5, -14), rf=(9, -1), le=(9, -46), lh=(6, -56), re=(-2, -44), rh=(5, -55)),
    "trot":   dict(hip=(0, -30), sh=(3, -51), hd=(5, -60), lk=(8, -18), lf=(6, -3), rk=(-4, -15), rf=(-11, -6), le=(-6, -42), lh=(-2, -35), re=(7, -62), rh=(9, -73)),
    "run":    dict(hip=(0, -29), sh=(6, -49), hd=(9, -57), lk=(10, -17), lf=(8, -2), rk=(-5, -14), rf=(-13, -5), le=(-6, -42), lh=(-2, -34), re=(12, -42), rh=(16, -48)),
    "lead":   dict(hip=(0, -24), sh=(5, -42), hd=(8, -50), lk=(-9, -12), lf=(-13, 0), rk=(9, -12), rf=(13, 0), le=(-3, -32), lh=(-8, -24), re=(12, -32), rh=(15, -24)),
    "kneel":  dict(hip=(0, -20), sh=(1, -41), hd=(2, -50), lk=(10, -20), lf=(10, 0), rk=(-3, -2), rf=(-13, 0), le=(7, -32), lh=(10, -27), re=(4, -32), rh=(9, -29)),
    "slump":  dict(hip=(0, -30), sh=(2, -50), hd=(5, -57), lk=(4, -15), lf=(6, 0), rk=(-3, -15), rf=(-6, 0), le=(-2, -40), lh=(-4, -30), re=(3, -40), rh=(4, -30)),
    "punch":  dict(hip=(0, -30), sh=(0, -51), hd=(0, -60), lk=(-6, -15), lf=(-8, 0), rk=(6, -15), rf=(8, 0), le=(-5, -41), lh=(-7, -31), re=(10, -50), rh=(19, -50)),
    "point":  dict(hip=(0, -30), sh=(0, -51), hd=(1, -60), lk=(-3, -15), lf=(-4, 0), rk=(3, -15), rf=(5, 0), le=(-5, -41), lh=(-6, -31), re=(11, -52), rh=(22, -56)),
    "mouth":  dict(hip=(0, -30), sh=(0, -51), hd=(0, -60), lk=(-4, -15), lf=(-5, 0), rk=(4, -15), rf=(6, 0), le=(7, -48), lh=(6, -58), re=(-4, -41), rh=(-5, -31)),
    "rake":   dict(hip=(0, -30), sh=(2, -51), hd=(4, -60), lk=(-3, -15), lf=(-5, 0), rk=(4, -15), rf=(7, 0), le=(8, -42), lh=(12, -38), re=(5, -40), rh=(10, -32)),
    "tray":   dict(hip=(0, -30), sh=(0, -51), hd=(1, -60), lk=(-3, -15), lf=(-5, 0), rk=(4, -15), rf=(6, 0), le=(5, -41), lh=(10, -34), re=(-3, -41), rh=(-1, -32)),
    "stretch": dict(hip=(0, -30), sh=(0, -51), hd=(0, -60), lk=(-8, -15), lf=(-12, 0), rk=(8, -15), rf=(12, 0), le=(-6, -62), lh=(-4, -74), re=(6, -62), rh=(4, -74)),
    "sit":    dict(hip=(0, -18), sh=(1, -39), hd=(2, -48), lk=(10, -18), lf=(10, 0), rk=(9, -17), rf=(8, 0), le=(5, -30), lh=(10, -22), re=(3, -30), rh=(8, -21)),
}

def guy(x, y, s, pose="stand", jer="#f4f2ec", pants="#f4f2ec", cap="#1f3f7a", skin="#dba67c", flip=False,
        bat=None, glove=None, helmet=False, mask=False, ink="#1a1a1a"):
    """bat=(hand-key, dx, dy) bat end relative to that hand; glove = hand key wearing it"""
    q = POSES[pose]
    def P_(k): return f'{q[k][0]} {q[k][1]}'
    o = [f'<g transform="translate({x:.0f} {y:.0f}) scale({-s if flip else s:.2f} {s:.2f})" stroke-linecap="round" stroke-linejoin="round" fill="none">']
    a = o.append
    if bat:
        hk, dx, dy = bat; hx, hy = q[hk]
        a(f'<path d="M{hx} {hy}L{hx + dx} {hy + dy}" stroke="#a8743c" stroke-width="3.2"/>')
    a(f'<path d="M{P_("hip")}L{P_("lk")}L{P_("lf")}M{P_("hip")}L{P_("rk")}L{P_("rf")}" stroke="{pants}" stroke-width="7"/>')
    a(f'<path d="M{q["lf"][0] - 2} {q["lf"][1]}h6M{q["rf"][0] - 2} {q["rf"][1]}h6" stroke="{ink}" stroke-width="4"/>')
    a(f'<path d="M{P_("hip")}L{P_("sh")}" stroke="{jer}" stroke-width="14"/>')
    a(f'<path d="M{q["hip"][0] - 6} {q["hip"][1] + 1}h12" stroke="{ink}" stroke-width="2" opacity=".7"/>')
    a(f'<path d="M{P_("sh")}L{P_("le")}L{P_("lh")}M{P_("sh")}L{P_("re")}L{P_("rh")}" stroke="{jer}" stroke-width="5.5"/>')
    hx, hy = q["hd"]
    a(f'<circle cx="{hx}" cy="{hy}" r="7" fill="{skin}"/>')
    if mask:
        a(f'<circle cx="{hx}" cy="{hy - 1}" r="7.5" fill="{cap}"/><path d="M{hx + 3} {hy - 4}v9M{hx + 6} {hy - 3}v7" stroke="#cfcfcf" stroke-width="1.4"/>')
    elif helmet:
        a(f'<path d="M{hx - 7.5} {hy}A7.5 7.5 0 0 1 {hx + 7.5} {hy - 1}L{hx + 11} {hy - 1}L{hx + 7} {hy + 1}L{hx - 2} {hy + 1}L{hx - 3} {hy + 6}L{hx - 7.5} {hy + 5}Z" fill="{cap}"/>')
    else:
        a(f'<path d="M{hx - 7} {hy - 1}A7 7 0 0 1 {hx + 7} {hy - 2}L{hx + 12} {hy - 1}L{hx + 7} {hy}Z" fill="{cap}"/>')
    if glove:
        gx, gy = q[glove]
        a(f'<ellipse cx="{gx + 1}" cy="{gy}" rx="4.6" ry="5.4" fill="#7a4a22"/>')
    a('</g>')
    return ''.join(o)

def baseball(x, y, r=3):
    return f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fbfaf4" stroke="#b8b0a0" stroke-width=".8"/>'

# ----------------------------------------------------------------- light towers
def tower(x, base, top, w, p, n, glow_anim=False, banks=(4, 6)):
    """a steel pole from base up to top, the lamp bank (w wide) on it; at night lit with a halo"""
    o = []
    bh = w * .62
    by = top
    if n:
        o.append(f'<circle cx="{x}" cy="{by + bh / 2:.0f}" r="{w * 1.6:.0f}" fill="url(#glow)" opacity=".85">'
                 + (f'<animate attributeName="opacity" values=".85;.55;.85" dur="4s" begin="{x % 3 * .7:.1f}s" repeatCount="indefinite"/>' if glow_anim else '') + '</circle>')
    pw0, pw1 = w * .07, w * .12
    o.append(poly([(x - pw0, by + bh), (x + pw0, by + bh), (x + pw1, base), (x - pw1, base)], p["steel2"]))
    o.append(f'<line x1="{x - pw0 * .3:.1f}" y1="{by + bh:.0f}" x2="{x - pw1 * .4:.1f}" y2="{base:.0f}" stroke="{p["steel"]}" stroke-width="{max(1, w * .03):.1f}"/>')
    o.append(f'<rect x="{x - w / 2:.0f}" y="{by:.0f}" width="{w:.0f}" height="{bh:.0f}" rx="2" fill="{p["steel2"]}"/>')
    o.append(f'<rect x="{x - w / 2 - 2:.0f}" y="{by + bh:.0f}" width="{w + 4:.0f}" height="{max(2, w * .05):.0f}" fill="{p["steel"]}"/>')
    rows, cols = banks; cw = w / cols; rh = bh / rows
    lc = p["lamp"] if n else "#e8e6dc"
    o.append(f'<g fill="{lc}">' + ''.join(f'<circle cx="{x - w / 2 + cw * (c + .5):.1f}" cy="{by + rh * (r_ + .5):.1f}" r="{min(cw, rh) * .36:.1f}"/>'
                                          for r_ in range(rows) for c in range(cols)) + '</g>')
    return ''.join(o)

# ================================================================= the Digest picture
# One ballpark seen from high behind home plate, a true one-point perspective: field coordinates in feet,
# home plate at the origin, Y out to centre field, X toward first base. The outfield wall and bleachers close
# the far end, the stands along both foul lines close the sides, and home plate sits just under the podium.
W, H, SPLIT = 1600, 1700, 377
F, D, H0 = 1230.0, 197.0, 298.0
HC = 102907.0 / F        # the eye is ~84 ft up
def pj(X, Y, h=0.0):
    d = Y + D
    return (800 + F * X / d, H0 + F * (HC - h) / d)

def rwall(th):
    a = abs(th)
    return 330 + 70 * math.cos(math.radians(2 * a)) if a <= 45 else 330 - 2 * (a - 45)

S2 = math.sqrt(.5)
def boundary():
    """the field's edge, in feet, with each point's outward normal and wall height: the third-base stands wall,
    the outfield wall, the first-base stands wall"""
    B = []
    for t in range(-40, 301, 40):
        B.append((-S2 * (t + 60), S2 * (t - 60), (-S2, -S2), 4))
    for i in range(23):
        th = -55 + i * 5
        r = rwall(th); s, c = math.sin(math.radians(th)), math.cos(math.radians(th))
        B.append((r * s, r * c, (s, c), 10))
    for t in range(300, -41, -40):
        B.append((S2 * (t + 60), S2 * (t - 60), (S2, -S2), 4))
    return B

def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    B = boundary()
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    beams = ('<linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6d0" stop-opacity=".22"/>'
             '<stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></linearGradient>')
    a(defs(skyg(n, id="sky") + beams + f'<clipPath id="fld"><polygon points="{pts([pj(X, Y) for X, Y, _, _ in B])}"/></clipPath>'))
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    if n:
        a(stars(30, 0, W, 0, 160, 3))
        a(moon(1150, 104, 30))
    else:
        a(sun(1150, 112, 34))
        for i, (x, y, w) in enumerate([(470, 128, 210), (1430, 160, 170)]):
            a(f'<g>{cloud(x, y, w, .5)}<animateTransform attributeName="transform" type="translate" values="0 0;{60 + i * 20} 0;0 0" dur="{40 + i * 9}s" repeatCount="indefinite"/></g>')
        for i, (x, y, sc) in enumerate([(470, 78, 1.1), (500, 66, .8)]):
            a(f'<g>{bird(x, y, sc, "#5a4a5a")}<animateTransform attributeName="transform" type="translate" values="0 0;{70 + i * 20} -8;0 0" dur="{14 + i * 3}s" repeatCount="indefinite"/></g>')
    # far-off hills behind the park
    a(f'<path d="M0 352 Q200 318 420 338 T860 330 T1300 334 T1600 326 L1600 380 L0 380Z" fill="{p["far"]}"/>')

    # the scoreboard in centre field, on the bleachers' back, its flags on top
    bx0, bx1, by0, by1 = 652, 948, 62, 340
    for fx, c, d0 in [(684, "#d8402a", 0), (800, "#f2c230", .5), (916, "#2f6ab0", 1)]:
        a(f'<rect x="{fx - 1.5}" y="6" width="3" height="58" fill="{p["steel"]}"/><circle cx="{fx}" cy="6" r="3" fill="{p["pole"]}"/>')
        f0 = f"M{fx + 1} 10 Q{fx + 16} 6 {fx + 30} 12 T{fx + 56} 13 L{fx + 54} 33 Q{fx + 40} 30 {fx + 28} 34 T{fx + 1} 32Z"
        f1 = f"M{fx + 1} 10 Q{fx + 14} 15 {fx + 28} 10 T{fx + 54} 16 L{fx + 52} 36 Q{fx + 38} 38 {fx + 26} 31 T{fx + 1} 32Z"
        a(f'<path d="{f0}" fill="{c}"><animate attributeName="d" values="{f0};{f1};{f0}" dur="1.6s" begin="{d0}s" repeatCount="indefinite"/></path>')
    a(f'<rect x="{bx0 + 30}" y="{by1 - 30}" width="14" height="40" fill="{p["steel2"]}"/><rect x="{bx1 - 44}" y="{by1 - 30}" width="14" height="40" fill="{p["steel2"]}"/>')
    a(f'<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0 - 30}" rx="4" fill="{p["board"]}" stroke="{p["board2"]}" stroke-width="6"/>')
    a(f'<rect x="{bx0 + 12}" y="{by0 + 10}" width="{bx1 - bx0 - 24}" height="40" rx="3" fill="#b8322a"/>')
    a(f'<text x="800" y="{by0 + 38}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="20" textLength="250" lengthAdjust="spacingAndGlyphs" fill="{p["ink"]}">FULL COUNT COVERAGE</text>')
    # the bulbs round the sign chase each other: three sets lit in turn
    bulbs = [[], [], []]; k = 0
    for xx in range(bx0 + 18, bx1 - 12, 14):
        bulbs[k % 3].append((xx, by0 + 6)); bulbs[(k + 1) % 3].append((xx, by0 + 54)); k += 1
    for i, L in enumerate(bulbs):
        a(f'<g fill="#ffe08a" opacity="{1 if i == 0 else .25}">' + ''.join(f'<circle cx="{x}" cy="{y}" r="2.6"/>' for x, y in L)
          + f'<animate attributeName="opacity" values="1;.25;.25;1" keyTimes="0;.33;.66;1" dur="1.2s" begin="{-i * .4:.1f}s" calcMode="discrete" repeatCount="indefinite"/></g>')
    # ball, strike, out: the count fills and clears on a loop
    yy = by0 + 82
    for lab, x0, k_, col in [("BALL", 668, 3, "#5ad16a"), ("STRIKE", 774, 2, "#f2c230"), ("OUT", 882, 2, "#ff5a4a")]:
        a(f'<text x="{x0}" y="{yy + 5}" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="{p["ink"]}">{lab}</text>')
        tx = x0 + (42 if lab == "BALL" else 58 if lab == "STRIKE" else 36)
        for j in range(k_):
            on = f'{(j + 1) / (k_ + 2):.2f}'
            a(f'<circle cx="{tx + j * 14}" cy="{yy}" r="5" fill="#0a1a12"/><circle cx="{tx + j * 14}" cy="{yy}" r="4" fill="{col}" opacity="0">'
              + show(["0", on, ".92"], ["0", "1", "0"], 5.5 + (lab == "STRIKE") * 1.5 + (lab == "OUT") * 3) + '</circle>')
    # the line score, mostly under the tiles
    for r_ in range(3):
        a(f'<text x="{bx0 + 16}" y="{by0 + 128 + r_ * 34}" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="{p["ink"]}">{["INNING", "HOME", "RISK"][r_]}</text>')
        for c in range(7):
            a(f'<rect x="{bx0 + 84 + c * 28}" y="{by0 + 114 + r_ * 34}" width="18" height="20" fill="{p["board2"]}"/>')

    # the two light towers on the bleachers' back
    tw = []
    for sgn in (-1, 1):
        th = 32 * sgn; r = rwall(th) + 140; s, c = math.sin(math.radians(th)), math.cos(math.radians(th))
        bxp, byp = pj(r * s, r * c, 60); _, ty = pj(r * s, r * c, 196)
        tw.append((bxp, byp, ty))
    for bxp, byp, ty in tw:
        a(tower(bxp, byp + 4, ty, 92, p, n, glow_anim=True))

    # the stands: one bowl wrapping the field, rows rising away from the wall, a crowd in them
    def ring(k):
        """row k of the stands: the field's edge pushed out 10k ft and raised"""
        L = []
        for X, Y, (nx, ny), h in B:
            L.append(pj(X + nx * 10 * k, Y + ny * 10 * k, h + 4.4 * k))
        return L
    top = ring(14)
    edge = [pj(X, Y, h) for X, Y, _, h in B]
    a(f'<rect x="0" y="360" width="{W}" height="{H - 360}" fill="{p["seat"]}"/>')
    a(poly(edge + top[::-1], p["seat"]))
    a(f'<g fill="none" stroke="{p["row"]}" stroke-width="1.6">' + ''.join(f'<polyline points="{pts(ring(k))}"/>' for k in range(1, 14)) + '</g>')
    a(f'<polyline points="{pts(ring(3.4))}" fill="none" stroke="{p["conc"]}" stroke-width="7"/>')   # the cross aisle
    a(f'<polyline points="{pts(top)}" fill="none" stroke="{p["roof"]}" stroke-width="6"/>')
    # the crowd: heads in shirts of every colour along each row, sized by how far off they sit
    r = random.Random(8); groups = {}
    cols = CROWD_N if n else CROWD
    def along(k, u):
        """a point on row k at u in 0..len(B)-1, in feet, and its height"""
        i = min(int(u), len(B) - 2); f = u - i
        X0, Y0, (nx0, ny0), h0 = B[i]; X1, Y1, (nx1, ny1), h1 = B[i + 1]
        return (X0 + (X1 - X0) * f + (nx0 + (nx1 - nx0) * f) * 10 * k, Y0 + (Y1 - Y0) * f + (ny0 + (ny1 - ny0) * f) * 10 * k,
                h0 + (h1 - h0) * f + 4.4 * k)
    for k in [x + .5 for x in range(13) if x not in (3,)]:
        u = r.uniform(0, .3)
        while u < len(B) - 1:
            X, Y, h = along(k, u); x, y = pj(X, Y, h); d = Y + D
            u += r.uniform(.36, .62) * (d / 400) ** .5
            if not (-4 < x < 1604 and 362 < y < 870) or r.random() < .18: continue
            if 640 < x < 960 and y < 330: continue
            rr = max(1.9, F * .8 / d)
            groups.setdefault(r.choice(cols), []).append(f'<circle cx="{x:.0f}" cy="{y - rr:.0f}" r="{rr:.1f}"/>')
    for c, L in groups.items(): a(f'<g fill="{c}">' + ''.join(L) + '</g>')
    # the wave rolls round the outfield bleachers: a band of the crowd on its feet, arms up
    bl = ring(13.5)[9:32]; fr = ring(.6)[9:32]
    a(f'<defs><clipPath id="blc"><polygon points="{pts(fr + bl[::-1])}"/></clipPath></defs>')
    wave = [f'<ellipse cx="-34" cy="400" rx="40" ry="80" fill="#fff" opacity=".12"/>']
    rr = random.Random(5)
    for k in range(30):   # fans on their feet: a head up above the row, both arms in the air
        x = -68 + rr.randint(0, 64); y = 350 + k * 4 + rr.randint(-2, 2); c = rr.choice(cols)
        wave.append(f'<circle cx="{x}" cy="{y - 4:.0f}" r="2.2" fill="{p["skin"]}"/><path d="M{x - 2} {y - 3:.0f}l-2 -8M{x + 2} {y - 3:.0f}l2 -8" stroke="{c}" stroke-width="1.8"/>')
    a('<g clip-path="url(#blc)"><g>' + ''.join(wave)
      + '<animateTransform attributeName="transform" type="translate" values="0 0;0 0;1720 0" keyTimes="0;.2;1" dur="11s" repeatCount="indefinite"/></g></g>')

    # the walls: the padded outfield wall with its ads, the low wall in front of the stands
    a(poly(edge + [pj(X, Y) for X, Y, _, _ in B][::-1], p["wall"]))
    a(f'<polyline points="{pts(edge)}" fill="none" stroke="{p["pole"]}" stroke-width="2.4"/>')

    # the field
    a(poly([pj(X, Y) for X, Y, _, _ in B], p["foul"]))
    a('<g clip-path="url(#fld)">')
    # mowing: stripes running out to centre (lines of one X all meet at the vanishing point), crossed by bands
    a(f'<g fill="{p["grass2"]}">' + ''.join(poly([pj(X, -70), pj(X + 18, -70), pj(X + 18, 640), pj(X, 640)], p["grass2"]).replace(f' fill="{p["grass2"]}"', '') for X in range(-414, 400, 36)) + '</g>')
    a('<g fill="#000" opacity=".07">' + ''.join(f'<polygon points="{pts([pj(-600, Y), pj(600, Y), pj(600, Y + 30), pj(-600, Y + 30)])}"/>' for Y in range(-60, 560, 60)) + '</g>')
    # the warning track inside the wall
    trk = []
    for th in [x * 2.5 for x in range(-22, 23)]:
        rr_ = rwall(th) - 15; s, c = math.sin(math.radians(th)), math.cos(math.radians(th)); trk.append(pj(rr_ * s, rr_ * c))
    wl = [pj(rwall(th) * math.sin(math.radians(th)), rwall(th) * math.cos(math.radians(th))) for th in [x * 2.5 for x in range(-22, 23)]]
    a(poly(wl + trk[::-1], p["track"]))
    a('</g>')
    # foul lines out to the poles
    for sg in (-1, 1):
        x0, y0 = pj(0, 0); x1, y1 = pj(sg * 233.3, 233.3)
        a(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{p["chalk"]}" stroke-width="2.6"/>')
    # the infield: the dirt arc round the mound from line to line, the grass square, the mound, the plate
    dirt = [pj(0, -4), pj(S2 * 6, -2)]
    dirt += [pj(93, 87.4)]
    for k in range(0, 33):
        ph = math.radians(18.2 + k * (161.8 - 18.2) / 32)
        dirt.append(pj(95 * math.cos(ph), 60.5 + 95 * math.sin(ph)))
    dirt += [pj(-93, 87.4), pj(-S2 * 6, -2)]
    a(poly(dirt, p["dirt"]))
    a(poly([pj(0, 6), pj(59.4, 63.64), pj(0, 123), pj(-59.4, 63.64)], p["grass2"]))
    a(f'<g clip-path="url(#ig)">' + '</g>')
    def circ(cx, cy, r_, k=28): return [pj(cx + r_ * math.cos(2 * math.pi * i / k), cy + r_ * math.sin(2 * math.pi * i / k)) for i in range(k)]
    a(poly(circ(0, 60.5, 9), p["dirt"]) + poly(circ(0, 60.5, 4), p["dirt2"], ' opacity=".5"'))
    a(poly([pj(-1, 60.2), pj(1, 60.2), pj(1, 60.8), pj(-1, 60.8)], p["chalk"]))
    a(poly(circ(0, 1, 13), p["dirt"]))
    for bx, by_ in [(63.64, 63.64), (0, 127.3), (-63.64, 63.64)]:
        a(poly(circ(bx, by_, 7, 16), p["dirt"]))
        a(poly([pj(bx - 1.3, by_), pj(bx, by_ - 1.3), pj(bx + 1.3, by_), pj(bx, by_ + 1.3)], p["chalk"]))
    # the batter's boxes and the plate, just in front of the podium
    for sg in (-1, 1):
        a(f'<polygon points="{pts([pj(sg * 1.6, -3), pj(sg * 5.6, -3), pj(sg * 5.6, 3.4), pj(sg * 1.6, 3.4)])}" fill="none" stroke="{p["chalk"]}" stroke-width="1.6"/>')
    a(poly([pj(-.7, .3), pj(.7, .3), pj(.7, -.4), pj(0, -1), pj(-.7, -.4)], p["chalk"]))
    a(poly(circ(-50, -6, 2.6, 14), p["dirt2"]) + poly(circ(50, -6, 2.6, 14), p["dirt2"]))   # on-deck circles
    # the foul poles
    for sg in (-1, 1):
        x0, y0 = pj(sg * 233.3, 233.3); _, y1 = pj(sg * 233.3, 233.3, 82)
        a(f'<rect x="{x0 - 2:.0f}" y="{y1:.0f}" width="4" height="{y0 - y1:.0f}" fill="{p["pole"]}"/>'
          f'<rect x="{x0 + (2 if sg > 0 else -12):.0f}" y="{y1 + 6:.0f}" width="10" height="{(y0 - y1) * .6:.0f}" fill="{p["pole"]}" opacity=".35"/>')
    # the ads along the outfield wall, and its distance marks
    ads = [(-27, "HOME RUN HOMEOWNERS"), (-9, "SAFE AT HOME"), (9, "NO LAPSE LEAGUE"), (27, "BUNDLE THE BASES")]
    for th, txt in ads:
        L = []
        for d_ in (-7, 7):
            t2 = math.radians(th + d_); r_ = rwall(th + d_)
            L.append((r_ * math.sin(t2), r_ * math.cos(t2)))
        q = [pj(L[0][0], L[0][1], 2), pj(L[1][0], L[1][1], 2), pj(L[1][0], L[1][1], 8.4), pj(L[0][0], L[0][1], 8.4)]
        a(poly(q, "#f4ead2" if not n else "#d8ceb2"))
        cx = (q[0][0] + q[1][0]) / 2; cy = (q[0][1] + q[1][1] + q[2][1] + q[3][1]) / 4
        fs = (q[0][1] - q[3][1]) * .62; wd = abs(q[1][0] - q[0][0]) * .9
        ang = math.degrees(math.atan2(q[1][1] - q[0][1], q[1][0] - q[0][0]))
        a(f'<text x="{cx:.0f}" y="{cy + fs * .36:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="{fs:.1f}" '
          f'textLength="{wd:.0f}" lengthAdjust="spacingAndGlyphs" fill="{p["wall"]}" transform="rotate({ang:.1f} {cx:.0f} {cy:.0f})">{txt}</text>')
    for th, txt in [(0, "400"), (-45, "330"), (45, "330")]:
        r_ = rwall(th); t2 = math.radians(th); x_, y_ = pj(r_ * math.sin(t2) * (.995 if th else 1), r_ * math.cos(t2), 5)
        if th: x_ += 16 * (1 if th > 0 else -1) * -1
        a(f'<text x="{x_:.0f}" y="{y_ + 4:.0f}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="11" fill="{p["chalk"]}">{txt}</text>')

    # the dugouts, sunk in the walls along each line between home and the bases, a few caps showing
    for sg in (-1, 1):
        def sp(t, off, h): return pj(sg * S2 * (t + off), S2 * (t - off), h)
        t0, t1 = 72, 132
        a(poly([sp(t0, 60, 0), sp(t1, 60, 0), sp(t1, 60, 7), sp(t0, 60, 7)], "#0e0f12"))
        a(poly([sp(t0, 60, 7), sp(t1, 60, 7), sp(t1, 67, 7.4), sp(t0, 67, 7.4)], p["wall2"]))
        a(poly([sp(t0, 60, 7), sp(t1, 60, 7), sp(t1, 60, 8.2), sp(t0, 60, 8.2)], p["wall"]))
        a(poly([sp(t0, 60, 0), sp(t1, 60, 0), sp(t1, 60, 1.6), sp(t0, 60, 1.6)], p["pad"]))
        for i in range(5):
            t = t0 + 8 + i * 11; x_, y_ = sp(t, 61, 3.6)
            a(f'<circle cx="{x_:.0f}" cy="{y_:.0f}" r="4" fill="{p["skin"]}"/><path d="M{x_ - 4:.0f} {y_ - 1:.0f}a4 4 0 0 1 8 0z" fill="#1f3f7a"/>')

    # the bullpen in foul ground down the first-base line: the pitcher throws to his catcher on a 4s loop
    pmx, pmy = pj(S2 * 200, S2 * 140); cmx, cmy = pj(S2 * 140, S2 * 80)
    a(f'<ellipse cx="{pmx:.0f}" cy="{pmy:.0f}" rx="30" ry="9" fill="{p["dirt"]}"/><ellipse cx="{cmx:.0f}" cy="{cmy + 2:.0f}" rx="24" ry="8" fill="{p["dirt"]}"/>')
    sc_p = F * 6.2 / (S2 * 140 + D) / 60 * 1.2; sc_c = F * 6.2 / (S2 * 80 + D) / 60 * 1.2
    a(f'<g>{guy(pmx, pmy, sc_p, "windup", flip=True, glove="lh", skin=p["skin"])}{show(["0", ".45", ".8"], ["1", "0", "1"], 4)}</g>')
    a(f'<g opacity="0">{guy(pmx, pmy, sc_p, "throw", flip=True, glove="lh", skin=p["skin"])}{show(["0", ".45", ".8"], ["0", "1", "0"], 4)}</g>')
    a(guy(cmx + 6, cmy, sc_c, "crouch", glove="lh", mask=True, cap="#2a2a2a", skin=p["skin"]))
    hx_, hy_ = pmx - 27 * sc_p, pmy - 46 * sc_p; mx_, my_ = cmx + 6 + 16 * sc_c, cmy - 30 * sc_c
    a(f'<g transform="translate({hx_:.0f} {hy_:.0f})"><circle r="2.6" fill="#fff" opacity="0">'
      f'{show(["0", ".46", ".6"], ["0", "1", "0"], 4)}'
      f'<animateMotion path="M0 0 Q{(mx_ - hx_) / 2:.0f} {(my_ - hy_) / 2 - 10:.0f} {mx_ - hx_:.0f} {my_ - hy_:.0f}" keyPoints="0;0;1;1" keyTimes="0;.46;.58;1" calcMode="linear" dur="4s" repeatCount="indefinite"/></circle></g>')

    # fungo before the game: a coach in foul ground by third hits fly balls to an outfielder in left-centre
    fcx, fcy = pj(-S2 * 140, S2 * 80)
    sc_f = F * 6.2 / (S2 * 80 + D) / 60 * 1.2
    a(f'<g>{guy(fcx, fcy, sc_f, "bat", jer="#1f3f7a", pants="#d8d8d0", bat=("lh", -10, -26), skin=p["skin"])}{show(["0", ".1", ".5"], ["1", "0", "1"], 6)}</g>')
    a(f'<g opacity="0">{guy(fcx, fcy, sc_f, "swing", jer="#1f3f7a", pants="#d8d8d0", bat=("lh", -24, -4), skin=p["skin"])}{show(["0", ".1", ".5"], ["0", "1", "0"], 6)}</g>')
    ofx, ofy = pj(-95, 330); sc_o = F * 6.2 / (330 + D) / 60 * 1.35
    a(f'<g>{guy(ofx, ofy, sc_o, "ready", glove="lh", skin=p["skin"], flip=True)}{show(["0", ".5", ".86"], ["1", "0", "1"], 6)}'
      f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;-14 0;-14 0;0 0" keyTimes="0;.15;.5;.86;1" dur="6s" repeatCount="indefinite"/></g>')
    a(f'<g opacity="0">{guy(ofx - 14, ofy, sc_o, "catch", glove="lh", skin=p["skin"], flip=True)}{show(["0", ".5", ".86"], ["0", "1", "0"], 6)}</g>')
    bsx, bsy = fcx + 6 * sc_f, fcy - 54 * sc_f
    gx_, gy_ = ofx - 14 + 7 * sc_o * -1, ofy - 72 * sc_o
    a(f'<g transform="translate({bsx:.0f} {bsy:.0f})"><circle r="2.8" fill="#fff" opacity="0">{show(["0", ".1", ".86"], ["0", "1", "0"], 6)}'
      f'<animateMotion path="M0 0 Q{(gx_ - bsx) * .45:.0f} {-300:.0f} {gx_ - bsx:.0f} {gy_ - bsy:.0f}" keyPoints="0;0;1;1" keyTimes="0;.1;.5;1" calcMode="spline" keySplines="0 0 1 1;.3 .1 .7 .9;0 0 1 1" dur="6s" repeatCount="indefinite"/></circle></g>')

    # the hot-dog vendor works the cross aisle of the left-field bleachers, there and back
    def ap(th):
        r_ = rwall(th) + 34; t2 = math.radians(th)
        return pj(r_ * math.sin(t2), r_ * math.cos(t2), 10 + 4.4 * 3.4), r_ * math.cos(t2) + D
    (vx0, vy0), dv = ap(-22); (vx1, vy1), _ = ap(-6)
    sc_v = F * 6 / dv / 60 * 1.7
    vend = lambda fl: (guy(0, 0, sc_v, "tray", jer="#f6f3ea", pants="#c8402a", cap="#c8402a", skin=p["skin"], flip=fl)
                       + f'<rect x="{-1 if not fl else -9}" y="{-37 * sc_v:.0f}" width="10" height="5" fill="#e9c75a" stroke="#a8743c" stroke-width=".8"/>')
    mv = f'values="{vx0:.0f} {vy0:.0f};{vx1:.0f} {vy1:.0f};{vx0:.0f} {vy0:.0f}" dur="12s" repeatCount="indefinite"'
    a(f'<g transform="translate({vx0:.0f} {vy0:.0f})">{vend(True)}<animateTransform attributeName="transform" type="translate" {mv}/>{show(["0", ".5"], ["1", "0"], 12)}</g>')
    a(f'<g transform="translate({vx0:.0f} {vy0:.0f})" opacity="0">{vend(False)}<animateTransform attributeName="transform" type="translate" {mv}/>{show(["0", ".5"], ["0", "1"], 12)}</g>')

    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(V, body + SHADE)
def base(n, sky=DAYSKY, nt=NIGHTSKY, star=40, h=V):
    return defs(skyg(n, day=sky, nt=nt)) + f'<rect width="1600" height="{h}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 120, 7) if n else '')

def corners(c="#0b1610"):
    """darken the corners the title and line sit on, fading toward the middle"""
    return (f'<defs><linearGradient id="cl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c}" stop-opacity=".8"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="cr" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{c}" stop-opacity=".8"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient></defs>'
            '<rect x="0" y="168" width="560" height="72" fill="url(#cl)"/><rect x="1000" y="180" width="600" height="60" fill="url(#cr)"/>')

def stands_band(p, n, y0, y1, seed, x0=0, x1=1600, rows=5):
    """a flat run of stands from y0 to y1 behind a wall: rows of seats, a crowd"""
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{p["seat"]}"/>']
    r = random.Random(seed); cols = CROWD_N if n else CROWD; g = {}
    for k in range(rows):
        y = y0 + (y1 - y0) * (k + .7) / rows
        o.append(f'<rect x="{x0}" y="{y + 3:.0f}" width="{x1 - x0}" height="2" fill="{p["row"]}"/>')
        for x in range(x0 + r.randint(0, 10), x1, r.randint(21, 26)):
            if r.random() < .3: continue
            g.setdefault(r.choice(cols), []).append(f'<circle cx="{x}" cy="{y - 1:.0f}" r="{3 + k * .35:.1f}"/>')
    for c, L in g.items(): o.append(f'<g fill="{c}">' + ''.join(L) + '</g>')
    o.append(f'<rect x="{x0}" y="{y0 - 4}" width="{x1 - x0}" height="5" fill="{p["roof"]}"/>')
    return ''.join(o)

def wall_band(p, y, h=22, ads=()):
    o = [f'<rect x="0" y="{y}" width="1600" height="{h}" fill="{p["wall"]}"/><rect x="0" y="{y - 2}" width="1600" height="3" fill="{p["pole"]}"/>']
    for x, w, t in ads:
        o.append(f'<rect x="{x}" y="{y + 4}" width="{w}" height="{h - 8}" fill="#f4ead2"/>'
                 f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + 4:.0f}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="{h - 12}" fill="{p["wall"]}">{t}</text>')
    return ''.join(o)

def turf(p, y, c=None):
    return f'<rect x="0" y="{y}" width="1600" height="{V - y}" fill="{c or p["grass"]}"/>' + ''.join(
        f'<rect x="{x}" y="{y}" width="80" height="{V - y}" fill="{p["grass2"]}" opacity=".7"/>' for x in range(40, 1600, 160))

def v_sales(n):  # the home-run trot: the runner rounds third, the coach's hand out, the ball long gone over the wall
    p = P(n); o = [base(n, sky=("#3f6fb4", "#efb57a", "#fbdcac"))]
    o.append(moon(1250, 52, 16) if n else sun(1250, 56, 18))
    o.append(stands_band(p, n, 64, 116, 1, rows=4))
    o.append(wall_band(p, 116, 20, [(330, 190, "HOME RUN HOMEOWNERS"), (1090, 140, "SAFE AT HOME")]))
    o.append(turf(p, 136))
    o.append(f'<path d="M0 240 L0 212 Q600 176 1600 190 L1600 240Z" fill="{p["dirt"]}"/>')
    o.append(f'<path d="M0 222 Q600 190 1600 200" stroke="{p["chalk"]}" stroke-width="3" fill="none"/>')
    o.append(f'<path d="M848 196 l20 -5 l16 5 l-20 5z" fill="{p["chalk"]}"/>')   # third base
    o.append(bob(guy(720, 212, 1.3, "trot", jer="#f4f2ec", pants="#f4f2ec", cap="#1f3f7a", helmet=True, skin=p["skin"]), 5, .8, dx=6))
    o.append(rock(guy(960, 200, 1.25, "point", jer="#1f3f7a", pants="#d8d8d0", flip=True, skin=p["skin"]), 960, 200, 2.5, 2))
    # the ball's long arc away over the wall and the bleachers
    for i in range(1, 12):
        t = i / 12; x = 480 + 600 * t; y = 112 - 220 * t * (1 - t) * 1.1 - 52 * t
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.2" fill="#fff" opacity="{.25 + t * .55:.2f}"/>')
    o.append(bob(baseball(1086, 58, 5) + '<path d="M1070 62 l-14 4 M1072 54 l-12 0" stroke="#fff" stroke-width="2" opacity=".6"/>', 8, 3, dx=14))
    o.append(twinkle(6, 900, 1580, 8, 60, 11) if n else bob(cloud(1420, 30, 120, .5), 0, 12, dx=-60))
    o.append(corners())
    return vwrap(''.join(o))

def v_messages(n):  # the press box behind home: lit windows, two voices on the headsets, every call on the air
    p = P(n); o = [base(n, sky=("#4f80c0", "#f0c08a", "#f8e0b8"))]
    o.append(moon(300, 56, 18) if n else sun(300, 60, 20))
    o.append(stands_band(p, n, 150, 240, 2, rows=4))
    # the upper deck's face and the press box hung on it
    o.append(f'<rect x="0" y="118" width="1600" height="32" fill="{p["conc"]}"/><rect x="0" y="146" width="1600" height="4" fill="{p["roof"]}"/>')
    x0, x1 = 500, 1100
    o.append(f'<rect x="{x0}" y="46" width="{x1 - x0}" height="96" fill="{p["roof"]}"/><rect x="{x0 - 10}" y="40" width="{x1 - x0 + 20}" height="10" fill="{p["wall"]}"/>')
    o.append(f'<rect x="{x0 + 220}" y="54" width="160" height="16" fill="{p["wall"]}"/><text x="800" y="67" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="{p["ink"]}" letter-spacing="3">PRESS BOX</text>')
    for i in range(5):
        wx = x0 + 20 + i * 116
        if n: o.append(f'<circle cx="{wx + 48}" cy="104" r="70" fill="url(#glow)" opacity=".6"/>')
        o.append(f'<rect x="{wx}" y="76" width="96" height="56" fill="{p["glass"]}" stroke="{p["steel2"]}" stroke-width="3"/>')
        if i in (1, 3):
            o.append(f'<path d="M{wx + 22} 132q12 -22 24 0z" fill="#2a3a5a"/><path d="M{wx + 58} 132q12 -22 24 0z" fill="#7a2a2a"/>')
            o.append(rock(f'<circle cx="{wx + 34}" cy="104" r="9" fill="#5a3a2a"/><path d="M{wx + 24} 102a10 10 0 0 1 20 0" stroke="#222" stroke-width="3" fill="none"/>'
                          f'<path d="M{wx + 46} 104l14 4" stroke="#222" stroke-width="2"/><circle cx="{wx + 62}" cy="108" r="3" fill="#222"/>', wx + 34, 114, 5, 1.6, i * .3))
            o.append(rock(f'<circle cx="{wx + 70}" cy="104" r="9" fill="#c89a76"/><path d="M{wx + 60} 102a10 10 0 0 1 20 0" stroke="#222" stroke-width="3" fill="none"/>', wx + 70, 114, 5, 2.2, 1 + i * .2))
    # the radio mast and the sound waves going out
    o.append(f'<rect x="{x1 - 40}" y="6" width="4" height="36" fill="{p["steel2"]}"/><circle cx="{x1 - 38}" cy="8" r="4" fill="#ff5a4a">{am("opacity", ["1", ".2", "1"], 2)}</circle>')
    for k in range(3): o.append(f'<path d="M{x1 - 20 + k * 12} {6 - k * 2}q10 10 0 22" stroke="#fff" stroke-width="2" fill="none" opacity="{.8 - k * .2:.1f}">{am("opacity", [".1", ".9", ".1"], 1.8, k * .3)}</path>')
    o.append(corners())
    return vwrap(''.join(o))

_NETS = [0]
def net(x0, y0, x1, y1, step, c, op=.5):
    """netting as a pattern of squares, so a big net costs a few bytes"""
    _NETS[0] += 1; i = _NETS[0]
    return (f'<defs><pattern id="nt{i}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" x="{x0}" y="{y0}">'
            f'<path d="M0 0H{step}M0 0V{step}" stroke="{c}" stroke-width="1.2" fill="none"/></pattern></defs>'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#nt{i})" opacity="{op}"/>')

def v_coaching(n):  # the batting cage: a hitter in the tunnel, the coach at the net with a bucket of balls
    p = P(n); o = [base(n, sky=("#5a8cc8", "#f0c896", "#fae6c2"))]
    o.append(moon(1260, 56, 18) if n else sun(1260, 60, 20))
    o.append(f'<rect x="0" y="120" width="1600" height="16" fill="{p["tree"]}"/>')
    o.append(turf(p, 134))
    # the cage: a tunnel of netting on its frame, the hitter at the near end, the L-screen and machine at the far end
    o.append(f'<path d="M420 200 L420 70 L1180 70 L1180 200Z" fill="{p["far"]}" opacity=".25"/>')
    o.append(f'<rect x="420" y="190" width="760" height="14" fill="{p["dirt"]}"/>')
    o.append(net(420, 70, 1180, 200, 14, p["chalk"], .35))
    o.append(f'<path d="M420 200V70H1180V200M800 70V200" stroke="{p["steel2"]}" stroke-width="5" fill="none"/>')
    o.append(f'<path d="M1060 196 v-56 h40 v56 M1060 140 h-26 v56" stroke="{p["steel2"]}" stroke-width="4" fill="none"/>' + net(1036, 142, 1098, 194, 8, p["chalk"], .5))
    o.append(rock(guy(560, 198, 1.65, "swing", jer="#1f3f7a", pants="#f4f2ec", cap="#1f3f7a", helmet=True, bat=("lh", -32, -8), skin=p["skin"]), 560, 198, 3, 3))
    o.append(f'<g>{baseball(900, 128, 4)}<path d="M870 132 h-30 M872 126 h-22" stroke="#fff" stroke-width="2" opacity=".6"/>'
             '<animateMotion path="M-310 -30 L0 0 L150 -8" keyPoints="0;0;.67;1;1" keyTimes="0;.45;.6;.75;1" calcMode="linear" dur="3s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.45;.7;.75;1" dur="3s" repeatCount="indefinite"/></g>')
    # the coach, outside the net, pointing at the swing
    o.append(rock(guy(700, 204, 1.6, "point", jer="#c8402a", pants="#d8d8d0", cap="#c8402a", flip=True, skin=p["skin"]), 700, 204, 2.5, 2.4))
    o.append(f'<path d="M730 204 l4 -28 h24 l4 28z" fill="#e9e6dc" stroke="#9a968a" stroke-width="2"/>')
    for k in range(4): o.append(baseball(738 + k * 6, 174 - (k % 2) * 3, 3))
    o.append(corners())
    return vwrap(''.join(o))

def v_roleplay(n):  # the bullpen: two arms warming up, two catchers, the bench along the fence
    p = P(n); o = [base(n, sky=("#5f90c6", "#f1c494", "#f9e2bc"))]
    o.append(moon(1250, 54, 18) if n else sun(1250, 58, 20))
    o.append(stands_band(p, n, 60, 126, 4))
    o.append(wall_band(p, 126, 18, []))
    o.append(f'<rect x="0" y="122" width="1600" height="3" fill="{p["chalk"]}" opacity=".6"/>')
    o.append(net(0, 92, 1600, 126, 10, p["chalk"], .3))
    o.append(turf(p, 144))
    for mx, cx in ((560, 1040), (620, 1100)):
        pass
    for k, (mx, cx, y) in enumerate([(520, 920, 186), (700, 1110, 214)]):
        o.append(f'<ellipse cx="{mx}" cy="{y}" rx="70" ry="12" fill="{p["dirt"]}"/><ellipse cx="{cx}" cy="{y}" rx="50" ry="10" fill="{p["dirt"]}"/>')
        pose = "windup" if k == 0 else "throw"
        o.append(rock(guy(mx, y - 2, 1.25 + k * .2, pose, jer="#f4f2ec", pants="#f4f2ec", cap="#1f3f7a", glove="lh", skin=p["skin"]), mx, y - 2, 4, 2.5, k * 1.2))
        o.append(guy(cx, y, 1.2 + k * .2, "crouch", jer="#1f3f7a", pants="#d8d8d0", cap="#2a2a2a", flip=True, mask=True, glove="lh", skin=p["skin"]))
    o.append(f'<g>{baseball(930, 184, 4)}<path d="M900 186 h-26" stroke="#fff" stroke-width="2" opacity=".6"/>'
             '<animateMotion path="M-390 -50 Q-200 -50 -28 -34" keyPoints="0;0;1;1" keyTimes="0;.3;.6;1" calcMode="linear" dur="2.5s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.3;.8;1" dur="2.5s" repeatCount="indefinite"/></g>')
    o.append(f'<g opacity="0">{baseball(1090, 182, 4)}'
             '<animateMotion path="M-350 -35 Q-170 -30 0 -10" keyPoints="0;0;1;1" keyTimes="0;.3;.6;1" calcMode="linear" dur="2.5s" begin="1.2s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.3;.8;1" dur="2.5s" begin="1.2s" repeatCount="indefinite"/></g>')
    # the bench along the wall
    o.append(f'<rect x="250" y="150" width="200" height="8" fill="{p["wall2"]}"/><rect x="262" y="158" width="6" height="12" fill="{p["wall2"]}"/><rect x="432" y="158" width="6" height="12" fill="{p["wall2"]}"/>')
    o.append(guy(320, 170, 1.0, "sit", jer="#1f3f7a", pants="#f4f2ec", skin=p["skin"]))
    o.append(corners())
    return vwrap(''.join(o))

def v_rphistory(n):  # the scoreboard's replay screen: the swing on the big board, again
    p = P(n); o = [base(n, sky=("#4f7cba", "#eab27e", "#f6d8ac"))]
    o.append(stands_band(p, n, 176, 240, 5, rows=3))
    for x in (380, 1220):
        o.append(tower(x, 176, 30, 86, p, n, glow_anim=True))
    bx0, bx1 = 560, 1040
    o.append(f'<rect x="{bx0 + 60}" y="160" width="16" height="20" fill="{p["steel2"]}"/><rect x="{bx1 - 76}" y="160" width="16" height="20" fill="{p["steel2"]}"/>')
    o.append(f'<rect x="{bx0}" y="34" width="{bx1 - bx0}" height="128" rx="5" fill="{p["board"]}" stroke="{p["board2"]}" stroke-width="6"/>')
    o.append(f'<rect x="{bx0 + 14}" y="44" width="300" height="108" fill="#0c1a24"/>')
    if n: o.append(f'<circle cx="{bx0 + 164}" cy="98" r="160" fill="#7fb2e0" opacity=".1"/>')
    # on the screen: the batter's swing and the ball flying off, a play button and the scrub bar
    sx = bx0 + 14
    o.append(f'<rect x="{sx}" y="44" width="300" height="70" fill="#4a7ab0"/><rect x="{sx}" y="114" width="300" height="38" fill="#4c8a3a"/>')
    o.append(f'<path d="M{sx} 114 Q{sx + 150} 96 {sx + 300} 114" fill="#2f5f86"/>')
    o.append(guy(sx + 90, 146, .62, "swing", jer="#f4f2ec", pants="#f4f2ec", helmet=True, bat=("lh", -26, -6)))
    o.append(f'<path d="M{sx + 104} 110 Q{sx + 190} 40 {sx + 270} 70" stroke="#fff" stroke-width="2" stroke-dasharray="3 5" fill="none"/>'
             f'<g>{baseball(sx + 270, 70, 3)}<animateMotion path="M-166 40 Q-80 -30 0 0" keyPoints="0;1;1" keyTimes="0;.6;1" calcMode="linear" dur="5s" repeatCount="indefinite"/></g>')
    o.append(f'<path d="M{sx + 12} 54 l14 8 l-14 8z" fill="#fff">{am("opacity", ["1", ".3", "1"], 1.5)}</path><rect x="{sx}" y="146" width="300" height="6" fill="#000" opacity=".4"/>'
             f'<rect x="{sx}" y="146" width="190" height="6" fill="#ff5a4a"><animate attributeName="width" values="0;300" dur="5s" repeatCount="indefinite"/></rect>')
    # the line score beside it
    for r_ in range(3):
        o.append(f'<text x="{sx + 318}" y="{68 + r_ * 32}" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="{p["ink"]}">{["INN", "HOME", "RISK"][r_]}</text>')
        for c in range(3):
            o.append(f'<rect x="{sx + 362 + c * 28}" y="{54 + r_ * 32}" width="22" height="20" fill="{p["board2"]}"/>')
            if r_: o.append(f'<text x="{sx + 373 + c * 28}" y="{69 + r_ * 32}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="#ffd27a">{(c + r_ * 2) % 4 if r_ == 1 else 0}</text>')
    o.append(f'<rect x="{bx0 + 150}" y="12" width="180" height="22" rx="3" fill="#b8322a"/><text x="800" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="{p["ink"]}" letter-spacing="4">INSTANT REPLAY</text>')
    o.append(corners())
    return vwrap(''.join(o))

def v_training(n):  # spring practice: the squad stretching in a line, cones, a coach with the whistle
    p = P(n); o = [base(n, sky=("#5a9ad8", "#a8d0ec", "#eef4e0"))]
    o.append(moon(1260, 54, 18) if n else sun(1260, 58, 20))
    o.append(f'<path d="M0 138 Q300 108 600 128 T1200 118 T1600 132 L1600 150 L0 150Z" fill="{p["far"]}"/>')
    o.append(f'<rect x="0" y="134" width="1600" height="10" fill="{p["tree"]}"/>')
    o.append(f'<rect x="0" y="120" width="1600" height="3" fill="{p["steel2"]}"/>' + ''.join(f'<rect x="{x}" y="120" width="3" height="24" fill="{p["steel2"]}"/>' for x in range(0, 1600, 80)))
    o.append(turf(p, 144))
    if not n:
        for x, y, w, d in ((900, 40, 140, 11), (1450, 28, 110, 9)): o.append(bob(cloud(x, y, w, .6), 0, d, dx=-50))
    for i in range(6):
        x = 470 + i * 100; pose = "stretch" if i % 2 == 0 else "stand"; y = 200 - (i % 2) * 4
        g = guy(x, y, 1.3, pose, jer=["#1f3f7a", "#c8402a"][i % 2], pants="#f4f2ec", cap=["#1f3f7a", "#c8402a"][i % 2], skin=p["skin"])
        o.append(rock(g, x, y, 6, 3, i * .25) if i % 2 == 0 else bob(g, 6, 1.5, i * .2))
    for x in range(480, 1100, 90): o.append(f'<path d="M{x} 224 l7 -16 l7 16z" fill="#f28a2a"/>')
    o.append(rock(guy(1150, 204, 1.4, "point", jer="#2a2a2a", pants="#d8d8d0", cap="#2a2a2a", flip=True, skin=p["skin"]), 1150, 204, 2.5, 2))
    if n: o.append(twinkle(6, 700, 1580, 8, 70, 12))
    o.append(f'<path d="M1200 210 l4 -24 h22 l4 24z" fill="#e9e6dc" stroke="#9a968a" stroke-width="2"/>')
    o.append(corners())
    return vwrap(''.join(o))

def v_map(n, athena):  # the scorecard on the dugout bench: one big diamond, the route round the bases in pencil
    o = [defs()]
    o.append(f'<rect width="1600" height="{V}" fill="{"#2a1d14" if not n else "#140d09"}"/>')
    o.append(''.join(f'<rect x="0" y="{y}" width="1600" height="2" fill="#000" opacity=".25"/>' for y in range(10, 240, 34)))
    pap = "#f5edd8" if not n else "#cfc6ad"; ln = "#9ab4c8" if not n else "#6a8090"; ink = "#2a3a5a"
    x0, x1, y0, y1 = 470, 1130, 20, 198
    o.append(f'<rect x="{x0 + 8}" y="{y0 + 6}" width="{x1 - x0}" height="{y1 - y0}" fill="#000" opacity=".35" transform="rotate(-1 800 110)"/>')
    o.append(f'<g transform="rotate(-1 800 110)"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{pap}"/>')
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="22" fill="{"#1f5238" if not athena else "#2f6a52"}"/>')
    o.append(f'<text x="800" y="{y0 + 16}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="#f5edd8" letter-spacing="4">{"OFFICIAL SCORECARD" if not athena else "SERVICE SCORECARD"}</text>')
    for x in range(x0, x1 + 1, 60): o.append(f'<line x1="{x}" y1="{y0 + 22}" x2="{x}" y2="{y1}" stroke="{ln}" stroke-width="1"/>')
    for y in range(y0 + 22, y1 + 1, 44): o.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{ln}" stroke-width="1"/>')
    # the diamond: home at the bottom, first to the right, second at the top, third to the left
    hm, b1, b2, b3 = (800, 182), (960, 118), (800, 56), (640, 118)
    o.append(f'<polygon points="{pts([hm, b1, b2, b3])}" fill="{pap}" stroke="{ink}" stroke-width="2.5"/>')
    route = "#c8302a" if not athena else "#2f8a5a"
    stops = ["Dial", "Discovery", "Quote", "Close"] if not athena else ["Listen", "Understand", "Handle", "Follow up"]
    # the run round the bases in pencil: out of the box to first, round to second and third, and home
    o.append(f'<path d="M{hm[0]} {hm[1]} L{b1[0]} {b1[1]} L{b2[0]} {b2[1]} L{b3[0]} {b3[1]} L{hm[0]} {hm[1]}" stroke="{route}" stroke-width="5" fill="none" stroke-linejoin="round" opacity=".85"/>')
    for (xa, ya), (xb, yb) in [(hm, b1), (b1, b2), (b2, b3), (b3, hm)]:
        mx, my = (xa + xb) / 2, (ya + yb) / 2; ang = math.degrees(math.atan2(yb - ya, xb - xa))
        o.append(f'<path d="M-7 -6 L5 0 L-7 6" stroke="{route}" stroke-width="4" fill="none" transform="translate({mx:.0f} {my:.0f}) rotate({ang:.0f})"/>')
    for (x, y) in (b1, b2, b3):
        o.append(f'<rect x="{x - 8}" y="{y - 8}" width="16" height="16" fill="#fff" stroke="{ink}" stroke-width="2" transform="rotate(45 {x} {y})"/>')
    o.append(f'<path d="M{hm[0] - 9} {hm[1] - 7} h18 v5 l-9 7 l-9 -7z" fill="#fff" stroke="{ink}" stroke-width="2"/>')
    # the four stops, written by the bases: the first at first base, the last coming home
    for i, (x, y, anc) in enumerate([(b1[0] + 20, b1[1] + 7, "start"), (b2[0] + 20, b2[1] + 8, "start"),
                                      (b3[0] - 20, b3[1] + 7, "end"), (hm[0] + 22, hm[1] + 3, "start")]):
        o.append(f'<text x="{x}" y="{y}" text-anchor="{anc}" font-family="Georgia, serif" font-weight="bold" font-size="20" fill="{ink}">{i + 1} {stops[i]}</text>')
    o.append(f'<circle cx="{hm[0]}" cy="{hm[1]}" r="7" fill="{route}" stroke="#fff" stroke-width="2" opacity="0">{am("opacity", ["1", "1"], 8)}'
             f'<animateMotion path="M0 0L160 -64L0 -126L-160 -64Z" dur="8s" repeatCount="indefinite"/></circle>')
    o.append(f'<text x="{x0 + 22}" y="{y0 + 58}" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="{route}" opacity=".8">K</text>')
    o.append(f'<text x="{x1 - 52}" y="{y0 + 58}" font-family="Georgia, serif" font-weight="bold" font-size="20" fill="{route}" opacity=".8">HR</text>')
    o.append('</g>')
    o.append('<g><g transform="rotate(-24 1240 150)"><rect x="1170" y="144" width="150" height="11" rx="2" fill="#f2c230"/><path d="M1170 144 l-20 5.5 l20 5.5z" fill="#e8c89a"/><path d="M1157 147.5 l-7 2 l7 2z" fill="#2a2a2a"/><rect x="1312" y="144" width="16" height="11" fill="#e88a9a"/></g>'
             + mv(["0 0", "-6 -4", "4 -2", "0 0"], 4) + '</g>')
    return vwrap(''.join(o))

def v_service(n):  # the grounds crew: the drag behind the cart, a rake on the line, the hose wetting the dirt
    p = P(n); o = [base(n, sky=("#4f80c0", "#efbd88", "#f9e0b6"))]
    o.append(moon(1250, 54, 18) if n else sun(1250, 58, 20))
    o.append(stands_band(p, n, 66, 128, 6))
    o.append(wall_band(p, 128, 18, [(700, 200, "NO LAPSE LEAGUE")]))
    o.append(turf(p, 146))
    o.append(f'<path d="M0 240 L0 196 Q800 168 1600 196 L1600 240Z" fill="{p["dirt"]}"/>')
    # the utility cart pulling the drag mat, the fresh-dragged dirt behind it in neat arcs
    for k in range(4): o.append(f'<path d="M420 {204 + k * 7} Q560 {192 + k * 7} 700 {200 + k * 7}" stroke="{p["dirt2"]}" stroke-width="2" fill="none"/>')
    o.append(f'<rect x="690" y="196" width="80" height="12" fill="#6a6a62"/><path d="M770 202 L812 194" stroke="#3a3a3a" stroke-width="3"/>')
    o.append(f'<g><rect x="812" y="174" width="96" height="22" rx="4" fill="#2f6a4a"/><rect x="860" y="148" width="4" height="28" fill="#3a3a3a"/>'
             f'<rect x="856" y="144" width="58" height="6" fill="#2f6a4a"/><rect x="904" y="148" width="4" height="28" fill="#3a3a3a"/>'
             + guy(872, 180, 1.05, "sit", jer="#e98a2a", pants="#3a4a3a", cap="#f2c230", skin=p["skin"]) + mv(["0 0", "0 -1.5", "0 0", "0 -1", "0 0"], 1.2) + '</g>'
             '<circle cx="834" cy="198" r="10" fill="#222"/><circle cx="890" cy="198" r="10" fill="#222"/>')
    # the rake on the baseline
    o.append(bob(guy(1070, 214, 1.5, "rake", jer="#e98a2a", pants="#3a4a3a", cap="#f2c230", skin=p["skin"])
                 + f'<line x1="1090" y1="160" x2="1150" y2="214" stroke="{p["dirt2"]}" stroke-width="4"/><path d="M1134 214 h34" stroke="#5a5a5a" stroke-width="5"/>', 0, 2.4, dx=16))
    # the hose
    o.append(guy(560, 214, 1.5, "point", jer="#e98a2a", pants="#3a4a3a", cap="#f2c230", skin=p["skin"]))
    o.append(f'<path d="M592 130 Q640 110 690 160" stroke="#cfe8f5" stroke-width="5" fill="none" opacity=".8" stroke-dasharray="14 6"><animate attributeName="stroke-dashoffset" values="0;-40" dur="1s" repeatCount="indefinite"/></path>'
             f'<path d="M594 134 Q648 122 676 172" stroke="#cfe8f5" stroke-width="3" fill="none" opacity=".6" stroke-dasharray="8 6"><animate attributeName="stroke-dashoffset" values="0;-28" dur=".8s" repeatCount="indefinite"/></path>')
    o.append('<path d="M560 200 Q500 230 440 222" stroke="#2f8a3a" stroke-width="4" fill="none"/>')
    o.append(corners())
    return vwrap(''.join(o))

def bunting(x0, x1, y, k, cols):
    """half-moon bunting swags hung along a rail"""
    o = []; w = (x1 - x0) / k
    for i in range(k):
        x = x0 + i * w
        for j, c in enumerate(cols):
            r_ = w / 2 - j * 7
            o.append(f'<path d="M{x + j * 7:.0f} {y} A{r_:.0f} {r_ * .7:.0f} 0 0 0 {x + w - j * 7:.0f} {y}Z" fill="{c}"/>')
    return ''.join(o)

def v_renewals(n):  # opening day: bunting on the rail, the whole roster lined up on the baseline, balloons going up
    p = P(n); o = [base(n, sky=("#4f8ad0", "#a8cfee", "#f2f2e2"), star=24)]
    o.append(moon(1270, 54, 18) if n else sun(1270, 58, 20))
    o.append(stands_band(p, n, 60, 132, 7))
    o.append(bunting(0, 1600, 132, 8, ["#b0262a", "#f6f3ea", "#1f3f7a"]))
    o.append(wall_band(p, 132, 20, []))
    o.append(turf(p, 152))
    o.append(f'<path d="M0 216 L1600 192" stroke="{p["chalk"]}" stroke-width="3"/>')
    for i in range(9):
        x = 500 + i * 70; y = 214 - i * 70 * 24 / 1600
        o.append(guy(x, y, 1.15, "stand", jer="#f4f2ec" if i % 2 else "#e8e4da", pants="#f4f2ec", cap="#1f3f7a", skin=["#dba67c", "#a8744e", "#f0c8a0", "#7a4e32"][i % 4]))
    o.append(rock(guy(1180, 194, 1.2, "point", jer="#1f3f7a", pants="#d8d8d0", flip=True, skin=p["skin"]), 1180, 194, 3, 2))
    r = random.Random(3); bl = ['', '', '']
    for i in range(10):
        x = r.randint(470, 1140); y = r.randint(30, 110); c = r.choice(["#b0262a", "#f6f3ea", "#2f6ab0", "#f2c230"])
        bl[i % 3] += f'<path d="M{x} {y + 13} q-3 12 2 22" stroke="#fff" stroke-width="1" fill="none" opacity=".6"/><ellipse cx="{x}" cy="{y}" rx="9" ry="12" fill="{c}"/>'
    for i, b in enumerate(bl): o.append(bob(b, 10 + i * 3, 4 + i, i * .7, dx=4 - i * 4))
    o.append(corners())
    return vwrap(''.join(o))

def v_claims(n):  # the rain delay: the crew running the tarp over the infield, the sky open
    p = P(n); o = [base(n, sky=("#5a6676", "#8a96a4", "#b8c0c6"), nt=("#05070f", "#10161f", "#1c232e"), star=0)]
    for x in (300, 760, 1240): o.append(f'<ellipse cx="{x}" cy="40" rx="260" ry="30" fill="{"#6a7484" if not n else "#161c28"}"/>')
    o.append(stands_band(p, n, 74, 132, 8, rows=4))
    o.append(wall_band(p, 132, 18, []))
    o.append(turf(p, 150, "#4e7e3e" if not n else "#244a26"))
    # the tarp pulled out over the infield, its roll still turning at the far edge
    tp = "#2f5a8a" if not n else "#1f3a5a"
    o.append(f'<path d="M430 236 L560 168 L1120 168 L1240 236Z" fill="{tp}"/><path d="M560 168 L1120 168" stroke="#fff" stroke-width="2" opacity=".3"/>')
    o.append(f'<rect x="460" y="200" width="680" height="3" fill="#fff" opacity=".12"/>')
    o.append(f'<rect x="1110" y="160" width="40" height="72" rx="18" fill="{tp}" stroke="#14283e" stroke-width="3" transform="rotate(-28 1130 196)"/>')
    for i, x in enumerate((620, 800, 980)):
        o.append(bob(guy(x, 172 - i * 0, 1.0, "run", jer="#e98a2a", pants="#3a4a3a", cap="#f2c230", skin=p["skin"]), 3, .5, i * .15))
    o.append(bob(guy(1210, 216, 1.3, "run", jer="#e98a2a", pants="#3a4a3a", cap="#f2c230", skin=p["skin"], flip=True), 4, .55))
    # the rain and the puddles
    r = random.Random(4)
    o.append('<g stroke="#dfe8ee" stroke-width="1.6" opacity=".55">' + ''.join(f'<line x1="{x}" y1="{y}" x2="{x - 6}" y2="{y + 18}"/>' for x, y in [(r.randint(0, 1600), r.randint(40, 200)) for _ in range(70)])
             + '<animateTransform attributeName="transform" type="translate" values="0 0;-8 24" dur=".5s" repeatCount="indefinite"/></g>')
    for x, y, w in [(320, 186, 60), (1340, 190, 70)]: o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="5" fill="#cfe0ea" opacity=".35">{am("rx", [str(w), str(w + 8), str(w)], 2.5)}</ellipse>')
    o.append(corners("#0b131a"))
    return vwrap(''.join(o))

def v_commercial(n):  # the luxury boxes: a level of glass suites over the stands, each one somebody's business
    p = P(n); o = [base(n, sky=("#4a74b0", "#e8a87a", "#f4d2a6"))]
    o.append(stands_band(p, n, 168, 240, 9, rows=3))
    o.append(f'<rect x="0" y="40" width="1600" height="128" fill="{p["conc"]}"/><rect x="0" y="36" width="1600" height="8" fill="{p["roof"]}"/>')
    o.append(f'<rect x="0" y="154" width="1600" height="14" fill="{p["wall"]}"/>')
    names = ["SUITE 1", "SUITE 2", "BUSINESS OWNERS BOX", "SUITE 4", "SUITE 5"]
    for i in range(5):
        x = 330 + i * 196; w = 176
        if n: o.append(f'<circle cx="{x + w / 2:.0f}" cy="104" r="110" fill="url(#glow)" opacity=".45">{am("opacity", [".45", ".3", ".45"], 4 + i % 3, i * .6)}</circle>')
        o.append(f'<rect x="{x}" y="66" width="{w}" height="82" fill="{p["glass"]}" stroke="{p["steel2"]}" stroke-width="4"/>')
        o.append(f'<rect x="{x + w / 2 - 1:.0f}" y="66" width="2" height="82" fill="{p["steel2"]}"/>')
        o.append(f'<rect x="{x}" y="50" width="{w}" height="14" fill="{p["wall"]}"/><text x="{x + w / 2:.0f}" y="61" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="10" fill="{p["ink"]}" letter-spacing="1.5">{names[i]}</text>')
        for j in range(2 + i % 2):
            px = x + 30 + j * 52
            hd = f'<circle cx="{px}" cy="100" r="9" fill="{["#c89a76", "#8a5a3a", "#e8c09a"][j % 3]}"/>'
            o.append((rock(hd, px, 112, 6, 2 + j * .6, (i + j) * .4) if i else hd) + f'<path d="M{px - 14} 148 q14 -40 28 0z" fill="{["#2a3a5a", "#5a2a2a", "#3a3a3a"][(i + j) % 3]}"/>')
        o.append(f'<rect x="{x}" y="140" width="{w}" height="8" fill="{p["steel"]}" opacity=".7"/>')
    o.append(corners())
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the home run trot: premium over the wall"],
    "messages": ["Texts & Emails", "the press box: every call on the air"],
    "coaching": ["Coaching", "the batting cage: every swing, looked at"],
    "roleplay": ["Role Play", "the bullpen: warm up before you go in"],
    "rphistory": ["Session History", "the replay screen: every at-bat, again"],
    "training": ["Training", "spring practice: the fundamentals"],
    "blueprint": ["Apollo's Road Map", "the scorecard, in plain words"],
    "athenamap": ["Athena's Road Map", "the service scorecard, in plain words"],
    "service": ["Service Digest", "the grounds crew: keeping the book in shape"],
    "renewals": ["Renewals", "opening day: what came back"],
    "claims": ["Claims", "the rain delay: after the storm"],
    "commercial": ["Commercial Center", "the luxury boxes: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=26):
    return defs(skyg(n, day=day, nt=nt)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 80, 21) if n else '')

def s_park(p, n, seed, wall=84, grass=None, seat=None, crowd=True):
    """the strip's ballpark: a run of stands, the outfield wall, the grass; only units ~45-115 show"""
    o = []
    if crowd:
        q = dict(p)
        if seat: q["seat"] = seat
        o.append(stands_band(q, n, wall - 22, wall, seed, rows=2))
    else:
        o.append(f'<rect x="0" y="{wall - 22}" width="1600" height="22" fill="{seat or p["seat"]}"/>' + ''.join(f'<rect x="0" y="{y}" width="1600" height="2" fill="#000" opacity=".25"/>' for y in (wall - 15, wall - 7)))
    o.append(f'<rect x="0" y="{wall}" width="1600" height="9" fill="{p["wall"]}"/><rect x="0" y="{wall - 1}" width="1600" height="2" fill="{p["pole"]}" opacity=".8"/>')
    o.append(f'<rect x="0" y="{wall + 9}" width="1600" height="{S - wall - 9}" fill="{grass or p["grass"]}"/>')
    return ''.join(o)

def burst(cx, cy, rr, c):
    d = ''.join(f'M{cx + rr * .3 * math.cos(i / 12 * 2 * math.pi):.0f} {cy + rr * .3 * math.sin(i / 12 * 2 * math.pi):.0f}L{cx + rr * math.cos(i / 12 * 2 * math.pi):.0f} {cy + rr * math.sin(i / 12 * 2 * math.pi):.0f}' for i in range(12))
    return f'<path d="{d}" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="3" fill="#fff"/>'

def s_sold(n):  # the home run: the swing finished, the ball sailing over the wall, fireworks over the stands
    p = P(n); o = [sbase(n, ("#2a3a70", "#c86a6a", "#f4a868"), ("#050816", "#121a3c", "#28305a"))]
    o.append(s_park(p, n, 31))
    for cx, cy, c, rr in [(760, 58, "#ffd27a", 18), (930, 50, "#ff7a6a", 20), (1110, 60, "#8ad0ff", 16)]:
        o.append(burst(cx, cy, rr, c))
    o.append(f'<ellipse cx="560" cy="111" rx="60" ry="5" fill="{p["dirt"]}"/>')
    o.append(guy(556, 112, .95, "swing", jer="#f4f2ec", pants="#f4f2ec", helmet=True, bat=("lh", -26, -6), skin=p["skin"]))
    for i in range(1, 10):
        t = i / 10; x = 590 + 640 * t; y = 64 - 50 * t * (1 - t) * 1.6 - 6 * t
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.8" fill="#fff" opacity="{.3 + t * .5:.2f}"/>')
    o.append(baseball(1236, 54, 4.5))
    return wrap(S, ''.join(o))

def s_open(n):  # a runner on third, leading off, home plate ninety feet away
    p = P(n); o = [sbase(n, ("#4f88c6", "#a6cce6", "#eef0dc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(s_park(p, n, 32))
    o.append(f'<path d="M0 160 L0 104 Q800 96 1600 104 L1600 160Z" fill="{p["dirt"]}"/>')
    o.append(f'<path d="M300 116 L1240 104" stroke="{p["chalk"]}" stroke-width="2.6"/>')
    o.append(f'<path d="M598 114 l18 -4 l14 4 l-18 4z" fill="{p["chalk"]}"/>')    # third base
    o.append(f'<path d="M1100 102 h20 v5 l-10 6 l-10 -6z" fill="{p["chalk"]}"/>')  # home, still to go
    o.append(guy(700, 112, .95, "lead", jer="#f4f2ec", pants="#f4f2ec", helmet=True, skin=p["skin"]))
    o.append(f'<path d="M740 100 H1080" stroke="#fff" stroke-width="2.4" stroke-dasharray="6 9" opacity=".75"/><path d="M1072 94 l10 6 l-10 6" stroke="#fff" stroke-width="2.4" fill="none" opacity=".75"/>')
    return wrap(S, ''.join(o))

GREY = ("#6c7078", "#9a9ea6", "#c2c4c8"), ("#0a0c12", "#181b24", "#262a34")
def s_lost(n):  # struck out under a grey sky: the batter walks off dragging the bat, the umpire rings him up
    p = P(n); o = [sbase(n, *GREY, 6)]
    for x in (300, 760, 1200): o.append(f'<ellipse cx="{x}" cy="40" rx="240" ry="18" fill="{"#7a7e86" if not n else "#1e212a"}"/>')
    q = dict(p); q.update(wall="#3a4a40" if not n else "#0e1a14", pole="#8a8a70")
    o.append(s_park(q, True, 33, grass="#6a7e5a" if not n else "#1c3020", seat="#4a5260" if not n else "#151a24"))
    o.append(f'<ellipse cx="820" cy="112" rx="300" ry="12" fill="{"#9a8a70" if not n else "#3a3024"}"/>')
    o.append(f'<path d="M850 108 h20 v5 l-10 6 l-10 -6z" fill="#e8e4da"/>')
    o.append(guy(660, 113, .95, "slump", jer="#d8d8d0", pants="#d8d8d0", cap="#4a5a6a", helmet=True, bat=("lh", -24, 28), skin="#b89478", flip=True))
    o.append(guy(950, 113, .95, "punch", jer="#2a3040", pants="#6a6e76", cap="#1a1a1a", flip=True, skin="#b89478"))
    o.append(guy(898, 113, .85, "crouch", jer="#4a5a6a", pants="#d8d8d0", cap="#2a2a2a", mask=True, glove="lh", flip=True, skin="#b89478"))
    return wrap(S, ''.join(o))

def s_dead(n):  # a rain-out: the tarp on the infield, the rain still coming, nobody playing today
    p = P(n); o = [sbase(n, ("#6a7480", "#8e98a2", "#aeb6bc"), ("#06080e", "#121820", "#1e2630"), 0)]
    for x in (260, 700, 1160): o.append(f'<ellipse cx="{x}" cy="40" rx="250" ry="20" fill="{"#5e6874" if not n else "#151b24"}"/>')
    q = dict(p); q.update(wall="#3a4a40" if not n else "#0e1a14", pole="#7a7a68")
    o.append(s_park(q, n, 34, grass="#557048" if not n else "#1c3020", seat="#4a5260" if not n else "#151a24", crowd=False))
    tp = "#3a5a7a" if not n else "#1c2c40"
    o.append(f'<path d="M460 122 L560 96 L1060 96 L1160 122Z" fill="{tp}"/><path d="M560 96 L1060 96" stroke="#fff" stroke-width="2" opacity=".3"/>')
    o.append(''.join(f'<path d="M{560 + k * 100} 96 L{520 + k * 120} 122" stroke="#000" stroke-width="1.5" opacity=".18"/>' for k in range(1, 5)))
    for x, w in [(660, 60), (900, 80)]: o.append(f'<ellipse cx="{x}" cy="108" rx="{w}" ry="3.5" fill="#cfe0ea" opacity=".35"/>')
    r = random.Random(6)
    o.append('<g stroke="#dfe8ee" stroke-width="1.6" opacity=".5">' + ''.join(f'<line x1="{x}" y1="{y}" x2="{x - 5}" y2="{y + 14}"/>' for x, y in [(r.randint(300, 1300), r.randint(40, 110)) for _ in range(46)]) + '</g>')
    return wrap(S, ''.join(o))

def s_reached(n):  # two players at the mound, gloves up over their mouths, talking it over
    p = P(n); o = [sbase(n, ("#5a94c8", "#a8d0ea", "#eef0dc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(s_park(p, n, 35))
    o.append(f'<ellipse cx="800" cy="112" rx="170" ry="11" fill="{p["dirt"]}"/><rect x="788" y="109" width="24" height="3" fill="{p["chalk"]}"/>')
    o.append(guy(772, 113, .95, "mouth", jer="#f4f2ec", pants="#f4f2ec", cap="#1f3f7a", glove="lh", skin=p["skin"]))
    o.append(guy(830, 113, .95, "mouth", jer="#1f3f7a", pants="#d8d8d0", cap="#2a2a2a", glove="lh", flip=True, skin=p["skin"]))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # a batter in the on-deck circle, down on one knee, waiting a turn
    p = P(n); o = [sbase(n, ("#d98a4a", "#f2c27a", "#fbe6b8"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(s_park(p, n, 36))
    o.append(f'<ellipse cx="770" cy="111" rx="80" ry="9" fill="{p["dirt2"]}"/><ellipse cx="770" cy="111" rx="72" ry="7" fill="{p["dirt"]}"/>')
    o.append(guy(760, 112, .95, "kneel", jer="#f4f2ec", pants="#f4f2ec", helmet=True, cap="#1f3f7a", bat=("lh", -18, -34), skin=p["skin"]))
    o.append(f'<line x1="820" y1="112" x2="834" y2="88" stroke="#a8743c" stroke-width="3.4"/><circle cx="835" cy="87" r="4" fill="#3a3a3a"/>')
    return wrap(S, ''.join(o))

def s_vm(n):  # the empty park at night: the lights out, the seats empty, the moon over centre field
    p = P(True); o = [sbase(True, ("#141c38", "#1e2a50", "#2c3a64"), ("#03050c", "#080d1e", "#121a34"), 34)]
    if not n: o.append(stars(16, 0, 1600, 0, 70, 22))
    o.append(moon(1040, 56, 11))
    for x in (560, 900):
        o.append(tower(x, 72, 46, 44, p, False, banks=(2, 4)))
    q = dict(p); q.update(wall="#0b1f15", pole="#4a4a3a")
    o.append(s_park(q, True, 37, wall=92, grass="#14301c", seat="#10182a", crowd=False))
    o.append(f'<ellipse cx="760" cy="112" rx="220" ry="11" fill="#3a2a1c"/><path d="M750 108 h20 v5 l-10 6 l-10 -6z" fill="#6a6a6a"/>')
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}
# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Batter up, {n}.", "Step up to the plate, {n}.", "Keep your eye on the ball, {n}.", "Swing for the fences, {n}.",
             "Play ball, {n}!", "Bases loaded, {n}. Bring them home.", "Full count, full coverage, {n}.",
             "Every at-bat counts, {n}.", "Round the bases and close it, {n}.", "Safe at home, {n}.",
             "Lead off strong today, {n}.", "Hit 'em where they ain't, {n}.", "Knock it out of the park, {n}.",
             "The bullpen's warm, {n}. You're in.", "Touch every base, {n}."]

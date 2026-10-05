"""The Carnival world: one county-fair midway at dusk. Colour looks, fonts, the Digest picture, page banners, card strips."""
import random, math

KEY = "carnival"
NAME = "Carnival"
CATEGORY = "Fun"   # the group it is listed under in Settings
FONTS = "family=Rye&family=Nunito+Sans:wght@400;500;600;700"
DISPLAY = "'Rye', Georgia, serif"
DW = 400   # Rye has one weight
BODY = "'Nunito Sans', system-ui, sans-serif"
SKY_BG = (("#8a7f9e", "#9c7e4c"), ("#080b20", "#1d1712"))

LOOKS = [
    ("midway", "Midway",
     "--surface: #f4ede0; --surface-raised: #fffaf1; --card2: #f8f1e3; --chip: #eee2cb; --text-primary: #2a1a14; --text-muted: #6b5648; --text-secondary: #54402f; --grid: #ebdfc9; --border: #e2d3b8; --border-strong: #c8af88; --accent: #b3271e; --accent-d: #8c1c15; --side: #5a1612; --side2: #731f18; --sideInk: #f7e6c8; --brand: #fbefd6; --brand2: #f2b632; --rad: 14px;",
     "--surface: #150e0c; --surface-raised: #1f1512; --card2: #271b17; --chip: #31221d; --text-primary: #f3e6d6; --text-muted: #b49d8a; --text-secondary: #cdb8a4; --grid: #31221d; --border: #35251f; --border-strong: #4d362b; --accent: #f2b632; --accent-d: #f7cd6b; --side: #0d0706; --side2: #1c100d; --sideInk: #f7e6c8; --brand: #fbefd6; --brand2: #f2b632;",
     ["#f4ede0", "#5a1612", "#f2b632"]),
    ("bigtop", "Big Top",
     "--surface: #eaeef5; --surface-raised: #fafbfe; --card2: #f0f3f9; --chip: #dfe5f0; --text-primary: #141c33; --text-muted: #56607a; --text-secondary: #424c66; --grid: #dde3ee; --border: #d3dae7; --border-strong: #b2bdd2; --accent: #1f3a8a; --accent-d: #162a66; --side: #13214d; --side2: #1c2d63; --sideInk: #e2e8f6; --brand: #f2f5fb; --brand2: #ffcf3a; --rad: 12px;",
     "--surface: #0b0f1d; --surface-raised: #121831; --card2: #18203b; --chip: #202a48; --text-primary: #e7ecf8; --text-muted: #9ba6c2; --text-secondary: #b5bfd6; --grid: #202a48; --border: #232d4d; --border-strong: #33416a; --accent: #ffcf3a; --accent-d: #ffdf7a; --side: #060914; --side2: #0e1530; --sideInk: #e2e8f6; --brand: #f2f5fb; --brand2: #ffcf3a;",
     ["#eaeef5", "#13214d", "#ffcf3a"]),
    ("cottoncandy", "Cotton Candy",
     "--surface: #e8f2f8; --surface-raised: #f9fcfe; --card2: #eef6fa; --chip: #dbebf4; --text-primary: #10263a; --text-muted: #4f6577; --text-secondary: #3b5266; --grid: #dae8f1; --border: #cfe1ec; --border-strong: #a8c7d9; --accent: #0f6a98; --accent-d: #0a5277; --side: #123a52; --side2: #1a4b68; --sideInk: #e3f1f8; --brand: #f1f8fc; --brand2: #f6e36a; --rad: 16px;",
     "--surface: #0b141b; --surface-raised: #111d26; --card2: #172530; --chip: #1e2f3b; --text-primary: #e4f0f7; --text-muted: #98afbf; --text-secondary: #b2c6d3; --grid: #1e2f3b; --border: #213441; --border-strong: #2f4859; --accent: #7fcbf0; --accent-d: #a9ddf6; --side: #060c11; --side2: #0e1b25; --sideInk: #e3f1f8; --brand: #f1f8fc; --brand2: #f6e36a;",
     ["#e8f2f8", "#123a52", "#f6e36a"]),
]

TOUR = {"k": "Ringmaster", "next": "Next ride", "back": "Back", "done": "Ta-da!", "skip": "Leave the fair"}

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(grass="#1a2215", grass2="#141b10", dirt="#4c3a28", dirt2="#3b2c1e", tree="#0b1110",
                    red="#b8332a", red2="#82231c", gold="#e0a52c", gold2="#a87a1a", teal="#1b8580", teal2="#11605c",
                    purple="#58358c", purple2="#3d2466", cream="#d9caa8", cream2="#b3a582", wood="#4e3322", wood2="#2f1e13",
                    steel="#8a8796", steel2="#5e5b6a", dark="#1c120c", win="#ffcf6a", bulb="#ffd978", bulbon="#ffffff",
                    skin="#c0906a", skin2="#86583c", wheel="#a6a3b2", navy="#1b2347", ink="#fff3d6", hair="#20140c")
    return dict(grass="#7c8a48", grass2="#6d7a3e", dirt="#d6ab70", dirt2="#bf935a", tree="#3c4a35",
                red="#d23a2e", red2="#a32a22", gold="#f2b632", gold2="#cf8f1d", teal="#1f9a95", teal2="#167570",
                purple="#6b3fa0", purple2="#4f2d7a", cream="#f7ecd4", cream2="#e0cfab", wood="#8a5a34", wood2="#62401f",
                steel="#f3eee4", steel2="#cbc3b3", dark="#3b2519", win="#ffd77a", bulb="#ffe08a", bulbon="#fffbe6",
                skin="#e2b48c", skin2="#b07a52", wheel="#f6f2e8", navy="#24305e", ink="#fff6de", hair="#3a2618")

DAYSKY = ("#3b5598", "#d98a58", "#f6cf86")
NIGHTSKY = ("#04071a", "#10173a", "#251f4a")

def f(v): return f"{v:.0f}"

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc85a" stop-opacity=".55"/>'
            '<stop offset="1" stop-color="#ffc85a" stop-opacity="0"/></radialGradient>' + extra + '</defs>')

def skyg(n, day=DAYSKY, nt=NIGHTSKY, id="g"):
    c = nt if n else day
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/>'
            f'<stop offset=".62" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

def stars(k, x0, x1, y0, y1, seed, op=(0.35, 0.55, 0.85)):
    r = random.Random(seed); o = []
    for _ in range(k):
        o.append(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([0.7, 1, 1.3, 1.8])}" fill="#fff" opacity="{r.choice(op)}"/>')
    return ''.join(o)

def moon(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.8}" fill="#e9eefc" opacity=".1"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4efdc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#ddd6bd"/>'
            f'<circle cx="{x + r * .3:.0f}" cy="{y + r * .3:.0f}" r="{r * .12:.0f}" fill="#ddd6bd"/>')

def cloud(x, y, w, op=.5, c="#fff2dc"):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="9" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .12:.0f}" cy="{y - 8}" rx="{w * .3:.0f}" ry="9" fill="{c}" opacity="{op * .85:.2f}"/>')

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s} {y - 3 * s} Q{x - 5 * s} {y - 7 * s} {x} {y} Q{x + 5 * s} {y - 7 * s} {x + 10 * s} {y - 3 * s}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

# ---- movement: SMIL only, self-closing, so build.py's still copy (every <animate*/> taken out) is the resting picture
def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {b};{deg} {x} {b};{-deg} {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

def SP(k): return ';'.join(['.45 0 .55 1'] * k)   # keySplines for k segments, eased

def bulbs(d, S, n, w=6, chase=None, glow=True, wire="#2a1c14", ws=1.6):
    """a string of bulbs on a wire: one path draws every bulb (zero-length dashes with round caps); when chase is a
    duration, every third bulb is lit brighter and the lit ones hop along one bulb at a time"""
    p = P(n); o = []
    if wire: o.append(f'<path d="{d}" fill="none" stroke="{wire}" stroke-width="{ws}"/>')
    if n and glow: o.append(f'<path d="{d}" fill="none" stroke="{p["bulb"]}" stroke-width="{w * 3.2:.0f}" stroke-linecap="round" stroke-dasharray="0 {S}" opacity=".16"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{p["bulb"]}" stroke-width="{w}" stroke-linecap="round" stroke-dasharray="0 {S}"/>')
    if chase:
        o.append(f'<g fill="none" stroke-linecap="round" stroke-dasharray="0 {S * 3}">'
                 f'<path d="{d}" stroke="{p["bulbon"]}" stroke-width="{w * 2.6:.1f}" opacity="{.32 if n else .22}"/>'
                 f'<path d="{d}" stroke="{p["bulbon"]}" stroke-width="{w + 1}"/>'
                 f'<animate attributeName="stroke-dashoffset" values="0;{-S};{-2 * S}" dur="{chase}s" calcMode="discrete" repeatCount="indefinite"/></g>')
    return ''.join(o)

def sag(x0, y0, x1, y1, s):
    """a wire hung between two points, sagging s units at its middle"""
    cx = (x0 + x1) / 2; cy = (y0 + y1) / 2 + 2 * s
    return f"M{x0:.0f} {y0:.0f} Q{cx:.0f} {cy:.0f} {x1:.0f} {y1:.0f}"

def pole(x, top, base, c, w=6, cap=None):
    return (f'<rect x="{x - w / 2:.1f}" y="{top}" width="{w}" height="{base - top}" fill="{c}"/>'
            + (f'<circle cx="{x}" cy="{top}" r="{w * .9:.1f}" fill="{cap}"/>' if cap else ''))

def pennant(x, y, h, c, wave=False, dur=1.6):
    d0 = f"M{x} {y} Q{x + h * .5:.0f} {y + h * .06:.0f} {x + h:.0f} {y + h * .2:.0f} L{x} {y + h * .42:.0f}Z"
    d1 = f"M{x} {y} Q{x + h * .5:.0f} {y + h * .26:.0f} {x + h * .96:.0f} {y + h * .14:.0f} L{x} {y + h * .42:.0f}Z"
    a = f'<animate attributeName="d" values="{d0};{d1};{d0}" dur="{dur}s" repeatCount="indefinite"/>' if wave else ''
    return f'<path d="{d0}" fill="{c}">{a}</path>'

# ---- people: drawn standing on (x, y), ~72 units tall at s=1, facing right
def person(x, y, s, shirt, pants, skin, hair="#3a2618", pose="stand", flip=False, extra='', long_hair=False):
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{pants}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    arm = f'stroke="{shirt}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    legs = {"walk": "M-9 0 L-2 -30 M10 -1 L2 -30", "lean": "M-10 0 L-4 -30 M8 0 L2 -30"}.get(pose, "M-5 0 L-3 -30 M6 0 L3 -30")
    arms = {"stand": "M6 -52 L10 -32 M-6 -52 L-10 -32",
            "walk": "M6 -52 L12 -36 M-6 -52 L-12 -38",
            "toss": "M6 -52 L20 -58 L32 -64 M-6 -52 L-10 -34",
            "up": "M6 -52 L12 -68 L14 -84 M-6 -52 L-10 -34",
            "hammer": "M6 -52 L6 -76 M-6 -52 L2 -78",
            "hold": "M6 -52 L14 -40 L22 -44 M-6 -52 L-10 -34",
            "lever": "M6 -52 L18 -40 L26 -38 M-6 -52 L-10 -34",
            "pull": "M6 -52 L22 -46 L34 -44 M-6 -52 L16 -48 L34 -44",
            "cheer": "M6 -52 L16 -68 L20 -80 M-6 -52 L-16 -68 L-20 -80",
            "point": "M6 -52 L22 -58 L34 -62 M-6 -52 L-10 -34"}.get(pose, "M6 -52 L10 -32 M-6 -52 L-10 -32")
    lean = ' transform="rotate(-10 0 -30)"' if pose == "lean" else ''
    hr = (f'<path d="M-8 -64 Q-9 -74 0 -74 Q9 -74 8 -64 L9 -54 L5 -58 L4 -66 L-4 -66 L-5 -58 L-9 -54Z" fill="{hair}"/>' if long_hair
          else f'<path d="M-8 -64 Q-8 -74 0 -74 Q8 -74 8 -64 Q4 -69 -8 -64Z" fill="{hair}"/>')
    b = (f'<path d="{legs}" {leg}/><ellipse cx="-6" cy="0" rx="5" ry="2.4" fill="#2a2420"/><ellipse cx="7" cy="0" rx="5" ry="2.4" fill="#2a2420"/>'
         f'<g{lean}><path d="M-9 -56 Q0 -60 9 -56 L8 -28 L-8 -28Z" fill="{shirt}"/><path d="{arms}" {arm}/>'
         f'<circle cx="0" cy="-64" r="7.5" fill="{skin}"/>{hr}{extra}</g>')
    return g + b + '</g>'

def balloon(x, y, r, c, string_to=None, shine=True):
    o = []
    if string_to: o.append(f'<path d="M{x} {y + r * 1.15:.0f} Q{x - 6} {(y + string_to[1]) / 2:.0f} {string_to[0]} {string_to[1]}" stroke="#f3eadb" stroke-width="1.4" fill="none" opacity=".8"/>')
    o.append(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 1.18:.1f}" fill="{c}"/><path d="M{x - 3} {y + r * 1.3:.0f} L{x} {y + r * 1.12:.0f} L{x + 3} {y + r * 1.3:.0f}Z" fill="{c}"/>')
    if shine: o.append(f'<ellipse cx="{x - r * .35:.1f}" cy="{y - r * .4:.1f}" rx="{r * .22:.1f}" ry="{r * .34:.1f}" fill="#fff" opacity=".45"/>')
    return ''.join(o)

def horse(x, y, s, body, mane, saddle, flip=False):
    """a carousel horse on its pole at (x, y), facing left, front legs tucked, back legs out"""
    lg = f'stroke="{body}" stroke-width="5" fill="none" stroke-linecap="round"'
    return (f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
            f'<path d="M-15 4 L-24 12 L-30 6 M-10 6 L-16 18 L-22 16 M14 5 L26 14 M10 6 L18 20" {lg}/>'
            f'<path d="M22 -4 Q36 -4 34 14" stroke="{mane}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="0" rx="24" ry="10" fill="{body}"/>'
            f'<path d="M-14 -4 L-24 -26 Q-30 -32 -38 -24 L-40 -18 Q-36 -14 -30 -18 L-22 -10 L-8 -6Z" fill="{body}"/>'
            f'<path d="M-20 -28 Q-12 -22 -10 -8" stroke="{mane}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M-6 -10 Q2 -15 10 -10 L8 -2 L-5 -2Z" fill="{saddle}"/><circle cx="-31" cy="-24" r="1.6" fill="#2a1a10"/></g>')

def carousel(cx, base, s, p, n, anim=False):
    """the carousel, its platform's front edge on base: cone roof, scalloped crown of bulbs, horses on brass poles"""
    rx, ry = 175 * s, 30 * s
    ey = base - 180 * s               # the crown's lower edge
    pk = base - 290 * s               # the roof's peak
    def at(th, y, rr=1.0): return (cx + rx * rr * math.cos(th), y + ry * rr * math.sin(th))
    o = []; a = o.append
    if n: a(f'<ellipse cx="{cx}" cy="{(ey + base) / 2:.0f}" rx="{rx * 1.5:.0f}" ry="{(base - ey) * .9:.0f}" fill="url(#glow)"/>')
    # the platform and its skirt
    a(f'<path d="M{cx - rx:.0f} {base:.0f} A{rx:.0f} {ry:.0f} 0 0 0 {cx + rx:.0f} {base:.0f} L{cx + rx:.0f} {base + 14 * s:.0f} A{rx:.0f} {ry:.0f} 0 0 1 {cx - rx:.0f} {base + 14 * s:.0f}Z" fill="{p["gold2"]}"/>')
    a(f'<ellipse cx="{cx}" cy="{base:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{p["cream2"]}"/>')
    # the inside: a lit drum behind the horses, the centre column with its mirrors
    a(f'<path d="M{cx - rx * .96:.0f} {ey + 10 * s:.0f} L{cx + rx * .96:.0f} {ey + 10 * s:.0f} L{cx + rx * .96:.0f} {base:.0f} A{rx * .96:.0f} {ry * .9:.0f} 0 0 1 {cx - rx * .96:.0f} {base:.0f}Z" fill="{p["red2"] if not n else "#4a1a16"}" opacity=".9"/>')
    a(f'<rect x="{cx - 26 * s:.0f}" y="{ey:.0f}" width="{52 * s:.0f}" height="{base - ey:.0f}" fill="{p["gold"]}"/>')
    for k in range(3): a(f'<rect x="{cx - 20 * s + k * 14 * s:.0f}" y="{ey + 20 * s:.0f}" width="{10 * s:.0f}" height="{(base - ey) * .62:.0f}" rx="{3 * s:.0f}" fill="{"#cfe3ea" if not n else "#ffe7a0"}" opacity=".85"/>')
    # brass poles, the horses riding them
    cols = [(p["cream"], p["gold"], p["teal"]), (p["navy"] if not n else "#3a4878", p["cream"], p["red"]), (p["cream"], p["purple"], p["gold"]),
            ("#8a5a34" if not n else "#6a4a34", p["cream"], p["teal"]), (p["cream"], p["red"], p["purple"])]
    for i, th in enumerate([math.radians(d) for d in (160, 125, 90, 55, 20)]):
        x, yt = at(th, ey + 6 * s, .82); _, yb = at(th, base, .82)
        a(f'<line x1="{x:.0f}" y1="{yt:.0f}" x2="{x:.0f}" y2="{yb:.0f}" stroke="{p["gold"]}" stroke-width="{3.4 * s:.1f}"/>')
        hs = s * (1.0 + .18 * math.sin(th))
        hy = (yt + yb) / 2 + 6 * s
        body, mane, sad = cols[i]
        h = horse(x, hy, hs, body, mane, sad)
        if anim:
            up = -16 * s
            a(f'<g>{h}<animateTransform attributeName="transform" type="translate" values="0 0;0 {up:.0f};0 0" dur="3.2s" begin="{-i * .64:.2f}s" '
              f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></g>')
        else:
            a(f'<g transform="translate(0 {(-8 * s if i % 2 else 0):.0f})">{h}</g>')
    # the roof: striped cone, the crown band under it, scallops
    arc = [at(math.radians(d), ey) for d in range(0, 181, 15)]
    for k in range(len(arc) - 1):
        (x0, y0), (x1, y1) = arc[k], arc[k + 1]
        a(f'<path d="M{cx} {pk:.0f} L{x0:.0f} {y0 - 24 * s:.0f} L{x1:.0f} {y1 - 24 * s:.0f}Z" fill="{p["red"] if k % 2 else p["cream"]}"/>')
    a(f'<path d="M{cx - rx:.0f} {ey - 24 * s:.0f} A{rx:.0f} {ry:.0f} 0 0 0 {cx + rx:.0f} {ey - 24 * s:.0f} L{cx + rx:.0f} {ey:.0f} A{rx:.0f} {ry:.0f} 0 0 1 {cx - rx:.0f} {ey:.0f}Z" fill="{p["gold"]}"/>')
    sc = ''.join(f'M{x0:.0f} {y0:.0f} Q{(x0 + x1) / 2:.0f} {(y0 + y1) / 2 + 16 * s:.0f} {x1:.0f} {y1:.0f}' for (x0, y0), (x1, y1) in zip(arc, arc[1:]))
    a(f'<path d="{sc}" fill="{p["teal"]}" stroke="{p["teal2"]}" stroke-width="1"/>')
    # the finial and its pennant
    a(f'<line x1="{cx}" y1="{pk:.0f}" x2="{cx}" y2="{pk - 34 * s:.0f}" stroke="{p["gold2"]}" stroke-width="{3 * s:.1f}"/><circle cx="{cx}" cy="{pk:.0f}" r="{6 * s:.1f}" fill="{p["gold"]}"/>')
    a(pennant(cx, pk - 34 * s, 30 * s, p["teal"]))
    # the sign on the crown
    a(f'<rect x="{cx - 70 * s:.0f}" y="{ey - 22 * s + ry * .8:.0f}" width="{140 * s:.0f}" height="{18 * s:.0f}" rx="{8 * s:.0f}" fill="{p["red2"]}" stroke="{p["cream"]}" stroke-width="{1.5 * s:.1f}"/>'
      f'<text x="{cx}" y="{ey - 9 * s + ry * .8:.0f}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{12 * s:.1f}" fill="{p["ink"]}" letter-spacing="{1.5 * s:.1f}">NO LAPSE LOOP</text>')
    d = f"M{cx - rx:.0f} {ey - 25 * s:.0f} A{rx:.0f} {ry:.0f} 0 0 0 {cx + rx:.0f} {ey - 25 * s:.0f}"
    a(bulbs(d, round(math.pi * rx / 22, 1) if False else 18 * s, n, max(2.5, 5 * s), chase=2.4 if anim else None, wire=None))
    return ''.join(o)

def ferris(cx, cy, r, p, n, anim=False, legs_to=None, gk=12, ymax=9999):
    """the wheel: rim, spokes and bulbs turn about the hub; the gondolas hang plumb whatever the angle"""
    o = []; a = o.append
    wc = p["wheel"]
    cols = [p["red"], p["gold"], p["teal"]]
    if n: a(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.25:.0f}" fill="url(#glow)" opacity=".7"/>')
    if legs_to:  # the rear legs, behind the wheel
        a(f'<path d="M{cx} {cy} L{cx - r * .55:.0f} {legs_to} M{cx} {cy} L{cx + r * .55:.0f} {legs_to}" stroke="{p["steel2"]}" stroke-width="{r * .035:.1f}"/>')
    g = []
    spokes = ''.join(f'M{cx} {cy} L{cx + r * math.cos(k * math.pi / 8):.0f} {cy + r * math.sin(k * math.pi / 8):.0f}' for k in range(16))
    g.append(f'<path d="{spokes}" stroke="{wc}" stroke-width="{max(1.2, r * .012):.1f}" opacity=".9"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{wc}" stroke-width="{max(2, r * .03):.1f}"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{r * .9:.0f}" fill="none" stroke="{wc}" stroke-width="{max(1.2, r * .016):.1f}"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{r * .32:.0f}" fill="none" stroke="{wc}" stroke-width="{max(1.2, r * .016):.1f}"/>')
    zz = ''.join(f'{"M" if k == 0 else "L"}{cx + (r if k % 2 else r * .9) * math.cos(k * math.pi / 24):.0f} {cy + (r if k % 2 else r * .9) * math.sin(k * math.pi / 24):.0f}' for k in range(49))
    g.append(f'<path d="{zz}" fill="none" stroke="{wc}" stroke-width="{max(1, r * .01):.1f}" opacity=".8"/>')
    circ = 2 * math.pi * r
    rim = f"M{cx + r} {cy} A{r} {r} 0 1 1 {cx - r} {cy} A{r} {r} 0 1 1 {cx + r} {cy}"
    g.append(bulbs(rim, round(circ / 48, 2), n, max(2.5, r * .026), wire=None))
    if n: g.append(bulbs(spokes, round(r / 6, 1), n, max(2, r * .018), wire=None, glow=False))
    turn = (f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};90 {cx} {cy}" dur="12s" repeatCount="indefinite"/>' if anim else '')
    gs = r / 165
    for k in range(gk):
        th = k * 2 * math.pi / gk - math.pi / 2
        px, py = cx + r * math.cos(th), cy + r * math.sin(th)
        c = cols[k % 3]
        if py > ymax: continue
        cab = (f'<g transform="scale({gs:.2f})"><line x1="0" y1="0" x2="0" y2="9" stroke="{p["steel2"]}" stroke-width="2"/>'
               f'<path d="M-14 9 Q0 1 14 9 L12 12 L-12 12Z" fill="{c}"/>'
               f'<path d="M-11 12 L11 12 L12 24 Q0 32 -12 24Z" fill="{c}"/>'
               f'<rect x="-9" y="14" width="18" height="5" rx="2" fill="{p["win"] if n else "#33282a"}" opacity="{.95 if n else .55}"/>'
               f'<circle r="2.6" fill="{p["gold"]}"/></g>')
        if anim:
            g.append(f'<g transform="translate({px:.1f} {py:.1f})"><g>{cab}<animateTransform attributeName="transform" type="rotate" values="0;-90" dur="12s" repeatCount="indefinite"/></g></g>')
        else:
            g.append(f'<g transform="translate({px:.1f} {py:.1f})">{cab}</g>')
    a('<g>' + ''.join(g) + turn + '</g>')
    a(f'<circle cx="{cx}" cy="{cy}" r="{r * .07:.1f}" fill="{p["gold"]}" stroke="{p["gold2"]}" stroke-width="2"/>')
    if legs_to:  # the front A-frame, the loading deck at its feet
        a(f'<path d="M{cx} {cy} L{cx - r * .62:.0f} {legs_to} M{cx} {cy} L{cx + r * .62:.0f} {legs_to}" stroke="{wc}" stroke-width="{r * .045:.1f}" stroke-linecap="round"/>')
        yb = cy + (legs_to - cy) * .72
        a(f'<path d="M{cx - r * .45:.0f} {yb:.0f} L{cx + r * .45:.0f} {yb:.0f}" stroke="{wc}" stroke-width="{r * .025:.1f}"/>')
        a(f'<rect x="{cx - r * .75:.0f}" y="{legs_to - 6}" width="{r * 1.5:.0f}" height="12" fill="{p["red2"]}"/><rect x="{cx - r * .75:.0f}" y="{legs_to - 9}" width="{r * 1.5:.0f}" height="4" fill="{p["gold"]}"/>')
    return ''.join(o)

def bigtop(cx, peak, eave, base, half, p, n, flag_anim=False):
    """the striped big top: a king pole, a curved canopy, a scalloped valance, striped walls and a lit door"""
    o = []; a = o.append
    l, r = cx - half, cx + half
    can = f"M{cx} {peak} C{cx - half * .2:.0f} {peak + (eave - peak) * .45:.0f} {l + half * .3:.0f} {eave - 30:.0f} {l} {eave} L{r} {eave} C{r - half * .3:.0f} {eave - 30:.0f} {cx + half * .2:.0f} {peak + (eave - peak) * .45:.0f} {cx} {peak}Z"
    a(f'<defs><clipPath id="tc"><path d="{can}"/></clipPath><clipPath id="tw"><rect x="{l + 14}" y="{eave}" width="{2 * half - 28}" height="{base - eave}"/></clipPath></defs>')
    if n: a(f'<ellipse cx="{cx}" cy="{base - 20}" rx="{half * 1.3:.0f}" ry="{(base - eave) * 1.2:.0f}" fill="url(#glow)" opacity=".6"/>')
    # walls
    a(f'<rect x="{l + 14}" y="{eave}" width="{2 * half - 28}" height="{base - eave}" fill="{p["cream"]}"/>')
    a('<g clip-path="url(#tw)">' + ''.join(f'<rect x="{l + 14 + k * 46}" y="{eave}" width="23" height="{base - eave}" fill="{p["red"]}"/>' for k in range(int(half * 2 / 46) + 1)) + '</g>')
    a(f'<rect x="{l + 14}" y="{eave}" width="{2 * half - 28}" height="{base - eave}" fill="#000" opacity="{.12 if not n else .25}"/>')
    # the door, curtains tied back
    a(f'<path d="M{cx - 40} {base} L{cx - 40} {eave + 50} Q{cx} {eave + 20} {cx + 40} {eave + 50} L{cx + 40} {base}Z" fill="{p["win"] if n else "#4a2a1a"}"/>')
    if not n: a(f'<path d="M{cx - 40} {base} L{cx - 40} {eave + 50} Q{cx} {eave + 20} {cx + 40} {eave + 50} L{cx + 40} {base}Z" fill="#ffc260" opacity=".35"/>')
    a(f'<path d="M{cx - 46} {eave + 40} Q{cx - 10} {eave + 60} {cx - 26} {base} L{cx - 46} {base}Z M{cx + 46} {eave + 40} Q{cx + 10} {eave + 60} {cx + 26} {base} L{cx + 46} {base}Z" fill="{p["red2"]}"/>')
    # canopy, striped from the peak
    pts = [l + k * (2 * half) / 14 for k in range(15)]
    a(f'<path d="{can}" fill="{p["cream"]}"/>')
    a('<g clip-path="url(#tc)">' + ''.join(f'<path d="M{cx} {peak} L{pts[k]:.0f} {eave + 4} L{pts[k + 1]:.0f} {eave + 4}Z" fill="{p["red"]}"/>' for k in range(0, 14, 2)) + '</g>')
    a(f'<path d="M{cx} {peak} C{cx + half * .2:.0f} {peak + (eave - peak) * .45:.0f} {r - half * .3:.0f} {eave - 30:.0f} {r} {eave} L{cx} {eave}Z" fill="#000" opacity="{.1 if not n else .22}"/>')
    sc = ''.join(f'M{pts[k]:.0f} {eave} Q{(pts[k] + pts[k + 1]) / 2:.0f} {eave + 22} {pts[k + 1]:.0f} {eave}' for k in range(14))
    a(f'<path d="{sc}" fill="{p["gold"]}"/><rect x="{l}" y="{eave - 3}" width="{2 * half}" height="6" fill="{p["gold2"]}"/>')
    # the king pole and its flag
    a(f'<line x1="{cx}" y1="{peak}" x2="{cx}" y2="{peak - 44}" stroke="{p["wood2"]}" stroke-width="4"/><circle cx="{cx}" cy="{peak - 44}" r="4" fill="{p["gold"]}"/>')
    a(pennant(cx, peak - 42, 46, p["gold"], wave=flag_anim, dur=1.4))
    return ''.join(o)

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
VP = (805, 432)   # the far end of the midway, at the big top's door

def L(t, side=-1):
    """a point on the booth line: t 0 at the far end, 1 at the near edge; returns (x, bottom y, height)"""
    return VP[0] + side * 805 * t, VP[1] + 468 * t, 300 * t

def booth(t1, t2, p, n, sign, awn=("red", "cream"), seed=1):
    """a game booth along the left of the midway, its front facing the lane, in perspective"""
    def F(t, fr):
        x, yb, h = L(t); return (x, yb - fr * h)
    def quad(ta, tb, fa, fb, c, extra=''):
        pts = [F(ta, fa), F(tb, fa), F(tb, fb), F(ta, fb)]
        return f'<path d="M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + f'Z" fill="{c}"{extra}/>'
    o = []; a = o.append
    # side wall facing us and the roof seen from above
    dx = 70 * t2
    x2, yb2, h2 = L(t2); x1, yb1, h1 = L(t1)
    a(f'<path d="M{x2:.0f} {yb2:.0f} L{x2 - dx:.0f} {yb2 - 8 * t2:.0f} L{x2 - dx:.0f} {yb2 - h2 * .84 - 8 * t2:.0f} L{x2:.0f} {yb2 - h2 * .84:.0f}Z" fill="{p["wood2"]}"/>')
    a(f'<path d="M{x1:.0f} {yb1 - h1:.0f} L{x2:.0f} {yb2 - h2:.0f} L{x2 - dx:.0f} {yb2 - h2 - 8 * t2:.0f} L{x1 - 70 * t1:.0f} {yb1 - h1 - 8 * t1:.0f}Z" fill="{p[awn[0] + "2"] if awn[0] + "2" in p else p["red2"]}"/>')
    # front: lower panel, counter, the open front with prizes, awning, header sign
    a(quad(t1, t2, 0, .84, p["wood"]))
    a(quad(t1, t2, 0, .16, p[awn[0]]))
    if n: a(f'<ellipse cx="{(x1 + x2) / 2:.0f}" cy="{(yb1 + yb2) / 2 - h2 * .4:.0f}" rx="{(x1 - x2) * .8:.0f}" ry="{h2 * .5:.0f}" fill="url(#glow)"/>')
    m1, m2 = t1 + (t2 - t1) * .05, t2 - (t2 - t1) * .05
    a(quad(m1, m2, .2, .62, p["dark"] if not n else "#6a4020"))
    if n: a(quad(m1, m2, .2, .62, p["win"], ' opacity=".35"'))
    # the prizes: plush bears on the back shelf and hanging from the top
    r = random.Random(seed)
    cols = [p["gold"], p["teal"], p["purple"], p["red"], p["cream"]]
    k = 7
    for i in range(k):
        tt = m1 + (m2 - m1) * (i + .5) / k
        x, yb, h = L(tt); c = cols[(i + seed) % 5]
        rr = h * .042
        for fr, sz in ((.3, 1.0), (.5, .85)):
            y = yb - fr * h
            a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr * sz:.1f}" fill="{c}"/><circle cx="{x:.0f}" cy="{y - rr * 1.3 * sz:.0f}" r="{rr * .7 * sz:.1f}" fill="{c}"/>'
              f'<circle cx="{x - rr * .5 * sz:.1f}" cy="{y - rr * 1.9 * sz:.1f}" r="{rr * .28 * sz:.1f}" fill="{c}"/><circle cx="{x + rr * .5 * sz:.1f}" cy="{y - rr * 1.9 * sz:.1f}" r="{rr * .28 * sz:.1f}" fill="{c}"/>')
            c = cols[(i + seed + 2) % 5]
    a(quad(t1, t2, .16, .21, p["gold2"]))
    # awning stripes with a scalloped edge
    ns = 8
    for i in range(ns):
        ta = t1 + (t2 - t1) * i / ns; tb = t1 + (t2 - t1) * (i + 1) / ns
        a(quad(ta, tb, .66, .84, p[awn[i % 2]]))
        (xa, ya), (xb, yb_) = F(ta, .66), F(tb, .66)
        a(f'<path d="M{xa:.0f} {ya:.0f} Q{(xa + xb) / 2:.0f} {(ya + yb_) / 2 + 9 * tb:.0f} {xb:.0f} {yb_:.0f}Z" fill="{p[awn[i % 2]]}"/>')
    a(quad(t1, t2, .84, 1.0, p["navy"] if not n else "#1c2550"))
    # the header sign's words, laid along the front
    (nx, ny), (fx, fy) = F(t2, .92), F(t1, .92)
    Lx = math.hypot(fx - nx, fy - ny); ux, uy = (fx - nx) / Lx, (fy - ny) / Lx
    fs = h2 * .1
    a(f'<text transform="matrix({ux:.3f} {uy:.3f} 0 1 {nx:.1f} {ny:.1f})" x="{Lx * .05:.0f}" y="{fs * .36:.1f}" textLength="{Lx * .9:.0f}" lengthAdjust="spacingAndGlyphs" '
      f'font-family="Georgia, serif" font-weight="bold" font-size="{fs:.1f}" fill="{p["gold"] if not n else "#ffd86a"}">{sign}</text>')
    # bulbs along the header's top edge
    (ax, ay), (bx, by) = F(t2, 1.0), F(t1, 1.0)
    a(bulbs(f"M{ax:.0f} {ay:.0f} L{bx:.0f} {by:.0f}", round(14 * (t1 + t2) / 2 + 6, 1), n, 4 * t2 + 1, wire=None))
    return ''.join(o)

def coaster_track():
    segs = [((-80, 380), None, (150, 118)), ((150, 118), (215, 40), (280, 118)), ((280, 118), None, (370, 360)),
            ((370, 360), (395, 420), (440, 382)), ((440, 382), (500, 300), (600, 330))]
    pts = []
    for p0, c, p1 in segs:
        n = 28
        for i in range(n + (1 if p1 == segs[-1][2] else 0)):
            t = i / n
            if c is None: pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))
            else: pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]))
    d = "M-80 380 L150 118 Q215 40 280 118 L370 360 Q395 420 440 382 Q500 300 600 330"
    return pts, d

def track_y(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / max(1e-6, x1 - x0)
    return None

def coaster(p, n, ground, anim=True):
    o = []; a = o.append
    pts, d = coaster_track()
    st = p["steel"]
    # the lattice: posts every 30 units, ties and braces between them
    xs = list(range(-60, 600, 30)); posts = []; ties = []
    for x in xs:
        y = track_y(pts, x)
        if y is None: continue
        posts.append(f'M{x} {y + 4:.0f} V{ground}');
    a(f'<path d="{"".join(posts)}" stroke="{st}" stroke-width="3"/>')
    for x0, x1 in zip(xs, xs[1:]):
        y0, y1 = track_y(pts, x0), track_y(pts, x1)
        if y0 is None or y1 is None: continue
        top = max(y0, y1) + 10
        lv = [y for y in range(140, ground, 50) if y > top]
        for i, y in enumerate(lv):
            ties.append(f'M{x0} {y} H{x1}')
            if i + 1 < len(lv): ties.append(f'M{x0} {y} L{x1} {lv[i + 1]}' if i % 2 == 0 else f'M{x1} {y} L{x0} {lv[i + 1]}')
    a(f'<path d="{"".join(ties)}" stroke="{st}" stroke-width="1.6" opacity=".85" fill="none"/>')
    # the rails
    a(f'<path d="{d}" fill="none" stroke="{p["red2"]}" stroke-width="12" stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{p["red"]}" stroke-width="5" stroke-linejoin="round" transform="translate(0 -3)"/>')
    if n: a(bulbs(d, 16, n, 3, wire=None))
    # the train cresting the lift hill: it climbs slowly, tips over the top and is gone down the drop
    apex = (215, 79)
    seg = [(x, y) for x, y in pts if 70 <= x <= 330]
    rel = ' '.join(f'{"M" if i == 0 else "L"}{x - apex[0]:.1f} {y - apex[1]:.1f}' for i, (x, y) in enumerate(seg))
    lens = [0]
    for (x0, y0), (x1, y1) in zip(seg, seg[1:]): lens.append(lens[-1] + math.hypot(x1 - x0, y1 - y0))
    i_apex = min(range(len(seg)), key=lambda i: abs(seg[i][0] - apex[0]))
    fa = lens[i_apex] / lens[-1]
    car = []
    for k, dxc in enumerate((-22, 22)):
        c = p["gold"] if k else p["teal"]
        car.append(f'<g transform="translate({dxc} 0)"><circle cx="-8" cy="-21" r="4.5" fill="{p["skin"]}"/><circle cx="7" cy="-21" r="4.5" fill="{p["skin2"]}"/>'
                   f'<path d="M-8 -24 L-12 -36 M7 -24 L11 -36" stroke="{p["skin"]}" stroke-width="2.4" stroke-linecap="round"/>'
                   f'<path d="M-19 -2 L-21 -16 L19 -16 L19 -2Z" fill="{c}"/><rect x="-19" y="-7" width="38" height="3" fill="#fff" opacity=".6"/></g>')
    mv = (f'<animateMotion path="{rel}" rotate="auto" keyPoints="0;{fa:.3f};1;1" keyTimes="0;.62;.78;1" calcMode="linear" dur="9s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.76;.78;.97;1" dur="9s" repeatCount="indefinite"/>') if anim else ''
    a(f'<g transform="translate({apex[0]} {apex[1] - 4})"><g>{"".join(car)}{mv}</g></g>')
    return ''.join(o)

def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    HZ = VP[1]
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(defs(skyg(n, id="sky") +
           f'<radialGradient id="stg" cx=".5" cy=".4" r=".6"><stop offset="0" stop-color="{"#e9c48a" if not n else "#7a5434"}"/><stop offset="1" stop-color="{"#b98a56" if not n else "#4a3220"}"/></radialGradient>'
           '<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd89a" stop-opacity=".45"/><stop offset="1" stop-color="#ffd89a" stop-opacity="0"/></radialGradient>'
           '<clipPath id="skc"><path d="M460 700 A345 92 0 0 0 1150 700 L1150 748 A345 92 0 0 1 460 748Z"/></clipPath>'))
    a(f'<rect width="{W}" height="{HZ + 30}" fill="url(#sky)"/>')
    if n:
        a(stars(40, 0, W, 0, 300, 3)); a(moon(985, 62, 26))
    else:
        a('<ellipse cx="700" cy="420" rx="700" ry="300" fill="url(#sun)"/>')
        a(cloud(560, 60, 200) + cloud(1480, 120, 170, .45) + cloud(80, 40, 150, .4))
        a(bird(940, 70, 1.1, "#3a3048") + bird(966, 58, .8, "#3a3048"))
    # the back lot: a treeline at the horizon, the grass
    r = random.Random(4)
    tl = ''.join(f'<circle cx="{x}" cy="{HZ - r.randint(4, 18)}" r="{r.randint(18, 30)}"/>' for x in range(-10, 1620, 34))
    a(f'<g fill="{p["tree"]}">{tl}</g>')
    a(f'<rect x="0" y="{HZ - 6}" width="{W}" height="{H - HZ + 6}" fill="{p["grass"]}"/>')
    # the coaster, left; the wheel, right; the big top at the end of the midway
    a(coaster(p, n, 440))
    a(ferris(1290, 238, 186, p, n, anim=True, legs_to=470))
    a(bigtop(805, 92, 296, HZ, 245, p, n, flag_anim=True))
    # two light masts beside the tent, strings of bulbs from the king pole out to them (the top crop's chase)
    for x in (488, 1080):
        a(pole(x, 120, 448, p["wood2"], 7, p["gold"]))
    a(bulbs(sag(805, 100, 488, 124, 26), 15, n, 5, chase=2.4))
    a(bulbs(sag(805, 100, 1080, 124, 26), 15, n, 5, chase=2.4))
    # balloons let go on the midway, drifting up past the tiles
    for i, (x, y, c, dur, beg) in enumerate([(1010, 128, p["red"], 11, -2), (1046, 104, p["gold"], 12, -7), (455, 118, p["teal"], 10, -4.5)]):
        a(f'<g>{balloon(x, y, 13, c, (x + 4, y + 46))}<animateTransform attributeName="transform" type="translate" values="0 110;-10 -20;8 -200" '
          f'dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;1;0" keyTimes="0;.8;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></g>')
    # the midway: sawdust running from the tent door toward us, to the bandstand
    a(f'<path d="M770 {HZ} L840 {HZ} L1260 900 L350 900Z" fill="{p["dirt"]}"/>')
    a(f'<path d="M790 {HZ} L820 {HZ} L960 900 L650 900Z" fill="{p["dirt2"]}" opacity=".35"/>')
    if n: a(f'<ellipse cx="805" cy="520" rx="260" ry="90" fill="url(#glow)" opacity=".7"/>')
    # far fairgoers at the tent door
    for x, y, s, c in [(770, 452, .34, p["teal"]), (790, 448, .3, p["gold"]), (842, 456, .36, p["purple"]), (858, 452, .32, p["red"])]:
        a(person(x, y, s, c, p["navy"], p["skin"], p["hair"], "walk", flip=x > 805))
    # the back string across the lane
    for x in (640, 970): a(pole(x, 392, 456, p["wood2"], 4, p["gold"]))
    a(bulbs(sag(640, 394, 970, 394, 16), 12, n, 3.5, chase=2.4))
    # the booths, left
    a(booth(.42, .58, p, n, "EVERYBODY WINS A QUOTE", ("teal", "cream"), seed=1))
    a(booth(.66, .94, p, n, "STEP RIGHT UP TO SAVINGS", ("red", "cream"), seed=3))
    # the carousel, right
    a(carousel(1352, 690, 1.0, p, n, anim=True))
    # the front string, pole to pole across the midway, sagging over the bandstand
    a(pole(470, 418, 650, p["wood2"], 7, p["gold"]) + pole(1150, 424, 656, p["wood2"], 7, p["gold"]))
    a(f'<ellipse cx="470" cy="650" rx="14" ry="4" fill="#000" opacity=".25"/><ellipse cx="1150" cy="656" rx="14" ry="4" fill="#000" opacity=".25"/>')
    a(bulbs(sag(470, 420, 1150, 426, 32), 17, n, 6, chase=2.4))
    # the bandstand: a round stage in the middle of the midway, striped skirt and bunting
    a(f'<ellipse cx="805" cy="752" rx="352" ry="96" fill="#000" opacity=".18"/>')
    a(f'<path d="M460 700 A345 92 0 0 0 1150 700 L1150 748 A345 92 0 0 1 460 748Z" fill="{p["cream"]}"/>')
    a('<g clip-path="url(#skc)">' + ''.join(f'<rect x="{x}" y="690" width="22" height="70" fill="{p["red"]}"/>' for x in range(460, 1150, 44)) + '</g>')
    a(f'<ellipse cx="805" cy="700" rx="345" ry="92" fill="url(#stg)"/>')
    a(f'<ellipse cx="805" cy="700" rx="300" ry="74" fill="none" stroke="{p["gold2"]}" stroke-width="3" opacity=".6"/>')
    bun = []
    for k in range(24):
        t0 = math.pi * k / 24; t1 = math.pi * (k + 1) / 24
        x0, y0 = 805 + 345 * math.cos(t0), 700 + 92 * math.sin(t0); x1, y1 = 805 + 345 * math.cos(t1), 700 + 92 * math.sin(t1)
        bun.append(f'M{x0:.0f} {y0:.0f} L{(x0 + x1) / 2:.0f} {(y0 + y1) / 2 + 16:.0f} L{x1:.0f} {y1:.0f}Z')
    a(f'<path d="{"".join(bun[0::2])}" fill="{p["gold"]}"/><path d="{"".join(bun[1::2])}" fill="{p["teal"]}"/>')
    a(bulbs("M460 702 A345 92 0 0 0 1150 702", 21, n, 4, wire=None))
    # the steps up to the stage from the lane
    a(f'<path d="M760 790 L850 790 L858 806 L752 806Z M752 806 L858 806 L866 822 L744 822Z" fill="{p["wood"]}"/><path d="M752 806 L858 806 M744 822 L866 822" stroke="{p["wood2"]}" stroke-width="2"/>')
    # fairgoers: a ring toss at the near booth, a family with a balloon, a couple by the carousel
    a(person(330, 806, 1.5, p["teal"], p["navy"], p["skin"], p["hair"], "toss", flip=True))
    a(f'<ellipse cx="236" cy="694" rx="9" ry="4" fill="none" stroke="{p["gold"]}" stroke-width="3" transform="rotate(-20 236 694)"/>')
    a(person(420, 742, 1.15, p["red"], "#2b3348", p["skin2"], "#1c120c", "walk", long_hair=True))
    a(balloon(452, 600, 15, p["gold"], (447, 676)))
    a(person(446, 748, .78, p["gold"], "#2b3348", p["skin"], p["hair"], "up", extra=''))
    a(person(1200, 806, 1.25, p["purple"], "#2b3348", p["skin"], p["hair"], "stand", flip=True))
    a(person(1236, 808, 1.2, p["gold"], p["navy"], p["skin2"], "#1c120c", "point", flip=True, long_hair=True))
    # a few scuffs of sawdust and grass tufts, kept off the stage
    r = random.Random(9)
    for _ in range(26):
        x = r.randint(0, W); y = r.randint(470, 860)
        if 300 < x < 1300: continue
        a(f'<path d="M{x - 6} {y} l3 -8 l3 6 l3 -9 l3 11" stroke="{p["grass2"]}" stroke-width="2" fill="none"/>')
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(V, body + SHADE)

def base(n, sky=DAYSKY, nt=NIGHTSKY, star=45, extra=''):
    return defs(skyg(n, day=sky, nt=nt) + extra) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 150, 7) if n else '')

def ground(p, y, c=None):
    return f'<path d="M0 {y} Q400 {y - 8} 800 {y} T1600 {y - 4} L1600 240 L0 240Z" fill="{c or p["grass"]}"/>'

def corners(p, n):
    c = "#2a1d14" if not n else "#0c0907"
    return (f'<path d="M0 176 Q220 168 470 190 L470 240 L0 240Z" fill="{c}" opacity=".85"/>'
            f'<path d="M1600 180 Q1320 174 1040 198 L1040 240 L1600 240Z" fill="{c}" opacity=".85"/>')

def far_fair(p, n, wheel_x=1320, tent_x=260):
    """the fair in silhouette behind a banner: a small wheel and a tent peak, under the corner shadows"""
    c = "#5a4a66" if not n else "#151a30"
    o = [f'<circle cx="{wheel_x}" cy="110" r="64" fill="none" stroke="{c}" stroke-width="4"/>',
         f'<path d="' + ''.join(f'M{wheel_x} 110 L{wheel_x + 64 * math.cos(k * math.pi / 6):.0f} {110 + 64 * math.sin(k * math.pi / 6):.0f}' for k in range(12)) + f'" stroke="{c}" stroke-width="1.6"/>',
         f'<path d="M{wheel_x} 110 L{wheel_x - 40} 190 M{wheel_x} 110 L{wheel_x + 40} 190" stroke="{c}" stroke-width="4"/>',
         f'<path d="M{tent_x} 96 C{tent_x - 20} 130 {tent_x - 90} 150 {tent_x - 120} 160 L{tent_x - 110} 200 L{tent_x + 110} 200 L{tent_x + 120} 160 C{tent_x + 90} 150 {tent_x + 20} 130 {tent_x} 96Z" fill="{c}"/>',
         f'<line x1="{tent_x}" y1="96" x2="{tent_x}" y2="74" stroke="{c}" stroke-width="3"/>']
    if n:
        rim = f"M{wheel_x + 64} 110 A64 64 0 1 1 {wheel_x - 64} 110 A64 64 0 1 1 {wheel_x + 64} 110"
        o.append(bulbs(rim, 16.75, n, 3, wire=None, glow=False))
    return ''.join(o)

def sign(x, y, w, h, text, p, fs=16, bg=None, fg=None, bulb=True, n=False):
    o = [f'<rect x="{x - w / 2:.0f}" y="{y}" width="{w}" height="{h}" rx="6" fill="{bg or p["red2"]}" stroke="{p["gold"]}" stroke-width="3"/>',
         f'<text x="{x}" y="{y + h / 2 + fs * .36:.0f}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{fg or p["ink"]}" letter-spacing="1.5">{text}</text>']
    if bulb:
        d = f"M{x - w / 2 + 6:.0f} {y + 4} H{x + w / 2 - 6:.0f} M{x - w / 2 + 6:.0f} {y + h - 4} H{x + w / 2 - 6:.0f}"
        o.append(bulbs(d, 14, n, 3.4, wire=None, glow=n))
    return ''.join(o)

def awning(x0, x1, y, h, c1, c2, k=10):
    w = (x1 - x0) / k; o = []
    for i in range(k):
        c = c1 if i % 2 == 0 else c2
        o.append(f'<path d="M{x0 + i * w:.0f} {y} H{x0 + (i + 1) * w:.0f} V{y + h} Q{x0 + (i + .5) * w:.0f} {y + h + 14} {x0 + i * w:.0f} {y + h}Z" fill="{c}"/>')
    return ''.join(o)

def bear(x, y, s, c):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cy="0" r="9" fill="{c}"/><circle cy="-13" r="7" fill="{c}"/><circle cx="-5" cy="-19" r="3" fill="{c}"/>'
            f'<circle cx="5" cy="-19" r="3" fill="{c}"/><circle cy="-11" r="2.6" fill="#fff" opacity=".6"/><circle cx="-2.6" cy="-15" r="1" fill="#222"/><circle cx="2.6" cy="-15" r="1" fill="#222"/></g>')

def v_sales(n):  # the ring toss: bottles, prizes, a ring in the air
    p = P(n); o = [base(n)]
    o.append(far_fair(p, n))
    o.append(ground(p, 196, p["dirt2"]))
    x0, x1 = 600, 1000
    if n: o.append(f'<ellipse cx="800" cy="140" rx="300" ry="110" fill="url(#glow)"/>')
    o.append(f'<rect x="{x0}" y="70" width="{x1 - x0}" height="130" fill="{p["dark"] if not n else "#5a3a1e"}"/>')
    if n: o.append(f'<rect x="{x0}" y="70" width="{x1 - x0}" height="130" fill="{p["win"]}" opacity=".3"/>')
    # prizes hanging along the back
    for i, x in enumerate(range(630, 990, 46)):
        o.append(bear(x, 104, 1.1, [p["gold"], p["teal"], p["purple"], p["cream"], p["red"]][i % 5]))
    # the bottle tiers
    for row, (y, k) in enumerate([(176, 9), (154, 7), (134, 5)]):
        w = k * 30; sx = 800 - w / 2
        o.append(f'<rect x="{sx - 10:.0f}" y="{y}" width="{w + 20:.0f}" height="6" fill="{p["wood"]}"/>')
        for i in range(k):
            bx = sx + 15 + i * 30
            c = [p["teal"], p["gold"], p["cream2"]][(i + row) % 3]
            o.append(f'<path d="M{bx - 7:.0f} {y} V{y - 14} Q{bx - 7:.0f} {y - 18} {bx - 3:.0f} {y - 20} V{y - 26} H{bx + 3:.0f} V{y - 20} Q{bx + 7:.0f} {y - 18} {bx + 7:.0f} {y - 14} V{y}Z" fill="{c}" opacity=".95"/>')
    o.append(f'<ellipse cx="830" cy="146" rx="10" ry="3.5" fill="none" stroke="{p["red"]}" stroke-width="3"/>')
    # posts, counter, awning, sign
    o.append(f'<rect x="{x0 - 22}" y="56" width="22" height="160" fill="{p["red"]}"/><rect x="{x1}" y="56" width="22" height="160" fill="{p["red"]}"/>')
    o.append(f'<rect x="{x0 - 30}" y="186" width="{x1 - x0 + 60}" height="12" fill="{p["gold"]}"/><rect x="{x0 - 22}" y="198" width="{x1 - x0 + 44}" height="20" fill="{p["red2"]}"/>')
    o.append(awning(x0 - 30, x1 + 30, 46, 22, p["red"], p["cream"], 12))
    o.append(bulbs(f"M{x0 - 26} 47 H{x1 + 26}", 16, n, 4.5, wire=None, chase=2.4))
    o.append(sign(800, 156 - 100, 0, 0, '', p, bulb=False) if False else '')
    o.append(f'<rect x="640" y="200" width="250" height="16" fill="{p["navy"]}"/><text x="765" y="213" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="11" fill="{p["gold"]}" letter-spacing="1.5">STEP RIGHT UP TO SAVINGS</text>')
    # the player and the ring on its way
    o.append(person(520, 222, 1.55, p["teal"], p["navy"], p["skin"], p["hair"], "toss"))
    o.append(f'<path d="M574 116 Q660 70 760 112" stroke="#fff" stroke-width="2" stroke-dasharray="3 7" fill="none" opacity=".6"/>')
    o.append(f'<g><ellipse cx="760" cy="112" rx="11" ry="4" fill="none" stroke="{p["gold"]}" stroke-width="3.5" transform="rotate(-18 760 112)"/>'
             '<animateMotion path="M-186 4 Q-100 -42 0 0 L70 34" keyPoints="0;0;.82;1;1" keyTimes="0;.15;.62;.75;1" calcMode="spline" '
             f'keySplines="{SP(4)}" dur="3.6s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.15;.72;.8;1" dur="3.6s" repeatCount="indefinite"/></g>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_messages(n):  # the ticket booth: a ticket ribbon coming out of the window
    p = P(n); o = [base(n)]
    o.append(far_fair(p, n, 1340, 240))
    o.append(ground(p, 198, p["dirt2"]))
    bx = 800
    if n: o.append(f'<ellipse cx="{bx}" cy="140" rx="220" ry="110" fill="url(#glow)"/>')
    # the booth: a little striped kiosk with a peaked roof
    o.append(f'<rect x="{bx - 90}" y="96" width="180" height="116" fill="{p["red"]}"/>')
    for k in range(5): o.append(f'<rect x="{bx - 90 + k * 40}" y="150" width="20" height="62" fill="{p["cream"]}"/>')
    o.append(f'<path d="M{bx - 112} 98 L{bx} 46 L{bx + 112} 98Z" fill="{p["navy"] if not n else "#2a356a"}"/><path d="M{bx} 46 L{bx + 112} 98 L{bx + 40} 98Z" fill="#000" opacity=".2"/>')
    o.append(bulbs(f"M{bx - 108} 97 L{bx} 49 L{bx + 108} 97", 14, n, 4, wire=None, chase=2.1))
    o.append(f'<circle cx="{bx}" cy="46" r="6" fill="{p["gold"]}"/>')
    o.append(f'<rect x="{bx - 70}" y="104" width="140" height="18" rx="3" fill="{p["navy"]}"/><text x="{bx}" y="118" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["gold"]}" letter-spacing="3">TICKETS</text>')
    o.append(f'<path d="M{bx - 54} 176 V136 Q{bx} 122 {bx + 54} 136 V176Z" fill="{p["win"] if n else "#f5e2b0"}" stroke="{p["gold"]}" stroke-width="4"/>')
    o.append(person(bx, 184, .8, p["teal"], p["navy"], p["skin"], p["hair"], "hold"))
    o.append(f'<rect x="{bx - 62}" y="174" width="124" height="8" fill="{p["gold2"]}"/>')
    # the ticket ribbon unrolling out of the window and down to the ground
    rib = f"M{bx + 40} 178 C{bx + 120} 176 {bx + 150} 140 {bx + 210} 150 S{bx + 260} 206 {bx + 330} 196"
    o.append(f'<path d="{rib}" fill="none" stroke="{p["gold2"]}" stroke-width="20"/><path d="{rib}" fill="none" stroke="{p["gold"]}" stroke-width="16"/>'
             f'<path d="{rib}" fill="none" stroke="{p["gold2"]}" stroke-width="16" stroke-dasharray="2 30">'
             '<animate attributeName="stroke-dashoffset" values="0;-32" dur="1.6s" repeatCount="indefinite"/></path>')
    o.append(f'<text font-family="Georgia, serif" font-weight="bold" font-size="9" fill="{p["red2"]}" letter-spacing="1"><textPath href="#rb" startOffset="8%">ADMIT ONE  &#183;  ADMIT ONE  &#183;  ADMIT ONE</textPath></text>')
    o.insert(1, f'<defs><path id="rb" d="M{bx + 40} 181 C{bx + 120} 179 {bx + 150} 143 {bx + 210} 153 S{bx + 260} 209 {bx + 330} 199"/></defs>')
    # the line: rope stanchions on the left
    for x in (560, 640): o.append(f'<rect x="{x - 3}" y="166" width="6" height="40" fill="{p["gold"]}"/><circle cx="{x}" cy="164" r="6" fill="{p["gold"]}"/><ellipse cx="{x}" cy="206" rx="12" ry="4" fill="{p["gold2"]}"/>')
    o.append(f'<path d="M560 172 Q600 192 640 172" stroke="{p["red"]}" stroke-width="5" fill="none"/>')
    o.append(person(600, 214, 1.1, p["purple"], "#2b3348", p["skin2"], "#1c120c", "stand", long_hair=True))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_coaching(n):  # the fortune-teller's tent: a crystal ball at the door
    p = P(n); o = [base(n, sky=("#33407e", "#8a6a9a", "#e8b47a"), nt=("#04061a", "#120f34", "#2a1b4a"))]
    o.append(far_fair(p, n, 1340, 220))
    o.append(ground(p, 200, p["dirt2"]))
    cx = 800
    pu, pu2 = (p["purple"], p["purple2"])
    tent = f"M{cx} 44 C{cx - 30} 90 {cx - 150} 140 {cx - 190} 150 L{cx - 180} 212 L{cx + 180} 212 L{cx + 190} 150 C{cx + 150} 140 {cx + 30} 90 {cx} 44Z"
    o.append(f'<defs><clipPath id="ft"><path d="{tent}"/></clipPath></defs>')
    if n: o.append(f'<ellipse cx="{cx}" cy="180" rx="260" ry="80" fill="url(#glow)"/>')
    o.append(f'<path d="{tent}" fill="{pu}"/>')
    o.append('<g clip-path="url(#ft)">' + ''.join(f'<path d="M{cx} 44 L{cx - 200 + k * 50} 214 L{cx - 175 + k * 50} 214Z" fill="{p["gold"]}" opacity=".9"/>' for k in range(9)) + '</g>')
    o.append(f'<path d="M{cx - 190} 150 L{cx + 190} 150" stroke="{p["gold2"]}" stroke-width="4"/>')
    o.append(awning(cx - 190, cx + 190, 148, 10, p["gold"], pu2, 12))
    # stars and a crescent on the canvas
    for i, (x, y, s) in enumerate([(cx - 120, 178, 7), (cx + 128, 176, 7), (cx - 40, 110, 5), (cx + 50, 120, 5)]):
        o.append(f'<path d="M{x} {y - s} L{x + s * .3:.1f} {y - s * .3:.1f} L{x + s} {y} L{x + s * .3:.1f} {y + s * .3:.1f} L{x} {y + s} L{x - s * .3:.1f} {y + s * .3:.1f} L{x - s} {y} L{x - s * .3:.1f} {y - s * .3:.1f}Z" fill="{p["cream"]}">'
                 f'<animate attributeName="opacity" values="1;.35;1" dur="2.6s" begin="{-i * .65:.2f}s" repeatCount="indefinite"/></path>')
    o.append(f'<path d="M{cx + 10} 70 a12 12 0 1 0 12 16 a9 9 0 1 1 -12 -16Z" fill="{p["cream"]}"/>')
    # the open door: the fortune teller, her table, the glowing ball
    o.append(f'<path d="M{cx - 60} 212 L{cx - 60} 170 Q{cx} 140 {cx + 60} 170 L{cx + 60} 212Z" fill="{"#2a1838" if not n else "#3a2050"}"/>')
    o.append(f'<path d="M{cx - 70} 160 Q{cx - 40} 180 {cx - 50} 212 L{cx - 72} 212Z M{cx + 70} 160 Q{cx + 40} 180 {cx + 50} 212 L{cx + 72} 212Z" fill="{p["red2"]}"/>')
    o.append(person(cx, 214, 1.0, p["teal"], p["teal2"], p["skin2"], p["red"], "hold", long_hair=True,
                    extra=f'<circle cx="-7" cy="-60" r="1.6" fill="{p["gold"]}"/><circle cx="7" cy="-60" r="1.6" fill="{p["gold"]}"/>'))
    o.append(f'<rect x="{cx - 46}" y="190" width="92" height="8" fill="{p["red"]}"/><path d="M{cx - 40} 198 L{cx - 46} 216 L{cx + 46} 216 L{cx + 40} 198Z" fill="{p["red2"]}"/>')
    op = .25 if not n else .35
    o.append(f'<circle cx="{cx}" cy="176" r="30" fill="#7fe0e8" opacity="{op}"><animate attributeName="r" values="28;33;28" dur="4s" calcMode="spline" keySplines="{SP(2)}" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="{op};{op + .22:.2f};{op}" dur="4s" calcMode="spline" keySplines="{SP(2)}" repeatCount="indefinite"/></circle>'
             f'<circle cx="{cx}" cy="176" r="15" fill="#bff2f4"><animate attributeName="fill" values="#bff2f4;#ffffff;#e2c8ff;#bff2f4" keyTimes="0;.35;.7;1" dur="4s" repeatCount="indefinite"/></circle><circle cx="{cx - 5}" cy="171" r="4" fill="#fff" opacity=".85"/>'
             f'<path d="M{cx - 12} 190 L{cx + 12} 190 L{cx + 8} 184 L{cx - 8} 184Z" fill="{p["gold"]}"/>')
    # the easel sign
    o.append(f'<path d="M540 214 L560 120 M600 214 L580 120" stroke="{p["wood2"]}" stroke-width="5"/>')
    o.append(f'<rect x="500" y="110" width="140" height="62" rx="6" fill="{p["navy"]}" stroke="{p["gold"]}" stroke-width="3"/>'
             f'<text x="570" y="134" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="{p["gold"]}" letter-spacing="1">YOUR FUTURE,</text>'
             f'<text x="570" y="154" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="{p["gold"]}" letter-spacing="1">FULLY COVERED</text>')
    o.append(f'<line x1="{cx}" y1="44" x2="{cx}" y2="22" stroke="{p["gold"]}" stroke-width="3"/>' + pennant(cx, 22, 24, p["red"], True, 1.8))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def striker(x, base, h, p, n, puck=.45, ring=False, anim=False):
    """the high striker: a lever pad, a graduated column, the puck and the bell at the top"""
    o = []; a = o.append
    top = base - h
    a(f'<rect x="{x - 40}" y="{base - 10}" width="80" height="14" fill="{p["wood2"]}"/><rect x="{x - 20}" y="{base - 18}" width="40" height="8" rx="3" fill="{p["red"]}"/>')
    a(f'<rect x="{x - 12}" y="{top + 18}" width="24" height="{h - 28}" fill="{p["cream"]}"/>')
    segs = [p["teal"], p["gold"], p["red"]]
    seg = (h - 28) / 9
    for k in range(9):
        a(f'<rect x="{x - 9}" y="{base - 10 - (k + 1) * seg:.0f}" width="18" height="{seg - 3:.0f}" fill="{segs[k // 3]}"/>')
    a(f'<line x1="{x}" y1="{top + 18}" x2="{x}" y2="{base - 10}" stroke="{p["dark"]}" stroke-width="1.5" opacity=".4"/>')
    py = base - 18 - (h - 34) * puck
    T = 'dur="4s" repeatCount="indefinite"'
    pa = (f'<animate attributeName="y" values="{py - 6:.0f};{py - 6:.0f};{base - 24};{top + 20};{top + 20};{py - 6:.0f}" keyTimes="0;.2;.3;.44;.52;1" '
          f'calcMode="spline" keySplines="{SP(5)}" {T}/>') if anim else ''
    a(f'<rect x="{x - 15}" y="{py - 6:.0f}" width="30" height="12" rx="4" fill="{p["navy"] if not n else "#d8d8e8"}">{pa}</rect>')
    a(f'<path d="M{x - 16} {top + 18} Q{x - 16} {top} {x} {top} Q{x + 16} {top} {x + 16} {top + 18}Z" fill="{p["gold"]}"/><circle cx="{x}" cy="{top + 19}" r="3" fill="{p["gold2"]}"/>')
    if ring:
        a(f'<path d="M{x - 26} {top + 2} Q{x - 34} {top + 10} {x - 28} {top + 22} M{x + 26} {top + 2} Q{x + 34} {top + 10} {x + 28} {top + 22} M{x - 38} {top - 6} Q{x - 50} {top + 10} {x - 40} {top + 28} M{x + 38} {top - 6} Q{x + 50} {top + 10} {x + 40} {top + 28}" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9"/>')
        if n: a(f'<circle cx="{x}" cy="{top + 10}" r="40" fill="url(#glow)"/>')
    if anim:   # the bell's ring lines and flash, only for the moment the puck hits
        a(f'<g opacity="0"><path d="M{x - 26} {top + 2} Q{x - 34} {top + 10} {x - 28} {top + 22} M{x + 26} {top + 2} Q{x + 34} {top + 10} {x + 28} {top + 22} M{x - 38} {top - 6} Q{x - 50} {top + 10} {x - 40} {top + 28} M{x + 38} {top - 6} Q{x + 50} {top + 10} {x + 40} {top + 28}" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>'
          f'<circle cx="{x}" cy="{top + 10}" r="22" fill="#fff6b0" opacity=".45"/>'
          f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.43;.45;.6;.7;1" {T}/></g>')
    return ''.join(o)

def mallet(hx, hy, ang, p, L_=58):
    return (f'<g transform="rotate({ang} {hx} {hy})"><line x1="{hx}" y1="{hy}" x2="{hx}" y2="{hy - L_}" stroke="{p["wood"]}" stroke-width="4" stroke-linecap="round"/>'
            f'<rect x="{hx - 15}" y="{hy - L_ - 10}" width="30" height="16" rx="4" fill="{p["red"]}"/><rect x="{hx - 15}" y="{hy - L_ - 4}" width="30" height="4" fill="{p["gold"]}"/></g>')

def v_roleplay(n):  # the high striker: hammer up, test your pitch
    p = P(n); o = [base(n)]
    o.append(far_fair(p, n, 1330, 250))
    o.append(ground(p, 200, p["dirt2"]))
    if n: o.append('<ellipse cx="800" cy="130" rx="200" ry="110" fill="url(#glow)" opacity=".7"/>')
    o.append(f'<rect x="666" y="62" width="268" height="22" rx="5" fill="{p["navy"]}" stroke="{p["gold"]}" stroke-width="3"/>'
             f'<text x="782" y="78" text-anchor="end" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["gold"]}" letter-spacing="2">TEST YOUR</text>'
             f'<text x="818" y="78" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["gold"]}" letter-spacing="2">PITCH</text>')
    o.append(striker(800, 212, 170, p, n, .38, anim=True))
    # the swinger, mallet up over his head, and a friend cheering
    o.append(person(880, 214, 1.5, p["red"], p["navy"], p["skin"], p["hair"], "hammer", flip=True))
    o.append(f'<g>{mallet(884, 100, 26, p, 50)}<animateTransform attributeName="transform" type="rotate" values="0 884 100;10 884 100;-62 884 100;-62 884 100;0 884 100" '
             f'keyTimes="0;.12;.2;.3;1" calcMode="spline" keySplines="{SP(4)}" dur="4s" repeatCount="indefinite"/></g>')
    o.append(person(660, 214, 1.3, p["gold"], "#2b3348", p["skin2"], "#1c120c", "cheer", long_hair=True))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_rphistory(n):  # the funhouse mirrors: every session played back, stretched and squashed
    p = P(n)
    wall = "#4f2d7a" if not n else "#20123a"; wall2 = "#43256a" if not n else "#180d2c"
    o = [defs(), f'<rect width="1600" height="{V}" fill="{wall}"/>']
    for x in range(0, 1600, 70): o.append(f'<rect x="{x}" y="0" width="35" height="{V}" fill="{wall2}"/>')
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{"#2a1838" if not n else "#0e0818"}"/>')
    for x in range(0, 1600, 40): o.append(f'<rect x="{x}" y="{196 + (x // 40 % 2) * 22}" width="20" height="22" fill="{p["gold"]}" opacity=".35"/>')
    o.append(f'<path d="M560 34 Q800 14 1040 34 L1040 56 Q800 36 560 56Z" fill="{p["red"]}" stroke="{p["gold"]}" stroke-width="3"/>'
             f'<text x="800" y="50" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{p["ink"]}" letter-spacing="3">FULL COVERAGE FUNHOUSE</text>')
    glass = "#bcd8e4" if not n else "#6a86a4"
    sk = p["skin"]
    for i, (mx, sx, sy, wav) in enumerate([(610, .6, 1.5, 0), (800, 1.6, .75, 0), (990, 1.0, 1.0, 1)]):
        o.append('<g transform="translate(0 12)">')
        frame = f'M{mx - 70} 192 L{mx - 70} 90 Q{mx - 70} 66 {mx - 40} 70 Q{mx} 52 {mx + 40} 70 Q{mx + 70} 66 {mx + 70} 90 L{mx + 70} 192Z'
        o.append(f'<path d="{frame}" fill="{p["gold"]}"/>')
        o.append(f'<path d="M{mx - 60} 188 L{mx - 60} 92 Q{mx - 60} 76 {mx - 36} 80 Q{mx} 64 {mx + 36} 80 Q{mx + 60} 76 {mx + 60} 92 L{mx + 60} 188Z" fill="{glass}"/>')
        o.append(f'<path d="M{mx - 40} 100 L{mx - 20} 90 L{mx - 44} 150Z" fill="#fff" opacity=".35"><animate attributeName="opacity" values=".35;.1;.35" dur="5s" begin="{-i * 1.6:.1f}s" repeatCount="indefinite"/></path>')
        wob = (f'<animateTransform attributeName="transform" type="scale" values="1 1;1.1 .94;.94 1.04;1 1" keyTimes="0;.35;.7;1" calcMode="spline" keySplines="{SP(3)}" '
               f'dur="{4.2 + i * .7:.1f}s" repeatCount="indefinite"/>')
        # the reflection, stretched by the glass
        ref = person(0, 0, 1, p["teal"], p["navy"], sk, p["hair"], "stand")
        ref = f'<g>{ref}{wob}</g>'
        if wav:
            o.append(f'<g transform="translate({mx} 184) skewX(-14) scale(.9 1.2)" opacity=".75">{ref}</g>')
        else:
            o.append(f'<g transform="translate({mx} 184) scale({sx} {sy})" opacity=".75">{ref}</g>')
        o.append('</g>')
    o.append(person(1160, 220, 1.5, p["teal"], p["navy"], sk, p["hair"], "point", flip=True))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def bumper(x, y, s, c, p, flip=False, face=None):
    return (f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
            f'<line x1="18" y1="-30" x2="18" y2="-150" stroke="{p["steel2"]}" stroke-width="2.4"/><circle cx="18" cy="-150" r="3" fill="{p["gold"]}"/>'
            f'<ellipse cx="0" cy="-6" rx="46" ry="12" fill="#1c1c22"/>'
            f'<path d="M-40 -10 Q-42 -34 -14 -36 L28 -36 Q40 -34 40 -10Z" fill="{c}"/><path d="M-30 -30 L-6 -30 L-6 -20 L-36 -20Z" fill="#fff" opacity=".35"/>'
            f'<circle cx="6" cy="-50" r="9" fill="{face or p["skin"]}"/><path d="M-2 -52 Q6 -64 14 -52Z" fill="{p["hair"]}"/>'
            f'<path d="M-2 -40 L10 -40 L14 -32 L-6 -32Z" fill="{p["cream"]}"/></g>')

def v_training(n):  # bumper cars: the no-fault zone
    p = P(n); o = [base(n, star=20)]
    # the arena: roof fascia, the ceiling mesh the poles run on, the floor and its rail
    o.append(f'<rect x="0" y="40" width="1600" height="28" fill="{p["navy"]}"/><rect x="0" y="64" width="1600" height="6" fill="{p["gold"]}"/>')
    o.append(f'<rect x="0" y="70" width="1600" height="8" fill="#2a2a34"/>')
    o.append(''.join(f'<rect x="{x}" y="40" width="{24}" height="28" fill="{p["red"]}"/>' for x in range(0, 1600, 48)))
    o.append(f'<rect x="640" y="42" width="320" height="24" rx="4" fill="{p["navy"]}" stroke="{p["gold"]}" stroke-width="2"/>'
             f'<text x="800" y="60" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{p["gold"]}" letter-spacing="3">NO-FAULT ZONE</text>')
    o.append(bulbs("M0 72 H1600", 24, n, 4, wire=None, chase=2.4))
    fl = "#7c8794" if not n else "#262b36"
    o.append(f'<rect x="0" y="150" width="1600" height="90" fill="{fl}"/>')
    o.append(''.join(f'<path d="M{x} 150 L{x - 60} 240" stroke="#000" stroke-width="1" opacity=".15"/>' for x in range(0, 1700, 80)))
    o.append(f'<rect x="0" y="80" width="1600" height="70" fill="{"#d9b98a" if not n else "#1a1530"}" opacity=".5"/>')
    o.append(''.join(f'<rect x="{x}" y="204" width="{40}" height="12" fill="{p["gold"] if (x // 40) % 2 else p["red"]}"/>' for x in range(0, 1600, 40)))
    o.append(f'<rect x="0" y="216" width="1600" height="24" fill="#1c1c22"/>')
    T = 'dur="3.6s" repeatCount="indefinite"'
    for x, y, s, c, fl_, fc, dx in [(560, 196, 1.0, p["teal"], False, None, 24), (720, 184, .86, p["gold"], True, p["skin2"], 34), (870, 198, 1.04, p["red"], False, None, -34), (1030, 182, .84, p["purple"], True, p["skin2"], -24)]:
        o.append(f'<g>{bumper(x, y, s, c, p, fl_, fc)}<animateTransform attributeName="transform" type="translate" values="0 0;{-dx * .3:.0f} 0;{dx} 0;{dx * .6:.0f} 0;0 0" keyTimes="0;.3;.5;.58;1" '
                 f'calcMode="spline" keySplines="{SP(4)}" {T}/></g>')
    # a spark where two cars meet, on the pole tips too
    for x, y, rr in [(800, 172, 12), (650, 40 + 4, 6)]:
        o.append(f'<path d="M{x} {y - rr} L{x + rr * .3:.1f} {y - rr * .3:.1f} L{x + rr} {y} L{x + rr * .3:.1f} {y + rr * .3:.1f} L{x} {y + rr} L{x - rr * .3:.1f} {y + rr * .3:.1f} L{x - rr} {y} L{x - rr * .3:.1f} {y - rr * .3:.1f}Z" fill="#fff6b0">'
                 f'<animate attributeName="opacity" values="0;0;1;.6;0;0" keyTimes="0;.45;.5;.56;.66;1" {T}/></path>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the fairground map pinned to the gate, a route through four stops
    paper = "#efe2c2" if not n else "#3a3326"; paper2 = "#e2d2ac" if not n else "#2e281e"
    ink = "#5a3a22" if not n else "#d9c8a0"
    route = "#1f9a95" if athena else "#d23a2e"
    if n: route = "#5fd6cf" if athena else "#ff7a5a"
    p = P(n)
    o = [defs(), f'<rect width="1600" height="{V}" fill="{"#2a1d14" if not n else "#0c0907"}"/>']
    o.append(f'<rect x="300" y="18" width="1000" height="222" fill="{paper}" transform="rotate(-.6 800 130)"/>')
    o.append(f'<rect x="300" y="18" width="1000" height="222" fill="none" stroke="{ink}" stroke-width="3" stroke-dasharray="10 6" opacity=".4" transform="rotate(-.6 800 130)"/>')
    # paths, grass patches, and the attractions drawn as map pictures
    o.append(f'<path d="M340 200 C500 190 560 120 700 120 S900 180 1020 150 S1200 80 1280 90" stroke="{paper2}" stroke-width="34" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M700 120 L720 40 M1020 150 L1080 228" stroke="{paper2}" stroke-width="22" fill="none" stroke-linecap="round"/>')
    for x, y, rr in [(420, 90, 40), (880, 80, 34), (1180, 190, 36), (600, 210, 26)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{"#c9d4a0" if not n else "#2a3020"}"/>')
    o.append(f'<path d="M420 70 L392 106 L448 106Z" fill="{p["red"]}"/><path d="M420 70 L420 106 L448 106Z" fill="#fff" opacity=".3"/>')
    o.append(f'<circle cx="880" cy="72" r="22" fill="none" stroke="{ink}" stroke-width="3"/><path d="M880 72 L866 104 M880 72 L894 104 M858 72 H902 M880 50 V94" stroke="{ink}" stroke-width="2"/>')
    o.append(f'<ellipse cx="1180" cy="196" rx="24" ry="8" fill="{ink}" opacity=".5"/><path d="M1156 186 L1180 160 L1204 186Z" fill="{p["teal"]}"/><rect x="1160" y="186" width="40" height="8" fill="{p["gold"]}"/>')
    o.append(f'<path d="M332 214 L332 182 Q346 168 360 182 L360 214" stroke="{ink}" stroke-width="3" fill="none"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    pts = [(530, 160), (720, 112), (920, 150), (1110, 104)]
    d = f"M352 204 C400 196 440 186 {pts[0][0]} {pts[0][1]} S620 120 {pts[1][0]} {pts[1][1]} S840 170 {pts[2][0]} {pts[2][1]} S1060 112 {pts[3][0]} {pts[3][1]} S1220 94 1262 92"
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="5" stroke-dasharray="4 10" stroke-linecap="round"><animate attributeName="stroke-dashoffset" values="0;-14" dur="1.2s" repeatCount="indefinite"/></path>')
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        o.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{route}" stroke="{paper}" stroke-width="4"/><text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#fff">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{y - 24}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="{ink}" stroke="{paper}" stroke-width="5" paint-order="stroke">{t}</text>')
    o.append(f'<path d="M1262 80 l4 9 10 1 -8 6 3 10 -9 -6 -9 6 3 -10 -8 -6 10 -1Z" fill="{p["gold"]}" stroke="{ink}" stroke-width="1.5"><animate attributeName="opacity" values="1;.45;1" dur="2.4s" repeatCount="indefinite"/></path>')
    o.append(f'<text x="352" y="58" font-family="Georgia, serif" font-style="italic" font-size="15" fill="{ink}" opacity=".8">'
             + ('the service grounds &#183; you are here' if athena else 'the midway &#183; you are here') + '</text>')
    o.append(f'<g transform="translate(1230 190)"><circle r="24" fill="none" stroke="{ink}" stroke-width="2"/><g><path d="M0 -20 L5 0 L0 20 L-5 0Z" fill="{ink}"/>'
             f'<path d="M0 -20 L5 0 L-5 0Z" fill="{route}"/>{sway(0, 0, 9, 5)}</g><text y="-28" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="11" fill="{ink}">N</text></g>')
    o.append(corners(p, n))
    for x, y in [(318, 30), (1282, 26)]: o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{p["red"]}"/><circle cx="{x - 2}" cy="{y - 2}" r="2" fill="#fff" opacity=".6"/>')
    return vwrap(''.join(o))

def v_service(n):  # the ride operators at the controls, the swing ride behind them
    p = P(n); o = [base(n)]
    o.append(ground(p, 196, p["dirt2"]))
    # the swing ride: a tower, a spinning crown, chairs flung out on their chains
    tx = 1000
    if n: o.append(f'<ellipse cx="{tx}" cy="110" rx="240" ry="90" fill="url(#glow)" opacity=".6"/>')
    o.append(f'<rect x="{tx - 12}" y="60" width="24" height="140" fill="{p["wheel"]}"/>')
    o.append(f'<path d="M{tx - 120} 92 L{tx} 52 L{tx + 120} 92Z" fill="{p["red"]}"/><path d="M{tx - 120} 92 Q{tx} 112 {tx + 120} 92 L{tx + 120} 100 Q{tx} 120 {tx - 120} 100Z" fill="{p["gold"]}"/>')
    o.append(bulbs(f"M{tx - 118} 98 Q{tx} 118 {tx + 118} 98", 15, n, 4, wire=None, chase=2.1))
    ch = []
    for k, (ex, ey) in enumerate([(tx - 220, 150), (tx - 150, 168), (tx - 60, 176), (tx + 60, 176), (tx + 150, 168), (tx + 220, 150)]):
        sx = tx + (-110 + k * 44)
        ch.append(f'<line x1="{sx}" y1="104" x2="{ex}" y2="{ey - 12}" stroke="{p["steel2"]}" stroke-width="1.5"/>'
                  f'<path d="M{ex - 9} {ey - 12} L{ex + 9} {ey - 12} L{ex + 7} {ey} L{ex - 7} {ey}Z" fill="{[p["teal"], p["gold"], p["purple"]][k % 3]}"/>')
    o.append(f'<g transform="translate({tx} 104)"><g><g transform="translate({-tx} -104)">{"".join(ch)}</g>'
             f'<animateTransform attributeName="transform" type="scale" values="1 1;1.08 .94;1 1" calcMode="spline" keySplines="{SP(2)}" dur="5s" repeatCount="indefinite"/></g></g>')
    # the control booth: an open-front kiosk with a panel of buttons and a big lever
    o.append(f'<rect x="560" y="96" width="250" height="118" fill="{p["navy"] if not n else "#222a50"}"/>'
             f'<path d="M548 98 L822 98 L810 80 L560 80Z" fill="{p["red"]}"/><rect x="548" y="96" width="274" height="6" fill="{p["gold"]}"/>')
    o.append(f'<rect x="580" y="108" width="210" height="16" rx="3" fill="{p["cream"]}"/><text x="685" y="120" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="10" fill="{p["red2"]}" letter-spacing="1">KEEP HANDS INSIDE THE POLICY</text>')
    o.append(f'<rect x="572" y="160" width="226" height="16" fill="{p["steel2"]}"/><path d="M572 160 L590 150 L780 150 L798 160Z" fill="#3a3a44"/>')
    for i, c in enumerate(["#e04a3a", "#3ac76a", "#f2c23a", "#3ac76a", "#e04a3a"]):
        o.append(f'<circle cx="{610 + i * 22}" cy="155" r="4.5" fill="{c}">' + (f'<animate attributeName="opacity" values="1;.3;1" dur="1.4s" begin="{-i * .5:.1f}s" repeatCount="indefinite"/>' if i % 2 else '') + '</circle>')
        if n: o.append(f'<circle cx="{610 + i * 22}" cy="155" r="10" fill="{c}" opacity=".3"/>')
    o.append(f'<g><line x1="740" y1="158" x2="756" y2="128" stroke="#8a8a96" stroke-width="4"/><circle cx="756" cy="128" r="6" fill="#e04a3a"/>'
             f'<animateTransform attributeName="transform" type="rotate" values="0 740 158;0 740 158;-34 740 158;-34 740 158;0 740 158" keyTimes="0;.4;.5;.85;1" calcMode="spline" keySplines="{SP(4)}" dur="5s" repeatCount="indefinite"/></g>')
    cap = f'<path d="M-9 -66 Q0 -76 9 -66 L14 -64 L9 -63Z" fill="{p["red"]}"/>'
    o.append(person(720, 210, 1.15, p["gold"], "#2b3348", p["skin"], p["hair"], "lever", extra=cap))
    o.append(person(640, 210, 1.15, p["teal"], "#2b3348", p["skin2"], "#1c120c", "hold", extra=cap + f'<rect x="18" y="-50" width="10" height="13" fill="{p["cream"]}"/>'))
    o.append(f'<rect x="548" y="176" width="274" height="40" fill="{p["red2"]}"/><rect x="548" y="176" width="274" height="5" fill="{p["gold"]}"/>')
    o.append(f'<path d="M820 214 L1180 214" stroke="{p["gold"]}" stroke-width="4"/>' + ''.join(f'<rect x="{x}" y="196" width="5" height="20" fill="{p["gold"]}"/>' for x in range(840, 1180, 40)))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # the carousel: what comes back around
    p = P(n); o = [base(n)]
    o.append(far_fair(p, n, 1360, 230))
    o.append(ground(p, 198, p["dirt2"]))
    o.append(carousel(800, 196, .6, p, n))
    o.append(person(1060, 214, 1.15, p["purple"], "#2b3348", p["skin"], p["hair"], "point", flip=True))
    o.append(person(560, 214, 1.2, p["gold"], p["navy"], p["skin2"], "#1c120c", "stand", long_hair=True))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_claims(n):  # the storm-tossed tent and the crew holding it down
    p = P(n)
    sky = ("#4a5466", "#7a8090", "#a8a8a8") if not n else ("#05070e", "#11151f", "#22262e")
    o = [base(n, sky=sky, nt=sky, star=0)]
    for x, y, w in [(300, 40, 300), (760, 30, 360), (1200, 46, 320), (520, 70, 260), (1000, 66, 300)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="26" fill="{"#5a6272" if not n else "#181c26"}"/>')
    o.append(f'<path d="M1130 46 L1112 92 L1128 92 L1110 138" stroke="#fff6c0" stroke-width="4" fill="none" stroke-linejoin="round"/>')
    o.append(ground(p, 196, "#6a5a40" if not n else "#2a2218"))
    for x, y, w in [(620, 214, 90), (1010, 222, 70)]: o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="5" fill="#9aa8b8" opacity=".6"/>')
    # the tent leaning in the wind, a torn flap snapping
    o.append('<g transform="rotate(-6 800 200)">')
    t = "M800 66 C780 100 700 130 660 140 L668 200 L932 200 L940 140 C900 130 820 100 800 66Z"
    o.append(f'<defs><clipPath id="st"><path d="{t}"/></clipPath></defs><path d="{t}" fill="{p["cream"]}"/>')
    o.append('<g clip-path="url(#st)">' + ''.join(f'<path d="M800 66 L{650 + k * 40} 202 L{670 + k * 40} 202Z" fill="{p["red"]}"/>' for k in range(8)) + '</g>')
    o.append(f'<path d="M932 142 L990 118 L976 148 L1002 154 L940 172Z" fill="{p["red"]}"/>')
    o.append(f'<line x1="800" y1="66" x2="800" y2="48" stroke="{p["wood2"]}" stroke-width="3"/><path d="M800 48 L770 40 L800 60Z" fill="{p["gold"]}"/></g>')
    # guy ropes out to the crew, who lean back on them
    o.append(f'<path d="M676 140 L560 186 M930 136 L1060 184 M720 116 L600 176" stroke="{p["cream2"]}" stroke-width="2.4"/>')
    rain = ''.join(f'M{x} {y} l-14 30' for x, y in [(random.Random(i).randint(300, 1400), random.Random(i * 7).randint(0, 190)) for i in range(70)])
    yel = "#f2c23a"
    o.append(person(556, 212, 1.1, yel, "#2b3348", p["skin"], yel, "pull", flip=True))
    o.append(person(596, 212, 1.1, yel, "#2b3348", p["skin2"], yel, "pull", flip=True))
    o.append(person(1064, 212, 1.15, yel, "#2b3348", p["skin"], yel, "pull"))
    o.append(f'<path d="{rain}" stroke="#d8e2ee" stroke-width="1.6" opacity=".55"/>')
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the main gate and its marquee
    p = P(n); o = [base(n)]
    o.append(far_fair(p, n, 1000, 640))
    o.append(ground(p, 200, p["dirt2"]))
    if n: o.append('<ellipse cx="800" cy="110" rx="340" ry="110" fill="url(#glow)" opacity=".8"/>')
    for tx in (560, 1040):
        o.append(f'<rect x="{tx - 32}" y="70" width="64" height="146" fill="{p["red"]}"/>')
        for k in range(5): o.append(f'<rect x="{tx - 32}" y="{80 + k * 28}" width="64" height="12" fill="{p["cream"]}"/>')
        o.append(f'<path d="M{tx - 40} 72 L{tx} 44 L{tx + 40} 72Z" fill="{p["navy"] if not n else "#2a356a"}"/><line x1="{tx}" y1="44" x2="{tx}" y2="30" stroke="{p["gold"]}" stroke-width="3"/>')
        o.append(pennant(tx, 30, 26, p["gold"]))
        o.append(f'<rect x="{tx - 20}" y="160" width="40" height="30" rx="4" fill="{p["win"] if n else "#f5e2b0"}" stroke="{p["gold"]}" stroke-width="3"/>')
    # the arch and its marquee
    o.append(f'<path d="M592 96 Q800 40 1008 96 L1008 128 Q800 74 592 128Z" fill="{p["navy"] if not n else "#1c2550"}" stroke="{p["gold"]}" stroke-width="4"/>')
    o.append(bulbs("M600 100 Q800 46 1000 100", 15, n, 4.5, wire=None))
    o.append(bulbs("M600 124 Q800 70 1000 124", 15, n, 4.5, wire=None))
    o.append(f'<defs><path id="mq" d="M620 117 Q800 64 980 117"/></defs><text font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{p["gold"]}" letter-spacing="1">'
             f'<textPath href="#mq" startOffset="50%" text-anchor="middle">BIG TOP BUSINESS COVERAGE</textPath></text>')
    o.append(f'<rect x="700" y="130" width="200" height="22" rx="4" fill="{p["red2"]}" stroke="{p["gold"]}" stroke-width="2"/>'
             f'<text x="800" y="146" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="{p["ink"]}" letter-spacing="3">MAIN GATE</text>')
    # turnstiles
    for x in (720, 800, 880):
        o.append(f'<rect x="{x - 8}" y="182" width="16" height="32" fill="{p["steel2"]}"/><path d="M{x} 186 L{x + 22} 192 M{x} 186 L{x - 22} 192 M{x} 186 L{x} 174" stroke="{p["steel2"]}" stroke-width="4"/>')
    o.append(person(840, 218, .85, p["teal"], "#2b3348", p["skin"], p["hair"], "walk"))
    o.append(corners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the ring toss: everyone wins a quote"],
    "messages": ["Texts & Emails", "the ticket booth: every reply punched"],
    "coaching": ["Coaching", "the fortune teller: every call, read"],
    "roleplay": ["Role Play", "the high striker: swing till it rings"],
    "rphistory": ["Session History", "the funhouse mirrors: every session, replayed"],
    "training": ["Training", "the bumper cars: a no-fault place to learn"],
    "blueprint": ["Apollo's Road Map", "the fairground map, in plain words"],
    "athenamap": ["Athena's Road Map", "the service grounds map, in plain words"],
    "service": ["Service Digest", "the ride operators: keeping the book running"],
    "renewals": ["Renewals", "the carousel: what comes back around"],
    "claims": ["Claims", "the tent crew: after the storm"],
    "commercial": ["Commercial Center", "the main gate: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day=DAYSKY, nt=NIGHTSKY, star=30):
    return defs(skyg(n, day=day, nt=nt)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 90, 21) if n else '')

def sground(p, y, c=None):
    return f'<path d="M0 {y} Q800 {y - 10} 1600 {y} L1600 160 L0 160Z" fill="{c or p["dirt2"]}"/>'

def s_sold(n):  # the hammer rings the bell
    p = P(n); o = [sbase(n, ("#e09a3a", "#f6c66a", "#fde6a8"), ("#0a1030", "#1a2858", "#3a3a6a"))]
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        o.append(f'<path d="M760 46 L{760 + 700 * math.cos(ang):.0f} {46 + 700 * math.sin(ang):.0f} L{760 + 700 * math.cos(ang + .12):.0f} {46 + 700 * math.sin(ang + .12):.0f}Z" fill="#fff" opacity="{.18 if not n else .07}"/>')
    o.append(sground(p, 122))
    o.append(striker(760, 132, 94, p, n, 1.0, ring=True))
    o.append(person(842, 130, .95, p["red"], p["navy"], p["skin"], p["hair"], "lever", flip=True))
    o.append(mallet(800, 120, -78, p, 40))
    r = random.Random(5)
    for _ in range(34):
        x = r.randint(540, 1020); y = r.randint(30, 110)
        o.append(f'<rect x="{x}" y="{y}" width="6" height="10" fill="{r.choice([p["gold"], p["teal"], p["red"], "#7fb2e8", "#fff"])}" transform="rotate({r.randint(0, 90)} {x} {y})"/>')
    return wrap(S, ''.join(o))

def s_open(n):  # a gondola at the very top of the wheel, the riders looking out
    p = P(n); o = [sbase(n, ("#4f7ac0", "#e0a070", "#f6d39a"))]
    o.append(f'<path d="M0 132 Q400 120 800 128 T1600 124 L1600 160 L0 160Z" fill="{p["tree"]}"/>')
    if n: o.append(''.join(f'<circle cx="{x}" cy="{y}" r="2" fill="{p["bulb"]}" opacity=".8"/>' for x, y in [(200, 128), (260, 126), (380, 130), (1040, 126), (1120, 128), (1180, 125)]))
    o.append(f'<defs><clipPath id="sc"><rect width="1600" height="160"/></clipPath></defs><g clip-path="url(#sc)">' + ferris(800, 470, 420, p, n, gk=36, ymax=170).replace('url(#glow)', 'none') + '</g>')
    # riders in the top car
    o.append(f'<circle cx="790" cy="72" r="5" fill="{p["skin"]}"/><circle cx="806" cy="72" r="5" fill="{p["skin2"]}"/><path d="M806 70 L822 62" stroke="{p["skin2"]}" stroke-width="2.4" stroke-linecap="round"/>')
    return wrap(S, ''.join(o))

def s_lost(n):  # a popped balloon in the drizzle
    p = P(n); o = [sbase(n, ("#6a6e78", "#9a9ea6", "#c4c6ca"), ("#0a0c14", "#1a1d28", "#2a2d3a"), 6)]
    for x in (300, 720, 1150): o.append(f'<ellipse cx="{x}" cy="34" rx="220" ry="24" fill="{"#7a7e88" if not n else "#20232e"}"/>')
    o.append(sground(p, 124, "#6a6458" if not n else "#1c1a18"))
    o.append(f'<ellipse cx="840" cy="134" rx="80" ry="6" fill="#9aa8b8" opacity=".5"/>')
    # the burst: ragged shreds around where it was, the string falling
    c = p["red"]
    o.append(f'<path d="M790 66 l-8 -14 l14 6 l2 -16 l8 14 l12 -10 l-2 16 l16 2 l-14 8 l10 12 l-16 -2 l-4 14 l-6 -14 l-14 6 l6 -14Z" fill="{c}" opacity=".9"/>')
    for x, y, rot in [(760, 50, 30), (828, 46, -20), (836, 82, 60), (770, 86, -40)]:
        o.append(f'<path d="M{x} {y} q6 -4 10 2 q-4 6 -10 -2Z" fill="{c}" transform="rotate({rot} {x} {y})"/>')
    o.append(f'<path d="M800 76 Q792 96 806 110 Q818 124 808 132" stroke="#e8e2d8" stroke-width="1.6" fill="none"/>')
    o.append(f'<path d="M754 40 L746 32 M846 40 L854 32 M760 98 L750 104 M842 96 L852 102" stroke="#fff" stroke-width="2" opacity=".6"/>')
    rain = ''.join(f'M{x} {y} l-8 20' for x, y in [(random.Random(i).randint(380, 1260), random.Random(i * 5).randint(10, 120)) for i in range(46)])
    o.append(f'<path d="{rain}" stroke="#dbe4ee" stroke-width="1.4" opacity=".55"/>')
    return wrap(S, ''.join(o))

def s_dead(n):  # a ride closed, the chain up across its gate
    p = P(n); o = [sbase(n, ("#8a9aa4", "#bcc6cc", "#e2e2d8"), ("#0c0e14", "#1c1f28", "#30333e"), 10)]
    o.append(sground(p, 124, "#9a8a70" if not n else "#26221c"))
    # the ride behind, dark: a coaster car parked at its station
    dim = "#7a7a80" if not n else "#2e3038"
    o.append(f'<path d="M520 60 L1080 60 L1080 70 L520 70Z" fill="{dim}"/>' + ''.join(f'<rect x="{x}" y="70" width="8" height="56" fill="{dim}"/>' for x in (540, 700, 900, 1060)))
    o.append(f'<path d="M760 96 L758 80 L838 80 L838 96Z" fill="{dim}"/><rect x="740" y="96" width="120" height="6" fill="{dim}"/>')
    # the gate posts, the chain, the red sign hanging from it
    for x in (660, 940): o.append(f'<rect x="{x - 7}" y="58" width="14" height="70" fill="{p["red2"]}"/><circle cx="{x}" cy="58" r="9" fill="{p["gold2"]}"/>')
    ch = "M667 82 Q800 118 933 82"
    o.append(f'<path d="{ch}" fill="none" stroke="#c9c4b8" stroke-width="5" stroke-dasharray="7 3"/>')
    o.append(f'<rect x="770" y="100" width="60" height="30" rx="4" fill="#d23a2e" stroke="#fff" stroke-width="3"/><rect x="782" y="112" width="36" height="6" fill="#fff"/>')
    o.append(f'<path d="M560 128 L572 96 L584 128Z M1010 128 L1022 96 L1034 128Z" fill="#e98a2a"/><rect x="564" y="112" width="16" height="4" fill="#fff"/><rect x="1014" y="112" width="16" height="4" fill="#fff"/>')
    return wrap(S, ''.join(o))

def cone(x, y, c):
    return (f'<path d="M{x} {y} L{x - 9} {y - 30} L{x + 9} {y - 30}Z" fill="#e8d4a8"/>'
            f'<circle cx="{x - 8}" cy="{y - 38}" r="11" fill="{c}"/><circle cx="{x + 7}" cy="{y - 40}" r="12" fill="{c}"/><circle cx="{x}" cy="{y - 50}" r="11" fill="{c}"/>'
            f'<circle cx="{x - 3}" cy="{y - 46}" r="4" fill="#fff" opacity=".45"/>')

def s_reached(n):  # two friends sharing cotton candy on the midway
    p = P(n); o = [sbase(n)]
    o.append(f'<path d="M0 128 Q400 118 800 124 T1600 120 L1600 160 L0 160Z" fill="{p["tree"]}"/>')
    o.append(bulbs(sag(300, 44, 1250, 44, 18), 26, n, 5))
    o.append(sground(p, 132))
    o.append(person(720, 140, 1.25, p["teal"], p["navy"], p["skin"], p["hair"], "hold"))
    o.append(person(880, 140, 1.25, p["gold"], "#2b3348", p["skin2"], "#1c120c", "hold", flip=True, long_hair=True))
    o.append(cone(752, 88, "#8fd0f4"))
    o.append(cone(848, 86, "#f6e36a"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # waiting in line at the ticket booth
    p = P(n); o = [sbase(n, ("#d98a4a", "#f2c27a", "#fbe6b8"))]
    o.append(sground(p, 128))
    bx = 900
    o.append(f'<rect x="{bx - 60}" y="56" width="120" height="74" fill="{p["red"]}"/><path d="M{bx - 76} 58 L{bx} 22 L{bx + 76} 58Z" fill="{p["navy"]}"/>')
    o.append(f'<path d="M{bx - 38} 112 V82 Q{bx} 70 {bx + 38} 82 V112Z" fill="{p["win"] if n else "#f5e2b0"}" stroke="{p["gold"]}" stroke-width="3"/><rect x="{bx - 44}" y="110" width="88" height="6" fill="{p["gold2"]}"/>')
    o.append(f'<circle cx="{bx}" cy="96" r="7" fill="{p["skin2"]}"/>')
    for x in (640, 760): o.append(f'<rect x="{x - 3}" y="100" width="6" height="30" fill="{p["gold"]}"/><circle cx="{x}" cy="98" r="5" fill="{p["gold"]}"/>')
    o.append(f'<path d="M640 104 Q700 122 760 104" stroke="{p["red"]}" stroke-width="4" fill="none"/>')
    o.append(person(800, 134, 1.05, p["teal"], p["navy"], p["skin"], p["hair"], "stand"))
    return wrap(S, ''.join(o))

def s_vm(n):  # the midway dark after closing, under the moon
    p = P(True); o = [sbase(True, nt=("#04060f", "#0a0f24", "#141a38"), star=50)]
    o.append(moon(1060, 50, 16))
    sil = "#0a0c16"
    o.append(f'<circle cx="700" cy="96" r="70" fill="none" stroke="#2a2e44" stroke-width="4"/>'
             f'<path d="' + ''.join(f'M700 96 L{700 + 70 * math.cos(k * math.pi / 6):.0f} {96 + 70 * math.sin(k * math.pi / 6):.0f}' for k in range(12)) + '" stroke="#2a2e44" stroke-width="1.6"/>'
             f'<path d="M700 96 L660 160 M700 96 L740 160" stroke="#2a2e44" stroke-width="4"/>')
    o.append(f'<path d="M880 70 C866 92 820 108 796 114 L800 160 L960 160 L964 114 C940 108 894 92 880 70Z" fill="{sil}"/><line x1="880" y1="70" x2="880" y2="56" stroke="{sil}" stroke-width="3"/>')
    o.append(f'<path d="{sag(470, 60, 1180, 60, 14)}" stroke="#2a2e44" stroke-width="1.4" fill="none"/>' + bulbs(sag(470, 60, 1180, 60, 14), 22, False, 4, wire=None).replace(P(False)["bulb"], "#3a3a4a"))
    o.append(f'<path d="M0 126 Q800 116 1600 126 L1600 160 L0 160Z" fill="{sil}"/>')
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Step right up, {n}.", "The midway's open, {n}.", "Everybody wins a quote today, {n}.", "Ring the bell, {n}.",
             "Grab a ticket, {n} -- the rides are running.", "The big top is yours, {n}.", "Knock 'em down, {n}.",
             "Win the big prize today, {n}.", "Take it for a spin, {n}.", "The wheel is turning, {n}.",
             "Toss it right on the peg, {n}.", "Hold on tight, {n} -- here comes the drop.", "Lights are on at the fair, {n}.",
             "Every ride comes back around, {n}.", "Show 'em the greatest quote in town, {n}."]

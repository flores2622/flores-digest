"""The Autumn world: a New England-style valley in peak colour at golden hour. Colour looks, fonts, the
Digest picture, page banners, card strips."""
import random, math

KEY = "autumn"
NAME = "Autumn"
CATEGORY = "Scenic"   # the group it is listed under in Settings
FONTS = "family=Playfair+Display:wght@700;800&family=Nunito+Sans:wght@400;500;600;700"
DISPLAY = "'Playfair Display', Georgia, serif"
DW = 700
BODY = "'Nunito Sans', system-ui, sans-serif"
SKY_BG = (("#e9b27a", "#9a9a4a"), ("#0a0d1f", "#161c16"))

LOOKS = [
    ("maple", "Maple",
     "--surface: #f3ece2; --surface-raised: #fffbf5; --card2: #f8f1e7; --chip: #efe2d2; --text-primary: #2a1a14; --text-muted: #6c564a; --text-secondary: #533f35; --grid: #ece0d1; --border: #e3d5c4; --border-strong: #c9b19a; --accent: #a8321e; --accent-d: #84240f; --side: #4a1a14; --side2: #5c241b; --sideInk: #f6e6dc; --brand: #fbf1e6; --brand2: #f2b25a; --rad: 12px;",
     "--surface: #15100e; --surface-raised: #1e1714; --card2: #251d19; --chip: #2e241f; --text-primary: #f2e7e0; --text-muted: #b4a196; --text-secondary: #cbb9ae; --grid: #2e241f; --border: #322722; --border-strong: #4a3a32; --accent: #f08a6a; --accent-d: #f6ad94; --side: #0d0806; --side2: #1e110d; --sideInk: #f6e6dc; --brand: #fbf1e6; --brand2: #f2b25a;",
     ["#f3ece2", "#4a1a14", "#c23a22"]),
    ("harvesthome", "Harvest",
     "--surface: #f2eadb; --surface-raised: #fdf8ee; --card2: #f7efe0; --chip: #eee0c8; --text-primary: #2b1d10; --text-muted: #6c5a44; --text-secondary: #544330; --grid: #ebdfca; --border: #e2d3ba; --border-strong: #c8b08a; --accent: #a8500e; --accent-d: #843c08; --side: #3a2614; --side2: #4a321c; --sideInk: #f3e6d2; --brand: #f8efe0; --brand2: #f4a23e; --rad: 14px;",
     "--surface: #15110b; --surface-raised: #1d1811; --card2: #241e15; --chip: #2d251a; --text-primary: #f1e8da; --text-muted: #b2a288; --text-secondary: #c9bba2; --grid: #2d251a; --border: #31281c; --border-strong: #46392a; --accent: #f4a24e; --accent-d: #f8bf7e; --side: #0e0a06; --side2: #1c140c; --sideInk: #f3e6d2; --brand: #f8efe0; --brand2: #f4a23e;",
     ["#f2eadb", "#3a2614", "#e07a1c"]),
    ("birch", "Birch",
     "--surface: #eceae4; --surface-raised: #fbfaf7; --card2: #f2f0eb; --chip: #e3e0d8; --text-primary: #1f1e1a; --text-muted: #5d5a52; --text-secondary: #46443d; --grid: #e2dfd7; --border: #d8d4cb; --border-strong: #bab4a6; --accent: #8a6a0a; --accent-d: #6a5006; --side: #33322e; --side2: #43413c; --sideInk: #ebe8e0; --brand: #f4f2ec; --brand2: #e8c24a; --rad: 10px;",
     "--surface: #111110; --surface-raised: #191917; --card2: #1f1f1c; --chip: #282823; --text-primary: #ecebe6; --text-muted: #a9a69c; --text-secondary: #c3c0b6; --grid: #282823; --border: #2b2b26; --border-strong: #3e3d36; --accent: #e8c24a; --accent-d: #f0d47c; --side: #0a0a09; --side2: #171715; --sideInk: #ebe8e0; --brand: #f4f2ec; --brand2: #e8c24a;",
     ["#eceae4", "#33322e", "#d8b23a"]),
]

TOUR = {"k": "Trail guide", "next": "Next leaf", "back": "Back", "done": "Harvest's in!", "skip": "Head home"}

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(far="#2a2b4a", far2="#23243f", hill="#2a2230", hill2="#221b28",
                    red="#6a2a26", red2="#55201e", orange="#74401f", gold="#7a6230", yel="#857238", ever="#16241f",
                    grass="#1e2a1a", grass2="#19241a", lawn="#23321f", lawn2="#1e2b1b", road="#3e3b40", road2="#2f2c32",
                    stone="#55555e", stone2="#3c3c44", water="#1a2f52", water2="#4a6a9a", wood="#3e2818", wood2="#2a1a0e",
                    barn="#4e1c1a", barn2="#3c1513", white="#8e92a6", white2="#6e7288", roof="#2a2630", roof2="#1e1b24",
                    win="#ffcf6a", ink="#f6e8d0", trunk="#2a1c14", birch="#a8aab8", pump="#a8521c", pump2="#7c3a12",
                    hay="#7e6a3a", hay2="#5e4e28", skin="#c2946e", sky=("#060918", "#121a3a", "#2a2a4a"))
    return dict(far="#b59bb0", far2="#a48aa2", hill="#9a5a34", hill2="#86492a",
                red="#c8361f", red2="#a52a18", orange="#e3762a", gold="#efae32", yel="#f3d04e", ever="#3c5a3c",
                grass="#a7a54e", grass2="#958f40", lawn="#9db054", lawn2="#8aa046", road="#c9b48e", road2="#a8946e",
                stone="#b2aca0", stone2="#8c867a", water="#5d93b8", water2="#a8d0e6", wood="#7a4e2c", wood2="#55341a",
                barn="#b2302a", barn2="#8a221e", white="#f6f1e6", white2="#ddd5c4", roof="#4a4448", roof2="#36313a",
                win="#9fbccc", ink="#fbf2de", trunk="#5a3a24", birch="#f2efe8", pump="#e8761e", pump2="#c25a10",
                hay="#e6c46a", hay2="#c4a04a", skin="#e2b48c", sky=("#5a8cc4", "#f0b07a", "#f8d8a8"))

def leafcols(p): return [p["red"], p["red2"], p["orange"], p["gold"], p["yel"]]

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc35a" stop-opacity=".6"/>'
            '<stop offset="1" stop-color="#ffc35a" stop-opacity="0"/></radialGradient>' + LEAF + extra + '</defs>')

def skyg(p, id="g"):
    c = p["sky"]
    return (f'<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/>'
            f'<stop offset=".62" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>')

def stars(k, x0, x1, y0, y1, seed, op=(0.35, 0.55, 0.85)):
    r = random.Random(seed); g = {}
    for _ in range(k):
        g.setdefault(r.choice(op), []).append((r.randint(x0, x1), r.randint(y0, y1), r.choice([1, 1, 1.4, 2]), "#fff"))
    return ''.join(blobs(v, f' opacity="{o_}"') for o_, v in g.items())

def moon(x, y, r):
    """the harvest moon: big, low and amber"""
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3.2:.0f}" fill="#ffcf8a" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.8:.0f}" fill="#ffcf8a" opacity=".13"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f7c873"/><circle cx="{x - r * .32:.0f}" cy="{y - r * .18:.0f}" r="{r * .2:.0f}" fill="#e6b060" opacity=".7"/>'
            f'<circle cx="{x + r * .3:.0f}" cy="{y + r * .32:.0f}" r="{r * .13:.0f}" fill="#e6b060" opacity=".7"/><circle cx="{x + r * .36:.0f}" cy="{y - r * .36:.0f}" r="{r * .09:.0f}" fill="#e6b060" opacity=".6"/>')

def sun(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3:.0f}" fill="#ffe3a8" opacity=".25"/><circle cx="{x}" cy="{y}" r="{r * 1.7:.0f}" fill="#ffe8b8" opacity=".4"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff2cc"/>')

def hills(pts, b, c):
    d = f'M{pts[0][0]} {b} L{pts[0][0]} {pts[0][1]}'
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2; my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f' Q{pts[i][0]} {pts[i][1]} {mx:.0f} {my:.0f}'
    d += f' L{pts[-1][0]} {pts[-1][1]} L{pts[-1][0]} {b}Z'
    return f'<path d="{d}" fill="{c}"/>'

def show(times, vals, dur, attr="opacity", begin=0):
    """an <animate> that steps an attribute through vals at keyTimes, looping"""
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s" begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>')

def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {b};{deg} {x} {b};{-deg} {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

def blobs(cs, extra=''):
    """many circles as one path per colour (in first-seen order): [(cx, cy, r, fill), ...]"""
    g = {}
    for cx, cy, r, c in cs:
        r = max(1, round(r)); cx = round(cx); cy = round(cy)
        g.setdefault(c, []).append(f'M{cx} {cy}h{r}v{r}h-{r}z' if r <= 1 else f'M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0')
    return ''.join(f'<path d="{"".join(v)}" fill="{c}"{extra}/>' for c, v in g.items())

# ----------------------------------------------------------------- trees
def maple(x, b, h, cols, seed, tc, w=1.0):
    """a round-crowned maple: tapering trunk and limbs, the crown dark beneath, lit clumps on top, a leafy edge"""
    r = random.Random(seed); R = h * .34 * w; cy = b - h * .64
    o = [f'<path d="M{x - h * .045:.0f} {b} Q{x - h * .02:.0f} {b - h * .3:.0f} {x - h * .02:.0f} {b - h * .5:.0f} L{x + h * .02:.0f} {b - h * .5:.0f} Q{x + h * .02:.0f} {b - h * .3:.0f} {x + h * .045:.0f} {b}Z" fill="{tc}"/>']
    o.append(f'<ellipse cx="{x}" cy="{cy:.0f}" rx="{R * 1.02:.0f}" ry="{R * .86:.0f}" fill="{cols[0]}"/>')
    L = []
    for k in range(14):  # the leafy edge
        t = k / 14 * 2 * math.pi
        L.append((x + math.cos(t) * R * .98, cy + math.sin(t) * R * .82, R * r.uniform(.16, .24), cols[0] if math.sin(t) > .2 else cols[1]))
    o.append(blobs(L)); L = []
    for k in range(7):
        t = r.uniform(0, 2 * math.pi); d = r.uniform(0, .5)
        L.append((x + math.cos(t) * R * d, cy + math.sin(t) * R * d * .8 - R * .12, R * r.uniform(.3, .42), cols[1 + k % 2]))
    o.append(blobs(L)); L = []
    o.append(f'<path d="M{x} {b - h * .44:.0f} L{x - R * .45:.0f} {cy + R * .25:.0f} M{x} {b - h * .48:.0f} L{x + R * .4:.0f} {cy + R * .1:.0f} M{x} {b - h * .5:.0f} L{x + R * .05:.0f} {cy - R * .2:.0f}" stroke="{tc}" stroke-width="{max(2, h * .016):.1f}" fill="none" stroke-linecap="round"/>')
    for k in range(6):
        t = r.uniform(-2.6, -.6); d = r.uniform(.25, .7)
        L.append((x + math.cos(t) * R * d, cy + math.sin(t) * R * d * .8, R * r.uniform(.16, .28), cols[3 + k % 2]))
    o.append(blobs(L))
    return ''.join(o)

def birch(x, b, h, cols, seed, bark="#f2efe8", mark="#3a3530", lean=0):
    """a slim white birch: the trunk with its dark marks, a narrow golden crown"""
    r = random.Random(seed); tw = max(3, h * .03); tx = x + lean
    o = [f'<path d="M{x - tw:.1f} {b} L{tx - tw * .5:.1f} {b - h * .8:.0f} L{tx + tw * .5:.1f} {b - h * .8:.0f} L{x + tw:.1f} {b}Z" fill="{bark}"/>']
    for k in range(int(h / 24)):
        t = r.uniform(.08, .7); yy = b - h * t; xx = x + lean * t
        o.append(f'<rect x="{xx - tw * .9:.1f}" y="{yy:.0f}" width="{tw * r.uniform(.6, 1.4):.1f}" height="{max(1.5, h * .008):.1f}" fill="{mark}"/>')
    cy = b - h * .72; R = h * .2
    for k, (dx, dy, rr) in enumerate([(0, -.9, .7), (-.5, -.2, .75), (.5, -.3, .7), (0, .3, .8), (-.3, .8, .6), (.35, .7, .6), (0, -.1, .7)]):
        o.append(f'<ellipse cx="{tx + dx * R + r.uniform(-2, 2):.0f}" cy="{cy + dy * R:.0f}" rx="{rr * R * .8:.0f}" ry="{rr * R:.0f}" fill="{cols[k % len(cols)]}"/>')
    return ''.join(o)

def pine(x, b, h, c):
    w = h * .36
    return (f'<path d="M{x} {b - h} L{x + w * .32:.0f} {b - h * .62:.0f} L{x + w * .18:.0f} {b - h * .62:.0f} L{x + w * .5:.0f} {b - h * .1:.0f} '
            f'L{x - w * .5:.0f} {b - h * .1:.0f} L{x - w * .18:.0f} {b - h * .62:.0f} L{x - w * .32:.0f} {b - h * .62:.0f}Z" fill="{c}"/>'
            f'<rect x="{x - 2}" y="{b - h * .1:.0f}" width="4" height="{h * .1:.0f}" fill="{c}"/>')

def canopy(x0, x1, b, rmin, rmax, cols, seed, step=26, base=None):
    """a hillside of trees in colour, seen from afar: overlapping crowns along a line"""
    r = random.Random(seed); o = []; L = []
    if base: o.append(f'<rect x="{x0}" y="{b - rmin}" width="{x1 - x0}" height="{rmin + 2}" fill="{base}"/>')
    x = x0
    while x < x1:
        rr = r.randint(rmin, rmax); L.append((x, b - rr * .55 + r.randint(-rmin // 3, rmin // 3), rr, r.choice(cols))); x += r.randint(step - 8, step + 8)
    return ''.join(o) + blobs(L)

def bare(x, b, h, c, seed, w=3):
    """a bare tree, its branches forking (one path per thickness)"""
    r = random.Random(seed); lv = {}
    def br(x0, y0, ang, ln, d):
        if d == 0: return
        x1 = x0 + ln * math.sin(ang); y1 = y0 - ln * math.cos(ang)
        lv.setdefault(d, []).append(f'M{x0:.0f} {y0:.0f}L{x1:.0f} {y1:.0f}')
        for s_ in (-1, 1): br(x1, y1, ang + s_ * r.uniform(.3, .6), ln * r.uniform(.6, .75), d - 1)
    br(x, b - h * .45, 0, h * .25, 4)
    o = [f'<path d="M{x - w * 1.6:.0f} {b} L{x - w * .6:.0f} {b - h * .45:.0f} L{x + w * .6:.0f} {b - h * .45:.0f} L{x + w * 1.6:.0f} {b}Z" fill="{c}"/>']
    for d, segs in lv.items():
        o.append(f'<path d="{"".join(segs)}" stroke="{c}" stroke-width="{w * 1.2 * .65 ** (4 - d):.1f}" stroke-linecap="round" fill="none"/>')
    return ''.join(o)

# ----------------------------------------------------------------- farm things
def pumpkin(x, y, r, p, stem="#4a5a2a"):
    return (f'<ellipse cx="{x}" cy="{y - r * .8:.1f}" rx="{r * 1.2:.1f}" ry="{r * .85:.1f}" fill="{p["pump"]}"/>'
            f'<ellipse cx="{x}" cy="{y - r * .8:.1f}" rx="{r * .45:.1f}" ry="{r * .85:.1f}" fill="none" stroke="{p["pump2"]}" stroke-width="{max(1, r * .14):.1f}"/>'
            f'<path d="M{x} {y - r * 1.6:.1f} q{r * .1:.1f} {-r * .5:.1f} {r * .4:.1f} {-r * .55:.1f}" stroke="{stem}" stroke-width="{max(1.4, r * .25):.1f}" fill="none" stroke-linecap="round"/>')

def haybale(x, y, w, h, p):
    o = [f'<rect x="{x - w / 2:.0f}" y="{y - h}" width="{w}" height="{h}" rx="{h * .18:.0f}" fill="{p["hay"]}"/>']
    for k in range(1, 4): o.append(f'<line x1="{x - w / 2 + 3:.0f}" y1="{y - h * k / 4:.0f}" x2="{x + w / 2 - 3:.0f}" y2="{y - h * k / 4:.0f}" stroke="{p["hay2"]}" stroke-width="1.2" opacity=".7"/>')
    o.append(f'<line x1="{x - w * .22:.0f}" y1="{y - h}" x2="{x - w * .22:.0f}" y2="{y}" stroke="{p["hay2"]}" stroke-width="2"/><line x1="{x + w * .22:.0f}" y1="{y - h}" x2="{x + w * .22:.0f}" y2="{y}" stroke="{p["hay2"]}" stroke-width="2"/>')
    return ''.join(o)

def crate(x, y, w, h, p, fruit="#c8361f"):
    """an apple crate, side on, heaped with apples"""
    o = []
    for k in range(int(w / (h * .32))):
        o.append(f'<circle cx="{x - w / 2 + h * .2 + k * h * .32:.0f}" cy="{y - h - h * .06:.0f}" r="{h * .2:.1f}" fill="{fruit}"/>')
    o.append(f'<rect x="{x - w / 2:.0f}" y="{y - h}" width="{w}" height="{h}" fill="{p["wood"]}"/>')
    o.append(f'<line x1="{x - w / 2:.0f}" y1="{y - h / 2:.0f}" x2="{x + w / 2:.0f}" y2="{y - h / 2:.0f}" stroke="{p["wood2"]}" stroke-width="1.5"/>')
    o.append(f'<rect x="{x - w / 2:.0f}" y="{y - h}" width="{w}" height="{h}" fill="none" stroke="{p["wood2"]}" stroke-width="1.5"/>')
    return ''.join(o)

def stonewall(pts, h, p, seed):
    """a dry-stone wall along a polyline: the dark body, then two courses of rounded stones (dashed strokes)"""
    up = lambda dy: 'M' + ' L'.join(f'{x:.0f} {y - dy:.0f}' for x, y in pts)
    top = ' '.join(f'{x:.0f},{y - h:.0f}' for x, y in pts); bot = ' '.join(f'{x:.0f},{y:.0f}' for x, y in reversed(pts))
    return (f'<polygon points="{top} {bot}" fill="{p["stone2"]}"/>'
            f'<path d="{up(h * .7)}" fill="none" stroke="{p["stone"]}" stroke-width="{h * .55:.1f}" stroke-linecap="round" stroke-dasharray="{h * .6:.1f} {h * .7:.1f}"/>'
            f'<path d="{up(h * .25)}" fill="none" stroke="{p["stone"]}" stroke-width="{h * .45:.1f}" stroke-linecap="round" stroke-dasharray="{h * .9:.1f} {h * .6:.1f}" stroke-dashoffset="{h * .6:.1f}" opacity=".85"/>')

LEAF = '<path id="lf" d="M0-10 2.5-4 8-6 5.5 0 9 3 3 3.5 1 8 0 4-1 8-3 3.5-9 3-5.5 0-8-6-2.5-4Z"/>'
def leaf(x, y, s, c, rot=0):
    """a maple leaf, five points (the shape lives in defs as #lf)"""
    return f'<use href="#lf" transform="translate({x} {y}) rotate({rot}) scale({s})" fill="{c}"/>'

def person(x, y, s, pose="stand", coat="#2f5a8a", pants="#3a3a44", hat="#7a3a1e", skin="#e2b48c", flip=False, hk="cap"):
    """a villager in a field jacket; feet on y"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{pants}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    arm = f'stroke="{coat}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    boots = '<ellipse cx="-6" cy="-1" rx="5" ry="2.8" fill="#3a2a1e"/><ellipse cx="7" cy="-1" rx="5" ry="2.8" fill="#3a2a1e"/>'
    hx, hy = 0, -64
    if pose == "sit":   # sitting on something 18 high, facing right
        b = (f'<path d="M-4 -18 L12 -18 L14 0 M-2 -20 L14 -20 L16 0" {leg}/>' + '<ellipse cx="16" cy="-1" rx="5" ry="2.8" fill="#3a2a1e"/>' +
             f'<path d="M-9 -46 Q0 -50 8 -46 L6 -18 L-8 -18Z" fill="{coat}"/><path d="M5 -42 L14 -28 L18 -26" {arm}/>')
        hx, hy = 0, -54
    else:
        b = f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + boots + f'<path d="M-9 -56 Q0 -60 9 -56 L8 -28 L-8 -28Z" fill="{coat}"/>'
        if pose == "rake":     # rake held across, tines on the ground ahead
            b += f'<path d="M5 -52 L14 -42 L20 -40 M-5 -52 L4 -36 L12 -32" {arm}/><line x1="-2" y1="-56" x2="44" y2="-2" stroke="#8a6a3a" stroke-width="2.6"/>'
            b += '<path d="M36 0 L52 -6 M38 1 L40 -4 M42 0 L44 -5 M46 -1 L48 -6 M50 -3 L52 -7" stroke="#6a6a6a" stroke-width="2" fill="none"/>'
        elif pose == "carry":  # a crate held at the chest
            b += f'<path d="M5 -52 L16 -42 M-5 -52 L6 -40" {arm}/>'
            b += '<circle cx="14" cy="-52" r="3.6" fill="#c8361f"/><circle cx="21" cy="-52" r="3.6" fill="#d8452a"/><circle cx="28" cy="-52" r="3.6" fill="#c8361f"/>'
            b += '<rect x="8" y="-50" width="26" height="14" fill="#8a5a32" stroke="#5a3418" stroke-width="1.5"/>'
        elif pose == "reach":  # reaching up into the branches
            b += f'<path d="M5 -52 L12 -68 L16 -82 M-5 -52 L-9 -36" {arm}/>'
        elif pose == "wave":
            b += f'<path d="M5 -52 L16 -66 L20 -80 M-5 -52 L-9 -36" {arm}/>'
        elif pose == "point":
            b += f'<path d="M5 -52 L22 -58 L34 -60 M-5 -52 L-9 -36" {arm}/>'
        elif pose == "lean":   # forearms on a wall top at about -38
            b += f'<path d="M5 -52 L10 -38 L26 -38 M-5 -52 L2 -40 L20 -40" {arm}/>'
        elif pose == "saw":    # a chainsaw held low in front
            b += f'<path d="M5 -52 L14 -36 M-5 -52 L4 -34" {arm}/><rect x="8" y="-40" width="18" height="12" rx="3" fill="#e8761e"/><rect x="24" y="-36" width="30" height="5" rx="2" fill="#9a9a9a"/>'
        elif pose == "mail":   # reaching into a mailbox at chest height
            b += f'<path d="M5 -52 L18 -46 L28 -46 M-5 -52 L-9 -36" {arm}/>'
        else:
            b += f'<path d="M5 -52 L10 -34 M-5 -52 L-9 -34" {arm}/>'
    b += f'<circle cx="{hx}" cy="{hy}" r="7.5" fill="{skin}"/>'
    if hk == "cap":
        b += f'<path d="M{hx - 8} {hy - 3} Q{hx} {hy - 12} {hx + 8} {hy - 3} L{hx + 13} {hy - 1} L{hx + 8} {hy} Z" fill="{hat}"/>'
    elif hk == "beanie":
        b += f'<path d="M{hx - 8} {hy - 1} Q{hx - 8} {hy - 12} {hx} {hy - 12} Q{hx + 8} {hy - 12} {hx + 8} {hy - 1}Z" fill="{hat}"/><circle cx="{hx}" cy="{hy - 13}" r="3" fill="{hat}"/>'
    elif hk == "hard":
        b += f'<path d="M{hx - 9} {hy - 2} Q{hx - 8} {hy - 13} {hx} {hy - 13} Q{hx + 8} {hy - 13} {hx + 9} {hy - 2}Z" fill="#f2c230"/><rect x="{hx - 11}" y="{hy - 3}" width="22" height="3" rx="1" fill="#f2c230"/>'
    elif hk == "brim":
        b += f'<rect x="{hx - 12}" y="{hy - 5}" width="24" height="3" rx="1.5" fill="{hat}"/><path d="M{hx - 7} {hy - 4} L{hx - 6} {hy - 13} L{hx + 6} {hy - 13} L{hx + 7} {hy - 4}Z" fill="{hat}"/>'
    elif hk == "hair":
        b += f'<path d="M{hx - 8} {hy + 4} Q{hx - 10} {hy - 10} {hx} {hy - 9} Q{hx + 9} {hy - 9} {hx + 8} {hy - 2} Q{hx + 2} {hy - 6} {hx - 4} {hy - 4} L{hx - 4} {hy + 6}Z" fill="{hat}"/>'
    return g + b + '</g>'

def pickup(x, y, s, body, p, n=False, flip=False, cargo=None, driver=True):
    """a farm pickup, side on, facing right, wheels on y"""
    o = [f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">']
    a = o.append
    if cargo == "crates":
        for i, (cx, cy) in enumerate([(-48, -30), (-26, -30), (-37, -46)]):
            a(crate(cx, cy, 20, 14, p).replace(f'translate', 'translate'))
    elif cargo == "pumpkins":
        for cx in (-50, -34, -18): a(pumpkin(cx, -30, 7, p))
    elif cargo == "hay":
        a(haybale(-34, -30, 46, 16, p))
    a(f'<path d="M-62 -12 L-62 -32 L0 -32 L4 -56 Q6 -60 12 -60 L32 -60 Q36 -60 40 -54 L48 -36 L62 -34 Q66 -32 66 -26 L66 -12Z" fill="{body}"/>')
    a(f'<path d="M10 -54 L32 -54 L42 -36 L10 -36Z" fill="{"#ffd98a" if n else "#c6dbe4"}" opacity="{.75 if n else .9}"/>')
    if driver: a(f'<circle cx="22" cy="-44" r="5" fill="{p["skin"]}"/><path d="M16 -47 Q22 -54 28 -47Z" fill="#5a3a24"/>')
    a('<path d="M-62 -32 L0 -32" stroke="#000" stroke-opacity=".25" stroke-width="3"/><rect x="62" y="-24" width="6" height="8" rx="2" fill="#3a3a3a"/>')
    a(f'<rect x="60" y="-32" width="6" height="5" rx="1" fill="{"#fff6c8" if n else "#f2ead0"}"/>')
    for wx in (-38, 40): a(f'<circle cx="{wx}" cy="-10" r="12" fill="#1e1e1e"/><circle cx="{wx}" cy="-10" r="5" fill="#a0a0a0"/>')
    a('</g>')
    if n:  # the headlight's beam on the road ahead
        d = -1 if flip else 1
        o.insert(0, f'<path d="M{x + d * 66 * s:.0f} {y - 29 * s:.0f} L{x + d * 170 * s:.0f} {y - 44 * s:.0f} L{x + d * 170 * s:.0f} {y + 2 * s:.0f}Z" fill="#fff2b0" opacity=".22"/>')
    return ''.join(o)

def church(cx, b, p, n, s=1.0):
    """a white meeting house: nave with a gable, the tower in front, belfry and a tall spire"""
    o = [f'<g transform="translate({cx} {b}) scale({s})">']; a = o.append
    w, w2 = p["white"], p["white2"]
    a(f'<rect x="-64" y="-78" width="128" height="78" fill="{w}"/><path d="M-72 -76 L0 -118 L72 -76Z" fill="{p["roof"]}"/><path d="M0 -118 L72 -76 L40 -76Z" fill="{p["roof2"]}"/>')
    for wx in (-52, -32, 22, 42):
        if n: a(f'<circle cx="{wx + 5}" cy="-42" r="22" fill="url(#glow)"/>')
        a(f'<path d="M{wx} -18 L{wx} -54 Q{wx + 5} -62 {wx + 10} -54 L{wx + 10} -18Z" fill="{p["win"] if n else "#7d93a0"}"/>')
    # the tower
    a(f'<rect x="-17" y="-210" width="34" height="210" fill="{w}"/><rect x="-17" y="-210" width="8" height="210" fill="{w2}"/>')
    a(f'<path d="M-7 0 L-7 -30 Q0 -40 7 -30 L7 0Z" fill="{p["win"] if n else "#4a3a2c"}"/>')
    a(f'<circle cx="0" cy="-150" r="10" fill="#fbf6e6" stroke="#2a2a2a" stroke-width="1.6"/><path d="M0 -150 L0 -157 M0 -150 L5 -148" stroke="#2a2a2a" stroke-width="1.6"/>')
    a(f'<rect x="-21" y="-214" width="42" height="7" fill="{w2}"/>')
    a(f'<rect x="-14" y="-258" width="28" height="44" fill="{w}"/><path d="M-8 -216 L-8 -244 Q0 -254 8 -244 L8 -216Z" fill="{"#ffcf6a" if n else "#3a3a40"}"/>')
    for k in range(3): a(f'<line x1="-8" y1="{-238 + k * 8}" x2="8" y2="{-238 + k * 8}" stroke="{w2}" stroke-width="2"/>')
    a(f'<rect x="-17" y="-262" width="34" height="6" fill="{w2}"/>')
    a(f'<path d="M-12 -262 L0 -392 L12 -262Z" fill="{w}"/><path d="M0 -392 L12 -262 L4 -262Z" fill="{w2}"/>')
    a(f'<line x1="0" y1="-392" x2="0" y2="-408" stroke="#b8902a" stroke-width="2"/><path d="M-8 -404 L8 -404 L10 -406 L8 -402Z" fill="#b8902a"/>')
    if n: a('<circle cx="0" cy="-236" r="34" fill="url(#glow)" opacity=".8"/>')
    a('</g>')
    return ''.join(o)

def farmhouse(cx, b, p, n, s=1.0, chimney=True):
    """a white clapboard farmhouse and its red barn"""
    o = [f'<g transform="translate({cx} {b}) scale({s})">']; a = o.append
    # barn
    a(f'<path d="M30 0 L30 -54 L54 -78 L96 -78 L120 -54 L120 0Z" fill="{p["barn"]}"/><path d="M26 -52 L54 -82 L96 -82 L124 -52 L118 -50 L94 -76 L56 -76 L32 -50Z" fill="{p["roof"]}"/>')
    a(f'<rect x="58" y="-38" width="34" height="38" fill="{p["barn2"]}"/><path d="M58 -38 L92 0 M92 -38 L58 0" stroke="{p["white"]}" stroke-width="2.4"/><rect x="58" y="-38" width="34" height="38" fill="none" stroke="{p["white"]}" stroke-width="2.4"/>')
    a(f'<rect x="68" y="-66" width="14" height="12" fill="{p["win"] if n else p["barn2"]}" stroke="{p["white"]}" stroke-width="2"/>')
    # house
    a(f'<rect x="-70" y="-56" width="90" height="56" fill="{p["white"]}"/><path d="M-78 -54 L-25 -90 L28 -54Z" fill="{p["roof"]}"/>')
    if chimney: a(f'<rect x="-50" y="-92" width="12" height="26" fill="{p["barn2"]}"/>')
    for wx, wy in [(-60, -46), (-36, -46), (2, -46), (-60, -24), (2, -24)]:
        if n: a(f'<circle cx="{wx + 7}" cy="{wy + 8}" r="16" fill="url(#glow)"/>')
        a(f'<rect x="{wx}" y="{wy}" width="13" height="15" fill="{p["win"]}" stroke="{p["white2"]}" stroke-width="1.5"/>')
    a(f'<rect x="-34" y="-28" width="14" height="28" fill="{p["barn2"]}"/>')
    a('</g>')
    return ''.join(o)

def lightstring(x0, y0, x1, y1, sag, n, k=9, seed=1, twinkle=False):
    """a string of bulbs hung between two post tops"""
    mx, my = (x0 + x1) / 2, max(y0, y1) + sag
    o = [f'<path d="M{x0} {y0} Q{mx:.0f} {my + sag * .9:.0f} {x1} {y1}" fill="none" stroke="#2a2a2a" stroke-width="1.4"/>']
    for i in range(1, k):
        t = i / k; x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1; y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (my + sag * .9) + t * t * y1
        c = ["#ffd46a", "#ff9e5a", "#fff0b0"][i % 3]
        if n: o.append(f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="9" fill="{c}" opacity=".28"/>')
        o.append(f'<circle cx="{x:.0f}" cy="{y + 4:.0f}" r="2.6" fill="{c if n else "#f4ead0"}" stroke="#2a2a2a" stroke-width=".6"/>')
    return ''.join(o)

def post(x, b, h, p):
    return f'<rect x="{x - 2.5}" y="{b - h}" width="5" height="{h}" fill="{p["wood2"]}"/><rect x="{x - 4}" y="{b - h - 3}" width="8" height="4" fill="{p["wood"]}"/>'

def roadsign(x, b, text, p, w=150, fs=13, h=30, post_h=40):
    return (f'<rect x="{x - 3}" y="{b - post_h - h}" width="6" height="{post_h + h}" fill="{p["wood2"]}"/>'
            f'<rect x="{x - w / 2}" y="{b - post_h - h}" width="{w}" height="{h}" rx="3" fill="{p["wood"]}" stroke="{p["wood2"]}" stroke-width="2.5"/>'
            f'<text x="{x}" y="{b - post_h - h / 2 + fs * .36:.0f}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["ink"]}" letter-spacing="1">{text}</text>')

def geese(x, y, s, c, flapdur=1.0):
    """a skein of geese in a V, each wing beating"""
    o = []
    for i, (dx, dy) in enumerate([(0, 0), (-22, 10), (-44, 20), (-66, 30), (-22, -10), (-44, -20), (-66, -30)][:7]):
        gx, gy = x + dx * s, y + dy * s * .6
        w = lambda k: f"M{gx - 9 * s:.0f} {gy - 4 * s * k:.1f} Q{gx - 4 * s:.0f} {gy - 5 * s * k:.1f} {gx:.0f} {gy:.0f} Q{gx + 4 * s:.0f} {gy - 5 * s * k:.1f} {gx + 9 * s:.0f} {gy - 4 * s * k:.1f}"
        o.append(f'<path d="{w(1)}" fill="none" stroke="{c}" stroke-width="{2 * s:.1f}" stroke-linecap="round">'
                 f'<animate attributeName="d" values="{w(1)};{w(-.6)};{w(1)}" dur="{flapdur}s" begin="{i * .13:.2f}s" repeatCount="indefinite"/></path>'
                 f'<circle cx="{gx + 3 * s:.0f}" cy="{gy:.0f}" r="{1.8 * s:.1f}" fill="{c}"/>')
    return ''.join(o)

def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(240, body + SHADE)

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    HZ = 455   # the foot of the hillside, a little below the split, so the woods run on into the leaderboard
    LC = leafcols(p)
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(defs(skyg(p, "sky") +
           f'<linearGradient id="lawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["lawn"]}"/><stop offset="1" stop-color="{p["lawn2"]}"/></linearGradient>'
           f'<linearGradient id="wat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["water"]}"/><stop offset="1" stop-color="{"#3f7aa2" if not n else "#14284a"}"/></linearGradient>'))
    a(f'<rect width="{W}" height="{HZ + 20}" fill="url(#sky)"/>')
    if n:
        a(stars(60, 0, W, 0, 260, 3))
        a(moon(1210, 104, 44))
    else:
        a(sun(1240, 128, 30))
        for x, y, w in [(360, 96, 200), (760, 54, 160)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="9" fill="#fff4e0" opacity=".55"/><ellipse cx="{x + w * .14:.0f}" cy="{y - 7}" rx="{w * .28:.0f}" ry="8" fill="#fff4e0" opacity=".45"/>')
    # MOVES 1: geese in a V, flying west across the sky on a 12 s loop
    a(f'<g>{geese(930, 74, 1.1, "#3a3040" if not n else "#c9c2d8")}'
      '<animateTransform attributeName="transform" type="translate" values="260 10;-420 -18" dur="12s" repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" dur="12s" repeatCount="indefinite"/></g>')
    # the far ridge in haze, its crest wooded, and the near hillside in full colour
    a(hills([(0, 196), (190, 140), (430, 192), (650, 162), (880, 204), (1090, 156), (1320, 190), (1490, 136), (1600, 168)], HZ, p["far"]))
    a(hills([(0, 300), (300, 252), (620, 300), (900, 248), (1250, 292), (1600, 262)], HZ, p["hill"]))
    a(canopy(-10, 1610, 412, 16, 24, LC + [p["ever"]], 12, 28))
    # the farm on the hill, right, behind its own maples
    a(farmhouse(1330, HZ - 4, p, n, .9, chimney=False))
    # the meeting house on the hill above the green; its spire rises between the tiles
    a(church(640, HZ - 6, p, n))
    a(canopy(-10, 560, HZ + 6, 16, 26, LC + [p["ever"]], 21, 26))
    a(canopy(722, 1250, HZ + 6, 16, 26, LC + [p["ever"]], 22, 26))
    a(canopy(1460, 1610, HZ + 6, 16, 26, LC + [p["ever"]], 23, 26))
    # the meadow and the valley floor
    a(f'<rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="{p["grass"]}"/>')
    a(f'<path d="M0 {HZ + 2} L{W} {HZ + 2} L{W} {HZ + 14} Q800 {HZ + 4} 0 {HZ + 16}Z" fill="#000" opacity=".12"/>')
    # birches along the hill's foot, behind the road
    for i, (x, h) in enumerate([(150, 120), (470, 110), (512, 96), (900, 118), (1190, 104), (1236, 124), (1474, 100)]):
        a(f'<g>{birch(x, HZ + 4, h, [p["gold"], p["yel"], p["orange"]], 30 + i, p["birch"], "#3a3530" if not n else "#20202a", lean=(-6 if i % 2 else 5))}</g>')
    # the far stone wall along the road
    a(stonewall([(430, 478), (700, 472), (1000, 470), (1320, 474), (1610, 480)], 12, p, 5))
    a(stonewall([(-10, 486), (170, 482)], 12, p, 6))
    # the stream: down from the woods, under the bridge, widening toward us
    a(f'<path d="M300 {HZ} C292 470 300 490 312 512 L392 512 C372 490 352 470 336 {HZ}Z" fill="url(#wat)"/>')
    sd = "M296 520 C250 600 120 640 60 720 C30 760 10 800 -10 860 L380 860 C360 800 380 740 430 690 C470 640 430 570 410 520Z"
    a(f'<path d="{sd}" fill="{p["stone2"]}" transform="translate(0 -3) scale(1 1)" opacity=".7"/><path d="{sd}" fill="url(#wat)"/>')
    for x, y, rx in [(110, 690, 18), (380, 640, 14), (420, 760, 20), (40, 800, 16), (330, 580, 10)]:
        a(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .55:.0f}" fill="{p["stone"]}"/><ellipse cx="{x - 3}" cy="{y - 3}" rx="{rx * .6:.0f}" ry="{rx * .25:.0f}" fill="#fff" opacity=".15"/>')
    # MOVES 2: the stream running -- ripples slide downstream and fade
    for i, (x, y, w, dx, dy) in enumerate([(330, 560, 34, -40, 50), (220, 640, 44, -60, 50), (150, 720, 50, -50, 60), (300, 700, 40, -30, 60), (230, 800, 54, -40, 40)]):
        a(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{p["water2"] if not n else "#5f80b8"}" opacity=".8" transform="rotate(-18 {x} {y})">'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy}" dur="{4 + i * .7:.1f}s" repeatCount="indefinite" additive="sum"/>'
          f'<animate attributeName="opacity" values="0;.85;.85;0" keyTimes="0;.2;.7;1" dur="{4 + i * .7:.1f}s" repeatCount="indefinite"/></rect>')
    # the country road: in from the left, through the covered bridge, along the valley and out to the right
    road = "M-20 500 L180 500 L410 500 C470 498 520 490 600 488 C800 484 1000 484 1200 490 C1350 494 1480 500 1620 504"
    a(f'<path d="{road}" fill="none" stroke="{p["road2"]}" stroke-width="30"/><path d="{road}" fill="none" stroke="{p["road"]}" stroke-width="24"/>')
    # the lane down to the green, and the pull-off at the farm stand
    a(f'<path d="M1230 500 C1240 560 1250 620 1260 668 L1430 668 C1400 610 1350 560 1330 500Z" fill="{p["road"]}" opacity=".85"/>')
    # MOVES 3: a pickup with a load of pumpkins drives in, through the bridge, and away along the valley
    a(f'<g opacity="0">{pickup(0, 504, .42, "#2f5a7a" if not n else "#26405a", p, n, cargo="pumpkins")}'
      '<animateTransform attributeName="transform" type="translate" values="-90 0;1720 -14" dur="12s" repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.96;1" dur="12s" repeatCount="indefinite"/></g>')
    # the red covered bridge, drawn over the road so the truck passes inside it
    bx0, bx1, by = 170, 412, 502
    a(f'<path d="M{bx0 - 10} {by + 4} L{bx0 + 16} {by + 4} L{bx0 + 24} {by + 44} L{bx0 - 22} {by + 44}Z" fill="{p["stone"]}"/>'
      f'<path d="M{bx1 - 16} {by + 4} L{bx1 + 10} {by + 4} L{bx1 + 22} {by + 44} L{bx1 - 24} {by + 44}Z" fill="{p["stone"]}"/>')
    a(f'<rect x="{bx0}" y="{by - 46}" width="{bx1 - bx0}" height="52" fill="{p["barn"]}"/>')
    a(f'<path d="{"".join(f"M{x} {by - 46}v52" for x in range(bx0 + 8, bx1, 12))}" stroke="{p["barn2"]}" stroke-width="2"/>')
    a(f'<rect x="{bx0 + 20}" y="{by - 34}" width="{bx1 - bx0 - 40}" height="9" fill="{p["barn2"] if not n else "#ffcf6a"}" opacity="{1 if not n else .55}"/>')
    a(f'<path d="M{bx0 - 14} {by - 44} L{bx0 + 6} {by - 64} L{bx1 - 6} {by - 64} L{bx1 + 14} {by - 44}Z" fill="{p["roof"]}"/><path d="M{bx0 - 14} {by - 44} L{bx1 + 14} {by - 44}" stroke="{p["roof2"]}" stroke-width="3"/>')
    a(f'<path d="M{bx0 - 2} {by + 6} L{bx0 - 2} {by - 40} L{bx0 + 8} {by - 56} L{bx0 + 18} {by - 40} L{bx0 + 18} {by + 6}Z" fill="{p["barn2"]}"/><path d="M{bx0 + 1} {by + 6} L{bx0 + 1} {by - 30} Q{bx0 + 8} {by - 40} {bx0 + 15} {by - 30} L{bx0 + 15} {by + 6}Z" fill="#1a1210"/>')
    a(f'<rect x="{bx0 + 66}" y="{by - 60}" width="110" height="14" rx="2" fill="{p["white"]}"/><text x="{bx0 + 121}" y="{by - 49}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="10" fill="{p["barn2"] if not n else "#2a1a18"}" letter-spacing="1">COVERED BRIDGE</text>')
    a(f'<rect x="{bx0 - 4}" y="{by + 4}" width="{bx1 - bx0 + 8}" height="6" fill="{p["wood2"]}"/>')
    # the near stone wall up to the bridge, and the lane's sign
    a(stonewall([(-10, 530), (150, 528)], 13, p, 7))
    a(roadsign(120, 516, "NO LAPSE LANE", p, 104, 10, 22, 30))
    # the village green: the podium's lawn, a few leaves already down on it
    gp = "M440 600 C430 548 560 528 800 528 C1040 528 1180 546 1172 610 C1166 700 1120 800 1100 880 L480 880 C470 800 446 690 440 600Z"
    a(f'<path d="{gp}" fill="{p["lawn2"]}" stroke="{p["lawn2"]}" stroke-width="18" stroke-linejoin="round"/><path d="{gp}" fill="url(#lawn)"/>')
    a(f'<ellipse cx="760" cy="580" rx="260" ry="26" fill="#fff" opacity="{.08 if not n else .03}"/>')
    r = random.Random(17)
    for _ in range(22):
        x = r.randint(470, 1150); y = r.randint(540, 840)
        a(leaf(x, y, .8, r.choice(LC), r.randint(0, 360)))
    # the posts along the road's edge with lights strung between them, kept above the podium
    for x0, x1 in [(470, 800), (800, 1140)]:
        a(lightstring(x0, 466, x1, 466, 14, n, 10, x0))
    for x in (470, 800, 1140): a(post(x, 534, 68, p))
    # the farm stand, right: a red shed with a stovepipe, its sign, crates, pumpkins and hay
    fx, fb = 1335, 668
    a(f'<ellipse cx="{fx}" cy="{fb + 4}" rx="140" ry="10" fill="#000" opacity=".14"/>')
    a(f'<rect x="{fx - 96}" y="{fb - 90}" width="192" height="90" fill="{p["barn"]}"/>')
    a(f'<path d="{"".join(f"M{x} {fb - 90}v90" for x in range(fx - 90, fx + 96, 12))}" stroke="{p["barn2"]}" stroke-width="1.6"/>')
    a(f'<rect x="{fx - 80}" y="{fb - 76}" width="160" height="40" fill="{"#2a1a12" if not n else "#3a2414"}"/>')
    if n: a(f'<circle cx="{fx}" cy="{fb - 58}" r="70" fill="url(#glow)"/>')
    a(f'<path d="M{fx - 112} {fb - 86} L{fx - 70} {fb - 120} L{fx + 70} {fb - 120} L{fx + 112} {fb - 86}Z" fill="{p["roof"]}"/>')
    a(f'<rect x="{fx + 48}" y="{fb - 150}" width="9" height="34" fill="#2a2a2a"/><rect x="{fx + 45}" y="{fb - 153}" width="15" height="5" fill="#2a2a2a"/>')
    a(f'<rect x="{fx - 100}" y="{fb - 118}" width="200" height="22" rx="3" fill="{p["white"]}"/><text x="{fx}" y="{fb - 103}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="11.5" fill="{p["barn2"] if not n else "#2a1a18"}" letter-spacing=".5">HARVEST HOME COVERAGE</text>')
    # a lantern hung from the eave on a hook
    a(f'<line x1="{fx - 60}" y1="{fb - 86}" x2="{fx - 60}" y2="{fb - 74}" stroke="#2a2a2a" stroke-width="1.5"/><rect x="{fx - 65}" y="{fb - 74}" width="10" height="14" rx="2" fill="{"#ffd46a" if n else "#e8d8a8"}" stroke="#2a2a2a" stroke-width="1.5"/>')
    # the farmer behind the counter, the front wall hiding her legs
    a(person(fx - 52, fb - 4, .62, "wave", "#5a6a3a", "#3a3530", "#7a3a1e", p["skin"], hk="hair"))
    a(f'<rect x="{fx - 96}" y="{fb - 36}" width="192" height="36" fill="{p["barn"]}"/>')
    a(f'<path d="{"".join(f"M{x} {fb - 36}v36" for x in range(fx - 90, fx + 96, 12))}" stroke="{p["barn2"]}" stroke-width="1.6"/>')
    a(f'<rect x="{fx - 90}" y="{fb - 36}" width="180" height="8" fill="{p["wood"]}"/>')
    for i, cx in enumerate((fx - 70, fx - 40, fx - 10, fx + 20, fx + 50)):
        a(crate(cx, fb - 36, 26, 14, p, [p["red"], "#d8a52a", p["red2"], "#7aa040", p["red"]][i] if not n else p["red"]))
    a(f'<rect x="{fx - 20}" y="{fb - 28}" width="74" height="26" rx="2" fill="#1e2a22" stroke="{p["wood"]}" stroke-width="3"/><text x="{fx + 17}" y="{fb - 18}" text-anchor="middle" font-family="Georgia, serif" font-size="8" fill="#f6efe0">FALL INTO</text><text x="{fx + 17}" y="{fb - 8}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="8.5" fill="#f6efe0">SAVINGS</text>')
    for x, y, rr in [(fx - 96, fb + 10, 10), (fx - 72, fb + 14, 8), (fx - 110, fb + 20, 12), (fx + 100, fb + 12, 9), (fx + 80, fb + 18, 11), (fx - 50, fb + 20, 7)]:
        a(pumpkin(x, y, rr, p))
    a(haybale(1196, fb + 30, 52, 24, p) + haybale(1236, fb + 34, 52, 24, p) + haybale(1214, fb + 6, 52, 24, p))
    # MOVES 4: smoke from the stand's stovepipe
    for i in range(3):
        a(f'<circle cx="{fx + 52}" cy="{fb - 160}" r="7" fill="{"#efe6dc" if not n else "#8a8a9a"}" opacity="0">'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;{-14 - i * 4} -70" dur="6s" begin="{i * 2}s" repeatCount="indefinite"/>'
          f'<animate attributeName="r" values="6;18" dur="6s" begin="{i * 2}s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0;.55;0" dur="6s" begin="{i * 2}s" repeatCount="indefinite"/></circle>')
    a(f'<circle cx="{fx + 50}" cy="{fb - 166}" r="8" fill="{"#efe6dc" if not n else "#8a8a9a"}" opacity=".35"/>')
    # the big maples framing both edges, in the wind
    a(f'<g>{maple(40, 600, 560, [p["red2"], p["red"], p["orange"], p["red"], p["gold"]], 41, p["trunk"], 1.05)}{sway(40, 600, .6, 7)}</g>')
    a(f'<g>{maple(1548, 590, 540, [p["orange"], p["gold"], p["red"], p["yel"], p["orange"]], 42, p["trunk"], 1.05)}{sway(1548, 590, .6, 8, 1.2)}</g>')
    # the scarecrow in his corn shocks, right, scarf in the wind
    sx, sb = 1500, 760
    for cx in (1446, 1556):
        a(f'<path d="M{cx - 22} {sb} L{cx} {sb - 70} L{cx + 22} {sb}Z" fill="{p["hay2"]}"/><path d="M{cx - 12} {sb} L{cx} {sb - 70} L{cx + 8} {sb}Z" fill="{p["hay"]}"/><path d="M{cx - 14} {sb - 30} L{cx + 14} {sb - 30}" stroke="{p["wood2"]}" stroke-width="3"/>')
    a(f'<rect x="{sx - 3}" y="{sb - 110}" width="6" height="110" fill="{p["wood2"]}"/><rect x="{sx - 40}" y="{sb - 84}" width="80" height="5" fill="{p["wood2"]}"/>')
    a(f'<path d="M{sx - 20} {sb - 88} L{sx + 20} {sb - 88} L{sx + 16} {sb - 46} L{sx - 16} {sb - 46}Z" fill="#7a4a8a"/><path d="M{sx - 20} {sb - 86} L{sx - 42} {sb - 80} L{sx - 40} {sb - 74} L{sx - 18} {sb - 76}Z M{sx + 20} {sb - 86} L{sx + 42} {sb - 80} L{sx + 40} {sb - 74} L{sx + 18} {sb - 76}Z" fill="#7a4a8a"/>')
    a(f'<path d="M{sx - 44} {sb - 80} l-8 -4 M{sx - 44} {sb - 78} l-9 2 M{sx + 44} {sb - 80} l8 -4 M{sx + 44} {sb - 78} l9 2" stroke="{p["hay"]}" stroke-width="2.4"/>')
    a(f'<path d="M{sx - 14} {sb - 46} L{sx - 18} {sb - 20} L{sx - 6} {sb - 20} L{sx} {sb - 40} L{sx + 6} {sb - 20} L{sx + 18} {sb - 20} L{sx + 14} {sb - 46}Z" fill="#3a5a8a"/>')
    a(f'<circle cx="{sx}" cy="{sb - 100}" r="13" fill="{p["hay"]}"/><path d="M{sx - 6} {sb - 102} l3 3 M{sx - 3} {sb - 102} l-3 3 M{sx + 3} {sb - 102} l3 3 M{sx + 6} {sb - 102} l-3 3" stroke="#3a2a1e" stroke-width="1.6"/>')
    a(f'<path d="M{sx - 24} {sb - 110} L{sx + 24} {sb - 110} L{sx + 12} {sb - 112} L{sx + 8} {sb - 130} L{sx - 8} {sb - 130} L{sx - 12} {sb - 112}Z" fill="#6a4a2a"/>')
    a(f'<rect x="{sx - 12}" y="{sb - 90}" width="24" height="6" rx="2" fill="#c8361f"/>')
    sc0 = f"M{sx + 8} {sb - 88} Q{sx + 22} {sb - 86} {sx + 34} {sb - 92} L{sx + 36} {sb - 84} Q{sx + 22} {sb - 80} {sx + 6} {sb - 82}Z"
    sc1 = f"M{sx + 8} {sb - 88} Q{sx + 22} {sb - 96} {sx + 36} {sb - 94} L{sx + 34} {sb - 86} Q{sx + 22} {sb - 88} {sx + 6} {sb - 82}Z"
    # MOVES 5: the scarf flapping
    a(f'<path d="{sc0}" fill="#c8361f"><animate attributeName="d" values="{sc0};{sc1};{sc0}" dur="3s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path>')
    # MOVES 6: leaves coming down off the maples (and a few drifting through the sky), each on its own loop
    for i, (x, y, dx, dy, dur, c) in enumerate([(150, 280, 90, 300, 9, p["red"]), (40, 360, 120, 250, 8, p["orange"]), (230, 330, 60, 330, 11, p["gold"]),
                                               (1500, 300, -110, 320, 10, p["gold"]), (1400, 380, -90, 260, 8.5, p["orange"]), (1580, 420, -70, 240, 9.5, p["red"]),
                                               (470, 40, 120, 120, 9, p["red"]), (1020, 30, -80, 130, 10.5, p["orange"])]):
        mp = f"M0 0 C{dx * .5 + 30:.0f} {dy * .2:.0f} {dx * .3 - 30:.0f} {dy * .5:.0f} {dx * .7:.0f} {dy * .7:.0f} S{dx + 20:.0f} {dy * .9:.0f} {dx} {dy}"
        a(f'<g transform="translate({x} {y})" opacity="0"><g>{leaf(0, 0, 1.3, c)}'
          f'<animateTransform attributeName="transform" type="rotate" values="0;200;360" dur="{dur / 2:.1f}s" repeatCount="indefinite"/></g>'
          f'<animateMotion path="{mp}" dur="{dur}s" begin="{i * .9:.1f}s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="{dur}s" begin="{i * .9:.1f}s" repeatCount="indefinite"/></g>')
    # a few tufts and leaves on the meadow, kept off the green
    r = random.Random(11)
    for _ in range(26):
        x = r.randint(0, W); y = r.randint(540, 860)
        if 420 < x < 1190: continue
        if x < 440 and y < 860 and 520 < y: continue
        a(leaf(x, y, .9, r.choice(LC), r.randint(0, 360)))
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def base(n, p, star=40, extra=''):
    return defs(skyg(p) + extra) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(min(star, 36), 0, 1600, 0, 130, 7) if n else '')

def valley(p, y, seed, far=True):
    """the far ridge and a wooded hillside in colour behind the subject"""
    o = []
    if far: o.append(hills([(0, y - 50), (260, y - 82), (560, y - 46), (860, y - 76), (1160, y - 44), (1420, y - 80), (1600, y - 56)], y + 10, p["far"]))
    o.append(canopy(-10, 1610, y, 14, 24, leafcols(p) + [p["ever"]], seed, 25, base=p["hill"]))
    return ''.join(o)

def ground(p, y, c=None):
    return f'<path d="M0 {y} Q400 {y - 8} 800 {y} T1600 {y - 4} L1600 240 L0 240Z" fill="{c or p["grass"]}"/>'

def corners(p, n):
    """darker ground under the corners the title and the line sit on"""
    c = "#4a2616" if not n else "#0e0a0a"
    return (f'<path d="M0 172 Q220 160 470 190 L470 240 L0 240Z" fill="{c}"/>'
            f'<path d="M1600 178 Q1330 168 1040 198 L1040 240 L1600 240Z" fill="{c}"/>')

def edge_trees(p, left=True, right=True):
    o = []
    if left: o.append(maple(120, 200, 230, [p["red2"], p["red"], p["orange"], p["red"], p["gold"]], 51, p["trunk"]) + birch(260, 200, 170, [p["gold"], p["yel"]], 52, p["birch"]))
    if right: o.append(birch(1340, 200, 160, [p["yel"], p["gold"]], 53, p["birch"]) + maple(1480, 200, 240, [p["orange"], p["gold"], p["red"], p["yel"], p["orange"]], 54, p["trunk"]))
    return ''.join(o)

def skyobj(n, x, y):
    return moon(x, y, 22) if n else sun(x, y, 22)

def appletree(x, b, h, p, seed, n=False, fruit=12):
    r = random.Random(seed); R = h * .36
    g1, g2, g3 = ("#5e7a34", "#6f8c3c", "#93a446") if not n else ("#1c2a1a", "#22321e", "#2e3a22")
    o = [f'<path d="M{x - h * .05:.0f} {b} L{x - h * .03:.0f} {b - h * .45:.0f} L{x + h * .03:.0f} {b - h * .45:.0f} L{x + h * .05:.0f} {b}Z" fill="{p["trunk"]}"/>',
         f'<ellipse cx="{x}" cy="{b - h * .62:.0f}" rx="{R * 1.3:.0f}" ry="{R:.0f}" fill="{g1}"/>']
    o.append(blobs([(x + r.uniform(-.8, .8) * R, b - h * .62 + r.uniform(-.6, .3) * R, R * r.uniform(.4, .55), g2 if k % 2 else g3) for k in range(5)]))
    o.append(blobs([(x + r.uniform(-1.1, 1.1) * R, b - h * .62 + r.uniform(-.7, .75) * R, max(2, h * .035), p["red"] if k % 4 else "#e8b63a") for k in range(fruit)]))
    return ''.join(o)

def ladder(x0, y0, x1, y1, c, rungs=6, w=10):
    o = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{c}" stroke-width="3"/><line x1="{x0 + w}" y1="{y0}" x2="{x1 + w}" y2="{y1}" stroke="{c}" stroke-width="3"/>']
    for k in range(1, rungs):
        t = k / rungs; xa = x0 + (x1 - x0) * t; ya = y0 + (y1 - y0) * t
        o.append(f'<line x1="{xa:.0f}" y1="{ya:.0f}" x2="{xa + w:.0f}" y2="{ya:.0f}" stroke="{c}" stroke-width="2.4"/>')
    return ''.join(o)

def basket(x, y, r, p, fruit=None):
    """a bushel basket heaped with apples"""
    fruit = fruit or p["red"]
    o = []
    for k, (dx, dy) in enumerate([(-.6, -.1), (-.2, -.25), (.2, -.22), (.6, -.08), (-.38, -.42), (.05, -.48), (.42, -.38)]):
        o.append(f'<circle cx="{x + dx * r:.1f}" cy="{y - r * 1.05 + dy * r:.1f}" r="{r * .3:.1f}" fill="{fruit if k % 3 else "#e8a63a"}"/>')
    o.append(f'<path d="M{x - r} {y - r * 1.1:.1f} L{x + r} {y - r * 1.1:.1f} L{x + r * .78:.1f} {y} L{x - r * .78:.1f} {y}Z" fill="#c49254"/>')
    for k in (1, 2): o.append(f'<line x1="{x - r * (1 - .08 * k):.1f}" y1="{y - r * 1.1 + r * .36 * k:.1f}" x2="{x + r * (1 - .08 * k):.1f}" y2="{y - r * 1.1 + r * .36 * k:.1f}" stroke="#8a6030" stroke-width="{max(1, r * .1):.1f}"/>')
    o.append(f'<rect x="{x - r * 1.04:.1f}" y="{y - r * 1.16:.1f}" width="{r * 2.08:.1f}" height="{r * .16:.1f}" rx="1" fill="#9a6a34"/>')
    return ''.join(o)

def v_sales(n):  # the apple harvest: pickers on ladders, crates going onto the truck
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 1150, 58))
    o.append(valley(p, 128, 61))
    o.append(ground(p, 150, "#8e9a44" if not n else p["grass"]))
    for i, x in enumerate((470, 1140)):
        o.append(appletree(x, 190, 150, p, 62 + i, n, 16))
    o.append(ladder(1112, 196, 1150, 96, p["wood2"] if not n else "#5a4030"))
    o.append(person(1146, 150, .95, "reach", "#2f5a8a", "#3a3a44", "#c8361f", p["skin"], flip=True))
    o.append(basket(1180, 204, 16, p))
    # the truck, tailgate down, crates stacked high in its bed
    tx, ty = 820, 210
    o.append(f'<ellipse cx="{tx}" cy="{ty + 2}" rx="110" ry="7" fill="#000" opacity=".18"/>')
    o.append(pickup(tx, ty, 1.5, "#2f5a7a" if not n else "#22384e", p, n, driver=False))
    for row in range(3):
        for k in range(3 - (row == 2)):
            o.append(crate(tx - 76 + k * 30 + row * 14, ty - 48 - row * 22, 28, 20, p))
    for k, (cx, cy) in enumerate([(640, 212), (672, 212), (656, 190)]):
        o.append(crate(cx, cy, 30, 21, p))
    o.append(person(720, 212, 1.0, "carry", "#7a3a1e", "#3a3a44", "#2f5a3a", p["skin"]))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def mailbox(x, y, w, h, c, p, flag=False, letter=False):
    o = [f'<path d="M{x} {y} L{x} {y - h * .6:.1f} Q{x} {y - h} {x + h * .4:.1f} {y - h} L{x + w - h * .4:.1f} {y - h} Q{x + w} {y - h} {x + w} {y - h * .6:.1f} L{x + w} {y}Z" fill="{c}"/>',
         f'<path d="M{x} {y} L{x} {y - h * .6:.1f} Q{x} {y - h} {x + h * .4:.1f} {y - h} L{x + h * .4:.1f} {y}Z" fill="#000" opacity=".22"/>']
    if letter: o.append(f'<path d="M{x - 6} {y - h * .55:.1f} L{x + 10} {y - h * .62:.1f} L{x + 12} {y - h * .3:.1f} L{x - 4} {y - h * .24:.1f}Z" fill="#fbf6ea" stroke="#c8b89a" stroke-width="1"/>')
    if flag: o.append(f'<rect x="{x + w - 10}" y="{y - h - 14}" width="3" height="20" fill="#c8361f"/><rect x="{x + w - 10}" y="{y - h - 14}" width="12" height="7" fill="#c8361f"/>')
    else: o.append(f'<rect x="{x + w - 22}" y="{y - h * .55:.1f}" width="20" height="3" fill="#c8361f"/>')
    return ''.join(o)

def v_messages(n):  # the mailbox row at the end of the lane
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 1260, 56))
    o.append(valley(p, 130, 71))
    o.append(ground(p, 150))
    o.append(farmhouse(1010, 152, p, n, .55))
    o.append(stonewall([(300, 168), (700, 164), (1100, 166), (1400, 170)], 11, p, 72))
    o.append(f'<path d="M0 214 Q800 196 1600 212 L1600 240 L0 240Z" fill="{p["road"]}"/><path d="M0 214 Q800 196 1600 212" fill="none" stroke="{p["road2"]}" stroke-width="3"/>')
    # one long plank on its posts, five mailboxes along it
    o.append(f'<rect x="540" y="146" width="460" height="9" fill="{p["wood"]}"/>')
    for x in (570, 970): o.append(f'<rect x="{x - 5}" y="146" width="10" height="58" fill="{p["wood2"]}"/>')
    cols = ["#3a4a5a", "#c8361f", "#2f5a3a", "#d9d2c0", "#7a4a2a"] if not n else ["#2a323e", "#5a221e", "#1e3424", "#6e6c66", "#3e2a1e"]
    for i, c in enumerate(cols):
        o.append(mailbox(560 + i * 88, 146, 64, 34, c, p, flag=i in (1, 3), letter=i == 2))
    o.append(person(800, 206, 1.05, "mail", "#5a6a3a", "#3a3530", "#7a3a1e", p["skin"], flip=True, hk="hair"))
    o.append(f'<rect x="700" y="182" width="22" height="18" rx="2" fill="#c8a46a" transform="rotate(-8 711 191)"/>')
    for x, y, c, rt in [(640, 222, p["red"], 20), (900, 226, p["gold"], 80), (1060, 218, p["orange"], 140)]: o.append(leaf(x, y, 1.2, c, rt))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def fire(x, y, s, n):
    o = []
    o.append(f'<circle cx="{x}" cy="{y - 14 * s:.0f}" r="{90 * s:.0f}" fill="url(#glow)" opacity="{1 if n else .7}"/>')
    o.append(f'<path d="M{x - 30 * s:.0f} {y} L{x + 26 * s:.0f} {y - 8 * s:.0f} M{x + 30 * s:.0f} {y} L{x - 26 * s:.0f} {y - 8 * s:.0f}" stroke="#5a3a24" stroke-width="{7 * s:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M{x - 20 * s:.0f} {y - 6 * s:.0f} Q{x - 24 * s:.0f} {y - 30 * s:.0f} {x - 8 * s:.0f} {y - 44 * s:.0f} Q{x - 10 * s:.0f} {y - 28 * s:.0f} {x} {y - 26 * s:.0f} Q{x + 2 * s:.0f} {y - 50 * s:.0f} {x + 12 * s:.0f} {y - 62 * s:.0f} Q{x + 10 * s:.0f} {y - 40 * s:.0f} {x + 20 * s:.0f} {y - 30 * s:.0f} Q{x + 26 * s:.0f} {y - 16 * s:.0f} {x + 20 * s:.0f} {y - 6 * s:.0f}Z" fill="#f08a2a"/>')
    o.append(f'<path d="M{x - 10 * s:.0f} {y - 6 * s:.0f} Q{x - 12 * s:.0f} {y - 22 * s:.0f} {x - 2 * s:.0f} {y - 30 * s:.0f} Q{x} {y - 20 * s:.0f} {x + 5 * s:.0f} {y - 40 * s:.0f} Q{x + 14 * s:.0f} {y - 22 * s:.0f} {x + 10 * s:.0f} {y - 6 * s:.0f}Z" fill="#ffd25a"/>')
    for k, (dx, dy) in enumerate([(-14, -74), (8, -86), (20, -66), (-4, -98)]):
        o.append(f'<circle cx="{x + dx * s:.0f}" cy="{y + dy * s:.0f}" r="{1.6 * s:.1f}" fill="#ffd25a" opacity=".85"/>')
    return ''.join(o)

def v_coaching(n):  # the campfire circle: logs round the fire, everyone talking it over
    p = P(n); sp = dict(p); sp["sky"] = ("#3a4a7a", "#d8804a", "#f2b070") if not n else p["sky"]
    o = [base(n, sp, 60)]
    o.append(skyobj(n, 1240, 52) if n else '')
    o.append(valley(p, 120, 81))
    o.append(ground(p, 140, "#6a6a34" if not n else "#151d14"))
    for x in range(380, 1260, 46): o.append(pine(x, 150, 60 + (x * 7) % 30, p["ever"] if not n else "#0e1814"))
    o.append(f'<ellipse cx="800" cy="204" rx="330" ry="30" fill="#000" opacity=".16"/>')
    o.append(fire(800, 200, 1.0, n))
    # four on the logs, two each side, facing the fire
    for x, flip, coat, hat, hk in [(600, False, "#2f5a8a", "#c8361f", "beanie"), (680, False, "#7a3a1e", "#3a2a1e", "hair"),
                                    (920, True, "#5a6a3a", "#e8a63a", "cap"), (1000, True, "#8a3a5a", "#2a2a2a", "hair")]:
        o.append(person(x, 212, 1.0, "sit", coat, "#3a3a44", hat, p["skin"], flip=flip, hk=hk))
    for x0, x1 in [(560, 720), (880, 1040)]:
        o.append(f'<rect x="{x0}" y="194" width="{x1 - x0}" height="16" rx="8" fill="#6a4426"/><ellipse cx="{x0 + 4}" cy="202" rx="5" ry="8" fill="#a8784a"/>')
    o.append(f'<path d="M800 120 q-20 -30 6 -56 q24 -26 -4 -58" fill="none" stroke="#e8e0d8" stroke-width="10" stroke-linecap="round" opacity="{.18 if not n else .1}"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def tractor(x, y, s, p, n):
    """a red farm tractor, facing right, wheels on y"""
    o = [f'<g transform="translate({x} {y}) scale({s})">']
    o.append('<rect x="-30" y="-46" width="70" height="26" rx="4" fill="#b2302a"/><rect x="18" y="-40" width="30" height="20" rx="3" fill="#c8402a"/>')
    o.append('<rect x="30" y="-62" width="4" height="22" fill="#2a2a2a"/><path d="M-26 -46 L-22 -78 L4 -78 L8 -46" fill="none" stroke="#2a2a2a" stroke-width="3"/><rect x="-28" y="-82" width="38" height="6" rx="2" fill="#2a2a2a"/>')
    o.append(f'<circle cx="-6" cy="-58" r="6" fill="{p["skin"]}"/><path d="M-12 -61 Q-6 -68 0 -61 L4 -60 Z" fill="#2f5a3a"/><path d="M-12 -52 L0 -52 L0 -40 L-12 -40Z" fill="#2f5a8a"/>')
    o.append('<circle cx="-14" cy="-20" r="20" fill="#1e1e1e"/><circle cx="-14" cy="-20" r="9" fill="#e8b63a"/><circle cx="38" cy="-11" r="11" fill="#1e1e1e"/><circle cx="38" cy="-11" r="5" fill="#e8b63a"/>')
    o.append('<line x1="-34" y1="-24" x2="-60" y2="-22" stroke="#2a2a2a" stroke-width="3"/>')
    if n: o.append('<circle cx="48" cy="-34" r="4" fill="#fff6c8"/>')
    o.append('</g>')
    return ''.join(o)

def v_roleplay(n):  # the hayride: a tractor pulling a wagon of bales and riders down the farm lane
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 1220, 56))
    o.append(valley(p, 126, 91))
    o.append(ground(p, 146))
    # the cornfield behind the lane, shocks standing in it
    for x in range(380, 1300, 70):
        o.append(f'<path d="M{x - 14} 176 L{x} 136 L{x + 14} 176Z" fill="{p["hay2"]}"/><path d="M{x - 6} 176 L{x} 136 L{x + 5} 176Z" fill="{p["hay"]}"/>')
    o.append(f'<path d="M0 206 Q800 186 1600 204 L1600 228 Q800 212 0 230Z" fill="{p["road"]}"/>')
    # the wagon: a flat bed on four wheels, bales along it, riders sitting on the bales
    wx = 650
    o.append(f'<rect x="{wx - 150}" y="184" width="300" height="12" fill="{p["wood"]}"/><rect x="{wx - 150}" y="164" width="6" height="22" fill="{p["wood2"]}"/><rect x="{wx + 144}" y="164" width="6" height="22" fill="{p["wood2"]}"/>')
    for k in range(4): o.append(haybale(wx - 112 + k * 74, 184, 70, 24, p))
    for k, (coat, hat, hk) in enumerate([("#c8361f", "#2a2a2a", "hair"), ("#2f5a8a", "#e8a63a", "beanie"), ("#5a6a3a", "#3a2a1e", "cap"), ("#8a3a5a", "#5a3a24", "hair")]):
        o.append(person(wx - 120 + k * 76, 178, .82, "sit", coat, "#3a3a44", hat, p["skin"], hk=hk))
    for x in (wx - 110, wx + 110): o.append(f'<circle cx="{x}" cy="204" r="13" fill="#1e1e1e"/><circle cx="{x}" cy="204" r="5" fill="{p["wood"]}"/>')
    o.append(f'<line x1="{wx + 150}" y1="192" x2="{wx + 196}" y2="194" stroke="#2a2a2a" stroke-width="4"/>')
    o.append(tractor(wx + 254, 216, 1.15, p, n))
    for x, y in [(450, 214), (1100, 218), (520, 226)]: o.append(pumpkin(x, y, 9, p))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def truck_rear(x, y, s, body, p, n, riders=()):
    """a pickup seen from behind, people sitting in the bed"""
    o = [f'<g transform="translate({x} {y}) scale({s})">']
    for k, (coat, hat) in enumerate(riders):
        dx = -16 + k * 32
        o.append(f'<rect x="{dx - 9}" y="-62" width="18" height="24" rx="5" fill="{coat}"/><circle cx="{dx}" cy="-68" r="7" fill="{"#2a1a12" if n else "#6a4a2a"}"/><path d="M{dx - 7} -70 Q{dx} -80 {dx + 7} -70Z" fill="{hat}"/>')
    o.append(f'<rect x="-30" y="-74" width="60" height="22" rx="5" fill="{body}"/><rect x="-24" y="-70" width="48" height="12" rx="3" fill="#1a1a1a" opacity=".6"/>')
    o.append(f'<rect x="-44" y="-50" width="88" height="34" rx="3" fill="{body}"/><rect x="-44" y="-50" width="88" height="5" fill="#000" opacity=".2"/>')
    o.append(f'<rect x="-40" y="-40" width="8" height="10" rx="2" fill="{"#ff5040" if n else "#c8302a"}"/><rect x="32" y="-40" width="8" height="10" rx="2" fill="{"#ff5040" if n else "#c8302a"}"/>')
    o.append('<rect x="-46" y="-18" width="92" height="6" rx="2" fill="#5a5a5a"/><rect x="-40" y="-14" width="16" height="14" rx="3" fill="#1e1e1e"/><rect x="24" y="-14" width="16" height="14" rx="3" fill="#1e1e1e"/>')
    if n: o.append('<circle cx="-36" cy="-35" r="14" fill="#ff5040" opacity=".22"/><circle cx="36" cy="-35" r="14" fill="#ff5040" opacity=".22"/>')
    o.append('</g>')
    return ''.join(o)

def v_rphistory(n):  # the drive-in at the pumpkin patch: the screen up on its frame, trucks backed in
    p = P(n); sp = dict(p); sp["sky"] = ("#2a3a6a", "#b86a5a", "#e8a070") if not n else p["sky"]
    o = [base(n, sp, 60)]
    o.append(valley(p, 132, 101))
    o.append(ground(p, 150, "#6e6a36" if not n else "#161d14"))
    # the screen on its timber frame
    o.append(f'<rect x="604" y="40" width="392" height="10" fill="{p["wood"]}"/>')
    for x in (620, 800, 980): o.append(f'<rect x="{x - 6}" y="44" width="12" height="130" fill="{p["wood2"]}"/>')
    o.append(f'<path d="M620 174 L590 174 L620 120Z M980 174 L1010 174 L980 120Z" fill="{p["wood2"]}"/>')
    scr = "#f4ecd8" if not n else "#cfe2f2"
    if n: o.append('<rect x="580" y="30" width="440" height="150" rx="20" fill="#cfe2f2" opacity=".12"/>')
    o.append(f'<rect x="630" y="52" width="340" height="104" fill="{scr}"/>')
    # on the screen: a hillside of maples and a big harvest moon, and the play mark
    o.append('<path d="M630 132 Q720 104 800 124 T970 116 L970 156 L630 156Z" fill="#c8602a" opacity=".85"/><path d="M630 146 Q760 128 970 142 L970 156 L630 156Z" fill="#8a3a1e" opacity=".85"/>')
    o.append('<circle cx="890" cy="90" r="22" fill="#f2b04a" opacity=".9"/><path d="M780 80 L808 98 L780 116Z" fill="#fff" opacity=".9"/>')
    # string lights from the frame out to two poles
    for x0, x1 in [(370, 614), (986, 1230)]:
        o.append(lightstring(x0, 70, x1, 52, 12, n, 7, x0))
    for x in (370, 1230): o.append(post(x, 200, 132, p))
    # the patch, pumpkins on the vine
    r = random.Random(102)
    for _ in range(18):
        x = r.choice([r.randint(380, 560), r.randint(1040, 1240)]); y = r.randint(178, 214)
        o.append(pumpkin(x, y, r.randint(6, 10), p))
    o.append(f'<path d="M380 196 q40 -10 80 4 t90 -4 M1040 200 q50 -12 100 2 t90 0" fill="none" stroke="#4a6a2a" stroke-width="2.4"/>')
    # three trucks backed in, people sitting in the beds
    o.append(truck_rear(670, 218, .95, "#2f5a7a" if not n else "#20384a", p, n, [("#c8361f", "#2a2a2a"), ("#e8a63a", "#7a3a1e")]))
    o.append(truck_rear(800, 222, 1.05, "#8a2a22" if not n else "#4a1a16", p, n, [("#2f5a8a", "#c8361f"), ("#5a6a3a", "#2a2a2a")]))
    o.append(truck_rear(930, 218, .95, "#5a6a3a" if not n else "#26301e", p, n, [("#8a3a5a", "#e8a63a")]))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_training(n):  # the trail into the woods, a blazed post at the start
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 820, 50))
    o.append(valley(p, 120, 111))
    o.append(ground(p, 134, "#8a6a34" if not n else "#1a1a14"))
    # the trail winding away into the trees, narrowing with distance
    o.append(f'<path d="M640 240 C700 210 860 200 860 180 C860 162 760 160 770 146 C778 136 820 132 830 126 L846 126 C842 134 800 140 804 148 C812 164 920 168 916 186 C912 210 820 222 860 240Z" fill="{p["road"]}"/>')
    # woods both sides, the trees smaller as they go back
    LC = leafcols(p)
    for k, (x, b, h) in enumerate([(700, 128, 50), (960, 130, 54), (640, 140, 70), (1020, 142, 74), (560, 160, 110), (1100, 162, 104),
                                   (470, 190, 150), (1190, 196, 150)]):
        cols = [LC[k % 5], LC[(k + 1) % 5], LC[(k + 2) % 5], LC[(k + 3) % 5], LC[(k + 4) % 5]]
        o.append(birch(x, b, h, [p["gold"], p["yel"]], 112 + k, p["birch"]) if k % 3 == 1 else maple(x, b, h, cols, 112 + k, p["trunk"], .8))
    for x, y, c, rt in [(770, 214, p["red"], 30), (830, 196, p["gold"], 120), (820, 170, p["orange"], 200), (880, 222, p["orange"], 60)]:
        o.append(leaf(x, y, 1.1, c, rt))
    # the trail post with its yellow blaze, and a hiker setting off
    o.append(f'<rect x="604" y="150" width="12" height="62" fill="{p["wood"]}"/><rect x="604" y="160" width="12" height="16" fill="#f2c230"/>')
    o.append(person(890, 214, .95, "stand", "#c8361f", "#3a3a44", "#2f5a3a", p["skin"], hk="beanie") +
             '<rect x="878" y="160" width="12" height="22" rx="4" fill="#3a5a3a"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the hand-drawn trail map pinned to the table, a route through four stops
    wood, wood2 = ("#5a3a22", "#4a2e1a") if not n else ("#1e140e", "#170f0a")
    paper, edge = ("#f2e6c8", "#d8c49a") if not n else ("#8a8070", "#6e6454")
    ink = "#5a3a22" if not n else "#2a1e14"
    route = "#2f7a4a" if athena else "#b8321e"
    o = [defs(), f'<rect width="1600" height="{V}" fill="{wood}"/>']
    for y in range(0, V, 30): o.append(f'<rect x="0" y="{y}" width="1600" height="2" fill="{wood2}"/>')
    if n: o.append('<circle cx="800" cy="110" r="420" fill="url(#glow)" opacity=".5"/>')
    o.append(f'<path d="M372 34 L1226 26 L1232 188 L376 196Z" fill="#000" opacity=".25" transform="translate(4 5)"/>')
    o.append(f'<path d="M372 34 L1226 26 L1232 188 L376 196Z" fill="{paper}" stroke="{edge}" stroke-width="3"/>')
    # drawn on it: the stream, a covered bridge, the hills, little trees
    o.append(f'<path d="M560 30 C580 80 520 120 600 150 C650 170 640 190 660 194" fill="none" stroke="#6a9ac0" stroke-width="7" opacity=".8"/>')
    o.append(f'<rect x="578" y="122" width="40" height="14" fill="#b8321e" opacity=".8"/><path d="M574 122 L622 122 L614 114 L582 114Z" fill="{ink}" opacity=".8"/>')
    o.append(f'<path d="M960 60 l26 -22 l26 22 M994 60 l20 -16 l20 16" fill="none" stroke="{ink}" stroke-width="2.5" opacity=".7"/>')
    r = random.Random(121)
    for _ in range(16):
        x = r.randint(420, 1180); y = r.randint(52, 176)
        if abs(x - 600) < 40: continue
        o.append(f'<path d="M{x} {y} l-7 12 h14Z" fill="{r.choice(["#c8602a", "#d8a03a", "#b8321e", "#5a7a3a"])}" opacity=".75"/><line x1="{x}" y1="{y + 12}" x2="{x}" y2="{y + 16}" stroke="{ink}" stroke-width="1.5" opacity=".7"/>')
    pts = [(470, 150), (690, 96), (900, 146), (1110, 84)]
    d = f'M410 176 C430 166 450 156 {pts[0][0]} {pts[0][1]} S640 96 {pts[1][0]} {pts[1][1]} S850 148 {pts[2][0]} {pts[2][1]} S1060 86 {pts[3][0]} {pts[3][1]} S1180 70 1196 60'
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="4" stroke-dasharray="10 7" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        o.append(f'<circle cx="{x}" cy="{y}" r="14" fill="{paper}" stroke="{route}" stroke-width="4"/><text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{route}">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{y - 22}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-style="italic" font-size="21" fill="{ink}">{t}</text>')
    o.append(f'<path d="M1196 60 l-8 -22 M1196 60 l0 -24 l16 6 l-16 6" fill="none" stroke="{route}" stroke-width="3"/>')
    o.append(f'<g transform="translate(1160 152)"><circle r="22" fill="none" stroke="{ink}" stroke-width="2" opacity=".7"/><path d="M0 -18 L5 0 L0 18 L-5 0Z" fill="{ink}" opacity=".7"/><path d="M0 -18 L5 0 L-5 0Z" fill="{route}"/>'
             f'<text y="-26" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="11" fill="{ink}">N</text></g>')
    o.append(f'<text x="700" y="184" font-family="Georgia, serif" font-style="italic" font-size="15" fill="{ink}" opacity=".8">'
             + ('the service loop &#183; back by the bridge' if athena else 'the sales trail &#183; over the covered bridge') + '</text>')
    for x, y in ((380, 40), (1220, 32)): o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#c8361f"/><circle cx="{x - 1}" cy="{y - 1}" r="2" fill="#fff" opacity=".6"/>')
    # leaves fallen on the table, and a pencil
    P_ = P(n)
    for x, y, c, rt, sc in [(120, 60, P_["red"], 20, 3), (260, 120, P_["gold"], 140, 2.6), (1380, 70, P_["orange"], 70, 3.2), (1500, 150, P_["red"], 200, 2.4), (300, 30, P_["orange"], 300, 2)]:
        o.append(leaf(x, y, sc, c, rt))
    o.append('<g transform="rotate(-12 1330 190)"><rect x="1260" y="186" width="130" height="9" fill="#e8b63a"/><path d="M1390 186 L1406 190.5 L1390 195Z" fill="#e8d0a8"/><rect x="1252" y="186" width="10" height="9" fill="#c87a8a"/></g>')
    return vwrap(''.join(o))

def leafpile(x, y, w, h, p, seed):
    r = random.Random(seed); LC = leafcols(p)
    o = [f'<path d="M{x - w / 2} {y} Q{x - w * .3:.0f} {y - h} {x} {y - h} Q{x + w * .3:.0f} {y - h} {x + w / 2} {y}Z" fill="{p["red2"]}"/>']
    for _ in range(int(w / 6)):
        t = r.uniform(-.45, .45); yy = y - h * (1 - (2 * t) ** 2) * r.uniform(.2, .95)
        o.append(leaf(x + t * w, yy, r.uniform(.8, 1.2), r.choice(LC), r.randint(0, 360)))
    return ''.join(o)

def v_service(n):  # raking the leaves in front of the house
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 340, 56))
    o.append(valley(p, 126, 131))
    o.append(ground(p, 146))
    # the house, porch and all
    hx = 1000
    o.append(f'<rect x="{hx - 120}" y="94" width="240" height="98" fill="{p["white"]}"/><path d="M{hx - 134} 96 L{hx} 40 L{hx + 134} 96Z" fill="{p["roof"]}"/><rect x="{hx + 60}" y="40" width="16" height="36" fill="{p["barn2"]}"/>')
    for y in range(100, 192, 9): o.append(f'<line x1="{hx - 120}" y1="{y}" x2="{hx + 120}" y2="{y}" stroke="{p["white2"]}" stroke-width="1.2"/>')
    for wx, wy in [(hx - 96, 108), (hx + 62, 108), (hx - 22, 62)]:
        if n: o.append(f'<circle cx="{wx + 17}" cy="{wy + 16}" r="34" fill="url(#glow)"/>')
        o.append(f'<rect x="{wx}" y="{wy}" width="34" height="{30 if wy > 100 else 22}" fill="{p["win"]}" stroke="{p["white2"]}" stroke-width="3"/>')
    o.append(f'<path d="M{hx - 130} 150 L{hx + 130} 150 L{hx + 120} 140 L{hx - 120} 140Z" fill="{p["roof"]}"/>')
    for x in (hx - 120, hx - 40, hx + 40, hx + 120): o.append(f'<rect x="{x - 3}" y="150" width="6" height="42" fill="{p["white"]}"/>')
    o.append(f'<rect x="{hx - 16}" y="158" width="32" height="34" fill="{p["barn2"]}"/><rect x="{hx - 130}" y="190" width="260" height="6" fill="{p["white2"]}"/>')
    for x in (hx - 100, hx + 96): o.append(pumpkin(x, 190, 8, p))
    o.append(maple(700, 200, 220, [p["red2"], p["red"], p["orange"], p["red"], p["gold"]], 132, p["trunk"], .9))
    # the rakers and their piles, a barrow and the bags
    o.append(leafpile(620, 216, 120, 30, p, 133) + leafpile(860, 214, 90, 24, p, 134))
    o.append(person(540, 216, 1.0, "rake", "#2f5a8a", "#3a3a44", "#c8361f", p["skin"], hk="beanie"))
    o.append(person(950, 214, 1.0, "rake", "#5a6a3a", "#3a3530", "#7a3a1e", p["skin"], flip=True, hk="hair"))
    o.append(f'<path d="M1130 196 L1210 196 L1196 214 L1140 214Z" fill="#3a5a7a"/>{leafpile(1170, 198, 78, 16, p, 135)}<circle cx="1140" cy="218" r="8" fill="#1e1e1e"/><path d="M1206 204 L1234 222" stroke="{p["wood2"]}" stroke-width="4"/>')
    for x in (440, 470): o.append(f'<path d="M{x - 13} 220 L{x - 11} 184 L{x + 11} 184 L{x + 13} 220Z" fill="#c8a46a"/><path d="M{x - 11} 184 l4 -4 l4 4 l4 -4 l4 4 l4 -4 l2 4" fill="none" stroke="#a8844a" stroke-width="1.5"/>')
    r = random.Random(136); LC = leafcols(p)
    for _ in range(14): o.append(leaf(r.randint(480, 1260), r.randint(200, 232), 1, r.choice(LC), r.randint(0, 360)))
    for _ in range(5): o.append(leaf(r.randint(560, 860), r.randint(60, 180), 1.1, r.choice(LC), r.randint(0, 360)))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # the orchard in harvest: the rows coming back to us, bushels full at their feet
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 800, 46))
    o.append(valley(p, 112, 141))
    o.append(ground(p, 122, "#8e9a44" if not n else p["grass"]))
    for k in range(5):  # mown alleys between the rows, meeting at the far end
        o.append(f'<path d="M800 122 L{400 + k * 200 - 50} 240 L{400 + k * 200 + 50} 240Z" fill="{"#a2ac54" if not n else "#232e1e"}"/>')
    for rowx in (-1, 1):
        for k in range(6):
            t = k / 5; x = 800 + rowx * (40 + 470 * t ** 1.3); b = 126 + 90 * t ** 1.2; h = 26 + 120 * t ** 1.3
            o.append(appletree(x, b, h, p, 142 + k + (rowx + 1) * 10, n, 6 + k * 2))
    for x, y, rr in [(620, 222, 15), (980, 222, 15), (700, 196, 10), (900, 196, 10), (760, 178, 7), (840, 178, 7)]:
        o.append(basket(x, y, rr, p))
    o.append(ladder(1056, 216, 1090, 130, p["wood2"] if not n else "#5a4030"))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_claims(n):  # after the windstorm: the big maple down across the road, a crew cutting it clear
    p = P(n); sp = dict(p); sp["sky"] = ("#6a7488", "#b4a898", "#e8d2b0") if not n else ("#05070f", "#121828", "#222a3e")
    o = [base(n, sp, 24)]
    for x in (300, 760, 1240): o.append(f'<ellipse cx="{x}" cy="44" rx="230" ry="26" fill="{"#8a8f9e" if not n else "#1c2234"}"/>')
    if not n: o.append('<circle cx="1080" cy="72" r="30" fill="#fff6d8" opacity=".6"/>')
    o.append(valley(p, 126, 151))
    o.append(ground(p, 144))
    o.append(f'<path d="M0 214 Q800 194 1600 210 L1600 240 L0 240Z" fill="{p["road"]}"/>')
    # the stump snapped off, the trunk down across the road, its crown in the far ditch, a limb torn off
    o.append(f'<path d="M556 208 L562 172 L590 174 L598 208Z" fill="{p["trunk"]}"/><path d="M562 172 L568 158 L575 170 L582 156 L590 174Z" fill="#d8b07a"/>')
    o.append(f'<path d="M592 196 C700 186 840 188 960 172 L966 186 C840 204 700 206 596 210Z" fill="{p["trunk"]}"/>')
    o.append(f'<path d="M760 192 L790 160 M860 186 L900 150 M930 180 L990 160" stroke="{p["trunk"]}" stroke-width="7" stroke-linecap="round"/>')
    LC = leafcols(p)
    o.append(blobs([(x, y, rr, LC[i % 5]) for i, (x, y, rr) in enumerate([(985, 170, 26), (1010, 190, 22), (900, 146, 18), (950, 152, 20), (790, 156, 14), (1030, 168, 18), (965, 196, 18)])]))
    r = random.Random(152)
    for _ in range(12): o.append(leaf(r.randint(600, 1100), r.randint(196, 230), 1.1, r.choice(LC), r.randint(0, 360)))
    # the cut rounds, the crew, the cones and the crew's truck
    for x in (1100, 1124, 1112): o.append(f'<ellipse cx="{x}" cy="{216 - (x == 1112) * 18}" rx="12" ry="12" fill="#c8a06a" stroke="{p["trunk"]}" stroke-width="3"/>')
    o.append(person(740, 214, 1.0, "saw", "#e8761e", "#3a3a44", "#f2c230", p["skin"], hk="hard"))
    o.append(person(520, 214, 1.0, "point", "#e8761e", "#3a3a44", "#f2c230", p["skin"], hk="hard"))
    for x in (470, 1170): o.append(f'<path d="M{x - 10} 222 L{x} 194 L{x + 10} 222Z" fill="#e8761e"/><rect x="{x - 6}" y="206" width="12" height="4" fill="#fff"/>')
    o.append(pickup(1290, 222, 1.1, "#e8e2d0" if not n else "#5a5a5e", p, n, flip=True, driver=False))
    o.append('<rect x="1270" y="153" width="40" height="7" rx="2" fill="#f2a020"/>' + ('<circle cx="1290" cy="156" r="20" fill="#f2a020" opacity=".3"/>' if n else ''))
    o.append(edge_trees(p, right=False))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the general store on Main Street
    p = P(n); o = [base(n, p)]
    o.append(skyobj(n, 1290, 52))
    o.append(valley(p, 120, 161))
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{p["road"]}"/><rect x="0" y="190" width="1600" height="8" fill="{p["stone"]}"/>')
    # neighbours: a brick block left, a white clapboard right
    o.append(f'<rect x="380" y="80" width="170" height="112" fill="{"#a8503a" if not n else "#3a1e18"}"/><rect x="374" y="74" width="182" height="10" fill="{p["roof"]}"/>')
    o.append(f'<rect x="1080" y="96" width="160" height="96" fill="{p["white"]}"/><path d="M1070 98 L1160 56 L1250 98Z" fill="{p["roof"]}"/>')
    for wx, wy in [(400, 100), (470, 100), (400, 146), (470, 146), (1100, 116), (1180, 116)]:
        if n: o.append(f'<circle cx="{wx + 15}" cy="{wy + 14}" r="26" fill="url(#glow)"/>')
        o.append(f'<rect x="{wx}" y="{wy}" width="30" height="28" fill="{p["win"]}" stroke="{p["white2"]}" stroke-width="2"/>')
    # the store: a false front with its name, the porch roof on posts, two big windows
    sx0, sx1 = 580, 1050
    o.append(f'<rect x="{sx0}" y="40" width="{sx1 - sx0}" height="152" fill="{"#d8c49a" if not n else "#4a4234"}"/><rect x="{sx0 - 6}" y="34" width="{sx1 - sx0 + 12}" height="10" fill="{p["wood2"]}"/>')
    o.append(f'<rect x="{sx0 + 70}" y="52" width="{sx1 - sx0 - 140}" height="30" rx="3" fill="{p["barn"]}" stroke="{p["wood2"]}" stroke-width="3"/>'
             f'<text x="{(sx0 + sx1) // 2}" y="74" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="19" fill="{p["ink"]}" letter-spacing="3">GENERAL STORE</text>')
    o.append(f'<path d="M{sx0 - 10} 112 L{sx1 + 10} 112 L{sx1} 96 L{sx0} 96Z" fill="{p["roof"]}"/>')
    for i in range(12):
        o.append(f'<path d="M{sx0 + i * 39} 112 L{sx0 + 39 + i * 39} 112 L{sx0 + 39 + i * 39} 122 Q{sx0 + 19.5 + i * 39} 128 {sx0 + i * 39} 122Z" fill="{"#c8361f" if i % 2 == 0 else "#f4ecd8"}"/>')
    for x in (sx0, sx0 + 156, sx1 - 156, sx1): o.append(f'<rect x="{x - 4}" y="112" width="8" height="78" fill="{p["wood2"]}"/>')
    for wx in (sx0 + 26, sx1 - 176):
        if n: o.append(f'<circle cx="{wx + 75}" cy="160" r="80" fill="url(#glow)"/>')
        o.append(f'<rect x="{wx}" y="132" width="150" height="54" fill="{p["win"]}" stroke="{p["wood2"]}" stroke-width="4"/>')
    o.append(f'<rect x="{sx0 + 40}" y="140" width="122" height="16" fill="#fbf2de" opacity=".92"/><text x="{sx0 + 101}" y="152" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="10" fill="#8a2a1e">FALL INTO SAVINGS</text>')
    o.append(f'<rect x="{(sx0 + sx1) // 2 - 28}" y="128" width="56" height="62" fill="{p["win"] if n else p["wood"]}"/><rect x="{sx0 - 10}" y="188" width="{sx1 - sx0 + 20}" height="6" fill="{p["wood"]}"/>')
    for x in (sx0 + 186, sx0 + 214): o.append(f'<rect x="{x - 12}" y="164" width="24" height="26" rx="5" fill="#8a5a32"/><rect x="{x - 12}" y="170" width="24" height="3" fill="#4a3a2a"/><rect x="{x - 12}" y="182" width="24" height="3" fill="#4a3a2a"/>')
    for x, rr in [(sx1 - 200, 9), (sx1 - 184, 7), (sx1 - 214, 7)]: o.append(pumpkin(x, 190, rr, p))
    # the street lamp on its post, and a pickup at the kerb
    o.append(f'<rect x="1286" y="110" width="5" height="84" fill="#2a2a2a"/><rect x="1279" y="98" width="19" height="16" rx="3" fill="#2a2a2a"/><rect x="1283" y="101" width="11" height="10" fill="{"#ffd98a" if n else "#e8e2cc"}"/>' + ('<circle cx="1288" cy="106" r="40" fill="url(#glow)"/>' if n else ''))
    o.append(pickup(830, 228, 1.0, "#8a2a22" if not n else "#3e1a16", p, n, cargo="pumpkins"))
    o.append(maple(160, 196, 230, [p["red2"], p["red"], p["orange"], p["red"], p["gold"]], 162, p["trunk"]) + maple(1460, 196, 230, [p["orange"], p["gold"], p["red"], p["yel"], p["orange"]], 163, p["trunk"]))
    o.append(corners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the apple harvest: every crate on the truck"],
    "messages": ["Texts & Emails", "the mailbox row: flags up, answers out"],
    "coaching": ["Coaching", "the campfire circle: every call, talked over"],
    "roleplay": ["Role Play", "the hayride: practice the whole way round"],
    "rphistory": ["Session History", "the drive-in: every session, replayed"],
    "training": ["Training", "the trail through the woods, one blaze at a time"],
    "blueprint": ["Apollo's Road Map", "the trail map, in plain words"],
    "athenamap": ["Athena's Road Map", "the service loop, in plain words"],
    "service": ["Service Digest", "raking leaves: keeping the book tidy"],
    "renewals": ["Renewals", "the orchard in harvest: what came back"],
    "claims": ["Claims", "after the windstorm: the crew clears the road"],
    "commercial": ["Commercial Center", "the general store: Cerberus's book on main street"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, p, sky=None, star=30):
    q = dict(p)
    if sky: q["sky"] = sky
    return defs(skyg(q)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 90, 21) if n else '')

def cap(t, c="#fff"):
    return f'<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="24" fill="{c}" letter-spacing="2">{t}</text>'

def sground(p, y=112, c=None):
    return f'<path d="M0 {y} Q800 {y - 10} 1600 {y} L1600 160 L0 160Z" fill="{c or p["grass"]}"/>'

def s_sold(n):  # a full bushel on a bale, the blue ribbon pinned on it, the sun bursting behind
    p = P(n); o = [sbase(n, p, ("#e08a3a", "#f6c066", "#fde2a8") if not n else None)]
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        o.append(f'<path d="M800 84 L{800 + 700 * math.cos(ang):.0f} {84 + 700 * math.sin(ang):.0f} L{800 + 700 * math.cos(ang + .12):.0f} {84 + 700 * math.sin(ang + .12):.0f}Z" fill="#fff" opacity="{.2 if not n else .06}"/>')
    o.append(canopy(-10, 1610, 106, 12, 20, leafcols(p), 201, 26))
    o.append(sground(p, 108))
    o.append(haybale(800, 126, 130, 30, p))
    o.append(basket(800, 98, 34, p))
    # the blue ribbon: a rosette and its two tails
    o.append('<path d="M836 76 L828 112 L838 104 L844 114 L846 78Z" fill="#1f4aa8"/><path d="M846 76 L852 110 L858 100 L866 108 L856 74Z" fill="#2a5ac8"/>')
    for k in range(10):
        a_ = k / 10 * 2 * math.pi
        o.append(f'<circle cx="{844 + 11 * math.cos(a_):.1f}" cy="{72 + 11 * math.sin(a_):.1f}" r="6" fill="#2a5ac8"/>')
    o.append('<circle cx="844" cy="72" r="9" fill="#f2c230"/><circle cx="844" cy="72" r="5" fill="#1f4aa8"/>')
    r = random.Random(5)
    for _ in range(18):
        o.append(leaf(r.randint(560, 1060), r.randint(40, 100), 1.1, r.choice(leafcols(P(False)) if not n else leafcols(p)), r.randint(0, 360)))
    o.append(cap("FULL BUSHEL"))
    return wrap(S, ''.join(o))

def s_open(n):  # apples still ripening on the branch: half red, half green
    p = P(n); o = [sbase(n, p, ("#5a8cc4", "#a8c8de", "#f2dcae") if not n else None)]
    o.append(canopy(-10, 1610, 120, 14, 22, ["#7a8c3e", "#8a9a44", "#6a7a36"] if not n else ["#1c2a1a", "#22321e"], 202, 26))
    o.append(sground(p, 122, "#9aa850" if not n else p["grass"]))
    br = p["trunk"]
    o.append(f'<path d="M380 30 C520 46 640 60 760 62 C880 64 1000 52 1120 40" fill="none" stroke="{br}" stroke-width="9" stroke-linecap="round"/>')
    o.append(f'<path d="M620 58 L640 82 M880 62 L870 86 M1000 54 L1024 78" stroke="{br}" stroke-width="4"/>')
    g1, g2 = ("#5e7a34", "#7f9a40") if not n else ("#1e2e1c", "#2a3a22")
    for k, (x, y, rt) in enumerate([(520, 46, 30), (580, 62, 160), (700, 54, 20), (760, 76, 190), (820, 52, 340), (940, 68, 170), (1060, 44, 20), (1090, 62, 200)]):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="22" ry="9" fill="{g1 if k % 2 else g2}" transform="rotate({rt} {x} {y})"/>')
    for x, y, rr in [(640, 94, 16), (870, 98, 17), (1024, 90, 15)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{"#9ab84a" if not n else "#3a4a22"}"/><path d="M{x} {y - rr} A{rr} {rr} 0 0 0 {x} {y + rr} Q{x - rr * .3:.0f} {y} {x} {y - rr}Z" fill="{p["red"]}"/>'
                 f'<circle cx="{x + rr * .35:.0f}" cy="{y - rr * .35:.0f}" r="{rr * .2:.0f}" fill="#fff" opacity=".35"/>')
    o.append(cap("RIPENING"))
    return wrap(S, ''.join(o))

def s_lost(n):  # bare trees in a grey drizzle, the leaves already down and sodden
    p = P(n); o = [sbase(n, p, ("#6a6e78", "#9a9ea6", "#c4c6ca") if not n else ("#0a0c14", "#1a1d28", "#2a2d3a"), 8)]
    for x in (300, 720, 1150): o.append(f'<ellipse cx="{x}" cy="34" rx="220" ry="24" fill="{"#7a7e88" if not n else "#20232e"}"/>')
    o.append(f'<path d="M0 104 Q800 96 1600 104 L1600 160 L0 160Z" fill="{"#6a6a58" if not n else "#18201a"}"/>')
    tc = "#4a4440" if not n else "#262428"
    for x, h, sd in [(560, 96, 1), (800, 116, 2), (1040, 90, 3), (420, 70, 4), (1200, 76, 5)]:
        o.append(bare(x, 108, h, tc, 210 + sd, 3))
    o.append(f'<ellipse cx="800" cy="122" rx="120" ry="8" fill="{"#8a94a0" if not n else "#2a3448"}" opacity=".8"/>')
    for x, y, rt in [(640, 118, 30), (700, 124, 100), (940, 120, 200), (980, 128, 300), (880, 132, 60)]:
        o.append(leaf(x, y, 1.1, "#7a5a3a" if not n else "#3a2a20", rt))
    r = random.Random(211)
    o.append('<g stroke="#e4e8ee" stroke-width="1.6" opacity=".55" stroke-linecap="round">' +
             ''.join(f'<line x1="{x}" y1="{y}" x2="{x - 6}" y2="{y + 16}"/>' for x, y in ((r.randint(380, 1260), r.randint(30, 120)) for _ in range(44))) + '</g>')
    o.append(cap("BARE BRANCHES"))
    return wrap(S, ''.join(o))

def s_dead(n):  # a pickup stopped on the country road with a flat
    p = P(n); o = [sbase(n, p, ("#8a9aa8", "#c8c4b8", "#e8dcc4") if not n else None, 12)]
    o.append(canopy(-10, 1610, 96, 12, 20, leafcols(p) + [p["ever"]], 203, 26))
    o.append(sground(p, 98))
    o.append(stonewall([(300, 104), (1300, 104)], 11, p, 204))
    o.append(f'<rect x="0" y="112" width="1600" height="48" fill="{p["road"]}"/>')
    # the truck sits down at the back, the rear tyre flat on the road
    o.append(f'<g transform="rotate(-3 760 130)">{pickup(800, 134, .95, "#2f5a7a" if not n else "#22384e", p, n, driver=False)}</g>')
    o.append(f'<rect x="740" y="124" width="40" height="14" fill="{p["road"]}"/><ellipse cx="764" cy="128" rx="15" ry="7" fill="#1e1e1e"/><ellipse cx="764" cy="128" rx="5" ry="3" fill="#a0a0a0"/>')
    # the spare leaning on the wall, waiting
    o.append('<ellipse cx="1000" cy="110" rx="9" ry="14" fill="#1e1e1e"/><ellipse cx="1000" cy="110" rx="4" ry="6" fill="#a0a0a0"/>')
    o.append('<path d="M712 148 l16 -6 M700 142 l14 -2" stroke="#f2f0e8" stroke-width="2" opacity=".6"/>')
    o.append(cap("FLAT TIRE"))
    return wrap(S, ''.join(o))

def s_reached(n):  # two neighbours leaning on the stone wall, talking
    p = P(n); o = [sbase(n, p, ("#5a8cc4", "#f0b07a", "#f8d8a8") if not n else None)]
    o.append(canopy(-10, 1610, 98, 12, 22, leafcols(p) + [p["ever"]], 205, 26))
    o.append(sground(p, 100))
    o.append(maple(1040, 116, 110, [p["red2"], p["red"], p["orange"], p["red"], p["gold"]], 206, p["trunk"], .9))
    o.append(person(720, 136, 1.0, "lean", "#2f5a8a", "#3a3a44", "#c8361f", p["skin"], hk="cap"))
    o.append(person(880, 136, 1.0, "lean", "#8a3a5a", "#3a3530", "#7a3a1e", p["skin"], flip=True, hk="hair"))
    o.append(stonewall([(560, 140), (1040, 140)], 32, p, 207))
    o.append('<path d="M742 58 q8 -14 24 -14 h20 q16 0 16 14 q0 12 -16 12 h-24 l-10 8z" fill="#fff" opacity=".92"/><path d="M858 50 q-8 -14 -24 -14 h-20 q-16 0 -16 14 q0 12 16 12 h24 l10 8z" fill="#fff" opacity=".92"/>')
    for x in (758, 772, 786): o.append(f'<circle cx="{x}" cy="57" r="2.6" fill="#7a3a1e"/>')
    for x in (814, 828, 842): o.append(f'<circle cx="{x}" cy="49" r="2.6" fill="#7a3a1e"/>')
    o.append(pumpkin(620, 112, 9, p) + pumpkin(980, 112, 8, p))
    o.append(cap("OVER THE WALL"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # the scarecrow in the field, a crow on his arm, waiting
    p = P(n); o = [sbase(n, p, ("#d98a4a", "#f2c27a", "#fbe6b8") if not n else None)]
    o.append(canopy(-10, 1610, 92, 12, 20, leafcols(p), 208, 26))
    o.append(sground(p, 94, "#a8964a" if not n else p["grass"]))
    for cx in (620, 980, 1120, 500):
        o.append(f'<path d="M{cx - 18} 132 L{cx} 70 L{cx + 18} 132Z" fill="{p["hay2"]}"/><path d="M{cx - 9} 132 L{cx} 70 L{cx + 7} 132Z" fill="{p["hay"]}"/><path d="M{cx - 12} 104 L{cx + 12} 104" stroke="{p["wood2"]}" stroke-width="3"/>')
    sx, sb = 800, 148
    o.append(f'<rect x="{sx - 3}" y="{sb - 104}" width="6" height="104" fill="{p["wood2"]}"/><rect x="{sx - 50}" y="{sb - 82}" width="100" height="5" fill="{p["wood2"]}"/>')
    o.append(f'<path d="M{sx - 20} {sb - 86} L{sx + 20} {sb - 86} L{sx + 16} {sb - 44} L{sx - 16} {sb - 44}Z" fill="#7a4a8a"/><path d="M{sx - 20} {sb - 84} L{sx - 46} {sb - 80} L{sx - 46} {sb - 72} L{sx - 18} {sb - 74}Z M{sx + 20} {sb - 84} L{sx + 46} {sb - 80} L{sx + 46} {sb - 72} L{sx + 18} {sb - 74}Z" fill="#7a4a8a"/>')
    o.append(f'<path d="M{sx - 14} {sb - 44} L{sx - 18} {sb - 18} L{sx - 6} {sb - 18} L{sx} {sb - 38} L{sx + 6} {sb - 18} L{sx + 18} {sb - 18} L{sx + 14} {sb - 44}Z" fill="#3a5a8a"/>')
    o.append(f'<circle cx="{sx}" cy="{sb - 98}" r="13" fill="{p["hay"]}"/><path d="M{sx - 24} {sb - 108} L{sx + 24} {sb - 108} L{sx + 12} {sb - 110} L{sx + 8} {sb - 126} L{sx - 8} {sb - 126} L{sx - 12} {sb - 110}Z" fill="#6a4a2a"/>')
    o.append(f'<rect x="{sx - 12}" y="{sb - 88}" width="24" height="6" rx="2" fill="#c8361f"/><path d="M{sx + 8} {sb - 86} Q{sx + 22} {sb - 84} {sx + 34} {sb - 90} L{sx + 36} {sb - 82} Q{sx + 22} {sb - 78} {sx + 6} {sb - 80}Z" fill="#c8361f"/>')
    # the crow on his left arm
    o.append(f'<path d="M{sx - 40} {sb - 82} q-4 -12 6 -16 q8 -2 12 4 l8 -2 l-6 6 q2 8 -8 10Z" fill="#1a1a1e"/><path d="M{sx - 26} {sb - 96} l7 -1 l-6 4Z" fill="#e8a63a"/>')
    o.append(cap("WAITING"))
    return wrap(S, ''.join(o))

def s_vm(n):  # a quiet barn under the harvest moon, every window dark
    p = P(True); o = [sbase(True, p, None, 50)]
    if not n: o.append(stars(16, 0, 1600, 0, 80, 22))
    o.append(moon(1010, 58, 26))
    o.append(hills([(0, 96), (400, 76), (800, 94), (1200, 72), (1600, 90)], 160, "#1c1a2c"))
    o.append(f'<path d="M0 108 Q800 98 1600 108 L1600 160 L0 160Z" fill="#141c14"/>')
    bx = 760
    o.append(f'<path d="M{bx - 80} 118 L{bx - 80} 70 L{bx - 50} 44 L{bx + 50} 44 L{bx + 80} 70 L{bx + 80} 118Z" fill="#3a1614"/><path d="M{bx - 86} 72 L{bx - 50} 40 L{bx + 50} 40 L{bx + 86} 72 L{bx + 78} 74 L{bx + 48} 46 L{bx - 48} 46 L{bx - 78} 74Z" fill="#1a1620"/>')
    o.append(f'<rect x="{bx - 26}" y="78" width="52" height="40" fill="#2a100e"/><path d="M{bx - 26} 78 L{bx + 26} 118 M{bx + 26} 78 L{bx - 26} 118" stroke="#6a6878" stroke-width="2.4"/><rect x="{bx - 26}" y="78" width="52" height="40" fill="none" stroke="#6a6878" stroke-width="2.4"/>')
    o.append(f'<rect x="{bx - 10}" y="52" width="20" height="16" fill="#120a0a" stroke="#6a6878" stroke-width="2"/>')
    o.append(f'<rect x="{bx + 110}" y="56" width="34" height="62" rx="16" fill="#4a4a58"/><path d="M{bx + 110} 70 Q{bx + 127} 46 {bx + 144} 70Z" fill="#2a2a34"/>')
    for x in range(520, 1100, 40): o.append(f'<rect x="{x}" y="112" width="4" height="22" fill="#0c0c10"/>')
    o.append('<rect x="520" y="118" width="584" height="3" fill="#0c0c10"/><rect x="520" y="128" width="584" height="3" fill="#0c0c10"/>')
    o.append(cap("NO ONE HOME"))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["The leaves are turning, {n}.", "Peak colour on the floor today, {n}.", "Fall into a good day, {n}.",
             "Harvest time, {n}. Bring in every quote.", "Grab a cider and a phone, {n}.", "Every call is a crisp one, {n}.",
             "Rake in the households, {n}.", "The orchard is full today, {n}.", "Sweater weather and full coverage, {n}.",
             "Cross the covered bridge, {n}: bundle it.", "Pick the ripe ones first, {n}.", "No lapse on this lane, {n}.",
             "Golden hour on the board, {n}.", "Fill the bushel, {n}.", "Pumpkin-spiced and policy-priced, {n}."]

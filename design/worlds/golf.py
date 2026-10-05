"""The Golf world: one course at golden hour. Colour looks, fonts, the Digest picture, page banners, card strips."""
import random, math

KEY = "golf"
NAME = "Golf"
FONTS = "family=Playfair+Display:wght@700;800&family=Nunito+Sans:wght@400;500;600;700"
DISPLAY = "'Playfair Display', Georgia, serif"
DW = 700
BODY = "'Nunito Sans', system-ui, sans-serif"
SKY_BG = (("#9cbfdc", "#6f9e4c"), ("#081022", "#12241b"))

LOOKS = [
    ("fairway", "Fairway",
     "--surface: #eef2ec; --surface-raised: #fcfdfb; --card2: #f2f6f0; --chip: #e2eadf; --text-primary: #15241a; --text-muted: #556558; --text-secondary: #3e4f43; --grid: #e1e8dd; --border: #d5ddd1; --border-strong: #b4c2ae; --accent: #1d7238; --accent-d: #145628; --side: #174a2a; --side2: #1f5a35; --sideInk: #e2efe4; --brand: #f4f8f1; --brand2: #e9c75a; --rad: 12px;",
     "--surface: #0d1510; --surface-raised: #142019; --card2: #1a281f; --chip: #213226; --text-primary: #e5eee6; --text-muted: #9cb0a1; --text-secondary: #b7c7ba; --grid: #213226; --border: #24362a; --border-strong: #32493a; --accent: #e3c25a; --accent-d: #eed486; --side: #08100b; --side2: #112018; --sideInk: #e2efe4; --brand: #f4f8f1; --brand2: #e9c75a;",
     ["#eef2ec", "#174a2a", "#e9c75a"]),
    ("clubhouse", "Clubhouse",
     "--surface: #f1ebdc; --surface-raised: #fdfaf1; --card2: #f6f0e2; --chip: #ebe2cc; --text-primary: #1f2419; --text-muted: #5f5f4c; --text-secondary: #4a4b38; --grid: #e8e0cc; --border: #dfd5bd; --border-strong: #c4b694; --accent: #87581a; --accent-d: #6a4410; --side: #1d3324; --side2: #284331; --sideInk: #ece6d2; --brand: #f6f0e0; --brand2: #d6a64e; --rad: 14px;",
     "--surface: #13120d; --surface-raised: #1b1a13; --card2: #222119; --chip: #2b2a1f; --text-primary: #efe9da; --text-muted: #ada58e; --text-secondary: #c6bea6; --grid: #2b2a1f; --border: #2f2d22; --border-strong: #433f2f; --accent: #dcab5c; --accent-d: #e8c487; --side: #0b120d; --side2: #152219; --sideInk: #ece6d2; --brand: #f6f0e0; --brand2: #d6a64e;",
     ["#f1ebdc", "#1d3324", "#b8873a"]),
    ("links", "Links",
     "--surface: #e7ebee; --surface-raised: #f8fafb; --card2: #eef1f3; --chip: #dfe4e8; --text-primary: #1a2129; --text-muted: #5a6470; --text-secondary: #45505c; --grid: #dfe4e9; --border: #d4dae0; --border-strong: #b5bfc8; --accent: #7a3d6c; --accent-d: #5e2c53; --side: #34404f; --side2: #424f60; --sideInk: #e1e6ec; --brand: #eef1f3; --brand2: #e3cc96; --rad: 10px;",
     "--surface: #0e1115; --surface-raised: #151a20; --card2: #1b2128; --chip: #222a33; --text-primary: #e6eaef; --text-muted: #9ea8b4; --text-secondary: #b8c1cb; --grid: #222a33; --border: #252d37; --border-strong: #354150; --accent: #cf9fc4; --accent-d: #dfbcd7; --side: #090c10; --side2: #141a22; --sideInk: #e1e6ec; --brand: #eef1f3; --brand2: #e3cc96;",
     ["#e7ebee", "#34404f", "#9b5a8c"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(far="#1d2a47", near="#17263a", treeline="#0d1c20", tree="#0c1a19", tree2="#091413", cyp="#0a1716",
                    rough="#13261c", rough2="#102119", fair="#1c3727", fair2="#18311f", green="#2a5237", green2="#234831",
                    fringe="#193323", sand="#5f5e66", sand2="#4a4a54", water="#14284a", water2="#2b4774", path="#464955",
                    path2="#353845", wall="#3a3944", wall2="#2b2a33", roof="#13251c", roof2="#0d1a14", trim="#3a2a1c",
                    win="#ffcf6a", wood="#3e2a1a", wood2="#28190e", ink="#f3e7cf", flag="#c63c2a", trunk="#22160e",
                    stone="#4a4c58", skin="#c89a76")
    return dict(far="#98b4bc", near="#86a97a", treeline="#3e6b45", tree="#2f5c3a", tree2="#244b2f", cyp="#24482e",
                rough="#6c9e4e", rough2="#5f9045", fair="#8dc262", fair2="#81b757", green="#a2d46e", green2="#96ca64",
                fringe="#7fb456", sand="#eedfb2", sand2="#d8c28e", water="#4f97c4", water2="#86c0e2", path="#e4ddcc",
                path2="#c8bfab", wall="#f2e9d6", wall2="#d8ccb2", roof="#2e5a3d", roof2="#22472f", trim="#7a5a34",
                win="#a7cbe0", wood="#7f5230", wood2="#5a3618", ink="#fbf2d8", flag="#d8402a", trunk="#5a3a22",
                stone="#c9c2b2", skin="#e2b48c")

DAYSKY = ("#4a86c6", "#f1c88f", "#fbe3b6")
NIGHTSKY = ("#040917", "#0f1c40", "#27365e")

def defs(extra=''):
    return ('<defs><radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc35a" stop-opacity=".6"/><stop offset="1" stop-color="#ffc35a" stop-opacity="0"/></radialGradient>'
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
    g = f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".08"/><circle cx="{x}" cy="{y}" r="{r * 1.8}" fill="#e9eefc" opacity=".12"/>' if glow else ''
    return g + f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f4efdc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#ddd6bd"/><circle cx="{x + r * .3:.0f}" cy="{y + r * .3:.0f}" r="{r * .12:.0f}" fill="#ddd6bd"/>'

def sun(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r * 2.8}" fill="#fff1c8" opacity=".22"/><circle cx="{x}" cy="{y}" r="{r * 1.7}" fill="#fff1c8" opacity=".35"/><circle cx="{x}" cy="{y}" r="{r}" fill="#fff6d8"/>'

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s} {y - 3 * s} Q{x - 5 * s} {y - 7 * s} {x} {y} Q{x + 5 * s} {y - 7 * s} {x + 10 * s} {y - 3 * s}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

def cloud(x, y, w, op=.55, c="#fff"):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="10" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .12:.0f}" cy="{y - 9}" rx="{w * .3:.0f}" ry="10" fill="{c}" opacity="{op * .85:.2f}"/>')

def hills(pts, b, c):
    d = f'M{pts[0][0]} {b} L{pts[0][0]} {pts[0][1]}'
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2; my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f' Q{pts[i][0]} {pts[i][1]} {mx:.0f} {my:.0f}'
    d += f' L{pts[-1][0]} {pts[-1][1]} L{pts[-1][0]} {b}Z'
    return f'<path d="{d}" fill="{c}"/>'

def cypress(x, b, h, c, tc=None):
    w = h * .16
    t = f'<rect x="{x - 3}" y="{b - h * .08:.0f}" width="6" height="{h * .08:.0f}" fill="{tc}"/>' if tc else ''
    return t + (f'<path d="M{x} {b - h} C{x + w * .55:.0f} {b - h * .78:.0f} {x + w:.0f} {b - h * .4:.0f} {x + w * .7:.0f} {b - h * .06:.0f} '
                f'L{x - w * .7:.0f} {b - h * .06:.0f} C{x - w:.0f} {b - h * .4:.0f} {x - w * .55:.0f} {b - h * .78:.0f} {x} {b - h}Z" fill="{c}"/>')

def oak(x, b, h, c, c2, tc):
    r = h * .32
    return (f'<path d="M{x - h * .04:.0f} {b} L{x - h * .025:.0f} {b - h * .5:.0f} L{x + h * .025:.0f} {b - h * .5:.0f} L{x + h * .04:.0f} {b}Z" fill="{tc}"/>'
            f'<circle cx="{x - r * .7:.0f}" cy="{b - h * .55:.0f}" r="{r * .75:.0f}" fill="{c2}"/><circle cx="{x + r * .7:.0f}" cy="{b - h * .57:.0f}" r="{r * .8:.0f}" fill="{c2}"/>'
            f'<circle cx="{x}" cy="{b - h * .7:.0f}" r="{r:.0f}" fill="{c}"/><circle cx="{x + r * .45:.0f}" cy="{b - h * .8:.0f}" r="{r * .55:.0f}" fill="{c}"/>')

def treeline(x0, x1, b, rmin, rmax, c, seed, step=34):
    r = random.Random(seed); o = []; x = x0
    while x < x1:
        rr = r.randint(rmin, rmax); o.append(f'<circle cx="{x}" cy="{b - rr * .6:.0f}" r="{rr}" fill="{c}"/>'); x += r.randint(step - 10, step + 10)
    return f'<rect x="{x0}" y="{b - rmin}" width="{x1 - x0}" height="{rmin + 2}" fill="{c}"/>' + ''.join(o)

def flag(x, y, h, c="#d8402a", cup=True, wave=0):
    o = []
    if cup: o.append(f'<ellipse cx="{x}" cy="{y}" rx="{h * .09:.1f}" ry="{h * .03:.1f}" fill="#1a1a14"/>')
    o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y - h}" stroke="#f3f0e6" stroke-width="{max(2, h * .035):.1f}"/>')
    o.append(f'<path d="M{x} {y - h} Q{x + h * .22:.0f} {y - h * (.95 - wave):.0f} {x + h * .42:.0f} {y - h * .9:.0f} L{x} {y - h * .74:.0f}Z" fill="{c}"/>')
    return ''.join(o)

def bunker(cx, cy, rx, ry, p, rot=0):
    return (f'<g transform="rotate({rot} {cx} {cy})"><ellipse cx="{cx}" cy="{cy + ry * .12:.0f}" rx="{rx + 4}" ry="{ry + 3}" fill="{p["sand2"]}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{p["sand"]}"/>'
            f'<path d="M{cx - rx * .8:.0f} {cy - ry * .2:.0f} Q{cx} {cy - ry * 1.05:.0f} {cx + rx * .8:.0f} {cy - ry * .2:.0f}" fill="none" stroke="{p["sand2"]}" stroke-width="2" opacity=".6"/></g>')

def bunker2(pts, p, n):
    """a real greenside bunker: an irregular flashed shape, the far lip in shadow, the sand face lit"""
    d = "M" + " ".join(f"{x},{y}" for x, y in pts[:1])
    k = len(pts)
    for i in range(k):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % k]
        d += f" Q{x0 + (x1 - x0) * .5 + (y1 - y0) * .18:.0f} {y0 + (y1 - y0) * .5 - (x1 - x0) * .18:.0f} {x1} {y1}"
    d += "Z"
    lip = p["rough2"] if not n else "#0b170f"
    return (f'<path d="{d}" fill="{lip}" transform="translate(0 -4)"/><path d="{d}" fill="{p["sand2"]}"/>'
            f'<path d="{d}" fill="{p["sand"]}" transform="translate(0 3) scale(1 .985)" opacity=".95"/>')

def ball(x, y, r=4, c="#ffffff"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="#9aa0a0" stroke-width="{max(.6, r * .15):.1f}"/>'

def golfer(x, y, s, pose="stand", shirt="#c8452a", pants="#2e3a4c", cap="#f3efe2", flip=False, skin="#e2b48c", club="#c9ccd2"):
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{pants}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    arm = f'stroke="{shirt}" stroke-width="6" fill="none" stroke-linecap="round"'
    shoes = '<ellipse cx="-6" cy="0" rx="5" ry="2.5" fill="#f4f4f0"/><ellipse cx="7" cy="0" rx="5" ry="2.5" fill="#f4f4f0"/>'
    if pose == "swing":  # the follow-through, facing right, club over the shoulder
        b = (f'<path d="M-6 0 L-2 -30 M8 -2 L4 -16 L2 -30" {leg}/>' + shoes +
             f'<path d="M-9 -56 Q0 -60 9 -54 L8 -28 L-8 -28Z" fill="{shirt}"/>'
             f'<path d="M6 -52 Q12 -58 4 -66 M-6 -52 Q2 -62 4 -66" {arm}/>'
             f'<line x1="4" y1="-66" x2="-30" y2="-78" stroke="{club}" stroke-width="2.4"/><rect x="-36" y="-82" width="8" height="5" rx="2" fill="{club}" transform="rotate(-20 -32 -80)"/>'
             f'<circle cx="2" cy="-63" r="7.5" fill="{skin}"/><path d="M-6 -66 Q2 -74 10 -66 L14 -65 L10 -63 Z" fill="{cap}"/>')
    elif pose == "address":  # set up over the ball, club behind
        b = (f'<path d="M-7 0 L-4 -28 M8 0 L4 -28" {leg}/>' + shoes +
             f'<path d="M-8 -28 L4 -28 L14 -50 Q6 -56 -2 -52Z" fill="{shirt}"/>'
             f'<path d="M10 -48 L14 -30" {arm}/><line x1="14" y1="-30" x2="24" y2="0" stroke="{club}" stroke-width="2.4"/><rect x="21" y="-3" width="9" height="4" rx="2" fill="{club}"/>'
             f'<circle cx="16" cy="-58" r="7.5" fill="{skin}"/><path d="M8 -61 Q16 -69 24 -61 L28 -59 L24 -58 Z" fill="{cap}"/>')
    elif pose == "putt":
        b = (f'<path d="M-6 0 L-3 -28 M8 0 L5 -28" {leg}/>' + shoes +
             f'<path d="M-6 -28 L6 -28 L16 -48 Q8 -54 0 -50Z" fill="{shirt}"/>'
             f'<path d="M12 -46 L14 -28" {arm}/><line x1="14" y1="-28" x2="16" y2="-1" stroke="{club}" stroke-width="2.2"/><rect x="12" y="-3" width="10" height="3.5" rx="1.5" fill="{club}"/>'
             f'<circle cx="19" cy="-55" r="7.5" fill="{skin}"/><path d="M11 -58 Q19 -66 27 -58 L31 -56 L27 -55 Z" fill="{cap}"/>')
    elif pose == "crouch":  # reading the line, putter held up as a plumb line
        b = (f'<path d="M-8 0 L-12 -14 L2 -18 M6 0 L10 -12 L2 -18" {leg}/>' + '<ellipse cx="-8" cy="0" rx="5" ry="2.5" fill="#f4f4f0"/><ellipse cx="7" cy="0" rx="5" ry="2.5" fill="#f4f4f0"/>' +
             f'<path d="M-6 -18 L8 -18 L8 -42 Q0 -46 -6 -42Z" fill="{shirt}"/>'
             f'<path d="M6 -38 L20 -42" {arm}/><line x1="21" y1="-64" x2="21" y2="-14" stroke="{club}" stroke-width="2.2"/><rect x="17" y="-16" width="9" height="3.5" rx="1.5" fill="{club}"/>'
             f'<circle cx="3" cy="-50" r="7.5" fill="{skin}"/><path d="M-5 -53 Q3 -61 11 -53 L15 -51 L11 -50 Z" fill="{cap}"/>')
    elif pose == "point":  # the pro, arm out, explaining
        b = (f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + shoes +
             f'<path d="M-9 -56 Q0 -60 9 -56 L8 -28 L-8 -28Z" fill="{shirt}"/>'
             f'<path d="M6 -52 L22 -58 L32 -62 M-6 -52 L-10 -36" {arm}/>'
             f'<circle cx="0" cy="-64" r="7.5" fill="{skin}"/><path d="M-8 -67 Q0 -75 8 -67 L12 -65 L8 -64 Z" fill="{cap}"/>')
    else:  # stand, club as a cane
        b = (f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + shoes +
             f'<path d="M-9 -56 Q0 -60 9 -56 L8 -28 L-8 -28Z" fill="{shirt}"/>'
             f'<path d="M6 -52 L12 -34 M-6 -52 L-9 -34" {arm}/><line x1="12" y1="-34" x2="18" y2="0" stroke="{club}" stroke-width="2.4"/>'
             f'<circle cx="0" cy="-64" r="7.5" fill="{skin}"/><path d="M-8 -67 Q0 -75 8 -67 L12 -65 L8 -64 Z" fill="{cap}"/>')
    return g + b + '</g>'

def bag(x, y, s, c="#2f5a8a"):
    return (f'<g transform="translate({x} {y}) scale({s})"><line x1="-4" y1="-46" x2="-8" y2="-60" stroke="#c9ccd2" stroke-width="2"/><line x1="2" y1="-46" x2="4" y2="-62" stroke="#c9ccd2" stroke-width="2"/>'
            f'<line x1="6" y1="-46" x2="12" y2="-58" stroke="#c9ccd2" stroke-width="2"/><rect x="-9" y="-48" width="20" height="48" rx="6" fill="{c}"/><rect x="-9" y="-30" width="20" height="5" fill="#fff" opacity=".7"/></g>')

def cart(x, y, s, body="#f2efe4", roof="#1f5a35", label=None, flip=False):
    """a golf cart side on, wheels on y, facing left"""
    o = [f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">',
         f'<rect x="-52" y="-74" width="104" height="7" rx="3" fill="{roof}"/>',
         '<line x1="-40" y1="-68" x2="-34" y2="-30" stroke="#5a5a5a" stroke-width="3"/><line x1="40" y1="-68" x2="40" y2="-30" stroke="#5a5a5a" stroke-width="3"/>',
         f'<path d="M-56 -12 L-52 -32 L-30 -34 L-20 -22 L46 -22 L52 -34 L58 -34 L58 -12Z" fill="{body}" stroke="#9a968a" stroke-width="1.5"/>',
         '<path d="M-36 -32 L-48 -50" stroke="#3a3a3a" stroke-width="3"/><rect x="0" y="-36" width="34" height="14" rx="3" fill="#3a3a3a"/>',
         f'<rect x="46" y="-62" width="14" height="40" rx="4" fill="#8a2a2a"/><line x1="50" y1="-62" x2="48" y2="-74" stroke="#c9ccd2" stroke-width="2"/><line x1="56" y1="-62" x2="58" y2="-72" stroke="#c9ccd2" stroke-width="2"/>',
         '<circle cx="-36" cy="-8" r="10" fill="#222"/><circle cx="-36" cy="-8" r="4" fill="#9a9a9a"/><circle cx="38" cy="-8" r="10" fill="#222"/><circle cx="38" cy="-8" r="4" fill="#9a9a9a"/>']
    if label: o.append(f'<text x="14" y="-14" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="8" fill="#1f3a28"' + (' transform="scale(-1 1)" ' if flip else '') + f'>{label}</text>')
    o.append('</g>')
    return ''.join(o)

def lamp(x, b, h, n, c="#2b2b2b"):
    o = [f'<rect x="{x - 2}" y="{b - h}" width="4" height="{h}" fill="{c}"/><rect x="{x - 6}" y="{b - h - 12}" width="12" height="12" rx="2" fill="{c}"/>'
         f'<rect x="{x - 4}" y="{b - h - 10}" width="8" height="8" fill="{"#ffe39a" if n else "#e8e2cc"}"/>']
    if n: o.insert(0, f'<circle cx="{x}" cy="{b - h - 6}" r="{h * .9:.0f}" fill="url(#glow)"/>')
    return ''.join(o)

def sign(x, y, w, h, text, p, fs=16, posts=40, sub=None):
    o = [f'<rect x="{x - w * .36:.0f}" y="{y}" width="6" height="{h + posts}" fill="{p["wood2"]}"/><rect x="{x + w * .36 - 6:.0f}" y="{y}" width="6" height="{h + posts}" fill="{p["wood2"]}"/>',
         f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{h}" rx="4" fill="{p["wood"]}" stroke="{p["wood2"]}" stroke-width="3"/>',
         f'<text x="{x}" y="{y + h / 2 + fs * .36 - (fs * .5 if sub else 0):.0f}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="{fs}" fill="{p["ink"]}" letter-spacing="1">{text}</text>']
    if sub: o.append(f'<text x="{x}" y="{y + h / 2 + fs * .78:.0f}" text-anchor="middle" font-family="Georgia, serif" font-size="{fs * .62:.0f}" fill="{p["ink"]}" opacity=".9">{sub}</text>')
    return ''.join(o)

def clubhouse(cx, b, p, n, s=1.0, tower=True, sign_text="FULL COVERAGE COUNTRY CLUB"):
    """body 280 wide x 80 tall at scale 1, hip roof, central clock tower to ~b-382"""
    o = [f'<g transform="translate({cx} {b}) scale({s})">']
    a = o.append
    if tower:
        a(f'<rect x="-28" y="-370" width="56" height="300" fill="{p["wall"]}"/><rect x="-28" y="-370" width="10" height="300" fill="{p["wall2"]}" opacity=".7"/>')
        a(f'<rect x="-34" y="-376" width="68" height="10" fill="{p["trim"]}"/>')
        a(f'<path d="M-36 -376 L0 -426 L36 -376Z" fill="{p["roof"]}"/><path d="M0 -426 L36 -376 L14 -376Z" fill="{p["roof2"]}"/>')
        a(f'<line x1="0" y1="-426" x2="0" y2="-466" stroke="{p["trim"]}" stroke-width="3"/><path d="M0 -466 L30 -458 L0 -450Z" fill="{p["flag"]}"/>')
        a(f'<circle cx="0" cy="-345" r="17" fill="#fbf6e6" stroke="{p["trim"]}" stroke-width="3"/><line x1="0" y1="-345" x2="0" y2="-356" stroke="#2a2a2a" stroke-width="2.4"/><line x1="0" y1="-345" x2="8" y2="-341" stroke="#2a2a2a" stroke-width="2.4"/>')
        if n: a('<circle cx="0" cy="-345" r="40" fill="url(#glow)" opacity=".7"/>')
        for k in range(3): a(f'<rect x="-10" y="{-300 + k * 60}" width="20" height="30" rx="10" fill="{p["win"] if n else "#7e98a6"}"/>')
    a(f'<rect x="-140" y="-80" width="280" height="80" fill="{p["wall"]}"/><rect x="-140" y="-10" width="280" height="10" fill="{p["wall2"]}"/>')
    a(f'<path d="M-156 -78 L-110 -128 L110 -128 L156 -78Z" fill="{p["roof"]}"/><path d="M110 -128 L156 -78 L120 -78Z" fill="{p["roof2"]}"/><rect x="-158" y="-82" width="316" height="6" fill="{p["trim"]}"/>')
    if tower: a(f'<rect x="-28" y="-128" width="56" height="50" fill="{p["wall"]}"/>')
    a(f'<rect x="-120" y="-74" width="240" height="17" rx="2" fill="{p["roof2"]}"/><text x="0" y="-61" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="11.5" fill="{p["ink"]}" letter-spacing="1.5">{sign_text}</text>')
    for wx in (-122, -92, -62, 40, 70, 100):
        if n: a(f'<circle cx="{wx + 11}" cy="-34" r="30" fill="url(#glow)"/>')
        a(f'<path d="M{wx} -14 L{wx} -38 Q{wx + 11} -50 {wx + 22} -38 L{wx + 22} -14Z" fill="{p["win"]}" stroke="{p["trim"]}" stroke-width="2"/>')
    a(f'<path d="M-22 -50 L22 -50 L26 -44 L-26 -44Z" fill="{p["roof"]}"/><rect x="-24" y="-44" width="5" height="44" fill="{p["wall2"]}"/><rect x="19" y="-44" width="5" height="44" fill="{p["wall2"]}"/>')
    a(f'<path d="M-12 0 L-12 -30 Q0 -40 12 -30 L12 0Z" fill="{p["win"] if n else p["wood"]}"/>')
    a('</g>')
    return ''.join(o)

def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient></defs>'
         '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')
def vwrap(body): return wrap(240, body + SHADE)

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    HZ = 432  # the far treeline sits a little below the split so the hills run on into the leaderboard
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a(defs(skyg(n, day=("#4a86c6", "#f0c68c", "#f9deb0"), id="sky") +
           '<radialGradient id="mg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
           f'<linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["green"]}"/><stop offset="1" stop-color="{p["green2"]}"/></linearGradient>'
           '<clipPath id="fw"><path d="M700 432 C650 470 540 515 455 580 L1150 580 C1060 515 950 470 900 432Z"/></clipPath>'))
    a(f'<rect width="{W}" height="{HZ + 30}" fill="url(#sky)"/>')
    if n:
        a(stars(70, 0, W, 0, 300, 3))
        a(moon(640, 92, 32)); a('<ellipse cx="640" cy="96" rx="280" ry="140" fill="url(#mg)"/>')
    else:
        a(sun(640, 100, 34))
        for x, y, w in [(470, 132, 220), (980, 70, 190), (1420, 150, 160)]: a(cloud(x, y, w))
        a(bird(820, 84, 1.2, "#4a4a5a") + bird(852, 70, .9, "#4a4a5a") + bird(1060, 120, 1, "#4a4a5a"))
    # far and near hills
    a(hills([(0, 262), (200, 196), (430, 250), (640, 220), (830, 252), (1000, 150), (1180, 232), (1390, 196), (1600, 244)], HZ, p["far"]))
    a(hills([(0, 340), (260, 300), (520, 344), (760, 316), (1000, 346), (1300, 312), (1600, 340)], HZ, p["near"]))
    # the course below
    a(f'<rect x="0" y="{HZ - 4}" width="{W}" height="{H - HZ}" fill="{p["rough"]}"/>')
    a(treeline(-10, 1610, HZ + 4, 18, 32, p["treeline"], 2, 30))
    # the clubhouse on the rise, right; its clock tower rises between the tiles
    a(clubhouse(1235, 506, p, n))
    # tall cypress framing both edges
    for x, b, h in [(40, 660, 560), (118, 620, 470), (1488, 640, 520), (1566, 680, 600)]:
        a(cypress(x, b, h, p["cyp"], p["trunk"]))
    a(oak(190, 560, 170, p["tree"], p["tree2"], p["trunk"]))
    a(oak(1410, 520, 120, p["tree"], p["tree2"], p["trunk"]))
    # rough tones, and the shadows the big trees throw across the grass
    a(f'<path d="M0 {HZ + 90} Q300 {HZ + 60} 600 {HZ + 110} T1200 {HZ + 120} T1600 {HZ + 100} L1600 {H} L0 {H}Z" fill="{p["rough2"]}" opacity=".6"/>')
    for x, y, rx in [(120, 662, 120), (1520, 672, 110), (230, 566, 80), (1440, 528, 60)]:
        a(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .16:.0f}" fill="#000" opacity="{.12 if not n else .2}"/>')
    # another hole crossing the distance, its own green and flag
    a(f'<path d="M80 452 C300 440 520 446 640 452 L640 462 C520 458 300 456 80 466Z" fill="{p["fair2"]}"/>'
      f'<ellipse cx="120" cy="458" rx="34" ry="7" fill="{p["green"]}"/>' + flag(124, 458, 26, p["flag"]))
    # the hole, as the course has it: the tee box at the top, a fairway that bends down to the green,
    # organic edges, a band of first-cut rough, diagonal mowing stripes
    fw = "M786 438 C760 462 690 492 610 522 C540 548 500 562 486 574 L1124 574 C1100 556 1040 530 990 508 C920 478 850 458 826 438Z"
    a(f'<path d="{fw}" fill="none" stroke="{p["fringe"]}" stroke-width="22" stroke-linejoin="round"/><path d="{fw}" fill="{p["fair"]}"/>')
    a(f'<defs><clipPath id="fw2"><path d="{fw}"/></clipPath></defs>')
    # mowing stripes run the length of the hole, converging on the tee
    vx, vy = 806, 420
    a('<g clip-path="url(#fw2)">' + ''.join(f'<path d="M{vx} {vy}L{vx + (k - 6) * 90} 600L{vx + (k - 5.5) * 90} 600Z" fill="{p["fair2"]}"/>' for k in range(0, 13, 2)) + '</g>')
    a(f'<rect x="772" y="434" width="64" height="9" rx="3" fill="{p["green2"]}"/><circle cx="786" cy="438" r="2.4" fill="#f3efe2"/><circle cx="822" cy="438" r="2.4" fill="#f3efe2"/>')
    a(golfer(752, 462, .34, "stand", "#2f5a8a", "#e8e2d0", skin=p["skin"]) + bag(770, 462, .32, "#8a2a2a"))
    # the pond with its footbridge, left
    a(f'<path d="M30 660 Q60 612 200 618 Q330 622 410 660 Q450 700 380 728 Q250 760 110 742 Q20 726 30 660Z" fill="{p["water"]}"/>')
    for x, y, w in [(110, 668, 70), (240, 690, 110), (170, 718, 60), (330, 676, 50)]:
        a(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{p["water2"]}" opacity=".8"/>')
    if n: a('<ellipse cx="230" cy="680" rx="40" ry="10" fill="#f4efdc" opacity=".18"/>')
    for x in (52, 76, 400, 418): a(f'<path d="M{x} 668 q-4 -26 2 -40 M{x + 6} 668 q2 -22 8 -32" stroke="{p["tree2"]}" stroke-width="3" fill="none"/>')
    bw, bw2 = p["wood"], p["wood2"]
    a(f'<path d="M300 708 Q360 668 430 702 L430 712 Q360 680 300 718Z" fill="{bw}"/>')
    a(f'<path d="M300 690 Q360 650 430 684" fill="none" stroke="{bw2}" stroke-width="4"/>')
    for i in range(7):
        t = i / 6; x = 300 + 130 * t; yb = 713 - 40 * 4 * t * (1 - t) * .9; yt = 690 - 40 * 4 * t * (1 - t) * .9 - 2
        a(f'<line x1="{x:.0f}" y1="{yb:.0f}" x2="{x:.0f}" y2="{yt:.0f}" stroke="{bw2}" stroke-width="3"/>')
    a(f'<path d="M430 708 Q450 704 470 700" stroke="{p["path"]}" stroke-width="12" fill="none" stroke-linecap="round"/>')
    # the hole sign, left
    a(sign(268, 512, 230, 46, "18 &#183; DEDUCTIBLE DOGLEG", p, 14, 40, "PAR 4 &#183; 410 YDS"))
    # the cart path from the clubhouse down to the green, and the cart parked on its pull-off
    path = "M1235 506 C1260 540 1380 556 1380 600 C1380 650 1260 660 1172 682"
    a(f'<path d="{path}" fill="none" stroke="{p["path2"]}" stroke-width="34" stroke-linecap="round"/><path d="{path}" fill="none" stroke="{p["path"]}" stroke-width="28" stroke-linecap="round"/>')
    a(cart(1326, 626, 1.0, "#f2efe4" if not n else "#9a988e", p["roof"], "ON PAR"))
    for lx, lb in [(1186, 560), (1430, 592), (1240, 726)]: a(lamp(lx, lb, 54, n))
    # bunkers: a fairway bunker on the bend, greenside bunkers hugging the green's shoulders
    a(bunker2([(640, 506), (700, 496), (724, 508), (676, 520), (636, 516)], p, n))
    a(bunker2([(930, 482), (984, 486), (1006, 498), (958, 504), (924, 494)], p, n))
    a(bunker2([(452, 566), (520, 556), (560, 568), (520, 584), (462, 584)], p, n))
    a(bunker2([(1020, 820), (1100, 812), (1140, 836), (1070, 852), (1010, 846)], p, n))
    # the putting green: kidney-shaped inside its collar, its own cut lines, the podium's stage
    gp = ("M440 690 C430 610 590 574 800 578 C1010 574 1140 606 1132 690 C1126 768 1000 812 820 806 "
          "C700 802 650 776 570 800 C480 822 446 760 440 690Z")
    a(f'<path d="{gp}" fill="{p["fringe"]}" stroke="{p["fringe"]}" stroke-width="30" stroke-linejoin="round"/>')
    a(f'<path d="{gp}" fill="url(#gr)"/>')
    a(f'<defs><clipPath id="gc"><path d="{gp}"/></clipPath></defs><g clip-path="url(#gc)" opacity="{.10 if not n else .06}">'
      + ''.join(f'<rect x="{x}" y="560" width="60" height="270" fill="#fff"/>' for x in range(430, 1150, 120)) + '</g>')
    a(f'<ellipse cx="700" cy="620" rx="210" ry="34" fill="#fff" opacity="{.08 if not n else .04}"/>')
    # the pin at the back of the green
    a(flag(900, 590, 92, p["flag"]))
    # a few tufts in the rough, kept off the stage
    r = random.Random(11); tc = p["rough2"] if not n else "#0e1d15"
    for _ in range(30):
        x = r.randint(0, W); y = r.randint(HZ + 60, 860)
        if 400 < x < 1200 and y > 490: continue
        if x < 460 and 600 < y < 770: continue
        if 1180 < x < 1440 and 500 < y < 700: continue
        a(f'<path d="M{x - 6} {y} l3 -9 l3 7 l3 -10 l3 12" stroke="{tc}" stroke-width="2" fill="none"/>')
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
def base(n, sky=DAYSKY, nt=NIGHTSKY, star=50, extra=''):
    return defs(skyg(n, day=sky, nt=nt) + extra) + f'<rect width="1600" height="{V}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 150, 7) if n else '')

def ground(p, y, c=None):
    return f'<path d="M0 {y} Q400 {y - 10} 800 {y} T1600 {y - 4} L1600 240 L0 240Z" fill="{c or p["rough"]}"/>'

def corners(p, n):
    """darken the corners the title and line sit on"""
    c = p["tree2"]
    return (f'<path d="M0 170 Q200 160 470 186 L470 240 L0 240Z" fill="{c}"/>'
            f'<path d="M1600 176 Q1320 170 1040 196 L1040 240 L1600 240Z" fill="{c}"/>')

def edge_trees(p, left=True, right=True):
    o = []
    if left: o.append(cypress(60, 200, 190, p["cyp"]) + cypress(130, 204, 150, p["cyp"]) + oak(250, 206, 120, p["tree"], p["tree2"], p["trunk"]))
    if right: o.append(oak(1350, 206, 120, p["tree"], p["tree2"], p["trunk"]) + cypress(1470, 204, 160, p["cyp"]) + cypress(1540, 200, 200, p["cyp"]))
    return ''.join(o)

def v_sales(n):  # the tee shot: the ball flying down the fairway
    p = P(n); o = [base(n)]
    o.append(moon(1250, 62, 22) if n else sun(1250, 66, 24))
    o.append(hills([(0, 150), (300, 118), (600, 140), (900, 110), (1200, 134), (1600, 120)], 190, p["far"]))
    o.append(treeline(0, 1600, 172, 12, 22, p["treeline"], 4, 26))
    o.append(ground(p, 168))
    o.append(f'<path d="M560 240 C700 210 900 190 1100 172 L1180 172 C1120 190 1000 214 900 240Z" fill="{p["fair"]}"/>')
    o.append(f'<ellipse cx="1150" cy="172" rx="60" ry="8" fill="{p["green"]}"/>' + flag(1160, 172, 30, p["flag"]))
    o.append(f'<path d="M420 214 L700 214 L720 232 L400 232Z" fill="{p["fair2"]}"/>')
    o.append('<circle cx="470" cy="214" r="6" fill="#d8402a"/><circle cx="650" cy="214" r="6" fill="#d8402a"/>')
    o.append(golfer(560, 222, 1.7, "swing", "#2f5a8a", "#e8e2d0", skin=p["skin"]))
    pts = [(600, 210)]
    for i in range(1, 15):
        t = i / 14; pts.append((600 + 520 * t, 210 - 180 * t * (1 - t) * 1.25 - 20 * t))
    for x, y in pts[2:-1]: o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2" fill="#fff" opacity=".75"/>')
    o.append(ball(int(pts[10][0]), int(pts[10][1]), 6))
    o.append(f'<line x1="{pts[10][0] - 20:.0f}" y1="{pts[10][1] + 3:.0f}" x2="{pts[10][0] - 8:.0f}" y2="{pts[10][1] + 1:.0f}" stroke="#fff" stroke-width="2" opacity=".6"/>')
    if not n: o.append(bird(400, 70, 1.1, "#4a4a5a") + bird(430, 58, .8, "#4a4a5a"))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_messages(n):  # the starter's shack and the scoreboard
    p = P(n); o = [base(n)]
    o.append(moon(300, 60, 20) if n else sun(300, 66, 22))
    o.append(treeline(0, 1600, 160, 16, 30, p["treeline"], 5, 30))
    o.append(ground(p, 156))
    # the starter's shack
    sx = 600
    o.append(f'<rect x="{sx}" y="110" width="150" height="90" fill="{p["wall"]}"/><path d="M{sx - 14} 112 L{sx + 75} 70 L{sx + 164} 112Z" fill="{p["roof"]}"/>')
    if n: o.append(f'<circle cx="{sx + 75}" cy="146" r="60" fill="url(#glow)"/>')
    o.append(f'<rect x="{sx + 20}" y="126" width="110" height="36" fill="{p["win"]}" stroke="{p["trim"]}" stroke-width="4"/><rect x="{sx + 14}" y="162" width="122" height="8" fill="{p["trim"]}"/>')
    o.append(f'<rect x="{sx + 22}" y="88" width="106" height="18" rx="3" fill="{p["roof2"]}"/><text x="{sx + 75}" y="102" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="{p["ink"]}" letter-spacing="2">STARTER</text>')
    o.append(golfer(sx + 75, 162, .7, "stand", "#c8452a", "#2e3a4c", skin=p["skin"]).replace('<line x1="12" y1="-34" x2="18" y2="0" stroke="#c9ccd2" stroke-width="2.4"/>', ''))
    o.append(bag(sx + 190, 198, .8, "#2f5a8a") + bag(sx + 214, 198, .8, "#8a2a2a"))
    # the scoreboard
    bx = 890; bd = "#1f4a30" if not n else "#12281b"
    o.append(f'<rect x="{bx + 20}" y="150" width="10" height="56" fill="{p["wood2"]}"/><rect x="{bx + 330}" y="150" width="10" height="56" fill="{p["wood2"]}"/>')
    o.append(f'<rect x="{bx}" y="52" width="360" height="110" rx="4" fill="{bd}" stroke="{p["wood"]}" stroke-width="6"/>')
    o.append(f'<rect x="{bx + 12}" y="60" width="336" height="20" fill="#f6f2e4"/><text x="{bx + 180}" y="75" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="#1f4a30" letter-spacing="2">NO LAPSE LEADERS</text>')
    for i, sc in enumerate(["-4", "-3", "-2", "-1"]):
        y = 86 + i * 18
        o.append(f'<rect x="{bx + 16}" y="{y}" width="{200 - i * 24}" height="12" fill="#f6f2e4" opacity=".85"/><rect x="{bx + 296}" y="{y}" width="40" height="12" fill="#f6f2e4"/>'
                 f'<text x="{bx + 316}" y="{y + 11}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="#c8302a">{sc}</text>')
    o.append(f'<path d="M{bx + 380} 70 q14 -14 30 0 M{bx + 372} 58 q22 -24 46 0" fill="none" stroke="#fff" stroke-width="3" opacity=".7"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_coaching(n):  # the practice range, a pro coaching a player
    p = P(n); o = [base(n, sky=("#5a90c8", "#b8d8ec", "#f2eed6"))]
    o.append(moon(1280, 60, 20) if n else sun(1280, 62, 22))
    o.append(treeline(0, 1600, 140, 14, 26, p["treeline"], 6, 28))
    o.append(ground(p, 136, p["fair"]))
    for i, (x, y) in enumerate([(820, 130), (1000, 126), (1160, 134), (700, 128)]):
        o.append(flag(x, y, 22, ["#d8402a", "#e9c75a", "#2f7ad0", "#fff"][i], cup=False))
    r = random.Random(4)
    for _ in range(24): o.append(f'<circle cx="{r.randint(560, 1240)}" cy="{r.randint(140, 180)}" r="2" fill="#fff" opacity=".85"/>')
    o.append(f'<rect x="460" y="196" width="680" height="18" fill="{p["fair2"]}"/>')
    for x in (520, 760): o.append(f'<rect x="{x}" y="190" width="120" height="10" fill="#3a6a3a"/>')
    o.append(golfer(590, 192, 1.45, "swing", "#e9c75a", "#2e3a4c", skin=p["skin"]))
    o.append(golfer(720, 192, 1.45, "point", "#1f5a35", "#e8e2d0", cap="#1f5a35", flip=True, skin=p["skin"]))
    o.append(f'<path d="M640 186 L660 196 L680 186Z" fill="#a8752a"/><rect x="640" y="182" width="40" height="8" fill="#a8752a"/>')
    for x in range(646, 678, 7): o.append(ball(x, 180, 3))
    o.append(f'<path d="M680 72 q-8 -24 30 -26 h70 q24 0 24 18 q0 18 -24 18 h-60 l-20 12z" fill="#fff" opacity=".92"/>'
             '<path d="M712 64 l10 -10 l10 10 l10 -10 l10 10" stroke="#1f5a35" stroke-width="3" fill="none"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_roleplay(n):  # the putting practice green
    p = P(n); o = [base(n, sky=("#5a90c8", "#c6dfe8", "#f6eccc"))]
    o.append(moon(1240, 58, 20) if n else sun(1240, 62, 22))
    o.append(treeline(0, 1600, 130, 14, 26, p["treeline"], 8, 28))
    o.append(ground(p, 126))
    o.append(f'<ellipse cx="800" cy="180" rx="440" ry="56" fill="{p["fringe"]}"/><ellipse cx="800" cy="180" rx="424" ry="48" fill="{p["green"]}"/>')
    for i, (x, y) in enumerate([(560, 168), (720, 152), (1010, 160), (1130, 186), (880, 200)]):
        o.append(flag(x, y, 34, ["#d8402a", "#e9c75a", "#2f7ad0", "#d8402a", "#e9c75a"][i]))
    for x, y in [(600, 182), (760, 176), (980, 182), (1080, 200)]: o.append(ball(x, y, 3.5))
    o.append(golfer(820, 206, 1.3, "putt", "#2f7ad0", "#e8e2d0", skin=p["skin"]) + ball(844, 205, 3.5))
    o.append(f'<path d="M846 205 Q900 196 960 200" stroke="#fff" stroke-width="2" stroke-dasharray="4 6" fill="none" opacity=".7"/>')
    o.append(golfer(690, 204, 1.25, "stand", "#c8452a", "#2e3a4c", skin=p["skin"]))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_rphistory(n):  # the clubhouse scorecard wall
    o = [defs()]
    wd = "#6e4a2c" if not n else "#26190f"; wd2 = "#5c3c22" if not n else "#1c120a"
    o.append(f'<rect width="1600" height="{V}" fill="{wd}"/>')
    for x in range(0, 1600, 80): o.append(f'<rect x="{x}" y="0" width="3" height="{V}" fill="{wd2}"/>')
    o.append(f'<rect x="0" y="176" width="1600" height="12" fill="{wd2}"/>')
    card = "#f6f1e0" if not n else "#bdb59c"; ln = "#7a9a7a" if not n else "#5a6e5a"
    r = random.Random(9)
    for i, (x, y, rot) in enumerate([(470, 50, -3), (600, 64, 2), (1000, 52, -2), (1130, 66, 3)]):
        o.append(f'<g transform="rotate({rot} {x + 55} {y + 40})"><rect x="{x - 6}" y="{y - 6}" width="122" height="92" fill="#c9a24a"/><rect x="{x}" y="{y}" width="110" height="80" fill="{card}"/>')
        o.append(f'<rect x="{x}" y="{y}" width="110" height="14" fill="#1f5a35"/>')
        for k in range(1, 5): o.append(f'<line x1="{x}" y1="{y + 14 + k * 13}" x2="{x + 110}" y2="{y + 14 + k * 13}" stroke="{ln}" stroke-width="1"/>')
        for k in range(1, 6): o.append(f'<line x1="{x + k * 18}" y1="{y + 14}" x2="{x + k * 18}" y2="{y + 80}" stroke="{ln}" stroke-width="1"/>')
        for k in range(5):
            o.append(f'<circle cx="{x + 9 + r.randint(0, 5) * 18}" cy="{y + 21 + r.randint(0, 4) * 13}" r="4" fill="none" stroke="#c8302a" stroke-width="1.5"/>')
        o.append('</g>')
    # the replay screen
    o.append(f'<rect x="730" y="40" width="240" height="132" rx="6" fill="#1a1a1a"/><rect x="740" y="50" width="220" height="112" fill="{"#7fb2e0" if not n else "#2a4a7a"}"/>')
    o.append(f'<path d="M740 130 Q850 110 960 126 L960 162 L740 162Z" fill="#6fae52"/><ellipse cx="900" cy="128" rx="30" ry="6" fill="#9ed06a"/>' + flag(906, 128, 26, "#d8402a"))
    o.append(golfer(790, 150, .7, "swing", "#e9c75a", "#2e3a4c"))
    o.append('<path d="M812 104 Q860 70 900 122" stroke="#fff" stroke-width="2" stroke-dasharray="3 5" fill="none"/>')
    o.append('<path d="M760 64 l14 8 l-14 8z" fill="#fff" opacity=".9"/><rect x="740" y="156" width="220" height="6" fill="#000" opacity=".4"/><rect x="740" y="156" width="130" height="6" fill="#d8402a"/>')
    o.append(f'<path d="M1300 176 L1310 120 L1350 120 L1360 176Z" fill="#c9a24a"/><path d="M1312 120 q18 -40 36 0z" fill="#e2c26a"/><rect x="1298" y="168" width="64" height="8" fill="#8a6a2a"/>')
    if n: o.append('<circle cx="850" cy="110" r="300" fill="#7fb2e0" opacity=".08"/>')
    o.append(f'<rect x="0" y="188" width="1600" height="52" fill="{wd2}" opacity=".7"/>')
    return vwrap(''.join(o))

def v_training(n):  # the driving range with distance markers
    p = P(n); o = [base(n)]
    o.append(moon(300, 56, 20) if n else sun(300, 60, 22))
    o.append(hills([(0, 120), (400, 100), (800, 116), (1200, 96), (1600, 112)], 140, p["far"]))
    o.append(treeline(0, 1600, 126, 10, 20, p["treeline"], 9, 24))
    o.append(f'<path d="M0 122 L1600 122 L1600 240 L0 240Z" fill="{p["fair"]}"/>')
    for i, y in enumerate([122, 128, 136, 148, 164, 186, 214, 240]):
        if i % 2 == 0 and i < 7: o.append(f'<rect x="0" y="{y}" width="1600" height="{[128, 136, 148, 164, 186, 214, 240][i] - y}" fill="{p["fair2"]}"/>')
    for x, y, s, t in [(1090, 128, .5, "250"), (980, 136, .62, "200"), (850, 150, .8, "150"), (700, 170, 1.0, "100")]:
        o.append(f'<g transform="translate({x} {y}) scale({s})"><rect x="-3" y="-44" width="6" height="44" fill="{p["wood2"]}"/><rect x="-30" y="-74" width="60" height="32" rx="4" fill="#f6f2e4" stroke="#1f5a35" stroke-width="3"/>'
                 f'<text x="0" y="-51" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#1f5a35">{t}</text></g>')
    r = random.Random(12)
    for _ in range(36):
        y = r.randint(130, 196); o.append(f'<circle cx="{r.randint(480, 1180)}" cy="{y}" r="{1.5 + (y - 130) / 40:.1f}" fill="#fff" opacity=".9"/>')
    for x in (480, 600, 720, 840, 960):
        o.append(f'<rect x="{x}" y="206" width="90" height="10" fill="#3a6a3a"/>')
    o.append(golfer(530, 208, 1.1, "address", "#c8452a", "#2e3a4c", skin=p["skin"]) + ball(558, 206, 3))
    o.append(golfer(650, 208, 1.1, "swing", "#2f7ad0", "#e8e2d0", skin=p["skin"]))
    o.append(f'<path d="M670 180 Q740 96 820 120" stroke="#fff" stroke-width="2" stroke-dasharray="3 6" fill="none" opacity=".8"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the yardage-book page: one hole, top down, with the route through four stops
    rough = "#2f5a36" if not n else "#0f1f16"; rough2 = "#295030" if not n else "#0c1a12"
    fair = "#7fb558" if not n else "#2a4f34"; green = "#a6d872" if not n else "#3a6a44"
    sand = "#eedfb2" if not n else "#6a6658"; water = "#4f97c4" if not n else "#1d3a66"
    route = ("#8fd0ff" if not n else "#8fd0ff") if athena else ("#ffd25a" if not n else "#ffd25a")
    o = [f'<rect width="1600" height="{V}" fill="{rough}"/>']
    for y in range(0, V, 16): o.append(f'<rect x="0" y="{y}" width="1600" height="8" fill="{rough2}"/>')
    # the hole: tee left, dogleg, green right
    o.append(f'<path d="M430 176 C500 140 560 120 650 96 C760 70 820 130 910 130 C1010 130 1040 70 1120 58 L1150 86 C1070 98 1040 172 910 170 C800 168 760 116 670 134 C590 150 520 172 470 200Z" fill="{fair}"/>')
    o.append(f'<rect x="416" y="172" width="50" height="28" rx="6" fill="{fair}" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>')
    o.append(f'<ellipse cx="1150" cy="70" rx="46" ry="32" fill="{green}" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>' + flag(1156, 72, 30, "#d8402a"))
    o.append(f'<path d="M720 186 Q790 168 860 190 Q830 214 760 210 Q710 204 720 186Z" fill="{water}"/>')
    for cx, cy, rx, ry in [(600, 76, 30, 12), (1040, 150, 28, 12), (1200, 106, 22, 10), (950, 92, 24, 10)]:
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{sand}"/>')
    for x, y in [(500, 56), (820, 60), (1230, 170), (380, 110), (1000, 200), (1300, 50)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="#1c3a22" opacity=".8"/><circle cx="{x + 14}" cy="{y + 6}" r="12" fill="#1c3a22" opacity=".8"/>')
    pts = [(520, 154), (700, 106), (900, 150), (1090, 84)]
    d = f'M440 186 C470 172 490 164 {pts[0][0]} {pts[0][1]} S640 108 {pts[1][0]} {pts[1][1]} S840 152 {pts[2][0]} {pts[2][1]} S1040 86 {pts[3][0]} {pts[3][1]} S1140 70 1150 72'
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="5" stroke-dasharray="3 11" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    yards = ["410", "290", "150", "40"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        ty = y - 24
        o.append(f'<circle cx="{x}" cy="{y}" r="14" fill="{route}" stroke="#14301c" stroke-width="4"/><text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#14301c">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="22" fill="#fff" stroke="#10241a" stroke-width="5" paint-order="stroke">{t}</text>')
        o.append(f'<text x="{x}" y="{y + 32}" text-anchor="middle" font-family="monospace" font-size="12" fill="#fff" opacity=".75">{yards[i]}</text>')
    o.append('<g transform="translate(1250 70)"><circle r="30" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/><path d="M0 -26 L6 0 L0 26 L-6 0Z" fill="#fff" opacity=".8"/>'
             f'<path d="M0 -26 L6 0 L-6 0Z" fill="{route}"/><text y="-34" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="12" fill="#fff">N</text></g>')
    o.append('<text x="420" y="50" font-family="Georgia, serif" font-style="italic" font-size="16" fill="#fff" opacity=".7">'
             + ('hole 2 &#183; the service dogleg' if athena else 'hole 1 &#183; the sales dogleg') + '</text>')
    o.append('<rect x="0" y="0" width="1600" height="240" fill="none" stroke="#fff" stroke-width="6" opacity=".25"/>')
    return vwrap(''.join(o))

def v_service(n):  # the greenskeepers keeping the course
    p = P(n); o = [base(n, sky=("#5a90c8", "#bcd9ea", "#f2ead2"))]
    o.append(moon(1300, 56, 20) if n else sun(1300, 60, 22))
    o.append(treeline(0, 1600, 136, 14, 28, p["treeline"], 10, 28))
    o.append(ground(p, 132, p["fair"]))
    for i in range(6): o.append(f'<path d="M{440 + i * 60} 240 L{700 + i * 34} 136 L{730 + i * 34} 136 L{500 + i * 60} 240Z" fill="{p["fair2"]}"/>' if i % 2 == 0 else '')
    # riding mower
    mx, my = 620, 196
    o.append(f'<g transform="translate({mx} {my})"><rect x="-50" y="-22" width="90" height="20" rx="6" fill="#d8402a"/><rect x="-20" y="-40" width="26" height="20" rx="4" fill="#3a3a3a"/>'
             f'<rect x="-56" y="-4" width="100" height="8" fill="#5a5a5a"/><circle cx="-36" cy="4" r="12" fill="#222"/><circle cx="30" cy="6" r="10" fill="#222"/><path d="M14 -24 L26 -44" stroke="#3a3a3a" stroke-width="4"/></g>')
    o.append(golfer(mx - 8, my - 6, .9, "stand", "#e9c75a", "#3a4a3a", cap="#e9c75a", skin=p["skin"]).replace('<line x1="12" y1="-34" x2="18" y2="0" stroke="#c9ccd2" stroke-width="2.4"/>', '')
             .replace('<path d="M-6 0 L-3 -30 M7 0 L3 -30"', '<path d="M-6 -24 L-3 -30 M7 -24 L3 -30"'))
    # raking a bunker
    o.append(bunker(900, 196, 90, 20, p))
    o.append(golfer(930, 200, 1.0, "stand", "#e9c75a", "#3a4a3a", cap="#e9c75a", skin=p["skin"]).replace('<line x1="12" y1="-34" x2="18" y2="0" stroke="#c9ccd2" stroke-width="2.4"/>', ''))
    o.append(f'<line x1="942" y1="166" x2="880" y2="204" stroke="{p["wood"]}" stroke-width="4"/><path d="M866 200 L894 208" stroke="#7a7a7a" stroke-width="5"/>')
    for k in range(4): o.append(f'<path d="M840 {196 + k * 4} q30 -4 60 0" stroke="{p["sand2"]}" stroke-width="1.5" fill="none"/>')
    # changing the cup on the green
    o.append(f'<ellipse cx="1110" cy="174" rx="120" ry="20" fill="{p["green"]}"/>' + flag(1080, 172, 40, p["flag"]))
    o.append(golfer(1150, 182, .9, "crouch", "#e9c75a", "#3a4a3a", cap="#e9c75a", skin=p["skin"]))
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # the course in spring bloom
    p = P(n); o = [base(n, sky=("#6aa6d8", "#c2e0f0", "#f6f0d6"))]
    o.append(moon(1260, 56, 20) if n else sun(1260, 60, 22))
    o.append(hills([(0, 130), (400, 104), (800, 124), (1200, 100), (1600, 124)], 160, p["far"]))
    o.append(treeline(0, 1600, 150, 12, 22, p["treeline"], 11, 26))
    o.append(ground(p, 146, p["fair"]))
    bl = ["#f4a8c4", "#f8d0de", "#ffffff"] if not n else ["#8a5a74", "#9a7486", "#a8a0b0"]
    r = random.Random(14)
    for x, b, h in [(520, 196, 120), (700, 180, 100), (930, 186, 110), (1130, 196, 120)]:
        o.append(f'<path d="M{x - 4} {b} L{x - 2} {b - h * .45:.0f} L{x + 2} {b - h * .45:.0f} L{x + 4} {b}Z" fill="{p["trunk"]}"/>')
        for _ in range(12):
            o.append(f'<circle cx="{x + r.randint(-int(h * .4), int(h * .4))}" cy="{b - h * .5 + r.randint(-int(h * .3), int(h * .2)):.0f}" r="{r.randint(10, 18)}" fill="{r.choice(bl)}"/>')
    o.append(f'<ellipse cx="820" cy="212" rx="150" ry="18" fill="{p["green"]}"/>' + flag(840, 210, 40, p["flag"]))
    for _ in range(46):
        x = r.choice([r.randint(420, 700), r.randint(960, 1200)]); y = r.randint(200, 226)
        o.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{r.choice(["#f2d14a", "#e86a8a", "#f7f3e8", "#9b7fe0"] if not n else ["#a89a5a", "#8a5a6a", "#a8a4b0"])}"/>')
    for _ in range(10):
        o.append(f'<circle cx="{r.randint(460, 1180)}" cy="{r.randint(60, 150)}" r="3" fill="{bl[0]}" opacity=".8"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_claims(n):  # after the storm: a fallen branch on the fairway, the crew clearing it
    p = P(n); o = [base(n, sky=("#6a7890", "#a8b4c0", "#e2dccc"), nt=("#05070f", "#121828", "#222a3e"), star=20)]
    for x in (300, 760, 1240): o.append(f'<ellipse cx="{x}" cy="46" rx="220" ry="24" fill="{"#8590a4" if not n else "#1c2234"}"/>')
    if not n: o.append('<circle cx="1100" cy="70" r="40" fill="#fff6d8" opacity=".5"/>')
    o.append(treeline(0, 1600, 140, 14, 28, p["treeline"], 12, 28))
    o.append(ground(p, 136, p["fair"]))
    for x, y, w in [(560, 206, 90), (1020, 214, 70), (760, 222, 60)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="{"#9ab4c8" if not n else "#2a3a5a"}" opacity=".8"/>')
    # the broken oak and its branch across the fairway
    o.append(f'<path d="M640 200 L646 96 L676 96 L686 200Z" fill="{p["trunk"]}"/><path d="M646 110 L630 92 L660 100Z" fill="{p["trunk"]}"/>')
    o.append(f'<circle cx="640" cy="80" r="40" fill="{p["tree2"]}"/><circle cx="676" cy="70" r="32" fill="{p["tree"]}"/>')
    o.append(f'<path d="M690 190 L960 172 L962 182 L692 200Z" fill="{p["trunk"]}"/><path d="M820 180 L860 150 M900 176 L940 146 M760 186 L780 160" stroke="{p["trunk"]}" stroke-width="6"/>')
    for x, y, rr in [(860, 150, 22), (940, 146, 26), (780, 160, 18), (990, 172, 22)]: o.append(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{p["tree"]}"/>')
    # the crew
    o.append(golfer(1040, 204, 1.0, "stand", "#e98a2a", "#3a4a3a", cap="#f2c230", flip=True, skin=p["skin"]).replace('<line x1="12" y1="-34" x2="18" y2="0" stroke="#c9ccd2" stroke-width="2.4"/>', ''))
    o.append('<g transform="translate(1012 172) rotate(-14)"><rect x="-18" y="-6" width="22" height="12" rx="3" fill="#e98a2a"/><rect x="-46" y="-3" width="30" height="6" fill="#9a9a9a"/></g>')
    o.append(golfer(560, 202, 1.0, "point", "#e98a2a", "#3a4a3a", cap="#f2c230", skin=p["skin"]))
    o.append(f'<g transform="translate(1160 204)"><path d="M-30 -24 L30 -24 L22 -4 L-22 -4Z" fill="#2f6a4a"/><circle cx="0" cy="0" r="8" fill="#222"/><path d="M22 -20 L50 -34" stroke="#5a5a5a" stroke-width="4"/>'
             f'<path d="M-24 -24 L-14 -36 L4 -30 L18 -38 L26 -24Z" fill="{p["trunk"]}"/></g>')
    o.append('<path d="M460 196 L470 170 L480 196Z M1240 200 L1250 174 L1260 200Z" fill="#e98a2a"/><rect x="462" y="184" width="16" height="4" fill="#fff"/><rect x="1242" y="188" width="16" height="4" fill="#fff"/>')
    o.append(edge_trees(p))
    o.append(corners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the clubhouse pro shop
    p = P(n); o = [base(n)]
    o.append(moon(1300, 54, 20) if n else sun(1300, 58, 22))
    o.append(treeline(0, 1600, 170, 16, 30, p["treeline"], 13, 30))
    o.append(ground(p, 196, p["path"]))
    wall = p["wall"]; x0, x1 = 540, 1080
    o.append(f'<rect x="{x0}" y="70" width="{x1 - x0}" height="128" fill="{wall}"/><path d="M{x0 - 24} 72 L{x0 + 40} 30 L{x1 - 40} 30 L{x1 + 24} 72Z" fill="{p["roof"]}"/><rect x="{x0 - 26}" y="68" width="{x1 - x0 + 52}" height="7" fill="{p["trim"]}"/>')
    o.append(f'<rect x="{x0 + 150}" y="80" width="240" height="22" rx="3" fill="{p["roof2"]}"/><text x="{(x0 + x1) // 2}" y="96" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="14" fill="{p["ink"]}" letter-spacing="3">PRO SHOP</text>')
    for i in range(10):
        c = "#1f5a35" if i % 2 == 0 else "#f6f2e4"
        o.append(f'<path d="M{x0 + 10 + i * 52} 108 L{x0 + 62 + i * 52} 108 L{x0 + 62 + i * 52} 124 Q{x0 + 36 + i * 52} 132 {x0 + 10 + i * 52} 124Z" fill="{c}"/>')
    for wx in (x0 + 24, x1 - 184):
        if n: o.append(f'<circle cx="{wx + 80}" cy="160" r="90" fill="url(#glow)"/>')
        o.append(f'<rect x="{wx}" y="132" width="160" height="56" fill="{p["win"]}" stroke="{p["trim"]}" stroke-width="4"/>')
    o.append(bag(x0 + 64, 186, .8, "#2f5a8a") + bag(x0 + 104, 186, .8, "#8a2a2a") + bag(x0 + 144, 186, .8, "#1f5a35"))
    o.append(f'<rect x="{x1 - 160}" y="150" width="120" height="6" fill="{p["trim"]}"/>')
    for k in range(4): o.append(f'<rect x="{x1 - 150 + k * 28}" y="158" width="18" height="24" rx="3" fill="{["#e9c75a", "#fff", "#d8402a", "#2f7ad0"][k]}"/>')
    o.append(f'<rect x="{(x0 + x1) // 2 - 30}" y="136" width="60" height="62" fill="{p["win"] if n else p["wood"]}"/>')
    o.append(edge_trees(p, right=False) + cypress(1470, 204, 160, p["cyp"]) + cypress(1540, 200, 200, p["cyp"]))
    o.append(corners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the tee shot: premium down the fairway"],
    "messages": ["Texts & Emails", "the starter: every reply on the board"],
    "coaching": ["Coaching", "the range: every swing, looked at"],
    "roleplay": ["Role Play", "the practice green: putt it till it drops"],
    "rphistory": ["Session History", "the scorecard wall: every round, kept"],
    "training": ["Training", "the driving range: learn your yardages"],
    "blueprint": ["Apollo's Road Map", "the yardage book, in plain words"],
    "athenamap": ["Athena's Road Map", "the service yardage book, in plain words"],
    "service": ["Service Digest", "the greenskeepers: keeping the book in shape"],
    "renewals": ["Renewals", "spring on the course: what came back"],
    "claims": ["Claims", "the grounds crew: after the storm"],
    "commercial": ["Commercial Center", "the pro shop: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=30):
    return (defs(skyg(n, day=day, nt=nt)) + f'<rect width="1600" height="{S}" fill="url(#g)"/>' + (stars(star, 0, 1600, 0, 90, 21) if n else ''))

def green_band(p, y=112, c=None):
    return f'<path d="M0 {y} Q800 {y - 14} 1600 {y} L1600 160 L0 160Z" fill="{c or p["green"]}"/>'

def s_sold(n):  # hole in one: the ball dropping in, the flag, a confetti burst
    p = P(n); o = [sbase(n, ("#e09a3a", "#f6c66a", "#fde6a8"), ("#0a1030", "#1a2858", "#3a3a6a"))]
    for i in range(16):
        ang = i / 16 * 2 * math.pi
        o.append(f'<path d="M780 96 L{780 + 700 * math.cos(ang):.0f} {96 + 700 * math.sin(ang):.0f} L{780 + 700 * math.cos(ang + .12):.0f} {96 + 700 * math.sin(ang + .12):.0f}Z" fill="#fff" opacity="{.18 if not n else .07}"/>')
    o.append(treeline(0, 1600, 100, 10, 20, p["treeline"], 31, 30))
    o.append(green_band(p, 100))
    o.append('<ellipse cx="780" cy="108" rx="24" ry="7" fill="#1a1a14"/>')
    o.append(flag(788, 108, 64, p["flag"], cup=False))
    o.append(ball(776, 100, 8) + '<path d="M752 62 L764 84 M776 56 L776 82 M800 62 L788 84" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".85"/>')
    r = random.Random(5)
    for _ in range(34):
        x = r.randint(520, 1060); y = r.randint(30, 100)
        o.append(f'<rect x="{x}" y="{y}" width="6" height="10" fill="{r.choice(["#ffd27a", "#5ec97a", "#e2552b", "#7fb2e8", "#fff"])}" transform="rotate({r.randint(0, 90)} {x} {y})"/>')
    return wrap(S, ''.join(o))

def s_open(n):  # the ball on the green, short of the cup, flag in
    p = P(n); o = [sbase(n, ("#4f8ac4", "#a2cce6", "#eaf0dc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(treeline(0, 1600, 96, 12, 22, p["treeline"], 32, 28))
    o.append(green_band(p, 96))
    o.append(f'<ellipse cx="800" cy="112" rx="420" ry="20" fill="{p["green2"]}" opacity=".5"/>')
    o.append('<ellipse cx="900" cy="106" rx="18" ry="5.5" fill="#1a1a14"/>' + flag(904, 106, 62, p["flag"], cup=False))
    o.append(ball(800, 108, 8) + '<path d="M500 116 Q640 106 752 108" stroke="#fff" stroke-width="2" stroke-dasharray="4 7" fill="none" opacity=".6"/>'.replace("752 108", "790 108"))
    return wrap(S, ''.join(o))

def s_lost(n):  # the ball splashing into the water hazard, grey sky
    p = P(n); o = [sbase(n, ("#6a6e78", "#9a9ea6", "#c4c6ca"), ("#0a0c14", "#1a1d28", "#2a2d3a"), 8)]
    for x in (300, 720, 1150): o.append(f'<ellipse cx="{x}" cy="34" rx="210" ry="22" fill="{"#7a7e88" if not n else "#20232e"}"/>')
    o.append(treeline(0, 1600, 92, 10, 20, "#4a5a4c" if not n else "#121a18", 33, 30))
    o.append(f'<rect x="0" y="88" width="1600" height="72" fill="{"#6a8060" if not n else "#18241c"}"/>')
    wt = "#6f8a9c" if not n else "#1e2e44"
    o.append(f'<path d="M420 160 Q440 98 800 96 Q1160 98 1180 160Z" fill="{wt}"/>')
    for rx in (24, 46, 70): o.append(f'<ellipse cx="800" cy="112" rx="{rx}" ry="{rx * .22:.0f}" fill="none" stroke="#fff" stroke-opacity="{.6 - rx / 160:.2f}" stroke-width="2"/>')
    o.append('<path d="M800 108 Q794 84 786 72 M800 108 Q802 80 802 66 M800 108 Q808 84 818 74" stroke="#dfe8ee" stroke-width="3" fill="none" stroke-linecap="round"/>')
    for x, y in [(780, 64), (824, 68), (804, 56), (770, 80), (830, 82)]: o.append(f'<circle cx="{x}" cy="{y}" r="3" fill="#dfe8ee"/>')
    for x in (520, 1080): o.append(f'<path d="M{x} 120 q-3 -26 3 -40 M{x + 8} 122 q2 -22 8 -34" stroke="{"#4a5a4c" if not n else "#121a18"}" stroke-width="3" fill="none"/>')
    return wrap(S, ''.join(o))

def s_dead(n):  # the ball deep in a sand bunker
    p = P(n); o = [sbase(n, ("#8a9aa4", "#bcc6cc", "#e2e2d8"), ("#0c0e14", "#1c1f28", "#30333e"), 10)]
    o.append(treeline(0, 1600, 80, 12, 22, p["treeline"], 34, 28))
    o.append(f'<rect x="0" y="76" width="1600" height="84" fill="{p["rough"]}"/>')
    o.append(f'<path d="M430 160 Q430 70 800 68 Q1170 70 1170 160Z" fill="{p["sand2"]}"/><path d="M450 160 Q460 84 800 82 Q1140 84 1150 160Z" fill="{p["sand"]}"/>')
    o.append(f'<path d="M440 76 Q800 54 1160 76 L1170 84 Q800 66 430 84Z" fill="{p["fringe"]}"/>')
    for k in range(5): o.append(f'<path d="M{560 + k * 10} {120 + k * 7} Q800 {100 + k * 7} {1040 - k * 10} {120 + k * 7}" stroke="{p["sand2"]}" stroke-width="1.5" fill="none" opacity=".7"/>')
    o.append(f'<ellipse cx="820" cy="106" rx="20" ry="6" fill="{p["sand2"]}"/>' + ball(820, 100, 8))
    o.append(f'<line x1="980" y1="90" x2="1080" y2="60" stroke="{p["wood"]}" stroke-width="4"/><path d="M968 84 L992 98" stroke="#7a7a7a" stroke-width="6"/>')
    return wrap(S, ''.join(o))

def s_reached(n):  # two golfers chatting on the tee
    p = P(n); o = [sbase(n, ("#5f97c9", "#a8d0ea", "#eef0dc"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(treeline(0, 1600, 98, 12, 24, p["treeline"], 35, 28))
    o.append(f'<rect x="0" y="94" width="1600" height="66" fill="{p["rough"]}"/><path d="M560 128 L1040 128 L1060 146 L540 146Z" fill="{p["fair"]}"/>')
    o.append('<circle cx="600" cy="128" r="5" fill="#2f7ad0"/><circle cx="1000" cy="128" r="5" fill="#2f7ad0"/>')
    o.append(golfer(720, 136, 1.2, "stand", "#c8452a", "#2e3a4c", skin=p["skin"]) + golfer(880, 136, 1.2, "stand", "#2f7ad0", "#e8e2d0", flip=True, skin=p["skin"]))
    o.append('<path d="M740 64 q8 -14 24 -14 h20 q16 0 16 14 q0 12 -16 12 h-24 l-10 8z" fill="#fff" opacity=".92"/><path d="M860 56 q-8 -14 -24 -14 h-20 q-16 0 -16 14 q0 12 16 12 h24 l10 8z" fill="#fff" opacity=".92"/>')
    for x in (756, 770, 784): o.append(f'<circle cx="{x}" cy="63" r="2.6" fill="#3a5a3a"/>')
    for x in (816, 830, 844): o.append(f'<circle cx="{x}" cy="55" r="2.6" fill="#3a5a3a"/>')
    o.append(bag(980, 134, .7, "#1f5a35"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # a golfer lining up a putt
    p = P(n); o = [sbase(n, ("#d98a4a", "#f2c27a", "#fbe6b8"), ("#050a1a", "#0f1d3d", "#27375e"))]
    o.append(treeline(0, 1600, 94, 12, 22, p["treeline"], 36, 28))
    o.append(green_band(p, 94))
    o.append(golfer(680, 130, 1.45, "crouch", "#e9c75a", "#2e3a4c", skin=p["skin"]))
    o.append(ball(760, 126, 7) + '<path d="M768 126 Q860 112 950 118" stroke="#fff" stroke-width="2" stroke-dasharray="3 7" fill="none" opacity=".6"/>')
    o.append('<ellipse cx="960" cy="118" rx="11" ry="3.5" fill="#1a1a14"/>' + flag(960, 118, 60, p["flag"], cup=False))
    return wrap(S, ''.join(o))

def s_vm(n):  # an empty course at night, the flag still under the moon
    p = P(True); o = [sbase(True, ("#1a2850", "#2a3a6a", "#4a5a8a"), ("#04060f", "#0a0f24", "#141a38"), 50)]
    if not n: o.append(stars(20, 0, 1600, 0, 80, 22))
    o.append(moon(620, 60, 18))
    o.append(treeline(0, 1600, 98, 12, 24, "#0a1616", 37, 28))
    o.append(green_band(p, 98, "#1b3626"))
    o.append('<ellipse cx="620" cy="114" rx="80" ry="6" fill="#f4efdc" opacity=".08"/>')
    o.append('<ellipse cx="860" cy="110" rx="10" ry="3.5" fill="#05080a"/>' + flag(860, 110, 62, "#9a3428", cup=False))
    o.append(cypress(1080, 104, 90, "#081212") + cypress(1120, 104, 70, "#081212") + cypress(440, 104, 80, "#081212"))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}
# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Fore! The leads are flying, {n}.", "Keep it on the fairway, {n}.", "Tee time, {n}.", "Grip it and quote it, {n}.",
             "Every putt counts, {n}.", "Hit 'em straight today, {n}.", "Play it as it lies, {n}.", "Aim for the pin, {n}.",
             "Nice and easy through the ball, {n}.", "Fairways and full coverage, {n}.", "Stay out of the bunkers, {n}.",
             "The green is waiting, {n}.", "Read the line, then roll it, {n}.", "One good swing at a time, {n}.",
             "Drive for show, close for dough, {n}."]

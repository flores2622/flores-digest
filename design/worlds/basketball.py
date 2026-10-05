"""The Basketball world: one arena on game night. Colour looks, fonts, the Digest picture, page banners, card strips.
The centre-hung scoreboard and the rafters' banners over the tiles; the stands, the hardwood in perspective and its
centre circle under the podium for the leaderboard. No real teams, leagues, players, brands or arenas."""
import math, random

KEY = "basketball"
NAME = "Basketball"
CATEGORY = "Sports"
FONTS = "family=Bungee&family=Barlow:wght@400;500;600;700"
DISPLAY = "'Bungee', 'Arial Black', sans-serif"
DW = 400   # Bungee has one weight, drawn heavy
BODY = "'Barlow', system-ui, sans-serif"
SKY_BG = (("#3c4250", "#c99a62"), ("#07080d", "#191310"))
TOUR = {"k": "Playbook", "next": "Next play", "back": "Back", "done": "Swish!", "skip": "Bench me"}

LOOKS = [
    ("hardwood", "Hardwood",
     "--surface: #f2ebdf; --surface-raised: #fdfaf3; --card2: #f6f0e5; --chip: #ebe1d0; --text-primary: #24170e; --text-muted: #65564a; --text-secondary: #4e4034; --grid: #e8dfcf; --border: #e0d4c0; --border-strong: #c7b496; --accent: #b4470f; --accent-d: #8c360a; --side: #3a2416; --side2: #4b301d; --sideInk: #f3e6d6; --brand: #f8efe2; --brand2: #ff9a4a; --rad: 12px;",
     "--surface: #15100c; --surface-raised: #1d1712; --card2: #241d17; --chip: #2e251d; --text-primary: #f2e9de; --text-muted: #b0a291; --text-secondary: #c9bcab; --grid: #2e251d; --border: #33291f; --border-strong: #4a3c2e; --accent: #ff9a52; --accent-d: #ffb983; --side: #0c0805; --side2: #1a120c; --sideInk: #f3e6d6; --brand: #f8efe2; --brand2: #ff9a4a;",
     ["#f2ebdf", "#3a2416", "#e8641c"]),
    ("courtside", "Courtside",
     "--surface: #eeece5; --surface-raised: #fbfaf6; --card2: #f3f1ea; --chip: #e5e2d8; --text-primary: #141414; --text-muted: #5c5a52; --text-secondary: #46443d; --grid: #e4e1d7; --border: #dbd7cb; --border-strong: #bfb9a8; --accent: #86650c; --accent-d: #664c06; --side: #121212; --side2: #1f1f1f; --sideInk: #f1ead6; --brand: #f6f2e6; --brand2: #f2c230; --rad: 10px;",
     "--surface: #0e0e0e; --surface-raised: #171717; --card2: #1e1e1d; --chip: #282825; --text-primary: #f1eee6; --text-muted: #aaa595; --text-secondary: #c4bfb0; --grid: #282825; --border: #2c2b28; --border-strong: #423f38; --accent: #f2c230; --accent-d: #f7d76e; --side: #070707; --side2: #141414; --sideInk: #f1ead6; --brand: #f6f2e6; --brand2: #f2c230;",
     ["#eeece5", "#121212", "#f2c230"]),
    ("street", "Street",
     "--surface: #e5e8ec; --surface-raised: #f7f8fa; --card2: #eceff2; --chip: #dde1e7; --text-primary: #161a20; --text-muted: #59616d; --text-secondary: #444c58; --grid: #dde1e7; --border: #d3d8df; --border-strong: #b3bbc6; --accent: #0b5fd0; --accent-d: #0848a2; --side: #2a2e35; --side2: #373c45; --sideInk: #e2e7ee; --brand: #eef1f4; --brand2: #4ab8ff; --rad: 14px;",
     "--surface: #0f1114; --surface-raised: #171a1f; --card2: #1d2127; --chip: #252a32; --text-primary: #e7ebf0; --text-muted: #9ca5b2; --text-secondary: #b8c0cb; --grid: #252a32; --border: #282e37; --border-strong: #3a4250; --accent: #4aa8ff; --accent-d: #85c4ff; --side: #08090b; --side2: #14171c; --sideInk: #e2e7ee; --brand: #eef1f4; --brand2: #4ab8ff;",
     ["#e5e8ec", "#2a2e35", "#1f8bff"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(roof="#06070c", roof2="#0d0f18", steel="#2a2e3c", steel2="#1c1f2a", wall="#0f1018", seat="#2a1418", seat2="#1e0f12",
                    maple="#a8743f", maple2="#9a6a38", apron="#5e3a1e", paint="#8a3a14", line="#efe6d6", floor="#0d0d12",
                    board="#14161e", led="#ff9a3a", ledoff="#3a2a1e", glass="#9ec8e8", pad="#1f3a6a", rim="#ff6a2a",
                    crowd=["#3a2a2a", "#2a2e3a", "#3a3428", "#4a2a20", "#2a3a34"], skin=["#6a4a36", "#4a3426", "#8a6a50", "#5a3e2c"],
                    home="#c8501e", away="#2a4a8a", ink="#fff3e0", chair="#1a1a22", bg1="#05060b", bg2="#0e1018")
    return dict(roof="#3a4150", roof2="#4b5363", steel="#8a93a6", steel2="#6a7286", wall="#4a4f5e", seat="#9a3a2a", seat2="#7e2e22",
                maple="#e6b97e", maple2="#dcab6c", apron="#b06a34", paint="#d0581c", line="#ffffff", floor="#2a2a32",
                board="#1c1e26", led="#ffb04a", ledoff="#4a3a2a", glass="#cfe6f6", pad="#2a5aa8", rim="#ff5a1a",
                crowd=["#c84a3a", "#3a5a9a", "#e8c24a", "#f2f2f2", "#2a8a6a", "#e87a2a", "#7a4a9a"], skin=["#e2b48c", "#a8714c", "#7a4e34", "#f0c8a4"],
                home="#d8541a", away="#2f5fae", ink="#fff8ec", chair="#2a2a34", bg1="#4a5263", bg2="#5c6474")

def wrap(h, body, par="xMidYMid slice"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="{par}">{body}</svg>'

def lg(i, stops, x2=0, y2=1):
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + ''.join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops) + '</linearGradient>'

def rg(i, c, op=.6):
    return f'<radialGradient id="{i}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity="{op}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'

def show(times, vals, dur, attr="opacity", begin=0):
    """an <animate> that steps an attribute through vals at keyTimes, looping"""
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{";".join(times)}" '
            f'dur="{dur}s" begin="{begin}s" calcMode="discrete" repeatCount="indefinite"/>')

def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {b};{deg} {x} {b};{-deg} {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

def T(x, y, s, size, c, anchor="middle", w="bold", fam="Arial, sans-serif", ls=1, extra=''):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{fam}" font-weight="{w}" font-size="{size}" fill="{c}" letter-spacing="{ls}"{extra}>{s}</text>'

# ----------------------------------------------------------------- people
def player(x, y, s, pose="stand", jersey="#d8541a", shorts=None, skin="#a8714c", flip=False, ball=False, num=None):
    """a player, feet on y, about 80 units tall at s=1"""
    sh = shorts or jersey
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{skin}" stroke-width="6.5" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    arm = f'stroke="{skin}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    shoe = lambda sx, sy: f'<ellipse cx="{sx}" cy="{sy}" rx="5.5" ry="2.8" fill="#f4f4f0"/>'
    bl = lambda bx, by: f'<circle cx="{bx}" cy="{by}" r="5.2" fill="#e0701e" stroke="#5a2a0a" stroke-width="1"/>' if ball else ''
    torso = lambda tx, ty, rot=0: (f'<g transform="rotate({rot} {tx} {ty})"><path d="M{tx - 9} {ty} L{tx - 8} {ty - 28} Q{tx} {ty - 31} {tx + 8} {ty - 28} L{tx + 9} {ty}Z" fill="{jersey}"/>'
                                   + ((T(-tx if flip else tx, ty - 9, num, 9, "#fff", extra=' transform="scale(-1 1)"' if flip else '')) if num else '') + '</g>')
    head = lambda hx, hy: f'<circle cx="{hx}" cy="{hy}" r="7" fill="{skin}"/><path d="M{hx - 7} {hy - 2} Q{hx} {hy - 11} {hx + 7} {hy - 2}" fill="#1a1410"/>'
    shorts_ = lambda tx, ty: f'<path d="M{tx - 10} {ty - 2} L{tx + 10} {ty - 2} L{tx + 11} {ty + 12} L{tx + 1} {ty + 12} L{tx} {ty + 6} L{tx - 1} {ty + 12} L{tx - 11} {ty + 12}Z" fill="{sh}"/>'
    if pose == "set":  # knees bent, ball at the chest, eyes on the rim
        b = (f'<path d="M-7 0 L-9 -14 L-3 -30 M7 0 L9 -14 L3 -30" {leg}/>' + shoe(-7, 0) + shoe(8, 0) + shorts_(0, -36) + torso(1, -36, 6)
             + f'<path d="M6 -60 L10 -50 L8 -44 M-5 -60 L2 -50 L6 -45" {arm}/>' + bl(9, -45) + head(4, -71))
    elif pose == "jump":  # rising, both arms up, ball over the forehead
        b = (f'<path d="M-6 0 L-4 -16 L-3 -30 M6 -2 L5 -16 L3 -30" {leg}/>' + shoe(-6, 0) + shoe(6, -2) + shorts_(0, -36) + torso(0, -36)
             + f'<path d="M6 -62 L10 -76 L8 -90 M-6 -62 L-4 -76 L4 -88" {arm}/>' + bl(8, -94) + head(1, -72))
    elif pose == "follow":  # landed, shooting arm still up, wrist flicked
        b = (f'<path d="M-7 0 L-5 -16 L-3 -30 M7 0 L5 -16 L3 -30" {leg}/>' + shoe(-7, 0) + shoe(7, 0) + shorts_(0, -36) + torso(0, -36)
             + f'<path d="M6 -62 L12 -78 L14 -92 L19 -94 M-6 -62 L-10 -48" {arm}/>' + head(1, -72))
    elif pose == "contest":  # a defender, one hand high
        b = (f'<path d="M-9 0 L-8 -15 L-3 -30 M9 0 L8 -15 L3 -30" {leg}/>' + shoe(-9, 0) + shoe(9, 0) + shorts_(0, -36) + torso(0, -36)
             + f'<path d="M6 -62 L10 -78 L10 -94 M-6 -62 L-16 -54 L-20 -46" {arm}/>' + head(0, -72))
    elif pose == "ready":  # hands out for the pass
        b = (f'<path d="M-7 0 L-9 -14 L-3 -30 M7 0 L9 -14 L3 -30" {leg}/>' + shoe(-7, 0) + shoe(8, 0) + shorts_(0, -36) + torso(1, -36, 4)
             + f'<path d="M6 -60 L14 -54 L20 -54 M-5 -60 L4 -52 L14 -52" {arm}/>' + head(4, -71))
    elif pose == "highfive":  # arm up and across toward the other player
        b = (f'<path d="M-6 0 L-4 -16 L-3 -30 M7 0 L5 -16 L3 -30" {leg}/>' + shoe(-6, 0) + shoe(7, 0) + shorts_(0, -36) + torso(0, -36, 5)
             + f'<path d="M6 -62 L16 -76 L22 -86 M-6 -62 L-10 -46" {arm}/>' + f'<circle cx="23" cy="-88" r="3.6" fill="{skin}"/>' + head(2, -72))
    elif pose == "dunk":  # in the air, arm through the rim
        b = (f'<path d="M-4 -2 L-14 -12 L-10 -28 M6 -4 L4 -18 L3 -30" {leg}/>' + shoe(-4, -2) + shoe(6, -4) + shorts_(0, -36) + torso(0, -36, 10)
             + f'<path d="M6 -62 L18 -80 L26 -94 M-6 -62 L-16 -70 L-22 -82" {arm}/>' + bl(28, -98) + head(4, -72))
    elif pose == "tip":  # jumping for the tip, one arm stretched straight up
        b = (f'<path d="M-5 -2 L-6 -16 L-3 -30 M6 -8 L8 -20 L3 -30" {leg}/>' + shoe(-5, -2) + shoe(6, -8) + shorts_(0, -36) + torso(0, -36)
             + f'<path d="M6 -62 L8 -80 L9 -100 M-6 -62 L-14 -52" {arm}/>' + head(0, -72))
    elif pose == "dribble":
        b = (f'<path d="M-8 0 L-10 -14 L-3 -30 M8 0 L10 -14 L3 -30" {leg}/>' + shoe(-8, 0) + shoe(9, 0) + shorts_(0, -36) + torso(2, -36, 10)
             + f'<path d="M7 -60 L14 -46 L18 -34 M-5 -60 L-12 -48" {arm}/>' + bl(20, -20) + head(6, -71))
    elif pose == "sit":  # on the bench
        b = (f'<path d="M-4 -24 L10 -24 L10 0 M2 -24 L16 -22 L16 0" {leg}/>' + shoe(12, 0) + shoe(18, 0)
             + f'<rect x="-8" y="-30" width="14" height="10" fill="{sh}"/>' + torso(-1, -26, -4) + f'<path d="M4 -48 L12 -36" {arm}/>' + head(-1, -62))
    else:  # stand, hands at the side (or the ball on the hip)
        b = (f'<path d="M-6 0 L-4 -16 L-3 -30 M7 0 L5 -16 L3 -30" {leg}/>' + shoe(-6, 0) + shoe(7, 0) + shorts_(0, -36) + torso(0, -36)
             + f'<path d="M6 -62 L10 -48 L12 -38 M-6 -62 L-10 -48 L-12 -38" {arm}/>' + bl(15, -40) + head(0, -72))
    return g + b + '</g>'

def person(x, y, s, shirt, pants="#2a2e3a", skin="#a8714c", pose="stand", flip=False, hat=None):
    """staff and coaches: trousers, a polo or jacket"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    leg = f'stroke="{pants}" stroke-width="7" fill="none" stroke-linecap="round"'
    arm = f'stroke="{shirt}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    shoes = '<ellipse cx="-6" cy="0" rx="5" ry="2.5" fill="#1a1a1a"/><ellipse cx="7" cy="0" rx="5" ry="2.5" fill="#1a1a1a"/>'
    body = f'<path d="M-9 -58 Q0 -62 9 -58 L9 -30 L-9 -30Z" fill="{shirt}"/>'
    head = f'<circle cx="0" cy="-66" r="7.5" fill="{skin}"/>' + (f'<path d="M-8 -68 Q0 -77 8 -68 L12 -67 L8 -66Z" fill="{hat}"/>' if hat else '<path d="M-7.5 -68 Q0 -76 7.5 -68" fill="#2a1e16"/>')
    if pose == "point":
        b = f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + shoes + body + f'<path d="M6 -54 L20 -62 L30 -66 M-6 -54 L-10 -36" {arm}/>' + head
    elif pose == "mop":  # pushing a wide dust mop ahead
        b = (f'<path d="M-10 0 L-5 -30 M8 0 L3 -30" {leg}/>' + shoes + body.replace('M-9 -58', 'M-6 -60') + f'<path d="M6 -54 L18 -44 M-4 -54 L14 -40" {arm}/>'
             + '<line x1="14" y1="-42" x2="44" y2="-2" stroke="#8a6a3a" stroke-width="2.6"/><rect x="26" y="-3" width="40" height="6" rx="2" fill="#3a3a44"/>' + head)
    elif pose == "toss":  # the referee, arm up from the toss
        b = f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + shoes + body + f'<path d="M6 -54 L10 -72 L10 -86 M-6 -54 L-10 -36" {arm}/>' + head
    elif pose == "kneel":  # the coach down on one knee with the board
        b = (f'<path d="M-6 0 L-6 -16 L-2 -28 M10 0 L14 -14 L2 -28" {leg}/>' + shoes + body.replace('L9 -30 L-9 -30', 'L9 -26 L-9 -26').replace('-58', '-54').replace('-62', '-58')
             + f'<path d="M6 -50 L18 -40 M-6 -50 L4 -38" {arm}/>' + head.replace('-66', '-62').replace('-68', '-64').replace('-76', '-72').replace('-77', '-73').replace('-67', '-63'))
    else:
        b = f'<path d="M-6 0 L-3 -30 M7 0 L3 -30" {leg}/>' + shoes + body + f'<path d="M6 -56 L10 -36 M-6 -56 L-10 -36" {arm}/>' + head
    return g + b + '</g>'

def ref_shirt(x0, y0, w, h):
    """black-and-white stripes for an official's shirt, as a group of rects"""
    return ''.join(f'<rect x="{x0 + i * 4}" y="{y0}" width="2" height="{h}" fill="#111"/>' for i in range(int(w / 4)))

def bball(x, y, r, n=False):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{"#e0701e" if not n else "#c8601a"}"/>'
            f'<path d="M{x - r} {y} H{x + r} M{x} {y - r} V{y + r} M{x - r * .7:.1f} {y - r * .7:.1f} Q{x - r * .2:.1f} {y} {x - r * .7:.1f} {y + r * .7:.1f} M{x + r * .7:.1f} {y - r * .7:.1f} Q{x + r * .2:.1f} {y} {x + r * .7:.1f} {y + r * .7:.1f}" '
            f'stroke="#4a1e06" stroke-width="{max(.8, r * .12):.1f}" fill="none"/>')

def hoop(x, y, s, n, face=-1, pole_to=None, broken=False, red=False):
    """a side-on basket: the glass board at x (its face toward `face`), the rim at y, the arm back to a padded stanchion"""
    f = face; o = []
    if pole_to:  # arm over to the stanchion and down to the floor
        px = x - f * 70 * s
        o.append(f'<path d="M{x - f * 4 * s:.0f} {y - 46 * s:.0f} L{px:.0f} {y - 52 * s:.0f} L{px:.0f} {pole_to}" fill="none" stroke="#3a3e4a" stroke-width="{9 * s:.1f}" stroke-linejoin="round"/>')
        o.append(f'<path d="M{x - f * 4 * s:.0f} {y - 20 * s:.0f} L{px:.0f} {y - 46 * s:.0f}" stroke="#3a3e4a" stroke-width="{4 * s:.1f}"/>')
        o.append(f'<rect x="{px - 14 * s:.0f}" y="{pole_to - 46 * s:.0f}" width="{28 * s:.0f}" height="{46 * s:.0f}" rx="{4 * s:.0f}" fill="#2a4a8a"/>')
    bw, bh = 8 * s, 64 * s
    o.append(f'<rect x="{x - bw / 2:.1f}" y="{y - 52 * s:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{"#d8ecf8" if not n else "#8ab0cc"}" opacity=".85" stroke="#f4f4f4" stroke-width="{1.6 * s:.1f}"/>')
    if red: o.append(f'<rect x="{x - bw / 2 - 2:.1f}" y="{y - 54 * s:.1f}" width="{bw + 4:.1f}" height="{bh + 4:.1f}" fill="none" stroke="#ff2a1a" stroke-width="{3 * s:.1f}"/>')
    if broken:
        o.append(f'<path d="M{x} {y - 30 * s:.0f} l{-6 * s:.0f} {-14 * s:.0f} M{x} {y - 30 * s:.0f} l{5 * s:.0f} {-12 * s:.0f} M{x} {y - 30 * s:.0f} l{-4 * s:.0f} {16 * s:.0f}" stroke="#5a6a7a" stroke-width="{1.4 * s:.1f}"/>')
    rx = x + f * 18 * s
    o.append(f'<line x1="{x}" y1="{y}" x2="{rx - f * 14 * s:.0f}" y2="{y}" stroke="#d84a1a" stroke-width="{2.4 * s:.1f}"/>')
    o.append(f'<ellipse cx="{rx:.0f}" cy="{y}" rx="{14 * s:.1f}" ry="{4 * s:.1f}" fill="none" stroke="#e8541a" stroke-width="{2.4 * s:.1f}"/>')
    o.append(net(rx, y, s))
    return ''.join(o)

def net(cx, y, s, sw=0):
    """the net under a rim of half-width 14*s: a tapered mesh"""
    w0, w1, h = 13 * s, 8 * s, 22 * s - sw
    d = f'M{cx - w0:.1f} {y:.1f} L{cx - w1:.1f} {y + h:.1f} M{cx + w0:.1f} {y:.1f} L{cx + w1:.1f} {y + h:.1f} M{cx - w0:.1f} {y:.1f} L{cx + w1:.1f} {y + h:.1f} M{cx + w0:.1f} {y:.1f} L{cx - w1:.1f} {y + h:.1f} M{cx:.1f} {y + 2 * s:.1f} L{cx - w1:.1f} {y + h:.1f} M{cx:.1f} {y + 2 * s:.1f} L{cx + w1:.1f} {y + h:.1f} M{cx - w1:.1f} {y + h:.1f} L{cx + w1:.1f} {y + h:.1f}'
    return f'<path d="{d}" stroke="#f4f4f4" stroke-width="{1.1 * s:.1f}" fill="none" opacity=".9"/>'

def crowd_pattern(i, p, n, w=26, h=22, seed=1):
    """two rows of fans in their seats: the stands' fill"""
    r = random.Random(seed); o = [f'<pattern id="{i}" width="{w * 4}" height="{h * 2}" patternUnits="userSpaceOnUse">',
                                  f'<rect width="{w * 4}" height="{h * 2}" fill="{p["seat2"]}"/>']
    for row in range(2):
        for k in range(4):
            cx = k * w + w / 2 + (w / 2 if row else 0); cy = row * h
            cx = cx % (w * 4)
            o.append(f'<rect x="{cx - w * .42:.1f}" y="{cy + h * .55:.1f}" width="{w * .84:.1f}" height="{h * .45:.1f}" fill="{p["seat"]}"/>')
            o.append(f'<path d="M{cx - w * .36:.1f} {cy + h:.1f} Q{cx - w * .34:.1f} {cy + h * .42:.1f} {cx:.1f} {cy + h * .42:.1f} Q{cx + w * .34:.1f} {cy + h * .42:.1f} {cx + w * .36:.1f} {cy + h:.1f}Z" fill="{r.choice(p["crowd"])}"/>')
            o.append(f'<circle cx="{cx:.1f}" cy="{cy + h * .26:.1f}" r="{w * .17:.1f}" fill="{r.choice(p["skin"])}"/>')
    o.append('</pattern>')
    return ''.join(o)

def mascot(x, y, s, n):
    """a generic big-headed fuzzy mascot in a jersey"""
    fur = "#e8762a" if not n else "#b85a20"; fur2 = "#c85a14" if not n else "#8a4012"
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-8 0 L-8 -26 M8 0 L8 -26" stroke="{fur2}" stroke-width="9" stroke-linecap="round"/>'
            '<ellipse cx="-10" cy="0" rx="10" ry="4" fill="#f4f4f0"/><ellipse cx="10" cy="0" rx="10" ry="4" fill="#f4f4f0"/>'
            f'<path d="M-16 -22 L16 -22 L18 -56 Q0 -62 -18 -56Z" fill="#2f5fae"/>{T(0, -33, "6", 13, "#fff")}'
            f'<path d="M-16 -54 L-30 -72 M16 -54 L30 -72" stroke="{fur}" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="-31" cy="-74" r="5" fill="{fur}"/><circle cx="31" cy="-74" r="5" fill="{fur}"/>'
            f'<circle cx="-15" cy="-94" r="7" fill="{fur2}"/><circle cx="15" cy="-94" r="7" fill="{fur2}"/>'
            f'<circle cx="0" cy="-76" r="20" fill="{fur}"/><ellipse cx="0" cy="-70" rx="11" ry="8" fill="#f6e2c6"/>'
            '<circle cx="-7" cy="-81" r="4" fill="#fff"/><circle cx="7" cy="-81" r="4" fill="#fff"/><circle cx="-6" cy="-80" r="2" fill="#111"/><circle cx="8" cy="-80" r="2" fill="#111"/>'
            '<ellipse cx="0" cy="-73" rx="3" ry="2.2" fill="#3a1a0a"/><path d="M-5 -67 Q0 -63 5 -67" stroke="#3a1a0a" stroke-width="1.6" fill="none"/></g>')

def cheer(x, y, s, top, skin, arms_up=True, pom="#ffd24a"):
    """a cheerleader with two pom-poms, arms in a V or out to the side"""
    leg = f'stroke="{skin}" stroke-width="5" fill="none" stroke-linecap="round"'
    ax = [(-16, -88), (16, -88)] if arms_up else [(-22, -56), (22, -56)]
    pp = ''.join(f'<circle cx="{px}" cy="{py}" r="8" fill="{pom}"/><path d="M{px - 8} {py} h16 M{px} {py - 8} v16 M{px - 6} {py - 6} l12 12 M{px + 6} {py - 6} l-12 12" stroke="#fff" stroke-width="1.4" opacity=".7"/>' for px, py in ax)
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<path d="M-4 0 L-3 -28 M5 0 L3 -28" {leg}/><ellipse cx="-4" cy="0" rx="4.5" ry="2.4" fill="#fff"/><ellipse cx="5" cy="0" rx="4.5" ry="2.4" fill="#fff"/>'
            f'<path d="M-10 -24 L10 -24 L7 -36 L-7 -36Z" fill="{top}"/><path d="M-7 -36 L7 -36 L8 -58 Q0 -61 -8 -58Z" fill="{top}"/><path d="M-7 -44 h14" stroke="#fff" stroke-width="2"/>'
            f'<path d="M6 -56 L{ax[1][0]} {ax[1][1]} M-6 -56 L{ax[0][0]} {ax[0][1]}" stroke="{skin}" stroke-width="4" stroke-linecap="round"/>{pp}'
            f'<circle cx="0" cy="-66" r="7" fill="{skin}"/><path d="M-7 -68 Q0 -77 7 -68 Q9 -60 6 -56 M-7 -68 Q-9 -60 -6 -56" fill="#3a2414" stroke="#3a2414" stroke-width="2"/></g>')

# ================================================================= the court's perspective
# The court is drawn side on from a camera high behind the near sideline: X is feet along the court (-47..47),
# Z feet from the far sideline (0) to the near one (50), h feet up. The far sideline is y 548, the near one y 800.
VY, DF, DN = -82, 630, 882
def _d(Z):
    t = Z / 50
    return 1 / ((1 - t) / DF + t / DN)
def pr(X, Z, h=0):
    d = _d(Z); s = (1000 / 94) * (d / DF)
    return (800 + X * s, VY + d - h * s)
def sc(Z): return (1000 / 94) * (_d(Z) / DF)
def poly(pts, close=False):
    return 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + ('Z' if close else '')
def arc(cx, cz, r, a0, a1, k=18):
    return [pr(cx + r * math.cos(a), cz + r * math.sin(a)) for a in [a0 + (a1 - a0) * i / k for i in range(k + 1)]]

def court_lines(p):
    o = []; L = []
    L.append(poly([pr(-47, 0), pr(47, 0), pr(47, 50), pr(-47, 50)], True))
    L.append(poly([pr(0, 0), pr(0, 50)]))
    L.append(poly(arc(0, 25, 6, 0, 2 * math.pi, 28), True))
    for sgn in (-1, 1):
        bx = 47 * sgn; ft = sgn * (47 - 19); hx = sgn * 41.75
        L.append(poly([pr(bx, 17), pr(ft, 17), pr(ft, 33), pr(bx, 33)]))
        L.append(poly(arc(ft, 25, 6, -math.pi / 2, math.pi / 2, 12) if sgn < 0 else arc(ft, 25, 6, math.pi / 2, 3 * math.pi / 2, 12)))
        # the three-point line: corners 3 ft in from each sideline, the arc 23.75 ft from the basket
        a = math.asin(22 / 23.75); cxs = hx + (-sgn) * 23.75 * math.cos(a)
        if sgn < 0: pts = [pr(bx, 3), pr(cxs, 3)] + arc(hx, 25, 23.75, -a, a, 22) + [pr(bx, 47)]
        else: pts = [pr(bx, 3), pr(cxs, 3)] + arc(hx, 25, 23.75, math.pi + a, math.pi - a, 22) + [pr(bx, 47)]
        L.append(poly(pts))
    return f'<path d="{" ".join(L)}" fill="none" stroke="{p["line"]}" stroke-width="3" stroke-linejoin="round" opacity=".95"/>'

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
HK = 1.25  # the baskets drawn a little over true height so they read from the high camera
BANNERS = [("COVERED", "2019"), ("BUNDLED", "2021"), ("NO LAPSE", "2022"), ("RENEWED", "2023"), ("CLAIM FREE", "2024"), ("RETAINED", "2025")]

def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a('<defs>' + lg("roof", [(0, p["roof"], 1), (1, p["roof2"], 1)])
      + lg("beam", [(0, "#fff6d8", .0), (.7, "#fff6d8", .3 if n else .2), (1, "#fff6d8", .6 if n else .4)])
      + rg("glow", "#ffc35a", .6) + rg("pool", "#ffe9b8", .32 if n else .14) + rg("scr", "#7ac0ff", .35)
      + crowd_pattern("cr", p, n, 26, 22, 3) + crowd_pattern("cr2", p, n, 16, 14, 5)
      + f'<clipPath id="court"><path d="{poly([pr(-53, -5), pr(53, -5), pr(53, 55), pr(-53, 55)], True)}"/></clipPath></defs>')
    # the roof and the far upper deck
    a(f'<rect width="{W}" height="380" fill="url(#roof)"/>')
    a(f'<rect x="0" y="100" width="{W}" height="300" fill="url(#cr2)" opacity="{.75 if not n else .55}"/>')
    a(f'<rect x="0" y="100" width="{W}" height="300" fill="{p["roof"]}" opacity="{.4 if not n else .5}"/>')
    a(f'<rect x="0" y="94" width="{W}" height="8" fill="{p["steel2"]}"/>')
    if n:  # phone lights in the upper deck, a sparse tile of them
        a('<pattern id="ph" width="230" height="70" patternUnits="userSpaceOnUse"><circle cx="30" cy="8" r="1.6" fill="#fff"/><circle cx="140" cy="40" r="1.6" fill="#fff" opacity=".5"/><circle cx="200" cy="22" r="1.6" fill="#fff" opacity=".8"/></pattern>'
          f'<rect x="0" y="104" width="{W}" height="70" fill="url(#ph)"/>')
    # the roof trusses: a lattice girder right across, the catwalk under it
    a(f'<rect x="0" y="28" width="{W}" height="5" fill="{p["steel"]}"/><rect x="0" y="58" width="{W}" height="5" fill="{p["steel"]}"/>')
    a(f'<path d="' + ''.join(f'M{x} 33 L{x + 40} 58 M{x + 40} 33 L{x + 80} 58 ' for x in range(0, W, 80)) + f'" stroke="{p["steel2"]}" stroke-width="2.5"/>')
    a(f'<rect x="0" y="70" width="{W}" height="3" fill="{p["steel2"]}"/>' + ''.join(f'<line x1="{x}" y1="63" x2="{x}" y2="70" stroke="{p["steel2"]}" stroke-width="2"/>' for x in range(20, W, 60)))
    for x in (180, 300, 1300, 1420):  # lamps hung under the girder
        a(f'<rect x="{x - 2}" y="63" width="4" height="10" fill="{p["steel2"]}"/><path d="M{x - 14} 84 L{x - 8} 73 L{x + 8} 73 L{x + 14} 84Z" fill="{p["steel2"]}"/>'
          f'<ellipse cx="{x}" cy="84" rx="13" ry="3" fill="#fff4cf" opacity="{.95 if n else .8}"/>')
        if n: a(f'<circle cx="{x}" cy="90" r="40" fill="url(#glow)" opacity=".6"/>')
    # the championship banners, hung from the girder on two rods each
    for i, (word, yr) in enumerate(BANNERS):
        bx = [380, 472, 564, 968, 1060, 1152][i]; c = p["home"] if i % 2 == 0 else p["away"]
        a(f'<line x1="{bx + 6}" y1="63" x2="{bx + 6}" y2="82" stroke="{p["steel2"]}" stroke-width="1.6"/><line x1="{bx + 62}" y1="63" x2="{bx + 62}" y2="82" stroke="{p["steel2"]}" stroke-width="1.6"/>')
        a(f'<rect x="{bx - 2}" y="80" width="72" height="5" rx="2" fill="{p["steel"]}"/>')
        a(f'<path d="M{bx} 84 h68 v92 l-34 14 l-34 -14Z" fill="{c}" stroke="#f2c230" stroke-width="2.5"/>')
        a(f'<path d="M{bx + 26} 98 h16 v6 q0 10 -8 12 q-8 -2 -8 -12Z M{bx + 30} 116 h8 v4 h4 v3 h-16 v-3 h4Z" fill="#f2c230"/>')
        a(T(bx + 34, 140, word, 10.5 if len(word) < 9 else 9, "#fff", ls=.5) + T(bx + 34, 160, yr, 15, "#f2c230", ls=1))
    # spotlights: floor cans at the far corners, their beams sweeping up between the tiles
    for k, (sx, a0, a1, dur) in enumerate([(236, 6, 30, 8), (1364, -6, -30, 11)]):
        beam = f'M{sx} 528 L{sx - 70} -60 L{sx + 70} -60Z'
        a(f'<path d="{beam}" fill="url(#beam)" transform="rotate({a0 + (a1 - a0) / 2} {sx} 528)">'
          f'<animateTransform attributeName="transform" type="rotate" values="{a0 + (a1 - a0) / 2} {sx} 528;{a1} {sx} 528;{a0} {sx} 528;{a0 + (a1 - a0) / 2} {sx} 528" dur="{dur}s" begin="{k * 1.5}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>')
    # the centre-hung scoreboard: four cables to the girder, the LED ring, the screen
    jx = 800
    for cx in (690, 738, 862, 910): a(f'<line x1="{cx}" y1="33" x2="{cx + (12 if cx < jx else -12)}" y2="58" stroke="{p["steel2"]}" stroke-width="2"/>')
    a('<g transform="translate(0 -16)">')
    a(f'<path d="M680 74 L920 74 L944 84 L656 84Z" fill="#1a1c24"/>')
    a(f'<rect x="656" y="84" width="288" height="18" fill="#101116"/>' + T(800, 98, "NOTHING BUT NET PREMIUM", 12, p["led"], ls=2))
    a(f'<path d="M656 102 L680 108 L680 156 L656 166Z" fill="#14161c"/><path d="M944 102 L920 108 L920 156 L944 166Z" fill="#14161c"/>')
    a(f'<rect x="680" y="104" width="240" height="56" fill="#0a0c12" stroke="#2a2e3a" stroke-width="3"/>')
    if n: a('<ellipse cx="800" cy="132" rx="220" ry="70" fill="url(#scr)"/>')
    a(f'<rect x="684" y="108" width="232" height="48" fill="{"#132a52" if n else "#1a3466"}"/>')
    a(T(728, 124, "COVERED", 11, "#fff", ls=1) + T(872, 124, "RISK", 11, "#fff", ls=1))
    a(T(728, 150, "98", 24, "#ffd24a", fam="monospace") + T(872, 150, "96", 24, "#ffd24a", fam="monospace"))
    a(f'<rect x="776" y="114" width="48" height="36" rx="3" fill="#000"/>' + T(800, 128, "4TH", 10, "#ff9a3a") + T(800, 145, "0:00.4", 10, "#ff4a2a", fam="monospace"))
    a(f'<path d="M656 166 L680 158 L920 158 L944 166 L944 176 L656 176Z" fill="#101116"/>')
    # the chase lights on the bottom ring
    a(f'<g fill="{p["led"]}">')
    for i in range(16):
        bx = 668 + i * 17.6
        a(f'<circle cx="{bx:.0f}" cy="171" r="3" opacity=".3"><animate attributeName="opacity" values="1;.3;.3" keyTimes="0;.15;1" dur="3s" begin="{i * 3 / 16:.2f}s" repeatCount="indefinite"/></circle>')
    a('</g></g>')
    # ------------------------------------------------ the lower bowl behind the court (the leaderboard's top)
    a(f'<rect x="0" y="372" width="{W}" height="140" fill="url(#cr)"/>')
    a(f'<rect x="0" y="372" width="{W}" height="140" fill="#000" opacity="{.22 if not n else .5}"/>')
    # the crowd doing the wave: the same fans as the seats (same seed, same grid) drawn standing, arms up, and half up;
    # two masks sweep across the bowl, so each fan rises in place as the band reaches them and sits back down behind it
    r = random.Random(3); fans = []
    for row in range(2):
        for k in range(4):
            cx = (k * 26 + 13 + (13 if row else 0)) % 104; cy = row * 22
            fans.append((cx, cy, r.choice(p["crowd"]), r.choice(p["skin"])))
    def lay(sid, oy):
        u = []
        for cx, cy, sh, sk in fans:
            for dx in ((0, 104) if cx == 0 else (0,)):
                for dy in ((0, 44) if cy == 0 else (0,)):
                    u.append(f'<use href="#{sid}" x="{cx + dx}" y="{cy + dy + oy}" fill="{sh}" color="{sk}"/>')
        return ''.join(u)
    wv = ('<defs><g id="wf"><path d="M-9.4 22L-8 3Q0 0 8 3L9.4 22z"/><path d="M-6 5L-9-15M6 5L9-15" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/><circle cy="-4" r="4.7" fill="currentColor"/></g>'
          '<g id="wh"><path d="M-9.4 22L-8 7Q0 4 8 7L9.4 22z"/><path d="M-6 9L-9 1M6 9L9 1" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"/><circle cy="1" r="4.6" fill="currentColor"/></g>'
          f'<pattern id="wvF" width="104" height="44" patternUnits="userSpaceOnUse">{lay("wf", 0)}</pattern>'
          f'<pattern id="wvH" width="104" height="44" patternUnits="userSpaceOnUse">{lay("wh", 0)}</pattern>')
    for mid, x0, w0 in (("mF", -320, 120), ("mH", -372, 198)):
        wv += (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="372" width="{W}" height="140"><rect x="{x0}" y="384" width="{w0}" height="128" fill="#fff">'
               f'<animate attributeName="x" values="{x0};{x0 + 2000};{x0 + 2000}" keyTimes="0;.74;1" dur="10s" repeatCount="indefinite"/></rect></mask>')
    a(wv + '</defs>' + ''.join(f'<rect x="0" y="384" width="{W}" height="122" fill="url(#{pt})" mask="url(#{m})"/>' for pt, m in (("wvH", "mH"), ("wvF", "mF"))))
    for x in (400, 800, 1200): a(f'<path d="M{x - 10} 372 L{x + 10} 372 L{x + 14} 506 L{x - 14} 506Z" fill="{p["wall"]}"/>' + ''.join(f'<line x1="{x - 12}" y1="{y}" x2="{x + 12}" y2="{y}" stroke="#000" stroke-opacity=".3"/>' for y in range(380, 506, 11)))
    a(f'<rect x="0" y="372" width="{W}" height="8" fill="{p["steel2"]}"/><rect x="0" y="380" width="{W}" height="3" fill="{p["led"]}" opacity=".6"/>')
    # the floor of the arena, the ad boards along the far side
    a(f'<rect x="0" y="506" width="{W}" height="{H - 506}" fill="{p["floor"]}"/>')
    a(f'<rect x="196" y="500" width="1208" height="28" fill="{p["board"]}"/>')
    a(f'<path d="M200 514 H470 M1130 514 H1400" stroke="{p["led"]}" stroke-width="4" stroke-dasharray="2 6" opacity=".7"/>')
    for i, t in enumerate(["FULL COURT COVERAGE", "SLAM DUNK SAVINGS"]):
        x0 = 474 + i * 328
        a(f'<rect x="{x0}" y="503" width="324" height="22" fill="{["#c8501e", "#1d2a4a"][i] if not n else ["#7a2e10", "#121a30"][i]}"/>' + T(x0 + 162, 519, t, 13, "#fff" if not n else "#ffd9a8", ls=1.5))
    # the end stands beyond each baseline
    for sgn in (-1, 1):
        x0 = 0 if sgn < 0 else W; x1 = 150 if sgn < 0 else W - 150
        a(f'<path d="M{x0} 506 L{x1} 506 L{x1 - sgn * 20} 560 L{x0} 640Z" fill="url(#cr)"/><path d="M{x0} 506 L{x1} 506 L{x1 - sgn * 20} 560 L{x0} 640Z" fill="#000" opacity="{.2 if not n else .5}"/>')
        a(f'<path d="M{x1 - sgn * 20} 560 L{x0} 640" stroke="{p["steel2"]}" stroke-width="4"/>')
    # the hardwood: apron, playing surface, the planks, the paint and the centre circle
    a(f'<path d="{poly([pr(-53, -5), pr(53, -5), pr(53, 55), pr(-53, 55)], True)}" fill="{p["apron"]}"/>')
    a(f'<path d="{poly([pr(-47, 0), pr(47, 0), pr(47, 50), pr(-47, 50)], True)}" fill="{p["maple"]}"/>')
    pl = ' '.join(poly([pr(-53, z), pr(53, z)]) for z in range(-4, 55, 3))
    a(f'<g clip-path="url(#court)"><path d="{pl}" stroke="{p["maple2"]}" stroke-width="1.4"/></g>')
    for sgn in (-1, 1):
        bx = 47 * sgn; ft = sgn * 28
        a(f'<path d="{poly([pr(bx, 17), pr(ft, 17), pr(ft, 33), pr(bx, 33)], True)}" fill="{p["paint"]}"/>')
    a(f'<path d="{poly(arc(0, 25, 6, 0, 2 * math.pi, 28), True)}" fill="{p["paint"]}"/>')
    a(f'<ellipse cx="800" cy="654" rx="560" ry="150" fill="url(#pool)"/>')
    a(court_lines(p))
    cx, cy = pr(0, 25)
    a(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="30" ry="12" fill="{p["home"]}" stroke="{p["line"]}" stroke-width="2"/>')
    # the benches on the far apron, outside the podium's row
    for bx0, col in ((318, p["home"]), (1150, p["away"])):
        a(f'<rect x="{bx0}" y="526" width="132" height="6" fill="#3a3a44"/><rect x="{bx0 + 4}" y="532" width="4" height="8" fill="#2a2a30"/><rect x="{bx0 + 124}" y="532" width="4" height="8" fill="#2a2a30"/>')
        for k in range(4): a(player(bx0 + 18 + k * 32, 538, .5, "sit", col, skin=p["skin"][k % 4]))
    for sx in (236, 1364):  # the spotlight cans on their stands
        a(f'<path d="M{sx - 12} 530 L{sx} 516 L{sx + 12} 530Z" fill="#2a2a30"/><rect x="{sx - 9}" y="504" width="18" height="16" rx="3" fill="#3a3a44"/><ellipse cx="{sx}" cy="504" rx="8" ry="3" fill="#fff6d8"/>')
    # the baskets: left quiet, right the jump shot
    for sgn in (-1, 1):
        bx, by = pr(sgn * 43, 25)
        st, sy = pr(sgn * 52, 25)
        s = sc(25) / 12.4
        rimx, rimy = pr(sgn * 41.75, 25, 10 * HK)
        bd = [pr(sgn * 43, 21.5, 9.5 * HK), pr(sgn * 43, 28.5, 9.5 * HK), pr(sgn * 43, 28.5, 13.6 * HK), pr(sgn * 43, 21.5, 13.6 * HK)]
        top = pr(sgn * 43, 25, 12.6 * HK); pt = pr(sgn * 52, 25, 13.8 * HK)
        a(f'<path d="M{st:.0f} {sy:.0f} L{pt[0]:.0f} {pt[1]:.0f} L{top[0]:.0f} {top[1]:.0f}" fill="none" stroke="#3a3e4a" stroke-width="9" stroke-linejoin="round"/>'
          f'<path d="M{pt[0]:.0f} {pt[1] + 34:.0f} L{top[0]:.0f} {top[1] + 20:.0f}" stroke="#3a3e4a" stroke-width="4"/>')
        a(f'<path d="M{st - 26:.0f} {sy:.0f} L{st - 20:.0f} {sy - 42:.0f} L{st + 20:.0f} {sy - 42:.0f} L{st + 26:.0f} {sy:.0f}Z" fill="{p["pad"]}"/>' + T(round(st), round(sy - 14), "NO LAPSE", 7.5, "#fff", ls=.5))
        a(f'<path d="{poly(bd, True)}" fill="{p["glass"]}" opacity=".8" stroke="#f4f4f4" stroke-width="3.4"/>')
        sq = [pr(sgn * 43, 24, 10.2 * HK), pr(sgn * 43, 26, 10.2 * HK), pr(sgn * 43, 26, 11.8 * HK), pr(sgn * 43, 24, 11.8 * HK)]
        a(f'<path d="{poly(sq, True)}" fill="none" stroke="#fff" stroke-width="1.6"/>')
        if sgn < 0:
            a(f'<line x1="{bx:.0f}" y1="{rimy:.0f}" x2="{rimx:.0f}" y2="{rimy:.0f}" stroke="{p["rim"]}" stroke-width="2.5"/>'
              f'<ellipse cx="{rimx:.0f}" cy="{rimy:.0f}" rx="10" ry="3.4" fill="none" stroke="{p["rim"]}" stroke-width="2.6"/>' + net(rimx, rimy, .72))
        else:
            RX, RY = rimx, rimy
            a(f'<line x1="{bx:.0f}" y1="{rimy:.0f}" x2="{rimx:.0f}" y2="{rimy:.0f}" stroke="{p["rim"]}" stroke-width="2.5"/>'
              f'<path d="M{RX - 10:.0f} {RY:.0f} A10 3.4 0 0 1 {RX + 10:.0f} {RY:.0f}" fill="none" stroke="{p["rim"]}" stroke-width="2.6"/>')
    # the shooter and the defender on the right wing, the ball arcing into the basket
    SX, SY = pr(28, 36); s1 = sc(36) / 12.4 * .98
    DX, DY = pr(33, 30); s2 = sc(30) / 12.4 * .98
    a(player(DX, DY, s2, "contest", p["away"], skin=p["skin"][2], flip=True, num="3"))
    hx, hy = SX + 9 * s1, SY - 45 * s1          # the ball at the chest in the set
    jx2, jy2 = SX + 8 * s1, SY - 94 * s1 - 22    # over the head at the top of the jump
    J = 'translate(0 -22)'
    sh = lambda pose, vis, times, vals, ball=False: (('<g>' if vis else '<g opacity="0">') + player(SX, SY, s1, pose, p["home"], skin=p["skin"][1], ball=ball, num="23")
                                                    + show(times, vals, 6) + '</g>')
    a(sh("set", True, ["0", ".12", ".96"], ["1", "0", "1"], True))
    a(f'<g opacity="0"><g transform="{J}">' + player(SX, SY, s1, "jump", p["home"], skin=p["skin"][1], num="23") + '</g>' + show(["0", ".12", ".3"], ["0", "1", "0"], 6) + '</g>')
    a(sh("follow", False, ["0", ".3", ".8"], ["0", "1", "0"]))
    a(sh("ready", False, ["0", ".8", ".96"], ["0", "1", "0"]))
    # the ball's whole trip: up with the jump, the arc, through the net, the bounce, the bounce pass back to the hands
    fx, fy = pr(41.75, 25)
    pts = [(hx, hy), (jx2, jy2)]
    p0, p2 = (jx2, jy2), (RX, RY - 6); c1 = ((jx2 + RX) / 2, min(jy2, RY) - 150)
    for i in range(1, 21):
        t = i / 20; pts.append(((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c1[1] + t * t * p2[1]))
    pts += [(RX, RY + 20), (fx - 2, fy - 4), ((fx + hx) / 2 + 10, fy + 34), (hx, hy)]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(seg); cum = [0]
    for sgl in seg: cum.append(cum[-1] + sgl)
    kp = lambda idx: f'{cum[idx] / tot:.3f}'
    i_rim = 22; i_net = 23; i_floor = 24
    path = ' '.join(('M' if i == 0 else 'L') + f'{x - hx:.0f} {y - hy:.0f}' for i, (x, y) in enumerate(pts))
    a(f'<g transform="translate({hx:.0f} {hy:.0f})"><g opacity="0">{bball(0, 0, 5.4, n)}'
      f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.12;.95;.96;1" dur="6s" calcMode="discrete" repeatCount="indefinite"/>'
      f'<animateMotion path="{path}" keyPoints="0;0;{kp(1)};{kp(1)};{kp(i_rim)};{kp(i_net)};{kp(i_floor)};1;1" keyTimes="0;.12;.18;.2;.44;.5;.58;.86;1" calcMode="linear" dur="6s" repeatCount="indefinite"/></g></g>')
    # the net in front of the ball, swishing as it drops through; the rim's front lip
    n0 = net(RX, RY, .72); n1 = net(RX, RY, .72, sw=7)
    d0 = n0.split('d="')[1].split('"')[0]; d1 = n1.split('d="')[1].split('"')[0]
    a(n0.replace('/>', f'><animate attributeName="d" values="{d0};{d0};{d1};{d0};{d0}" keyTimes="0;.45;.5;.58;1" dur="6s" repeatCount="indefinite"/></path>'))
    a(f'<path d="M{RX - 10:.0f} {RY:.0f} A10 3.4 0 0 0 {RX + 10:.0f} {RY:.0f}" fill="none" stroke="{p["rim"]}" stroke-width="2.6"/>')
    # the mascot dancing by the near sideline, the cheer squad at the near corner, both off the podium's row
    mx, my = 392, 794
    a(f'<ellipse cx="{mx}" cy="{my}" rx="30" ry="5" fill="#000" opacity=".2"/>')
    a(f'<g><g>{mascot(mx, my, .78, n)}'
      f'<animateTransform attributeName="transform" type="rotate" values="-7 {mx} {my};7 {mx} {my};-7 {mx} {my}" dur="1.6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></g>'
      f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0;0 0;0 -10;0 0;0 0" keyTimes="0;.1;.2;.5;.6;.7;1" dur="4s" repeatCount="indefinite"/></g>')
    for k, (cxh, top) in enumerate([(178, p["home"]), (240, "#f4f4f0")]):
        sk = p["skin"][k * 2]
        a(f'<g>{cheer(cxh, 794, .82, top, sk, True)}{show(["0", ".5"], ["1", "0"], 3, begin=k * .75)}</g>')
        a(f'<g opacity="0">{cheer(cxh, 794, .82, top, sk, False)}{show(["0", ".5"], ["0", "1"], 3, begin=k * .75)}</g>')
    # the near courtside seats, the fans' heads and shoulders in front of the sideline
    r = random.Random(17); fans = []
    for k in range(32):
        x = 60 + k * 47 + r.randint(-6, 6)
        fans.append(f'<path d="M{x - 18} 860q1-34 18-34t18 34z" fill="{r.choice(p["crowd"])}"/><circle cx="{x}" cy="{816 + r.randint(-2, 3)}" r="10" fill="{r.choice(p["skin"])}"/>')
    a(f'<rect x="0" y="828" width="{W}" height="40" fill="{p["chair"]}"/>' + ''.join(fans))
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
SHADE = ('<linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>')
def vwrap(body): return wrap(V, '<defs>' + SHADE + '</defs>' + body + '<rect x="0" y="150" width="1600" height="90" fill="url(#vs)"/>')

def arena(n, floor_y=176, crowd=True, board=None, seed=2, dim=False):
    """the arena behind a banner's subject: the dark bowl, the ad boards, the hardwood"""
    p = P(n); o = []
    o.append('<defs>' + crowd_pattern("cr", p, n, 22, 18, seed) + rg("glow", "#ffc35a", .6) + rg("pool", "#ffe9b8", .35 if n else .18) + '</defs>')
    o.append(f'<rect width="1600" height="{V}" fill="{p["roof"]}"/>')
    if crowd:
        o.append(f'<rect x="0" y="0" width="1600" height="{floor_y - 20}" fill="url(#cr)"/>')
        o.append(f'<rect x="0" y="0" width="1600" height="{floor_y - 20}" fill="{p["roof"]}" opacity="{(.55 if not n else .65) + (.2 if dim else 0)}"/>')
    yb = floor_y - 26
    o.append(f'<rect x="0" y="{yb}" width="1600" height="26" fill="{p["board"]}"/>')
    o.append(f'<path d="M0 {yb + 13} H1600" stroke="{p["led"]}" stroke-width="4" stroke-dasharray="2 7" opacity=".6"/>')
    if False:
        for i, t in enumerate(board):
            x0 = 20 + i * 400
            o.append(f'<rect x="{x0}" y="{yb + 3}" width="390" height="20" fill="{["#c8501e", "#1d2a4a"][i % 2] if not n else ["#7a2e10", "#121a30"][i % 2]}"/>' + T(x0 + 195, yb + 18, t, 13, "#fff" if not n else "#ffd9a8", ls=2))
    o.append(f'<path d="M0 {floor_y} L1600 {floor_y} L1600 240 L0 240Z" fill="{p["maple"]}"/>')
    o.append(''.join(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="{p["maple2"]}" stroke-width="1.4"/>' for y in range(floor_y + 6, 240, 9)))
    o.append(f'<ellipse cx="800" cy="{floor_y + 30}" rx="560" ry="60" fill="url(#pool)"/>')
    if dim: o.append(f'<rect width="1600" height="240" fill="#05060c" opacity="{.35 if not n else .5}"/>')
    return ''.join(o)

def big(body, k=1.2, cx=800, by=204):
    """draw a banner's subject a size up, standing where it stands"""
    return f'<g transform="translate({cx} {by}) scale({k}) translate({-cx} {-by})">{body}</g>'

def vcorners(p, n):
    """the darker apron at the corners the title and line sit on"""
    c = p["apron"]
    return (f'<path d="M0 196 L430 196 L470 240 L0 240Z" fill="{c}"/><path d="M1600 202 L1060 202 L1030 240 L1600 240Z" fill="{c}"/>'
            f'<path d="M0 196 L430 196 L470 240 L0 240Z M1600 202 L1060 202 L1030 240 L1600 240Z" fill="#000" opacity=".35"/>')

def v_sales(n):  # the slam dunk
    p = P(n); o = [arena(n, 150, board=["SLAM DUNK SAVINGS", "FULL COURT COVERAGE", "NO LAPSE LAYUPS", "NOTHING BUT NET PREMIUM"])]
    o.append(hoop(930, 92, 1.5, n, face=-1, pole_to=200))
    o.append(f'<ellipse cx="880" cy="200" rx="40" ry="6" fill="#000" opacity=".25"/>')
    o.append(player(868, 174, 1.15, "dunk", p["home"], skin=p["skin"][1], num="1"))
    o.append(f'<path d="M780 178 Q800 150 830 130" stroke="#fff" stroke-width="2" stroke-dasharray="3 7" fill="none" opacity=".5"/>')
    o.append(player(760, 196, 1.15, "contest", p["away"], skin=p["skin"][2], flip=False))
    for x, y in [(984, 70), (1004, 98), (980, 120)]: o.append(f'<path d="M{x} {y} l18 -6 M{x} {y} l16 6" stroke="#ffd24a" stroke-width="3" stroke-linecap="round"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_messages(n):  # the scorer's table
    p = P(n); o = [arena(n, 150)]
    o.append(f'<rect x="460" y="130" width="680" height="16" fill="#2a2a34"/>')
    o.append(person(600, 150, 1.0, "#1d2a4a", skin=p["skin"][0]) + person(800, 150, 1.0, "#3a3a44", skin=p["skin"][2]) + person(1000, 150, 1.0, "#1d2a4a", skin=p["skin"][1]))
    for x in (600, 800, 1000):  # headsets, laptops
        o.append(f'<path d="M{x - 8} {150 - 70} Q{x} {150 - 80} {x + 8} {150 - 70}" stroke="#111" stroke-width="2.4" fill="none"/><path d="M{x + 8} {150 - 68} q8 6 4 12" stroke="#111" stroke-width="1.6" fill="none"/>')
        o.append(f'<path d="M{x - 30} 130 L{x - 24} 112 L{x + 2} 112 L{x - 4} 130Z" fill="#9aa4b4"/><path d="M{x - 26} 128 L{x - 22} 115 L{x - 2} 115 L{x - 6} 128Z" fill="{"#7ac0ff" if n else "#cfe6f6"}"/>')
    o.append(f'<rect x="440" y="140" width="720" height="58" rx="3" fill="#101116"/>')
    o.append(f'<rect x="452" y="148" width="696" height="42" fill="{"#7a2e10" if n else "#c8501e"}"/>' + T(800, 177, "EVERY TEXT ANSWERED · NO LAPSE LAYUPS", 20, "#fff", ls=2))
    o.append(f'<rect x="784" y="88" width="32" height="20" rx="3" fill="#000"/>' + T(800, 103, "24", 14, "#ff4a2a", fam="monospace"))
    o.append(f'<path d="M760 98 L774 90 L774 106Z" fill="#ffd24a"/><path d="M840 98 L826 90 L826 106Z" fill="#555"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def whiteboard(x, y, w, h, n, routes=True):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#f6f6f2" stroke="#9aa0aa" stroke-width="3"/>',
         f'<path d="M{x + 6} {y + h * .5} H{x + w - 6} M{x + w / 2} {y + 6} V{y + h - 6}" stroke="#c0c4cc" stroke-width="1.5"/>',
         f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w * .1:.0f}" ry="{h * .14:.0f}" fill="none" stroke="#c0c4cc" stroke-width="1.5"/>']
    if routes:
        for cx, cy in [(x + w * .2, y + h * .3), (x + w * .3, y + h * .7), (x + w * .42, y + h * .45)]:
            o.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="5" fill="none" stroke="#2a5aa8" stroke-width="2.4"/>')
        for cx, cy in [(x + w * .65, y + h * .35), (x + w * .75, y + h * .65)]:
            o.append(f'<path d="M{cx - 5:.0f} {cy - 5:.0f} l10 10 M{cx + 5:.0f} {cy - 5:.0f} l-10 10" stroke="#c8301a" stroke-width="2.4"/>')
        o.append(f'<path d="M{x + w * .2 + 6:.0f} {y + h * .3:.0f} Q{x + w * .4:.0f} {y + h * .1:.0f} {x + w * .58:.0f} {y + h * .28:.0f}" stroke="#2a5aa8" stroke-width="2" fill="none" stroke-dasharray="4 4"/>')
    return ''.join(o)

def v_coaching(n):  # the huddle: the coach down on a knee with the whiteboard, the players leaning in
    p = P(n); o = [arena(n, 150, board=["FULL COURT COVERAGE", "NO LAPSE LAYUPS", "SLAM DUNK SAVINGS", "NOTHING BUT NET PREMIUM"])]
    o.append(f'<rect x="560" y="176" width="480" height="10" fill="#3a3a44"/>')
    o.append(player(610, 210, 1.1, "stand", p["home"], skin=p["skin"][0]) + player(680, 204, 1.1, "stand", p["home"], skin=p["skin"][3]))
    o.append(player(920, 204, 1.1, "stand", p["home"], skin=p["skin"][1], flip=True) + player(990, 210, 1.1, "stand", p["home"], skin=p["skin"][2], flip=True))
    o.append(person(790, 214, 1.15, "#2a2e3a", skin=p["skin"][1], pose="kneel"))
    o.append(whiteboard(800, 120, 120, 76, n))
    o.append(f'<line x1="806" y1="186" x2="820" y2="166" stroke="#222" stroke-width="3"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_roleplay(n):  # free-throw practice: the lane, the line, a rack of balls
    p = P(n); o = [arena(n, 150, board=["NOTHING BUT NET PREMIUM", "NO LAPSE LAYUPS", "FULL COURT COVERAGE", "SLAM DUNK SAVINGS"], dim=False)]
    o.append(f'<path d="M640 216 L1120 196 L1120 172 L700 180Z" fill="{p["paint"]}"/><path d="M640 216 L700 180" stroke="#fff" stroke-width="3"/><path d="M640 216 L1120 196 M700 180 L1120 172" stroke="#fff" stroke-width="3"/>')
    o.append(hoop(1120, 92, 1.4, n, face=-1, pole_to=190))
    o.append(player(660, 202, 1.2, "set", p["home"], skin=p["skin"][3], ball=True, num="7"))
    o.append(f'<path d="M680 140 Q860 20 1088 86" stroke="#fff" stroke-width="2" stroke-dasharray="3 8" fill="none" opacity=".45"/>')
    o.append(f'<rect x="470" y="170" width="90" height="6" fill="#5a5a64"/><rect x="474" y="176" width="4" height="26" fill="#5a5a64"/><rect x="552" y="176" width="4" height="26" fill="#5a5a64"/><rect x="470" y="196" width="90" height="5" fill="#5a5a64"/>')
    for k in range(4): o.append(bball(484 + k * 21, 160, 9, n))
    for k in range(3): o.append(bball(494 + k * 21, 186, 9, n))
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_rphistory(n):  # the centre-hung scoreboard showing the replay
    p = P(n); o = ['<defs>' + rg("scr", "#7ac0ff", .3) + '</defs>', f'<rect width="1600" height="{V}" fill="{p["roof"]}"/>']
    o.append(f'<rect x="0" y="14" width="1600" height="5" fill="{p["steel"]}"/><rect x="0" y="40" width="1600" height="5" fill="{p["steel"]}"/>'
             + f'<path d="' + ''.join(f'M{x} 19 L{x + 30} 40 M{x + 30} 19 L{x + 60} 40 ' for x in range(0, 1600, 60)) + f'" stroke="{p["steel2"]}" stroke-width="2"/>')
    for cx in (560, 1040): o.append(f'<line x1="{cx}" y1="45" x2="{cx}" y2="56" stroke="{p["steel2"]}" stroke-width="3"/>')
    if n: o.append('<ellipse cx="800" cy="130" rx="460" ry="120" fill="url(#scr)"/>')
    o.append(f'<path d="M520 56 L1080 56 L1120 70 L480 70Z" fill="#1a1c24"/><rect x="480" y="70" width="640" height="16" fill="#101116"/>' + T(800, 83, "INSTANT REPLAY", 11, p["led"], ls=4))
    o.append(f'<path d="M480 86 L520 94 L520 196 L480 210Z" fill="#14161c"/><path d="M1120 86 L1080 94 L1080 196 L1120 210Z" fill="#14161c"/>')
    o.append(f'<rect x="520" y="90" width="560" height="110" fill="#0a0c12"/>')
    o.append(f'<rect x="528" y="96" width="544" height="98" fill="{"#1a3466" if not n else "#132a52"}"/>')
    # on the screen: the shot, frozen, the arc traced
    o.append(f'<rect x="528" y="164" width="544" height="30" fill="#c99a62" opacity=".9"/>')
    o.append(hoop(1000, 128, .9, n, face=-1, pole_to=None))
    o.append(player(660, 178, .85, "jump", "#d8541a", skin="#a8714c"))
    o.append('<path d="M668 100 Q820 60 980 126" stroke="#fff" stroke-width="2" stroke-dasharray="3 6" fill="none"/>' + bball(820, 82, 6))
    o.append('<path d="M548 110 l16 9 l-16 9z" fill="#fff"/><rect x="528" y="188" width="544" height="6" fill="#000" opacity=".5"/><rect x="528" y="188" width="330" height="6" fill="#ff4a2a"/>')
    o.append(f'<path d="M480 210 L520 200 L1080 200 L1120 210 L1120 220 L480 220Z" fill="#101116"/>' + ''.join(f'<circle cx="{490 + i * 20}" cy="215" r="2.6" fill="{p["led"]}"/>' for i in range(32)))
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="#000" opacity=".35"/>')
    return vwrap(''.join(o))

def cone(x, y, s=1):
    return f'<path d="M{x - 9 * s:.0f} {y} L{x - 2.5 * s:.0f} {y - 22 * s:.0f} L{x + 2.5 * s:.0f} {y - 22 * s:.0f} L{x + 9 * s:.0f} {y}Z" fill="#ff7a1a"/><rect x="{x - 12 * s:.0f}" y="{y - 2}" width="{24 * s:.0f}" height="3" fill="#d8541a"/><path d="M{x - 6 * s:.0f} {y - 10 * s:.0f} h{12 * s:.0f}" stroke="#fff" stroke-width="2.4"/>'

def v_training(n):  # a dribbling drill through cones, the coach with the whistle
    p = P(n); o = [arena(n, 150, board=["NO LAPSE LAYUPS", "FULL COURT COVERAGE", "SLAM DUNK SAVINGS", "NOTHING BUT NET PREMIUM"])]
    for k, (x, y) in enumerate([(540, 190), (640, 182), (740, 194), (840, 184), (940, 196), (1040, 186)]):
        o.append(cone(x, y, 1.1))
    o.append(f'<path d="M500 200 Q590 168 640 196 Q690 214 740 180 Q790 160 840 200 Q890 220 940 182 Q990 160 1060 196" stroke="#fff" stroke-width="2" stroke-dasharray="4 7" fill="none" opacity=".55"/>')
    o.append(player(790, 206, 1.15, "dribble", p["home"], skin=p["skin"][1], ball=True, num="11"))
    o.append(person(1160, 196, 1.1, "#2a2e3a", skin=p["skin"][0], pose="point", flip=True))
    o.append(f'<path d="M1142 128 l-10 4" stroke="#c0c4cc" stroke-width="3"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the chalk playbook: the half court, Xs and Os, the play drawn through four stops
    board = "#1f3a2c" if not n else "#0e1c16"; chalk = "#eef2ea"
    route = "#5ec8ff" if athena else "#ff9a3a"
    o = [f'<rect width="1600" height="{V}" fill="#5a3a22"/><rect x="0" y="6" width="1600" height="228" fill="{board}"/>']
    r = random.Random(3)
    for _ in range(14): o.append(f'<ellipse cx="{r.randint(0, 1600)}" cy="{r.randint(20, 220)}" rx="{r.randint(60, 160)}" ry="{r.randint(8, 20)}" fill="#fff" opacity=".035"/>')
    # half court in chalk, the basket at the right
    cl = f'stroke="{chalk}" stroke-width="3" fill="none" opacity=".75"'
    o.append(f'<path d="M380 30 H1340 V214 H380" {cl}/>')
    o.append(f'<path d="M1340 82 H1150 V162 H1340 M1150 82 A40 40 0 0 0 1150 162" {cl}/>')
    o.append(f'<path d="M1340 40 H1200 A110 82 0 0 0 1200 204 H1340" {cl}/>')
    o.append(f'<path d="M380 82 A60 40 0 0 1 380 162" {cl}/><circle cx="1312" cy="122" r="9" {cl}/><path d="M1326 104 V140" {cl}/>')
    pts = [(520, 160), (760, 82), (1000, 168), (1250, 104)]
    d = f'M410 190 Q460 172 {pts[0][0]} {pts[0][1]} Q640 70 {pts[1][0]} {pts[1][1]} Q900 70 {pts[2][0]} {pts[2][1]} Q1130 196 {pts[3][0]} {pts[3][1]} Q1286 112 1306 120'
    o.append(f'<path d="{d}" fill="none" stroke="{route}" stroke-width="5" stroke-dasharray="10 8" stroke-linecap="round"/>')
    o.append(f'<path d="M1296 110 L1310 121 L1294 128" fill="none" stroke="{route}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    for x, y in [(640, 190), (880, 120), (1100, 70), (470, 92)]:
        o.append(f'<path d="M{x - 9} {y - 9} l18 18 M{x + 9} {y - 9} l-18 18" stroke="{chalk}" stroke-width="3.5" opacity=".7" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{board}" stroke="{route}" stroke-width="4"/>' + T(x, y + 6, str(i + 1), 16, route, fam="Arial, sans-serif"))
        ty = y - 26 if y > 100 else y + 44
        o.append(T(x, ty, t, 22, "#fff", fam="Arial, sans-serif", ls=1, extra=f' stroke="{board}" stroke-width="5" paint-order="stroke"'))
    o.append(T(400, 56, "play 2 · the service set" if athena else "play 1 · the sales set", 15, chalk, anchor="start", w="normal", fam="Georgia, serif", extra=' font-style="italic" opacity=".7"'))
    o.append(f'<rect x="0" y="226" width="1600" height="14" fill="#5a3a22"/><rect x="300" y="222" width="70" height="6" rx="2" fill="#f4f4f0"/><rect x="380" y="222" width="40" height="6" rx="2" fill="#ff9a3a"/>')
    return vwrap(''.join(o))

def v_service(n):  # the floor crew, dust mops across the hardwood at the break
    p = P(n); o = [arena(n, 150, board=["FULL COURT COVERAGE", "NO LAPSE LAYUPS", "SLAM DUNK SAVINGS", "NOTHING BUT NET PREMIUM"])]
    o.append(f'<path d="M560 192 L1100 192" stroke="#fff" stroke-width="3" opacity=".8"/>')
    for k, x in enumerate((600, 760, 920)):
        o.append(f'<path d="M{x + 30} 206 L{x + 160} 206" stroke="#fff" stroke-width="6" opacity="{.18 if not n else .1}"/>')
        o.append(person(x, 206, 1.15, "#2a5aa8" if k != 1 else "#3a3a44", skin=p["skin"][k], pose="mop"))
    o.append(f'<rect x="1140" y="176" width="40" height="30" rx="4" fill="#ffd24a"/><rect x="1136" y="172" width="48" height="6" fill="#d8a82a"/><path d="M1150 172 L1162 120" stroke="#8a6a3a" stroke-width="3"/>'
             '<circle cx="1146" cy="208" r="4" fill="#222"/><circle cx="1174" cy="208" r="4" fill="#222"/>')
    o.append(f'<path d="M1240 206 L1252 168 L1264 168 L1276 206Z M1246 186 h24" fill="#ffd24a" stroke="#222" stroke-width="2"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_renewals(n):  # the tip-off: the ball tossed up between two centres at the centre circle
    p = P(n); o = [arena(n, 150, board=["NO LAPSE LAYUPS", "NOTHING BUT NET PREMIUM", "FULL COURT COVERAGE", "SLAM DUNK SAVINGS"])]
    o.append(f'<ellipse cx="800" cy="206" rx="170" ry="26" fill="{p["paint"]}" stroke="#fff" stroke-width="3"/><path d="M800 166 V240" stroke="#fff" stroke-width="3"/>')
    o.append(player(752, 204, 1.2, "tip", p["home"], skin=p["skin"][1], num="5"))
    o.append(player(848, 204, 1.2, "tip", p["away"], skin=p["skin"][2], flip=True, num="9"))
    o.append(bball(800, 64, 9, n) + '<path d="M800 82 V100" stroke="#fff" stroke-width="2" stroke-dasharray="2 4" opacity=".6"/>')
    o.append(person(950, 214, 1.1, "#f4f4f4", skin=p["skin"][0], pose="toss"))
    o.append(ref_shirt(941, 156, 18, 28))
    for x in (620, 660, 940 + 60, 1040): o.append(player(x, 220, 1.0, "ready", p["home"] if x < 800 else p["away"], skin=p["skin"][x % 4], flip=x > 800))
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_claims(n):  # the shattered backboard, the crew on the lift with the new glass
    p = P(n); o = [arena(n, 150, board=["CLAIM FILED · CLAIM FIXED", "FULL COURT COVERAGE", "NO LAPSE LAYUPS", "SLAM DUNK SAVINGS"], dim=True)]
    o.append(hoop(860, 96, 1.5, n, face=-1, pole_to=198, broken=True))
    r = random.Random(6)
    for _ in range(16):
        x = r.randint(760, 900); y = r.randint(196, 214)
        o.append(f'<path d="M{x} {y} l{r.randint(4, 9)} -{r.randint(2, 5)} l{r.randint(-3, 3)} {r.randint(3, 6)}Z" fill="{p["glass"]}" opacity=".85"/>')
    # the scissor lift beside the basket, a worker on it holding the new board
    o.append(f'<rect x="1060" y="196" width="90" height="12" fill="#ffb02a"/><circle cx="1072" cy="210" r="5" fill="#222"/><circle cx="1138" cy="210" r="5" fill="#222"/>')
    o.append(f'<path d="M1066 196 L1144 150 M1144 196 L1066 150 M1066 150 L1144 104 M1144 150 L1066 104" stroke="#d8901a" stroke-width="4"/><rect x="1054" y="98" width="102" height="8" fill="#ffb02a"/>'
             f'<path d="M1054 98 V80 H1156 V98" fill="none" stroke="#d8901a" stroke-width="3"/>')
    o.append(person(1100, 98, .9, "#ff8a1a", skin=p["skin"][1], hat="#ffd24a"))
    o.append(f'<rect x="1114" y="40" width="10" height="56" fill="{p["glass"]}" opacity=".85" stroke="#fff" stroke-width="1.5"/>')
    o.append(person(700, 210, 1.1, "#ff8a1a", skin=p["skin"][2], hat="#ffd24a", pose="mop"))
    o.append(cone(600, 212, 1.1) + cone(1210, 210, 1.1))
    o.append(f'<path d="M600 196 L1210 194" stroke="#ffd24a" stroke-width="4" stroke-dasharray="14 10"/>')
    o[1:] = [big(''.join(o[1:]))]; o.append(vcorners(p, n))
    return vwrap(''.join(o))

def v_commercial(n):  # the courtside suites: a row of glass boxes over the court, guests at the rail
    p = P(n); o = [arena(n, 196, crowd=True, board=None, seed=9)]
    o.append(f'<rect x="0" y="40" width="1600" height="118" fill="{p["wall"]}"/>')
    for k in range(5):
        x = 330 + k * 196
        if n: o.append(f'<circle cx="{x + 90}" cy="96" r="110" fill="url(#glow)" opacity=".6"/>')
        o.append(f'<rect x="{x}" y="56" width="180" height="84" fill="{"#f6e4b8" if not n else "#ffd58a"}" opacity="{.85 if not n else .9}"/>')
        o.append(f'<path d="M{x} 56 h180 v84 h-180Z M{x + 60} 56 v84 M{x + 120} 56 v84" fill="none" stroke="#2a2e3a" stroke-width="4"/>')
        for j in range(3):
            o.append(person(x + 30 + j * 60, 140, .8, ["#2a2e3a", "#7a2e22", "#2a5aa8"][(k + j) % 3], skin=p["skin"][(k + j) % 4]))
        o.append(f'<rect x="{x - 6}" y="138" width="192" height="8" fill="#1a1c24"/>' + T(x + 90, 154, ["SUITE 1 · BUNDLED", "SUITE 2 · FLEET", "SUITE 3 · LIABILITY", "SUITE 4 · BOP", "SUITE 5 · WORK COMP"][k], 10, "#ffd24a", ls=1.5))
    o.append(f'<rect x="0" y="146" width="1600" height="16" fill="{p["board"]}"/>')
    o.append(f'<rect x="0" y="34" width="1600" height="8" fill="{p["steel2"]}"/>')
    o.append(vcorners(p, n))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the slam dunk: premium through the rim"],
    "messages": ["Texts & Emails", "the scorer's table: every reply on the clock"],
    "coaching": ["Coaching", "the huddle: every possession, drawn up"],
    "roleplay": ["Role Play", "free throws: shoot till it's automatic"],
    "rphistory": ["Session History", "the replay: every shot, again"],
    "training": ["Training", "the drill: around the cones, every day"],
    "blueprint": ["Apollo's Road Map", "the playbook, in plain words"],
    "athenamap": ["Athena's Road Map", "the service playbook, in plain words"],
    "service": ["Service Digest", "the floor crew: keeping the book clean"],
    "renewals": ["Renewals", "tip-off: what came back up"],
    "claims": ["Claims", "the crew: new glass after the break"],
    "commercial": ["Commercial Center", "the suites: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
FL = 100   # the floor line in the strips: the band shows ~45..115
def sbase(n, dim=False, seed=11):
    p = P(n)
    o = ['<defs>' + crowd_pattern("cr", p, n, 16, 13, seed) + rg("pool", "#ffe9b8", .35) + '</defs>',
         f'<rect width="1600" height="{S}" fill="{p["roof"]}"/><rect width="1600" height="{FL - 8}" fill="url(#cr)"/>',
         f'<rect width="1600" height="{FL - 8}" fill="{p["roof"]}" opacity="{(.72 if not n else .78) + (.15 if dim else 0)}"/>',
         f'<rect x="0" y="{FL - 10}" width="1600" height="10" fill="{p["board"]}"/>',
         f'<rect x="0" y="{FL}" width="1600" height="{S - FL}" fill="{p["maple"]}"/>' + ''.join(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="{p["maple2"]}" stroke-width="1.3"/>' for y in (106, 114, 124, 138))]
    if dim: o.append(f'<rect width="1600" height="160" fill="#05060c" opacity=".45"/>')
    return ''.join(o)

def cap(t): return T(120, 92, t, 24, "#fff", anchor="start", fam="monospace", ls=2)

def s_sold(n):  # the buzzer-beater: the swish, the board's red light on, confetti
    p = P(n); o = [sbase(n)]
    o.append(f'<ellipse cx="800" cy="{FL}" rx="380" ry="30" fill="url(#pool)"/>')
    o.append(f'<circle cx="900" cy="56" r="56" fill="#ff2a1a" opacity=".2"/>')
    o.append(hoop(900, 64, .95, n, face=-1, red=True))
    o.append(bball(884, 74, 7, n))
    o.append('<path d="M862 50 L872 60 M884 46 V58 M906 50 L896 60" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".85"/>')
    r = random.Random(5)
    for _ in range(30):
        x = r.randint(520, 1100); y = r.randint(44, 104)
        o.append(f'<rect x="{x}" y="{y}" width="7" height="12" fill="{r.choice(["#ffd24a", "#ff5a1a", "#4ab8ff", "#fff", "#5ec97a"])}" transform="rotate({r.randint(0, 90)} {x} {y})"/>')
    o.append(player(700, FL, .66, "follow", p["home"], skin=p["skin"][1]))
    o.append(cap("BUZZER BEATER"))
    return wrap(S, ''.join(o))

def s_open(n):  # the ball rolling round the rim, not down yet
    p = P(n); o = [sbase(n)]
    o.append(hoop(880, 64, .95, n, face=-1))
    o.append(bball(866, 58, 8, n))
    o.append('<path d="M842 60 Q866 44 890 60" stroke="#fff" stroke-width="2.4" fill="none" stroke-dasharray="4 5" opacity=".75"/><path d="M846 72 Q866 80 886 72" stroke="#fff" stroke-width="2.4" fill="none" stroke-dasharray="4 5" opacity=".5"/>')
    o.append(player(660, FL, .66, "follow", p["home"], skin=p["skin"][3]) + player(740, FL, .66, "ready", p["away"], skin=p["skin"][2], flip=True))
    o.append(cap("ON THE RIM"))
    return wrap(S, ''.join(o))

def s_lost(n):  # the airball under a dimmed arena: the ball falling short, under the rim, the shooter's head down
    p = P(n); o = [sbase(n, dim=True, seed=13)]
    o.append(hoop(960, 64, .95, n, face=-1))
    o.append('<path d="M650 54 Q790 30 906 90" stroke="#9aa0aa" stroke-width="2.4" stroke-dasharray="4 7" fill="none" opacity=".6"/>')
    o.append(bball(912, 94, 7, n).replace('#e0701e', '#8a6248').replace('#c8601a', '#6a4836'))
    o.append(player(610, FL, .66, "stand", "#6a5a54", skin=p["skin"][1]))
    o.append(cap("AIRBALL"))
    return wrap(S, ''.join(o))

def s_dead(n):  # out of bounds: the ball bounced over the sideline toward the empty courtside chairs
    p = P(n); o = [sbase(n, seed=17)]
    o.append(f'<rect x="0" y="{FL}" width="760" height="{S - FL}" fill="{p["apron"]}"/><path d="M760 {FL} V160" stroke="#fff" stroke-width="6"/>')
    for x in (430, 520, 610):
        o.append(f'<rect x="{x}" y="74" width="56" height="8" fill="{p["chair"]}"/><rect x="{x + 2}" y="82" width="4" height="18" fill="{p["chair"]}"/><rect x="{x + 50}" y="82" width="4" height="18" fill="{p["chair"]}"/><rect x="{x}" y="50" width="7" height="32" fill="{p["chair"]}"/>')
    o.append('<path d="M940 98 Q900 56 840 96 Q800 68 720 90" stroke="#fff" stroke-width="2.4" fill="none" stroke-dasharray="4 6" opacity=".6"/>')
    o.append(bball(706, 90, 8, n))
    o.append(cap("OUT OF BOUNDS"))
    return wrap(S, ''.join(o))

def s_reached(n):  # two teammates high-fiving
    p = P(n); o = [sbase(n, seed=19)]
    o.append(f'<ellipse cx="800" cy="{FL}" rx="220" ry="22" fill="url(#pool)"/>')
    o.append(player(766, FL, .66, "highfive", p["home"], skin=p["skin"][1]))
    o.append(player(834, FL, .66, "highfive", p["home"], skin=p["skin"][2], flip=True))
    o.append('<path d="M790 46 l-7 -7 M800 44 V34 M810 46 l7 -7" stroke="#ffd24a" stroke-width="3.4" stroke-linecap="round"/>')
    o.append(cap("NICE PASS"))
    return wrap(S, ''.join(o))

def s_live_noq(n):  # at the free-throw line, ball in hand, waiting on the whistle
    p = P(n); o = [sbase(n, seed=23)]
    o.append(f'<path d="M700 160 L760 {FL} L1040 {FL} L1040 160Z" fill="{p["paint"]}" opacity=".85"/><path d="M700 160 L760 {FL}" stroke="#fff" stroke-width="4"/>')
    o.append(hoop(1040, 64, .95, n, face=-1))
    o.append(player(730, FL + 4, .66, "stand", p["home"], skin=p["skin"][3], ball=True))
    o.append(cap("AT THE LINE"))
    return wrap(S, ''.join(o))

def s_vm(n):  # the empty court after hours: one work light over centre court
    o = ['<defs><linearGradient id="lb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff2c8" stop-opacity=".4"/><stop offset="1" stop-color="#fff2c8" stop-opacity=".06"/></linearGradient></defs>',
         f'<rect width="1600" height="{S}" fill="{"#0c0d14" if not n else "#040509"}"/>',
         f'<rect x="0" y="{FL}" width="1600" height="{S - FL}" fill="{"#2a1e14" if not n else "#1a120c"}"/>',
         '<rect x="0" y="28" width="1600" height="5" fill="#1a1c24"/>',
         '<line x1="800" y1="33" x2="800" y2="44" stroke="#2a2e3a" stroke-width="3"/><path d="M786 50 L793 44 L807 44 L814 50Z" fill="#2a2e3a"/>',
         f'<path d="M790 50 L690 {FL + 8} L910 {FL + 8} L810 50Z" fill="url(#lb)"/>',
         f'<ellipse cx="800" cy="{FL + 6}" rx="120" ry="10" fill="#fff2c8" opacity=".25"/>',
         f'<ellipse cx="800" cy="{FL + 6}" rx="70" ry="6" fill="none" stroke="#e8dcc0" stroke-width="2" opacity=".55"/>',
         bball(840, FL + 2, 6, True),
         hoop(1160, 66, 1.0, True, face=-1).replace('opacity=".85"', 'opacity=".25"'),
         cap("NO ANSWER")]
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Game night, {n}. Lace 'em up.", "Nothing but net today, {n}.", "Full court coverage, {n}.", "Take the open shot, {n}.",
             "Box out and close, {n}.", "You've got the hot hand, {n}.", "Run the play, {n}.", "Every possession counts, {n}.",
             "Eyes on the rim, {n}.", "Crash the boards, {n}.", "Beat the buzzer, {n}.", "Pass, quote, score, {n}.",
             "Follow through on every call, {n}.", "Tip-off is now, {n}.", "Slam dunk savings, {n}. Go get 'em."]

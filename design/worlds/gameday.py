"""Game Day world: American football. The Digest's stadium, the page banners and the coaching-card strips.
No real teams, leagues, logos or stadiums -- insurance names on the scoreboard, the end zones and the banners."""
import random

KEY = "gameday"
NAME = "Game Day"
FONTS = "family=Oswald:wght@500;600;700&family=Barlow:wght@400;500;600;700"
DISPLAY = "'Oswald', 'Arial Narrow', system-ui, sans-serif"
DW = 700
BODY = "'Barlow', system-ui, sans-serif"
SKY_BG = (("#3b8fdc", "#3f8f3a"), ("#070b18", "#1d4a26"))

LOOKS = [
    ("home", "Home",
     "--surface: #eceff4; --surface-raised: #ffffff; --card2: #f3f5f8; --chip: #e2e7ef; --text-primary: #111a2c; --text-muted: #5d6675; --text-secondary: #46505f; --grid: #e2e6ee; --border: #d7dce5; --border-strong: #b8c0cd; --accent: #c8102e; --accent-d: #9a0c23; --side: #0b1f44; --side2: #13305f; --sideInk: #dbe4f3; --brand: #ffffff; --brand2: #ff6b6b; --rad: 10px;",
     "--surface: #0c1220; --surface-raised: #141c2e; --card2: #1a2338; --chip: #222d46; --text-primary: #e8edf6; --text-muted: #9aa6b8; --text-secondary: #b6c0d0; --grid: #222d46; --border: #263250; --border-strong: #34446a; --accent: #ff5a64; --accent-d: #ff8a91; --side: #060d1e; --side2: #0e1d3d; --sideInk: #dbe4f3; --brand: #ffffff; --brand2: #ff6b6b;",
     ["#eceff4", "#0b1f44", "#c8102e"]),
    ("away", "Away",
     "--surface: #eef0ef; --surface-raised: #fbfcfb; --card2: #f3f5f4; --chip: #e3e8e5; --text-primary: #141a17; --text-muted: #5b6560; --text-secondary: #46504b; --grid: #e2e7e4; --border: #d6ddd9; --border-strong: #b6c1bb; --accent: #0e7a38; --accent-d: #0a5c2a; --side: #262b2e; --side2: #353c40; --sideInk: #e4e9e6; --brand: #ffffff; --brand2: #4fd27f; --rad: 12px;",
     "--surface: #0e1411; --surface-raised: #151d19; --card2: #1b2520; --chip: #223029; --text-primary: #e6eee9; --text-muted: #98a69e; --text-secondary: #b3c0b8; --grid: #223029; --border: #26352d; --border-strong: #34493d; --accent: #3fd47a; --accent-d: #79e3a2; --side: #0a0d0c; --side2: #18201c; --sideInk: #e4e9e6; --brand: #ffffff; --brand2: #4fd27f;",
     ["#eef0ef", "#262b2e", "#0e7a38"]),
    ("nightgame", "Night Game",
     "--surface: #ecebe6; --surface-raised: #fffefa; --card2: #f5f3ec; --chip: #e7e3d6; --text-primary: #17150f; --text-muted: #635e50; --text-secondary: #4d483c; --grid: #e6e2d6; --border: #dcd7c8; --border-strong: #c0b9a4; --accent: #8a6500; --accent-d: #6a4d00; --side: #0a0a0a; --side2: #1c1b17; --sideInk: #ece6d2; --brand: #ffffff; --brand2: #f5c518; --rad: 8px;",
     "--surface: #0d0d0c; --surface-raised: #171716; --card2: #1e1e1c; --chip: #282722; --text-primary: #efece2; --text-muted: #a39e8e; --text-secondary: #bfb9a8; --grid: #282722; --border: #2d2c27; --border-strong: #423f35; --accent: #f5c518; --accent-d: #ffd95a; --side: #050505; --side2: #141412; --sideInk: #ece6d2; --brand: #ffffff; --brand2: #f5c518;",
     ["#ecebe6", "#0a0a0a", "#f5c518"]),
]

RED, NAVY, GOLD, WHITE = "#c8102e", "#0b1f44", "#f5c518", "#ffffff"
SKIN = ["#f1c9a5", "#c98e62", "#8d5a3b", "#e3b48a", "#5e3b26"]
W = 1600


# ------------------------------------------------------------------ helpers
def wrap(h, body, par="xMidYMid slice"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="{par}">{body}</svg>'


def grad(gid, cols, x2=0, y2=1):
    st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in cols)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>'


def glowdef(gid, c, op=.6):
    return (f'<radialGradient id="{gid}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>')


def stars(n, x0, x1, y0, y1, seed, ops=(.35, .6, .9)):
    r = random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([.8, 1.1, 1.5, 2])}" fill="#fff" opacity="{r.choice(ops)}"/>' for _ in range(n))


def confetti(n, x0, x1, y0, y1, seed, sz=1.0):
    r = random.Random(seed); o = []
    for _ in range(n):
        x, y = r.randint(x0, x1), r.randint(y0, y1)
        o.append(f'<rect x="{x}" y="{y}" width="{6*sz:.0f}" height="{11*sz:.0f}" fill="{r.choice([RED, GOLD, WHITE, "#3fa9f5", "#4fd27f"])}" transform="rotate({r.randint(0, 170)} {x} {y})"/>')
    return ''.join(o)


def birds(pts, c="#24324a"):
    return ''.join(f'<path d="M{x-10*s:.0f} {y-5*s:.0f} q{5*s:.0f} {-4*s:.0f} {10*s:.0f} {5*s:.0f} q{5*s:.0f} {-9*s:.0f} {10*s:.0f} {-5*s:.0f}" fill="none" stroke="{c}" stroke-width="2.4" stroke-linecap="round"/>' for x, y, s in pts)


def cloud(x, y, w, op=.9, c="#fff"):
    return (f'<g fill="{c}" opacity="{op}"><ellipse cx="{x}" cy="{y}" rx="{w/2:.0f}" ry="{w/7:.0f}"/>'
            f'<ellipse cx="{x-w*.15:.0f}" cy="{y-w*.08:.0f}" rx="{w*.2:.0f}" ry="{w*.13:.0f}"/><ellipse cx="{x+w*.12:.0f}" cy="{y-w*.1:.0f}" rx="{w*.17:.0f}" ry="{w*.15:.0f}"/></g>')


def ball(x, y, r, rot=0, c="#7a3b16"):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><ellipse rx="{r}" ry="{r*.6:.1f}" fill="{c}" stroke="#3b1a08" stroke-width="{max(1, r*.08):.1f}"/>'
            f'<line x1="{-r*.35:.1f}" y1="0" x2="{r*.35:.1f}" y2="0" stroke="#fff" stroke-width="{max(1, r*.1):.1f}"/>'
            + ''.join(f'<line x1="{i*r*.12:.1f}" y1="{-r*.12:.1f}" x2="{i*r*.12:.1f}" y2="{r*.12:.1f}" stroke="#fff" stroke-width="{max(.8, r*.06):.1f}"/>' for i in (-2, -1, 0, 1, 2))
            + f'<path d="M{-r*.7:.1f} {-r*.42:.1f} q{r*.1:.1f} {r*.42:.1f} 0 {r*.84:.1f} M{r*.7:.1f} {-r*.42:.1f} q{-r*.1:.1f} {r*.42:.1f} 0 {r*.84:.1f}" fill="none" stroke="#fff" stroke-width="{max(.8, r*.07):.1f}"/></g>')


def player(x, y, s, jc, num="", pose="stand", flip=False, pants="#eeeeee", hc=None, trim="#ffffff", sock=None):
    """A footballer side-on, feet at (x, y), about 125 units tall at s=1, facing right (flip faces left)."""
    hc = hc or jc; sock = sock or jc; dk = "#1b1b22"
    o = [f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">']
    if pose == "kick":
        o.append(f'<g transform="rotate(14 -8 -46)"><rect x="-15" y="-48" width="13" height="42" rx="5" fill="{pants}"/><rect x="-15" y="-16" width="13" height="10" fill="{sock}"/><rect x="-18" y="-7" width="18" height="7" rx="3" fill="{dk}"/></g>'
                 f'<g transform="rotate(-78 8 -46)"><rect x="2" y="-48" width="13" height="44" rx="5" fill="{pants}"/><rect x="2" y="-16" width="13" height="10" fill="{sock}"/><rect x="1" y="-7" width="19" height="7" rx="3" fill="{dk}"/></g>')
    elif pose == "run":
        o.append(f'<g transform="rotate(24 -8 -46)"><rect x="-15" y="-48" width="13" height="42" rx="5" fill="{pants}"/><rect x="-15" y="-16" width="13" height="10" fill="{sock}"/><rect x="-18" y="-7" width="18" height="7" rx="3" fill="{dk}"/></g>'
                 f'<g transform="rotate(-30 8 -46)"><rect x="2" y="-48" width="13" height="42" rx="5" fill="{pants}"/><rect x="2" y="-16" width="13" height="10" fill="{sock}"/><rect x="1" y="-7" width="19" height="7" rx="3" fill="{dk}"/></g>')
    else:
        o.append(f'<rect x="-15" y="-48" width="13" height="42" rx="5" fill="{pants}"/><rect x="2" y="-48" width="13" height="42" rx="5" fill="{pants}"/>'
                 f'<rect x="-15" y="-16" width="13" height="10" fill="{sock}"/><rect x="2" y="-16" width="13" height="10" fill="{sock}"/>'
                 f'<rect x="-17" y="-7" width="17" height="7" rx="3" fill="{dk}"/><rect x="1" y="-7" width="19" height="7" rx="3" fill="{dk}"/>')
    # arms behind the body
    if pose == "up":
        arms = (f'<rect x="-33" y="-128" width="11" height="44" rx="5" fill="{jc}" transform="rotate(-16 -27 -86)"/>'
                f'<rect x="22" y="-128" width="11" height="44" rx="5" fill="{jc}" transform="rotate(16 27 -86)"/>'
                f'<circle cx="-38" cy="-128" r="6" fill="{dk}"/><circle cx="38" cy="-128" r="6" fill="{dk}"/>')
    elif pose in ("kick", "run"):
        arms = (f'<rect x="-33" y="-88" width="11" height="40" rx="5" fill="{jc}" transform="rotate(60 -27 -86)"/>'
                f'<rect x="22" y="-88" width="11" height="40" rx="5" fill="{jc}" transform="rotate(-70 27 -86)"/>')
    else:
        arms = (f'<rect x="-31" y="-86" width="11" height="40" rx="5" fill="{jc}" transform="rotate(8 -25 -86)"/>'
                f'<rect x="20" y="-86" width="11" height="40" rx="5" fill="{jc}" transform="rotate(-8 25 -86)"/>')
    o.append(arms)
    o.append(f'<path d="M-26 -88 Q0 -98 26 -88 L21 -46 L-21 -46 Z" fill="{jc}"/><rect x="-21" y="-52" width="42" height="7" fill="{pants}"/>')
    if num:
        o.append(f'<text x="0" y="-60" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="22" fill="{trim}"'
                 + (' transform="scale(-1 1)"' if flip else '') + f'>{num}</text>')
    o.append(f'<rect x="-6" y="-100" width="12" height="8" fill="{SKIN[1]}"/><circle cx="0" cy="-112" r="17" fill="{hc}"/>'
             f'<rect x="-3" y="-129" width="6" height="22" fill="{trim}" opacity=".9"/>'
             f'<path d="M9 -116 h12 v14 h-12 M12 -116 v14 M9 -109 h12" fill="none" stroke="#c9cdd4" stroke-width="2.4"/></g>')
    return ''.join(o)


def ref(x, y, s, flip=False, signal="T"):
    """A referee, stripes and white cap; signal "T" is the timeout."""
    dk = "#16161c"
    o = [f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">',
         f'<rect x="-14" y="-48" width="12" height="42" rx="4" fill="{dk}"/><rect x="2" y="-48" width="12" height="42" rx="4" fill="{dk}"/>'
         f'<rect x="-16" y="-7" width="16" height="7" rx="3" fill="#000"/><rect x="1" y="-7" width="17" height="7" rx="3" fill="#000"/>']
    if signal == "T":
        o.append('<rect x="-34" y="-158" width="56" height="11" rx="5" fill="#f4f4f4"/>'
                 '<rect x="-4" y="-150" width="11" height="66" rx="5" fill="#f4f4f4"/>'
                 '<g fill="#111"><rect x="-26" y="-158" width="5" height="11"/><rect x="-14" y="-158" width="5" height="11"/><rect x="-4" y="-140" width="11" height="5"/><rect x="-4" y="-124" width="11" height="5"/></g>'
                 '<rect x="-30" y="-110" width="11" height="40" rx="5" fill="#f4f4f4" transform="rotate(-45 -24 -88)"/>')
    else:
        o.append('<rect x="-31" y="-86" width="11" height="40" rx="5" fill="#f4f4f4" transform="rotate(8 -25 -86)"/><rect x="20" y="-86" width="11" height="40" rx="5" fill="#f4f4f4" transform="rotate(-8 25 -86)"/>')
    o.append('<path d="M-22 -90 Q0 -96 22 -90 L19 -46 L-19 -46 Z" fill="#f4f4f4"/>'
             '<g fill="#111"><rect x="-15" y="-92" width="6" height="46"/><rect x="-3" y="-94" width="6" height="48"/><rect x="9" y="-92" width="6" height="46"/></g>'
             f'<rect x="-6" y="-100" width="12" height="9" fill="{SKIN[0]}"/><circle cx="0" cy="-110" r="14" fill="{SKIN[0]}"/>'
             '<path d="M-15 -114 a15 13 0 0 1 30 0 z" fill="#fff"/><rect x="2" y="-117" width="20" height="5" rx="2" fill="#fff"/><circle cx="7" cy="-108" r="1.8" fill="#222"/></g>')
    return ''.join(o)


def goalpost(x, base, h, sc=1.0, c="#f2c21b"):
    """Front-on goalpost: post from base, crossbar at base-h*.45, uprights to base-h."""
    cb = base - h * .45; hw = 90 * sc; t = 7 * sc
    return (f'<g fill="{c}"><rect x="{x-t:.0f}" y="{cb:.0f}" width="{2*t:.0f}" height="{base-cb:.0f}"/>'
            f'<path d="M{x-t:.0f} {cb+30*sc:.0f} q0 {-24*sc:.0f} {-30*sc:.0f} {-24*sc:.0f} h{-hw+30*sc+t:.0f}" fill="none" stroke="{c}" stroke-width="0"/>'
            f'<rect x="{x-hw:.0f}" y="{cb-t:.0f}" width="{2*hw:.0f}" height="{1.6*t:.0f}"/>'
            f'<rect x="{x-hw-t*.6:.0f}" y="{base-h:.0f}" width="{1.3*t:.0f}" height="{h*.55:.0f}"/><rect x="{x+hw-t*.7:.0f}" y="{base-h:.0f}" width="{1.3*t:.0f}" height="{h*.55:.0f}"/></g>'
            f'<rect x="{x-hw-t*.5:.0f}" y="{base-h-14*sc:.0f}" width="{1.1*t:.0f}" height="{14*sc:.0f}" fill="{RED}"/><rect x="{x+hw-t*.6:.0f}" y="{base-h-14*sc:.0f}" width="{1.1*t:.0f}" height="{14*sc:.0f}" fill="{RED}"/>')


def goalpost_persp(k, base=612, h0=170, c="#f2c21b"):
    """A goalpost on end line k, seen from the 50: post at `base`, crossbar along the end line."""
    sc = lambda y: (y - VPY) / (base - VPY)
    y1, y2 = base - 44, base + 44                     # the two uprights, back and front along the end line
    p = lambda y, up: (fx(k, y), y - up * h0 * sc(y))
    bx, by = p(base, 0); cx, cy = p(base, .45)
    (ax, ay), (ex, ey) = p(y1, .45), p(y2, .45)
    (atx, aty), (etx, ety) = p(y1, 1), p(y2, 1)
    w = lambda y: 7 * sc(y)
    return (f'<g stroke="{c}" stroke-linecap="round" fill="none">'
            f'<line x1="{bx:.0f}" y1="{by:.0f}" x2="{cx:.0f}" y2="{cy:.0f}" stroke-width="{2 * w(base):.1f}"/>'
            f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{ex:.0f}" y2="{ey:.0f}" stroke-width="{1.6 * w(base):.1f}"/>'
            f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{atx:.0f}" y2="{aty:.0f}" stroke-width="{1.3 * w(y1):.1f}"/>'
            f'<line x1="{ex:.0f}" y1="{ey:.0f}" x2="{etx:.0f}" y2="{ety:.0f}" stroke-width="{1.3 * w(y2):.1f}"/></g>'
            f'<line x1="{atx:.0f}" y1="{aty:.0f}" x2="{atx:.0f}" y2="{aty - 14 * sc(y1):.0f}" stroke="{RED}" stroke-width="{w(y1):.1f}"/>'
            f'<line x1="{etx:.0f}" y1="{ety:.0f}" x2="{etx:.0f}" y2="{ety - 14 * sc(y2):.0f}" stroke="{RED}" stroke-width="{w(y2):.1f}"/>')


def crowd_def(pid, night, sc=1.0, seat=None):
    """A two-row tile of fans (8 people), so a stand is one rect."""
    if night:
        shirts = ["#7a1424", "#1d2c55", "#9aa0ad", "#7a1424", "#6b5a1a", "#1d2c55", "#5a1222", "#3a4566"]
        skins = ["#6e5444", "#4a3528", "#7b5e4a", "#3a2a20"]; seat = seat or "#0d1428"
    else:
        shirts = [RED, NAVY, WHITE, RED, GOLD, NAVY, "#e04050", "#2f4f8f"]
        skins = SKIN; seat = seat or "#55607a"
    o = [f'<pattern id="{pid}" width="48" height="40" patternUnits="userSpaceOnUse" patternTransform="scale({sc})"><rect width="48" height="40" fill="{seat}"/>']
    for i in range(8):
        row = i // 4; cx = 6 + (i % 4) * 12 + (6 if row else 0); cy = 8 + row * 20
        o.append(f'<rect x="{cx-5}" y="{cy+4}" width="11" height="10" rx="4" fill="{shirts[i]}"/><circle cx="{cx}" cy="{cy}" r="4.6" fill="{skins[(i*3) % len(skins)]}"/>')
    o.append('</pattern>')
    return ''.join(o)


def flashes(n, x0, x1, y0, y1, seed):
    r = random.Random(seed); o = []
    for _ in range(n):
        x, y = r.randint(x0, x1), r.randint(y0, y1); s = r.choice([3, 4, 5])
        o.append(f'<circle cx="{x}" cy="{y}" r="{s*3}" fill="url(#fg)"/><path d="M{x-s*2} {y} L{x+s*2} {y} M{x} {y-s*2} L{x} {y+s*2}" stroke="#fff" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="{s*.6:.1f}" fill="#fff"/>')
    return ''.join(o)


def light_bank(x, y, w, night, rows=3, cols=5):
    """A stadium light bank: a frame of lamps centred on x, top y."""
    lw = w / cols; h = rows * lw * .8 + 8
    o = [f'<rect x="{x-w/2-4:.0f}" y="{y-4}" width="{w+8:.0f}" height="{h+4:.0f}" rx="3" fill="{"#262c38" if night else "#5a6372"}"/>']
    lc = "#fffbe6" if night else "#e8edf2"
    for rr in range(rows):
        for cc in range(cols):
            o.append(f'<circle cx="{x-w/2+lw*(cc+.5):.0f}" cy="{y+4+lw*.8*(rr+.5):.0f}" r="{lw*.36:.1f}" fill="{lc}"/>')
    if night:
        o.insert(0, f'<circle cx="{x}" cy="{y+h/2:.0f}" r="{w*1.3:.0f}" fill="url(#lg)"/>')
    return ''.join(o)


def vignette(h, op=.5):
    return (f'<defs><radialGradient id="nv" cx=".5" cy=".45" r=".75"><stop offset=".4" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="{op}"/></radialGradient></defs><rect width="1600" height="{h}" fill="url(#nv)"/>')


def shade(h=240):
    """A soft dark wash in the bottom corners so the board's white words read."""
    return (f'<defs><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></linearGradient></defs>'
            f'<rect x="0" y="{h-90}" width="1600" height="90" fill="url(#sh)"/>')


# ------------------------------------------------------------------ the Digest: the stadium
SPLIT = 377
VPY, YF, DF = -600, 512, 52     # field perspective: vanishing point y, far sideline y, 5-yard spacing at the far sideline


def fx(k, y):
    return 800 + k * DF * (y - VPY) / (YF - VPY)


def skyline(night):
    H = 1700; o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice"><defs>')
    if night:
        a(grad("sky", [(0, "#04070f"), (.55, "#0b1430"), (1, "#26355e")]))
        a(glowdef("lg", "#fff6cf", .75) + glowdef("fg", "#ffffff", .8) + glowdef("mg", "#fff3c4", .35))
        a('<linearGradient id="bm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6d6" stop-opacity=".32"/><stop offset="1" stop-color="#fff6d6" stop-opacity=".04"/></linearGradient>')
        a('<radialGradient id="pool" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#e9ffd8" stop-opacity=".22"/><stop offset="1" stop-color="#e9ffd8" stop-opacity="0"/></radialGradient>')
    else:
        a(grad("sky", [(0, "#2a78d0"), (.6, "#6fb4ea"), (1, "#d8eefa")]))
        a(glowdef("sun", "#fff3b0", .8))
    a(crowd_def("cr", night) + crowd_def("cu", night, .72, "#3c4660" if not night else "#0a1022"))
    a('</defs>')
    a(f'<rect width="{W}" height="{SPLIT+10}" fill="url(#sky)"/>')
    # ---- sky ----
    if night:
        a(stars(70, 0, W, 0, 230, 7))
        a('<circle cx="300" cy="118" r="80" fill="url(#mg)"/><circle cx="300" cy="118" r="30" fill="#f4eed8"/><circle cx="312" cy="110" r="27" fill="#0a1229"/>')
    else:
        a('<circle cx="300" cy="120" r="110" fill="url(#sun)"/><circle cx="300" cy="120" r="34" fill="#fff8d2"/>')
        a(cloud(560, 120, 220, .85) + cloud(1060, 160, 260, .75) + cloud(150, 210, 200, .7))
        a(birds([(470, 140, 1.2), (500, 128, 1), (528, 146, .9), (1395, 150, 1.1), (1420, 138, .9)]))
        a(confetti(24, 520, 1450, 10, 165, 3, .9))
    # ---- the upper deck and roof, rising to the sky band ----
    roof = "#1a2236" if night else "#c9d0da"; roof2 = "#0e1424" if night else "#9aa4b3"
    a(f'<path d="M0 250 Q800 222 1600 250 L1600 {SPLIT} L0 {SPLIT} Z" fill="url(#cu)"/>')
    a(f'<path d="M0 236 Q800 206 1600 236 L1600 256 Q800 226 0 256 Z" fill="{roof}"/><path d="M0 256 Q800 226 1600 256 L1600 264 Q800 234 0 264 Z" fill="{roof2}"/>')
    for x in range(40, 1600, 80):
        a(f'<line x1="{x}" y1="{238 - 30*(1-((x-800)/800)**2):.0f}" x2="{x+40}" y2="{256 - 30*(1-((x+40-800)/800)**2):.0f}" stroke="{roof2}" stroke-width="2"/>')
    # facade band with FLORES across the rim's front
    fac = "#152040" if night else NAVY
    a(f'<path d="M0 334 Q800 312 1600 334 L1600 352 Q800 330 0 352 Z" fill="{fac}"/>')
    # pennants on the roof
    for x in [150, 380, 1240, 1380]:
        yb = 238 - 30 * (1 - ((x - 800) / 800) ** 2)
        a(f'<line x1="{x}" y1="{yb:.0f}" x2="{x}" y2="{yb-48:.0f}" stroke="{roof2}" stroke-width="3"/><path d="M{x} {yb-48:.0f} l34 9 l-34 9 z" fill="{RED if x % 3 else GOLD}"/>')
    # ---- light towers ----
    for tx, tw in [(470, 120), (1490, 120)]:
        pc = "#2d3546" if night else "#7c8695"
        a(f'<path d="M{tx-7} 90 L{tx+7} 90 L{tx+12} 250 L{tx-12} 250 Z" fill="{pc}"/>')
        for yy in range(110, 240, 34):
            a(f'<path d="M{tx-9} {yy} L{tx+9} {yy+26} M{tx+9} {yy} L{tx-9} {yy+26}" stroke="{pc}" stroke-width="2"/>')
        a(light_bank(tx, 22, tw, night))
    # ---- scoreboard ----
    sb = "#0a0f1a"; fr = "#2b3446" if night else "#4b5566"
    a(f'<rect x="690" y="140" width="16" height="100" fill="{fr}"/><rect x="894" y="140" width="16" height="100" fill="{fr}"/>')
    if night:
        a('<rect x="560" y="0" width="480" height="200" fill="url(#lg)" opacity=".5"/>')
    a(f'<rect x="590" y="16" width="420" height="140" rx="6" fill="{fr}"/><rect x="600" y="26" width="400" height="120" rx="3" fill="{sb}"/>')
    a(f'<rect x="600" y="26" width="400" height="40" fill="{RED}"/><text x="800" y="58" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="32" letter-spacing="6" fill="#fff">PREMIUM BOWL</text>')
    a('<text x="680" y="88" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" letter-spacing="3" fill="#c9d1dc">HOME</text>'
      '<text x="920" y="88" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" letter-spacing="3" fill="#c9d1dc">RISK</text>'
      f'<text x="680" y="134" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="44" fill="{GOLD}">28</text>'
      f'<text x="920" y="134" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="44" fill="{GOLD}">14</text>'
      '<rect x="752" y="78" width="96" height="30" rx="3" fill="#000"/><text x="800" y="100" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="22" fill="#ff5040">0:42</text>'
      '<text x="800" y="132" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="16" fill="#8fd0ff">4TH QTR</text>')
    # ---- blimp ----
    bc = "#c5ccd8" if night else "#f3f5f8"
    a(f'<g transform="translate(1210 78)"><path d="M86 0 l38 -22 l0 44 z M70 -6 l40 -6 l0 12 z" fill="{NAVY}"/><ellipse rx="100" ry="34" fill="{bc}"/>'
      f'<path d="M-100 0 A100 34 0 0 0 100 0 L90 8 A96 24 0 0 1 -90 8 Z" fill="{RED}"/><rect x="-22" y="30" width="44" height="12" rx="5" fill="{NAVY}"/>'
      + (f'<rect x="-60" y="-12" width="120" height="18" rx="3" fill="#0a0f1a"/><text x="0" y="2" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" letter-spacing="4" fill="{GOLD}">GET COVERED</text>'
         if night else f'<text x="0" y="4" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="16" letter-spacing="4" fill="{NAVY}">GET COVERED</text>')
      + '</g>')
    # ---- the lower bowl, horizon down ----
    a(f'<rect x="0" y="{SPLIT}" width="{W}" height="{YF-SPLIT}" fill="url(#cr)"/>')
    ai = "#2e3850" if night else "#8d97aa"
    for k in range(-14, 15, 3):
        x0 = 800 + k * 62; x1 = 800 + k * 70
        a(f'<path d="M{x0-4} {SPLIT} L{x0+4} {SPLIT} L{x1+6} 476 L{x1-6} 476 Z" fill="{ai}"/>')
    # field wall, FLORES banners, the tunnel
    wall = "#0d1730" if night else NAVY
    a(f'<rect x="0" y="474" width="{W}" height="32" fill="{wall}"/><rect x="0" y="474" width="{W}" height="4" fill="{RED}"/>')
    for x, t in [(240, "BUNDLE UP"), (1360, "NO LAPSE ZONE")]:
        a(f'<text x="{x}" y="500" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="20" letter-spacing="6" fill="#fff" opacity=".9">{t}</text>')
    a(f'<path d="M740 506 L740 470 Q800 432 860 470 L860 506 Z" fill="{wall}"/><path d="M752 506 L752 474 Q800 444 848 474 L848 506 Z" fill="#05070d"/>')
    if night:
        a('<path d="M752 506 L752 474 Q800 444 848 474 L848 506 Z" fill="#ffd27a" opacity=".25"/>')
        a(flashes(16, 20, 1580, SPLIT + 8, 466, 9))
        a(flashes(8, 20, 1580, 270, 330, 13))
    # ---- the field ----
    g1, g2 = ("#2c6e30", "#327a36") if night else ("#3d8c3a", "#47993f")
    a(f'<rect x="0" y="506" width="{W}" height="{H-506}" fill="{g1}"/>')
    yb = H
    for k in range(-16, 16):
        if k % 2:
            a(f'<path d="M{fx(k, YF):.0f} {YF} L{fx(k+1, YF):.0f} {YF} L{fx(k+1, yb):.0f} {yb} L{fx(k, yb):.0f} {yb} Z" fill="{g2}"/>')
    # end zones
    ez1, ez2 = (RED, NAVY)
    for s, c in [(-1, ez1), (1, ez2)]:
        a(f'<path d="M{fx(10*s, YF):.0f} {YF} L{fx(12*s, YF):.0f} {YF} L{fx(12*s, yb):.0f} {yb} L{fx(10*s, yb):.0f} {yb} Z" fill="{c}" opacity="{.8 if night else .92}"/>')
    a(f'<text transform="translate({fx(-11, 700):.0f} 700) rotate(-90)" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="38" letter-spacing="8" fill="#fff" opacity=".9">COVERED</text>')
    a(f'<text transform="translate({fx(11, 700):.0f} 700) rotate(90)" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="38" letter-spacing="8" fill="#fff" opacity=".9">BUNDLED</text>')
    # yard lines, sidelines
    lc = "#f2f6ee"
    a(f'<rect x="0" y="{YF-6}" width="{W}" height="6" fill="{lc}"/>')
    for k in range(-12, 13):
        w0 = 2.4 if k else 4.5
        a(f'<path d="M{fx(k, YF)-w0/2:.1f} {YF} L{fx(k, YF)+w0/2:.1f} {YF} L{fx(k, yb)+w0:.1f} {yb} L{fx(k, yb)-w0:.1f} {yb} Z" fill="{lc}" opacity="{.95 if abs(k) in (0, 10, 12) else .8}"/>')
    # numbers near the far sideline
    for k in range(-8, 9, 2):
        n = 50 - 5 * abs(k)
        a(f'<text x="{fx(k, 566):.0f}" y="566" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="34" fill="{lc}" opacity=".9">{n}</text>')
    # hash marks, every 5 yards between the lines
    for row in (628, 690):
        for k in range(-10, 10):
            x = fx(k + .5, row)
            a(f'<rect x="{x-1.5:.0f}" y="{row-5}" width="3" height="10" fill="{lc}" opacity=".7"/>')
    # goalposts at both ends
    # (Frank, 2026-10-05: "angle the field goals") -- each one stands on its end line, so its crossbar
    # runs along that line into the distance and the near upright is the taller
    for k in (-12, 12):
        a(goalpost_persp(k))
    # the benches on the far sideline, and the team coming out of the tunnel
    r = random.Random(4)
    for x0, jc in [(330, RED), (1130, NAVY)]:
        a(f'<rect x="{x0-10}" y="508" width="240" height="10" rx="3" fill="{"#1b2234" if night else "#8a93a3"}"/>')
        for i in range(9):
            px = x0 + 12 + i * 26
            a(f'<rect x="{px-5}" y="514" width="10" height="16" rx="3" fill="{jc}"/><circle cx="{px}" cy="510" r="5" fill="{jc}"/>')
    for i, (x, yy) in enumerate([(296, 534), (262, 530), (1330, 534)]):
        a(player(x, yy, .2, RED if x < 800 else NAVY, "", pose="run", flip=x > 800, hc=RED if x < 800 else NAVY, pants="#f2f2f2"))
    # ---- the stage on the 50 ----
    sx, sy = 810, 802
    if night:
        a('<radialGradient id="nv" cx=".5" cy=".3" r=".7"><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></radialGradient>'.join(['<defs>', '</defs>']))
        a(f'<rect x="0" y="506" width="{W}" height="500" fill="url(#nv)"/>')
        a(f'<path d="M{470+18} 60 L{470-18} 60 L{sx-200} {sy} L{sx-40} {sy} Z" fill="url(#bm)"/><path d="M{1490+18} 60 L{1490-18} 60 L{sx+40} {sy} L{sx+200} {sy} Z" fill="url(#bm)"/>')
        a(f'<ellipse cx="{sx}" cy="{sy}" rx="420" ry="110" fill="url(#pool)"/>')
    else:
        a(f'<ellipse cx="{sx+30}" cy="{sy+30}" rx="340" ry="52" fill="#000" opacity=".18"/>')
    side = "#16244a" if night else NAVY
    a(f'<path d="M{sx-310} {sy} L{sx-310} {sy+34} A310 46 0 0 0 {sx+310} {sy+34} L{sx+310} {sy} Z" fill="{side}"/>')
    a(f'<path d="M{sx-310} {sy+10} A310 46 0 0 0 {sx+310} {sy+10} L{sx+310} {sy+16} A310 46 0 0 1 {sx-310} {sy+16} Z" fill="{RED}"/>')
    for i in range(-5, 6):
        bx = sx + i * 56; by = sy + 26 + 40 * (1 - (i / 5.6) ** 2) ** .5
        a(f'<circle cx="{bx}" cy="{by:.0f}" r="4" fill="{"#fff3b0" if night else "#e8edf2"}"/>')
    a(f'<ellipse cx="{sx}" cy="{sy}" rx="310" ry="46" fill="{"#d9dee8" if not night else "#aeb6c6"}"/><ellipse cx="{sx}" cy="{sy}" rx="282" ry="36" fill="none" stroke="{GOLD}" stroke-width="4"/>')
    a(f'<text x="{sx}" y="{sy+12}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="30" fill="{NAVY}" opacity=".35" transform="translate(0 {sy*0.0:.0f})">50</text>')
    a('</svg>')
    return ''.join(o)


# ------------------------------------------------------------------ banners (1600 x 240)
V = 240


def sky(h, night, day=("#2a78d0", "#6fb4ea", "#d8eefa"), nt=("#04070f", "#0b1430", "#22305a"), gid="g"):
    c = nt if night else day
    return (f'<defs>{grad(gid, [(0, c[0]), (.6, c[1]), (1, c[2])])}{glowdef("lg", "#fff6cf", .7)}{glowdef("fg", "#ffffff", .8)}</defs>'
            f'<rect width="1600" height="{h}" fill="url(#{gid})"/>')


def grass(y, h, night, stripes=True, x0=0):
    g1, g2 = ("#2c6e30", "#327a36") if night else ("#3d8c3a", "#47993f")
    o = [f'<rect x="0" y="{y}" width="1600" height="{h-y}" fill="{g1}"/>']
    if stripes:
        for x in range(x0, 1600, 160):
            o.append(f'<rect x="{x}" y="{y}" width="80" height="{h-y}" fill="{g2}"/>')
    return ''.join(o)


def stands(y0, y1, night, pid="cr", sc=1.0):
    return f'<defs>{crowd_def(pid, night, sc)}</defs><rect x="0" y="{y0}" width="1600" height="{y1-y0}" fill="url(#{pid})"/>'


def tower(x, top, bottom, night, w=90):
    pc = "#2d3546" if night else "#7c8695"
    return (f'<rect x="{x-5}" y="{top+40}" width="10" height="{bottom-top-40}" fill="{pc}"/>' + light_bank(x, top, w, night, 2, 4))


def v_sales(n):  # the touchdown celebration in the end zone
    o = [sky(V, n)]
    if n:
        o.append(stars(30, 0, 1600, 0, 30, 1) + tower(300, 2, 40, n, 80) + tower(1300, 2, 40, n, 80))
    o.append(stands(34, 92, n))
    o.append(f'<rect x="0" y="30" width="1600" height="6" fill="{"#1a2236" if n else "#c9d0da"}"/>')
    if n:
        o.append(flashes(9, 40, 1560, 40, 86, 2))
    o.append(f'<rect x="0" y="92" width="1600" height="16" fill="{NAVY}"/><rect x="0" y="92" width="1600" height="3" fill="{RED}"/>')
    o.append(grass(108, V, n, False))
    o.append(f'<path d="M0 132 L1600 132 L1600 240 L0 240 Z" fill="{RED}" opacity="{.75 if n else .9}"/><rect x="0" y="128" width="1600" height="5" fill="#f2f6ee"/>')
    o.append('<text x="800" y="230" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="64" letter-spacing="22" fill="#fff" opacity=".2">PREMIUM</text>')
    o.append(goalpost(1180, 180, 150, .75))
    o.append(player(760, 196, .95, NAVY, "21", "up", hc=NAVY, trim=GOLD))
    o.append(ball(806, 54, 13, -40))
    o.append(player(660, 200, .85, NAVY, "8", "up", flip=True, hc=NAVY, trim=GOLD))
    o.append(player(870, 204, .85, NAVY, "55", "run", hc=NAVY, trim=GOLD))
    o.append(ref(1010, 204, .8, signal="TD").replace('transform="rotate(8 -25 -86)"', 'transform="rotate(172 -25 -86)"').replace('transform="rotate(-8 25 -86)"', 'transform="rotate(188 25 -86)"'))
    o.append(confetti(46, 420, 1250, 6, 200, 3))
    if n:
        o.append(vignette(V, .4))
    o.append(shade())
    return wrap(V, ''.join(o))


def v_messages(n):  # the press box: headsets, monitors, the field through the glass
    wall = "#1a2236" if n else "#3a4660"
    o = [f'<defs>{grad("gw", [(0, "#0c1a33" if n else "#6fb4ea"), (1, "#26355e" if n else "#cde8f8")])}{crowd_def("cr", n, .6)}{glowdef("sg", "#8fd0ff", .55)}</defs>',
         f'<rect width="1600" height="{V}" fill="{wall}"/>',
         '<rect x="0" y="14" width="1600" height="124" fill="url(#gw)"/>',
         '<rect x="0" y="62" width="1600" height="30" fill="url(#cr)"/>']
    o.append(grass(92, 138, n))
    for x in range(140, 1600, 220):
        o.append(f'<line x1="{x}" y1="92" x2="{x-60}" y2="138" stroke="#f2f6ee" stroke-width="2" opacity=".8"/>')
    for x in range(0, 1601, 320):
        o.append(f'<rect x="{x-6}" y="14" width="12" height="124" fill="{wall}"/>')
    o.append(f'<rect x="0" y="134" width="1600" height="16" fill="{"#2b3446" if n else "#5a6680"}"/>')
    # desk and three headset callers seen from behind, monitors
    o.append(f'<rect x="0" y="150" width="1600" height="90" fill="{"#121827" if n else "#29324a"}"/>')
    for i, x in enumerate([520, 800, 1080]):
        o.append(f'<rect x="{x-150}" y="104" width="86" height="54" rx="4" fill="#0a0f1a"/><rect x="{x-145}" y="109" width="76" height="44" fill="{"#1f6fb0" if i != 1 else "#2e8a4a"}"/>')
        o.append(f'<circle cx="{x-107}" cy="131" r="40" fill="url(#sg)"/>' if n else '')
        o.append(f'<polyline points="{x-140},146 {x-124},130 {x-110},138 {x-90},118 {x-75},126" fill="none" stroke="#fff" stroke-width="2.5"/>')
        o.append(f'<path d="M{x-46} 240 L{x-40} 176 Q{x} 154 {x+40} 176 L{x+46} 240 Z" fill="{[RED, NAVY, "#3c4660"][i]}"/>'
                 f'<circle cx="{x}" cy="150" r="24" fill="{["#3a2a20", "#7b5e4a", "#5e3b26"][i]}"/>'
                 f'<path d="M{x-26} 150 A26 26 0 0 1 {x+26} 150" fill="none" stroke="#111" stroke-width="6"/>'
                 f'<rect x="{x-32}" y="140" width="12" height="22" rx="5" fill="#111"/><rect x="{x+20}" y="140" width="12" height="22" rx="5" fill="#111"/>'
                 f'<path d="M{x+28} 160 q14 10 2 22" fill="none" stroke="#111" stroke-width="3"/><circle cx="{x+30}" cy="182" r="4" fill="#111"/>')
    o.append(f'<rect x="1220" y="112" width="150" height="40" rx="4" fill="#0a0f1a"/><text x="1295" y="140" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="22" fill="#ff5040">ON AIR</text>')
    o.append(shade())
    return wrap(V, ''.join(o))


def xo(x0, y0, w, h, chalk, red=RED):
    """X's and O's: a formation and a route, drawn in chalk."""
    o = [f'<line x1="{x0}" y1="{y0+h*.55:.0f}" x2="{x0+w}" y2="{y0+h*.55:.0f}" stroke="{chalk}" stroke-width="2" stroke-dasharray="8 6" opacity=".6"/>']
    for i in range(5):
        cx = x0 + w * (.3 + i * .1)
        o.append(f'<circle cx="{cx:.0f}" cy="{y0+h*.65:.0f}" r="{h*.05:.0f}" fill="none" stroke="{chalk}" stroke-width="3"/>')
        o.append(f'<path d="M{cx-h*.04:.0f} {y0+h*.36:.0f} l{h*.08:.0f} {h*.08:.0f} m0 {-h*.08:.0f} l{-h*.08:.0f} {h*.08:.0f}" stroke="{chalk}" stroke-width="3"/>')
    for cx, cy in [(.15, .7), (.85, .7), (.5, .82)]:
        o.append(f'<circle cx="{x0+w*cx:.0f}" cy="{y0+h*cy:.0f}" r="{h*.05:.0f}" fill="none" stroke="{chalk}" stroke-width="3"/>')
    o.append(f'<path d="M{x0+w*.15:.0f} {y0+h*.64:.0f} L{x0+w*.15:.0f} {y0+h*.25:.0f} L{x0+w*.32:.0f} {y0+h*.12:.0f}" fill="none" stroke="{red}" stroke-width="3.5"/>'
             f'<path d="M{x0+w*.32:.0f} {y0+h*.12:.0f} l-12 -2 m12 2 l-7 10" stroke="{red}" stroke-width="3.5"/>'
             f'<path d="M{x0+w*.85:.0f} {y0+h*.64:.0f} Q{x0+w*.9:.0f} {y0+h*.2:.0f} {x0+w*.68:.0f} {y0+h*.14:.0f}" fill="none" stroke="{chalk}" stroke-width="3" stroke-dasharray="7 6"/>')
    return ''.join(o)


def v_coaching(n):  # the film room: the replay on the screen, rows of chairs
    room = "#0b0f19" if n else "#1d2538"
    o = [f'<defs>{glowdef("pg", "#cfe6ff", .35)}<linearGradient id="pb" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#cfe6ff" stop-opacity=".22"/><stop offset="1" stop-color="#cfe6ff" stop-opacity="0"/></linearGradient></defs>',
         f'<rect width="1600" height="{V}" fill="{room}"/>']
    if not n:
        o.append('<rect width="1600" height="24" fill="#2a3450"/>' + ''.join(f'<rect x="{x}" y="6" width="80" height="10" rx="4" fill="#e9eef7" opacity=".7"/>' for x in (200, 760, 1320)))
    o.append('<circle cx="800" cy="100" r="420" fill="url(#pg)"/>')
    o.append('<rect x="440" y="28" width="720" height="156" rx="4" fill="#d9dee8"/><rect x="452" y="38" width="696" height="136" fill="#2f7a36"/>')
    for x in range(520, 1148, 90):
        o.append(f'<line x1="{x}" y1="38" x2="{x}" y2="174" stroke="#fff" stroke-width="2" opacity=".35"/>')
    o.append(xo(470, 38, 660, 136, "#fff"))
    o.append('<rect x="460" y="44" width="92" height="22" rx="3" fill="#000" opacity=".6"/><text x="506" y="61" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="15" fill="#ff5040">REPLAY</text>')
    o.append('<path d="M780 240 L830 240 L1160 174 L440 174 Z" fill="url(#pb)" opacity=".7"/>')
    # rows of chairs, backs to us
    cc = "#060910" if n else "#0d1220"
    for row, (y, s) in enumerate([(176, 1), (206, 1.25)]):
        for i in range(-6, 7):
            x = 800 + i * 112 * s + (40 if row else 0)
            o.append(f'<rect x="{x-38*s:.0f}" y="{y}" width="{76*s:.0f}" height="{64*s:.0f}" rx="{10*s:.0f}" fill="{cc}"/><rect x="{x-38*s:.0f}" y="{y}" width="{76*s:.0f}" height="{8*s:.0f}" rx="4" fill="{RED}" opacity=".7"/>')
    o.append(f'<circle cx="700" cy="168" r="20" fill="{cc}"/><circle cx="930" cy="166" r="21" fill="{cc}"/><rect x="926" y="140" width="8" height="8" fill="{cc}"/>')
    o.append(shade())
    return wrap(V, ''.join(o))


def dummy(x, y, h, c, pad="#e9ecf1", tilt=0):
    return (f'<g transform="rotate({tilt} {x} {y})"><ellipse cx="{x}" cy="{y}" rx="34" ry="9" fill="#111" opacity=".25"/>'
            f'<rect x="{x-26}" y="{y-h}" width="52" height="{h}" rx="22" fill="{c}"/><rect x="{x-26}" y="{y-h*.62:.0f}" width="52" height="{h*.16:.0f}" fill="{pad}"/>'
            f'<rect x="{x-26}" y="{y-h*.3:.0f}" width="52" height="{h*.08:.0f}" fill="{pad}" opacity=".8"/></g>')


def v_roleplay(n):  # the practice field: tackling dummies
    o = [sky(V, n, day=("#3c86d6", "#8cc6ee", "#e6f3fb"))]
    if n:
        o.append(stars(40, 0, 1600, 0, 90, 4))
    tree = "#0d1a14" if n else "#2f6b3e"
    for x in range(-40, 1640, 70):
        o.append(f'<circle cx="{x}" cy="{118 - (x*37 % 30)}" r="{40 + x % 20}" fill="{tree}"/>')
    o.append(grass(120, V, n, True, 40))
    for x in range(0, 1600, 24):
        o.append(f'<line x1="{x}" y1="104" x2="{x}" y2="126" stroke="{"#3a4560" if n else "#8a93a3"}" stroke-width="1.5"/>')
    o.append(f'<line x1="0" y1="106" x2="1600" y2="106" stroke="{"#3a4560" if n else "#8a93a3"}" stroke-width="2.5"/>')
    if n:
        o.append(tower(140, 22, 124, n) + tower(1460, 22, 124, n))
    for i, (x, c) in enumerate([(520, RED), (640, NAVY), (980, RED), (1100, NAVY)]):
        o.append(dummy(x, 196 + (i % 2) * 6, 104, c))
    o.append(dummy(860, 200, 104, RED, tilt=18))
    o.append(player(790, 206, .9, WHITE, "52", "run", hc=NAVY, trim=NAVY, pants="#d9dee8", sock=NAVY))
    o.append(f'<path d="M880 120 l14 -10 M888 134 l18 -4 M884 148 l16 6" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>')
    if n:
        o.append(vignette(V, .4))
    o.append(shade())
    return wrap(V, ''.join(o))


def v_rphistory(n):  # the highlight reel on the big screen
    o = [sky(V, n, day=("#2a78d0", "#6fb4ea", "#b9e0f7"))]
    if n:
        o.append(stars(40, 0, 1600, 0, 120, 5))
    else:
        o.append(cloud(260, 60, 220, .8) + cloud(1340, 70, 260, .7))
    o.append(stands(150, V, n, "cr", .9))
    if n:
        o.append(flashes(8, 30, 1560, 160, 230, 6))
    fr = "#2b3446" if n else "#4b5566"
    o.append(f'<rect x="770" y="170" width="18" height="70" fill="{fr}"/><rect x="812" y="170" width="18" height="70" fill="{fr}"/>')
    if n:
        o.append('<rect x="420" y="0" width="760" height="230" fill="url(#lg)" opacity=".45"/>')
    o.append(f'<rect x="470" y="14" width="660" height="168" rx="6" fill="{fr}"/><rect x="482" y="24" width="636" height="134" fill="#0a0f1a"/>')
    # film-strip edges
    for x in range(492, 1110, 30):
        o.append(f'<rect x="{x}" y="28" width="16" height="8" rx="2" fill="#3a4560"/><rect x="{x}" y="146" width="16" height="8" rx="2" fill="#3a4560"/>')
    o.append('<rect x="500" y="40" width="600" height="102" fill="#2f7a36"/><line x1="760" y1="40" x2="760" y2="142" stroke="#fff" stroke-width="3" opacity=".6"/>')
    o.append(f'<g transform="rotate(-62 860 128)">{player(860, 128, .62, RED, "21", "up", hc=RED)}</g>')
    o.append(ball(690, 72, 11, -30) + '<path d="M600 92 q40 -40 80 -22" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="6 6"/>')
    o.append(f'<rect x="482" y="158" width="636" height="24" fill="{RED}"/><text x="800" y="176" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="17" letter-spacing="6" fill="#fff">CLOSER HIGHLIGHTS · PLAY OF THE DAY</text>')
    o.append('<circle cx="1080" cy="56" r="7" fill="#ff3b3b"/><text x="1072" y="62" text-anchor="end" font-family="monospace" font-weight="bold" font-size="16" fill="#fff">REC</text>')
    if n:
        o.append(vignette(V, .4))
    o.append(shade())
    return wrap(V, ''.join(o))


def cone(x, y, s=1):
    return f'<path d="M{x-14*s:.0f} {y} L{x-4*s:.0f} {y-32*s:.0f} L{x+4*s:.0f} {y-32*s:.0f} L{x+14*s:.0f} {y} Z" fill="#ff7a1a"/><rect x="{x-9*s:.0f}" y="{y-16*s:.0f}" width="{18*s:.0f}" height="{5*s:.0f}" fill="#fff"/><rect x="{x-18*s:.0f}" y="{y-3}" width="{36*s:.0f}" height="5" rx="2" fill="#e05a10"/>'


def v_training(n):  # agility ladder and cone drills
    o = [sky(V, n, day=("#3c86d6", "#8cc6ee", "#f1e6c8"))]
    if n:
        o.append(stars(40, 0, 1600, 0, 80, 7) + tower(160, 20, 110, n) + tower(1450, 20, 110, n))
    else:
        o.append(cloud(1240, 54, 240, .8))
    o.append(f'<path d="M0 104 Q400 84 800 100 T1600 96 L1600 112 L0 112 Z" fill="{"#0d1a14" if n else "#5d8f5a"}"/>')
    o.append(grass(108, V, n, False))
    # the ladder in perspective, running away from us
    lc = "#ffd21a"
    o.append(f'<path d="M560 236 L700 120 M760 236 L740 120" stroke="{lc}" stroke-width="4" fill="none"/>')
    for i in range(10):
        t = i / 9; y = 236 - 116 * t ** .8
        o.append(f'<line x1="{560 + 140*t ** .8:.0f}" y1="{y:.0f}" x2="{760 - 20*t ** .8:.0f}" y2="{y:.0f}" stroke="{lc}" stroke-width="{4 - 2*t:.1f}"/>')
    o.append(player(690, 190, .78, RED, "4", "run", hc=RED))
    for i, x in enumerate(range(900, 1260, 72)):
        o.append(cone(x, 200 - (i % 2) * 34, .9))
    o.append('<path d="M890 196 Q930 150 970 172 T1050 150 T1130 170 T1210 150" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="8 7" opacity=".85"/>')
    for x in (430, 470):
        o.append(cone(x, 150, .6))
    if n:
        o.append(vignette(V, .4))
    o.append(shade())
    return wrap(V, ''.join(o))


def v_map(n, athena):  # the chalkboard playbook
    wall = "#1a1612" if n else "#6b4a2e"; wood = "#5a3a1e" if n else "#9a6a3a"
    ink = "#4fd27f" if athena else "#ff5a5a"
    stops = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    o = [f'<defs>{glowdef("lp", "#ffe9b0", .5)}</defs><rect width="1600" height="{V}" fill="{wall}"/>',
         f'<rect x="110" y="14" width="1380" height="212" rx="6" fill="{wood}"/><rect x="124" y="26" width="1352" height="188" fill="{"#1c2b22" if n else "#2c4434"}"/>']
    if n:
        o.append('<circle cx="800" cy="40" r="520" fill="url(#lp)" opacity=".5"/>')
    chalk = "#e9efe6"
    # smudges and faint old plays
    o.append(f'<ellipse cx="400" cy="90" rx="160" ry="40" fill="#fff" opacity=".05"/><ellipse cx="1160" cy="160" rx="200" ry="40" fill="#fff" opacity=".05"/>')
    for x, y in [(210, 62), (250, 120), (1380, 70), (1420, 130), (330, 190)]:
        o.append(f'<path d="M{x-9} {y-9} l18 18 m0 -18 l-18 18" stroke="{chalk}" stroke-width="3" opacity=".45"/>')
    for x, y in [(1300, 190), (1240, 60), (180, 170)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="11" fill="none" stroke="{chalk}" stroke-width="3" opacity=".45"/>')
    pts = [(400, 128), (660, 70), (940, 140), (1210, 76)]
    o.append(f'<path d="M250 190 Q300 160 {pts[0][0]} {pts[0][1]} Q470 40 {pts[1][0]} {pts[1][1]} Q760 120 {pts[2][0]} {pts[2][1]} Q1080 190 {pts[3][0]} {pts[3][1]} L1330 44" '
             f'fill="none" stroke="{chalk}" stroke-width="4" stroke-dasharray="3 12" stroke-linecap="round"/>')
    o.append(f'<path d="M1330 44 l-20 2 m20 -2 l-8 18" stroke="{chalk}" stroke-width="4" stroke-linecap="round"/>')
    for i, ((x, y), lab) in enumerate(zip(pts, stops)):
        o.append(f'<circle cx="{x}" cy="{y}" r="17" fill="{ink}"/><text x="{x}" y="{y+7}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="#fff">{i+1}</text>')
        ty = y + 42 if y < 120 else y - 28
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="bold" font-size="26" fill="{ink}">{lab}</text>')
    o.append(f'<rect x="124" y="214" width="1352" height="12" fill="{wood}"/>')
    o.append(shade())
    return wrap(V, ''.join(o))


def jersey(x, y, c, num, trim="#fff", s=1):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="-6" r="4" fill="#9aa3b5"/><path d="M-4 -4 L-28 6 L-40 34 L-26 40 L-22 30 L-22 96 L22 96 L22 30 L26 40 L40 34 L28 6 L4 -4 Q0 4 -4 -4 Z" fill="{c}"/>'
            f'<path d="M-40 34 L-26 40 M40 34 L26 40" stroke="{trim}" stroke-width="5"/><text x="0" y="66" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="30" fill="{trim}">{num}</text></g>')


def helmet(x, y, c, s=1, flip=False, stripe="#fff"):
    return (f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})"><path d="M-30 14 A30 30 0 1 1 30 4 L30 14 Z" fill="{c}"/><path d="M-25 -4 A26 26 0 0 1 22 -14" fill="none" stroke="{stripe}" stroke-width="6"/>'
            f'<path d="M22 -2 h20 v22 h-18 M30 -2 v22 M22 9 h20" fill="none" stroke="#c9cdd4" stroke-width="3.5"/><circle cx="-6" cy="4" r="5" fill="#111" opacity=".5"/></g>')


def v_service(n):  # the equipment room: jerseys on hooks, helmets on the shelf
    wall = "#1b2130" if n else "#cfd5de"; ply = "#11151f" if n else "#a9b2c0"
    o = [f'<defs>{glowdef("lp", "#ffe9b0", .55)}</defs><rect width="1600" height="{V}" fill="{wall}"/>']
    for x in range(0, 1600, 200):
        o.append(f'<rect x="{x}" y="0" width="190" height="240" fill="{ply}" opacity=".35"/>')
    if n:
        o.append('<line x1="800" y1="0" x2="800" y2="20" stroke="#555" stroke-width="2"/><path d="M780 20 h40 l12 16 h-64 z" fill="#2a2a2a"/><circle cx="800" cy="90" r="420" fill="url(#lp)" opacity=".7"/>')
    # hooks and jerseys
    o.append(f'<rect x="200" y="20" width="1200" height="8" rx="3" fill="{"#555c6a" if n else "#6c7584"}"/>')
    for i, x in enumerate(range(260, 1400, 120)):
        o.append(jersey(x, 34, [RED, NAVY][i % 2], [7, 12, 21, 33, 44, 52, 80, 88, 3, 99][i % 10], GOLD if i % 2 else "#fff", .9))
    # FLORES nameplates
    o.append(f'<rect x="680" y="140" width="240" height="0" fill="none"/>')
    # shelf with helmets
    sh = "#4a3a28" if n else "#8a6a44"
    o.append(f'<rect x="0" y="176" width="1600" height="12" fill="{sh}"/><rect x="0" y="188" width="1600" height="52" fill="{"#0c1018" if n else "#3a4152"}"/>')
    for i, x in enumerate(range(200, 1450, 140)):
        o.append(helmet(x, 150, [RED, NAVY, RED, NAVY][i % 4], .78, i % 2 == 1, GOLD if i % 2 else "#fff"))
    o.append(f'<rect x="1440" y="134" width="120" height="44" rx="4" fill="{"#2b3446" if n else "#5a6372"}"/>' + ball(1480, 140, 16, -12) + ball(1520, 136, 16, 15))
    o.append(shade())
    return wrap(V, ''.join(o))


def fan(x, y, s, shirt, skin, cap=None, flip=False):
    o = [f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})"><rect x="-12" y="-44" width="10" height="44" rx="4" fill="#2c3448"/><rect x="2" y="-44" width="10" height="44" rx="4" fill="#2c3448"/>'
         f'<path d="M-18 -92 Q0 -100 18 -92 L16 -40 L-16 -40 Z" fill="{shirt}"/><circle cx="0" cy="-108" r="14" fill="{skin}"/>']
    if cap:
        o.append(f'<path d="M-15 -110 a15 13 0 0 1 30 0 z" fill="{cap}"/><rect x="4" y="-113" width="18" height="4" rx="2" fill="{cap}"/>')
    o.append('</g>')
    return ''.join(o)


def v_renewals(n):  # the season ticket office, a line out the window
    o = [sky(V, n, day=("#3c86d6", "#8cc6ee", "#f4e6c4"))]
    if n:
        o.append(stars(40, 0, 1600, 0, 90, 8))
    else:
        o.append(cloud(1300, 50, 240, .85) + cloud(220, 40, 180, .7))
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{"#1f2430" if n else "#9a948a"}"/>')
    bw = "#2a3348" if n else "#e8e2d4"
    o.append(f'<rect x="300" y="50" width="420" height="150" fill="{bw}"/><rect x="290" y="40" width="440" height="14" fill="{NAVY}"/>')
    o.append(f'<rect x="300" y="60" width="420" height="38" fill="{RED}"/><text x="510" y="88" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="24" letter-spacing="5" fill="#fff">SEASON TICKETS</text>')
    o.append(f'<rect x="420" y="108" width="180" height="78" rx="4" fill="{"#ffd27a" if n else "#5a7a9a"}"/><rect x="420" y="146" width="180" height="6" fill="{bw}"/><rect x="410" y="182" width="200" height="10" fill="#6c7584"/>')
    o.append(fan(510, 182, .6, NAVY, SKIN[2]))
    o.append(f'<text x="510" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="{"#3a2a10" if n else "#fff"}">RENEW HERE</text>')
    o.append(f'<path d="M300 50 L270 50 L270 200 L300 200 Z" fill="{NAVY}"/><path d="M720 50 L750 50 L750 200 L720 200 Z" fill="{NAVY}"/>')
    # the line
    r = random.Random(11)
    for i, x in enumerate(range(640, 1340, 66)):
        o.append(fan(x, 214 - (i % 2) * 2, .82 - i * .012, r.choice([RED, NAVY, WHITE, GOLD]), SKIN[i % 5], r.choice([None, RED, NAVY]), flip=True))
    o.append('<path d="M1230 70 h120 v46 h-120 z" fill="#fff" opacity=".9"/><text x="1290" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="#c8102e">SOLD OUT</text>')
    if n:
        o.append(vignette(V, .4))
    o.append(shade())
    return wrap(V, ''.join(o))


def v_claims(n):  # the rain delay: the grounds crew pulls the tarp, the sky clearing
    o = [f'<defs>{grad("g", [(0, "#0c1020" if n else "#5d6678"), (1, "#26355e" if n else "#b9c8d8")], 1, 0)}{glowdef("lg", "#fff6cf", .7)}'
         f'<linearGradient id="cl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a4150" stop-opacity=".9"/><stop offset=".55" stop-color="#3a4150" stop-opacity=".5"/><stop offset="1" stop-color="#3a4150" stop-opacity="0"/></linearGradient></defs>',
         f'<rect width="1600" height="{V}" fill="url(#g)"/>']
    if n:
        o.append(stars(30, 1000, 1600, 0, 90, 9) + tower(1460, 20, 110, n))
    else:
        o.append('<circle cx="1380" cy="40" r="30" fill="#fff6c8"/>' + f'<path d="M1080 150 A240 200 0 0 1 1560 150" fill="none" stroke="#ffd27a" stroke-width="8" opacity=".5"/><path d="M1094 150 A226 186 0 0 1 1546 150" fill="none" stroke="#7fd0ff" stroke-width="8" opacity=".45"/>')
    o.append('<rect x="0" y="0" width="1200" height="90" fill="url(#cl)"/>' + cloud(240, 36, 380, .9, "#4a5263") + cloud(640, 40, 340, .8, "#565e70"))
    for i in range(46):
        x = (i * 97) % 1000; y = (i * 53) % 150
        o.append(f'<line x1="{x}" y1="{y+30}" x2="{x-10}" y2="{y+58}" stroke="#cfe0f0" stroke-width="2" opacity=".55"/>')
    o.append(grass(120, V, n))
    o.append(f'<rect x="0" y="120" width="1600" height="{V-120}" fill="#1a2a3a" opacity=".18"/>')
    # the tarp being pulled across, the roll at the left
    o.append('<path d="M500 140 L1020 132 L1060 206 L470 212 Z" fill="#2f63b0"/><path d="M500 140 L1020 132 L1024 140 L502 148 Z" fill="#fff" opacity=".25"/>')
    o.append('<rect x="440" y="134" width="70" height="82" rx="30" fill="#24508f"/><ellipse cx="475" cy="175" rx="12" ry="38" fill="#1b3f75"/>')
    for i, x in enumerate([1090, 1160, 1230]):
        o.append(f'<line x1="{1024 + i*12}" y1="{136 + i*30}" x2="{x}" y2="{150 + i*16}" stroke="#ddd" stroke-width="2.5"/>')
        o.append(fan(x + 10, 206 + i * 6, .82, "#ffd21a", SKIN[i], "#2c3448"))
    o.append('<ellipse cx="760" cy="224" rx="90" ry="6" fill="#bcd4ea" opacity=".35"/><ellipse cx="300" cy="200" rx="60" ry="5" fill="#bcd4ea" opacity=".3"/>')
    o.append(shade())
    return wrap(V, ''.join(o))


def v_commercial(n):  # the owner's suite overlooking the field
    room = "#14100c" if n else "#3a2a20"
    o = [f'<defs>{grad("gw", [(0, "#0c1a33" if n else "#6fb4ea"), (1, "#26355e" if n else "#cde8f8")])}{crowd_def("cr", n, .55)}{glowdef("lg", "#fff6cf", .7)}{glowdef("fg", "#ffffff", .8)}{glowdef("lp", "#ffcf80", .45)}</defs>',
         f'<rect width="1600" height="{V}" fill="{room}"/>',
         '<rect x="120" y="18" width="1360" height="150" fill="url(#gw)"/>']
    if n:
        o.append(stars(24, 120, 1480, 18, 50, 12) + tower(300, 24, 80, n, 70) + tower(1300, 24, 80, n, 70))
    o.append('<rect x="120" y="58" width="1360" height="40" fill="url(#cr)"/>')
    o.append(grass(98, 168, n))
    o.append('<path d="M120 98 L1480 98" stroke="#f2f6ee" stroke-width="3"/>')
    for x in range(200, 1480, 120):
        o.append(f'<line x1="{x}" y1="98" x2="{x + (x-800)*.25:.0f}" y2="168" stroke="#f2f6ee" stroke-width="2" opacity=".8"/>')
    for x in range(120, 1481, 340):
        o.append(f'<rect x="{x-7}" y="18" width="14" height="150" fill="{room}"/>')
    if n:
        o.append('<circle cx="800" cy="200" r="520" fill="url(#lp)" opacity=".6"/>')
    # the ledge, a leather chair, the table and drinks
    o.append(f'<rect x="0" y="160" width="1600" height="16" fill="{"#3a2a1a" if n else "#6b4a2e"}"/><rect x="0" y="176" width="1600" height="64" fill="{"#0c0a08" if n else "#24180f"}"/>')
    ch = "#5a1a1a" if n else "#7a2020"
    for cx in (560, 720):
        o.append(f'<path d="M{cx-56} 240 L{cx-56} 146 Q{cx-56} 126 {cx-36} 126 L{cx+36} 126 Q{cx+56} 126 {cx+56} 146 L{cx+56} 240 Z" fill="{ch}"/>'
                 f'<path d="M{cx-40} 150 h80 M{cx-40} 176 h80 M{cx} 134 v80" stroke="#000" stroke-opacity=".25" stroke-width="2"/>'
                 f'<rect x="{cx-72}" y="180" width="22" height="60" rx="9" fill="{ch}"/><rect x="{cx+50}" y="180" width="22" height="60" rx="9" fill="{ch}"/>')
    o.append('<circle cx="700" cy="122" r="15" fill="#3a2a20"/>')
    o.append(f'<rect x="860" y="186" width="260" height="10" rx="3" fill="#8a6a44"/><rect x="980" y="196" width="20" height="44" fill="#5a4028"/>'
             '<path d="M900 186 l-6 -30 h24 l-6 30 z" fill="#ffd27a" opacity=".85"/><path d="M1060 186 l-4 -26 h18 l-4 26 z" fill="#cfe6ff" opacity=".7"/><rect x="1040" y="174" width="50" height="12" rx="3" fill="#1b1b22"/>')
    o.append(f'<rect x="1180" y="132" width="180" height="34" rx="4" fill="#1b1b22"/><text x="1270" y="155" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="15" letter-spacing="4" fill="{GOLD}">OWNER&apos;S SUITE</text>')
    o.append(shade())
    return wrap(V, ''.join(o))


VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "touchdown: premium in the end zone"],
    "messages": ["Texts & Emails", "the press box: every call heard"],
    "coaching": ["Coaching", "the film room: every call, rewound"],
    "roleplay": ["Role Play", "the practice field"],
    "rphistory": ["Session History", "the highlight reel"],
    "training": ["Training", "ladders and cones"],
    "blueprint": ["Apollo's Road Map", "the playbook, in plain words"],
    "athenamap": ["Athena's Road Map", "the service playbook, in plain words"],
    "service": ["Service Digest", "the equipment room: keeping the book"],
    "renewals": ["Renewals", "season tickets: who came back"],
    "claims": ["Claims", "rain delay: the crew pulls the tarp"],
    "commercial": ["Commercial Center", "the owner's suite: Cerberus's book"],
}


# ------------------------------------------------------------------ coaching-card strips (1600 x 160; visible ~45..115)
S = 160


def cap(text, c="#fff", size=24):
    return (f'<rect x="100" y="64" width="{len(text)*size*.62 + 40:.0f}" height="38" rx="5" fill="#000" opacity=".35"/>'
            f'<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="{size}" fill="{c}">{text}</text>')


def s_sold(n):  # TOUCHDOWN: the ball through the uprights, confetti
    o = [sky(S, n, day=("#2a78d0", "#6fb4ea", "#d8eefa"))]
    if n:
        o.append(stars(40, 0, 1600, 0, 100, 21) + '<circle cx="800" cy="70" r="260" fill="url(#lg)" opacity=".6"/>')
    o.append(grass(120, S, n))
    o.append(goalpost(800, 126, 104, .8))
    o.append(ball(800, 58, 11, -60) + '<path d="M690 120 Q740 70 790 62" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="5 6" opacity=".8"/>')
    o.append(confetti(40, 380, 1180, 10, 130, 5, .9))
    o.append(cap("TOUCHDOWN", GOLD, 28))
    return wrap(S, ''.join(o))


def s_open(n):  # 1ST & 10: the down marker on the sideline, the drive alive
    o = [sky(S, n, day=("#3c86d6", "#8cc6ee", "#e6f3fb"))]
    if n:
        o.append(stars(30, 0, 1600, 0, 60, 22))
    o.append(stands(10, 74, n, "cr", .7))
    o.append(f'<rect x="0" y="70" width="1600" height="10" fill="{NAVY}"/>')
    o.append(grass(80, S, n))
    o.append('<line x1="0" y1="96" x2="1600" y2="96" stroke="#f2f6ee" stroke-width="5"/>')
    for x in (620, 1000):
        o.append(f'<line x1="{x}" y1="96" x2="{x-30}" y2="160" stroke="#f2f6ee" stroke-width="3"/>')
    # chain gang: two rods and the chain, the box with the 1
    o.append('<path d="M620 80 Q810 100 1000 80" fill="none" stroke="#c9cdd4" stroke-width="3"/>')
    for x in (620, 1000):
        o.append(f'<rect x="{x-3}" y="58" width="6" height="58" fill="#1b1b22"/><rect x="{x-10}" y="52" width="20" height="14" rx="3" fill="#ff7a1a"/>')
    o.append('<rect x="797" y="60" width="6" height="56" fill="#1b1b22"/><rect x="774" y="46" width="52" height="40" rx="4" fill="#ff7a1a"/><text x="800" y="79" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="32" fill="#111">1</text>')
    o.append(ball(880, 104, 12, 0))
    o.append(cap("1ST &amp; 10", "#fff", 26))
    return wrap(S, ''.join(o))


def s_lost(n):  # TURNOVER: a loose ball bouncing away, grey
    o = [sky(S, n, day=("#5a5f6c", "#868b98", "#b5b9c2"), nt=("#0a0c12", "#181b24", "#262a34"))]
    o.append(f'<rect x="0" y="104" width="1600" height="56" fill="{"#2a332c" if n else "#6b7a6e"}"/>')
    o.append('<line x1="0" y1="112" x2="1600" y2="112" stroke="#d9dde0" stroke-width="3" opacity=".5"/>')
    o.append('<path d="M560 96 Q600 40 650 96 Q680 62 712 96 Q730 78 750 96" fill="none" stroke="#e8eaee" stroke-width="2.5" stroke-dasharray="4 7" opacity=".7"/>')
    o.append(ball(780, 92, 16, 30, "#6b4a35"))
    o.append('<path d="M806 74 l14 -8 M810 92 l18 0 M806 110 l14 8" stroke="#e8eaee" stroke-width="3" stroke-linecap="round" opacity=".7"/>')
    o.append(f'<g opacity=".7">{player(980, 120, .55, "#7a7f8c", "", "run", flip=True, hc="#7a7f8c", pants="#b5b9c2")}</g>')
    o.append(cap("TURNOVER", "#e8eaee", 26))
    return wrap(S, ''.join(o))


def s_dead(n):  # THREE AND OUT: the punter on the sideline's edge, the ball away
    o = [sky(S, n, day=("#6a7d99", "#a7b7c9", "#dfe5ea"), nt=("#06080f", "#101626", "#1e2638"))]
    if n:
        o.append(stars(30, 0, 1600, 0, 70, 23))
    o.append(grass(110, S, n))
    o.append('<line x1="0" y1="116" x2="1600" y2="116" stroke="#f2f6ee" stroke-width="3"/>')
    o.append(player(760, 132, .66, NAVY, "9", "kick", hc=NAVY))
    o.append(ball(910, 54, 10, -70) + '<path d="M812 92 Q860 48 900 54" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="5 6" opacity=".8"/>')
    # the sideline bench, heads down
    for i, x in enumerate(range(1050, 1240, 34)):
        o.append(f'<rect x="{x-9}" y="96" width="18" height="24" rx="5" fill="{RED}"/><circle cx="{x+3}" cy="94" r="8" fill="{RED}"/>')
    o.append(f'<rect x="1030" y="118" width="220" height="10" rx="3" fill="{"#2b3446" if n else "#5a6372"}"/>')
    o.append(cap("THREE AND OUT", "#fff", 24))
    return wrap(S, ''.join(o))


def s_huddle(n):  # IN THE HUDDLE: players huddled, backs to us
    o = [sky(S, n, day=("#2a78d0", "#6fb4ea", "#d8eefa"))]
    if n:
        o.append(stars(30, 0, 1600, 0, 60, 24) + '<circle cx="800" cy="80" r="240" fill="url(#lg)" opacity=".4"/>')
    o.append(grass(104, S, n))
    for i, x in enumerate(range(600, 1020, 60)):
        h = 0 if i in (0, 6) else 4
        o.append(f'<g transform="translate({x} {130+h}) scale(.62)"><path d="M-30 -100 Q0 -112 30 -100 L26 -40 L-26 -40 Z" fill="{RED}"/>'
                 f'<text x="0" y="-60" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="26" fill="#fff">{[11, 24, 7, 81, 3, 66, 40][i]}</text>'
                 f'<circle cx="0" cy="-116" r="18" fill="{RED}"/><rect x="-3" y="-134" width="6" height="24" fill="#fff"/><rect x="-26" y="-44" width="52" height="40" rx="6" fill="#eee"/></g>')
    o.append(cap("IN THE HUDDLE", "#fff", 24))
    return wrap(S, ''.join(o))


def s_timeout(n):  # TIMEOUT: the ref signalling T
    o = [sky(S, n, day=("#3c86d6", "#8cc6ee", "#e6f3fb"))]
    if n:
        o.append(stars(30, 0, 1600, 0, 60, 25))
    o.append(stands(0, 66, n, "cr", .7))
    o.append(f'<rect x="0" y="62" width="1600" height="8" fill="{NAVY}"/>')
    o.append(grass(70, S, n))
    o.append(ref(800, 116, .42))
    o.append(f'<rect x="900" y="40" width="130" height="40" rx="4" fill="#0a0f1a"/><text x="965" y="68" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="24" fill="#ff5040">0:30</text>')
    o.append(cap("TIMEOUT", "#fff", 26))
    return wrap(S, ''.join(o))


def s_empty(n):  # EMPTY STADIUM: one light on, the moon, the mascot asleep
    o = [sky(S, True, nt=("#03050c", "#0a1022", "#141c34") if n else ("#0d1530", "#1e2a50", "#36406a"))]
    o.append(stars(46, 0, 1600, 0, 100, 26))
    o.append('<circle cx="1140" cy="60" r="16" fill="#f2ecd8"/><circle cx="1147" cy="55" r="14" fill="#0a1022"/>')
    o.append(f'<path d="M0 74 L1600 74 L1600 116 L0 116 Z" fill="#1c2438"/>')
    for y in range(80, 116, 10):
        o.append(f'<line x1="0" y1="{y}" x2="1600" y2="{y}" stroke="#2c3550" stroke-width="3"/>')
    o.append(f'<rect x="0" y="116" width="1600" height="44" fill="#14301a"/>')
    o.append('<rect x="556" y="66" width="8" height="10" fill="#2d3546"/>' + light_bank(560, 40, 70, False, 2, 4).replace("#5a6372", "#262c38").replace("#e8edf2", "#3a4256"))
    o.append('<circle cx="534" cy="50" r="6" fill="#fffbe6"/><circle cx="534" cy="50" r="26" fill="url(#lg)"/><path d="M528 56 L440 116 L620 116 Z" fill="#fff6cf" opacity=".1"/>')
    # the mascot: a round furry character asleep on the bottom row
    o.append('<g transform="translate(800 98) scale(.85)"><ellipse cx="0" cy="0" rx="46" ry="16" fill="#b57a3a"/><circle cx="-38" cy="-14" r="20" fill="#c98a46"/>'
             '<circle cx="-52" cy="-30" r="7" fill="#c98a46"/><circle cx="-26" cy="-32" r="7" fill="#c98a46"/><ellipse cx="-44" cy="-8" rx="9" ry="6" fill="#ecd2a8"/>'
             '<path d="M-46 -18 q4 3 8 0 M-32 -18 q4 3 8 0" fill="none" stroke="#3a2210" stroke-width="2"/><rect x="-6" y="-14" width="40" height="12" rx="4" fill="#c8102e"/></g>')
    o.append('<text x="770" y="68" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffd27a">z</text><text x="784" y="58" font-family="Arial, sans-serif" font-weight="bold" font-size="21" fill="#ffd27a">z</text><text x="800" y="48" font-family="Arial, sans-serif" font-weight="bold" font-size="26" fill="#ffd27a">z</text>')
    o.append(cap("EMPTY STADIUM", "#fff", 24))
    return wrap(S, ''.join(o))


STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_huddle, "live_no_quote": s_timeout,
             "callback_no_contact": s_empty}
# The header's greetings in this world only (Frank, 2026-10-05: "world themed ones that appear only in those worlds"); {n} is the first name.
GREETINGS = ['Game day, {n}.', 'Kickoff time, {n}.', 'First and ten, {n}.', 'Huddle up, {n}.', 'Put on your helmet, {n}.', "Let's run the play, {n}.", "The crowd's on its feet, {n}.", 'Go for it on fourth down, {n}.', "Scoreboard's waiting, {n}.", 'Two-minute drill, {n}.', 'Eyes on the end zone, {n}.', 'Coach says assume the sale, {n}.', 'Big game energy, {n}.', 'Call the audible, {n}. Bundle it.', 'Win the day, {n}.']

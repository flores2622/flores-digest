"""The Ocean world: a harbor at golden hour (and by moonlight).
Digest picture 1600x1700 split at 377; page vistas 1600x240; card strips 1600x160."""
import random

KEY = "ocean"
NAME = "Ocean"
CATEGORY = "Scenic"   # the group it is listed under in Settings
FONTS = "family=Merriweather:wght@700;900&family=Source+Sans+3:wght@400;500;600;700"
DISPLAY = "'Merriweather', Georgia, serif"
DW = 700
BODY = "'Source Sans 3', system-ui, sans-serif"
SKY_BG = (("#e39a6c", "#2d6c93"), ("#070d22", "#0a1730"))

LOOKS = [
    ("harbor", "Harbor",
     "--surface: #edf1f6; --surface-raised: #ffffff; --card2: #f3f6fa; --chip: #e0e7f0; --text-primary: #0f1d33; --text-muted: #55657c; --text-secondary: #3e4e66; --grid: #e2e8f0; --border: #d4dce7; --border-strong: #b4c0d0; --accent: #c8283a; --accent-d: #9c1c2b; --side: #0d1f3c; --side2: #16315c; --sideInk: #dbe5f3; --brand: #f1f5fa; --brand2: #ff6f73; --rad: 10px;",
     "--surface: #0b1424; --surface-raised: #122039; --card2: #172a48; --chip: #1f3456; --text-primary: #e8eef7; --text-muted: #9fb0c8; --text-secondary: #b9c6d8; --grid: #1f3456; --border: #233a5c; --border-strong: #33507a; --accent: #ff6b74; --accent-d: #ff9aa0; --side: #060d1a; --side2: #0e1c36; --sideInk: #dbe5f3; --brand: #f1f5fa; --brand2: #ff6f73;",
     ["#edf1f6", "#0d1f3c", "#c8283a"]),
    ("seaglass", "Sea Glass",
     "--surface: #eee8da; --surface-raised: #fbf8f1; --card2: #f3eee3; --chip: #dcebe4; --text-primary: #1b2e2a; --text-muted: #536b65; --text-secondary: #3c5550; --grid: #e6dfcf; --border: #dbd2bf; --border-strong: #bdb197; --accent: #1b7464; --accent-d: #12564a; --side: #17423d; --side2: #20564f; --sideInk: #d9efe8; --brand: #f3efe4; --brand2: #9fe0cc; --rad: 14px;",
     "--surface: #0d1716; --surface-raised: #142220; --card2: #1a2b28; --chip: #213633; --text-primary: #e4efe9; --text-muted: #98b2aa; --text-secondary: #b5cac3; --grid: #213633; --border: #24403b; --border-strong: #34574f; --accent: #6fd2bc; --accent-d: #a2e6d6; --side: #071110; --side2: #0f2320; --sideInk: #d9efe8; --brand: #f3efe4; --brand2: #9fe0cc;",
     ["#eee8da", "#17423d", "#1b7464"]),
    ("sunsetpier", "Sunset Pier",
     "--surface: #f6ece4; --surface-raised: #fffaf6; --card2: #f9efe7; --chip: #f3e0d4; --text-primary: #2a1630; --text-muted: #6b5664; --text-secondary: #563e51; --grid: #f0e1d6; --border: #e8d5c8; --border-strong: #d0b3a1; --accent: #bb4128; --accent-d: #92311d; --side: #2c1238; --side2: #3e1b4e; --sideInk: #f2dfe8; --brand: #fbefe6; --brand2: #ffc25a; --rad: 16px;",
     "--surface: #160d19; --surface-raised: #1f1424; --card2: #281a2e; --chip: #33213a; --text-primary: #f5e9ee; --text-muted: #b9a2b2; --text-secondary: #d1bcc8; --grid: #33213a; --border: #3a2742; --border-strong: #523a5c; --accent: #ff8a6b; --accent-d: #ffb199; --side: #0c0610; --side2: #1d0f26; --sideInk: #f2dfe8; --brand: #fbefe6; --brand2: #ffc25a;",
     ["#f6ece4", "#2c1238", "#ff8a6b"]),
]

# ------------------------------------------------------------------ helpers
def N(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s

def wrap(h, body, par="xMidYMid slice"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="{par}">{body}</svg>'

def lg(i, stops, x1=0, y1=0, x2=0, y2=1, user=None):
    u = f' gradientUnits="userSpaceOnUse"' if user else ""
    if user: x1, y1, x2, y2 = user
    return (f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>' +
            ''.join(f'<stop offset="{s[0]}" stop-color="{s[1]}" stop-opacity="{s[2] if len(s) > 2 else 1}"/>' for s in stops) +
            '</linearGradient>')

def rg(i, c, op=.6):
    return f'<radialGradient id="{i}"><stop offset="0" stop-color="{c}" stop-opacity="{op}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'

def stars(n, x0, x1, y0, y1, seed):
    r = random.Random(seed); o = []
    for _ in range(n):
        o.append(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([0.7, 1, 1.3, 1.8])}" fill="#fff" opacity="{r.choice([0.35, 0.55, 0.8, 0.95])}"/>')
    return ''.join(o)

def gull(x, y, s=1, c="#fff", w=3):
    return (f'<path d="M{N(x-14*s)} {N(y+3*s)} q{N(7*s)} -{N(10*s)} {N(14*s)} -1 q{N(7*s)} -{N(9*s)} {N(14*s)} 1" fill="none" '
            f'stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

def fish(x, y, s=1, c="#9fb8c8", r=0, eye="#1b2a3a"):
    return (f'<g transform="translate({N(x)} {N(y)}) rotate({r}) scale({s})"><path d="M-22 0 Q-2 -12 20 0 Q-2 12 -22 0 Z M-20 0 L-32 -9 L-29 0 L-32 9 Z" fill="{c}"/>'
            f'<circle cx="12" cy="-2" r="2" fill="{eye}"/></g>')

def waves(n, x0, x1, y0, y1, seed, c="#fff", op=.28, avoid=None):
    r = random.Random(seed); o = []
    for _ in range(n):
        x = r.randint(x0, x1); y = r.randint(y0, y1)
        if avoid and avoid(x, y): continue
        w = r.randint(10, 22)
        o.append(f'<path d="M{x} {y} q{w//2} -5 {w} 0 t{w} 0" fill="none" stroke="{c}" stroke-opacity="{op}" stroke-width="2" stroke-linecap="round"/>')
    return ''.join(o)

def sailboat(x, wy, s, hull, night, mast=120, sails=None, flag="#d8323f", flip=False, name="", flutter=0):
    """Hull centred on x with its waterline at wy; local units, scaled by s."""
    cab = "#e9e4d8" if not night else "#8a8f9e"; ink = "#2f3440" if not night else "#11141c"
    o = [f'<g transform="translate({N(x)} {N(wy)}) scale({-s if flip else s} {s})">']
    if sails:
        o.append(f'<path d="M3 {-mast+8} L3 -24 L46 -24 Z" fill="{sails[0]}"/><path d="M-3 {-mast+22} L-44 -21 L-3 -21 Z" fill="{sails[1]}"/>')
    else:
        o.append(f'<path d="M0 -27 L40 -29 L40 -24 L0 -23 Z" fill="{"#2f5f8a" if not night else "#1c2a44"}"/>')
    o.append(f'<line x1="0" y1="-16" x2="0" y2="{-mast}" stroke="{ink}" stroke-width="2.5"/>')
    if flutter:  # the pennant lifts and falls in the breeze
        d0 = f"M0 {N(-mast)} L18 {N(-mast+5)} L0 {N(-mast+10)} Z"; d1 = f"M0 {N(-mast)} L16 {N(-mast+7.5)} L0 {N(-mast+10)} Z"
        o.append(f'<path d="{d0}" fill="{flag}"><animate attributeName="d" values="{d0};{d1};{d0}" dur="{flutter}s" repeatCount="indefinite"/></path>')
    else:
        o.append(f'<path d="M0 {-mast} L18 {-mast+5} L0 {-mast+10} Z" fill="{flag}"/>')
    o.append(f'<path d="M-48 -16 L52 -16 Q45 0 30 0 L-38 0 Q-46 -6 -48 -16 Z" fill="{hull}"/>'
             f'<rect x="-46" y="-13" width="95" height="2.5" fill="#fff" opacity=".6"/>'
             f'<rect x="-18" y="-26" width="32" height="10" rx="3" fill="{cab}"/>')
    win = "#ffd56b" if night else "#5f8fb0"
    o.append(f'<rect x="-12" y="-23" width="6" height="4" fill="{win}"/><rect x="2" y="-23" width="6" height="4" fill="{win}"/>')
    if name:  # the boat's name across the hull (Frank, 2026-10-05: "be more creative with the hull names")
        tr = ' transform="scale(-1 1)"' if flip else ''
        ink2 = "#26405f" if hull in ("#f4f1ea", "#9aa0ae") else "#fff"
        o.append(f'<text x="{-2 if flip else 2}" y="-4.5" font-family="Georgia, serif" font-style="italic" font-weight="bold" font-size="7.5" fill="{ink2}" text-anchor="middle"{tr}>{name}</text>')
    o.append('</g>')
    return ''.join(o)

def trawler(x, wy, s, hull, night, flip=False, net=False, name="", mesh="mesh", haul=0):
    """A fishing boat facing right (bow at +x); flip faces it left."""
    house = "#f2ede2" if not night else "#9aa0ae"; roof = "#2f3440" if not night else "#151922"
    win = "#ffd56b" if night else "#7fb5d6"; ink = "#2f3440" if not night else "#151922"
    o = [f'<g transform="translate({N(x)} {N(wy)}) scale({-s if flip else s} {s})">']
    o.append(f'<line x1="-30" y1="-22" x2="-30" y2="-104" stroke="{ink}" stroke-width="3"/>'
             f'<line x1="-30" y1="-98" x2="-98" y2="-70" stroke="{ink}" stroke-width="2.5"/>'
             f'<line x1="-30" y1="-98" x2="40" y2="-60" stroke="{ink}" stroke-width="1.5"/>'
             f'<path d="M-30 -104 L-14 -100 L-30 -96 Z" fill="#d8323f"/>')
    if net:
        body = (f'<path d="M-100 -62 Q-128 -40 -116 -18 Q-100 -4 -82 -20 Q-74 -44 -94 -62 Z" fill="{"#c9b98a" if not night else "#6c6450"}"/>'
                + fish(-108, -36, .55, "#8fb3c7" if not night else "#5d7a8c", 70)
                + fish(-92, -30, .5, "#e3a25a" if not night else "#8a6a44", -110)
                + fish(-100, -22, .5, "#8fb3c7" if not night else "#5d7a8c", 15)
                + f'<path d="M-100 -62 Q-128 -40 -116 -18 Q-100 -4 -82 -20 Q-74 -44 -94 -62 Z" fill="url(#{mesh})" stroke="{"#8a7a50" if not night else "#4a4436"}" stroke-width="2"/>')
        if haul:
            # the net lowered into the sea and hauled back up, dripping (Frank, 2026-10-05: "i want this fish net
            # coming in and out of the water"): the line pays out, the net sinks below the waterline (clipped
            # there) and comes up full; at rest it hangs where it was drawn
            cid = f"nc{mesh}{int(x)}"
            o.append(f'<defs><clipPath id="{cid}"><rect x="-150" y="-140" width="110" height="138"/></clipPath></defs>'
                     f'<line x1="-98" y1="-70" x2="-98" y2="-62" stroke="{ink}" stroke-width="2">'
                     f'<animate attributeName="y2" values="-62;-62;-6;-6;-62;-62" keyTimes="0;.15;.4;.6;.85;1" dur="{haul}s" repeatCount="indefinite"/></line>'
                     f'<g clip-path="url(#{cid})"><g>{body}'
                     f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 70;0 70;0 0;0 0" keyTimes="0;.15;.4;.6;.85;1" dur="{haul}s" repeatCount="indefinite" '
                     f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;0 0 1 1;.45 0 .55 1;0 0 1 1"/></g></g>'
                     f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.4;.42;.7;1" dur="{haul}s" repeatCount="indefinite"/>'
                     f'<ellipse cx="-100" cy="-1" rx="22" ry="4" fill="none" stroke="#fff" stroke-width="2" opacity=".8"/>'
                     f'<path d="M-112 -2v-8M-100 -2v-12M-88 -2v-7" stroke="#cfe8f5" stroke-width="2" stroke-linecap="round"/></g>')
        else:
            o.append(f'<line x1="-98" y1="-70" x2="-98" y2="-62" stroke="{ink}" stroke-width="2"/>' + body)
    o.append(f'<path d="M-72 -22 L60 -22 Q74 -28 82 -36 L72 0 L-62 0 Q-71 -9 -72 -22 Z" fill="{hull}"/>'
             f'<path d="M-72 -22 L60 -22 Q74 -28 82 -36 L80 -30 Q72 -22 60 -17 L-71 -17 Z" fill="#fff" opacity=".55"/>'
             f'<rect x="-8" y="-54" width="40" height="32" rx="2" fill="{house}"/><rect x="-12" y="-59" width="48" height="6" rx="2" fill="{roof}"/>'
             f'<rect x="2" y="-48" width="10" height="9" fill="{win}"/><rect x="17" y="-48" width="10" height="9" fill="{win}"/>')
    if name:
        tr = ' transform="scale(-1 1)"' if flip else ''
        o.append(f'<text x="{22 if flip else -22}" y="-5" font-family="Arial, sans-serif" font-weight="bold" font-size="11" fill="#fff" text-anchor="middle"{tr}>{name}</text>')
    o.append('</g>')
    return ''.join(o)

def mesh_pattern(i="mesh", c="#7a6a44"):
    return (f'<pattern id="{i}" width="7" height="7" patternUnits="userSpaceOnUse">'
            f'<path d="M0 0 L7 7 M7 0 L0 7" stroke="{c}" stroke-width="1" opacity=".75"/></pattern>')

def lighthouse(x, base, top, w0, w1, night, red="#c8283a"):
    """Tapered striped tower from base (width w0) to top (width w1); lantern above top."""
    white = "#f6f1e6" if not night else "#b8b6b0"; rd = red if not night else "#8a2030"
    o = []
    def xs(y):
        t = (base - y) / (base - top); hw = (w0 + (w1 - w0) * t) / 2
        return x - hw, x + hw
    l0, r0 = xs(base); l1, r1 = xs(top)
    o.append(f'<path d="M{N(l0)} {base} L{N(l1)} {top} L{N(r1)} {top} L{N(r0)} {base} Z" fill="{white}"/>')
    n = 6; hgt = (base - top) / n
    for k in range(1, n, 2):
        ya = top + k * hgt; yb = ya + hgt
        la, ra = xs(ya); lb, rb = xs(yb)
        o.append(f'<path d="M{N(la)} {N(ya)} L{N(ra)} {N(ya)} L{N(rb)} {N(yb)} L{N(lb)} {N(yb)} Z" fill="{rd}"/>')
    k = 0; ya = top; yb = top + hgt; la, ra = xs(ya); lb, rb = xs(yb)
    o.append(f'<path d="M{N(la)} {N(ya)} L{N(ra)} {N(ya)} L{N(rb)} {N(yb)} L{N(lb)} {N(yb)} Z" fill="{rd}"/>')
    # shade on the right side of the tower
    o.append(f'<path d="M{N(x + (r0 - x) * .35)} {base} L{N(x + (r1 - x) * .35)} {top} L{N(r1)} {top} L{N(r0)} {base} Z" fill="#000" opacity=".12"/>')
    # small windows
    for k in range(1, n):
        yw = top + k * hgt - hgt * .5
        o.append(f'<rect x="{N(x - 4)}" y="{N(yw - 7)}" width="8" height="12" rx="4" fill="{"#ffd56b" if night else "#2f3440"}" opacity=".85"/>')
    gw = w1 + 26; L = 50
    dark = "#2f3440" if not night else "#151922"
    o.append(f'<rect x="{N(x - gw / 2)}" y="{top - 8}" width="{N(gw)}" height="8" fill="{dark}"/>')
    for k in range(7):
        xx = x - gw / 2 + 2 + k * (gw - 4) / 6
        o.append(f'<line x1="{N(xx)}" y1="{top - 8}" x2="{N(xx)}" y2="{top - 22}" stroke="{dark}" stroke-width="2"/>')
    o.append(f'<line x1="{N(x - gw / 2)}" y1="{top - 22}" x2="{N(x + gw / 2)}" y2="{top - 22}" stroke="{dark}" stroke-width="2"/>')
    lw = w1 * .7
    lamp = "#fff3c4" if night else "#ffe9a8"
    o.append(f'<rect x="{N(x - lw / 2)}" y="{top - 8 - L}" width="{N(lw)}" height="{L}" fill="{lamp}" stroke="{dark}" stroke-width="3"/>'
             f'<line x1="{x}" y1="{top - 8 - L}" x2="{x}" y2="{top - 8}" stroke="{dark}" stroke-width="2"/>'
             f'<path d="M{N(x - lw / 2 - 8)} {top - 8 - L} Q{x} {top - 8 - L - 40} {N(x + lw / 2 + 8)} {top - 8 - L} Z" fill="{rd}"/>'
             f'<circle cx="{x}" cy="{top - 8 - L - 34}" r="5" fill="{dark}"/>')
    return ''.join(o), (x, top - 8 - L / 2)

def person(x, y, s, shirt, night, wave=0, skin="#c98e6a"):
    """Standing figure, feet at y. wave: 0 none, 1 right arm up, 2 both arms up."""
    sk = skin if not night else "#7a5a48"; sh = shirt
    o = [f'<g transform="translate({N(x)} {N(y)}) scale({s})">',
         f'<rect x="-7" y="-26" width="14" height="26" rx="3" fill="#2f3440"/>',
         f'<rect x="-10" y="-52" width="20" height="28" rx="6" fill="{sh}"/>',
         f'<circle cx="0" cy="-60" r="8" fill="{sk}"/>']
    if wave >= 1: o.append(f'<path d="M8 -48 L18 -66 L22 -78" fill="none" stroke="{sh}" stroke-width="5" stroke-linecap="round"/><circle cx="22" cy="-80" r="3.5" fill="{sk}"/>')
    else: o.append(f'<path d="M8 -48 L12 -30" stroke="{sh}" stroke-width="5" stroke-linecap="round"/>')
    if wave >= 2: o.append(f'<path d="M-8 -48 L-18 -66 L-22 -78" fill="none" stroke="{sh}" stroke-width="5" stroke-linecap="round"/><circle cx="-22" cy="-80" r="3.5" fill="{sk}"/>')
    else: o.append(f'<path d="M-8 -48 L-12 -30" stroke="{sh}" stroke-width="5" stroke-linecap="round"/>')
    o.append('</g>')
    return ''.join(o)

def buoy(x, y, c, s=1, night=False, light=False):
    o = [f'<g transform="translate({N(x)} {N(y)}) scale({s})"><path d="M-12 0 L-8 -22 L8 -22 L12 0 Z" fill="{c}"/><rect x="-12" y="-12" width="24" height="5" fill="#fff" opacity=".7"/>'
         f'<line x1="0" y1="-22" x2="0" y2="-34" stroke="#2f3440" stroke-width="2.5"/>']
    if light:
        o.append(f'<circle cx="0" cy="-36" r="4" fill="#fff3c4"/><circle cx="0" cy="-36" r="12" fill="#fff3c4" opacity=".3"/>')
    o.append('</g>')
    return ''.join(o)

# ------------------------------------------------------------------ movement
# (Frank, 2026-10-05: "add movement to the other worlds too"). SMIL only -- it plays inside a background picture;
# build.py's still copy for Reduced motion deletes every <animate*/>, so each element's own attributes are its rest.
def rock(x, y, deg, dur, delay=0):
    """a gentle rock about (x, y): a moored boat or a buoy on the swell"""
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {y};{deg} {x} {y};{-deg} {x} {y}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
def drift(dx, dy, dur, delay=0):
    """drift out and back by (dx, dy): gulls gliding, ripples moving"""
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
def in_podium(el):
    """True when a wave path starts inside the podium zone, which stays still"""
    import re
    m = re.search(r'd="M(\d+) (\d+)', el)
    return bool(m) and 420 < int(m.group(1)) < 1150 and 525 < int(m.group(2)) < 815

def tw(attr, vals, dur, delay=0):
    """an attribute pulsing through its values and back to the first (banners)"""
    v = vals + vals[:1]; t = ";".join(N(i / (len(v) - 1)) for i in range(len(v)))
    return f'<animate attributeName="{attr}" values="{";".join(map(str, v))}" keyTimes="{t}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
def flow(period, dur):
    """dashes running along their line, seamless when period is the dash pattern's length"""
    return f'<animate attributeName="stroke-dashoffset" values="0;{-period}" keyTimes="0;1" dur="{dur}s" repeatCount="indefinite"/>'
def twinkle(pts):
    """a few night stars that brighten and dim"""
    return ''.join(f'<circle cx="{x}" cy="{y}" r="1.6" fill="#fff" opacity=".4">{tw("opacity", [.4, 1, .2], 2 + i * .7, i * .4)}</circle>' for i, (x, y) in enumerate(pts))

# ------------------------------------------------------------------ the Digest picture
W, H, SPLIT = 1600, 1700, 377

def skyline(night):
    o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    if night:
        a('<defs>' + lg("sky", [(0, "#050a1a"), (.55, "#0d1a3a"), (1, "#1d3058")]) +
          lg("sea", [(0, "#1a2a4a"), (.15, "#0f1f3c"), (1, "#081428")], user=(0, 377, 0, 1000)) +
          rg("glow", "#fff3c4", .5) + rg("moong", "#dfe8ff", .35) + rg("lampg", "#ffd27a", .55) +
          lg("beam", [(0, "#fff3c4", 0), (1, "#fff3c4", .38)], 0, 0, 1, 0) +
          lg("beam2", [(0, "#fff3c4", .32), (1, "#fff3c4", 0)], 0, 0, 1, 0) +
          mesh_pattern("mesh", "#3a3628") + '</defs>')
    else:
        a('<defs>' + lg("sky", [(0, "#3d5d96"), (.42, "#b98aa0"), (.72, "#f2a172"), (1, "#ffd99a")]) +
          lg("sea", [(0, "#e9ad80"), (.12, "#7f9db0"), (.3, "#3f7ea3"), (1, "#1d5a80")], user=(0, 377, 0, 1000)) +
          rg("glow", "#fff1c4", .7) + mesh_pattern("mesh", "#7a6a44") + '</defs>')
    a(f'<rect width="{W}" height="{SPLIT + 30}" fill="url(#sky)"/>')
    # ---------- sky
    if night:
        a(stars(130, 0, W, 0, 360, 7))
        for pts in [[(620, 40), (660, 62), (705, 58), (735, 92), (780, 84)], [(1250, 30), (1290, 52), (1330, 40), (1352, 78)]]:
            a('<polyline points="' + ' '.join(f'{x},{y}' for x, y in pts) + '" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1"/>')
            for x, y in pts: a(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff"/>')
        a('<circle cx="1080" cy="105" r="140" fill="url(#moong)"/><circle cx="1080" cy="105" r="42" fill="#f1eedf"/>'
          '<circle cx="1066" cy="94" r="8" fill="#d9d4c0"/><circle cx="1094" cy="118" r="6" fill="#d9d4c0"/><circle cx="1090" cy="88" r="4" fill="#d9d4c0"/>')
        for x, y, w in [(330, 150, 300), (860, 160, 260)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="9" fill="#3a4c78" opacity=".55"/>')
    else:
        a('<circle cx="1080" cy="120" r="170" fill="url(#glow)"/><circle cx="1080" cy="120" r="50" fill="#fff4d0"/><circle cx="1080" cy="120" r="44" fill="#ffe7a6"/>')
        for x, y, w in [(330, 140, 320), (820, 70, 240), (1290, 160, 300), (560, 165, 220)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="11" fill="#ffd0b0" opacity=".55"/><ellipse cx="{x + 50}" cy="{y - 9}" rx="{w // 3}" ry="9" fill="#ffe1c8" opacity=".5"/>')
    gc = "#fff" if night else "#3a3346"
    for i, (x, y, s) in enumerate([(560, 70, 1.1), (610, 48, .9), (660, 82, .8), (930, 40, 1), (975, 60, .75), (1200, 150, .8)]):
        a(f'<g>{gull(x, y, s, gc if not night else "#cfd8ee", 3)}{drift(26 + i * 5, -6 + (i % 3) * 5, 8 + i * 1.3, -i * 1.7)}</g>')
    # ---------- far shore with the town
    shore = "#7a6478" if not night else "#0b1326"
    a(f'<path d="M0 {SPLIT} L1600 {SPLIT} L1600 404 L0 404 Z" fill="url(#sea)"/>')
    a(f'<path d="M380 404 Q420 384 470 386 L1240 384 Q1280 386 1300 404 Z" fill="{shore}"/>')
    r = random.Random(4); x = 480
    lights = []
    while x < 1220:
        w = r.randint(18, 34); h = r.randint(10, 24)
        c = r.choice(["#efe0cf", "#e7c3a6", "#cfe0e6", "#f2d48c"]) if not night else "#141d36"
        a(f'<rect x="{x}" y="{402 - h}" width="{w}" height="{h}" fill="{c}"/><path d="M{x - 2} {402 - h} L{x + w / 2:.0f} {394 - h} L{x + w + 2} {402 - h} Z" fill="{"#a5574a" if not night else "#0c1224"}"/>')
        if night and r.random() < .75:
            wx = x + w // 2 - 3; lights.append(wx + 3)
            tw = (f'<animate attributeName="opacity" values="1;1;.25;1" keyTimes="0;.8;.88;1" dur="{5 + len(lights) % 5}s" begin="{-(len(lights) * 1.3) % 7:.1f}s" repeatCount="indefinite"/>'
                  if len(lights) % 3 == 0 else '')
            a(f'<rect x="{wx}" y="{404 - h + 6}" width="6" height="5" fill="#ffd56b">{tw}</rect>' if tw else f'<rect x="{wx}" y="{404 - h + 6}" width="6" height="5" fill="#ffd56b"/>')
        x += w + r.randint(2, 14)
    a(f'<rect x="760" y="356" width="12" height="40" fill="{"#efe0cf" if not night else "#141d36"}"/><path d="M756 356 L766 336 L776 356 Z" fill="{"#a5574a" if not night else "#0c1224"}"/>')
    # ---------- the water
    a(f'<rect x="0" y="404" width="{W}" height="{H - 404}" fill="url(#sea)"/>')
    for lx in lights:
        a(f'<rect x="{lx - 2}" y="408" width="4" height="{random.Random(lx).randint(18, 40)}" fill="#ffd56b" opacity=".45"/>')
    r = random.Random(9)
    for i in range(26):
        y = 412 + i * 13; w = 18 + i * 5 + r.randint(-6, 8)
        op = max(.15, .8 - i * .025)
        sh = (f'<animate attributeName="opacity" values="{op:.2f};{op * .35:.2f};{op:.2f}" dur="{3 + (i * 7) % 5 * .6:.1f}s" begin="{-i * .7:.1f}s" repeatCount="indefinite"/>'
              if y < 530 else '')
        rx = f'{1080 - w / 2 + r.randint(-12, 12):.0f}'; fc_ = "#ffe1a0" if not night else "#e6ecfb"
        a(f'<rect x="{rx}" y="{y}" width="{w}" height="3" rx="1.5" fill="{fc_}" opacity="{op:.2f}">{sh}</rect>' if sh else
          f'<rect x="{rx}" y="{y}" width="{w}" height="3" rx="1.5" fill="{fc_}" opacity="{op:.2f}"/>')
    wv = waves(70, 0, 1600, 420, 840, 3, "#fff", .22 if not night else .14,
               avoid=lambda x, y: (520 < x < 1110 and y > 750) or (x > 1220 and y < 760) or (1040 < x < 1300 and 600 < y < 830))
    wv = [e + '/>' for e in wv.split('/>') if e]
    a(''.join(e for e in wv if in_podium(e)))
    rest = [e for e in wv if not in_podium(e)]
    for k in range(2):  # the ripples drift with the swell, two sets out of step
        a(f'<g>{"".join(rest[k::2])}{drift(14 if k else -12, 2, 7 + k * 2.5, -k * 3)}</g>')
    # ---------- moored sailboats, masts rising into the sky
    hulls = ["#f4f1ea", "#1f3d66", "#2a8a86", "#c8283a", "#f4f1ea", "#26405f"] if not night else ["#9aa0ae", "#16243c", "#1a4a4c", "#5e1c26", "#9aa0ae", "#16243c"]
    names = ["SEAS THE DEAL", "NO LAPSE", "BUNDLE UP", "SHIP HAPPENS", "PAID IN FULL", "KNOT INSURED"]
    for (bx, wy, s, top, sails), hc, fl, nm in zip([(110, 500, 1.2, 104, None), (250, 468, 1.0, 92, None), (420, 524, 1.3, 70, None),
                                               (565, 480, .9, 120, None), (760, 528, 1.0, 64, None), (905, 512, .9, 108, None)],
                                              hulls, ["#d8323f", "#f2c14e", "#d8323f", "#2f6fa8", "#f2c14e", "#d8323f"], names):
        k = names.index(nm)
        a(f'<g>{sailboat(bx, wy, s, hc, night, mast=(wy - 16 * s - top) / s + 16, flag=fl, name=nm, flutter=round(1.6 + k * .23, 2))}'
          f'{rock(bx, wy, 1.1 + (k % 3) * .3, 4.5 + k * .7, -k * 1.1)}</g>')
        a(f'<ellipse cx="{bx}" cy="{wy + 4}" rx="{60 * s:.0f}" ry="4" fill="#000" opacity=".12"/>')
    # ---------- the rocky point and the lighthouse (right)
    rk = "#6b5a5a" if not night else "#151b2c"; rk2 = "#55474b" if not night else "#0d1220"; rk3 = "#8a7470" if not night else "#1d2538"
    a(f'<path d="M1230 640 Q1240 580 1300 560 Q1320 500 1380 486 Q1430 446 1500 452 Q1560 440 1600 430 L1600 780 L1250 760 Q1220 700 1230 640 Z" fill="{rk}"/>'
      f'<path d="M1300 560 Q1360 560 1380 600 Q1420 640 1500 620 L1600 640 L1600 780 L1250 760 Q1240 700 1260 650 Z" fill="{rk2}"/>'
      f'<path d="M1330 520 Q1370 500 1420 512 Q1400 530 1350 534 Z M1480 470 Q1530 458 1580 466 Q1550 480 1500 482 Z" fill="{rk3}"/>')
        # keeper's house
    hw = "#f6f1e6" if not night else "#2a3046"
    a(f'<rect x="1316" y="470" width="86" height="56" fill="{hw}"/><path d="M1308 472 L1359 436 L1410 472 Z" fill="{"#c8283a" if not night else "#5e1c26"}"/>'
      f'<rect x="1330" y="488" width="16" height="16" fill="{"#7fb5d6" if not night else "#ffd56b"}"/><rect x="1372" y="488" width="16" height="16" fill="{"#7fb5d6" if not night else "#ffd56b"}"/>'
      f'<rect x="1388" y="430" width="10" height="24" fill="{rk2}"/>')
    lh, (lx, ly) = lighthouse(1480, 470, 128, 104, 60, night)
    if night:
        a(f'<g><path d="M{lx} {ly - 6} L380 0 L380 200 L{lx} {ly + 6} Z" fill="url(#beam)"/>'
          f'<path d="M{lx} {ly - 4} L1600 {ly - 40} L1600 {ly + 40} L{lx} {ly + 4} Z" fill="url(#beam2)"/>'
          f'<animateTransform attributeName="transform" type="rotate" values="0 {lx} {ly};6 {lx} {ly};-3 {lx} {ly};0 {lx} {ly}" dur="10s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></g>')
    a(lh)
    if night:
        a(f'<circle cx="{lx}" cy="{ly}" r="70" fill="url(#lampg)"/>')
    # ---------- fishing boats coming in
    for x0, y0, fl, sc in [(250, 690, False, 1.55), (1130, 502, True, 1.05)]:
        d = -1 if fl else 1; st = x0 - d * 64 * sc; L = 80 if fl else 150
        a(f'<ellipse cx="{st:.0f}" cy="{y0 - 2}" rx="{18 * sc:.0f}" ry="5" fill="#fff" opacity=".5"/><path d="M{st:.0f} {y0 - 2} q{-d * L // 2} -2 {-d * L} -10 M{st:.0f} {y0 + 2} q{-d * L // 2} 6 {-d * (L - 10)} 18" stroke="#fff" stroke-opacity=".45" stroke-width="3" fill="none" stroke-linecap="round"/>')
    a(f'<g>{trawler(250, 690, 1.55, "#1f3d66" if not night else "#16243c", night, net=True, name="PREMIUM CATCH", haul=9)}{rock(250, 690, 1.3, 5.5, -2)}</g>')
    a(f'<g>{trawler(1130, 502, 1.05, "#c8283a" if not night else "#5e1c26", night, flip=True, net=True, name="REEL QUOTE", haul=7.5)}{rock(1130, 502, 1.2, 6.3, -4.2)}</g>')
    for x, y, s in [(170, 520, .9), (220, 550, .7), (100, 570, .8), (1240, 440, .7), (1280, 425, .6)]:
        a(gull(x, y, s, "#fff" if not night else "#cfd8ee", 3))
    # channel buoys
    a(f'<g>{buoy(80, 760, "#c8283a", 1, night, night)}{rock(80, 760, 5, 3.4)}</g><g>{buoy(452, 640, "#2f8f5a", 1, night, night)}{rock(452, 640, 5, 4.1, -1.5)}</g>')
    # ---------- the boardwalk from the point to the pier
    wood = "#b98a58" if not night else "#3e3440"; wood2 = "#8d6640" if not night else "#2a2230"; post = "#6d4c30" if not night else "#1e1822"
    A0, A1, B0, B1 = (1262, 676), (1176, 772), (1296, 694), (1206, 800)
    for k in range(5):
        t = k / 4; px = B0[0] + (B1[0] - B0[0]) * t; py = B0[1] + (B1[1] - B0[1]) * t
        a(f'<rect x="{px - 4:.0f}" y="{py:.0f}" width="8" height="{26 + 8 * t:.0f}" fill="{post}"/>')
    a(f'<path d="M{A0[0]} {A0[1]} L{B0[0]} {B0[1]} L{B1[0]} {B1[1]} L{A1[0]} {A1[1]} Z" fill="{wood}"/>')
    for k in range(1, 9):
        t = k / 9
        ax = A0[0] + (A1[0] - A0[0]) * t; ay = A0[1] + (A1[1] - A0[1]) * t
        bx = B0[0] + (B1[0] - B0[0]) * t; by = B0[1] + (B1[1] - B0[1]) * t
        a(f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" stroke="{wood2}" stroke-width="1.5"/>')
    for k in range(4):
        t = k / 3; ax = A0[0] + (A1[0] - A0[0]) * t; ay = A0[1] + (A1[1] - A0[1]) * t
        a(f'<rect x="{ax - 2.5:.0f}" y="{ay - 20:.0f}" width="5" height="20" fill="{post}"/>')
    a(f'<line x1="{A0[0]}" y1="{A0[1] - 16}" x2="{A1[0]}" y2="{A1[1] - 16}" stroke="{post}" stroke-width="3"/>')
    # ---------- the main pier: the podium stands on it
    a(f'<path d="M388 770 L1212 770 L1250 900 L350 900 Z" fill="{wood}"/>'
      f'<rect x="384" y="764" width="832" height="9" rx="2" fill="{wood2}"/>')
    for y in range(786, 900, 14):
        t = (y - 770) / 130
        a(f'<line x1="{388 - 38 * t:.0f}" y1="{y}" x2="{1212 + 38 * t:.0f}" y2="{y}" stroke="{wood2}" stroke-width="1.5" opacity=".8"/>')
    a(f'<path d="M389 752 q7 6 14 0 M389 758 q7 6 14 0" fill="none" stroke="#e8dcc0" stroke-width="2"/>')
    # crates of fish, left of the podium
    cr = "#c79a5e" if not night else "#4c3f3a"; cr2 = "#8d6640" if not night else "#2c2428"
    fc = ["#8fb3c7", "#e3a25a", "#b9c9d4"] if not night else ["#5d7a8c", "#8a6a44", "#6e7f8c"]
    a(f'<rect x="414" y="780" width="62" height="36" fill="{cr}" stroke="{cr2}" stroke-width="2"/><line x1="414" y1="798" x2="476" y2="798" stroke="{cr2}" stroke-width="2"/>')
    a(fish(432, 776, .5, fc[0], -20) + fish(456, 776, .5, fc[1], 200) + fish(444, 772, .45, fc[2], 160))
    a(f'<rect x="422" y="744" width="48" height="30" fill="{cr}" stroke="{cr2}" stroke-width="2"/>' + fish(438, 742, .45, fc[1], -15) + fish(456, 742, .45, fc[0], 190))
    # the hanging scale, right of the podium
    a(f'<rect x="1142" y="636" width="9" height="182" fill="{post}"/><rect x="1136" y="640" width="64" height="8" fill="{post}"/>'
      f'<line x1="1148" y1="676" x2="1176" y2="648" stroke="{post}" stroke-width="5"/>'
      f'<line x1="1190" y1="648" x2="1190" y2="668" stroke="#3a3a3a" stroke-width="2"/>'
      f'<circle cx="1190" cy="684" r="16" fill="#f6f1e6" stroke="#b08a3a" stroke-width="4"/><line x1="1190" y1="684" x2="1198" y2="674" stroke="#c8283a" stroke-width="2.5"/>'
      f'<path d="M1190 700 L1190 712 Q1190 718 1196 716" fill="none" stroke="#3a3a3a" stroke-width="2"/>')
    a(fish(1192, 748, 1.0, fc[0], 90))
    a(f'<rect x="1158" y="788" width="50" height="28" fill="{cr}" stroke="{cr2}" stroke-width="2"/>' + fish(1174, 786, .45, fc[2], -10) + fish(1192, 786, .45, fc[1], 190))
    # lamps on the pier
    for px in [384, 1228]:
        a(f'<rect x="{px - 3}" y="740" width="6" height="{830 - 740}" fill="{post}"/><rect x="{px - 9}" y="730" width="18" height="16" rx="3" fill="{"#f2e6c0" if not night else "#ffe08a"}" stroke="{post}" stroke-width="2"/>')
        if night: a(f'<circle cx="{px}" cy="738" r="60" fill="url(#lampg)"/><rect x="{px - 3}" y="905" width="6" height="40" fill="#ffd56b" opacity=".35"/>')
    if night:
        a('<ellipse cx="815" cy="800" rx="320" ry="60" fill="#ffd27a" opacity=".08"/>')
    a('</svg>')
    return ''.join(o)

# ------------------------------------------------------------------ vistas
V = 240

def base(night, day=("#3d5d96", "#f2a172", "#ffd99a"), nt=("#050a1a", "#0d1a3a", "#1d3058"),
         horizon=150, sea_d=("#3f7ea3", "#123a58"), sea_n=("#0f1f3c", "#050c18"), extra_defs=""):
    c = nt if night else day; s = sea_n if night else sea_d
    return ('<defs>' + lg("g", [(0, c[0]), (.6, c[1]), (1, c[2])], user=(0, 0, 0, horizon)) +
            lg("w", [(0, s[0]), (1, s[1])], user=(0, horizon, 0, V)) + rg("gl", "#ffe7a6", .6) + extra_defs + '</defs>'
            f'<rect width="1600" height="{V}" fill="url(#g)"/><rect y="{horizon}" width="1600" height="{V - horizon}" fill="url(#w)"/>')

def corner_shade():
    return ('<defs>' + lg("cs", [(0, "#000", 0), (1, "#000", .35)]) + '</defs><rect y="150" width="1600" height="90" fill="url(#cs)"/>')

def v_sales(n):  # the fleet coming in with full nets
    o = [base(n, extra_defs=mesh_pattern("mesh", "#7a6a44" if not n else "#3a3628"))]
    if n: o.append(stars(70, 0, 1600, 0, 120, 1) + '<circle cx="1260" cy="66" r="26" fill="#f1eedf"/><circle cx="1260" cy="66" r="80" fill="url(#gl)" opacity=".5"/>')
    else: o.append('<circle cx="1260" cy="118" r="110" fill="url(#gl)"/><circle cx="1260" cy="118" r="34" fill="#fff1c4"/>')
    for i in range(8):
        w = 30 + i * 14; o.append(f'<rect x="{1260 - w // 2}" y="{156 + i * 9}" width="{w}" height="3" fill="{"#ffe1a0" if not n else "#e6ecfb"}" opacity="{.7 - i * .07:.2f}"/>')
    o.append(waves(30, 0, 1600, 160, 230, 2, "#fff", .25))
    for (x, wy, s, hc), nm in zip([(560, 196, .85, "#c8283a"), (800, 210, 1.05, "#1f3d66"), (1030, 190, .8, "#2a8a86")], ["NET PREMIUM", "THE CLOSER", "HOOKED LEAD"]):
        o.append(f'<path d="M{x + 80 * s:.0f} {wy} L{x + 190 * s:.0f} {wy - 8} M{x + 80 * s:.0f} {wy + 3} L{x + 180 * s:.0f} {wy + 18}" stroke="#fff" stroke-opacity=".5" stroke-width="2.5" fill="none"/>')
        o.append(trawler(x, wy, s, hc if not n else "#16243c", n, flip=True, net=True, name=nm))
    for x, y, s in [(470, 60, .9), (520, 40, .7), (700, 70, 1), (760, 50, .7), (930, 80, .8), (980, 58, .6)]:
        o.append(gull(x, y, s, "#fff" if n else "#3a3346", 2.5))
    return wrap(V, ''.join(o))

def v_messages(n):  # signal flags on a mast, and the lighthouse beam
    o = [base(n, day=("#4a5a92", "#d98aa0", "#ffd2a6"), extra_defs=lg("bm", [(0, "#fff3c4", 0), (1, "#fff3c4", .45 if n else .3)], 0, 0, 1, 0))]
    if n: o.append(stars(80, 0, 1600, 0, 140, 3))
    o.append(waves(26, 0, 1600, 160, 230, 4, "#fff", .22))
    # lighthouse on its rock, beam sweeping left over the flags
    o.append(f'<path d="M1120 160 Q1160 128 1230 130 Q1300 124 1340 160 Z" fill="{"#5a4a52" if not n else "#151b2c"}"/>')
    lh, (lx, ly) = lighthouse(1230, 136, 52, 46, 28, n)
    o.append(f'<path d="M{lx} {ly - 3} L560 0 L560 70 L{lx} {ly + 3} Z" fill="url(#bm)"/>')
    o.append(lh)
    # the mast with flags dressed overall
    ink = "#2f3440" if not n else "#cfd8ee"
    hullc = "#1f3d66" if not n else "#16243c"; deck = "#f2ede2" if not n else "#9aa0ae"; win = "#7fb5d6" if not n else "#ffd56b"
    # a proper boat under the flags: hull with a white stripe and her name, a deck house with portholes
    o.append(f'<path d="M660 184 L940 184 Q930 206 900 214 L700 214 Q672 206 660 184 Z" fill="{hullc}"/>'
             f'<path d="M662 188 L938 188 L934 194 L666 194 Z" fill="#fff" opacity=".55"/>'
             f'<text x="800" y="208" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-weight="bold" font-size="12" fill="#fff">TEXT ME BACK</text>'
             f'<rect x="750" y="160" width="100" height="24" rx="4" fill="{deck}"/><rect x="744" y="156" width="112" height="6" rx="3" fill="{"#2f3440" if not n else "#151922"}"/>'
             + ''.join(f'<circle cx="{x}" cy="172" r="4.5" fill="{win}" stroke="#2f3440" stroke-width="1"/>' for x in (770, 790, 810, 830)))
    o.append(f'<line x1="800" y1="156" x2="800" y2="28" stroke="{ink}" stroke-width="4"/><line x1="760" y1="60" x2="840" y2="60" stroke="{ink}" stroke-width="3"/>')
    cols = ["#d8323f", "#f2c14e", "#2f6fa8", "#ffffff", "#2f8f5a", "#d8323f", "#f2c14e", "#2f6fa8"]
    for side in (-1, 1):
        x1, y1, x2, y2 = 800, 30, 800 + side * 150, 184
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ink}" stroke-width="1.5"/>')
        for k in range(1, 9):
            t = k / 9.2; fx = x1 + (x2 - x1) * t; fy = y1 + (y2 - y1) * t; c = cols[(k + (side > 0)) % len(cols)]
            if k % 2: o.append(f'<rect x="{fx - 7:.0f}" y="{fy:.0f}" width="14" height="12" fill="{c}" stroke="#2f3440" stroke-width=".8"/>')
            else: o.append(f'<path d="M{fx - 7:.0f} {fy:.0f} L{fx + 7:.0f} {fy:.0f} L{fx:.0f} {fy + 15:.0f} Z" fill="{c}" stroke="#2f3440" stroke-width=".8"/>')
    o.append(f'<rect x="784" y="66" width="32" height="22" fill="#f2c14e" stroke="#2f3440"/><rect x="784" y="66" width="16" height="11" fill="#2f6fa8"/><rect x="800" y="77" width="16" height="11" fill="#2f6fa8"/>')
    return wrap(V, ''.join(o))

def v_coaching(n):  # the chart room
    wall = "#6b4630" if not n else "#2a1a12"; wall2 = "#5c3b28" if not n else "#22150f"
    o = ['<defs>' + rg("gl", "#ffd27a", .7 if n else .45) + '</defs>', f'<rect width="1600" height="{V}" fill="{wall}"/>']
    for x in range(0, 1600, 80): o.append(f'<rect x="{x}" y="0" width="3" height="{V}" fill="{wall2}"/>')
    # porthole
    sea = ("#ffd99a", "#3f7ea3") if not n else ("#1d3058", "#0f1f3c")
    o.append(f'<circle cx="1250" cy="78" r="56" fill="#b08a3a"/><circle cx="1250" cy="78" r="44" fill="{sea[0]}"/><path d="M1206 84 A44 44 0 0 0 1294 84 Z" fill="{sea[1]}"/>')
    if n: o.append('<circle cx="1262" cy="62" r="9" fill="#f1eedf"/>')
    else: o.append('<circle cx="1262" cy="78" r="10" fill="#fff1c4"/>')
    for k in range(8):
        import math
        ang = k * math.pi / 4; o.append(f'<circle cx="{1250 + 50 * math.cos(ang):.0f}" cy="{78 + 50 * math.sin(ang):.0f}" r="3" fill="#6b5320"/>')
    # ship's wheel on the wall
    import math
    wc = "#a87b4c" if not n else "#5a412a"
    o.append(f'<circle cx="360" cy="74" r="46" fill="none" stroke="{wc}" stroke-width="7"/><circle cx="360" cy="74" r="10" fill="{wc}"/>')
    for k in range(8):
        ang = k * math.pi / 4
        o.append(f'<line x1="360" y1="74" x2="{360 + 64 * math.cos(ang):.0f}" y2="{74 + 64 * math.sin(ang):.0f}" stroke="{wc}" stroke-width="6" stroke-linecap="round"/>')
    # hanging lamp
    o.append('<line x1="800" y1="0" x2="800" y2="34" stroke="#3a2a1a" stroke-width="3"/>'
             '<circle cx="800" cy="62" r="120" fill="url(#gl)"/>'
             '<path d="M782 34 L818 34 L824 74 L776 74 Z" fill="#fff1c4" stroke="#b08a3a" stroke-width="4"/><rect x="772" y="72" width="56" height="8" rx="2" fill="#b08a3a"/><path d="M786 34 Q800 22 814 34 Z" fill="#b08a3a"/>')
    # the chart table
    o.append(f'<rect y="148" width="1600" height="92" fill="{"#3a2416" if not n else "#1a0f0a"}"/><rect y="148" width="1600" height="6" fill="{"#4d321f" if not n else "#24160e"}"/>')
    paper = "#f1e6c8" if not n else "#c9bc98"
    o.append(f'<path d="M520 136 L990 136 L1014 214 L496 214 Z" fill="{paper}"/>'
             f'<path d="M540 160 Q600 150 640 172 Q690 190 700 214 L500 214 Z" fill="#cfd9b0" opacity=".8"/>'
             f'<path d="M600 196 Q760 140 900 176 T980 160" fill="none" stroke="#c8283a" stroke-width="3" stroke-dasharray="8 6"/>'
             f'<circle cx="930" cy="190" r="16" fill="none" stroke="#2f6fa8" stroke-width="2"/><line x1="914" y1="190" x2="946" y2="190" stroke="#2f6fa8"/><line x1="930" y1="174" x2="930" y2="206" stroke="#2f6fa8"/>')
    for t, x, y in [("12", 760, 200), ("8", 840, 196), ("15", 880, 204), ("6", 700, 182)]:
        o.append(f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="12" fill="#5a4a30">{t}</text>')
    # brass dividers and a sextant
    o.append('<path d="M820 140 L790 200 M820 140 L860 196" stroke="#b08a3a" stroke-width="4" stroke-linecap="round"/><circle cx="820" cy="140" r="5" fill="#b08a3a"/>')
    o.append('<g transform="translate(1110 168)"><path d="M-40 0 A50 50 0 0 1 40 0" fill="none" stroke="#b08a3a" stroke-width="6"/><path d="M0 -50 L-40 0 M0 -50 L40 0 M0 -50 L10 -2" stroke="#b08a3a" stroke-width="4"/><circle cx="0" cy="-50" r="6" fill="#b08a3a"/></g>')
    return wrap(V, ''.join(o))

def v_roleplay(n):  # a sailing drill around the buoys
    o = [base(n, day=("#3a78b8", "#7fb8e0", "#cfe8f4"), horizon=120, sea_d=("#3d8cb0", "#14466a"))]
    if n: o.append(stars(80, 0, 1600, 0, 110, 5) + '<circle cx="1380" cy="52" r="22" fill="#f1eedf"/>')
    else:
        o.append('<circle cx="1380" cy="50" r="26" fill="#fff6d6"/>')
        for x, y in [(300, 50), (900, 36)]: o.append(f'<ellipse cx="{x}" cy="{y}" rx="90" ry="12" fill="#fff" opacity=".7"/>')
    o.append(waves(36, 0, 1600, 128, 232, 6, "#fff", .3))
    o.append(f'<path d="M470 196 C520 100 700 120 800 140 S1120 210 1150 150 S960 90 800 112 S520 230 470 196 Z" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="3" stroke-dasharray="10 9"/>')
    for x, y in [(470, 196), (800, 126), (1150, 150)]:
        o.append(buoy(x, y + 10, "#f07a2a", 1.1, n, n))
    o.append(sailboat(640, 160, .95, "#f4f1ea" if not n else "#9aa0ae", n, mast=96, sails=("#f2c14e", "#f6f1e6"), flag="#d8323f"))
    o.append(sailboat(990, 190, 1.05, "#1f3d66" if not n else "#16243c", n, mast=96, sails=("#c8283a", "#f6f1e6"), flag="#2f6fa8", flip=True))
    o.append(f'<path d="M700 162 l60 -4 M1060 192 l70 -6" stroke="#fff" stroke-opacity=".55" stroke-width="2.5"/>')
    return wrap(V, ''.join(o))

def v_rphistory(n):  # the ship's log on a desk
    desk = "#5a3a24" if not n else "#20140c"
    o = ['<defs>' + rg("gl", "#ffd27a", .65 if n else .35) + '</defs>', f'<rect width="1600" height="{V}" fill="{desk}"/>']
    for y in range(18, 240, 34): o.append(f'<path d="M0 {y} Q400 {y + 6} 800 {y} T1600 {y}" fill="none" stroke="#000" stroke-opacity=".12" stroke-width="2"/>')
    o.append('<circle cx="1180" cy="80" r="260" fill="url(#gl)"/>')
    pg = "#f4ead0" if not n else "#d6c9a6"; ink = "#3a3048"
    o.append(f'<path d="M560 40 Q680 26 800 46 L800 212 Q680 194 560 206 Z" fill="{pg}"/><path d="M800 46 Q920 26 1040 40 L1040 206 Q920 194 800 212 Z" fill="{pg}"/>'
             f'<path d="M800 46 L800 212" stroke="#b8a77a" stroke-width="3"/><path d="M552 206 Q680 196 800 216 Q920 196 1048 206 L1048 214 Q920 204 800 224 Q680 204 552 214 Z" fill="#7a2a20"/>')
    o.append(f'<text x="680" y="70" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="18" fill="{ink}">SHIP&#8217;S LOG</text>')
    r = random.Random(8)
    for side, x0 in ((0, 584), (1, 824)):
        for k in range(7 if side else 6):
            y = (92 if not side else 66) + k * 18; w = r.randint(130, 190)
            pts = ' '.join(f'l{r.randint(6, 12)} {r.choice([-3, -2, 2, 3])}' for _ in range(w // 9))
            o.append(f'<path d="M{x0} {y} {pts}" fill="none" stroke="{ink}" stroke-opacity=".65" stroke-width="1.6"/>')
    o.append(f'<path d="M640 186 l14 -8 l10 10 l14 -16" fill="none" stroke="#c8283a" stroke-width="2.5"/>')
    # inkwell and quill
    o.append('<rect x="1112" y="150" width="44" height="34" rx="6" fill="#1b2230"/><rect x="1118" y="142" width="32" height="10" rx="3" fill="#b08a3a"/>'
             '<path d="M1136 146 Q1180 70 1236 30 Q1210 84 1144 146 Z" fill="#f6f1e6"/><line x1="1136" y1="148" x2="1220" y2="44" stroke="#b8a77a" stroke-width="2"/>')
    # candle / lamp
    o.append('<rect x="1280" y="120" width="26" height="60" fill="#f1e6c8"/><path d="M1293 100 Q1302 112 1293 120 Q1284 112 1293 100 Z" fill="#ffb347"/><ellipse cx="1293" cy="182" rx="34" ry="8" fill="#b08a3a"/>')
    # brass compass
    o.append('<circle cx="420" cy="140" r="44" fill="#b08a3a"/><circle cx="420" cy="140" r="34" fill="#f4ead0"/><path d="M420 112 L428 140 L420 168 L412 140 Z" fill="#c8283a"/><path d="M420 140 L428 140 L420 168 L412 140 Z" fill="#2f3440"/>')
    return wrap(V, ''.join(o))

def knot(cx, cy, kind, c):
    if kind == 0: return f'<path d="M{cx - 30} {cy + 20} Q{cx - 10} {cy - 26} {cx + 10} {cy} Q{cx + 24} {cy + 18} {cx - 4} {cy + 14} Q{cx - 20} {cy + 8} {cx + 30} {cy - 20}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/>'
    if kind == 1: return f'<path d="M{cx - 30} {cy} L{cx - 10} {cy} Q{cx + 20} {cy - 22} {cx + 8} {cy + 4} Q{cx - 4} {cy + 22} {cx + 20} {cy + 4} L{cx + 30} {cy}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/><circle cx="{cx + 6}" cy="{cy - 4}" r="10" fill="none" stroke="{c}" stroke-width="6"/>'
    if kind == 2: return f'<path d="M{cx} {cy - 26} L{cx} {cy - 4} M{cx - 14} {cy + 8} A14 14 0 1 0 {cx + 14} {cy + 8} A14 14 0 1 0 {cx - 14} {cy + 8}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/>'
    return f'<path d="M{cx - 30} {cy - 10} Q{cx} {cy + 26} {cx + 30} {cy - 10} M{cx - 30} {cy + 10} Q{cx} {cy - 26} {cx + 30} {cy + 10}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/>'

def v_training(n):  # sailing school: small boats and a knot board
    o = [base(n, day=("#3a78b8", "#7fb8e0", "#cfe8f4"), horizon=110, sea_d=("#3d8cb0", "#245e86"))]
    if n: o.append(stars(70, 0, 1600, 0, 100, 9) + '<circle cx="300" cy="46" r="20" fill="#f1eedf"/>')
    else: o.append('<circle cx="300" cy="44" r="24" fill="#fff6d6"/><ellipse cx="700" cy="40" rx="110" ry="12" fill="#fff" opacity=".7"/>')
    o.append(waves(24, 0, 1600, 118, 170, 10, "#fff", .3))
    sails = ["#c8283a", "#f2c14e", "#2f6fa8", "#2f8f5a"]
    for i, (x, y) in enumerate([(520, 150), (660, 136), (800, 156), (940, 140)]):
        o.append(sailboat(x, y, .55, "#f4f1ea" if not n else "#9aa0ae", n, mast=110, sails=(sails[i], "#f6f1e6"), flag=sails[i]))
        o.append(f'<text x="{x + 14}" y="{y - 40}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="#2f3440">{i + 1}</text>')
    # the dock along the bottom
    wood = "#6b4a2e" if not n else "#2a1e18"; wood2 = "#553a24" if not n else "#1c1410"
    o.append(f'<rect y="180" width="1600" height="60" fill="{wood}"/>')
    for x in range(0, 1600, 46): o.append(f'<rect x="{x}" y="180" width="2" height="60" fill="{wood2}"/>')
    o.append(f'<rect y="176" width="1600" height="6" fill="{wood2}"/>')
    # the knot board on its posts
    bd = "#c79a5e" if not n else "#5a4634"; rope = "#efe2c0" if not n else "#b9ab88"
    o.append(f'<rect x="1110" y="140" width="10" height="44" fill="{wood2}"/><rect x="1400" y="140" width="10" height="44" fill="{wood2}"/>'
             f'<rect x="1090" y="28" width="340" height="120" rx="8" fill="{bd}" stroke="{wood2}" stroke-width="5"/>'
             f'<text x="1260" y="52" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="17" fill="#3a2416">SAFE HARBOR SAILING</text>')
    for i, cx in enumerate([1140, 1220, 1300, 1380]):
        o.append(knot(cx, 100, i, rope))
    # the instructor's launch
    o.append(person(1000, 168, .55, "#c8283a", n, 1))
    o.append(f'<path d="M960 168 L1046 168 L1038 182 L968 182 Z" fill="{"#f07a2a" if not n else "#7a3a18"}"/>')
    return wrap(V, ''.join(o))

def compass(cx, cy, r, ink, red):
    o = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ink}" stroke-width="2"/><circle cx="{cx}" cy="{cy}" r="{r * .82:.0f}" fill="none" stroke="{ink}" stroke-width="1" stroke-opacity=".6"/>']
    import math
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2; L = r * (0.95 if k % 2 == 0 else .6); wdt = r * .14
        tx, ty = cx + L * math.cos(ang), cy + L * math.sin(ang)
        px, py = cx + wdt * math.cos(ang + math.pi / 2), cy + wdt * math.sin(ang + math.pi / 2)
        qx, qy = cx - wdt * math.cos(ang + math.pi / 2), cy - wdt * math.sin(ang + math.pi / 2)
        c = red if k == 0 else ink
        o.append(f'<path d="M{px:.0f} {py:.0f} L{tx:.0f} {ty:.0f} L{qx:.0f} {qy:.0f} Z" fill="{c}" opacity="{1 if k % 2 == 0 else .6}"/>')
    o.append(f'<text x="{cx}" y="{cy - r - 6}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="16" fill="{ink}">N</text>')
    return ''.join(o)

def v_map(n, athena=False):  # a nautical chart with a dotted route
    table = "#4a2e1c" if not n else "#160d08"
    paper = "#f1e6c8" if not n else "#14233a"; ink = "#3a3048" if not n else "#d6e2f2"
    land = "#d9c79a" if not n else "#22344e"; shallow = "#cfe3e4" if not n else "#1a3050"
    route = ("#2f8f5a" if not n else "#5fd08f") if athena else ("#c8283a" if not n else "#ff6b74")
    o = [f'<rect width="1600" height="{V}" fill="{table}"/>',
         f'<rect x="230" y="14" width="1140" height="168" fill="{paper}"/><rect x="240" y="22" width="1120" height="152" fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width="1.5"/>']
    o.append(f'<path d="M240 22 L560 22 Q520 60 450 70 Q380 90 330 140 Q300 168 240 174 Z" fill="{shallow}"/>'
             f'<path d="M240 22 L480 22 Q440 50 380 60 Q320 80 290 120 Q270 150 240 160 Z" fill="{land}"/>'
             f'<path d="M1360 174 L1060 174 Q1100 150 1150 150 Q1200 140 1220 110 Q1260 90 1360 96 Z" fill="{shallow}"/>'
             f'<path d="M1360 174 L1120 174 Q1150 160 1190 158 Q1240 150 1260 124 Q1300 108 1360 112 Z" fill="{land}"/>')
    for x in range(400, 1360, 160): o.append(f'<line x1="{x}" y1="22" x2="{x}" y2="174" stroke="{ink}" stroke-opacity=".1"/>')
    for y in range(60, 174, 50): o.append(f'<line x1="240" y1="{y}" x2="1360" y2="{y}" stroke="{ink}" stroke-opacity=".1"/>')
    r = random.Random(12 + athena)
    for _ in range(12):
        x, y = r.randint(520, 1080), r.randint(40, 166)
        o.append(f'<text x="{x}" y="{y}" font-family="Georgia, serif" font-size="11" fill="{ink}" opacity=".5">{r.randint(3, 40)}</text>')
    pts = [(420, 128), (640, 66), (870, 128), (1100, 72)]
    o.append(f'<path d="M330 150 Q370 130 420 128 C500 126 560 66 640 66 S790 128 870 128 S1020 72 1100 72 Q1150 72 1190 96" fill="none" stroke="{route}" stroke-width="4" stroke-dasharray="3 9" stroke-linecap="round"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for (x, y), t in zip(pts, steps):
        ty = y + 32 if y < 100 else y - 18
        o.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{route}" stroke="{paper}" stroke-width="3"/>'
                 f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="20" fill="{route}">{t}</text>')
    o.append(compass(1290, 96, 30, ink, route))
    o.append(f'<text x="800" y="166" text-anchor="middle" font-family="Georgia, serif" font-style="italic" font-size="13" fill="{ink}" opacity=".7">{"Athena" if athena else "Apollo"}&#8217;s chart of the {"service" if athena else "sales"} route</text>')
    o.append('<path d="M150 210 L190 150 M150 210 L120 152" stroke="#b08a3a" stroke-width="4" stroke-linecap="round"/><circle cx="150" cy="210" r="5" fill="#b08a3a"/>')
    return wrap(V, ''.join(o))

def boat_on_stands(x, gy, s, hull, bottom, night, painted=1.0):
    st = "#2f3440" if not night else "#11141c"
    o = [f'<g transform="translate({x} {gy}) scale({s})">',
         f'<path d="M-40 0 L-26 -40 M40 0 L26 -40 M-60 0 L-40 -50 M60 0 L40 -50" stroke="{st}" stroke-width="5"/>',
         f'<path d="M-120 -110 L130 -110 Q120 -60 60 -40 L-80 -40 Q-118 -60 -120 -110 Z" fill="{hull}"/>',
         f'<path d="M-112 -78 L126 -78 Q112 -50 60 -40 L-80 -40 Q-108 -54 -112 -78 Z" fill="{bottom}"/>',
         f'<path d="M-6 -40 L6 -40 L4 -20 L-4 -20 Z" fill="{st}"/>',
         f'<rect x="-50" y="-140" width="70" height="30" rx="4" fill="{"#f2ede2" if not night else "#9aa0ae"}"/>', '</g>']
    return ''.join(o)

def v_service(n):  # the boatyard: boats on stands, a hull being painted
    o = [base(n, day=("#3a78b8", "#8fc0e0", "#e6eef0"), horizon=118, sea_d=("#3d8cb0", "#3d8cb0"))]
    if n: o.append(stars(70, 0, 1600, 0, 100, 13) + '<circle cx="1300" cy="40" r="20" fill="#f1eedf"/>')
    else: o.append('<circle cx="1300" cy="40" r="24" fill="#fff6d6"/>')
    gr = "#b9a888" if not n else "#1e1c22"; gr2 = "#9c8c6e" if not n else "#17151a"
    o.append(f'<rect y="150" width="1600" height="90" fill="{gr}"/><path d="M0 150 L1600 150 L1600 156 L0 156 Z" fill="{gr2}"/>')
    r = random.Random(14)
    for _ in range(40): o.append(f'<circle cx="{r.randint(0, 1600)}" cy="{r.randint(160, 236)}" r="{r.choice([1.5, 2, 3])}" fill="{gr2}"/>')
    # the shed
    shed = "#7a3a2a" if not n else "#2a1612"
    o.append(f'<rect x="80" y="70" width="300" height="140" fill="{shed}"/><path d="M60 72 L230 30 L400 72 Z" fill="{"#4a2a20" if not n else "#1a0e0c"}"/>'
             f'<rect x="170" y="110" width="120" height="100" fill="{"#3a1e16" if not n else "#140a08"}"/>'
             f'<rect x="130" y="80" width="200" height="24" fill="#f6f1e6"/><text x="230" y="98" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="16" fill="#3a2416">DRY DOCK BOATYARD</text>')
    if n: o.append('<rect x="174" y="114" width="112" height="96" fill="#ffd56b" opacity=".35"/>')
    o.append(boat_on_stands(640, 196, .9, "#f4f1ea" if not n else "#8a8f9e", "#c8283a" if not n else "#5e1c26", n))
    o.append(boat_on_stands(1000, 200, 1.0, "#1f3d66" if not n else "#16243c", "#2f8f5a" if not n else "#1a4a34", n))
    # fresh paint going on: half the hull is new
    o.append(f'<path d="M1000 90 L1130 90 Q1120 140 1060 160 L1000 160 Z" fill="{"#2a8a86" if not n else "#1a4a4c"}"/>')
    o.append(f'<line x1="1150" y1="200" x2="1176" y2="96" stroke="#b08a3a" stroke-width="4"/><line x1="1172" y1="200" x2="1196" y2="96" stroke="#b08a3a" stroke-width="4"/>')
    for k in range(5): o.append(f'<line x1="{1154 + k * 5}" y1="{186 - k * 22}" x2="{1176 + k * 5}" y2="{186 - k * 22}" stroke="#b08a3a" stroke-width="3"/>')
    o.append(person(1176, 150, .8, "#f2c14e", n))
    o.append(f'<line x1="1166" y1="112" x2="1140" y2="108" stroke="#2f3440" stroke-width="3"/><rect x="1128" y="98" width="12" height="22" rx="3" fill="#2a8a86"/>')
    o.append('<rect x="1206" y="186" width="20" height="18" fill="#9aa0ae"/><path d="M1206 186 Q1216 176 1226 186" fill="none" stroke="#2f3440" stroke-width="2"/>')
    o.append(corner_shade())
    return wrap(V, ''.join(o))

def v_renewals(n):  # the tide comes back in; boats return to their moorings
    o = [base(n, day=("#4a5a92", "#f2a172", "#ffd99a"), horizon=110, sea_d=("#4c86a8", "#1f5a80"))]
    if n: o.append(stars(70, 0, 1600, 0, 100, 15) + '<circle cx="1180" cy="54" r="22" fill="#f1eedf"/>')
    else: o.append('<circle cx="1180" cy="96" r="80" fill="url(#gl)"/><circle cx="1180" cy="96" r="26" fill="#fff1c4"/>')
    sand = "#e3cc9c" if not n else "#2a2a34"; wet = "#c9ae7a" if not n else "#20212a"
    o.append(f'<path d="M0 170 Q300 160 600 190 Q800 210 900 240 L0 240 Z" fill="{sand}"/><path d="M0 176 Q300 166 600 196 Q760 212 860 240 L820 240 Q700 214 560 200 Q300 178 0 190 Z" fill="{wet}"/>')
    for k in range(3):
        o.append(f'<path d="M{-20 + k * 30} {170 - k * 8} Q300 {160 - k * 8} {600 + k * 40} {190 - k * 6} Q780 {208 - k * 6} {900 + k * 30} {240}" fill="none" stroke="#fff" stroke-opacity="{.7 - k * .2:.1f}" stroke-width="3"/>')
    # tide pole with marks, the water halfway up
    o.append('<rect x="456" y="70" width="10" height="120" fill="#6d4c30"/>')
    for k in range(6): o.append(f'<rect x="466" y="{80 + k * 16}" width="{14 if k % 2 == 0 else 8}" height="3" fill="#f6f1e6"/>')
    o.append('<path d="M482 120 l14 -10 l0 6 l18 0 l0 8 l-18 0 l0 6 z" fill="#2f8f5a"/>')
    # moorings and boats
    for x, y in [(700, 140), (880, 150), (1060, 136), (1240, 156)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#f07a2a"/>')
    o.append(sailboat(760, 148, .6, "#f4f1ea" if not n else "#9aa0ae", n, mast=100, flag="#d8323f", name="REEL DEAL"))
    o.append(f'<line x1="736" y1="148" x2="700" y2="140" stroke="#2f3440" stroke-width="1.5"/>')
    o.append(sailboat(940, 162, .65, "#1f3d66" if not n else "#16243c", n, mast=100, flag="#f2c14e", name="SALE AWAY"))
    o.append(f'<line x1="912" y1="162" x2="880" y2="150" stroke="#2f3440" stroke-width="1.5"/>')
    o.append(trawler(1140, 176, .6, "#c8283a" if not n else "#5e1c26", n, flip=True, name="CROSS-SELL"))
    o.append(f'<path d="M1190 178 L1280 168 M1190 180 L1270 194" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>')
    o.append(sailboat(1350, 186, .7, "#2a8a86" if not n else "#1a4a4c", n, mast=110, sails=("#f6f1e6", "#f6f1e6"), flip=True))
    for x, y in [(840, 60), (880, 44), (1000, 70)]: o.append(gull(x, y, .8, "#3a3346" if not n else "#cfd8ee", 2.5))
    o.append(corner_shade())
    return wrap(V, ''.join(o))

def v_claims(n):  # after the storm: the rescue boat, the dock being repaired, the sky clearing
    ex = lg("rays", [(0, "#fff3c4", .5), (1, "#fff3c4", 0)])
    o = [base(n, day=("#5a6f96", "#a8c4dc", "#e8dcc0"), nt=("#060a16", "#121c34", "#24314e"), horizon=130, sea_d=("#4c7f9a", "#1c4a66"), extra_defs=ex)]
    if n: o.append(stars(50, 700, 1600, 0, 110, 16) + '<circle cx="1180" cy="52" r="24" fill="#f1eedf"/>')
    else: o.append('<circle cx="1180" cy="40" r="28" fill="#fff6d6"/>')
    o.append('<path d="M1180 40 L900 240 L1000 240 Z M1180 40 L1120 240 L1220 240 Z M1180 40 L1340 240 L1420 240 Z" fill="url(#rays)" opacity=".7"/>')
    cl = "#5a6070" if not n else "#151a28"; cl2 = "#6c7282" if not n else "#1c2234"
    o.append(f'<path d="M0 0 L760 0 Q740 40 680 44 Q660 80 590 70 Q540 100 470 82 Q400 110 330 90 Q240 110 160 90 Q80 100 0 86 Z" fill="{cl}"/>'
             f'<path d="M0 0 L620 0 Q600 30 540 32 Q500 56 430 46 Q360 70 280 54 Q180 70 0 50 Z" fill="{cl2}"/>')
    for x in range(40, 600, 46): o.append(f'<line x1="{x}" y1="{88 if x < 400 else 80}" x2="{x - 14}" y2="{120}" stroke="#9aa8c0" stroke-opacity=".5" stroke-width="2"/>')
    if not n: o.append('<path d="M780 130 A300 160 0 0 1 1380 130" fill="none" stroke="#f2c14e" stroke-opacity=".35" stroke-width="8"/><path d="M790 130 A290 150 0 0 1 1370 130" fill="none" stroke="#2f8f5a" stroke-opacity=".3" stroke-width="8"/><path d="M800 130 A280 140 0 0 1 1360 130" fill="none" stroke="#2f6fa8" stroke-opacity=".3" stroke-width="8"/>')
    o.append(waves(26, 0, 1600, 138, 230, 17, "#fff", .25))
    # rescue boat
    o.append(f'<g transform="translate(600 186)"><path d="M-90 -24 L80 -24 Q96 -30 104 -40 L92 0 L-80 0 Q-90 -10 -90 -24 Z" fill="#f07a2a"/>'
             f'<rect x="-88" y="-20" width="176" height="6" fill="#fff"/><text x="0" y="-4" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="#fff">RESCUE</text>'
             f'<rect x="-30" y="-58" width="54" height="34" rx="4" fill="#f6f1e6"/><rect x="-22" y="-52" width="16" height="12" fill="{"#7fb5d6" if not n else "#ffd56b"}"/><rect x="0" y="-52" width="16" height="12" fill="{"#7fb5d6" if not n else "#ffd56b"}"/>'
             f'<rect x="-6" y="-70" width="6" height="12" fill="#2f3440"/><circle cx="-3" cy="-74" r="5" fill="#3b8cff"/>'
             f'<circle cx="-60" cy="-36" r="10" fill="none" stroke="#f6f1e6" stroke-width="5"/><circle cx="-60" cy="-36" r="10" fill="none" stroke="#c8283a" stroke-width="5" stroke-dasharray="8 8"/></g>')
    if n: o.append('<circle cx="597" cy="112" r="24" fill="#3b8cff" opacity=".3"/>')
    # the damaged dock under repair
    wood = "#8d6640" if not n else "#3a2e30"; post = "#5c3f26" if not n else "#1e1822"
    for x in [880, 960, 1040, 1120, 1200, 1280]: o.append(f'<rect x="{x}" y="150" width="12" height="60" fill="{post}"/>')
    o.append(f'<rect x="870" y="144" width="170" height="12" fill="{wood}"/><rect x="1130" y="144" width="170" height="12" fill="{wood}"/>'
             f'<rect x="1046" y="140" width="70" height="10" fill="#d9b27a" transform="rotate(-6 1080 145)"/>')
    o.append(person(1110, 144, .7, "#f2c14e", n, 1))
    o.append('<rect x="1120" y="80" width="5" height="22" fill="#6d4c30" transform="rotate(30 1122 90)"/><rect x="1118" y="76" width="16" height="8" fill="#5a6070" transform="rotate(30 1122 90)"/>')
    for x, y, rt in [(760, 200, 10), (820, 214, -14), (1340, 206, 8)]:
        o.append(f'<rect x="{x}" y="{y}" width="48" height="8" fill="{wood}" transform="rotate({rt} {x} {y})"/>')
    return wrap(V, ''.join(o))

def v_commercial(n):  # the cargo port
    o = [base(n, day=("#4a6aa0", "#9cc0e0", "#f0dcc0"), horizon=160, sea_d=("#2f6f96", "#14405e"))]
    if n: o.append(stars(70, 0, 1600, 0, 120, 18))
    else: o.append('<ellipse cx="500" cy="40" rx="130" ry="12" fill="#fff" opacity=".6"/>')
    # the freighter
    o.append(f'<path d="M260 150 L1080 150 L1060 196 L300 196 Q270 180 260 150 Z" fill="{"#7a2a20" if not n else "#3a1410"}"/><rect x="262" y="146" width="818" height="8" fill="{"#2f3440" if not n else "#11141c"}"/>'
             f'<rect x="300" y="182" width="760" height="5" fill="#c8283a" opacity=".8"/>'
             f'<text x="360" y="176" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#f6f1e6">FULL COVERAGE</text>')
    o.append(f'<rect x="960" y="92" width="80" height="54" fill="{"#f2ede2" if not n else "#9aa0ae"}"/><rect x="970" y="100" width="60" height="10" fill="{"#7fb5d6" if not n else "#ffd56b"}"/><rect x="1000" y="70" width="14" height="22" fill="#2f3440"/>')
    cols = ["#c8283a", "#2f6fa8", "#f2c14e", "#2f8f5a", "#f07a2a", "#1f3d66"] if not n else ["#6a1c24", "#1c3c66", "#7a6424", "#1a4a34", "#7a3a18", "#16243c"]
    r = random.Random(19)
    for col, x in enumerate(range(380, 940, 46)):
        for row in range(r.randint(2, 4)):
            c = r.choice(cols)
            o.append(f'<rect x="{x}" y="{146 - 22 * (row + 1)}" width="44" height="21" fill="{c}"/><line x1="{x + 11}" y1="{146 - 22 * (row + 1) + 3}" x2="{x + 11}" y2="{146 - 22 * row - 3}" stroke="#000" stroke-opacity=".2" stroke-width="2"/><line x1="{x + 33}" y1="{146 - 22 * (row + 1) + 3}" x2="{x + 33}" y2="{146 - 22 * row - 3}" stroke="#000" stroke-opacity=".2" stroke-width="2"/>')
    # quay and gantry cranes
    o.append(f'<rect x="1080" y="160" width="520" height="80" fill="{"#6f6a66" if not n else "#1a1a20"}"/>')
    cr = "#d8323f" if not n else "#6a1c24"
    for cx in (1160, 1350):
        o.append(f'<rect x="{cx}" y="40" width="10" height="122" fill="{cr}"/><rect x="{cx + 70}" y="40" width="10" height="122" fill="{cr}"/>'
                 f'<rect x="{cx - 170}" y="34" width="290" height="12" fill="{cr}"/><line x1="{cx}" y1="100" x2="{cx + 80}" y2="60" stroke="{cr}" stroke-width="5"/>'
                 f'<rect x="{cx + 10}" y="46" width="30" height="16" fill="#2f3440"/><line x1="{cx - 100}" y1="46" x2="{cx - 100}" y2="96" stroke="#2f3440" stroke-width="2"/>'
                 f'<rect x="{cx - 122}" y="96" width="44" height="21" fill="{cols[1] if cx == 1160 else cols[2]}"/>')
        if n: o.append(f'<circle cx="{cx + 40}" cy="34" r="4" fill="#ff3b3b"/><circle cx="{cx + 40}" cy="34" r="12" fill="#ff3b3b" opacity=".3"/>')
    for k, x in enumerate(range(1440, 1600, 46)):
        for row in range(2): o.append(f'<rect x="{x}" y="{160 - 22 * (row + 1)}" width="44" height="21" fill="{cols[(k + row) % 6]}"/>')
    o.append(trawler(200, 212, .5, "#2a8a86" if not n else "#1a4a4c", n, name=""))
    o.append(corner_shade())
    return wrap(V, ''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay,
             "rphistory": v_rphistory, "training": v_training, "blueprint": lambda n: v_map(n),
             "athenamap": lambda n: v_map(n, True), "service": v_service, "renewals": v_renewals,
             "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the fleet comes in: nets full of premium"],
    "messages": ["Texts & Emails", "flags up: every text, every reply"],
    "coaching": ["Coaching", "the chart room: every call, plotted"],
    "roleplay": ["Role Play", "drills around the buoys"],
    "rphistory": ["Session History", "the ship's log: every session, every word"],
    "training": ["Training", "sailing school: learn the ropes"],
    "blueprint": ["Apollo's Road Map", "the sales chart, in plain words"],
    "athenamap": ["Athena's Road Map", "the service chart, in plain words"],
    "service": ["Service Digest", "the boatyard: keeping the book seaworthy"],
    "renewals": ["Renewals", "the tide comes back in"],
    "claims": ["Claims", "after the storm: the dock rebuilt"],
    "commercial": ["Commercial Center", "the cargo port: commercial lines"],
}

# ------------------------------------------------------------------ strips
S = 160

def sbase(n, day, nt, sea_d=("#3f7ea3", "#1d5a80"), sea_n=("#0f1f3c", "#081428"), horizon=100, extra=""):
    c = nt if n else day; s = sea_n if n else sea_d
    return ('<defs>' + lg("g", [(0, c[0]), (.6, c[1]), (1, c[2])], user=(0, 30, 0, horizon)) +
            lg("w", [(0, s[0]), (1, s[1])], user=(0, horizon, 0, 130)) + rg("gl", "#ffe7a6", .6) + extra + '</defs>'
            f'<rect width="1600" height="{S}" fill="url(#g)"/><rect y="{horizon}" width="1600" height="{S - horizon}" fill="url(#w)"/>')

def cap(t, c="#fff"):
    sc = "#0b1424" if c == "#fff" else "#fff"
    return f'<text x="120" y="91" font-family="monospace" font-weight="bold" font-size="26" fill="{c}" stroke="{sc}" stroke-opacity=".45" stroke-width="4" paint-order="stroke">{t}</text>'

def s_sold(n):  # FULL NET
    o = [sbase(n, ("#3d5d96", "#f2a172", "#ffd99a"), ("#060b1c", "#122248", "#24386a"), extra=mesh_pattern("mesh", "#7a6a44"))]
    if n: o.append(stars(40, 300, 1250, 40, 90, 21))
    o.append('<circle cx="1120" cy="90" r="120" fill="url(#gl)"/>')
    o.append(waves(16, 400, 1250, 104, 120, 22, "#fff", .3))
    o.append('<g transform="translate(0 8)">')
    ink = "#2f3440" if not n else "#cfd8ee"
    o.append(f'<line x1="560" y1="44" x2="820" y2="44" stroke="{ink}" stroke-width="5"/><line x1="560" y1="40" x2="560" y2="120" stroke="{ink}" stroke-width="5"/><line x1="770" y1="44" x2="770" y2="54" stroke="{ink}" stroke-width="2"/>')
    o.append('<path d="M752 54 Q706 70 716 92 Q740 114 784 108 Q830 96 818 72 Q806 56 788 54 Z" fill="#c9b98a"/>')
    fc = ["#8fb3c7", "#e3a25a", "#b9c9d4", "#f2c14e"]
    for i, (x, y, rt) in enumerate([(740, 74, 20), (770, 90, -10), (796, 76, 160), (752, 96, 190), (790, 100, 30)]):
        o.append(fish(x, y, .55, fc[i % 4], rt))
    o.append('<path d="M752 54 Q706 70 716 92 Q740 114 784 108 Q830 96 818 72 Q806 56 788 54 Z" fill="url(#mesh)" stroke="#8a7a50" stroke-width="2"/>')
    for x, y, rt in [(860, 64, -40), (900, 86, 30), (680, 82, 220)]:
        o.append(fish(x, y, .5, "#f2c14e", rt))
    for x, y in [(840, 50), (930, 60), (660, 58), (700, 46)]:
        o.append(f'<path d="M{x} {y - 6} L{x + 2} {y - 2} L{x + 6} {y} L{x + 2} {y + 2} L{x} {y + 6} L{x - 2} {y + 2} L{x - 6} {y} L{x - 2} {y - 2} Z" fill="#fff6c8"/>')
    o.append('</g>')
    o.append(cap("FULL NET"))
    return wrap(S, ''.join(o))

def s_open(n):  # LINE'S STILL OUT
    o = [sbase(n, ("#4a5a92", "#d98aa0", "#ffd2a6"), ("#060b1c", "#122248", "#24386a"))]
    if n: o.append(stars(40, 400, 1250, 40, 90, 23))
    o.append(waves(16, 400, 1250, 104, 122, 24, "#fff", .3))
    hull = "#1f3d66" if not n else "#4a6a9a"
    o.append(f'<path d="M500 96 L640 96 L626 116 L512 116 Z" fill="{hull}"/>')
    o.append(person(590, 98, .62, "#c8283a", n))
    o.append('<path d="M600 66 Q700 26 810 62" fill="none" stroke="#3a3a3a" stroke-width="3.5" stroke-linecap="round"/>')
    o.append(f'<path d="M810 62 Q836 78 850 104" fill="none" stroke="{"#f6f1e6" if not n else "#cfd8ee"}" stroke-width="1.2"/>')
    o.append('<circle cx="850" cy="104" r="5" fill="#d8323f"/><rect x="846" y="98" width="8" height="4" fill="#fff"/>'
             '<ellipse cx="850" cy="108" rx="18" ry="4" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="1.5"/><ellipse cx="850" cy="108" rx="32" ry="7" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1.5"/>')
    o.append(cap("LINE&#8217;S STILL OUT"))
    return wrap(S, ''.join(o))

def s_lost(n):  # THE ONE THAT GOT AWAY
    o = [sbase(n, ("#5f6676", "#8f96a4", "#b8bcc6"), ("#0a0c14", "#1a1d28", "#2a2d3a"), sea_d=("#6d7684", "#4a5260"), sea_n=("#1a1d28", "#0e1018"))]
    o.append(waves(16, 400, 1250, 104, 122, 25, "#fff", .25))
    o.append(f'<path d="M520 98 L640 98 L628 116 L532 116 Z" fill="{"#4a5260" if not n else "#5a6272"}"/>')
    o.append('<path d="M604 80 Q680 50 740 70" fill="none" stroke="#3a3a3a" stroke-width="3.5" stroke-linecap="round"/><path d="M740 70 Q748 84 742 96" fill="none" stroke="#d9dde6" stroke-width="1.2"/>')
    o.append('<path d="M770 104 Q840 20 920 100" fill="none" stroke="#d9dde6" stroke-opacity=".5" stroke-width="2" stroke-dasharray="5 6"/>')
    o.append(fish(846, 56, 1.35, "#b9c2cc" if not n else "#7a8494", -20))
    for x, y in [(770, 104), (920, 104)]:
        o.append(f'<path d="M{x - 12} {y} l4 -12 M{x} {y} l0 -14 M{x + 12} {y} l-4 -12" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>')
    o.append(cap("THE ONE THAT GOT AWAY", "#fff"))
    return wrap(S, ''.join(o))

def s_dead(n):  # NO BITES
    o = [sbase(n, ("#9aa6b4", "#c4ccd4", "#e2e4e2"), ("#0c1018", "#1a2030", "#2a3242"), sea_d=("#a6b4c0", "#7a8c9c"), sea_n=("#1e2636", "#121824"))]
    o.append('<rect y="100" width="1600" height="1.5" fill="#fff" opacity=".5"/>')
    ink = "#3a3a3a" if not n else "#cfd8ee"
    o.append(f'<line x1="780" y1="30" x2="780" y2="82" stroke="{ink}" stroke-width="1.4"/>'
             f'<path d="M780 82 L780 92 Q780 100 772 98 Q766 96 768 90" fill="none" stroke="{ink}" stroke-width="2.5" stroke-linecap="round"/>')
    o.append(f'<line x1="780" y1="108" x2="780" y2="118" stroke="{ink}" stroke-opacity=".3" stroke-width="1.4"/><path d="M780 118 L780 112 Q780 104 772 106 Q766 108 768 114" fill="none" stroke="{ink}" stroke-opacity=".25" stroke-width="2.5"/>')
    o.append(f'<path d="M560 98 L660 98 L650 112 L570 112 Z" fill="{"#7a8494" if not n else "#4a5468"}"/>')
    o.append(cap("NO BITES", "#fff" if n else "#2f3440"))
    return wrap(S, ''.join(o))

def s_hail(n):  # HAILING
    o = [sbase(n, ("#3a78b8", "#7fb8e0", "#cfe8f4"), ("#060b1c", "#122248", "#24386a"))]
    if n: o.append(stars(40, 400, 1250, 40, 90, 26))
    o.append(waves(16, 400, 1250, 104, 122, 27, "#fff", .3))
    o.append('<path d="M590 102 L770 102 L756 122 L604 122 Z" fill="#c8283a"/><path d="M790 102 L970 102 L956 122 L804 122 Z" fill="#1f3d66"/><rect x="594" y="104" width="170" height="3" fill="#fff" opacity=".6"/><rect x="794" y="104" width="170" height="3" fill="#fff" opacity=".6"/>')
    o.append(person(708, 104, .72, "#f2c14e", n, 1) + person(852, 104, .72, "#2a8a86", n, 2))
    o.append(f'<text x="780" y="50" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="18" fill="{"#1f3d66" if not n else "#ffd56b"}">AHOY!</text>')
    o.append(cap("HAILING", "#fff" if n else "#13294a"))
    return wrap(S, ''.join(o))

def s_mooring(n):  # ON THE MOORING
    o = [sbase(n, ("#4a6aa0", "#9cc0e0", "#e6eef0"), ("#060b1c", "#122248", "#24386a"))]
    if n: o.append(stars(40, 400, 1250, 40, 90, 28))
    o.append(waves(12, 400, 1250, 106, 122, 29, "#fff", .25))
    o.append('<circle cx="660" cy="104" r="9" fill="#f07a2a"/><rect x="651" y="102" width="18" height="3" fill="#fff" opacity=".7"/>')
    o.append('<path d="M660 104 Q720 116 806 106" fill="none" stroke="#3a3a3a" stroke-width="1.6"/>')
    o.append(sailboat(840, 108, .8, "#f4f1ea" if not n else "#9aa0ae", n, mast=72, flag="#d8323f"))
    o.append(cap("ON THE MOORING", "#fff" if n else "#13294a"))
    return wrap(S, ''.join(o))

def s_bottle(n):  # MESSAGE IN A BOTTLE
    o = [sbase(n, ("#2a3a6a", "#6a6a9a", "#b8a8c0"), ("#04060f", "#0a0f24", "#1a2448"), sea_d=("#4a6a90", "#2a4a70"), sea_n=("#0f1f3c", "#081428"), horizon=88)]
    o.append(stars(50, 300, 1250, 36, 84, 30))
    o.append('<circle cx="1020" cy="60" r="60" fill="#dfe8ff" opacity=".12"/><circle cx="1020" cy="60" r="18" fill="#f1eedf"/>')
    sand = "#d9c49a" if not n else "#2c2c38"
    o.append(f'<path d="M0 106 Q400 98 800 104 T1600 102 L1600 160 L0 160 Z" fill="{sand}"/><path d="M0 104 Q400 96 800 102 T1600 100" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2.5"/>')
    o.append('<g transform="translate(780 104) rotate(-12) scale(1.35)"><rect x="-34" y="-11" width="56" height="22" rx="10" fill="#7fc8a8" opacity=".85"/><rect x="20" y="-6" width="20" height="12" rx="3" fill="#7fc8a8" opacity=".85"/><rect x="38" y="-6" width="8" height="12" fill="#a87b4c"/>'
             '<rect x="-24" y="-6" width="38" height="12" rx="2" fill="#f4ead0"/><line x1="-18" y1="-1" x2="8" y2="-1" stroke="#a87b4c"/><line x1="-18" y1="3" x2="4" y2="3" stroke="#a87b4c"/></g>')
    o.append('<path d="M860 112 q10 -6 20 0 M600 114 q8 -5 16 0" fill="none" stroke="#a88a5a" stroke-width="2"/>')
    o.append(cap("MESSAGE IN A BOTTLE"))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open,
             "quoted_call_lost": s_lost, "followup_lost": s_lost, "dead_no_quote": s_dead,
             "live_quote_ok": s_hail, "live_no_quote": s_mooring, "callback_no_contact": s_bottle}
# The header's greetings in this world only (Frank, 2026-10-05: "world themed ones that appear only in those worlds"); {n} is the first name.
GREETINGS = ['Ahoy, {n}.', 'Fair winds and full nets, {n}.', 'All hands on deck, {n}.', 'Cast a wide net today, {n}.', "The tide's coming in, {n}.", 'Anchors up, phones up, {n}.', 'Smooth sailing, {n}.', "Let's reel one in, {n}.", 'Full speed ahead, {n}.', 'Calm seas never made a closer, {n}.', 'The fish are biting, {n}.', 'Batten down the bundles, {n}.', 'Hoist the sails, {n}. Quotes away.', 'Plenty of fish in the pipeline, {n}.', "Land ho, {n}. A sale's in sight."]

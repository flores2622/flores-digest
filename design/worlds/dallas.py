"""The Dallas world: Dallas at dusk. Colour looks, fonts, the Digest picture, page banners, card strips.
Drawn from the real places -- the observation tower with its lit ball, the tower outlined in green light,
the pointed glass towers, the flying red horse on its rooftop derrick, the white single-arch bridge over the
river's grassy floodway, the stacked interchange, the brick warehouses and their murals, the bluebonnets --
never named."""
import math, random

KEY = "dallas"
NAME = "Dallas"
CATEGORY = "Cities"
FONTS = "family=Montserrat:wght@700;800&family=Nunito+Sans:wght@400;500;600;700"
DISPLAY = "'Montserrat', 'Arial Black', sans-serif"
DW = 800
BODY = "'Nunito Sans', system-ui, sans-serif"
SKY_BG = (("#7a4f8e", "#6f9a58"), ("#070b1e", "#14231c"))

LOOKS = [
    ("skyline", "Skyline",
     "--surface: #e7edf3; --surface-raised: #f8fbfd; --card2: #edf2f7; --chip: #dce5ee; --text-primary: #13202e; --text-muted: #556677; --text-secondary: #405164; --grid: #dde5ed; --border: #d3dde7; --border-strong: #b4c3d2; --accent: #1d5fa3; --accent-d: #154a80; --side: #0e1f33; --side2: #16304c; --sideInk: #d9e6f2; --brand: #eef4f9; --brand2: #5fe08a; --rad: 10px;",
     "--surface: #0c131b; --surface-raised: #131c27; --card2: #19242f; --chip: #212e3b; --text-primary: #e4edf5; --text-muted: #96a8ba; --text-secondary: #b3c3d2; --grid: #212e3b; --border: #24323f; --border-strong: #344658; --accent: #5fa8f0; --accent-d: #8cc2f5; --side: #070c12; --side2: #0f1a26; --sideInk: #d9e6f2; --brand: #eef4f9; --brand2: #5fe08a;",
     ["#e7edf3", "#0e1f33", "#5fe08a"]),
    ("lonestar", "Lone Star",
     "--surface: #eeebe5; --surface-raised: #fbfaf7; --card2: #f3f1ec; --chip: #e4e0d7; --text-primary: #111d33; --text-muted: #56607a; --text-secondary: #404a63; --grid: #e3dfd6; --border: #dad5ca; --border-strong: #bcb5a6; --accent: #b31f2c; --accent-d: #8c1621; --side: #0b2a57; --side2: #133a72; --sideInk: #dee6f4; --brand: #f6f4ef; --brand2: #ff7a82; --rad: 10px;",
     "--surface: #0e1118; --surface-raised: #161a24; --card2: #1c212d; --chip: #252b39; --text-primary: #ebedf2; --text-muted: #a0a6b6; --text-secondary: #bcc1ce; --grid: #252b39; --border: #2a303e; --border-strong: #3c4456; --accent: #ff6b72; --accent-d: #ff9a9f; --side: #070b16; --side2: #0f1a33; --sideInk: #dee6f4; --brand: #f6f4ef; --brand2: #ff7a82;",
     ["#eeebe5", "#0b2a57", "#b31f2c"]),
    ("bluebonnet", "Bluebonnet",
     "--surface: #f1eee3; --surface-raised: #fdfbf4; --card2: #f5f2e8; --chip: #e7e3d4; --text-primary: #1b1d33; --text-muted: #5c5e78; --text-secondary: #454762; --grid: #e6e2d3; --border: #ddd8c7; --border-strong: #c2bca6; --accent: #4650b0; --accent-d: #353d8c; --side: #23285a; --side2: #2f3570; --sideInk: #e4e6f6; --brand: #f6f2e2; --brand2: #b3bbff; --rad: 14px;",
     "--surface: #10111c; --surface-raised: #171927; --card2: #1d2030; --chip: #26293c; --text-primary: #ebebf4; --text-muted: #a2a4bc; --text-secondary: #bec0d4; --grid: #26293c; --border: #2b2e42; --border-strong: #3d4160; --accent: #9aa4ff; --accent-d: #bcc3ff; --side: #090a14; --side2: #14162a; --sideInk: #e4e6f6; --brand: #f6f2e2; --brand2: #b3bbff;",
     ["#f1eee3", "#23285a", "#4650b0"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(glass="#1a2340", glass2="#121a32", glass3="#26325c", conc="#44465a", conc2="#30323f", grass="#1c3324", grass2="#15281c",
                    far="#18291f", river="#16244a", oak="#13261a", oak2="#0d1c12", trunk="#2a2018", path="#4c4a52", plaza="#4e4838",
                    plaza2="#3a3428", brick="#4e2c26", brick2="#3a201c", road="#24242c", ink="#f3ecdc", win="#ffd47a", bb="#5566d8",
                    roof="#2a2a34", roof2="#202028", dirt="#4e3e30", dirt2="#3a2c22", wood="#4a3828", wood2="#33261a", argon="#4dff88",
                    horse="#ff3434", white="#e8ecf6", hill="#1e2a3c", trim="#5a5a66")
    return dict(glass="#4f6f9e", glass2="#3d5884", glass3="#86a6cc", conc="#dcd6cc", conc2="#b2aa9e", grass="#7aa456", grass2="#5e8a42",
                far="#86a466", river="#7184ba", oak="#3e6a34", oak2="#2e5428", trunk="#5a4030", path="#e4dac6", plaza="#e4d4b0",
                plaza2="#c8b48a", brick="#a8553a", brick2="#86412a", road="#5a5a64", ink="#fff8ea", win="#33415e", bb="#3f56c8",
                roof="#6a5e58", roof2="#544a46", dirt="#c89a68", dirt2="#a87c50", wood="#8a5a34", wood2="#5e3a1e", argon="#5fe08a",
                horse="#d8262e", white="#f7f5ef", hill="#9a8aa8", trim="#f2efe6")

def wrap(h, body, par="xMidYMid slice"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="{par}">{body}</svg>'

def lg(i, stops, x2=0, y2=1):
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>'

def rg(i, c, op=.6):
    return f'<radialGradient id="{i}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{c}" stop-opacity="{op}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'

GLOWS = rg("glow", "#ffc35a", .65) + rg("wglow", "#dfeaff", .55) + rg("gglow", "#4dff88", .5) + rg("rglow", "#ff3a3a", .6)

def stars(k, x0, x1, y0, y1, seed):
    r = random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([.8, 1.1, 1.5, 2])}" fill="#fff" opacity="{r.choice([.4, .6, .9])}"/>' for _ in range(k))

def moon(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.7:.0f}" fill="#e9eefc" opacity=".12"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6f0dc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#e0d8bd"/><circle cx="{x + r * .35:.0f}" cy="{y + r * .3:.0f}" r="{r * .12:.0f}" fill="#e0d8bd"/>')

def sun(x, y, r, c="#fff3c8"):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 2.6:.0f}" fill="{c}" opacity=".2"/><circle cx="{x}" cy="{y}" r="{r * 1.6:.0f}" fill="{c}" opacity=".35"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff8dc"/>')

def orb(n, x, y, r): return moon(x, y, r * .8) if n else sun(x, y, r)

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s:.0f} {y - 3 * s:.0f}Q{x - 5 * s:.0f} {y - 7 * s:.0f} {x} {y}Q{x + 5 * s:.0f} {y - 7 * s:.0f} {x + 10 * s:.0f} {y - 3 * s:.0f}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

def cloud(x, y, w, c, op):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="{w / 14:.0f}" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .12:.0f}" cy="{y - w / 22:.0f}" rx="{w / 4:.0f}" ry="{w / 16:.0f}" fill="{c}" opacity="{op}"/>')

def star5(cx, cy, r, c):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * .4
        pts.append(f'{cx + rr * math.cos(a):.1f} {cy + rr * math.sin(a):.1f}')
    return f'<path d="M{"L".join(pts)}Z" fill="{c}"/>'

def tx_flag(x, y, w, pole_b=None, pole="#8a8a92", anim=False):
    """the Lone Star flag on its pole; x,y = the flag's hoist top"""
    h = w * 2 / 3; o = []
    if pole_b: o.append(f'<rect x="{x - 4}" y="{y - 8}" width="4" height="{pole_b - y + 8}" fill="{pole}"/><circle cx="{x - 2}" cy="{y - 9}" r="4" fill="#d8c070"/>')
    o.append(f'<path d="M{x} {y}Q{x + w * .25:.0f} {y - 5} {x + w * .5:.0f} {y}T{x + w} {y}V{y + h / 2:.0f}Q{x + w * .75:.0f} {y + h / 2 + 5:.0f} {x + w * .5:.0f} {y + h / 2:.0f}T{x} {y + h / 2:.0f}Z" fill="#fff"/>')
    o.append(f'<path d="M{x} {y + h / 2:.0f}Q{x + w * .25:.0f} {y + h / 2 - 5:.0f} {x + w * .5:.0f} {y + h / 2:.0f}T{x + w} {y + h / 2:.0f}V{y + h:.0f}Q{x + w * .75:.0f} {y + h + 5:.0f} {x + w * .5:.0f} {y + h:.0f}T{x} {y + h:.0f}Z" fill="#c8202e"/>')
    o.append(f'<path d="M{x} {y}Q{x + w * .17:.0f} {y - 4} {x + w / 3:.0f} {y - 2}V{y + h - 2:.0f}Q{x + w * .17:.0f} {y + h + 4:.0f} {x} {y + h:.0f}Z" fill="#0c2f66"/>')
    o.append(star5(x + w / 6, y + h / 2, w * .1, "#fff"))
    o.append(f'<path d="M{x + w * .6:.0f} {y}V{y + h:.0f}" stroke="#000" stroke-opacity=".1" stroke-width="{w * .12:.0f}"/>')
    if anim:
        wave = ('<animateTransform attributeName="transform" type="skewY" values="0;2.5;0;-2;0" dur="3.2s" repeatCount="indefinite" '
                'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>')
        sq = ('<animateTransform attributeName="transform" type="scale" additive="sum" values="1 1;.97 1;1 1;.985 1;1 1" dur="3.2s" repeatCount="indefinite"/>')
        o = o[:1] + [f'<g transform="translate({x} {y})"><g>{wave}{sq}<g transform="translate({-x} {-y})">'] + o[1:] + ['</g></g></g>']
    return ''.join(o)

def sway(x, b, deg, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="rotate" values="{-deg} {x} {b};{deg} {x} {b};{-deg} {x} {b}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

def drift(dx, dur, delay=0):
    return (f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} 0;0 0" dur="{dur}s" begin="{delay}s" '
            f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>')

# ---------------------------------------------------------------- Dallas pieces
def reunion(x, base, cy, r, n, p, lit=1.0, dark=False, anim=False):
    """the observation tower: a tapering concrete shaft, the cup, the geodesic ball and its LED dots"""
    hb, ht, yt = r * .42, r * .27, cy + r * 1.25
    cc = p["conc"] if not dark else "#262a3a"; cc2 = p["conc2"] if not dark else "#1c1f2c"
    o = [f'<path d="M{x - hb:.0f} {base}L{x - ht:.1f} {yt:.0f}L{x + ht:.1f} {yt:.0f}L{x + hb:.0f} {base}Z" fill="{cc}"/>',
         f'<path d="M{x + 2:.0f} {base}L{x + 2:.0f} {yt:.0f}L{x + ht:.1f} {yt:.0f}L{x + hb:.0f} {base}Z" fill="{cc2}"/>',
         f'<path d="M{x - ht * .45:.1f} {yt:.0f}L{x - hb * .45:.1f} {base}M{x + ht * .45:.1f} {yt:.0f}L{x + hb * .45:.1f} {base}" stroke="{cc2}" stroke-width="{max(1, r * .05):.1f}"/>',
         f'<path d="M{x - ht:.1f} {yt:.0f}L{x - r * .5:.1f} {cy + r * .84:.0f}H{x + r * .5:.1f}L{x + ht:.1f} {yt:.0f}Z" fill="{cc2}"/>']
    if lit and n and not dark: o.append(f'<circle cx="{x}" cy="{cy}" r="{r * 2.6:.0f}" fill="url(#glow)"/>')
    ball = ("#d6dae4" if not n else "#1e2236") if not dark else "#14172a"
    o.append(f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{ball}"/>')
    lc = "#8f98aa" if not n else "#2c3250"
    if dark: lc = "#22263c"
    d = []
    for ph in (-50, -25, 0, 25, 50):
        y = cy - r * math.sin(math.radians(ph)); hw = r * math.cos(math.radians(ph))
        d.append(f'M{x - hw:.1f} {y:.1f}H{x + hw:.1f}')
    o.append(f'<path d="{"".join(d)}" stroke="{lc}" stroke-width="{max(.8, r * .035):.1f}"/>'
             f'<ellipse cx="{x}" cy="{cy}" rx="{r * .42:.1f}" ry="{r}" fill="none" stroke="{lc}" stroke-width="{max(.8, r * .035):.1f}"/>'
             f'<ellipse cx="{x}" cy="{cy}" rx="{r * .8:.1f}" ry="{r}" fill="none" stroke="{lc}" stroke-width="{max(.8, r * .035):.1f}"/>')
    if lit and not dark:
        dd = []
        for ph in range(-60, 61, 15):
            c = math.cos(math.radians(ph)); y = cy - r * .94 * math.sin(math.radians(ph)); m = max(2, round(8 * c))
            for i in range(m):
                th = -1.25 + 2.5 * i / (m - 1)
                dd.append(f'M{x + r * .94 * c * math.sin(th):.1f} {y:.1f}h0')
        o.append(f'<path d="{"".join(dd)}" stroke="#fff3c4" stroke-width="{max(1.6, r * .09):.1f}" stroke-linecap="round" opacity="{lit:.2f}">'
                 + (f'<animate attributeName="opacity" values="{lit:.2f};{lit * .45:.2f};{lit:.2f};{lit * .8:.2f};{lit:.2f}" dur="3.6s" repeatCount="indefinite"/>' if anim else '') + '</path>')
    o.append(f'<rect x="{x - max(1, r * .04):.1f}" y="{cy - r * 1.45:.0f}" width="{max(2, r * .08):.1f}" height="{r * .46:.0f}" fill="{cc2}"/>')
    if n and not dark: o.append(f'<circle cx="{x}" cy="{cy - r * 1.45:.0f}" r="2.5" fill="#ff4a3a"/>')
    return ''.join(o)

HORSE = ('M-34 -2C-30 -12 -6 -12 18 -10C24 -12 30 -20 36 -30L44 -34L47 -41L50 -33L60 -24L58 -17L48 -20C42 -14 36 -4 30 2'
         'C24 10 -10 12 -30 8C-38 6 -40 2 -34 -2Z')
LEGS = 'M26 4L40 10L54 7M22 6L34 16L48 19M-28 4L-42 10L-57 8M-24 6L-36 16L-51 21M-34 -2C-46 -6 -54 -2 -63 7'
WING = 'M-2 -10C-6 -34 -20 -52 -44 -62L-38 -52L-55 -54L-44 -44L-61 -42L-46 -34L-58 -28C-36 -24 -18 -16 -10 -8Z'

def pegasus(x, y, s, c, n):
    g = f'<g transform="translate({x} {y}) scale({s})">'
    glow = f'<circle cx="0" cy="-16" r="80" fill="url(#rglow)"/>' if n else ''
    return (g + glow + f'<path d="{HORSE}{WING}" fill="{c}"/><path d="{LEGS}" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/></g>')

def derrick(x, b, t, w, c, lw=2.5):
    d = [f'M{x - w / 2:.0f} {b}L{x - w * .12:.0f} {t}M{x + w / 2:.0f} {b}L{x + w * .12:.0f} {t}']
    k = 5; pts = []
    for i in range(k + 1):
        f = i / k; y = b - (b - t) * f; hw = w / 2 - (w / 2 - w * .12) * f; pts.append((y, hw))
        d.append(f'M{x - hw:.1f} {y:.0f}H{x + hw:.1f}')
    for (y0, h0), (y1, h1) in zip(pts, pts[1:]):
        d.append(f'M{x - h0:.1f} {y0:.0f}L{x + h1:.1f} {y1:.0f}M{x + h0:.1f} {y0:.0f}L{x - h1:.1f} {y1:.0f}')
    return f'<path d="{"".join(d)}" stroke="{c}" stroke-width="{lw}" fill="none"/>'

def argon_tower(x0, x1, top, base, p, n, body=None, sp=34, glowing=True, anim=False):
    """the slab tower outlined in green light along its edges"""
    xm = (x0 + x1) / 2; body = body or p["glass2"]
    o = [f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{base - top}" fill="{body}"/>',
         f'<rect x="{xm:.0f}" y="{top}" width="{(x1 - x0) / 2:.0f}" height="{base - top}" fill="#000" opacity=".14"/>',
         f'<rect x="{xm - 1:.0f}" y="{top - sp}" width="3" height="{sp}" fill="{p["conc2"]}"/>']
    if glowing:
        e = f'M{x0} {base}V{top}H{x1}V{base}M{xm:.0f} {top}V{base}'
        if n: o.append(f'<path d="{e}" stroke="{p["argon"]}" stroke-width="14" opacity=".18" fill="none">'
                       + ('<animate attributeName="opacity" values=".18;.06;.18" dur="4.4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>' if anim else '') + '</path>')
        o.append(f'<path d="{e}" stroke="{p["argon"]}" stroke-width="{3 if n else 2.2}" fill="none" opacity="{1 if n else .85}"/>')
    return ''.join(o)

def spire_tower(x0, x1, top, tip, base, c1, c2):
    xm = (x0 + x1) / 2
    return (f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{base - top}" fill="{c1}"/><rect x="{xm:.0f}" y="{top}" width="{(x1 - x0) / 2:.0f}" height="{base - top}" fill="{c2}"/>'
            f'<path d="M{x0 - 3} {top}L{xm:.0f} {tip}L{x1 + 3} {top}Z" fill="{c1}"/><path d="M{xm:.0f} {tip}L{x1 + 3} {top}H{xm:.0f}Z" fill="{c2}"/>'
            f'<rect x="{xm - 1:.0f}" y="{tip - (top - tip) * .5:.0f}" width="2.5" height="{(top - tip) * .5:.0f}" fill="{c2}"/>')

def mini_skyline(cx, base, s, c, n, p, lit=True, ball_dark=False):
    """a compact Dallas skyline for the banners and strips"""
    o = []
    for dx, w, h in ((-250, 70, 70), (-190, 56, 110), (-60, 50, 95), (140, 60, 120), (240, 70, 80), (300, 54, 55)):
        o.append(f'<rect x="{cx + dx * s:.0f}" y="{base - h * s:.0f}" width="{w * s:.0f}" height="{h * s:.0f}" fill="{c}"/>')
    o.append(f'<path d="M{cx - 140 * s:.0f} {base}V{base - 150 * s:.0f}L{cx - 108 * s:.0f} {base - 200 * s:.0f}L{cx - 86 * s:.0f} {base - 165 * s:.0f}V{base}Z" fill="{c}"/>')
    o.append(spire_tower(cx + 70 * s, cx + 120 * s, base - 150 * s, base - 190 * s, base, c, c))
    o.append(argon_tower(round(cx - 30 * s), round(cx + 22 * s), round(base - 225 * s), base, p, n, c, round(30 * s), lit))
    o.append(f'<rect x="{cx + 186 * s:.0f}" y="{base - 85 * s:.0f}" width="{46 * s:.0f}" height="{85 * s:.0f}" fill="{c}"/>' + derrick(cx + 209 * s, base - 85 * s, base - 120 * s, 26 * s, c, 1.6))
    o.append(pegasus(round(cx + 209 * s), round(base - 132 * s), round(.3 * s, 2), p["horse"] if lit else c, n and lit))
    o.append(reunion(cx - 300 * s, base, base - 150 * s, 24 * s, n, p, 1.0 if lit else 0, ball_dark))
    return ''.join(o)

def liveoak(x, b, s, c, c2, tr):
    return (f'<path d="M{x - 9 * s:.0f} {b}L{x - 6 * s:.0f} {b - 40 * s:.0f}L{x - 40 * s:.0f} {b - 64 * s:.0f}L{x - 34 * s:.0f} {b - 70 * s:.0f}L{x} {b - 52 * s:.0f}L{x + 36 * s:.0f} {b - 72 * s:.0f}L{x + 42 * s:.0f} {b - 66 * s:.0f}L{x + 8 * s:.0f} {b - 40 * s:.0f}L{x + 10 * s:.0f} {b}Z" fill="{tr}"/>'
            f'<ellipse cx="{x - 52 * s:.0f}" cy="{b - 76 * s:.0f}" rx="{54 * s:.0f}" ry="{28 * s:.0f}" fill="{c2}"/><ellipse cx="{x + 54 * s:.0f}" cy="{b - 80 * s:.0f}" rx="{56 * s:.0f}" ry="{28 * s:.0f}" fill="{c2}"/>'
            f'<ellipse cx="{x}" cy="{b - 104 * s:.0f}" rx="{82 * s:.0f}" ry="{36 * s:.0f}" fill="{c}"/><ellipse cx="{x - 34 * s:.0f}" cy="{b - 90 * s:.0f}" rx="{44 * s:.0f}" ry="{24 * s:.0f}" fill="{c}"/>'
            f'<ellipse cx="{x + 40 * s:.0f}" cy="{b - 94 * s:.0f}" rx="{44 * s:.0f}" ry="{24 * s:.0f}" fill="{c}"/>')

def bluebonnets(x0, x1, y0, y1, k, seed, p, n, scale=1.0):
    """bluebonnets in drifts: a soft blue patch under each clump of spikes with their white tips"""
    r = random.Random(seed); blue, blue2, white, leaf, drift = [], [], [], [], []
    for _ in range(max(1, k // 7)):
        cx, cy = r.uniform(x0, x1), r.uniform(y0, y1)
        h = (6 + 8 * (cy - y0) / max(1, y1 - y0)) * scale
        drift.append(f'<ellipse cx="{cx:.0f}" cy="{cy + 1:.0f}" rx="{h * 2.6:.0f}" ry="{h * .55:.1f}"/>')
        for _ in range(r.randint(6, 9)):
            x = cx + r.uniform(-h * 2.1, h * 2.1); y = cy + r.uniform(-h * .35, h * .35); hh = h * r.uniform(.75, 1.15)
            leaf.append(f'M{x - h * .45:.0f} {y + 1:.0f}h{h * .9:.0f}')
            (blue if r.random() < .6 else blue2).append(f'M{x:.0f} {y:.0f}v{-hh:.0f}')
            white.append(f'M{x:.0f} {y - hh - h * .2:.0f}h0')
    w = 4.8 * scale; b2 = "#6f86e8" if not n else "#3a48a8"
    return (f'<g fill="{p["bb"]}" opacity=".45">' + ''.join(drift) + '</g>'
            f'<path d="{"".join(leaf)}" stroke="{p["grass2"]}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<path d="{"".join(blue)}" stroke="{p["bb"]}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<path d="{"".join(blue2)}" stroke="{b2}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
            f'<path d="{"".join(white)}" stroke="{"#f4f2ff" if not n else "#b8bce0"}" stroke-width="{w * .8:.1f}" stroke-linecap="round"/>')

def lamp(x, b, h, n, c="#2a2a32"):
    o = f'<rect x="{x - 2}" y="{b - h}" width="4" height="{h}" fill="{c}"/><path d="M{x - 8} {b - h}h16l-3 -9h-10Z" fill="{c}"/><rect x="{x - 5}" y="{b - h + 1}" width="10" height="5" fill="{"#ffe39a" if n else "#e8e2cc"}"/>'
    if n: o = f'<circle cx="{x}" cy="{b - h + 4}" r="{h * .8:.0f}" fill="url(#glow)"/>' + o
    return o

def person(x, y, s, shirt, pants="#2e3446", hat="#c8a46a", flip=False, arm=0, skin="#c98e6a"):
    """a Texan in a cowboy hat; y is the feet; arm lifts the forward arm"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    b = (f'<path d="M-5 0L-3 -24M6 0L4 -24" stroke="{pants}" stroke-width="6.5" stroke-linecap="round"/><rect x="-9" y="-50" width="18" height="28" rx="6" fill="{shirt}"/>'
         f'<path d="M7 -44L{14 + arm * .5:.0f} {-30 - arm * 1.5:.0f}" stroke="{shirt}" stroke-width="5" stroke-linecap="round"/><path d="M-7 -44L-10 -28" stroke="{shirt}" stroke-width="5" stroke-linecap="round"/>'
         f'<circle cx="0" cy="-58" r="8" fill="{skin}"/>')
    if hat: b += f'<path d="M-15 -62Q0 -58 15 -62Q12 -66 7 -65L5 -73Q0 -70 -5 -73L-7 -65Q-12 -66 -15 -62Z" fill="{hat}"/>'
    return g + b + '</g>'

def runner(x, y, s, shirt, flip=False, skin="#c98e6a", ph=0):
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    a, b2 = (14, -12) if ph == 0 else (-10, 12)
    return (g + f'<path d="M0 -26L{a} -12L{a + 6} 0M0 -26L{b2} -12L{b2 - 8} -6" stroke="#2e3446" stroke-width="6" stroke-linecap="round" fill="none"/>'
            f'<path d="M0 -26L6 -50" stroke="{shirt}" stroke-width="11" stroke-linecap="round"/><path d="M5 -46L14 -36L22 -42M5 -46L-4 -36L-12 -32" stroke="{skin}" stroke-width="4.5" stroke-linecap="round" fill="none"/>'
            f'<circle cx="9" cy="-60" r="7.5" fill="{skin}"/><path d="M2 -63Q9 -71 16 -63" stroke="#2a2a30" stroke-width="3" fill="none"/></g>')

def car(x, y, s, col, ang=0, n=False, flip=False):
    g = f'<g transform="translate({x:.0f} {y:.0f}) rotate({ang:.1f}) scale({-s if flip else s} {s})">'
    # the long hood is the FRONT, at +x where the headlights are (Frank, 2026-10-05: "the cars are moving backwards
    # on the bridge" -- the hood was drawn at the back)
    b = (f'<path d="M24 -4L23 -11L11 -13L5 -20L-9 -20L-16 -13L-22 -11L-22 -4Z" fill="{col}"/><path d="M8 -14L3 -18H-7L-12 -14Z" fill="{"#ffd47a" if n else "#c8dcf0"}" opacity=".85"/>'
         f'<circle cx="-12" cy="-4" r="4.5" fill="#1e1e24"/><circle cx="14" cy="-4" r="4.5" fill="#1e1e24"/>')
    if n: b += '<rect x="21" y="-11" width="4" height="3" fill="#fff6d0"/><path d="M25 -10L70 -16L70 -2Z" fill="#fff6d0" opacity=".16"/><rect x="-23" y="-11" width="3" height="3" fill="#ff3a3a"/>'
    return g + b + '</g>'

def pickup(x, y, s, col, n=False, flip=False, hood=False, hazards=False):
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    b = [f'<rect x="-62" y="-30" width="62" height="20" fill="{col}"/><path d="M-62 -30h62" stroke="#000" stroke-opacity=".25" stroke-width="3"/>',
         f'<path d="M0 -10V-36L22 -36L32 -23L54 -21L58 -10Z" fill="{col}"/><path d="M6 -32H20L27 -23H6Z" fill="{"#ffd47a" if n else "#bcd4ea"}" opacity=".9"/>',
         '<rect x="-66" y="-12" width="128" height="6" fill="#2a2a32"/>',
         '<circle cx="-40" cy="-6" r="10" fill="#1e1e24"/><circle cx="-40" cy="-6" r="4" fill="#9a9aa4"/><circle cx="38" cy="-6" r="10" fill="#1e1e24"/><circle cx="38" cy="-6" r="4" fill="#9a9aa4"/>']
    if hood: b.append(f'<path d="M33 -23L46 -48L58 -44L56 -21Z" fill="{col}"/><path d="M33 -23L46 -48" stroke="#000" stroke-opacity=".3" stroke-width="2"/>')
    if hazards:
        for hx, hy in ((56, -16), (-62, -26)):
            b.append(f'<circle cx="{hx}" cy="{hy}" r="4" fill="#ffa62a"/>' + (f'<circle cx="{hx}" cy="{hy}" r="18" fill="#ffa62a" opacity=".35"/>' if True else ''))
    elif n: b.append('<rect x="55" y="-19" width="4" height="4" fill="#fff6d0"/><path d="M59 -17L130 -28L130 -4Z" fill="#fff6d0" opacity=".15"/>')
    return g + ''.join(b) + '</g>'

def longhorn(x, y, s, n, flip=False):
    body = "#e8dccb" if not n else "#5a5450"; patch = "#9a4a2a" if not n else "#3a2a24"; horn = "#f2e8d0" if not n else "#8a8478"
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    b = (f'<path d="M-18 -28L-20 0M-6 -28L-5 0M30 -28L31 0M42 -28L44 0" stroke="{body}" stroke-width="7" stroke-linecap="round"/>'
         f'<path d="M-20 0h0M-5 0h0M31 0h0M44 0h0" stroke="#2a2420" stroke-width="7" stroke-linecap="round"/>'
         f'<path d="M52 -48C60 -40 58 -26 56 -16" stroke="{body}" stroke-width="3" fill="none"/>'
         f'<ellipse cx="14" cy="-40" rx="42" ry="19" fill="{body}"/><path d="M-22 -50Q-10 -64 8 -56" fill="{body}"/>'
         f'<ellipse cx="22" cy="-44" rx="14" ry="10" fill="{patch}"/><ellipse cx="-4" cy="-34" rx="9" ry="7" fill="{patch}"/>'
         f'<path d="M-38 -56C-56 -60 -74 -62 -90 -76C-72 -66 -56 -62 -38 -51ZM-30 -56C-12 -60 6 -62 22 -76C4 -66 -12 -62 -30 -51Z" fill="{horn}"/>'
         f'<path d="M-43 -58L-25 -58L-29 -34Q-34 -30 -39 -34Z" fill="{body}"/><path d="M-39 -36Q-34 -30 -29 -36" fill="{patch}"/>'
         f'<circle cx="-38" cy="-50" r="1.8" fill="#2a2420"/><circle cx="-30" cy="-50" r="1.8" fill="#2a2420"/></g>')
    return g + b

def fence(x0, x1, top, b, c, gap=60, rails=2):
    d = ''.join(f'M{x} {top}V{b}' for x in range(x0, x1 + 1, gap))
    rr = ''.join(f'M{x0} {top + (b - top) * (k + .5) / (rails + .5):.0f}H{x1}' for k in range(rails))
    return f'<path d="{d}" stroke="{c}" stroke-width="6"/><path d="{rr}" stroke="{c}" stroke-width="3.5"/>'

def quad(p0, p1, p2, t):
    u = 1 - t
    x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]; y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
    dx = 2 * u * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0]); dy = 2 * u * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return x, y, math.degrees(math.atan2(dy, dx))

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
BASE = 412           # downtown's feet, behind the far bank's trees
DECK = 440           # the bridge deck
AX0, AX1, APK, AY = 880, 1560, 1220, 104   # the arch: feet on the deck, its peak

def arch_y(x): return DECK - (DECK - AY) * (1 - ((x - APK) / ((AX1 - AX0) / 2)) ** 2)

def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    sky = (("0", "#050818"), (".55", "#111a3e"), ("1", "#2c2552")) if n else (("0", "#3a3474"), (".32", "#7a4f8e"), (".62", "#d9707a"), (".86", "#f6a05a"), ("1", "#f8c070"))
    riv = (("0", "#1a2850"), ("1", "#0e1630")) if n else (("0", "#9a86b8"), ("1", "#6a78ae"))
    win = (f'<pattern id="wn" width="14" height="18" patternUnits="userSpaceOnUse"><rect x="4" y="5" width="6" height="8" fill="#ffd47a" opacity=".8"/></pattern>'
           f'<pattern id="wo" width="42" height="54" patternUnits="userSpaceOnUse"><rect x="4" y="5" width="6" height="8" fill="{p["glass2"]}"/><rect x="18" y="23" width="6" height="8" fill="{p["glass2"]}"/><rect x="32" y="41" width="6" height="8" fill="{p["glass2"]}"/><rect x="4" y="41" width="6" height="8" fill="{p["glass2"]}"/></pattern>'
           if n else '<pattern id="wn" width="12" height="14" patternUnits="userSpaceOnUse"><rect y="12" width="12" height="1.6" fill="#fff" opacity=".22"/><rect x="11" width="1" height="14" fill="#fff" opacity=".1"/></pattern>')
    a('<defs>' + lg("sky", sky) + lg("riv", riv) + lg("sun", (("0", "#ffb070"), ("1", "#ffb070")), 1, 0) + GLOWS + win + '</defs>')
    a(f'<rect width="{W}" height="{BASE + 30}" fill="url(#sky)"/>')
    if n:
        a(stars(70, 0, W, 0, 330, 5)); a(moon(1470, 74, 30))
    else:
        for x, y, w in ((210, 150, 260), (1010, 58, 320), (1420, 150, 280), (620, 196, 360)): a(cloud(x, y, w, "#ffc9b0", .38))
        a('<g>' + '<animateTransform attributeName="transform" type="translate" values="0 0;46 -8;0 0" dur="10s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
          + bird(1040, 120, 1.1, "#4a3a5a") + bird(1066, 110, .8, "#4a3a5a") + bird(1100, 128, .9, "#4a3a5a") + '</g>')
    def win_over(x, y, w, h):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#wn)"/>'
        if n: s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#wo)"/>'
        return s
    # the low downtown blocks behind the icons
    G, G2, G3 = p["glass"], p["glass2"], p["glass3"]
    for x, w, t in ((-10, 110, 290), (90, 90, 250), (190, 70, 300), (360, 70, 270), (660, 60, 230), (930, 80, 190), (1010, 100, 230), (1100, 80, 270), (1180, 90, 320), (1270, 110, 350)):
        a(f'<rect x="{x}" y="{t}" width="{w}" height="{BASE - t}" fill="{G2}"/>' + win_over(x, t, w, BASE - t))
    # the flying red horse on its derrick, on its old rooftop
    a(f'<rect x="424" y="236" width="98" height="{BASE - 236}" fill="{G}"/><rect x="420" y="230" width="106" height="8" fill="{p["conc2"]}"/>' + win_over(424, 238, 98, BASE - 238))
    a(derrick(473, 232, 146, 54, p["conc2"] if not n else "#5a5e74", 3))
    a(pegasus(470, 128, .78, p["horse"], n))
    # the pointed glass prism
    a(f'<path d="M548 {BASE}V160L604 62L604 {BASE}Z" fill="{G3}"/><path d="M604 62L656 132V{BASE}H604Z" fill="{G}"/>')
    a(f'<path d="M548 {BASE}V160L604 62L604 {BASE}Z" fill="url(#wn)"/><path d="M604 62L656 132V{BASE}H604Z" fill="url(#wn)"/>' if not n else
      f'<path d="M604 62L656 132V{BASE}H604Z" fill="url(#wn)" opacity=".6"/>')
    if not n: a(f'<path d="M560 150L604 76V110L566 176Z" fill="#ffc890" opacity=".45"/>')
    # the slab tower outlined in green light
    a(argon_tower(690, 788, 50, BASE, p, n, G, 34, anim=True))
    a(win_over(692, 54, 94, BASE - 54))
    # the pointed tower with its crown and needle
    a(spire_tower(826, 912, 152, 94, BASE, G, G2) + win_over(826, 152, 86, BASE - 152))
    # the observation tower and its ball (lights just coming on at dusk)
    a(reunion(300, BASE, 122, 38, n, p, 1.0 if n else .6, anim=True))
    # the far bank: live oaks along the floodway's edge
    r = random.Random(9)
    a(f'<g fill="{p["oak2"]}">' + ''.join(f'<circle cx="{x}" cy="{404 + r.randint(-4, 6)}" r="{r.randint(15, 24)}"/>' for x in range(-10, 1620, 34)) + '</g>')
    a(f'<rect x="0" y="414" width="{W}" height="56" fill="{p["far"]}"/>')
    if n: a(f'<path d="M0 414H1600" stroke="#ffd47a" stroke-opacity=".25" stroke-width="3"/>')
    # the bridge: viaduct piers, the deck, the single white arch and its crossing cables
    piers = ''.join(f'M{x} {DECK + 8}V{468}' for x in range(40, 1600, 120))
    a(f'<path d="{piers}" stroke="{p["conc2"]}" stroke-width="12"/>')
    for fx in (AX0, AX1): a(f'<path d="M{fx - 14} {DECK + 8}h28l-6 26h-16Z" fill="{p["conc2"]}"/>')
    a(f'<rect x="-10" y="{DECK}" width="1620" height="10" fill="{p["conc"]}"/><rect x="-10" y="{DECK + 8}" width="1620" height="4" fill="#000" opacity=".18"/>'
      f'<path d="M-10 {DECK - 5}H1610" stroke="{p["conc"]}" stroke-width="2"/>')
    cab = []
    for k in range(1, 15):
        xa = AX0 + (AX1 - AX0) * k / 15; ya = arch_y(xa)
        for off in (-54, 54):
            xd = min(AX1 - 6, max(AX0 + 6, xa + off)); cab.append(f'M{xa:.0f} {ya:.0f}L{xd:.0f} {DECK}')
    a(f'<path d="{"".join(cab)}" stroke="{p["white"]}" stroke-width="1.4" opacity="{.75 if n else .9}"/>')
    arch = 'M' + 'L'.join(f'{x:.0f} {arch_y(x):.0f}' for x in [AX0 + (AX1 - AX0) * i / 40 for i in range(41)])
    if n: a(f'<path d="{arch}" fill="none" stroke="#cfe0ff" stroke-width="34" opacity=".14" stroke-linecap="round"/>')
    a(f'<path d="{arch}" fill="none" stroke="{p["white"] if not n else "#ffffff"}" stroke-width="12" stroke-linecap="round"/>')
    if not n: a(f'<path d="{arch}" fill="none" stroke="#c8c0d0" stroke-width="3" transform="translate(4 2)" opacity=".7"/>')
    if n:
        a(''.join(f'<circle cx="{x}" cy="{DECK - 6}" r="2.5" fill="#ffe7a0"/>' for x in range(60, 1600, 80)))
    # traffic both ways over the bridge (Frank, 2026-10-05: "add more cars to dallas"): each lane's cars on their
    # own speeds and starts, the far lane a touch higher and smaller, already under way when the page opens
    traffic = [("#c8202e", 11, 0), ("#2f6aa8", 13, -4.5), ("#e2a33a", 10, -7.5), ("#3a3a44", 12, -2), ("#e8e2d6", 14, -9.5)]
    for i, (col, dur, beg) in enumerate(traffic):
        for fl, path, dy, sc in ((False, "M-60 0H1660", 0, .75), (True, "M1660 0H-60", -5, .68)):
            c = traffic[(i + 2) % 5][0] if fl else col
            d = dur - 1.5 if fl else dur; b = beg - 3.2 if fl else beg
            a(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.96;1" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>'
              f'<animateMotion path="{path}" dur="{d}s" begin="{b}s" repeatCount="indefinite"/>' + car(0, DECK + dy, sc, c, 0, n, fl) + '</g>')
    # the river, sky in it, and at night the lights in it
    a(f'<path d="M0 466Q400 458 800 468T1600 462V510Q1200 516 800 508T0 512Z" fill="url(#riv)"/>')
    rr = random.Random(4)
    a('<g>' + drift(18, 7))
    if n:
        a('<path d="' + ''.join(f'M{x + rr.randint(-6, 6)} {y}h{rr.randint(14, 34)}' for x in range(AX0, AX1, 40) for y in (474, 486, 498)) + '" stroke="#fff" stroke-opacity=".45" stroke-width="2.5" stroke-linecap="round"/>')
        a('<path d="' + ''.join(f'M{x + rr.randint(-6, 6)} {y}h{rr.randint(8, 22)}' for x in range(240, 860, 46) for y in (478, 492)) + '" stroke="#ffd47a" stroke-opacity=".4" stroke-width="2.5" stroke-linecap="round"/>')
        a('<path d="M720 476h40M726 490h28M734 502h18" stroke="#4dff88" stroke-opacity=".45" stroke-width="2.5" stroke-linecap="round"/>')
        a('<path d="M290 480h22M294 494h14" stroke="#fff3c4" stroke-opacity=".5" stroke-width="2.5" stroke-linecap="round"/>')
    else:
        a('<path d="' + ''.join(f'M{rr.randint(0, 1560)} {rr.randint(472, 504)}h{rr.randint(20, 60)}' for _ in range(16)) + '" stroke="#ffe0c0" stroke-opacity=".5" stroke-width="2.5" stroke-linecap="round"/>')
        a(f'<path d="M1100 474h240M1150 488h140M1190 500h70" stroke="#fff" stroke-opacity=".35" stroke-width="3" stroke-linecap="round"/>')
    a('</g>')
    # the near levee and its park
    a(f'<path d="M0 506Q800 516 1600 504V{H}H0Z" fill="{p["grass2"]}"/>')
    a(f'<path d="M0 516Q800 526 1600 514V548Q800 560 0 548Z" fill="{p["grass"]}"/>')
    a(f'<path d="M0 532Q800 542 1600 530" fill="none" stroke="{p["path"]}" stroke-width="10"/>')
    a(f'<path d="M0 560Q800 572 1600 558V{H}H0Z" fill="{p["grass"]}" opacity=".55"/>')
    # the path down to the lawn, and the lawn's plaza where the podium stands
    a(f'<path d="M392 538C392 600 430 650 520 690" fill="none" stroke="{p["path"]}" stroke-width="30" stroke-linecap="round"/>')
    a(f'<ellipse cx="805" cy="692" rx="352" ry="114" fill="{p["plaza2"]}"/><ellipse cx="805" cy="686" rx="334" ry="100" fill="{p["plaza"]}"/>')
    a(f'<ellipse cx="805" cy="700" rx="220" ry="58" fill="none" stroke="{p["plaza2"]}" stroke-width="3" opacity=".6"/>')
    # the frame: a live oak and bluebonnets each side, the park sign and the flag
    a(bluebonnets(0, 440, 600, 860, 190, 11, p, n, 1.3))
    a(bluebonnets(1160, 1600, 610, 860, 190, 12, p, n, 1.3))
    a('<g>' + sway(150, 640, .9, 6.5) + liveoak(150, 640, 1.05, p["oak"], p["oak2"], p["trunk"]) + '</g>')
    a('<g>' + sway(1470, 650, .9, 7.5, 1.4) + liveoak(1470, 650, 1.0, p["oak"], p["oak2"], p["trunk"]) + '</g>')
    ink = "#fff"; sb = "#0c2f66" if not n else "#0a2048"
    a(f'<rect x="222" y="566" width="5" height="44" fill="#4a4a52"/><rect x="411" y="566" width="5" height="44" fill="#4a4a52"/>'
      f'<rect x="198" y="552" width="242" height="34" rx="4" fill="{sb}" stroke="{ink}" stroke-width="2"/>' + star5(218, 569, 9, "#ffffff") +
      f'<text x="328" y="575" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="15" fill="{ink}" letter-spacing="1">LONE STAR COVERAGE</text>')
    a(tx_flag(1288, 470, 96, 650, anim=True))
    a(lamp(450, 534, 46, n) + lamp(1170, 532, 46, n))
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient></defs>'
         '<rect x="0" y="140" width="1600" height="100" fill="url(#vs)"/>')
DUSK = ("#3a3474", "#c46a86", "#f6a85e"); DAY = ("#3d86c9", "#9cc9ea", "#e6f0f2"); NT = ("#050a1e", "#121a40", "#2a2552")
def vwrap(body): return wrap(V, body + SHADE)
def vbase(n, day=DUSK, nt=NT, star=50):
    c = nt if n else day
    return ('<defs>' + lg("g", (("0", c[0]), (".6", c[1]), ("1", c[2]))) + GLOWS + '</defs>' + f'<rect width="1600" height="{V}" fill="url(#g)"/>'
            + (stars(star, 0, 1600, 0, 140, 7) if n else ''))
def corners(c, op=.55):
    return f'<rect x="0" y="186" width="450" height="54" fill="{c}" opacity="{op}"/><rect x="1050" y="196" width="550" height="44" fill="{c}" opacity="{op}"/>'

def v_sales(n):  # the stacked interchange, traffic flowing on every level
    p = P(n); o = [vbase(n, star=22)]
    o.append(orb(n, 1430, 60, 24))
    o.append(mini_skyline(1180, 150, .55, "#5a5a8a" if not n else "#1a2040", n, p))
    o.append(f'<rect x="0" y="196" width="1600" height="44" fill="{"#4a4250" if not n else "#14141c"}"/>')
    cc, cc2 = p["conc"], p["conc2"]
    decks = [((-60, 172), (800, 172), (1660, 172), 1), ((-80, 186), (560, 30), (1300, 172), -1), ((260, 214), (980, -20), (1700, 104), 1), ((-60, 212), (800, 212), (1660, 212), -1)]
    cols = ["#c8442a", "#2f6aa8", "#e8e2d6", "#3a3a44", "#e2a33a", "#4a8a5a"]; r = random.Random(3)
    # each car rests where it was drawn; moving, its transform is replaced and it rides its deck (begin = where it rests),
    # faded out over the title's left 420px
    used = set(); RI = '<animateTransform attributeName="transform" type="translate" values="0 0" dur="1s" repeatCount="indefinite"/>'
    for di, (p0, p1, p2, dr) in enumerate(decks):
        a_, b_ = (p0, p2) if dr > 0 else (p2, p0)
        md = f'M{a_[0]} {a_[1]}Q{p1[0]} {p1[1]} {b_[0]} {b_[1]}'
        sm = [quad(a_, p1, b_, i / 300)[:2] for i in range(301)]; cl = [0.0]
        for (xa, ya), (xb, yb) in zip(sm, sm[1:]): cl.append(cl[-1] + math.hypot(xb - xa, yb - ya))
        L = cl[-1]; dur = round(min(12, L / 150), 1)
        fr = lambda x: next(cl[i] / L for i in range(301) if (sm[i][0] >= x if dr > 0 else sm[i][0] <= x))
        if dr > 0: f0 = max(.02, fr(400)); f1 = f0 + .03; ov, okt = "0;0;1;1;0", f"0;{f0:.3f};{f1:.3f};.97;1"
        else: f0 = fr(440); f1 = fr(400); ov, okt = "0;1;1;0;0", f"0;.03;{f0:.3f};{f1:.3f};1"
        rot = "auto" if dr > 0 else "auto-reverse"
        if di < 3:
            col = []
            for k in range(1, 12):
                x, y, _ = quad(p0, p1, p2, k / 12)
                if y < 205: col.append(f'M{x:.0f} {y + 8:.0f}V214')
            o.append(f'<path d="{"".join(col)}" stroke="{cc2}" stroke-width="12"/>')
        d = f'M{p0[0]} {p0[1]}Q{p1[0]} {p1[1]} {p2[0]} {p2[1]}'
        o.append(f'<path d="{d}" fill="none" stroke="{cc2}" stroke-width="14" transform="translate(0 4)"/><path d="{d}" fill="none" stroke="{cc}" stroke-width="10"/>')
        if n:
            o.append(f'<path d="{d}" fill="none" stroke="{"#ff4a3a" if dr > 0 else "#fff3c4"}" stroke-width="2.5" stroke-dasharray="40 26" opacity=".7" transform="translate(0 -9)"/>')
        for k in range(6):
            t = .06 + k * .16 + r.uniform(-.03, .03); x, y, ang = quad(p0, p1, p2, t)
            if -20 < x < 1620:
                ci = f'c{(k + di) % 6}{"f" if dr < 0 else ""}'; used.add(ci)
                if x < 400:
                    o.append(f'<use href="#{ci}" transform="translate({x:.0f} {y:.0f}) rotate({ang:.1f})"><animate attributeName="opacity" values="0" dur="1s" repeatCount="indefinite"/></use>'); continue
                j = min(range(301), key=lambda i: math.hypot(sm[i][0] - x, sm[i][1] - y)); bg = -cl[j] / L * dur
                o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({ang:.1f})"><use href="#{ci}"/>{RI}'
                         f'<animateMotion path="{md}" rotate="{rot}" dur="{dur}s" begin="{bg:.2f}s" repeatCount="indefinite"/>'
                         f'<animate attributeName="opacity" values="{ov}" keyTimes="{okt}" dur="{dur}s" begin="{bg:.2f}s" repeatCount="indefinite"/></g>')
    o.insert(1, '<defs>' + ''.join(f'<g id="{ci}">{car(0, -5, .62, cols[int(ci[1])], 0, n, ci.endswith("f"))}</g>' for ci in sorted(used)) + '</defs>')
    o.append(corners("#1a1620" if not n else "#05050a"))
    return vwrap(''.join(o))

def v_messages(n):  # the ball tower's lights talking to the night, the radio mast beside it
    p = P(n); o = [vbase(n, DUSK, NT, 60)]
    o.append(orb(n, 300, 64, 22))
    for i, rr in enumerate((70, 96, 122)):
        arc = f'M{800 - rr} {92 - rr * .5:.0f}A{rr} {rr} 0 0 0 {800 - rr} {92 + rr * .5:.0f}M{800 + rr} {92 - rr * .5:.0f}A{rr} {rr} 0 0 1 {800 + rr} {92 + rr * .5:.0f}'
        o.append(f'<path d="{arc}" fill="none" stroke="{"#fff3c4" if n else "#fff"}" stroke-width="3" opacity=".55" stroke-linecap="round">'
                 f'<animate attributeName="opacity" values=".55;.12;.85;.55" keyTimes="0;.3;.6;1" dur="2.4s" begin="{i * .4:.1f}s" repeatCount="indefinite"/></path>')
    o.append(reunion(800, 240, 92, 44, n, p, 1.0 if n else .7, anim=True))
    mx = 1120; mc = "#3a3a4a" if not n else "#5a5e74"
    o.append(derrick(mx, 214, 40, 40, mc, 2) + f'<path d="M{mx} 40V22" stroke="{mc}" stroke-width="2"/>')
    o.append(f'<path d="M{mx} 70L980 214M{mx} 70L1260 214M{mx} 130L1030 214M{mx} 130L1210 214" stroke="{mc}" stroke-width="1" opacity=".6"/>')
    bk = '<animate attributeName="opacity" values="1;1;.15;1" keyTimes="0;.55;.7;1" dur="2s" repeatCount="indefinite"/>'
    o.append('<g>' + ''.join(f'<circle cx="{mx}" cy="{y}" r="3.5" fill="#ff3a3a"/>' + (f'<circle cx="{mx}" cy="{y}" r="16" fill="url(#rglow)"/>' if n else '') for y in (22, 80, 140)) + bk + '</g>')
    for i, d in enumerate((f'M{mx - 32} 40A40 40 0 0 1 {mx + 32} 40', f'M{mx - 50} 30A60 60 0 0 1 {mx + 50} 30')):
        o.append(f'<path d="{d}" fill="none" stroke="{"#fff3c4" if n else "#fff"}" stroke-width="2.5" opacity=".5">'
                 f'<animate attributeName="opacity" values=".5;.1;.8;.5" keyTimes="0;.3;.6;1" dur="2s" begin="{i * .35:.2f}s" repeatCount="indefinite"/></path>')
    # a plane's lights crossing high over the right
    o.append(f'<g opacity="0"><circle cx="0" cy="0" r="2.4" fill="#fff"/><circle cx="-7" cy="1" r="1.8" fill="#ff4a3a">'
             '<animate attributeName="opacity" values="1;.1;1" dur=".9s" repeatCount="indefinite"/></circle>'
             '<animateTransform attributeName="transform" type="translate" values="1660 30;900 18" dur="12s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="12s" repeatCount="indefinite"/></g>')
    sil = "#3a2f52" if not n else "#0e1226"
    for x, w, h in ((0, 120, 50), (110, 90, 80), (200, 120, 40), (330, 80, 66), (420, 120, 36), (1300, 100, 60), (1400, 80, 90), (1480, 130, 50)):
        o.append(f'<rect x="{x}" y="{214 - h}" width="{w}" height="{h + 30}" fill="{sil}"/>')
        if n: o.append(''.join(f'<rect x="{x + 10 + k * 22}" y="{224 - h}" width="7" height="8" fill="#ffd47a" opacity=".7"/>' for k in range(w // 26)))
    o.append(f'<rect x="0" y="212" width="1600" height="28" fill="{sil}"/>')
    return vwrap(''.join(o))

def v_coaching(n):  # the brick warehouse mural wall at night under string lights
    p = P(n); o = [vbase(n, DUSK, NT, 40)]
    br, br2 = p["brick"], p["brick2"]
    o.append(f'<defs><pattern id="bk" width="40" height="16" patternUnits="userSpaceOnUse"><path d="M0 15.5H40M20 0V8M0 8H40M0 8V16" stroke="{br2}" stroke-width="1.5" fill="none"/></pattern></defs>')
    o.append(f'<rect x="0" y="44" width="1600" height="170" fill="{br}"/><rect x="0" y="44" width="1600" height="170" fill="url(#bk)"/>'
             f'<path d="M0 44H1600" stroke="{br2}" stroke-width="10"/>')
    # the mural: a sunset, the Lone Star and a longhorn skull in bold colour
    mx0, mx1 = 420, 1180
    o.append(f'<rect x="{mx0}" y="64" width="{mx1 - mx0}" height="130" fill="#1e8a9a"/>')
    o.append(f'<path d="M{mx0} 194V150Q600 110 800 150T{mx1} 140V194Z" fill="#f2b230"/><path d="M{mx0} 194V172Q620 146 800 176T{mx1} 166V194Z" fill="#e2552b"/>')
    o.append(f'<circle cx="640" cy="120" r="34" fill="#f6d04a"/>' + ''.join(f'<path d="M640 120L{640 + 70 * math.cos(a):.0f} {120 + 70 * math.sin(a):.0f}" stroke="#f6d04a" stroke-width="5"/>' for a in [math.pi + k * math.pi / 6 for k in range(7)]))
    o.append(star5(1060, 112, 34, "#ffffff") + f'<circle cx="1060" cy="112" r="44" fill="none" stroke="#c8202e" stroke-width="7"/>')
    o.append('<g transform="translate(860 118)"><path d="M-14 -16H14L10 18Q0 28 -10 18Z" fill="#f4ecd8"/><circle cx="-6" cy="-4" r="4" fill="#1e1e28"/><circle cx="6" cy="-4" r="4" fill="#1e1e28"/>'
             '<path d="M-14 -14C-40 -16 -64 -22 -80 -40C-62 -24 -40 -20 -14 -6ZM14 -14C40 -16 64 -22 80 -40C62 -24 40 -20 14 -6Z" fill="#f4ecd8"/></g>')
    o.append(f'<rect x="{mx0}" y="64" width="{mx1 - mx0}" height="130" fill="none" stroke="#1e1e28" stroke-width="3" opacity=".4"/>')
    if n: o.append(f'<rect x="{mx0}" y="64" width="{mx1 - mx0}" height="130" fill="#0a0c20" opacity=".35"/>')
    # the warehouse's loading door and arched windows either side
    for x in (120, 250, 1290, 1420):
        o.append(f'<path d="M{x} 130V92A26 26 0 0 1 {x + 52} 92V130Z" fill="{"#ffd47a" if n else "#2a3044"}" opacity="{.8 if n else 1}"/><path d="M{x + 26} 66V130M{x} 104H{x + 52}" stroke="{br2}" stroke-width="3"/>')
    o.append(f'<rect x="0" y="206" width="1600" height="34" fill="{"#5a5258" if not n else "#18161c"}"/><path d="M0 206H1600" stroke="#8a8088" stroke-width="3" opacity=".6"/>')
    # string lights hung from two posts
    pc = "#1e1e24"
    for x in (330, 1270): o.append(f'<rect x="{x - 4}" y="54" width="8" height="154" fill="{pc}"/>')
    sx = [(-40, 64), (330, 58), (800, 58), (1270, 58), (1640, 64)]; bulbs = []; d = []
    for (x0, y0), (x1, y1) in zip(sx, sx[1:]):
        sag = 34; d.append(f'M{x0} {y0}Q{(x0 + x1) / 2:.0f} {(y0 + y1) / 2 + sag * 2:.0f} {x1} {y1}')
        for k in range(1, 12):
            t = k / 12; xx, yy, _ = quad((x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + sag * 2), (x1, y1), t); bulbs.append(f'M{xx:.0f} {yy + 5:.0f}h0')
    o.append(f'<path d="M800 58V48" stroke="{pc}" stroke-width="2"/><path d="{"".join(d)}" fill="none" stroke="{pc}" stroke-width="1.6"/>')
    if n: o.append(f'<path d="{"".join(bulbs)}" stroke="#ffc35a" stroke-width="18" stroke-linecap="round" opacity=".18">'
                   '<animate attributeName="opacity" values=".18;.1;.22;.18" keyTimes="0;.4;.7;1" dur="5s" repeatCount="indefinite"/></path>')
    # the bulbs twinkle in two alternating sets, the title's end steady
    for h in (0, 1):
        bs = [b for i, b in enumerate(bulbs) if i % 2 == h and float(b[1:].split()[0]) > 420]
        o.append(f'<path d="{"".join(bs)}" stroke="{"#ffe7a0" if n else "#f6d27a"}" stroke-width="7" stroke-linecap="round">'
                 f'<animate attributeName="opacity" values="1;.45;1" dur="3s" begin="{h * 1.5}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path>')
    o.append(f'<path d="{"".join(b for b in bulbs if float(b[1:].split()[0]) <= 420)}" stroke="{"#ffe7a0" if n else "#f6d27a"}" stroke-width="7" stroke-linecap="round"/>')
    # two birds over the roofline
    for i in range(2):
        o.append(f'<g opacity="0">{bird(0, 0, 1.1 - i * .2, "#2a1e2a" if not n else "#8a8aa8")}'
                 f'<animateTransform attributeName="transform" type="translate" values="{1660 + i * 50} {22 + i * 10};{560 + i * 50} {16 + i * 8}" dur="11s" begin="{i * .6}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.06;.88;1" dur="11s" begin="{i * .6}s" repeatCount="indefinite"/></g>')
    o.append(corners("#140e10"))
    return vwrap(''.join(o))

def bronco(x, y, s, n):
    hc = "#6a3e22" if not n else "#3a2416"
    g = f'<g transform="translate({x} {y}) rotate(14) scale({s})">'
    rider = ('<path d="M2 -12L8 2" stroke="#2e4a7a" stroke-width="6" stroke-linecap="round"/><path d="M0 -12L-8 -38" stroke="#c8442a" stroke-width="10" stroke-linecap="round"/>'
             '<path d="M-4 -32L18 -24M-6 -34L-22 -56" stroke="#c8442a" stroke-width="4.5" stroke-linecap="round"/><circle cx="-10" cy="-46" r="6" fill="#c98e6a"/>'
             '<path d="M-22 -50Q-10 -46 2 -50Q0 -54 -4 -53L-6 -60Q-10 -57 -14 -60L-16 -53Q-20 -54 -22 -50Z" fill="#e8d6a8"/><path d="M18 -24L44 -30" stroke="#2a1a10" stroke-width="1.5"/>')
    return g + f'<path d="{HORSE}" fill="{hc}"/><path d="{LEGS}" fill="none" stroke="{hc}" stroke-width="6" stroke-linecap="round"/><path d="M40 -32L36 -10" stroke="#2a1a10" stroke-width="5"/>' + rider + '</g>'

def v_roleplay(n):  # the rodeo arena under its lights
    p = P(n); o = [vbase(n, DUSK, NT, 40)]
    st = "#5a4a6a" if not n else "#1a1a2a"
    o.append(f'<path d="M0 120L0 66H1600V120Z" fill="{st}"/>' + '<path d="' + ''.join(f'M0 {y}H1600' for y in range(76, 120, 10)) + f'" stroke="#000" stroke-opacity=".2" stroke-width="2"/>')
    r = random.Random(5)
    o.append('<path d="' + ''.join(f'M{r.randint(0, 1600)} {r.choice([80, 90, 100, 110])}h0' for _ in range(90)) + f'" stroke="{"#e8c8a8" if not n else "#5a5470"}" stroke-width="6" stroke-linecap="round"/>')
    for x in (180, 1420):
        o.append(f'<rect x="{x - 4}" y="34" width="8" height="90" fill="#2a2a32"/><rect x="{x - 30}" y="26" width="60" height="16" rx="2" fill="#2a2a32"/>'
                 + ''.join(f'<circle cx="{x - 20 + k * 13}" cy="34" r="4.5" fill="{"#fff6d0" if n else "#d8d4c4"}"/>' for k in range(4)))
        if n: o.append(f'<path d="M{x - 30} 40L{x - 200 if x < 800 else x - 520} 230L{x + 520 if x < 800 else x + 200} 230L{x + 30} 40Z" fill="#fff6d0" opacity=".08">'
                       '<animate attributeName="opacity" values=".08;.05;.1;.08" keyTimes="0;.35;.7;1" dur="6s" repeatCount="indefinite"/></path>')
    # camera flashes in the stands
    for i, (fx, fy) in enumerate(((560, 84), (930, 98), (1240, 80), (700, 108), (1500, 92))):
        o.append(f'<circle cx="{fx}" cy="{fy}" r="7" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.5;.53;.6;1" dur="{3 + i * .7:.1f}s" begin="{i * .9:.1f}s" repeatCount="indefinite"/></circle>')
    o.append(f'<rect x="0" y="118" width="1600" height="122" fill="{p["dirt"]}"/><path d="M0 170Q800 160 1600 172V240H0Z" fill="{p["dirt2"]}" opacity=".5"/>')
    o.append(fence(-10, 1610, 104, 150, "#f2efe6" if not n else "#6a6a78", 80, 2))
    o.append(''.join(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{p["dirt"]}" opacity=".75"><animate attributeName="r" values="{rr};{rr * 1.5:.0f};{rr}" dur="1.4s" begin="{i * .35:.2f}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="opacity" values=".75;.35;.75" dur="1.4s" begin="{i * .35:.2f}s" repeatCount="indefinite"/></circle>' for i, (x, y, rr) in enumerate(((720, 196, 16), (700, 184, 12), (870, 200, 14), (900, 190, 10)))))
    # the bronco bucks: rocking about its hind hooves, kicking up off the dirt
    o.append('<g><animateTransform attributeName="transform" type="rotate" values="0 690 200;-9 690 200;5 690 200;0 690 200" keyTimes="0;.35;.7;1" dur="1.4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>'
             '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -12;0 0" dur=".7s" repeatCount="indefinite" calcMode="spline" keySplines=".3 0 .6 1;.4 0 .7 1"/>'
             + bronco(760, 178, 1.9, n) + '</g></g>')
    o.append(person(1000, 204, .9, "#e2a33a", hat="#2a2a30", flip=True, arm=10))
    o.append(corners("#2a1c12"))
    return vwrap(''.join(o))

def v_rphistory(n):  # the old movie palace and its marquee
    p = P(n); o = [vbase(n, DUSK, NT, 30)]
    fac = "#d8b48a" if not n else "#4a3a30"; fac2 = "#b8906a" if not n else "#382c24"
    for x, w, t, c in ((0, 220, 96, p["brick"]), (210, 230, 70, p["brick2"]), (1160, 230, 80, p["brick2"]), (1380, 230, 104, p["brick"])):
        o.append(f'<rect x="{x}" y="{t}" width="{w}" height="{240 - t}" fill="{c}"/>' + ''.join(f'<rect x="{x + 24 + k * 64}" y="{t + 24}" width="34" height="40" fill="{"#ffcf6a" if n and k % 2 == 0 else ("#3a2a30" if n else "#5a6a86")}" opacity=".85"/>' for k in range(3)))
    o.append(f'<rect x="460" y="36" width="680" height="204" fill="{fac}"/><rect x="452" y="30" width="696" height="12" fill="{fac2}"/>')
    for x in range(500, 1120, 104):
        o.append(f'<path d="M{x} 132V74A22 22 0 0 1 {x + 44} 74V132Z" fill="{"#ffd98a" if n else "#5a6a86"}" opacity="{.7 if n else .8}"/>')
    o.append(f'<path d="M770 32H830V128L800 140L770 128Z" fill="#b5323a" stroke="#ffe7a0" stroke-width="3">'
             '<animate attributeName="stroke" values="#ffe7a0;#fff8e0;#c89a4a;#ffe7a0" keyTimes="0;.2;.6;1" dur="2.6s" repeatCount="indefinite"/></path>')
    for i, ch in enumerate("REPLAY"): o.append(f'<text x="800" y="{50 + i * 15}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#ffe7a0">{ch}</text>')
    if n: o.append('<ellipse cx="800" cy="160" rx="320" ry="70" fill="url(#glow)"><animate attributeName="opacity" values="1;.75;1" dur="4s" repeatCount="indefinite"/></ellipse>')
    o.append('<path d="M520 136H1080L1060 184H540Z" fill="#2a2030"/>')
    # the marquee's bulbs chase round in three sets
    for h in range(3):
        o.append('<g fill="#ffe7a0">' + ''.join(f'<circle cx="{x}" cy="140" r="3"/><circle cx="{x}" cy="180" r="3"/>' for x in range(540 + h * 20, 1062, 60))
                 + f'<animate attributeName="opacity" values="1;.3;.3;1" keyTimes="0;.33;.67;1" calcMode="discrete" dur=".9s" begin="{-h * .3:.1f}s" repeatCount="indefinite"/></g>')
    o.append('<rect x="556" y="146" width="488" height="28" fill="#fbf2d8"/>'
             '<text x="800" y="166" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="17" fill="#2a2030" letter-spacing="2">NOW SHOWING: YOUR BEST CALLS</text>')
    o.append(f'<rect x="740" y="190" width="120" height="50" fill="#3a1a22"/><rect x="752" y="198" width="44" height="42" fill="#ffd98a" opacity=".7"/><rect x="804" y="198" width="44" height="42" fill="#ffd98a" opacity=".7"/>')
    o.append(f'<rect x="0" y="214" width="1600" height="26" fill="{"#5a5258" if not n else "#18161c"}"/>')
    # a couple strolls up to the doors
    o.append('<g opacity="0"><animateTransform attributeName="transform" type="translate" values="0 0;-300 0" dur="10s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="10s" repeatCount="indefinite"/>'
             '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur=".5s" repeatCount="indefinite"/>'
             + person(1180, 222, .7, "#c8442a", hat="#c8a46a", flip=True, arm=4) + person(1206, 222, .66, "#2f5a8a", hat=None, flip=True) + '</g></g>')
    o.append(lamp(1000, 214, 60, n) + lamp(600, 214, 60, n))
    o.append(corners("#140e10"))
    return vwrap(''.join(o))

def v_training(n):  # a sunrise run on the levee trail along the floodway
    p = P(n); o = [vbase(n, ("#4a6aaa", "#f0a0a0", "#ffd890"), ("#060a1e", "#1a2050", "#5a3a5a"), 40)]
    o.append(sun(330, 150, 34, "#ffe0a0") if not n else moon(330, 70, 18))
    o.append(mini_skyline(1150, 148, .5, "#6a5a8a" if not n else "#161c38", n, p))
    # the little arch bridge across, far off
    ax0, ax1, top, dk = 480, 820, 64, 136
    o.append(f'<path d="M420 {dk}V148M540 {dk}V148M760 {dk}V148M880 {dk}V148" stroke="{"#c8c0d0" if not n else "#3a4060"}" stroke-width="5"/>')
    o.append(f'<path d="M380 {dk}H900" stroke="{"#e8e4ec" if not n else "#5a6080"}" stroke-width="4"/>')
    o.append(f'<path d="M{ax0} {dk}Q{(ax0 + ax1) / 2} {2 * top - dk} {ax1} {dk}" fill="none" stroke="{"#ffffff" if not n else "#e8f0ff"}" stroke-width="5"/>')
    o.append(f'<rect x="0" y="146" width="1600" height="94" fill="{p["far"]}"/>')
    o.append(f'<path d="M0 156Q800 150 1600 158V176Q800 170 0 178Z" fill="{p["river"]}"/>')
    if not n: o.append('<path d="M290 164h80M310 170h40" stroke="#ffe0a0" stroke-width="3" opacity=".8" stroke-linecap="round"/>')
    o.append(f'<path d="M0 182Q800 176 1600 184V240H0Z" fill="{p["grass2"]}"/>')
    o.append(f'<path d="M-20 214Q800 190 1620 212" fill="none" stroke="{p["path"]}" stroke-width="14"/>')
    # ripples drifting on the river
    o.append(f'<path d="M560 166h26M760 162h18M980 168h30M1240 164h22M1420 167h16" stroke="{"#fff" if not n else "#8a9ad8"}" stroke-width="2" stroke-linecap="round" opacity=".5">'
             '<animateTransform attributeName="transform" type="translate" values="0 0;24 0;0 0" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
             '<animate attributeName="opacity" values=".5;.15;.5" dur="3.5s" repeatCount="indefinite"/></path>')
    # the runners stride along the trail, legs swapping
    def strider(x, y, s_, c, ph):
        sw = lambda v: f'<animate attributeName="opacity" values="{v}" keyTimes="0;.5;1" calcMode="discrete" dur=".5s" repeatCount="indefinite"/>'
        return (f'<g>{runner(x, y, s_, c, ph=ph)}{sw("1;0;1")}</g><g opacity="0">{runner(x, y, s_, c, ph=1 - ph)}{sw("0;1;0")}</g>')
    runs = ((((740, 202, .9, "#e2552b", 0), (820, 200, .9, "#2f6aa8", 1)), (-220, 300, 11)), (((1010, 199, .75, "#5a9a4a", 0),), (-200, 240, 12)))
    for grp, (dx0, dx1, dur) in runs:
        o.append(f'<g><animateTransform attributeName="transform" type="translate" values="{dx0} 0;{dx1} 0" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.88;1" dur="{dur}s" repeatCount="indefinite"/>'
                 '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur=".5s" repeatCount="indefinite"/>' + ''.join(strider(*r_) for r_ in grp) + '</g></g>')
    for i in range(2):
        o.append(f'<g opacity="0">{bird(0, 0, 1 - i * .2, "#4a3a5a" if not n else "#9a9ab8")}'
                 f'<animateTransform attributeName="transform" type="translate" values="{560 + i * 40} {40 + i * 12};{1500 + i * 40} {26 + i * 10}" dur="12s" begin="{i * .8}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="12s" begin="{i * .8}s" repeatCount="indefinite"/></g>')
    o.append(bluebonnets(40, 380, 222, 238, 30, 3, p, n, .8) + bluebonnets(1200, 1580, 222, 238, 30, 4, p, n, .8))
    o.append(corners(p["grass2"], .6))
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the city street map: grid, river and floodway, highway loop, four stops
    paper = "#efe8d6" if not n else "#121620"; ink = "#3a3448" if not n else "#d6dae6"
    st = "#ffffff" if not n else "#262c3a"; blk = "#e4dcc6" if not n else "#181d2a"
    route = ("#2f8a5a" if not n else "#5cd08a") if athena else ("#c8202e" if not n else "#ff6a72")
    o = [f'<rect width="1600" height="{V}" fill="{paper}"/>']
    o.append(f'<rect width="1600" height="{V}" fill="{blk}"/>' + '<path d="' + ''.join(f'M{x} 0V240' for x in range(0, 1600, 64)) + ''.join(f'M0 {y}H1600' for y in range(10, 240, 46)) + f'" stroke="{st}" stroke-width="7"/>')
    for x, y, w, h in ((128, 102, 128, 46), (1152, 56, 128, 46), (640, 194, 64, 46)):
        o.append(f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="{h - 8}" fill="{"#b8d49a" if not n else "#1e3424"}"/>')
    o.append(f'<path d="M-20 240C200 200 260 120 420 110S700 20 900 30 1300 -10 1640 20" fill="none" stroke="{"#c8dca8" if not n else "#1e3424"}" stroke-width="60"/>'
             f'<path d="M-20 240C200 200 260 120 420 110S700 20 900 30 1300 -10 1640 20" fill="none" stroke="{"#8ab4d8" if not n else "#1c3a5a"}" stroke-width="12"/>')
    o.append(f'<path d="M560 60H1060Q1100 60 1100 100V180Q1100 220 1060 220H560Q520 220 520 180V100Q520 60 560 60Z" fill="none" stroke="{"#f2b84a" if not n else "#8a6a2a"}" stroke-width="10"/>')
    pts = [(400, 170), (660, 92), (940, 168), (1210, 96)]
    d = f'M230 230C260 200 330 180 {pts[0][0]} {pts[0][1]}S600 92 {pts[1][0]} {pts[1][1]}S880 168 {pts[2][0]} {pts[2][1]}S1150 96 {pts[3][0]} {pts[3][1]}S1380 140 1440 60'
    o.append(f'<path d="{d}" fill="none" stroke="{paper}" stroke-width="16" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{route}" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2" stroke-dasharray="6 12"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        ty = y - 26 if i % 2 == 0 else y + 44
        o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{route}" stroke="{paper}" stroke-width="4"/><text x="{x}" y="{y + 6}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#fff">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="23" fill="{ink}" stroke="{paper}" stroke-width="6" paint-order="stroke">{t}</text>')
    # a marker drives the route from the first stop, each stop pinging as it passes
    for (x, y), tk in zip(pts[1:], (.25, .52, .78)):
        o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="none" stroke="{route}" stroke-width="3" opacity="0">'
                 f'<animate attributeName="r" values="16;16;36;36" keyTimes="0;{tk};{tk + .12:.2f};1" dur="10s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0;.8;0;0" keyTimes="0;{tk};{tk + .01:.2f};{tk + .12:.2f};1" dur="10s" repeatCount="indefinite"/></circle>')
    md = f'M{pts[0][0]} {pts[0][1]}C470 160 600 92 {pts[1][0]} {pts[1][1]}S880 168 {pts[2][0]} {pts[2][1]}S1150 96 {pts[3][0]} {pts[3][1]}S1380 140 1440 60'
    o.append(f'<g opacity="0"><circle r="11" fill="{paper}" stroke="{ink}" stroke-width="3"/><circle r="5" fill="{ink}"/>'
             f'<animateMotion path="{md}" dur="10s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.04;.94;1" dur="10s" repeatCount="indefinite"/></g>')
    o.append(f'<g transform="translate(1510 92)"><circle r="32" fill="{paper}" stroke="{ink}" stroke-width="2"/>'
             f'<g>{star5(0, 0, 26, route)}<animateTransform attributeName="transform" type="rotate" values="-10;10;-10" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></g>' +
             f'<text y="-38" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="13" fill="{ink}" stroke="{paper}" stroke-width="4" paint-order="stroke">N</text></g>')
    o.append(corners("#1a1622" if not n else "#05070c", .5))
    return vwrap(''.join(o))

def ranch(x, b, w, p, n, brick=None, garage=True):
    """a low brick ranch house with a hipped roof, white trim and an attached garage"""
    brick = brick or p["brick"]; h = 52; o = []
    o.append(f'<rect x="{x}" y="{b - h}" width="{w}" height="{h}" fill="{brick}"/><rect x="{x}" y="{b - h}" width="{w}" height="{h}" fill="url(#bk)"/>')
    o.append(f'<path d="M{x - 14} {b - h + 2}L{x + 40} {b - h - 34}H{x + w - 40}L{x + w + 14} {b - h + 2}Z" fill="{p["roof"]}"/><path d="M{x - 14} {b - h + 2}H{x + w + 14}" stroke="{p["roof2"]}" stroke-width="4"/>')
    wc = "#ffd47a" if n else "#3a4660"
    for k in range(2): o.append(f'<rect x="{x + 22 + k * 56}" y="{b - h + 14}" width="34" height="24" fill="{wc}" stroke="{p["trim"]}" stroke-width="3"/>')
    o.append(f'<rect x="{x + 134}" y="{b - 40}" width="22" height="40" fill="{"#6a2a2a" if not n else "#3a1a1a"}" stroke="{p["trim"]}" stroke-width="2"/>')
    if n: o.append(f'<circle cx="{x + 162}" cy="{b - 40}" r="20" fill="url(#glow)"/><circle cx="{x + 162}" cy="{b - 40}" r="2.5" fill="#fff3c4"/>')
    if garage: o.append(f'<rect x="{x + w - 104}" y="{b - 38}" width="84" height="38" fill="{p["trim"]}"/>' + '<path d="' + ''.join(f'M{x + w - 104} {b - 38 + k * 9}h84' for k in range(1, 5)) + f'" stroke="#000" stroke-opacity=".12" stroke-width="2"/>')
    return ''.join(o)

def v_service(n):  # the vintage trolley on its rails down a red-brick avenue of live oaks and brick storefronts
    p = P(n); o = [vbase(n, DAY, NT, 40)]
    o.append(f'<defs><pattern id="bk" width="20" height="8" patternUnits="userSpaceOnUse"><path d="M0 7.5H20M10 0V4M0 4H20M0 4V8" stroke="#000" stroke-opacity=".14" stroke-width="1" fill="none"/></pattern>'
             f'<pattern id="pv" width="16" height="6" patternUnits="userSpaceOnUse"><rect width="16" height="6" fill="{"#a24a34" if not n else "#3e2420"}"/><path d="M0 5.5H16M8 0V3M0 3H16M0 3V6" stroke="#000" stroke-opacity=".22" stroke-width="1" fill="none"/></pattern>'
             + ''.join(f'<pattern id="{k}" width="30" height="32" patternUnits="userSpaceOnUse"><rect x="7" y="4" width="16" height="20" fill="{"#ffd47a" if n else "#3a4660"}" opacity="{op}"/></pattern>' for k, op in (("wa", .85 if n else .9), ("wb", .45 if n else .9))) + '</defs>')
    o.append(orb(n, 1460, 52, 20))
    if not n: o.append(cloud(260, 50, 220, "#fff", .7) + cloud(1120, 40, 190, "#fff", .55))
    # the storefronts and lofts: two- and three-storey brick, cornices, awnings, shop windows
    bricks = (p["brick"], "#b8784a" if not n else "#4a3424", p["brick2"], "#c4945e" if not n else "#40302a", "#9a4a3a" if not n else "#3e2622")
    awn = ("#2f6a4a", "#c8442a", "#2f5a8a", "#e2a33a", "#6a3a6a")
    shop = "#ffe0a0" if n else "#7a9ab0"
    x = -20; i = 0
    while x < 1620:
        w = (150, 130, 170, 140, 120, 160)[i % 6]; fl = (3, 2, 3, 2, 2, 3)[i % 6]; top = 186 - 34 - fl * 32
        o.append(f'<rect x="{x}" y="{top}" width="{w}" height="{186 - top}" fill="{bricks[i % 5]}"/><rect x="{x}" y="{top}" width="{w}" height="{186 - top}" fill="url(#bk)"/>'
                 f'<rect x="{x - 3}" y="{top - 7}" width="{w + 6}" height="9" fill="{p["trim"]}" opacity=".85"/>')
        o.append(f'<rect transform="translate({x + (w - (w - 12) // 30 * 30) // 2} {top + 6})" width="{(w - 12) // 30 * 30}" height="{fl * 32}" fill="url(#{"wa" if i % 2 else "wb"})"/>')
        o.append(f'<rect x="{x + 10}" y="160" width="{w - 20}" height="26" fill="{shop}" opacity="{.8 if n else .7}"/><path d="M{x + 6} 150h{w - 12}l-8 12h{-(w - 28)}Z" fill="{awn[i % 5]}"/>')
        if n: o.append(f'<ellipse cx="{x + w / 2:.0f}" cy="180" rx="{w * .55:.0f}" ry="26" fill="url(#glow)"/>')
        x += w; i += 1
    # sidewalk, then the red-brick avenue with its rails
    o.append(f'<rect x="0" y="186" width="1600" height="10" fill="{p["path"]}"/><rect x="0" y="194" width="1600" height="3" fill="{p["conc2"]}"/>')
    o.append(f'<rect x="0" y="197" width="1600" height="43" fill="url(#pv)"/>')
    rl = "#9aa0aa" if not n else "#6a6e7a"
    o.append(f'<path d="M0 219H1600M0 234H1600" stroke="{rl}" stroke-width="2.5"/>')
    # live oaks along the walk
    for tx, s in ((330, .8), (1270, .8), (110, .7), (1500, .7)):
        o.append(liveoak(tx, 192, s, p["oak"], p["oak2"], p["trunk"]))
    # the overhead wire on its posts: bracket arms out over the street
    pc = "#3a3a44" if not n else "#5a5e70"; posts = (210, 560, 1040, 1390); wy = 82
    for px in posts:
        o.append(f'<rect x="{px - 3}" y="{wy - 14}" width="6" height="{196 - wy + 14}" fill="{pc}"/><path d="M{px} {wy - 8}H{px + 70}" stroke="{pc}" stroke-width="3"/><path d="M{px} {wy + 6}L{px + 40} {wy - 8}" stroke="{pc}" stroke-width="2"/>'
                 f'<circle cx="{px}" cy="{wy - 16}" r="4" fill="{pc}"/>')
    wire = ''.join(f'M{a + 70} {wy - 8}Q{(a + b) / 2 + 70:.0f} {wy - 4} {b + 70} {wy - 8}' for a, b in zip((-140,) + posts, posts + (1740,)))
    o.append(f'<path d="{wire}" stroke="#2a2a30" stroke-width="1.6" fill="none"/>')
    # the trolley: a vintage double-ended car, cream and green, pole up to the wire
    cb, cb2, cr = ("#2f6a4a", "#22503a", "#f2e6c8") if not n else ("#1f4434", "#16342a", "#c8bc9c")
    t = ['<g>', drift(-46, 26)]
    t.append(f'<rect x="618" y="202" width="48" height="7" fill="#2a2a30"/><rect x="934" y="202" width="48" height="7" fill="#2a2a30"/>'
             f'<circle cx="632" cy="211" r="8" fill="#1e1e24"/><circle cx="660" cy="211" r="8" fill="#1e1e24"/><circle cx="940" cy="211" r="8" fill="#1e1e24"/><circle cx="968" cy="211" r="8" fill="#1e1e24"/>'
             f'<path d="M632 211h0M660 211h0M940 211h0M968 211h0" stroke="#8a8e98" stroke-width="5" stroke-linecap="round"/>')
    t.append(f'<path d="M604 204V140Q604 128 618 126H982Q996 128 996 140V204Z" fill="{cb}"/><rect x="604" y="168" width="392" height="8" fill="{cr}"/>'
             f'<path d="M612 126Q800 104 988 126Z" fill="{cr}"/><rect x="700" y="108" width="200" height="12" rx="3" fill="{cb2}"/>'
             f'<rect x="604" y="196" width="392" height="8" fill="{cb2}"/>')
    for k in range(8):
        wx = 626 + k * 44
        t.append(f'<rect x="{wx}" y="136" width="34" height="28" rx="3" fill="{"#ffe39a" if n else "#bcd6ea"}" stroke="{cr}" stroke-width="2"/>')
    t.append(f'<rect x="710" y="180" width="180" height="12" fill="{cr}" opacity=".9"/>'
             f'<text x="800" y="190" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="10" fill="{cb2}" letter-spacing="3">ON TRACK</text>'
             f'<rect x="770" y="128" width="60" height="8" fill="#1e2a24"/><text x="800" y="135" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="7" fill="#ffd47a" letter-spacing="1">ROUTE 1</text>')
    t.append(f'<circle cx="607" cy="190" r="4" fill="{"#fff6d0" if n else "#f4ecd0"}"/><circle cx="993" cy="190" r="4" fill="#ff5a4a"/>')
    if n: t.append('<path d="M603 190L520 176V204Z" fill="#fff6d0" opacity=".18"/>')
    # the pole: from its base on the roof up to the wire, the harp on the wire
    t.append(f'<path d="M780 110L846 {wy - 6}" stroke="#2a2a30" stroke-width="3" stroke-linecap="round"/><circle cx="780" cy="110" r="4" fill="#2a2a30"/><circle cx="846" cy="{wy - 6}" r="3" fill="#2a2a30"/>')
    if n:
        t.append(f'<g opacity="0"><circle cx="846" cy="{wy - 6}" r="14" fill="url(#wglow)"/><path d="M846 {wy - 14}l2 6l7 -2l-5 5l5 5l-7 -2l-2 6l-2 -6l-7 2l5 -5l-5 -5l7 2Z" fill="#e6f0ff"/>'
                 '<animate attributeName="opacity" values="0;0;1;0;0;.8;0" keyTimes="0;.55;.58;.62;.8;.82;1" dur="4.5s" repeatCount="indefinite"/></g>')
    t.append('</g>')
    o.append(''.join(t))
    # riders waiting on the walk
    o.append(person(470, 194, .62, "#c8442a", hat="#c8a46a", arm=6) + person(500, 194, .6, "#2f5a8a", hat=None, flip=True) + person(1130, 194, .62, "#e2a33a", hat="#2a2a30", flip=True))
    if n: o.append(lamp(1180, 194, 64, n) + lamp(420, 194, 64, n))
    cc = "#1e0e0a" if not n else "#05050a"
    o.append(f'<defs><linearGradient id="cl" x1="0" x2="1" y1="0" y2="0"><stop offset=".55" stop-color="{cc}" stop-opacity=".5"/><stop offset="1" stop-color="{cc}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="cr" x1="1" x2="0" y1="0" y2="0"><stop offset=".55" stop-color="{cc}" stop-opacity=".5"/><stop offset="1" stop-color="{cc}" stop-opacity="0"/></linearGradient></defs>'
             '<rect x="0" y="176" width="560" height="64" fill="url(#cl)"/><rect x="1000" y="186" width="600" height="54" fill="url(#cr)"/>')
    return vwrap(''.join(o))

def v_renewals(n):  # a field of bluebonnets in spring
    p = P(n); o = [vbase(n, ("#5a9ad8", "#b0d4ee", "#eef4e8"), NT, 28)]
    o.append(orb(n, 260, 54, 22))
    if not n: o.append('<g>' + drift(60, 12) + cloud(700, 50, 260, "#fff", .75) + '</g><g>' + drift(-40, 10, 2) + cloud(1200, 70, 200, "#fff", .6) + '</g>')
    o.append(f'<path d="M0 132Q400 104 800 126T1600 114V240H0Z" fill="{p["far"]}"/>')
    o.append(f'<path d="M0 150Q500 126 900 146T1600 138V240H0Z" fill="{p["grass"]}"/>')
    o.append(f'<path d="M0 150Q500 126 900 146T1600 138V240H0Z" fill="{p["bb"]}" opacity=".5"/>')
    o.append(fence(980, 1600, 128, 156, p["wood"], 70, 2))
    o.append('<g>' + sway(1180, 150, .8, 7) + liveoak(1180, 150, .95, p["oak"], p["oak2"], p["trunk"]) + '</g>')
    # the field leans in the breeze: a skew about the ground line, nothing at rest
    o.append('<g transform="translate(0 236)"><g><animateTransform attributeName="transform" type="skewX" values="0;-1.4;0;.9;0" dur="6s" repeatCount="indefinite" '
             'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/><g transform="translate(0 -236)">')
    o.append(bluebonnets(0, 1600, 156, 236, 455, 21, p, n, 1.35))
    r = random.Random(8)
    o.append('<path d="' + ''.join(f'M{r.randint(0, 1600)} {r.randint(170, 236)}v-7' for _ in range(40)) + f'" stroke="{"#e2552b" if not n else "#7a3a2a"}" stroke-width="5" stroke-linecap="round"/>')
    o.append('</g></g></g>')
    # butterflies by day, fireflies by night
    for i, (bx, by, mp) in enumerate(((760, 150, "M0 0C40 -30 90 10 130 -20S200 -10 160 20S40 30 0 0"), (1020, 176, "M0 0C-30 -24 -90 -6 -110 -30S-40 -50 0 0"))):
        if not n:
            wing = lambda sx: f'<path d="M0 0C{-8 * sx} -10 {-14 * sx} -2 {-10 * sx} 5Z" fill="{("#f2a43a", "#f6e05a")[i]}"/>'
            o.append(f'<g transform="translate({bx} {by})"><g>{wing(1)}{wing(-1)}<animateTransform attributeName="transform" type="scale" values="1 1;.25 1;1 1" dur=".35s" repeatCount="indefinite"/></g>'
                     f'<path d="M0 -4V5" stroke="#2a2420" stroke-width="2"/><animateMotion path="{mp}" dur="{8 + i * 2}s" repeatCount="indefinite"/></g>')
        else:
            o.append('<g>' + ''.join(f'<circle cx="{bx + k * 70}" cy="{by + k * 9 - 20}" r="2.6" fill="#e8ff8a" opacity="0"><animate attributeName="opacity" values="0;.95;0" dur="{2.4 + k * .5:.1f}s" begin="{(i + k) * .7:.1f}s" repeatCount="indefinite"/></circle>' for k in range(3))
                     + f'<animateMotion path="{mp}" dur="{10 + i * 2}s" repeatCount="indefinite"/></g>')
    o.append(corners(p["grass2"], .6))
    return vwrap(''.join(o))

def v_claims(n):  # after the hailstorm: dented cars in the lot, hail on the ground, the crew
    p = P(n); o = [vbase(n, ("#4a5068", "#8a94aa", "#e8dcc0"), ("#05070f", "#121828", "#2a2c40"), 20)]
    cc = "#3a4058" if not n else "#1a2034"
    for i, (x, y, w) in enumerate(((140, 30, 420), (480, 18, 400), (780, 36, 300))):
        o.append(('<g>' + drift(26 + i * 10, 9 + i * 2) if i else '') + f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="34" fill="{cc}"/><ellipse cx="{x + 60}" cy="{y - 14}" rx="{w // 3}" ry="30" fill="{cc}"/>' + ('</g>' if i else ''))
    o.append('<path d="' + ''.join(f'M{x} {64 + (x % 3) * 8}l-8 30' for x in range(40, 760, 30)) + f'" stroke="{"#c8d0e0" if not n else "#4a5470"}" stroke-width="2" opacity=".6"/>')
    if not n: o.append(sun(1420, 50, 20) + '<path d="M1120 40L1600 0V140Z" fill="#fff8dc" opacity=".15"><animate attributeName="opacity" values=".15;.05;.2;.15" keyTimes="0;.4;.75;1" dur="6s" repeatCount="indefinite"/></path>')
    else: o.append(moon(1420, 56, 18))
    o.append(mini_skyline(1240, 140, .4, "#6a6e86" if not n else "#151a2e", n, p, lit=n))
    o.append(f'<rect x="0" y="136" width="1600" height="104" fill="{"#6a6a72" if not n else "#1e1e26"}"/>')
    o.append('<path d="' + ''.join(f'M{x} 150l-30 70' for x in range(200, 1500, 150)) + '" stroke="#fff" stroke-opacity=".4" stroke-width="3"/>')
    o.append(''.join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="{"#9aa8c0" if not n else "#2a3450"}" opacity=".8"/>' for x, y, w in ((380, 214, 70), (1000, 222, 60), (760, 208, 40))))
    # rings spreading on the puddles
    o.append(''.join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="1.5" fill="none" stroke="#fff" stroke-width="1.5" opacity="0"><animate attributeName="rx" values="4;{w * .8:.0f}" dur="2.5s" begin="{b}s" repeatCount="indefinite"/>'
                     f'<animate attributeName="ry" values="1.5;5" dur="2.5s" begin="{b}s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.5s" begin="{b}s" repeatCount="indefinite"/></ellipse>'
                     for x, y, w, b in ((1000, 222, 60, 0), (760, 208, 40, 1.2), (1020, 223, 60, 1.6))))
    for x, c in ((470, "#c8442a"), (700, "#2f6aa8"), (930, "#e8e2d6")):
        o.append(car(x, 196, 2.4, c, 0, n))
        o.append('<path d="' + ''.join(f'M{x + dx} {yy}h0' for dx, yy in ((-30, 158), (-6, 156), (16, 160), (40, 166), (-40, 170), (24, 152))) + '" stroke="#000" stroke-opacity=".28" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<path d="M694 152L702 162L696 168L706 176" stroke="#fff" stroke-width="1.5" fill="none" opacity=".8"/>')
    # meltwater dripping off the roofs
    o.append(''.join(f'<circle cx="{x}" cy="{y}" r="2.2" fill="{"#dfe8f6" if not n else "#8a96b4"}" opacity="0"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 {196 - y}" keyTimes="0;.6;1" dur="{d}s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.5 0 1 1"/>'
                     f'<animate attributeName="opacity" values="0;.9;.9;0" keyTimes="0;.15;.95;1" dur="{d}s" repeatCount="indefinite"/></circle>' for x, y, d in ((436, 178, 2.6), (742, 176, 3.2), (962, 180, 2.9))))
    r = random.Random(6)
    o.append('<path d="' + ''.join(f'M{r.randint(60, 1500)} {r.randint(150, 236)}h0' for _ in range(90)) + f'" stroke="{"#f4f6fa" if not n else "#aab4cc"}" stroke-width="4" stroke-linecap="round"/>')
    o.append(person(1110, 214, .95, "#f2b230", hat="#f4f0e4", flip=True, arm=12) + f'<rect x="1088" y="168" width="14" height="18" fill="#f4f0e4" stroke="#5a4a3a" stroke-width="1.5"/>')
    # the crew lead points at the damage, then drops his arm
    sw = lambda v: f'<animate attributeName="opacity" values="{v}" keyTimes="0;.5;1" calcMode="discrete" dur="4s" repeatCount="indefinite"/>'
    o.append(f'<g>{person(1190, 216, .95, "#f2b230", hat="#2a2a30", arm=4)}{sw("1;0;1")}</g><g opacity="0">{person(1190, 216, .95, "#f2b230", hat="#2a2a30", arm=34)}{sw("0;1;0")}</g>')
    o.append(corners("#18181e"))
    return vwrap(''.join(o))

def v_commercial(n):  # the glass office towers at noon
    p = P(n); o = [vbase(n, ("#2e74c4", "#7ab8e8", "#cfe6f4"), NT, 40)]
    o.append(sun(800, 20, 26) if not n else moon(1460, 40, 16))
    G, G2, G3 = ("#5f8fc4", "#3f6ea4", "#a8cbe8") if not n else ("#1a2444", "#121a34", "#2a3a6a")
    pat = (f'<pattern id="wn" width="12" height="14" patternUnits="userSpaceOnUse"><rect y="12" width="12" height="1.6" fill="#fff" opacity=".3"/></pattern>' if not n else
           f'<pattern id="wn" width="14" height="16" patternUnits="userSpaceOnUse"><rect x="4" y="4" width="6" height="7" fill="#ffd47a" opacity=".7"/></pattern>')
    o.append(f'<defs>{pat}</defs>')
    for x0, x1, t in ((120, 260, 70), (300, 420, 40), (1180, 1310, 50), (1340, 1480, 86)):
        o.append(f'<rect x="{x0}" y="{t}" width="{x1 - x0}" height="{240 - t}" fill="{G2}"/><rect x="{x0}" y="{t}" width="{x1 - x0}" height="{240 - t}" fill="url(#wn)"/>')
    o.append(f'<path d="M500 240V70L580 30V240Z" fill="{G3}"/><path d="M580 30L660 90V240H580Z" fill="{G}"/><path d="M500 240V70L580 30V240Z" fill="url(#wn)"/><path d="M580 30L660 90V240H580Z" fill="url(#wn)"/>')
    o.append(argon_tower(720, 860, 34, 240, p, n, G, 20, n, anim=True) + f'<rect x="720" y="34" width="140" height="206" fill="url(#wn)"/>')
    o.append(spire_tower(930, 1080, 70, 26, 240, G, G2) + f'<rect x="930" y="70" width="150" height="170" fill="url(#wn)"/>')
    o.append(f'<circle cx="1005" cy="4" r="3" fill="#ff3a3a">' + ('<animate attributeName="opacity" values="1;1;.1;1" keyTimes="0;.5;.65;1" dur="2s" repeatCount="indefinite"/>') + '</circle>')
    if not n:
        # the sun's glare slides down the glass
        o.append('<path d="M500 140L580 100V130L500 170Z M720 120L790 80V110L720 150Z M930 150L1005 110V140L930 180Z" fill="#fff" opacity=".28">'
                 '<animateTransform attributeName="transform" type="translate" values="0 0;0 26;0 0" dur="10s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                 '<animate attributeName="opacity" values=".28;.12;.28" dur="10s" repeatCount="indefinite"/></path>')
        o.append('<g>' + drift(-70, 12) + cloud(1300, 22, 200, "#fff", .55) + '</g>')
    # the window washers' gondola working down and back up the tower
    sp = 'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="12s" repeatCount="indefinite"'
    o.append(f'<path d="M1206 50h12M1272 50h12" stroke="{"#2a2a32" if not n else "#9a9eb0"}" stroke-width="4"/>'
             + ''.join(f'<line x1="{cx}" y1="50" x2="{cx}" y2="110" stroke="{"#2a2a30" if not n else "#9a9eb0"}" stroke-width="1.2"><animate attributeName="y2" values="110;170;110" {sp}/></line>' for cx in (1212, 1278))
             + f'<g><rect x="1204" y="110" width="82" height="10" fill="#e2a33a"/><path d="M1204 110V100H1286V110" fill="none" stroke="{"#2a2a30" if not n else "#9a9eb0"}" stroke-width="2"/>'
             + person(1230, 110, .4, "#2f6aa8", hat=None) + person(1260, 110, .4, "#c8442a", hat=None, arm=30)
             + f'<animateTransform attributeName="transform" type="translate" values="0 0;0 60;0 0" {sp}/></g>')
    o.append(f'<rect x="0" y="200" width="1600" height="40" fill="{"#c8c2b6" if not n else "#1a1a22"}"/>')
    for x in (440, 700, 900, 1120): o.append(f'<rect x="{x - 26}" y="192" width="52" height="12" fill="{p["conc2"]}"/><circle cx="{x}" cy="180" r="18" fill="{p["oak"]}"/>')
    o.append(corners("#10141e"))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "the interchange: premium on every level"],
    "messages": ["Texts & Emails", "the ball's lit: every message answered"],
    "coaching": ["Coaching", "the mural wall: every call, reviewed"],
    "roleplay": ["Role Play", "the rodeo: hang on through the objection"],
    "rphistory": ["Session History", "the old marquee: every session, replayed"],
    "training": ["Training", "the levee trail: miles before the calls"],
    "blueprint": ["Apollo's Road Map", "the route across dallas, in plain words"],
    "athenamap": ["Athena's Road Map", "the service route, in plain words"],
    "service": ["Service Digest", "the trolley line: keeping the book on track"],
    "renewals": ["Renewals", "bluebonnet season: what came back"],
    "claims": ["Claims", "after the hail: the crew's out"],
    "commercial": ["Commercial Center", "the glass towers: cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=40):
    c = nt if n else day
    return ('<defs>' + lg("g", (("0", c[0]), (".6", c[1]), ("1", c[2]))) + GLOWS + '</defs>' + f'<rect width="1600" height="{S}" fill="url(#g)"/>'
            + (stars(star, 0, 1600, 0, 100, 21) if n else ''))
def sground(c, y=118): return f'<rect x="0" y="{y}" width="1600" height="{S - y}" fill="{c}"/>'

def burst(x, y, r, c):
    d = ''.join(f'M{x + r * .35 * math.cos(k * math.pi / 6):.0f} {y + r * .35 * math.sin(k * math.pi / 6):.0f}L{x + r * math.cos(k * math.pi / 6):.0f} {y + r * math.sin(k * math.pi / 6):.0f}' for k in range(12))
    return f'<path d="{d}" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="4" fill="{c}"/>'

def s_sold(n):  # fireworks over the skyline
    p = P(n); o = [sbase(n, ("#2a2a62", "#8a4a86", "#e8806a"), ("#04061a", "#0e143a", "#2a1e4a"))]
    for x, y, r, c in ((470, 62, 30, "#ffd24a"), (610, 50, 24, "#ff5a5a"), (1000, 58, 30, "#5ad0ff"), (1130, 66, 22, "#ffffff"), (900, 44, 18, "#7aff9a")): o.append(burst(x, y, r, c))
    o.append(mini_skyline(780, 116, .42, "#1e1a3a" if not n else "#0e1226", True, p))
    o.append(f'<rect x="0" y="114" width="1600" height="46" fill="{"#3a3a6a" if not n else "#101830"}"/>')
    o.append('<path d="M450 124h40M600 128h30M990 124h40M760 130h50" stroke="#ffd24a" stroke-opacity=".5" stroke-width="2.5" stroke-linecap="round"/>')
    return wrap(S, ''.join(o))

def s_open(n):  # a car on its way across the arch bridge
    p = P(n); o = [sbase(n, DUSK, NT)]
    o.append(f'<rect x="0" y="112" width="1600" height="48" fill="{p["river"]}"/>')
    x0, x1, top, dk = 420, 1180, 40, 108
    ay = lambda x: dk - (dk - top) * (1 - ((x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2)
    cab = ''.join(f'M{x0 + (x1 - x0) * k / 12:.0f} {ay(x0 + (x1 - x0) * k / 12):.0f}L{x0 + (x1 - x0) * k / 12 + off:.0f} {dk}' for k in range(1, 12) for off in (-30, 30))
    o.append(f'<path d="{cab}" stroke="{p["white"]}" stroke-width="1.2" opacity=".8"/>')
    arc = 'M' + 'L'.join(f'{x:.0f} {ay(x):.0f}' for x in [x0 + (x1 - x0) * i / 30 for i in range(31)])
    if n: o.append(f'<path d="{arc}" fill="none" stroke="#cfe0ff" stroke-width="18" opacity=".15"/>')
    o.append(f'<path d="{arc}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>')
    o.append(f'<rect x="-10" y="{dk}" width="1620" height="6" fill="{p["conc"]}"/><path d="M200 {dk + 6}V160M1400 {dk + 6}V160" stroke="{p["conc2"]}" stroke-width="10"/>')
    o.append(f'<path d="M600 {dk - 8}h-90M600 {dk - 14}h-60" stroke="{"#fff" if not n else "#ffe7a0"}" stroke-width="2.5" opacity=".7" stroke-linecap="round"/>')
    o.append(car(650, dk, 1.1, "#c8202e", 0, n))
    return wrap(S, ''.join(o))

def s_lost(n):  # a grey storm over a deflated balloon
    o = [sbase(n, ("#6a6e78", "#9a9ea6", "#c0bcb4"), ("#08090e", "#16181f", "#24262e"), 6)]
    cc = "#80848e" if not n else "#20222a"
    for x, w in ((300, 460), (820, 560), (1300, 420)): o.append(f'<ellipse cx="{x}" cy="34" rx="{w // 2}" ry="34" fill="{cc}"/>')
    o.append('<path d="' + ''.join(f'M{x} {58 + (x % 3) * 6}l-10 40' for x in range(30, 1600, 36)) + f'" stroke="{"#b8bcc6" if not n else "#3a3e4a"}" stroke-width="2" opacity=".6"/>')
    gr = "#7a8a6a" if not n else "#1e241e"
    o.append(sground(gr, 108))
    env = "#a85a5a" if not n else "#4a2a2a"; env2 = "#c8b48a" if not n else "#4a4234"
    o.append(f'<path d="M640 112Q660 96 700 100Q740 86 780 98Q830 88 870 102Q910 96 930 112Z" fill="{env}"/>'
             f'<path d="M700 100Q712 108 700 112M780 98Q792 108 782 112M870 102Q880 108 872 112" stroke="{env2}" stroke-width="7" fill="none"/>')
    o.append(f'<path d="M930 112L960 106M930 108L964 100" stroke="#5a4a3a" stroke-width="1.5"/><g transform="translate(978 104) rotate(24)"><rect x="-14" y="-12" width="28" height="22" fill="#8a6a44"/><path d="M-14 -4h28M-14 4h28" stroke="#5a4428" stroke-width="2"/></g>')
    return wrap(S, ''.join(o))

def s_dead(n):  # a stalled pickup on the shoulder, hood up, hazards on
    p = P(n); o = [sbase(n, DAY, NT)]
    o.append(f'<path d="M0 98Q800 86 1600 96V160H0Z" fill="{p["far"]}"/>')
    o.append(f'<rect x="0" y="112" width="1600" height="48" fill="{p["road"]}"/><path d="M0 112H1600" stroke="#e8e4d4" stroke-width="3"/><path d="M0 140H1600" stroke="#f2c14e" stroke-width="2.5" stroke-dasharray="30 22"/>')
    o.append(pickup(800, 120, 1.25, "#2f5a8a", n, hood=True, hazards=True))
    o.append(''.join(f'<circle cx="{866 + k * 10}" cy="{62 - k * 8}" r="{6 + k * 3}" fill="#f2f2f2" opacity="{.6 - k * .12:.2f}"/>' for k in range(4)))
    o.append('<path d="M680 116L690 98L700 116Z" fill="none" stroke="#e2352b" stroke-width="3"/>')
    return wrap(S, ''.join(o))

def s_reached(n):  # two people talking by a pickup
    p = P(n); o = [sbase(n, DUSK, NT)]
    o.append(f'<path d="M0 100Q800 90 1600 100V160H0Z" fill="{p["grass"]}"/>')
    o.append(fence(-10, 1610, 82, 112, p["wood"], 90, 2))
    o.append(f'<rect x="0" y="112" width="1600" height="48" fill="{p["dirt2"]}"/>')
    o.append(pickup(640, 124, .95, "#c8202e", n))
    o.append(person(830, 126, .95, "#2f6aa8", hat="#c8a46a", arm=8) + person(920, 126, .95, "#e2a33a", hat="#4a3a2a", flip=True, arm=4))
    o.append('<path d="M796 44q8 -12 22 -12h18q14 0 14 12q0 10 -14 10h-22l-10 8z M956 40q-8 -12 -22 -12h-18q-14 0 -14 12q0 10 14 10h22l10 8z" fill="#fff" opacity=".92"/>')
    o.append('<path d="M812 43h28M914 39h28" stroke="#5a4a3a" stroke-width="3" stroke-dasharray="4 6" stroke-linecap="round"/>')
    return wrap(S, ''.join(o))

def s_live_noq(n):  # a longhorn waiting by the fence
    p = P(n); o = [sbase(n, ("#5a9ad8", "#b0d4ee", "#f4e8c8"), NT)]
    o.append(orb(n, 1080, 60, 16))
    o.append(f'<path d="M0 98Q800 86 1600 98V160H0Z" fill="{p["grass"]}"/>')
    o.append(fence(400, 1200, 74, 118, p["wood"], 100, 3))
    o.append(liveoak(1060, 104, .45, p["oak"], p["oak2"], p["trunk"]))
    o.append(longhorn(780, 126, 1.2, n))
    o.append(bluebonnets(420, 700, 120, 150, 24, 2, p, n, .7))
    return wrap(S, ''.join(o))

def s_vm(n):  # the ball tower dark under the moon
    p = P(True); o = [sbase(n, ("#1a2050", "#2e3468", "#4a4a7a"), ("#02040e", "#080d24", "#141a38"), 60)]
    if not n: o.append(stars(30, 0, 1600, 0, 90, 22))
    o.append(moon(1000, 56, 18))
    o.append(mini_skyline(820, 130, .5, "#0e1226", True, p, lit=False, ball_dark=True))
    o.append(f'<rect x="0" y="128" width="1600" height="32" fill="#0a0d1e"/>')
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Howdy, {n}.", "Everything's bigger in Texas, {n}. So are today's leads.", "Dallas, big day, {n}.",
             "Saddle up, {n}. The phones are open.", "The ball's lit, {n}. Let's light up the board.",
             "Y'all ready, {n}? Let's quote it.", "Lone Star, long list, {n}.", "Hold on through the objection, {n}.",
             "The bluebonnets are up and so are we, {n}.", "Across the bridge and close it, {n}.",
             "Every level of the interchange, {n}. Every lead.", "Hook 'em with the bundle, {n}.",
             "Fixin' to have a big day, {n}?", "No lapse, no worries, {n}.", "Get along, little leads, {n}."]

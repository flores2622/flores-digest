"""The Yuma world: the sunniest city on the river. Colour looks, fonts, the Digest picture, page banners, card strips.
Drawn from the real places -- the river crossing and its two bridges, the old territorial prison on the bluff,
the irrigated fields and date groves, the dunes, the flight line, the canals, the old main street -- never named."""
import random, math

KEY = "yuma"
NAME = "Yuma"
FONTS = "family=Arvo:wght@400;700&family=Karla:wght@400;500;600;700"
DISPLAY = "'Arvo', Georgia, serif"
DW = 700
BODY = "'Karla', system-ui, sans-serif"
SKY_BG = (("#8cc4e4", "#c9a06a"), ("#081024", "#14222c"))

LOOKS = [
    ("river", "River",
     "--surface: #eee8da; --surface-raised: #fcf9f1; --card2: #f3eee1; --chip: #e5ddc9; --text-primary: #16282a; --text-muted: #566664; --text-secondary: #3f5150; --grid: #e4ddcb; --border: #dbd3be; --border-strong: #bfb498; --accent: #0f6f6c; --accent-d: #0a5250; --side: #0f3638; --side2: #17484a; --sideInk: #dcece9; --brand: #f4efe2; --brand2: #f2c14e; --rad: 12px;",
     "--surface: #0d1716; --surface-raised: #142120; --card2: #1a2a29; --chip: #213433; --text-primary: #e2eeec; --text-muted: #96aead; --text-secondary: #b3c7c5; --grid: #213433; --border: #243837; --border-strong: #33504e; --accent: #4fc7bf; --accent-d: #82dad4; --side: #081110; --side2: #10201f; --sideInk: #dcece9; --brand: #f4efe2; --brand2: #f2c14e;",
     ["#eee8da", "#0f3638", "#0f6f6c"]),
    ("harvest", "Harvest",
     "--surface: #ecebdc; --surface-raised: #fbfaf1; --card2: #f2f0e2; --chip: #e2e0cb; --text-primary: #1c2a1c; --text-muted: #5a6656; --text-secondary: #43503f; --grid: #e2dfcc; --border: #d8d5bf; --border-strong: #bab597; --accent: #ac4426; --accent-d: #85321a; --side: #22402a; --side2: #2e5236; --sideInk: #e1ecdc; --brand: #f4f1e2; --brand2: #f0a868; --rad: 12px;",
     "--surface: #101510; --surface-raised: #171e17; --card2: #1d261d; --chip: #253025; --text-primary: #e6ece2; --text-muted: #a0ae9c; --text-secondary: #bac6b5; --grid: #253025; --border: #283428; --border-strong: #384a38; --accent: #ec8a62; --accent-d: #f3aa8a; --side: #0a0f0a; --side2: #142014; --sideInk: #e1ecdc; --brand: #f4f1e2; --brand2: #f0a868;",
     ["#ecebdc", "#22402a", "#ac4426"]),
    ("dunes", "Dunes",
     "--surface: #f3ead6; --surface-raised: #fdf9ee; --card2: #f7efdc; --chip: #ede0c2; --text-primary: #2a2214; --text-muted: #6a5c44; --text-secondary: #524631; --grid: #ebdfc6; --border: #e2d5b8; --border-strong: #c9b48a; --accent: #1d62a2; --accent-d: #154a7c; --side: #16304e; --side2: #1f4066; --sideInk: #e0e9f4; --brand: #f6efdc; --brand2: #f4c25a; --rad: 14px;",
     "--surface: #0f1219; --surface-raised: #171b24; --card2: #1d222d; --chip: #252b38; --text-primary: #ece7dc; --text-muted: #a8a294; --text-secondary: #c3bdae; --grid: #252b38; --border: #2a303d; --border-strong: #3c4456; --accent: #6fb4ec; --accent-d: #9acbf2; --side: #090c12; --side2: #121a28; --sideInk: #e0e9f4; --brand: #f6efdc; --brand2: #f4c25a;",
     ["#f3ead6", "#16304e", "#f4c25a"]),
]

# ----------------------------------------------------------------- palette
def P(n):
    if n:
        return dict(mtn="#2e2c4c", mtn2="#22223c", river="#173a4c", river2="#10303f", sand="#4a4250", sand2="#3a3442",
                    soil="#2c2630", soil2="#241f28", green="#1d3a2c", green2="#16301f", red="#3a2228", leaf="#14301e",
                    adobe="#5a4638", adobe2="#463628", stone="#4a4650", stone2="#36343e", iron="#0e0c10",
                    steel="#5a6a80", steel2="#3e4a5c", rust="#4a2c24", trunk="#2c2018", frond="#13261c", frond2="#0e1d15",
                    canal="#1a4458", win="#ffcf6a", ink="#f3e6c8", wood="#3a2a1e", wood2="#2a1c12", tam="#2a2a38", tam2="#22222e",
                    yard="#5e4a3c", yard2="#4c3c30", road="#3a3440")
    return dict(mtn="#b99aa6", mtn2="#9a7a8c", river="#3aa59d", river2="#2b8b8c", sand="#ecd3a0", sand2="#dcb97c",
                soil="#c08a56", soil2="#a8743f", green="#6aa83e", green2="#4f8c2e", red="#a8443a", leaf="#3f7a2a",
                adobe="#dcb486", adobe2="#c39866", stone="#b3a48c", stone2="#94856e", iron="#2a2522",
                steel="#9aa6ae", steel2="#6f7c86", rust="#8a4a30", trunk="#86613e", frond="#4a8a3a", frond2="#336e2a",
                canal="#3a9fb0", win="#3a3a44", ink="#fbf0d6", wood="#8a5a34", wood2="#5e3a1e", tam="#a9a07a", tam2="#c99aa0",
                yard="#e6c38a", yard2="#cfa268", road="#d2b07a")

def wrap(h, body, par="xMidYMid slice"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="{par}">{body}</svg>'

def lg(i, stops, x2=0, y2=1):
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>'

GLOW = ('<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffc35a" stop-opacity=".65"/>'
        '<stop offset="1" stop-color="#ffc35a" stop-opacity="0"/></radialGradient>')

def stars(n, x0, x1, y0, y1, seed):
    r = random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(x0, x1)}" cy="{r.randint(y0, y1)}" r="{r.choice([.8, 1.1, 1.5, 2])}" fill="#fff" opacity="{r.choice([.4, .6, .9])}"/>' for _ in range(n))

def sun(x, y, r, rays=True):
    o = []
    if rays:
        for k in range(12):
            a = k * math.pi / 6 + .2; a2 = a + .06
            o.append(f'M{x} {y}L{x + r * 2.9 * math.cos(a):.0f} {y + r * 2.9 * math.sin(a):.0f}L{x + r * 2.9 * math.cos(a2):.0f} {y + r * 2.9 * math.sin(a2):.0f}Z')
        o = [f'<path d="{"".join(o)}" fill="#fff6c8" opacity=".16"/>']
    o.append(f'<circle cx="{x}" cy="{y}" r="{r * 2.6:.0f}" fill="#fff3c0" opacity=".22"/><circle cx="{x}" cy="{y}" r="{r * 1.6:.0f}" fill="#fff3c0" opacity=".35"/>'
             f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff8dc"/><circle cx="{x}" cy="{y}" r="{r * .82:.0f}" fill="#fffdf2"/>')
    return ''.join(o)

def moon(x, y, r):
    return (f'<circle cx="{x}" cy="{y}" r="{r * 3}" fill="#e9eefc" opacity=".07"/><circle cx="{x}" cy="{y}" r="{r * 1.7:.0f}" fill="#e9eefc" opacity=".12"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="#f6f0dc"/><circle cx="{x - r * .3:.0f}" cy="{y - r * .2:.0f}" r="{r * .18:.0f}" fill="#e0d8bd"/><circle cx="{x + r * .35:.0f}" cy="{y + r * .3:.0f}" r="{r * .12:.0f}" fill="#e0d8bd"/>')

def bird(x, y, s, c):
    return f'<path d="M{x - 10 * s:.0f} {y - 3 * s:.0f}Q{x - 5 * s:.0f} {y - 7 * s:.0f} {x} {y}Q{x + 5 * s:.0f} {y - 7 * s:.0f} {x + 10 * s:.0f} {y - 3 * s:.0f}" fill="none" stroke="{c}" stroke-width="{1.8 * s:.1f}" stroke-linecap="round"/>'

def jet(x, y, s, c, flip=False, night=False):
    """a generic swept-wing jet in side view, nose to the left (flip: nose right)"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    b = (f'<path d="M-46 0Q-40 -5 -26 -6L22 -6L36 -22L44 -22L40 -5L50 -4L50 3L-26 5Q-40 4 -46 0Z" fill="{c}"/>'
         f'<path d="M-4 0L20 0L34 14L24 14Z" fill="{c}" opacity=".8"/><path d="M-30 -5Q-22 -11 -12 -6Z" fill="#9fd0ee" opacity=".85"/>')
    if night: b += '<circle cx="44" cy="-22" r="2.5" fill="#ff4a3a"/><circle cx="26" cy="12" r="2.5" fill="#5aff8a"/><circle cx="44" cy="-22" r="9" fill="#ff4a3a" opacity=".25"/>'
    return g + b + '</g>'

def contrail(x0, y0, x1, y1, w0, w1, op=.75, c="#fff"):
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    return (f'<path d="M{x0 + nx * w0:.0f} {y0 + ny * w0:.0f}L{x1 + nx * w1:.0f} {y1 + ny * w1:.0f}L{x1 - nx * w1:.0f} {y1 - ny * w1:.0f}L{x0 - nx * w0:.0f} {y0 - ny * w0:.0f}Z" fill="{c}" opacity="{op}"/>')

def jagged(x0, x1, base, lo, hi, c, seed, step=(26, 60)):
    """the jagged desert ranges: sawtooth spires"""
    r = random.Random(seed); pts = [(x0, base)]; x = x0; up = True
    while x < x1:
        x += r.randint(*step); y = r.randint(lo, lo + (hi - lo) // 3) if up else r.randint(lo + (hi - lo) // 2, hi)
        if up and r.random() < .25: pts.append((x - 6, y + 18)); y -= r.randint(10, 30)
        pts.append((min(x, x1), y)); up = not up
    pts.append((x1, base))
    return '<path d="M' + 'L'.join(f'{a} {b}' for a, b in pts) + f'Z" fill="{c}"/>'

def palm(x, b, h, s, p, lean=0, dates=True):
    """a date palm: ringed trunk, a crown of fronds, orange date clusters"""
    t = b - h; tx = x + lean; L = 62 * s
    o = [f'<path d="M{x - 7 * s:.0f} {b}Q{x + lean * .2:.0f} {b - h * .5:.0f} {tx - 4 * s:.0f} {t}L{tx + 4 * s:.0f} {t}Q{x + lean * .2 + 9 * s:.0f} {b - h * .5:.0f} {x + 7 * s:.0f} {b}Z" fill="{p["trunk"]}"/>']
    if h > 120:
        o.append(f'<path d="M{x - 6 * s:.0f} {b - h * .25:.0f}h{12 * s:.0f}M{x - 5 * s + lean * .1:.0f} {b - h * .5:.0f}h{11 * s:.0f}M{x - 5 * s + lean * .35:.0f} {b - h * .75:.0f}h{10 * s:.0f}" stroke="{p["frond2"]}" stroke-opacity=".35" stroke-width="{3 * s:.0f}"/>')
    if dates: o.append(f'<ellipse cx="{tx - 8 * s:.0f}" cy="{t + 10 * s:.0f}" rx="{8 * s:.0f}" ry="{11 * s:.0f}" fill="#d9822b"/><ellipse cx="{tx + 9 * s:.0f}" cy="{t + 9 * s:.0f}" rx="{7 * s:.0f}" ry="{10 * s:.0f}" fill="#c76a22"/>')
    fr = [(-1, .5, -.5, -.3), (-.9, .05, -.45, -.45), (-.5, -.5, -.3, -.6), (.5, -.5, .3, -.6), (.9, .05, .45, -.45), (1, .5, .5, -.3), (-.55, .8, -.5, .05), (.55, .8, .5, .05), (0, -.65, -.05, -.4)]
    d1 = ''.join(f'M{tx} {t}Q{tx + cx * L:.0f} {t + cy * L:.0f} {tx + ex * L:.0f} {t + ey * L:.0f}' for ex, ey, cx, cy in fr[:6] + fr[8:])
    d2 = ''.join(f'M{tx} {t}Q{tx + cx * L:.0f} {t + cy * L:.0f} {tx + ex * L:.0f} {t + ey * L:.0f}' for ex, ey, cx, cy in fr[6:8] + fr[1:2] + fr[4:5])
    o.append(f'<path d="{d2}" stroke="{p["frond2"]}" stroke-width="{11 * s:.0f}" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{d1}" stroke="{p["frond"]}" stroke-width="{9 * s:.0f}" fill="none" stroke-linecap="round"/>')
    return ''.join(o)

def tamarisk(x, b, s, c, c2):
    """salt cedar: a soft grey-green clump with pink plumes on top"""
    o = [f'<ellipse cx="{x - 16 * s:.0f}" cy="{b - 16 * s:.0f}" rx="{22 * s:.0f}" ry="{17 * s:.0f}" fill="{c}"/><ellipse cx="{x + 16 * s:.0f}" cy="{b - 15 * s:.0f}" rx="{21 * s:.0f}" ry="{15 * s:.0f}" fill="{c}"/>'
         f'<ellipse cx="{x}" cy="{b - 30 * s:.0f}" rx="{19 * s:.0f}" ry="{21 * s:.0f}" fill="{c}"/>']
    o.append(f'<g fill="{c2}">' + ''.join(f'<ellipse cx="{x + dx * s:.0f}" cy="{b - dy * s:.0f}" rx="{4 * s:.0f}" ry="{7 * s:.0f}"/>' for dx, dy in [(-24, 30), (-8, 48), (6, 50), (20, 30), (-30, 20), (30, 22)]) + '</g>')
    return ''.join(o)

def cottonwood(x, b, s, c, c2, trunk):
    return (f'<path d="M{x - 6 * s:.0f} {b}L{x - 3 * s:.0f} {b - 50 * s:.0f}L{x + 3 * s:.0f} {b - 50 * s:.0f}L{x + 7 * s:.0f} {b}Z" fill="{trunk}"/>'
            f'<circle cx="{x - 26 * s:.0f}" cy="{b - 62 * s:.0f}" r="{28 * s:.0f}" fill="{c2}"/><circle cx="{x + 24 * s:.0f}" cy="{b - 66 * s:.0f}" r="{30 * s:.0f}" fill="{c2}"/>'
            f'<circle cx="{x}" cy="{b - 88 * s:.0f}" r="{34 * s:.0f}" fill="{c}"/><circle cx="{x - 18 * s:.0f}" cy="{b - 72 * s:.0f}" r="{22 * s:.0f}" fill="{c}"/>')

def truss(x0, x1, deck, spans, h, hc, c, lw=4, panels=6, camel=True):
    """a through truss seen from the side: end posts, top chord (humped for a camelback), verticals, diagonals"""
    w = (x1 - x0) / spans; d = []
    for k in range(spans):
        a = x0 + k * w
        xs = [a + w * i / panels for i in range(panels + 1)]
        top = lambda i: deck - h - (hc * math.sin(math.pi * i / panels) if camel else 0)
        d.append(f'M{a:.0f} {deck}L{xs[1]:.0f} {top(1):.0f}' + ''.join(f'L{xs[i]:.0f} {top(i):.0f}' for i in range(2, panels)) + f'L{xs[-1]:.0f} {deck}')
        for i in range(1, panels):
            d.append(f'M{xs[i]:.0f} {top(i):.0f}V{deck}')
            j = i + 1 if i < panels / 2 else i - 1
            if 0 < j < panels or True: d.append(f'M{xs[i]:.0f} {top(i):.0f}L{xs[j]:.0f} {deck}')
    return f'<path d="{"".join(d)}" stroke="{c}" stroke-width="{lw}" fill="none" stroke-linejoin="round"/>'

def person(x, y, s, shirt, p, hat="#e8d6a8", flip=False, bend=False, arm=0):
    """a field hand with a wide-brim hat; y is the feet"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    if bend:
        b = (f'<path d="M-6 0L-4 -22M8 0L6 -22" stroke="#3a3440" stroke-width="6" stroke-linecap="round"/><path d="M-8 -20Q4 -40 26 -34L22 -20Z" fill="{shirt}"/>'
             f'<circle cx="30" cy="-30" r="7.5" fill="#c98e6a"/><ellipse cx="31" cy="-34" rx="14" ry="4" fill="{hat}"/><path d="M18 -26L28 -8" stroke="{shirt}" stroke-width="5" stroke-linecap="round"/>')
    else:
        b = (f'<path d="M-5 0L-3 -24M6 0L4 -24" stroke="#3a3440" stroke-width="6" stroke-linecap="round"/><rect x="-9" y="-50" width="18" height="28" rx="6" fill="{shirt}"/>'
             f'<path d="M7 -44L{14 + arm} {-30 - arm * 2}" stroke="{shirt}" stroke-width="5" stroke-linecap="round"/>'
             f'<circle cx="0" cy="-58" r="8" fill="#c98e6a"/><ellipse cx="0" cy="-63" rx="15" ry="4" fill="{hat}"/><path d="M-7 -64Q0 -76 7 -64Z" fill="{hat}"/>')
    return g + b + '</g>'

def crates(x, y, nx, ny, w, c, c2):
    return ''.join(f'<rect x="{x + i * w}" y="{y - (j + 1) * w * .7:.0f}" width="{w - 2}" height="{w * .7 - 2:.0f}" fill="{c if (i + j) % 2 else c2}"/>' for i in range(nx) for j in range(ny))

def truck(x, y, s, cab, bed, load, p, flip=False, night=False, crates_=True):
    """a stake-bed produce truck, nose to the right; y is the road"""
    g = f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    b = [f'<rect x="-80" y="-44" width="110" height="30" fill="{bed}"/><path d="M-80 -44V-62M-60 -44V-62M-40 -44V-62M-20 -44V-62M0 -44V-62M20 -44V-62" stroke="{bed}" stroke-width="4"/>']
    if crates_: b.append(crates(-78, -42, 5, 2, 21, load[0], load[1]))
    b.append(f'<path d="M32 -14L32 -52L58 -52L72 -32L76 -14Z" fill="{cab}"/><path d="M38 -46L56 -46L66 -32L38 -32Z" fill="{"#ffd98a" if night else "#bfe2f2"}"/>'
             f'<rect x="-84" y="-16" width="164" height="8" fill="#3a3440"/><circle cx="-52" cy="-6" r="11" fill="#2a2530"/><circle cx="-52" cy="-6" r="4" fill="#9a9aa4"/><circle cx="52" cy="-6" r="11" fill="#2a2530"/><circle cx="52" cy="-6" r="4" fill="#9a9aa4"/>')
    if night: b.append('<circle cx="78" cy="-22" r="4" fill="#fff4c0"/><path d="M80 -22L180 -40L180 0Z" fill="#fff4c0" opacity=".18"/>')
    return g + ''.join(b) + '</g>'

def rows(x0, y0, x1, y1, gap, colors, w, dash="12 5"):
    """crop rows: thick dashed lines read as rows of heads"""
    o = []
    for i, y in enumerate(range(y0, y1, gap)):
        o.append(f'<path d="M{x0} {y}H{x1}" stroke="{colors[i % len(colors)]}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round"/>')
    return ''.join(o)

def sign(x, y, w, h, text, fs, bg, ink, post, posts=40, font="Georgia, serif"):
    return (f'<rect x="{x - w * .36:.0f}" y="{y}" width="6" height="{h + posts}" fill="{post}"/><rect x="{x + w * .36 - 6:.0f}" y="{y}" width="6" height="{h + posts}" fill="{post}"/>'
            f'<rect x="{x - w / 2:.0f}" y="{y}" width="{w}" height="{h}" rx="4" fill="{bg}" stroke="{post}" stroke-width="3"/>'
            f'<text x="{x}" y="{y + h / 2 + fs * .36:.0f}" text-anchor="middle" font-family="{font}" font-weight="bold" font-size="{fs}" fill="{ink}" letter-spacing="1">{text}</text>')

def strap_door(x, y, w, h, iron, dark="#1a1612"):
    """an arched cell door with an iron-strap lattice"""
    r = w / 2; d = [f'M{x + w * i / 4:.0f} {y + (r if i in (0, 4) else 4)}V{y + h}' for i in range(5)] + [f'M{x} {y + r + (h - r) * j / 4:.0f}H{x + w}' for j in range(4)]
    return (f'<path d="M{x} {y + h}V{y + r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h}Z" fill="{dark}"/>'
            f'<path d="{"".join(d)}" stroke="{iron}" stroke-width="3.2"/><path d="M{x} {y + h}V{y + r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h}" fill="none" stroke="{iron}" stroke-width="4"/>')

def tower(x, base, top, p, n, w0=84, w1=60):
    """The old prison's guard tower as it stands (Frank, 2026-10-05: "make the Yuma prison more
    recognizable"): a squat square stone guardhouse on the round stone water reservoir, an outside
    stair up its side, the open timber lookout deck with its railing, a low hip roof and the flag."""
    Hh = base - top; o = []
    rf, dk, st = top + Hh * .17, top + Hh * .32, top + Hh * .77
    rw = w0 * 1.75; sw = w0; dw = w0 * 1.25
    stone, stone2, wood, wood2, iron = p["stone"], p["stone2"], p["wood"], p["wood2"], p["iron"]
    r = random.Random(int(x))
    # the reservoir: a low round stone drum with its banding
    o.append(f'<path d="M{x - rw / 2:.0f} {base}V{st + 10:.0f}Q{x:.0f} {st - 14:.0f} {x + rw / 2:.0f} {st + 10:.0f}V{base}Z" fill="{stone}"/>')
    o.append(f'<path d="M{x + rw * .1:.0f} {base}V{st + 2:.0f}Q{x + rw * .35:.0f} {st + 2:.0f} {x + rw / 2:.0f} {st + 10:.0f}V{base}Z" fill="{stone2}" opacity=".55"/>')
    for k in range(1, 4):
        yy = st + 10 + (base - st - 10) * k / 4
        o.append(f'<path d="M{x - rw / 2:.0f} {yy:.0f}Q{x:.0f} {yy + 8:.0f} {x + rw / 2:.0f} {yy:.0f}" fill="none" stroke="{stone2}" stroke-width="2" opacity=".7"/>')
        o.append('<path d="' + ''.join(f'M{x - rw / 2 + 8 + r.randint(0, int(rw) - 24)} {yy - (base - st) / 8:.0f}h{r.randint(8, 14)}' for _ in range(5)) + f'" stroke="{stone2}" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<path d="M{x - rw / 2:.0f} {st + 10:.0f}Q{x:.0f} {st - 14:.0f} {x + rw / 2:.0f} {st + 10:.0f}" fill="none" stroke="{p["adobe2"]}" stroke-width="4"/>')
    # the guardhouse: square stone, a dark door, block joints
    o.append(f'<rect x="{x - sw / 2:.0f}" y="{dk:.0f}" width="{sw:.0f}" height="{st - dk + 4:.0f}" fill="{stone}"/>')
    o.append(f'<rect x="{x + sw * .12:.0f}" y="{dk:.0f}" width="{sw * .38:.0f}" height="{st - dk + 4:.0f}" fill="{stone2}" opacity=".5"/>')
    o.append('<path d="' + ''.join(f'M{x - sw / 2 + 6 + r.randint(0, int(sw) - 20)} {r.randint(int(dk) + 6, int(st) - 4)}h{r.randint(8, 14)}' for _ in range(8)) + f'" stroke="{stone2}" stroke-width="3" stroke-linecap="round"/>')
    dh = (st - dk) * .45
    o.append(f'<path d="M{x - sw * .14:.0f} {st + 4:.0f}V{st - dh:.0f}h{sw * .28:.0f}V{st + 4:.0f}Z" fill="{"#ffcf6a" if n else "#2a1e18"}"/>')
    # the outside stair from the reservoir's rim up to the deck
    o.append(f'<path d="M{x + rw / 2 - 4:.0f} {st + 8:.0f}L{x + sw / 2 + 2:.0f} {dk + 4:.0f}" stroke="{wood2}" stroke-width="{max(3, w0 * .07):.0f}"/>'
             f'<path d="M{x + rw / 2 - 2:.0f} {st - 6:.0f}L{x + sw / 2 + 4:.0f} {dk - 10:.0f}" stroke="{wood}" stroke-width="2"/>')
    # the open lookout: floor, corner posts, x-braced railing, the sky through it, a lantern
    o.append(f'<rect x="{x - dw / 2:.0f}" y="{dk - 6:.0f}" width="{dw:.0f}" height="7" fill="{wood2}"/>')
    for k in range(4):
        px = x - dw / 2 + 2 + (dw - 7) * k / 3
        o.append(f'<rect x="{px:.0f}" y="{rf:.0f}" width="5" height="{dk - rf:.0f}" fill="{wood}"/>')
    ry = dk - (dk - rf) * .38
    o.append(f'<path d="M{x - dw / 2:.0f} {ry:.0f}H{x + dw / 2:.0f}" stroke="{wood}" stroke-width="3"/>')
    for k in range(3):
        x0 = x - dw / 2 + (dw / 3) * k; x1 = x0 + dw / 3
        o.append(f'<path d="M{x0:.0f} {ry:.0f}L{x1:.0f} {dk - 6:.0f}M{x1:.0f} {ry:.0f}L{x0:.0f} {dk - 6:.0f}" stroke="{wood}" stroke-width="1.6"/>')
    if n:
        o.append(f'<circle cx="{x}" cy="{(rf + dk) / 2:.0f}" r="{w0 * .9:.0f}" fill="url(#glow)"/><rect x="{x - 4}" y="{ry - 12:.0f}" width="8" height="10" fill="#ffd98a"/>')
    # the low hip roof, eaves wide over the deck, and the flag
    ew = dw * 1.22; ph = (rf - top) * .7
    o.append(f'<path d="M{x - ew / 2:.0f} {rf + 4:.0f}L{x - ew * .18:.0f} {rf - ph:.0f}L{x + ew * .18:.0f} {rf - ph:.0f}L{x + ew / 2:.0f} {rf + 4:.0f}Z" fill="{wood}"/>'
             f'<path d="M{x + ew * .04:.0f} {rf - ph:.0f}L{x + ew * .18:.0f} {rf - ph:.0f}L{x + ew / 2:.0f} {rf + 4:.0f}L{x + ew * .2:.0f} {rf + 4:.0f}Z" fill="{wood2}" opacity=".6"/>'
             f'<rect x="{x - ew / 2:.0f}" y="{rf + 2:.0f}" width="{ew:.0f}" height="4" fill="{wood2}"/>')
    fy = rf - ph; fl = max(10, (rf - top) * .55)
    o.append(f'<path d="M{x} {fy:.0f}V{fy - fl:.0f}" stroke="{iron}" stroke-width="2.5"/><path d="M{x} {fy - fl:.0f}l{fl * .7:.0f} {fl * .18:.0f}l-{fl * .7:.0f} {fl * .18:.0f}Z" fill="#c8442a"/>')
    return ''.join(o)

def sally_port(x, base, w, h, p, n):
    """the prison's main gate: an arched opening through the thick wall under a stepped parapet,
    the heavy strap-iron gate across it"""
    r = w * .34
    o = [f'<path d="M{x - w / 2:.0f} {base}V{base - h:.0f}h{w * .2:.0f}v-8h{w * .6:.0f}v8h{w * .2:.0f}V{base}Z" fill="{p["adobe"]}"/>',
         f'<path d="M{x + w * .1:.0f} {base}V{base - h:.0f}h{w * .3:.0f}V{base}Z" fill="{p["stone2"]}" opacity=".35"/>']
    ax0, ax1, top = x - r, x + r, base - h * .78
    o.append(f'<path d="M{ax0:.0f} {base}V{top + r:.0f}A{r:.0f} {r:.0f} 0 0 1 {ax1:.0f} {top + r:.0f}V{base}Z" fill="{"#3a2a1e" if not n else "#ffcf6a"}" opacity="{1 if not n else .55}"/>')
    bars = ''.join(f'M{ax0 + 2 * r * i / 5:.0f} {top + (r * .45 if i in (1, 4) else (r * .1 if i in (2, 3) else r)):.0f}V{base}' for i in range(1, 5))
    rails = ''.join(f'M{ax0:.0f} {top + r + (base - top - r) * j / 3:.0f}H{ax1:.0f}' for j in range(3))
    o.append(f'<path d="{bars}{rails}" stroke="{p["iron"]}" stroke-width="3"/>'
             f'<path d="M{ax0:.0f} {base}V{top + r:.0f}A{r:.0f} {r:.0f} 0 0 1 {ax1:.0f} {top + r:.0f}V{base}" fill="none" stroke="{p["stone"]}" stroke-width="5"/>')
    return ''.join(o)

# ================================================================= the Digest picture
W, H, SPLIT = 1600, 1700, 377
HZ = 408
def skyline(night):
    n = night; p = P(n); o = []; a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    sky = (("0", "#07102a"), (".55", "#142a50"), ("1", "#2c3e66")) if n else (("0", "#3f8fd2"), (".42", "#9fd0ee"), (".78", "#ffe2a2"), ("1", "#ffc56a"))
    riv = (("0", "#1c4658"), ("1", "#0f2c3c")) if n else (("0", "#62c4b6"), ("1", "#2a8d8e"))
    a('<defs>' + lg("sky", sky) + lg("riv", riv) + GLOW + '</defs>')
    a(f'<rect width="{W}" height="{HZ + 20}" fill="url(#sky)"/>')
    if n:
        a('<path d="M-40 250 Q500 40 1660 120 L1660 200 Q500 110 -40 330Z" fill="#9fb4e6" opacity=".07"/>')
        a(stars(80, 0, W, 0, 330, 5))
        a(moon(1060, 92, 40))
    else:
        a(sun(1060, 96, 62))
        a(bird(880, 140, 1.1, "#5a4a4a") + bird(905, 128, .8, "#5a4a4a") + bird(1250, 150, .9, "#7a5a50"))
    # the jets: one crossing high under its contrail, one far and small
    ct = "#c8d4f0" if n else "#ffffff"
    a(contrail(770, 58, 1640, 4, 2, 9, .35 if n else .8, ct) + contrail(770, 58, 1640, 4, 1, 4, .2 if n else .5, ct))
    a(jet(720, 60, .9, "#3a4250" if not n else "#151a26", night=n))
    a(contrail(404, 143, 660, 104, 1, 5, .25 if n else .6, ct) + jet(380, 146, .45, "#4a5260" if not n else "#151a26", night=n))
    # the jagged ranges on the horizon
    a(jagged(-10, 1610, HZ, 128, 290, p["mtn"], 3, (24, 70)))
    a(jagged(-10, 1610, HZ, 240, 350, p["mtn2"], 8, (30, 80)))
    # far bank: fields and groves under the mountains' feet
    a(f'<rect x="0" y="{HZ - 6}" width="{W}" height="26" fill="{p["green2"]}"/>')
    a(rows(0, HZ - 2, W, HZ + 18, 5, [p["green"], p["red"], p["soil"]], 3, "40 6"))
    # the river
    a(f'<rect x="0" y="{HZ + 14}" width="{W}" height="{540 - HZ}" fill="url(#riv)"/>')
    if n: a('<path d="M1040 424 L1080 424 L1120 536 L1000 536Z" fill="#f6f0dc" opacity=".16"/>')
    else: a('<path d="M1030 424 L1090 424 L1140 536 L980 536Z" fill="#fff6d0" opacity=".25"/>')
    r = random.Random(4)
    a('<path d="' + ''.join(f'M{r.randint(560, 1560)} {r.randint(426, 532)}h{r.randint(20, 70)}' for _ in range(18)) + f'" stroke="#fff" stroke-opacity="{.22 if n else .5}" stroke-width="2.5" stroke-linecap="round"/>')
    # one bridge only (Frank, 2026-10-05, of the river: "too much going on here") -- the railroad truss,
    # its train, the far bank's palm clumps and the sign are gone
    # the steel through-truss highway bridge, nearer: camelback spans on piers
    dk = 498
    for x in (800, 1060, 1320):
        a(f'<rect x="{x - 10}" y="{dk + 6}" width="20" height="32" fill="{p["stone"]}"/><rect x="{x - 14}" y="{dk + 4}" width="28" height="6" fill="{p["stone2"]}"/>')
    a(truss(540, 1580, dk, 4, 36, 20, p["steel"], 4, 6))
    a(f'<rect x="530" y="{dk}" width="1070" height="9" fill="{p["steel2"]}"/>')
    # its nameplate, the real one's name made insurance (Frank, 2026-10-05: "in real life the bridge is
    # called Ocean to Ocean Bridge, make it insurance themed")
    a(f'<path d="M870 {dk - 51}V{dk - 68}M980 {dk - 52}V{dk - 68}" stroke="{p["steel"]}" stroke-width="3"/>')
    a(f'<rect x="830" y="{dk - 88}" width="190" height="20" rx="3" fill="{"#2f6a4a" if not n else "#1c3a2a"}" stroke="{p["ink"]}" stroke-width="1.5"/>'
      f'<text x="925" y="{dk - 74}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="11" fill="{p["ink"]}" letter-spacing="1">COAST TO COAST COVERAGE</text>')
    if n:
        for x in range(600, 1600, 130): a(f'<circle cx="{x}" cy="{dk - 8}" r="22" fill="url(#glow)"/><circle cx="{x}" cy="{dk - 8}" r="3" fill="#ffe7a0"/>')
        for x in range(600, 1600, 130): a(f'<rect x="{x - 14}" y="{dk + 30}" width="28" height="3" fill="#ffd27a" opacity=".45"/>')
    # the near bank: sand, tamarisk and a cottonwood at the right
    a(f'<path d="M0 536 Q800 544 1600 532 L1600 {H} L0 {H}Z" fill="{p["sand"]}"/>')
    a(f'<rect x="0" y="556" width="{W}" height="{H - 556}" fill="{p["soil"]}"/>')
    a(f'<path d="M0 556 Q800 562 1600 554 L1600 566 Q800 576 0 568Z" fill="{p["sand2"]}"/>')
    for x, s in [(1180, 1.0), (1330, .85), (1600, 1.1)]: a(tamarisk(x, 556, s, p["tam"], p["tam2"]))
    a(cottonwood(1250, 560, 1.0, p["green"], p["leaf"], p["trunk"]))
    # the bluff and the old territorial prison, left
    a(f'<path d="M0 470 L556 470 L566 490 L546 512 L556 532 L512 556 L470 568 L380 588 L0 598Z" fill="{p["adobe2"]}"/>')
    a(f'<path d="M556 470 L566 490 L546 512 L556 532 L512 556 L470 568 L430 562 L476 544 L502 516 L520 488Z" fill="{p["stone2"]}" opacity=".55"/>')
    a(f'<rect x="0" y="420" width="510" height="52" fill="{p["adobe"]}"/><rect x="0" y="448" width="510" height="24" fill="{p["stone"]}"/>')
    a('<path d="' + ''.join(f'M{x} {452 + (x // 20) % 2 * 9}h12' for x in range(10, 500, 26)) + f'" stroke="{p["stone2"]}" stroke-width="4" stroke-linecap="round"/>')
    a(f'<rect x="0" y="414" width="510" height="8" fill="{p["adobe2"]}"/>')
    for x in (60, 120, 180, 240): a(strap_door(x, 428, 34, 44, p["iron"], "#5a3a28" if n else "#2a1e18"))
    if n:
        for x in (60, 120, 180, 240): a(f'<path d="M{x + 4} 450h26v20h-26Z" fill="#ffcf6a" opacity=".55"/>')
    a(sally_port(316, 476, 84, 96, p, n))
    a(tower(450, 476, 66, p, n))
    a(palm(30, 600, 440, 1.25, p, lean=14))
    # the lane down from the bridge to the yard
    a(f'<path d="M548 506 Q506 540 548 572 Q590 604 580 640" fill="none" stroke="{p["yard2"]}" stroke-width="34" stroke-linecap="round"/>'
      f'<path d="M548 506 Q506 540 548 572 Q590 604 580 640" fill="none" stroke="{p["road"]}" stroke-width="26" stroke-linecap="round"/>')
    # the yard the podium stands on: packed earth on the near bank, raked
    a(f'<ellipse cx="805" cy="690" rx="356" ry="118" fill="{p["yard2"]}"/><ellipse cx="805" cy="684" rx="336" ry="104" fill="{p["yard"]}"/>')
    a(f'<path d="M520 684Q805 600 1090 684M560 720Q805 650 1050 720M600 750Q805 700 1010 750" fill="none" stroke="{p["yard2"]}" stroke-width="2" opacity=".5"/>')
    a(f'<path d="M1150 700 Q1240 724 1300 764 Q1360 804 1460 826" fill="none" stroke="{p["road"]}" stroke-width="20" stroke-linecap="round"/>')
    for x in (442, 1168):
        a(f'<rect x="{x - 4}" y="604" width="8" height="70" fill="{p["iron"]}"/><path d="M{x - 10} 604h20l-4 -18h-12Z" fill="{p["iron"]}"/>'
          f'<rect x="{x - 6}" y="588" width="12" height="14" fill="{"#ffd98a" if n else "#e8dcb0"}"/>')
        if n: a(f'<circle cx="{x}" cy="596" r="60" fill="url(#glow)"/>')
    # the fields, lower left: lettuce and red leaf, a canal along the top
    a(f'<rect x="0" y="574" width="420" height="12" fill="{p["canal"]}"/><path d="M0 573H420M0 587H420" stroke="{p["stone"]}" stroke-width="3"/>')
    a(f'<path d="M0 600 L420 600 L460 1000 L0 1000Z" fill="{p["soil2"]}"/>')
    a(rows(0, 612, 440, 900, 20, [p["green"], p["red"], p["green2"]], 11))
    a(sign(210, 596, 230, 30, "FULL COVERAGE FARMS", 15, p["wood"], p["ink"], p["wood2"], 30))
    # the date grove, lower right: tidy rows
    for j, yb in enumerate((640, 720, 800)):
        for i in range(4):
            x = 1230 + i * 100 + (j % 2) * 50
            if x < 1590: a(palm(x, yb, 70 + j * 16, .62 + j * .1, p))
    a(sign(1290, 588, 170, 28, "PREMIUM DATES", 14, p["wood"], p["ink"], p["wood2"], 26))
    a(palm(1490, 660, 520, 1.3, p, lean=-26))
    a(palm(1585, 700, 500, 1.15, p, lean=10))
    a('</svg>')
    return ''.join(o)

# ================================================================= page banners (1600 x 240)
V = 240
SHADE = ('<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient></defs>'
         '<rect x="0" y="140" width="1600" height="100" fill="url(#vs)"/>')
DAY = ("#3f8fd2", "#a3d4ef", "#ffe2a2"); GOLD = ("#5a8ed0", "#f2b878", "#ffd98e"); NT = ("#050b20", "#112246", "#2a3a62")
def vwrap(body): return wrap(V, body + SHADE)
def vbase(n, day=DAY, nt=NT, star=50, extra=''):
    c = nt if n else day
    return ('<defs>' + lg("g", (("0", c[0]), (".6", c[1]), ("1", c[2]))) + GLOW + extra + '</defs>' + f'<rect width="1600" height="{V}" fill="url(#g)"/>'
            + (stars(star, 0, 1600, 0, 140, 7) if n else ''))
def orb(n, x, y, r): return moon(x, y, r * .8) if n else sun(x, y, r, rays=False)
def corners(c, op=.55):
    return f'<rect x="0" y="186" width="450" height="54" fill="{c}" opacity="{op}"/><rect x="1050" y="196" width="550" height="44" fill="{c}" opacity="{op}"/>'

def v_sales(n):  # harvest crews and trucks rolling out of the fields
    p = P(n); o = [vbase(n, GOLD)]
    o.append(orb(n, 1320, 64, 34))
    o.append(jagged(-10, 1610, 160, 70, 140, p["mtn"], 21, (30, 70)))
    o.append(f'<rect x="0" y="150" width="1600" height="90" fill="{p["soil2"]}"/>')
    o.append(rows(0, 154, 1600, 240, 11, [p["green"], p["red"], p["green2"]], 7, "16 5"))
    o.append(f'<rect x="0" y="176" width="1600" height="16" fill="{p["road"]}"/>')
    for x in (470, 780):
        o.append(''.join(f'<circle cx="{x - 70 - k * 30}" cy="{180 - k * 6}" r="{12 + k * 5}" fill="{p["sand"]}" opacity="{.6 - k * .14:.2f}"/>' for k in range(4)))
    o.append(truck(560, 190, .9, "#c8442a", p["wood"], (p["green"], "#8fc45a"), p, night=n))
    o.append(truck(870, 190, .9, "#2f7a8a", p["wood"], (p["red"], p["green"]), p, night=n))
    for x, f in ((1010, False), (1060, True), (1130, False)): o.append(person(x, 216, .75, "#e2a33a" if x % 2 else "#4a8ac0", p, bend=True, flip=f))
    o.append(sign(1200, 98, 230, 30, "NO LAPSE LETTUCE CO.", 15, p["wood"], p["ink"], p["wood2"], 46))
    if not n: o.append(bird(300, 60, 1, "#6a4a40") + bird(326, 50, .8, "#6a4a40"))
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

def v_messages(n):  # the old railroad depot and its telegraph wires
    p = P(n); o = [vbase(n, ("#4a7ac0", "#f0a878", "#ffe0a8"))]
    o.append(orb(n, 260, 60, 26))
    o.append(jagged(-10, 1610, 170, 100, 150, p["mtn"], 22, (30, 70)))
    o.append(f'<rect x="0" y="168" width="1600" height="72" fill="{p["sand2"]}"/>')
    st = "#e8d6b4" if not n else "#4a4048"; tile = "#b5523a" if not n else "#4a2420"
    o.append(f'<rect x="560" y="110" width="480" height="86" fill="{st}"/>')
    o.append(f'<path d="M540 116 L600 92 L1000 92 L1060 116Z" fill="{tile}"/>')
    o.append(f'<path d="M700 112 L700 74 Q740 74 750 56 Q800 34 850 56 Q860 74 900 74 L900 112Z" fill="{st}"/><circle cx="800" cy="76" r="12" fill="{p["ink"] if n else "#fff"}" stroke="{p["wood2"]}" stroke-width="3"/><path d="M800 76V68M800 76h6" stroke="{p["wood2"]}" stroke-width="2"/>')
    for x in (590, 660, 730, 850, 920, 990):
        if n: o.append(f'<circle cx="{x + 13}" cy="150" r="30" fill="url(#glow)"/>')
        o.append(f'<path d="M{x} 182V146A13 13 0 0 1 {x + 26} 146V182Z" fill="{"#ffd27a" if n else "#5a4a40"}"/>')
    o.append(f'<rect x="770" y="140" width="60" height="56" fill="{p["wood2"]}"/><rect x="700" y="118" width="200" height="18" fill="{p["wood2"]}"/>'
             f'<text x="800" y="132" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{p["ink"]}" letter-spacing="3">TELEGRAPH</text>')
    o.append(f'<rect x="0" y="196" width="1600" height="10" fill="{p["stone2"]}"/><path d="M0 214H1600M0 224H1600" stroke="{p["steel2"]}" stroke-width="3"/>')
    o.append('<path d="' + ''.join(f'M{x} 210v18' for x in range(0, 1600, 22)) + f'" stroke="{p["wood2"]}" stroke-width="5"/>')
    pc = p["wood2"]; poles = [60, 330, 1270, 1540]
    for x in poles: o.append(f'<rect x="{x - 4}" y="40" width="8" height="160" fill="{pc}"/><rect x="{x - 30}" y="50" width="60" height="6" fill="{pc}"/><rect x="{x - 24}" y="68" width="48" height="5" fill="{pc}"/>')
    wires = []
    for a, b in zip([-210] + poles, poles + [1810]):
        for dx, y in ((-26, 50), (26, 50), (-20, 68), (20, 68)):
            wires.append(f'M{a + dx} {y}Q{(a + b) / 2:.0f} {y + 26} {b + dx} {y}')
    o.append(f'<path d="{"".join(wires)}" stroke="{"#3a2a2a" if not n else "#8a90a8"}" stroke-width="1.6" fill="none"/>')
    bc = "#3a2a2a" if not n else "#c8cce0"
    for x, y in ((420, 66), (444, 70), (470, 72), (1120, 72), (1146, 70), (1360, 62), (1390, 60)):
        o.append(f'<ellipse cx="{x}" cy="{y - 5}" rx="6" ry="5" fill="{bc}"/><circle cx="{x + 5}" cy="{y - 10}" r="3.5" fill="{bc}"/><path d="M{x - 6} {y - 4}l-7 4" stroke="{bc}" stroke-width="3"/>')
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

def v_coaching(n):  # the old cellblock, retold as a lessons yard: doors open, flowers, string lights
    p = P(n); o = [vbase(n, GOLD)]
    o.append(orb(n, 1360, 54, 24))
    o.append(tower(1250, 150, 26, p, n, 54, 40))
    o.append(f'<rect x="0" y="190" width="1600" height="50" fill="{p["yard2"]}"/><rect x="0" y="194" width="1600" height="46" fill="{p["yard"]}"/>')
    o.append(f'<rect x="360" y="88" width="880" height="108" fill="{p["adobe"]}"/><rect x="360" y="160" width="880" height="36" fill="{p["stone"]}"/><rect x="350" y="80" width="900" height="12" fill="{p["adobe2"]}"/>')
    o.append('<path d="' + ''.join(f'M{x} {166 + (x // 20) % 2 * 12}h14' for x in range(372, 1230, 30)) + f'" stroke="{p["stone2"]}" stroke-width="4" stroke-linecap="round"/>')
    for i, x in enumerate(range(420, 1200, 130)):
        if i == 3: continue
        o.append(f'<path d="M{x} 196V136A26 26 0 0 1 {x + 52} 136V196Z" fill="#ffd98a" opacity="{.9 if n else .75}"/>')
        if n: o.append(f'<circle cx="{x + 26}" cy="160" r="50" fill="url(#glow)"/>')
        o.append(f'<g transform="translate({x} 0) skewY(-8)">' + strap_door(-30, 130 + 4, 30, 66, p["iron"], "none").replace('<path d="M-30 200V149', '<path d="M-30 200V149', 1) + '</g>')
        o.append(f'<path d="M{x + 6} 196q20 -14 40 0Z" fill="#c8442a" opacity=".0"/>')
    o.append(f'<rect x="690" y="100" width="220" height="30" rx="4" fill="{p["wood"]}" stroke="{p["wood2"]}" stroke-width="3"/>'
             f'<text x="800" y="121" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="17" fill="{p["ink"]}" letter-spacing="3">LESSONS YARD</text>')
    o.append(f'<rect x="770" y="136" width="60" height="60" fill="{p["wood2"]}"/><path d="M776 142h48v54h-48Z" fill="#ffd98a" opacity=".85"/>')
    lights = ''.join(f'<circle cx="{x}" cy="{70 + 10 * math.sin((x - 360) / 900 * math.pi * 3) ** 2:.0f}" r="4" fill="{"#ffe7a0" if n else "#f6d27a"}"/>' for x in range(370, 1240, 40))
    o.append(f'<path d="M360 70 Q510 90 650 70 Q800 90 950 70 Q1100 90 1240 70" fill="none" stroke="{p["iron"]}" stroke-width="1.5"/>{lights}')
    for x in (400, 1180, 690, 910):
        o.append(f'<path d="M{x - 14} 196L{x - 10} 176H{x + 10}L{x + 14} 196Z" fill="#b5523a"/><circle cx="{x - 8}" cy="168" r="10" fill="#d94a8a"/><circle cx="{x + 8}" cy="166" r="9" fill="#e86aa6"/><circle cx="{x}" cy="158" r="8" fill="#3f7a2a"/>')
    o.append(f'<rect x="560" y="200" width="100" height="8" fill="{p["wood"]}"/><rect x="566" y="208" width="6" height="12" fill="{p["wood2"]}"/><rect x="648" y="208" width="6" height="12" fill="{p["wood2"]}"/>')
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

def v_roleplay(n):  # a rehearsal on a stage by the river
    p = P(n); o = [vbase(n, GOLD)]
    o.append(orb(n, 1240, 56, 26))
    o.append(jagged(-10, 1610, 120, 60, 110, p["mtn"], 23, (30, 70)))
    o.append(f'<rect x="0" y="116" width="1600" height="14" fill="{p["green2"]}"/>')
    o.append(f'<rect x="0" y="128" width="1600" height="56" fill="{p["river"]}"/>')
    o.append('<path d="' + ''.join(f'M{x} {y}h40' for x, y in ((120, 146), (300, 160), (1100, 150), (1300, 168), (1450, 140), (500, 172))) + f'" stroke="#fff" stroke-opacity=".4" stroke-width="2.5" stroke-linecap="round"/>')
    o.append(f'<rect x="0" y="180" width="1600" height="60" fill="{p["sand"]}"/>')
    o.append(cottonwood(300, 190, 1.0, p["green"], p["leaf"], p["trunk"]) + cottonwood(1340, 190, 1.0, p["green"], p["leaf"], p["trunk"]) + tamarisk(160, 192, .9, p["tam"], p["tam2"]) + tamarisk(1480, 192, .9, p["tam"], p["tam2"]))
    o.append(f'<rect x="560" y="168" width="480" height="28" fill="{p["wood"]}"/><path d="M560 168H1040" stroke="{p["wood2"]}" stroke-width="4"/>')
    o.append('<path d="' + ''.join(f'M{x} 172v24' for x in range(600, 1040, 40)) + f'" stroke="{p["wood2"]}" stroke-width="2" opacity=".6"/>')
    rc = "#b5323a" if not n else "#6a1a22"
    o.append(f'<rect x="560" y="48" width="14" height="122" fill="{p["wood2"]}"/><rect x="1026" y="48" width="14" height="122" fill="{p["wood2"]}"/><rect x="550" y="40" width="500" height="16" fill="{p["wood2"]}"/>')
    o.append(f'<path d="M574 56 Q600 120 590 168 L574 168Z M1026 56 Q1000 120 1010 168 L1026 168Z" fill="{rc}"/><path d="M574 56 Q640 74 700 56 Q760 74 800 56 Q840 74 900 56 Q960 74 1026 56Z" fill="{rc}"/>')
    if n: o.append('<path d="M640 56 L600 170 L760 170Z M960 56 L840 170 L1000 170Z" fill="#fff4c0" opacity=".14"/>')
    o.append(''.join(f'<circle cx="{x}" cy="170" r="3.5" fill="#ffe7a0"/>' for x in range(600, 1020, 46)))
    o.append(person(730, 168, .95, "#3a8ac0", p, arm=8) + person(870, 168, .95, "#e2a33a", p, flip=True, hat="#8a5a34", arm=4))
    o.append('<path d="M760 92 q8 -16 28 -16 h12 q18 0 18 14 q0 12 -18 12 h-24 l-12 8z" fill="#fff" opacity=".9"/>')
    o.append(corners(p["sand2"]))
    return vwrap(''.join(o))

def v_rphistory(n):  # the old main street theatre's marquee, lit
    p = P(n); o = [vbase(n, ("#3a5a9a", "#d08aa0", "#f6c88a"), star=30)]
    br = ("#a8563a", "#c88a5a", "#8a6a8a", "#b8784a") if not n else ("#3a2228", "#3e2c26", "#2c2434", "#382822")
    xs = [0, 210, 400, 1200, 1400]
    for i, x in enumerate(xs):
        w = 200 if i != 2 else 190; top = 70 + (i * 17) % 30
        o.append(f'<rect x="{x}" y="{top}" width="{w}" height="{200 - top}" fill="{br[i % 4]}"/><rect x="{x - 4}" y="{top - 8}" width="{w + 8}" height="10" fill="{p["adobe2"]}"/>')
        for k in range(3): o.append(f'<rect x="{x + 22 + k * 58}" y="{top + 20}" width="34" height="38" fill="{"#ffcf6a" if n else "#5a6a80"}" opacity="{.8 if n else .7}"/>')
        o.append(f'<rect x="{x + 16}" y="150" width="{w - 32}" height="44" fill="{"#ffd98a" if n else "#7a9ab0"}" opacity="{.55 if n else .6}"/><path d="M{x + 10} 140h{w - 20}l-8 10h{-(w - 36)}Z" fill="{["#2f6a4a", "#c8442a", "#2f7a8a", "#e2a33a", "#2f6a4a"][i]}"/>')
    th = "#c8a46a" if not n else "#4a3a2a"
    o.append(f'<rect x="600" y="40" width="400" height="160" fill="{th}"/><rect x="594" y="32" width="412" height="12" fill="{p["adobe2"]}"/>')
    o.append(f'<path d="M760 30 L840 30 L840 110 L800 124 L760 110Z" fill="#b5323a" stroke="#ffe7a0" stroke-width="3"/>')
    for i, ch in enumerate("STAR"): o.append(f'<text x="800" y="{52 + i * 17}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="16" fill="#ffe7a0">{ch}</text>')
    o.append(f'<path d="M570 118 L1030 118 L1010 168 L590 168Z" fill="#2a2030"/>')
    if n: o.append('<ellipse cx="800" cy="150" rx="300" ry="70" fill="url(#glow)"/>')
    o.append(''.join(f'<circle cx="{x}" cy="122" r="3" fill="#ffe7a0"/><circle cx="{x}" cy="164" r="3" fill="#ffe7a0"/>' for x in range(590, 1020, 22)))
    o.append(f'<rect x="604" y="128" width="392" height="30" fill="#fbf2d8"/>'
             f'<text x="800" y="150" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="19" fill="#2a2030" letter-spacing="2">NOW SHOWING: YOUR BEST CALLS</text>')
    o.append(f'<rect x="760" y="172" width="80" height="28" fill="#5a1a22"/><rect x="772" y="178" width="56" height="16" fill="#ffd98a" opacity=".8"/>')
    o.append(f'<rect x="0" y="198" width="1600" height="42" fill="{p["stone2"]}"/><rect x="0" y="198" width="1600" height="5" fill="{p["stone"]}"/>')
    for x in (180, 1180, 1390): o.append(f'<rect x="{x}" y="150" width="5" height="50" fill="{p["iron"]}"/><circle cx="{x + 2}" cy="148" r="7" fill="{"#ffe7a0" if n else "#e8dcb0"}"/>' + (f'<circle cx="{x + 2}" cy="148" r="34" fill="url(#glow)"/>' if n else ''))
    return vwrap(''.join(o))

def v_training(n):  # jets in formation over the flight line
    p = P(n); o = [vbase(n, DAY)]
    o.append(orb(n, 1420, 50, 22))
    o.append(jagged(-10, 1610, 150, 90, 140, p["mtn"], 24, (30, 70)))
    ct = "#c8d4f0" if n else "#fff"
    for dx, dy in ((0, 0), (70, -26), (70, 26), (140, 0)):
        x, y = 640 + dx, 82 + dy
        o.append(contrail(x + 44, y, 1300 + dx, y - 12, 1.5, 7, .3 if n else .75, ct))
        o.append(jet(x, y, .75, "#3a4250" if not n else "#6a7490", night=n))
    o.append(f'<rect x="0" y="146" width="1600" height="94" fill="{p["sand2"]}"/><rect x="0" y="180" width="1600" height="60" fill="{p["stone2"]}"/>')
    hg = "#c8c0b0" if not n else "#3a3a46"
    for x in (120, 420, 1000, 1300):
        o.append(f'<path d="M{x} 182V140Q{x + 120} 104 {x + 240} 140V182Z" fill="{hg}"/><rect x="{x + 40}" y="146" width="160" height="36" fill="{"#7a7a86" if not n else "#ffd27a"}" opacity="{1 if not n else .55}"/>')
    o.append(f'<rect x="800" y="96" width="24" height="86" fill="{hg}"/><path d="M786 96 L838 96 L830 74 L794 74Z" fill="{"#6fa6c4" if not n else "#ffd27a"}"/><rect x="784" y="68" width="56" height="6" fill="{hg}"/>')
    for x in range(560, 1060, 120): o.append(jet(x, 194, .5, "#7a828e" if not n else "#2a3040", flip=True))
    o.append('<path d="M0 214H1600" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-dasharray="40 30"/>')
    return vwrap(''.join(o))

def v_map(n, athena=False):  # the irrigation map: fields, canals, four stops
    paper = "#efe4c8" if not n else "#121a22"; ink = "#4a3a24" if not n else "#d2dce6"
    fld = ["#b9d08a", "#d6a88a", "#a8c878", "#e2c896", "#c4d89a"] if not n else ["#1e3426", "#3a2626", "#22381e", "#2e2a22", "#203222"]
    route = ("#2f8a5a" if not n else "#5cd08a") if athena else ("#1d8a92" if not n else "#4fd0d0")
    o = [f'<rect width="1600" height="{V}" fill="{paper}"/>']
    r = random.Random(31 if athena else 30)
    for y in range(20, 240, 54):
        x = -20
        while x < 1620:
            w = r.randint(90, 170); c = r.choice(fld)
            o.append(f'<rect x="{x + 4}" y="{y + 4}" width="{w - 8}" height="46" fill="{c}"/>')
            if r.random() < .5: o.append(f'<path d="M{x + 8} {y + 14}H{x + w - 8}M{x + 8} {y + 24}H{x + w - 8}M{x + 8} {y + 34}H{x + w - 8}M{x + 8} {y + 44}H{x + w - 8}" stroke="{ink}" stroke-opacity=".18" stroke-width="2"/>')
            x += w
    o.append(f'<path d="M0 26 Q400 6 800 22 T1600 14 L1600 0 L0 0Z" fill="{"#7ac0c8" if not n else "#1c4458"}"/>')
    pts = [(480, 150), (720, 76), (980, 146), (1240, 70)]
    d = f'M300 26 C320 90 400 150 {pts[0][0]} {pts[0][1]} S640 70 {pts[1][0]} {pts[1][1]} S900 150 {pts[2][0]} {pts[2][1]} S1160 66 {pts[3][0]} {pts[3][1]} S1360 120 1420 200'
    o.append(f'<path d="{d}" fill="none" stroke="{paper}" stroke-width="16" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{route}" stroke-width="9" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2" stroke-dasharray="6 12"/>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for i, ((x, y), t) in enumerate(zip(pts, steps)):
        ty = y - 24 if i % 2 == 0 else y + 42
        o.append(f'<rect x="{x - 14}" y="{y - 14}" width="28" height="28" rx="4" fill="{ink}" stroke="{paper}" stroke-width="4"/><text x="{x}" y="{y + 6}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="15" fill="{paper}">{i + 1}</text>')
        o.append(f'<text x="{x}" y="{ty}" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="23" fill="{ink}" stroke="{paper}" stroke-width="6" paint-order="stroke">{t}</text>')
    o.append(f'<g transform="translate(1500 90)"><circle r="30" fill="{paper}" stroke="{ink}" stroke-width="2"/><path d="M0 -26 L7 0 L0 26 L-7 0Z" fill="{ink}"/><path d="M0 -26 L7 0 L-7 0Z" fill="{route}"/>'
             f'<text y="-34" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="13" fill="{ink}" stroke="{paper}" stroke-width="4" paint-order="stroke">N</text></g>')
    o.append(f'<rect x="0" y="0" width="1600" height="{V}" fill="none" stroke="{ink}" stroke-width="8" opacity=".35"/>')
    o.append(corners("#2a2014" if not n else "#05080c", .45))
    return vwrap(''.join(o))

def v_service(n):  # the canal keepers at the headgate
    p = P(n); o = [vbase(n, DAY)]
    o.append(orb(n, 260, 54, 26))
    o.append(jagged(-10, 1610, 140, 80, 130, p["mtn"], 25, (30, 70)))
    o.append(f'<rect x="0" y="136" width="1600" height="104" fill="{p["green2"]}"/>')
    o.append(rows(0, 140, 1600, 170, 8, [p["green"], p["red"]], 4, "30 6"))
    for x in (130, 220, 1400, 1490): o.append(palm(x, 172, 90, .7, p))
    cn = p["canal"]; con = "#d8d2c4" if not n else "#4a4a54"
    o.append(f'<path d="M0 176 L1600 176 L1600 240 L0 240Z" fill="{con}"/><path d="M0 186 L1600 186 L1600 232 L0 232Z" fill="{cn}"/>')
    o.append('<path d="' + ''.join(f'M{x} {196 + (x // 30) % 3 * 10}h34' for x in range(40, 1580, 70) if not 600 < x < 1000) + '" stroke="#fff" stroke-opacity=".45" stroke-width="2.5" stroke-linecap="round"/>')
    gc = "#b8b0a0" if not n else "#3e3e48"
    o.append(f'<rect x="620" y="120" width="360" height="80" fill="{gc}"/><rect x="610" y="112" width="380" height="12" fill="{p["stone2"]}"/>')
    for x in (660, 750, 850, 940):
        o.append(f'<rect x="{x - 28}" y="150" width="56" height="50" fill="{"#7a7466" if not n else "#2a2a32"}"/><rect x="{x - 3}" y="78" width="6" height="40" fill="{p["iron"]}"/>'
                 f'<circle cx="{x}" cy="78" r="18" fill="none" stroke="#c8442a" stroke-width="5"/><path d="M{x - 18} 78h36M{x} 60v36" stroke="#c8442a" stroke-width="3"/>')
        o.append(f'<path d="M{x - 26} 200 Q{x} 230 {x + 26} 200Z" fill="#fff" opacity=".55"/>')
    o.append(f'<path d="M600 112 H1000" stroke="{p["iron"]}" stroke-width="3"/><path d="M600 96 H1000" stroke="{p["iron"]}" stroke-width="3"/>' + ''.join(f'<path d="M{x} 96V112" stroke="{p["iron"]}" stroke-width="3"/>' for x in range(600, 1001, 50)))
    o.append(person(700, 112, .8, "#e2a33a", p, arm=10) + person(800, 112, .8, "#3a8ac0", p, flip=True, arm=10))
    o.append(corners(cn))
    return vwrap(''.join(o))

def v_renewals(n):  # the date grove at harvest
    p = P(n); o = [vbase(n, GOLD)]
    o.append(orb(n, 1380, 50, 24))
    o.append(f'<rect x="0" y="150" width="1600" height="90" fill="{p["sand2"]}"/>')
    for x in range(-20, 1640, 125): o.append(palm(x, 160, 70, .55, p, dates=False))
    for x in range(20, 1640, 150):
        if 640 < x < 960: continue
        o.append(palm(x, 214, 130, 1.0, p))
    lc = "#c8a46a" if not n else "#5a4a3a"
    o.append(palm(800, 218, 150, 1.15, p))
    o.append(f'<path d="M730 218 L776 92 M760 218 L800 92" stroke="{lc}" stroke-width="5"/>' + '<path d="' + ''.join(f'M{730 + k * 5.5:.0f} {218 - k * 15}h{30}' for k in range(1, 8)) + f'" stroke="{lc}" stroke-width="4"/>')
    o.append(person(784, 124, .8, "#c8442a", p, arm=14))
    o.append(crates(880, 216, 4, 2, 26, "#d9822b", "#c76a22") + crates(980, 216, 2, 1, 26, "#d9822b", "#b85a1a"))
    o.append(person(600, 216, .85, "#2f7a8a", p, flip=True) + crates(520, 216, 2, 1, 26, "#d9822b", "#c76a22"))
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

def v_claims(n):  # after the monsoon: a flooded field, the clouds breaking, the crew out
    p = P(n); o = [vbase(n, ("#5a6a80", "#a8bccc", "#f2e2c0"), ("#060a18", "#121c34", "#2a3452"))]
    if not n:
        o.append('<path d="M900 200 A320 200 0 0 1 1540 200" fill="none" stroke="#e86a5a" stroke-width="7" opacity=".5"/><path d="M910 200 A310 190 0 0 1 1530 200" fill="none" stroke="#f2c14e" stroke-width="7" opacity=".5"/>'
                 '<path d="M920 200 A300 180 0 0 1 1520 200" fill="none" stroke="#6ac06a" stroke-width="7" opacity=".5"/><path d="M930 200 A290 170 0 0 1 1510 200" fill="none" stroke="#5a9ad6" stroke-width="7" opacity=".5"/>')
        o.append(sun(1400, 36, 18, rays=False))
    else: o.append(moon(1400, 46, 18))
    cc = "#6a7486" if not n else "#262e46"
    for x, y, w in ((120, 30, 360), (480, 20, 320), (800, 36, 260)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="30" fill="{cc}"/><ellipse cx="{x + 50}" cy="{y - 16}" rx="{w // 3}" ry="26" fill="{cc}"/>')
    o.append('<path d="' + ''.join(f'M{x} {60 + (x % 3) * 6}l-10 34' for x in range(60, 900, 34)) + f'" stroke="{"#9aaabc" if not n else "#3a4660"}" stroke-width="2" opacity=".6"/>')
    o.append(jagged(-10, 1610, 150, 100, 140, p["mtn"], 26, (30, 70)))
    o.append(f'<rect x="0" y="146" width="1600" height="94" fill="{p["soil2"]}"/>')
    o.append(rows(0, 150, 1600, 240, 12, [p["green"], p["soil"]], 6, "18 6"))
    wc = "#a8c8d8" if not n else "#2a405a"
    for x, y, w in ((300, 196, 220), (760, 174, 300), (1240, 206, 260), (540, 222, 160), (1000, 214, 180)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{w // 2}" ry="{w // 14}" fill="{wc}" opacity=".9"/><path d="M{x - w // 4} {y - 2}h{w // 6}" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>')
    o.append(truck(540, 178, .8, "#e8e0d0" if not n else "#5a5a64", "#8a8a90", ("#5a5a64", "#5a5a64"), p, night=n, crates_=False))
    o.append(person(820, 202, .85, "#f2b230", p, hat="#f2b230", arm=-6) + f'<path d="M840 170 L866 206" stroke="{p["wood"]}" stroke-width="4"/><path d="M860 200l14 10l-6 6l-14 -10z" fill="#8a8a90"/>')
    o.append(person(930, 204, .85, "#f2b230", p, flip=True, hat="#f2b230", arm=10))
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

def v_commercial(n):  # the produce packing sheds and loading docks
    p = P(n); o = [vbase(n, DAY)]
    o.append(orb(n, 1460, 46, 22))
    o.append(jagged(-10, 1610, 120, 70, 110, p["mtn"], 27, (30, 70)))
    o.append(f'<rect x="0" y="118" width="1600" height="122" fill="{p["road"]}"/>')
    sh = "#e2dccc" if not n else "#3e3e48"; rf = "#9aa6ae" if not n else "#2a3240"
    o.append(f'<rect x="300" y="78" width="1000" height="100" fill="{sh}"/><path d="M280 82 L420 44 L1180 44 L1320 82Z" fill="{rf}"/>')
    o.append('<path d="' + ''.join(f'M{x} 48V80' for x in range(430, 1180, 24)) + '" stroke="#000" stroke-opacity=".12" stroke-width="3"/>')
    o.append(f'<rect x="580" y="54" width="440" height="34" rx="4" fill="#2f6a4a"/><text x="800" y="78" text-anchor="middle" font-family="Georgia, serif" font-weight="bold" font-size="20" fill="#fbf0d6" letter-spacing="3">NO LAPSE LETTUCE CO.</text>')
    o.append(f'<rect x="290" y="160" width="1020" height="24" fill="{p["stone2"]}"/>')
    for i, x in enumerate(range(330, 1280, 120)):
        o.append(f'<rect x="{x}" y="100" width="84" height="60" fill="{"#ffd98a" if n else "#5a5a64"}" opacity="{.75 if n else 1}"/>')
        if i % 3 != 1: o.append(f'<rect x="{x}" y="100" width="84" height="{30 + (i * 13) % 26}" fill="{"#b8b0a0" if not n else "#2e2e38"}"/>' + '<path d="' + ''.join(f'M{x} {104 + k * 8}h84' for k in range(3)) + '" stroke="#000" stroke-opacity=".15" stroke-width="2"/>')
        if n and i % 3 == 1: o.append(f'<circle cx="{x + 42}" cy="140" r="54" fill="url(#glow)"/>')
    for x in (450, 1050):
        o.append(f'<rect x="{x - 64}" y="128" width="128" height="62" fill="{"#f2efe6" if not n else "#4a4a54"}"/><rect x="{x - 64}" y="186" width="128" height="8" fill="#3a3440"/><circle cx="{x - 40}" cy="198" r="10" fill="#2a2530"/><circle cx="{x + 40}" cy="198" r="10" fill="#2a2530"/>'
                 f'<path d="M{x - 64} 140h128" stroke="#2f7a8a" stroke-width="6"/>')
    o.append(f'<g transform="translate(780 196)"><rect x="-30" y="-36" width="44" height="28" rx="3" fill="#f2b230"/><path d="M14 -60V-8M20 -60V-8" stroke="#3a3440" stroke-width="4"/><path d="M14 -14h30" stroke="#3a3440" stroke-width="4"/>'
             f'<circle cx="-18" cy="-6" r="8" fill="#2a2530"/><circle cx="6" cy="-6" r="8" fill="#2a2530"/></g>' + crates(828, 184, 3, 2, 18, p["green"], "#8fc45a"))
    for x in (100, 1500): o.append(palm(x, 190, 140, 1.0, p))
    o.append(corners(p["soil2"]))
    return vwrap(''.join(o))

VISTA_FNS = {"sales": v_sales, "messages": v_messages, "coaching": v_coaching, "roleplay": v_roleplay, "rphistory": v_rphistory,
             "training": v_training, "blueprint": lambda n: v_map(n, False), "athenamap": lambda n: v_map(n, True),
             "service": v_service, "renewals": v_renewals, "claims": v_claims, "commercial": v_commercial}
VISTA_LINES = {
    "sales": ["Sales", "harvest: premium rolling out of the fields"],
    "messages": ["Texts & Emails", "the old depot: every wire answered"],
    "coaching": ["Coaching", "the lessons yard: every call, reviewed"],
    "roleplay": ["Role Play", "the riverbank stage: run your lines"],
    "rphistory": ["Session History", "the old marquee: every session, replayed"],
    "training": ["Training", "the flight line: drills in formation"],
    "blueprint": ["Apollo's Road Map", "the canal route, in plain words"],
    "athenamap": ["Athena's Road Map", "the service route, in plain words"],
    "service": ["Service Digest", "the headgate: keeping the book flowing"],
    "renewals": ["Renewals", "the date grove: what came back around"],
    "claims": ["Claims", "after the monsoon: the crew's out"],
    "commercial": ["Commercial Center", "the packing sheds: Cerberus's book"],
}

# ================================================================= coaching-card strips (1600 x 160)
S = 160
def sbase(n, day, nt, star=40):
    c = nt if n else day
    return ('<defs>' + lg("g", (("0", c[0]), (".6", c[1]), ("1", c[2]))) + GLOW + '</defs>' + f'<rect width="1600" height="{S}" fill="url(#g)"/>'
            + (stars(star, 0, 1600, 0, 100, 21) if n else ''))
def sground(c, y=118): return f'<rect x="0" y="{y}" width="1600" height="{S - y}" fill="{c}"/>'

def burst(x, y, r, c):
    d = ''.join(f'M{x + r * .35 * math.cos(k * math.pi / 6):.0f} {y + r * .35 * math.sin(k * math.pi / 6):.0f}L{x + r * math.cos(k * math.pi / 6):.0f} {y + r * math.sin(k * math.pi / 6):.0f}' for k in range(12))
    return f'<path d="{d}" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="4" fill="{c}"/>'

def s_sold(n):  # a full harvest truck under fireworks
    p = P(n); o = [sbase(n, ("#3a3a7a", "#c86a7a", "#f6b86a"), ("#060a20", "#14204a", "#3a2a5a"))]
    for x, y, r, c in ((560, 60, 34, "#ffd24a"), (700, 44, 26, "#ff6a5a"), (1000, 56, 32, "#5ad0e0"), (1120, 40, 22, "#ffd24a"), (860, 34, 20, "#9aff8a")): o.append(burst(x, y, r, c))
    o.append(jagged(-10, 1610, 104, 70, 96, p["mtn2"], 31, (30, 60)))
    o.append(sground(p["soil2"], 100) + rows(0, 104, 1600, 160, 9, [p["green"], p["red"]], 5, "14 5"))
    o.append(f'<rect x="0" y="112" width="1600" height="12" fill="{p["road"]}"/>')
    o.append(truck(800, 124, .95, "#c8442a", p["wood"], (p["green"], "#8fc45a"), p, night=n).replace('<g transform', '<g opacity="1" transform', 1))
    o.append(crates(724, 82, 3, 1, 22, "#8fc45a", p["green"]))
    return wrap(S, ''.join(o))

def s_open(n):  # a green field mid-growth, the sprinklers running
    p = P(n); o = [sbase(n, DAY, NT)]
    o.append(orb(n, 380, 56, 20))
    o.append(jagged(-10, 1610, 96, 60, 90, p["mtn"], 32, (30, 60)))
    o.append(sground(p["soil"], 92) + rows(0, 96, 1600, 160, 8, [p["green"], p["green2"]], 6, "10 6"))
    for x in (560, 800, 1040):
        o.append(f'<rect x="{x - 2}" y="70" width="4" height="40" fill="{p["iron"]}"/>')
        o.append(''.join(f'<path d="M{x} 70 Q{x + dx * .5:.0f} {40} {x + dx} {96}" fill="none" stroke="#dff4ff" stroke-width="2.5" stroke-dasharray="3 6" opacity=".9"/>' for dx in (-110, -70, 70, 110)))
    o.append(f'<path d="M0 104H1600" stroke="{p["steel2"]}" stroke-width="5"/>')
    return wrap(S, ''.join(o))

def s_lost(n):  # a dry, cracked field under a grey sky
    o = [sbase(n, ("#7a7e86", "#a8acb0", "#c8c4bc"), ("#0a0c12", "#1a1c24", "#2a2c34"), 10)]
    cc = "#8a8e96" if not n else "#20222c"
    for x, w in ((300, 400), (800, 500), (1300, 420)): o.append(f'<ellipse cx="{x}" cy="40" rx="{w // 2}" ry="26" fill="{cc}"/>')
    gr = "#c8b090" if not n else "#3a3430"
    o.append(sground(gr, 96))
    r = random.Random(4)
    o.append('<path d="' + ''.join(f'M{x} {r.randint(98, 150)}l{r.randint(-30, 30)} {r.randint(6, 16)}l{r.randint(-20, 30)} {r.randint(-10, 12)}' for x in range(40, 1600, 46)) + f'" stroke="{"#8a7458" if not n else "#1e1a18"}" stroke-width="2.5" fill="none"/>')
    o.append(f'<path d="M760 110 Q756 84 770 70 M770 70 Q790 72 796 88 M770 70 Q750 66 742 80" fill="none" stroke="{"#8a7a50" if not n else "#4a4434"}" stroke-width="4" stroke-linecap="round"/>')
    o.append(f'<circle cx="1000" cy="98" r="18" fill="none" stroke="{"#8a7a50" if not n else "#4a4434"}" stroke-width="3" stroke-dasharray="6 3"/><circle cx="1000" cy="98" r="10" fill="none" stroke="{"#8a7a50" if not n else "#4a4434"}" stroke-width="2"/>')
    return wrap(S, ''.join(o))

def s_dead(n):  # a dune buggy stuck in the sand
    p = P(n); o = [sbase(n, DAY, NT)]
    o.append(orb(n, 420, 50, 20))
    d1 = "#f0cf8a" if not n else "#4a4048"; d2 = "#ddb06a" if not n else "#3a3240"
    o.append(f'<path d="M0 100 Q200 60 420 96 Q640 50 900 92 Q1150 54 1400 94 L1600 80 L1600 160 L0 160Z" fill="{d2}"/>')
    o.append(f'<path d="M0 130 Q300 90 600 118 Q800 80 1000 116 Q1200 100 1600 124 L1600 160 L0 160Z" fill="{d1}"/>')
    o.append('<g transform="translate(780 112) rotate(-8)">'
             f'<path d="M-70 -6 L-50 -30 L30 -30 L60 -8Z" fill="none" stroke="{p["iron"]}" stroke-width="5"/><path d="M-80 -6 L70 -6 L64 6 L-74 6Z" fill="#e2552b"/>'
             f'<circle cx="-50" cy="8" r="16" fill="#2a2530"/><circle cx="46" cy="10" r="14" fill="#2a2530"/><circle cx="-8" cy="-18" r="8" fill="#e8d6a8"/></g>')
    o.append(f'<path d="M700 120 Q760 136 860 124 Q800 140 700 132Z" fill="{d1}"/>')
    o.append(''.join(f'<circle cx="{700 - k * 22}" cy="{112 - k * 8 + (k % 2) * 6}" r="{4 + k * 2}" fill="{d1}" opacity="{.9 - k * .15:.2f}"/>' for k in range(5)))
    return wrap(S, ''.join(o))

def s_reached(n):  # two farmers talking at the field's edge
    p = P(n); o = [sbase(n, GOLD, NT)]
    o.append(orb(n, 1120, 56, 20))
    o.append(jagged(-10, 1610, 100, 64, 94, p["mtn"], 33, (30, 60)))
    o.append(sground(p["soil2"], 98) + rows(0, 102, 1600, 160, 9, [p["green"], p["red"]], 6, "14 5"))
    o.append(f'<rect x="0" y="110" width="1600" height="14" fill="{p["road"]}"/>')
    o.append(f'<path d="M640 124V86M960 124V86M640 96H960M640 110H960" stroke="{p["wood"]}" stroke-width="4"/>')
    o.append(person(740, 124, .9, "#3a8ac0", p, arm=6) + person(860, 124, .9, "#e2a33a", p, flip=True, hat="#8a5a34", arm=6))
    o.append('<path d="M700 54 q8 -14 24 -14 h20 q16 0 16 14 q0 12 -16 12 h-24 l-10 8z M900 48 q-8 -14 -24 -14 h-20 q-16 0 -16 14 q0 12 16 12 h24 l10 8z" fill="#fff" opacity=".92"/>')
    o.append('<path d="M716 54h32M856 48h32" stroke="#5a4a3a" stroke-width="3" stroke-dasharray="4 6" stroke-linecap="round"/>')
    return wrap(S, ''.join(o))

def s_live_noq(n):  # a truck waiting at the bridge
    p = P(n); o = [sbase(n, DAY, NT)]
    o.append(orb(n, 360, 50, 20))
    o.append(f'<rect x="0" y="104" width="1600" height="56" fill="{p["river"]}"/>')
    o.append(f'<rect x="0" y="104" width="800" height="56" fill="{p["sand2"]}"/><path d="M800 104 L760 160 L0 160 L0 104Z" fill="{p["sand2"]}"/>')
    o.append(truss(820, 1260, 112, 2, 36, 14, p["steel"], 4, 6) + f'<rect x="810" y="110" width="460" height="8" fill="{p["steel2"]}"/>')
    o.append(f'<rect x="1010" y="116" width="16" height="44" fill="{p["stone"]}"/>')
    o.append(f'<rect x="0" y="108" width="820" height="10" fill="{p["road"]}"/>')
    o.append(truck(640, 112, .85, "#2f7a8a", p["wood"], (p["red"], p["green"]), p, night=n))
    o.append(f'<rect x="768" y="62" width="5" height="50" fill="{p["iron"]}"/><rect x="760" y="44" width="21" height="36" rx="4" fill="{p["iron"]}"/><circle cx="770" cy="54" r="6" fill="#ff4a3a"/><circle cx="770" cy="70" r="6" fill="#3a3a30"/>')
    if n: o.append('<circle cx="770" cy="54" r="20" fill="#ff4a3a" opacity=".3"/>')
    return wrap(S, ''.join(o))

def s_vm(n):  # the old prison tower asleep under the moon
    p = P(True); o = [sbase(n, ("#1e2a5a", "#3a4a7a", "#6a6a90"), ("#03050f", "#0a0f26", "#151c3a"), 60)]
    if not n: o.append(stars(30, 0, 1600, 0, 90, 22))
    o.append(moon(560, 60, 20))
    o.append(f'<path d="M0 124 L1600 124 L1600 160 L0 160Z" fill="{p["adobe2"]}"/><rect x="500" y="100" width="700" height="26" fill="{p["adobe"]}"/>')
    o.append(tower(800, 126, 14, p, False, 54, 40))
    o.append(f'<path d="M870 46 h12 l-12 12 h12 M890 30 h16 l-16 16 h16 M914 10 h20 l-20 20 h20" fill="none" stroke="#ffd27a" stroke-width="3" stroke-linejoin="round"/>')
    o.append(palm(1060, 126, 80, .7, p, dates=False) + palm(560, 126, 60, .55, p, dates=False))
    return wrap(S, ''.join(o))

STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost,
             "followup_lost": s_lost, "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq,
             "callback_no_contact": s_vm}

# The header's greetings in this world only; {n} is the first name.
GREETINGS = ["Sunniest city, hottest leads, {n}.", "Cross the river and close it, {n}.", "Three hundred days of sun, {n}. Make hay.",
             "The fields are ready, {n}. Time to harvest.", "Fresh lettuce, fresh leads, {n}.", "Keep the canal running, {n}.",
             "Clear skies on the flight line, {n}.", "Every row pays off, {n}.", "It's a dry heat, {n}. Bring the hot quotes.",
             "Dates are sweet, so are bundles, {n}.", "The river's up and so are we, {n}.", "Pick it, pack it, bind it, {n}.",
             "Sun's out, phones out, {n}.", "Full coverage from field to river, {n}.", "Open the headgate, {n}. Let it flow."]

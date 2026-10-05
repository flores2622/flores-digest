"""The desert (Old West) world's Digest picture: a frontier town at the edge of the Sonoran desert.

Frank, 2026-10-05: "need to get more creative with this image, theres not even any movement".

One place, drawn in true one-point perspective (camera 9 m up at the end of Main Street, horizon at
unit 377 = the leaderboard's top edge):
- the top card (units 0..~400) shows the sky above the tiles: red-rock buttes, a saguaro ridge, the
  railroad water tower, the mission's bell tower at the end of the street, a windmill turning on the
  ranch behind the right-hand row, a big moon, a hawk circling and drifting clouds;
- the leaderboard (from 377) shows Main Street: false fronts down both sides with porch awnings,
  lanterns and insurance-pun signs, the street ending at the foot of the mission's knoll, and the
  town's wooden stage in the foreground where the podium stands (x 480..1130, units 540..800 kept
  clear and still).

Movement is SMIL only (self-closing <animate*/>), so the still copy for Settings > Motion > Reduced is
the same drawing with every <animate*/> removed; each element's own attributes are its resting state.

skyline(night) -> the 1600 x 1700 SVG ("xMidYMin slice"). desert_splice.py writes it into index.html.
"""
import math, random

W, H = 1600, 1700
HX, HY = 800, 377          # vanishing point = the horizon
F, E = 1000.0, 9.0         # focal length (units), eye height (m)
WX = 18.4                  # facades stand at X = -WX / +WX (m); boardwalks 2 m wide in front
BW = 16.4
ZEND = 75.0                # the building rows end here; the mission's knoll closes the street


def pr(X, Y, Z):
    return HX + F * X / Z, HY - F * (Y - E) / Z


def f0(v):
    return f"{v:.0f}"


def poly(pts, fill, extra=""):
    return f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in pts)}Z" fill="{fill}"{extra}/>'


def wpoly(ws, fill, extra=""):
    """a polygon given in world coordinates"""
    return poly([pr(*w) for w in ws], fill, extra)


def hexc(c):
    c = c.lstrip("#")
    if len(c) == 3: c = "".join(ch * 2 for ch in c)
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    A, B = hexc(a), hexc(b)
    return "#" + "".join(f"{round(A[i] + (B[i] - A[i]) * t):02x}" for i in range(3))


def face_m(side, Z, Y):
    """an affine matrix that draws in metres on a facade (left: X=-WX, right: X=+WX) around (Z, Y):
    local x runs in reading direction, local y runs down"""
    X = -WX if side < 0 else WX
    x, y = pr(X, Y, Z)
    dxdZ = -F * X / Z ** 2; dydZ = F * (Y - E) / Z ** 2; dydY = -F / Z
    k = 1 if side < 0 else -1          # left facades read toward the far end, right ones toward us
    a, b = dxdZ * k, dydZ * k
    return f"matrix({a:.2f} {b:.2f} 0 {-dydY:.2f} {x:.1f} {y:.1f})"


def flat_m(X, Y, Z):
    """metres on a plane facing the camera at depth Z, origin at (X, Y), y down"""
    x, y = pr(X, Y, Z); s = F / Z
    return f"matrix({s:.2f} 0 0 {s:.2f} {x:.1f} {y:.1f})"


# ------------------------------------------------------------------ palette
def pal(n):
    if n:
        return dict(sky=("#05060f", "#0e1230", "#241c40", "#3f2440"), haze="#3a2340",
                    butte="#3b1c22", butte2="#2a1218", mesa="#2e1a26", hill="#24141c", sag="#14100f",
                    ground="#33202a", ground2="#24161d", street="#4a3238", rut="#2a1a1e",
                    board="#3a2620", board2="#24160f", post="#2a1a12", shade="#000",
                    win="#ffcf6a", wind="#2b2a33", ink="#f3dcb0", signbg="#24160f",
                    adobe="#4a3a48", adobe2="#3a2c3a", roof="#1e1418", moon="#f6efd6",
                    cloud="#5a4a6a", stage="#4a3020", stage2="#2e1d13", lamp="#ffc55a")
    return dict(sky=("#2d2456", "#71507e", "#de7d50", "#f8c88e"), haze="#e7a074",
                butte="#b5532f", butte2="#8a3a22", mesa="#c87756", hill="#8f4f36", sag="#3d4a30",
                ground="#d59c67", ground2="#c4834f", street="#cf9a66", rut="#b77d4b",
                board="#8e5c37", board2="#5e3a22", post="#5a3820", shade="#3a1a10",
                win="#4a3036", wind="#4a4048", ink="#f6e6c2", signbg="#3a2416",
                adobe="#ead2ad", adobe2="#c9a982", roof="#6a3a26", moon="#fbf2da",
                cloud="#ffd2a8", stage="#a0693e", stage2="#6e4426", lamp="#ffd27a")


NIGHT_TINT = "#1c1220"


def tint(c, n, t=.72):
    return mix(c, NIGHT_TINT, t) if n else c


# ------------------------------------------------------------------ helpers (drawn in screen units)
def saguaro(x, b, h, c, arms=((.42, -1, .5), (.55, 1, .38))):
    w = h * .085
    o = [f'<rect x="{x - w / 2:.0f}" y="{b - h:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{w / 2:.0f}" fill="{c}"/>']
    for at, d, ah in arms:
        y0 = b - h * at; aw = w * .78; ox = x + d * w * 1.25
        o.append(f'<path d="M{x:.0f} {y0:.0f} L{ox:.0f} {y0:.0f} L{ox:.0f} {y0 - h * ah:.0f}" fill="none" stroke="{c}" '
                 f'stroke-width="{aw:.0f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(o)


def butte(pts, base, c, c2):
    d = f"M{pts[0][0]} {base} " + " ".join(f"L{x} {y}" for x, y in pts) + f" L{pts[-1][0]} {base}Z"
    # the shaded flank: the right third of the silhouette
    xs = [p[0] for p in pts]; mx = min(xs) + (max(xs) - min(xs)) * .62
    sh = [(x, y) for x, y in pts if x >= mx]
    d2 = f"M{mx:.0f} {base} L{mx:.0f} {min(y for _, y in pts) + 10} " + " ".join(f"L{x} {y}" for x, y in sh) + f" L{pts[-1][0]} {base}Z"
    return f'<path d="{d}" fill="{c}"/><path d="{d2}" fill="{c2}" opacity=".55"/>'


def strata(x0, x1, y0, y1, c, k=4):
    return "".join(f'<path d="M{x0} {y0 + (y1 - y0) * i / k:.0f} Q{(x0 + x1) / 2:.0f} {y0 + (y1 - y0) * i / k - 4:.0f} {x1} {y0 + (y1 - y0) * i / k + 2:.0f}" '
                   f'stroke="{c}" stroke-width="2" fill="none" opacity=".35"/>' for i in range(1, k))


def cloud(x, y, w, c, op):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w / 2:.0f}" ry="7" fill="{c}" opacity="{op}"/>'
            f'<ellipse cx="{x + w * .15:.0f}" cy="{y - 6}" rx="{w * .26:.0f}" ry="7" fill="{c}" opacity="{op * .8:.2f}"/>')


def tumbleweed(r, c, c2):
    o = [f'<circle r="{r}" fill="none" stroke="{c}" stroke-width="{max(1.5, r * .12):.1f}"/>']
    rnd = random.Random(int(r * 10))
    for i in range(6):
        a1 = rnd.uniform(0, 6.28); a2 = a1 + rnd.uniform(1.6, 3.0)
        o.append(f'<path d="M{r * math.cos(a1):.1f} {r * math.sin(a1):.1f} Q{r * .2 * math.cos(a1 + 1):.1f} {r * .2 * math.sin(a1 + 1):.1f} '
                 f'{r * math.cos(a2):.1f} {r * math.sin(a2):.1f}" fill="none" stroke="{c2 if i % 2 else c}" stroke-width="{max(1, r * .08):.1f}"/>')
    return "".join(o)


def lamp_glow(x, y, r, n, flick, i):
    """a hanging lantern with its glow; the glow flickers"""
    op = .85 if n else .45
    a = (f'<animate attributeName="opacity" values="{op};{op * .55:.2f};{op * .9:.2f};{op * .6:.2f};{op}" dur="{1.3 + (i % 4) * .37:.2f}s" '
         f'begin="{(i % 5) * .3:.1f}s" repeatCount="indefinite"/>') if flick else ""
    return (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * (5 if n else 3.2):.0f}" fill="url(#lg)" opacity="{op}">{a}</circle>'
            f'<line x1="{x:.0f}" y1="{y - r * 1.9:.0f}" x2="{x:.0f}" y2="{y - r:.0f}" stroke="#20140c" stroke-width="{max(1, r * .2):.1f}"/>'
            f'<rect x="{x - r * .55:.1f}" y="{y - r:.1f}" width="{r * 1.1:.1f}" height="{r * 1.7:.1f}" rx="{r * .3:.1f}" fill="#ffe2a0" stroke="#3a2416" stroke-width="{max(.8, r * .18):.1f}"/>')


def person(c, hat, lean=0):
    """a townsperson in metres (feet at 0,0, y down), hat brim and all"""
    return (f'<g transform="skewX({lean})"><path d="M-.2 0 L-.16 -.9 L-.24 -.92 L-.26 -1.45 Q0 -1.6 .26 -1.45 L.24 -.92 L.16 -.9 L.2 0 L.06 0 L0 -.8 L-.06 0Z" fill="{c}"/>'
            f'<circle cx="0" cy="-1.6" r=".13" fill="{c}"/><rect x="-.3" y="-1.72" width=".6" height=".05" rx=".02" fill="{hat}"/>'
            f'<rect x="-.13" y="-1.86" width=".26" height=".16" rx=".04" fill="{hat}"/></g>')


def wagon(n):
    """a buckboard parked by the bank, side-on along the street"""
    X = 13.4; z0, z1 = 35.0, 39.5
    c = tint("#7a4a2a", n, .65); c2 = tint("#4a2c18", n, .6)
    o = [wpoly([(X, .7, z0), (X, 1.5, z0), (X, 1.5, z1), (X, .7, z1)], c),
         wpoly([(X, 1.5, z0), (X + 1.6, 1.5, z0), (X + 1.6, 1.5, z1), (X, 1.5, z1)], mix(c, "#000", .25))]
    for z in (z0 + .6, z1 - .6):
        x, y = pr(X - .05, .55, z); s = F / z
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{s * .55 * 13.4 / z:.0f}" ry="{s * .55:.0f}" fill="none" stroke="{c2}" stroke-width="3"/>'
                 f'<path d="M{x:.0f} {y - s * .55:.0f} L{x:.0f} {y + s * .55:.0f} M{x - s * .25 * 13.4 / z:.0f} {y:.0f} L{x + s * .25 * 13.4 / z:.0f} {y:.0f}" stroke="{c2}" stroke-width="1.5"/>')
    tx, ty = pr(X, .9, z0 - 2.4); tx1, ty1 = pr(X, .9, z0)
    o.append(f'<line x1="{tx:.0f}" y1="{ty:.0f}" x2="{tx1:.0f}" y2="{ty1:.0f}" stroke="{c2}" stroke-width="3"/>')
    return "".join(o)


# ------------------------------------------------------------------ the town
LEFT = [  # (Z0, Z1, height m, colour, sign, sign colours (bg, ink), kind)
    (23, 34, 9.6, "#9c4a2f", "SALOON & SAVINGS", ("#2e1a10", "#f6dfa8"), "saloon"),
    (34, 44, 8.4, "#c9a46a", "GENERAL STORE · GENERAL LIABILITY", ("#f3e3bf", "#7a2a18"), "store"),
    (46, 55, 7.8, "#55807a", "UMBRELLA HOTEL", ("#f3e3bf", "#23443f"), "hotel"),
    (55, 65, 8.0, "#8a5a36", "NO LAPSE LIVERY", ("#2e1a10", "#f6dfa8"), "livery"),
    (65, 75, 6.8, "#b98c5c", "ASSAY · APPRAISALS", ("#3a2416", "#f6dfa8"), "plain"),
]
RIGHT = [
    (23, 33, 9.2, "#b9a283", "BANK ON IT", ("#2b3b45", "#f4e7c6"), "bank"),
    (33, 43, 8.2, "#a65a3a", "DEDUCTIBLE DRY GOODS", ("#f3e3bf", "#6a2414"), "store"),
    (45, 54, 7.6, "#6c7a8a", "SHERIFF · CLAIMS DEPT.", ("#2e1a10", "#f6dfa8"), "plain"),
    (54, 64, 8.0, "#c8955a", "TELEGRAPH · TEXT ME BACK", ("#3a2416", "#f6dfa8"), "plain"),
    (64, 75, 7.0, "#93573a", "FEED & BUNDLE", ("#f3e3bf", "#5a2414"), "plain"),
]


def building(side, b, p, n, lamps):
    Z0, Z1, Ht, col, sign, (sbg, sink), kind = b
    X = side * WX
    o = []; a = o.append
    c = tint(col, n, .74)
    if side > 0: c = mix(c, "#000", .12)          # the right-hand row is in the evening shade
    dark = mix(c, "#000", .3)
    back = side * (WX + 13)
    # roof behind the false front (seen from above), then the near side wall where it shows
    a(wpoly([(X, Ht - 2.4, Z0), (back, Ht - 3.6, Z0), (back, Ht - 3.6, Z1), (X, Ht - 2.4, Z1)], tint(p["roof"] if not n else "#2a1a1c", False)))
    a(wpoly([(X, 0, Z0), (back, 0, Z0), (back, Ht - 3.6, Z0), (X, Ht - 2.4, Z0)], mix(c, "#000", .38)))
    # the false front, its top stepped or curved by kind
    if kind in ("saloon", "bank"):
        top = [(X, Ht - .8, Z0), (X, Ht - .8, Z0 + .6), (X, Ht, Z0 + 1.2)]
        top += [(X, Ht, Z1 - 1.2), (X, Ht - .8, Z1 - .6), (X, Ht - .8, Z1)]
    elif kind in ("hotel", "livery"):
        zm = (Z0 + Z1) / 2
        top = [(X, Ht - 1.2, Z0), (X, Ht - .4, zm - 1.5), (X, Ht, zm), (X, Ht - .4, zm + 1.5), (X, Ht - 1.2, Z1)]
    else:
        top = [(X, Ht, Z0), (X, Ht, Z1)]
    a(wpoly([(X, 0, Z0)] + top + [(X, 0, Z1)], c))
    # cornice line and the corner boards
    a(f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in [pr(*t) for t in top])}" fill="none" stroke="{dark}" stroke-width="{max(2, F / Z0 * .18):.0f}"/>')
    for z in (Z0, Z1):
        x0, y0 = pr(X, 0, z); _, y1 = pr(X, Ht - .8, z)
        a(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0:.0f}" y2="{y1:.0f}" stroke="{dark}" stroke-width="{max(1.5, F / z * .16):.1f}"/>')
    # siding: a few board lines
    for yy in (1.8, 4.2):
        if yy < Ht - 1:
            a(f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in (pr(X, yy, Z0), pr(X, yy, Z1)))}" stroke="{dark}" stroke-width="1" opacity=".35"/>')
    L = Z1 - Z0; zc = (Z0 + Z1) / 2
    # upper windows (above the awning) -- lit at night
    wc = p["win"]
    nw = 2 if L > 9.5 else 1
    for k in range(nw):
        zz = Z0 + L * (k + 1) / (nw + 1)
        if Ht > 7.4:
            a(f'<g transform="{face_m(side, zz, 6.6 if kind == "saloon" else 5.4)}"><rect x="-.55" y="-.75" width="1.1" height="1.5" fill="{wc}" stroke="{p["ink"] if not n else "#3a2a20"}" stroke-width=".14"/>'
              f'<line x1="0" y1="-.75" x2="0" y2=".75" stroke="{dark}" stroke-width=".1"/></g>')
    # the sign board on the false front
    sy = 4.55 if kind == "saloon" else (Ht - 1.45 if Ht > 7.4 else 4.4)
    sw = min(L - 1.6, max(5.2, len(sign) * .29))
    fs = min(.82, sw / max(1, len(sign)) * 1.7)
    a(f'<g transform="{face_m(side, zc, sy)}"><rect x="{-sw / 2:.2f}" y="-.55" width="{sw:.2f}" height="1.1" rx=".12" fill="{tint(sbg, n, .3)}" stroke="{dark}" stroke-width=".12"/>'
      f'<text x="0" y="{fs * .34:.2f}" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size="{fs:.2f}" '
      f'textLength="{sw - .5:.2f}" lengthAdjust="spacingAndGlyphs" fill="{sink if not n else mix(sink, "#ffcf6a", .25)}">{sign.replace("&", "&amp;")}</text></g>')
    # the ground floor: door and shop windows, or the saloon's batwing doors
    door_z = zc
    if kind == "saloon":
        a(f'<g transform="{face_m(side, zc, 1.6)}">'
          f'<rect x="-1" y="-1.3" width="2" height="2.9" fill="{"#ffb84a" if n else "#3a2216"}"/>'
          + (f'<rect x="-1" y="-1.3" width="2" height="2.9" fill="#ffdc8a" opacity=".6"><animate attributeName="opacity" values=".6;.35;.55;.4;.6" dur="2.1s" repeatCount="indefinite"/></rect>' if n else "")
          + f'<rect x="-3.6" y="-1" width="1.9" height="1.6" fill="{wc}" stroke="{dark}" stroke-width=".14"/>'
          f'<rect x="1.7" y="-1" width="1.9" height="1.6" fill="{wc}" stroke="{dark}" stroke-width=".14"/>')
        # the batwing doors swing (about their hinges)
        leaf = f'fill="{tint("#c7874e", n, .55)}" stroke="#2a160a" stroke-width=".1"'
        a(f'<g transform="translate(-.98 -.45)"><g><animateTransform attributeName="transform" type="scale" values="1 1;1 1;.35 1;1.06 1;.8 1;1 1;1 1" keyTimes="0;.5;.58;.66;.74;.82;1" dur="5s" repeatCount="indefinite"/>'
          f'<path d="M0 0 L.96 .08 L.96 1.25 L0 1.25Z" {leaf}/><line x1=".2" y1=".35" x2=".8" y2=".35" stroke="#2a160a" stroke-width=".08"/></g></g>'
          f'<g transform="translate(.98 -.45)"><g><animateTransform attributeName="transform" type="scale" values="1 1;1 1;.35 1;1.06 1;.8 1;1 1;1 1" keyTimes="0;.5;.58;.66;.74;.82;1" dur="5s" repeatCount="indefinite"/>'
          f'<path d="M0 0 L-.96 .08 L-.96 1.25 L0 1.25Z" {leaf}/><line x1="-.2" y1=".35" x2="-.8" y2=".35" stroke="#2a160a" stroke-width=".08"/></g></g></g>')
    elif kind == "livery":
        a(f'<g transform="{face_m(side, zc, 1.9)}"><rect x="-1.6" y="-1.5" width="3.2" height="3.1" fill="{mix(c, "#000", .45)}"/>'
          f'<path d="M-1.6 -1.5 L1.6 1.6 M1.6 -1.5 L-1.6 1.6" stroke="{mix(c, "#fff", .2)}" stroke-width=".18"/></g>')
    else:
        a(f'<g transform="{face_m(side, zc, 1.55)}"><rect x="-.6" y="-1.15" width="1.2" height="2.7" fill="{mix(c, "#000", .5)}"/>'
          f'<rect x="-3" y="-.9" width="1.8" height="1.4" fill="{wc}" stroke="{dark}" stroke-width=".14"/>'
          f'<rect x="1.2" y="-.9" width="1.8" height="1.4" fill="{wc}" stroke="{dark}" stroke-width=".14"/></g>')
    # the boardwalk in front, the awning over it, the posts holding it up, and a lantern per post
    bx = side * BW
    a(wpoly([(X, .4, Z0), (bx, .4, Z0), (bx, .4, Z1), (X, .4, Z1)], tint("#a8744a", n, .74) if side < 0 else tint("#94643f", n, .74)))
    a(wpoly([(bx, .4, Z0), (bx, 0, Z0), (bx, 0, Z1), (bx, .4, Z1)], tint("#5e3a22", n, .7)))
    aw = tint("#7a4a2c" if kind != "hotel" else "#3f6a62", n, .72)
    a(wpoly([(X, 3.7, Z0), (bx - side * .2, 3.15, Z0), (bx - side * .2, 3.15, Z1), (X, 3.7, Z1)], aw))
    a(wpoly([(bx - side * .2, 3.15, Z0), (bx - side * .2, 2.9, Z0), (bx - side * .2, 2.9, Z1), (bx - side * .2, 3.15, Z1)], mix(aw, "#000", .35)))
    for z in (Z0 + .3, Z1 - .3):
        x0, y0 = pr(bx, .4, z); _, y1 = pr(bx, 2.95, z)
        if 470 < x0 < 1140 and y0 > 530: continue
        a(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0:.0f}" y2="{y1:.0f}" stroke="{tint("#4a2c18", n, .6)}" stroke-width="{max(1.5, F / z * .18):.1f}"/>')
    lamps.append((side, zc))
    return "".join(o)


def horse(n):
    """a horse tied at the rail in front of the saloon, side on, head to the left; its tail swishes"""
    c = tint("#7a4424", n, .55); m = tint("#3a1c0e", n, .5)
    body = ('M-1.05 -1.55 C-.7 -1.62 .55 -1.62 .95 -1.5 C1.18 -1.42 1.2 -1.1 1.08 -.95 L1.0 -.9 L1.04 0 L.9 0 L.84 -.86 '
            'L.6 -.92 L.56 0 L.42 0 L.42 -.95 L-.62 -.95 L-.66 0 L-.8 0 L-.82 -.95 L-.92 -.98 L-.94 0 L-1.08 0 L-1.1 -1.0 '
            'C-1.2 -1.15 -1.2 -1.4 -1.05 -1.55Z')
    neck = 'M-.95 -1.5 L-1.18 -2.1 L-1.5 -2.1 L-1.72 -1.86 L-1.66 -1.78 L-1.38 -1.86 L-1.12 -1.36Z'
    tail = 'M1.06 -1.42 C1.4 -1.3 1.42 -.8 1.32 -.42 L1.2 -.45 C1.24 -.85 1.18 -1.15 1.0 -1.28Z'
    saddle = '<path d="M-.35 -1.62 L.25 -1.62 L.2 -1.25 L-.3 -1.25Z" fill="#3a1a12"/><rect x="-.2" y="-1.3" width=".14" height=".5" fill="#2a120a"/>'
    return (f'<path d="{body}" fill="{c}"/><path d="{neck}" fill="{c}"/>'
            f'<path d="M-1.0 -1.52 L-1.2 -2.08 L-1.12 -2.16 L-.92 -1.6Z" fill="{m}"/>'
            f'<path d="M-1.24 -2.1 L-1.2 -2.26 L-1.12 -2.1Z" fill="{c}"/>'
            f'{saddle}'
            f'<g><path d="{tail}" fill="{m}"/><animateTransform attributeName="transform" type="rotate" '
            f'values="0 1.06 -1.38;-14 1.06 -1.38;6 1.06 -1.38;-9 1.06 -1.38;0 1.06 -1.38;0 1.06 -1.38" keyTimes="0;.12;.24;.36;.48;1" dur="4.5s" repeatCount="indefinite"/></g>')


def mission(p, n):
    """the mission on its knoll at the end of Main Street; its bell tower rises between the tiles"""
    o = []; a = o.append
    Zk = 82.0; ek = 4.0
    adobe = p["adobe"]; adobe2 = p["adobe2"]
    # the knoll the street climbs to
    kl = pr(-24, 0, ZEND); kr = pr(24, 0, ZEND)
    _, ky = pr(0, ek, Zk)
    a(f'<path d="M{kl[0] - 140:.0f} {kl[1] + 8:.0f} C{kl[0] + 40:.0f} {kl[1] - 6:.0f} {kl[0] + 90:.0f} {ky - 2:.0f} {HX - 60} {ky - 4:.0f} '
      f'L{HX + 60} {ky - 4:.0f} C{kr[0] - 90:.0f} {ky - 2:.0f} {kr[0] - 40:.0f} {kr[1] - 6:.0f} {kr[0] + 140:.0f} {kr[1] + 8:.0f}Z" fill="{p["hill"] if n else "#b9744a"}"/>')
    # a path up to the door
    a(poly([pr(-2.2, 0, ZEND), pr(-1.0, ek, Zk - 1), pr(1.0, ek, Zk - 1), pr(2.2, 0, ZEND)], p["street"], ' opacity=".9"'))
    # the church: a curved parapet facade, door, and the tall tower to the right
    s = F / Zk
    def P(X, Y): return pr(X, ek + Y, Zk)
    x0, yb = P(-7, 0); x1, _ = P(5, 0); _, yt = P(0, 8.5)
    _, yp = P(0, 11)
    a(f'<path d="M{x0:.0f} {yb:.0f} L{x0:.0f} {yt:.0f} L{x0 + s * 3:.0f} {yt:.0f} C{x0 + s * 4:.0f} {yp:.0f} {x1 - s * 4:.0f} {yp:.0f} {x1 - s * 3:.0f} {yt:.0f} '
      f'L{x1:.0f} {yt:.0f} L{x1:.0f} {yb:.0f}Z" fill="{adobe}"/>')
    dx, dy = P(-1, 0)
    a(f'<path d="M{dx:.0f} {dy:.0f} L{dx:.0f} {dy - s * 2.4:.0f} A{s:.0f} {s:.0f} 0 0 1 {dx + s * 2:.0f} {dy - s * 2.4:.0f} L{dx + s * 2:.0f} {dy:.0f}Z" '
      f'fill="{"#ffb84a" if n else "#5a3324"}"/>')
    # the tower: from the knoll up past the tiles to the belfry, dome and cross
    tx0, _ = P(5, 0); tx1, _ = P(8.6, 0)
    _, ytt = P(0, 25.5)
    a(f'<rect x="{tx0:.0f}" y="{ytt:.0f}" width="{tx1 - tx0:.0f}" height="{yb - ytt:.0f}" fill="{adobe2 if not n else adobe}"/>')
    a(f'<rect x="{tx0 - 3:.0f}" y="{ytt - 2:.0f}" width="{tx1 - tx0 + 6:.0f}" height="6" fill="{adobe2}"/>')
    _, yb1 = P(0, 26.0); _, yb2 = P(0, 29.6)
    a(f'<rect x="{tx0 + 2:.0f}" y="{yb2:.0f}" width="{tx1 - tx0 - 4:.0f}" height="{yb1 - yb2:.0f}" fill="{adobe if not n else adobe2}"/>')
    bw = (tx1 - tx0 - 4) * .56; bx = (tx0 + tx1) / 2
    a(f'<path d="M{bx - bw / 2:.0f} {yb1:.0f} L{bx - bw / 2:.0f} {yb2 + bw * .55:.0f} A{bw / 2:.0f} {bw / 2:.0f} 0 0 1 {bx + bw / 2:.0f} {yb2 + bw * .55:.0f} L{bx + bw / 2:.0f} {yb1:.0f}Z" fill="{"#1a1020" if n else "#3a2a3a"}"/>')
    a(f'<path d="M{bx - 7:.0f} {yb1 - 9:.0f} Q{bx:.0f} {yb1 - 30:.0f} {bx + 7:.0f} {yb1 - 9:.0f}Z" fill="#c9962e"/><circle cx="{bx:.0f}" cy="{yb1 - 8:.0f}" r="2.5" fill="#8a5a1a"/>')
    a(f'<rect x="{tx0:.0f}" y="{yb2 - 5:.0f}" width="{tx1 - tx0:.0f}" height="5" fill="{adobe2}"/>')
    a(f'<path d="M{tx0 + 3:.0f} {yb2 - 5:.0f} C{tx0 + 3:.0f} {yb2 - 34:.0f} {tx1 - 3:.0f} {yb2 - 34:.0f} {tx1 - 3:.0f} {yb2 - 5:.0f}Z" fill="{adobe}"/>')
    a(f'<path d="M{bx:.0f} {yb2 - 30:.0f} L{bx:.0f} {yb2 - 56:.0f} M{bx - 8:.0f} {yb2 - 47:.0f} L{bx + 8:.0f} {yb2 - 47:.0f}" stroke="{"#c9a46a" if n else "#5a3a2a"}" stroke-width="3.5"/>')
    return "".join(o), (yb2, yb1)


def windmill(p, n):
    """the ranch windmill behind the right-hand row; the wheel turns, the vane holds into the wind"""
    cx, cy, R = 1488, 104, 64
    c = "#2a2228" if n else "#4a3a3c"
    o = [f'<path d="M{cx - 30} {cy + 400} L{cx - 6} {cy + 6} L{cx + 6} {cy + 6} L{cx + 30} {cy + 400}" fill="none" stroke="{c}" stroke-width="5"/>',
         f'<path d="M{cx - 26} {cy + 330} L{cx + 22} {cy + 250} M{cx + 26} {cy + 330} L{cx - 22} {cy + 250} M{cx - 18} {cy + 190} L{cx + 15} {cy + 120} M{cx + 18} {cy + 190} L{cx - 15} {cy + 120}" stroke="{c}" stroke-width="2.5"/>',
         f'<path d="M{cx + 6} {cy - 3} L{cx + 70} {cy - 8} L{cx + 92} {cy - 30} L{cx + 96} {cy + 8} L{cx + 70} {cy + 4} L{cx + 6} {cy + 4}Z" fill="{c}"/>']
    blades = []
    for k in range(16):
        t = k * math.pi * 2 / 16
        ca, sa = math.cos(t), math.sin(t); ca2, sa2 = math.cos(t + .2), math.sin(t + .2)
        blades.append(f"M{cx + ca * 12:.0f} {cy + sa * 12:.0f} L{cx + ca * R:.0f} {cy + sa * R:.0f} L{cx + ca2 * R:.0f} {cy + sa2 * R:.0f} L{cx + ca2 * 14:.0f} {cy + sa2 * 14:.0f}Z")
    o.append(f'<g><path d="{" ".join(blades)}" fill="{"#3a3238" if n else "#e8dccb"}" stroke="{c}" stroke-width="1.5"/>'
             f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{c}" stroke-width="2.5"/><circle cx="{cx}" cy="{cy}" r="{R * .55:.0f}" fill="none" stroke="{c}" stroke-width="1.5"/>'
             f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="9s" repeatCount="indefinite"/></g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{c}"/>')
    return "".join(o)


def water_tower(p, n):
    cx, top = 470, 78
    c = "#3a2620" if n else "#6e4428"; c2 = "#2a1a14" if n else "#4e2e1a"; leg = "#24160f" if n else "#4a2e1c"
    o = [f'<path d="M{cx - 46} {top + 330} L{cx - 40} {top + 100} M{cx + 46} {top + 330} L{cx + 40} {top + 100} M{cx - 16} {top + 330} L{cx - 14} {top + 100} M{cx + 16} {top + 330} L{cx + 14} {top + 100}" stroke="{leg}" stroke-width="5"/>',
         f'<path d="M{cx - 44} {top + 200} L{cx + 44} {top + 150} M{cx + 44} {top + 200} L{cx - 44} {top + 150}" stroke="{leg}" stroke-width="2.5"/>',
         f'<path d="M{cx - 52} {top + 30} L{cx} {top - 8} L{cx + 52} {top + 30}Z" fill="{c2}"/>',
         f'<rect x="{cx - 48}" y="{top + 28}" width="96" height="76" rx="4" fill="{c}"/>']
    for k in range(1, 4):
        o.append(f'<line x1="{cx - 48}" y1="{top + 28 + k * 19}" x2="{cx + 48}" y2="{top + 28 + k * 19}" stroke="{c2}" stroke-width="2.5"/>')
    o.append(f'<path d="M{cx + 40} {top + 104} L{cx + 66} {top + 132}" stroke="{leg}" stroke-width="4"/>')
    return "".join(o)


def hawk(n):
    """a red-tailed hawk circling high over the street (rotates with its path)"""
    c = "#1a1214" if n else "#3a2420"
    body = (f'<path d="M-14 0 C-8 -3 6 -3 12 -1 L16 0 L12 1 C6 3 -8 3 -14 0Z" fill="{c}"/>'
            f'<path d="M-2 0 C-6 -10 -2 -20 6 -26 L8 -24 C4 -16 4 -8 4 0Z" fill="{c}"/>'
            f'<path d="M-2 0 C-6 10 -2 20 6 26 L8 24 C4 16 4 8 4 0Z" fill="{c}"/>'
            f'<path d="M-14 0 L-20 -4 L-20 4Z" fill="{"#5a2a1a" if not n else c}"/>')
    path = "M760 92 C760 52 900 40 960 64 C1010 86 980 128 900 132 C820 136 760 122 760 92Z"
    return (f'<g transform="translate(560 96) scale(1.35)">'
            f'<g>{body}<animateMotion path="M0 0 C0 -36 110 -50 160 -30 C205 -12 190 24 120 30 C50 36 0 26 0 0Z" rotate="auto" dur="15s" repeatCount="indefinite"/></g></g>')


def dust(x, y, w, dx, dur, begin, c, op):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{w * .18:.0f}" fill="{c}" opacity="0">'
            f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;.25;.7;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} -6" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></ellipse>')


# ------------------------------------------------------------------ the picture
def skyline(night):
    n = bool(night); p = pal(n); o = []; a = o.append
    sk = p["sky"]
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    a('<defs>'
      f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sk[0]}"/><stop offset=".42" stop-color="{sk[1]}"/>'
      f'<stop offset=".78" stop-color="{sk[2]}"/><stop offset="1" stop-color="{sk[3]}"/></linearGradient>'
      f'<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["ground2"]}"/><stop offset=".25" stop-color="{p["ground"]}"/><stop offset="1" stop-color="{p["ground2"]}"/></linearGradient>'
      f'<linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mix(p["street"], p["haze"], .35)}"/><stop offset=".4" stop-color="{p["street"]}"/><stop offset="1" stop-color="{mix(p["street"], "#000", .12)}"/></linearGradient>'
      '<radialGradient id="lg"><stop offset="0" stop-color="#ffd27a" stop-opacity=".9"/><stop offset=".35" stop-color="#ffb04a" stop-opacity=".35"/><stop offset="1" stop-color="#ff9a3a" stop-opacity="0"/></radialGradient>'
      '<radialGradient id="mg"><stop offset="0" stop-color="#fff6dc" stop-opacity=".45"/><stop offset="1" stop-color="#fff6dc" stop-opacity="0"/></radialGradient>'
      f'<radialGradient id="sg"><stop offset="0" stop-color="{"#ff9a5a" if n else "#fff0c0"}" stop-opacity="{.35 if n else .85}"/><stop offset="1" stop-color="#ffb070" stop-opacity="0"/></radialGradient>'
      '<radialGradient id="mw"><stop offset="0" stop-color="#d8d0ff" stop-opacity=".2"/><stop offset=".55" stop-color="#b8b0ff" stop-opacity=".08"/><stop offset="1" stop-color="#b8b0ff" stop-opacity="0"/></radialGradient>'
      '</defs>')
    a(f'<rect width="{W}" height="{HY + 30}" fill="url(#sky)"/>')
    # the last of the sun behind the mission (dusk) / its afterglow (night)
    a(f'<ellipse cx="{HX}" cy="{HY}" rx="760" ry="{150 if not n else 90}" fill="url(#sg)"/>')
    rnd = random.Random(7)
    if n:
        a('<g transform="rotate(-18 800 160)"><ellipse cx="800" cy="160" rx="900" ry="58" fill="url(#mw)"/><ellipse cx="760" cy="168" rx="620" ry="22" fill="url(#mw)"/></g>')
        for i in range(52):
            x, y = rnd.randint(0, W), rnd.randint(0, 330); r = rnd.choice([.7, 1, 1, 1.4, 1.9]); op = rnd.choice([.4, .6, .85])
            tw = (f'<animate attributeName="opacity" values="{op};.1;{op}" dur="{2.2 + (i % 6) * .55:.2f}s" begin="{(i % 9) * .4:.1f}s" repeatCount="indefinite"/>' if i % 3 == 0 else "")
            a(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{op}">{tw}</circle>' if tw else f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{op}"/>')
    else:
        for i in range(14):
            x, y = rnd.randint(0, W), rnd.randint(0, 90)
            a(f'<circle cx="{x}" cy="{y}" r="{rnd.choice([.8, 1.1])}" fill="#fff" opacity="{rnd.choice([.35, .55])}"/>')
    # the moon, rising big over the buttes
    mx, my, mr = 1150, 92, 50
    a(f'<circle cx="{mx}" cy="{my}" r="{mr * 3.4:.0f}" fill="url(#mg)"/>')
    a(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="{p["moon"]}" opacity="{1 if n else .92}"/>'
      f'<circle cx="{mx - 15}" cy="{my - 10}" r="9" fill="#e4dabd" opacity=".7"/><circle cx="{mx + 16}" cy="{my + 14}" r="7" fill="#e4dabd" opacity=".7"/><circle cx="{mx + 8}" cy="{my - 22}" r="4" fill="#e4dabd" opacity=".7"/>')
    # thin lit clouds drifting
    for i, (x, y, w) in enumerate([(300, 150, 230), (720, 30, 180), (1010, 158, 200), (1330, 40, 150)]):
        a(f'<g>{cloud(x, y, w, p["cloud"], .55 if not n else .35)}<animateTransform attributeName="transform" type="translate" '
          f'values="0 0;{50 + i * 14} 0;0 0" dur="{44 + i * 7}s" repeatCount="indefinite"/></g>')
    # far mesas on the horizon, then the red-rock buttes
    a(f'<path d="M0 {HY + 4} L0 352 L90 348 L120 336 L260 334 L290 350 L520 352 L560 342 L700 340 L720 356 L1090 356 L1120 338 L1300 336 L1330 350 L1600 346 L1600 {HY + 4}Z" fill="{p["mesa"]}"/>')
    a(butte([(150, 330), (176, 120), (200, 102), (232, 98), (262, 104), (280, 126), (292, 200), (318, 214), (330, 330)], HY + 4, p["butte"], p["butte2"]))
    a(strata(176, 290, 120, 330, p["butte2"], 6))
    a(butte([(300, 330), (330, 168), (350, 150), (378, 150), (396, 172), (420, 330)], HY + 4, mix(p["butte"], p["mesa"], .3), p["butte2"]))
    a(butte([(960, 330), (986, 150), (1006, 128), (1040, 124), (1070, 132), (1080, 176), (1100, 186), (1110, 330)], HY + 4, p["butte"], p["butte2"]))
    a(butte([(1180, 330), (1206, 104), (1218, 86), (1236, 84), (1250, 98), (1262, 160), (1290, 172), (1300, 330)], HY + 4, mix(p["butte"], p["butte2"], .2), p["butte2"]))
    a(strata(1206, 1262, 100, 330, p["butte2"], 7))
    # the saguaro ridge behind the left-hand row
    a(f'<path d="M-10 {HY + 6} L-10 156 C40 146 90 150 130 172 C160 190 200 226 240 300 L280 {HY + 6}Z" fill="{p["hill"]}"/>')
    a(saguaro(58, 170, 104, p["sag"])); a(saguaro(132, 184, 64, p["sag"], ((.5, 1, .45),)))
    a(f'<path d="M1610 {HY + 6} L1610 214 C1560 210 1520 222 1480 250 C1440 280 1400 320 1360 {HY + 6}Z" fill="{p["hill"]}"/>')
    a(saguaro(1376, 300, 196, p["sag"], ((.45, -1, .38), (.6, 1, .3))))
    # the railroad water tower (left), the windmill (right)
    a(water_tower(p, n))
    a(windmill(p, n))
    # the hawk
    a(hawk(n))
    # ---- the ground: desert floor, then Main Street running to the mission's knoll
    a(f'<rect x="0" y="{HY}" width="{W}" height="{H - HY}" fill="url(#gd)"/>')
    m, bell = mission(p, n)
    a(m)
    # the street (dirt), with wheel ruts converging on the far end
    zn = 8.0
    a(poly([pr(-BW, 0, zn), pr(-BW, 0, ZEND), pr(BW, 0, ZEND), pr(BW, 0, zn)], "url(#st)"))
    for X in (-6.5, -4.8, 4.6, 6.4):
        a(f'<path d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in (pr(X * .6, 0, ZEND), pr(X, 0, 20), pr(X * 1.1, 0, 9)))}" fill="none" stroke="{p["rut"]}" stroke-width="3" opacity=".55"/>')
    # bunting strung across the street from awning to awning
    zb = 40.0
    bl, br = pr(-BW, 6.0, zb), pr(BW, 6.0, zb)
    sag = 26
    a(f'<path d="M{bl[0]:.0f} {bl[1]:.0f} Q{HX} {bl[1] + sag * 2:.0f} {br[0]:.0f} {br[1]:.0f}" fill="none" stroke="{"#5a4030" if not n else "#2a1a14"}" stroke-width="2"/>')
    flags = []
    for k in range(1, 22):
        t = k / 22; x = bl[0] + (br[0] - bl[0]) * t; y = bl[1] + 4 * sag * t * (1 - t) * 1.0 * 2 / 2
        y = (1 - t) ** 2 * bl[1] + 2 * (1 - t) * t * (bl[1] + sag * 2) + t * t * br[1]
        col = ["#c8402a", "#f0c050", "#2e6a8a", "#f3e3bf"][k % 4]
        if n:
            flags.append(f'<circle cx="{x:.0f}" cy="{y + 3:.0f}" r="3" fill="#ffd27a"/>')
        else:
            flags.append(f'<path d="M{x - 7:.0f} {y:.0f} L{x + 7:.0f} {y:.0f} L{x:.0f} {y + 15:.0f}Z" fill="{col}"/>')
    a("".join(flags))
    # the rows, far to near on both sides so the nearer ones overlap
    lamps = []
    for b in reversed(LEFT): a(building(-1, b, p, n, lamps))
    for b in reversed(RIGHT): a(building(1, b, p, n, lamps))
    # townsfolk on the boardwalks and a buckboard by the bank (still)
    pc2 = tint("#3a2a2a", n, .5); hc = tint("#5a3a24", n, .5)
    for X, Z, lean in [(-17.4, 37.5, 0), (-17.0, 50.0, 0), (17.5, 27.6, -4), (17.2, 47.0, 0), (-12.0, 58.0, 0)]:
        a(f'<g transform="{flat_m(X, .4 if abs(X) > BW else 0, Z)}">{person(pc2, hc, lean)}</g>')
    a(wagon(n))
    # lanterns hung under every awning, flickering
    for i, (side, zc) in enumerate(lamps):
        for zz in (zc - 2.4, zc + 2.4):
            x, y = pr(side * (BW + .5), 2.6, zz)
            if 440 < x < 1170 and y > 520: continue
            a(lamp_glow(x, y, F / zz * .17, n, zz < 50, i * 2 + (zz > zc)))
    # the far tumbleweed crosses the street right to left, before the knoll
    tw = tumbleweed(13, tint("#a8824a", n, .6), tint("#7a5a30", n, .6))
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.06;.5;.56;1" dur="14s" repeatCount="indefinite"/>'
      f'<animateMotion path="M1068 506 Q1010 494 950 507 Q890 496 830 507 Q770 495 710 507 Q650 497 590 507 L540 508" '
      f'keyPoints="0;1;1" keyTimes="0;.56;1" calcMode="linear" dur="14s" repeatCount="indefinite"/>'
      f'<g>{tw}<animateTransform attributeName="transform" type="rotate" values="0;-720" dur="7.8s" repeatCount="indefinite"/></g></g>')
    # dust blowing down the far street and across the near corners
    dc = "#f2d2a2" if not n else "#7a5a62"
    a(dust(1000, 520, 70, -260, 9, 0, dc, .45))
    a(dust(760, 528, 60, -220, 9, 4.5, dc, .4))
    a(dust(1500, 700, 90, -250, 8, 1.5, dc, .4))
    a(dust(1560, 790, 110, -290, 10, 6, dc, .38))
    a(dust(380, 820, 90, -320, 9, 3, dc, .38))
    # ---- the near left: hitching rail and the horse in front of the saloon
    hz = 24.5
    r0, r1 = pr(-15.0, 1.0, hz - 1.6), pr(-15.0, 1.0, hz + 2.0)
    for z in (hz - 1.6, hz + 2.0):
        x0, y0 = pr(-15.0, 0, z); _, y1 = pr(-15.0, 1.05, z)
        a(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0:.0f}" y2="{y1:.0f}" stroke="{tint("#4a2c18", n, .6)}" stroke-width="5"/>')
    a(f'<line x1="{r0[0]:.0f}" y1="{r0[1]:.0f}" x2="{r1[0]:.0f}" y2="{r1[1]:.0f}" stroke="{tint("#5a3820", n, .6)}" stroke-width="5"/>')
    hx, hy = pr(-12.9, 0, hz)
    a(f'<ellipse cx="{hx:.0f}" cy="{hy + 2:.0f}" rx="{F / hz * 1.3:.0f}" ry="5" fill="#000" opacity=".2"/>')
    a(f'<g transform="{flat_m(-12.9, 0, hz)}">{horse(n)}</g>')
    # a second horse, further down, standing at the hotel's rail (still)
    hx2 = 40.0
    a(f'<g transform="{flat_m(-14.3, 0, hx2)}">{horse(n).split("<g>")[0]}</g>')
    # the near tumbleweed: rolls in from the left edge and out under the table, growing as it comes
    tw2 = tumbleweed(22, tint("#b08a50", n, .6), tint("#7a5a30", n, .6))
    a(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.4;.45;.9;1" dur="11s" repeatCount="indefinite"/>'
      f'<animateMotion path="M-40 690 Q40 668 90 712 Q150 700 200 750 Q260 742 300 800 Q350 800 400 880" keyPoints="0;0;1" keyTimes="0;.4;1" calcMode="linear" dur="11s" repeatCount="indefinite"/>'
      f'<g>{tw2}<animateTransform attributeName="transform" type="rotate" values="0;540" dur="6.6s" repeatCount="indefinite"/></g></g>')
    # one that never moves, caught against the boardwalk
    tx, ty = pr(14.6, 0, 25.5)
    a(f'<g transform="translate({tx:.0f} {ty - 9:.0f})">{tumbleweed(10, tint("#a8824a", n, .6), tint("#7a5a30", n, .6))}</g>')
    # ---- the near right: barrels, a water trough and the notice board
    for i, (X, Z) in enumerate([(15.4, 22.2), (15.9, 23.3), (14.9, 23.6)]):
        x, y = pr(X, 0, Z); s = F / Z
        bc = tint("#8a5530", n, .65)
        a(f'<rect x="{x - s * .32:.0f}" y="{y - s * .9:.0f}" width="{s * .64:.0f}" height="{s * .9:.0f}" rx="{s * .12:.0f}" fill="{bc}"/>'
          f'<line x1="{x - s * .32:.0f}" y1="{y - s * .25:.0f}" x2="{x + s * .32:.0f}" y2="{y - s * .25:.0f}" stroke="#2a1a10" stroke-width="2"/>'
          f'<line x1="{x - s * .32:.0f}" y1="{y - s * .66:.0f}" x2="{x + s * .32:.0f}" y2="{y - s * .66:.0f}" stroke="#2a1a10" stroke-width="2"/>'
          f'<ellipse cx="{x:.0f}" cy="{y - s * .9:.0f}" rx="{s * .32:.0f}" ry="{s * .08:.0f}" fill="{mix(bc, "#000", .3)}"/>')
    nx, ny = pr(10.0, 0, 20.5); s = F / 20.5
    pc = tint("#4a2c18", n, .55)
    a(f'<line x1="{nx:.0f}" y1="{ny:.0f}" x2="{nx:.0f}" y2="{ny - s * 2.6:.0f}" stroke="{pc}" stroke-width="6"/>'
      f'<line x1="{nx + s * 2.4:.0f}" y1="{ny:.0f}" x2="{nx + s * 2.4:.0f}" y2="{ny - s * 2.6:.0f}" stroke="{pc}" stroke-width="6"/>')
    a(f'<g transform="{flat_m(10.15, 2.55, 20.5)}"><rect x="0" y="0" width="2.1" height="1.25" fill="{tint("#7a4a2a", n, .55)}"/>'
      f'<rect x=".12" y=".1" width="1.86" height="1.05" fill="{tint("#efdcae", n, .45)}"/>'
      f'<text x="1.05" y=".42" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size=".3" fill="#7a1a10">WANTED</text>'
      f'<text x="1.05" y=".72" text-anchor="middle" font-family="Georgia, serif" font-weight="700" font-size=".22" fill="#2a1a10">MORE QUOTES</text>'
      f'<text x="1.05" y=".98" text-anchor="middle" font-family="Georgia, serif" font-size=".14" fill="#5a3a20">REWARD · ASK AT THE BANK</text></g>')
    # ---- the town stage in the square: the podium stands on it (flat, still)
    za, zb2 = 17.6, 20.6
    a(wpoly([(-8.6, 1.0, za), (-8.6, 1.0, zb2), (8.6, 1.0, zb2), (8.6, 1.0, za)], tint("#b07848", n, .7)))
    a(wpoly([(-8.6, 1.0, za), (8.6, 1.0, za), (8.6, 0, za), (-8.6, 0, za)], tint("#6e4426", n, .7)))
    for k in range(1, 9):
        z = za + (zb2 - za) * k / 9
        x0, y0 = pr(-8.6, 1.0, z); x1, _ = pr(8.6, 1.0, z)
        a(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y0:.0f}" stroke="{tint("#8a5a34", n, .7)}" stroke-width="1.5" opacity=".6"/>')
    if n:
        sx, sy = pr(0, 1.0, (za + zb2) / 2)
        a(f'<ellipse cx="{sx:.0f}" cy="{sy:.0f}" rx="520" ry="70" fill="url(#lg)" opacity=".35"/>')
    # bunting along the stage front (below the podium row)
    sx0, sy0 = pr(-8.6, 1.0, za); sx1, _ = pr(8.6, 1.0, za)
    a("".join(f'<path d="M{sx0 + (sx1 - sx0) * k / 16:.0f} {sy0 + 2:.0f} Q{sx0 + (sx1 - sx0) * (k + .5) / 16:.0f} {sy0 + 22:.0f} {sx0 + (sx1 - sx0) * (k + 1) / 16:.0f} {sy0 + 2:.0f}Z" '
              f'fill="{["#c8402a", "#f3e3bf", "#2e6a8a"][k % 3]}" opacity="{.95 if not n else .6}"/>' for k in range(16)))
    a('</svg>')
    # attributes in single quotes (they survive URL-encoding as one character, where " costs three);
    # the root tag keeps its double quotes so the crop can still be found by its viewBox
    head, body = o[0], "".join(o[1:])
    return head + body.replace('"', "'")


if __name__ == "__main__":
    import sys, urllib.parse
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for nm, nt in (("light", False), ("dark", True)):
        s = skyline(nt)
        open(f"{out}/new_{nm}.svg", "w").write(s)
        print(nm, len(s), "chars,", len(urllib.parse.quote(s, safe="/:=,.;- '()")), "encoded")

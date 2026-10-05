"""Space world: the page vistas (1600x240) and the coaching cards' outcome strips (1600x160)."""
import random, urllib.parse
def enc(svg): return urllib.parse.quote(svg, safe="/:=,.;- '()")
def stars(n, w, y0, y1, seed, op=(0.3,0.5,0.8)):
    r=random.Random(seed); o=[]
    for _ in range(n):
        o.append(f'<circle cx="{r.randint(0,w)}" cy="{r.randint(y0,y1)}" r="{r.choice([0.6,0.9,1.2,1.6])}" fill="#fff" opacity="{r.choice(op)}"/>')
    return ''.join(o)
def sky(h, night, day=("#17306e","#4f8fd6","#bfe0f5"), nt=("#04060f","#0c1330","#1a2550")):
    c = nt if night else day
    return (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c[0]}"/><stop offset=".6" stop-color="{c[1]}"/><stop offset="1" stop-color="{c[2]}"/></linearGradient>'
            f'<radialGradient id="gl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a" stop-opacity=".6"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="fl" cx=".5" cy=".2" r=".7"><stop offset="0" stop-color="#fff4c8"/><stop offset=".45" stop-color="#ffb347" stop-opacity=".8"/><stop offset="1" stop-color="#ff6a1a" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="1600" height="{h}" fill="url(#g)"/>')
def earth(cx, cy, r, night):
    sea = "#2b6fc9" if not night else "#163d7a"; land = "#5aa35a" if not night else "#2e6b3a"
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sea}"/>'
            f'<path d="M{cx-r*.6} {cy-r*.2} q{r*.3} -{r*.5} {r*.7} -{r*.3} q{r*.2} {r*.3} -{r*.1} {r*.5} q-{r*.4} {r*.2} -{r*.6} -{r*.2} z" fill="{land}"/>'
            f'<path d="M{cx+r*.1} {cy+r*.3} q{r*.3} -{r*.2} {r*.5} {r*.1} q-{r*.1} {r*.3} -{r*.4} {r*.3} z" fill="{land}"/>'
            f'<ellipse cx="{cx-r*.2}" cy="{cy-r*.55}" rx="{r*.5}" ry="{r*.08}" fill="#fff" opacity=".55"/><ellipse cx="{cx+r*.3}" cy="{cy+r*.1}" rx="{r*.35}" ry="{r*.06}" fill="#fff" opacity=".45"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#9cd3ff" stroke-opacity=".6" stroke-width="{max(2,r*.04)}"/>')
def rocket(x, y, h, night, flame=False, scale=1):
    w = 26*scale; body="#eef1f6" if not night else "#d5dce8"; st="#e2552b"; dk="#2b3140"
    o=[f'<rect x="{x-w/2}" y="{y-h}" width="{w}" height="{h}" rx="{w/5}" fill="{body}"/>',
       f'<path d="M{x-w/2} {y-h+4} Q{x} {y-h-w*1.4} {x+w/2} {y-h+4} Z" fill="{st}"/>',
       f'<rect x="{x-w/2}" y="{y-h*.55}" width="{w}" height="{h*.08}" fill="{st}"/>',
       f'<path d="M{x-w/2} {y-h*.25} L{x-w} {y} L{x-w/2} {y} Z M{x+w/2} {y-h*.25} L{x+w} {y} L{x+w/2} {y} Z" fill="{st}"/>',
       f'<path d="M{x-w*.3} {y-3} L{x+w*.3} {y-3} L{x+w*.4} {y+6} L{x-w*.4} {y+6} Z" fill="{dk}"/>',
       f'<circle cx="{x}" cy="{y-h*.75}" r="{w*.18}" fill="#8ecdf2" stroke="{dk}" stroke-width="2"/>']
    if flame:
        o.append(f'<path d="M{x-w*.35} {y+6} Q{x} {y+h*.9} {x+w*.35} {y+6} Z" fill="url(#fl)"/><path d="M{x-w*.18} {y+6} Q{x} {y+h*.55} {x+w*.18} {y+6} Z" fill="#fff6c8" opacity=".9"/>')
    return ''.join(o)
def dish(x, y, r, night, tilt=-30):
    c="#cfd6e2" if not night else "#8d98b0"; c2="#8a95aa" if not night else "#5a6478"
    return (f'<rect x="{x-5}" y="{y}" width="10" height="{r*1.1}" fill="{c2}"/><g transform="rotate({tilt} {x} {y})"><path d="M{x-r} {y} A{r} {r} 0 0 1 {x+r} {y} Z" fill="{c}"/><path d="M{x-r} {y} A{r} {r} 0 0 1 {x+r} {y}" fill="none" stroke="{c2}" stroke-width="3"/><line x1="{x}" y1="{y}" x2="{x}" y2="{y-r}" stroke="{c2}" stroke-width="3"/><circle cx="{x}" cy="{y-r}" r="5" fill="{c2}"/></g>')
def astronaut(x, y, s, night, flip=False):
    suit="#f2f4f8" if not night else "#d9dee8"; vis="#f6b24a"; dk="#3a4150"
    g=f'<g transform="translate({x} {y}) scale({-s if flip else s} {s})">'
    return (g+f'<rect x="-22" y="-10" width="44" height="60" rx="14" fill="{suit}"/><rect x="-30" y="0" width="12" height="40" rx="6" fill="{suit}" transform="rotate(20)"/><rect x="18" y="0" width="12" height="40" rx="6" fill="{suit}" transform="rotate(-20)"/>'
            f'<rect x="-16" y="46" width="13" height="30" rx="6" fill="{suit}"/><rect x="3" y="46" width="13" height="30" rx="6" fill="{suit}"/><circle cx="0" cy="-26" r="22" fill="{suit}"/><path d="M-15 -30 a15 15 0 0 1 30 0 v10 a15 15 0 0 1 -30 0 z" fill="{vis}"/>'
            f'<rect x="-14" y="2" width="28" height="18" rx="3" fill="{dk}"/><rect x="-26" y="-14" width="52" height="8" rx="4" fill="{dk}" opacity=".3"/></g>')
def ground(h, y, night, c1=None, c2=None):
    c1 = c1 or ("#8d98a8" if not night else "#1b2440"); return f'<rect x="0" y="{y}" width="1600" height="{h-y}" fill="{c1}"/>'
def craters(n, y0, y1, seed, night):
    r=random.Random(seed); o=[]; c="#0f1328" if night else "#9aa3b5"; c2="#2b3350" if night else "#c3cad6"
    for _ in range(n):
        x=r.randint(0,1600); y=r.randint(y0,y1); rx=r.randint(14,60)
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx//3}" fill="{c}"/><ellipse cx="{x}" cy="{y-2}" rx="{rx-4}" ry="{rx//3-2}" fill="{c2}" opacity=".5"/>')
    return ''.join(o)
V=240
# ---- banner movement: self-closing SMIL only; each element's own attributes are its resting state (the still copy)
def _an(attr, vals, dur, begin=0, kt=None):
    k = f' keyTimes="{kt}"' if kt else ''
    return f'<animate attributeName="{attr}" values="{vals}"{k} dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
def _tf(typ, vals, dur, begin=0, kt=None):
    k = f' keyTimes="{kt}"' if kt else ''
    return f'<animateTransform attributeName="transform" type="{typ}" values="{vals}"{k} dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
def twinkle(n, y0, y1, seed, x0=460):  # a few stars that breathe, kept off the title at the left
    r=random.Random(seed)
    return ''.join(f'<circle cx="{r.randint(x0,1590)}" cy="{r.randint(y0,y1)}" r="1.7" fill="#fff" opacity=".85">{_an("opacity",".85;.15;.85",r.choice([2.5,3,3.5,4]),-r.randint(0,30)/10)}</circle>' for _ in range(n))
def wrap(h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {h}" preserveAspectRatio="xMidYMid slice">{body}</svg>'

# ------------------------------------------------------------- vistas
def v_sales(n):  # liftoff over the ocean
    o=[sky(V,n)]; o.append(stars(80 if n else 20,1600,0,120,1))
    sea="#1d4f8f" if not n else "#07122a"; o.append(f'<rect x="0" y="190" width="1600" height="50" fill="{sea}"/>')
    o.append('<g>'+''.join(f'<path d="M{x} 198 q22 -8 45 0 t45 0" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="2"/>' for x in range(0,1690,90))+_tf("translate","0 0;-90 0",6)+'</g>')
    o.append(f'<rect x="0" y="176" width="1600" height="16" fill="{"#5c7a63" if not n else "#101a30"}"/>')
    for cx,cy,rx,ry,c,d in [(560,186,260,34,"e9e4dc",5),(380,196,160,28,"dcd6cc",6),(760,196,170,26,"dcd6cc",7)]:  # the smoke billows
        o.append(f'<g transform="translate({cx} {cy})"><ellipse rx="{rx}" ry="{ry}" fill="#{c}" opacity=".8">{_an("rx",f"{rx};{rx*1.07:.0f};{rx}",d)}{_an("ry",f"{ry};{ry*1.2:.0f};{ry}",d)}</ellipse></g>')
    o.append('<g>'+rocket(560, 120, 120, n, flame=True, scale=1.6)+'<path d="M553 126 Q560 200 567 126 Z" fill="#fff" opacity=".7">'+_an("d","M553 126 Q560 200 567 126 Z;M552 126 Q560 222 568 126 Z;M554 126 Q560 186 566 126 Z;M553 126 Q560 200 567 126 Z",2)+'</path>'+_tf("translate","0 0;0 -3;0 0",3)+'</g>')
    if n: o.append('<circle cx="560" cy="150" r="200" fill="url(#gl)"/>')
    o.append(f'<rect x="700" y="60" width="14" height="116" fill="{"#b43a2a" if not n else "#7a2222"}"/>')
    o.append(dish(1300, 150, 50, n)); o.append(dish(1440, 160, 36, n, -20))
    o.append(f'<text x="1120" y="150" font-family="monospace" font-weight="bold" font-size="30" fill="{"#17306e" if not n else "#ff8a5b"}" opacity=".9">LIFTOFF</text>')
    if n: o.append(twinkle(6,10,110,51))
    return wrap(V,''.join(o))
def v_messages(n):  # the comms array
    o=[sky(V,n,day=("#5a3a7a","#e07a5f","#f6c48a"))]; o.append(stars(90 if n else 10,1600,0,110,2))
    o.append(ground(V,170,n,"#5d5a6e" if not n else "#161a2e"))
    for i,(x,r) in enumerate([(200,80),(520,110),(880,95),(1240,120),(1500,70)]):
        o.append(dish(x,170,r,n,-35+i*5))
        cx,cy=x+int(r*.55),170-int(r*.85)
        for k in range(1,4): o.append(f'<path d="M{cx-14*k} {cy} A{14*k} {14*k} 0 0 1 {cx+14*k} {cy}" fill="none" stroke="#fff" stroke-opacity="{.55-.12*k}" stroke-width="2.5" transform="rotate(-30 {cx} {cy})">'+(_an("stroke-opacity",f"{.55-.12*k:.2f};.75;{.55-.12*k:.2f};.05;{.55-.12*k:.2f}",3,i*.5+k*.25) if x>400 else '')+'</path>')
    o.append('<g><g transform="translate(1040 50) rotate(-15)"><rect x="-10" y="-7" width="20" height="14" fill="#cfd6e4"/><rect x="-46" y="-4" width="32" height="8" fill="#3f7fe0"/><rect x="14" y="-4" width="32" height="8" fill="#3f7fe0"/></g>'
             '<circle cx="1040" cy="50" r="5" fill="#ff5a36"/><circle cx="1040" cy="50" r="12" fill="#ff5a36" opacity=".3">'+_an("opacity",".3;0;.6;.3",2)+'</circle>'+_tf("translate","0 0;-40 8;0 0",12)+'</g>')
    if n: o.append(twinkle(6,8,100,52))
    return wrap(V,''.join(o))
def v_coaching(n):  # mission control, the debrief
    wall="#1b2236" if n else "#2c3a5a"; o=[f'<rect width="1600" height="{V}" fill="{wall}"/>']
    o.append(f'<rect x="300" y="24" width="1000" height="110" rx="6" fill="#0a1020" stroke="#4a5a80" stroke-width="3"/>')
    o.append(earth(560, 80, 42, True))
    o.append('<path d="M600 80 Q800 10 1180 60" fill="none" stroke="#5ee07a" stroke-width="3" stroke-dasharray="10 8">'+_an("stroke-dashoffset","0;-36",2)+'</path><circle r="6" fill="#d8ffe0" opacity="0"><animateMotion path="M600 80 Q800 10 1180 60" dur="4s" repeatCount="indefinite"/>'+_an("opacity","0;1;1;0","4",kt="0;.1;.9;1")+'</circle><circle cx="1180" cy="60" r="7" fill="#5ee07a"/><text x="1200" y="66" font-family="monospace" font-size="18" fill="#5ee07a">REPLAY</text>')
    o.append('<text x="330" y="124" font-family="monospace" font-size="16" fill="#8fb0ff">T+00:04:12  ·  CALL 17 OF 31  ·  FLOW: FOLLOW-UP</text>')
    for i,x in enumerate(range(120,1500,170)):
        o.append(f'<rect x="{x}" y="150" width="130" height="60" rx="4" fill="{"#2f3b5a" if not n else "#232c48"}"/><rect x="{x+10}" y="156" width="110" height="34" rx="3" fill="{["#5ee07a","#ffb347","#8fb0ff"][i%3]}" opacity=".55">{_an("opacity",".55;.85;.55",3+i%3,i*.4) if x>420 else ""}</rect><circle cx="{x+65}" cy="226" r="10" fill="#0a1020"/>')
    return wrap(V,''.join(o))
def v_roleplay(n):  # the simulator
    o=[f'<rect width="1600" height="{V}" fill="{"#283149" if not n else "#141a2c"}"/>']
    o.append('<rect x="0" y="200" width="1600" height="40" fill="#1a2238"/>')
    o.append(f'<rect x="420" y="40" width="760" height="170" rx="24" fill="{"#dfe4ee" if not n else "#8e98b0"}"/><rect x="470" y="70" width="660" height="80" rx="12" fill="#0a1020"/>')
    o.append('<path d="M500 110 Q800 40 1100 110" fill="none" stroke="#5ee07a" stroke-width="3">'+_an("d","M500 110 Q800 40 1100 110;M500 110 Q800 72 1100 110;M500 110 Q800 40 1100 110",4)+'</path><circle cx="800" cy="75" r="8" fill="#ffb347">'+_an("cy","75;91;75",4)+'</circle>')
    o.append('<text x="800" y="140" text-anchor="middle" font-family="monospace" font-size="20" fill="#8fb0ff">SIM · PROSPECT ON THE LINE</text>')
    for x in [500,560,620,980,1040,1100]: o.append(f'<circle cx="{x}" cy="180" r="9" fill="{"#ff5a36" if x in (620,1100) else "#5ee07a"}">{_an("opacity","1;.25;1",2,x%7*.3) if x in (620,1100) else ""}</circle>')
    o.append(f'<text x="200" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="40" fill="#ffb347" opacity=".9">SIM</text><text x="1400" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="40" fill="#ffb347" opacity=".9">GO</text>')
    o.append('<g>'+astronaut(1300, 120, .9, n)+_tf("translate","0 0;0 -6;0 0",4)+'</g>'); o.append(astronaut(300, 120, .9, n, flip=True))
    return wrap(V,''.join(o))
def v_rphistory(n):  # the flight recorder
    o=[f'<rect width="1600" height="{V}" fill="{"#2a2f3c" if not n else "#12151f"}"/>']
    o.append('<rect x="200" y="30" width="1200" height="180" rx="10" fill="#f06a1a"/><rect x="230" y="60" width="1140" height="120" rx="6" fill="#1a1d26"/>')
    for i,x in enumerate([330,1270]): o.append(f'<circle cx="{x}" cy="120" r="46" fill="#3a3f4c"/><circle cx="{x}" cy="120" r="30" fill="#0f1116"/><path d="M{x-26} 120 h52 M{x} 94 v52" stroke="#3a3f4c" stroke-width="5">{_tf("rotate",f"0 {x} 120;360 {x} 120",8)}</path><circle cx="{x}" cy="120" r="8" fill="#8fb0ff"/>')
    o.append('<path d="M420 120 ' + ' '.join(f'L{420+i*12} {120+(-1)**i*random.Random(i).randint(4,40)}' for i in range(1,64)) + '" fill="none" stroke="#5ee07a" stroke-width="2"/>')
    o.append('<rect x="1176" y="70" width="3" height="100" fill="#ffb347" opacity=".9">'+_tf("translate","-640 0;0 0",8)+'</rect><circle cx="1350" cy="45" r="6" fill="#ff3b30">'+_an("opacity","1;.15;1",2)+'</circle>')
    o.append('<text x="800" y="200" text-anchor="middle" font-family="monospace" font-size="16" fill="#fff" opacity=".9">FLIGHT RECORDER · EVERY SESSION, EVERY WORD</text>')
    return wrap(V,''.join(o))
def v_training(n):  # rover course on the moon
    o=[sky(V,n,day=("#1b2340","#3a4a7a","#8fa0c8"))]; o.append(stars(120,1600,0,110,4))
    o.append(earth(1380, 60, 46, n)); o.append(ground(V,130,n,"#9aa3b5" if not n else "#1c2240")); o.append(craters(10,140,230,7,n))
    o.append('<path d="M60 230 Q300 150 520 190 T980 160 T1540 200" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-dasharray="14 10"/>')
    for x,y in [(300,152),(760,172),(1240,170)]:
        o.append(f'<rect x="{x}" y="{y-40}" width="4" height="44" fill="#eee"/><path d="M{x+4} {y-40} l30 8 l-30 8 z" fill="#e2552b">{_an("d",f"M{x+4} {y-40} l30 8 l-30 8 z;M{x+4} {y-40} l27 11 l-27 5 z;M{x+4} {y-40} l30 8 l-30 8 z",2,x%5*.3) if x>420 else ""}</path>')
    rx,ry=560,186; o.append(f'<rect x="{rx-50}" y="{ry-30}" width="100" height="26" rx="6" fill="#cfd6e2"/><circle cx="{rx-30}" cy="{ry}" r="14" fill="#2b3140"/><circle cx="{rx+30}" cy="{ry}" r="14" fill="#2b3140"/><rect x="{rx-20}" y="{ry-60}" width="40" height="30" rx="4" fill="#8ecdf2"/><line x1="{rx+40}" y1="{ry-30}" x2="{rx+60}" y2="{ry-70}" stroke="#cfd6e2" stroke-width="3"/>')
    o[-1] = '<g>'+o[-1]+_tf("translate","0 0;360 -14",12)+_an("opacity","0;1;1;0",12,kt="0;.06;.92;1")+'</g>'
    if n: o.append(twinkle(6,8,100,54))
    return wrap(V,''.join(o))
def v_map(n, athena=False):  # the flight plan, plotted across a galaxy (Frank, 2026-10-05: "make it look like one")
    route = "#ff7a3d" if not athena else "#3fd68a"
    deep = ("#070b22", "#141a4a", "#2a1d5c") if not n else ("#03040e", "#0a0d2a", "#1a1040")
    r = random.Random(77 + athena)
    o = [f'<defs><radialGradient id="mbg" cx=".55" cy=".45" r=".9"><stop offset="0" stop-color="{deep[2]}"/><stop offset=".55" stop-color="{deep[1]}"/><stop offset="1" stop-color="{deep[0]}"/></radialGradient>'
         '<filter id="neb" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="28"/></filter>'
         '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
         '<radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6dc"/><stop offset=".25" stop-color="#ffd9a0" stop-opacity=".9"/><stop offset=".6" stop-color="#b48cff" stop-opacity=".35"/><stop offset="1" stop-color="#b48cff" stop-opacity="0"/></radialGradient></defs>'
         f'<rect width="1600" height="{V}" fill="url(#mbg)"/>']
    # nebula clouds
    for cx, cy, rx, ry, c, op in [(420, 60, 300, 70, "#7b3fd1", .55), (900, 190, 380, 60, "#1f8fd1", .45), (1250, 70, 260, 80, "#d13f8f", .4), (150, 200, 220, 50, "#3fd1c4", .3)]:
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{op}" filter="url(#neb)"/>')
    # the Milky Way band: a dense river of stars on a slant
    o.append('<g fill="#fff">')
    for _ in range(190):
        t = r.random(); x = t * 1600; y = 210 - t * 170 + r.gauss(0, 22)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.choice([.5, .7, .9, 1.2])}" opacity="{r.choice([.25, .4, .6, .85])}"/>')
    o.append('</g>' + stars(70, 1600, 0, V, 41 + athena))
    for _ in range(9):  # bright stars with a glint
        x, y = r.randint(40, 1560), r.randint(10, V - 10)
        o.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff"/><path d="M{x - 8} {y} H{x + 8} M{x} {y - 8} V{y + 8}" stroke="#fff" stroke-opacity=".6" stroke-width="1"/>')
    # a spiral galaxy far off
    gx, gy = 1460, 52
    o.append(f'<g transform="translate({gx} {gy}) rotate(-25)"><ellipse rx="70" ry="22" fill="url(#core)"/>'
             '<path d="M-60 0 Q-30 -26 0 -6 Q30 14 60 -4 M60 0 Q30 26 0 6 Q-30 -14 -60 4" fill="none" stroke="#d9c8ff" stroke-opacity=".55" stroke-width="5" filter="url(#soft)"/>'
             '<ellipse rx="12" ry="6" fill="#fff8e6"/></g>')
    # home (Earth) and the destination (a ringed planet)
    o.append(earth(140, 92, 46, n))
    o.append('<g transform="translate(1340 128)"><circle r="40" fill="#e0a25a"/><path d="M-40 -6 A40 40 0 0 1 40 -6 L40 2 A40 40 0 0 0 -40 2 Z" fill="#c97f3a" opacity=".7"/>'
             '<path d="M-36 12 A40 40 0 0 0 36 12" fill="none" stroke="#f3cf9a" stroke-width="5" opacity=".7"/>'
             '<ellipse rx="70" ry="14" fill="none" stroke="#f6e2b8" stroke-width="5" opacity=".85" transform="rotate(-12)"/></g>')
    # the route, glowing, with its four stops
    path = "M188 104 C420 40 560 170 760 132 S1060 70 1290 118"
    o.append(f'<path d="{path}" fill="none" stroke="{route}" stroke-width="10" stroke-opacity=".25" filter="url(#soft)"/>'
             f'<path d="{path}" fill="none" stroke="{route}" stroke-width="3.5" stroke-dasharray="12 8">{_an("stroke-dashoffset","0;-40",3)}</path>'
             f'<circle r="6" fill="#fff" stroke="{route}" stroke-width="3" opacity="0"><animateMotion path="{path}" dur="10s" repeatCount="indefinite"/>{_an("opacity","0;1;1;0",10,kt="0;.05;.95;1")}</circle>')
    steps = ["Listen", "Understand", "Handle", "Follow up"] if athena else ["Dial", "Discovery", "Quote", "Close"]
    for (x, y, dy), t in zip([(360, 82, -18), (620, 140, 34), (900, 112, -18), (1150, 96, -18)], steps):
        o.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{route}" opacity=".3">{_an("r","12;22;12",3,x/400)}</circle><circle cx="{x}" cy="{y}" r="8" fill="{route}" stroke="#fff" stroke-width="2.5"/>'
                 f'<text x="{x}" y="{y + dy}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="17" fill="#fff" stroke="#070b22" stroke-width="4" paint-order="stroke">{t}</text>')
    return wrap(V, ''.join(o))
def v_service(n):  # the station
    o=[sky(V,n,day=("#0b1a3a","#17306e","#2a4a8a"))]; o.append(stars(140,1600,0,V,8))
    o.append(earth(800, 420, 300, n))
    sx,sy=800,100; pan="#2a4fb0" if not n else "#1b3a8a"
    o.append('<g>'); o.append(f'<rect x="{sx-240}" y="{sy-4}" width="480" height="8" fill="#8d98b0"/>')
    for x in [sx-230, sx-120, sx+40, sx+150]: o.append(f'<rect x="{x}" y="{sy-40}" width="80" height="80" fill="{pan}" stroke="#9cc0ff" stroke-width="2"/><line x1="{x}" y1="{sy}" x2="{x+80}" y2="{sy}" stroke="#9cc0ff" stroke-width="1.5"/>')
    o.append(f'<rect x="{sx-60}" y="{sy-18}" width="120" height="36" rx="18" fill="#e4e8f0"/><rect x="{sx-20}" y="{sy+18}" width="40" height="30" rx="8" fill="#cfd6e2"/><circle cx="{sx}" cy="{sy}" r="7" fill="#8ecdf2"/>')
    o.append(f'<circle cx="{sx+244}" cy="{sy}" r="5" fill="#ff5a36"><animate attributeName="opacity" values="1;.1;1" dur="2s" repeatCount="indefinite"/></circle><circle cx="{sx-244}" cy="{sy}" r="5" fill="#5ee07a">{_an("opacity","1;.1;1",2,1)}</circle>'+_tf("translate","0 0;0 -6;0 0",8)+'</g>')
    o.append(twinkle(8,10,200,55))
    o.append(f'<text x="{sx}" y="226" text-anchor="middle" font-family="monospace" font-size="16" fill="#fff" opacity=".85">POLICY STATION · KEEPING THE BOOK</text>')
    return wrap(V,''.join(o))
def v_renewals(n):  # the orbit: what came back
    o=[sky(V,n,day=("#101c44","#2a3f80","#5d79b8"))]; o.append(stars(140,1600,0,V,9))
    o.append(earth(800, 130, 70, n))
    for rx,ry,rot in [(300,90,-15),(420,120,10)]: o.append(f'<ellipse cx="800" cy="130" rx="{rx}" ry="{ry}" fill="none" stroke="#9cc0ff" stroke-opacity=".6" stroke-width="2" stroke-dasharray="10 8" transform="rotate({rot} 800 130)"/>')
    sat='<rect x="-8" y="-6" width="16" height="12" fill="#cfd6e4"/><rect x="-32" y="-3" width="22" height="6" fill="#3f7fe0"/><rect x="10" y="-3" width="22" height="6" fill="#3f7fe0"/>'
    for rx,ry,rot,d in [(300,90,-15,10),(420,120,10,12)]:
        o.append(f'<g transform="rotate({rot} 800 130)"><g transform="translate({800+rx} 130)">{sat}<animateMotion path="M0 0 a{rx} {ry} 0 1 1 -{2*rx} 0 a{rx} {ry} 0 1 1 {2*rx} 0" dur="{d}s" repeatCount="indefinite"/></g></g>')
    for x,y in [(1180,70)]: o.append(f'<g transform="translate({x} {y})"><rect x="-8" y="-6" width="16" height="12" fill="#cfd6e4"/><rect x="-32" y="-3" width="22" height="6" fill="#3f7fe0"/><rect x="10" y="-3" width="22" height="6" fill="#3f7fe0"/></g>')
    o.append('<g><path d="M1200 40 l-20 40 l-16 -30 z" fill="#5ee07a"/><text x="1240" y="60" font-family="monospace" font-size="16" fill="#5ee07a">RETURNED</text>'+_an("opacity","1;.45;1",3)+'</g>')
    o.append(f'<text x="800" y="226" text-anchor="middle" font-family="monospace" font-size="15" fill="#fff" opacity=".8">EVERY ORBIT COMES BACK AROUND</text>')
    return wrap(V,''.join(o))
def v_commercial(n):  # the moon base
    o=[sky(V,n,day=("#0b1230","#1a2550","#2a3a6a"))]; o.append(stars(120,1600,0,110,10))
    o.append(earth(260, 60, 44, n)); o.append(ground(V,150,n,"#aab3c4" if not n else "#1c2240")); o.append(craters(8,160,230,12,n))
    dome="#dfe5ee" if not n else "#8d98b0"; win="#ffd27a"
    for x,r in [(700,70),(860,50),(1000,60),(560,40)]:
        o.append(f'<path d="M{x-r} 160 A{r} {r} 0 0 1 {x+r} 160 Z" fill="{dome}"/><path d="M{x-r*.5} 150 A{r*.5} {r*.5} 0 0 1 {x+r*.5} 150" fill="none" stroke="{win}" stroke-width="4" opacity=".9">{_an("opacity",".9;.4;.9",3+r%4,x%9*.3)}</path>')
    o.append('<rect x="600" y="140" width="400" height="12" fill="#8d98b0"/>')
    o.append(f'<rect x="1300" y="60" width="6" height="100" fill="#8d98b0"/><path d="M1306 60 l70 14 l-70 14 z" fill="#8f5be8">{_an("d","M1306 60 l70 14 l-70 14 z;M1306 60 l64 19 l-64 9 z;M1306 60 l70 14 l-70 14 z",2.5)}</path>')
    o.append('<g>'+astronaut(1180, 110, .8, n)+_tf("translate","0 0;0 0;0 -14;0 0",3,kt="0;.4;.7;1")+'</g>')
    if n: o.append(twinkle(6,8,100,56))
    o.append(f'<text x="800" y="210" text-anchor="middle" font-family="monospace" font-size="16" fill="#fff" opacity=".85">MOON BASE · CERBERUS</text>')
    return wrap(V,''.join(o))
VISTA_FNS = {"sales":v_sales,"messages":v_messages,"coaching":v_coaching,"roleplay":v_roleplay,"rphistory":v_rphistory,"training":v_training,
             "blueprint":lambda n:v_map(n,False),"athenamap":lambda n:v_map(n,True),"service":v_service,"renewals":v_renewals,"commercial":v_commercial}
VISTA_LINES = {"sales": ["Sales", "liftoff: premium leaving the pad"], "messages": ["Texts & Emails", "the comms array: every signal answered"], "coaching": ["Coaching", "mission control: every call, replayed"],
  "roleplay": ["Role Play", "the simulator"], "rphistory": ["Session History", "the flight recorder"], "training": ["Training", "the rover course"],
  "blueprint": ["Apollo's Road Map", "the flight plan, in plain words"], "athenamap": ["Athena's Road Map", "the service flight plan, in plain words"],
  "service": ["Service Digest", "the station: keeping the book"], "renewals": ["Renewals", "the orbit: what came back"], "commercial": ["Commercial Center", "the moon base: Cerberus's book"]}

# ------------------------------------------------------------- outcome strips (1600x160; the visible band is the middle ~70)
S=160
def s_sold(n):   # liftoff, confetti stars
    o=[sky(S,n,day=("#2b4fa8","#5aa0e6","#bfe0f5"))]; o.append(stars(60,1600,0,S,21,(0.6,0.9)))
    o.append(rocket(800, 118, 90, n, flame=True, scale=1.2)); o.append('<circle cx="800" cy="100" r="160" fill="url(#gl)"/>')
    r=random.Random(5)
    for _ in range(40): o.append(f'<rect x="{r.randint(0,1600)}" y="{r.randint(30,130)}" width="6" height="10" fill="{r.choice(["#ffd27a","#5ee07a","#ff5a36","#8fb0ff"])}" transform="rotate({r.randint(0,90)} 800 80)"/>')
    o.append('<text x="120" y="92" font-family="monospace" font-weight="bold" font-size="30" fill="#fff">GO FOR LAUNCH</text>')
    return wrap(S,''.join(o))
def s_open(n):   # holding on the pad, the clock running
    o=[sky(S,n,day=("#3b2a5a","#e07a5f","#f6c48a"))]; o.append(stars(40,1600,0,80,22))
    o.append(f'<rect x="0" y="126" width="1600" height="34" fill="{"#5c7a63" if not n else "#101a30"}"/>')
    o.append(rocket(520, 126, 80, n, scale=1.1)); o.append(f'<rect x="560" y="40" width="10" height="86" fill="{"#b43a2a" if not n else "#7a2222"}"/>')
    o.append('<text x="210" y="91" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="26" fill="#ffb347">T-00:02:00</text>')
    o.append('<text x="330" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".9">HOLDING · NEXT WINDOW SET</text>')
    return wrap(S,''.join(o))
def s_lost(n):   # the capsule drifting down, grey dusk
    o=[sky(S,n,day=("#55596a","#8a8e9c","#b8bcc6"),nt=("#0a0c14","#1a1d28","#2a2d3a"))]
    o.append('<path d="M700 30 Q800 10 900 30 L860 70 L740 70 Z" fill="#e2552b" opacity=".85"/><path d="M700 30 Q800 10 900 30" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2"/>')
    for x in [745,800,855]: o.append(f'<line x1="{x}" y1="68" x2="800" y2="106" stroke="#d9dde6" stroke-width="1.5"/>')
    o.append('<path d="M780 104 L820 104 L826 122 L774 122 Z" fill="#cfd6e2"/>')
    o.append('<path d="M1000 120 q40 -20 80 0 t80 0 t80 0" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="2"/>')
    o.append('<text x="120" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".8">SPLASHDOWN · MISSION OVER</text>')
    return wrap(S,''.join(o))
def s_dead(n):   # scrubbed: red light, no rocket on the pad
    o=[sky(S,n,day=("#5a3a3a","#9a6a5a","#c9a08a"),nt=("#120a0a","#241212","#3a1c1c"))]
    o.append(f'<rect x="0" y="126" width="1600" height="34" fill="{"#6b6f7a" if not n else "#1a1c28"}"/>')
    o.append(f'<rect x="560" y="40" width="10" height="86" fill="{"#8a2a1e" if not n else "#5a1a14"}"/><rect x="480" y="112" width="200" height="14" fill="{"#8e9aa8" if not n else "#38415a"}"/>')
    o.append('<circle cx="565" cy="34" r="8" fill="#ff3b3b"/><circle cx="565" cy="34" r="18" fill="#ff3b3b" opacity=".3"/>')
    o.append('<text x="195" y="91" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="28" fill="#ff5a36">SCRUB</text>')
    o.append('<text x="300" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".85">NO LAUNCH TODAY</text>')
    return wrap(S,''.join(o))
def s_reached(n):  # two astronauts talking
    o=[sky(S,n,day=("#1b2340","#3a4a7a","#8fa0c8"))]; o.append(stars(60,1600,0,S,23))
    o.append(f'<rect x="0" y="130" width="1600" height="30" fill="{"#9aa3b5" if not n else "#1c2240"}"/>')
    o.append(astronaut(720, 76, .6, n)); o.append(astronaut(880, 76, .6, n, flip=True))
    o.append('<path d="M750 56 q50 -24 100 0" fill="none" stroke="#5ee07a" stroke-width="3" stroke-dasharray="6 6"/>')
    o.append('<text x="120" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".9">COMMS OPEN · LOUD AND CLEAR</text>')
    return wrap(S,''.join(o))
def s_live_noq(n):  # reached, no quote: on a tether, drifting
    o=[sky(S,n,day=("#101c44","#2a3f80","#5d79b8"))]; o.append(stars(80,1600,0,S,24))
    o.append('<path d="M520 110 Q680 130 780 84" fill="none" stroke="#d9dde6" stroke-width="2"/>')
    o.append(astronaut(800, 70, .55, n)); o.append('<text x="120" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".85">ON THE TETHER · NO QUOTE YET</text>')
    return wrap(S,''.join(o))
def s_vm(n):  # voicemail: a probe asleep past a dark planet
    o=[sky(S,n,day=("#1a1a3a","#2a2a5a","#4a4a7a"),nt=("#04060f","#0a0f24","#141a38"))]; o.append(stars(90,1600,0,S,25))
    o.append('<circle cx="560" cy="80" r="40" fill="#3a3f6a"/><ellipse cx="560" cy="80" rx="70" ry="12" fill="none" stroke="#9c9ce0" stroke-width="4" transform="rotate(-18 560 80)"/>')
    o.append('<g transform="translate(900 80)"><rect x="-14" y="-10" width="28" height="20" fill="#cfd6e4"/><rect x="-60" y="-5" width="44" height="10" fill="#3f7fe0"/><rect x="16" y="-5" width="44" height="10" fill="#3f7fe0"/><path d="M-6 -10 a16 16 0 0 1 12 0" fill="none" stroke="#8d98b0" stroke-width="3"/></g>')
    o.append('<text x="940" y="70" font-family="Arial, sans-serif" font-weight="bold" font-size="22" fill="#ffd27a">z</text><text x="960" y="58" font-family="Arial, sans-serif" font-weight="bold" font-size="28" fill="#ffd27a">z</text><text x="986" y="46" font-family="Arial, sans-serif" font-weight="bold" font-size="34" fill="#ffd27a">z</text>')
    o.append('<text x="120" y="92" font-family="monospace" font-size="20" fill="#fff" opacity=".8">NO SIGNAL · LEFT A MESSAGE</text>')
    return wrap(S,''.join(o))
STRIP_FNS = {"sold_on_call": s_sold, "quoted_call_open": s_open, "followup_open": s_open, "quoted_call_lost": s_lost, "followup_lost": s_lost,
             "dead_no_quote": s_dead, "live_quote_ok": s_reached, "live_no_quote": s_live_noq, "callback_no_contact": s_vm}
if __name__ == "__main__":
    import sys, os
    d=sys.argv[1]
    for k,f in VISTA_FNS.items():
        open(f'{d}/v_{k}_l.svg','w').write(f(False)); open(f'{d}/v_{k}_d.svg','w').write(f(True))
    for k,f in STRIP_FNS.items():
        open(f'{d}/s_{k}_l.svg','w').write(f(False)); open(f'{d}/s_{k}_d.svg','w').write(f(True))
    print("ok", sum(len(f(n)) for f in list(VISTA_FNS.values())+list(STRIP_FNS.values()) for n in (0,1)))

"""The Space world's Digest picture: one drawing, 1600x1700, split at 377 like the desert's."""
import random, urllib.parse
W,H,SPLIT=1600,1700,377
def enc(svg): return urllib.parse.quote(svg, safe="/:=,.;- '()")
def stars(a, n, y0, y1, seed):
    r=random.Random(seed)
    for _ in range(n):
        a(f'<circle cx="{r.randint(0,W)}" cy="{r.randint(y0,y1)}" r="{r.choice([0.6,0.8,1,1.3,1.7])}" fill="#fff" opacity="{r.choice([0.25,0.4,0.6,0.85])}"/>')
def scene(night):
    o=[]; a=o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice">')
    if night:
        a('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05070f"/><stop offset=".6" stop-color="#0c1330"/><stop offset="1" stop-color="#1c2a52"/></linearGradient>'
          '<radialGradient id="fl" cx=".5" cy=".3" r=".6"><stop offset="0" stop-color="#fff2c0" stop-opacity=".95"/><stop offset=".4" stop-color="#ffb347" stop-opacity=".7"/><stop offset="1" stop-color="#ff6a1a" stop-opacity="0"/></radialGradient>'
          '<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a" stop-opacity=".55"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
          '<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6d6" stop-opacity=".0"/><stop offset="1" stop-color="#fff6d6" stop-opacity=".22"/></linearGradient>'
          '<linearGradient id="mw" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8fa6ff" stop-opacity="0"/><stop offset=".5" stop-color="#c9d4ff" stop-opacity=".16"/><stop offset="1" stop-color="#8fa6ff" stop-opacity="0"/></linearGradient></defs>')
    else:
        a('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#17306e"/><stop offset=".5" stop-color="#3f7fd0"/><stop offset=".85" stop-color="#9ccbee"/><stop offset="1" stop-color="#f4d9b4"/></linearGradient>'
          '<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff" stop-opacity=".5"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>')
    a(f'<rect width="{W}" height="{SPLIT+40}" fill="url(#sky)"/>')
    if night:
        a(f'<path d="M-100 60 Q500 260 900 120 T1700 240 L1700 340 Q1100 160 700 300 T-100 160 Z" fill="url(#mw)"/>')
        stars(a, 260, 0, SPLIT, 3)
        # a few constellations
        for pts in [[(1180,60),(1220,88),(1270,80),(1300,120),(1340,110)],[(140,40),(190,70),(240,60),(260,110)],[(820,40),(860,30),(900,52),(940,44)]]:
            a('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+'" fill="none" stroke="#fff" stroke-opacity=".25" stroke-width="1"/>')
            for x,y in pts: a(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#fff" opacity=".9"/>')
        a('<circle cx="1420" cy="130" r="40" fill="#f2ecd8"/><circle cx="1432" cy="120" r="36" fill="#070b19"/>')
        # satellite blinking
        a('<g transform="translate(600 150) rotate(-20)"><rect x="-6" y="-4" width="12" height="8" fill="#cfd6e4"/><rect x="-30" y="-2" width="20" height="4" fill="#4f7fe0"/><rect x="10" y="-2" width="20" height="4" fill="#4f7fe0"/></g>')
    else:
        stars(a, 30, 0, 120, 5)
        a('<circle cx="1420" cy="120" r="34" fill="#fff" opacity=".55"/>')
        for x,y,w in [(200,150,260),(700,90,200),(1150,200,320)]:
            a(f'<ellipse cx="{x}" cy="{y}" rx="{w//2}" ry="10" fill="#fff" opacity=".35"/><ellipse cx="{x+40}" cy="{y-8}" rx="{w//3}" ry="9" fill="#fff" opacity=".3"/>')
        # a contrail from an earlier launch
        a('<path d="M560 330 Q600 200 700 120 T940 20" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="10" stroke-linecap="round"/><path d="M560 330 Q600 200 700 120 T940 20" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="22" stroke-linecap="round"/>')
        # jet / plane
        a('<path d="M1040 70 l-22 6 l-6 -4 l10 -3 z M1030 64 l-6 -10 l4 0 l8 8 z" fill="#f4f4f4"/>')
    # ---- ground from the horizon down ----
    g1="#0d1526" if night else "#5c7a63"; g2="#121b30" if night else "#6f8c6a"; sea="#0a1226" if night else "#2f6fa8"
    a(f'<rect x="0" y="{SPLIT}" width="{W}" height="{H-SPLIT}" fill="{g1}"/>')
    # the sea line far right (the cape)
    a(f'<path d="M900 {SPLIT} L1600 {SPLIT} L1600 {SPLIT+54} Q1250 {SPLIT+66} 900 {SPLIT+40} Z" fill="{sea}"/><path d="M900 {SPLIT} L1600 {SPLIT} L1600 {SPLIT+8} L900 {SPLIT+8} Z" fill="#fff" opacity=".18"/>')
    # scrub / flats
    a(f'<path d="M0 {SPLIT+60} Q400 {SPLIT+40} 800 {SPLIT+70} T1600 {SPLIT+90} L1600 {H} L0 {H} Z" fill="{g2}"/>')
    # crawlerway: two gravel lanes running down to the podium
    cw="#2a3550" if night else "#b9b2a0"; cw2="#1c2540" if night else "#9d9684"
    a(f'<path d="M760 {SPLIT+30} L840 {SPLIT+30} L1040 {H} L560 {H} Z" fill="{cw}"/><path d="M795 {SPLIT+30} L805 {SPLIT+30} L830 {H} L770 {H} Z" fill="{g2}"/>')
    for y in range(SPLIT+60, H, 60):
        t=(y-SPLIT)/(H-SPLIT); hw=40+200*t
        a(f'<line x1="{800-hw:.0f}" y1="{y}" x2="{800+hw:.0f}" y2="{y}" stroke="{cw2}" stroke-width="1.5" opacity=".6"/>')
    # ---- launch complex, left: rocket on the pad with its service tower ----
    rx=300; padY=SPLIT+120
    # pad deck
    deck="#38415a" if night else "#8e9aa8"; deck2="#2b3348" if night else "#6f7b8a"
    a(f'<path d="M{rx-220} {padY} L{rx+260} {padY} L{rx+300} {padY+90} L{rx-260} {padY+90} Z" fill="{deck}"/><rect x="{rx-260}" y="{padY+90}" width="560" height="18" fill="{deck2}"/>')
    # flame trench
    a(f'<rect x="{rx-70}" y="{padY+30}" width="140" height="40" rx="6" fill="{"#111728" if night else "#4a5563"}"/>')
    # service tower (gantry)
    tw="#7a2222" if night else "#b43a2a"; tw2="#4d1515" if night else "#8a2a1e"
    tx=rx+120; top=70
    a(f'<rect x="{tx}" y="{top}" width="34" height="{padY-top}" fill="{tw}"/>')
    for y in range(top+10, padY, 36):
        a(f'<line x1="{tx}" y1="{y}" x2="{tx+34}" y2="{y+28}" stroke="{tw2}" stroke-width="3"/><line x1="{tx+34}" y1="{y}" x2="{tx}" y2="{y+28}" stroke="{tw2}" stroke-width="3"/>')
    # swing arms to the rocket
    for y in [130,260,400]:
        a(f'<rect x="{rx+40}" y="{y}" width="{tx-rx-40}" height="10" fill="{tw2}"/>')
    # lightning mast
    a(f'<rect x="{tx+14}" y="{top-60}" width="6" height="60" fill="{tw2}"/>')
    # rocket
    body="#e9edf3" if not night else "#cfd6e2"; stripe="#e2552b"; dark="#2b3140"
    a(f'<rect x="{rx-40}" y="110" width="80" height="{padY-120}" rx="6" fill="{body}"/>')
    a(f'<path d="M{rx-40} 120 Q{rx} -10 {rx+40} 120 Z" fill="{body}"/><path d="M{rx-40} 120 Q{rx} 30 {rx+40} 120 Z" fill="{stripe}" opacity=".9"/>')
    a(f'<rect x="{rx-40}" y="250" width="80" height="26" fill="{stripe}"/><rect x="{rx-40}" y="{padY-200}" width="80" height="14" fill="{dark}"/>')
    a(f'<text x="{rx}" y="{padY-110}" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="34" fill="{dark}" transform="rotate(-90 {rx} {padY-110})" letter-spacing="4">INSURED</text>')
    # fins and engines
    a(f'<path d="M{rx-40} {padY-80} L{rx-80} {padY-10} L{rx-40} {padY-10} Z M{rx+40} {padY-80} L{rx+80} {padY-10} L{rx+40} {padY-10} Z" fill="{stripe}"/>')
    for ex in [rx-26, rx, rx+26]:
        a(f'<path d="M{ex-10} {padY-12} L{ex+10} {padY-12} L{ex+14} {padY+6} L{ex-14} {padY+6} Z" fill="{dark}"/>')
    if night:
        # ignition: flame, smoke, the pad lit
        a(f'<ellipse cx="{rx}" cy="{padY+60}" rx="150" ry="70" fill="#d8d2c8" opacity=".55"/><ellipse cx="{rx-120}" cy="{padY+80}" rx="130" ry="50" fill="#cfc8bd" opacity=".45"/><ellipse cx="{rx+140}" cy="{padY+85}" rx="150" ry="55" fill="#cfc8bd" opacity=".45"/>')
        a(f'<path d="M{rx-40} {padY} Q{rx} {padY+220} {rx+40} {padY} Z" fill="url(#fl)"/><path d="M{rx-22} {padY} Q{rx} {padY+150} {rx+22} {padY} Z" fill="#fff6c8" opacity=".9"/>')
        a(f'<circle cx="{rx}" cy="{padY}" r="320" fill="url(#glow)"/>')
        # floodlights on poles
        for px in [60, 640, 1180, 1500]:
            a(f'<rect x="{px-3}" y="{SPLIT+20}" width="6" height="140" fill="#3a4560"/><rect x="{px-16}" y="{SPLIT+14}" width="32" height="10" rx="3" fill="#aab4c8"/><path d="M{px-16} {SPLIT+24} L{px-120} {SPLIT+330} L{px+120} {SPLIT+330} L{px+16} {SPLIT+24} Z" fill="url(#beam)"/>')
        # beacons
        for bx,by in [(tx+17, top-62),(1360, SPLIT-60)]:
            a(f'<circle cx="{bx}" cy="{by}" r="4" fill="#ff3b3b"/><circle cx="{bx}" cy="{by}" r="10" fill="#ff3b3b" opacity=".3"/>')
    else:
        for px in [60, 640, 1180, 1500]:
            a(f'<rect x="{px-3}" y="{SPLIT+20}" width="6" height="140" fill="#7b869a"/><rect x="{px-16}" y="{SPLIT+14}" width="32" height="10" rx="3" fill="#aab4c8"/>')
    # ---- right: fuel spheres, water tower, the big hangar, a tracking dish ----
    wh="#dfe5ee" if not night else "#8e98ad"; wh2="#b7c1cf" if not night else "#5d6780"
    a(f'<circle cx="1120" cy="{SPLIT+140}" r="52" fill="{wh}"/><circle cx="1210" cy="{SPLIT+150}" r="42" fill="{wh}"/><rect x="1068" y="{SPLIT+190}" width="180" height="10" fill="{wh2}"/>')
    # water tower
    a(f'<rect x="1316" y="{SPLIT-20}" width="8" height="200" fill="{wh2}"/><rect x="1356" y="{SPLIT-20}" width="8" height="200" fill="{wh2}"/><rect x="1300" y="{SPLIT-70}" width="80" height="60" rx="10" fill="{wh}"/><path d="M1296 {SPLIT-70} L1340 {SPLIT-110} L1384 {SPLIT-70} Z" fill="{wh2}"/>')
    # hangar (the assembly building)
    hb="#5f6c80" if not night else "#232c42"; hb2="#4b5668" if not night else "#1a2234"
    a(f'<rect x="1420" y="{SPLIT-170}" width="180" height="300" fill="{hb}"/><rect x="1440" y="{SPLIT-130}" width="60" height="220" fill="{hb2}"/><rect x="1520" y="{SPLIT-110}" width="64" height="64" rx="32" fill="#e2552b"/><path d="M1532 {SPLIT-62} Q1552 {SPLIT-130} 1572 {SPLIT-62}" fill="none" stroke="#fff" stroke-width="5"/><rect x="1420" y="{SPLIT+100}" width="180" height="30" fill="{hb2}"/>')
    # tracking dish on the left flank
    dc="#c9d1dc" if not night else "#7f8aa3"
    a(f'<rect x="86" y="{SPLIT+330}" width="12" height="90" fill="{wh2}"/><g transform="rotate(-30 92 {SPLIT+330})"><path d="M22 {SPLIT+330} A70 70 0 0 1 162 {SPLIT+330} Z" fill="{dc}"/><path d="M22 {SPLIT+330} A70 70 0 0 1 162 {SPLIT+330}" fill="none" stroke="{wh2}" stroke-width="3"/><line x1="92" y1="{SPLIT+330}" x2="92" y2="{SPLIT+262}" stroke="{wh2}" stroke-width="3"/><circle cx="92" cy="{SPLIT+260}" r="6" fill="{wh2}"/></g>')
    # ---- the mission patch / podium pad at the end of the crawlerway ----
    pp="#2f3b5a" if night else "#aeb6c6"
    a(f'<ellipse cx="800" cy="{SPLIT+640}" rx="300" ry="80" fill="{pp}" opacity=".55"/>')
    # countdown clock by the road
    a(f'<rect x="1000" y="{SPLIT+300}" width="120" height="44" rx="4" fill="#111"/><text x="1060" y="{SPLIT+331}" text-anchor="middle" font-family="monospace" font-weight="bold" font-size="26" fill="#ff5a36">T-00:10</text><rect x="1056" y="{SPLIT+344}" width="8" height="40" fill="{wh2}"/>')
    # ground scrub
    sc="#15213a" if night else "#55724f"
    r=random.Random(11)
    for _ in range(50):
        x=r.randint(0,W); y=r.randint(SPLIT+100, H-60)
        if 560 < x < 1040 and y > SPLIT+30: continue
        a(f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(10,26)}" ry="{r.randint(4,9)}" fill="{sc}"/>')
    a('</svg>')
    return ''.join(o)
if __name__=="__main__":
    import sys
    open(sys.argv[1]+'/sky_light.svg','w').write(scene(False)); open(sys.argv[1]+'/sky_dark.svg','w').write(scene(True))
    print(len(scene(False)), len(scene(True)))

import space_skyline as _sk, space_scenes as _sc
KEY = "space"; NAME = "Space"
FONTS = "family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600;700"
DISPLAY = "'Space Grotesk', system-ui, sans-serif"; DW = 700; BODY = "'IBM Plex Sans', system-ui, sans-serif"
SKY_BG = (("#17306e", "#5c7a63"), ("#05070f", "#0d1526"))
LOOKS = [('mission', 'Mission Control', '--surface: #e9edf3; --surface-raised: #f7f9fc; --card2: #eef2f7; --chip: #dde4ee; --text-primary: #141c2b; --text-muted: #5b6a80; --text-secondary: #4a5a70; --grid: #dfe5ee; --border: #d6dde8; --border-strong: #b9c4d4; --accent: #e2552b; --accent-d: #b23f1a; --side: #0f1a33; --side2: #16244a; --sideInk: #d8e1f3; --brand: #e9edf3; --brand2: #ff9b6b; --rad: 10px;', '--surface: #0b1120; --surface-raised: #121a2e; --card2: #18223a; --chip: #202c48; --text-primary: #e6ecf7; --text-muted: #9aa8c2; --text-secondary: #b2bdd3; --grid: #202c48; --border: #243050; --border-strong: #30406a; --accent: #ff7a4d; --accent-d: #ffa17f; --side: #060a16; --side2: #0e1730; --sideInk: #d8e1f3; --brand: #e9edf3; --brand2: #ff9b6b;', ['#e9edf3', '#0f1a33', '#e2552b']), ('deepfield', 'Deep Field', '--surface: #ecebf5; --surface-raised: #faf9ff; --card2: #f1effa; --chip: #e2dff2; --text-primary: #1a1630; --text-muted: #665f85; --text-secondary: #534c73; --grid: #e3e0f0; --border: #dcd8ec; --border-strong: #c2bcdc; --accent: #6d4fd8; --accent-d: #4b32a8; --side: #1a1433; --side2: #251d4a; --sideInk: #e2dcf7; --brand: #ecebf5; --brand2: #b89cff; --rad: 14px;', '--surface: #0d0a1c; --surface-raised: #151129; --card2: #1c1736; --chip: #261f46; --text-primary: #ece8fb; --text-muted: #a79fc9; --text-secondary: #bcb4da; --grid: #261f46; --border: #2b2450; --border-strong: #3a3170; --accent: #9d84ff; --accent-d: #bba9ff; --side: #07051a; --side2: #130e2c; --sideInk: #e2dcf7; --brand: #ecebf5; --brand2: #b89cff;', ['#ecebf5', '#1a1433', '#6d4fd8']), ('mars', 'Mars', '--surface: #f3e6dc; --surface-raised: #fdf6f0; --card2: #f6ebe2; --chip: #ecd9cb; --text-primary: #2b1a12; --text-muted: #7a5c4c; --text-secondary: #664a3b; --grid: #ecdccf; --border: #e6d3c3; --border-strong: #d2b59f; --accent: #c2451e; --accent-d: #8f2f10; --side: #3a1a10; --side2: #4e2416; --sideInk: #f3dccb; --brand: #f3e6dc; --brand2: #ff9f6f; --rad: 12px;', '--surface: #1a0f0b; --surface-raised: #241611; --card2: #2e1c15; --chip: #3a251b; --text-primary: #f4e6dc; --text-muted: #b79a88; --text-secondary: #c9ad9b; --grid: #3a251b; --border: #40291f; --border-strong: #533526; --accent: #ff6a3a; --accent-d: #ff9a76; --side: #110906; --side2: #22120c; --sideInk: #f3dccb; --brand: #f3e6dc; --brand2: #ff9f6f;', ['#f3e6dc', '#3a1a10', '#c2451e'])]
def skyline(night): return _sk.scene(night)
PATTERN = ('<svg xmlns="http://www.w3.org/2000/svg" width="260" height="260" viewBox="0 0 260 260"><g fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" opacity=".07">'
           '<path d="M60 200 l0 -60 q10 -24 20 0 l0 60 z M60 185 l-12 14 M80 185 l12 14"/><circle cx="190" cy="70" r="10"/><ellipse cx="190" cy="70" rx="24" ry="7" transform="rotate(-20 190 70)"/>'
           '<path d="M120 230 l3 3 M20 40 l3 3 M230 200 l3 3 M150 120 l3 3"/><path d="M200 150 l10 0 M205 145 l0 10"/></g></svg>')
VMAP_INK = ("#17306e", "#cfe0ff")
def v_claims(n):  # after the storm: a repair crew on the station's damaged array
    o=[_sc.sky(240,n,day=("#0b1a3a","#17306e","#2a4a8a"))]; o.append(_sc.stars(120,1600,0,240,31))
    o.append(_sc.earth(1300, 420, 260, n))
    o.append('<g transform="translate(700 110) rotate(-8)"><rect x="-200" y="-4" width="400" height="8" fill="#8d98b0"/>'
             '<rect x="-190" y="-38" width="76" height="76" fill="#2a4fb0" stroke="#9cc0ff" stroke-width="2"/><rect x="-100" y="-38" width="76" height="76" fill="#2a4fb0" stroke="#9cc0ff" stroke-width="2"/>'
             '<path d="M30 -38 h76 v40 l-20 10 l-14 26 h-42 z" fill="#2a4fb0" stroke="#9cc0ff" stroke-width="2"/><path d="M60 -6 l10 8 l-6 10 l12 6" fill="none" stroke="#ffb347" stroke-width="3"/>'
             '<rect x="120" y="-38" width="76" height="76" fill="#2a4fb0" stroke="#9cc0ff" stroke-width="2" opacity=".5" stroke-dasharray="6 4"/></g>')
    for x,y,r in [(980,60,6),(1040,150,4),(1120,90,5),(1180,170,3)]: o.append(f'<rect x="{x}" y="{y}" width="{r*2}" height="{r}" fill="#9aa3b5" transform="rotate({x%40} {x} {y})"/>')
    o.append(_sc.astronaut(900, 90, .55, n))
    o.append('<path d="M870 80 Q800 40 760 100" fill="none" stroke="#d9dde6" stroke-width="2"/><circle cx="822" cy="102" r="7" fill="#fff6c8"/><circle cx="822" cy="102" r="16" fill="#fff6c8" opacity=".35"/>')
    o.append('<text x="800" y="226" text-anchor="middle" font-family="monospace" font-size="15" fill="#fff" opacity=".85">REPAIR CREW · AFTER THE DEBRIS STORM</text>')
    return _sc.wrap(240, ''.join(o))
VISTA_FNS = dict(_sc.VISTA_FNS, claims=v_claims)
VISTA_LINES = dict(_sc.VISTA_LINES, claims=["Claims", "the repair crew: after the storm"])
STRIP_FNS = _sc.STRIP_FNS

"""Apollo -- Frank's blue-grey brindle Cane Corso, whom the board's assistant is named after --
as a flat icon (viewBox 0 0 100 100): broad square head, high-set hanging ears, amber eyes,
the white bib and his gold chain (Frank, 2026-10-04: "this is my boy apollo ... can you make an
icon based on him?"). The board inlines `svg()` on the assistant's button and panel; rerun
`python3 design/apollo_icon.py` to print it after a change."""
import math
def dog(bg=None, tongue=True):
    G="#6b717c"; GL="#7c838e"; D="#3d4149"; M="#454952"; N="#202227"; W="#f3f0ea"; AMB="#e3b25e"; GOLD="#e9b93f"; GOLD2="#9c7216"
    o=[]
    if bg: o.append(f'<circle cx="50" cy="50" r="50" fill="{bg}"/>')
    # shoulders, chest and the white bib
    o.append(f'<path d="M12 100 C13 84 24 76 34 73 L66 73 C76 76 87 84 88 100 Z" fill="{D}"/>')
    o.append(f'<path d="M38 76 C40 86 45 94 50 100 C55 94 60 86 62 76 C56 79 44 79 38 76 Z" fill="{W}"/>')
    # ears: set high at the corners of the skull, hanging and folding forward
    o.append(f'<path d="M30 21 C22 20 15 25 13 33 C11 42 13 51 17 55 C20 57 24 53 25.5 46 C27 38 28 31 32 26 Z" fill="{D}"/><path d="M27 25 C21 29 18 37 18 46" fill="none" stroke="#2f3238" stroke-width="1" opacity=".6"/>')
    o.append(f'<path d="M70 21 C78 20 85 25 87 33 C89 42 87 51 83 55 C80 57 76 53 74.5 46 C73 38 72 31 68 26 Z" fill="{D}"/><path d="M73 25 C79 29 82 37 82 46" fill="none" stroke="#2f3238" stroke-width="1" opacity=".6"/>')
    # the broad, square head
    o.append(f'<path d="M24 28 C28 17 72 17 76 28 C80 38 80 52 76 61 C73 68 68 72 62 74 L38 74 C32 72 27 68 24 61 C20 52 20 38 24 28 Z" fill="{G}"/>')
    o.append(f'<path d="M30 22 C38 18 62 18 70 22 C64 21 36 21 30 22 Z" fill="{GL}"/>')
    # a soft furrow and brows (concerned, not angry)
    o.append(f'<path d="M50 24 L50 32" stroke="{D}" stroke-width="1.3" stroke-linecap="round" opacity=".55"/>')
    o.append(f'<path d="M31 36 C34 33.5 40 33 44 35 M56 35 C60 33 66 33.5 69 36" stroke="{D}" stroke-width="2" stroke-linecap="round" fill="none" opacity=".8"/>')
    # eyes: light amber, open, a touch of droop underneath
    o.append('<g class="eyes">')
    for cx in (38.5, 61.5):
        o.append(f'<ellipse cx="{cx}" cy="41.5" rx="4.6" ry="4" fill="{AMB}"/><circle cx="{cx}" cy="41.8" r="2.1" fill="{N}"/><circle cx="{cx+1.2}" cy="40.6" r=".9" fill="#fff"/>')
        o.append(f'<path d="M{cx-4.8} 40.2 C{cx-2.5} 37.8 {cx+2.5} 37.8 {cx+4.8} 40.2" fill="none" stroke="{D}" stroke-width="1.2"/>')
        o.append(f'<path d="M{cx-3.5} 45.6 C{cx-1.5} 46.6 {cx+1.5} 46.6 {cx+3.5} 45.6" fill="none" stroke="#9a5a5a" stroke-width=".9" opacity=".7"/>')
    o.append('</g>')
    # the dark mask over a wide, square muzzle with jowls
    o.append(f'<path d="M31 51 C32 45 68 45 69 51 L71 62 C71 71 62 76 50 76 C38 76 29 71 29 62 Z" fill="{M}"/>')
    o.append(f'<path d="M50 59 L50 65 M50 65 C46 69.5 39 69.5 34 65.5 M50 65 C54 69.5 61 69.5 66 65.5" stroke="{N}" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    if tongue:
        o.append(f'<path d="M45.5 67.6 C45.5 74.5 54.5 74.5 54.5 67.6 C52 69 48 69 45.5 67.6 Z" fill="#e58a96"/><path d="M50 68.6 L50 72.2" stroke="#c76c79" stroke-width=".8"/>')
    # the big nose
    o.append(f'<path d="M40 51.5 C40 46.5 60 46.5 60 51.5 C60 56.6 55 59 50 59 C45 59 40 56.6 40 51.5 Z" fill="{N}"/>')
    o.append(f'<ellipse cx="45.6" cy="53.6" rx="2" ry="1.3" fill="#000"/><ellipse cx="54.4" cy="53.6" rx="2" ry="1.3" fill="#000"/><ellipse cx="47" cy="49.4" rx="3.4" ry="1.1" fill="#fff" opacity=".22"/>')
    # his gold Cuban chain, with the pendant
    pts=[(x, 81.5 - 0.0075*(x-50)**2) for x in range(27, 74, 1)]
    d='M'+' L'.join(f'{x} {y:.2f}' for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{GOLD2}" stroke-width="4.6" stroke-linecap="round"/>')
    o.append(f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="3.4" stroke-linecap="round"/>')
    ticks=''.join(f'<path d="M{x-.9:.1f} {81.5-0.0075*(x-50)**2-1.4:.1f} l1.8 2.8" stroke="{GOLD2}" stroke-width=".7"/>' for x in range(28, 74, 3))
    o.append(ticks)
    o.append(f'<path d="M50 83 l-2.6 4 l2.6 4.2 l2.6 -4.2 z" fill="{GOLD}" stroke="{GOLD2}" stroke-width=".7"/>')
    return ''.join(o)
def svg(cls="apollo"):
    return f'<svg class="{cls}" viewBox="0 0 100 100" aria-hidden="true">{dog()}</svg>'
if __name__ == "__main__":
    print(svg())

"""The board's app icon: Coeus's constellation owl on a night sky (Frank, 2026-10-03:
"coeus icon, build the app"). Writes design/app_icon.svg; render the PNGs with
`NODE_PATH=/opt/node22/lib/node_modules node design/app_icon.cjs` (iPhone 180, Android 192 / 512,
a maskable 512 and the 32px favicon into site/public/app/)."""
import random, os
HERE = os.path.dirname(os.path.abspath(__file__))
# the owl from index.html's .coeusfab, 48x48 units
OWL = ('<path d="M13 9 L17 14 L31 14 L35 9 L37 24 L33 38 L24 42 L15 38 L11 24 Z"/>'
       '<path d="M17 14 L13 24 M31 14 L35 24 M17 14 L24 19 L31 14 M11 24 L24 27 L37 24" stroke-width=".7" opacity=".6"/>')
DOTS = [(13,9),(17,14),(31,14),(35,9),(37,24),(33,38),(24,42),(15,38),(11,24),(24,19),(24,27)]
def icon(pad=0.0):
    r = random.Random(7); stars = ''.join(
        f'<circle cx="{r.randint(20,1004)}" cy="{r.randint(20,1004)}" r="{r.choice([1.6,2.2,3])}" fill="#fff" opacity="{r.choice([.25,.4,.6])}"/>' for _ in range(46))
    s = 1024 * (0.68 - pad) / 48; off = (1024 - 48 * s) / 2
    ink = "#f3e3c3"
    dots = ''.join(f'<circle cx="{x}" cy="{y}" r="1.25" fill="{ink}"/>' for x, y in DOTS)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
            '<defs><radialGradient id="sky" cx=".5" cy=".38" r=".75"><stop offset="0" stop-color="#2a2550"/><stop offset=".6" stop-color="#14122b"/><stop offset="1" stop-color="#0a0918"/></radialGradient>'
            '<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#e9a86a" stop-opacity=".28"/><stop offset="1" stop-color="#e9a86a" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="1024" height="1024" fill="url(#sky)"/>{stars}<circle cx="512" cy="500" r="380" fill="url(#halo)"/>'
            f'<g transform="translate({off:.1f} {off - 8:.1f}) scale({s:.3f})" fill="none" stroke="{ink}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">'
            f'{OWL}{dots}<circle cx="18" cy="23" r="3.6" fill="{ink}" stroke="none"/><circle cx="30" cy="23" r="3.6" fill="{ink}" stroke="none"/>'
            '<circle cx="18" cy="23" r="1.4" fill="#e2683a" stroke="none"/><circle cx="30" cy="23" r="1.4" fill="#e2683a" stroke="none"/><path d="M24 27 L24 31" stroke-width="1.3"/></g></svg>')
if __name__ == "__main__":
    open(os.path.join(HERE, "app_icon.svg"), "w").write(icon())
    open(os.path.join(HERE, "app_icon_maskable.svg"), "w").write(icon(pad=0.12))
    print("wrote design/app_icon.svg, design/app_icon_maskable.svg")

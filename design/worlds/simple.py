"""Simple: plain, neutral looks with one clean typeface (Frank, 2026-10-06: "a more basic look if someone
doesnt want all the extra design"). No pictures."""
KEY = "simple"
NAME = "Simple"
CATEGORY = "Plain"
PLAIN = True
FONTS = "family=Inter:wght@400;500;600;700"
DISPLAY = "'Inter', system-ui, sans-serif"
DW = 700
BODY = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
TOUR = None
def _l(surface, raised, card2, chip, grid, border, strong, text, muted, sec, accent, accent_d, side, side2, sideink, brand, brand2):
    return (f"--surface: {surface}; --surface-raised: {raised}; --card2: {card2}; --chip: {chip}; --grid: {grid}; --border: {border}; "
            f"--border-strong: {strong}; --text-primary: {text}; --text-muted: {muted}; --text-secondary: {sec}; --accent: {accent}; "
            f"--accent-d: {accent_d}; --side: {side}; --side2: {side2}; --sideInk: {sideink}; --brand: {brand}; --brand2: {brand2}")
LIGHT = "; --rad: 10px; --bw: 1px; --shadow: 0 1px 3px rgba(15,23,42,.08)"
DARK = "; --shadow: 0 1px 3px rgba(0,0,0,.5)"
LOOKS = [
    ("paper", "Paper",
     _l("#f5f6f8", "#ffffff", "#f8f9fb", "#eceef2", "#eceef2", "#e2e5ea", "#cfd4dc", "#1a1d23", "#5f6673", "#4a515d",
        "#2563eb", "#1d4ed8", "#1f2329", "#2b3038", "#e3e6eb", "#ffffff", "#93b4ff") + LIGHT,
     _l("#111316", "#1a1d22", "#20242a", "#292e35", "#292e35", "#2c3138", "#3a4049", "#e8eaee", "#a2a9b5", "#c3c8d1",
        "#6b9bff", "#a9c4ff", "#0b0d10", "#171a1f", "#d8dce3", "#ffffff", "#93b4ff") + DARK,
     ["#f5f6f8", "#1f2329", "#2563eb"]),
    ("graphite", "Graphite",
     _l("#eceef0", "#fafbfb", "#f1f3f4", "#e2e5e8", "#e2e5e8", "#d9dde1", "#c3c9cf", "#1b1f22", "#5a6268", "#465057",
        "#0f766e", "#0b5953", "#2a2f33", "#363c41", "#e1e5e8", "#fafbfb", "#7fd1c7") + LIGHT,
     _l("#121416", "#1b1e21", "#212528", "#2a2e32", "#2a2e32", "#2e3337", "#3b4146", "#e6e9eb", "#a1a9af", "#c2c8cd",
        "#2bb3a3", "#8fe3d8", "#0b0d0e", "#181b1d", "#d6dbde", "#fafbfb", "#7fd1c7") + DARK,
     ["#eceef0", "#2a2f33", "#0f766e"]),
    ("ink", "Ink",
     _l("#f6f4ef", "#fffefb", "#f9f7f2", "#ece8df", "#ece8df", "#e3ded3", "#d0c9bb", "#18202e", "#5c6370", "#454d5c",
        "#1e3a8a", "#172e6e", "#162033", "#203049", "#dfe5f0", "#fffefb", "#a8bdf0") + LIGHT,
     _l("#10131a", "#181c25", "#1e232d", "#272d39", "#272d39", "#2b3240", "#384052", "#e7e9ef", "#a1a8b8", "#c3c8d4",
        "#7d9bf0", "#b4c6f7", "#0a0d13", "#151a24", "#d4dae6", "#fffefb", "#a8bdf0") + DARK,
     ["#f6f4ef", "#162033", "#1e3a8a"]),
]
VISTA_LINES = {}

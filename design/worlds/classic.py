"""Arizona Classic: the board as it looked before the pictures (Frank, 2026-10-06: "plain themes as well,
like the arizona before we changed the background ... a more basic look if someone doesnt want all the
extra design"). The desert's five looks and type, no Digest picture, no page banners, no card strips."""
KEY = "classic"
NAME = "Arizona Classic"
CATEGORY = "Plain"
PLAIN = True
FONTS = ""   # the board's own Fraunces / Manrope, already loaded
DISPLAY = "'Fraunces', Georgia, serif"
DW = 700
BODY = "Manrope, system-ui, -apple-system, 'Segoe UI', sans-serif"
TOUR = None
# the desert's own values (index.html :root, its looks and Desert Night), set whole here since a plain
# look's light rule comes after Desert Night in the stylesheet
_DARK = ("--surface: #1b1613; --surface-raised: #25201c; --card2: #2e2823; --chip: #3a322b; --text-primary: #efe4d6; "
         "--text-muted: #b3a393; --text-secondary: #c4b5a5; --grid: #3a322b; --border: #3f3630; --border-strong: #4a3f36; "
         "--accent: #d06a3f; --accent-d: #ff9b74; --side: #120e0c; --side2: #241c18; --sideInk: #d9cbbb; --brand: #f3e9dc; "
         "--brand2: #e59a6f; --shadow: 0 2px 8px rgba(0,0,0,.45)")
LOOKS = [
    ("az-sonoran", "Sonoran",
     "--surface: #f3e9dc; --surface-raised: #fffaf3; --card2: #f8efe4; --chip: #e8dac9; --border: #e2d3c0; --border-strong: #d4c1aa; "
     "--text-primary: #2a2320; --text-secondary: #5e5046; --text-muted: #7a6a5d; --grid: #efe3d4; --accent: #b5532f; --accent-d: #8a2b12; "
     "--side: #2a2320; --side2: #3a302b; --sideInk: #e9ddd0; --brand: #f3e9dc; --brand2: #e59a6f; --rad: 18px; --bw: 2px; --shadow: 0 2px 8px rgba(42,35,32,.08)",
     _DARK, ["#f3e9dc", "#2a2320", "#b5532f"]),
    ("az-saguaro", "Saguaro",
     "--surface: #f1ece1; --surface-raised: #fdfbf6; --card2: #f4f0e6; --chip: #e6e3d6; --text-primary: #1f2a22; --text-muted: #5d6b5f; --text-secondary: #50605a; "
     "--grid: #e4e2d6; --border: #dcdfd0; --border-strong: #c9cdb9; --accent: #3e6b4f; --accent-d: #2b4f39; --side: #24382c; --side2: #2f4a3a; --sideInk: #dfe7dd; "
     "--brand: #f1ece1; --brand2: #b9d3a8; --rad: 12px; --bw: 2px; --shadow: 0 2px 8px rgba(42,35,32,.08)",
     "--surface: #141a16; --surface-raised: #1c241e; --card2: #232d26; --chip: #2c372f; --text-primary: #e8ede4; --text-muted: #a3b2a5; --text-secondary: #c3cfc4; "
     "--grid: #2c372f; --border: #33403a; --border-strong: #3b4a3f; --accent: #5e9a72; --accent-d: #9fd6b3; --side: #0d120f; --side2: #1a241d; --sideInk: #cfdccf; "
     "--brand: #f1ece1; --brand2: #b9d3a8; --shadow: 0 2px 8px rgba(0,0,0,.45)",
     ["#f1ece1", "#24382c", "#3e6b4f"]),
    ("az-turquoise", "Turquoise & Silver",
     "--surface: #eeebe5; --surface-raised: #fbfaf7; --card2: #f2f0eb; --chip: #e3e0da; --text-primary: #1d2a33; --text-muted: #5d6a73; --text-secondary: #4e5b64; "
     "--grid: #e3e0da; --border: #dcdfe1; --border-strong: #c8cdd0; --accent: #1f8a8a; --accent-d: #156464; --side: #1d2a33; --side2: #2a3a46; --sideInk: #d6dee3; "
     "--brand: #eeebe5; --brand2: #6cc7c4; --rad: 10px; --bw: 2px; --shadow: 0 2px 8px rgba(42,35,32,.08)",
     "--surface: #12181c; --surface-raised: #1a2228; --card2: #212b32; --chip: #29343c; --text-primary: #e6ebee; --text-muted: #9fadb6; --text-secondary: #c2cdd4; "
     "--grid: #29343c; --border: #2f3c45; --border-strong: #36444e; --accent: #34aeab; --accent-d: #8fe0dd; --side: #0b1013; --side2: #17202a; --sideInk: #cdd8de; "
     "--brand: #eeebe5; --brand2: #6cc7c4; --shadow: 0 2px 8px rgba(0,0,0,.45)",
     ["#eeebe5", "#1d2a33", "#1f8a8a"]),
    ("az-canyon", "Canyon Sunset",
     "--surface: #f6e6d6; --surface-raised: #fff8f0; --card2: #fbeee2; --chip: #f1dcc8; --text-primary: #3a1d12; --text-muted: #7d5a48; --text-secondary: #6a4a3a; "
     "--grid: #f0dccb; --border: #ecd2bb; --border-strong: #e0b994; --accent: #d9622b; --accent-d: #a8441a; --side: #5a2416; --side2: #733021; --sideInk: #f6dcc8; "
     "--brand: #fff1e4; --brand2: #ffb27e; --rad: 18px; --bw: 2.5px; --shadow: 0 2px 8px rgba(42,35,32,.08)",
     "--surface: #1d1210; --surface-raised: #2a1a16; --card2: #33211c; --chip: #40291f; --text-primary: #f7e6da; --text-muted: #c4a491; --text-secondary: #dcc0b0; "
     "--grid: #40291f; --border: #4a3026; --border-strong: #5a3a2c; --accent: #ec7a43; --accent-d: #ffb089; --side: #130b09; --side2: #2a1a14; --sideInk: #eccfbe; "
     "--brand: #fff1e4; --brand2: #ffb27e; --shadow: 0 2px 8px rgba(0,0,0,.45)",
     ["#f6e6d6", "#5a2416", "#d9622b"]),
    ("az-mesa", "Mesa Minimal",
     "--surface: #faf7f2; --surface-raised: #ffffff; --card2: #f7f3ec; --chip: #efe8de; --text-primary: #2a2320; --text-muted: #776a5f; --text-secondary: #5e5248; "
     "--grid: #efe8de; --border: #ece4d8; --border-strong: #e2d7c8; --accent: #b5532f; --accent-d: #8a2b12; --side: #efe6da; --side2: #e2d5c4; --sideInk: #4a3f38; "
     "--brand: #2a2320; --brand2: #b5532f; --rad: 10px; --bw: 1px; --shadow: none",
     "--surface: #171311; --surface-raised: #1f1a17; --card2: #26201c; --chip: #2f2824; --text-primary: #efe6da; --text-muted: #ad9e90; --text-secondary: #cdbfb1; "
     "--grid: #2f2824; --border: #332b26; --border-strong: #3d342e; --accent: #d06a3f; --accent-d: #ff9b74; --side: #1f1a17; --side2: #2a231f; --sideInk: #d5c8ba; "
     "--brand: #efe6da; --brand2: #e59a6f; --shadow: none",
     ["#faf7f2", "#efe6da", "#b5532f"]),
]
VISTA_LINES = {}

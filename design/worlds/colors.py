"""Colors: plain looks in bolder palettes (Frank, 2026-10-06: "other pallette styles and themes"). No
pictures; the colour is the design."""
KEY = "colors"
NAME = "Colors"
CATEGORY = "Plain"
PLAIN = True
FONTS = "family=DM+Sans:wght@400;500;600;700"
DISPLAY = "'DM Sans', system-ui, sans-serif"
DW = 700
BODY = "'DM Sans', system-ui, -apple-system, 'Segoe UI', sans-serif"
TOUR = None
from simple import _l
LIGHT = "; --rad: 14px; --bw: 2px; --shadow: 0 2px 8px rgba(20,20,40,.08)"
DARK = "; --shadow: 0 2px 8px rgba(0,0,0,.5)"
LOOKS = [
    ("oceanblue", "Ocean Blue",
     _l("#e8f0f8", "#f9fbfe", "#eef4fa", "#dbe6f2", "#dbe6f2", "#d0deec", "#b4c8de", "#0f2338", "#4f6478", "#3d5266",
        "#0b63b6", "#084c8c", "#0b2e52", "#123d69", "#d6e6f7", "#f9fbfe", "#7cc0ff") + LIGHT,
     _l("#0b1520", "#121e2b", "#172534", "#1f2f40", "#1f2f40", "#223448", "#2d435b", "#e3edf7", "#9cb0c5", "#bfd0e1",
        "#4fa3f0", "#9fcdf8", "#06101a", "#0f1d2c", "#cfe0f1", "#f9fbfe", "#7cc0ff") + DARK,
     ["#e8f0f8", "#0b2e52", "#0b63b6"]),
    ("forest", "Forest",
     _l("#ecf1ea", "#fbfcfa", "#f1f5ef", "#e0e8dc", "#e0e8dc", "#d4dfcf", "#b9c9b2", "#17251a", "#556657", "#435446",
        "#2f6b3a", "#22512b", "#1b3321", "#24432b", "#d9e7d6", "#fbfcfa", "#a6d9a0") + LIGHT,
     _l("#0e140f", "#161e17", "#1b251c", "#233025", "#233025", "#273528", "#334535", "#e4ece3", "#a0b0a1", "#c1cec1",
        "#5cb46c", "#a6deaf", "#080c09", "#121a13", "#d0dfcf", "#fbfcfa", "#a6d9a0") + DARK,
     ["#ecf1ea", "#1b3321", "#2f6b3a"]),
    ("plum", "Plum",
     _l("#f2ecf3", "#fdfbfd", "#f6f1f7", "#e9e0ec", "#e9e0ec", "#e0d4e4", "#ccbad2", "#2a1630", "#6a5670", "#55425b",
        "#7b2d8e", "#5f216e", "#331a3b", "#45234f", "#eadcf0", "#fdfbfd", "#d8a6ea") + LIGHT,
     _l("#140e16", "#1d1520", "#241a28", "#2e2233", "#2e2233", "#332538", "#433049", "#efe6f2", "#b1a0b7", "#cdbfd2",
        "#c27ad6", "#e2b9ec", "#0c080d", "#1a121d", "#e0d0e6", "#fdfbfd", "#d8a6ea") + DARK,
     ["#f2ecf3", "#331a3b", "#7b2d8e"]),
    ("sunrise", "Sunrise",
     _l("#fbefe6", "#fffbf8", "#fdf3ec", "#f6e2d4", "#f6e2d4", "#f1d8c6", "#e6bea2", "#2e1a10", "#6e5546", "#5a4234",
        "#c2410c", "#9a330a", "#3b2016", "#4f2b1d", "#f6dccb", "#fffbf8", "#ffb48a") + LIGHT,
     _l("#17100c", "#211812", "#291e17", "#33261d", "#33261d", "#3a2b21", "#4a372b", "#f6e9e0", "#bfa898", "#d9c6b8",
        "#f07a3e", "#ffb990", "#0e0907", "#1c1410", "#ecd4c4", "#fffbf8", "#ffb48a") + DARK,
     ["#fbefe6", "#3b2016", "#c2410c"]),
]
VISTA_LINES = {}

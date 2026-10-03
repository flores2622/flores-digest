# Drawing a world for the Flores Sales Floor board

The board (an insurance agency's sales dashboard) has "worlds": a world is design and font only --
its colour looks, its typeface pair, and its pictures. Figures, lists and buttons never change.
The desert world and the Space world exist. You are drawing one new world as ONE Python module.

## What to write: `worlds/<key>.py` (this folder)

Pure Python 3, standard library only. It must define:

    KEY = "<key>"                       # same as the filename
    NAME = "Ocean"                      # shown in Settings
    FONTS = "family=Merriweather:wght@700;900&family=Source+Sans+3:wght@400;500;600;700"   # Google Fonts css2 query
    DISPLAY = "'Merriweather', Georgia, serif"   # headings, the greeting and the big tile numbers
    DW = 700                            # the display face's weight -- must be a weight in FONTS; never thin
    BODY = "'Source Sans 3', system-ui, sans-serif"   # all other text, set at weight 500
    SKY_BG = (("<light top colour>", "<light leaderboard colour>"), ("<dark top>", "<dark leaderboard>"))  # shown while the picture loads
    LOOKS = [  # exactly 3 colour looks; each (key, name, light_css, dark_css, [3 swatch colours])
      ("harbor", "Harbor", "--surface: #...; --surface-raised: #...; ...", "--surface: #...; ...", ["#bg", "#side", "#accent"]),
      ...]
    def skyline(night: bool) -> str          # the Digest picture, viewBox "0 0 1600 1700"
    VISTA_FNS = {page: fn(night) -> str}     # 12 page banners, viewBox "0 0 1600 240"
    VISTA_LINES = {page: [title, line]}      # the banner's words for each page
    STRIP_FNS = {outcome: fn(night) -> str}  # 9 coaching-card strips, viewBox "0 0 1600 160"

Every look's light_css AND dark_css must set all of:
--surface --surface-raised --card2 --chip --text-primary --text-muted --text-secondary --grid --border
--border-strong --accent --accent-d --side --side2 --sideInk --brand --brand2 ; light_css also --rad (8-18px).
--surface is the page, --surface-raised the cards (lighter than surface in light mode), --side/--side2 the
left menu (dark in both modes, --sideInk its text), --brand / --brand2 the logo's two words on the menu,
--accent buttons and links (must read on --surface-raised: 4.5:1 contrast). Text colours must pass
4.5:1 on --surface-raised. Dark versions are true dark (surface around #0e-#1c). Copy the shape of
Space's looks below. Do NOT set the green/amber/red tier colours -- the board owns those.

    html[data-look="mission"] { --surface: #e9edf3; --surface-raised: #f7f9fc; --card2: #eef2f7; --chip: #dde4ee; --text-primary: #141c2b; --text-muted: #5b6a80; --text-secondary: #4a5a70; --grid: #dfe5ee; --border: #d6dde8; --border-strong: #b9c4d4; --accent: #e2552b; --accent-d: #b23f1a; --side: #0f1a33; --side2: #16244a; --sideInk: #d8e1f3; --brand: #e9edf3; --brand2: #ff9b6b; --rad: 10px; }
    dark: --surface: #0b1120; --surface-raised: #121a2e; --card2: #18223a; --chip: #202c48; --text-primary: #e6ecf7; --text-muted: #9aa8c2; --text-secondary: #b2bdd3; --grid: #202c48; --border: #243050; --border-strong: #30406a; --accent: #ff7a4d; --accent-d: #ffa17f; --side: #060a16; --side2: #0e1730; --sideInk: #d8e1f3; --brand: #e9edf3; --brand2: #ff9b6b;

## The pictures

All are inline SVG strings, flat illustration, drawn by code (paths, rects, circles, gradients). Light =
`night=False` (daytime or golden hour), dark = `night=True` (the same place at night: stars, lit windows,
glow). Both must look good. Rules:
- Root element exactly `<svg xmlns="http://www.w3.org/2000/svg" viewBox="..." preserveAspectRatio="...">`
  (skyline: `xMidYMin slice`; vistas and strips: `xMidYMid slice`). Valid XML: escape & < > in <text>.
- No <image>, no external links, no web fonts: <text> may use only Arial, Georgia, monospace, sans-serif, serif.
- ids are per-picture; reuse freely across pictures (each is its own document).
- Size budget, URL-encoded: skyline <= 70 KB, each vista <= 30 KB, each strip <= 14 KB. Keep star fields
  and repeated details to dozens, not hundreds. `python3 check.py <key>` enforces all of this.
- No real brands, logos, team names, characters or trademarks (no NFL, no Pac-Man, no named stadiums).
  The agency's name FLORES may appear on a sign, a boat, a jersey etc.
- Charming, readable at a glance, a bit playful. Not cluttered. Strong silhouettes, 3-5 colour families.

### skyline(night): the Sales Digest's main picture, 1600 x 1700 units, horizon at y = 377
Shown as TWO crops of one drawing on a ~1420px-wide page (so 1 unit ~ 0.89 px):
1. The top card shows units 0..~420. Its title sits at top-left (units ~20-70). Seven white tiles cover
   units ~170..~400 across the full width. So the SKY and the tall things' tops must sit in 0..170 and
   peek between/around the tiles: put the world's iconic tall features (towers, masts, peaks, lighthouse,
   rocket...) so their tops rise into 0..170. Moon / sun / stars / birds up there too.
2. The leaderboard card shows units 377..~1000 (its picture starts AT the horizon). Its title sits at
   top-left (377..430). A 3-step gold podium stands centred at x ~620-1000, units ~560..~720 -- draw the
   place it stands on (a stage, dock, field, platform) and a path or lane leading to it. A near-opaque
   table covers everything below unit ~850, so spend no detail there.
Look at `out/space/sky.png` (the Space world in the previewer) for how this lands.

### VISTA_FNS: 12 page banners, 1600 x 240 units
Shown 170px tall at ~1400px wide, cover-cropped: roughly units y 25..215 are visible; a few % of the
left/right may crop on narrow screens. The board writes the page title in white at the bottom-left
(x 0..450, y 180..240) and the line in small white caps at the bottom-right (x 1050..1600, y 195..240):
keep those corners darker/simple so white text reads, and put the subject in the middle.
Pages (keys): sales, messages, coaching, roleplay, rphistory (Role Play session history), training,
blueprint (Apollo's Road Map: the sales route -- label four stops Dial, Discovery, Quote, Close),
athenamap (Athena's Road Map: the service route -- label Listen, Understand, Handle, Follow up),
service (the service team keeping the book), renewals (what came back), claims (after the storm),
commercial (the commercial lines desk).
VISTA_LINES gives [title, line] per page; titles are fixed:
  sales "Sales", messages "Texts & Emails", coaching "Coaching", roleplay "Role Play",
  rphistory "Session History", training "Training", blueprint "Apollo's Road Map",
  athenamap "Athena's Road Map", service "Service Digest", renewals "Renewals", claims "Claims",
  commercial "Commercial Center"
and the line is yours, short, lower case, in the world's voice, e.g. Space's "liftoff: premium leaving
the pad", "mission control: every call, replayed", "the flight plan, in plain words".

### STRIP_FNS: 9 coaching-card outcome strips, 1600 x 160 units
Shown as a 58px band across a card ~1350px wide: roughly units y 45..115 are visible. A pill sits at
the far right (x 1300..1600) -- keep that end plain. Put a short monospace caption at the LEFT
(x ~120, y ~92, size ~20-30, white or high contrast) and the picture's subject around x 500..1000.
Outcomes (keys) and meaning:
  sold_on_call          sold on the call (the win)
  quoted_call_open      quoted, still open (in progress)
  followup_open         follow-up, still open (may reuse quoted_call_open's function)
  quoted_call_lost      quoted, lost
  followup_lost         follow-up, lost (may reuse quoted_call_lost's function)
  dead_no_quote         reached but no quote was made (a dead end)
  live_quote_ok         reached, okay to quote (a good conversation)
  live_no_quote         reached, no quote yet (paused, waiting)
  callback_no_contact   voicemail / no contact (asleep, no signal)
Space's set, for the idea: GO FOR LAUNCH (liftoff), HOLDING (pad, clock running), SPLASHDOWN (parachute,
grey), SCRUB (red light, empty pad), COMMS OPEN (two astronauts), ON THE TETHER, NO SIGNAL (probe asleep).

## Reference code and tools (read them first)
- `../space/skyline.py` and `../space/scenes.py`: the Space world; `space.py` here wraps it as a module
  in exactly the shape you must write. Reuse their helper ideas (sky gradient, star field, wrap()).
- `python3 check.py <key>` validates and writes the SVGs to `out/<key>/`.
- `NODE_PATH=/opt/node22/lib/node_modules node preview.cjs <key>` renders `out/<key>/sky.png` (the
  Digest with mock tiles, podium and table, light then dark) and `out/<key>/sheet.png` (every banner
  with its title and line, every strip with a mock pill), which you can open with the Read tool.
Work in loops: write, check, preview, LOOK at both PNGs carefully, fix what reads badly (things hidden
under tiles, text over text, crowded corners, unreadable night scenes, misplaced podium stage), repeat
until both modes look good. Then stop.

## Do not
- Touch anything outside this `worlds/` folder (no repo files, no index.html, no git).
- Change check.py, preview.cjs, space.py or another world's module.

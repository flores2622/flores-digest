"""Write the desert world's Digest picture (desert_digest.py) into site/public/index.html.

The desert's picture lives inline in index.html as four rules (`.skyline {`, its dark twin, `.lbsky {`,
its dark twin), each a url("data:image/svg+xml;utf8,...") background, followed by the still copies for
Settings > Motion > Reduced (`/* the desert Digest moves ...` and four
`html[data-motion="reduce"][data-theme="desert"] ...` rules). This replaces only the url(...) inside
each of the four rules -- the rest of each rule is kept as it is -- and rewrites the still block.

    python3 design/worlds/desert_splice.py
"""
import os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import desert_digest  # noqa: E402

P = os.path.join(HERE, "..", "..", "site", "public", "index.html")
KEYS = ['.skyline {', 'html[data-mode="dark"] .skyline {', '.lbsky {', 'html[data-mode="dark"] .lbsky {']
enc = lambda svg: urllib.parse.quote(svg, safe="/:=,.;- '()")
still = lambda svg: re.sub(r"<animate\w*\b[^>]*/>", "", svg)
FULL = 'viewBox="0 0 1600 1700"'
LB = 'viewBox="0 377 1600 1323"'


def pictures():
    light, dark = desert_digest.skyline(False), desert_digest.skyline(True)
    assert light.count(FULL) == 1 and dark.count(FULL) == 1
    return {KEYS[0]: light, KEYS[1]: dark,
            KEYS[2]: light.replace(FULL, LB, 1), KEYS[3]: dark.replace(FULL, LB, 1)}


def main():
    lines = open(P).read().split("\n")
    idx = {}
    for i, ln in enumerate(lines):
        for key in KEYS:
            if ln.startswith(key) and "data:image/svg+xml" in ln:
                assert key not in idx, f"two rules for {key}"
                idx[key] = i
    assert len(idx) == 4, idx
    pics = pictures()
    for key, i in idx.items():
        m = re.search(r'url\("data:image/svg\+xml;utf8,([^"]*)"\)', lines[i])
        assert m, key
        lines[i] = lines[i][:m.start(1)] + enc(pics[key]) + lines[i][m.end(1):]
        print(f"{key:40s} {len(enc(pics[key])) / 1024:5.1f} KB encoded, {pics[key].count('<animate')} animations")
    u = lambda key: 'url("data:image/svg+xml;utf8,' + enc(still(pics[key])) + '")'
    block = ('/* the desert Digest moves (the windmill, a hawk, clouds, the saloon doors, a horse\'s tail, lanterns, tumbleweeds, '
             'dust, and at night the stars); a still copy for Settings > Motion > Reduced */\n'
             'html[data-motion="reduce"][data-theme="desert"] .skyline { background-image: ' + u(KEYS[0]) + '; }\n'
             'html[data-motion="reduce"][data-theme="desert"][data-mode="dark"] .skyline { background-image: ' + u(KEYS[1]) + '; }\n'
             'html[data-motion="reduce"][data-theme="desert"] .lbsky { background-image: ' + u(KEYS[2]) + '; }\n'
             'html[data-motion="reduce"][data-theme="desert"][data-mode="dark"] .lbsky { background-image: ' + u(KEYS[3]) + '; }')
    keep = [l for l in lines if not l.startswith('/* the desert Digest moves')
            and not l.startswith('html[data-motion="reduce"][data-theme="desert"]')]
    # re-find the four rules in the kept lines and put the still block right after the last of them
    last = max(i for i, l in enumerate(keep) if any(l.startswith(k) and "data:image/svg+xml" in l for k in KEYS))
    keep.insert(last + 1, block)
    open(P, "w").write("\n".join(keep))
    print("wrote", os.path.normpath(P))


if __name__ == "__main__":
    main()

"""Add a jump link to the v2axes section in the header standfirst area."""
BASE = "/storage/roatienza.github.io/showcase_s7"
src = open(f"{BASE}/index.html").read()
if 'href="#v2axes"' in src:
    print("link already present")
else:
    anchor = '<div class="switch">'
    i = src.find(anchor)
    assert i > 0
    link = ('  <p style="margin:10px 0 0;font-size:13.5px"><a href="#v2axes" '
            'style="color:var(--amber)">New: V2 design-axes listening test (2026-09-17) '
            '&mdash; slow / emotional / high_pitch A/B, s6-40k baseline vs v2-19.5k &rarr;</a></p>\n  ')
    src = src[:i] + link + src[i:]
    open(f"{BASE}/index.html", "w").write(src)
    print("link added; size", len(src))
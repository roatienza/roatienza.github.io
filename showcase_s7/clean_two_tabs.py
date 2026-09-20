#!/usr/bin/env python3
"""Rebuild showcase_s7/index.html as exactly two tabs: S7.11-rope and S7.11-ttds2v3.

- Extract the 20 rope renders from the main 12-checkpoint grid into a new #rope
  section (chip anatomy preserved: vox/who/line/audio/cond).
- Keep the #ttds2v3 section verbatim except: retitle the section label, rewrite
  every reference to the removed S7.11-ttsds2 (20k) tab, drop the per-clip
  "UTMOS delta vs ttsds2-20k" fragment from chip conds, drop the closing
  comparison paragraph.
- Remove: #s711perf, #v2axes, #ttds2 sections, the 12-button checkpoint
  switcher, the switcher <script>, and the three "New:" header links
  (replaced by two tab links).
- Header gets a two-tab nav: S7.11-rope | S7.11-ttds2v3.
"""
import re, sys

ROOT = "/storage/roatienza.github.io/showcase_s7"
src = open(f"{ROOT}/index_backup_pre_clean_20260919.html", encoding="utf-8").read()
orig_len = len(src)
fails = []

def need(cond, msg):
    if not cond:
        fails.append(msg)

# ---- locate landmarks ------------------------------------------------------
i_grid = src.find('<main class="wrap"><div class="grid">')
need(i_grid >= 0, "main grid open")
i_perf = src.find('<section class="tr" id="s711perf"')
need(i_perf > i_grid, "s711perf section")
i_v2 = src.find('<section class="tr" id="v2axes"')
need(i_v2 > i_perf, "v2axes section")
i_t2 = src.find('<section class="tr" id="ttds2"')
need(i_t2 > i_v2, "ttds2 section")
i_v3 = src.find('<section class="tr" id="ttds2v3"')
need(i_v3 > i_t2, "ttds2v3 section")
i_main_end = src.find('</div></main>')
need(i_main_end > i_v3, "main close")
i_foot = src.find('<footer>')
need(i_foot > i_main_end, "footer")
i_script = src.rfind('<script>')  # the switcher script at EOF; #v2axes has its own inline script
need(i_script > i_foot, "script")
i_body_end = src.find('</body></html>')
need(i_body_end > i_script, "body close")

# ---- 1) extract rope chips from the main grid ------------------------------
grid = src[i_grid:i_perf]
grid = grid[len('<main class="wrap"><div class="grid">'):]
grid = grid[: grid.rfind("</section>")]  # drop trailing </section> of last chip? (grid has none; safe)
# split into chips
chip_parts = re.findall(r'<article class="chip[^"]*">.*?</article>', grid, flags=re.S)
need(len(chip_parts) == 20, f"expected 20 main-grid chips, got {len(chip_parts)}")

rope_chips = []
for k, chip in enumerate(chip_parts):
    m = re.search(r'<audio controls preload="none" data-set="S7\.11-rope" src="(audio/[^"]+)"', chip)
    need(m, f"chip {k}: no rope audio")
    rope_src = m.group(1)
    # strip every <audio ...> line AND any .absent "did not ship" paragraphs
    # (they reference removed checkpoints); keep everything else
    body = re.sub(r'[ \t]*<audio controls preload="none" data-set="[^"]*" src="[^"]*"[^>]*></audio>\n?', "", chip)
    body = re.sub(r'[ \t]*<p class="absent" data-set="[^"]*">.*?</p>\n?', "", body, flags=re.S)
    # re-insert single rope audio right before the cond paragraph
    mm = re.search(r'([ \t]*)<p class="cond">', body)
    need(mm, f"chip {k}: no cond paragraph")
    title = "S7.11-rope &middot; v6a 50k &middot; same 20 prompts &middot; seed 20260808"
    aud = f'{mm.group(1)}<audio controls preload="none" src="{rope_src}" title="{title}"></audio>\n'
    body = body[:mm.start()] + aud + body[mm.start():]
    rope_chips.append(body)

rope_section = (
    '<section class="tr" id="rope" style="max-width:none">\n'
    '  <p class="trlab">S7.11-rope &mdash; all 20 prompts, one take per prompt, v6a 50k, '
    'same operating point as every checkpoint on this page (text/caption CFG 8.0, caption CFG 8.0, '
    '32 steps, sway -1.0, best-of-4, seed 20260808)</p>\n'
    '  <div class="grid" style="grid-template-columns:1fr">\n'
    + "".join(rope_chips)
    + '  </div>\n</section>\n'
)

# ---- 2) keep #ttds2v3, rewrite ttsds2-20k references -----------------------
v3 = src[i_v3:i_main_end]  # includes trailing "</section>\n</div></main>" -> trim
v3 = v3[: v3.rfind("</section>") + len("</section>")] + "\n"

# 2a) section label: drop "same 20-axis voice-register captions as the S7.11-ttsds2 tab"
old_lbl = ('<p class="trlab">S7.11-ttsds2-v3 &mdash; all 20 prompts, one take per prompt, '
           'same 20-axis voice-register captions as the S7.11-ttsds2 tab (design &rarr; '
           'design_register.v1 &rarr; prose), same texts, same reference speakers, frozen serving '
           'path (schedule 64/48/48, first emit 32, eager), seed 1000</p>')
new_lbl = ('<p class="trlab">S7.11-ttsds2-v3 &mdash; all 20 prompts, one take per prompt, '
           '20-axis voice-register captions (design &rarr; design_register.v1 &rarr; prose), '
           'same texts, same reference speakers, frozen serving path (schedule 64/48/48, '
           'first emit 32, eager), seed 1000</p>')
need(old_lbl in v3, "v3 label not found verbatim")
v3 = v3.replace(old_lbl, new_lbl)

# 2b) note: rewrite the "same prose caption the S7.11-ttsds2 tab used" sentence
old_sent = ('renders each prompt with the <em>same</em> prose caption the\n'
            '    S7.11-ttsds2 tab used &mdash; the only variable between the two tabs is the checkpoint.')
new_sent = ('renders each prompt with a prose caption produced by the\n'
            '    same design &rarr; design_register.v1 &rarr; prose path used across this page.')
need(old_sent in v3, "v3 note sentence not found verbatim")
v3 = v3.replace(old_sent, new_sent)

# 2c) note: drop the "vs 80.52 / PROSODY 82.53 for ttsds2-20k on the identical prompt set" tail
old_tail = ' &mdash; vs 80.52 / PROSODY 82.53 for ttsds2-20k on the identical prompt set.'
need(old_tail in v3, "v3 note tail not found")
v3 = v3.replace(old_tail, ".")

# 2d) chip conds: drop " &middot; UTMOS &plusmn;X.XX vs ttsds2-20k" fragments.
#     6 of the 20 have trailing re-roll/CTC notes after the delta, so match up to
#     the next " &middot; " or "</p>", whichever comes first.
v3, n_sub = re.subn(r' &middot; UTMOS [^<]*? vs ttsds2-20k(?= &middot; |</p>)', "", v3)
need(n_sub == 20, f"expected 20 per-chip delta fragments, removed {n_sub}")

# 2e) closing comparison paragraph (Per-clip UTMOS deltas vs the ttsds2-20k tab ...)
m = re.search(r'[ \t]*<p style="margin-top:10px;font-size:13px;color:#9a9a9a;max-width:100ch">\s*Per-clip UTMOS deltas.*?</p>\n', v3, flags=re.S)
need(m, "closing comparison paragraph not found")
v3 = v3[:m.start()] + v3[m.end():]

# 2f) any other stray mentions of the removed tab/checkpoint
v3 = v3.replace("the S7.11-ttsds2 tab", "the S7.11-rope tab")

# ---- 3) header: replace three "New:" links with two tab links --------------
hdr_re = re.compile(
    r'[ \t]*<p style="margin:\d+px 0 0;font-size:13\.5px"><a href="#[^"]*" '
    r'style="color:var\(--amber\)">New: [^<]*&rarr;</a></p>\n')
hdr = src[:i_grid]
hdr, n_hdr = hdr_re.subn("", hdr)
need(n_hdr == 3, f"expected 3 New: links, removed {n_hdr}")
nav_links = (
    '    <p style="margin:10px 0 0;font-size:13.5px">'
    '<a href="#rope" style="color:var(--amber)">S7.11-rope &mdash; 20 prompts, one take per prompt &rarr;</a></p>\n'
    '    <p style="margin:6px 0 0;font-size:13.5px">'
    '<a href="#ttds2v3" style="color:var(--amber)">S7.11-ttsds2-v3 &mdash; variability-v3 12k, '
    'TTSDS2 80.78 / PROSODY 83.58 &rarr;</a></p>\n')
hdr = hdr.replace('<div class="switch">', nav_links + '  <div class="switch">', 1)
need(nav_links in hdr, "nav links not inserted")

# remove the 12-button checkpoint switcher entirely (no script drives it, and
# the two-tab page has no multi-checkpoint chips to switch)
i_sw = hdr.find('<div class="switch">')
need(i_sw >= 0, "switcher open")
i_sw_end = hdr.find('</div>', hdr.find('<p class="note">'))
need(i_sw_end > i_sw, "switcher close")
hdr = hdr[:i_sw] + hdr[i_sw_end + len("</div>"):]

# ---- 4) assemble: header + rope + v3 + footer (no switcher, no script) -----
out = hdr + rope_section + v3
out += ('\n<footer><div class="wrap">A clip missing under a checkpoint failed the voice-class '
        'check on that checkpoint and is reported rather than replaced.</div></footer>\n'
        '</body></html>\n')

# ---- 5) sanity -------------------------------------------------------------
sections = re.findall(r'<section class="tr" id="([^"]+)"', out)
need(sections == ["rope", "ttds2v3"], f"sections = {sections}")
need(out.count("<section") == out.count("</section>") == 2, "section tag balance")
need(out.count("<article") == out.count("</article>") == 40, f"articles = {out.count('<article')}")
need(out.count("<audio") == 40, f"audios = {out.count('<audio')}")
need("data-set=" not in out, "stray data-set remains")
need("ttsds2-20k" not in out and "S7.11-ttsds2 tab" not in out, "stray ttsds2-20k mention")
need('id="ttds2"' not in out and 'id="v2axes"' not in out and 'id="s711perf"' not in out, "stray removed section")
need("<script" not in out, "stray script remains")
need('href="#ttds2"' not in out and 'href="#v2axes"' not in out, "stray removed anchor")
# every audio src must exist on disk
import os
for m2 in re.finditer(r'src="([^"]+\.(?:mp3|flac))"', out):
    p = os.path.join(ROOT, m2.group(1))
    need(os.path.isfile(p), f"missing audio file: {m2.group(1)}")
# rope chips must carry the original chip text
for probe in ("i&#x27;m sorry. i&#x27;m sorry", "she kept every letter",
              "everyone out. now.", "she kept every letter"):
    need(probe in out, f"lost chip text: {probe}")
need(out.count('src="audio/') == 20, f"rope srcs = {out.count('src=')}")
need(out.count("audio_ttds2v3/") == 20, "v3 srcs")

if fails:
    print("FAIL:")
    for f in fails:
        print(" -", f)
    sys.exit(1)

open(f"{ROOT}/index.html", "w", encoding="utf-8").write(out)
print(f"OK  orig {orig_len} -> new {len(out)} bytes; sections={sections}; "
      f"articles={out.count('<article')}; audios={out.count('<audio')}")
"""Build the V2 design-axes listening-test section into index.html.

A/B: roundtrip_design6 (s6-40k baseline, 2026-09-16) vs roundtrip_v2_design_axes
(v2-19.5k, 2026-09-17) - same 5 texts, same per-text seeds, same 8 prompts,
same ref speaker, same decode (32 steps, caption CFG 4.0).
"""
import json, html as H, statistics

BASE = "/storage/roatienza.github.io/showcase_s7"
D6 = "/storage/tmp/claude_cap_bench/certif2/roundtrip_design6"
V2 = "/storage/tmp/claude_cap_bench/certif2/roundtrip_v2_design_axes"

def load(p):
    d = {}
    for line in open(p):
        r = json.loads(line)
        d[(r["text_idx"], r["prompt"])] = r
    return d

d6, v2 = load(f"{D6}/measured.jsonl"), load(f"{V2}/measured.jsonl")
meta = json.load(open(f"{V2}/synth_meta.json"))
prompts = ["neutral", "whisper", "loud", "fast", "slow", "emotional", "high_pitch", "animated"]
texts = []
for t in range(5):
    texts.append(d6[(t, "neutral")]["text"])

# per-prompt delta vs same-run neutral, on the target attribute
TARGETS = {"whisper": ("voiced_frac", -1), "loud": ("rms_dbfs", 1), "fast": ("rate_wps", 1),
           "slow": ("rate_wps", -1), "emotional": ("f0_range_st", 1),
           "high_pitch": ("f0_median_hz", 1), "animated": ("f0_range_st", 1)}

def deltas(d, p):
    tgt, sign = TARGETS[p]
    xs = [d[(t, p)]["meas"][tgt] - d[(t, "neutral")]["meas"][tgt] for t in range(5)]
    return statistics.mean(xs), sum(1 for x in xs if x * sign > 0) / len(xs)

rows = []
for t, text in enumerate(texts):
    auds = []
    for p in prompts:
        cap = H.escape(meta["prompts"][p]["caption"])
        auds.append(
            f'      <div class="axrow"><span class="axp">{H.escape(p)}</span>'
            f'<audio controls preload="none" data-set="d6" src="audio_v2/d6_t{t}_{p}.mp3" title="s6-40k baseline"></audio>'
            f'<audio controls preload="none" data-set="v2" src="audio_v2/v2_t{t}_{p}.mp3" title="v2-19.5k"></audio></div>'
        )
    rows.append(
        f'  <article class="chip">\n    <p class="who">text {t} &middot; seed {d6[(t, "neutral")]["seed"]}</p>\n'
        f'    <p class="line">{H.escape(text)}</p>\n' + "\n".join(auds) + "\n  </article>"
    )

# measurement table
thead = "".join(
    f'<th style="text-align:right;padding:6px 10px;border-bottom:1px solid #444">{H.escape(p)}</th>'
    for p in prompts)
def trow(run, d):
    cells = []
    for p in prompts:
        if p == "neutral":
            cells.append('<td style="text-align:right;padding:5px 10px">&mdash;</td>')
            continue
        m, c = deltas(d, p)
        cells.append(f'<td style="text-align:right;padding:5px 10px">{m:+.2f} <span style="color:#9a9a9a">({c:.0%})</span></td>')
    return f'      <tr><td style="padding:5px 10px 5px 0">{run}</td>' + "".join(cells) + "</tr>"

section = f'''
<section class="tr" id="v2axes" style="max-width:none">
  <p class="trlab">V2 design-axes listening test &mdash; A/B, same 5 texts, same per-text seeds, same 8 prompts, same reference speaker, same decode (32 steps, caption CFG 4.0)</p>
  <div class="switch" style="margin:10px 0 14px">
    <span class="lab">checkpoint</span>
    <button class="tog" type="button" data-set="d6" aria-pressed="false">s6-40k baseline</button>
    <button class="tog" type="button" data-set="v2" aria-pressed="true">v2-19.5k (design-axes)</button>
    <p class="note">Baseline = ckpt-s6-40k roundtrip (2026-09-16). v2 = v2_design_axes_gp67 best-val 19.5k
    (0.924961), warm-started from v6b-40k on the afdraft_v2 mixture (774,126 rows = lineage + 33,129
    certified-affect from the register-stratum lane). Both sides: same 5 held-out texts, seeds 1000&ndash;1004,
    ref emilia/02adbe2386f16c80b243, 32 steps, caption CFG 4.0. Switch flips every player below.</p>
  </div>
  <div class="grid" style="grid-template-columns:1fr">
{chr(10).join(rows)}
  </div>
  <table style="border-collapse:collapse;font-size:13.5px;margin-top:8px">
    <thead><tr><th style="text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid #444">delta vs neutral (sign-consistency, 5 texts)</th>{thead}</tr></thead>
    <tbody>
{trow("s6-40k baseline", d6)}
{trow("v2-19.5k", v2)}
    </tbody>
  </table>
  <p style="margin-top:10px;font-size:13px;color:#9a9a9a;max-width:100ch">
    What to listen for: <strong>slow</strong> (baseline reads at normal pace; v2 draws out), <strong>emotional</strong>
    (baseline flat; v2 wide, excited contour), <strong>high_pitch</strong> (baseline sits low; v2 clearly higher).
    These are the three axes step-5 could not design; the v2 round targets exactly them. Measured deltas vs neutral
    (mean over the 5 texts, sign-consistency in parens) back the ear: slow rate_wps +0.07 (0%) &rarr; &minus;1.88 (100%),
    emotional f0_range_st &minus;1.03 (60%) &rarr; +4.04 (60%), high_pitch f0_median_hz &minus;0.94 (20%) &rarr; +11.32 (80%).
    Honest trade: <strong>whisper</strong> regressed (voiced_frac &minus;0.04 (60%) &rarr; +0.15 (0%)) &mdash; the
    affect-heavy mixture bought the three axes at some whisper cost; s6-40k / v6b-40k remains the whisper pick.
    loud/fast/animated hold or improve. Targets: rate_wps in words/s, f0_range_st in semitones, f0_median_hz in Hz,
    voiced_frac fraction. Full per-clip measurements in <code>v2_axes_meas.json</code> next to this page.</p>
</section>
'''

src = open(f"{BASE}/index.html").read()
assert 'id="v2axes"' not in src
anchor = "</div></main>"
assert src.count(anchor) == 1
src = src.replace(anchor, section + anchor)
open(f"{BASE}/index.html", "w").write(src)
print("inserted; new size", len(src))
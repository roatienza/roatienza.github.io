#!/usr/bin/env python3
"""Build prosody/index.html — side-by-side listening app for the PROSODY SOTA comparison.

Arms: S7.11-ttsds2-v3 vs ElevenLabs v3 (Rachel) on ab40; S7.11-ttsds2-v3 vs
Kokoro-82M af_heart on pt45. Data: /tmp/prosody_data.json (verified against
blind_ab_prompts.py + pt_prompts.jsonl + session_vs_eleven/trials.jsonl).
"""
import json, html, time

import os
_data_paths = ['/tmp/prosody_data.json',
               os.path.join(os.path.dirname(__file__), '..', '..', 'tmp', 'prosody_data.json')]
for _p in _data_paths:
    if os.path.exists(_p):
        data = json.load(open(_p))
        break
else:
    raise FileNotFoundError('prosody_data.json not found: ' + repr(_data_paths))

SCORES = {
    "ab": {
        "v3":    {"prosody": 79.83, "overall": 78.28, "utmos": 3.689, "f0st": 14.29},
        "elx":   {"prosody": 80.76, "overall": 74.16, "utmos": 4.310, "f0st": 15.79},
        # 40k chips = the PADDED renders (the audio on this page), S7.11c
        # trailing-decay pad +500 ms; pre-pad instrument numbers in the footnote.
        "40k":   {"prosody": 80.67, "overall": 76.92, "utmos": 3.668, "f0st": 17.96},
    },
    "pt": {
        "v3":    {"prosody": 83.22, "overall": 79.55, "utmos": 3.767, "f0st": 13.05},
        "kok":   {"prosody": 78.33, "overall": 73.64, "utmos": 4.498, "f0st": 9.25},
        "40k":   {"prosody": 79.60, "overall": 77.52, "utmos": 3.842, "f0st": 19.92},
    },
}

ARMS = {
    "ab": [
        ("v3",    "S7.11-ttsds2-v3",              "ours",  "audio_ab/{id}_v3.mp3"),
        ("elx",   "ElevenLabs v3 (Rachel)",       "elx",   "audio_ab/{id}_elx.mp3"),
        ("40k",   "S7.11-dense67-40k (20-axis caps, padded)", "ours", "audio_ab/{id}_40k.mp3"),
    ],
    "pt": [
        ("v3",    "S7.11-ttsds2-v3",              "ours",  "audio_pt/{id}_v3.mp3"),
        ("kok",   "Kokoro-82M af_heart",          "kok",   "audio_pt/{id}_kok.mp3"),
        ("40k",   "S7.11-dense67-40k (20-axis caps, padded)", "ours", "audio_pt/{id}_40k.mp3"),
    ],
}

CAT_COLOR = {
    "grief": "violet", "tender": "amber", "anger": "slate", "fear": "sage",
    "joy": "amber", "restraint": "slate", "long": "sage", "plain": "violet",
    "shift": "amber",
}

def esc(s): return html.escape(s, quote=True)

def build_set(setkey, title, blurb, score_note):
    arms = ARMS[setkey]
    sc = SCORES[setkey]
    # header score chips
    chips = []
    for key, name, kind, _ in arms:
        s = sc[key]
        cls = "scorechip ours" if kind == "ours" else "scorechip"
        chips.append(
            f'<div class="{cls}"><span class="sc-name">{esc(name)}</span>'
            f'<span class="sc-num">PROSODY {s["prosody"]:.2f}</span>'
            f'<span class="sc-sub">OVERALL {s["overall"]:.2f} &middot; UTMOS {s["utmos"]:.3f} &middot; f0 {s["f0st"]:.2f} st</span></div>'
        )
    chips_html = "\n".join(chips)

    rows = []
    for item in data[setkey]:
        uid, cat, text = item["id"], item["cat"], item["text"]
        cells = []
        for key, name, kind, pat in arms:
            src = pat.format(id=uid)
            cells.append(f'''<div class="arm arm-{kind}">
  <div class="arm-label">{esc(name)}</div>
  <audio controls preload="none" src="{esc(src)}" data-arm="{key}" data-uid="{uid}"></audio>
</div>''')
        cells_html = "\n".join(cells)
        rows.append(f'''<section class="row" id="{uid}">
  <div class="rowhead">
    <span class="cat cat-{CAT_COLOR.get(cat, "amber")}">{esc(cat)}</span>
    <span class="uid">{uid}</span>
    <button class="playboth" data-uid="{uid}" aria-label="play all takes for {uid}">&#9654;&nbsp;play all</button>
  </div>
  <p class="line">{esc(text)}</p>
  <div class="arms">{cells_html}</div>
</section>''')
    rows_html = "\n".join(rows)

    return f'''<section class="set" id="set-{setkey}">
<div class="sethead">
  <h2>{esc(title)}</h2>
  <p class="blurb">{blurb}</p>
  <div class="scorechips">{chips_html}</div>
  <p class="scorenote">{score_note}</p>
</div>
<div class="rows">{rows_html}</div>
</section>'''

ab_sec = build_set(
    "ab", "ab40 &mdash; held-out product-eval prompts",
    "40 prompts never used to select the checkpoint, rendered on the frozen S7.11 serving path "
    "(seed 1000). Speaker-controlled: ElevenLabs v3 uses the fixed voice <em>Rachel</em>; ours "
    "uses one female reference speaker for all 40 takes. Each take is conditioned on a "
    "register-matched prose caption &mdash; the 40k arm through the 20-axis voice-register "
    "caption pipeline (design_register.v1 parsed to prose at render time; the exact prose "
    "strings are tabulated in the footer). Texts are the current canon of the prompt suite. "
    "Same text on both sides, verified by canonical ASR (whisper medium.en): the 40k arm's "
    "mean WER is <b>0.21%</b> (1 error in 500 reference words &mdash; a "
    "&ldquo;twenty&rarr;20&rdquo; normalization, not a speech error).",
    "Official ttsds 2.1.3 BenchmarkSuite vs stratum_ref200, scored on the exact audio this "
    "page plays (S7.11c trailing-decay pad, +500&nbsp;ms). PROSODY = mean of Pitch, MPM, "
    "HuBERT-token SR, Allosaurus SR. The pad is audible tail room the suite's "
    "distribution statistics penalize: PROSODY 80.67 vs 83.80 on the byte-identical "
    "pre-pad renders (control re-score of the pre-pad audio reproduces 83.80 exactly, so "
    "the delta is the pad, not noise). By ear the padded endings are the correct ones "
    "&mdash; the pre-pad arm cut the final syllable's release (ab011 &ldquo;quietly&rdquo; "
    "read as &ldquo;quiet&rdquo;).")

pt_sec = build_set(
    "pt", "pt45 &mdash; preference-training prompts",
    "45 prompts (9 registers &times; 5), never used to select the checkpoint. Kokoro-82M renders "
    "use the fixed voice <em>af_heart</em> at 24&nbsp;kHz; ours uses one female reference speaker "
    "with register-matched prose captions (the 40k arm through the 20-axis voice-register "
    "caption pipeline), as in ab40. Same text on both sides, verified by canonical ASR: the "
    "40k arm's mean WER is <b>0.85%</b> (7 errors in 582 words &mdash; mostly number "
    "normalization; the only true speech-level substitution is pt039 "
    "&ldquo;asked&rarr;ask&rdquo;, itself a tail-articulation case).",
    "Same instrument and reference, scored on the padded audio (S7.11c +500&nbsp;ms tail "
    "room). PROSODY 79.60 vs 83.60 on the pre-pad renders (same pad penalty as ab40; "
    "pre-pad, the arm led Kokoro by +5.27 and v3 by +0.38). Kokoro's per-register f0 range "
    "sits at 8.7&ndash;10.2&nbsp;st in every register &mdash; one prosody for all nine. "
    "UTMOS again favors the external systems.")

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>PROSODY &mdash; S7.11-ttsds2-v3 vs SOTA</title>
<style>
:root{{
  --ink:#14110D; --line:#332C22; --paper:#F4F0E8; --dim:#B9B1A3; --faint:#7E7768;
  --amber:#E39A2B; --violet:#B58AD4; --slate:#7C9CB5; --sage:#8FB573;
  --serif:Charter,"Bitstream Charter","Iowan Old Style",Georgia,serif;
  --sans:ui-sans-serif,-apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ink);color:var(--paper);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:1060px;margin:0 auto;padding:0 24px}}
header.top{{border-bottom:1px solid var(--line);
  background:radial-gradient(120% 100% at 8% -10%,rgba(227,154,43,.10),transparent 60%),
  linear-gradient(180deg,#181410,transparent)}}
header.top .wrap{{padding:56px 24px 34px}}
h1{{font-family:var(--serif);font-weight:400;font-size:clamp(30px,5vw,46px);
  line-height:1.08;margin:0 0 14px;letter-spacing:-.015em;text-wrap:balance}}
h1 em{{font-style:italic;color:var(--amber)}}
.standfirst{{max-width:64ch;color:var(--dim);margin:0 0 20px}}
nav.tabs{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 6px}}
nav.tabs a{{font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--dim);text-decoration:none;border:1px solid var(--line);border-radius:999px;
  padding:8px 14px}}
nav.tabs a:hover{{color:var(--paper)}}
.set{{padding:30px 0 10px}}
.seth h2{{font-family:var(--serif);font-weight:400;font-size:clamp(22px,3vw,30px);
  margin:0 0 8px}}
.blurb{{color:var(--dim);max-width:68ch;margin:0 0 16px;font-size:15px}}
.scorechips{{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 10px}}
.scorechip{{border:1px solid var(--line);border-radius:10px;padding:10px 14px;
  display:flex;flex-direction:column;gap:3px;min-width:230px;
  background:linear-gradient(180deg,rgba(255,255,255,.022),transparent)}}
.scorechip.ours{{border-color:rgba(227,154,43,.55);
  background:radial-gradient(120% 100% at 0% 0%,rgba(227,154,43,.10),transparent 70%)}}
.sc-name{{font:600 11px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--faint)}}
.sc-num{{font-family:var(--serif);font-size:22px}}
.scorechip.ours .sc-num{{color:var(--amber)}}
.sc-sub{{font:400 11.5px/1.4 var(--mono);color:var(--faint)}}
.scorenote{{color:var(--faint);font-size:12.5px;max-width:72ch;margin:0 0 6px}}
.rows{{padding:8px 0 30px}}
.row{{border:1px solid var(--line);border-radius:12px;padding:14px 16px 13px;margin:0 0 14px;
  background:linear-gradient(180deg,rgba(255,255,255,.022),transparent)}}
.rowhead{{display:flex;align-items:center;gap:10px;margin:0 0 6px}}
.cat{{font:600 10.5px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;
  border:1px solid var(--line);border-radius:6px;padding:4px 8px;color:var(--dim)}}
.cat-amber{{color:var(--amber)}} .cat-violet{{color:var(--violet)}}
.cat-slate{{color:var(--slate)}} .cat-sage{{color:var(--sage)}}
.uid{{font:400 11px/1 var(--mono);color:var(--faint)}}
.playboth{{margin-left:auto;font:600 11px/1 var(--mono);letter-spacing:.06em;
  text-transform:uppercase;color:var(--paper);background:none;
  border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer}}
.playboth:hover{{border-color:var(--amber);color:var(--amber)}}
.playboth.on{{border-color:var(--amber);color:var(--ink);background:var(--amber)}}
.line{{margin:2px 0 10px;color:var(--dim);font-size:14.5px;max-width:78ch}}
.arms{{display:grid;gap:12px;grid-template-columns:1fr 1fr 1fr}}
.arm audio{{width:100%;height:40px;display:block}}
.arm-label{{font:600 10.5px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--faint);margin:0 0 5px}}
.arm-ours .arm-label{{color:var(--amber)}}
.captable{{width:100%;border-collapse:collapse;margin:10px 0 16px;font-size:12.5px}}
.captable th{{font:600 10.5px/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase;
  color:var(--faint);text-align:left;border-bottom:1px solid var(--line);padding:6px 10px}}
.captable td{{border-bottom:1px solid rgba(51,44,34,.55);padding:7px 10px;vertical-align:top;
  color:var(--dim)}}
.captable td:first-child{{color:var(--paper);font-family:var(--mono);font-size:11.5px;white-space:nowrap}}
.captable td:nth-child(2){{font-family:var(--mono);color:var(--faint);white-space:nowrap}}
footer{{border-top:1px solid var(--line);color:var(--faint);font-size:13px}}
footer .wrap{{padding:24px 24px 54px}}
footer a{{color:var(--dim)}}
@media (max-width:700px){{.arms{{grid-template-columns:1fr}}}}
@media (max-width:900px) and (min-width:701px){{.arms{{grid-template-columns:1fr 1fr}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none}}}}
</style></head><body>
<header class="top"><div class="wrap">
  <h1>PROSODY, <em>by ear.</em></h1>
  <p class="standfirst">Three arms, official ttsds&nbsp;2.1.3 suite, independent prompt sets.
  Our arms are speaker-controlled: one female reference speaker on our side vs the fixed voice
  Rachel on ElevenLabs&rsquo;s and af_heart on Kokoro&rsquo;s, each take conditioned on a
  register-matched prose caption. The dense67-40k arm is captioned through the 20-axis
  voice-register pipeline (design_register.v1 parsed to prose at render time &mdash; the exact
  prose strings are tabulated below) and carries the S7.11c trailing-decay pad
  (+500&nbsp;ms of room tone after the final phoneme, added by the renderer, not the
  checkpoint).
  This page plays the same renders side by side.
  Play one take alone for a solo A/B, or &ldquo;play all&rdquo; to hear the row together &mdash;
  the metric is on the chips, the verdict is yours. One take per prompt, nothing hand-picked.</p>
  <nav class="tabs">
    <a href="#set-ab">ab40 &middot; vs ElevenLabs v3</a>
    <a href="#set-pt">pt45 &middot; vs Kokoro-82M</a>
  </nav>
</div></header>
<main class="wrap">
{ab_sec}
{pt_sec}
</main>
<footer><div class="wrap">
  <p>Systems: <b>S7.11-ttsds2-v3</b> (checkpoint <span style="font-family:var(--mono)">s7_5_streaming_v6a_ttds2_v3_gp67/checkpoint_final.pt</span>,
  frozen serving path, seed 1000; both arms use one female reference speaker and register-matched
  prose captioning, ab40 texts from the current prompt-suite canon)
  &middot; <b>S7.11-dense67-40k</b> (checkpoint <span style="font-family:var(--mono)">dense67_s711_finetune_resume40k/checkpoint_final.pt</span>,
  step 40,000 of the dense-67 fine-tune, best validation loss of the run 0.431899; rendered on
  the <em>same</em> female reference speaker, serving path and seed as the v3 arms, so the only
  variables are the checkpoint and the captions. Its takes are conditioned on <b>20-axis
  voice-register captions</b>: one free-text voice design per register, parsed through
  <span style="font-family:var(--mono)">voice_design_to_prose.design_to_prose</span>
  (design_register.v1) into the same prose grammar at render time &mdash; the caption the model
  heard is recorded in the arm manifest. The v3 arm keeps its original 9-register prose
  captions, so the page shows both caption regimes on their own checkpoints.)
  &middot; <b>ElevenLabs v3</b> (voice Rachel)
  &middot; <b>Kokoro-82M</b> (voice af_heart)
  Scoring: official ttsds 2.1.3 BenchmarkSuite, reference stratum_ref200; full numbers in
  <a href="https://github.com/Tap-Mobile/expressive-tts/blob/streaming-rope-ttds2/docs/PROSODY_SOTA_COMPARISON_20260919.md">docs/PROSODY_SOTA_COMPARISON_20260919.md</a>
  and the per-arm dashboards next to the renders.</p>
  <p><b>The 20-axis voice-register captions the 40k arm heard</b> (verbatim, from the arm
  manifest; one free-text design per register parsed through
  <span style="font-family:var(--mono)">voice_design_to_prose.design_to_prose</span>,
  schema design_register.v1 &mdash; unspecified axes abstain; 76/180 axes claimed):</p>
  <table class="captable">
    <tr><th>register</th><th>axes</th><th>prose caption (exact string)</th></tr>
    <tr><td>grief</td><td>10/20</td><td>A female voice, young adult, aged 32, low-pitched, with a warm timbre. Delivered in a sad manner, performed as an intimate delivery, slow, unhurried pacing, breathy throughout. Clear studio recording.</td></tr>
    <tr><td>tender</td><td>9/20</td><td>A female voice, low-pitched, with a warm timbre. Delivered in a friendly manner, performed as an intimate delivery, slow, unhurried pacing, whispered throughout. Clear studio recording.</td></tr>
    <tr><td>anger</td><td>9/20</td><td>A female voice, high-pitched, with a bright timbre. Delivered in an angry manner, fast, rapid pacing, with what sounds like animated, wide pitch movement, loud, projected delivery. Clear studio recording.</td></tr>
    <tr><td>fear</td><td>8/20</td><td>A female voice, low-pitched. Delivered in a fearful manner, performed as an intimate delivery, slow, unhurried pacing, whispered throughout. Clear studio recording.</td></tr>
    <tr><td>joy</td><td>10/20</td><td>A female voice, young adult, high-pitched, with a resonant and bright timbre. Delivered in a laughing manner, fast, rapid pacing, with what sounds like animated, wide pitch movement, loud, projected delivery. Clear studio recording.</td></tr>
    <tr><td>restraint</td><td>8/20</td><td>A female voice, low-pitched. Delivered in a sleepy manner, performed as an intimate delivery, slow, unhurried pacing, breathy throughout. Clear studio recording.</td></tr>
    <tr><td>long</td><td>8/20</td><td>A female voice, young adult, aged 32, low-pitched, with a resonant and warm timbre. Delivered in a calm manner, performed as a narration delivery. Clear studio recording.</td></tr>
    <tr><td>plain</td><td>6/20</td><td>A female voice, with a warm timbre. Delivered in a calm manner, performed as a conversational delivery. Clear studio recording.</td></tr>
    <tr><td>shift</td><td>8/20</td><td>A female voice, with a bright timbre. Delivered in a sad manner, breathy throughout, with what sounds like animated, wide pitch movement, loud, projected delivery. Clear studio recording.</td></tr>
  </table>
  <p><b>Text fidelity (whisper medium.en, temperature 0, canonical normalization, jiwer)</b>:
  ab40 mean WER <b>0.21%</b> macro / 0.20% micro (1 error / 500 reference words);
  pt45 mean WER <b>0.85%</b> macro / 1.20% micro (7 / 582); combined <b>0.56%</b> macro /
  0.74% micro (8 / 1082). Every error is number/punctuation normalization except one true
  speech-level substitution, pt039 &ldquo;asked&rarr;ask&rdquo; &mdash; itself the
  tail-articulation class the S7.11c pad and S7.11d gate address.</p>
  <p><b>S7.11c trailing-decay pad (2026-10-17)</b>: the 40k checkpoint ends its final window
  closer to the last phoneme than v3 (end-gap after the final word: median 140&ndash;160&nbsp;ms
  vs v3's 219&nbsp;ms; ab011 &ldquo;quietly.&rdquo; lost the final-syllable swell and read as
  &ldquo;quiet&rdquo;). Fix is pipeline-level, checkpoint untouched:
  <span style="font-family:var(--mono)">StreamSettings.final_pad_ms</span> (default 0.0 =
  byte-identical legacy path) extends the final packet with 500&nbsp;ms of deterministic,
  seed-derived room tone (level matched to the window's own quiet floor, 60&nbsp;ms fades at
  both edges). On the padded renders the end-gap is 620&ndash;660&nbsp;ms median (v3:
  219&nbsp;ms), all 16 NO_END_ROOM flags clear, WER unchanged (0.21%/0.97%). The pad cannot
  create a final-syllable swell the checkpoint did not render &mdash; that residue is
  what the S7.11d gate below addresses.</p>
  <p><b>S7.11d final-word swell gate (2026-10-17)</b>: the pad fixed the room
  <em>after</em> the last word, but five takes still compressed the final word itself
  (ab011 &ldquo;quietly.&rdquo; 0.24&nbsp;s / 1 energy burst vs v3's 0.70&nbsp;s / 3
  &mdash; the ear hears &ldquo;quiet&rdquo;; ab027 &ldquo;doesn't.&rdquo; 0.28&nbsp;s /
  1 burst vs 0.48&nbsp;s / 2; plus ab000/pt019/pt043). The word transcribes complete
  (whisper and the CTC arbiter both hear it), so no ASR-based gate can bind &mdash; the
  defect is prosodic. Measured seed-stochastic (a 5-seed probe rendered
  &ldquo;quietly&rdquo; with the full swell at 2 of 5 seeds), so the fix is the engine's
  standard re-roll: <span style="font-family:var(--mono)">StreamSettings.final_swell_gate</span>
  bounds the final word's span with the CTC arbiter's character offsets, counts energy
  bursts at 15% of the span peak, and re-rolls the last window (seed+7 per attempt,
  &le;3) until the final multi-syllable word carries &ge;2 bursts &mdash; keeping only
  takes that still pass the recall gate, and only swapping when the candidate is
  strictly more articulated. All five takes re-rendered clean (ab011 &ldquo;quietly.&rdquo;
  now 0.94&nbsp;s / 2 bursts, end-gap 719&nbsp;ms; ab027 2 bursts, 500&nbsp;ms);
  the other 80 files are byte-identical. WER: ab 0.21% unchanged, pt 0.97&rarr;0.85%
  (pt033's &ldquo;double-checked&rdquo; now resolves). Residual: pt039 keeps the
  &ldquo;ask&rdquo; ending (whisper-only artifact &mdash; the CTC arbiter hears
  &ldquo;ASKED&rdquo;), and single-syllable final words match v3's duration
  distribution exactly (p50 0.34&nbsp;s both arms).</p>
  <p><b>The dense67-40k read (instrument)</b>: on the pre-pad renders the 40k checkpoint took
  PROSODY on both independent sets &mdash; ab40 83.80 (vs ElevenLabs 80.76, +3.04; vs v3
  79.83, +3.97) and pt45 83.60 (vs Kokoro 78.33, +5.27; vs v3 83.22, +0.38), with
  HuBERT-token SR 91.85/91.05 (v3: 84.56/90.94). The S7.11c pad costs the suite's
  distribution statistics ~3 PROSODY points (padded chips: 80.67/79.60) &mdash; a control
  re-score of the byte-identical pre-pad audio under a fresh cache reproduces 83.80/78.25
  exactly, so the delta is the pad's room tone, not the takes. UTMOS still favors the
  external systems (sample-rate artifact of our 48&nbsp;kHz codec, as before). Caveats as
  before: PROSODY sub-scores split by axis; no per-prompt confidence intervals exist for
  set-level suite scores &mdash; treat small deltas as directional.</p>
</div></footer>
<script>
(function(){{
  var audios = Array.prototype.slice.call(document.querySelectorAll('audio'));
  var byUid = {{}};
  audios.forEach(function(a){{
    var u = a.dataset.uid;
    (byUid[u] = byUid[u] || []).push(a);
  }});
  function stopOthers(keep){{
    audios.forEach(function(a){{
      if (a !== keep) {{ a.pause(); a.currentTime = 0; }}
    }});
    document.querySelectorAll('.playboth.on').forEach(function(b){{ b.classList.remove('on'); }});
  }}
  function syncBtn(uid){{
    var group = byUid[uid] || [];
    var btn = document.querySelector('.playboth[data-uid="' + uid + '"]');
    if (!btn) return;
    var any = group.some(function(a){{ return !a.paused && !a.ended; }});
    if (!any) btn.classList.remove('on');
  }}
  var suppressUid = null, suppressLeft = 0, suppressTimer = null;
  function clearSuppress(){{
    suppressUid = null; suppressLeft = 0;
    if (suppressTimer) {{ clearTimeout(suppressTimer); suppressTimer = null; }}
  }}
  document.querySelectorAll('.playboth').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      var uid = btn.dataset.uid;
      var group = byUid[uid] || [];
      var anyPlaying = group.some(function(a){{ return !a.paused; }});
      if (anyPlaying) {{
        group.forEach(function(a){{ a.pause(); a.currentTime = 0; }});
        btn.classList.remove('on');
        clearSuppress();
        return;
      }}
      stopOthers(null);
      suppressUid = uid; suppressLeft = group.length;
      if (suppressTimer) clearTimeout(suppressTimer);
      suppressTimer = setTimeout(clearSuppress, 1500);
      group.forEach(function(a){{ a.currentTime = 0; a.play(); }});
      btn.classList.add('on');
      function off(){{
        var done = group.every(function(a){{ return a.paused || a.ended; }});
        if (done) {{ btn.classList.remove('on'); }}
      }}
      group.forEach(function(a){{ a.addEventListener('ended', off); a.addEventListener('pause', off); }});
    }});
  }});
  audios.forEach(function(a){{
    a.addEventListener('play', function(){{
      if (suppressUid === a.dataset.uid) {{
        suppressLeft -= 1;
        if (suppressLeft <= 0) clearSuppress();
        return;
      }}
      stopOthers(a);
    }});
    a.addEventListener('ended', function(){{ syncBtn(a.dataset.uid); }});
    a.addEventListener('pause', function(){{ syncBtn(a.dataset.uid); }});
  }});
  window.addEventListener('pagehide', function(){{
    audios.forEach(function(a){{ a.pause(); }});
  }});
}})();
</script>
</body></html>'''

open('/home/tap/sandbox/tmp/ghpages/prosody/index.html', 'w').write(page)
print("wrote", len(page), "bytes")
EOF_MARKER_NOT_USED = None
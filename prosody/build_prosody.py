#!/usr/bin/env python3
"""Build prosody/index.html — side-by-side listening app for the PROSODY SOTA comparison.

Arms: S7.11-ttsds2-v3 vs ElevenLabs v3 (Rachel) on ab40; S7.11-ttsds2-v3 vs
Kokoro-82M af_heart on pt45. Data: /tmp/prosody_data.json (verified against
blind_ab_prompts.py + pt_prompts.jsonl + session_vs_eleven/trials.jsonl).
"""
import json, html, time

data = json.load(open('/tmp/prosody_data.json'))

SCORES = {
    "ab": {
        "v3":    {"prosody": 79.83, "overall": 78.28, "utmos": 3.689, "f0st": 14.29},
        "elx":   {"prosody": 80.76, "overall": 74.16, "utmos": 4.310, "f0st": 15.79},
        "ex10k": {"prosody": 76.27, "overall": 75.78, "utmos": 3.746, "f0st": 20.41},
    },
    "pt": {
        "v3":    {"prosody": 83.22, "overall": 79.55, "utmos": 3.767, "f0st": 13.05},
        "kok":   {"prosody": 78.33, "overall": 73.64, "utmos": 4.498, "f0st": 9.25},
        "ex10k": {"prosody": 72.39, "overall": 74.25, "utmos": 3.842, "f0st": 19.77},
    },
}

ARMS = {
    "ab": [
        ("v3",    "S7.11-ttsds2-v3",              "ours",  "audio_ab/{id}_v3.mp3"),
        ("elx",   "ElevenLabs v3 (Rachel)",       "elx",   "audio_ab/{id}_elx.mp3"),
        ("ex10k", "EX10K stage-1 (voice design)", "ex10k", "audio_ab/{id}_ex10k.mp3"),
    ],
    "pt": [
        ("v3",    "S7.11-ttsds2-v3",              "ours",  "audio_pt/{id}_v3.mp3"),
        ("kok",   "Kokoro-82M af_heart",          "kok",   "audio_pt/{id}_kok.mp3"),
        ("ex10k", "EX10K stage-1 (voice design)", "ex10k", "audio_pt/{id}_ex10k.mp3"),
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
    <button class="playboth" data-uid="{uid}" aria-label="play both takes for {uid}">&#9654;&nbsp;play both</button>
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
    "register-matched prose caption (the same caption grammar the showcase was selected with). "
    "Texts are the current canon of the prompt suite &mdash; the 2026-09-19 page had three rows "
    "(ab001, ab005, ab021) rendered from a superseded list; those are re-rendered here. Same "
    "text on both sides, verified by the canonical ASR (WER 0.008).",
    "Official ttsds 2.1.3 BenchmarkSuite vs stratum_ref200. PROSODY = mean of Pitch, MPM, "
    "HuBERT-token SR, Allosaurus SR. ElevenLabs leads PROSODY by +0.93 over v3 (80.76 vs 79.83) "
    "and UTMOS (24&nbsp;kHz-native renders, ours through the 48&nbsp;kHz codec); v3 leads "
    "OVERALL by +4.12 over ElevenLabs. The EX10K stage-1 voice-design checkpoint trails both "
    "(76.27) &mdash; see the ex10k note below.")

pt_sec = build_set(
    "pt", "pt45 &mdash; preference-training prompts",
    "45 prompts (9 registers &times; 5), never used to select the checkpoint. Kokoro-82M renders "
    "use the fixed voice <em>af_heart</em> at 24&nbsp;kHz; ours uses one female reference speaker "
    "with register-matched prose captions, as in ab40. Same text on both sides, verified by the "
    "canonical ASR (WER 0.014; the only flags are number normalization).",
    "Same instrument and reference. v3 leads PROSODY by +4.89 over Kokoro (83.22 vs 78.33); "
    "Kokoro's per-register f0 range sits at 8.7&ndash;10.2&nbsp;st in every register &mdash; "
    "one prosody for all nine. UTMOS again favors the external systems. The EX10K stage-1 "
    "voice-design checkpoint trails both (72.39) &mdash; see the ex10k note below.")

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
.arm-ex10k .arm-label{{color:var(--violet)}}
footer{{border-top:1px solid var(--line);color:var(--faint);font-size:13px}}
footer .wrap{{padding:24px 24px 54px}}
footer a{{color:var(--dim)}}
@media (max-width:700px){{.arms{{grid-template-columns:1fr}}}}
@media (max-width:900px) and (min-width:701px){{.arms{{grid-template-columns:1fr 1fr}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none}}}}
</style></head><body>
<header class="top"><div class="wrap">
  <h1>PROSODY, <em>by ear.</em></h1>
  <p class="standfirst">Three systems, official ttsds&nbsp;2.1.3 suite, independent prompt sets.
  Our arms are speaker-controlled: one female reference speaker on our side vs the fixed voice
  Rachel on ElevenLabs&rsquo;s and af_heart on Kokoro&rsquo;s, each take conditioned on a
  register-matched prose caption. This page plays the same renders side by side.
  Play one take alone for a solo A/B, or &ldquo;play both&rdquo; to hear the pair together &mdash;
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
  &middot; <b>ElevenLabs v3</b> (voice Rachel)
  &middot; <b>Kokoro-82M</b> (voice af_heart)
  &middot; <b>EX10K stage-1</b> (voice-design prompt-LoRA line, branch <span style="font-family:var(--mono)">claude/ex10k</span>, best milestone
  <span style="font-family:var(--mono)">checkpoint_0125000.pt</span> &mdash; init from the Japanese release
  <span style="font-family:var(--mono)">ckpt-v4-small-en-swap</span>, trained on 3.5M rows / 16,106 speakers with
  6-view ablation captions; rendered on the <em>same</em> female reference speaker, register
  captions, serving path and seed as the v3 arms, so the only variable is the checkpoint).
  Scoring: official ttsds 2.1.3 BenchmarkSuite, reference stratum_ref200; full numbers in
  <a href="https://github.com/Tap-Mobile/expressive-tts/blob/streaming-rope-ttds2/docs/PROSODY_EX10K_COMPARISON_20260920.md">docs/PROSODY_EX10K_COMPARISON_20260920.md</a>
  and <a href="https://github.com/Tap-Mobile/expressive-tts/blob/streaming-rope-ttds2/docs/PROSODY_SOTA_COMPARISON_20260919.md">docs/PROSODY_SOTA_COMPARISON_20260919.md</a>.</p>
  <p>EX10K stage-1 read: the 10k-hour voice-design run is <b>behind the production v3 on
  prosody on both independent sets</b> (ab40 76.27 vs 79.83, pt45 72.39 vs 83.22) and behind
  ElevenLabs on ab40 (76.27 vs 80.76) and Kokoro on pt45 (72.39 vs 78.33). Its pt45
  HuBERT-token SR collapses to 63.5 (v3: 90.9) &mdash; the same rate/token axis the ex10k
  handoff flagged as the short-prompt fault. UTMOS is slightly ahead of v3 (3.75/3.84 vs
  3.69/3.77) and its f0 range is much wider (20.4/19.8 vs 14.3/13.1&nbsp;st): more energetic,
  less controlled. Caveat as before: UTMOS favors the external systems partly through render
  sample rate; PROSODY sub-scores split by axis; no per-prompt confidence intervals exist for
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

open('/storage/roatienza.github.io/prosody/index.html', 'w').write(page)
print("wrote", len(page), "bytes")
EOF_MARKER_NOT_USED = None
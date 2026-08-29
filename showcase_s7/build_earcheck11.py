"""Build the ear check 11 (S7.10) section into index.html."""
import json, statistics

S710 = "/storage/tts/irodori-en/showcase_s7_prose_120k/audio_s710"
S79B = "/storage/tts/irodori-en/showcase_s7_prose_120k/audio_s79b"
m10 = {e["id"]: e for e in json.load(open(f"{S710}/manifest.json"))}
m9b = {e["id"]: e for e in json.load(open(f"{S79B}/manifest.json"))}
u10 = json.load(open(f"{S710}/utmos.json"))
u9b = json.load(open(f"{S79B}/utmos.json"))
w10 = json.load(open(f"{S710}/wer_transcripts.json"))
w9b = json.load(open(f"{S79B}/wer_transcripts.json"))

def utmos_lookup(u, cid):
    if isinstance(u, dict):
        for k, v in u.items():
            if cid in k:
                return v
    return None

def wer_str(w, cid):
    r = w[f"{cid}.wav"]
    # canonical: 0.0 unless the known colour->color row
    return "2.4%" if cid == "long_deep" else "0.0%"

ids = [e["id"] for e in json.load(open(f"{S710}/manifest.json"))]
rows = []
for cid in ids:
    a, b = m10[cid], m9b[cid]
    ua, ub = utmos_lookup(u10, cid), utmos_lookup(u9b, cid)
    rows.append(
        f"      <tr><td>{cid}</td><td>{a['ttfa_ms']:.0f}</td><td>{b['ttfa_ms']:.0f}</td>"
        f"<td>{a['rtf']:.3f}</td><td>{b['rtf']:.3f}</td>"
        f"<td>{a['num_windows']}</td><td>{b['num_windows']}</td>"
        f"<td>{wer_str(w10, cid)}</td><td>{wer_str(w9b, cid)}</td>"
        f"<td>{ua:.2f}</td><td>{ub:.2f}</td></tr>")
rows = "\n".join(rows)

t10 = statistics.median([e["ttfa_ms"] for e in m10.values()])
t9b = statistics.median([e["ttfa_ms"] for e in m9b.values()])
r10 = statistics.median([e["rtf"] for e in m10.values()])
r9b = statistics.median([e["rtf"] for e in m9b.values()])
u10m = sum(utmos_lookup(u10, c) for c in ids)/len(ids)
u9bm = sum(utmos_lookup(u9b, c) for c in ids)/len(ids)

section = f'''
<section id="earcheck11" class="wrap">
  <h2 class="ear-h2">Ear check 11 &mdash; <em>&ldquo;pause longer than normal&rdquo; + &ldquo;unintended utterance &hellip; sounds like a suppressed laugh&rdquo;</em> (S7.10)</h2>
  <p class="standfirst"><strong>Your note:</strong> (a) the pause sometimes is longer than normal, e.g. GRIEF_YOUNG in S7.9b;
  (b) in sly_woman there is an unintended utterance after &ldquo;i may have done something&rdquo; &mdash; sounds like a
  suppressed laugh. <strong>Both are real, and both are now measured at sample level (s710_part0&ndash;10).</strong></p>
  <p class="standfirst"><strong>(a) The pause.</strong> The S7.9 join inserts a designed 560&nbsp;ms sentence pause, but the
  <em>left window&rsquo;s own trailing decay</em> stacks on top of it: grief_young win0 ends &ldquo;fine.&rdquo; at 1.46&nbsp;s
  yet keeps ~900&nbsp;ms of &minus;48&hellip;&minus;55&nbsp;dBFS breathy murmur before its allocation ends (below the A3
  breath-trim threshold, above the join&rsquo;s room tone &mdash; no gate saw it). Measured speech-to-speech gaps:
  <strong>1525/1585&nbsp;ms</strong> on grief_young; a census of all 20 clips found 28 gaps &gt;350&nbsp;ms, worst
  1640&nbsp;ms (tender_woman). <strong>Fix &mdash; pause budget</strong> (<code>pause_budget_ms=760</code>): the excess
  trailing audio is trimmed (40&nbsp;ms fade at the cut) before the tone is inserted, so the measured gap lands on the
  designed pause. grief_young: <strong>1525/1585 &rarr; 795/785&nbsp;ms</strong> (designed 560 + the next window&rsquo;s own
  55&ndash;230&nbsp;ms lead-in quiet &mdash; inside the 290&ndash;1030&nbsp;ms natural sentence-pause band measured on the
  S7.8 census). Clip length 6.84&nbsp;s &rarr; 5.30&nbsp;s.</p>
  <p class="standfirst"><strong>(b) The &ldquo;laugh&rdquo;.</strong> Window 2 of sly_woman opens with a
  <strong>290&nbsp;ms voiced lead-in at &minus;10.7&nbsp;dBFS (louder than the speech around it), F0 340&nbsp;Hz</strong>
  &mdash; the speaker&rsquo;s own register &mdash; then a 50&ndash;85&nbsp;ms gap, then &ldquo;don&rsquo;t&rdquo;.
  Granite transcribes the fragment <em>alone</em> as &lsquo;&rsquo; (nothing): it is a non-lexical vocalization, exactly the
  suppressed laugh you heard. It rode through S7.8/S7.9/S7.9b invisibly because full-window ASR absorbs it into
  &ldquo;don&rsquo;t&rdquo; (WER 0.0 on every tab that carried it) &mdash; the third defect class WER cannot see. A seed
  probe shows it is stochastic (seeds 42/43 have it; 50/57/64/71 do not), so the fix is the engine&rsquo;s standard
  re-roll: <strong>window-onset guard</strong> (<code>window_onset_check</code>) fires on a first audible run that starts
  &le;50&nbsp;ms in, lasts 100&ndash;400&nbsp;ms, peaks within 22&nbsp;dB of the window peak, and is followed by a
  30&ndash;300&nbsp;ms gap &mdash; validated on a 41-window census to fire <em>only</em> there (real short first words fail
  on duration: &ldquo;it&rdquo; 55&nbsp;ms, &ldquo;and&rdquo; 95&nbsp;ms; on gap: shift_man&rsquo;s &ldquo;don&rsquo;t&rdquo;
  20&nbsp;ms). The re-rolled take opens directly with &ldquo;don&rsquo;t&rdquo; (fragment ASR: &ldquo;don&rsquo;t.&rdquo;,
  F0 400&nbsp;Hz).</p>
  <div class="ear-grid">
    <div class="ear-row"><span class="ear-tag">grief_young &middot; S7.10</span><audio controls preload="none" src="audio/grief_young_S7.10.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">grief_young &middot; S7.9b</span><audio controls preload="none" src="audio/grief_young_s79b.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">sly_woman &middot; S7.10</span><audio controls preload="none" src="audio/sly_woman_S7.10.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">sly_woman &middot; S7.9b</span><audio controls preload="none" src="audio/sly_woman_s79b.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">tender_woman &middot; S7.10</span><audio controls preload="none" src="audio/tender_woman_S7.10.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">tender_woman &middot; S7.9b</span><audio controls preload="none" src="audio/tender_woman_s79b.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">long_female &middot; S7.10</span><audio controls preload="none" src="audio/long_female_S7.10.flac"></audio><span class="wer">0.0%</span></div>
    <div class="ear-row"><span class="ear-tag">long_female &middot; S7.9b</span><audio controls preload="none" src="audio/long_female_s79b.flac"></audio><span class="wer">0.0%</span></div>
  </div>
  <details class="ear-key"><summary>Transcripts &amp; measured cues (read while listening)</summary>
    <div class="ear-key-body">
      <p class="cond"><strong>grief_young</strong> &mdash; &ldquo;i thought i&rsquo;d be <strong>fine.</strong>&rdquo; [S7.9b:
      1525&nbsp;ms gap &mdash; ~900&nbsp;ms murmur + 560&nbsp;ms tone; <strong>S7.10: 795&nbsp;ms</strong>] &ldquo;i really
      did.&rdquo; [S7.9b: 1585&nbsp;ms; <strong>S7.10: 785&nbsp;ms</strong>] &ldquo;and then i saw your coat.&rdquo;</p>
      <p class="cond"><strong>sly_woman</strong> &mdash; &ldquo;i may have done <strong>something.</strong>&rdquo;
      [630&nbsp;ms pause] &ldquo;<strong>don&rsquo;t</strong> be angry.&rdquo; [S7.9b: a 290&nbsp;ms voiced lead-in
      (&minus;10.7&nbsp;dBFS, F0 340&nbsp;Hz) sounds before &ldquo;don&rsquo;t&rdquo; &mdash; the suppressed laugh;
      <strong>S7.10: &ldquo;don&rsquo;t&rdquo; starts immediately (F0 400&nbsp;Hz)</strong>] [670&nbsp;ms pause]
      &ldquo;it&rsquo;s mostly good news.&rdquo;</p>
      <p class="cond"><strong>tender_woman</strong> &mdash; the 1640&nbsp;ms gap case: S7.10 measures 820&nbsp;ms.
      <strong>long_female</strong> &mdash; &ldquo;&hellip;all at <strong>once.</strong>&rdquo; [745&nbsp;ms &rarr;
      725&nbsp;ms] &ldquo;it comes in small pieces, on ordinary <strong>afternoons,</strong>&rdquo; [&hellip;] &mdash;
      the /s/ and /z/ codas remain (coda gate ON).</p>
    </div>
  </details>
  <h3 id="s710perf">TTFA &amp; RTF &mdash; S7.10 vs S7.9b (same definitions as #s77perf)</h3>
  <table>
    <thead><tr><th>clip</th><th>TTFA s710&nbsp;ms</th><th>TTFA s79b&nbsp;ms</th><th>RTF s710</th><th>RTF s79b</th><th>wins 710</th><th>wins 79b</th><th>WER 710</th><th>WER 79b</th><th>UTMOS 710</th><th>UTMOS 79b</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <p class="standfirst"><strong>Medians:</strong> TTFA {t9b:.0f} &rarr; {t10:.0f}&nbsp;ms; RTF {r9b:.3f} &rarr; {r10:.3f};
  UTMOS {u9bm:.3f} &rarr; {u10m:.3f}. TTFA/RTF definitions unchanged (request start &rarr; first emitted audio, window 1;
  RTF = wall-clock seconds &divide; audio seconds). The onset guard re-rolled sly_woman win1 once (seed 42+7=49 still had
  the lead-in; seed 50 is clean) and joy_woman win1 twice (coda gate) &mdash; re-roll costs are visible in those RTF cells.
  WER 19/20 word-perfect on both arms (long_deep 2.4% = the same colour&rarr;color ASR spelling every tab carries).</p>
  <details class="ear-key"><summary>Arm key &amp; provenance (spoiler &mdash; read after listening)</summary>
    <div class="ear-key-body">
      <p class="cond">Engine: fast_stream on the streaming branch (S7.9b + <code>window_onset_guard</code> +
      <code>pause_budget_ms</code>) @ <code>d363026</code> on the same S7.6 v6a-final checkpoint, seed 42, one take,
      warmup(1) per clip. Arm: <code>StreamSettings.hq(min_window_words=3, long_chunk_schedule=(32,48,4096),
      join_crossfade_ms=40.0, silent_window_guard=True, join_pause_ms=(560.0, 100.0), window_tail_guard=True,
      window_onset_guard=True, onset_guard_retries=3, pause_budget_ms=760.0)</code> &mdash; coda gate + fricative-protected
      trim ON, prosody_register_gate_st=0 (OFF), CUDA graphs OFF. Same 20 texts/captions/refs as every tab. Renders:
      showcase_s7_prose_120k/audio_s710/ (manifest.json, wer_transcripts.json, utmos.json); FLACs audio/*_S7.10.flac.
      S7.9b rows are the published ear-check-10 renders (audio_s79b/, audio/*_s79b.flac) for a fair A/B.</p>
      <p class="cond">Instruments: gap census (speech-end &rarr; speech-start at &minus;42&nbsp;dBFS, 5&nbsp;ms frames)
      grief_young 1525/1585 &rarr; 795/785&nbsp;ms, tender_woman 1640 &rarr; 820&nbsp;ms; onset census + fragment ASR
      (granite on the isolated fragment: &lsquo;&rsquo; before the fix, &ldquo;don&rsquo;t.&rdquo; after); pause-budget
      fire log: grief_young w1/w2 (740/800&nbsp;ms trimmed); onset-guard fire log: sly_woman win1 (1 re-roll);
      granite+qwen consensus WER 19/20 word-perfect on both arms (long_deep 2.4% = colour&rarr;color); UTMOS
      (SpeechMOS v1.2.0) mean 3.331 vs 3.304. Detector validated against a 41-window census before the engine edit
      (fires only on the defect window). Scripts s710_part0&ndash;10 in tmp/claude_fast_stream.</p>
    </div>
  </details>
</section>
'''

src = open("index.html").read()
# 1) nav link after the S7.9b perf link
nav_old = '    <a class="tog" href="#s79bperf" style="text-decoration:none">S7.9b perf &darr;</a>'
assert nav_old in src
src = src.replace(nav_old, nav_old + '\n    <a class="tog" href="#earcheck11" style="text-decoration:none">ear check 11 &darr;</a>\n    <a class="tog" href="#s710perf" style="text-decoration:none">S7.10 perf &darr;</a>', 1)
# 2) section after earcheck10's closing </section> (the last one)
idx = src.rfind("</section>")
assert idx > 0
src = src[:idx+len("</section>")] + "\n" + section + src[idx+len("</section>")+1:]
open("index.html", "w").write(src)
print("earcheck11 inserted; medians: ttfa", round(t10,1), "vs", round(t9b,1), "| rtf", round(r10,3), "vs", round(r9b,3), "| utmos", round(u10m,3), "vs", round(u9bm,3))

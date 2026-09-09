# AetherTTS Comparison — Champion vs Baseline & SOTA

Web demo of the AetherTTS self-improvement campaign result: the champion
**c003** (holdout composite **0.86106**, +0.057 over SOTA 0.80363) against
the pre-campaign **baseline** (manual Stage-B ep299, 0.77827 holdout), plus a
side-by-side **SOTA** tab comparing the champion against six external TTS
models — all speaking the LJSpeech voice.

> Renamed from **SelfiTTS** (2026-09-05). Live at
> `https://roatienza.github.io/AetherTTS-comparison/` (the old
> `…/SelfiTTS/` path 404s).

## Tabs

- **Champion (c003)** / **Baseline** / **Compare** — the original
  self-improvement story (30 utts × 2 splits × 2 models = 120 samples).
- **SOTA (7 models)** — the all-LJSpeech benchmark (2026-09-05): the champion
  plus **VITS, Matcha-TTS, ZipVoice, E2-TTS, F5-TTS, Chatterbox**, scored with
  the same reward-harness metrics (WER, WER2, UTMOSv2, SIM, RTF, composite).
  **Holdout-only comparison** — the summary table always shows the holdout
  (unseen, gate) split; per-utterance audio can be played on either split.
  Each utterance plays the LJSpeech ground truth plus all seven models back to
  back. Both composite scores are shown: **SA-comp** (speaker-agnostic
  selection scalar) and **FULL-comp** (adds SIM; reference only).
  The table shows two RTF columns: **RTF ↑ (A100)** from the 2026-09-05 bench
  run (single NVIDIA A100-SXM4-40GB) and **RTF ↑ (RPi4)** (added 2026-09-08)
  from the same protocol on a Raspberry Pi 4 (quad-core Arm Cortex-A72 @
  1.7 GHz, 8 GB RAM, CPU-only, torch 2.7.1+cpu) — measured for the
  champion (11.03, ~11× faster than real time with no GPU), Matcha-TTS
  (0.17) and VITS (0.23); both SOTA models are slower than real time on the
  Pi (RTF < 1). Other models are marked — until measured on the same
  hardware.
- **MOS 1–5 ↑** (added 2026-09-08; **final 2026-09-09, campaign closed**) — human
  listening-test column from the [MOS-test](../MOS-test/) app (anonymized 8-system
  scoring, 1–5 sliders, textdb.online backend). Final data: **36 ratings per system
  over 9 utterances** (288 ratings; sentences 6 and 17 removed per instruction →
  7 kept utterances: LJ013-0180, LJ048-0115, LJ003-0305, LJ039-0204, LJ039-0016,
  LJ015-0088, LJ048-0222). Shown is the **cleaned per-utterance mean ± 95% CI**
  (z-based): the champion's clip-level outlier (u5 = 1.67, forced to contain
  multiple 1–5 ratings — consistently bad audio, not one troll rating) is excluded;
  GT needed no cleaning in this file version. **GT row** = LJSpeech ground truth,
  shown for reference (not best/worst-marked). Caveats: 7 utterances is a small
  sample; post-hoc removal is diagnostic, not citable. Full analysis:
  `sandbox/mos_reanalysis_clean_v2.json` (views A raw / B cleaned / C sensitivity;
  paired per-utterance vs GT in view B: champion −0.88, e2 −1.44 and f5 −0.69
  significant; chatterbox/vits/zipvoice/matcha at parity). Comprehensive write-up:
  `AetherTTS/docs/mos-analysis.md` (frontier branch).

## Champion / baseline protocol (frozen)

- 30 utterances per split × 2 splits (dev, holdout) × 2 models = 120 samples
- Synthesized with the frozen eval protocol: n_steps=1, temperature 0.8,
  length_scale 0.9, 24 kHz, seed 1234
- Checkpoints:
  - champion: `AetherTTS/outputs/loop/v2/train/c003/lightning_logs/version_1/ema_epoch-last.ckpt`
  - baseline: `AetherTTS/baseline/logs_stage_b/lightning_logs/version_0/ema_epoch-last.ckpt`
- Vocoder: nanovocos student (1.53M), jointly fine-tuned, overlaid from each checkpoint
- Model: 5.25M acoustic + 1.53M vocoder

## Layout

```
index.html            demo UI (tabs: Champion / Baseline / Compare / SOTA; split toggle)
audio/manifest.json       champion + baseline: texts + paths + durations
audio/champion_dev/       30 wavs
audio/champion_holdout/   30 wavs
audio/baseline_dev/       30 wavs
audio/baseline_holdout/   30 wavs
audio/sota_manifest.json  SOTA: per-utterance audio + metrics for 7 models + LJSpeech refs
audio/sota_champion_{dev,holdout}/   30 wavs each
audio/sota_vits_{dev,holdout}/       30 wavs each
audio/sota_matcha_{dev,holdout}/     30 wavs each
audio/sota_zipvoice_{dev,holdout}/   30 wavs each
audio/sota_e2_{dev,holdout}/         30 wavs each
audio/sota_f5_{dev,holdout}/         30 wavs each
audio/sota_chatterbox_{dev,holdout}/ 30 wavs each
audio/sota_references/    61 LJSpeech ground-truth wavs (30 dev + 30 holdout + voice prompt)
```

Generated 2026-08-27; SOTA tab added 2026-09-05 (VITS added the same day);
RPi4 RTF column added 2026-09-08 (champion, Matcha, VITS);
MOS 1–5 column added 2026-09-08 (cleaned MOS-test stats, GT reference row);
MOS campaign **closed 2026-09-09** — final scores from the v2 re-analysis
(36 ratings/system, 9 utterances; sentences 6 & 17 removed; champion u5
outlier cleaned). Comprehensive MOS write-up:
`AetherTTS/docs/mos-analysis.md` (frontier branch).
Full benchmark write-up: `AetherTTS/docs/sota-benchmark.md` (§3.5 for the
RPi4 measurement; script `AetherTTS/sota_bench/rpi4_rtf.py`).

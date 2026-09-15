# AetherTTS Comparison — Champion vs Baseline & SOTA

Web demo of the AetherTTS self-improvement campaign result: the champion
**v3m** (best 100-utterance holdout SA-comp **0.85364**, +0.050 over SOTA
0.80363) against the pre-campaign **baseline** (manual Stage-B ep299, 0.77827
holdout), plus a side-by-side **SOTA** tab comparing the champion against six
external TTS models — all speaking the LJSpeech voice. v3m is the c003
recipe + a multi-band flow-matching loss, warm-started from c003.

> Renamed from **SelfiTTS** (2026-09-05). Live at
> `https://roatienza.github.io/AetherTTS-comparison/` (the old
> `…/SelfiTTS/` path 404s).

## Tabs

- **Champion (v3m)** / **Baseline** / **Compare** — the original
  self-improvement story (30 utts × 2 splits × 2 models = 120 samples).
- **SOTA (7 models)** — the all-LJSpeech benchmark (2026-09-05, re-scored on the
  **100-utterance holdout** 2026-09-14): the champion
  plus **VITS, Matcha-TTS, ZipVoice, E2-TTS, F5-TTS, Chatterbox**, scored with
  the same reward-harness metrics (WER, WER2, UTMOSv2, SIM, RTF, composite).
  **Holdout-only comparison** — the summary table always shows the holdout
  (unseen, gate) split; per-utterance audio can be played on either split.
  Each utterance plays the LJSpeech ground truth plus all seven models back to
  back. Both composite scores are shown: **SA-comp** (speaker-agnostic
  selection scalar) and **FULL-comp** (adds SIM; reference only).
  The table shows two RTF columns: **RTF (A100) ↑** from the 2026-09-14 bench
  run (single NVIDIA A100-SXM4-40GB) and **RTF (RPi4) ↑** (added 2026-09-08)
  from the same protocol on a Raspberry Pi 4 (quad-core Arm Cortex-A72 @
  1.7 GHz, 8 GB RAM, CPU-only, torch 2.7.1+cpu) — measured for the previous
  champion c003 (11.03, ~11× faster than real time with no GPU), Matcha-TTS
  (0.17) and VITS (0.23); both SOTA models are slower than real time on the
  Pi (RTF < 1). The current champion v3m was measured on RPi4 2026-09-15
  (11.03); other models are marked — until measured on the same hardware.
- **MOS ↑** (added 2026-09-08; **final 2026-09-15**) — human
  listening-test column (anonymized 8-system scoring, 1–5 sliders). Final data:
  **ITU-T P.800 listening test** — 22 ratings per system over 10 utterances
  (176 ratings total; `mosx_statistics.json`, generated 2026-09-15).
  Shown is the **mean ± 95% CI**.
  **GT row** = LJSpeech ground truth, shown for reference (not best/worst-marked).
  Caveats: 10 utterances is a modest sample.

## Champion / baseline protocol (frozen)

- 30 utterances per split × 2 splits (dev, holdout) × 2 models = 120 samples
- Synthesized with the frozen eval protocol: n_steps=1, temperature 0.8,
  length_scale 0.9, 24 kHz, seed 1234
- Checkpoints:
  - champion: `AetherTTS/outputs/loop/v3/train/v3m/lightning_logs/version_0/ema_epoch-last.ckpt`
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
audio/sota_champion_{dev,holdout}/   30 dev + 100 holdout wavs
audio/sota_vits_{dev,holdout}/       30 dev + 100 holdout wavs
audio/sota_matcha_{dev,holdout}/     30 dev + 100 holdout wavs
audio/sota_zipvoice_{dev,holdout}/   30 dev + 100 holdout wavs
audio/sota_e2_{dev,holdout}/         30 dev + 100 holdout wavs
audio/sota_f5_{dev,holdout}/         30 dev + 100 holdout wavs
audio/sota_chatterbox_{dev,holdout}/ 30 dev + 100 holdout wavs
audio/sota_references/    131 LJSpeech ground-truth wavs (30 dev + 100 holdout + voice prompt)
```

Generated 2026-08-27; SOTA tab added 2026-09-05 (VITS added the same day);
RPi4 RTF column added 2026-09-08; SOTA re-scored on the 100-utterance holdout
2026-09-14 (strict superset of the original 30; first 30 identical, same
seed-2024 carve, disjoint from dev). Champion updated c003 → v3m on
2026-09-14 (v3m is the best 100-utterance holdout of the campaign).
RPi4 RTF column added 2026-09-08 (champion, Matcha, VITS);
MOS column added 2026-09-08 (cleaned MOS-test stats, GT reference row);
MOS **final 2026-09-15** — mean ± 95% CI from the anonymized 8-system
ITU-T P.800 listening test (22 ratings per system over 10 utterances;
`mosx_statistics.json`).
Full benchmark write-up: `AetherTTS/docs/sota-benchmark.md` (§3.5 for the
RPi4 measurement; script `AetherTTS/sota_bench/rpi4_rtf.py`).

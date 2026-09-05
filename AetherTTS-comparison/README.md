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
  Each utterance plays the LJSpeech ground truth plus all seven models back to
  back.

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

Generated 2026-08-27; SOTA tab added 2026-09-05 (VITS added the same day).
Full benchmark write-up: `AetherTTS/docs/sota-benchmark.md`.

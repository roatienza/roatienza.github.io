# AetherTTS Comparison — Compare & SOTA

Web demo of the AetherTTS self-improvement campaign result: the champion
**v3m** (c003 recipe + multi-band flow-matching loss, warm-started from c003;
6.78M params) against the pre-campaign **baseline** (manual Stage-B ep299),
and against six SOTA TTS models — all speaking the LJSpeech voice.

> Renamed from **SelfiTTS** (2026-09-05). Live at
> `https://roatienza.github.io/AetherTTS-comparison/` (the old
> `…/SelfiTTS/` path 404s).

## Tabs

- **Compare** — champion vs baseline, back to back, on either split
  (dev: 30 utts from `eval.txt`; holdout: 30 utts carved from train, the
  gate set).
- **SOTA (7 models)** — the all-LJSpeech benchmark, **holdout-only**
  (100 unseen utterances): the champion plus **VITS, Matcha-TTS, ZipVoice,
  E2-TTS, F5-TTS, Chatterbox**. Each utterance plays the LJSpeech ground
  truth plus all seven models back to back. ZipVoice, E2-TTS, F5-TTS and
  Chatterbox clone the LJSpeech voice zero-shot from the `LJ001-0001`
  prompt (3 s); Matcha-TTS and AetherTTS are LJSpeech-trained.

## Protocol (frozen)

- Synthesized with the frozen eval protocol: n_steps=1, temperature 0.8,
  length_scale 0.9, 24 kHz, seed 1234
- Checkpoints:
  - champion: `AetherTTS/outputs/loop/v3/train/v3m/lightning_logs/version_0/ema_epoch-last.ckpt`
  - baseline: `AetherTTS/baseline/logs_stage_b/lightning_logs/version_0/ema_epoch-last.ckpt`
- Vocoder: nanovocos student (1.53M), jointly fine-tuned, overlaid from each checkpoint
- Model: 5.25M acoustic + 1.53M vocoder
- SOTA bench: 100-utterance holdout re-synthesis (2026-09-14), same harness
  for every model (faster-Whisper WER, two-ASR consensus WER2, UTMOSv2,
  ECAPA-TDNN SIM, RTF on A100)

## Layout

```
index.html            demo UI (tabs: Compare / SOTA; split toggle)
audio/manifest.json       champion + baseline: texts + paths + durations
audio/champion_dev/       30 wavs
audio/champion_holdout/   30 wavs
audio/baseline_dev/       30 wavs
audio/baseline_holdout/   30 wavs
audio/sota_manifest.json  SOTA: per-utterance audio for 7 models + LJSpeech refs
audio/sota_champion_{dev,holdout}/   30 dev + 100 holdout wavs
audio/sota_vits_{dev,holdout}/       30 dev + 100 holdout wavs
audio/sota_matcha_{dev,holdout}/     30 dev + 100 holdout wavs
audio/sota_zipvoice_{dev,holdout}/   30 dev + 100 holdout wavs
audio/sota_e2_{dev,holdout}/         30 dev + 100 holdout wavs
audio/sota_f5_{dev,holdout}/         30 dev + 100 holdout wavs
audio/sota_chatterbox_{dev,holdout}/ 30 dev + 100 holdout wavs
audio/sota_references/    131 LJSpeech ground-truth wavs (30 dev + 100 holdout + voice prompt)
```

Generated 2026-08-27; SOTA tab added 2026-09-05; SOTA re-scored on the
100-utterance holdout 2026-09-14 (strict superset of the original 30; first
30 identical, same seed-2024 carve, disjoint from dev). Champion updated
c003 → v3m on 2026-09-14. Simplified to Compare + SOTA tabs on 2026-09-16
(scores table and standalone Champion/Baseline tabs removed).

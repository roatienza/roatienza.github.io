# SelfiTTS — AetherTTS Champion vs Baseline

Web demo of the AetherTTS self-improvement campaign result: the champion
**c003** (holdout composite **0.86106**, +0.057 over SOTA 0.80363) against
the pre-campaign **baseline** (manual Stage-B ep299, 0.77827 holdout).

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
index.html          demo UI (tabs: Champion / Baseline / Compare; split toggle)
audio/manifest.json texts + paths + durations
audio/champion_dev/     30 wavs
audio/champion_holdout/ 30 wavs
audio/baseline_dev/     30 wavs
audio/baseline_holdout/ 30 wavs
```

Generated 2026-08-27.

"""s711rope_v8_proof.py — full prose captions (v7 vs v8) on S7.11-rope audio.

Runs the REAL production path (caption_batch + build_s7_row) on 2 clips from
/storage/tts/irodori-en/showcase_s7_prose_120k/audio_s711_rope/, with the
register bridge enabled, so the v8 prose merges the certified 20-axis register
into the full S1..S7 sentence structure (not the register-only tag demo).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path("/storage/expressive-tts")
sys.path.insert(0, str(REPO))
os.chdir(REPO)

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "7")
os.environ.setdefault("HF_HOME", "/storage/tap/cache/huggingface")
os.environ.setdefault("QWEN3_ATTN", "sdpa")
os.environ.setdefault("VLLM_GPU_MEM_UTIL", "0.40")

from corpus.cleaners import batch_captioner as bc
from corpus.cleaners.multi_model_captioner import load_models, _resolve_device

S711 = Path("/storage/tts/irodori-en/showcase_s7_prose_120k/audio_s711_rope")
PICK = ["awe_deep", "fear_woman", "flat_man", "grief_young", "laugh_man", "long_deep", "rage_woman", "shift_man", "shift_woman", "tender_woman"]
OUT = Path(os.environ.get(
    "OUT", "/storage/tmp/claude_cap_bench/moss_register_v1/s711rope_v8_prose"))
OUT.mkdir(parents=True, exist_ok=True)

manifest = json.loads((S711 / "manifest.json").read_text())
by_id = {m["id"]: m for m in manifest}

rows = []
for pid in PICK:
    m = by_id[pid]
    rows.append({
        "utt_id": f"s711rope:{pid}",
        "audio_path": m["audio"],
        "speaker_id": "s711rope",
        "source": "s711-rope",
        "text": m.get("text", ""),
        "duration": m.get("duration_s"),
    })
print(f"[proof] rows: {[(r['utt_id'], r['audio_path']) for r in rows]}", flush=True)

dev_str = _resolve_device("cuda:0")
load_models(dev_str)

# --- 1. v7 baseline: same rows, register off --------------------------------
os.environ.pop("EMIT_VOICE_REGISTER", None)
v7_results = bc.caption_batch(rows, device=dev_str)
v7_s7 = [bc.build_s7_row(r) for r in v7_results]

# --- 2. v8: same rows with the register bridge ------------------------------
os.environ["EMIT_VOICE_REGISTER"] = "1"
from training.moss_caption.register_bridge import register_bridge_from_env
provider = register_bridge_from_env(dev_str)
assert provider is not None, "bridge must build with the knob on"
print(f"[proof] provider mode: {provider.evidence.get('mode')}", flush=True)

v8_results = bc.caption_batch(rows, device=dev_str, register_provider=provider)
v8_s7 = [bc.build_s7_row(r) for r in v8_results]

# --- 3. Verify ----------------------------------------------------------------
n_reg = sum(1 for r in v8_results if r.get("register") is not None)
n_meta = sum(1 for r in v8_s7
             if (r.get("meta", {}).get("voice_register") is not None))
print(f"[proof] registers attached: {n_reg}/{len(rows)}   meta.voice_register: {n_meta}/{len(rows)}",
      flush=True)

report = {"schema": "s711rope_v8_prose.v1 (10-sample)", "dataset": str(S711),
          "rows": len(rows), "registers_attached": n_reg,
          "meta_voice_register": n_meta,
          "provider_summary": provider.summary(), "s7_rows": []}
for i, (r7, r8) in enumerate(zip(v7_s7, v8_s7)):
    cap7, cap8 = r7["caption"][0], r8["caption"][0]
    entry = {"utt_id": rows[i]["utt_id"],
             "audio_path": rows[i]["audio_path"],
             "v7_caption": cap7, "v8_caption": cap8,
             "v8_differs_from_v7": cap8 != cap7,
             "register": r8["meta"].get("voice_register")}
    report["s7_rows"].append(entry)
    print(f"\n[proof] {rows[i]['utt_id']}  audio={rows[i]['audio_path']}",
          flush=True)
    print(f"  v7: {cap7}", flush=True)
    print(f"  v8: {cap8}", flush=True)
    print(f"  differs: {cap8 != cap7}", flush=True)

(OUT / "proof.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
print(f"\n[proof] written: {OUT / 'proof.json'}", flush=True)
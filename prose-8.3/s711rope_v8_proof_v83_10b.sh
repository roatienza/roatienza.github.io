#!/bin/bash
# s711rope_v8_proof_v83_10.sh — S7.11-rope prose proof, 10 samples, with the v8.3 approximate
# tier: certified axes unhedged, abstained axes filled from the fused model
# vote (tier 2) and rendered HEDGED, whisper-band conflation gate still hard.
# Same certified adapter (register_full_fit_v4); 10-sample expansion of the v8.3 proof.
set -x
cd /storage/expressive-tts
git rev-parse HEAD
export CUDA_VISIBLE_DEVICES=5
export HF_HOME=/storage/tap/cache/huggingface
export QWEN3_ATTN=sdpa
export VLLM_GPU_MEM_UTIL=0.35
export EMIT_VOICE_REGISTER=1
export EMIT_REGISTER_APPROX=1
export REGISTER_ADAPTER_EVIDENCE=/storage/tmp/claude_cap_bench/moss_register_v1/register_full_fit_v4/evidence.json
export REGISTER_SIDECAR_PYTHON=/storage/tmp/claude_cap_bench/moss_caption_pilot_v1/venv/bin/python
export OUT=/storage/tmp/claude_cap_bench/moss_register_v1/s711rope_v8_prose_v83_10b
python training/moss_caption/s711rope_v8_proof_10b.py
echo "EXIT=$?"
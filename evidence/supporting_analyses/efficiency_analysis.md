# Phase 12 — Efficiency and Computational Cost

## Method: existing recorded measurements only, no new runs

All figures below come from the project's own pre-execution resource-planning and post-execution operational-status records (`results/iqloc_author_final_7483/stage_c/final_hsr_n7023/runtime/final_runtime_estimate.json`, generated 2026-08-26, and companion status files) and from `retrieval_latency_sec` fields present in the raw BM25 ranking records this audit already holds. **No new inference or retrieval was run to produce this phase** — doing so for H+SR specifically would require GPU compute and is out of scope per the stop conditions.

## Offline vs. online cost, separated as requested

| Stage | Offline cost | Online (per-bug) cost |
|---|---|---|
| BM25 | Corpus/index construction per repository snapshot (not separately measured in available artifacts) | **Measured, N=7,023**: mean 0.710s, median 0.344s, p95 2.175s, max 4.963s (CPU-only) |
| Jina (dense) | Embedding index construction per snapshot (chunking + encoding) — not separately measured in available artifacts; `method/dense_retriever.py`'s `build_index_embeddings`/embedding cache (Phase 1) implies real, non-trivial one-time cost per repository | Not recorded in the raw `jina_records.jsonl` export (no `retrieval_latency_sec` field present) — gap, not fabricated |
| Hybrid (RRF) | None (pure CPU fusion of two already-computed rankings) | Negligible (simple arithmetic over two rank lists; not separately measured but structurally trivial relative to the other stages) |
| H+SR (Qwen3-8B) | Model weight transfer to MN5 (one-time, `mn5_transfer_complete=true`) | **Measured, N=24 pilot, generalized to N=7,023**: see below |

## H+SR inference cost — the dominant cost by orders of magnitude

**Per-bug (N=24 pilot measurement, `hsr_only_est_sec`)**: mean 723.3s (~12.1 min), median 733.0s, min 480.7s, max 1,074.8s. **Model size**: Qwen3-8B (8 billion parameters). **Peak VRAM**: median 15.8 GiB, max (full workflow) 35.4 GiB. **Model load overhead**: mean 31.1s/bug (4.3% of per-bug wall time) — the pipeline reloads the model fresh for every bug (`ONE_BUG_PER_SLURM_TASK` execution unit, chosen deliberately: "amortization ~4.3% of H+SR wall; multi-bug batching gain negligible vs. failure blast radius / resume complexity" — a considered engineering trade-off, not an oversight).

**Full N=7,023 run, GPU-hours**: mean **1,411.0 GPU-hours** (range 937.7–2,096.8), scaled from the N=24 pilot by a factor of 292.6x (i.e., the pilot-to-full scaling was close to exactly linear in bug count, as expected for a per-bug-independent workload). At various H100 concurrency levels (the project's own planning table): 8 GPUs → ~176 wall-clock hours; 16 → ~88h; 32 → ~44h; 64 → ~22h; 128 → ~11h. The actual run used concurrency 64 (`remainder_operational_status.json`, `"concurrency": 64`), i.e. **an actual wall-clock cost on the order of ~22 hours of compute time** (plus queueing, explicitly excluded from these estimates as "not deterministic, separate from compute").

**Storage**: expected final storage 11.53 GB for the full N=7,023 H+SR run's outputs (`storage.expected_final_storage_gb`), well within the 894–927 GB free capacity available on the cluster at planning time — this cost dimension was never a binding constraint.

**Tokens**: `max_new_tokens=1024` (hard-enforced "frozen decoding contract," Phase 1/2), applied per (bug, candidate) pair — up to 100 candidates per bug, so up to 102,400 generated tokens per bug in the worst case, though actual generation is typically much shorter (structured JSON output, not free-form text) — exact realized token counts were not found in available artifacts (gap; the raw RF outputs that would carry this are the same gitignored artifacts flagged missing throughout this audit).

## Cost comparison: H+SR vs. the retrieval-only pipeline

At the per-bug level, H+SR's ~723s mean inference time is **roughly 1,000x** the BM25 retrieval stage's ~0.7s mean latency. This is an enormous, structurally obvious cost asymmetry that the manuscript should state numerically rather than only qualitatively ("a comparatively lightweight... design," as the current draft states) — 1,000x is a striking, citable number that also puts the modest primary-cohort Hit@10 gain from adding H+SR (+0.010, Phase 11) in useful perspective: **a three-order-of-magnitude increase in per-bug compute cost buys a one-percentage-point aggregate Hit@10 improvement, concentrated mostly in the easier single-file-bug stratum (Phase 8: +0.029 MRR/MAP gain at `\|GT\|=1` vs. a net-negative Complete@10 effect at `\|GT\|=2`)**. This is an important, currently-missing piece of the paper's own cost-effectiveness argument and should be added to the Discussion.

## Comparison against IQLoc's own cost profile

Not directly measurable — IQLoc's own paper/repository does not report per-bug inference latency or GPU-hour figures in any material this audit has inspected (not re-checked exhaustively this phase; the original IQLoc PDF read in the prior manuscript's Stage C work focused on accuracy metrics, not cost). **Per the explicit instruction "Do NOT claim efficiency superiority over IQLoc unless comparable measurements exist," no such claim is made.** What can be stated structurally, not empirically: IQLoc's cross-encoder reranker is fine-tuned (a one-time training cost not present in H+SR's design) but likely has a smaller per-inference cost than an 8B-parameter generative LLM performing structured JSON generation (a cross-encoder forward pass is typically a single scoring computation per candidate, not autoregressive token generation) — this is a plausible, architecture-motivated expectation, not a measured comparison, and must be labeled as such if used at all.

## Effectiveness–efficiency Pareto framing

Given only one operating point for H+SR was measured (no depth/model-size ablation — Phase 7's GPU-dependent ablations were not run), **this audit cannot construct an actual Pareto frontier** (which requires multiple effectiveness/cost trade-off points, not one). What is available is a single (effectiveness, cost) pair for each of B/D/H/H+SR, with cost known precisely only for BM25 and H+SR. A genuine Pareto-frontier claim would require at minimum the missing Jina online-latency figure and, ideally, the GPU-dependent ablations (smaller reranker model, shallower candidate depth) flagged in Phase 7 — these are natural P1/P2 candidates for the Phase 19 table, not claims this phase can support now.

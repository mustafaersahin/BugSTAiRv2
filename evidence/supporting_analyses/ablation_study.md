# Phase 7 — Full Ablation Study

## What is achievable without new compute, and what requires a stop-condition

Per this phase's own instruction ("Every ablation should answer a scientific question... Do NOT create meaningless ablations"), three ablation questions are answerable from existing raw data with no new inference calls, and are executed below. A fourth category — isolating the reranker's contribution from the hybrid retriever's contribution (e.g., "BM25 alone + semantic rerank" or "Jina alone + semantic rerank", which Reviewer 1's adversarial review explicitly requested) — **requires rerunning the Qwen3-8B reranker over a different Top-100 candidate pool than the one it was actually run on**, i.e. new GPU-based LLM inference over up to 7,023 bugs. This is an explicit stop condition (substantial GPU compute) and is **not attempted**; it is carried forward to the Phase 19 prioritized-experiment table as a specific, well-defined P0/P1 candidate.

## Ablation 1 — Does lexical retrieval alone explain the gains, or does dense retrieval add real value? (B → D)

**Scientific question**: is Jina's dense embedding channel doing real work, or would BM25 alone capture most of the signal?

Paired, per-bug (N=7,023), computed from raw rankings, `q1_strengthening/scripts/ablation_stats.py`:

| Metric | Δ(D−B) | 95% CI (paired bootstrap, B=10,000, seed 20260826) | Wilcoxon z |
|---|---|---|---|
| Hit@10 | +0.1064 | [+0.0950, +0.1179] | −14.46 |
| MRR | +0.1167 | [+0.1068, +0.1268] | −22.77 |
| TREC MAP | +0.0940 | [+0.0858, +0.1023] | −23.39 |

**Answer**: yes, decisively — dense retrieval alone recovers a large, highly significant improvement over lexical retrieval alone, on every metric. This had never previously been given a formal paired significance test (only reported as point deltas in the prior manuscript's ladder).

## Ablation 2 — Does fusion add value beyond the better individual component? (D → H, i.e. Hybrid vs. Jina alone)

**Scientific question**: RRF fusion combines two channels; is the fused result actually better than just using the stronger of the two (Jina) alone, or does BM25 contribute nothing once Jina is available?

| Metric | Δ(H−D) | 95% CI | Wilcoxon z |
|---|---|---|---|
| Hit@10 | +0.0386 | [+0.0305, +0.0469] | −8.52 |
| MRR | +0.0343 | [+0.0266, +0.0420] | −11.93 |
| TREC MAP | +0.0356 | [+0.0295, +0.0416] | −16.84 |

**Answer**: yes — fusion adds a real, statistically robust improvement over the stronger individual channel alone. This directly answers a question Reviewer 1 raised implicitly (whether BM25 contributes anything once dense retrieval is available) with real evidence: **BM25 continues to contribute complementary signal even when fused with a substantially stronger dense channel**, confirming RRF fusion is not redundant with its better parent.

## Ablation 3 — Full lexical-to-hybrid effect size (B → H)

| Metric | Δ(H−B) | 95% CI | Wilcoxon z |
|---|---|---|---|
| Hit@10 | +0.1450 | [+0.1357, +0.1542] | −24.56 |
| MRR | +0.1510 | [+0.1437, +0.1586] | −41.86 |
| TREC MAP | +0.1296 | [+0.1237, +0.1355] | −47.08 |

The largest, most robust effect in the entire ladder, as expected (it is the composition of Ablations 1 and 2).

## Ablation 4 — H vs. H+SR (the reranking contribution)

**Not recomputed from scratch this phase** (no raw H+SR per-bug predictions available, per Phase 3) — carried forward from the frozen, hash-verified `BUGSTAIR_V2_FINAL_RESULTS.json` bootstrap (already reported in the prior manuscript, all six CIs exclude zero). No new work needed here; flagged only to keep the four-ablation numbering complete and honest about provenance tier (frozen aggregate vs. this phase's from-scratch raw recomputation for Ablations 1–3).

## What is NOT attempted, and is the correct scope for future GPU-based work

- **BM25-alone + semantic rerank** (bypassing the hybrid fusion step entirely): would isolate whether the reranker's benefit is contingent on the hybrid parent's candidate quality, or would reproduce comparably on a weaker candidate pool. Requires reranking BM25's own Top-100 with Qwen3-8B — new GPU inference, ~7,023 bug-level calls at minimum (likely ~700K individual candidate-scoring calls at 100/bug, matching the original Stage C cost structure). **P0/P1 candidate for Phase 19.**
- **Jina-alone + semantic rerank**: same reasoning, isolates whether hybrid fusion specifically (vs. dense retrieval alone) is necessary for the reranker to add value. Same GPU-cost profile.
- **RRF weighting sensitivity — executed** (`q1_strengthening/scripts/rrf_k_sensitivity.py`, `data/rrf_k_sensitivity.json`): RRF was recomputed at k ∈ {10, 30, 60, 100, 150, 200, 500} directly from the existing raw `bm25_records.jsonl`/`jina_records.jsonl`.

  **Important methodological caveat, disclosed rather than hidden**: this re-fusion does not exactly reproduce the officially reported k=60 numbers (Hit@1 0.4240 here vs. 0.430443 officially; a ~0.006 absolute gap). The cause was diagnosed: both `bm25_records.jsonl` and `jina_records.jsonl` store only each method's own **Top-200** candidates (`ranking_depth=200`) — the official Hybrid H record is *also* stored at `ranking_depth=200`, but this audit could not determine from available metadata whether the official fusion was computed from each method's *full* corpus ranking (then truncated to 200 for storage) or from the same pre-truncated Top-200 lists this re-fusion used; the two produce slightly different results whenever a file ranks outside the Top-200 of one method but inside the Top-200 of the other with a rank fine enough to matter at a given k. **This re-fusion's absolute values at k=60 should therefore not be treated as an exact reproduction; its internal, same-methodology comparison across k values remains valid** (all seven k-values were fused from the identical truncated inputs, so the *relative* trend is a fair comparison even if the absolute level has a small, explained offset from the official pipeline).

  **Finding**: Hit@10 ranges only from 0.7880 (k=500) to 0.7970 (k=30) across the full tested range — a spread of 0.0090, i.e. under one percentage point across a 50x range of k. Hit@10, MRR, and TREC MAP all **decline monotonically and smoothly** as k grows past ~30, with no sharp optimum or cliff. **This supports, with real (if slightly offset) evidence, the manuscript's claim that k=60 is a reasonable, non-arbitrary default** — it sits on a broad, flat plateau near the empirical optimum (k=30, only 0.0036 higher on Hit@10) rather than at a knife-edge or a poor choice. Given the small absolute-value offset explained above, this finding is reported as **directionally reliable, quantitatively approximate** — a full re-verification from un-truncated rankings (if recoverable) would be a cheap, worthwhile P2 follow-up.
- **Candidate pool depth ablation** (Top-50 vs. Top-100 vs. Top-200 reranking scope): requires rerunning the reranker at different depths — GPU stop condition.
- **Prompt-design ablation**: requires rerunning the reranker with a modified prompt — GPU stop condition.

## Recommendation

The RRF-k sensitivity sweep (cheap, CPU-only, no stop condition) should be executed as a fast follow-up within this same Q1 strengthening pass if time permits before Phase 19; the four GPU-dependent ablations above should be formally entered into the Phase 19 prioritized-experiment table rather than attempted here.

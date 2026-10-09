# Step 2 (of the earlier pass) / Step 3 (of this pass) — H+SR Metric Recomputation — UPDATED WITH TRUE RAW DATA

**This supersedes the earlier version of this file**, which could recompute B, D, and H from raw data but could only report H+SR's frozen aggregate (raw predictions were absent at that time). The raw H+SR predictions are now present, hash-verified, and used directly below.

## Method

`predictions/final_hsr_predictions.jsonl` (7,023 raw per-bug rankings) is joined to ground truth from `iqloc_author_final_7483/rankings/hybrid_rrf_records.jsonl` by `stable_identity_sha256`, and Hit@1/5/10, MRR, TREC MAP, and Package MAP are computed directly from each bug's `ranked_file_identities` and ground-truth set — no import of the project's own evaluation code, no use of `final_h_vs_hsr_metrics.json` as a source of truth (per the explicit instruction). Script: `scripts/master_hsr_raw_recomputation.py`.

## Four-way comparison

| Metric | RAW RECOMPUTED (this pass, from `final_hsr_predictions.jsonl` + GT) | PER-INSTANCE AGGREGATED (mean of `final_h_vs_hsr_per_instance.jsonl`'s own per-bug values) | FINAL METRICS FILE (`final_h_vs_hsr_metrics.json`, H_SR block) | MANUSCRIPT VALUE (Table 4) | MATCH |
|---|---|---|---|---|---|
| Hit@1 | 0.454649010 | 0.454649010 | 0.45464901039441835 | 0.4546 | **MATCH** (exact to 9 s.f.) |
| Hit@5 | 0.721628934 | 0.721628934 | 0.7216289335042004 | 0.7216 | **MATCH** |
| Hit@10 | 0.803502777 | 0.803502777 | 0.8035027765912004 | 0.8035 | **MATCH** |
| MRR | 0.574926695 | 0.574926695 | 0.5749266952214641 | 0.5749 | **MATCH** |
| TREC MAP | 0.462271947 | 0.462271947 | 0.4622719467896823 | 0.4623 | **MATCH** |
| Package MAP | 0.482547471 | 0.482547471 | 0.4825474708971206 | 0.4825 | **MATCH** |

**All three independent computations (raw-from-scratch, aggregated-from-per-instance-file, and the official aggregate file) agree exactly, to at least 9 significant figures.** No floating-point discrepancy exceeds ordinary summation-order noise. **No correction to Table 4 is required.**

## Additional metrics (GTRecall@5/10, Complete@5/10) — now independently computable for the first time

These were not previously independently verifiable (they require full per-bug ground-truth-set recall, not just the best-hit rank the per-instance file reports). Now computed directly from raw rankings:

| Metric | H | H+SR | Δ |
|---|---|---|---|
| GTRecall@5 | 0.541369 | 0.546656 | +0.005287 |
| GTRecall@10 | 0.647002 | 0.643418 | −0.003584 |
| Complete@5 | 0.412787 | 0.409369 | −0.003417 |
| Complete@10 | 0.519863 | 0.503061 | −0.016802 |

GTRecall@10 and Complete@10 deltas match the manuscript's Section 5.2/Table 4 figures exactly (−0.0036 and unreported-but-consistent respectively — the manuscript's Table 4 continued reports Package MAP Δ=+0.0180, consistent with +0.017955 here). No prior claim in the manuscript used GTRecall@5 or Complete@5 as a headline figure, so there is nothing to correct there; these are reported for completeness and for use in the updated cardinality analysis (`cardinality_analysis.md`).

## H (baseline) values reconfirmed unchanged

The H-side values in `final_h_vs_hsr_metrics.json` (Hit@1=0.430443, Hit@5=0.704542, Hit@10=0.793393, MRR=0.553750, TREC MAP=0.453770, Package MAP=0.464592) match this study's own independent B/D/H recomputation from the master ranking file exactly (previously verified in the earlier evidence pass), confirming the H+SR run reranked the correct, authoritative H ranking.

## Conclusion

Every H+SR aggregate metric in Table 4 is now independently reproduced directly from raw per-bug predictions, not merely reported from a frozen aggregate. No correction required to Table 4. The provenance dagger (†) previously used to mark H+SR's rows as a distinct, lower-verification tier is **no longer accurate** and should be removed in the final manuscript (applied in `17_manuscript_ist_final.md`).

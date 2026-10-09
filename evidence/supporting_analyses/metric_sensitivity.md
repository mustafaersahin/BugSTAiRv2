# P1-D — Metric Sensitivity Table

## The three definitions, restated precisely (per Phase 4)

1. **Standard IR/TREC AP-MAP**: denominator = `|D|` (count of localizable ground-truth files).
2. **IQLoc paper-defined AP-MAP**: identical formula to (1) — the paper's own prose states the `|D|`-denominator formula verbatim (Phase 4 finding: these two collapse into one).
3. **IQLoc released-code AP-MAP ("package")**: denominator = hits found, not `|D|` — confirmed by direct inspection of IQLoc's public `Evaluation_Metrics.py`.

## Sensitivity table — all four systems, both applicable definitions

| Method | TREC/Paper MAP | Package (released-code) MAP | Absolute gap | Relative gap | Provenance tier |
|---|---|---|---|---|---|
| BM25 | 0.324164 | 0.334853 | +0.010689 | +3.3% | Independently recomputed from raw data (Phase 3) |
| Jina | 0.418201 | 0.429580 | +0.011379 | +2.7% | Independently recomputed from raw data (Phase 3) |
| Hybrid H | 0.453770 | 0.464592 | +0.010822 | +2.4% | Independently recomputed from raw data (Phase 3) |
| H+SR | 0.462272 | 0.482547 | +0.020275 | +4.4% | Frozen aggregate, hash-verified (Phase 3) |

(Reproduced from Phase 4's original table; not recomputed again this phase — no new evidence changes these figures.)

## Do the paper's main conclusions change under either definition?

**No — every ordinal, directional claim in the paper's own results is identical under both definitions.** Checked explicitly:

- **B < D < H < H+SR ordering**: holds under both TREC and Package MAP (monotonic increase, both columns, all four methods).
- **H+SR vs. IQLoc's MAP comparison** (the one place the paper currently reports a "loss"): H+SR is below IQLoc's reported MAP under **both** BugSTAiR-side definitions (TREC 0.4623 and Package 0.4825, both below IQLoc's 0.493/0.520) — the loss is not an artifact of picking the less favorable definition; it holds under the *more* favorable definition too (Package MAP, +4.4% higher than TREC MAP, still below IQLoc's reported values).
- **The multi-file TREC MAP decline** (Phase 8: 0.4249 → 0.4186 on `|GT|≥2` under H+SR) — only TREC MAP was computed per-stratum by the original project (Package MAP per-stratum was not in the `MULTIFILE_METRICS_BY_STRATUM.json` fields this audit inspected in Phase 8); this specific fine-grained claim has not been cross-checked under Package MAP and is flagged as a minor, non-blocking gap (the aggregate-level finding above already confirms directional stability).

## Recommendation: one primary definition, clearly justified

**Recommend TREC MAP as BugSTAiR's own primary, headline-reported MAP definition**, for three converging reasons: (1) it is the definition BugSTAiR's own code comments explicitly anchor to a named external protocol ("TREC-style Average Precision (Bench4BL protocol §7.4)", Phase 1's reading of `method/ranking_metrics.py`'s docstring) rather than an internally-invented convention; (2) it matches the convention used by the two classical baselines already in the paper's comparison table (BLUiR, Blizzard, as reported via IQLoc's own Table 10, which computes their scores under whatever IQLoc's evaluation harness uses — itself a further reason not to over-index on matching IQLoc's code-level convention exactly, since even IQLoc's own baseline comparisons inherit this same ambiguity); (3) it is the more conservative (lower) of the two values wherever they diverge, which is the appropriate choice when a paper cannot fully resolve which definition a comparator uses — reporting the less-flattering number as primary is the more defensible, less-easily-challenged choice for a Q1 submission.

**Package MAP should be retained as a named, explicitly-labeled secondary/sensitivity metric**, specifically when discussing the IQLoc comparison, since it is the definition IQLoc's own released code actually implements (even though which one produced the *published* Table 10 numbers remains formally unresolved, per Phase 4/14). Reporting both, clearly labeled, in the comparison table (as the current manuscript's Table 5 already does) remains the correct practice — this recommendation is about which one anchors the paper's own internal narrative and abstract-level claims, not about dropping either from the tables.

## Metrics independent of the MAP ambiguity — confirmed exhaustively, not just asserted

Hit@K, MRR, GTRecall@K, and Complete@K share **no denominator or formula component with either AP definition** — they are separately and unambiguously defined (confirmed by direct inspection of both `method/ranking_metrics.py` and `method/iqloc_metrics.py` in Phase 1, and independently reimplemented from scratch without reference to either AP formula in Phase 3's `recompute_retrieval_metrics.py`). **Every Hit@K/MRR/GTRecall/Complete@K-based claim in the paper — including the central displacement-mechanism finding (Phase 9) and the multi-file cardinality analysis (Phase 8) — is entirely unaffected by the MAP ambiguity**, since none of those analyses invoke MAP at all except as one of several metrics reported alongside, never as the load-bearing evidence for the displacement claim itself (which rests on Hit@10, Complete@10, and the raw rank-transition data).

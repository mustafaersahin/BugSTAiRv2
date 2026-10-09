# CRITICAL RAW ARTIFACT CONTRADICTION

**STOP triggered.** The newly recovered raw H+SR predictions (`predictions/final_hsr_predictions.jsonl`, now present and cryptographically hash-verified — SHA-256 `28c84c1955d0a7e82326b91fcb32aaa82bd0fe65d3b2273cc0f186f0a0594301`, matching the documented value exactly) **materially contradict the manuscript's displacement/test-file magnitude claims**, though not its aggregate-effectiveness or qualitative conclusions. Manuscript integration has been halted pending a decision on which population definition to report. `17_manuscript_ist_final.md` has **not** been created. `18_final_claim_scan.md` and `19_hsr_reproducibility_gate.md` have **not** been created, since both depend on the manuscript text this contradiction affects.

## What was independently confirmed to be UNCHANGED and CORRECT (good news first)

Before describing the contradiction, the following were independently reproduced **exactly** from the true raw predictions and require no correction:

- **Full-cohort aggregate H+SR metrics** (Hit@1/5/10, MRR, TREC MAP, Package MAP): match `metrics/final_h_vs_hsr_metrics.json` and the manuscript's Table 4 exactly (e.g., Hit@10 = 0.803503, MRR = 0.574927).
- **Cardinality-stratified deltas** (|GT|=1/2/≥3): match the manuscript's Table 6 exactly, and — as a genuine, safe upgrade now possible with true raw data — now carry **real per-stratum paired bootstrap CIs** for the first time (previously only the pooled `|GT|≥2` row had one). These CIs are consistent with and refine, not contradict, the manuscript's existing cardinality narrative (see details below).
- **The two-file joint file-type breakdown** (129 test-displaced/production-stable, 5 test/test, 33 production/production, 44 production/test, of 211 total): matches exactly.
- **Ground-truth composition** (70.1% mixed): unaffected by H+SR data by construction, matches exactly.
- **Path-token lexical-overlap negative result**: unaffected, not touched by this pass.

## THE CONTRADICTION

### Previous claim (manuscript, Table 7 and Section 6.1)

Category A (retrieval/window failure) = 3,008 (18.05%); **Category B (reranking displacement) = 457 (2.74%)**; Category C (promotion) = 253 (1.52%); Category D (stable) = 8,365 (50.20%, corrected in the prior evidence pass). Framing: "Category A, true retrieval failure, is **6.6× larger** than Category B, reranking displacement."

### Raw result (this pass, computed directly from `final_hsr_predictions.jsonl` joined against the H master ranking file, independently verified twice — once via a from-scratch Fisher/OR implementation, once via `scipy.stats.fisher_exact`, both in exact agreement)

Classifying **every** ground-truth file instance (16,663 total) by its true H-rank and true H+SR-rank, with no additional scoping condition:

| Category | Definition (as literally stated in the manuscript's own Table 7) | N | % of 16,663 |
|---|---|---|---|
| A — Retrieval/window failure | Never in H's top-100 | 3,008 | 18.05% (unchanged) |
| **B — Reranking displacement** | In H's top-10, present in candidate pool, reranked to position >10 | **1,146** | **6.88%** |
| **C — Promotion** | Not in H's top-10, entered H+SR's top-10 | **1,086** | **6.52%** |
| **D — Stable** | In H's top-10, remains in H+SR's top-10 | **7,676** | **46.07%** |
| (in window 11–100, not promoted) | — | 3,747 | 22.49% |

**Category B is 2.51× larger than previously reported (457 → 1,146). Category A is now only 2.62× larger than Category B, not 6.6×.**

### Exact discrepancy and its cause (diagnosed, not merely observed)

The 457/253 figures in the manuscript trace to `results/multifile_displacement_analysis/DISPLACED_GT_FILES.json` and `RECOVERY_CASE_SUMMARY.json` — official artifacts whose own documentation (`MULTIFILE_DISPLACEMENT_SUMMARY.md`) states they cover "**Displaced GT files: 457 across 364 loss bugs**" and describes themselves explicitly as a "**Secondary post-hoc diagnostic of frozen BugSTAiR predictions**" scoped to bugs whose **Complete@10 status flipped from complete (under H) to incomplete (under H+SR)** — i.e., only bugs where *every* ground-truth file was in H's top-10 to begin with, and at least one left. **This is a narrower population than "every ground-truth file that was in H's top-10 and left,"** which is what the manuscript's own Table 7 caption literally defines Category B to be. A ground-truth file that was in H's top-10, gets displaced under H+SR, but belongs to a bug that *already* had another ground-truth file outside H's top-10 (so the bug's Complete@10 was 0 both before and after — no "loss" transition occurred at the bug level) is counted by the true per-file definition (and by this session's raw recomputation) but was **not** counted in the 457-record ledger, because that ledger only enumerates files belonging to the 364 bugs that underwent a bug-level complete→incomplete transition.

**Verified directly**: the individual example record cross-checked against the official ledger (`stable_identity_sha256 = d8fa33ce...`, `gt_path = .../RemoteFileConfiguration.java`) shows `h_rank=9, hsr_rank=24` in **both** the ledger and this session's independent raw computation — an exact match. The join mechanics and rank extraction are confirmed correct; **the discrepancy is a population-scope mismatch, not a computational error in either this session's work or the prior session's.**

### The test-file odds ratio is affected downstream, and changes more substantially

Recomputing the test/production breakdown using the true, unconditional Category B/C/D populations:

| Comparison | Previous (manuscript, ledger-scoped) | Raw (this pass, unconditional, true population) |
|---|---|---|
| Displaced vs. stable | OR=3.34 [2.76,4.04], p=7.7×10⁻³⁵ | **OR=2.107 [1.855,2.394], p=2.78×10⁻²⁹** |
| Promoted vs. stable | OR=1.52 [1.17,1.98], p=1.99×10⁻³ | **OR=0.743 [0.636,0.867], p=1.48×10⁻⁴** |
| Displaced vs. promoted | OR=2.19 [1.60,3.00], p=1.08×10⁻⁶ | **OR=2.837 [2.352,3.421], p=5.10×10⁻²⁹** |

**The "displaced vs. stable" and "displaced vs. promoted" comparisons remain highly significant with OR > 1 — the qualitative conclusion that test files are disproportionately displaced survives — but the magnitude drops substantially (3.34 → 2.11), and this number appears in the Abstract as a headline statistic.** More seriously: **the "promoted vs. stable" comparison reverses direction** — the manuscript states "Test files are also somewhat more likely to be promoted than the baseline (OR 1.52)... indicating they churn in both directions more than production files"; the true unconditional population shows the **opposite** (OR=0.743, test files *less* likely to be promoted than baseline), which directly contradicts this specific sentence in Section 6.3.

## Affected table(s)

Table 7 (Section 6.1) — Category B, C, D counts and percentages, and the "6.6×" framing sentence. Table 5 continued / Table 8 continued (Section 6.3) — all three odds-ratio rows, and the "somewhat more likely to be promoted... churn in both directions" sentence. Abstract — the "3.34 times the odds" headline figure.

## Affected RQ / conclusion

RQ4 (differential test/production displacement) and its Section 6.3 answer. The Discussion's Section 8.2 mechanistic account references the OR magnitude implicitly (via Section 6.3) but does not restate the number itself, so its prose is not directly falsified, only indirectly weakened if the OR changes.

**Not affected**: RQ1 (retrieval ladder), RQ2 (aggregate reranking gain), RQ3 (cardinality trade-off — actually strengthened by genuine per-stratum CIs now available), RQ5 (cost), RQ6 (BLUiR-style comparison), Section 6.4 (ground-truth composition), Section 6.2's two-file mechanism (the 211/129 figures, verified unaffected — see explanation below).

## Why the two-file mechanism (211/129) is unaffected despite the same underlying data

For a `|GT|=2` bug specifically, "one file displaced, one file stable" requires **both** files to have started in H's top-10 (a prerequisite for either "displaced" or "stable" status under either definition) — and if both started in top-10 and one leaves, that bug's Complete@10 necessarily flips from 1 to 0, i.e., it is *automatically* one of the 364 "loss bugs" by construction. The ledger-scoped and unconditional definitions therefore coincide exactly for this specific two-file subset, which is why this session's raw recomputation reproduces 211/129/5/33/44 precisely. This is a genuine, verified non-contradiction, not an oversight.

## Likely cause (root-cause statement)

The manuscript's Table 7 caption defines Category B without a "loss-bug" scoping condition, but the underlying evidence artifact used to populate that table (`DISPLACED_GT_FILES.json`) was generated under a **different, narrower scope** by the original pipeline's own diagnostic script, and this scope mismatch was not caught in either the original manuscript-drafting pass or the prior evidence-integration pass (both of which treated the 457/253 ledger counts as directly answering the Table 7 question, since — until this pass — no true raw H+SR predictions were available to check the ledger's actual scope against the full, unconditional population).

## Required corrective action (decision needed, not made unilaterally here)

Per this pass's explicit instruction not to redesign the paper or introduce new narrative framing unilaterally, **this requires the user's decision** among at least three defensible options, each of which changes different amounts of manuscript text:

1. **Report the true, unconditional Category B/C/D figures** (1,146 / 1,086 / 7,676) throughout Table 7, Section 6.1, Section 6.3's odds ratios, and the Abstract — the most faithful reading of Table 7's own stated definition, but requires updating the Abstract's headline "3.34" figure to "2.11" and correcting or removing the "promoted... churn in both directions" sentence, since that direction reverses.
2. **Keep the loss-bug-scoped 457/253/8,365 figures** but **rename and re-define Category B/C/D explicitly as scoped to the 364 loss bugs** (matching what the source ledger actually measures), and add a new, clearly-labeled row or footnote reporting the broader, unconditional population (1,146/1,086/7,676) as a supplementary, non-headline statistic — preserving the existing Abstract number but requiring a new methodological caveat and likely a supplementary table.
3. **Report both explicitly, side by side**, with Table 7 restructured to show both the "loss-bug-scoped" and "unconditional" counts as two clearly labeled columns, letting the reader see both populations rather than requiring the paper to commit to one as primary.

**This pass makes no such decision and applies no manuscript edit.** `12_manuscript_ist_submission_candidate.md` remains the last manuscript state; `17_manuscript_ist_final.md` will be created only after this is resolved.

---

## ADDENDUM (post-decision): the original 3.34 figure is a population-mismatch artifact, not merely a narrower-scope statistic

The user selected Option 1 (report the true unconditional population as authoritative). While implementing that decision, a further, more precise diagnosis was made: the original OR=3.34 was **not** a cleanly-scoped "conditional on the 364 loss bugs" statistic as initially described to the user when this STOP was raised. It compared a numerator restricted to the 364 loss bugs (displaced=457) against a denominator that was **not** restricted to those same bugs (stable=8,365, drawn from all 7,023 bugs). This is a population mismatch, not a valid alternative population definition. A properly-scoped, same-population conditional statistic was computed instead: **OR=4.277, 95% CI [3.199,5.720], p=2.72×10⁻²⁴**, using displaced=457 (test=252/prod=205) against a stable baseline drawn from the *same* 364 bugs only (test=98/prod=341, total=439) — see `test_file_analysis.md` for full detail. This refinement does not change the resolution already selected (unconditional OR=2.107 remains primary) and does not reopen the STOP, per the user's explicit instruction to trigger it again only for a new contradiction materially changing a central conclusion — this is a within-the-same-issue refinement discovered while executing the already-made decision, not a new, separate contradiction.

# Step 7 (earlier pass) / Step 8 (this pass) — Test vs. Production Reanalysis — CORRECTED WITH TRUE RAW DATA

**Supersedes the earlier version.** Per the user's explicit decision (Option 1: unconditional raw-derived population is authoritative for all primary manuscript claims), this file reports the true unconditional test/production displacement analysis and explains precisely why the previously-reported OR=3.34 should be **retired entirely**, not merely relabeled — a further, more precise finding than initially understood at STOP time.

## PRIMARY analysis: true unconditional population (now authoritative)

Computed directly from Categories A–D as reconstructed in `displacement_analysis.md` (no loss-bug or any other scoping condition), test/production classified by the rule in `test_file_classification.md`.

| Category | Test | Production | Total | % test |
|---|---|---|---|---|
| Displaced | 491 | 655 | 1,146 | 42.8% |
| **Stable (baseline)** | **2,014** | **5,662** | **7,676** | **26.2%** |
| Promoted | 227 | 859 | 1,086 | 20.9% |

| Comparison | OR | 95% CI | Fisher exact two-sided p | Survives Bonferroni (α/3=0.0167)? |
|---|---|---|---|---|
| Displaced vs. stable | **2.107** | [1.855, 2.394] | 2.78×10⁻²⁹ | Yes |
| Promoted vs. stable | **0.743** | [0.636, 0.867] | 1.48×10⁻⁴ | Yes |
| Displaced vs. promoted | **2.837** | [2.352, 3.421] | 5.10×10⁻²⁹ | Yes |

Independently confirmed twice: once via a from-scratch Fisher's-exact implementation, once via `scipy.stats.fisher_exact` — both give identical results to the precision shown.

**Test files are displaced at roughly twice the odds of production files, relative to the stable baseline — a real, highly significant, and large effect, though smaller in magnitude than the previously reported 3.34.** Wording per the user's explicit instruction: *"Test files were disproportionately represented among displaced relevant files under the measured configuration."* No causal language is used.

**The promoted-vs-stable comparison reverses direction from the previous report** (OR=1.52 → OR=0.743): under the true unconditional population, test files are *less* likely to be promoted into the top-10 than production files, not more. The manuscript's previous sentence "Test files are also somewhat more likely to be promoted than the baseline... indicating they churn in both directions more than production files" is **false under the corrected analysis and must be removed**, per the user's explicit instruction not to construct a symmetric "churn" narrative. The corrected, separate characterization is: test files are disproportionately *displaced* (OR=2.11) and disproportionately *under-represented among promotions* (OR=0.74) — two distinct, non-symmetric findings, not a bidirectional "churn" pattern.

## SECONDARY analysis: properly-scoped conditional statistic — the original "3.34" is retired, not relabeled

A further investigation was needed here, beyond what was understood at the STOP point. The original manuscript's OR=3.34 was computed as: displaced=457 (correctly scoped to the 364 Complete@10-loss bugs) **against a stable baseline of 8,365 that was *not* scoped to those same 364 bugs** (it was "all H-top-10 files across all 7,023 bugs, minus the 457 loss-scoped displaced files"). **This is a population mismatch, not a valid conditional statistic** — the numerator and denominator were drawn from different populations (one restricted to loss bugs, one not), which is why simply re-labeling "3.34" as "the loss-bug-scoped OR" would still misrepresent it.

A **properly scoped** conditional analysis — both numerator and denominator restricted to the same 364 loss-bug population — was computed for this report:

| Within the 364 Complete@10-loss bugs only | Test | Production | Total |
|---|---|---|---|
| Displaced (left H's top-10) | 252 | 205 | 457 |
| Stable (remained in H's top-10, within the same 364 bugs) | 98 | 341 | 439 |

**Properly-scoped conditional OR (displaced vs. stable, within the 364 loss bugs): 4.277, 95% CI [3.199, 5.720], Fisher exact two-sided p=2.72×10⁻²⁴.**

This is a legitimate, well-defined statistic — "among the specific bugs where reranking visibly broke complete multi-file recovery, how much more likely was the file that got displaced to be a test file, compared to the file(s) in the same bugs that stayed" — and its value (4.28) is neither the old, invalid 3.34 nor the new unconditional 2.11. Per the instruction to give this figure's numerator, denominator, population definition, and purpose explicitly wherever used, and given it adds genuine interpretive value to the mechanistic discussion of *why* the multi-file trade-off occurs specifically in loss bugs (Section 8.2), it is retained as a single, precisely-labeled secondary figure — but the number **3.34 itself does not appear anywhere in the final manuscript**, since it was never a valid statistic under any consistent population definition.

## Conclusion

Primary analysis (Table 5/8, Abstract): OR=2.107 [1.855,2.394], p=2.78×10⁻²⁹, unconditional. Section 6.3's "churn in both directions" sentence is removed and replaced with separate displaced/promoted characterizations. One new, properly-scoped secondary statistic (OR=4.277, explicitly labeled as conditional on the 364 loss bugs) may be used in Section 8.2's mechanistic discussion if it adds value there; the previously-reported 3.34 is retired as an invalid, mismatched-population artifact and does not appear in the final manuscript under any label.

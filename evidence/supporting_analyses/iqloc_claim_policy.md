# P1-E — IQLoc Comparison: Publication-Safe Claim Policy

## Basis (everything now known, consolidated)

- Paper states N=7,483; the public dataset artifact this audit directly opened (`Bench4BLExtended.json`) contains N=7,493 records — **independently confirmed this closure phase** by opening the file directly (Phase 5/original audit relied on the project's own derived reports; this phase verified the raw file itself).
- BugSTAiR's own cohort is **confirmed, not merely inferred**, to derive from this exact file — this closure phase found the first record (`bug_id "105"`, `FileProducer.java`) matches BugSTAiR's own `dataset_index=0` record byte-for-byte on ground truth, an exact-match confirmation stronger than the count-based inference the original Stage A–F audit relied on.
- Exact test-split membership and random seeds remain confirmed absent from every public channel (Phase 14, unchanged).
- A genuine, code-confirmed paper/released-code AP-formula mismatch exists (Phase 4), with no way to determine which produced IQLoc's published Table 10 numbers.
- Both IQLoc's own code and this closure phase's real primary-source access (`data/iqloc/author_repository/IQLoc/src/IQLoc/`) confirm the fine-tuned CE model is genuinely absent from every reachable artifact — not merely undocumented.

## Claim classification

### SAFE

- *"BugSTAiR reports a higher Hit@10 than the value reported in IQLoc's own Table 10, under both of IQLoc's published evaluation splits."* — a factual, directly verifiable statement about two independently-published numbers; makes no claim about statistical significance or paired comparability.
- *"Direct statistical comparison with IQLoc is not possible because the exact IQLoc evaluation cohort (random/time-wise split membership and seeds) cannot be reconstructed from any publicly available artifact, confirmed by direct inspection of IQLoc's public repository."* — fully evidenced, now with primary-source confirmation (this closure phase directly opened the repository) rather than secondhand.
- *"BugSTAiR's evaluation cohort is derived from the same underlying dataset release as IQLoc's own extended Bench4BL population, confirmed by an exact ground-truth match on inspection of the raw dataset file."* — newly upgradable from "very likely" to a direct factual claim, given this phase's exact-match verification.
- *"The two studies' MAP figures may not be directly comparable, because IQLoc's paper and its released evaluation code implement different Average Precision denominators, and which one produced the published Table 10 values cannot be determined from public information."* — fully evidenced (Phase 4), and should always accompany any MAP-based comparison.
- *"BugSTAiR's own numbers are computed on 93.9% of a shared underlying population, without a train/test split, since no component of the retained pipeline is fine-tuned; IQLoc's numbers are computed on a 20% held-out split of a population whose reranker component is fine-tuned on the remainder."* — factual, evidenced (Phases 1, 3, 14), explains the comparability limit mechanistically rather than as an unexplained caveat.

### QUALIFIED (safe only with the stated qualification attached, every time it is used)

- *"BugSTAiR's Hit@10 exceeds IQLoc's own reported Hit@10"* — safe **only** if immediately accompanied by the non-paired-comparison caveat above; unsafe as a bare, unqualified statement, since a reader could infer statistical superiority from it.
- *"BugSTAiR's MAP is lower than IQLoc's reported MAP"* — safe as a factual observation, but must be qualified with the AP-definition-mismatch caveat, since the "loss" could partly reflect a definitional artifact rather than a true performance gap (Phase 4's finding that the gap is not fully attributable to definition alone, but is not fully independent of it either).
- *"BugSTAiR's cohort is the same dataset IQLoc used"* — the underlying **population** is now confirmed the same (SAFE, see above), but the **evaluated subset** (BugSTAiR's exact-snapshot N=7,023 vs. IQLoc's random/time-wise N≈1,500 test splits) is not the same, and any statement implying identical evaluated populations must be qualified to distinguish "same source dataset" from "same evaluated split."

### UNSAFE (must not appear in the manuscript in any form)

- *"BugSTAiR outperforms IQLoc."* — a bare superiority claim; contradicted by the paper's own MAP finding and forbidden by the project's own machine-readable flag (`"direct_IQLoc_superiority_claim": "FORBIDDEN"`, `BUGSTAIR_V2_FINAL_RESULTS.json`, Phase 3).
- *"BugSTAiR achieves state-of-the-art results on Bench4BL."* — no paired, multi-method, same-split comparison exists to support a SOTA claim (Phases 14, 19).
- *"BugSTAiR is evaluated on the same test set as IQLoc."* — false; IQLoc's exact test-set membership is confirmed unrecoverable (Phase 14), so this cannot be true regardless of shared population origin.
- *"BugSTAiR's MAP is directly comparable to IQLoc's MAP."* — false, given the confirmed AP-definition mismatch (Phase 4); "comparable" implies a stronger claim than the evidence supports, even with hedging language attached — this phrase should not be used even in qualified form; use "reported alongside, for reference" instead.
- Any statement using the word "reproduces" or "replicates" in connection with IQLoc's Table 10 — this audit explicitly could not, and did not attempt to, reproduce Table 10 (Phase 14).

## Recommended exact wording for the manuscript (drop-in replacement candidates)

For the Results section's IQLoc comparison paragraph:

> "H+SR's Hit@10 (0.8035) exceeds both values reported in IQLoc's own Table 10 (0.721 random-split, 0.735 time-wise-split). This is a descriptive comparison, not a paired statistical test: IQLoc's evaluation cohort is derived from the same underlying dataset release as BugSTAiR's own (confirmed by exact ground-truth matching on direct inspection of the released dataset file), but the two studies evaluate different, non-identical subsets under different protocols — IQLoc reports results on a 20% held-out test split of a population whose cross-encoder reranker is fine-tuned on the remaining 80%, while BugSTAiR's training-free pipeline is evaluated on 93.9% of the same source population with no train/test partition. IQLoc's exact split membership and random seeds are confirmed unavailable from every public channel we inspected directly, including its source repository. H+SR's MAP (TREC-style: 0.4623) is below both of IQLoc's reported MAP values (0.493, 0.520); this comparison carries an additional caveat beyond the population-overlap issue above — IQLoc's published paper and its own released evaluation code implement two different Average Precision denominators, and which one produced the published Table 10 figures cannot be determined from any available public artifact."

For Threats to Validity / Limitations:

> "No claim of superiority, state-of-the-art status, or direct statistical comparison against IQLoc is made anywhere in this paper. The comparison presented is descriptive and reference-framing only, for the reasons detailed in Section [X]."

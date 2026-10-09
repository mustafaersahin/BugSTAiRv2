# Step 4 (earlier pass) / Step 6 (this pass) — Cardinality Reanalysis — UPDATED WITH TRUE RAW DATA

**Supersedes the earlier version.** Individual-stratum paired bootstrap CIs are now computed for the first time — the previous limitation ("only the pooled `|GT|≥2` row carries a formal bootstrap") is genuinely resolved, not merely re-described.

## Method

For each stratum (`|GT|=1`, `|GT|=2`, `|GT|≥3`, pooled `|GT|≥2`), paired bootstrap (B=10,000, seed=20260826, bugs resampled with replacement within the stratum) computed directly from true per-bug H and H+SR metrics. Script: `scripts/master_hsr_raw_recomputation.py`.

## Full per-stratum results, with individual-stratum CIs (new)

| Stratum | N | Metric | H | H+SR | Δ | 95% CI | Excludes zero |
|---|---|---|---|---|---|---|---|
| \|GT\|=1 | 2,942 | Hit@10 | 0.7366 | 0.7468 | +0.0102 | [−0.0020, +0.0224] | **No** |
| \|GT\|=1 | 2,942 | MRR | 0.4937 | 0.5228 | +0.0290 | [+0.0204, +0.0380] | Yes |
| \|GT\|=1 | 2,942 | TREC MAP | 0.4937 | 0.5228 | +0.0290 | [+0.0204, +0.0380] | Yes |
| \|GT\|=1 | 2,942 | GTRecall@10 | 0.7366 | 0.7468 | +0.0102 | [−0.0020, +0.0224] | **No** |
| \|GT\|=1 | 2,942 | Complete@10 | 0.7366 | 0.7468 | +0.0102 | [−0.0020, +0.0224] | **No** |
| \|GT\|=2 | 2,219 | Hit@10 | 0.8373 | 0.8400 | +0.0027 | [−0.0095, +0.0149] | **No** |
| \|GT\|=2 | 2,219 | MRR | 0.6174 | 0.6289 | +0.0115 | [+0.0022, +0.0207] | Yes |
| \|GT\|=2 | 2,219 | TREC MAP | 0.4996 | 0.4893 | −0.0103 | [−0.0186, −0.0021] | Yes |
| \|GT\|=2 | 2,219 | GTRecall@10 | 0.6913 | 0.6721 | −0.0192 | [−0.0311, −0.0072] | Yes |
| \|GT\|=2 | 2,219 | Complete@10 | 0.5453 | 0.5043 | −0.0410 | [−0.0590, −0.0230] | Yes |
| \|GT\|≥3 | 1,862 | Hit@10 | 0.8308 | 0.8496 | +0.0188 | [+0.0059, +0.0317] | Yes |
| \|GT\|≥3 | 1,862 | MRR | 0.5727 | 0.5929 | +0.0202 | [+0.0108, +0.0294] | Yes |
| \|GT\|≥3 | 1,862 | TREC MAP | 0.3360 | 0.3345 | −0.0015 | [−0.0077, +0.0046] | **No** |
| \|GT\|≥3 | 1,862 | GTRecall@10 | 0.4527 | 0.4459 | −0.0068 | [−0.0164, +0.0030] | **No** |
| \|GT\|≥3 | 1,862 | Complete@10 | 0.1472 | 0.1165 | −0.0306 | [−0.0446, −0.0172] | Yes |
| \|GT\|≥2 pooled | 4,081 | Hit@10 | 0.8344 | 0.8444 | +0.0100 | [+0.0010, +0.0189] | Yes |
| \|GT\|≥2 pooled | 4,081 | Complete@10 | 0.3636 | 0.3274 | −0.0363 | [−0.0478, −0.0247] | Yes |

**Point estimates reconfirmed exactly matching the manuscript's existing Table 6** in every cell. **Individual-stratum CIs are new** and refine, rather than contradict, the manuscript's existing descriptive framing.

## Re-verifying the central empirical statement, now with genuine inferential support

"Single-file bugs benefit clearly, while multi-file bugs expose a first-hit/completeness trade-off, with the strongest observed trade-off around exactly two-file ground truth":

- **Single-file bugs benefit clearly**: **Partially confirmed with new nuance.** MRR/TREC MAP gains are statistically significant (CI excludes zero); Hit@10/GTRecall@10/Complete@10 gains are **not** individually significant at |GT|=1 (CI includes zero, [−0.0020,+0.0224]), though the point estimate is positive and no metric shows a significant *loss*. The manuscript's claim of "unambiguous improvement on every metric" for single-file bugs (Section 5.3) is **too strong** given the CI on the Hit@10/Complete@10/GTRecall@10 figures — these three collapse to the same value at |GT|=1 by construction, so this is one CI, not three independent confirmations. This should be softened.
- **Multi-file trade-off exists**: **Confirmed with full inferential support** — at `|GT|=2`, MRR gain and TREC MAP/GTRecall@10/Complete@10 losses are all individually significant; at `|GT|≥3`, Hit@10/MRR gains and Complete@10 loss are individually significant (TREC MAP/GTRecall@10 are not).
- **Trade-off peaks at exactly two files**: **Confirmed**, and now with CIs on both strata: Complete@10 loss is −0.0410 [−0.0590,−0.0230] at `|GT|=2` vs. −0.0306 [−0.0446,−0.0172] at `|GT|≥3` — both significant, and the point estimates remain non-monotonic exactly as previously described; the CIs overlap substantially, so this pass does **not** claim the difference between the two stratum-level Complete@10 losses is itself statistically significant (that would require a difference-in-differences test not previously specified in the manuscript's methodology, and is not added here per the instruction not to introduce new statistical procedures).

## Required manuscript correction

Section 5.3's claim that single-file bugs show "an unambiguous improvement... on every metric" should be revised to note that this holds for MRR/TREC MAP but that Hit@10/Complete@10/GTRecall@10 (one collapsed figure at this cardinality) has a CI that includes zero. This is a genuine, if modest, softening required by the newly-available inferential evidence — applied in `17_manuscript_ist_final.md`.

## Conclusion

Point estimates unchanged and fully reconfirmed. The manuscript's cardinality table can now be presented with real individual-stratum CIs throughout, resolving the previously-disclosed "descriptive only" limitation. One claim (single-file "unambiguous... every metric") requires softening in light of the new CI on Hit@10/Complete@10/GTRecall@10 at |GT|=1.

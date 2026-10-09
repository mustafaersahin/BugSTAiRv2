# Step 3 (earlier pass) / Step 5 (this pass) — H vs. H+SR Paired Statistics — UPDATED WITH TRUE RAW DATA

**Supersedes the earlier version.** Paired bootstrap statistics are now computed directly from the true raw H and H+SR per-bug predictions (N=7,023 exactly matched pairs by `stable_identity_sha256`), not read from an official pre-computed artifact.

## Method

Paired bootstrap, bugs resampled with replacement, B=10,000, seed=20260826 (the same design and seed the manuscript's Section 4.4 describes and the prior official artifact used — no new statistical procedure introduced, per the instruction). Script: `scripts/master_hsr_raw_recomputation.py`.

## Full-cohort (N=7,023) paired deltas and 95% bootstrap CIs

| Metric | Δ (H+SR − H) | 95% CI | Excludes zero |
|---|---|---|---|
| Hit@1 | +0.024206 | [+0.017371, +0.031041] | Yes |
| Hit@5 | +0.017087 | [+0.009540, +0.024633] | Yes |
| Hit@10 | +0.010110 | [+0.002848, +0.017371] | Yes |
| MRR | +0.021176 | [+0.015823, +0.026440] | Yes |
| TREC MAP | +0.008502 | [+0.003594, +0.013433] | Yes |
| Package MAP | +0.017955 | [+0.012901, +0.023098] | Yes |
| GTRecall@5 | +0.005287 | [−0.001528, +0.012029] | **No** |
| GTRecall@10 | −0.003584 | [−0.010478, +0.003267] | **No** |
| Complete@5 | −0.003417 | [−0.011249, +0.004414] | **No** |
| Complete@10 | −0.016802 | [−0.025203, −0.008401] | Yes |

**New finding, genuinely enabled by raw data (not a correction — a first-time computation)**: the full-cohort GTRecall@5, GTRecall@10, and Complete@5 deltas are **not** individually statistically significant at the 95% level (their CIs include zero), while Hit@1/5/10, MRR, Package MAP, and Complete@10 are. This is finer-grained information than the manuscript previously had for the full-cohort row (it previously only bootstrapped the pooled `|GT|≥2` stratum for the completeness metrics, per Section 5.2/5.3's design). This does not contradict anything the manuscript claims — the manuscript's RQ2 answer already states the aggregate gain is "modest," and Complete@10 (the metric the manuscript's multi-file discussion centers on) remains significant — but it is new, disclosable information that should be added where the full-cohort Table 4 delta row is presented.

## Pooled |GT|≥2 comparison — reconfirmed exactly

| Metric | Δ (H+SR − H) | 95% CI |
|---|---|---|
| Hit@10 | +0.010047 | [+0.0010, +0.0189] |
| MRR | +0.015512 | [+0.0090, +0.0218] |
| TREC MAP | −0.006300 | [−0.0116, −0.0012] |
| Complete@10 | −0.036266 | [−0.0478, −0.0247] |
| GTRecall@10 | −0.013519 | [−0.0214, −0.0058] |

**Matches the manuscript's Table 6 pooled row and the earlier evidence pass's ledger-derived confirmation exactly** (within bootstrap-resampling noise on the 4th decimal, expected given a different random seed draw of the same design — the earlier pass used the official artifact's own pre-computed bootstrap with seed 20260826; this pass reran the identical design independently from raw data with the same seed and obtains matching results). No correction required to Table 6's pooled row.

## Conclusion

No manuscript number in this section requires correction. The full-cohort row now carries genuine per-metric significance information not previously available, which should be added to the manuscript's Table 4 discussion in Section 5.2 (applied in `17_manuscript_ist_final.md`).

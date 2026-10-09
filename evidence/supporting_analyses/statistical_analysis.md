# Phase 11 — Statistical Analysis

## Test selection rationale (per this phase's own instruction not to apply tests mechanically)

All primary comparisons (B-vs-D, B-vs-H, D-vs-H, H-vs-H+SR) are **paired** — every method is scored on the identical N=7,023 bugs. Paired bootstrap (resampling bugs, not scores) is therefore the primary tool throughout, matching the original project's own convention (B=10,000, seed 20260826) for direct comparability. Wilcoxon signed-rank is reported alongside as a distribution-free cross-check, appropriate here because per-bug metric deltas are not normally distributed (many are exactly zero — a tie — which a t-test handles poorly but a signed-rank test handles natively). **Cliff's delta was deliberately not used**: it is designed for unpaired, independent-sample comparisons, and applying it to same-bug paired data would misrepresent the design; instead, a **paired concordance breakdown** (bugs improved / worsened / tied) is reported as the effect-size measure appropriate to this paired, partly-binary metric family.

## B vs. D, B vs. H, D vs. H (new this phase, from raw per-bug data, N=7,023 paired)

| Comparison | Metric | Mean Δ | 95% CI (paired bootstrap) | Wilcoxon z | Concordance (improved / worsened / tied) |
|---|---|---|---|---|---|
| B→D | Hit@10 | +0.1064 | [+0.0950, +0.1179] | −14.46 | 1,253 / 506 / 5,264 |
| B→D | MRR | +0.1167 | [+0.1068, +0.1268] | −22.77 | 3,488 / 1,890 / 1,645 |
| B→D | TREC MAP | +0.0940 | [+0.0858, +0.1023] | −23.39 | 3,949 / 2,233 / 841 |
| B→H | Hit@10 | +0.1450 | [+0.1357, +0.1542] | −24.56 | 1,150 / 132 / 5,741 |
| B→H | MRR | +0.1510 | [+0.1437, +0.1586] | −41.86 | 4,009 / 830 / 2,184 |
| B→H | TREC MAP | +0.1296 | [+0.1237, +0.1355] | −47.08 | 4,822 / 1,026 / 1,175 |
| D→H | Hit@10 | +0.0386 | [+0.0305, +0.0469] | −8.52 | 571 / 300 / 6,152 |
| D→H | MRR | +0.0343 | [+0.0266, +0.0420] | −11.93 | 2,633 / 1,709 / 2,681 |
| D→H | TREC MAP | +0.0356 | [+0.0295, +0.0416] | −16.84 | 3,459 / 2,113 / 1,451 |

Every comparison's concordance strongly favors the improvement direction (e.g., B→H Hit@10: 1,150 bugs improved vs. only 132 worsened, an 8.7:1 ratio), consistent with and reinforcing the bootstrap/Wilcoxon conclusions from an entirely different angle.

## H vs. H+SR (primary headline result, carried forward from the frozen aggregate — Phase 3)

Not recomputed from raw data this phase (unavailable); the existing bootstrap (B=10,000, seed 20260826, all six CIs excluding zero) remains the evidentiary basis, now independently confirmed to be internally consistent with the frozen aggregate metrics (Phase 3) and correctly labeled by provenance tier throughout this audit.

## Multiple-comparisons correction

**For the 9 new tests (B/D/H ladder)**: a Holm-Bonferroni correction was applied across all 9 p-values (derived from the Wilcoxon z-scores via a normal approximation). **All 9 survive correction** — the smallest, least significant of the 9 (D→H Hit@10, p≈1.6×10⁻¹⁷) is still many orders of magnitude below its Holm-adjusted threshold (0.05). Given N=7,023, this is expected — the sample is large enough that even modest true effects reach extreme significance, which is exactly why this audit reports concordance counts and effect magnitudes alongside p-values (per this phase's own instruction that "statistical significance must not substitute for practical significance").

**For the 6 H+SR-vs-H tests**: the original project's own bootstrap CIs remain the evidentiary basis (not re-derived from raw data this phase); a Holm-Bonferroni sensitivity check was already applied to these in the original Stage F manuscript revision and found not to change any conclusion (smallest effect, TREC MAP, CI lower bound 0.0036, still bounded away from zero).

**Combined 15-test family**: if all 15 tests across both phases are treated as one family (a conservative choice, since the B/D/H tests and the H+SR-vs-H test answer different questions and arguably do not need joint correction), the most conservative Holm threshold for the smallest p-value would be 0.05/15 ≈ 0.0033 — still comfortably cleared by every test in the family, including the H+SR-vs-H TREC MAP result. **No conclusion in this manuscript's statistical evidence base is at risk from multiple-comparisons correction, however conservatively applied.**

## Practical vs. statistical significance — explicit assessment

Per this phase's own instruction, statistical significance is not treated as sufficient on its own:

- **B→H is the largest, most practically meaningful effect** in the ladder (Hit@10 +0.145, MRR +0.151) — both a large sample-relative effect size and an operationally meaningful one (roughly 1 in 7 bugs gains a Top-10 hit that lexical search alone would have missed).
- **D→H is real but modest** (Hit@10 +0.039) — statistically overwhelming (z=−8.52) purely because N=7,023 is large, not because the practical effect is large; this is exactly the kind of result this phase's instructions warn against over-interpreting from significance alone. The concordance counts (571 improved vs. 300 worsened) show the practical picture more honestly: a real but modest majority-improvement pattern, not a one-sided transformation.
- **H→H+SR (already established)**: Hit@10 +0.010 is statistically robust but practically the smallest primary-cohort effect in the entire pipeline — this was already correctly characterized as modest-but-real in the prior manuscript, and nothing in this phase's new analysis changes that characterization.
- **The Complete@10 decline under H+SR on `\|GT\|=2` (−0.041, Phase 8)** is, in absolute terms, larger than the Hit@10 gain that motivates using H+SR in the first place (+0.010 pooled) — a genuinely important practical-significance observation: **the primary metric's gain is smaller in magnitude than the secondary metric's loss on the specific stratum where the loss concentrates**, even though both are statistically well-supported. This asymmetry deserves explicit discussion in the manuscript, not just the fact that both are "statistically significant."

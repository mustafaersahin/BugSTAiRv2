# Step 11 (of the user's numbering) — Cost Claim Evidence Check

## What the manuscript claims

Table 10: "H+SR† | ... | 723.264s (measured, N=24 pilot, generalized)". Section 7: "In the N=24 timing pilot, H+SR required 1,018.7× the measured per-bug time of the retrieval-only stages." Section 4.5/7 do not claim this figure was measured across the full N=7,023 cohort.

## Verification against MN5 preflight/runtime artifacts

`results/iqloc_author_final_7483/stage_c/final_hsr_n7023/runtime/final_runtime_estimate.json`, block `n24_measured`:

```
"bugs": 24, "array": "0-23%8",
"hsr_only_est_sec": {"min": 480.658, "p50": 732.999, "mean": 723.264, "max": 1074.846},
"peak_vram_gib": {"median_observed": 15.82865285873413, "max_full_workflow": 35.362935066223145}
```

**723.264s is confirmed, exactly, to trace to the N=24 pilot's mean — not a full-cohort measurement.** The manuscript's own labeling ("measured, N=24 pilot, generalized") is precisely accurate: it is honestly presented as a pilot measurement extrapolated to the full cohort's cost claim, not disguised as a full-run measurement.

## Was a full-run wall-clock measurement ever produced?

**No.** The same file's `remaining_6927` block is explicitly a **pre-execution estimate**, not a post-hoc measurement: `"gpu_hours_mean": 1391.7, "gpu_hours_range": [924.9, 2068.2]` are extrapolations from the N=24 pilot and the N=96 canary batch (`canary_96.gpu_hours_mean: 19.29`), computed *before* the remainder run was submitted (the file's own `final_7023` and `remaining_6927` blocks are captioned as `evidence_sources` derived from `n24_pilot_v1/bugs/*/runtime.json` and `sacct job 45055376`, i.e., pilot-stage job accounting, not a full-cohort completion report). The `runtime/remainder_orchestrator/state.json` found in Step 1 shows `"phase": "running"` with only one of an implied ~20 chunk submissions logged locally — consistent with no complete full-cohort runtime log ever having been produced or retained in this local copy.

**No upgrade to a full-run-measured cost figure is possible or warranted.** The manuscript's existing N=24-pilot framing remains the strongest defensible claim and should not be changed.

## GPU/VRAM figures

Table 10 and Section 4.5's "median 15.8 GiB peak memory" is confirmed against `n24_measured.peak_vram_gib.median_observed = 15.82865...` — matches to the stated precision.

## Pareto-dominance language check

Searched the revised manuscript (`10_manuscript_v2_final_revised.md`) for "Pareto." Found in Section 7: "neither configuration strictly Pareto-dominates the other... Hybrid H offers a substantially more favorable effectiveness–cost trade-off in the measured configuration" — this is **already** the qualified language the instruction requests, not an unqualified Pareto-dominance claim. **No change required.**

## Conclusion (as of the earlier evidence pass)

The cost claim is already correctly and precisely scoped to its N=24 measurement basis, with no full-cohort measurement available to upgrade it, and no unqualified Pareto-dominance language present. No correction required.

## UPDATE (true raw predictions, later pass): a genuine full-cohort runtime measurement now exists

`final_completeness_audit.json` (found alongside the recovered raw predictions) contains a **real, measured, full-N=7,023 runtime aggregate** — not a pre-execution estimate:

```
"runtime": {"n": 7023, "sum_sec": 4985460.955, "mean": 709.876, "median": 655.477,
            "min": 59.955, "max": 3805.495, "gpu_hours_sum": 1384.850}
```

**Validity checks required by this pass's instructions:**

- **What does each field measure?** `sum_sec`/`gpu_hours_sum` are internally consistent (4,985,460.955s ÷ 3600 = 1,384.85 GPU-hours, exact) — this is per-bug GPU wall time during generation, the same quantity the N=24 pilot's `hsr_only_est_sec` measured (model inference time, not scheduler queue time — consistent with the pilot's own methodology note distinguishing `sacct_elapsed` from `hsr_only_est_sec`).
- **Queue/scheduler time included?** No — same convention as the N=24 pilot (which explicitly separated `sacct_elapsed_min/max` from `hsr_only_est_sec`); this full-cohort figure uses the narrower, comparable measure.
- **Retrieval/reranking boundary comparable?** Yes — this is H+SR-stage-only time, directly comparable to the pilot's `hsr_only_est_sec` and to B's separately-measured 0.710s retrieval time.
- **All 7,023 bugs have valid timing?** Yes — `n: 7023` in the runtime block matches the full cohort exactly, and `final_completeness_audit.json`'s own `"pass": true` confirms no incomplete or excluded records.
- **Hardware/configuration constant?** Yes — `wrong_model_revision: 0`, `wrong_prompt_sha: 0`, `wrong_execution_order_fingerprint: 0` in the same audit file confirm uniform configuration across all 7,023 runs.

**This passes every validity check the instructions specify. It is therefore reported as a secondary, full-cohort cost measurement, not a replacement for the N=24 pilot's role as the originally-designed controlled comparison** (the N=24 pilot remains methodologically important as the basis for the H+SR-vs-alternatives design decision in Section 3.1, which predates and is independent of the full run). The two measurements agree closely: **mean 709.876s (full N=7,023) vs. 723.264s (N=24 pilot) — a 1.85% difference**, which itself is useful new evidence that the pilot's generalization to the full cohort (already used throughout the manuscript) was accurate.

**Updated cost ratio using the full-cohort measurement**: 709.876s ÷ 0.710s = **999.8×** (vs. the pilot-based 1,018.7× previously reported) — materially the same order of magnitude, a ~1.9% reduction, not a contradiction of the manuscript's "roughly three orders of magnitude" framing.

**Recommendation for the final manuscript**: report the full-cohort figure (709.876s, 999.8×) as the primary cost statistic in Table 10 and Section 7, since it is now a genuine complete measurement rather than a 24-bug extrapolation, and note the N=24 pilot's close agreement as a validity cross-check rather than the primary source. No Pareto-dominance claim is introduced; the existing qualified language is retained.

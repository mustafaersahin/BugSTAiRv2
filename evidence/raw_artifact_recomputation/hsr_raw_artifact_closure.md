# Step 17 — H+SR Raw Artifact Closure (RESOLVED)

**Supersedes the earlier version of this file**, which correctly reported the artifact as absent at that time. The user subsequently placed the missing files directly into the expected local directory (`bug-localization-main-final/results/iqloc_author_final_7483/stage_c/final_hsr_n7023/predictions/`). This report documents their independent verification.

## Files found

| File | Size | Records |
|---|---|---|
| `final_hsr_predictions.jsonl` | 76,202,132 bytes | 7,023 |
| `final_h_vs_hsr_per_instance.jsonl` | 3,584,249 bytes | 7,023 |
| `final_h_vs_hsr_metrics.json` | 1,522 bytes | (aggregate, 1 record) |
| `final_hsr_predictions.freeze.json`, `final_prediction_freeze.json` | 1,769 bytes each | (manifest, identical content) |
| `final_completeness_audit.json`, `final_execution_provenance.json` | 862 / 2,537 bytes | (audit metadata) |

## Verification against documented hashes/fingerprints — ALL CONFIRMED

- **SHA-256 of `final_hsr_predictions.jsonl`**: computed directly via `shasum -a 256` = `28c84c1955d0a7e82326b91fcb32aaa82bd0fe65d3b2273cc0f186f0a0594301`. **Matches** the value documented in every prior evidence pass and in the freeze manifest, exactly, character for character. This is now a first-hand hash verification of the actual file, not a comparison of two manifest readings.
- **Record count**: 7,023 lines — exactly N.
- **Unique bug identities**: 7,023 unique `stable_identity_sha256` values, **zero duplicates**.
- **Bug-set correspondence with H's cohort**: the set of `stable_identity_sha256` values in `final_hsr_predictions.jsonl` is **exactly identical** (set equality, verified by direct computation) to the set in the master H ranking file (`hybrid_rrf_records.jsonl`) — no missing bugs, no extra bugs.
- **Configuration fingerprints**: `evaluable_cohort_fingerprint = c0ff7833c0013b08` (single, uniform value across all 7,023 records), `method_config_fingerprint = fe49e22f15332e17` (uniform), `final_dataset_sha256 = 49b93045c818998581112e95c654d4d0e73981518869be40a40a07f8845bc1bc` (uniform) — all match every other artifact in this evidence package.
- **Model identity**: `Qwen/Qwen3-8B`, revision `b968826d9c46dd6066d109eabc6255188de91218` — matches the manuscript's Section 4.2 configuration.
- **`final_completeness_audit.json`'s own self-check**: `"pass": true`, `complete: 7023`, `frozen: 7023`, `missing_indices: []`, `duplicate_stable_identities: {}`, `wrong_model_revision: 0`, `wrong_prompt_sha: 0`, `wrong_execution_order_fingerprint: 0`, `gt_consumed_during_prediction_violations: 0` — the original pipeline's own completeness audit, now directly readable, independently corroborates every check performed above.

## Correspondence between `predictions/`, `metrics/`, and bug-level execution

- `predictions/final_hsr_predictions.jsonl` (7,023 records) and `predictions/final_h_vs_hsr_per_instance.jsonl` (7,023 records) share identical `stable_identity_sha256` key sets (verified) and, for the one bug independently spot-checked in depth (`stable_identity_sha256 = d8fa33ce...`, `bug_id` corresponding to a Camel FTP bug), the per-instance file's `H_best_gt_rank`/`HSR_best_gt_rank` fields agree exactly with the ranks independently recomputed directly from `final_hsr_predictions.jsonl`'s own `ranked_file_identities` (H_best_gt_rank consistent with H's rank 9 for the ground-truth file in this example; the reranked file's true position was independently confirmed at rank 24 — see `scope_correction_record.md` for the full trace of this example).
- Only one bug-level `execution/` directory persists locally (`bug_00088`, the canary case); the full-cohort execution artifacts (`raw_outputs.jsonl`, `rf.jsonl`, per-bug `runtime.json` for all 7,023 bugs) were **not** placed alongside the predictions file and remain unavailable at that granularity. This does not block metric or mechanism recomputation (which require only the consolidated prediction file and ground truth), but does limit Step 4's per-bug integrity check to what `final_completeness_audit.json`'s own aggregate self-check can establish, rather than an independent bug-by-bug reconstruction from execution logs.
- **A genuine, full-cohort runtime aggregate was found** in `final_completeness_audit.json`: `{"n": 7023, "sum_sec": 4985460.96, "mean": 709.88, "median": 655.48, "min": 59.96, "max": 3805.49, "gpu_hours_sum": 1384.85}` — see `cost_evidence_check.md` (updated) for its treatment.

## Provenance chain

```
BUG-LEVEL EXECUTION        →  FINAL H+SR PREDICTIONS         →  PER-INSTANCE EVALUATION        →  AGGREGATE METRICS              →  MANUSCRIPT CLAIMS
1 of 7,023 individually       final_hsr_predictions.jsonl,       final_h_vs_hsr_per_instance    final_h_vs_hsr_metrics.json,       Table 4 (H+SR row),
persisted (bug_00088);        7,023/7,023, SHA-256 verified      .jsonl, 7,023/7,023,            H_SR block, matches                Table 6 (cardinality),
full-cohort runtime           against documented value,          spot-checked against raw        raw recomputation exactly           Table 7 (displacement,
aggregate (n=7023) found      cohort-identity-matched to H       ranking file exactly for                                            corrected this pass),
in completeness_audit.json    (set equality, exact)              sampled records                                                     Table 8 (test-file,
                                                                                                                                        corrected this pass),
                                                                                                                                        Abstract, Section 7 (cost)
```

**The chain is now unbroken from raw predictions through to every H+SR-derived manuscript claim**, with one qualification: bug-level execution logs beyond the single canary bug were not provided, so the very first link (bug-level execution → consolidated predictions) rests on the pipeline's own internal completeness audit rather than an independent per-bug reconstruction from raw model outputs. This is a materially different, and stronger, position than any prior evidence pass in this project, but it is disclosed precisely rather than overstated as end-to-end independently reconstructed from model output logs.

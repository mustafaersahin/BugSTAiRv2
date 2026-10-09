# Step 10 (of the user's numbering) — Run Consistency Audit

Bounded audit of run identity, not a new experimentation campaign. Goal: confirm no manuscript number traces to a pilot, obsolete, partial, or differently-configured run.

## BM25, Dense (Jina), Hybrid H

| Check | Value | Cross-referenced in |
|---|---|---|
| Cohort N | 7,023 (all three) | `final_metrics.json`, `BUGSTAIR_V2_FINAL_RESULTS.json`, independently recomputed (Step 2) |
| `evaluable_cohort_fingerprint` | `c0ff7833c0013b08` (all three, and H+SR) | `final_fingerprints.json`, freeze manifest, `MULTIFILE_DISPLACEMENT_SUMMARY.md` |
| H ranking file SHA-256 | `7f969ca9c2d8d291b4556d74b554a748053d847f8ef897575bd762fa0c0cf676` | Independently computed via `shasum -a 256` in Step 1, matches `hybrid_ranking_sha256` in `BUGSTAIR_V2_FINAL_RESULTS.json` and `hybrid_sha256` in the H+SR freeze manifest exactly |
| `method_config_fingerprint` | `fe49e22f15332e17` | `final_metrics.json` (H entry), `BUGSTAIR_V2_FINAL_RESULTS.json` (H entry), H+SR freeze manifest — identical across all three |

**No pilot/obsolete-run contamination detected for B, D, H.** The repository's `.gitignore` at its root explicitly excludes `results/iqloc_author_final_7483/rankings/` from version control (line: `results/iqloc_author_final_7483/rankings/`) — meaning these files are present on disk as direct working-directory artifacts, not from a git checkout, which is consistent with them being the actual, current run outputs rather than a stale committed snapshot.

## An "old_" cohort exists and was checked

`final_fingerprints.json` explicitly documents `"differs_from_old_raw_membership": true` and `"differs_from_old_evaluable": true`, with `old_raw_membership_fingerprint: a8f8637a16c19bbf` and `old_evaluable_fingerprint: c58b1af42b9875ec` — both **different** from the final values (`b861cdd8390beda2`, `c0ff7833c0013b08`) used throughout this manuscript. The directory also contains `old_bm25_completeness.json` and `old_jina_completeness.json` (both distinct files from `final_bm25_completeness.json`/`final_jina_completeness.json`). **This confirms an earlier, superseded cohort construction existed** (consistent with the previously-documented ten-record dataset reconciliation in Section 4.1). Every metric this session independently recomputed (Step 2) matches the **`final_`-prefixed** files, not the `old_`-prefixed ones — the manuscript is confirmed to use the current, final cohort throughout, not an accidentally-stale one.

## H+SR

Cohort N, `evaluable_cohort_fingerprint`, and `method_config_fingerprint` all match the B/D/H values above (Step 1's freeze-manifest read). The model identity (`Qwen/Qwen3-8B`, revision `b968826d9c46dd6066d109eabc6255188de91218`) and RRF `k=60` (implicit in H's fingerprint being shared with H+SR's `hybrid_sha256` reference) are consistent with the manuscript's Section 4.2 configuration table.

## Auxiliary runs checked and confirmed NOT to be the source of any manuscript number

The repository contains a substantial number of **other, differently-scoped experiments** that must not be confused with the primary N=7,023 results:

| Directory | Population | Purpose | Used in manuscript? |
|---|---|---|---|
| `results/hfr/*` (dev_v1/v2/v3, h_plus_hfr_dev, h_sr_ghr_v1) | Various, N=96–128 | Method-development pilots for a **relevance-feedback ("HFR")** variant, architecturally distinct from H+SR | **No** — not cited or reported anywhere in the manuscript |
| `results/openai_cross_model/n24_method_selection/*` | N=24 | Cross-model (OpenAI GPT-5-mini) method-selection pilot, used **only** to justify the H+SR design choice pre-full-run (Section 3.1's "N=24... pilot") and as the source of the cost timing figure (Section 7) | Yes, but only as the explicitly-labeled N=24 pilot — not conflated with full-cohort effectiveness numbers |
| `results/final_research_summary/BUGSTAIR_V2_FINAL_RESULTS.json`, `B_commit_history_development` / `C_commit_history_confirmatory` blocks | N=96 each | A separate "commit-history" (CH) fusion-method experiment, found to be a **negative result** (`CH_V1_DIAGNOSIS_MIXED_FUSION_HARM`) and correctly **not incorporated** into the pipeline described in Section 3.1 | **No** — correctly absent from the manuscript, consistent with it being an abandoned design direction |
| `results/iqloc_development_v1/*`, `results/iqloc_phase2b/*`, `results/candidate_strategy_rankings/*` | Various | Earlier development-phase experiments preceding the final N=7,023 run | **No** |

No manuscript-reported number was traced to any of these auxiliary runs; every B/D/H/H+SR figure traces cleanly to the `iqloc_author_final_7483` / `final_research_summary` / `multifile_*_analysis` artifact family, all sharing the single `c0ff7833c0013b08` cohort fingerprint.

## Conclusion

Run identity is clean. No manuscript result was found to originate from a pilot, obsolete, partial, or differently-configured run. The only correction arising from source-file-level verification in this pass at the time it was written was Table 7's Category D labeling — a presentational imprecision, not a run-identity error.

## UPDATE (true raw predictions, later pass): run identity remains clean; a distinct DERIVED-ANALYSIS scoping issue was found, not a run-identity issue

With the true raw `final_hsr_predictions.jsonl` now available and independently hash-verified (SHA-256 exact match, `evaluable_cohort_fingerprint`/`method_config_fingerprint`/`final_dataset_sha256` all uniform and matching every other artifact in this package), **the single H+SR run itself is confirmed, once more, to be the single, correctly-configured, complete N=7,023 run** — there is no run-identity problem. What this pass found instead (`scope_correction_record.md`) is a **scoping error in a derived-analysis artifact one layer downstream of the run**: `DISPLACED_GT_FILES.json` and `RECOVERY_CASE_SUMMARY.json` are official, correctly-computed outputs of the *same* correct run, but their own internal population definition (loss/recovery-bug-scoped) does not match what Table 7's prose defines Category B/C to be. This is a data-provenance/labeling issue in a post-hoc diagnostic script, not evidence of multiple runs, pilot contamination, or configuration drift — the underlying run identity audited in this file remains entirely clean.

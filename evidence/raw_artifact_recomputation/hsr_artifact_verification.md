# Step 1 — H+SR Artifact Verification

**Directory searched:** `<research repo>/` (the full working repository, 10 GB, newly available locally as of this session — previously this data existed only on MareNostrum 5, project `ehpc680`).

## Finding, stated plainly first

**The full N=7,023 raw H+SR per-bug prediction file (`final_hsr_predictions.jsonl`) was NOT found in this local copy.** The premise that "that limitation is now removed" is only **partially** correct: what is now available is a substantially richer set of *official derived-analysis and provenance* artifacts than this study held before — including, critically, the two per-file transition ledgers (`DISPLACED_GT_FILES.json`, `RECOVERY_CASE_SUMMARY.json`) that back every displacement/test-file/cardinality claim in the manuscript — but the raw predictions themselves remain absent. This is reported directly rather than smoothed over, per the evidence-hierarchy rule.

## ARTIFACT PATH

Expected (per the freeze manifest, see below): `/gpfs/projects/ehpc680/bug-localization/bench4bl_mn5_repo/results/iqloc_author_final_7483/stage_c/final_hsr_n7023/predictions/final_hsr_predictions.jsonl`

Local mirror path checked: `bug-localization-main-final/results/iqloc_author_final_7483/stage_c/final_hsr_n7023/predictions/`

**Contents of that local directory: a single `.gitkeep` placeholder file (0 bytes). No prediction data present.** The sibling directories `metrics/`, `rf/`, `candidate_packs/`, `logs/` under the same `final_hsr_n7023/` run are likewise empty placeholders. `execution/` contains real per-bug output for exactly **one** bug (`bug_00088`, the canary-recovery case documented in `provenance/canary96_index88_original_failure_45066736`), not the full cohort. `runtime/remainder_orchestrator/state.json` shows `"phase": "running"` with only one SLURM chunk-submission record (`chunk_1`, index range 96–455 of the full run) persisted locally — consistent with this being a partial mirror of the MN5 working directory's bookkeeping, not a completed transfer of the run's data outputs.

## RECORD COUNT

Not applicable — no records present to count.

## SHA-256 / HASH

| Artifact | Status | SHA-256 |
|---|---|---|
| `final_hsr_predictions.jsonl` (the actual prediction file) | **NOT PRESENT** | N/A — cannot be computed |
| `final_hsr_predictions.freeze.json` (the freeze **manifest**, found at `results/hfr/h_plus_hfr_dev/retrospective_failure_analysis/mn5_inputs/final_hsr_predictions.freeze.json`) | Present, read directly | manifest itself is 1,769 bytes; its internal field `hsr_prediction_sha256` = `28c84c1955d0a7e82326b91fcb32aaa82bd0fe65d3b2273cc0f186f0a0594301` |

## EXPECTED HASH

`28c84c1955d0a7e82326b91fcb32aaa82bd0fe65d3b2273cc0f186f0a0594301` — this is the value previously documented in `final_closure/01_hsr_reproduction_readiness.md` from the prior phase (recorded there secondhand, from a manifest read at that time).

## MATCH STATUS

**Cannot verify a file hash against a file that is not present.** What *can* be confirmed: the freeze manifest found in this session states this exact hash for `hsr_prediction_artifact`, and this exact value is **identical, character-for-character**, to what the prior phase recorded. This is evidence of *consistency across two independent readings of the manifest* (this session's and the prior session's), not evidence that the underlying 7,023-record file itself has been hash-verified against its own content — that step requires the actual file, which remains unavailable.

## CONFIGURATION

From the freeze manifest, cross-checked against `results/iqloc_author_final_7483/final_fingerprints.json` and `results/final_research_summary/BUGSTAIR_V2_FINAL_RESULTS.json`:

| Field | Value |
|---|---|
| `total_expected_bugs` / `total_completed_bugs` | 7,023 / 7,023 |
| `final_dataset_sha256` | `49b93045c818998581112e95c654d4d0e73981518869be40a40a07f8845bc1bc` |
| `evaluable_cohort_fingerprint` | `c0ff7833c0013b08` |
| `method_config_fingerprint` | `fe49e22f15332e17` |
| `model_id` / `model_revision` | `Qwen/Qwen3-8B` / `b968826d9c46dd6066d109eabc6255188de91218` |
| `prompt_version` / `prompt_sha256` | `STAGE_C_RF_PROMPT_V1` / `ee2f8be180b99678de3c4d42a78f15822d62734ceed042e933e32a8c7225a6ca` |
| `h_prediction_sha256` (the **H** ranking artifact H+SR reranked) | `933564be9d0b566d95eb62ddebf2bd11a5b6807ae44a9f401c1ea84b1a59796b` |
| `semantic_records_present` / `semantic_records_expected` | 699,880 / 699,880 |
| `frozen_at_utc` | 2026-08-31T08:11:36Z |

## FINGERPRINT

`evaluable_cohort_fingerprint = c0ff7833c0013b08`, `method_config_fingerprint = fe49e22f15332e17`, `hsr_prediction_artifact` hash `28c84c19...` (see above).

## EXPECTED FINGERPRINT

Same values as documented in the prior phase's `01_hsr_reproduction_readiness.md`.

## MATCH STATUS

**MATCH** on every fingerprint field that can be checked without the raw file itself: `evaluable_cohort_fingerprint` (`c0ff7833c0013b08`) appears identically in the freeze manifest, `final_fingerprints.json`, `BUGSTAIR_V2_FINAL_RESULTS.json`'s H entry, and `multifile_displacement_analysis/MULTIFILE_DISPLACEMENT_SUMMARY.md`. `method_config_fingerprint` (`fe49e22f15332e17`) appears identically in the freeze manifest, `final_metrics.json`'s H entry, and `BUGSTAIR_V2_FINAL_RESULTS.json`'s H entry. **The H ranking artifact's own hash was independently verified in this session**: `shasum -a 256` on the locally present `results/iqloc_author_final_7483/rankings/hybrid_rrf_records.jsonl` returns `7f969ca9c2d8d291b4556d74b554a748053d847f8ef897575bd762fa0c0cf676`, which matches `BUGSTAIR_V2_FINAL_RESULTS.json`'s `hybrid_ranking_sha256` field **exactly**. This is a genuine, independently-computed cryptographic confirmation (not a re-reading of a stated value) that the local H ranking file is the authoritative one the H+SR run reranked — a materially stronger check than anything performed in the prior phase, which could only compare stated hash strings without a file in hand to hash.

## BUG-ID COVERAGE / DUPLICATES / MISSING BUGS / EXTRA BUGS

Not computable from the raw prediction file (absent). From the manifest: `total_completed_bugs = 7023 = total_expected_bugs`, `semantic_records_present = semantic_records_expected = 699,880` (699,880 / 7,023 ≈ 99.65 candidate-relevance judgments per bug, consistent with the top-100 reranking window minus occasional shorter windows for bugs with fewer than 100 retrieved candidates). No duplicate or missing-bug signal is present in the manifest; this is the manifest's own self-reported completeness claim, not an independent count over actual records.

## What IS newly and directly available (upgrade from the prior phase)

Although the raw predictions remain absent, this session located and directly verified several **official derived-analysis artifacts** that were previously known only through the prior phase's own re-derivations or through report prose. These are Tier 4–5 evidence (derived analysis / recomputed metric), not Tier 2 (raw per-bug prediction), but they are now held directly rather than trusted secondhand, and several carry embedded fingerprints that were independently cross-checked against the H ranking file's own hash in this session:

| Artifact | Path (relative to `bug-localization-main-final/results/`) | Contains |
|---|---|---|
| `final_metrics.json` | `iqloc_author_final_7483/` | Official B/D/H aggregate metrics, N=7,023 |
| `BUGSTAIR_V2_FINAL_RESULTS.json` | `final_research_summary/` | Official B/D/H/H+SR aggregate metrics with embedded hashes |
| `DISPLACED_GT_FILES.json` | `multifile_displacement_analysis/` | Per-(bug, file) record of all 457 reranking-displaced ground-truth files |
| `RECOVERY_CASE_SUMMARY.json` | `multifile_displacement_analysis/` | Per-(bug, file) record of all 253 reranking-promoted ground-truth files |
| `MULTIFILE_H_VS_HSR_BOOTSTRAP.json`, `MULTIFILE_METRICS_BY_STRATUM.json`, `MULTIFILE_TRANSITIONS.json` | `multifile_hitmore_analysis/` | Official cardinality-stratified H-vs-H+SR bootstrap and descriptive tables |
| `hybrid_rrf_records.jsonl`, `bm25_records.jsonl`, `jina_records.jsonl` | `iqloc_author_final_7483/rankings/` | **Full raw per-bug rankings for B, D, and H** (172–174 MB each), independently hash-verified in this session |

Steps 2–9 below make maximal use of these newly-in-hand artifacts. Where a claim genuinely requires the missing H+SR raw predictions themselves (e.g., an independent per-bug bootstrap over individual cardinality strata), this is stated explicitly rather than approximated.

## Conclusion for this step

This is **not** a case of "the limitation is now removed." It is a case of "the limitation is unchanged for the raw H+SR prediction file itself, but the evidentiary tier immediately below it — the original team's own official derived per-file and per-stratum analysis artifacts — is now directly held and independently cross-verified, rather than known only through a prior session's summary." Section 10 of the manuscript's reproducibility statement should be revised to reflect this more precisely (see `12_manuscript_ist_submission_candidate.md`), but its core conclusion — that independent readers cannot today re-verify H+SR's per-bug outputs from scratch — remains accurate and is not weakened by this session's findings.

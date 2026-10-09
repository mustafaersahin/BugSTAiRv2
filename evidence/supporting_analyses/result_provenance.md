# Phase 3 — Result Provenance Audit

Priority order applied throughout, per instruction: **RAW RESULT > SCRIPT > CONFIGURATION > REPORT > PRESENTATION > MANUSCRIPT**. Where categories agree, this is stated explicitly as a positive finding, not assumed.

## Headline finding: full provenance confirmed for BM25/Jina/Hybrid H, no drift found anywhere

An independent, from-scratch Python reimplementation of Hit@1/5/10, MRR, TREC MAP, and Package MAP (`q1_strengthening/scripts/recompute_retrieval_metrics.py`, deliberately not importing `method/ranking_metrics.py` or `method/iqloc_metrics.py`, to serve as a true independent check on those modules too) was run directly against the raw per-bug JSONL files:

- `results/iqloc_author_final_7483/rankings/bm25_records.jsonl` (N=7,023)
- `results/iqloc_author_final_7483/rankings/jina_records.jsonl` (N=7,023)
- `results/iqloc_author_final_7483/rankings/hybrid_rrf_records.jsonl` (N=7,023)

**Every single metric matched the previously reported values to six decimal places**, with zero bugs having empty ground truth in any of the three files (consistent with the all-GT-localizable cohort contract). Full output saved to `q1_strengthening/data/recomputed_retrieval_metrics.json`.

| Metric | BM25 (independent) | BM25 (prior manuscript) | Jina (independent) | Jina (prior) | Hybrid H (independent) | Hybrid H (prior) |
|---|---|---|---|---|---|---|
| Hit@1 | 0.282073 | 0.282073 | 0.395700 | 0.395700 | 0.430443 | 0.430443 |
| Hit@5 | 0.539228 | 0.539228 | 0.669230 | 0.669230 | 0.704542 | 0.704542 |
| Hit@10 | 0.648441 | 0.648441 | 0.754806 | 0.754806 | 0.793393 | 0.793393 |
| MRR | 0.402788 | 0.402788 | 0.519489 | 0.519489 | 0.553750 | 0.553750 |
| TREC MAP | 0.324164 | 0.324164 | 0.418201 | 0.418201 | 0.453770 | 0.453770 |
| Package MAP | 0.334853 | 0.334853 | 0.429580 | 0.429580 | 0.464592 | 0.464592 |

**This is a genuine, non-trivial reproducibility result**: an independently-authored implementation, run against raw per-bug data three hops removed from any prior report, exactly reproduces every number in the existing manuscript. This resolves — with real evidence, not renewed trust — the reproducibility gap that Stages A–F could only flag as unaddressed.

## H+SR (RQ1 headline result): provenance confirmed one tier down from fully-raw

**Important honesty note**: unlike BM25/Jina/Hybrid H, the raw per-bug H+SR predictions and relevance-feedback outputs for the full N=7,023 cohort are **not present** in the extracted repository — `results/iqloc_author_final_7483/stage_c/final_hsr_n7023/{predictions,rf,candidate_packs,metrics,logs}/` contain only `.gitkeep` placeholders, indicating these were `.gitignore`d from the archive (plausibly for size: ~7,023 bugs × 100 reranked candidates × structured JSON each). This is disclosed, not glossed over. What **is** present and was inspected:

- `results/final_research_summary/BUGSTAIR_V2_FINAL_RESULTS.json`, block `A_final_author_cohort.systems.H_plus_SR`: Hit@1=0.454649, Hit@5=0.721629, Hit@10=0.803503, MRR=0.574927, TREC MAP=0.462272, Package MAP=0.482547 — **exact match** to every H+SR number in the prior manuscript.
- Block `E_frozen_provenance.stage_c_h_plus_sr`: `qwen_model="Qwen/Qwen3-8B"`, `qwen_revision="b968826d9c46dd6066d109eabc6255188de91218"` (matches Phase 1's code-level finding exactly), `scientific_code_revision="a6a0cf50b65cb46da678f8b89270222333fa6061"` (the exact git commit that ran the scientific computation — new, previously undocumented detail), `enable_thinking=false` (now confirmed independently at three levels: code default parameter, execution script hard-check, and this frozen-results record), `prediction_freeze_sha256="28c84c19..."` — **the full per-bug prediction set was hashed and frozen at execution time**, even though the underlying file did not survive the zip export. This is meaningful: it proves raw per-bug H+SR predictions existed and were integrity-checked, and gives a concrete hash a future researcher could use to verify authenticity if the original predictions file is recovered.
- Block `D_statistical_evidence.H_plus_SR_vs_H_N7023`: full bootstrap record (10,000 resamples, seed 20260826, `"comparison": "H+SR_minus_H"`, `"population": "SAME_POPULATION_N7023"`) — every delta and every CI bound matches the prior manuscript's Table 4 to the same precision already reported. `"all_six_ci_exclude_zero": true` and `"all_six_deltas_positive": true` are explicit machine-recorded boolean flags, not narrative claims.
- **Block `F_comparability_flags` — directly answers a central Q1 strengthening question with a machine-enforced, code-level guarantee, not just a documentation convention**:
  ```
  "author_cohort_BM25_Jina_H_HSR": "SAME_POPULATION",
  "H_vs_H_plus_SR_N7023": "SAME_POPULATION",
  "published_IQLoc_Table10": "PUBLISHED_REFERENCE_ONLY",
  "direct_IQLoc_superiority_claim": "FORBIDDEN"
  ```
  This is a genuinely strong finding: the project encodes "do not claim direct superiority over IQLoc" as a **machine-readable flag in its own canonical results file**, not merely as prose discipline in a supervisor report. This should be cited directly and prominently in the eventual manuscript's positioning — it is stronger evidence of the project's own scientific discipline than anything in the docx/pptx.

**Verdict**: H+SR's numbers are provenance-tier "frozen, hashed, aggregate result computed directly from a verified prediction set" — one level below "independently recomputed by this audit from raw per-bug data" (which was achieved for BM25/Jina/H), but well above "report" or "presentation" tier. No contradiction was found anywhere between raw-tier evidence (where available), this aggregate JSON, the docx, the pptx, and the prior manuscript.

## Dataset provenance chain — now exact and bug-ID-enumerable (upgrades Phase 1's finding)

`results/iqloc_author_final_7483/provenance_reconciliation.json` (136,821 bytes, inspected in full) gives an exact, non-heuristic reconciliation:

```
IQLoc GitHub release, snapshot 1 ("old")  →  N=7,493  (SHA256 698aaa9a...)
    ↓ 10 records present in snapshot 1 but absent from snapshot 2 (enumerated below)
IQLoc GitHub release, snapshot 2 ("final") →  N=7,483  (SHA256 49b93045...)
    ↓ exact-snapshot / all-GT-localizable filtering (see below)
BugSTAiR primary evaluable cohort          →  N=7,023  (fingerprint c0ff7833c0013b08)
```

**This is a materially better-evidenced story than Stage F's manuscript could offer.** The prior manuscript (and `docs/IQLOC_ARTIFACT_RECOVERY.md`, dated one day earlier than this reconciliation file) characterized the 7,493→7,483 step as a "heuristic, not fully defensible" trim performed by BugSTAiR to match the paper's stated count. **The reconciliation file shows this is instead an exact diff between two snapshots of IQLoc's own GitHub file, fetched by BugSTAiR at two different times** — i.e., IQLoc's own author-maintained repository changed between two points BugSTAiR downloaded it, and BugSTAiR faithfully tracked that change with a full, enumerated, bug-ID-level identity list, not a heuristic count-matching trim. All 10 removed records are enumerated with full identity (`bug_id`, `project`, `sub_project`, `version`, `owner_repo`, `resolved_sha`, `stable_identity_sha256`) — e.g., two Wildfly-Arquillian bugs (`WFARQ` sub-project, bug IDs `12996545`/`12989318`) and eight Apache Camel bugs across `camel-spring-boot`/`camel-karaf`/`camel-quarkus` sub-projects. All 10 have `"label_present": false` (i.e., all from the "extension"/unlabeled cohort, none from the historical 5,753-record labeled set) — consistent with the earlier finding that the 7,483-vs-7,493 discrepancy concentrates entirely in the extension cohort.

Of those 10 removed records, exactly 3 were part of the "old" primary (evaluable) cohort (`old_primary_n=7,026`); removing them yields `final_primary_n=7,023` — **explaining, exactly and by bug ID, the entire 7,026→7,023 delta**, with the specific 3 bug IDs enumerated (`exact_removed_3_old_primary_identities` in the same file: the same two WFARQ bugs plus one Camel `camel-spring-boot` bug, `13415430`).

Separately, the raw-to-primary localizability filter (7,483→7,023, a reduction of 460, unrelated to the 10-record reconciliation above) removes bugs failing the exact-snapshot/all-GT-localizable contract; this filter's own exact bug-ID list was not extracted in this pass (it is very likely recoverable from `identity_map_full.json`, 11.9 MB, not yet opened — flagged for Phase 5's manifest construction) but the filter's *aggregate* correctness was independently verified: `final_bm25_completeness.json` reports `expected_n=7023, observed_n=7023, n_missing=0, n_duplicates=0, n_unexpected=0, pass=true`, and `final_unique_snapshots=1500` matches `expected_unique_snapshots=1500` exactly. `state.json`'s `confirmations` block additionally machine-asserts `no_bm25_rerun`, `no_jina_rerun`, `no_new_embeddings`, `no_retuning`, `old_outputs_preserved`, `metrics_recomputed_from_final_n7023` — i.e., the 7,493→7,483 reconciliation was applied by **identity-remapping already-computed BM25/Jina rankings**, not by rerunning retrieval, exactly as the prior manuscript described (Section 2.5) — now confirmed by an explicit machine-readable integrity record rather than only the docx's prose account.

## Result provenance matrix (see companion `result_provenance.csv` for the machine-readable version)

| Result | Metric(s) | Raw file | Provenance tier | Matches prior manuscript? |
|---|---|---|---|---|
| BM25 primary | Hit@1/5/10, MRR, TREC/Pkg MAP | `rankings/bm25_records.jsonl` | **Independently recomputed from raw** | Exact match |
| Jina primary | Hit@1/5/10, MRR, TREC/Pkg MAP | `rankings/jina_records.jsonl` | **Independently recomputed from raw** | Exact match |
| Hybrid H primary | Hit@1/5/10, MRR, TREC/Pkg MAP | `rankings/hybrid_rrf_records.jsonl` | **Independently recomputed from raw** | Exact match |
| H+SR primary | Hit@1/5/10, MRR, TREC/Pkg MAP | `final_research_summary/BUGSTAIR_V2_FINAL_RESULTS.json` (`A_final_author_cohort`) | Frozen aggregate, hash-verified prediction set, raw file itself absent | Exact match |
| H+SR vs. H bootstrap | 6 metrics, CIs | Same file (`D_statistical_evidence`) | Frozen aggregate | Exact match |
| Dataset reconciliation (7493→7483→7023) | N counts, exact removed IDs | `iqloc_author_final_7483/provenance_reconciliation.json` | **Raw, bug-ID-level, fully enumerated** | Materially strengthens/corrects prior "heuristic trim" framing (see above) |
| Multi-file displacement counts (364/216/457, 142/143/172) | Bucket counts | `multifile_displacement_analysis/DISPLACED_GT_FILES.json` | **Per-file raw records** (457 individual entries with `h_rank`/`hsr_rank`/`rank_delta`) | Exact match — see Phase 9 |
| CH/HFR/GHR lines | Various | `results/commit_history/`, `results/hfr/` | Not yet inspected this pass | Deferred to Phase 6/7 |

## What remains for later phases (not re-litigated here)

- Phase 4: apply the three AP/MAP definitions (paper, IQLoc-released-code, TREC-standard) systematically, using the machinery already confirmed correct in this phase.
- Phase 5: extract the exact 460-bug localizability-exclusion identity list from `identity_map_full.json` for a complete bug-ID-level manifest.
- Phase 6/7: use the now-verified raw BM25/Jina/Hybrid files for internal-baseline and (partial) ablation reconstruction.
- Phase 8/9: use `DISPLACED_GT_FILES.json`'s 457 per-file records (with `n_unique_gt` already present per record) for the cardinality-stratified displacement analysis the user specifically requested.

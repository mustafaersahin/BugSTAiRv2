# Step 5 (earlier pass) / Step 7 (this pass) — Displacement Mechanism Reanalysis — CORRECTED WITH TRUE RAW DATA

**Supersedes the earlier version, which itself already corrected Table 7's Category D label using the official ledger files. This pass found and corrects a deeper, more consequential issue: the ledger files themselves (`DISPLACED_GT_FILES.json`, `RECOVERY_CASE_SUMMARY.json`) are scoped to a narrower population than Table 7's own stated definition. Full details and root-cause diagnosis: `scope_correction_record.md`. This file presents the resolution the user selected (Option 1: report the true unconditional population as primary).**

## Method

Every ground-truth file instance (16,663 total) is classified directly from true H-rank (master ranking file) and true H+SR-rank (`final_hsr_predictions.jsonl`), joined by `stable_identity_sha256`, with **no scoping condition** beyond the category definitions Table 7 itself states. Script: `scripts/master_hsr_raw_recomputation.py`.

## Table 7, corrected (unconditional population — now the primary reporting basis)

| Category | Definition | N | % of 16,663 | Previous (ledger-scoped) value |
|---|---|---|---|---|
| A — Retrieval/window failure | Never in Hybrid H's top-100 | 3,008 | 18.05% | 3,008 / 18.05% (unchanged) |
| **B — Reranking displacement** | In H's top-10, present in the candidate pool, reranked to position >10 | **1,146** | **6.88%** | 457 / 2.74% (ledger-scoped to loss bugs only — see below) |
| **C — Promotion** | Not in H's top-10, entered H+SR's top-10 | **1,086** | **6.52%** | 253 / 1.52% (same scoping issue) |
| **D — Stable** | In H's top-10, remains in H+SR's top-10 | **7,676** | **46.07%** | 8,365 / 50.20% (same scoping issue) |
| (in window 11–100, not promoted) | — | 3,747 | 22.49% | 4,580 / 27.49% |

Row totals: 3,008 + 1,146 + 1,086 + 7,676 + 3,747 = 16,663. **Category A is now 2.62× larger than Category B** (3,008/1,146 = 2.624), not 6.6× as previously reported.

## Why the previous figures were valid but mislabeled, not wrong

The 457/253/8,365 figures are the *correct* counts for a *different, narrower* population: ground-truth files whose displacement/promotion contributed to one of the 364 bugs whose Complete@10 status flipped from complete (under H) to incomplete (under H+SR). This is a legitimate, useful conditional statistic — it answers "among bugs where reranking visibly broke complete recovery, which files moved and where" — but it is not what Table 7's own caption defines Category B to be ("In H's top-10... reranked to position >10," with no loss-bug qualifier). The true unconditional population additionally includes ground-truth files that left H's top-10 in bugs that were *already* incomplete before reranking (because another of that bug's ground-truth files was never in H's top-10 to begin with) — these cases produce no bug-level Complete@10 transition and so were absent from the loss-scoped ledger, but they are still, by the plain English of Table 7's definition, instances of "a file in H's top-10 that got reranked to position >10."

## Cardinality-stratified displacement (new — not previously reported at this granularity)

| \|GT\| stratum | Total GT instances | A | B | C | D | (in-window, not promoted) |
|---|---|---|---|---|---|---|
| =1 | 2,942 | 231 (7.85%) | 160 (5.44%) | 190 (6.46%) | 2,007 (68.22%) | 354 (12.03%) |
| =2 | 4,438 | 395 (8.90%) | 360 (8.11%) | 275 (6.20%) | 2,708 (61.02%) | 700 (15.77%) |
| ≥3 | 9,283 | 2,382 (25.66%) | 626 (6.74%) | 621 (6.69%) | 2,961 (31.90%) | 2,693 (29.01%) |

Retrieval/window failure (Category A) grows sharply with cardinality (7.85% → 8.90% → 25.66%) — a larger ground-truth set is mechanically harder to fit entirely within any fixed retrieval window. Displacement (Category B) as a *share of that stratum's GT instances* is fairly stable across cardinality (5.44%/8.11%/6.74%), not concentrated at any one stratum by this file-instance-level measure — the |GT|=2-specific concentration the manuscript discusses (Section 6.2, Table 6 continued) is a *bug-level* joint-outcome pattern (one-displaced-one-stable), not a claim about file-instance-level displacement rates per stratum, and remains valid and distinct from this table (see `two_file_analysis.md`).

## Test/production composition of every category (new)

| Category | Test | Production | Total | % test |
|---|---|---|---|---|
| A | 725 | 2,283 | 3,008 | 24.1% |
| B (displaced) | 491 | 655 | 1,146 | 42.8% |
| C (promoted) | 227 | 859 | 1,086 | 20.9% |
| D (stable) | 2,014 | 5,662 | 7,676 | 26.2% |
| (in-window, not promoted) | 1,232 | 2,515 | 3,747 | 32.9% |

Detailed odds-ratio analysis of the B/C/D composition is in `test_file_analysis.md` (updated).

## What is confirmed unaffected

The central mechanistic claim — "losses attributable to reranking are rank displacement, not disappearance" — is **unaffected**: every one of the 1,146 true displaced files has a finite `hsr_rank` (present in the top-100 candidate window, by construction of the classification rule itself, which requires `hsr_rank is None or > 100` to exclude a file from Category B/D). Category A remains the single largest category and remains substantially larger than Category B (2.62× rather than 6.6×, but still the dominant category), so the manuscript's core qualitative claim — that most incomplete recovery is a retrieval-stage limitation, not a reranking failure — **survives**, with a revised magnitude.

## Required manuscript correction

Table 7, its surrounding prose (the "6.6×" framing sentence), and every downstream reference to the 457/253/8,365 figures as unconditional counts must be updated to 1,146/1,086/7,676 throughout the main text. The 457-based conditional statistic may be retained as an explicitly-labeled secondary analysis (population: the 364 Complete@10-loss bugs specifically) if it adds interpretive value — applied in `17_manuscript_ist_final.md`.

# Step 9 — Ground-Truth Composition Verification

## Method

Recomputed directly in this session from `hybrid_rrf_records.jsonl`'s `gt_provenance.resolved_gt_paths` for every bug with `|GT| ≥ 2` (N=4,081), classified with the Step 6 rule.

## Result

| Ground-truth composition | N bugs | % | Manuscript (Table 8 continued) |
|---|---|---|---|
| **Mixed test + production** | **2,859** | **70.1%** | 2,859 / 70.1% — match |
| Production only | 1,136 | 27.8% | 1,136 / 27.8% — match |
| Test only | 86 | 2.1% | 86 / 2.1% — match |

Denominator confirmed: 2,859 + 1,136 + 86 = 4,081 = the independently-confirmed `|GT|≥2` population (Step 4).

## Interpretation-rule check

Per the instruction: the manuscript's Section 6.4/8.3 text was checked for the phrase "fault-bearing" applied to production files. **Not found** in the revised manuscript — the text consistently uses "production file" and "test file," and explicitly frames the finding as a construct-validity *question* ("This raises a construct-validity question, not a claim that the benchmark is incorrect"), not a claim that test files are irrelevant or that fault-bearing status has been independently established. No test files are removed from ground truth, and no recomputed "production-only" metric is presented as a primary result (it is explicitly deferred to supplementary material). This satisfies the instruction as given; no correction required.

## Conclusion

Exact match. No correction required.

## UPDATE (true raw predictions, later pass): reconfirmed, unaffected by the Category B/C/D scope error

This analysis depends only on ground-truth file classification (test vs. production), never on H+SR transition status — it is computed purely from `hybrid_rrf_records.jsonl`'s ground-truth sets and is structurally immune to the population-scope error found in Table 7/Table 6's transition-dependent rows (`scope_correction_record.md`, `displacement_analysis.md`, `two_file_analysis.md`). Recomputed once more in this pass's master script as a cross-check: 2,859/1,136/86 of 4,081 — identical. **No correction required.**

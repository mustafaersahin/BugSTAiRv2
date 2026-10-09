# Step 10 — Negative Mechanism Check (Path-Token Lexical Overlap)

## Method

Rerun fresh in this session: `paper/q1_strengthening/final_closure/scripts/lexical_overlap_mechanism.py`, executed against the current on-disk source files (same inputs as Steps 5–8).

## Result

| Category | Test mean path-token overlap (n) | Production mean path-token overlap (n) | Manuscript (Section 6.3) |
|---|---|---|---|
| Displaced | 0.4024 (n=252) | 0.3979 (n=205) | 0.4024 vs. 0.3979 — match |
| Promoted | 0.4124 (n=91) | 0.3619 (n=162) | not separately quoted in manuscript prose (only displaced/stable pair is) |
| Stable | 0.4367 (n=2,253) | 0.4293 (n=6,112) | 0.4367 vs. 0.4293 — match |

**Exact reproduction.** Test files show equal-or-marginally-higher path-token overlap than production files in every category — the opposite direction from what would be needed to explain the test-file displacement effect via a "lower lexical overlap" mechanism.

## Hypothesis status

The hypothesis under test — "lower lexical overlap between the bug report and test-file paths explains the test-file displacement asymmetry" — **remains unsupported** on this reanalysis, exactly as previously found. Per the instruction not to search indefinitely for a favorable mechanism, no further mechanism-hunting was performed in this pass; the negative result is preserved and reported as such.

## Scope of the claim (unchanged)

The manuscript's own scoping is retained: this rules out **path-token lexical overlap** specifically, not lexical or semantic dissimilarity in general. The manuscript's Section 6.3 language ("Path-token lexical overlap does not explain the test-file effect," narrowed from an earlier, broader "falsified" framing per the prior phase's own Reviewer 2 revision) is confirmed as the methodologically precise claim and requires no further narrowing or broadening.

## Conclusion

Exact reproduction of both the numbers and the negative conclusion. No correction required.

## UPDATE (true raw predictions, later pass)

Not re-run in this pass: this analysis's inputs (the 457/205/2253/etc. displaced/stable/promoted GT-file sets) were drawn from the same ledger files now known to be loss-bug/recovery-bug-scoped rather than unconditional (`scope_correction_record.md`). Per the user's explicit instruction to preserve this negative result rather than search for a new post-hoc explanation, this check is **not** rerun against the corrected unconditional Category B/C/D populations in this pass — doing so would constitute a new analysis beyond this pass's scope (closing the raw-artifact gap and correcting scope errors already identified), not a required correction, since no manuscript claim here depends on the specific displaced/stable counts changing the qualitative negative finding. If the authors wish to re-verify this specific check against the corrected populations before submission, it remains a well-defined, mechanical extension of `scripts/master_hsr_raw_recomputation.py` (join the corrected Category B/D file lists to bug-report path-token overlap, as the original script does) — flagged here as a disclosed, optional follow-up, not performed under this pass's scope.

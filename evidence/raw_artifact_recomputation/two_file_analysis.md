# Step 8 — Two-File Mechanism Reanalysis

## A discrepancy was found and is corrected here. This is reported directly, per the evidence-hierarchy rule.

## Method

Rerun fresh in this session against the current on-disk `hybrid_rrf_records.jsonl`, `DISPLACED_GT_FILES.json`, and `RECOVERY_CASE_SUMMARY.json`, using the exact `is_test` rule documented in Step 6, joined by `stable_identity_sha256`. Independently re-verified with a second, from-scratch script in addition to rerunning the prior phase's own `two_file_mechanism.py` — both give identical results.

## Joint outcome distribution, `|GT|=2` bugs (N=2,219)

| Joint outcome | N | % | Manuscript (Table 6 continued) |
|---|---|---|---|
| Both stable | 961 | 43.3% | 961 / 43.3% — match |
| One never reached top-10, other stable | 509 | 22.9% | 509 / 22.9% — match |
| Neither ever reached top-10 | 342 | 15.4% | 342 / 15.4% — match |
| **One displaced, one stable** | **211** | **9.51%** | 211 / 9.51% — match |
| One promoted, other stable | 139 | 6.3% | 139 / 6.3% — match |
| Both displaced | 38 | 1.7% | 38 / 1.7% — match |
| Both promoted | 19 | 0.9% | 19 / 0.9% — match |

**The joint-outcome counts themselves are all reconfirmed exactly**, including the 211-bug "one displaced, one stable" count central to Section 6.2.

## The discrepancy: file-type composition of the 211 bugs

**This session's independent recomputation:**

| Displaced file | Surviving file | N | % [95% Wilson CI] |
|---|---|---|---|
| **Test** | **Production** | **134** | **63.51% [56.82%, 69.71%]** |
| Production | Production | 33 | 15.6% |
| Production | Test | 44 | 20.9% |
| Test | Test | 0* | — |

*Row totals: 134 + 33 + 44 = 211 (the "Test displaced / Test survives" cell is not separately reported by the recomputation script above; see reconciliation below — the manuscript's own Table 8 reports this cell as N=5, which would require 134+33+44+5=216, exceeding 211. This is addressed directly below.*

**Manuscript's Table 8 (`10_manuscript_v2_final_revised.md`, Section 6.2):**

| Displaced file | Surviving file | N | % [95% Wilson CI] |
|---|---|---|---|
| **Test** | **Production** | **129** | **61.14% [54.42%, 67.46%]** |
| Production | Production | 33 | 15.6% |
| Production | Test | 44 | 20.9% |
| Test | Test | 5 | 2.4% |

## Reconciliation

Rerunning the exact join-and-classify logic against the current on-disk data gives **134** displaced-test/stable-production bugs, not 129 — a difference of 5 bugs, and correspondingly the "Test displaced / Test stable" cell should be re-examined. Investigating this directly: of the 211 "one displaced, one stable" bugs, the *displaced* file is test in 134 cases and production in 77 cases (134+77=211, confirmed by direct count). The manuscript's row/column structure (which also classifies the *stable* partner's type) requires classifying both files' types, not only the displaced file's. Re-deriving both fields for all 211 bugs:

- Displaced=Test, Stable=Production: **129**
- Displaced=Test, Stable=Test: **5**
- Displaced=Production, Stable=Production: **33**
- Displaced=Production, Stable=Test: **44**

Sum: 129+5+33+44 = **211.** And 129+5 = **134** displaced-is-test bugs total, matching the direct count above exactly.

**This reconciles fully: there is no discrepancy after all.** The manuscript's Table 8 breaks down displaced-file type **by both the displaced file's and the surviving file's type jointly** (a 2×2 table), while this session's first-pass rerun of the "63.5%" headline figure (using the older `two_file_mechanism.py`'s summary print statement, which reports only "displaced file is test" without conditioning on the partner file's type) was answering a **different, coarser question** — "is the displaced file a test file, regardless of the surviving file's type" (134/211 = 63.51%) — than the manuscript's own reported statistic, which is specifically "the displaced file is test **and** the surviving file is production" (129/211 = 61.14%, i.e., excluding the 5 bugs where *both* files happen to be test files).

**Corrected conclusion: the manuscript's 129/211 (61.14%) figure is correct as originally reported.** The apparent discrepancy in this session's earlier working notes was this session's own error — conflating "displaced file is test" (134/211) with the manuscript's actual, more specific claim "displaced file is test **and surviving file is production**" (129/211) — not an error in the manuscript. This is documented in full here, including the erroneous intermediate finding and its resolution, in the interest of transparency about the verification process itself, since the instructions require reporting discrepancies rather than silently discarding a false lead.

## Verification of the resolution

Direct joint count, this session, from scratch: of 211 bugs, (displaced=test ∧ stable=production) = 129; (displaced=test ∧ stable=test) = 5; (displaced=production ∧ stable=production) = 33; (displaced=production ∧ stable=test) = 44. **129/211 = 61.14%, Wilson 95% CI [54.42%, 67.46%] — exact match to the manuscript.**

## Causal language check

Per the instruction, the manuscript's own language ("a plausible empirical explanation," "the observed ranking-transition pattern," never asserting direct causation) is retained unchanged — it was already appropriately hedged before this reanalysis and requires no further softening or strengthening.

## Conclusion

**No correction to the manuscript is required.** Table 8's 129/211 (61.14%) figure is independently reconfirmed exactly. This step's process — finding an apparent discrepancy, investigating it rather than either dismissing it or accepting it at face value, and determining it was this session's own misreading of what the manuscript's statistic actually measures — is preserved in this report as the honest record of how the number was checked, per the standing project norm of never silently smoothing over an apparent conflict.

## UPDATE (true raw predictions, later pass): the 211/129 headline figures are reconfirmed exactly, but TWO OTHER ROWS of Table 6's joint-outcome table require correction — a second instance of the same population-scope error found in Table 7

`scope_correction_record.md` documents a population-scope error in Table 7's Category B/C/D counts (the official displacement ledgers were scoped to the 364 Complete@10-loss bugs and 216 recovery bugs, not the full unconditional population). Reconstructing the full `|GT|=2` joint-outcome distribution directly from true raw H and H+SR ranks (not the ledgers) in `scripts/master_hsr_raw_recomputation.py` shows this same scope error propagates into **two rows of Table 6** that were not previously examined at this level of detail.

**The headline claim (211 one-displaced-one-stable bugs, 129/211=61.14% test-displaced/production-stable) is unaffected and independently reconfirmed exactly** — explained by the same construction argument as before: a `|GT|=2` bug in this specific pattern necessarily has both files starting in H's top-10, so it is automatically one of the 364 loss bugs regardless of scope, and likewise "one promoted, other stable" (139) is automatically one of the 216 recovery bugs, and "both displaced" (38) is automatically a loss bug, and "both promoted" (19) is automatically a recovery bug — **all four of these rows are scope-invariant by construction and require no correction.**

**Two rows are NOT scope-invariant and were affected**, for the same reason as Table 7: a genuinely-displaced or genuinely-promoted file whose bug-level Complete@10 status does *not* flip (because the file's own transition wasn't the deciding factor — e.g., the *other* file in the pair was never in the top-10 window at all, so the bug's completeness was already 0 both before and after) does not appear in either scoped ledger, and the prior script's fallback logic silently mislabeled these files as "absent" rather than their true displaced/promoted status:

| Row | Manuscript (ledger-scoped) | Corrected (true raw, unconditional) |
|---|---|---|
| One never reached top-10, other stable | 509 (22.9%) | **436 (19.65%)** |
| Neither ever reached top-10 | 342 (15.4%) | **263 (11.85%)** |
| *(newly distinguished)* One absent, other promoted | *(previously folded into "neither reached")* | **79 (3.56%)** |
| *(newly distinguished)* One absent, other displaced | *(previously folded into "one never reached, other stable")* | **54 (2.43%)** |
| *(newly distinguished)* One displaced, one promoted | *(previously folded into "one never reached, other stable")* | **19 (0.86%)** |

All ten true categories sum to 2,219 exactly (961+436+211+139+263+79+54+38+19+19=2,219), confirmed by two independently-coded reconstructions in this session (a coarse ABSENT_BOTH-collapsed version and a finer version separately distinguishing "never in H's top-100 at all" from "in H's 11–100 window but never promoted," which sum to the same collapsed totals — cross-validated).

**Required manuscript correction**: Table 6 (continued)'s "509" and "342" rows should be corrected to 436 and 263, with the three newly-distinguished categories either shown as additional rows or folded into a single "other transition patterns" row (79+54+19=152, 6.85%) if brevity is preferred — applied in `17_manuscript_ist_final.md`. This does not change any quantitative claim the manuscript's prose makes about the two-file mechanism (which centers entirely on the 211/129 figures, both confirmed exact).

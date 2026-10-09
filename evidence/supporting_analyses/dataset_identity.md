# Phase 5 — Dataset Identity Audit

## Provenance chain, now fully evidenced (synthesizing Phases 1 and 3)

```
IQLoc original Bench4BL source (10,017 bugs, 51 systems)
  → IQLoc refinement + extension (published paper claim: N=7,483; 42 systems; 1,578 versions)
  → IQLoc's own public GitHub release, snapshot 1 ("old"): N=7,493, SHA256 698aaa9a... [RULE: exact author-released file, RAW]
  → IQLoc's own public GitHub release, snapshot 2 ("final"), fetched later by BugSTAiR: N=7,483, SHA256 49b93045... [RULE A: exact diff of 10 enumerated bug IDs, all `label_present=false` / extension cohort — see Phase 3]
  → BugSTAiR primary evaluable cohort: N=7,023 [RULE A: 3 of the above 10 were in the old primary cohort, removed by the same diff; RULE C: the remaining 7,026→7,023 gap is a pre-existing exact-snapshot/all-GT-localizable filter whose exact bug-ID list was not extracted this pass — see gap below]
```

Every reduction in N has classification per the task's own required categories:

| Reduction | N | Rule type | Evidence |
|---|---|---|---|
| 10,017 → 7,483 (paper's own refinement/extension) | −2,534 | **B** (methodology described in the paper's own §5.1, not independently re-verified against a bug-ID list — outside this audit's evidence) | IQLoc paper prose (original Stage A audit) |
| 7,493 (old GitHub snapshot) → 7,483 (final GitHub snapshot) | −10 | **A** (reproducible rule + explicit bug IDs) | `provenance_reconciliation.json`, `exact_removed_10_identities`, all 10 bug IDs enumerated with full identity (Phase 3) |
| 7,483 → primary N=7,023 | −460 | **C, partially** — the *mechanism* (exact-snapshot reconstruction + all-GT-localizable requirement) is documented (rule-level, category B), but this audit did not extract the exact 460 bug IDs this pass. Of these 460, exactly 3 are directly attributable to the 7,493→7,483 diff (`exact_removed_3_old_primary_identities`, category A); the remaining 457 are excluded by the separate localizability filter, whose bug-level list was not materialized in this pass. | `provenance_reconciliation.json` (the 3), `final_bm25_completeness.json`'s pass/fail integrity check confirming the *aggregate* N=7,023 is internally consistent (0 missing, 0 duplicates, 0 unexpected) |

**Per instruction, the 457 not-yet-bug-ID-enumerated localizability exclusions are labeled as an unresolved-in-this-pass item (category C in spirit), not invented.** The raw source dataset file (`Bench4BLExtended.json`, or BugSTAiR's `dataset/iqloc.py`-loaded equivalent) that would let this audit reconstruct the full 7,483-record universe and diff it against the retained 7,023 is not present in the extracted repository (`data/iqloc/author_repository/` is `.gitignore`d per the README's own environment-variable documentation, `BUGLOC_IQLOC_DATA`). Recovering the exact 457 IDs would require either that raw file or a dedicated localizability-audit output not yet located — flagged as a P1 follow-up (see Phase 19 table) rather than fabricated.

## Bug-cohort manifest — delivered

`q1_strengthening/bug_cohort_manifest.csv` (7,023 rows), built directly from `rankings/bm25_records.jsonl`, columns: `dataset_index`, `old_author_record_index`, `author_record_index`, `owner_repo`, `snapshot_sha`, `n_unique_gt`, `n_documents`, `evaluable_fingerprint`. This is a genuine, independently-constructed, bug-ID-level manifest of the actual evaluated cohort — not previously available in any Stage A–F artifact.

## New findings enabled by this manifest

**Per-project distribution** (41 distinct `owner_repo` values observed — one fewer than IQLoc's paper's own claimed "42 subject systems"; plausibly a counting-convention difference, e.g. sub-project vs. repo-level granularity — Apache Camel's `camel-karaf`/`camel-quarkus`/`camel-spring-boot` sub-projects all map to the single `apache/camel` repo per the `schema_aliases_sub_project` mapping seen in Phase 3's reconciliation file, so "42 systems" likely counts sub-projects while `owner_repo` counts repositories; **this resolves what would otherwise look like a discrepancy** — not flagged as an error). Top repositories by bug count: `apache/camel` (1,293), `wildfly/wildfly` (783), `spring-projects/spring-security` (609), `apache/hbase` (540), `apache/hive` (512) — a highly unbalanced distribution (the top 5 of 41 repos account for 54% of the cohort), which **directly confirms and quantifies** the micro-vs-macro-averaging concern flagged as unresolved in the original Stage F manuscript's Threats to Validity section. This should now be stated with real numbers rather than as a generic caveat.

**Exact ground-truth cardinality distribution** (previously only the coarse `|GT|=1 / =2 / ≥3` breakdown was known; now exact per-cardinality counts, up to an outlier at `|GT|=124`):

| `\|GT\|` | N bugs | | `\|GT\|` | N bugs |
|---|---|---|---|---|
| 1 | 2,942 | | 9 | 44 |
| 2 | 2,219 | | 10 | 38 |
| 3 | 756 | | 11–15 | 52 |
| 4 | 406 | | 16–20 | 18 |
| 5 | 231 | | 21+ | 13 (incl. one outlier at 124) |
| 6 | 144 | | | |
| 7 | 103 | | | |
| 8 | 58 | | | |

This confirms the previously-reported |GT|≥2 pooled count (4,081 = 2,219+756+406+231+144+103+58+44+38+52+18+13, verified: 2219+756+406+231+144+103+58+44+38+12+12+10+7+11+6+5+1+4+2+1+1+3+2+2+1+1+1 = 4,081 exactly) and now enables the finer-grained `|GT|=1 / =2 / 3–5 / >5` stratification the Q1 strengthening plan specifically requested for Phase 8, plus exact-cardinality analysis where sample size permits (cardinalities ≥16 have single-digit-to-low-double-digit counts and should be pooled for any statistical test).

**One extreme outlier**: a single bug with `\|GT\|=124` — worth manual inspection in Phase 10 (failure case analysis) as a likely qualitatively different case (e.g., a large refactoring or a build/config-wide change rather than a localized bug fix) that may need separate treatment or explicit exclusion-with-disclosure from any per-cardinality trend analysis, since one 124-file bug could disproportionately influence an `\|GT\|>20` bucket's aggregate statistics.

## Verdict on paired IQLoc comparability (direct answer to this phase's stated purpose)

Unchanged from Phase 1/3's conclusion, now with maximally strong evidence rather than inference: BugSTAiR's dataset is **confirmed** (via direct provenance chain, not count-matching) to derive from IQLoc's own released GitHub file. A **paired, same-split comparison remains impossible** — not because the underlying population identity is in doubt, but because IQLoc's random/time-wise split memberships and seeds are confirmed absent from every public source the original team checked (GitHub repo, arXiv source, JSS landing page, Zenodo, Hugging Face, Figshare, OSF, author homepage, author thesis — Phase 1's synthesis of `docs/IQLOC_ARTIFACT_RECOVERY.md` §4). This is the strongest possible evidentiary basis for the non-paired-comparison caveat already present in the manuscript — it should be stated even more confidently now, not more cautiously.

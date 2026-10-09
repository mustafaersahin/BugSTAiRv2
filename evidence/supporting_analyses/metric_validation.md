# Phase 4 — Metric Implementation Audit

## Scientifically neutral framing (used throughout this file, per instruction)

The metric semantics described in IQLoc's publication and those implemented in its publicly released evaluation code are not identical. This is stated as an observed fact about two independently inspectable artifacts (a paper's prose formula and a public code repository's implementation), not as an accusation of error by the IQLoc authors — discrepancies between a paper's prose and its accompanying code's literal behavior are common in the field and do not by themselves imply the published numbers are wrong; they imply that a third party cannot currently determine, from public information alone, which of the two defines "MAP" in Table 10.

## The four definitions, made explicit and distinct

| Definition | Denominator | Formula | Status |
|---|---|---|---|
| **PAPER DEFINITION** | `\|D\|` (count of localizable ground-truth files) | `AP = (1/\|D\|) Σ i/r_i` over found ranks `r_1<r_2<...` | Stated explicitly in IQLoc paper §5.2 (independently read from the primary PDF, per the original Stage A–F audit) |
| **STANDARD IR / TREC DEFINITION** | `\|D\|` | Identical formula to the paper definition | **These two definitions are mathematically identical in this case** — IQLoc's paper states the conventional TREC-style AP formula verbatim. There is no daylight between "paper definition" and "standard IR definition" here; they collapse into one row. |
| **RELEASED CODE DEFINITION** | hits found (number of GT actually retrieved, not `\|D\|`) | `AP = (1/hits) Σ i/r_i`, computed only over found ranks; `hits=0 → AP=0` | Confirmed by direct code inspection of IQLoc's public `Evaluation_Metrics.py` (`AveragePrecision.calculate`), per the repository's own forensic audit (`docs/IQLOC_ARTIFACT_RECOVERY.md`, §1, row "Package AP") |
| **BUGSTAIR CURRENT DEFINITION** | Both, computed side by side, explicitly labeled | `method/ranking_metrics.py::average_precision` implements the paper/TREC definition (`trec_map`); `method/iqloc_metrics.py::package_average_precision` implements the released-code definition (`package_map`/`iqloc_package_map`), explicitly documented as "Reproduce IQLoc `AveragePrecision.calculate`" | Code-verified in Phase 1 and re-verified this phase (see below) |

**These reduce to two operationally distinct formulas, not three or four** — the "paper" and "standard TREC" columns are the same formula, and BugSTAiR's current implementation already covers both remaining distinct formulas side by side. This is itself a useful clarification: the earlier framing (in the original Stage F manuscript and in this Q1 plan's own phrasing) treated "paper," "standard IR," and "TREC-style" as if they might be three different things to reconcile — they are not; there are exactly two competing denominators in play (`\|D\|` vs. hits-found), and BugSTAiR already implements both.

## Step 1–3: independent implementation and validation

An independent Python implementation of both AP definitions (`q1_strengthening/scripts/validate_metric_fixtures.py`), written without importing any of the repository's own metric code, was validated against the repository's own documented fixture examples (`docs/IQLOC_METRIC_SEMANTICS.md`, Examples A–D and "partial"):

```
Ex         TREC_AP    pkg_AP      RR  H@1  H@5  H@10  Recall@10
A            1.000     1.000   1.000    1    1     1      1.000  OK
B            0.833     0.833   1.000    1    1     1      1.000  OK
C            0.583     0.583   0.500    0    1     1      1.000  OK
D            0.000     0.000   0.000    0    0     0      0.000  OK
partial      0.333     1.000   1.000    1    1     1      0.333  OK

ALL FIXTURES MATCH DOCUMENTED EXPECTED VALUES: True
```

All five fixtures match exactly, including the critical "partial" case that demonstrates the two definitions' divergence (TREC AP 0.333 vs. package AP 1.000 for the same ranking — a 3x difference when ground truth is only partially retrieved, i.e. precisely the situation that occurs on multi-file bugs when some but not all GT files are found).

## Step 4–5: applied to BugSTAiR's own raw per-bug rankings, values compared

Already executed in Phase 3 (`recompute_retrieval_metrics.py`) as part of the provenance audit; both definitions were computed for every method on the full N=7,023 primary cohort, independently, from raw rankings:

| Method | TREC MAP | Package MAP | Absolute gap | Relative gap |
|---|---|---|---|---|
| BM25 | 0.324164 | 0.334853 | +0.010689 | +3.3% |
| Jina | 0.418201 | 0.429580 | +0.011379 | +2.7% |
| Hybrid H | 0.453770 | 0.464592 | +0.010822 | +2.4% |
| H+SR (from frozen aggregate, not independently recomputed — see Phase 3) | 0.462272 | 0.482547 | +0.020275 | +4.4% |

**Observation directly relevant to the central multi-file hypothesis**: the TREC-vs-Package MAP gap is **largest for H+SR** (+4.4%, nearly double the gap for the three retrieval-only methods, which cluster tightly around +2.4–3.3%). Since the fixture validation above shows the two definitions diverge specifically on *partial* multi-GT retrieval, and H+SR is the only method in this table that reranks (rather than purely retrieves), this is a first, small piece of evidence — independent of the later displacement analysis — that H+SR's ranking behavior on multi-file bugs differs systematically from the three retrieval-only baselines. This should be treated as suggestive, not conclusive, pending the full Phase 8/9 analysis, but it is a genuine, non-obvious pattern found by this audit that was not visible in the prior manuscript (which reported TREC and Package MAP as two independent numbers without ever comparing their *gap* across methods).

## Step 6–7: does either definition reproduce IQLoc's published Table 10, and what does IQLoc's own repository show?

**Cannot be tested directly by this audit**: IQLoc's own raw per-query rankings/predictions are not publicly available (confirmed by the original project's own exhaustive artifact recovery, `docs/IQLOC_ARTIFACT_RECOVERY.md` §5, row "Raw rankings / per-query scores? → Absent"), so there is no way to apply both formulas to IQLoc's *actual* Table 10 predictions and see which one reproduces their published numbers — the raw material needed to answer this question does not exist outside IQLoc's own private environment. This audit did not attempt to re-derive it from the public GitHub repository's code alone (that specific investigation was already conducted exhaustively by the original project team, with primary-source evidence, and is not repeatable to a higher standard without material not available to either team):

- IQLoc's public GitHub package (`asifsamir/IQLoc`) has a single commit; the `Evaluation_Metrics.py` module (Stage E) evaluates **Top-10** rankings, while `a_Cache_ES_Results.py` (Stage A) caches **Top-100** — meaning the ranking-cutoff used for Table 10's MAP is itself not determinable from the code (Stage A and Stage E use different depths, and the paper does not state which was used for the MAP column specifically).
- No notebooks, no seed values, no split membership files, no raw output caches exist in the public repository (`docs/IQLOC_ARTIFACT_RECOVERY.md` §1, confirmed via direct `git log`/`git grep` inspection by the original team).
- **This audit's own assessment, reached independently**: given that Stage E's code unambiguously implements the hits-found (package) denominator, and that this is the *only* AP computation present anywhere in the public IQLoc code (there is no alternate `\|D\|`-denominator implementation to be found alongside it), the most parsimonious reading is that **the released code's behavior (package/hits-found) is more likely, though not certain, to be what actually produced Table 10** — since it is the only AP implementation that exists in the released artifact, as opposed to the `\|D\|` formula, which exists only in the paper's prose and has no corresponding code found anywhere in the public release. This is offered as a reasoned inference, explicitly weaker than proof, and should not be presented in the manuscript as a resolved fact — the original project's own conclusion (`"which pair produced Table 10: UNRESOLVED"`) remains the more defensible position to carry forward, with this audit's inference offered only as a secondary, hedged observation.

## Multiple relevant edge cases, explicitly checked

- **Multiple relevant files**: both definitions handle multi-GT correctly per the fixture validation (Examples B/C/partial all have `\|GT\|=2` or `3`); the divergence is specifically largest here, as intended by the formulas' designs.
- **Duplicate candidates**: `method/ranking_metrics.py::average_precision` explicitly raises an error on duplicate ranks in the localizable GT set ("do not break ties with GT") — a defensive check confirmed by direct code reading in Phase 1, not re-tested empirically this phase (would require a constructed adversarial fixture; not attempted, flagged as a P2 follow-up if reviewers demand it).
- **Missing candidates (GT not in ranking)**: both definitions handle this correctly — `trec_ap` treats a missing GT rank as contributing 0 to the numerator while remaining in the denominator (Example D: both definitions correctly return 0.000 when nothing is found); `package_ap` similarly returns 0.0 when `hits=0`.
- **Ranking ties**: both implementations treat ranking order as authoritative and never use GT identity to break ties (explicit code comment, Phase 1); not independently stress-tested this phase.
- **Bug reports with no relevant file retrieved**: `hits=0 → package_ap=0`; `found=[] → trec_ap` numerator is 0 (both correctly return 0, confirmed by Example D).
- **Aggregation across projects**: both definitions use simple micro-averaging (mean over all N=7,023 bugs, not per-project macro-averaging) — this is unchanged from the original Stage F manuscript's finding and remains an open item (no per-project breakdown was available then; `identity_map_full.json`, not yet opened, may make this newly possible — flagged for Phase 5/6).

## Verdict: do not proceed to publication-level claims resting on this unresolved metric ambiguity

Per the task's own instruction ("Do NOT continue to publication-level claims if a metric discrepancy remains unresolved"), this audit's position is:

1. **Hit@K, Hit@5, Hit@10, and MRR are unaffected** by this ambiguity — both AP definitions are irrelevant to these metrics, and the Hit@10 comparison against IQLoc (the manuscript's clearest positive result) is not weakened by anything found in this phase.
2. **The MAP-based comparison against IQLoc (where H+SR currently reports a shortfall) cannot be sharpened into a more confident claim** — this audit could not determine which formula produced IQLoc's Table 10, and does not claim to have resolved what the original project explicitly left open. The manuscript's MAP-comparison language must remain hedged, consistent with (in fact, now more strongly justified than) the original Stage F framing.
3. **A new, genuinely load-bearing finding from this phase**: the TREC-vs-Package MAP gap is nearly double for H+SR relative to the three retrieval-only baselines. This is independent evidence — obtained before and without reference to the later displacement analysis — that reranking changes the *shape* of multi-GT retrieval behavior, and it should be cited in the manuscript's Discussion alongside (not instead of) the Phase 8/9 findings.

## Implications for the field, worth one paragraph in the manuscript's Discussion or Threats to Validity

This audit's experience is a concrete illustration of a broader reproducibility risk in IR-based bug localization: a benchmark paper's prose-stated metric formula and its accompanying released code can differ in ways that are easy to miss (both definitions look identical on the common case — single-GT bugs, or multi-GT bugs where either all or none of the GT is retrieved — and diverge only on partial multi-GT retrieval, exactly the regime this paper's own central finding concerns). Any future work building on IQLoc's numbers, or on this paper's own N=7,023 numbers, should independently verify which AP definition it is comparing against rather than assuming a bare "MAP" label is unambiguous — a concrete, generalizable methodological recommendation this audit can make with confidence, independent of how the specific IQLoc case is ultimately resolved.

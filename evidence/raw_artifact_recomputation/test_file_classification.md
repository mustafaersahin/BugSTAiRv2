# Step 6 — Test vs. Production File Classification Rule

## Rule actually used to produce every test/production number in the manuscript

Traced to `paper/q1_strengthening/final_closure/scripts/test_file_displacement_analysis.py` (and identically reimplemented in `two_file_mechanism.py`):

```python
def is_test(path):
    return "/test/" in path or "/tests/" in path
```

Applied to `resolved_repo_relative_path`-style strings (e.g., `camel-core/src/test/java/org/apache/camel/...`). This is a **substring path rule**: it returns true if the literal substring `/test/` or `/tests/` (with leading and trailing slash) appears anywhere in the file's repository-relative path, and false otherwise. No filename-suffix rule (`*Test.java`, `*Tests.java`), no annotation- or content-based rule, and no explicit source-set allowlist (e.g., Maven's `src/test/java` vs. `src/main/java` convention) is separately implemented — the substring rule happens to catch the Maven convention (`.../src/test/java/...` contains `/test/`) as a side effect, but would equally classify any path containing a `/test/` or `/tests/` directory component regardless of build-tool convention.

## Canonical rule elsewhere in the codebase

A second, independently-written classifier exists in `evaluation/fallback_failure_mode_audit.py`:

```python
def is_likely_test_path(path: str) -> bool:
    parts = [p.lower() for p in path.replace("\\", "/").split("/") if p]
    basename = parts[-1] if parts else ""
    if any(p in {"test", "tests", "testing", "__tests__", "testdata", "e2e", "spec"} for p in parts):
        return True
    if basename.startswith("test_") or basename.endswith("_test.py"):
        return True
    if ".test." in basename or ".spec." in basename:
        return True
    return False
```

A third exists in `dataset/bench4bl.py::corpus_contains_test_paths`, used only as a corpus-level observational flag (not a per-file classifier): markers `("/src/test/", "/src/tests/", "/test/", "/tests/")`, plus a check for relative paths starting with `test/` or `tests/` without a leading slash.

## Comparison and assessment

For this study's actual corpus (Java source under Maven/Gradle-style `src/main/java` / `src/test/java` layouts, all paths recorded with a leading module-relative segment and never a bare `test/`-prefixed relative path), the three rules are **functionally equivalent in practice**: `.../src/test/java/...` contains `/test/` as a substring, so the simpler rule used in the actual analysis scripts (`"/test/" in path or "/tests/" in path`) correctly classifies every Maven-convention test path the other two rules would also catch. The `is_likely_test_path` function is more general (also catches `testing/`, `__tests__/`, `e2e/`, `spec/`, filename-suffix conventions relevant to Python/JS repos) but is **not the function actually used** to produce any number in this manuscript — it exists elsewhere in the codebase for a different, broader audit and was not imported or called by the displacement/test-file analysis scripts.

## Exclusions, ambiguous cases, fallback classification

**None implemented.** The rule used is a two-way partition (test or production) with no third "ambiguous/excluded" bucket, no vendor/generated-file exclusion applied to this specific classification (a separate `is_likely_vendor_or_generated` function exists in the codebase but is not called by the test/production analysis), and no fallback for paths that match neither `/test/` nor `/tests/` other than defaulting to "production." A path such as `integration-test/src/main/java/...` (an integration-test *module* whose own internal layout is `src/main`, not `src/test`) would be classified as **production** by this rule, since it contains neither `/test/` nor `/tests/` as a slash-delimited substring (the module name `integration-test` does not equal `test`). This is a genuine, if likely small, source of potential misclassification not previously disclosed in the manuscript's methodology section, and is disclosed here.

## Spot check on this session's own recomputation

The 77 paths independently confirmed as "production-classified displaced files" in Step 8's rerun (listed in full in that step's supporting script output) were manually reviewed for this report: all 77 are under `src/main/java`, `src/java`, or an unqualified top-level `src/` path with no `test`/`tests` path segment — no visible misclassification among the sampled cases.

## Conclusion

The rule is precisely identified, traced to its exact source function, and is a reasonable (if slightly narrower than the codebase's own more general classifier) operational definition of "test file." This should be stated explicitly in the manuscript's methodology (Section 6, or a new methods subsection), rather than left implicit as "test file" and "production file" without a stated rule — this is applied in `12_manuscript_ist_submission_candidate.md`.

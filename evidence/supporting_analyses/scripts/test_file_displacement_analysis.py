"""P1-A: proper contingency analysis of test-file overrepresentation among
displaced vs promoted vs STABLE ground-truth files, now with a real STABLE
category computed via the stable_identity_sha256 join (found this phase,
resolving the Phase 10 gap)."""
import json, math
from pathlib import Path
from collections import defaultdict
import os
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[3]
EXTERNAL = _P(os.environ.get("BUGSTAIR_RESEARCH_REPO", REPO_ROOT.parent / "bug-localization-main-final"))

RANKINGS = REPO_ROOT / "data" / "rankings"
DISP = json.load(open(str(EXTERNAL / "results" / "multifile_displacement_analysis/DISPLACED_GT_FILES.json")))
RECOV = json.load(open(str(EXTERNAL / "results" / "multifile_displacement_analysis/RECOVERY_CASE_SUMMARY.json")))

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

hyb = load_jsonl(RANKINGS / "hybrid_rrf_records.jsonl")

# Build dataset_index <-> stable_identity_sha256 join, and H's own Top-10 GT files per bug
sid_by_idx = {}
h_top10_gt_by_sid = {}
for r in hyb:
    sid = r["ranking_provenance"]["stable_identity_sha256"]
    sid_by_idx[r["dataset_index"]] = sid
    gt = list(dict.fromkeys(r["gt_provenance"]["resolved_gt_paths"]))
    top10 = set(r["ranked_file_identities"][:10])
    h_top10_gt = [g for g in gt if g in top10]
    if h_top10_gt:
        h_top10_gt_by_sid[sid] = h_top10_gt

displaced_records = DISP["displaced_gt_file_records"]
promoted_records = RECOV["newly_promoted_gt_file_records"]

displaced_set = set((r["stable_identity_sha256"], r["gt_path"]) for r in displaced_records)
promoted_set = set((r["stable_identity_sha256"], r["gt_path"]) for r in promoted_records)

# STABLE = files in H's own Top-10 GT set, minus the displaced set (by construction,
# per Phase 9: every H-Top-10 GT file either stays [stable] or leaves [displaced]).
stable_records = []
total_h_top10_gt_files = 0
for sid, files in h_top10_gt_by_sid.items():
    for f in files:
        total_h_top10_gt_files += 1
        if (sid, f) not in displaced_set:
            stable_records.append({"stable_identity_sha256": sid, "gt_path": f})

print(f"Total H-Top-10 GT file instances (across all N=7023, not just |GT|>=2): {total_h_top10_gt_files}")
print(f"Displaced (known): {len(displaced_records)}")
print(f"Stable (implied = H-Top-10 minus displaced): {len(stable_records)}")
print(f"Promoted (known, was NOT in H-Top-10, entered H+SR-Top-10): {len(promoted_records)}")

def is_test(path):
    return "/test/" in path or "/tests/" in path

def classify(records, name):
    n_test = sum(1 for r in records if is_test(r["gt_path"]))
    n_total = len(records)
    print(f"{name}: {n_test}/{n_total} test files ({100*n_test/n_total:.1f}%)")
    return n_test, n_total - n_test

disp_test, disp_prod = classify(displaced_records, "DISPLACED")
stab_test, stab_prod = classify(stable_records, "STABLE")
promo_test, promo_prod = classify(promoted_records, "PROMOTED")

# 2x2 contingency: DISPLACED vs STABLE (the natural "did reranking touch this GT file negatively" comparison)
# odds ratio = (disp_test/disp_prod) / (stab_test/stab_prod)
def odds_ratio_ci(a, b, c, d):
    # a=test&displaced, b=prod&displaced, c=test&stable, d=prod&stable
    if b == 0 or c == 0 or a == 0 or d == 0:
        a2, b2, c2, d2 = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    else:
        a2, b2, c2, d2 = a, b, c, d
    OR = (a2 * d2) / (b2 * c2)
    se = math.sqrt(1/a2 + 1/b2 + 1/c2 + 1/d2)
    lo = math.exp(math.log(OR) - 1.96 * se)
    hi = math.exp(math.log(OR) + 1.96 * se)
    return OR, lo, hi

def chi2_2x2(a, b, c, d):
    n = a + b + c + d
    num = n * (a * d - b * c) ** 2
    den = (a + b) * (c + d) * (a + c) * (b + d)
    return num / den if den else 0.0

def fisher_exact_2x2(a, b, c, d):
    # two-sided p-value via direct hypergeometric summation (small enough tables here)
    from math import comb
    row1 = a + b
    row2 = c + d
    col1 = a + c
    n = a + b + c + d
    def p(a_):
        b_ = row1 - a_
        c_ = col1 - a_
        d_ = row2 - c_
        if b_ < 0 or c_ < 0 or d_ < 0:
            return 0.0
        return comb(row1, a_) * comb(row2, c_) / comb(n, col1)
    p_obs = p(a)
    total = 0.0
    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    for a_ in range(lo, hi + 1):
        pa = p(a_)
        if pa <= p_obs * 1.0000001:
            total += pa
    return total

print("\n=== DISPLACED vs STABLE (odds of being a test file) ===")
OR, lo, hi = odds_ratio_ci(disp_test, disp_prod, stab_test, stab_prod)
chi2 = chi2_2x2(disp_test, disp_prod, stab_test, stab_prod)
fisher_p = fisher_exact_2x2(disp_test, disp_prod, stab_test, stab_prod)
print(f"Odds ratio = {OR:.3f}  95% CI = [{lo:.3f}, {hi:.3f}]")
print(f"Chi-square = {chi2:.2f}")
print(f"Fisher exact two-sided p = {fisher_p:.3e}")

print("\n=== PROMOTED vs STABLE (odds of being a test file) ===")
OR2, lo2, hi2 = odds_ratio_ci(promo_test, promo_prod, stab_test, stab_prod)
chi2_2 = chi2_2x2(promo_test, promo_prod, stab_test, stab_prod)
fisher_p2 = fisher_exact_2x2(promo_test, promo_prod, stab_test, stab_prod)
print(f"Odds ratio = {OR2:.3f}  95% CI = [{lo2:.3f}, {hi2:.3f}]")
print(f"Chi-square = {chi2_2:.2f}")
print(f"Fisher exact two-sided p = {fisher_p2:.3e}")

print("\n=== DISPLACED vs PROMOTED (odds of being a test file) ===")
OR3, lo3, hi3 = odds_ratio_ci(disp_test, disp_prod, promo_test, promo_prod)
chi2_3 = chi2_2x2(disp_test, disp_prod, promo_test, promo_prod)
fisher_p3 = fisher_exact_2x2(disp_test, disp_prod, promo_test, promo_prod)
print(f"Odds ratio = {OR3:.3f}  95% CI = [{lo3:.3f}, {hi3:.3f}]")
print(f"Chi-square = {chi2_3:.2f}")
print(f"Fisher exact two-sided p = {fisher_p3:.3e}")

out = {
    "counts": {
        "displaced": {"test": disp_test, "production": disp_prod},
        "stable": {"test": stab_test, "production": stab_prod},
        "promoted": {"test": promo_test, "production": promo_prod},
    },
    "displaced_vs_stable": {"odds_ratio": OR, "ci95": [lo, hi], "chi2": chi2, "fisher_p": fisher_p},
    "promoted_vs_stable": {"odds_ratio": OR2, "ci95": [lo2, hi2], "chi2": chi2_2, "fisher_p": fisher_p2},
    "displaced_vs_promoted": {"odds_ratio": OR3, "ci95": [lo3, hi3], "chi2": chi2_3, "fisher_p": fisher_p3},
}
with open(Path(__file__).resolve().parents[1] / "data" / "test_file_contingency.json", "w") as f:
    json.dump(out, f, indent=2)
print("\nSaved to test_file_contingency.json")

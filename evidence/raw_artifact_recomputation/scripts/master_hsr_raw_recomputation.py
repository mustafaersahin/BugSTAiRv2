"""Final H+SR raw-artifact closure: independently recompute every H+SR-dependent
manuscript claim directly from the now-available raw prediction file, joined
against ground truth from the H ranking master file. No prior derived ledgers
are used as primary evidence here (they are used only as a secondary cross-check).
"""
import json
import random
import math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import os
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[3]
EXTERNAL = _P(os.environ.get("BUGSTAIR_RESEARCH_REPO", REPO_ROOT.parent / "bug-localization-main-final"))

RANKINGS = REPO_ROOT / "data" / "rankings"
HSR_PRED = REPO_ROOT / "data" / "h_sr" / "final_hsr_predictions.jsonl"
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)


def load_jsonl(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def is_test(path):
    return "/test/" in path or "/tests/" in path


print("Loading H master rankings + ground truth...")
h_by_sid = {}
gt_by_sid = {}
for r in load_jsonl(RANKINGS / "hybrid_rrf_records.jsonl"):
    sid = r["ranking_provenance"]["stable_identity_sha256"]
    h_by_sid[sid] = r["ranked_file_identities"]
    gt_by_sid[sid] = list(dict.fromkeys(r["gt_provenance"]["resolved_gt_paths"]))

print("Loading H+SR raw predictions...")
hsr_by_sid = {}
for r in load_jsonl(HSR_PRED):
    sid = r["stable_identity_sha256"]
    hsr_by_sid[sid] = r["ranked_file_identities"]

assert set(h_by_sid) == set(hsr_by_sid), "cohort mismatch"
sids = sorted(h_by_sid.keys())
print(f"N={len(sids)} bugs, cohort match confirmed")


def per_bug_metrics(ranked, gt):
    pos = {f: i + 1 for i, f in enumerate(ranked)}
    ranks = sorted(pos[g] for g in gt if g in pos)
    n_gt = len(gt)
    metrics = {}
    first = ranks[0] if ranks else None
    metrics["hit1"] = 1.0 if first is not None and first <= 1 else 0.0
    metrics["hit5"] = 1.0 if first is not None and first <= 5 else 0.0
    metrics["hit10"] = 1.0 if first is not None and first <= 10 else 0.0
    metrics["rr"] = (1.0 / first) if first is not None else 0.0
    hits_found = 0
    prec_sum = 0.0
    for k in ranks:
        hits_found += 1
        prec_sum += hits_found / k
    metrics["trec_ap"] = prec_sum / n_gt if n_gt else 0.0
    metrics["pkg_ap"] = (prec_sum / hits_found) if hits_found > 0 else 0.0
    for K in (5, 10):
        found_le_K = sum(1 for r in ranks if r <= K)
        metrics[f"gtrecall{K}"] = found_le_K / n_gt if n_gt else 0.0
        metrics[f"complete{K}"] = 1.0 if found_le_K == n_gt else 0.0
    metrics["first_rank"] = first
    metrics["ranks"] = ranks
    return metrics


print("Computing per-bug H and H+SR metrics...")
per_bug = {}
cardinality = {}
for sid in sids:
    gt = gt_by_sid[sid]
    cardinality[sid] = len(gt)
    h_m = per_bug_metrics(h_by_sid[sid], gt)
    hsr_m = per_bug_metrics(hsr_by_sid[sid], gt)
    per_bug[sid] = {"H": h_m, "HSR": hsr_m, "n_gt": len(gt)}

N = len(sids)


def aggregate(metric_key, system, subset=None):
    s = subset if subset is not None else sids
    return sum(per_bug[sid][system][metric_key] for sid in s) / len(s)


METRIC_KEYS = ["hit1", "hit5", "hit10", "rr", "trec_ap", "pkg_ap", "gtrecall5", "gtrecall10", "complete5", "complete10"]
LABELS = {"hit1": "hit_at_1", "hit5": "hit_at_5", "hit10": "hit_at_10", "rr": "mrr",
          "trec_ap": "trec_map", "pkg_ap": "package_map", "gtrecall5": "gtrecall_at_5",
          "gtrecall10": "gtrecall_at_10", "complete5": "complete_at_5", "complete10": "complete_at_10"}

print("\n=== FULL COHORT (N=7023) AGGREGATE ===")
full_agg = {"H": {}, "HSR": {}, "delta": {}}
for mk in METRIC_KEYS:
    h_v = aggregate(mk, "H")
    hsr_v = aggregate(mk, "HSR")
    full_agg["H"][LABELS[mk]] = h_v
    full_agg["HSR"][LABELS[mk]] = hsr_v
    full_agg["delta"][LABELS[mk]] = hsr_v - h_v
    print(f"{LABELS[mk]:15s} H={h_v:.6f}  H+SR={hsr_v:.6f}  delta={hsr_v-h_v:+.6f}")

# ---- Paired bootstrap over full cohort (vectorized with numpy) ----
B = 10000

def bootstrap_ci(subset_sids, seed=20260826):
    m = len(subset_sids)
    mat_h = np.array([[per_bug[sid]["H"][mk] for mk in METRIC_KEYS] for sid in subset_sids])
    mat_hsr = np.array([[per_bug[sid]["HSR"][mk] for mk in METRIC_KEYS] for sid in subset_sids])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, m, size=(B, m))
    h_means = mat_h[idx].mean(axis=1)   # (B, n_metrics)
    hsr_means = mat_hsr[idx].mean(axis=1)
    deltas = hsr_means - h_means
    lo = np.percentile(deltas, 2.5, axis=0)
    hi = np.percentile(deltas, 97.5, axis=0)
    return lo, hi

print("\nRunning paired bootstrap (full cohort, B=10000, seed=20260826, vectorized)...")
lo_arr, hi_arr = bootstrap_ci(sids)
full_ci = {}
for i, mk in enumerate(METRIC_KEYS):
    lo, hi = float(lo_arr[i]), float(hi_arr[i])
    full_ci[LABELS[mk]] = {"delta": full_agg["delta"][LABELS[mk]], "ci_lo": lo, "ci_hi": hi, "excludes_zero": (lo > 0 or hi < 0)}
    print(f"{LABELS[mk]:15s} delta={full_agg['delta'][LABELS[mk]]:+.6f}  CI=[{lo:+.6f},{hi:+.6f}]  excl0={lo>0 or hi<0}")

# ---- Cardinality strata ----
print("\n=== CARDINALITY STRATA ===")
strata = {
    "gt_eq_1": [sid for sid in sids if cardinality[sid] == 1],
    "gt_eq_2": [sid for sid in sids if cardinality[sid] == 2],
    "gt_ge_3": [sid for sid in sids if cardinality[sid] >= 3],
    "gt_ge_2": [sid for sid in sids if cardinality[sid] >= 2],
}
strata_results = {}
for sname, subset in strata.items():
    print(f"\n-- {sname} (N={len(subset)}) --")
    res = {"n": len(subset), "H": {}, "HSR": {}, "delta": {}, "ci": {}}
    for mk in METRIC_KEYS:
        h_v = aggregate(mk, "H", subset)
        hsr_v = aggregate(mk, "HSR", subset)
        res["H"][LABELS[mk]] = h_v
        res["HSR"][LABELS[mk]] = hsr_v
        res["delta"][LABELS[mk]] = hsr_v - h_v
    # bootstrap within stratum (vectorized)
    lo_arr_s, hi_arr_s = bootstrap_ci(subset, seed=20260826)
    for i, mk in enumerate(METRIC_KEYS):
        lo, hi = float(lo_arr_s[i]), float(hi_arr_s[i])
        res["ci"][LABELS[mk]] = {"lo": lo, "hi": hi, "excludes_zero": (lo > 0 or hi < 0)}
        if mk in ("hit10", "rr", "trec_ap", "gtrecall10", "complete10"):
            print(f"  {LABELS[mk]:15s} H={res['H'][LABELS[mk]]:.4f} H+SR={res['HSR'][LABELS[mk]]:.4f} delta={res['delta'][LABELS[mk]]:+.4f} CI=[{lo:+.4f},{hi:+.4f}]")
    strata_results[sname] = res

# ---- Displacement mechanism (TRUE raw reconstruction) ----
print("\n=== DISPLACEMENT MECHANISM (true raw) ===")
cat_A = cat_B = cat_C = cat_D = cat_other = 0
total_gt_instances = 0
displaced_records = []  # (sid, path)
promoted_records = []
stable_records = []
for sid in sids:
    gt = gt_by_sid[sid]
    h_ranked = h_by_sid[sid]
    hsr_ranked = hsr_by_sid[sid]
    h_pos = {f: i + 1 for i, f in enumerate(h_ranked)}
    hsr_pos = {f: i + 1 for i, f in enumerate(hsr_ranked)}
    for g in gt:
        total_gt_instances += 1
        h_rank = h_pos.get(g)
        hsr_rank = hsr_pos.get(g)
        if h_rank is None or h_rank > 100:
            cat_A += 1
            continue
        if h_rank <= 10:
            if hsr_rank is not None and hsr_rank <= 10:
                cat_D += 1
                stable_records.append((sid, g))
            else:
                cat_B += 1
                displaced_records.append((sid, g))
        else:
            if hsr_rank is not None and hsr_rank <= 10:
                cat_C += 1
                promoted_records.append((sid, g))
            else:
                cat_other += 1

print(f"total GT instances: {total_gt_instances}")
print(f"Category A (never H top-100): {cat_A} ({100*cat_A/total_gt_instances:.2f}%)")
print(f"Category B (displaced): {cat_B} ({100*cat_B/total_gt_instances:.2f}%)")
print(f"Category C (promoted): {cat_C} ({100*cat_C/total_gt_instances:.2f}%)")
print(f"Category D (stable): {cat_D} ({100*cat_D/total_gt_instances:.2f}%)")
print(f"other (in window 11-100, not promoted): {cat_other} ({100*cat_other/total_gt_instances:.2f}%)")

# ---- Test-file displacement ----
print("\n=== TEST-FILE DISPLACEMENT ===")
disp_test = sum(1 for _, g in displaced_records if is_test(g))
disp_prod = len(displaced_records) - disp_test
stab_test = sum(1 for _, g in stable_records if is_test(g))
stab_prod = len(stable_records) - stab_test
prom_test = sum(1 for _, g in promoted_records if is_test(g))
prom_prod = len(promoted_records) - prom_test
print(f"Displaced: test={disp_test} prod={disp_prod} total={len(displaced_records)}")
print(f"Stable: test={stab_test} prod={stab_prod} total={len(stable_records)}")
print(f"Promoted: test={prom_test} prod={prom_prod} total={len(promoted_records)}")


def fisher_exact_2x2(a, b, c, d):
    # a,b top row; c,d bottom row -- two-sided via hypergeometric enumeration
    from math import comb
    n = a + b + c + d
    row1 = a + b
    row2 = c + d
    col1 = a + c
    def p_val(x):
        return comb(row1, x) * comb(row2, col1 - x) / comb(n, col1)
    obs = p_val(a)
    total = 0.0
    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    for x in range(lo, hi + 1):
        p = p_val(x)
        if p <= obs * 1.0000001:
            total += p
    return total


def odds_ratio_ci(a, b, c, d):
    # a=test in group1, b=prod in group1, c=test in baseline, d=prod in baseline
    or_ = (a * d) / (b * c)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    lo = math.exp(math.log(or_) - 1.96 * se)
    hi = math.exp(math.log(or_) + 1.96 * se)
    return or_, lo, hi


or_disp_stab, lo1, hi1 = odds_ratio_ci(disp_test, disp_prod, stab_test, stab_prod)
p_disp_stab = fisher_exact_2x2(disp_test, disp_prod, stab_test, stab_prod)
or_prom_stab, lo2, hi2 = odds_ratio_ci(prom_test, prom_prod, stab_test, stab_prod)
p_prom_stab = fisher_exact_2x2(prom_test, prom_prod, stab_test, stab_prod)
or_disp_prom, lo3, hi3 = odds_ratio_ci(disp_test, disp_prod, prom_test, prom_prod)
p_disp_prom = fisher_exact_2x2(disp_test, disp_prod, prom_test, prom_prod)

print(f"\nDisplaced vs Stable: OR={or_disp_stab:.3f} CI=[{lo1:.3f},{hi1:.3f}] Fisher p={p_disp_stab:.3e}")
print(f"Promoted vs Stable: OR={or_prom_stab:.3f} CI=[{lo2:.3f},{hi2:.3f}] Fisher p={p_prom_stab:.3e}")
print(f"Displaced vs Promoted: OR={or_disp_prom:.3f} CI=[{lo3:.3f},{hi3:.3f}] Fisher p={p_disp_prom:.3e}")

# ---- Two-file mechanism ----
print("\n=== TWO-FILE MECHANISM (true raw) ===")
displaced_set = set(displaced_records)
promoted_set = set(promoted_records)
stable_set = set(stable_records)
two_file_outcomes = Counter()
mixed_stable_displaced_joint = Counter()
for sid in strata["gt_eq_2"]:
    gt = gt_by_sid[sid]
    statuses = []
    for g in gt:
        if (sid, g) in displaced_set:
            statuses.append(("DISPLACED", g))
        elif (sid, g) in stable_set:
            statuses.append(("STABLE", g))
        elif (sid, g) in promoted_set:
            statuses.append(("PROMOTED", g))
        else:
            statuses.append(("ABSENT_BOTH", g))
    combo = tuple(sorted(s for s, _ in statuses))
    two_file_outcomes[combo] += 1
    if sorted(s for s, _ in statuses) == ["DISPLACED", "STABLE"]:
        disp_g = [g for s, g in statuses if s == "DISPLACED"][0]
        stab_g = [g for s, g in statuses if s == "STABLE"][0]
        key = ("test" if is_test(disp_g) else "prod", "test" if is_test(stab_g) else "prod")
        mixed_stable_displaced_joint[key] += 1

for combo, cnt in two_file_outcomes.most_common():
    print(f"  {combo}: {cnt}")
print("\nOne-displaced-one-stable joint file-type breakdown:")
for k, v in mixed_stable_displaced_joint.items():
    print(f"  {k}: {v}")
total_mixed = sum(mixed_stable_displaced_joint.values())
print(f"total: {total_mixed}")

# ---- Ground truth composition (unaffected by H+SR, but recomputed for completeness) ----
print("\n=== GROUND TRUTH COMPOSITION (multi-file) ===")
mixed = prod_only = test_only = 0
for sid in strata["gt_ge_2"]:
    gt = gt_by_sid[sid]
    flags = set(is_test(g) for g in gt)
    if flags == {True, False}:
        mixed += 1
    elif flags == {False}:
        prod_only += 1
    else:
        test_only += 1
total_multi = mixed + prod_only + test_only
print(f"mixed={mixed} ({100*mixed/total_multi:.1f}%) prod_only={prod_only} ({100*prod_only/total_multi:.1f}%) test_only={test_only} ({100*test_only/total_multi:.1f}%) total={total_multi}")

# ---- Save everything ----
output = {
    "n": N,
    "full_cohort_aggregate": full_agg,
    "full_cohort_bootstrap_ci": full_ci,
    "cardinality_strata": {k: {"n": v["n"], "H": v["H"], "HSR": v["HSR"], "delta": v["delta"], "ci": v["ci"]} for k, v in strata_results.items()},
    "displacement": {
        "total_gt_instances": total_gt_instances,
        "category_A": cat_A, "category_A_pct": 100*cat_A/total_gt_instances,
        "category_B": cat_B, "category_B_pct": 100*cat_B/total_gt_instances,
        "category_C": cat_C, "category_C_pct": 100*cat_C/total_gt_instances,
        "category_D": cat_D, "category_D_pct": 100*cat_D/total_gt_instances,
        "category_other": cat_other, "category_other_pct": 100*cat_other/total_gt_instances,
    },
    "test_file_displacement": {
        "displaced": {"test": disp_test, "prod": disp_prod},
        "stable": {"test": stab_test, "prod": stab_prod},
        "promoted": {"test": prom_test, "prod": prom_prod},
        "or_displaced_vs_stable": {"or": or_disp_stab, "ci": [lo1, hi1], "p": p_disp_stab},
        "or_promoted_vs_stable": {"or": or_prom_stab, "ci": [lo2, hi2], "p": p_prom_stab},
        "or_displaced_vs_promoted": {"or": or_disp_prom, "ci": [lo3, hi3], "p": p_disp_prom},
    },
    "two_file_mechanism": {
        "joint_outcomes": {str(k): v for k, v in two_file_outcomes.items()},
        "mixed_stable_displaced_joint_type": {str(k): v for k, v in mixed_stable_displaced_joint.items()},
        "total_one_displaced_one_stable": total_mixed,
    },
    "ground_truth_composition": {"mixed": mixed, "prod_only": prod_only, "test_only": test_only, "total_multi": total_multi},
}
with open(OUT / "master_hsr_raw_recomputation.json", "w") as f:
    json.dump(output, f, indent=2)
print("\nSaved to", OUT / "master_hsr_raw_recomputation.json")

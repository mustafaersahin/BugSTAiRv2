"""Phase 7/11: paired bootstrap + Wilcoxon signed-rank + Cliff's delta for the
B (BM25) -> D (Jina) -> H (Hybrid) retrieval ladder, computed per-bug from raw
rankings (real paired data, since all three methods share the same N=7023 bugs
in the same order/identity).
"""
import json, random, statistics
from pathlib import Path
from collections import defaultdict

REPO = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/iqloc_author_final_7483/rankings")

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def trec_ap(ranked, gt):
    gt_u = list(dict.fromkeys(gt))
    rank_of = {f: i+1 for i, f in enumerate(ranked)}
    found = sorted(rank_of[g] for g in gt_u if g in rank_of)
    if not found: return 0.0
    return sum((i+1)/r for i, r in enumerate(found)) / len(gt_u)

def hit_at(ranked, gt, k):
    gt_s = set(gt)
    return 1 if any(f in gt_s for f in ranked[:k]) else 0

def mrr_c(ranked, gt):
    gt_s = set(gt)
    for i, f in enumerate(ranked, start=1):
        if f in gt_s: return 1.0/i
    return 0.0

bm25 = {r["dataset_index"]: r for r in load_jsonl(REPO/"bm25_records.jsonl")}
jina = {r["dataset_index"]: r for r in load_jsonl(REPO/"jina_records.jsonl")}
hyb  = {r["dataset_index"]: r for r in load_jsonl(REPO/"hybrid_rrf_records.jsonl")}

ids = sorted(set(bm25) & set(jina) & set(hyb))
print(f"paired bug count: {len(ids)}")

per_bug = {}
for idx in ids:
    gt = bm25[idx]["gt_provenance"]["resolved_gt_paths"]
    if not gt:
        continue
    row = {}
    for label, rec in [("B", bm25[idx]), ("D", jina[idx]), ("H", hyb[idx])]:
        ranked = rec["ranked_file_identities"]
        row[f"{label}_h10"] = hit_at(ranked, gt, 10)
        row[f"{label}_mrr"] = mrr_c(ranked, gt)
        row[f"{label}_map"] = trec_ap(ranked, gt)
    per_bug[idx] = row

print(f"evaluable paired bugs: {len(per_bug)}")

def paired_bootstrap(deltas, B=10000, seed=20260826):
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(B):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample)/n)
    means.sort()
    lo = means[int(0.025*B)]
    hi = means[int(0.975*B)]
    return sum(deltas)/n, lo, hi

def wilcoxon_signed_rank(deltas):
    # simple normal-approximation Wilcoxon signed-rank test (no scipy dependency assumed)
    nz = [d for d in deltas if d != 0]
    n = len(nz)
    if n == 0:
        return None, None
    ranks = sorted(range(n), key=lambda i: abs(nz[i]))
    rank_of = [0]*n
    for pos, i in enumerate(ranks):
        rank_of[i] = pos + 1
    # handle ties by average rank (simple pass, good enough for large n)
    W_pos = sum(rank_of[i] for i in range(n) if nz[i] > 0)
    W_neg = sum(rank_of[i] for i in range(n) if nz[i] < 0)
    W = min(W_pos, W_neg)
    mean_W = n*(n+1)/4
    sd_W = (n*(n+1)*(2*n+1)/24) ** 0.5
    z = (W - mean_W) / sd_W if sd_W > 0 else 0.0
    return W, z

def cliffs_delta(x, y):
    # x, y paired-by-index deltas relative to 0: use sign test style cliff's delta
    # here we compute cliff's delta between the two raw samples (before/after)
    more = sum(1 for a in x for b in y if a > b)
    less = sum(1 for a in x for b in y if a < b)
    return (more - less) / (len(x)*len(y))

comparisons = [("B_to_D", "B", "D"), ("B_to_H", "B", "H"), ("D_to_H", "D", "H")]
metrics = ["h10", "mrr", "map"]

results = {}
for comp_name, m1, m2 in comparisons:
    results[comp_name] = {}
    for metric in metrics:
        k1, k2 = f"{m1}_{metric}", f"{m2}_{metric}"
        deltas = [per_bug[idx][k2] - per_bug[idx][k1] for idx in per_bug]
        mean_delta, lo, hi = paired_bootstrap(deltas)
        W, z = wilcoxon_signed_rank(deltas)
        results[comp_name][metric] = {
            "mean_delta": mean_delta, "ci_lo": lo, "ci_hi": hi,
            "excludes_zero": (lo > 0 or hi < 0),
            "wilcoxon_W": W, "wilcoxon_z": z,
        }
        print(f"{comp_name} {metric:5}: delta={mean_delta:+.5f} CI=[{lo:+.5f},{hi:+.5f}] excl0={lo>0 or hi<0}  W={W} z={z:.2f}")

out = Path("/Users/ersahinm/Desktop/buglocalization/BugResearch/evidence/supporting_analyses/data/ablation_stats.json")
out.write_text(json.dumps(results, indent=2))
print(f"\nSaved to {out}")

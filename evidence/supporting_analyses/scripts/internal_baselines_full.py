"""Phase 6: full metric set (Hit@1/5/10, MRR, TREC/Pkg MAP, GTRecall@5/10, Complete@5/10)
for BM25, Jina, Hybrid H -- aggregate AND per-project (owner_repo) -- from raw rankings.
H+SR is NOT included here (no raw per-bug predictions available for N=7023 -- see Phase 3).
"""
import json
from pathlib import Path
from collections import defaultdict

REPO = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/iqloc_author_final_7483/rankings")
OUT_DIR = Path("/Users/ersahinm/Desktop/buglocalization/BugResearch/evidence/supporting_analyses/data")

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def trec_ap(ranked, gt):
    gt_u = list(dict.fromkeys(gt))
    rank_of = {f: i+1 for i, f in enumerate(ranked)}
    found = sorted(rank_of[g] for g in gt_u if g in rank_of)
    if not found: return 0.0
    return sum((i+1)/r for i, r in enumerate(found)) / len(gt_u)

def package_ap(ranked, gt):
    gt_s = set(gt); hits = 0; s = 0.0
    for i, f in enumerate(ranked, start=1):
        if f in gt_s:
            hits += 1; s += hits/i
    return 0.0 if hits == 0 else s/hits

def mrr_c(ranked, gt):
    gt_s = set(gt)
    for i, f in enumerate(ranked, start=1):
        if f in gt_s: return 1.0/i
    return 0.0

def hit_at(ranked, gt, k):
    gt_s = set(gt)
    return 1 if any(f in gt_s for f in ranked[:k]) else 0

def gtrecall_at(ranked, gt, k):
    gt_u = list(dict.fromkeys(gt))
    top = set(ranked[:k])
    return sum(1 for g in gt_u if g in top) / len(gt_u)

def complete_at(ranked, gt, k):
    gt_u = set(gt)
    top = set(ranked[:k])
    return 1 if gt_u.issubset(top) else 0

def eval_records(records):
    n = len(records)
    acc = defaultdict(list)
    for rec in records:
        ranked = rec["ranked_file_identities"]
        gt = rec["gt_provenance"]["resolved_gt_paths"]
        if not gt:
            continue
        acc["trec_ap"].append(trec_ap(ranked, gt))
        acc["pkg_ap"].append(package_ap(ranked, gt))
        acc["mrr"].append(mrr_c(ranked, gt))
        acc["h1"].append(hit_at(ranked, gt, 1))
        acc["h5"].append(hit_at(ranked, gt, 5))
        acc["h10"].append(hit_at(ranked, gt, 10))
        acc["gtr5"].append(gtrecall_at(ranked, gt, 5))
        acc["gtr10"].append(gtrecall_at(ranked, gt, 10))
        acc["c5"].append(complete_at(ranked, gt, 5))
        acc["c10"].append(complete_at(ranked, gt, 10))
    m = len(acc["trec_ap"])
    if m == 0:
        return None
    return {
        "n": n, "m_evaluable": m,
        "hit_at_1": sum(acc["h1"])/m, "hit_at_5": sum(acc["h5"])/m, "hit_at_10": sum(acc["h10"])/m,
        "mrr": sum(acc["mrr"])/m, "trec_map": sum(acc["trec_ap"])/m, "package_map": sum(acc["pkg_ap"])/m,
        "gtrecall_at_5": sum(acc["gtr5"])/m, "gtrecall_at_10": sum(acc["gtr10"])/m,
        "complete_at_5": sum(acc["c5"])/m, "complete_at_10": sum(acc["c10"])/m,
    }

methods = {
    "BM25": "bm25_records.jsonl",
    "Jina": "jina_records.jsonl",
    "Hybrid_H": "hybrid_rrf_records.jsonl",
}

all_results = {"aggregate": {}, "per_project": {}}
for label, fname in methods.items():
    recs = load_jsonl(REPO / fname)
    all_results["aggregate"][label] = eval_records(recs)

    by_repo = defaultdict(list)
    for r in recs:
        by_repo[r["owner_repo"]].append(r)
    project_results = {}
    for repo, repo_recs in by_repo.items():
        res = eval_records(repo_recs)
        if res:
            project_results[repo] = res
    all_results["per_project"][label] = project_results

print("=== AGGREGATE (full metric set) ===")
for label, res in all_results["aggregate"].items():
    print(f"\n{label} (n={res['n']}):")
    for k, v in res.items():
        if k not in ("n", "m_evaluable"):
            print(f"  {k:16} = {v:.6f}")

print("\n\n=== PER-PROJECT (Hybrid_H example, top 10 by bug count) ===")
proj_h = all_results["per_project"]["Hybrid_H"]
sorted_projs = sorted(proj_h.items(), key=lambda kv: -kv[1]["n"])[:10]
print(f"{'repo':38} {'n':>5} {'Hit@10':>8} {'MRR':>8} {'TREC_MAP':>9} {'Complete@10':>12}")
for repo, res in sorted_projs:
    print(f"{repo:38} {res['n']:5} {res['hit_at_10']:8.4f} {res['mrr']:8.4f} {res['trec_map']:9.4f} {res['complete_at_10']:12.4f}")

out_path = OUT_DIR / "internal_baselines_full.json"
out_path.write_text(json.dumps(all_results, indent=2))
print(f"\nSaved full results to {out_path}")

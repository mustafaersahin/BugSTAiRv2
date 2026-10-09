"""Independently recompute Hit@K/MRR/TREC-MAP/Package-MAP for BM25/Jina/Hybrid H
directly from the raw per-bug ranking JSONL files, with NO dependency on any
previously reported aggregate. This is a from-scratch, independent reimplementation
of the metric formulas (deliberately not importing method/ranking_metrics.py or
method/iqloc_metrics.py, to serve as a true independent check on those modules too).
"""
import json, sys
from pathlib import Path

REPO = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/iqloc_author_final_7483/rankings")

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]

def trec_ap(ranked_files, gt_paths):
    gt = list(dict.fromkeys(gt_paths))  # unique, first-seen order
    if not gt:
        return None
    rank_of = {f: i+1 for i, f in enumerate(ranked_files)}
    found_ranks = sorted(rank_of[g] for g in gt if g in rank_of)
    num = sum((i+1)/r for i, r in enumerate(found_ranks))
    return num / len(gt)

def package_ap(ranked_files, gt_paths):
    gt = set(gt_paths)
    hits = 0
    s = 0.0
    for i, f in enumerate(ranked_files, start=1):
        if f in gt:
            hits += 1
            s += hits / i
    return 0.0 if hits == 0 else s / hits

def mrr_contrib(ranked_files, gt_paths):
    gt = set(gt_paths)
    for i, f in enumerate(ranked_files, start=1):
        if f in gt:
            return 1.0 / i
    return 0.0

def hit_at_k(ranked_files, gt_paths, k):
    gt = set(gt_paths)
    return 1 if any(f in gt for f in ranked_files[:k]) else 0

def evaluate(records, label):
    n = len(records)
    trec_aps, pkg_aps, mrrs = [], [], []
    h1 = h5 = h10 = 0
    skipped_empty_gt = 0
    for rec in records:
        ranked = rec["ranked_file_identities"]
        gt = rec["gt_provenance"]["resolved_gt_paths"]
        if not gt:
            skipped_empty_gt += 1
            continue
        trec_aps.append(trec_ap(ranked, gt))
        pkg_aps.append(package_ap(ranked, gt))
        mrrs.append(mrr_contrib(ranked, gt))
        h1 += hit_at_k(ranked, gt, 1)
        h5 += hit_at_k(ranked, gt, 5)
        h10 += hit_at_k(ranked, gt, 10)
    m = len(trec_aps)
    print(f"=== {label} ===")
    print(f"  n_records={n}  n_evaluable(gt non-empty)={m}  skipped_empty_gt={skipped_empty_gt}")
    print(f"  Hit@1  = {h1/m:.6f}")
    print(f"  Hit@5  = {h5/m:.6f}")
    print(f"  Hit@10 = {h10/m:.6f}")
    print(f"  MRR    = {sum(mrrs)/m:.6f}")
    print(f"  TREC MAP    = {sum(trec_aps)/m:.6f}")
    print(f"  Package MAP = {sum(pkg_aps)/m:.6f}")
    print()
    return {
        "label": label, "n": n, "m_evaluable": m,
        "hit_at_1": h1/m, "hit_at_5": h5/m, "hit_at_10": h10/m,
        "mrr": sum(mrrs)/m, "trec_map": sum(trec_aps)/m, "package_map": sum(pkg_aps)/m,
    }

results = {}
for fname, label in [("bm25_records.jsonl", "BM25 (independently recomputed)"),
                      ("jina_records.jsonl", "Jina (independently recomputed)"),
                      ("hybrid_rrf_records.jsonl", "Hybrid H (independently recomputed)")]:
    recs = load_jsonl(REPO / fname)
    results[label] = evaluate(recs, label)

out_path = Path("/Users/ersahinm/Desktop/buglocalization/BugResearch/evidence/supporting_analyses/data/recomputed_retrieval_metrics.json")
out_path.write_text(json.dumps(results, indent=2))
print(f"Saved to {out_path}")

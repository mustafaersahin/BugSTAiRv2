"""Cheap, CPU-only RRF k-sensitivity sweep using only the existing raw BM25/Jina
rankings (no new retrieval or inference). Tests whether k=60 is a reasonable,
non-knife-edge choice.
"""
import json
from pathlib import Path
import os
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[3]
EXTERNAL = _P(os.environ.get("BUGSTAIR_RESEARCH_REPO", REPO_ROOT.parent / "bug-localization-main-final"))

REPO = REPO_ROOT / "data" / "rankings"

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
ids = sorted(set(bm25) & set(jina))

def rrf_fuse(bm25_ranked, jina_ranked, k):
    scores = {}
    for i, f in enumerate(bm25_ranked, start=1):
        scores[f] = scores.get(f, 0.0) + 1.0/(k+i)
    for i, f in enumerate(jina_ranked, start=1):
        scores[f] = scores.get(f, 0.0) + 1.0/(k+i)
    return sorted(scores.keys(), key=lambda f: -scores[f])

k_values = [10, 30, 60, 100, 150, 200, 500]
results = {}
for k in k_values:
    h1=h5=h10=0; mrrs=[]; maps=[]; m=0
    for idx in ids:
        gt = bm25[idx]["gt_provenance"]["resolved_gt_paths"]
        if not gt:
            continue
        fused = rrf_fuse(bm25[idx]["ranked_file_identities"], jina[idx]["ranked_file_identities"], k)
        h1 += hit_at(fused, gt, 1); h5 += hit_at(fused, gt, 5); h10 += hit_at(fused, gt, 10)
        mrrs.append(mrr_c(fused, gt)); maps.append(trec_ap(fused, gt))
        m += 1
    results[k] = {"n": m, "hit_at_1": h1/m, "hit_at_5": h5/m, "hit_at_10": h10/m,
                  "mrr": sum(mrrs)/m, "trec_map": sum(maps)/m}
    print(f"k={k:4}  Hit@1={h1/m:.4f}  Hit@5={h5/m:.4f}  Hit@10={h10/m:.4f}  MRR={sum(mrrs)/m:.4f}  TREC_MAP={sum(maps)/m:.4f}")

out = Path(__file__).resolve().parents[1] / "data" / "rrf_k_sensitivity.json"
out.write_text(json.dumps(results, indent=2))
print(f"\nSaved to {out}")

best_k = max(results, key=lambda k: results[k]["hit_at_10"])
print(f"\nBest k by Hit@10: {best_k} ({results[best_k]['hit_at_10']:.4f}); k=60 gives {results[60]['hit_at_10']:.4f}")
spread = max(r["hit_at_10"] for r in results.values()) - min(r["hit_at_10"] for r in results.values())
print(f"Hit@10 spread across all tested k: {spread:.4f}")

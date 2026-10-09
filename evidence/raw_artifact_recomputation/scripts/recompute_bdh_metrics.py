"""Step 2 (partial): independently recompute B, D, H metrics directly from the
master raw ranking records now available locally at
bug-localization-main-final/results/iqloc_author_final_7483/rankings/
(bm25_records.jsonl, jina_records.jsonl, hybrid_rrf_records.jsonl), and compare
against the official final_metrics.json aggregate.

H+SR cannot be recomputed here: the full N=7023 raw per-bug prediction file
(final_hsr_predictions.jsonl) is confirmed complete via its freeze manifest but
is not physically present in this local copy (see hsr_artifact_verification.md).
"""
import json
from pathlib import Path

ROOT = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results")
RANKINGS = ROOT / "iqloc_author_final_7483/rankings"
OUT = Path("/Users/ersahinm/Desktop/buglocalization/BugResearch/evidence/raw_artifact_recomputation/data")


def load_jsonl(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def metrics_for_file(path, label):
    n = 0
    hit1 = hit5 = hit10 = 0
    rr_sum = 0.0
    trec_ap_sum = 0.0
    pkg_ap_sum = 0.0
    for r in load_jsonl(path):
        gt = list(dict.fromkeys(r["gt_provenance"]["resolved_gt_paths"]))
        if not gt:
            continue
        ranked = r["ranked_file_identities"]
        pos = {f: i + 1 for i, f in enumerate(ranked)}
        ranks = sorted(pos[g] for g in gt if g in pos)
        n += 1
        first_rank = ranks[0] if ranks else None
        if first_rank is not None:
            if first_rank <= 1:
                hit1 += 1
            if first_rank <= 5:
                hit5 += 1
            if first_rank <= 10:
                hit10 += 1
            rr_sum += 1.0 / first_rank
        # AP: standard TREC (denominator = |G_q|) and package (denominator = hits found)
        hits_found = 0
        prec_sum = 0.0
        # need precision@k at each gt rank; iterate over sorted gt ranks that were found
        found_ranks = ranks  # ranks of gt files actually present in the (possibly truncated) list, sorted
        for k in found_ranks:
            hits_found += 1
            prec_sum += hits_found / k
        trec_ap = prec_sum / len(gt)
        pkg_ap = (prec_sum / hits_found) if hits_found > 0 else 0.0
        trec_ap_sum += trec_ap
        pkg_ap_sum += pkg_ap
    result = {
        "method": label,
        "n": n,
        "hit_at_1": hit1 / n,
        "hit_at_5": hit5 / n,
        "hit_at_10": hit10 / n,
        "mrr": rr_sum / n,
        "trec_map": trec_ap_sum / n,
        "package_map": pkg_ap_sum / n,
    }
    return result


if __name__ == "__main__":
    out = {}
    out["bm25"] = metrics_for_file(RANKINGS / "bm25_records.jsonl", "B (BM25)")
    print("bm25 done:", out["bm25"])
    out["jina"] = metrics_for_file(RANKINGS / "jina_records.jsonl", "D (Jina dense)")
    print("jina done:", out["jina"])
    out["hybrid_rrf"] = metrics_for_file(RANKINGS / "hybrid_rrf_records.jsonl", "H (Hybrid RRF)")
    print("hybrid done:", out["hybrid_rrf"])

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "bdh_independent_recomputation.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote", OUT / "bdh_independent_recomputation.json")

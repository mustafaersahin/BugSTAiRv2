"""Validate our independent metric implementation against the exact fixture
examples documented in docs/IQLOC_METRIC_SEMANTICS.md (Examples A-D + partial).
This is an independent cross-check, not a re-import of the repo's own code.
"""
def trec_ap(ranked, gt):
    gt_u = list(dict.fromkeys(gt))
    rank_of = {f: i+1 for i, f in enumerate(ranked)}
    found = sorted(rank_of[g] for g in gt_u if g in rank_of)
    if not found:
        return 0.0
    num = sum((i+1)/r for i, r in enumerate(found))
    return num / len(gt_u)

def package_ap(ranked, gt):
    gt_s = set(gt)
    hits = 0; s = 0.0
    for i, f in enumerate(ranked, start=1):
        if f in gt_s:
            hits += 1
            s += hits / i
    return 0.0 if hits == 0 else s / hits

def rr(ranked, gt):
    gt_s = set(gt)
    for i, f in enumerate(ranked, start=1):
        if f in gt_s:
            return 1.0 / i
    return 0.0

def hit_at(ranked, gt, k):
    gt_s = set(gt)
    return 1 if any(f in gt_s for f in ranked[:k]) else 0

def recall_at(ranked, gt, k):
    gt_u = list(dict.fromkeys(gt))
    top = set(ranked[:k])
    return sum(1 for g in gt_u if g in top) / len(gt_u)

cases = [
    ("A", ["A"], ["A","B","C"], 1.000, 1.000, 1.000, 1, 1, 1, 1.000),
    ("B", ["A","C"], ["A","B","C"], 0.833, 0.833, 1.000, 1, 1, 1, 1.000),
    ("C", ["A","C"], ["B","C","A"], 0.583, 0.583, 0.500, 0, 1, 1, 1.000),
    ("D", ["A","C"], ["B","D"], 0.000, 0.000, 0.000, 0, 0, 0, 0.000),
    ("partial", ["A","B","C"], ["A","X","Y"], 0.333, 1.000, 1.000, 1, 1, 1, 0.333),
]

print(f"{'Ex':8} {'TREC_AP':>9} {'pkg_AP':>9} {'RR':>7} {'H@1':>4} {'H@5':>4} {'H@10':>5} {'Recall@10':>10}")
all_pass = True
for name, gt, ranking, exp_trec, exp_pkg, exp_rr, exp_h1, exp_h5, exp_h10, exp_recall in cases:
    t = trec_ap(ranking, gt)
    p = package_ap(ranking, gt)
    r = rr(ranking, gt)
    h1 = hit_at(ranking, gt, 1)
    h5 = hit_at(ranking, gt, 5)
    h10 = hit_at(ranking, gt, 10)
    rec = recall_at(ranking, gt, 10)
    ok = (round(t,3)==exp_trec and round(p,3)==exp_pkg and round(r,3)==exp_rr
          and h1==exp_h1 and h5==exp_h5 and h10==exp_h10 and round(rec,3)==exp_recall)
    all_pass = all_pass and ok
    print(f"{name:8} {t:9.3f} {p:9.3f} {r:7.3f} {h1:4} {h5:4} {h10:5} {rec:10.3f}  {'OK' if ok else 'MISMATCH'}")

print()
print("ALL FIXTURES MATCH DOCUMENTED EXPECTED VALUES:" , all_pass)

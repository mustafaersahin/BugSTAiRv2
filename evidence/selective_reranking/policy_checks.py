"""Further checks of the selective policy: simple rules, feature group ablation, and
leave one ecosystem out evaluation. Same utility, model (ridge), and rule (predicted utility > 0)."""
import csv, json
from pathlib import Path
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "data/features.csv")))
fcols = [c for c in rows[0] if c.startswith("f_")]
F = {c: np.array([float(r[c]) for r in rows]) for c in fcols}
G = np.array([r["repository"] for r in rows])
M = {m: (np.array([float(r["H_" + m]) for r in rows]), np.array([float(r["S_" + m]) for r in rows])) for m in ("hit10", "rr", "gtrecall10", "complete10")}
u = (M["rr"][1] - M["rr"][0]) + (M["complete10"][1] - M["complete10"][0]); N = len(rows)
groups = {
    "report": ["f_title_words", "f_desc_words", "f_has_trace", "f_n_camel", "f_mentions_test"],
    "report_and_candidates": ["f_n_cand_mentioned", "f_top10_mentioned", "f_top1_mentioned"],
    "retrievers": ["f_overlap10_BD", "f_top1_agree", "f_rank_H1_in_B", "f_rank_H1_in_D", "f_score_top1", "f_score_margin", "f_score_10"],
    "repository": ["f_log_ndocs"], "file_types": ["f_test_share_top10"]}
assert sorted(sum(groups.values(), [])) == sorted(fcols)
def summ(sel): return {m: float(np.where(sel, M[m][1], M[m][0]).mean()) for m in M} | {"share": float(sel.mean())}
def oof(cols, folds):
    X = np.column_stack([F[c] for c in cols]); pred = np.zeros(N)
    for tr, te in folds:
        m = make_pipeline(StandardScaler(), Ridge(alpha=10.0)); m.fit(X[tr], u[tr]); pred[te] = m.predict(X[te])
    return pred > 0
out = {"always_H": summ(np.zeros(N, bool)), "always_SR": summ(np.ones(N, bool))}
base_folds = list(GroupKFold(n_splits=5).split(np.zeros(N), u, G))
out["full_model"] = summ(oof(fcols, base_folds))
# simple rules (no learning)
out["rule_skip_if_top1_named"] = summ(F["f_top1_mentioned"] == 0)
out["rule_skip_if_score_top1_high"] = summ(F["f_score_top1"] < np.median(F["f_score_top1"]))
out["rule_skip_if_retrievers_agree"] = summ(F["f_top1_agree"] == 0)
# ablation
for g, cols in groups.items():
    out["without_" + g] = summ(oof([c for c in fcols if c not in cols], base_folds))
    out["only_" + g] = summ(oof(cols, base_folds))
# leave one ecosystem out
eco = np.array(["spring" if r["repository"].startswith("spring") else "apache" if r["repository"].startswith("apache") else "jboss_wildfly" for r in rows])
pred = np.zeros(N, bool); per = {}
for e in np.unique(eco):
    te = eco == e; tr = ~te
    X = np.column_stack([F[c] for c in fcols]); m = make_pipeline(StandardScaler(), Ridge(alpha=10.0)); m.fit(X[tr], u[tr]); pred[te] = m.predict(X[te]) > 0
    per[e] = {"n": int(te.sum()), "policy": {k: float(np.where(pred, M[k][1], M[k][0])[te].mean()) for k in M},
              "always_H": {k: float(M[k][0][te].mean()) for k in M}, "always_SR": {k: float(M[k][1][te].mean()) for k in M}, "share": float(pred[te].mean())}
out["leave_one_ecosystem_out"] = {"overall": summ(pred), "per_ecosystem": per}
json.dump(out, open(HERE / "data/selective_reranking_checks.json", "w"), indent=1)
f = lambda e: f"share={e['share']:.3f} Hit@10={e['hit10']:.4f} MRR={e['rr']:.4f} GTR@10={e['gtrecall10']:.4f} Compl@10={e['complete10']:.4f}"
for k, v in out.items():
    if k != "leave_one_ecosystem_out": print(f"{k:34s}", f(v))
print("leave one ecosystem out (overall):", f(out["leave_one_ecosystem_out"]["overall"]))
for e, v in per.items():
    print(" ", e, "n=%d share=%.3f" % (v["n"], v["share"]), "policy", {k: round(x, 4) for k, x in v["policy"].items()}, "H", {k: round(x, 4) for k, x in v["always_H"].items()}, "SR", {k: round(x, 4) for k, x in v["always_SR"].items()})

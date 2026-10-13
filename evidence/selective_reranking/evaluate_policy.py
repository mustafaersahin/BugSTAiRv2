"""Selective reranking: decide per bug whether to apply SR, using only features
known before reranking. Out-of-fold predictions, folds grouped by repository.
Utility (fixed in advance): u = delta RR + delta Complete@10 (S minus H)."""
import csv, json
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "data/features.csv")))
fcols = [c for c in rows[0] if c.startswith("f_")]
X = np.array([[float(r[c]) for c in fcols] for r in rows])
G = np.array([r["repository"] for r in rows])
M = {m: (np.array([float(r["H_" + m]) for r in rows]), np.array([float(r["S_" + m]) for r in rows]))
     for m in ("hit10", "rr", "gtrecall10", "complete10")}
nGT = np.array([int(r["n_gt"]) for r in rows])
u = (M["rr"][1] - M["rr"][0]) + (M["complete10"][1] - M["complete10"][0])
N = len(rows)
print(f"N={N}, features={len(fcols)}, mean u={u.mean():+.4f}, share u>0: {np.mean(u>0):.3f}, u<0: {np.mean(u<0):.3f}")

def oof(model_fn, seed=0):
    pred = np.zeros(N)
    for tr, te in GroupKFold(n_splits=5).split(X, u, G):
        m = model_fn(); m.fit(X[tr], u[tr]); pred[te] = m.predict(X[te])
    return pred

models = {
    "gradient_boosting": lambda: HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=200, random_state=0),
    "ridge": lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
}

def evaluate(rerank):
    out = {}
    for m, (h, s) in M.items():
        out[m] = float(np.where(rerank, s, h).mean())
    out["share_reranked"] = float(np.mean(rerank))
    return out

res = {"always_H": evaluate(np.zeros(N, bool)), "always_SR": evaluate(np.ones(N, bool)), "oracle": evaluate(u > 0)}
rng = np.random.default_rng(20261014)
rand = {}
curves = {}
for name, fn in models.items():
    p = oof(fn)
    corr = float(np.corrcoef(p, u)[0, 1])
    res[name + "_tau0"] = evaluate(p > 0); res[name + "_tau0"]["pred_corr_with_u"] = corr
    curve = []
    for q in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        thr = np.quantile(p, 1 - q) if 0 < q < 1 else (np.inf if q == 0 else -np.inf)
        sel = p >= thr if 0 < q < 1 else (np.ones(N, bool) if q == 1 else np.zeros(N, bool))
        e = evaluate(sel)
        # random selection with the same share
        rr_ = [evaluate(rng.random(N) < q) for _ in range(100)]
        e["random_same_share"] = {k: float(np.mean([r[k] for r in rr_])) for k in M}
        curve.append(dict(target_share=q, **e))
    curves[name] = curve
    # paired bootstrap at tau=0: policy vs always SR
    sel = p > 0
    B = 2000; diffs = {m: [] for m in M}
    for _ in range(B):
        idx = rng.integers(0, N, N)
        for m, (h, s) in M.items():
            pol = np.where(sel, s, h)[idx].mean(); alw = s[idx].mean(); diffs[m].append(pol - alw)
    res[name + "_tau0"]["vs_always_SR_ci95"] = {m: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for m, v in diffs.items()}
    # by cardinality
    byc = {}
    for lab, mask in (("one_file", nGT == 1), ("two_files", nGT == 2), ("three_plus", nGT >= 3)):
        byc[lab] = dict(n=int(mask.sum()), share_reranked=float(np.mean(sel[mask])))
    res[name + "_tau0"]["by_cardinality"] = byc
res["curves"] = curves
json.dump(res, open(HERE / "data/selective_reranking_results.json", "w"), indent=1)

def line(k, e): return f"{k:22s} reranked={e['share_reranked']:.3f} Hit@10={e['hit10']:.4f} MRR={e['rr']:.4f} GTR@10={e['gtrecall10']:.4f} Compl@10={e['complete10']:.4f}"
for k in ("always_H", "always_SR", "oracle", "gradient_boosting_tau0", "ridge_tau0"):
    print(line(k, res[k]))
for k in ("gradient_boosting_tau0", "ridge_tau0"):
    print(k, "corr(pred,u)=%.3f" % res[k]["pred_corr_with_u"], "CI vs always SR:", {m: [round(x, 4) for x in v] for m, v in res[k]["vs_always_SR_ci95"].items()})
    print("   by cardinality", res[k]["by_cardinality"])
print("\ncurve (gradient boosting) vs random at same share:")
for c in curves["gradient_boosting"]:
    r = c["random_same_share"]
    print(f"share={c['target_share']:.1f} MRR={c['rr']:.4f} (rand {r['rr']:.4f})  Compl@10={c['complete10']:.4f} (rand {r['complete10']:.4f})  Hit@10={c['hit10']:.4f} (rand {r['hit10']:.4f})")

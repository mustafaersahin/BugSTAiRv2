"""Robustness checks for the selective reranking policy (ridge, tau = 0)."""
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
X = np.array([[float(r[c]) for c in fcols] for r in rows]); G = np.array([r["repository"] for r in rows])
M = {m: (np.array([float(r["H_" + m]) for r in rows]), np.array([float(r["S_" + m]) for r in rows])) for m in ("hit10", "rr", "gtrecall10", "complete10")}
nGT = np.array([int(r["n_gt"]) for r in rows]); N = len(rows)
d = {m: M[m][1] - M[m][0] for m in M}
out = {}

def run(u, groups, seed=0):
    pred = np.zeros(N)
    ug = np.unique(groups); rng = np.random.default_rng(seed); perm = dict(zip(ug, rng.permutation(len(ug))))
    g2 = np.array([perm[g] for g in groups])
    for tr, te in GroupKFold(n_splits=5).split(X, u, g2):
        m = make_pipeline(StandardScaler(), Ridge(alpha=10.0)); m.fit(X[tr], u[tr]); pred[te] = m.predict(X[te])
    return pred > 0

def summ(sel):
    return {m: float(np.where(sel, M[m][1], M[m][0]).mean()) for m in M} | {"share": float(sel.mean())}

# 1. different utility weights
u_main = d["rr"] + d["complete10"]
for lam in (0.5, 1.0, 2.0):
    sel = run(d["rr"] + lam * d["complete10"], G); out[f"lambda_{lam}"] = summ(sel)
# 2. repeated fold assignments
reps = [summ(run(u_main, G, seed=s)) for s in range(20)]
out["repeats_20"] = {k: [float(np.min([r[k] for r in reps])), float(np.max([r[k] for r in reps]))] for k in reps[0]}
# 3. by cardinality (main)
sel = run(u_main, G); out["main"] = summ(sel)
for lab, mask in (("one_file", nGT == 1), ("two_files", nGT == 2), ("three_plus", nGT >= 3)):
    out["by_cardinality_" + lab] = {"n": int(mask.sum()), "share_reranked": float(sel[mask].mean()),
        "policy": {m: float(np.where(sel, M[m][1], M[m][0])[mask].mean()) for m in M},
        "always_H": {m: float(M[m][0][mask].mean()) for m in M}, "always_SR": {m: float(M[m][1][mask].mean()) for m in M}}
# 4. leaving out the largest repository (apache/camel) from evaluation
big = G == "apache/camel"
out["excluding_camel"] = {"n": int((~big).sum()), "policy": {m: float(np.where(sel, M[m][1], M[m][0])[~big].mean()) for m in M},
    "always_SR": {m: float(M[m][1][~big].mean()) for m in M}, "always_H": {m: float(M[m][0][~big].mean()) for m in M}}
# 5. standardized coefficients on all data (interpretation only)
m = make_pipeline(StandardScaler(), Ridge(alpha=10.0)); m.fit(X, u_main)
out["coefficients_std"] = dict(sorted(zip(fcols, [float(c) for c in m[-1].coef_]), key=lambda kv: -abs(kv[1])))
json.dump(out, open(HERE / "data/selective_reranking_robustness.json", "w"), indent=1)
f = lambda e: " ".join(f"{k}={v:.4f}" for k, v in e.items())
print("main        ", f(out["main"]))
for lam in (0.5, 1.0, 2.0): print(f"lambda {lam}  ", f(out[f"lambda_{lam}"]))
print("20 repeats (min,max):", {k: [round(x, 4) for x in v] for k, v in out["repeats_20"].items()})
for lab in ("one_file", "two_files", "three_plus"):
    e = out["by_cardinality_" + lab]; print(lab, "n=", e["n"], "share=%.3f" % e["share_reranked"])
    for k in ("always_H", "always_SR", "policy"): print("   ", k, f(e[k]))
e = out["excluding_camel"]; print("excluding camel n=", e["n"]); [print("   ", k, f(e[k])) for k in ("always_H", "always_SR", "policy")]
print("top coefficients:", {k: round(v, 4) for k, v in list(out["coefficients_std"].items())[:8]})

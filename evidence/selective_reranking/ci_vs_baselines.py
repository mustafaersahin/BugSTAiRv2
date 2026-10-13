"""Paired bootstrap intervals (10,000 resamples) of the selective policy against always H and always H+SR."""
import csv, json
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "data/features.csv")))
fcols = [c for c in rows[0] if c.startswith("f_")]
X = np.array([[float(r[c]) for c in fcols] for r in rows]); G = np.array([r["repository"] for r in rows])
M = {m: (np.array([float(r["H_" + m]) for r in rows]), np.array([float(r["S_" + m]) for r in rows])) for m in ("hit10", "rr", "gtrecall10", "complete10")}
u = (M["rr"][1] - M["rr"][0]) + (M["complete10"][1] - M["complete10"][0]); N = len(rows)
models = {"ridge": lambda: make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
          "gradient_boosting": lambda: HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=200, random_state=0)}
rng = np.random.default_rng(20261014); B = 10000; out = {}
idx = rng.integers(0, N, size=(B, N))
for name, fn in models.items():
    pred = np.zeros(N)
    for tr, te in GroupKFold(n_splits=5).split(X, u, G):
        m = fn(); m.fit(X[tr], u[tr]); pred[te] = m.predict(X[te])
    sel = pred > 0
    res = {"share_reranked": float(sel.mean())}
    for m_, (h, s) in M.items():
        pol = np.where(sel, s, h)
        res[m_] = {"policy": float(pol.mean()), "always_H": float(h.mean()), "always_SR": float(s.mean())}
        for lab, base in (("vs_H", h), ("vs_SR", s)):
            d = (pol - base)[idx].mean(axis=1)
            res[m_][lab] = {"delta": float((pol - base).mean()), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]}
    out[name] = res
json.dump(out, open(HERE / "data/selective_reranking_ci.json", "w"), indent=1)
for name, r in out.items():
    print(name, "share %.4f" % r["share_reranked"])
    for m_ in M:
        print("  ", m_, "policy=%.4f" % r[m_]["policy"], "vs H %+.4f [%+.4f, %+.4f]" % (r[m_]["vs_H"]["delta"], *r[m_]["vs_H"]["ci95"]), "vs SR %+.4f [%+.4f, %+.4f]" % (r[m_]["vs_SR"]["delta"], *r[m_]["vs_SR"]["ci95"]))

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

HERE = Path(__file__).resolve().parent
res = json.load(open(HERE.parent / "evidence/selective_reranking/data/selective_reranking_results.json"))
plt.rcParams["font.family"] = "Helvetica" if any("Helvetica" in f.name for f in fm.fontManager.ttflist) else "DejaVu Sans"
curve = res["curves"]["ridge"]
x = [c["target_share"] for c in curve]
panels = [("rr", "MRR"), ("complete10", "Complete@10")]
fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), dpi=300)
for ax, (key, label) in zip(axes, panels):
    ax.plot(x, [c[key] for c in curve], color="#1d4ed8", marker="o", ms=4, lw=1.8, label="Selective (ridge)")
    ax.plot(x, [c["random_same_share"][key] for c in curve], color="#6b7280", ls="--", lw=1.4, label="Random selection")
    p = res["ridge_tau0"]
    ax.scatter([p["share_reranked"]], [p[key]], s=70, color="#b91c1c", zorder=5, label="Predicted gain > 0")
    ax.set_xlabel("Share of bugs reranked (0 = always H, 1 = always H+SR)", fontsize=9)
    ax.set_ylabel(label, fontsize=10)
    ax.grid(True, color="#e5e7eb", lw=0.8)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0].legend(fontsize=8, frameon=False, loc="lower right")
plt.tight_layout()
plt.savefig(HERE / "fig4_selective_reranking.pdf")
print("done")

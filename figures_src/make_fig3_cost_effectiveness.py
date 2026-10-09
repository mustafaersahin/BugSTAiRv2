import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams["font.family"] = "Helvetica" if any("Helvetica" in f.name for f in fm.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 1.0

systems = [
    ("B (BM25)", 0.710, 0.6484, "#1d4ed8", "o", False),
    ("H (Hybrid)", 0.710, 0.7934, "#16a34a", "s", True),   # lower bound: dense-retrieval online cost not logged
    ("H+SR", 709.876, 0.8035, "#b91c1c", "^", False),
]

fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=300)

for name, cost, hit10, color, marker, is_lower_bound in systems:
    face = "white" if is_lower_bound else color
    ax.scatter([cost], [hit10], s=170, c=face, marker=marker, edgecolors=color,
               linewidths=2.0, zorder=5, label=name)
    if is_lower_bound:
        # right-pointing chevron to indicate "at least this value"
        ax.annotate("", xy=(cost * 1.55, hit10), xytext=(cost * 1.08, hit10),
                     arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6))

# annotate points
ax.annotate("B (BM25)\n0.710s measured\nonline retrieval latency\nHit@10=0.648", (0.710, 0.6484), xytext=(1.3, 0.60),
            fontsize=9.5, color="#1d4ed8", ha="left",
            arrowprops=dict(arrowstyle="-", color="#1d4ed8", lw=0.8))
ax.annotate("H (Hybrid)\n≥ 0.710s (BM25 component only;\ndense-retrieval online cost not logged)\nHit@10=0.793", (0.710, 0.7934), xytext=(1.3, 0.855),
            fontsize=9.5, color="#16a34a", ha="left",
            arrowprops=dict(arrowstyle="-", color="#16a34a", lw=0.8))
ax.annotate("H+SR\n709.9s reranking-stage\ncompute (mean)\nHit@10=0.804", (709.876, 0.8035), xytext=(90, 0.71),
            fontsize=9.5, color="#b91c1c", ha="left",
            arrowprops=dict(arrowstyle="-", color="#b91c1c", lw=0.8))

# dashed connector from the H point to the H+SR point; x and y changes are two separate comparisons
ax.annotate("", xy=(709.876, 0.8035), xytext=(0.90, 0.7934),
            arrowprops=dict(arrowstyle="->", color="#6b7280", lw=1.4, linestyle=(0, (5, 4))))
ax.text(5.0, 0.745, "Horizontal change: ~1,000×\n(reranking stage time vs. BM25 latency)\nVertical change: +0.0101 Hit@10\n(H+SR vs. H)", fontsize=9, color="#374151",
        ha="center", style="italic")

ax.set_xscale("log")
ax.set_xlim(0.3, 2500)
ax.set_ylim(0.55, 0.90)
ax.set_xlabel("Measured stage time per bug (seconds, log scale)", fontsize=12)
ax.set_ylabel("Hit@10 (full N = 7,023 cohort)", fontsize=12)
ax.set_title("Effectiveness–cost plane", fontsize=14, fontweight="bold")
ax.grid(True, which="major", axis="both", color="#e5e7eb", linewidth=0.8, zorder=0)
ax.grid(True, which="minor", axis="x", color="#f3f4f6", linewidth=0.5, zorder=0)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("/Users/ersahinm/Desktop/buglocalization/BugResearch/manuscript/figures/fig3_cost_effectiveness.pdf")
print("done")

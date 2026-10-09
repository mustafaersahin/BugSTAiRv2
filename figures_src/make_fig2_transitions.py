"""Generate Figure 4: Sankey-style transition diagram, H top-10/window state
-> H+SR top-10 state, using the corrected unconditional Table 7 counts."""

# Corrected unconditional counts (Table 7 + the "other" row)
A = 3008       # never in H's top-100
WINDOW = 4833  # in H's 11-100 window (not top-10)
TOP10 = 8822   # in H's top-10
C = 1086       # promoted (window -> H+SR top-10)
OTHER = 3747   # window -> stays out of H+SR top-10
D = 7676       # top10 -> stable (H+SR top-10)
B = 1146       # top10 -> displaced (out of H+SR top-10)
TOTAL = 16663
assert WINDOW == C + OTHER
assert TOP10 == D + B
assert A + WINDOW + TOP10 == TOTAL

W, H = 1700, 860
scale = 540.0 / TOTAL
left_x = 260
right_x = 1440
node_w = 26

left_top = 90
nodes_left = [
    ("Never in H's\ntop-100", A, "#fecaca", "#b91c1c"),
    ("In H's window,\noutside top-10\n(rank 11–100)", WINDOW, "#fde68a", "#92400e"),
    ("In H's top-10", TOP10, "#bbf7d0", "#166534"),
]

right_top = 90
nodes_right = [
    ("In H+SR's top-10", D + C, "#bfdbfe", "#1e3a8a"),
    ("Not in H+SR's top-10", A + OTHER + B, "#e5e7eb", "#374151"),
]

flows = [
    # (from_node_idx, to_node_idx, value, color, label)
    (0, 1, A, "#ef4444", f"A — retrieval/window failure: {A:,} (18.05%)"),
    (1, 0, C, "#2563eb", f"C — promoted: {C:,} (6.52%)"),
    (1, 1, OTHER, "#f59e0b", f"in window, never promoted: {OTHER:,} (22.49%)"),
    (2, 0, D, "#16a34a", f"D — stable: {D:,} (46.07%)"),
    (2, 1, B, "#dc2626", f"B — reranking displacement: {B:,} (6.88%)"),
]


def node_geom(nodes, x):
    y = left_top
    geom = []
    for label, val, fill, stroke in nodes:
        h = val * scale
        geom.append({"x": x, "y": y, "h": h, "val": val, "label": label, "fill": fill, "stroke": stroke})
        y += h + 34
    return geom


L = node_geom(nodes_left, left_x)
R = node_geom(nodes_right, right_x)

# track cumulative offset used on each node's right/left edge for stacking flows
left_offset = [0.0] * len(L)
right_offset = [0.0] * len(R)

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
svg.append(f'<text x="{W/2}" y="32" text-anchor="middle" font-size="20" fill="#111827" font-weight="700">Hybrid H state &#8594; H+SR state, all 16,663 ground-truth file instances</text>')
svg.append(f'<text x="{W/2}" y="58" text-anchor="middle" font-size="15" fill="#374151" font-style="italic">'
            f'Band width is proportional to N; percentages are of the full 16,663-instance population.</text>')

flow_colors = {0: "#ef4444", 1: "#2563eb", 2: "#f59e0b", 3: "#16a34a", 4: "#dc2626"}

for i, (li, ri, val, color, label) in enumerate(flows):
    lnode = L[li]
    rnode = R[ri]
    band_h = val * scale
    y0a = lnode["y"] + left_offset[li]
    y0b = y0a + band_h
    left_offset[li] += band_h

    y1a = rnode["y"] + right_offset[ri]
    y1b = y1a + band_h
    right_offset[ri] += band_h

    x0 = lnode["x"] + node_w
    x1 = rnode["x"]
    xm = (x0 + x1) / 2

    path = (f'M{x0},{y0a} C{xm},{y0a} {xm},{y1a} {x1},{y1a} '
            f'L{x1},{y1b} C{xm},{y1b} {xm},{y0b} {x0},{y0b} Z')
    svg.append(f'<path d="{path}" fill="{color}" opacity="0.55" stroke="none"/>')

# draw nodes on top
for geom in L + R:
    svg.append(f'<rect x="{geom["x"]}" y="{geom["y"]}" width="{node_w}" height="{geom["h"]:.1f}" '
                f'fill="{geom["fill"]}" stroke="{geom["stroke"]}" stroke-width="2"/>')

# left labels (outside, to the left)
for geom in L:
    cy = geom["y"] + geom["h"] / 2
    lines = geom["label"].split("\n")
    n = len(lines)
    for i, line in enumerate(lines):
        dy = (i - (n - 1) / 2) * 20
        svg.append(f'<text x="{geom["x"]-14}" y="{cy+dy+6}" text-anchor="end" font-size="17" '
                    f'font-weight="600" fill="#111827">{line}</text>')
    svg.append(f'<text x="{geom["x"]-14}" y="{cy + (n/2)*20 + 24}" text-anchor="end" font-size="14" '
                f'fill="#4b5563">N={geom["val"]:,}</text>')

# right labels (outside, to the right)
for geom in R:
    cy = geom["y"] + geom["h"] / 2
    lines = geom["label"].split("\n")
    n = len(lines)
    for i, line in enumerate(lines):
        dy = (i - (n - 1) / 2) * 20
        svg.append(f'<text x="{geom["x"]+node_w+14}" y="{cy+dy+6}" text-anchor="start" font-size="17" '
                    f'font-weight="600" fill="#111827">{line}</text>')
    svg.append(f'<text x="{geom["x"]+node_w+14}" y="{cy + (n/2)*20 + 24}" text-anchor="start" font-size="14" '
                f'fill="#4b5563">N={geom["val"]:,}</text>')

# legend band at bottom, on its own white strip clear of the diagram
leg_top = 750
svg.append(f'<rect x="0" y="{leg_top}" width="{W}" height="{H-leg_top}" fill="#ffffff"/>')
svg.append(f'<line x1="40" y1="{leg_top}" x2="{W-40}" y2="{leg_top}" stroke="#e5e7eb" stroke-width="1.5"/>')
legend_items = [
    ("#ef4444", f"A — retrieval/window failure: 3,008 (18.05%)"),
    ("#f59e0b", f"in window (11–100), never promoted: 3,747 (22.49%)"),
    ("#2563eb", f"C — promotion: 1,086 (6.52%)"),
    ("#16a34a", f"D — stable: 7,676 (46.07%)"),
    ("#dc2626", f"B — reranking displacement: 1,146 (6.88%)"),
]
cols = 2
col_w = (W - 160) / cols
leg_y0 = leg_top + 34
for i, (color, text) in enumerate(legend_items):
    col = i % cols
    row = i // cols
    x = 90 + col * col_w
    y = leg_y0 + row * 30
    svg.append(f'<rect x="{x}" y="{y-15}" width="22" height="16" fill="{color}" opacity="0.7"/>')
    svg.append(f'<text x="{x+32}" y="{y-2}" font-size="15" fill="#111827">{text}</text>')

svg.append('</svg>')

with open(str(__import__("pathlib").Path(__file__).resolve().parent / "fig2_transitions.svg"), "w") as f:
    f.write("\n".join(svg))
print("written")

import json, csv
from pathlib import Path

REPO = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/iqloc_author_final_7483/rankings")
OUT = Path("/Users/ersahinm/Desktop/buglocalization/BugResearch/evidence/supporting_analyses/data/bug_cohort_manifest.csv")

with open(REPO / "bm25_records.jsonl") as f:
    recs = [json.loads(line) for line in f]

rows = []
for r in recs:
    gt = r["gt_provenance"]["resolved_gt_paths"]
    rows.append({
        "dataset_index": r["dataset_index"],
        "old_author_record_index": r.get("old_author_record_index"),
        "author_record_index": r.get("author_record_index"),
        "owner_repo": r["owner_repo"],
        "snapshot_sha": r.get("snapshot_sha", ""),
        "n_unique_gt": len(set(gt)),
        "n_documents": r["n_documents"],
        "evaluable_fingerprint": r["evaluable_fingerprint"],
    })

rows.sort(key=lambda x: x["dataset_index"])
with open(OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUT}")

# Summary stats
from collections import Counter
repo_counts = Counter(r["owner_repo"] for r in rows)
gt_card_counts = Counter(r["n_unique_gt"] for r in rows)
print(f"\nDistinct owner_repo values: {len(repo_counts)}")
print(f"Top 10 repos by bug count:")
for repo, n in repo_counts.most_common(10):
    print(f"  {repo}: {n}")
print(f"\nGT cardinality distribution:")
for card in sorted(gt_card_counts):
    print(f"  |GT|={card}: {gt_card_counts[card]} bugs")

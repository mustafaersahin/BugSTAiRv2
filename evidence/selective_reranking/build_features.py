"""Build one row per bug with features available BEFORE reranking and the
per-bug outcomes of H and H+SR. No new model inference is involved."""
import csv, json, os, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
EXTERNAL = Path(os.environ.get("BUGSTAIR_RESEARCH_REPO", REPO_ROOT.parent / "bug-localization-main-final"))
RES = EXTERNAL / "results" / "iqloc_author_final_7483"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)

def jsonl(p):
    with open(p) as f:
        for line in f:
            yield json.loads(line)

def is_test(path):
    return "/test/" in path or "/tests/" in path

def metrics(ranked, gt):
    pos = {f: i + 1 for i, f in enumerate(ranked)}
    ranks = sorted(pos[g] for g in gt if g in pos)
    n = len(gt); first = ranks[0] if ranks else None
    return dict(hit10=float(first is not None and first <= 10), rr=(1 / first if first else 0.0),
                gtrecall10=sum(r <= 10 for r in ranks) / n, complete10=float(sum(r <= 10 for r in ranks) == n))

print("loading rankings")
bm25 = {r["dataset_index"]: r for r in jsonl(RES / "rankings/bm25_records.jsonl")}
jina = {r["dataset_index"]: r for r in jsonl(RES / "rankings/jina_records.jsonl")}
hyb = {}
sid2idx = {}
for r in jsonl(RES / "rankings/hybrid_rrf_records.jsonl"):
    hyb[r["dataset_index"]] = r
    sid2idx[r["ranking_provenance"]["stable_identity_sha256"]] = r["dataset_index"]
hsr = {}
for r in jsonl(RES / "stage_c/final_hsr_n7023/predictions/final_hsr_predictions.jsonl"):
    hsr[sid2idx[r["stable_identity_sha256"]]] = r["ranked_file_identities"]
assert set(hsr) == set(hyb)

print("loading report texts")
ident = json.load(open(RES / "identity_map_full.json"))["primary_map_rows"]
key2idx = {}
for x in ident:
    key2idx.setdefault((str(x["bug_id"]), x["version"]), []).append(x)
ds = json.load(open(EXTERNAL / "data/iqloc/author_repository/IQLoc/Dataset/Bench4BLExtended.json"))
text = {}
for d in ds:
    for x in key2idx.get((str(d["bug_id"]), d["version"]), []):
        same = d["sub_project"].lower() == str(x["sub_project_final"]).lower() or len(key2idx[(str(d["bug_id"]), d["version"])]) == 1
        if same:
            text[int(x["final_dataset_index"])] = ((d.get("bug_title") or ""), (d.get("bug_description") or ""))
assert len(text) == 7023, len(text)

TRACE = re.compile(r"\bat\s+[\w.$]+\([\w$]+\.java:\d+\)|Exception|Caused by")
CAMEL = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b")
rows = []
for i, h in sorted(hyb.items()):
    gt = list(dict.fromkeys(h["gt_provenance"]["resolved_gt_paths"]))
    H, S = h["ranked_file_identities"], hsr[i]
    title, desc = text[i]; full = title + "\n" + desc
    B, D = bm25[i]["ranked_file_identities"], jina[i]["ranked_file_identities"]
    top10H = H[:10]
    words = set(re.findall(r"[A-Za-z0-9_$]+", full))
    base = lambda p: Path(p).stem
    mentioned = [p for p in H[:100] if base(p) in words]
    mh, ms = metrics(H, gt), metrics(S, gt)
    sc = h["ranked_scores"]
    rows.append(dict(
        cohort_index=i, repository=h["owner_repo"], n_gt=len(gt),
        f_title_words=len(title.split()), f_desc_words=len(desc.split()),
        f_has_trace=int(bool(TRACE.search(full))), f_n_camel=len(set(CAMEL.findall(full))),
        f_mentions_test=int("test" in full.lower()),
        f_n_cand_mentioned=len(mentioned), f_top10_mentioned=sum(base(p) in words for p in top10H),
        f_top1_mentioned=int(base(H[0]) in words),
        f_overlap10_BD=len(set(B[:10]) & set(D[:10])), f_top1_agree=int(B[0] == D[0]),
        f_rank_H1_in_B=min(B.index(H[0]) + 1 if H[0] in B else 201, 201),
        f_rank_H1_in_D=min(D.index(H[0]) + 1 if H[0] in D else 201, 201),
        f_log_ndocs=__import__("math").log(h["n_documents"]),
        f_score_top1=sc[0], f_score_margin=sc[0] - sc[1], f_score_10=sc[9],
        f_test_share_top10=sum(is_test(p) for p in top10H) / 10,
        H_hit10=mh["hit10"], H_rr=mh["rr"], H_gtrecall10=mh["gtrecall10"], H_complete10=mh["complete10"],
        S_hit10=ms["hit10"], S_rr=ms["rr"], S_gtrecall10=ms["gtrecall10"], S_complete10=ms["complete10"]))
with open(OUT / "features.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows written")
import statistics as st
for k in ("H_hit10","S_hit10","H_complete10","S_complete10","H_rr","S_rr"):
    print(k, round(st.mean(r[k] for r in rows), 4))

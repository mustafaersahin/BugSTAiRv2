"""P1-A mechanism check: does the bug report text share fewer tokens with
test-file paths than with production-file paths? Uses path-token overlap
as a lightweight, available-everywhere proxy for lexical relevance (full
source content is only available for the Camel subset via the BLUiR
extraction; path tokens are available for all N=7023 bugs)."""
import json, re
from pathlib import Path
from collections import defaultdict

RANKINGS = Path("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/iqloc_author_final_7483/rankings")
EXT_PATH = "/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/data/iqloc/author_repository/IQLoc/Dataset/Bench4BLExtended.json"
DISP = json.load(open("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/multifile_displacement_analysis/DISPLACED_GT_FILES.json"))
RECOV = json.load(open("/Users/ersahinm/Desktop/buglocalization/bug-localization-main-final/results/multifile_displacement_analysis/RECOVERY_CASE_SUMMARY.json"))

def load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f]

hyb = load_jsonl(RANKINGS / "hybrid_rrf_records.jsonl")
ext = json.load(open(EXT_PATH))

sid_to_query = {}
sid_to_gt_top10 = {}
for r in hyb:
    sid = r["ranking_provenance"]["stable_identity_sha256"]
    src = ext[r["old_author_record_index"]]
    sid_to_query[sid] = (src.get("bug_title", "") or "") + " " + (src.get("bug_description", "") or "")
    gt = list(dict.fromkeys(r["gt_provenance"]["resolved_gt_paths"]))
    top10 = set(r["ranked_file_identities"][:10])
    sid_to_gt_top10[sid] = [g for g in gt if g in top10]

def split_ident(name):
    parts = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    parts = re.sub(r'[_/\.\-]', ' ', parts)
    return set(p.lower() for p in parts.split() if len(p) > 1)

def query_tokens(text):
    words = re.findall(r"[A-Za-z0-9_]+", text or "")
    out = set()
    for w in words:
        out |= split_ident(w)
    return out

def path_overlap(query_toks, path):
    path_toks = split_ident(path)
    if not path_toks:
        return 0.0
    return len(query_toks & path_toks) / len(path_toks)

def is_test(path):
    return "/test/" in path or "/tests/" in path

def analyze(records, name):
    test_overlaps, prod_overlaps = [], []
    for r in records:
        sid = r["stable_identity_sha256"]
        q = sid_to_query.get(sid)
        if q is None:
            continue
        qtoks = query_tokens(q)
        ov = path_overlap(qtoks, r["gt_path"])
        if is_test(r["gt_path"]):
            test_overlaps.append(ov)
        else:
            prod_overlaps.append(ov)
    mt = sum(test_overlaps)/len(test_overlaps) if test_overlaps else float('nan')
    mp = sum(prod_overlaps)/len(prod_overlaps) if prod_overlaps else float('nan')
    print(f"{name}: mean path-token overlap  TEST files={mt:.4f} (n={len(test_overlaps)})  PRODUCTION files={mp:.4f} (n={len(prod_overlaps)})")
    return mt, mp

print("=== Lexical (path-token) overlap between bug report and GT file path ===")
analyze(DISP["displaced_gt_file_records"], "DISPLACED")
analyze(RECOV["newly_promoted_gt_file_records"], "PROMOTED")

# Also for the implied STABLE set, reuse displaced set to exclude
displaced_set = set((r["stable_identity_sha256"], r["gt_path"]) for r in DISP["displaced_gt_file_records"])
stable_records = []
for sid, files in sid_to_gt_top10.items():
    for f in files:
        if (sid, f) not in displaced_set:
            stable_records.append({"stable_identity_sha256": sid, "gt_path": f})
analyze(stable_records, "STABLE")

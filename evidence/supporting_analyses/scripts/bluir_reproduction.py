"""P0-B: Genuine BLUiR-style structured-field retrieval reproduction on the
apache/camel subset (N=1293) of BugSTAiR's exact N=7023 cohort, using real
Java source extracted from Bench4BL's own git-backed archive at the exact
same before-fix commit SHAs BugSTAiR used.

Structured fields (adapted from BLUiR's class/method/variable/comment split,
using classes/methods/constants/imports -- the fields BugSTAiR's own
LexicalJavaExtractor regex-based extractor supports; "constants" substitutes
for "variables" and "imports" substitutes for "comments", disclosed as an
honest adaptation, not a hidden deviation).

BM25 (Okapi, k1=1.2, b=0.75) computed independently per field over the query
tokens, then summed (equal weighting, BLUiR's own default combination rule)
to produce the final per-file score.
"""
import json, math, re, subprocess, tempfile, shutil, os, sys, time
from pathlib import Path
from collections import Counter, defaultdict
import os
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[3]
EXTERNAL = _P(os.environ.get("BUGSTAIR_RESEARCH_REPO", REPO_ROOT.parent / "bug-localization-main-final"))

GITDIR = os.environ.get("BUGSTAIR_CAMEL_GITDIR", "")  # .git directory of the archived Bench4BL Apache Camel history
RANKINGS_DIR = REPO_ROOT / "data" / "rankings"
OUT_DIR = Path(__file__).resolve().parents[1] / "data"
import tempfile
TMP_WORK = Path(os.environ.get("BUGSTAIR_WORKDIR", tempfile.gettempdir())) / "bugstair_bluir_work"

# --- field extraction (independent reimplementation, not importing BugSTAiR's code) ---
CLASS_RE = re.compile(r"\b(?:class|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)")
METHOD_RE = re.compile(
    r"\b(?:public|protected|private|static|final|synchronized|native|abstract|default|strictfp|\s)+"
    r"(?:[\w.<>,\[\]?]+\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)
CONST_RE = re.compile(r"\b(?:public|protected|private|static|final|\s)+(?:[\w.<>,\[\]]+\s+)?([A-Z][A-Z0-9_]{1,})\s*=")
IMPORT_RE = re.compile(r"\bimport\s+(?:static\s+)?([A-Za-z0-9_.]+)\s*;")
COMMENT_STRIP_RE = re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE | re.DOTALL)
STRING_STRIP_RE = re.compile(r'"(?:[^"\\]|\\.)*"')
CONTROL_KEYWORDS = {"if", "for", "while", "switch", "catch"}

def split_ident(name):
    # camelCase / snake_case / digit-letter boundary split, lowercase
    parts = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    parts = re.sub(r'[_\.]', ' ', parts)
    return [p.lower() for p in parts.split() if p]

def extract_fields(source):
    cleaned = STRING_STRIP_RE.sub('""', COMMENT_STRIP_RE.sub(' ', source))
    classes = CLASS_RE.findall(cleaned)
    methods = [m for m in METHOD_RE.findall(cleaned) if m not in CONTROL_KEYWORDS]
    consts = CONST_RE.findall(cleaned)
    imports = IMPORT_RE.findall(source)
    def toks(items):
        out = []
        for it in items:
            out.extend(split_ident(it))
        return out
    return {
        "classes": toks(classes),
        "methods": toks(methods),
        "constants": toks(consts),
        "imports": [t for imp in imports for t in split_ident(imp.split('.')[-1])],
    }

def tokenize_query(text):
    text = text or ""
    words = re.findall(r"[A-Za-z0-9_]+", text)
    out = []
    for w in words:
        out.extend(split_ident(w))
    return [w for w in out if len(w) > 1]

# --- BM25 (Okapi, standard params) ---
def bm25_scores(query_tokens, field_docs, k1=1.2, b=0.75):
    """field_docs: dict[file_id] -> list[tokens]. Returns dict[file_id] -> score."""
    N = len(field_docs)
    if N == 0:
        return {}
    avgdl = sum(len(d) for d in field_docs.values()) / N
    df = Counter()
    for d in field_docs.values():
        for t in set(d):
            df[t] += 1
    idf = {t: math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5)) for t in set(query_tokens)}
    scores = {}
    for fid, doc in field_docs.items():
        if not doc:
            scores[fid] = 0.0
            continue
        tf = Counter(doc)
        dl = len(doc)
        s = 0.0
        for t in query_tokens:
            if t not in tf:
                continue
            f = tf[t]
            s += idf.get(t, 0.0) * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
        scores[fid] = s
    return scores

def blur_rank(query_tokens, corpus_fields):
    """corpus_fields: dict[file_id] -> {field_name: tokens}. BLUiR = sum of per-field BM25."""
    field_names = ["classes", "methods", "constants", "imports"]
    per_field_docs = {fn: {fid: corpus_fields[fid].get(fn, []) for fid in corpus_fields} for fn in field_names}
    total = defaultdict(float)
    for fn in field_names:
        sc = bm25_scores(query_tokens, per_field_docs[fn])
        for fid, v in sc.items():
            total[fid] += v
    ranked = sorted(total.keys(), key=lambda f: -total[f])
    return ranked

# --- main pipeline ---
EXT_DATASET_PATH = str(EXTERNAL / "data" / "iqloc/author_repository/IQLoc/Dataset/Bench4BLExtended.json")

def load_camel_bugs():
    with open(RANKINGS_DIR / "bm25_records.jsonl") as f:
        recs = [json.loads(l) for l in f]
    camel = [r for r in recs if r["owner_repo"] == "apache/camel"]
    ext = json.load(open(EXT_DATASET_PATH))
    for r in camel:
        src = ext[r["old_author_record_index"]]
        r["_bug_title"] = src.get("bug_title", "") or ""
        r["_bug_description"] = src.get("bug_description", "") or ""
    return camel

def snapshot_resolvable(sha):
    r = subprocess.run(["git", "--git-dir", GITDIR, "cat-file", "-t", sha],
                        capture_output=True, text=True)
    return r.returncode == 0

def extract_snapshot(sha, workdir):
    dest = workdir / sha
    if dest.exists():
        return dest
    dest.mkdir(parents=True)
    tar_path = workdir / f"{sha}.tar"
    with open(tar_path, "wb") as f:
        subprocess.run(["git", "--git-dir", GITDIR, "archive", sha], stdout=f, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["tar", "-x", "-f", str(tar_path), "-C", str(dest)], check=True)
    tar_path.unlink()
    return dest

def trec_ap(ranked, gt):
    gt_u = list(dict.fromkeys(gt))
    rank_of = {f: i+1 for i, f in enumerate(ranked)}
    found = sorted(rank_of[g] for g in gt_u if g in rank_of)
    if not found: return 0.0
    return sum((i+1)/r for i, r in enumerate(found)) / len(gt_u)

def hit_at(ranked, gt, k):
    gt_s = set(gt)
    return 1 if any(f in gt_s for f in ranked[:k]) else 0

def mrr_c(ranked, gt):
    gt_s = set(gt)
    for i, f in enumerate(ranked, start=1):
        if f in gt_s: return 1.0/i
    return 0.0

def gtrecall_at(ranked, gt, k):
    gt_u = list(dict.fromkeys(gt))
    top = set(ranked[:k])
    return sum(1 for g in gt_u if g in top) / len(gt_u)

def resolve_gt_to_relative(gt_paths, java_files_relpaths):
    """BugSTAiR's resolved_gt_paths are repo-root-relative paths; match by suffix
    against the extracted snapshot's relative paths (git archive root == repo root,
    so this should be an exact match, but resolve defensively by suffix as fallback)."""
    relset = set(java_files_relpaths)
    out = []
    for g in gt_paths:
        if g in relset:
            out.append(g)
        else:
            cands = [r for r in java_files_relpaths if r.endswith(g) or g.endswith(r)]
            if len(cands) == 1:
                out.append(cands[0])
            else:
                out.append(g)  # will simply not match in ranking -> correctly counted as a miss
    return out

def main(limit_snapshots=None, out_suffix=""):
    camel = load_camel_bugs()
    print(f"Total camel bugs: {len(camel)}")
    by_sha = defaultdict(list)
    for r in camel:
        by_sha[r["snapshot_sha"]].append(r)
    shas = sorted(by_sha.keys())
    if limit_snapshots:
        shas = shas[:limit_snapshots]
    print(f"Distinct snapshots to process: {len(shas)} (of {len(by_sha)} total)")

    TMP_WORK.mkdir(parents=True, exist_ok=True)
    per_bug_results = []
    unresolvable_snapshots = []
    t0 = time.time()
    exact_gt_match_fail = 0
    for i, sha in enumerate(shas):
        bugs = by_sha[sha]
        if not snapshot_resolvable(sha):
            unresolvable_snapshots.append({"sha": sha, "n_bugs": len(bugs),
                                            "dataset_indices": [b["dataset_index"] for b in bugs]})
            print(f"[{i+1}/{len(shas)}] sha={sha[:10]} UNRESOLVABLE (not in extracted git history) -- {len(bugs)} bugs skipped")
            continue
        snap_dir = extract_snapshot(sha, TMP_WORK)
        java_files = list(snap_dir.rglob("*.java"))
        relpaths = [str(jf.relative_to(snap_dir)) for jf in java_files]
        corpus_fields = {}
        for jf, rel in zip(java_files, relpaths):
            try:
                text = jf.read_text(errors="ignore")
            except Exception:
                continue
            corpus_fields[rel] = extract_fields(text)

        for bug in bugs:
            gt_raw = bug["gt_provenance"]["resolved_gt_paths"]
            if not gt_raw:
                continue
            gt_resolved = resolve_gt_to_relative(gt_raw, relpaths)
            if not any(g in corpus_fields for g in gt_resolved):
                exact_gt_match_fail += 1
            query_text = (bug["_bug_title"] + " " + bug["_bug_description"])[:2000]
            q_tokens = tokenize_query(query_text)
            ranked = blur_rank(q_tokens, corpus_fields)
            per_bug_results.append({
                "dataset_index": bug["dataset_index"],
                "owner_repo": bug["owner_repo"],
                "snapshot_sha": sha,
                "n_candidates": len(ranked),
                "gt": gt_resolved,
                "hit_at_1": hit_at(ranked, gt_resolved, 1),
                "hit_at_5": hit_at(ranked, gt_resolved, 5),
                "hit_at_10": hit_at(ranked, gt_resolved, 10),
                "mrr": mrr_c(ranked, gt_resolved),
                "trec_ap": trec_ap(ranked, gt_resolved),
                "gtrecall_at_10": gtrecall_at(ranked, gt_resolved, 10),
                "top10": ranked[:10],
            })
        shutil.rmtree(snap_dir, ignore_errors=True)
        elapsed = time.time() - t0
        print(f"[{i+1}/{len(shas)}] sha={sha[:10]} bugs={len(bugs)} java_files={len(java_files)} elapsed={elapsed:.1f}s")

    print(f"\nTotal bugs evaluated: {len(per_bug_results)}")
    print(f"Unresolvable snapshots: {len(unresolvable_snapshots)} covering {sum(u['n_bugs'] for u in unresolvable_snapshots)} bugs")
    print(f"GT resolution failures (GT path not found in extracted snapshot at all): {exact_gt_match_fail}")
    with open(OUT_DIR / f"bluir_unresolvable_snapshots{out_suffix}.json", "w") as f:
        json.dump(unresolvable_snapshots, f, indent=2)
    if per_bug_results:
        n = len(per_bug_results)
        print(f"Hit@1={sum(r['hit_at_1'] for r in per_bug_results)/n:.4f}")
        print(f"Hit@5={sum(r['hit_at_5'] for r in per_bug_results)/n:.4f}")
        print(f"Hit@10={sum(r['hit_at_10'] for r in per_bug_results)/n:.4f}")
        print(f"MRR={sum(r['mrr'] for r in per_bug_results)/n:.4f}")
        print(f"TREC_MAP={sum(r['trec_ap'] for r in per_bug_results)/n:.4f}")
        print(f"GTRecall@10={sum(r['gtrecall_at_10'] for r in per_bug_results)/n:.4f}")

    out_path = OUT_DIR / f"bluir_per_bug_results{out_suffix}.json"
    with open(out_path, "w") as f:
        json.dump(per_bug_results, f)
    print(f"Saved to {out_path}")
    return per_bug_results

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--limit-snapshots", type=int, default=None)
    p.add_argument("--out-suffix", type=str, default="")
    args = p.parse_args()
    main(limit_snapshots=args.limit_snapshots, out_suffix=args.out_suffix)

# BugLocalization: artifacts for the study on LLM reranking in bug localization

This repository contains the data artifacts, analysis scripts, and numerical traceability materials for the study *Beyond First Hits: LLM Reranking, File Recovery, and Cost in Bug Localization*.

The study compares lexical (BM25), dense, hybrid, and semantically reranked (H+SR) retrieval on 7,023 Java bugs from the Bench4BL family.

## Contents

| Path | Description |
|---|---|
| `data/rankings/` | Per-bug rankings (to depth 200) of BM25, dense (Jina), and hybrid (RRF, k=60) retrieval, with resolved ground truth files. One JSON record per bug, gzip compressed. |
| `data/h_sr/` | Per-bug H+SR predictions (reranked top 100 of H), execution provenance, a per-instance comparison of H and H+SR, and summary metrics. |
| `evidence/raw_artifact_recomputation/` | Independent recomputation of all reported metrics and of the file transition, file type, and two file analyses from the raw rankings and predictions (documents, outputs in `data/`, scripts in `scripts/`). |
| `evidence/supporting_analyses/` | Cohort provenance, metric validation, internal and external (BLUiR-style) baselines, ablation, sensitivity analyses, and cost (documents, `data/`, `scripts/`). |
| `evidence/numerical_traceability.csv` | Traceability of the numbers in the paper to their sources. |
| `figures_src/` | Sources and scripts for the figures. |

## Reproducing the analyses

1. Decompress the data files in place: `gunzip -k data/rankings/*.gz data/h_sr/*.gz` (the uncompressed `.jsonl` files are ignored by git).
2. Run the scripts from anywhere. Inputs in `data/` and outputs next to each script are found with relative paths.
3. Some scripts need inputs that are not part of this repository: the IQLoc dataset file and the multi file displacement summaries (`lexical_overlap_mechanism.py`, `test_file_displacement_analysis.py`, `two_file_mechanism.py`, `bluir_reproduction.py`), and a git history of the archived Bench4BL Apache Camel snapshots (`bluir_reproduction.py`). Point the environment variable `BUGSTAIR_RESEARCH_REPO` to the research repository that holds them (default: `../bug-localization-main-final`), and `BUGSTAIR_CAMEL_GITDIR` to the `.git` directory of the Camel history.
4. The H+SR predictions were produced with Qwen/Qwen3-8B on MareNostrum 5. The pipeline source code is not part of this repository. Original LLM generation traces are not preserved for every bug (see Section 10 of the paper).

## Notes

- The benchmark data (Bench4BL and the IQLoc release) and the source code repositories of the studied projects are not included. They remain subject to their original licenses and distribution terms.

## License

The scripts and the artifacts generated for this study are released under the Apache License 2.0 (see `LICENSE`). Third party data keeps its original license.

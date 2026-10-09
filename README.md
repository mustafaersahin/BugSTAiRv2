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

## Notes

- Decompress the `.jsonl.gz` files before use (`gunzip -k`). The analysis scripts expect the uncompressed files in the layout of the original research repository; their input and output paths are absolute paths from the authors' machine and must be adjusted.
- The benchmark data (Bench4BL and the IQLoc release) and the source code repositories of the studied projects are not included. They remain subject to their original licenses and distribution terms.
- Original LLM generation traces are not preserved for every bug (see Section 10 of the paper).

## License

To be added.

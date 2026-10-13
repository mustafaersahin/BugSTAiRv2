# Selective reranking: decide per bug whether to apply SR

Question: can features known before reranking tell for which bugs SR should be applied?
No new model inference: uses the existing H and H+SR rankings of all 7,023 bugs.

## Design (fixed before looking at results)
- Features (17, all available before reranking): report length, stack trace present, number of CamelCase identifiers, number of candidate classes named in the report (top 100, top 10, top 1), agreement of BM25 and dense top 10, rank of H top 1 in B and D, number of repository files, RRF score of H top 1 / margin / tenth, share of test files in H top 10. See `build_features.py`.
- Target: per bug utility u = (RR of H+SR - RR of H) + (Complete@10 of H+SR - Complete@10 of H).
- Model: ridge regression (alpha 10) and gradient boosting (depth 3); no tuning.
- Evaluation: 5 folds grouped by repository (no repository is in both training and test); out-of-fold predictions.
- Policy: apply SR when the predicted utility is above 0 (no threshold tuning).

## Main result (ridge, 7,023 bugs)
| Policy | SR applied | Hit@10 | MRR | GTRecall@10 | Complete@10 |
|---|---|---|---|---|---|
| Always H | 0% | 0.7934 | 0.5538 | 0.6470 | 0.5199 |
| Always H+SR | 100% | 0.8035 | 0.5749 | 0.6434 | 0.5031 |
| Selective | 56.0% | 0.8153 | 0.5840 | 0.6648 | 0.5311 |
| Oracle (upper bound) | 29.5% | 0.8481 | 0.6070 | 0.7012 | 0.5777 |

Selective vs always H+SR (paired bootstrap, 95% CI): Hit@10 +0.0077 to +0.0161, MRR +0.0055 to +0.0125, GTRecall@10 +0.0174 to +0.0256, Complete@10 +0.0226 to +0.0336.
Gradient boosting gives a similar but slightly smaller gain (53% reranked; Hit@10 0.8109, MRR 0.5811, Complete@10 0.5294).

## Robustness
- 20 different fold assignments: all metrics vary by at most 0.0006.
- Utility weights 0.5, 1, 2 on the completeness term: conclusions unchanged (see `data/selective_reranking_robustness.json`).
- Excluding apache/camel (largest repository): policy beats both baselines on all four metrics.
- By number of relevant files: for one and two relevant files the policy beats both baselines in MRR and Complete@10 (two files: Complete@10 0.5498; H 0.5453, H+SR 0.5043, so the loss is removed). For three or more files Complete@10 is 0.1407 (H 0.1472, H+SR 0.1165): most but not all of the loss is removed.
- Random selection at the same share only moves along the line between H and H+SR (see curves in `data/selective_reranking_results.json`).

## Caveats
Correlation between predicted and true utility is modest (0.18); the oracle shows much headroom. Labels come from one reranker and one benchmark. Associations only; no causal claim about why a feature predicts benefit.

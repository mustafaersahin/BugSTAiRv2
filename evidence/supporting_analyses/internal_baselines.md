# Phase 6 — Internal Baselines Reconstruction (B / D / H / H+SR)

## Method

Full metric set (Hit@1/5/10, MRR, TREC MAP, Package MAP, GTRecall@5/10, Complete@5/10) independently computed from raw per-bug rankings for BM25 (B), Jina/dense (D), and Hybrid H, both aggregate and per-project (`owner_repo`). Script: `q1_strengthening/scripts/internal_baselines_full.py`; full machine-readable output: `q1_strengthening/data/internal_baselines_full.json`. **H+SR is not independently reconstructed here** — no raw per-bug predictions for the full N=7,023 cohort were recoverable (Phase 3); H+SR's aggregate-only numbers (from the frozen, hash-verified `BUGSTAIR_V2_FINAL_RESULTS.json`) are carried forward for comparison but cannot be broken out per-project in this audit.

## Aggregate results, all four systems (Hit@K/MRR/MAP independently recomputed for B/D/H; H+SR carried from frozen aggregate)

| Method | Hit@1 | Hit@5 | Hit@10 | MRR | TREC MAP | Package MAP | GTRecall@5 | GTRecall@10 | Complete@5 | Complete@10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **B (BM25)** | 0.2821 | 0.5392 | 0.6484 | 0.4028 | 0.3242 | 0.3349 | **0.3979** | **0.5047** | **0.2910** | **0.3901** |
| **D (Jina)** | 0.3957 | 0.6692 | 0.7548 | 0.5195 | 0.4182 | 0.4296 | **0.5009** | **0.6029** | **0.3722** | **0.4723** |
| **H (Hybrid)** | 0.4304 | 0.7045 | 0.7934 | 0.5538 | 0.4538 | 0.4646 | **0.5414** | **0.6470** | **0.4128** | **0.5199** |
| **H+SR** (frozen aggregate, not independently recomputed) | 0.4546 | 0.7216 | 0.8035 | 0.5749 | 0.4623 | 0.4825 | *not available* | *not available* | *not available* | *not available* |

**Bolded columns are new** — GTRecall@5/10 and Complete@5/10 were not previously reported for B/D/H individually in the prior manuscript (only H vs. H+SR on the `\|GT\|≥2` stratum was reported). These confirm the same monotonic-improvement pattern already established for Hit@K/MRR/MAP extends to the completeness metrics too, **for the three systems that don't rerank**: Complete@10 rises from 0.390 (BM25) → 0.472 (Jina) → 0.520 (Hybrid) — retrieval quality improvements straightforwardly improve complete multi-file recovery when no reranking is involved. This is an important baseline for Phase 8/9: it establishes that the Complete@10 *decline* seen when H+SR is added (0.520 → the already-known lower H+SR value on the `\|GT\|≥2` stratum) is specific to the reranking step, not a general property of "better retrieval" — better retrieval alone (B→D→H) only ever *helps* Complete@10 in this data.

## Per-project results — a genuinely new contribution of this Q1 strengthening pass

Full 41-project breakdown saved in `internal_baselines_full.json`. Top 10 by bug count, Hybrid H shown (B and D show the same qualitative pattern, smaller in magnitude):

| Project | N | Hit@10 | MRR | TREC MAP | Complete@10 |
|---|---|---|---|---|---|
| apache/camel | 1,293 | 0.7486 | 0.5015 | 0.4028 | 0.4741 |
| wildfly/wildfly | 783 | 0.6884 | 0.4277 | 0.3374 | 0.4163 |
| spring-projects/spring-security | 609 | 0.8506 | 0.6215 | 0.5284 | 0.6108 |
| apache/hbase | 540 | 0.8204 | 0.5845 | 0.4834 | 0.5574 |
| apache/hive | 512 | 0.6367 | 0.3878 | 0.3068 | 0.3984 |
| wildfly/wildfly-core | 433 | 0.7298 | 0.4887 | 0.3867 | 0.4203 |
| spring-projects/spring-roo | 408 | 0.7426 | 0.4842 | 0.4192 | 0.5515 |
| spring-projects/spring-batch | 310 | 0.8645 | 0.6174 | 0.5042 | 0.5516 |
| spring-projects/spring-data-mongodb | 282 | 0.8404 | 0.5813 | 0.4367 | 0.4610 |
| spring-projects/spring-data-commons | 167 | 0.9341 | 0.7015 | 0.5832 | 0.6407 |

**This directly resolves the micro-vs-macro-averaging gap flagged as an open Threats-to-Validity item in the original Stage F manuscript, with real numbers rather than a generic caveat.** The spread is large and systematic: Hit@10 ranges from 0.637 (`apache/hive`) to 0.934 (`spring-projects/spring-data-commons`) — nearly a 30-point absolute range across projects, all within the same single micro-averaged N=7,023 number. A macro-average (mean of per-project means, unweighted by project size) would materially differ from the reported micro-average, since large projects (`apache/camel`, `wildfly/wildfly`) sit below the median project's performance while several smaller projects sit well above it. Computing this macro-average is a cheap, high-value robustness check that should be added to the manuscript's Results section — not yet done in this pass (flagged as a fast P1 follow-up, trivial from the already-saved `internal_baselines_full.json`).

## What this phase could not do, and why (honest limitation, not silently dropped)

H+SR's per-project breakdown, and therefore a per-project comparison of the reranking effect, cannot be constructed by this audit — it would require either the raw N=7,023 H+SR predictions (confirmed absent, Phase 3) or rerunning the Qwen3-8B reranker over the existing frozen Hybrid H candidates for all 7,023 bugs, which is a **substantial GPU compute operation** and therefore an explicit stop-condition under this phase's operating instructions (condition 3). This is flagged for a P0/P1 decision at the Phase 19 gate rather than attempted.

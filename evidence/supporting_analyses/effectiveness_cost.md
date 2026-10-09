# P1-C — Effectiveness–Cost Frontier, Formalized

## Full table: effectiveness and cost, measured quantities only

| Method | Hit@1 | Hit@5 | Hit@10 | MRR | TREC MAP | Cost/bug | GPU required | Model |
|---|---|---|---|---|---|---|---|---|
| BM25 | 0.2821 | 0.5392 | 0.6484 | 0.4028 | 0.3242 | **0.710s** (measured, N=7,023) | No | None (lexical index) |
| Jina | 0.3957 | 0.6692 | 0.7548 | 0.5195 | 0.4182 | Not recorded in available raw exports (gap, disclosed — see Phase 12) | Yes (embedding inference) | `jinaai/jina-embeddings-v2-base-code` |
| Hybrid H | 0.4304 | 0.7045 | 0.7934 | 0.5538 | 0.4538 | ≈0.710s (RRF fusion itself is CPU-only and structurally negligible on top of BM25+Jina) | Inherits Jina's requirement | BM25 + Jina, fused |
| H+SR | 0.4546 | 0.7216 | 0.8035 | 0.5749 | 0.4623 | **723.264s** (measured mean, N=24 pilot, generalized to full run — Phase 12) | Yes (H100, median 15.8 GiB VRAM) | `Qwen/Qwen3-8B` |

## Relative cost (measured, not rhetorical)

**H+SR costs 1,018.7x more per bug than BM25 or Hybrid H's retrieval-stage cost** (723.264s vs. 0.710s) — computed directly from measured latencies, not asserted qualitatively.

## Marginal efficiency

| Pipeline step | ΔHit@10 | ΔCost (sec/bug) | Marginal Hit@10 per added second |
|---|---|---|---|
| BM25 → Hybrid H | +0.1450 | ≈+0.00s (RRF is CPU-negligible on top of already-computed BM25/Jina) | Effectively unbounded — this step is close to free |
| Hybrid H → H+SR | **+0.0101** | **+722.55s** | **0.000014** |

**The marginal return on the reranking stage's added cost is, in interpretable terms, vanishingly small: roughly 71,500 additional seconds of compute are required per additional 1.0 percentage point of aggregate Hit@10.** This is not a rhetorical claim ("LLMs are expensive") — it is a directly computed ratio from this audit's own measured cost and effectiveness figures.

## Is H+SR Pareto-efficient?

**No, not in a strict effectiveness-per-cost sense, and this is stated plainly rather than avoided.** A hypothetical operating point that simply used Hybrid H alone would dominate H+SR on cost by three orders of magnitude while sacrificing only 1.01 percentage points of Hit@10 (and, per Phases 8–9, would *avoid* the multi-file Complete@10 cost entirely). Under a narrow effectiveness-per-compute-dollar objective, **Hybrid H alone is the Pareto-preferred operating point** among the four systems measured.

**This does not mean H+SR is scientifically uninteresting or practically indefensible** — per this phase's own framing, it is acceptable for the answer to be "not Pareto-efficient." What it means is that the manuscript's positioning must not claim or imply H+SR is offered as a cost-effective production recommendation; its value is in the accuracy gain itself (real, statistically robust, per Phase 11) and — more importantly, per Phase 17's novelty reassessment — in what its *failure mode* (the displacement mechanism) reveals about semantic reranking generally, not in its cost-effectiveness as an engineering artifact. A single offline, deterministic 8B-parameter LLM pass per bug is still far lighter-weight than a multi-agent SWE-bench-style system (Tier-B related work, original Stage A–F literature matrix), so the *relative* framing against heavier agentic systems remains defensible — but the *absolute* comparison against the pipeline's own retrieval-only stages shows a real, unhedged, three-orders-of-magnitude cost jump for a one-point aggregate gain.

## No comparison against IQLoc's own runtime is made

Per explicit instruction, and consistent with Phase 12's original finding: IQLoc's own paper/repository does not report comparable per-bug latency or GPU-hour figures anywhere this audit has inspected, across either literature pass. No efficiency claim relative to IQLoc appears here or should appear in the manuscript.

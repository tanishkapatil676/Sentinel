# Sentinel — Submission Concurrency Analysis

**Experiment:** 10 jobs at submission concurrency 2 versus 5, with one registered RQ worker.

## Results

| Metric | Concurrency 2 | Concurrency 5 |
|---|---:|---:|
| Jobs completed | 10.00 | 10.00 |
| Failed jobs | 0.00 | 0.00 |
| Timed out jobs | 0.00 | 0.00 |
| Errors | 0.00 | 0.00 |
| Throughput | 0.69 jobs/sec | 0.62 jobs/sec |
| API submission p50 | 144.42 ms | 268.18 ms |
| API submission p95 | 321.38 ms | 355.01 ms |
| End-to-end p50 | 2722.89 ms | 7660.91 ms |
| End-to-end p95 | 3655.07 ms | 9948.12 ms |

## Raw Evidence

- Concurrency 2: `artifacts/benchmarks/submission_concurrency_c2.json` (source: `benchmark_results_1793075044.json`)
- Concurrency 5: `artifacts/benchmarks/submission_concurrency_c5.json` (source: `benchmark_results_1793075061.json`)

## Interpretation and Limitations

Both configurations used the same requested job count and one registered RQ worker. The results describe these individual local runs; they do not establish a general performance trend or production capacity.

A single run per configuration is preliminary. Repeat each configuration several times under comparable conditions before drawing strong conclusions. This harness comparison does not by itself prove queue congestion, database connection contention, or queue-wait time unless those are separately measured.

Do not claim a throughput of approximately 0.70 jobs/sec for the 10-job comparison unless the recorded results support it.

# Sentinel — Worker Scaling Analysis

**Workload:** 10 jobs per run; submission concurrency 2; Redis RQ queue `sentinel-jobs`.

## Measured Results

| Metric | 1 worker | 2 workers |
|---|---:|---:|
| Jobs completed | 10.00 | 10.00 |
| Failed jobs | 0.00 | 0.00 |
| Timeouts | 0.00 | 0.00 |
| Errors | 0.00 | 0.00 |
| Throughput | 0.64 jobs/sec | 0.84 jobs/sec |
| API submission p50 | 139.29 ms | 121.08 ms |
| End-to-end p50 | 2951.51 ms | 1915.46 ms |

## Raw Evidence

- One worker: `artifacts/benchmarks/worker_scaling_1_worker.json` (source: `benchmark_results_1793075077.json`)
- Two workers: `artifacts/benchmarks/worker_scaling_2_worker.json` (source: `benchmark_results_1793075090.json`)

## Interpretation and Limitations

These are individual local runs. Throughput and end-to-end latency do not directly measure queue waiting time, so they cannot establish a 40% queue-wait reduction. Queue-wait timestamps must be instrumented and measured to verify that specific claim.

Repeat both configurations under comparable conditions before making scaling claims. Do not infer absence of data-integrity conflicts from successful completion counts alone; verify this with appropriate concurrency and database integrity tests.

# Benchmark Analyzer Validation

- Validation date: 2026-10-27T04:23:07+00:00
- Analyzer: `scripts/analyze_benchmark_results.py`
- Python syntax: PASS
- Successful benchmark analysis: PASS (5/5 jobs completed)
- Failed benchmark handling: PASS (50 errors, zero completed)
- Missing-file handling: PASS
- Malformed-JSON handling: PASS
- Temporary test-file cleanup: PASS

## Successful test results

- Jobs: 5
- Concurrency: 2
- Throughput: 0.69 jobs/sec
- API submission latency p50: 118.93 ms
- API submission latency p95: 156.95 ms
- End-to-end latency p50: 2875.51 ms
- End-to-end latency p95: 3006.12 ms

## Limitation

The successful run used only five jobs. These measurements are a smoke-test
baseline, not evidence of production-scale performance. The failed 50-job run
is diagnostic evidence only and must not be presented as a successful benchmark.

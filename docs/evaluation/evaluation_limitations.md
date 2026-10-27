# Sentinel — Evaluation Limitations

**Document:** `docs/evaluation/evaluation_limitations.md`

1. **Local Concurrency Constraints:** Local single-node execution introduces CPU scheduling jitter and database connection pool contention under higher load (e.g., 50+ concurrent requests).

2. **Polling Overhead:** End-to-end completion latency includes HTTP polling intervals (`--poll-interval`), which slightly inflate perceived completion time compared to push-based notification mechanisms.

## Current Benchmark Evidence

The verified five-job smoke test completed all five jobs with no recorded errors. Its measured throughput was 0.69 jobs/sec. These results are preliminary and do not establish behavior under higher concurrency.

A separate 50-job run at concurrency 10 recorded 50 errors and zero completed jobs. This failed run is diagnostic evidence, not a valid successful performance benchmark. Its errors should be investigated before drawing conclusions about system capacity.

## Interpretation

Benchmark results depend on the local execution environment, workload, database and queue configuration, and polling interval. Repeat tests under controlled conditions before making scalability or production-performance claims.

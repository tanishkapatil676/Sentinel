# Sentinel — Benchmark Harness Guide

**Document:** `docs/evaluation/benchmark_harness.md`

## 1. Overview

The Sentinel benchmark harness (`scripts/benchmark_sentinel.py`) is an asynchronous test client built with `httpx`. It submits jobs through the FastAPI application, polls job status, and records API submission and end-to-end completion latency.

## 2. Command Usage

Run against a running Sentinel API instance:

    python scripts/benchmark_sentinel.py --api-url http://localhost:8000 --jobs 10 --concurrency 2 --timeout 30.0 --poll-interval 0.5

Five-job smoke-test command used in Colab:

    python scripts/benchmark_sentinel.py --api-url http://127.0.0.1:8000 --jobs 5 --concurrency 2 --timeout 30 --poll-interval 0.5

Prerequisites:
- Sentinel API is running and reachable.
- Database is available and ready.
- Redis is available.
- An RQ worker is running.
- Commands are run from the repository root.

## 3. Verified Five-Job Smoke Test

- Jobs requested: 5
- Concurrency: 2
- Completed: 5
- Failed: 0
- Timed out: 0
- Errors: 0
- Throughput: 0.69 jobs/sec
- API submission latency p50: 118.93 ms
- API submission latency p95: 156.95 ms
- End-to-end latency p50: 2875.51 ms
- End-to-end latency p95: 3006.12 ms

These measurements apply only to this five-job run and are not production-scale performance claims.

## 4. Failed 50-Job Run

- Jobs requested: 50
- Concurrency: 10
- Completed: 0
- Failed: 0
- Timed out: 0
- Errors: 50
- Throughput: 0.00 jobs/sec

This is diagnostic evidence, not a successful performance benchmark. Investigate the recorded errors before repeating the test.

## 5. Results Analysis

Analyze the successful results file with:

    python scripts/analyze_benchmark_results.py benchmark_results_1792996384.json

The analyzer reports job outcomes, available throughput, and p50/p95 API submission and end-to-end latency for valid completed-job samples.

## 6. Measurement Interpretation

- API submission latency measures the time taken to submit a job request.
- End-to-end latency measures the time from submission until job completion as recorded by the harness.
- Throughput depends on the harness's measured run duration and completed jobs.
- Percentiles from five observations are preliminary and sensitive to individual jobs.
- Compare runs only when configuration and environment are recorded.
- Do not invent missing metrics or silently discard benchmark errors.

## 7. Validation Checklist

- [x] Benchmark harness ran for a five-job smoke test.
- [x] API health and readiness returned HTTP 200.
- [x] Redis connectivity was verified.
- [x] An RQ worker processed the smoke-test job.
- [x] Five jobs completed without recorded errors.
- [x] Analyzer processed the successful results.
- [x] Analyzer warned when zero jobs completed.
- [x] Missing-file and malformed-JSON handling were tested.
- [ ] Investigate and rerun the failed 50-job benchmark.
- [ ] Run a larger benchmark before making scalability claims.

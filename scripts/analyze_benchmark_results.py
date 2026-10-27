#!/usr/bin/env python3
"""
Analyze Sentinel benchmark JSON output and calculate latency statistics.
"""

import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


def percentile(values: list[float], percent: float) -> float:
    """Calculate a nearest-rank percentile, safely handling small samples."""
    if not values:
        raise ValueError("Cannot calculate a percentile from an empty sample.")
    if not 0 < percent <= 100:
        raise ValueError("Percentile must be greater than 0 and at most 100.")

    ordered = sorted(values)
    rank = math.ceil((percent / 100) * len(ordered))
    return ordered[max(0, rank - 1)]


def valid_numbers(results: list[dict[str, Any]], field: str) -> list[float]:
    """Return finite numeric values for a field from completed jobs."""
    values = []

    for result in results:
        if result.get("status") != "COMPLETED":
            continue

        value = result.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if math.isfinite(value) and value >= 0:
                values.append(float(value))

    return values


def analyze(filepath: str) -> int:
    path = Path(filepath)

    if not path.is_file():
        print(f"ERROR: Results file not found: {path}", file=sys.stderr)
        return 1

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not read valid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("ERROR: Results JSON must contain an object.", file=sys.stderr)
        return 1

    results = data.get("results", [])
    if not isinstance(results, list):
        print("ERROR: 'results' must be a JSON list.", file=sys.stderr)
        return 1

    results = [item for item in results if isinstance(item, dict)]

    completed = sum(r.get("status") == "COMPLETED" for r in results)
    failed = sum(r.get("status") == "FAILED" for r in results)
    timed_out = sum(r.get("status") == "TIMEOUT" for r in results)
    errors = sum(r.get("status") == "ERROR" for r in results)
    total = data.get("total_jobs", len(results))
    concurrency = data.get("concurrency", "unknown")
    throughput = data.get("throughput_jobs_per_sec")

    print(f"--- Benchmark Analysis: {path} ---")
    print(f"Total Jobs: {total}")
    print(f"Concurrency: {concurrency}")

    if isinstance(throughput, (int, float)) and not isinstance(throughput, bool) and math.isfinite(throughput):
        print(f"Throughput: {throughput:.2f} jobs/sec")
    else:
        print("Throughput: unavailable (missing or invalid value)")

    print(
        f"Completed: {completed} | Failed: {failed} | "
        f"Timeouts: {timed_out} | Errors: {errors}"
    )

    api_latencies = valid_numbers(results, "api_latency_ms")
    e2e_latencies = valid_numbers(results, "e2e_latency_ms")

    for title, values in (
        ("API Submission Latency (ms)", api_latencies),
        ("End-to-End Latency (ms)", e2e_latencies),
    ):
        print(f"\n{title}")
        print(f"  Valid completed-job samples: {len(values)}")

        if not values:
            print("  No valid completed-job latency samples.")
            continue

        print(f"  Median (p50): {statistics.median(values):.2f}")
        print(f"  p95 (nearest rank): {percentile(values, 95):.2f}")

    if completed == 0:
        print(
            "\nWARNING: No jobs completed. Do not interpret this run "
            "as a successful job-processing performance benchmark."
        )

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage: python scripts/analyze_benchmark_results.py <results.json>",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(analyze(sys.argv[1]))

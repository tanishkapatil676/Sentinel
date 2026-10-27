#!/usr/bin/env python3
"""
Sentinel Asynchronous Benchmark Harness
Measures API submission latency, end-to-end completion latency, and throughput.
"""

import asyncio
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx


async def submit_and_track_job(
    client: httpx.AsyncClient,
    api_url: str,
    job_payload: dict,
    timeout: float,
    poll_interval: float,
) -> dict:
    start_time = time.perf_counter()
    submission_timestamp = datetime.now(timezone.utc).isoformat()

    result = {
        "submission_timestamp": submission_timestamp,
        "job_id": None,
        "status": "ERROR",
        "api_latency_ms": 0.0,
        "e2e_latency_ms": 0.0,
        "error": None,
    }

    try:
        resp = await client.post(
            f"{api_url}/jobs", json=job_payload, timeout=10.0
        )
        result["api_latency_ms"] = (
            time.perf_counter() - start_time
        ) * 1000.0

        if resp.status_code not in (200, 201):
            result["error"] = f"HTTP {resp.status_code}: {resp.text}"
            return result

        data = resp.json()
        job_id = data.get("id")
        if not job_id:
            result["error"] = "Successful submission response did not contain 'id'."
            return result

        result["job_id"] = job_id

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    poll_start = time.perf_counter()

    while time.perf_counter() - poll_start < timeout:
        try:
            poll_resp = await client.get(
                f"{api_url}/jobs/{job_id}", timeout=5.0
            )

            if poll_resp.status_code == 200:
                job_data = poll_resp.json()
                status = job_data.get("status")

                if status in ("COMPLETED", "SUCCEEDED"):
                    result["status"] = "COMPLETED"
                    result["e2e_latency_ms"] = (
                        time.perf_counter() - start_time
                    ) * 1000.0
                    return result

                if status in ("FAILED", "CANCELLED"):
                    result["status"] = "FAILED"
                    result["e2e_latency_ms"] = (
                        time.perf_counter() - start_time
                    ) * 1000.0
                    result["error"] = f"Terminal job status: {status}"
                    return result

            elif poll_resp.status_code >= 400:
                result["error"] = (
                    f"Polling HTTP {poll_resp.status_code}: {poll_resp.text}"
                )

        except Exception as exc:
            result["error"] = f"Polling {type(exc).__name__}: {exc}"

        await asyncio.sleep(poll_interval)

    result["status"] = "TIMEOUT"
    return result


async def run_benchmark(
    api_url: str,
    total_jobs: int,
    concurrency: int,
    timeout: float,
    poll_interval: float,
):
    api_url = api_url.rstrip("/")
    print(
        f"Starting Sentinel Benchmark: {total_jobs} jobs, "
        f"concurrency={concurrency}, target={api_url}"
    )

    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_worker(client, payload):
        async with semaphore:
            return await submit_and_track_job(
                client, api_url, payload, timeout, poll_interval
            )

    job_payload = {
        "name": "benchmark-task",
        "payload": {"value": 42},
        "max_retries": 3,
    }

    async with httpx.AsyncClient() as client:
        tasks = [
            bounded_worker(client, job_payload)
            for _ in range(total_jobs)
        ]
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks)
        total_duration = time.perf_counter() - start_time

    successful = [r for r in results if r["status"] == "COMPLETED"]
    failed = [r for r in results if r["status"] == "FAILED"]
    timed_out = [r for r in results if r["status"] == "TIMEOUT"]
    errors = [r for r in results if r["status"] == "ERROR"]

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "api_url": api_url,
        "total_jobs": total_jobs,
        "concurrency": concurrency,
        "timeout_seconds": timeout,
        "poll_interval_seconds": poll_interval,
        "duration_seconds": total_duration,
        "throughput_jobs_per_sec": (
            len(successful) / total_duration if total_duration > 0 else 0
        ),
        "completed": len(successful),
        "failed": len(failed),
        "timed_out": len(timed_out),
        "errors": len(errors),
        "results": results,
    }

    output_filename = f"benchmark_results_{int(time.time())}.json"
    output_path = Path(__file__).resolve().parent.parent / output_filename
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nBenchmark Complete!")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Throughput: {summary['throughput_jobs_per_sec']:.2f} jobs/sec")
    print(
        f"Completed: {len(successful)} | Failed: {len(failed)} | "
        f"Timeouts: {len(timed_out)} | Errors: {len(errors)}"
    )
    print(f"Raw results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel Benchmark Harness"
    )
    parser.add_argument(
        "--api-url", default="http://localhost:8000",
        help="Sentinel API base URL"
    )
    parser.add_argument("--jobs", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    args = parser.parse_args()

    if args.jobs < 1 or args.concurrency < 1:
        parser.error("--jobs and --concurrency must be at least 1")
    if args.timeout <= 0 or args.poll_interval <= 0:
        parser.error("--timeout and --poll-interval must be positive")

    asyncio.run(
        run_benchmark(
            args.api_url,
            args.jobs,
            args.concurrency,
            args.timeout,
            args.poll_interval,
        )
    )


if __name__ == "__main__":
    main()

# Sentinel End-to-End Job Lifecycle Scenarios

## 1. Overview

This document outlines the end-to-end execution scenarios for the Sentinel asynchronous job processing platform, tracing the lifecycle from API submission to final result retrieval. Verification statuses must reflect tests that have actually passed against the relevant implementation.

## 2. Lifecycle Stages

1. **API Intake & Validation**: Requests are validated against Pydantic schemas and idempotency keys are fingerprinted. **Status: Requires verification.**
2. **Durable Registration**: Jobs are committed to PostgreSQL before queue publication. Confirm the actual initial state and transaction boundaries. **Status: Requires verification.**
3. **Queue Dispatch & Worker Claim**: RQ dispatches job IDs and the worker claims eligible jobs. Confirm the actual claim mechanism; do not assume `SELECT ... FOR UPDATE` is used. **Status: Requires verification.**
4. **Execution & State Transition**: The worker executes the task and persists transitions to `COMPLETED` or `FAILED`. **Status: Unit-tested paths exist; end-to-end verification required.**
5. **Result Retrieval**: `GET /jobs/{job_id}` should return the authoritative database state and persisted result. **Status: Requires API integration verification.**

## 3. Scenario Matrix

| Scenario | Expected Behaviour | Verification Status |
| --- | --- | --- |
| **Successful Completion** | Job transitions from an eligible initial state to `RUNNING`, then `COMPLETED`, with its result persisted. | **Requires end-to-end test confirmation** (`tests/integration/test_e2e_lifecycle.py`) |
| **Transient Failure & Retry** | Retryable failures increment `retry_count` and schedule retries using the configured backoff policy. | **Unit-test coverage reported** (`tests/unit/test_jobs_worker.py`); confirm current test results |
| **Idempotency Key Reuse** | Reusing a key with an identical payload returns the existing job; a different payload returns a conflict. | **Requires API test confirmation** |

## 4. Verification Evidence

Record the exact command, test result, database configuration, and whether Redis/RQ and the real API were exercised. A mocked unit test or a manually simulated state transition must not be described as a full end-to-end integration test.

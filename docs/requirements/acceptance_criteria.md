# Acceptance Criteria Specification

## Functional Requirements Acceptance Criteria (FR-01 to FR-14)

### FR-01: Job Submission
* **Preconditions**: Client has a valid auth token.
* **Action**: `POST /api/v1/jobs` with valid task name and payload.
* **Expected Outcome**: HTTP 201 Created returned with unique UUID job ID and `QUEUED` status.
* **Pass/Rule**: Response contains valid UUID and status code is 201.
* **Verification**: API Integration Test (`pytest`).

### FR-02: Payload & Task Validation
* **Preconditions**: Client authenticated.
* **Action**: Submit request with unknown task name or malformed JSON body.
* **Expected Outcome**: HTTP 422 Unprocessable Entity returned with validation error details.
* **Pass/Rule**: Invalid requests never reach database insertion.
* **Verification**: Unit Test.

### FR-03: Durable Persistence
* **Preconditions**: DB online.
* **Action**: Submit valid job.
* **Expected Outcome**: Record durably committed in PostgreSQL `jobs` table before API responds.
* **Pass/Rule**: Direct SQL query confirms row exists.
* **Verification**: DB Integration Test.

### FR-04: Asynchronous Worker Execution
* **Preconditions**: Worker process active and connected to Redis.
* **Action**: Submit job; wait for worker poll.
* **Expected Outcome**: Worker picks up job and transitions state from `QUEUED` to `RUNNING`.
* **Pass/Rule**: Worker log shows task execution start.
* **Verification**: End-to-End Test.

### FR-05 & FR-06: Status & Result Retrieval
* **Preconditions**: Job submitted.
* **Action**: `GET /api/v1/jobs/{id}`.
* **Expected Outcome**: Returns HTTP 200 with accurate lifecycle status, results, or sanitized error summary.
* **Pass/Rule**: Response fields match expected state without leaking internal stack traces.
* **Verification**: API Test.

### FR-07 & FR-08: Retry & Attempt Recording
* **Preconditions**: Job throws transient exception.
* **Action**: Worker catches exception with retries remaining.
* **Expected Outcome**: Job transitions to `RETRY_WAIT`, attempt count increments, and attempt record logged.
* **Pass/Rule**: Attempt table records error summary and backoff timer.
* **Verification**: Fault Injection Test.

### FR-09: Authentication & Ownership
* **Preconditions**: Client A and Client B authenticated.
* **Action**: Client B attempts `GET /api/v1/jobs/{client_a_job_id}`.
* **Expected Outcome**: HTTP 404 Not Found (or 403 Forbidden).
* **Pass/Rule**: Client B cannot view Client A's data.
* **Verification**: Security Test.

### FR-10: Health Endpoints
* **Preconditions**: Services running.
* **Action**: `GET /health/live` and `GET /health/ready`.
* **Expected Outcome**: `/health/live` returns 200; `/health/ready` reflects DB/Redis connectivity.
* **Pass/Rule**: Correct HTTP status codes corresponding to dependency health.
* **Verification**: Health Check Test.

### FR-11 & FR-12: Reproducibility & Automated Tests
* **Preconditions**: Clean environment with Docker Compose.
* **Action**: Run `docker compose up` and `pytest`.
* **Expected Outcome**: Stack boots successfully and 100% of test suite passes.
* **Pass/Rule**: Zero test failures and clean container startup.
* **Verification**: CI Pipeline / Clean Env Test.

### FR-13: Idempotent Submission
* **Preconditions**: Client submits job with `Idempotency-Key: key-123`.
* **Action**: Re-submit identical request with same key.
* **Expected Outcome**: Second request returns cached response (`200 OK`) without creating duplicate job.
* **Pass/Rule**: `jobs` table count remains 1.
* **Verification**: API Idempotency Test.

### FR-14: Structured Logging
* **Preconditions**: Worker processing job.
* **Action**: Inspect stdout logs.
* **Expected Outcome**: JSON logs contain structured fields (`job_id`, `state`, `timestamp`, `worker_id`).
* **Pass/Rule**: Logs parse correctly as valid JSON.
* **Verification**: Log Inspection Test.

---

## Non-Functional Requirements Acceptance Criteria (NFR-01 to NFR-10)

* **NFR-01 (State Machine)**: State machine unit tests verify invalid transitions throw errors.
* **NFR-02 (Durable Acceptance)**: Database failure injection guarantees API returns 500 without creating phantom job records.
* **NFR-03 (Sanitized Errors)**: Security tests confirm production error responses hide internal stack traces.
* **NFR-04 (Secrets & Allowlist)**: Config tests ensure unknown task types are rejected and environment secrets remain protected.
* **NFR-05 (Modular Boundaries)**: Architecture code review confirms strict separation between API, service, and worker layers.
* **NFR-06 (Reproducibility)**: Clean environment boot verification confirms zero manual setup steps outside Docker Compose.
* **NFR-07 (Traceability)**: Log audit confirms `job_id` correlates across all log events and DB tables.
* **NFR-08 (Performance Metrics)**: Locust benchmark executes 100 concurrent users and records p50/p95/p99 latency (thresholds pending Phase 2 validation).
* **NFR-09 (Resource Bounds)**: Timeout and payload limit tests confirm oversized payloads (e.g., >10MB) are rejected with HTTP 413.
* **NFR-10 (Partial Failures)**: Failure-injection tests confirm worker crashes during execution correctly trigger retry or failure recovery without false success claims.

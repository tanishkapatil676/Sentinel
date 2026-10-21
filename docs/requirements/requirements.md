# Sentinel Requirements Specification

## 1. Functional Requirements (FR)

| Identifier | Priority | Requirement Statement | Expected Observable Behavior | Planned Phase / Milestone | Planned Implementation Component | Verification Method | Required Evidence | Dependencies / Unresolved Decisions | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Must | Accept valid job submissions and return a job identifier. | API responds with HTTP 201/200 and a valid UUID `id`. | Phase 2 / M2 | `src/sentinel/api/jobs.py` | API Test | HTTP Response Code & Body JSON | Schema validation rules. | `PLANNED` |
| **FR-02** | Must | Validate payloads and reject unsupported task types. | API returns HTTP 422 for invalid payloads or unknown tasks. | Phase 2 / M2 | `src/sentinel/api/schemas.py` | Unit Test | Test runner logs & HTTP 422 response | Task allowlist registry design. | `PLANNED` |
| **FR-03** | Must | Persist job state and relevant metadata in PostgreSQL. | Job row created in `jobs` table with correct attributes. | Phase 2 / M2 | `src/sentinel/db/models.py` | DB Integration Test | SQL query assertion on `jobs` table | DB connection pooling parameters. | `PLANNED` |
| **FR-04** | Must | Execute registered tasks asynchronously using a separate worker. | Background worker picks up job from Redis queue and executes task. | Phase 3 / M3 | `src/sentinel/workers/` | End-to-End Test | Worker execution logs & DB status change | Redis connection resilience under load. | `PLANNED` |
| **FR-05** | Must | Allow authorized clients to retrieve job status. | `GET /api/v1/jobs/{id}` returns accurate job lifecycle state. | Phase 2 / M2 | `src/sentinel/api/jobs.py` | API Test | HTTP 200 response with state payload | Auth token scoping. | `PLANNED` |
| **FR-06** | Must | Expose successful results and safe failure summaries. | Result JSON or sanitized error message populated upon completion. | Phase 2 / M2 | `src/sentinel/api/schemas.py` | Integration Test | Verified API response fields | Stack trace sanitization logic. | `PLANNED` |
| **FR-07** | Must | Apply bounded retries to eligible transient failures. | Retry count increments and job state transitions to `RETRY_WAIT`. | Phase 4 / M4 | `src/sentinel/services/retry.py` | Integration Test | Attempt log inspect & status transitions | Transient vs. permanent exception rules. | `PLANNED` |
| **FR-08** | Must | Record execution attempts and their outcomes. | `attempts` records created with timestamps and worker IDs. | Phase 3 / M3 | `src/sentinel/db/models.py` | DB Integration Test | Attempt table SQL query output | Retention policy for historical attempts. | `PLANNED` |
| **FR-09** | Must | Enforce authentication and job ownership. | Unauthenticated or unauthorized requests return HTTP 401/403. | Phase 4 / M4 | `src/sentinel/core/auth.py` | Security Test | HTTP 401/403 responses | Bearer token hashing format. | `PLANNED` |
| **FR-10** | Must | Provide liveness and dependency-aware readiness endpoints. | `/health` returns HTTP 200/503 depending on DB and Redis connectivity. | Phase 2 / M2 | `src/sentinel/api/health.py` | API Test | Endpoint JSON response showing DB/Redis health | Dependency timeout thresholds. | `PLANNED` |
| **FR-11** | Must | Provide reproducible local setup instructions. | Environment boots locally using Docker Compose without missing scripts. | Phase 5 / M5 | `docker-compose.yml` & `README.md` | Clean Environment Test | Docker container boot logs | Local port collision rules. | `PLANNED` |
| **FR-12** | Must | Verify core behavior through automated tests. | Pytest test suite executes and passes 100% of core unit/integration tests. | Phase 5 / M5 | `tests/` | Automated Test Suite | Pytest execution report | Test coverage target percentage. | `PLANNED` |
| **FR-13** | Must (Completed MVP) | Support idempotent job submission using scoped idempotency keys. | Re-submitting identical payload with same key returns cached job record. | Phase 4 / M4 | `src/sentinel/core/idempotency.py` | API Test | HTTP response header & body comparison | Idempotency key TTL. | `PLANNED` |
| **FR-14** | Must (Completed MVP) | Provide structured logs for relevant lifecycle events. | JSON-formatted log output contains `job_id`, `state`, and `timestamp`. | Phase 4 / M4 | `src/sentinel/observability/` | Log Inspection Test | Structlog stdout JSON parsing | Context key naming conventions. | `PLANNED` |
| **FR-15** | Should | Support reproducible performance and reliability experiments. | Locust benchmark executes and reports p50/p95/p99 latency and throughput. | Phase 6 / M6 | `benchmarks/locustfile.py` | Load Test | Locust CSV report & latency graphs | Target target RPS baseline. | `PLANNED` |
| **FR-16** | Could | Provide an optional web dashboard. | Web interface visualizes worker queues and active jobs. | Post-MVP | `src/sentinel/web/` | Manual Inspection | UI rendering in browser | Choice of framework (FastAPI templates/React). | `PLANNED` |

*Note on Priorities*: FR-13 and FR-14 follow the first working vertical slice. FR-15 must precede measured performance claims. FR-16 must not delay backend correctness.

---

## 2. Non-Functional Requirements (NFR)

| Identifier | Requirement Statement | Verification Method | Planned Phase / Component | Current Status |
| :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | Job state transitions follow documented rules without skipping states. | State-machine unit tests | Phase 2 / `docs/state_machine.md` | `PLANNED` |
| **NFR-02** | The API does not claim durable acceptance before required persistence succeeds. | Database failure injection tests | Phase 2 / `src/sentinel/api/jobs.py` | `PLANNED` |
| **NFR-03** | Errors are clear, documented, and appropriately sanitized (no raw traces in production). | API and security contract tests | Phase 4 / `src/sentinel/core/errors.py` | `PLANNED` |
| **NFR-04** | Secrets are protected, task types are allowlisted, and job ownership is enforced. | Security & configuration tests | Phase 4 / `src/sentinel/core/auth.py` | `PLANNED` |
| **NFR-05** | API, business logic, persistence, queue integration, and workers have clear boundaries. | Architecture and code review | Phase 1–6 / System Architecture | `PLANNED` |
| **NFR-06** | Setup, configuration, migrations, and tests are reproducible across fresh environments. | Clean-environment verification | Phase 5 / `docker-compose.yml` | `PLANNED` |
| **NFR-07** | Relevant execution events are traceable via `job_id` across logs and DB records. | Log and attempt-record inspection | Phase 4 / `src/sentinel/observability/` | `PLANNED` |
| **NFR-08** | Performance and reliability claims are supported by measured evidence. | Reproducible load experiments | Phase 6 / `benchmarks/` | `PLANNED` |
| **NFR-09** | Resource usage and execution duration are appropriately bounded by timeouts and payload limits. | Timeout, payload-limit, and worker tests | Phase 4 / `src/sentinel/workers/` | `PLANNED` |
| **NFR-10** | The application handles partial failures without falsely reporting success. | Failure-injection tests | Phase 4 / System Fault Injection | `PLANNED` |

---

## 3. Job Lifecycle & State Machine Specification

### Provisional Job States
* **`QUEUED`**: The job has been durably committed to PostgreSQL and dispatched to the Redis broker queue.
* **`RUNNING`**: A worker has acquired the job, claimed a worker lease, and initiated execution.
* **`RETRY_WAIT`**: The job encountered a transient error and is waiting for exponential backoff duration before re-dispatch.
* **`SUCCEEDED`**: Terminal State. The task finished without error and final results are persisted.
* **`FAILED`**: Terminal State. The task encountered a permanent error or exhausted all retry attempts.

### State Transition Matrix
| Current State | Trigger / Event | Conditions | Next State | Persistence | Retry Eligible? | Recovery Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *None* | API Job Post | Payload valid & DB write succeeds | `QUEUED` | Job record inserted | N/A | Abort request if DB write fails |
| `QUEUED` | Worker Pick-up | Worker acquires lock/lease | `RUNNING` | `started_at` updated | No | Re-queue if worker crashes before heartbeat |
| `RUNNING` | Task Finish | Logic succeeds | `SUCCEEDED` | Result written | No | None (Terminal) |
| `RUNNING` | Transient Error | Retries remaining | `RETRY_WAIT` | `attempt_count` + 1 | Yes | Schedule backoff timer in Redis |
| `RETRY_WAIT` | Backoff Elapses | Timer finished | `QUEUED` | Re-queued status | Yes | Re-push payload to active queue |
| `RUNNING` | Permanent Failure | Exception non-transient | `FAILED` | Error summary saved | No | None (Terminal) |
| `RUNNING` | Retries Exhausted | `attempt_count` >= `max_retries` | `FAILED` | Terminal error logged | No | None (Terminal) |
| `RUNNING` | Worker Crash | Lease/heartbeat expires | `QUEUED` | Reset execution state | Yes | Interrupted job worker reclaims task |

---

## 4. Retry Policy & Duplicate Execution Semantics

### Failure Classification
* **Transient Failures**: External API timeouts, temporary network blips, database lock timeouts. Eligible for retries.
* **Permanent Failures**: Schema mismatch, division by zero, invalid job payloads, unknown task type. Immediate transition to `FAILED`.

### Max Retries & Backoff
* **Default Attempts**: Initial execution counts as Attempt 1. `max_retries = 3` allows up to 2 retry attempts.
* **Backoff Strategy**: Exponential backoff with jitter ($T = \text{base} \times 2^{\text{attempt}} + \text{jitter}$).

### Distinction of Lifecycle Boundaries
1. *Request Accepted*: Validation passes.
2. *Durable Record Committed*: PostgreSQL `INSERT` succeeds. (Durable Acceptance Boundary).
3. *Work Dispatched*: Redis `LPUSH` completes.
4. *Worker Begins*: Worker lease set.
5. *Task Finishes*: Computation complete.
6. *Outcome Persisted*: DB updated to `SUCCEEDED`/`FAILED`.

### Interrupted Job Recovery & Side Effects
* **Worker Crash Handling**: Workers periodically update a lease heartbeat in Redis. If a lease expires, an operator reconciliation task transitions stalled `RUNNING` jobs back to `QUEUED`.
* **Idempotency of Tasks**: At-least-once queue delivery implies tasks may run more than once. External side effects (e.g., payment charges, email dispatches) MUST implement external idempotency keys or reconciliation safeguards.


---

## 5. REST API Contract & Security Specification

All API endpoints are built with FastAPI, using JSON payloads and returning standardized response/error structures.

### Required Endpoints Summary
1. **`POST /api/v1/jobs`**: Submit a new background task.
2. **`GET /api/v1/jobs/{job_id}`**: Retrieve status, metadata, results, and safe failure summary.
3. **`GET /api/v1/jobs`**: List jobs with bounded pagination, ordering, and client ownership filtering.
4. **`POST /api/v1/jobs/{job_id}/retry`**: Manually trigger retry for an eligible failed or retry-waiting job.
5. **`GET /health/live`**: Liveness probe (process running).
6. **`GET /health/ready`**: Dependency-aware readiness probe (PostgreSQL and Redis connectivity).

---

### Endpoint Detailed Contracts

#### 1. `POST /api/v1/jobs` (Submit Job)
* **Purpose**: Accept a supported task type and payload, validate request, enforce idempotency, and durably commit job record.
* **Authentication**: Required (`Authorization: Bearer <token>`).
* **Headers**: `Idempotency-Key` (Optional string, scoped per client).
* **Request Schema**:
  ```json
  {
    "task_name": "process_data_batch",
    "payload": { "batch_id": "b_12345", "source": "s3://bucket/data.csv" },
    "max_retries": 3
  }

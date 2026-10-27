# Sentinel — Reliability and Fault-Injection Evaluation

## 1. Purpose

This report evaluates the reliability mechanisms visible in the current Sentinel source code and the supplied tests. It distinguishes implemented mechanisms from directly tested behavior and scenarios that still require fault-injection evidence.

## 2. Evidence reviewed

Source files reviewed:
- `src/sentinel/tasks/jobs.py`
- `src/sentinel/models/job.py`
- `src/sentinel/api/jobs.py`
- `src/sentinel/queue.py`
- `src/sentinel/tasks/recovery.py`

Test files reviewed:
- `tests/unit/test_recovery.py`
- `tests/integration/test_job_lifecycle.py`
- `tests/unit/test_observability.py`

Earlier baseline: 22 tests passed. Latest full-suite run after adding `tests/unit/test_job_retries.py`: `python -m pytest -q` — 24 tests passed, exit code 0. The two new targeted retry tests also passed independently.

## 3. Scenario assessment

| ID | Scenario | Implementation evidence | Test evidence reviewed | Assessment |
|---|---|---|---|---|
| R1 | Transient failure and retry | `_execute_job_async()` increments `retry_count`, records the error, resets the status to `PENDING` when retries remain, and schedules a delayed RQ job using capped exponential backoff. | No supplied test forces a transient exception and verifies retry scheduling or subsequent success. | Implemented in source; targeted mocked unit test passed |
| R2 | Permanent failure | `PermanentJobError` is caught separately; the job is marked `FAILED` and the error is persisted. | No supplied test raises `PermanentJobError` and asserts the persisted terminal state. | Implemented in source; targeted mocked unit test passed |
| R3 | Retry exhaustion | Transient failures mark a job `FAILED` after the retry limit is exceeded. Stale recovery also marks exhausted jobs `FAILED`. | No supplied test verifies either exhaustion path. | Implemented in source; targeted mocked unit test passed |
| R4 | Worker interruption | A job left in `RUNNING` can be considered by the stale-recovery function once it exceeds the configured threshold. | No supplied test interrupts an actual RQ worker or verifies recovery following interruption. | Recovery mechanism exists; interruption scenario not verified |
| R5 | Stale-job recovery | `recover_stale_jobs()` selects stale `RUNNING` jobs with `with_for_update()`, increments the retry counter, and moves jobs to `PENDING` or `FAILED`. | `test_stale_job_recovery_requeues` and `test_healthy_job_not_reclaimed` cover stale recovery and protection of a recent job. | Partially verified by direct tests |
| R6 | Duplicate queue delivery | `_execute_job_async()` uses a conditional database update to claim only `PENDING` or `QUEUED` jobs. A job that cannot be claimed is skipped. | The supplied tests do not dispatch the same job concurrently or assert that processing happens only once. | Claim mechanism implemented; concurrent duplicate-delivery behavior not directly verified |
| R7 | Idempotent submission | `create_job()` accepts an `Idempotency-Key`, compares request fingerprints, returns the existing job for a matching key, and rejects a different request fingerprint with HTTP 409. | The supplied tests do not exercise repeated HTTP requests, concurrent submissions, or conflicting keys. The database uniqueness constraint and migration still need verification. | API mechanism implemented; end-to-end guarantee not verified |
| R8 | Database–queue dispatch consistency | The API commits the job before enqueueing it. On an enqueue exception, it attempts to mark the job `FAILED` and returns HTTP 503. Retry scheduling also commits before enqueueing. | No supplied test injects Redis failure between database commit and queue submission. No transactional outbox is shown in the reviewed source. | Failure handling exists; atomic dispatch consistency is not established |

## 4. State and execution safeguards

### Conditional worker claim

The worker attempts to update a job to `RUNNING` only if its current status is `PENDING` or `QUEUED`. If no row is returned, the worker skips execution.

This is a database-level claim safeguard. Concurrent execution behavior still requires a dedicated test against the actual database and worker entry point.

### Retry policy

For a transient exception:
- The retry counter is incremented.
- The error message is persisted.
- The job returns to `PENDING` while retries remain.
- The delay is calculated as `min(2 ** retry_count, 60)` seconds.
- The job is marked `FAILED` when the retry limit is exceeded.

The code schedules retry work after committing the database update. A queue outage at that point can leave the job unscheduled; the reviewed code does not establish durable retry dispatch.

### Stale recovery

The recovery function selects stale `RUNNING` jobs using a row lock. Jobs with retries remaining return to `PENDING`; jobs exceeding their retry limit become `FAILED`.

The recovery function does not itself enqueue recovered jobs in Redis. A separate dispatcher or recovery scheduling mechanism would be needed to establish automatic re-execution.

### Idempotent submission

The API computes a deterministic fingerprint of the request. Reuse of an existing key with the same fingerprint returns the previously recorded job; reuse with a different fingerprint returns HTTP 409.

Concurrent submissions and the database constraint must be tested before claiming a complete concurrency-safe idempotency guarantee.

## 5. Verified test evidence

The supplied tests directly establish the following behaviors when those tests pass:

- A stale `RUNNING` job can be reset to `PENDING`, with its retry counter incremented.
- A recent `RUNNING` job is not reclaimed by the stale-recovery function.
- Direct worker execution can persist a job as `COMPLETED` with a result and no error.
- The observability unit test checks successful completion fields and a completion log message.

The integration test explicitly does not exercise the HTTP API or real Redis dispatch.

## 6. Reliability claims not yet established

The reviewed evidence does not establish:
- Successful retry after a forced transient failure.
- Permanent-failure behavior through a dedicated test.
- Retry exhaustion through a dedicated test.
- Recovery after an actual worker process interruption.
- Concurrent duplicate delivery resulting in only one task execution.
- Concurrent idempotent submissions being handled safely.
- A transactional outbox or atomic PostgreSQL–Redis commit.
- Automatic Redis re-enqueueing of jobs reset to `PENDING` by stale recovery.
- Exactly-once task execution.

These should remain unverified until source review and scenario-specific tests provide evidence.

## 7. Recommended next tests

1. Inject a transient processor failure; verify the retry counter, status, error, and scheduled retry.
2. Inject `PermanentJobError`; verify persisted `FAILED` status and error details.
3. Force retry exhaustion and verify the terminal status.
4. Create an old `RUNNING` job at its retry limit and verify stale recovery marks it `FAILED`.
5. Execute two concurrent claims for the same job and verify only one obtains the claim.
6. Exercise the HTTP endpoint with matching and conflicting idempotency keys, including concurrent requests.
7. Make Redis enqueueing raise an exception and verify the API response and persisted database state.
8. Test the recovery-to-dispatch path so a reclaimed `PENDING` job is eventually enqueued.
9. Simulate worker interruption and verify recovery after the configured stale threshold.

## 8. Conclusion

Sentinel contains meaningful reliability mechanisms for conditional job claiming, retry accounting, permanent failures, stale-job recovery, structured logging, and idempotency-key handling.

The supplied tests cover selected recovery, lifecycle, and observability behaviors. The remaining failure modes and cross-system guarantees require targeted tests before they can be reported as verified.

No exactly-once guarantee or transactional outbox guarantee is claimed in this report.


## 9. Latest validation update

Latest observed full-suite command:
`python -m pytest -q`

Result: **24 tests passed, exit code 0**.

New test file: `tests/unit/test_job_retries.py`

- `test_transient_failure_schedules_retry`: passed. With mocked sessions and queue, verifies the retry counter increment, `PENDING` status, persisted error message, two-second first retry delay, and scheduled job arguments.
- `test_retry_exhaustion_marks_job_failed`: passed. With mocked sessions and queue, verifies `FAILED` status when `max_retries=0`, incremented retry count, persisted error message, and no further retry enqueue.

These are unit tests using mocks. They do not verify real Redis delivery, PostgreSQL integration, concurrent execution, or worker-process interruption. Retry exhaustion is now tested for the transient-failure path; stale-recovery exhaustion remains without a dedicated test.

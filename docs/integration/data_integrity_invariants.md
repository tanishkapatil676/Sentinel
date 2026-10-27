# Sentinel — Data Integrity Invariants

**Document:** `docs/integration/data_integrity_invariants.md`

**Purpose:** Define the data integrity guarantees Sentinel must preserve across database transactions, concurrent job execution, retries, and recovery.

## 1. Overview

This document specifies the critical data integrity invariants for Sentinel's asynchronous job-processing platform.

It covers idempotent job submission, worker execution, stale-job recovery, retry accounting, and result persistence.

Each invariant must be supported by implementation evidence and an appropriate automated test before it is marked **Verified**.

### Status convention

- **Required:** Intended system behavior is defined.
- **Implemented — requires verification:** Code exists, but sufficient test evidence is unavailable.
- **Verified:** Relevant automated tests have passed against the current implementation.

## 2. Data Integrity Invariants

### 2.1 Concurrent Idempotency Submissions

**Required behavior**

- The same idempotency key within its defined scope must not create multiple logical jobs.
- Repeated requests with the same key and equivalent request fingerprint should return the existing job or an equivalent response.
- Reusing a key with a different request fingerprint must produce a conflict response.
- Concurrent submissions must be protected by database-enforced uniqueness or an equivalent atomic mechanism.

**Verification required**

- Submit the same key concurrently and verify that only one logical job record exists.
- Reuse the same key with a different payload and verify the conflict response.
- Confirm that the uniqueness constraint matches the intended key scope.

**Status:** Requires verification.

### 2.2 Competing Worker Claims

**Required behavior**

- A job must not be claimed for execution by multiple workers through the same valid state transition.
- A claim must atomically verify that the job remains eligible for execution.
- A worker that fails to claim a job must not execute its task.

**Implementation note**

Sentinel's worker uses a conditional database update to restrict claims to eligible states. This differs from relying solely on `SELECT ... FOR UPDATE`.

**Verification required**

- Run competing claim attempts against the same eligible job.
- Verify that only one claim succeeds.
- Verify that an unsuccessful claimant does not execute the task.

**Status:** Requires concurrency-test evidence.

### 2.3 Worker Execution vs. Stale-Job Recovery

**Required behavior**

- Recovery must only consider jobs that remain in `RUNNING` state and exceed the configured staleness threshold.
- A job that has transitioned to another state must not be reclaimed based on an outdated observation.
- Concurrent recovery operations must not independently increment retry counts or schedule duplicate recovery attempts without appropriate safeguards.

**Implementation note**

The recovery implementation selects stale `RUNNING` jobs and uses `SELECT ... FOR UPDATE`. The worker uses a conditional state update when claiming jobs. These mechanisms must be tested together to establish the actual concurrency guarantees.

**Verification required**

- Verify that stale jobs are identified and transitioned according to retry policy.
- Verify that healthy `RUNNING` jobs remain unchanged.
- Test concurrent recovery calls and worker state transitions.
- Verify queue dispatch for recovered jobs. Changing a database state to `PENDING` alone does not prove the job has been placed back on the queue.

**Status:** Basic stale-state and healthy-job tests passed; concurrent recovery and queue-dispatch guarantees require further verification.

### 2.4 Terminal State Protection

**Required behavior**

- `COMPLETED`, `FAILED`, and `CANCELLED` jobs must not be reactivated by late queue messages or stale worker executions.
- State transitions must validate the job's current state before applying updates.
- A duplicate execution attempt must not overwrite a terminal result.

**Verification required**

- Attempt to claim a terminal job and verify that the claim fails.
- Deliver a duplicate or late task message and verify that terminal state and result remain unchanged.
- Test cancellation, worker completion, and recovery interactions.

**Status:** Requires verification.

### 2.5 Retry Counter Consistency

**Required behavior**

- Retry counts must follow the defined retry policy.
- Each qualifying retry or recovery attempt must update the counter consistently.
- Once the retry limit is exhausted, the job must not be scheduled for another automatic retry.
- Tests must establish whether `max_retries` means retries after the initial attempt and verify the boundary behavior.

**Verification required**

- Test the first retry.
- Test the final permitted retry.
- Test behavior when the retry limit is exhausted.
- Verify that concurrent recovery does not increment the counter multiple times for one recovery event.

**Status:** Partially exercised by recovery tests; retry-limit boundary and concurrency tests remain required.

### 2.6 Result Durability

**Required behavior**

- A successful job result must be persisted in the database before the job is reported as successfully completed.
- A later failed or duplicate execution must not overwrite an already committed successful result.
- Database transactions must preserve consistent job status, result, and error information.

**Verification required**

- Execute a successful job and retrieve its persisted result in a new database session.
- Simulate a later failure or duplicate execution and verify that the terminal result remains unchanged.
- Test rollback behavior when result persistence fails.

**Status:** Requires verification.

## 3. Evidence Register

| Invariant | Current evidence | Status |
|---|---|---|
| Stale job recovery | Recovery test checks that a stale job becomes `PENDING` and its retry count increments | Basic behavior verified |
| Healthy job protection | Recovery test checks that a recent `RUNNING` job remains unchanged | Basic behavior verified |
| Concurrent worker claims | Dedicated competing-claim test required | Requires verification |
| Idempotency uniqueness | Concurrent submission and fingerprint-conflict tests required | Requires verification |
| Terminal state protection | Late-message and terminal-result tests required | Requires verification |
| Retry-limit enforcement | Boundary tests required | Requires verification |
| Result durability | Persistence and duplicate-execution tests required | Requires verification |
| Recovery queue dispatch | Queue integration test required | Requires verification |

## 4. Acceptance Criteria

The data integrity requirements may be marked fully verified only when:

1. Database constraints and transaction boundaries match the documented invariants.
2. Automated tests exercise normal and competing execution paths.
3. Retry-limit and terminal-state boundaries are tested.
4. Recovery and queue dispatch are verified together.
5. Test results correspond to the current code revision and are reproducible.

## 5. Known Limitations

Passing isolated unit tests does not, by itself, establish production-level concurrency safety, exactly-once execution, or end-to-end queue reliability.

Redis-backed integration tests, database concurrency tests, and failure-injection tests are required before making those claims.

This document must be updated whenever the implementation or its verified behavior changes.

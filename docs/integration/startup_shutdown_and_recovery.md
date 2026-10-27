# Sentinel — Startup, Shutdown, and Diagnostics

**Document:** `docs/integration/startup_shutdown_and_recovery.md`

**Purpose:** Define the expected startup checks, graceful shutdown behavior, dependency-failure handling, recovery procedures, and diagnostic logging for Sentinel.

## 1. Startup and Initialization

### 1.1 Database Connectivity

**Required behavior**

- Initialize the SQLAlchemy database engine and session factory using the configured database URL.
- Verify database connectivity before reporting database readiness.
- Check migration status using Alembic during deployment or startup validation.
- Fail readiness checks when the database is unavailable.

**Diagnostic commands**

Run these from the Sentinel repository root in an environment where the database is reachable:

```bash
alembic current
alembic upgrade head
```

`alembic upgrade head` changes the database schema. Run it only in the intended environment after reviewing pending migrations and confirming that the database is backed up appropriately.

**Verification required**

- Test successful database connectivity.
- Test behavior when the database is unavailable.
- Verify migration status against the expected schema revision.

**Status:** Requires environment-specific verification.

### 1.2 Queue Availability

**Required behavior**

- Verify Redis connectivity before reporting worker queue readiness.
- Configure the Redis connection through environment settings.
- Handle connection failures without falsely reporting queue readiness.
- Log queue connectivity failures without exposing credentials.

**Verification required**

- Verify that Redis can be reached from the API and worker environments.
- Test Redis disconnection and reconnection behavior.
- Confirm that failed queue dispatches are observable and recoverable.

**Status:** Requires verification.

### 1.3 Readiness and Liveness

**Required behavior**

- Liveness indicates whether the process is alive and able to respond to health checks.
- Readiness indicates whether the service can safely perform its intended work.
- API readiness should reflect the dependencies required for API operations.
- Worker readiness should reflect the dependencies required for job execution and queue consumption.

A service must not report readiness merely because its process started.

**Verification required**

- Test readiness with dependencies available.
- Test readiness with PostgreSQL unavailable.
- Test worker readiness with Redis unavailable.
- Confirm that liveness and readiness are not incorrectly treated as equivalent.

**Status:** Requires verification.

## 2. Shutdown and Restart Behavior

### 2.1 Graceful Termination

**Required behavior**

- Handle supported termination signals, such as `SIGTERM`, according to the process runtime.
- Stop accepting new work when shutdown begins, where applicable.
- Allow active work to finish within the configured shutdown grace period or stop it safely.
- Close database sessions, Redis connections, and other managed resources cleanly.
- Avoid marking a job `COMPLETED` unless successful processing and result persistence have finished.

**Verification required**

- Test termination while a worker is idle.
- Test termination during active job execution.
- Verify the final database state after the process exits.
- Verify that interrupted work can be handled after restart.

**Status:** Requires verification.

### 2.2 Durable Persistence and Restart Recovery

**Required behavior**

- PostgreSQL is the durable source of truth for job records.
- A queued job must remain discoverable in the database even if a worker process exits.
- Jobs left in `RUNNING` beyond the configured stale threshold should be identified by recovery logic.
- Recovery must respect retry limits and terminal-state rules.
- Recovered jobs must be dispatched back to the queue before automatic re-execution can occur.

**Current implementation note**

The recovery function currently detects stale `RUNNING` jobs and can transition them to `PENDING`. The existing recovery tests passed for stale-job state recovery and healthy-job protection.

This does not yet establish complete recovery-to-Redis dispatch or automatic recovery after process restart.

**Verification required**

- Verify stale-job detection after a simulated worker interruption.
- Verify retry-limit exhaustion.
- Verify that recovered jobs are enqueued in Redis.
- Verify that restart recovery does not create duplicate or conflicting execution attempts.

**Status:** Basic recovery-state tests passed; queue integration and restart behavior require further verification.

## 3. Dependency Failure Scenarios

### 3.1 Database Unavailable

**Required behavior**

- Database connection failures must be handled without returning false readiness.
- Failures must be recorded in diagnostic logs.
- API requests requiring database access must return an appropriate controlled error.
- The application must not claim that a job was durably created when its database transaction failed.

**Verification required**

- Start the service with an unreachable database.
- Submit a request that requires database access.
- Verify the error response, logs, and readiness state.
- Confirm that no false-success response is returned.

**Status:** Requires verification.

### 3.2 Redis Interruption

**Required behavior**

- Redis connection failures must be observable.
- Queue submission failures must not be silently reported as successful dispatch.
- The system must preserve enough durable state to identify jobs that require reconciliation.
- Recovery or reconciliation must safely handle jobs whose database state and queue state diverge.

**Important limitation**

Database persistence and Redis enqueueing are separate operations unless an explicit atomic coordination mechanism is implemented. A successful database commit does not prove that a job was successfully enqueued.

**Verification required**

- Simulate Redis being unavailable during queue submission.
- Verify the API response and database state.
- Restore Redis and verify the documented recovery mechanism.
- Confirm that reconciliation does not cause unintended duplicate processing.

**Status:** Requires verification.

## 4. Integrated Diagnostics and Structured Logging

### 4.1 Structured Events

**Required behavior**

Where appropriate, logs should include:

- Timestamp and severity.
- Event name.
- Service or component name.
- Job identifier.
- Request or correlation identifier, when available.
- Retry count and job state for relevant recovery events.
- Exception details in protected internal logs when necessary.

Suggested event names include:

- `database_connection_failed`
- `redis_connection_failed`
- `job_dispatch_failed`
- `job_execution_started`
- `job_execution_completed`
- `job_execution_failed`
- `stale_job_detected`
- `stale_job_recovered_to_pending`
- `stale_job_exhausted_retries`
- `shutdown_started`
- `shutdown_completed`

Event names are recommendations; their presence in the code must be checked before claiming they are implemented.

### 4.2 Correlation Identifiers

**Required behavior**

- Assign or accept a validated request correlation identifier at API intake.
- Include it in relevant logs and propagate it through job dispatch and worker execution when supported by the job schema and queue contract.
- Keep job identifiers distinct from request correlation identifiers.

**Verification required**

- Submit a request with a correlation identifier.
- Verify that relevant API and worker logs contain the same identifier.
- Verify behavior when no identifier is supplied.

**Status:** Requires verification.

### 4.3 Error Sanitization and Sensitive Data

**Required behavior**

- Public API errors must not expose database credentials, Redis credentials, environment variables, internal stack traces, or sensitive payload contents.
- Internal diagnostic logs should contain only the information needed for debugging and operations.
- Avoid logging authentication tokens, passwords, or full request payloads by default.
- Return stable, controlled error messages to API clients.

**Verification required**

- Trigger representative database, Redis, and worker errors.
- Inspect public responses for sensitive information.
- Inspect logs to ensure payloads and credentials are not exposed.
- Confirm that unexpected exceptions do not leak stack traces to clients.

**Status:** Requires verification.

## 5. Verification Checklist

- [ ] Database connectivity and migration status verified.
- [ ] Redis connectivity verified.
- [ ] API and worker readiness behavior tested.
- [ ] Graceful shutdown tested during active execution.
- [ ] Restart recovery tested.
- [ ] Stale-job recovery and retry exhaustion tested.
- [ ] Recovery-to-Redis queue dispatch verified.
- [ ] Database and Redis failure scenarios tested.
- [ ] Correlation identifiers traced across components.
- [ ] Public error responses and logs checked for sensitive data.

## 6. Acceptance Criteria

Startup, shutdown, and diagnostics may be marked fully verified only when the relevant checks have passed against the current code revision and the target deployment environment.

Unit tests alone do not establish real Redis connectivity, container shutdown behavior, or complete end-to-end restart recovery.

Record test commands, outcomes, environment assumptions, and unresolved issues before marking a checklist item complete.

## 7. Known Limitations

This document defines required behavior and records the currently known recovery-test evidence. It does not claim that every startup check, readiness probe, shutdown handler, correlation mechanism, or failure-recovery path is already implemented.

Update this document as the implementation and verification evidence evolve.

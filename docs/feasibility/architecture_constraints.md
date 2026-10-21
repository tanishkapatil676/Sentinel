# Architecture Constraints

This document defines the architectural constraints that Phase 3 and future development of **Sentinel** must respect, based on Milestone 1 & 2 verification, PoC results, and design decisions.

## 1. Durable Job State
- **Constraint**: PostgreSQL serves as the sole authoritative durable job-state store.
- **Status**: Accepted.
- **Implications**: All state transitions (`PENDING`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`) must be persisted in PostgreSQL. Redis/RQ is strictly a transient message broker and task queue.

## 2. Queue Responsibilities
- **Constraint**: Redis and RQ are restricted to task dispatch, concurrency queuing, and worker notification.
- **Status**: Accepted.
- **Implications**: Job payloads and critical business states must not live exclusively in Redis. If Redis restarts or drops transient queues, PostgreSQL retains the authoritative state records.

## 3. Process Separation
- **Constraint**: Strict operational separation between the FastAPI API service and background RQ worker processes.
- **Status**: Accepted.
- **Implications**: API instances handle incoming HTTP requests and enqueue task IDs; worker instances poll Redis and execute backend workloads independently.

## 4. Job Lifecycle
- **Constraint**: Jobs follow a strictly defined lifecycle.
- **Status**: Accepted.
- **Permitted Transitions**: `PENDING` -> `QUEUED` -> `RUNNING` -> (`COMPLETED` | `FAILED` | `CANCELLED`).

## 5. Retry Policy
- **Constraint**: Automated retries must be bounded by attempt limits and exponential backoff.
- **Status**: Provisional.
- **Implications**: Unhandled exceptions in worker tasks trigger retry counting before moving to permanent `FAILED` status.

## 6. Idempotency
- **Constraint**: Client-scoped request idempotency and database uniqueness constraints prevent duplicate submissions.
- **Status**: Provisional.

## 7. Security
- **Constraint**: Future authentication, ownership enforcement, task allowlisting, and secure logging policies must be implemented.
- **Status**: Accepted.

## 8. Database / Queue Consistency
- **Constraint**: Reconciling out-of-sync state between PostgreSQL and Redis after worker crashes.
- **Status**: Provisional.

## 9. Interrupted Work
- **Constraint**: Detection and reconciliation of stale or abandoned jobs stuck in `RUNNING`.
- **Status**: Provisional.

## 10. External Side Effects
- **Constraint**: Idempotency and reconciliation requirements for jobs interacting with external APIs.
- **Status**: Deferred.

## 11. Resource Boundaries
- **Constraint**: Enforce payload size limits and execution timeouts.
- **Status**: Accepted.

## 12. Reproducibility
- **Constraint**: Deterministic environment setup, Alembic migrations, pytest test suite, and CI execution.
- **Status**: Accepted.

## 13. Observability
- **Constraint**: Lifecycle structured logging and audit trails.
- **Status**: Accepted.

## 14. Performance Claims
- **Constraint**: No numerical throughput or latency claims without reproducible measurement evidence.
- **Status**: Accepted.

## 15. Deferred Features
- **Constraint**: No Kubernetes, UI dashboards, multi-tenant quotas, priority queues, scheduled jobs, or distributed tracing without explicit justification.
- **Status**: Accepted.

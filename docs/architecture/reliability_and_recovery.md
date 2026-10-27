# Sentinel Reliability and Recovery Architecture

## 1. Consistency Strategy
Sentinel enforces **PostgreSQL as the durable job-state authority**. Because PostgreSQL and Redis do not share an atomic distributed transaction:
1. The job record is durably committed to PostgreSQL with status `QUEUED`.
2. The task is dispatched to Redis/RQ.
3. If queue publication fails after database commit, a recovery worker or manual retry endpoint detects the orphaned `QUEUED` job and re-triggers dispatch.

## 2. Retry Semantics & Backoff
- **Transient vs. Permanent**: Exceptions are classified upon failure. Connection timeouts, rate limits, and temporary resource unavailability trigger retries; validation errors and code faults trigger permanent failure.
- **Max Attempts**: Configurable per job type (default: 3 attempts).
- **Backoff**: Exponential backoff with jitter to prevent retry storms.

## 3. Worker Crash & Duplicate Execution
- If a worker crashes while a job is `RUNNING`, the job state in PostgreSQL remains `RUNNING`. A recovery mechanism identifies stale `RUNNING` jobs exceeding execution timeouts and transitions them to `FAILED` or re-queues them based on attempt limits.

# Sentinel Job Lifecycle Specification

## 1. Canonical States
Sentinel defines five canonical states for any job processed within the platform:
1. **QUEUED**: The job has been durably committed to PostgreSQL and successfully enqueued in Redis/RQ for worker execution.
2. **RUNNING**: An RQ worker has claimed the job and is actively executing the task handler.
3. **RETRY_WAIT**: The job encountered a transient failure and is waiting for the scheduled backoff interval before re-entering the queue.
4. **SUCCEEDED**: The job completed execution successfully, and the final output or result summary has been durably persisted to PostgreSQL.
5. **FAILED**: The job encountered a permanent failure or exhausted all permitted retry attempts.

## 2. State Transition Table
| Current State | Event / Action | Target State | Responsible Component | Database Update | Queue Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| *None* | Valid API Submission | `QUEUED` | API Server / Service | Insert Job (status=`QUEUED`) | Enqueue task in Redis/RQ |
| `QUEUED` | Worker Claims Job | `RUNNING` | RQ Worker | Update status=`RUNNING`, increment attempt | None |
| `RUNNING` | Task Completes Successfully | `SUCCEEDED` | RQ Worker | Update status=`SUCCEEDED`, store result | Acknowledge RQ message |
| `RUNNING` | Transient Exception / Failure | `RETRY_WAIT` or `QUEUED` | RQ Worker | Update status, record attempt error | Schedule retry or re-enqueue |
| `RUNNING` or `RETRY_WAIT` | Max Retries Exhausted | `FAILED` | RQ Worker | Update status=`FAILED`, record terminal error | Acknowledge RQ message |

## 3. Lifecycle Invariants
- **Terminal Finality**: A job in a terminal state (`SUCCEEDED` or `FAILED`) must never transition back to a non-terminal state (`QUEUED`, `RUNNING`, or `RETRY_WAIT`).
- **Attempt Tracking**: Every execution attempt must be logged in the attempt history table with start time, completion time, outcome, and error details.

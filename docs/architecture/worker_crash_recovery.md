# Sentinel Worker Crash Recovery & Stale Job Reclamation

> **Verification status:** Proposed behavior. Confirm the implementation and tests before describing these guarantees as implemented.

## 1. Overview

Sentinel's planned database-backed reconciliation scan, `recover_stale_jobs`, detects and recovers jobs abandoned by crashed or terminated workers. Verify that this function exists and is invoked by an operational process.

## 2. Recovery Rules

- **Nonterminal state:** `RUNNING`.
- **Stale threshold:** 15 minutes. Jobs active for less than 15 minutes should be protected from reclamation.
- **Attempt increment:** Reclaiming a stale job consumes one retry attempt.
- **Exhaustion:** After the retry policy is exhausted, mark the job `FAILED` with a crash-recovery error message.
- **Idempotency:** Repeated recovery scans must not repeatedly reclaim the same job without a new execution attempt.

## 3. Evidence Required

Before marking this mechanism as implemented, verify:

1. A `recover_stale_jobs` function exists.
2. Staleness is determined using a persisted timestamp and a 15-minute cutoff.
3. Concurrent recovery scans cannot claim the same job.
4. Retry counts and terminal-state transitions follow the documented policy.
5. Reclaimed jobs are actually re-enqueued or otherwise scheduled for execution.
6. Tests cover stale jobs, healthy jobs, retry exhaustion, repeated scans, and concurrent recovery.

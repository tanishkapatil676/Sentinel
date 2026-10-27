# Sentinel Queue and Database Consistency

> **Verification status:** The consistency guarantees below must be validated against the current implementation and integration tests.

## 1. Consistency Model

The intended design is at-least-once job delivery with database state guards and idempotent handling where applicable. Do not claim end-to-end at-least-once delivery until queue publication, retries, and crash recovery are verified.

## 2. Failure Scenarios and Safeguards

- **Orphaned Running Jobs:** Recovery requires a stale-job scan based on a persisted timestamp, an atomic state transition, and a mechanism to reschedule or fail abandoned jobs. Confirm that these components exist and are invoked.
- **Duplicate Deliveries:** The worker's conditional claim should prevent a job from being claimed when its status is no longer claimable. Verify this with duplicate-delivery tests.
- **Concurrent Executions:** The current worker design uses a conditional database `UPDATE` with eligible statuses and `RETURNING` to claim a job atomically. This differs from pessimistic row locking using `SELECT ... FOR UPDATE`. Confirm the exact SQL and concurrency behavior in tests.

## 3. Verification Required

Before describing these guarantees as complete, verify:
1. Atomic job claiming against the real database.
2. Queue/database failure handling and recovery.
3. Retry scheduling and retry exhaustion.
4. Duplicate-delivery behavior.
5. Stale-worker recovery.
6. Integration tests using the actual queue and database.

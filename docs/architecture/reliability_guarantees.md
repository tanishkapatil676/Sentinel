# Sentinel Reliability Guarantees and Limitations

## 1. Implemented Transition-Safety Mechanisms

- **Exclusive Row Locking:** Utilizing SQLAlchemy `.with_for_update()` during job fetching ensures serializable access per job ID across concurrent workers.
- **Atomic State Guards:** Workers explicitly validate that `job.status == JobStatus.PENDING` before transitioning to `RUNNING`. Terminal states (`COMPLETED`, `FAILED`, `CANCELLED`) are strictly immutable.

## 2. Handling of Concurrency & Delivery Scenarios

- **Concurrent Worker Claims:** Prevented by database row locks. Only one transaction succeeds in acquiring the lock and transitioning the state.
- **Duplicate Queue Deliveries:** Handled via state guards. If a duplicate message arrives after a job has started or finished, the worker detects the non-pending state and exits safely.
- **Delayed Messages & Retries:** Scheduled retries check version/attempt counts and respect idempotency keys and state guards.

## 3. Database Safety vs. External-Side-Effect Safety

- **Database State:** Fully guaranteed atomic state transitions, transaction rollbacks, and isolation against race conditions.
- **External Side Effects:** **Not guaranteed exactly-once.** If a worker successfully communicates with an external API and crashes before committing its database transaction, a retry will re-execute the side effect. Downstream idempotency keys or API-level deduplication are required for non-database actions.

## 4. Known Limitations

- Network partitions between Redis and PostgreSQL may require manual or automated queue reconciliation (addressed in Sub-prompt 5).
- Exactly-once execution is not generally guaranteed across a database and an external queue without additional coordination. Sentinel should document its actual delivery semantics and use idempotency protections where applicable.

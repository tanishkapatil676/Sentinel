# Sentinel Test Architecture

## 1. Test Levels & Scope
1. **Unit Tests (`tests/unit/`)**: Verify Pydantic validation schemas, state transition logic, retry calculation algorithms, and error classification without external I/O.
2. **API Tests (`tests/unit/test_api.py`)**: Use `pytest` and `HTTPX` AsyncClient with SQLite/PostgreSQL mocks to verify status codes, JSON responses, authentication headers, and idempotency key behavior.
3. **Database Integration Tests**: Validate SQLAlchemy async session factories, Alembic migration scripts, and relational integrity constraints (`Job`, `JobAttempt`, `IdempotencyRecord`).
4. **Queue & Worker Integration Tests**: Verify task enqueuing, RQ worker dispatch, execution, and state persistence.
5. **Failure-Injection & Concurrency Tests**: Verify behavior under simulated Redis outages, database connection drops, concurrent duplicate job submissions, and worker crash scenarios.

## 2. Key Verification Scenarios
- **Durable Submission**: Verifies that a successful `POST /jobs` request creates a durable record in PostgreSQL before queue enqueuing.
- **Idempotency Key Collision**: Verifies that duplicate submissions with the same idempotency key return the original job record without duplicating entries.
- **Cross-User Access Denial**: Verifies that clients cannot access or modify jobs owned by another principal.
- **Retryable vs. Permanent Failures**: Verifies correct transition to `RETRY_WAIT` on transient errors and `FAILED` on permanent errors or retry exhaustion.

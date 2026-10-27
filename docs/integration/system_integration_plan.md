# Sentinel System Integration Plan

## 1. Revision & Status

- **Repository Revision**: Active working tree (`sentinel` repository).
- **Environment**: Python 3.13.16, PostgreSQL (SQLAlchemy AsyncIO + asyncpg), Redis (RQ queue).
- **Baseline Status**: Milestone 5 baseline and Milestone 6 reliability mechanisms require verification against the current implementation and test evidence.

## 2. Component Entry Points & Contracts

- **API Intake**: FastAPI application (`src/sentinel/main.py`), handling request validation, schema parsing, and idempotency fingerprinting. Verify each behaviour against the current implementation.
- **Persistence Layer**: PostgreSQL relational database managed via Alembic migrations (`alembic/versions/`), mapped by Async SQLAlchemy models (`src/sentinel/models/job.py`). Verify migration files and database schema alignment.
- **Queue & Worker Boundary**: Redis RQ queue publisher (`src/sentinel/queue.py`) and background worker entry point. Verify the actual worker file and invocation path in the repository.
- **Reliability & Recovery**: Concurrency control, stale-job reconciliation, and structured diagnostics. Verify the actual locking or conditional-update mechanism, the existence and configuration of `recover_stale_jobs`, and structured log fields before claiming these features are complete.

## 3. Verification Strategy

- **Static Checks**: Git status cleanliness, Alembic migration verification, and whitespace checks.
- **Unit & Database Tests**: Run the async pytest suite under `tests/unit/`; distinguish mocked unit tests from tests requiring a live database.
- **Integration & Lifecycle**: Run `tests/integration/test_e2e_lifecycle.py` against the intended services and verify persistence across separate sessions.
- **Concurrency & Recovery**: Verify race-condition and stale-job recovery tests, including `test_concurrency.py` and `test_recovery.py`, if these files exist. Confirm test collection and actual pass results before reporting success.

# Sentinel Component Design

## 1. API Route Handlers (`src/sentinel/api/`)
- **Responsibility**: Validate HTTP requests, parse Pydantic schemas, invoke application logic, and return appropriate status codes.
- **Inputs/Outputs**: HTTP request payloads $\rightarrow$ JSON responses.
- **Error Handling**: Catch database and validation exceptions, returning standardized error envelopes.

## 2. Application Services & Business Logic (`src/sentinel/tasks/`, `src/sentinel/queue.py`)
- **Responsibility**: Orchestrate job creation, idempotency validation, and RQ queue dispatch.
- **Dependencies**: Database session factory, Redis queue connection.

## 3. Database Persistence (`src/sentinel/database.py`, `src/sentinel/models/`)
- **Responsibility**: Manage async SQLAlchemy session lifecycles and define relational models (`Job`, `JobAttempt`).
- **Invariants**: Unique constraints on idempotency keys; foreign key integrity for attempt tracking.

## 4. Background Worker (`src/sentinel/tasks/jobs.py`)
- **Responsibility**: Claim jobs from Redis/RQ, execute task logic, handle retries, and persist terminal states to PostgreSQL.

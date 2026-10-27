# Idempotency Specification & Guarantees

## Key Scope & Format
- **Header**: `Idempotency-Key` (string provided by client).
- **Scope**: Global per deployment / authenticated client context.

## Fingerprinting Rules
- Requests are canonicalized by sorting dictionary keys (`job_type`, `payload`, `max_retries`) and hashing via SHA-256.
- Reusing an existing `Idempotency-Key` with a modified payload returns HTTP 409 Conflict.

## Concurrency Safety
- Backed by PostgreSQL primary key constraints on `idempotency_keys.idempotency_key`.
- Handles concurrent duplicate requests via transaction rollback and retry lookup without creating duplicate jobs.

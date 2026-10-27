# Sentinel Data Model Specification

## 1. Persistent Entities
Sentinel utilizes three core persistent entities stored in PostgreSQL:
1. **Job**: Stores job metadata, current lifecycle state, input payloads, result summaries, and retry counters.
2. **JobAttempt**: Records detailed execution metrics for each attempt (start/end timestamps, outcome, error summaries).
3. **IdempotencyRecord**: Stores client-supplied idempotency keys mapped to job IDs to prevent duplicate submissions.

## 2. Entity Schema Details

### `jobs` Table
- `id`: UUID (Primary Key, default: `uuid4`)
- `status`: String / Enum (`QUEUED`, `RUNNING`, `RETRY_WAIT`, `SUCCEEDED`, `FAILED`) - Not null
- `task_type`: String - Not null (Identifies the worker task handler)
- `payload`: JSONB - Not null (Input parameters for the task)
- `result`: JSONB - Nullable (Output summary upon successful completion)
- `error_message`: Text - Nullable (Safe error summary if failed)
- `attempt_count`: Integer - Default `0`
- `max_attempts`: Integer - Default `3`
- `idempotency_key`: String - Nullable, Indexed, Unique per client scope
- `created_at`: Timestamp with timezone - Default `now()`
- `updated_at`: Timestamp with timezone - Default `now()`

### `job_attempts` Table
- `id`: UUID (Primary Key)
- `job_id`: UUID (Foreign Key referencing `jobs.id`, ON DELETE CASCADE)
- `attempt_number`: Integer - Not null
- `status`: String - Not null
- `started_at`: Timestamp with timezone - Default `now()`
- `completed_at`: Timestamp with timezone - Nullable
- `error_details`: Text - Nullable

### `idempotency_records` Table
- `id`: UUID (Primary Key)
- `idempotency_key`: String - Unique, Not null, Indexed
- `job_id`: UUID (Foreign Key referencing `jobs.id`, ON DELETE CASCADE)
- `created_at`: Timestamp with timezone - Default `now()`

## 3. Idempotency Design
- **Scope & Uniqueness**: Uniqueness constraint on `idempotency_key` backed by PostgreSQL database unique index.
- **Duplicate Handling**: If a client submits a request with an existing idempotency key, the API checks the record, avoids creating a duplicate job, and returns the existing job record with status `200 OK` or `201 Created` as appropriate.

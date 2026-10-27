# Sentinel Observability & Operations

## 1. Structured Logging Conventions
Sentinel outputs JSON-formatted structured logs containing contextual tracing metadata:
- `timestamp`: RFC3339 timestamp.
- `level`: `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- `job_id`: UUID of the associated job.
- `attempt_id`: UUID of the current execution attempt.
- `task_type`: Task handler name.
- `execution_duration_ms`: Duration of execution in milliseconds.

## 2. Operational Health Signals & Probes
- **`/health/live`**: Liveness probe returning `200 OK` if the web application is running.
- **`/health/ready`**: Readiness probe verifying active database connection pool (`asyncpg`) and Redis connectivity before routing traffic.

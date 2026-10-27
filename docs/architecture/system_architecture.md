# Sentinel System Architecture

## 1. Purpose and Architectural Scope
Sentinel is an asynchronous, distributed job-processing platform designed for reliable task dispatch, execution tracking, and durable persistence. Its primary scope is to provide a robust API gateway for job submission and management, paired with a scalable background worker pool backed by Redis/RQ and PostgreSQL.

## 2. External Actors and Dependencies
- **API Clients**: Users and external microservices submitting jobs, querying job statuses, and retrieving execution results via REST endpoints.
- **Developers & Operators**: Engineers managing deployments, database migrations, and monitoring via Docker Compose and structured logs.
- **External Dependencies**: PostgreSQL 16 (durable data store) and Redis (message broker and job queue).

## 3. System and Trust Boundaries
- **API Boundary**: FastAPI application layer handling incoming HTTP requests, input validation, authentication checks, and database session management.
- **Persistence Boundary**: PostgreSQL database enforcing ACID guarantees, relational integrity, and durable job history.
- **Execution Boundary**: Isolated background worker processes pulling jobs from Redis/RQ, executing tasks, and updating job outcomes back to PostgreSQL.

## 4. Main Runtime Components
1. **FastAPI Web Server**: Exposes REST endpoints (`/jobs`, `/health`).
2. **PostgreSQL 16**: Durable state store for jobs, attempt history, and idempotency records.
3. **Redis Broker**: In-memory message broker managing the RQ task queue.
4. **RQ Worker Process**: Independent background worker executing registered Python tasks.

## 5. Communication Methods and Protocols
- **Client to API**: HTTPS / HTTP over JSON REST API.
- **API to PostgreSQL**: Asynchronous SQL queries via SQLAlchemy 2.0 and `asyncpg`.
- **API to Redis**: TCP connection for enqueuing jobs via RQ.
- **Worker to Redis**: Polling and job status updates via Redis TCP connection.
- **Worker to PostgreSQL**: Direct async database updates for state transitions (`RUNNING`, `SUCCEEDED`, `FAILED`).

## 6. Local Development and Deployment Topology
- Orchestrated via `docker-compose.yaml` running four core containers: `web` (FastAPI), `worker` (RQ), `db` (PostgreSQL), and `redis` (Redis).

## 7. Assumptions and Limitations
- PostgreSQL and Redis do not share an atomic distributed transaction; state is durably committed to PostgreSQL prior to queue enqueuing.
- Task execution is at-least-once; tasks must be designed to be idempotent.

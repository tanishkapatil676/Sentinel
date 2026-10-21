# Project Charter: Sentinel

## 1. Project Identity & Administrative Metadata
* **Project Name**: Sentinel
* **Core Category**: Reliable Backend & Distributed Job Processing Platform (Backend Engineering, Distributed Systems, SDE Internship Portfolio)
* **Milestone**: Milestone 1 of 10 (Planning and Specification)
* **Execution Mode**: AI-assisted, human-reviewed
* **Milestone Type**: Planning and specification only (No application implementation code)

---

## 2. Problem Statement
Applications frequently encounter tasks too time-consuming or resource-intensive to execute synchronously within the lifecycle of an HTTP request. Synchronous execution increases response latency, risks client connection timeouts, and makes failure recovery complex.

Sentinel accepts supported jobs via a REST API, validates requests, durably persists job records, dispatches work to asynchronous background workers, records execution outcomes, enforces controlled retries, and exposes job status and results to authorized clients.

### The 6 Distinct Lifecycle Events
Sentinel strictly distinguishes between the following discrete operational milestones:
1. **Request Accepted**: The API gateway has validated client headers, authentication tokens, and input payload schemas.
2. **Job Durably Recorded**: The job record is committed to PostgreSQL with a `PENDING` state and a unique primary key / idempotency key.
3. **Work Successfully Dispatched**: The job task payload is pushed onto the Redis/RQ broker queue (`QUEUED`).
4. **Task Execution Started**: A background worker picks up the job payload and begins execution (`RUNNING`).
5. **Task Completed**: The underlying task logic finishes execution without throwing unhandled exceptions.
6. **Final Outcome Successfully Persisted**: The task result or error stack trace is durably written back to PostgreSQL (`COMPLETED` or `FAILED`).

#### Why These Events Cannot Be Treated as Equivalent
Treating these events as equivalent introduces catastrophic failure modes in distributed systems:
* *Acceptance vs. Durability*: An API response can confirm receipt before the database write commits, resulting in silent data loss if the database drops connection mid-write.
* *Dispatch vs. Execution*: A job can be successfully pushed to a queue broker while the worker pool is offline or deadlocked, leaving jobs stranded in `QUEUED` indefinitely.
* *Execution vs. Persistence*: A task can successfully compute a result in memory, but if the worker crashes before updating PostgreSQL, the system state remains out of sync with reality.

---

## 3. Target Users & Operational Boundaries
* **API Client**: Submits supported jobs with authentication headers and polls or retrieves job status and results.
* **Platform Operator**: Inspects system health, liveness/readiness endpoints, worker logs, failure metrics, and recovery states.
* **Developer**: Adds new background task handlers, runs automated test suites, configures environment settings, and operates the platform locally via Docker Compose.
* *Boundary*: The initial target environment is a single developer running a reproducible local stack. Multi-tenant enterprise quotas and distributed clusters are explicitly outside initial MVP scope.

---

## 4. Proposed Solution & Technology Stack (Provisional)
*Note: All items below are **PROPOSED** and subject to verification during Phase 2 feasibility and integration checks.*
* **Language**: Python 3.12+
* **API Framework**: FastAPI, Pydantic, Pydantic-Settings
* **Database Layer**: PostgreSQL, SQLAlchemy 2.0+, Alembic
* **Queue Broker & Workers**: Redis, RQ (Redis Queue)
* **Testing & Quality**: pytest, HTTPX
* **Performance Benchmarking**: Locust
* **Containerization & CI**: Docker Compose, GitHub Actions
* **Observability**: Structured JSON logging (`structlog`)

---

## 5. MVP Scope & Feature Classification

### Must-Haves (Required for Completed MVP)
* Client-facing REST API with authentication and job ownership checks.
* Validated API request submission and persistent job tracking in PostgreSQL.
* Asynchronous dispatch and background worker execution via Redis/RQ.
* Bounded retry policy with exponential backoff for transient failures.
* Scoped idempotency key enforcement (FR-13).
* Structured lifecycle logging (FR-14).
* Liveness and dependency-aware readiness endpoints (`/health`).
* Automated test suite (pytest) and reproducible local execution.

### Should-Haves (Reliability & Performance Verification)
* Performance benchmarking scripts (Locust) to establish p50/p95/p99 latency metrics under load (FR-15).
* Worker crash recovery verification and deadlock handling.

### Could-Haves (Optional Enhancements)
* Optional administrative dashboard or CLI metrics reporter.

### Explicitly Excluded (Unless Concrete Requirements Emerge)
* React frontend dashboard as a prerequisite.
* Full cloud provider deployment (AWS/GCP managed infra).
* Multi-tenant rate limiting and resource quotas.
* Advanced priority queues and scheduled/cron jobs.
* Distributed tracing (OpenTelemetry) across multiple microservices.
* Multiple broker backends (RabbitMQ/Kafka).
* Kubernetes orchestration manifests.
* Any claim of exact-once external execution.

---

## 6. Constraints, Assumptions, and Limitations
* **No Numerical Performance Targets Yet**: Baseline numbers will be measured during benchmarking milestones, not assumed.
* **Unverified Architecture**: The proposed architecture has not yet been executed as a running application.
* **Duplicate Execution Risk**: At-least-once queue delivery guarantees mean duplicate execution is possible unless task handlers are explicitly idempotent.
* **Idempotency Scope**: API idempotency keys prevent duplicate *job creation*, but do not guarantee exactly-once side effects for external APIs called by workers.
* **Queue/Database Consistency**: Asynchronous communication between PostgreSQL and Redis introduces potential split-brain or sync lag during abrupt network partitions.
* **Local vs. Production**: Successful local execution via Docker Compose does not automatically guarantee production resilience under heavy concurrent workloads.

---

## 7. Success Definition
Sentinel's MVP will be considered successful when a developer can spin up the containerized environment, submit an authenticated job with an idempotency key, verify durably persisted states across the 6 lifecycle stages, observe structured logs during worker execution, and execute an automated test suite that validates error handling and retry mechanics.

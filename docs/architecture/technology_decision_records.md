

# Sentinel Technology Decision Records (TDR)

## DEC-001: API Framework Selection
* **Status**: Accepted
* **Context**: Sentinel requires a robust, high-performance asynchronous REST API framework to handle job submissions, status queries, health probes, and authentication with automated OpenAPI documentation and validation.
* **Options Considered**: FastAPI vs. Flask vs. Django REST Framework (DRF).
* **Selected Option**: **FastAPI**.
* **Evidence & References**: FastAPI Official Documentation (`https://fastapi.tiangolo.com/`), Starlette ASGI benchmarks.
* **Rationale**: FastAPI natively supports asynchronous I/O (`async/def`), integrates seamlessly with Pydantic v2 for robust data validation, generates interactive OpenAPI specs automatically, and provides clean dependency injection (`Depends`) ideal for authentication and session management. DRF and Flask lack native async routing speed and modern type-hint validation out of the box.
* **Trade-offs**: Steeper learning curve for advanced ASGI middleware; smaller ecosystem than legacy Django/Flask.
* **Revisit Condition**: Extreme ecosystem shift away from Starlette/FastAPI.

## DEC-002: Durable Relational Database Selection
* **Status**: Accepted
* **Context**: Sentinel requires a robust ACID-compliant relational data store for persistent job records, state history, authentication tokens, and idempotency keys.
* **Options Considered**: PostgreSQL vs. SQLite (limited local-only).
* **Selected Option**: **PostgreSQL (v16+)**.
* **Evidence & References**: PostgreSQL 16 official release notes; SQLAlchemy 2.0 async engine compatibility.
* **Rationale**: PostgreSQL offers native `UUID` and `JSONB` data types, robust concurrent transaction isolation (`READ COMMITTED` / `SERIALIZABLE`), high reliability, and excellent production readiness via Docker. SQLite lacks robust concurrent write performance and native enterprise JSON indexing features required for production worker scaling.
* **Trade-offs**: Higher operational overhead than SQLite; requires a containerized service during local development.
* **Revisit Condition**: Shift toward a fully serverless persistence architecture.

## DEC-003: Background Queue and Worker Framework
* **Status**: Accepted
* **Context**: Sentinel requires an asynchronous background task queue to manage job dispatch, worker execution pools, retries, and failure registries.
* **Options Considered**: Redis + RQ vs. Celery vs. Dramatiq.
* **Selected Option**: **Redis + RQ**.
* **Evidence & References**: RQ Documentation (`https://python-rq.org/`), comparison studies on developer ergonomics vs. Celery complexity.
* **Rationale**: RQ provides a simple, Python-native API that relies directly on Redis without requiring complex message broker topologies (like RabbitMQ) or heavyweight configuration scaffolds (like Celery). It perfectly matches a focused backend portfolio scope while providing robust retry decorators and worker lifecycle hooks.
* **Trade-offs**: Less feature-rich than Celery for complex multi-broker choreography or periodic cron scheduling (though sufficient for Sentinel's core needs).
* **Revisit Condition**: Requirement for multi-broker routing or complex distributed chord workflows.

## DEC-004: ORM and Migration System
* **Status**: Accepted
* **Context**: Sentinel requires a type-safe Object Relational Mapper and database migration tool to manage schema evolution safely across development and deployment environments.
* **Options Considered**: SQLAlchemy 2.0 + Alembic vs. Django ORM.
* **Selected Option**: **SQLAlchemy 2.0 + Alembic**.
* **Evidence & References**: SQLAlchemy 2.0 Unified Tutorial; Alembic Documentation.
* **Rationale**: SQLAlchemy 2.0 introduces fully typed, modern async paradigms (`AsyncSession`, `select()`) that pair perfectly with FastAPI. Alembic provides industry-standard, version-controlled database migrations essential for reliable schema deployments.
* **Trade-offs**: Boilerplate configuration required for async session makers and migration environment scripts (`env.py`).
* **Revisit Condition**: Adoption of a non-relational or alternative database store.

## DEC-005: Job and Attempt Persistence Architecture
* **Status**: Accepted
* **Context**: Relying solely on Redis for job history is risky because Redis data is primarily ephemeral or subject to TTL eviction. Sentinel requires a queryable audit trail of execution attempts.
* **Options Considered**: Redis-only registry vs. Dedicated PostgreSQL `jobs` and `job_attempts` tables.
* **Selected Option**: **Dedicated PostgreSQL `jobs` and `job_attempts` tables**.
* **Evidence & References**: System reliability requirements (`NFR-02`, `NFR-07`).
* **Rationale**: Storing master job state and detailed attempt histories in PostgreSQL ensures durable long-term auditability, fast relational filtering by status/client, and protection against Redis memory eviction policies.
* **Trade-offs**: Requires dual-system updates (DB + Queue sync).
* **Revisit Condition**: Transition to an event-sourcing architectural model.

## DEC-006: Retry Semantics and Backoff Policy
* **Status**: Accepted
* **Context**: Background jobs frequently fail due to transient downstream issues (network blips, rate limits). Sentinel needs a predictable retry policy.
* **Options Considered**: Immediate infinite retries vs. Bounded exponential backoff with jitter and max attempt limits.
* **Selected Option**: **Bounded exponential backoff with configurable max attempts**.
* **Evidence & References**: Distributed systems reliability best practices; RQ retry configuration rules.
* **Rationale**: Prevents retry storms from overwhelming downstream services while giving transient failures room to recover automatically before entering terminal `FAILED` status.
* **Trade-offs**: Requires tracking attempt counts and retry wait timestamps in both the queue and database.
* **Revisit Condition**: Introduction of dynamic SLA-based job priority queues.

## DEC-007: Request Idempotency Mechanism
* **Status**: Accepted
* **Context**: Clients may re-submit requests due to network timeouts, risking duplicate job creation (`FR-13`).
* **Options Considered**: Client-managed GUIDs without server enforcement vs. Server-side `Idempotency-Key` header with PostgreSQL unique constraints.
* **Selected Option**: **Server-side `Idempotency-Key` header with database unique constraints and cached response retrieval**.
* **Evidence & References**: API design best practices for payment and job gateways.
* **Rationale**: Guarantees that identical requests submitted within a retention window return cached responses (`200 OK` / `201 Created`) without spawning duplicate database records or worker tasks.
* **Trade-offs**: Requires storage overhead for idempotency keys and TTL cleanup logic.
* **Revisit Condition**: Migration to an external distributed caching layer (e.g., Redis-based token bucket).

## DEC-008: Database and Queue Consistency Strategy
* **Status**: Accepted
* **Context**: A PostgreSQL transaction cannot atomically span across Redis queue publishing, leading to potential split-brain states (phantom DB records vs. unqueued tasks).
* **Options Considered**: Two-phase commit (impossible across Redis/PG) vs. Transactional commit followed by broker enqueue with background reconciliation sweeps.
* **Selected Option**: **PostgreSQL commit first, followed by RQ enqueue, backed by a periodic orphaned job reconciliation task**.
* **Evidence & References**: Distributed transactional outbox patterns.
* **Rationale**: Ensures master state is safely committed to the database before broker dispatch. If broker dispatch fails, a background reconciliation sweeper detects unqueued `QUEUED` records and re-publishes them.
* **Trade-offs**: Eventual consistency window between database commit and queue pickup.
* **Revisit Condition**: Adoption of a unified broker-database architecture.

## DEC-009: Authentication Approach
* **Status**: Accepted
* **Context**: Sentinel requires secure client authentication and data ownership isolation (`FR-09`) suitable for a portfolio MVP.
* **Options Considered**: OAuth2/OIDC provider (Auth0/Keycloak) vs. Simple API Bearer token with database lookup or hashed validation.
* **Selected Option**: **Opaque API Bearer tokens verified via database lookup with scoped client ownership (`client_id`)**.
* **Evidence & References**: FastAPI Security documentation (`fastapi.security`).
* **Rationale**: Provides robust, straightforward security isolation without the heavyweight infrastructure complexity of external identity providers, perfectly suited for an engineering portfolio project.
* **Trade-offs**: Requires maintaining client credentials and tokens in the database.
* **Revisit Condition**: Requirement for enterprise SSO or multi-tenant federated identity.

## DEC-010: Testing Strategy
* **Status**: Accepted
* **Context**: Sentinel requires high code quality, reliable unit testing, and isolated database/API testing.
* **Options Considered**: Manual testing vs. Automated pytest suite with transaction rollbacks and Docker integration tests.
* **Selected Option**: **Automated `pytest` suite with `httpx` ASGI client, database savepoint isolation, and Docker Compose integration tests**.
* **Evidence & References**: FastAPI testing guide; SQLAlchemy async test patterns.
* **Rationale**: Guarantees fast, isolated unit tests using transaction rollbacks alongside realistic containerized integration tests for Redis and PostgreSQL.
* **Trade-offs**: Requires maintaining fixture factories and test database cleanup routines.
* **Revisit Condition**: None.

## DEC-011: Local Environment and CI Pipeline
* **Status**: Accepted
* **Context**: The development and test environments must be fully reproducible across local machines and cloud CI runners.
* **Options Considered**: Manual host installations vs. Docker Compose local orchestration and GitHub Actions CI.
* **Selected Option**: **Docker Compose for local service orchestration + GitHub Actions for automated test pipelines**.
* **Evidence & References**: Docker Compose Specification; GitHub Actions workflow guides.
* **Rationale**: Ensures zero "works on my machine" discrepancies by standardizing database, redis, API, and worker containers across development and CI environments.
* **Trade-offs**: Requires container runtime availability on developer machines.
* **Revisit Condition**: Shift toward cloud-native Kubernetes deployment pipelines.

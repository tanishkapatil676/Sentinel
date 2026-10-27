# Sentinel Architecture Decision Records (ADRs)

## ADR-01: Asynchronous Python Stack (FastAPI & SQLAlchemy 2.0)
- **Status**: Accepted
- **Context**: Sentinel requires high concurrency for handling job submissions and status queries while managing database I/O efficiently.
- **Decision**: Use Python 3.13, FastAPI, SQLAlchemy 2.0 (async), and `asyncpg`.
- **Trade-offs**: Requires async-compatible database drivers and careful session management, but yields superior I/O throughput.

## ADR-02: PostgreSQL as Durable Source of Truth & Redis/RQ as Broker
- **Status**: Accepted
- **Context**: Message brokers like Redis are transient and volatile. Job state and audit trails must survive broker crashes.
- **Decision**: PostgreSQL stores all durable job metadata and attempt history. Redis and RQ are strictly used for task queueing and worker dispatch.
- **Trade-offs**: Requires dual-system coordination, managed via durable commit prior to queue dispatch.

## ADR-03: Separate API and Worker Processes
- **Status**: Accepted
- **Context**: Heavy task execution must not block incoming HTTP request-response cycles.
- **Decision**: Decouple the FastAPI web server process from background RQ worker processes.
- **Trade-offs**: Requires independent container scaling and separate deployment configurations.

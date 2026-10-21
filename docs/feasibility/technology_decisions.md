# Technology Decisions

- **FastAPI / Pydantic v2**: Accepted. Verified via local execution and test suite.
- **SQLAlchemy 2.0 (Async) + asyncpg**: Accepted. Verified via async database session mocks and unit tests.
- **PostgreSQL 16**: Accepted as authoritative durable state store.
- **Redis & RQ**: Accepted for transient task queuing and worker dispatch.
- **Docker Compose**: Accepted for local multi-service orchestration.
- **pytest & HTTPX**: Accepted for unit and API testing.
- **Locust**: Accepted for future load testing (Deferred execution).

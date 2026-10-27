# Sentinel Deployment & Configuration Architecture

## 1. Container Topology (`docker-compose.yaml`)
Sentinel runs four distinct containerized services in local/production environments:
1. **`web`**: FastAPI process exposing the HTTP API.
2. **`worker`**: Background RQ worker executing tasks.
3. **`db`**: PostgreSQL 16 server storing job state and attempt logs.
4. **`redis`**: Redis server acting as the RQ broker.

## 2. Service Dependencies & Readiness
- **Startup Order**: `db` and `redis` $\rightarrow$ `web` and `worker`.
- **Health Checks**: PostgreSQL is checked via `pg_isready`; Redis via `redis-cli ping`.
- **Graceful Shutdown**: The worker process intercepts `SIGTERM` / `SIGINT` signals, allowing in-flight tasks to complete before exiting.

# Sentinel 🛡️

**Reliable Backend & Distributed Job Processing Platform**

[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Job_Queue-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)](https://www.sqlalchemy.org/)

Sentinel is a backend engineering project focused on reliable asynchronous job processing using Python, FastAPI, Redis Queue (RQ), and PostgreSQL.

The platform is designed to accept background jobs through a REST API, persist job information in a relational database, dispatch work to background workers, and track execution states and results. Its development roadmap covers reliability mechanisms, failure handling, observability, testing, performance evaluation, and operational readiness.

The project emphasizes practical backend engineering principles, including durable state management, explicit job lifecycles, controlled retries, worker recovery, and reproducible testing.

---

## 📑 Table of Contents

- [Core Features](#-core-features)
- [System Architecture](#️-system-architecture)
- [Development Roadmap](#-development-roadmap)
- [Technology Stack](#️-technology-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Testing and Quality Assurance](#-testing-and-quality-assurance)
- [Documentation](#-documentation)
- [Engineering Principles](#-engineering-principles)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🌟 Core Features

### 1. Asynchronous Job Processing
- REST API for submitting background jobs.
- Redis Queue (RQ) integration for dispatching jobs to workers.
- Separation of API request handling from background task execution.

### 2. Persistent Job State
- PostgreSQL-backed job records.
- SQLAlchemy-based database interactions.
- Job lifecycle tracking, including queued, running, completed, failed, and cancelled states where supported by the implementation.

### 3. API Design
- FastAPI-based REST endpoints.
- Structured request and response validation.
- Job submission and status retrieval.

### 4. Reliability Engineering
The project roadmap addresses:
- Retry handling and backoff strategies.
- Concurrent job-state updates.
- Idempotent job submission.
- Worker failure detection and recovery.
- Queue and database consistency.
- Explicit handling of terminal failures.

These mechanisms should be considered implemented only to the extent verified by the current source code and tests.

### 5. Observability and Operations
- Application logging.
- Health-check endpoints.
- Error handling and operational diagnostics.
- Performance testing and benchmarking.
- Documentation for system behavior and failure scenarios.

---

## 🏗️ System Architecture

```text
                  ┌─────────────────────────┐
                  │      Client / UI        │
                  └────────────┬────────────┘
                               │ HTTP / JSON
                               ▼
                  ┌─────────────────────────┐
                  │       FastAPI API       │
                  │                         │
                  │ Job submission          │
                  │ Request validation      │
                  │ Status retrieval        │
                  └────────────┬────────────┘
                               │
                  ┌────────────┴────────────┐
                  ▼                         ▼
       ┌────────────────────┐    ┌────────────────────┐
       │    PostgreSQL      │    │       Redis        │
       │                    │    │                    │
       │ Persistent jobs    │    │ RQ task queue      │
       │ Job status         │    │ Worker coordination│
       │ Results and errors │    │                    │
       └──────────┬─────────┘    └──────────┬─────────┘
                  │                         │
                  │                         ▼
                  │              ┌────────────────────┐
                  └─────────────►│ Background Worker  │
                                 │                    │
                                 │ Execute jobs       │
                                 │ Handle failures    │
                                 │ Update job state   │
                                 └────────────────────┘
```

### Architectural Responsibilities

| Component | Responsibility |
|---|---|
| FastAPI | Receives requests and exposes the REST API |
| PostgreSQL | Stores persistent job information |
| SQLAlchemy | Manages database models and interactions |
| Alembic | Manages database schema migrations |
| Redis | Supports queue storage and worker coordination |
| Redis Queue (RQ) | Dispatches background jobs |
| Worker | Executes background tasks |
| Pytest | Supports automated verification |

**Reliability principle:** A queue acknowledgment alone should not be treated as proof that a job completed successfully. Persistent job state, worker execution, retries, and recovery must be verified independently.

---

## 🚀 Development Roadmap

Sentinel follows a structured 10-milestone development plan.

| Milestone | Focus |
|---|---|
| M1 | Database schema, SQLAlchemy models, and persistence |
| M2 | Redis Queue integration and background workers |
| M3 | REST API and job lifecycle endpoints |
| M4 | Retry policies, backoff strategies, and failure handling |
| M5 | Logging, health checks, and observability |
| M6 | Concurrency control and queue-database consistency |
| M7 | Worker crash recovery and orphaned-job handling |
| M8 | Benchmarking, load testing, and bottleneck analysis |
| M9 | Production hardening and operational security |
| M10 | Integration verification, documentation, and project handover |

The roadmap describes the intended scope of the project. Completion and verification status should be established using the current repository, migration history, test results, and supporting documentation.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Language | Python 3.13 |
| API Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database Driver | asyncpg |
| Background Queue | Redis Queue (RQ) |
| Queue Backend | Redis |
| Validation | Pydantic |
| Testing | Pytest, pytest-asyncio, HTTPX |
| Containers | Docker Compose |
| Version Control | Git and GitHub |

Refer to `pyproject.toml` for the actual dependency versions and supported Python configuration.

---

## 📁 Repository Structure

The following is the intended high-level structure. Actual paths may differ as the implementation evolves.

```text
Sentinel/
├── .github/
│   └── workflows/              # CI workflows, if configured
├── docs/
│   ├── architecture/            # Architecture and reliability design
│   ├── integration/             # Integration plans and scenarios
│   └── evaluation/              # Benchmarking and evaluation
├── migrations/
│   └── versions/                # Alembic revision scripts
├── sentinel/
│   ├── api/                     # API routes and handlers
│   ├── models/                  # Database models
│   ├── tasks/                   # Background tasks and recovery
│   ├── config.py                # Application configuration
│   ├── database.py              # Database engine and sessions
│   ├── main.py                  # FastAPI application
│   ├── queue.py                 # Redis Queue configuration
│   └── worker.py                # Worker entry point
├── tests/
│   ├── integration/             # Integration tests
│   └── unit/                    # Unit tests
├── pyproject.toml               # Project metadata and dependencies
├── alembic.ini                  # Migration configuration
├── docker-compose.yml            # Local service configuration
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

Install the following tools before running the application:

- Python version supported by `pyproject.toml`
- PostgreSQL
- Redis
- Git
- Docker and Docker Compose, if using the container-based setup

### 1. Clone the Repository

```bash
git clone https://github.com/tanishkapatil676/Sentinel.git
cd Sentinel
```

### 2. Create a Virtual Environment

**Windows — PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

If the project defines a development dependency group named `dev`, install it using:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If this command does not match the dependency configuration in `pyproject.toml`, use the installation instructions defined by the project.

### 4. Configure Environment Variables

Create a `.env` file in the project root using the variable names expected by the application configuration.

Example configuration:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sentinel_db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
LOG_LEVEL=INFO
```

Update the credentials, database name, and other settings to match your local environment. Do not commit real passwords, API keys, or other secrets.

### 5. Start PostgreSQL and Redis

If the repository's Docker Compose configuration defines these services, run:

```bash
docker compose up -d
```

Check that the containers started successfully:

```bash
docker compose ps
```

### 6. Apply Database Migrations

After verifying the database connection and confirming that the required migration revisions exist, run:

```bash
alembic upgrade head
```

If the repository does not contain a valid initial migration, resolve that issue before attempting to initialize the database through Alembic.

### 7. Start the Background Worker

In a separate terminal, activate the virtual environment and run:

```bash
python -m sentinel.worker
```

Use the actual worker entry point defined in the repository if it differs.

### 8. Start the API Server

In another terminal, activate the virtual environment and run:

```bash
uvicorn sentinel.main:app --host 127.0.0.1 --port 8000 --reload
```

If the application uses a different import path, replace `sentinel.main:app` with the correct module and application object.

### 9. Explore the API

Open the interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

These pages are available when the application is running and the corresponding FastAPI documentation routes are enabled.

---

## 🔌 API Reference

The exact paths depend on the registered FastAPI routers. The following table describes the intended API surface; verify each route against the current application before relying on it.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/jobs` | Submit a background job |
| `GET` | `/jobs/{job_id}` | Retrieve a job's status and available result |
| `GET` | `/jobs` | List jobs, if implemented |
| `GET` | `/health` | Basic health check, if implemented |
| `GET` | `/health/live` | Liveness probe, if implemented |
| `GET` | `/health/ready` | Readiness probe, if implemented |

### Example: Submit a Job

The following is an illustrative request. Use the actual request schema and required fields defined by the API.

```bash
curl -X POST "http://127.0.0.1:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example-job",
    "payload": {
      "numbers": [1, 2, 3, 4, 5]
    }
  }'
```

A successful response should be checked against the API's actual response model. If a job identifier is returned, use it to retrieve the job's current state.

### Example: Retrieve a Job

Replace `<job_id>` with the identifier returned by the job-submission endpoint.

```bash
curl "http://127.0.0.1:8000/jobs/<job_id>"
```

A job may be queued, running, completed, failed, or in another state supported by the implementation.

---

## 🧪 Testing and Quality Assurance

Sentinel uses Pytest for automated testing.

### Run the Test Suite

```bash
pytest -v
```

### Run Unit Tests

```bash
pytest -v tests/unit/
```

### Run Integration Tests

```bash
pytest -v tests/integration/
```

### What to Verify

- Job creation and persistent storage.
- Correct job-state transitions.
- Queue dispatch and worker execution.
- Handling of invalid requests.
- Failure and retry behavior.
- Duplicate submission and idempotency behavior, where implemented.
- Recovery from interrupted worker execution.
- Database and queue interaction under concurrent workloads.
- Health-check behavior.
- Regression testing after changes.

Test counts, performance results, and reliability guarantees should be published only when supported by reproducible runs and recorded evidence.

---

## 📄 Documentation

Technical documentation is organized under `docs/`.

### Architecture

- [Architecture documentation](docs/architecture/)
- [Queue and database consistency](docs/architecture/queue_database_consistency.md)
- [Worker crash recovery](docs/architecture/worker_crash_recovery.md)
- [Reliability and observability](docs/architecture/reliability_observability.md)
- [Failure-scenario verification matrix](docs/architecture/failure_scenarios_verification_matrix.md)

### Integration

- [Integration documentation](docs/integration/)
- [System integration plan](docs/integration/system_integration_plan.md)
- [Data integrity invariants](docs/integration/data_integrity_invariants.md)
- [End-to-end scenarios](docs/integration/end_to_end_scenarios.md)

### Evaluation

- [Evaluation documentation](docs/evaluation/)
- [Reliability evaluation](docs/evaluation/reliability_evaluation.md)
- [Bottleneck analysis](docs/evaluation/bottleneck_analysis.md)

These relative links work when the corresponding files exist at the specified paths in the GitHub repository. Remove or update any links that do not match the committed documentation.

---

## 🧭 Engineering Principles

Sentinel is developed around the following principles:

- **Durability:** Store job state persistently rather than relying solely on queue state.
- **Explicit state transitions:** Make job lifecycle changes clear and testable.
- **Failure awareness:** Treat worker crashes, retries, and partial failures as normal engineering scenarios.
- **Idempotency:** Define and test duplicate-submission behavior where required.
- **Observability:** Use logs, health checks, and diagnostic information to investigate failures.
- **Reproducibility:** Keep setup instructions, test commands, and benchmark procedures repeatable.
- **Honest engineering claims:** Document only the behavior and results supported by the current implementation and verification evidence.

---

## 🔭 Future Improvements

Potential areas for further development include:

- More comprehensive retry and dead-letter handling.
- Stronger recovery guarantees for interrupted jobs.
- Improved concurrency control and queue-database coordination.
- Authentication, authorization, and job ownership enforcement.
- Rate limiting and request-size enforcement.
- Metrics, tracing, and operational dashboards.
- Reproducible load tests and benchmark reports.
- Continuous integration and automated migration verification.
- Containerized deployment and operational runbooks.

The priority of each improvement depends on the current implementation and outstanding verification results.

---

## 🛡️ License

This project is intended to use the MIT License if an MIT `LICENSE` file is included in the repository.

See the [`LICENSE`](LICENSE) file for the applicable terms.

---

## 👩‍💻 Author

**Tanishka Patil**

GitHub: [@tanishkapatil676](https://github.com/tanishkapatil676)

Project: [Sentinel](https://github.com/tanishkapatil676/Sentinel)

*Built as a backend engineering portfolio project focused on asynchronous processing, reliability, and distributed systems.*

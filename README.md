# Sentinel

Reliable, asynchronous distributed job-processing platform built with Python 3.13, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL 16, and Redis/RQ.

## Implementation Status
- **Milestone 4**: Foundation, asynchronous architecture, local infrastructure, and testing suite completed successfully.

## Prerequisites & Installation
1. Python 3.13+
2. Docker & Docker Compose
3. Install dependencies: `pip install .[dev]`

## Test & Quality Commands
- Run tests: `pytest`
- Start app: `uvicorn sentinel.main:app --reload`

## CI Workflow
- Configured in `.github/workflows/ci.yml`.

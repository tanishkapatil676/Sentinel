# Foundation Implementation Guide

## Overview
Sentinel is structured around an asynchronous, production-grade architecture built with Python 3.13, FastAPI, SQLAlchemy 2.0 (async), and Redis/RQ.

## Core Architectural Components
- **Centralized Configuration**: Managed via `pydantic-settings` in `src/sentinel/config.py`, reading from environment variables and `.env`.
- **Database Layer**: Asynchronous engine (`create_async_engine`) using `asyncpg` with a session lifecycle dependency (`get_db`).
- **Application Entry Point**: FastAPI application instance with lifespan management for graceful startup/shutdown and health probes (`/health`, `/health/live`, `/health/ready`).

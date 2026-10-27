# Sentinel — Test Environment and Reproducible Harness Guide

## 1. Environment & Dependencies
- **Runtime**: Python 3.13.16
- **Database**: PostgreSQL with Async SQLAlchemy (`asyncpg`)
- **Queue / Broker**: Redis RQ
- **Testing Tools**: Pytest (`pytest-asyncio`)

## 2. Execution Procedures
### Level 1: Static & Linting Checks
```bash
git status
pytest -v tests/unit/test_handler.py
```

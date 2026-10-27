# Sentinel Database & Migration Guide

## 1. Prerequisites & Architecture
- PostgreSQL 16 server.
- SQLAlchemy 2.0 with async engine and `asyncpg` driver.
- Alembic for database migration management.

## 2. Session Lifecycle & Transactions
- Sessions are scoped per request using `AsyncSessionLocal` dependency injection.
- Automatic commit on successful request completion and automatic rollback on unhandled exceptions.

## 3. Migration Commands
- **Initialize/Upgrade**: `alembic upgrade head`
- **Check Current Status**: `alembic current`

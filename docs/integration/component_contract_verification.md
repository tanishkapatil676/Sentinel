# Sentinel Component Contract Verification

## 1. Overview

This document records the cross-component contract verification for Sentinel, validating that the API, database, queue, worker, and recovery subsystems share consistent data models, state enums, and transaction boundaries.

## 2. Subsystem Alignment Matrix

| Subsystem | Contract / Interface | Verified Invariant | Status |
| :--- | :--- | :--- | :--- |
| **API Layer** | FastAPI Request/Response Schemas | Validates payload structure; enforces idempotency key handling; returns standardized job states. | **Requires verification** |
| **Persistence** | PostgreSQL (`jobs` table & Enum) | Enforces unique primary keys, non-null status constraints, and timestamp auditing. | **Requires verification** |
| **Queue / Worker** | Redis RQ Task Dispatch | Passes lightweight job IDs; workers query authoritative PostgreSQL state. | **Requires verification** |
| **Concurrency** | Worker job claiming (`FOR UPDATE`) | Prevents simultaneous workers from successfully claiming the same eligible job. Verify the actual claim mechanism; do not assume `FOR UPDATE` is implemented. | **Requires verification** |
| **Recovery** | Stale Job Reconciliation Scan | Reclaims abandoned `RUNNING` jobs older than the 15-minute threshold. | **Unverified until implementation and tests are confirmed** |

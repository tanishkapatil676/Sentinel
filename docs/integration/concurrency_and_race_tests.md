# Sentinel Concurrency and Reliability Interaction Testing

## 1. Overview

This document evaluates the combined interactions of Sentinel's reliability mechanisms under concurrency, worker crashes, duplicate deliveries, and recovery scans. Statuses must be supported by the current implementation and passing test evidence.

## 2. Interaction Scenarios

### 2.1 Idempotency + Retry

- **Intended guarantee**: Retries operate strictly on the original job record linked to the idempotency fingerprint.
- **Verification required**: Confirm retry attempts reuse the original job ID and do not create duplicate job records.
- **Status**: Requires verification.

### 2.2 Worker Interruption + Recovery

- **Intended guarantee**: Stale jobs abandoned by abrupt worker termination (>15 min) are reclaimed by `recover_stale_jobs`.
- **Verification required**: Confirm the recovery function exists, verify its configured threshold, and test recovery against persisted stale jobs.
- **Status**: Unverified until implementation and tests are confirmed.

### 2.3 Duplicate Queue Delivery

- **Intended guarantee**: Database concurrency control prevents duplicate concurrent claims on the same job.
- **Verification required**: Inspect the actual claim mechanism and run concurrent deliveries using separate sessions. Do not assume `FOR UPDATE` is used unless the implementation confirms it.
- **Status**: Requires concurrency testing.

### 2.4 Terminal State Protection

- **Intended guarantee**: Completed or failed jobs cannot be reactivated by late messages or stale workers.
- **Verification required**: Test late delivery after a terminal state and confirm stale executions cannot overwrite the terminal result.
- **Status**: Requires verification.

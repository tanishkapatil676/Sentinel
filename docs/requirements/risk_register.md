# Sentinel Risk Register

## Risk Assessment Scale
* **Likelihood**: Low (L), Medium (M), High (H)
* **Impact**: Low (L), Medium (M), High (H), Critical (C)

---

| Risk ID | Description & Cause | Likelihood | Impact | Mitigation Strategy | Verification Method | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RISK-01** | PostgreSQL or Redis becomes unavailable during operation. | M | C | Health check probes (`/health/ready`), connection retry wrappers, and circuit breakers. | Failure injection tests (`pytest-mock`) | `PLANNED` |
| **RISK-02** | A worker crashes mid-execution due to OOM or node termination. | M | H | Worker heartbeat leases, timeout detection, and state machine recovery reset to `QUEUED`. | Worker kill simulation test | `PLANNED` |
| **RISK-03** | A background job executes more than once due to broker redelivery. | H | M | Idempotent task handler design guidelines and unique execution deduplication checks. | Duplicate message delivery test | `PLANNED` |
| **RISK-04** | An external side-effect (e.g., API call) succeeds before result persistence. | M | H | External idempotency keys, transactional outbox pattern, or explicit reconciliation workers. | Side-effect mock verification | `PLANNED` |
| **RISK-05** | Retry storms or queue growth overwhelm available worker capacity. | M | H | Exponential backoff with jitter, max retry limits, and dead-letter queue (DLQ) isolation. | Load test with Locust (`benchmarks/`) | `PLANNED` |
| **RISK-06** | A malicious or unauthorized client accesses another client's job. | L | C | Strict ownership filters (`client_id`) on all API queries and token validation middleware. | Security penetration & isolation tests | `PLANNED` |
| **RISK-07** | Sensitive customer data or credentials leak through application logs. | M | H | Structured logging filters, automatic payload redaction, and strict sanitization policies. | Log audit parser tests | `PLANNED` |
| **RISK-08** | AI-assisted code generation introduces unverified assumptions or bugs. | H | M | Strict human code review, automated test coverage gates, and modular verification milestones. | Comprehensive pytest test suite | `PLANNED` |
| **RISK-09** | Queue (Redis) and database (PostgreSQL) state become inconsistent. | M | H | Reconciliation background tasks, atomic state transitions, and idempotency key constraints. | Consistency fault-injection test | `PLANNED` |
| **RISK-10** | Project scope or feature creep exceeds available SDE timeline. | M | M | Strict adherence to MVP boundaries, milestone partitioning (10 phases), and deferred features (FR-16). | Milestone gate reviews | `PLANNED` |

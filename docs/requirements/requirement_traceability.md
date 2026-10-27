# Requirement Traceability Matrix (RTM)

## Functional Requirements Mapping

| ID | Priority | Responsible Phase / Milestone | Planned Component | Verification Method | Evidence Required | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Must | Phase 2 / M2 | `src/sentinel/api/jobs.py` | API Test | HTTP 201/200 & Job UUID | `PLANNED` |
| **FR-02** | Must | Phase 2 / M2 | `src/sentinel/api/schemas.py` | Unit Test | HTTP 422 for invalid payloads | `PLANNED` |
| **FR-03** | Must | Phase 2 / M2 | `src/sentinel/db/models.py` | DB Integration Test | Query verification on `jobs` table | `PLANNED` |
| **FR-04** | Must | Phase 3 / M3 | `src/sentinel/workers/` | End-to-End Test | Worker execution logs | `PLANNED` |
| **FR-05** | Must | Phase 2 / M2 | `src/sentinel/api/jobs.py` | API Test | HTTP 200 response with state | `PLANNED` |
| **FR-06** | Must | Phase 2 / M2 | `src/sentinel/api/schemas.py` | Integration Test | Safe failure summary response | `PLANNED` |
| **FR-07** | Must | Phase 4 / M4 | `src/sentinel/services/retry.py` | Integration Test | DB state transition to `RETRY_WAIT` | `PLANNED` |
| **FR-08** | Must | Phase 3 / M3 | `src/sentinel/db/models.py` | DB Integration Test | Attempt table SQL records | `PLANNED` |
| **FR-09** | Must | Phase 4 / M4 | `src/sentinel/core/auth.py` | Security Test | HTTP 401/403 for invalid tokens | `PLANNED` |
| **FR-10** | Must | Phase 2 / M2 | `src/sentinel/api/health.py` | API Test | `/health` endpoint response | `PLANNED` |
| **FR-11** | Must | Phase 5 / M5 | `docker-compose.yml` | Clean Environment Test | Docker container boot logs | `PLANNED` |
| **FR-12** | Must | Phase 5 / M5 | `tests/` | Automated Test Suite | Pytest execution results | `PLANNED` |
| **FR-13** | Must (MVP) | Phase 4 / M4 | `src/sentinel/core/idempotency.py` | API Test | Re-submission match header | `PLANNED` |
| **FR-14** | Must (MVP) | Phase 4 / M4 | `src/sentinel/observability/` | Log Inspection | Structlog JSON stdout logs | `PLANNED` |
| **FR-15** | Should | Phase 6 / M6 | `benchmarks/locustfile.py` | Load Test | Locust p50/p95/p99 latency metrics | `PLANNED` |
| **FR-16** | Could | Post-MVP | `src/sentinel/web/` | Manual Inspection | Dashboard rendering in browser | `PLANNED` |

## Non-Functional Requirements Mapping

| ID | Priority | Responsible Phase / Milestone | Planned Component | Verification Method | Evidence Required | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | High | Phase 2 / M2 | `docs/state_machine.md` | State Machine Test | Valid transition logs | `PLANNED` |
| **NFR-02** | High | Phase 2 / M2 | `src/sentinel/api/jobs.py` | DB Failure Test | HTTP 500 without job creation | `PLANNED` |
| **NFR-03** | Medium | Phase 4 / M4 | `src/sentinel/core/errors.py` | Security Test | Sanitized JSON error responses | `PLANNED` |
| **NFR-04** | High | Phase 4 / M4 | `src/sentinel/core/auth.py` | Security Test | Config validation logs | `PLANNED` |
| **NFR-05** | High | Phase 1–6 | System Architecture | Architecture Review | Modular codebase structure | `PLANNED` |
| **NFR-06** | High | Phase 5 / M5 | `docker-compose.yml` | Reproducibility Test | Clean boot verification | `PLANNED` |
| **NFR-07** | High | Phase 4 / M4 | `src/sentinel/observability/` | Log Audit | `job_id` tracing across logs | `PLANNED` |
| **NFR-08** | High | Phase 6 / M6 | `benchmarks/` | Load Experiment | Reproducible benchmark metrics | `PLANNED` |
| **NFR-09** | High | Phase 4 / M4 | `src/sentinel/workers/` | Timeout Test | Task cancellation logs | `PLANNED` |
| **NFR-10** | High | Phase 4 / M4 | Fault Injection System | Fault Injection Test | Clean rollback & status reporting | `PLANNED` |


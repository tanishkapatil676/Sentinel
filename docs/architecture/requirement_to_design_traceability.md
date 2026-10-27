# Sentinel Requirement-to-Design Traceability

| Req ID | Requirement Summary | Design Document / Component | Planned Verification | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FR-01** | Asynchronous Job Submission | `api_contract.md`, `src/sentinel/api/jobs.py` | API integration test (`test_api.py`) | DESIGNED |
| **FR-02** | Idempotent Submission Handling | `data_model.md`, `api_contract.md` | Concurrency test with duplicate keys | DESIGNED |
| **FR-03** | Job Status Tracking | `job_lifecycle.md`, `data_model.md` | Unit & API tests for `GET /jobs/{id}` | DESIGNED |
| **FR-04** | Background Task Queue Dispatch | `system_architecture.md`, `queue.py` | Worker integration test | DESIGNED |
| **FR-05** | Attempt History & Error Logging | `data_model.md`, `job_lifecycle.md` | Database integration test | DESIGNED |
| **NFR-01** | Asynchronous I/O Performance | `system_architecture.md` (FastAPI/AsyncPG) | Load testing and async benchmarks | PLANNED |
| **NFR-02** | Secure Token Authentication | `security_design.md` | API auth header tests | DESIGNED |
| **NFR-03** | Structured JSON Logging | `observability_and_operations.md` | Log format inspection tests | DESIGNED |

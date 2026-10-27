# Sentinel Architecture Risk Register

| Risk ID | Risk Description & Cause | Likelihood | Impact | Mitigation Strategy / Design Decision | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AR-01** | Database and queue desynchronization if publication fails post-commit. | Medium | High | Periodic reconciliation sweep for orphaned `QUEUED` jobs and manual retry endpoints. | Mitigated |
| **AR-02** | Duplicate job execution due to network retries or worker redelivery. | High | Medium | Enforce idempotent task implementation and unique idempotency keys at the API layer. | Active |
| **AR-03** | Unbounded worker retry storms exhausting system resources. | Medium | High | Exponential backoff with jitter and strict maximum attempt limits (`max_attempts`). | Mitigated |
| **AR-04** | Unauthorized cross-tenant job access via ID guessing. | Low | High | Strict `client_id` ownership checks on all job retrieval and modification endpoints. | Mitigated |

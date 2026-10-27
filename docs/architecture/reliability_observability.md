# Reliability Observability & Diagnostics

> **Verification status:** These are intended observability requirements. Confirm them against the worker implementation and captured logs before claiming they are fully implemented.

## 1. Structured Events

Worker actions, retries, claim conflicts, and recovery scans should emit structured key-value log entries. Verify that the relevant code paths log these events consistently.

## 2. Traceability

Where applicable, log entries should include:
- `job_id`
- `attempt` or `retry_count`
- `status_prev`
- `status_target`
- An event name and timestamp

State-transition fields must reflect the actual transition rather than a planned or assumed transition.

## 3. Data Safety

Sensitive payload contents, authentication tokens, credentials, and raw secrets must not be written to logs. Log identifiers and safe diagnostic metadata instead. Review exception messages and third-party logging to avoid accidental disclosure.

## 4. Monitoring Scope

The intended scope is diagnostic logging. Metrics dashboards and alerting infrastructure are deferred. Do not describe logs alone as a complete monitoring or alerting system.

## 5. Verification Checklist

- [ ] Worker success and failure paths emit useful structured logs.
- [ ] Retry events include job and attempt identifiers.
- [ ] State transitions record accurate previous and target states.
- [ ] Payloads and secrets are excluded from logs.
- [ ] Recovery events are logged if stale-job recovery is implemented.
- [ ] Tests or captured output demonstrate the expected behavior.

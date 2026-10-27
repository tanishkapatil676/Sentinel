# Sentinel Failure Scenarios & Verification Matrix

> Verification note: The test names and pass statuses below were supplied in project notes. They must be confirmed against the current repository and actual pytest output before being treated as verified evidence.

| Scenario | Safeguard to Verify | Test Status | Evidence / Test Name |
| :--- | :--- | :--- | :--- |
| 1. Duplicate queue message delivery | State guard prevents processing when the job is no longer claimable | Unverified | `test_worker_duplicate_delivery_ignored` |
| 2. Two workers claiming the same job concurrently | Atomic conditional database claim or verified row-level locking | Unverified | `test_concurrent_worker_claims` |
| 3. Delayed message arriving after completion | Terminal-state guard prevents reprocessing | Unverified | `test_delayed_message_post_completion` |
| 4. Stale execution overwriting a result | Status/version check prevents stale writes | Unverified | `test_stale_execution_result_rejection` |
| 5. Terminal job reactivation attempt | State-transition guard prevents terminal-state reactivation | Unverified | `test_terminal_job_reactivation_prevented` |
| 6. Failure handling overwriting success | Conditional failure transition protects completed jobs | Unverified | `test_failure_does_not_overwrite_success` |

# Risk Register

## Mandatory Risks

1. **PostgreSQL or Redis Unavailability**
   - **Likelihood**: Low-Medium | **Impact**: High
   - **Mitigation**: Health-check-backed startup ordering, connection retry loops, and container health probes.
   - **Status**: Verified (Local PoC).

2. **Worker Crashes During Execution**
   - **Likelihood**: Medium | **Impact**: Medium
   - **Mitigation**: Reconnection logic and stale job detection.
   - **Status**: Provisional.

3. **Duplicate Execution**
   - **Likelihood**: Low | **Impact**: Medium
   - **Mitigation**: Database uniqueness constraints and task idempotency design.
   - **Status**: Provisional.

4. **External Side Effects Succeeding Before Outcome Persistence**
   - **Likelihood**: Medium | **Impact**: High
   - **Mitigation**: State updates prior to side-effect invocation.
   - **Status**: Deferred.

5. **Retry Storms or Queue Growth**
   - **Likelihood**: Medium | **Impact**: Medium
   - **Mitigation**: Exponential backoff and maximum attempt thresholds.
   - **Status**: Provisional.

6. **Cross-Client Job Access**
   - **Likelihood**: Medium | **Impact**: High
   - **Mitigation**: Tenant ownership foreign keys and strict authorization filters.
   - **Status**: Deferred.

7. **Sensitive Information Leaking Through Logs**
   - **Likelihood**: Medium | **Impact**: Medium
   - **Mitigation**: Redacting payload data and authorization tokens from logger output.
   - **Status**: Accepted.

8. **Unverified AI-Generated Assumptions**
   - **Likelihood**: Medium | **Impact**: High
   - **Mitigation**: Strict validation against official documentation and unit test verification.
   - **Status**: Verified.

9. **Queue / Database Inconsistency**
   - **Likelihood**: Medium | **Impact**: High
   - **Mitigation**: Transactional boundaries and eventual consistency reconciliation routines.
   - **Status**: Provisional.

10. **Scope Exceeding Available Development Time**
    - **Likelihood**: Medium | **Impact**: High
    - **Mitigation**: Phased milestone execution and strict anti-scope-creep constraints.
    - **Status**: Accepted.

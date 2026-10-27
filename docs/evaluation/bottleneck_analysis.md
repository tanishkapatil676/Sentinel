# Sentinel — Bottleneck Assessment and Regression Verification

**Document:** `docs/evaluation/bottleneck_analysis.md`
**Generated:** 2026-10-27 04:26 UTC
**Regression test command:** `python -m pytest -v tests/unit/ tests/integration/`
**Observed command result:** **FAIL** (exit code 1)

## 1. Bottleneck Hypothesis & Analysis

This section separates plausible explanations from conclusions supported by measurements. Benchmark observations alone do not prove the underlying cause of latency or throughput limits.

### 1.1 API Request Validation & Routing

**Hypothesis:** FastAPI request validation and routing may contribute to request latency, but database operations, transaction commits, queue submission, and worker execution may also contribute.

**Evidence needed:** Compare API request latency with database transaction timings and queue-enqueue timings. Use repeated runs and report sample counts and percentiles. Do not attribute latency to `asyncpg` or FastAPI without component-level measurements.

### 1.2 Database Connection Pool Contention

**Hypothesis:** At higher submission concurrency, database connection-pool contention could increase waiting time and reduce throughput.

**Current evidence limitation:** The failed 50-job benchmark reported zero completed jobs and 50 errors. Its recorded duration was approximately 0.079 seconds. This is a failed run, not a valid throughput measurement, and it does not establish connection-pool saturation as the cause.

**Verification needed:**
- Capture and categorize the errors from the failed run.
- Confirm that the API and its database were healthy during each benchmark.
- Measure connection acquisition wait time, pool utilization, database transaction duration, and database errors.
- Repeat controlled runs at multiple concurrency levels while holding other settings constant.

### 1.3 Queue Polling & HTTP Overhead

**Hypothesis:** The benchmark polling interval (`--poll-interval 0.5`, where used) can affect the observed time at which completion is detected. It may add measurement delay between actual job completion and the next status poll.

This is measurement overhead; it does not by itself prove that queue polling is the dominant system bottleneck.

**Verification needed:** Record worker-side completion timestamps alongside client-observed completion timestamps and compare the results across repeated runs.

## 2. Regression Test Execution

The following command was executed by this report-generation script:

```bash
python -m pytest -v tests/unit/ tests/integration/
```

**Result:** FAIL
**Exit code:** 1

Captured test output:

```text
============================= test session starts ==============================
platform linux -- Python 3.13.16, pytest-8.4.2, pluggy-1.7.0
rootdir: /content/sentinel
configfile: pyproject.toml
plugins: asyncio-1.4.1, langsmith-0.14.11, typeguard-4.6.0, anyio-4.15.1, platformdirs-4.13.5
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 24 items

tests/unit/test_handler.py ....                                          [ 16%]
tests/unit/test_job_retries.py ..                                        [ 25%]
tests/unit/test_jobs_worker.py .........                                 [ 62%]
tests/unit/test_observability.py .                                       [ 66%]
tests/unit/test_recovery.py ..                                           [ 75%]
tests/unit/test_worker.py ....                                           [ 91%]
tests/integration/test_e2e_lifecycle.py F                                [ 95%]
tests/integration/test_job_lifecycle.py .                                [100%]

=================================== FAILURES ===================================
______________________ test_end_to_end_job_lifecycle_flow ______________________

self = <sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_cursor object at 0x7ea12f1a0f20>
operation = 'INSERT INTO jobs (id, name, status, payload, result, error_message, retry_count, max_retries) VALUES ($1::VARCHAR, $2...jobstatus, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::INTEGER, $8::INTEGER) RETURNING jobs.created_at, jobs.updated_at'
parameters = ('e2e-test-job-5494f6c0-7d36-4991-8a0f-513cbe04d776', 'e2e-integration-task', 'PENDING', '{"value": 42}', None, None, ...)

    async def _prepare_and_execute(self, operation, parameters):
        adapt_connection = self._adapt_connection
    
        async with adapt_connection._execute_mutex:
            if adapt_connection._transaction is None:
                await adapt_connection._start_transaction()
    
            if parameters is None:
                parameters = ()
    
            try:
                prepared_stmt, attributes = await adapt_connection._prepare(
                    operation, self._invalidate_schema_cache_asof
                )
    
                if attributes:
                    self._description = [
                        (
                            attr.name,
                            attr.type.oid,
                            None,
                            None,
                            None,
                            None,
                            None,
                        )
                        for attr in attributes
                    ]
                else:
                    self._description = None
    
                if self.server_side:
                    self._cursor = await prepared_stmt.cursor(*parameters)
                    self._rowcount = -1
                else:
>                   self._rows = deque(await prepared_stmt.fetch(*parameters))
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:605: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.13/dist-packages/asyncpg/prepared_stmt.py:177: in fetch
    data = await self.__bind_execute(args, 0, timeout)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/asyncpg/prepared_stmt.py:268: in __bind_execute
    data, status, _ = await self.__do_execute(
/usr/local/lib/python3.13/dist-packages/asyncpg/prepared_stmt.py:257: in __do_execute
    return await executor(protocol)
           ^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

>   ???
E   asyncpg.exceptions.StringDataRightTruncationError: value too long for type character varying(36)

asyncpg/protocol/protocol.pyx:197: StringDataRightTruncationError

The above exception was the direct cause of the following exception:

self = <sqlalchemy.engine.base.Connection object at 0x7ea12f156360>
dialect = <sqlalchemy.dialects.postgresql.asyncpg.PGDialect_asyncpg object at 0x7ea12f879940>
context = <sqlalchemy.dialects.postgresql.asyncpg.PGExecutionContext_asyncpg object at 0x7ea12f15d940>
statement = <sqlalchemy.dialects.postgresql.asyncpg.PGCompiler_asyncpg object at 0x7ea12f1774d0>
parameters = [('e2e-test-job-5494f6c0-7d36-4991-8a0f-513cbe04d776', 'e2e-integration-task', 'PENDING', '{"value": 42}', None, None, ...)]

    def _exec_single_context(
        self,
        dialect: Dialect,
        context: ExecutionContext,
        statement: Union[str, Compiled],
        parameters: Optional[_AnyMultiExecuteParams],
    ) -> CursorResult[Unpack[TupleAny]]:
        """continue the _execute_context() method for a single DBAPI
        cursor.execute() or cursor.executemany() call.
    
        """
        if dialect.bind_typing is BindTyping.SETINPUTSIZES:
            generic_setinputsizes = context._prepare_set_input_sizes()
    
            if generic_setinputsizes:
                try:
                    dialect.do_set_input_sizes(
                        context.cursor, generic_setinputsizes, context
                    )
                except BaseException as e:
                    self._handle_dbapi_exception(
                        e, str(statement), parameters, None, context
                    )
    
        cursor, str_statement, parameters = (
            context.cursor,
            context.statement,
            context.parameters,
        )
    
        effective_parameters: Optional[_AnyExecuteParams]
    
        if not context.executemany:
            effective_parameters = parameters[0]
        else:
            effective_parameters = parameters
    
        evt_handled: bool = False
        try:
            if self._has_events or self.engine._has_events:
                for fn in self.dispatch.before_cursor_execute:
                    str_statement, effective_parameters = fn(
                        self,
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                        context.executemany,
                    )
    
            if self._echo:
                self._log_info(str_statement)
    
                stats = context._get_cache_stats()
    
                if not self.engine.hide_parameters:
                    self._log_info(
                        "[%s] %r",
                        stats,
                        sql_util._repr_params(
                            effective_parameters,
                            batches=10,
                            ismulti=context.executemany,
                        ),
                    )
                else:
                    self._log_info(
                        "[%s] [SQL parameters hidden due to "
                        "hide_parameters=True]",
                        stats,
                    )
            if context.execute_style is ExecuteStyle.EXECUTEMANY:
                effective_parameters = cast(
                    "_CoreMultiExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_executemany:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_executemany(
                        cursor,
                        str_statement,
                        effective_parameters,
                        context,
                    )
            elif not effective_parameters and context.no_parameters:
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute_no_params:
                        if fn(cursor, str_statement, context):
                            evt_handled = True
                            break
                if not evt_handled:
                    self.dialect.do_execute_no_params(
                        cursor, str_statement, context
                    )
            else:
                effective_parameters = cast(
                    "_CoreSingleExecuteParams", effective_parameters
                )
                if self.dialect._has_events:
                    for fn in self.dialect.dispatch.do_execute:
                        if fn(
                            cursor,
                            str_statement,
                            effective_parameters,
                            context,
                        ):
                            evt_handled = True
                            break
                if not evt_handled:
>                   self.dialect.do_execute(
                        cursor, str_statement, effective_parameters, context
                    )

/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1953: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/default.py:1192: in do_execute
    cursor.execute(statement, parameters)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:656: in execute
    await_(self._prepare_and_execute(operation, parameters))
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/concurrency.py:167: in await_
    return current.parent.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/concurrency.py:205: in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:618: in _prepare_and_execute
    self._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:568: in _handle_exception
    self._adapt_connection._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:847: in _handle_exception
    super()._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/connectors/asyncio.py:412: in _handle_exception
    self._handle_exception_no_connection(self.dbapi, error)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_connection'>
dbapi = <sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi object at 0x7ea12fb0b4d0>
error = StringDataRightTruncationError('value too long for type character varying(36)')

    @classmethod
    def _handle_exception_no_connection(
        cls, dbapi: Any, error: Exception
    ) -> NoReturn:
        if not isinstance(error, AsyncAdapt_asyncpg_dbapi.Error):
            exception_mapping = dbapi._asyncpg_error_translate
    
            for super_ in type(error).__mro__:
                if super_ in exception_mapping:
                    message = error.args[0]
                    translated_error = exception_mapping[super_](
                        message, error
                    )
>                   raise translated_error from error
E                   sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.Error: value too long for type character varying(36)

/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:840: Error

The above exception was the direct cause of the following exception:

    @pytest.mark.asyncio
    async def test_end_to_end_job_lifecycle_flow():
        """
        Verifies the end-to-end lifecycle:
        1. Durable job creation in PostgreSQL.
        2. Simulated queue dispatch & worker execution.
        3. Safe state transition to COMPLETED with persisted results.
        """
        job_id = f"e2e-test-job-{uuid.uuid4()}"
    
        # Step 1: Durable registration (simulating API intake)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                job = Job(
                    id=job_id,
                    name="e2e-integration-task",
                    payload="{\"value\": 42}",
                    status=JobStatus.PENDING,
                    retry_count=0,
                    max_retries=3
                )
                session.add(job)
>               await session.commit()

tests/integration/test_e2e_lifecycle.py:30: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/local/lib/python3.13/dist-packages/sqlalchemy/ext/asyncio/session.py:1308: in commit
    await greenlet_spawn(self.sync_session.commit)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/concurrency.py:212: in greenlet_spawn
    result = context.switch(value)
             ^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:2095: in commit
    trans.commit(_to_root=True)
<sqlalchemy generated _go() wrapper for sqlalchemy.orm.session.SessionTransaction.commit>:2: in commit
    return target(fn, self, _to_root=_to_root)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/state_changes.py:137: in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:1330: in commit
    self._prepare_impl()
<sqlalchemy generated _go() wrapper for sqlalchemy.orm.session.SessionTransaction._prepare_impl>:2: in _prepare_impl
    return target(fn, self)
           ^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/state_changes.py:137: in _go
    ret_value = fn(self, *arg, **kw)
                ^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:1304: in _prepare_impl
    self.session.flush()
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:4536: in flush
    self._flush(objects)
<sqlalchemy generated warned() wrapper for sqlalchemy.orm.session.Session._flush>:2: in _flush
    return target(fn, self, objects=objects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/deprecations.py:281: in warned
    return fn(*args, **kwargs)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:4679: in _flush
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/langhelpers.py:166: in __exit__
    raise exc_value.with_traceback(exc_tb)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/session.py:4640: in _flush
    flush_context.execute()
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/unitofwork.py:467: in execute
    rec.execute(self)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/unitofwork.py:643: in execute
    util.preloaded.orm_persistence._save_obj(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/persistence.py:92: in _save_obj
    _emit_insert_statements(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/orm/persistence.py:1237: in _emit_insert_statements
    result = connection.execute(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1458: in execute
    return meth(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/sql/elements.py:533: in _execute_on_connection
    return connection._execute_clauseelement(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1678: in _execute_clauseelement
    ret = self._execute_context(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1832: in _execute_context
    return self._exec_single_context(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1972: in _exec_single_context
    self._handle_dbapi_exception(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:2342: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/base.py:1953: in _exec_single_context
    self.dialect.do_execute(
/usr/local/lib/python3.13/dist-packages/sqlalchemy/engine/default.py:1192: in do_execute
    cursor.execute(statement, parameters)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:656: in execute
    await_(self._prepare_and_execute(operation, parameters))
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/concurrency.py:167: in await_
    return current.parent.switch(awaitable)  # type: ignore[no-any-return]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/util/concurrency.py:205: in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:618: in _prepare_and_execute
    self._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:568: in _handle_exception
    self._adapt_connection._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:847: in _handle_exception
    super()._handle_exception(error)
/usr/local/lib/python3.13/dist-packages/sqlalchemy/connectors/asyncio.py:412: in _handle_exception
    self._handle_exception_no_connection(self.dbapi, error)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

cls = <class 'sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_connection'>
dbapi = <sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi object at 0x7ea12fb0b4d0>
error = StringDataRightTruncationError('value too long for type character varying(36)')

    @classmethod
    def _handle_exception_no_connection(
        cls, dbapi: Any, error: Exception
    ) -> NoReturn:
        if not isinstance(error, AsyncAdapt_asyncpg_dbapi.Error):
            exception_mapping = dbapi._asyncpg_error_translate
    
            for super_ in type(error).__mro__:
                if super_ in exception_mapping:
                    message = error.args[0]
                    translated_error = exception_mapping[super_](
                        message, error
                    )
>                   raise translated_error from error
E                   sqlalchemy.exc.DBAPIError: (sqlalchemy.dialects.postgresql.asyncpg.Error) value too long for type character varying(36)
E                   [SQL: INSERT INTO jobs (id, name, status, payload, result, error_message, retry_count, max_retries) VALUES ($1::VARCHAR, $2::VARCHAR, $3::jobstatus, $4::VARCHAR, $5::VARCHAR, $6::VARCHAR, $7::INTEGER, $8::INTEGER) RETURNING jobs.created_at, jobs.updated_at]
E                   [parameters: ('e2e-test-job-5494f6c0-7d36-4991-8a0f-513cbe04d776', 'e2e-integration-task', 'PENDING', '{"value": 42}', None, None, 0, 3)]
E                   (Background on this error at: https://sqlalche.me/e/21/dbapi)

/usr/local/lib/python3.13/dist-packages/sqlalchemy/dialects/postgresql/asyncpg.py:840: DBAPIError
=========================== short test summary info ============================
FAILED tests/integration/test_e2e_lifecycle.py::test_end_to_end_job_lifecycle_flow
========================= 1 failed, 23 passed in 2.49s =========================
```

A passing result verifies the tests included in this command. It does not establish that every documented failure scenario, production deployment behavior, or real infrastructure failure has been tested.

## 3. Available Benchmark Results

The following table is generated from the benchmark JSON artifacts found in the repository. Durations are in seconds; throughput is in jobs per second.

| Artifact | Requested | Concurrency | Completed | Failed | Timed out | Errors | Duration (s) | Throughput (jobs/s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `benchmark_results_1793074968.json` | 5 | 2 | 5 | 0 | 0 | 0 | 7.269 | 0.688 |
| `benchmark_results_1793075021.json` | 5 | 2 | 5 | 0 | 0 | 0 | 6.789 | 0.736 |
| `benchmark_results_1793075044.json` | 10 | 2 | 10 | 0 | 0 | 0 | 14.482 | 0.691 |
| `benchmark_results_1793075061.json` | 10 | 5 | 10 | 0 | 0 | 0 | 16.154 | 0.619 |
| `benchmark_results_1793075077.json` | 10 | 2 | 10 | 0 | 0 | 0 | 15.513 | 0.645 |
| `benchmark_results_1793075090.json` | 10 | 2 | 10 | 0 | 0 | 0 | 11.885 | 0.841 |

### Incomplete or error-containing runs

- No incomplete or error-containing runs were identified by the available summary fields.

Successful and failed runs must be interpreted separately. A run with zero completed jobs cannot support a successful throughput claim. Error counts should be investigated before drawing conclusions about performance.

## 4. Regression Assessment

- **Automated regression suite:** FAIL for the command and exit code recorded above.
- **Benchmark repeatability:** The artifacts provide multiple observations, but repeated runs under identical conditions are needed to estimate variability.
- **Bottleneck attribution:** Not established by aggregate benchmark results alone.
- **Database pool saturation:** Requires direct pool and database timing evidence.
- **Polling overhead:** Requires comparison of worker completion time and client-detected completion time.
- **Failed high-concurrency run:** Requires error investigation before any performance conclusion is drawn.

## 5. Recommended Follow-Up Experiments

1. Preserve the failed benchmark artifact and capture the corresponding error details.
2. Confirm API, PostgreSQL, and Redis health before each run.
3. Repeat concurrency levels such as 2, 5, and 10 with the same job workload and worker count.
4. Repeat worker-count comparisons with submission concurrency held constant.
5. Record completed jobs, failures, timeouts, throughput, API latency percentiles, end-to-end latency percentiles, and environment settings.
6. Measure database transaction and connection-pool timings before claiming a database bottleneck.
7. Compare worker-side completion timestamps with client-observed completion timestamps to quantify polling delay.
8. Run each configuration multiple times and report the individual results as well as an aggregate; do not hide failed runs.

## 6. Conclusion

This document records the available benchmark artifacts and the observed regression-test result. It treats the database, API, and polling explanations as hypotheses pending targeted measurements. No causal bottleneck conclusion is made from the failed 50-job run alone.

The evidence supports a bounded statement: the automated tests executed by this script returned the status recorded above, and the benchmark artifacts contain both successful and unsuccessful runs. Further instrumentation and repeatable experiments are required before selecting a bottleneck as the primary optimization target.

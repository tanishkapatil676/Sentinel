# Open Questions

| ID | Question | Why it Matters | Status |
|---|---|---|---|
| OQ-01 | What exact retry backoff strategy should RQ enforce for transient failures? | Prevents worker starvation and queue congestion. | Open |
| OQ-02 | How should orphaned jobs stuck in `RUNNING` status be reconciled after worker crashes? | Ensures system self-healing. | Open |
| OQ-03 | What authentication mechanism (JWT vs API keys) will be used for client ownership enforcement? | Secures multi-client isolation. | Open |
| OQ-04 | What specific concurrency levels and workloads will Locust target during benchmarking? | Validates performance bounds without speculation. | Open |

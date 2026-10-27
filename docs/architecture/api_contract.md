# Sentinel REST API Contract

## 1. Endpoint Inventory
1. **`POST /jobs`**: Submit a new asynchronous job for background processing.
2. **`GET /jobs/{job_id}`**: Retrieve current job status, execution metadata, and results.
3. **`GET /jobs`**: List jobs with optional filtering (status, task type) and pagination.
4. **`POST /jobs/{job_id}/retry`**: Manually trigger a retry for a failed job.
5. **`GET /health/live`**: Liveness probe endpoint.
6. **`GET /health/ready`**: Readiness probe checking PostgreSQL and Redis connectivity.

## 2. Detailed Endpoint Specifications

### `POST /jobs`
- **Request Body**:
  ```json
  {
    "task_type": "process_data",
    "payload": {"dataset_id": "12345"},
    "max_attempts": 3
  }

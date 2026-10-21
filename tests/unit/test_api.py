import pytest
from fastapi.testclient import TestClient
from sentinel.main import app

client = TestClient(app)


@pytest.mark.unit
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.unit
def test_create_job_validation():
    # Test validation error on invalid/empty name payload
    response = client.post("/jobs/", json={"name": ""})
    assert response.status_code == 422

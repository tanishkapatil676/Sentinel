import pytest
from pydantic import ValidationError
from sentinel.jobs.handlers import compute_numeric_summary

def test_compute_numeric_summary_valid():
    payload = {"numbers": [10.0, 20.0, 30.0, 40.0]}
    result = compute_numeric_summary(payload)

    assert result["count"] == 4
    assert result["sum"] == 100.0
    assert result["mean"] == 25.0
    assert result["min"] == 10.0
    assert result["max"] == 40.0

def test_compute_numeric_summary_single_value():
    payload = {"numbers": [42.5]}
    result = compute_numeric_summary(payload)

    assert result["count"] == 1
    assert result["sum"] == 42.5
    assert result["mean"] == 42.5
    assert result["min"] == 42.5
    assert result["max"] == 42.5

def test_compute_numeric_summary_empty_raises():
    with pytest.raises(ValidationError):
        compute_numeric_summary({"numbers": []})

def test_compute_numeric_summary_invalid_type_raises():
    with pytest.raises(ValidationError):
        compute_numeric_summary({"numbers": ["not_a_number"]})

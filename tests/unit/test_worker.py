import pytest
from unittest.mock import AsyncMock, patch

from sentinel.tasks.jobs import _decode_payload, process_job


def test_decode_json_payload():
    assert _decode_payload('{"value": 42}') == {"value": 42}


def test_decode_non_json_payload():
    assert _decode_payload("plain text") == "plain text"


def test_decode_existing_object():
    payload = {"value": 42}
    assert _decode_payload(payload) is payload


@pytest.mark.asyncio
async def test_process_job_returns_success_message():
    with patch(
        "sentinel.tasks.jobs.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        result = await process_job("demo", {"value": 1})

    assert result == (
        "Successfully processed job demo. Payload: {'value': 1}"
    )

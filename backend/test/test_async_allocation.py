# tests/test_async_allocation.py
import asyncio
import pytest
from allocation import get_available_channels_sync, process_request

@pytest.mark.asyncio
async def test_get_available_channels_sync_returns_list():
    channels = get_available_channels_sync()
    # Even if the DB is empty, we expect a list
    assert isinstance(channels, list)

@pytest.mark.asyncio
async def test_process_request_handles_no_requests(monkeypatch):
    # Monkey-patch redisRequestClient.get_all to return an empty dict.
    async def fake_get_all():
        return {}
    # Assuming redisRequestClient is imported as part of allocation module:
    from allocation import redisRequestClient
    monkeypatch.setattr(redisRequestClient, "get_all", fake_get_all)
    
    # Run process_request for one cycle
    task = asyncio.create_task(process_request())
    await asyncio.sleep(6)  # wait enough for one iteration
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


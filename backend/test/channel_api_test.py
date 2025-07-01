# tests/test_channel_api.py
import pytest
from fastapi.testclient import TestClient
from main import app


"""change database to test database!"""
client = TestClient(app)

def test_get_all_channels():
    # Call the endpoint that returns all channels
    response = client.get("/api/channel/get/all")
    assert response.status_code == 200
    data = response.json()
    # Expecting a list (possibly empty)
    assert isinstance(data, list)

def test_get_channels_for_user():
    # Use a test username. In a real test, set up a test user in the test DB.
    username = "Jane"
    response = client.get(f"/api/channel/get/{username}")
    assert response.status_code == 200
    data = response.json()
    # Expecting a list of channels
    assert isinstance(data, list)

def test_delete_channel():
    # Test deletion for a channel with id=1. Depending on test DB state, channel may not exist.
    response = client.delete("/api/channel/delete/1")
    # If channel not found, status code 404 is expected
    if response.status_code == 404:
        detail = response.json().get("detail")
        assert detail is not None
    else:
        json_data = response.json()
        assert "Channel deletion successful" in json_data.get("message", "")

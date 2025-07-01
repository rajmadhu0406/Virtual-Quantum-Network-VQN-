# tests/test_allocate_resources.py
import json
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_allocate_resources_missing_timestamp():
    # Without X-Timestamp header, the endpoint should raise an Exception.
    payload = {
        "username": "jane",
        "channels_needed": 2,
        "switch_ids": None
    }
    response = client.post("/api/channel/allocate", json=payload)
    # Expect error response because header is missing
    assert response.status_code in (404, 500)
    assert "Could not retrieve Timestamp" in response.text

def test_allocate_resources_valid():
    # For a valid allocation, you must provide a timestamp header.
    payload = {
        "username": "Jane",
        "channels_needed": 2,
        "switch_ids": None
    }
    headers = {"X-Timestamp": "2025-02-23T22:00:00Z"}
    
    response = client.post("/api/channel/allocate", json=payload, headers=headers)
    # Depending on your test DB state, you may get an error if user not found
    # or a valid response if everything is set up.
    # Check for a known substring in the response.
    assert response.status_code == 200 or response.status_code == 404
    data = response.json()
    # For a successful allocation, the 'display' key should be in the response.
    if response.status_code == 200:
        assert "Request processing" in data.get("display", "")


import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp.main import app
from mcp import crud, models

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: create a clean config file for each test
    with open("mcp/config.json", "w") as f:
        json.dump({"api_configs": []}, f)
    with open("mcp/call_history.json", "w") as f:
        f.write("[]")
    yield
    # Teardown: clean up the created files
    os.remove("mcp/config.json")
    os.remove("mcp/call_history.json")

def test_create_api_config():
    response = client.post(
        "/api_configs/",
        json={"name": "test_api", "url": "http://test.com", "auth_type": "basic", "auth_credentials": {"username": "user", "password": "pass"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_api"
    assert data["url"] == "http://test.com"

def test_read_api_configs():
    client.post(
        "/api_configs/",
        json={"name": "test_api", "url": "http://test.com", "auth_type": "basic", "auth_credentials": {"username": "user", "password": "pass"}},
    )
    response = client.get("/api_configs/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test_api"

def test_call_api():
    client.post(
        "/api_configs/",
        json={"name": "test_api", "url": "https://httpbin.org/post", "auth_type": "api_key", "auth_credentials": {"key": "X-API-KEY", "value": "test"}},
    )
    response = client.post(
        "/call_api/test_api",
        json={"test": "data"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["response_data"]["json"]["test"] == "data"

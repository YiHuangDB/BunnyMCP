# MCP Module

This module provides a generic context protocol for LLMs to interact with third-party REST APIs.

## Running the application

1. Install the dependencies:
```bash
pip install "fastapi[all]" httpx PyYAML
```

2. Run the application:
```bash
uvicorn mcp.main:app --reload
```

## API Usage

### Create an API Config

```bash
curl -X POST "http://127.0.0.1:8000/api_configs/" -H "Content-Type: application/json" -d '{
  "name": "my_api",
  "url": "https://httpbin.org/post",
  "auth_type": "api_key",
  "auth_credentials": {
    "key": "X-API-KEY",
    "value": "my_secret_key"
  }
}'
```

### Call an API

```bash
curl -X POST "http://127.0.0.1:8000/call_api/my_api" -H "Content-Type: application/json" -d '{
  "some_key": "some_value"
}'
```

### Get Call History

```bash
curl -X GET "http://127.0.0.1:8000/call_history/"
```

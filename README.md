# MCP Module

This module provides a generic context protocol for LLMs to interact with third-party REST APIs.

## Installation

### Prerequisites

* Python 3.11 or higher
* A virtual environment tool (e.g., `venv`)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd mcp-module
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install the package:**
    ```bash
    pip install -e .
    ```

## Configuration

1.  **Create a `config.json` file in the `mcp` directory.** This file will store the configurations for the APIs you want to connect to.

2.  **Add API configurations to the `config.json` file.** The file should contain a list of API configurations, where each configuration is a JSON object with the following fields:
    *   `name`: A unique name for the API configuration.
    *   `url`: The base URL of the API.
    *   `auth_type`: The authentication type. Supported values are `basic` and `api_key`.
    *   `auth_credentials`: A JSON object containing the authentication credentials.
        *   For `basic` authentication, this should contain `username` and `password` fields.
        *   For `api_key` authentication, this should contain `key` and `value` fields, where `key` is the name of the API key header and `value` is the API key itself.

    **Example `config.json`:**
    ```json
    {
      "api_configs": [
        {
          "name": "my_api",
          "url": "https://httpbin.org/post",
          "auth_type": "api_key",
          "auth_credentials": {
            "key": "X-API-KEY",
            "value": "my_secret_key"
          }
        },
        {
          "name": "another_api",
          "url": "https://api.example.com",
          "auth_type": "basic",
          "auth_credentials": {
            "username": "my_username",
            "password": "my_password"
          }
        }
      ]
    }
    ```

## Usage

### Running the application

1.  **Run the application using `uvicorn`:**
    ```bash
    uvicorn mcp.main:app --reload
    ```

### API Usage

*   **Create an API Config:**
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

*   **Call an API:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/call_api/my_api" -H "Content-Type: application/json" -d '{
      "some_key": "some_value"
    }'
    ```

*   **Get Call History:**
    ```bash
    curl -X GET "http://127.0.0.1:8000/call_history/"
    ```

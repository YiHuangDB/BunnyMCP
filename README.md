# Universal REST API to MCP Tool Gateway

This project implements a universal REST API to MCP Tool Gateway, as specified in the requirements document.

The gateway includes the following features:

- **MCP Gateway Service:** A stateless service that acts as the entry point for AI agents, handling the MCP protocol and orchestrating API calls.
- **Tool Configuration Service:** A RESTful API for managing tool configurations, including CRUD operations for tools and their authentication settings.
- **Secure Credential Vault:** Integration with HashiCorp Vault for secure storage and retrieval of API credentials.
- **Execution Engine:** A dedicated service for executing API calls, with just-in-time credential retrieval and support for various authentication methods.
- **Call History and Audit Service:** A service for logging all API calls and administrative actions, providing a persistent and immutable audit trail.
- **Role-Based Access Control (RBAC):** A basic RBAC system for the management API to enforce the principle of least privilege.
- **Advanced Querying:** Advanced querying capabilities for the Tool Configuration and Call History services.
- **Monitoring and Alerting:** A Prometheus-compatible `/metrics` endpoint for monitoring API latency, error rates, and other key metrics.

## Installation

### Prerequisites

* Python 3.11 or higher
* A virtual environment tool (e.g., `venv`)
* Docker and Docker Compose (for running the database and vault)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd gateway
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -e .
    ```

4.  **Start the database and vault using Docker Compose:**
    ```bash
    docker-compose up -d
    ```
    This will start a PostgreSQL database and a HashiCorp Vault instance in the background.

## Configuration

1.  **Set the environment variables.** The application requires the following environment variables to be set:
    *   `DATABASE_URL`: The URL of the PostgreSQL database.
    *   `VAULT_URL`: The URL of the HashiCorp Vault instance.
    *   `VAULT_TOKEN`: The token for authenticating with HashiCorp Vault.

    A `.env.example` file is provided with the default values for the Docker Compose setup. You can copy this file to `.env` and modify it as needed:
    ```bash
    cp .env.example .env
    ```

2.  **Run the database migrations.** The first time you run the application, you will need to create the database tables. You can do this by running the following command:
    ```bash
    python -c "from gateway.tool_configuration.database import Base, engine; Base.metadata.create_all(bind=engine)"
    ```

## Usage

### Running the application

1.  **Run the application using `uvicorn`:**
    ```bash
    uvicorn gateway.tool_configuration.main:app --reload
    ```

### Running the tests

1.  **Run the tests using `pytest`:**
    ```bash
    pytest
    ```

## MCP Client Configuration

To connect to the gateway, an MCP client needs to be configured with the following information:

*   **Host:** The hostname or IP address of the gateway.
*   **Port:** The port that the gateway is listening on.
*   **Authentication:** The client will need to authenticate with the gateway using a JWT. The JWT can be obtained from the `/token` endpoint of the management API.

The client should send the JWT in the `Authorization` header of the `initialize` request, using the `Bearer` scheme. For example:

```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "0.1",
    "capabilities": {
      "tools": true
    }
  },
  "id": 1,
  "headers": {
    "Authorization": "Bearer <your_jwt>"
  }
}
```

## Integration with Claude Desktop

To configure the gateway in Claude Desktop, you will need to edit the `claude_desktop_config.json` file. On macOS, this file is located at `~/Library/Application Support/Claude/claude_desktop_config.json`.

Add a new entry to the `mcpServers` object with the following configuration:

```json
{
  "mcpServers": {
    "My Gateway": {
      "command": "uvicorn",
      "args": [
        "gateway.tool_configuration.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000"
      ],
      "env": {
        "DATABASE_URL": "postgresql://user:password@localhost/mcp_gateway",
        "VAULT_URL": "http://localhost:8200",
        "VAULT_TOKEN": "root"
      }
    }
  }
}
```

**Note:** The `command` and `args` in this example assume that `uvicorn` is in your system's `PATH`. If you are using a virtual environment, you will need to provide the full path to the `uvicorn` executable in your virtual environment (e.g., `/path/to/your/project/.venv/bin/uvicorn`).

Restart Claude Desktop to apply the changes.

### Authentication Configuration

The gateway supports two types of authentication: API Key and Basic Auth. The authentication type is configured in the `ToolConfiguration` object.

#### API Key Authentication

To use API Key authentication, set the `auth_type` to `API_KEY` and provide the API key details in the `api_key_details` field. The `api_key_details` field should be a JSON object with the following fields:

*   `in`: The location of the API key. Supported values are `header` and `query`.
*   `name`: The name of the API key header or query parameter.

**Example:**

```json
{
  "name": "my_api",
  "url": "https://httpbin.org/post",
  "auth_type": "API_KEY",
  "auth_credentials": {
    "key": "X-API-KEY",
    "value": "my_secret_key"
  },
  "api_key_details": {
    "in": "header",
    "name": "X-API-KEY"
  }
}
```

#### Basic Authentication

To use Basic Authentication, set the `auth_type` to `BASIC_AUTH`. The `auth_credentials` field should be a JSON object with `username` and `password` fields.

**Example:**

```json
{
  "name": "another_api",
  "url": "https://api.example.com",
  "auth_type": "BASIC_AUTH",
  "auth_credentials": {
    "username": "my_username",
    "password": "my_password"
  }
}
```

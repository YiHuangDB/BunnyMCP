import httpx
from gateway.tool_configuration.models import ToolConfiguration, AuthenticationConfiguration
from gateway.tool_configuration.vault import VaultClient

class ExecutionEngine:
    def __init__(self, vault_client: VaultClient):
        self.vault_client = vault_client

    async def execute(
        self,
        tool_config: ToolConfiguration,
        auth_config: AuthenticationConfiguration,
        params: dict,
    ) -> httpx.Response:
        credentials = self.vault_client.read_secret(auth_config.credential_vault_path)
        headers = self._get_headers(auth_config, credentials)
        auth = self._get_auth(auth_config, credentials)
        url = self._get_url(tool_config, params)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=tool_config.target_api_method,
                url=url,
                headers=headers,
                auth=auth,
                json=params.get("body"),
            )
        return response

    def _get_headers(self, auth_config: AuthenticationConfiguration, credentials: dict) -> dict:
        headers = {}
        if auth_config.auth_type == "API_KEY":
            key_details = auth_config.api_key_details
            if key_details["in"] == "header":
                headers[key_details["name"]] = credentials["api_key"]
        return headers

    def _get_auth(self, auth_config: AuthenticationConfiguration, credentials: dict):
        if auth_config.auth_type == "BASIC_AUTH":
            return httpx.BasicAuth(credentials["username"], credentials["password"])
        return None

    def _get_url(self, tool_config: ToolConfiguration, params: dict) -> str:
        url = tool_config.target_api_url_template
        for key, value in params.get("path", {}).items():
            url = url.replace(f"{{{key}}}", str(value))

        query_params = []
        for key, value in params.get("query", {}).items():
            query_params.append(f"{key}={value}")
        if query_params:
            url += "?" + "&".join(query_params)

        return url

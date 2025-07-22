import hvac

class VaultClient:
    def __init__(self, vault_url: str, vault_token: str):
        self.client = hvac.Client(url=vault_url, token=vault_token)

    def write_secret(self, path: str, secret: dict):
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=secret,
        )

    def read_secret(self, path: str) -> dict:
        read_response = self.client.secrets.kv.v2.read_secret_version(
            path=path,
        )
        return read_response["data"]["data"]

    def delete_secret(self, path: str):
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path,
        )

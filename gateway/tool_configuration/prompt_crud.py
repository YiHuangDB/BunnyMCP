from sqlalchemy.orm import Session
from . import models, database, vault
import uuid

def create_tool_from_prompt(
    db: Session,
    vault_client: vault.VaultClient,
    owner_id: uuid.UUID,
    mcp_tool_name: str,
    mcp_tool_description: str,
    target_api_method: str,
    target_api_url_template: str,
    parameter_mappings: dict,
    auth_type: str,
    raw_credentials: dict,
    api_key_details: dict = None,
):
    # Create the authentication configuration
    auth_config = models.AuthenticationConfiguration(
        auth_type=auth_type,
        credential_vault_path="",  # Will be updated after storing in vault
        api_key_details=api_key_details,
    )
    db_auth_config = database.AuthenticationConfiguration(**auth_config.dict())
    db.add(db_auth_config)
    db.commit()
    db.refresh(db_auth_config)

    # Store the raw credentials in the vault
    vault_path = f"secret/data/{owner_id}/{db_auth_config.id}"
    vault_client.write_secret(path=vault_path, secret=raw_credentials)

    # Update the authentication configuration with the vault path
    db_auth_config.credential_vault_path = vault_path
    db.commit()

    # Create the tool configuration
    tool_config = models.ToolConfiguration(
        owner_id=owner_id,
        mcp_tool_name=mcp_tool_name,
        mcp_tool_description=mcp_tool_description,
        target_api_method=target_api_method,
        target_api_url_template=target_api_url_template,
        parameter_mappings=parameter_mappings,
        authentication_config_id=db_auth_config.id,
    )
    db_tool_config = database.ToolConfiguration(**tool_config.dict())
    db.add(db_tool_config)
    db.commit()
    db.refresh(db_tool_config)

    return db_tool_config

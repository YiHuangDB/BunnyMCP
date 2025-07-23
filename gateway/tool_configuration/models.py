import uuid
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from enum import Enum
import datetime

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class AuthType(str, Enum):
    API_KEY = "API_KEY"
    BASIC_AUTH = "BASIC_AUTH"

class Parameter(BaseModel):
    name: str
    required: bool = False
    default: Any | None = None
    options: List[str] | None = None

class ToolConfiguration(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    owner_id: uuid.UUID
    mcp_tool_name: str
    mcp_tool_description: str
    target_api_method: HttpMethod
    target_api_url_template: str
    parameter_mappings: Dict[str, List[Parameter]]
    authentication_config_id: uuid.UUID
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

class AuthenticationConfiguration(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    auth_type: AuthType
    credential_vault_path: str
    api_key_details: Dict[str, Any] | None = None

class CallRecord(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tool_configuration_id: uuid.UUID
    request_timestamp: datetime.datetime
    request_arguments: Dict[str, Any]
    response_status_code: int
    response_body: str
    was_successful: bool
    duration_ms: int

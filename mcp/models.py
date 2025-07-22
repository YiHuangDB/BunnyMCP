from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import datetime

class AuthType(str, Enum):
    BASIC = "basic"
    API_KEY = "api_key"

class APIConfig(BaseModel):
    name: str
    url: str
    auth_type: AuthType
    auth_credentials: Dict[str, str]

class APIConfigIn(BaseModel):
    name: str
    url: str
    auth_type: AuthType
    auth_credentials: Dict[str, str]

class CallStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class APICall(BaseModel):
    task_id: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    request_data: Dict[str, Any]
    response_data: Optional[Dict[str, Any]] = None
    status: CallStatus
    error_message: Optional[str] = None

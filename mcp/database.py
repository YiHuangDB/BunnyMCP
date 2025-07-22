import json
from typing import List, Dict, Any
from . import models
from .models import APIConfig

CONFIG_FILE = "mcp/config.json"

def load_config() -> Dict[str, Any]:
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f) or {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_config(config: Dict[str, Any]):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_api_configs() -> List[APIConfig]:
    config = load_config()
    return [APIConfig(**c) for c in config.get("api_configs", [])]

def get_api_config(name: str) -> APIConfig:
    configs = get_api_configs()
    for config in configs:
        if config.name == name:
            return config
    return None

def save_api_call(api_call: "models.APICall"):
    def default(o):
        if isinstance(o, models.datetime.datetime):
            return o.isoformat()
        raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')

    try:
        with open("mcp/call_history.json", 'r+') as f:
            history = json.load(f)
            history.append(api_call.model_dump())
            f.seek(0)
            json.dump(history, f, indent=4, default=default)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("mcp/call_history.json", 'w') as f:
            json.dump([api_call.model_dump()], f, indent=4, default=default)

def get_call_history() -> List["models.APICall"]:
    try:
        with open("mcp/call_history.json", 'r') as f:
            history_data = json.load(f)
            return [models.APICall(**call) for call in history_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

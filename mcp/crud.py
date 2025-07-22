from typing import List
from . import models, database

def create_api_config(api_config: models.APIConfigIn) -> models.APIConfig:
    config = database.load_config()
    if "api_configs" not in config:
        config["api_configs"] = []

    new_config = models.APIConfig(**api_config.model_dump())
    config["api_configs"].append(new_config.model_dump(mode='json'))
    database.save_config(config)
    return new_config

def get_api_configs() -> List[models.APIConfig]:
    return database.get_api_configs()

def get_api_config(name: str) -> models.APIConfig:
    return database.get_api_config(name)

def update_api_config(name: str, api_config: models.APIConfigIn) -> models.APIConfig:
    config = database.load_config()
    if "api_configs" not in config:
        return None

    for i, c in enumerate(config["api_configs"]):
        if c["name"] == name:
            updated_config = models.APIConfig(**api_config.model_dump())
            config["api_configs"][i] = updated_config.model_dump(mode='json')
            database.save_config(config)
            return updated_config
    return None

def delete_api_config(name: str) -> bool:
    config = database.load_config()
    if "api_configs" not in config:
        return False

    original_len = len(config["api_configs"])
    config["api_configs"] = [c for c in config["api_configs"] if c["name"] != name]

    if len(config["api_configs"]) < original_len:
        database.save_config(config)
        return True
    return False

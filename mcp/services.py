import httpx
import uuid
import logging
from . import models, crud, database

logger = logging.getLogger(__name__)

async def call_api(config_name: str, request_data: dict):
    logger.info(f"Calling API with config: {config_name}")
    api_config = crud.get_api_config(config_name)
    if not api_config:
        logger.error(f"API Config not found: {config_name}")
        raise ValueError("API Config not found")

    task_id = str(uuid.uuid4())
    api_call = models.APICall(task_id=task_id, request_data=request_data, status=models.CallStatus.ERROR)

    try:
        auth = None
        if api_config.auth_type == models.AuthType.BASIC:
            auth = httpx.BasicAuth(api_config.auth_credentials["username"], api_config.auth_credentials["password"])
        elif api_config.auth_type == models.AuthType.API_KEY:
            # Assuming api key is sent in a header
            headers = {api_config.auth_credentials["key"]: api_config.auth_credentials["value"]}
        else:
            headers = {}

        async with httpx.AsyncClient() as client:
            response = await client.post(api_config.url, json=request_data, auth=auth, headers=headers)
            response.raise_for_status()
            api_call.response_data = response.json()
            api_call.status = models.CallStatus.SUCCESS
    except httpx.HTTPStatusError as e:
        api_call.error_message = str(e)
        api_call.response_data = e.response.json()
    except Exception as e:
        api_call.error_message = str(e)

    database.save_api_call(api_call)
    return api_call

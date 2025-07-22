from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict
from . import crud, models, services
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the MCP Module"}

@app.post("/api_configs/", response_model=models.APIConfig)
def create_api_config(api_config: models.APIConfigIn):
    return crud.create_api_config(api_config)

@app.get("/api_configs/", response_model=List[models.APIConfig])
def read_api_configs():
    return crud.get_api_configs()

@app.get("/api_configs/{name}", response_model=models.APIConfig)
def read_api_config(name: str):
    db_config = crud.get_api_config(name)
    if db_config is None:
        raise HTTPException(status_code=404, detail="API Config not found")
    return db_config

@app.put("/api_configs/{name}", response_model=models.APIConfig)
def update_api_config(name: str, api_config: models.APIConfigIn):
    updated_config = crud.update_api_config(name, api_config)
    if updated_config is None:
        raise HTTPException(status_code=404, detail="API Config not found")
    return updated_config

@app.delete("/api_configs/{name}")
def delete_api_config(name: str):
    if not crud.delete_api_config(name):
        raise HTTPException(status_code=404, detail="API Config not found")
    return {"message": "API Config deleted successfully"}

@app.post("/call_api/{config_name}", response_model=models.APICall)
async def call_api(config_name: str, request_data: Dict):
    try:
        return await services.call_api(config_name, request_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/call_history/", response_model=List[models.APICall])
def get_call_history():
    return database.get_call_history()

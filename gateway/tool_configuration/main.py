from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, database, vault, security, monitoring, history_crud
from typing import List
import uuid
import os
from datetime import timedelta
from starlette.responses import Response
from prometheus_client import generate_latest

from sqlalchemy import inspect

def check_db_initialized():
    inspector = inspect(database.engine)
    if not inspector.has_table("tool_configurations"):
        models.Base.metadata.create_all(bind=database.engine)

check_db_initialized()

app = FastAPI()

def get_vault_client():
    return vault.VaultClient(
        vault_url=os.environ.get("VAULT_URL"),
        vault_token=os.environ.get("VAULT_TOKEN"),
    )

def get_current_user_role(current_user: models.User = Depends(security.get_current_active_user)):
    return current_user.role

@app.post("/tools/", response_model=models.ToolConfiguration)
def create_tool(tool: models.ToolConfiguration, db: Session = Depends(database.get_db), role: str = Depends(get_current_user_role)):
    if role not in [rbac.Role.ADMIN, rbac.Role.EDITOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.create_tool_configuration(db=db, tool_config=tool)

@app.get("/tools/", response_model=List[models.ToolConfiguration])
def read_tools(
    name_contains: str = None,
    method: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    role: str = Depends(get_current_user_role),
):
    return crud.get_tool_configurations(
        db, name_contains=name_contains, method=method, skip=skip, limit=limit
    )

@app.get("/tools/{tool_id}", response_model=models.ToolConfiguration)
def read_tool(tool_id: uuid.UUID, db: Session = Depends(database.get_db), role: str = Depends(get_current_user_role)):
    db_tool = crud.get_tool_configuration(db, tool_id=tool_id)
    if db_tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool

@app.put("/tools/{tool_id}", response_model=models.ToolConfiguration)
def update_tool(tool_id: uuid.UUID, tool: models.ToolConfiguration, db: Session = Depends(database.get_db), role: str = Depends(get_current_user_role)):
    if role not in [rbac.Role.ADMIN, rbac.Role.EDITOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.update_tool_configuration(db=db, tool_id=tool_id, tool_config=tool)

@app.delete("/tools/{tool_id}", response_model=models.ToolConfiguration)
def delete_tool(tool_id: uuid.UUID, db: Session = Depends(database.get_db), role: str = Depends(get_current_user_role)):
    if role != rbac.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.delete_tool_configuration(db=db, tool_id=tool_id)

@app.post("/tools/{tool_id}/authentication/", response_model=models.AuthenticationConfiguration)
def create_authentication(
    tool_id: uuid.UUID,
    auth: models.AuthenticationConfiguration,
    raw_credentials: dict,
    db: Session = Depends(database.get_db),
    vault_client: vault.VaultClient = Depends(get_vault_client),
):
    db_tool = crud.get_tool_configuration(db, tool_id=tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Store the raw credentials in the vault
    vault_path = f"secret/data/{db_tool.owner_id}/{tool_id}"
    vault_client.write_secret(path=vault_path, secret=raw_credentials)

    # Create the authentication configuration with the vault path
    auth.credential_vault_path = vault_path
    db_auth = crud.create_authentication_configuration(db=db, auth_config=auth)
    db_tool.authentication_config_id = db_auth.id
    db.commit()
    return db_auth

@app.post("/token", response_model=security.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/history/", response_model=models.CallRecord)
def create_call_record(call_record: models.CallRecord, db: Session = Depends(database.get_db)):
    return history_crud.create_call_record(db=db, call_record=call_record)

@app.get("/history/", response_model=List[models.CallRecord])
def read_call_records(
    tool_id: uuid.UUID = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    was_successful: bool = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    return history_crud.get_call_records(
        db,
        tool_id=tool_id,
        start_date=start_date,
        end_date=end_date,
        was_successful=was_successful,
        skip=skip,
        limit=limit,
    )

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

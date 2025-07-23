from sqlalchemy.orm import Session
from . import models, database
import uuid

def create_tool_configuration(db: Session, tool_config: models.ToolConfiguration):
    db_tool_config = database.ToolConfiguration(**tool_config.dict())
    db.add(db_tool_config)
    db.commit()
    db.refresh(db_tool_config)
    return db_tool_config

def get_tool_configuration(db: Session, tool_id: uuid.UUID):
    return db.query(database.ToolConfiguration).filter(database.ToolConfiguration.id == tool_id).first()

def get_tool_configurations(
    db: Session,
    name_contains: str = None,
    method: str = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(database.ToolConfiguration)
    if name_contains:
        query = query.filter(database.ToolConfiguration.mcp_tool_name.contains(name_contains))
    if method:
        query = query.filter(database.ToolConfiguration.target_api_method == method)
    return query.offset(skip).limit(limit).all()

def update_tool_configuration(db: Session, tool_id: uuid.UUID, tool_config: models.ToolConfiguration):
    db_tool_config = db.query(database.ToolConfiguration).filter(database.ToolConfiguration.id == tool_id).first()
    if db_tool_config:
        for key, value in tool_config.dict().items():
            setattr(db_tool_config, key, value)
        db.commit()
        db.refresh(db_tool_config)
    return db_tool_config

def delete_tool_configuration(db: Session, tool_id: uuid.UUID):
    db_tool_config = db.query(database.ToolConfiguration).filter(database.ToolConfiguration.id == tool_id).first()
    if db_tool_config:
        db.delete(db_tool_config)
        db.commit()
    return db_tool_config

def create_authentication_configuration(db: Session, auth_config: models.AuthenticationConfiguration):
    db_auth_config = database.AuthenticationConfiguration(**auth_config.dict())
    db.add(db_auth_config)
    db.commit()
    db.refresh(db_auth_config)
    return db_auth_config

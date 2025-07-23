from sqlalchemy.orm import Session
from . import models, database
import uuid
import datetime

def create_call_record(db: Session, call_record: models.CallRecord):
    db_call_record = database.CallRecord(**call_record.dict())
    db.add(db_call_record)
    db.commit()
    db.refresh(db_call_record)
    return db_call_record

def get_call_records(
    db: Session,
    tool_id: uuid.UUID = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    was_successful: bool = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(database.CallRecord)
    if tool_id:
        query = query.filter(database.CallRecord.tool_configuration_id == tool_id)
    if start_date:
        query = query.filter(database.CallRecord.request_timestamp >= start_date)
    if end_date:
        query = query.filter(database.CallRecord.request_timestamp <= end_date)
    if was_successful is not None:
        query = query.filter(database.CallRecord.was_successful == was_successful)
    return query.offset(skip).limit(limit).all()

def get_call_records_by_tool_name(db: Session, tool_name: str, skip: int = 0, limit: int = 100):
    return db.query(database.CallRecord).join(database.ToolConfiguration).filter(database.ToolConfiguration.mcp_tool_name == tool_name).offset(skip).limit(limit).all()

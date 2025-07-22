from sqlalchemy import create_engine, Column, String, DateTime, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid
import datetime

DATABASE_URL = "postgresql://user:password@localhost/mcp_gateway"

Base = declarative_base()

class ToolConfiguration(Base):
    __tablename__ = "tool_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    mcp_tool_name = Column(String, nullable=False)
    mcp_tool_description = Column(String)
    target_api_method = Column(String, nullable=False)
    target_api_url_template = Column(String, nullable=False)
    parameter_mappings = Column(JSON, nullable=False)
    authentication_config_id = Column(UUID(as_uuid=True), ForeignKey("authentication_configurations.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    authentication_configuration = relationship("AuthenticationConfiguration")

class AuthenticationConfiguration(Base):
    __tablename__ = "authentication_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_type = Column(String, nullable=False)
    credential_vault_path = Column(String, nullable=False)
    api_key_details = Column(JSON)

class CallRecord(Base):
    __tablename__ = "call_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_configuration_id = Column(UUID(as_uuid=True), ForeignKey("tool_configurations.id"))
    request_timestamp = Column(DateTime, nullable=False)
    request_arguments = Column(JSON)
    response_status_code = Column(Integer)
    response_body = Column(String)
    was_successful = Column(Boolean)
    duration_ms = Column(Integer)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

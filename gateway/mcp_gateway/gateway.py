from mcp_sdk import "MCPServer, MCPConnection, Tool"
from gateway.tool_configuration.crud import get_tool_configuration, get_tool_configurations
from gateway.execution_engine.engine import ExecutionEngine
from gateway.tool_configuration.database import SessionLocal
from gateway.tool_configuration import prompt_crud, history_crud
import json
import uuid

class Gateway(MCPServer):
    def __init__(self, execution_engine: ExecutionEngine):
        super().__init__()
        self.execution_engine = execution_engine

    async def handle_tools_call(self, connection: "MCPConnection", name: str, arguments: any) -> any:
        db = SessionLocal()
        try:
            tool_config = get_tool_configuration(db, name)
            if not tool_config:
                return {"error": "Tool not found"}

            auth_config = tool_config.authentication_configuration
            response = await self.execution_engine.execute(tool_config, auth_config, arguments)

            # Log the call
            # ...

            return {
                "content": response.text,
                "isError": response.is_error,
            }
        finally:
            db.close()

    async def handle_get_call_history_by_tool_name(self, connection: "MCPConnection", arguments: any) -> any:
        db = SessionLocal()
        try:
            call_records = history_crud.get_call_records_by_tool_name(
                db=db,
                tool_name=arguments["tool_name"],
                skip=arguments.get("skip", 0),
                limit=arguments.get("limit", 100),
            )
            return {
                "content": [record.__dict__ for record in call_records],
                "isError": False,
            }
        finally:
            db.close()

    async def handle_tools_list(self, connection: "MCPConnection") -> list["Tool"]:
        db = SessionLocal()
        try:
            tool_configs = get_tool_configurations(db)
            tools = []
            for tool_config in tool_configs:
                tools.append(
                    Tool(
                        name=tool_config.mcp_tool_name,
                        description=tool_config.mcp_tool_description,
                        inputSchema=self._generate_input_schema(tool_config.parameter_mappings),
                    )
                )
            tools.append(
                Tool(
                    name="create_tool_from_prompt",
                    description="Create a new tool from a prompt.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mcp_tool_name": {"type": "string"},
                            "mcp_tool_description": {"type": "string"},
                            "target_api_method": {"type": "string"},
                            "target_api_url_template": {"type": "string"},
                            "parameter_mappings": {"type": "object"},
                            "auth_type": {"type": "string"},
                            "raw_credentials": {"type": "object"},
                            "api_key_details": {"type": "object"},
                        },
                    },
                )
            )
            tools.append(
                Tool(
                    name="get_call_history_by_tool_name",
                    description="Get the call history for a specific tool.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tool_name": {"type": "string"},
                            "skip": {"type": "integer"},
                            "limit": {"type": "integer"},
                        },
                    },
                )
            )
            return tools
        finally:
            db.close()

    def _generate_input_schema(self, parameter_mappings: dict) -> dict:
        schema = {"type": "object", "properties": {}, "required": []}
        for param_type, params in parameter_mappings.items():
            for param in params:
                param_schema = {"type": "string"}
                if param.default:
                    param_schema["default"] = param.default
                if param.options:
                    param_schema["enum"] = param.options
                schema["properties"][param.name] = param_schema
                if param.required:
                    schema["required"].append(param.name)
        return schema

    async def handle_create_tool_from_prompt(self, connection: "MCPConnection", arguments: any) -> any:
        db = SessionLocal()
        try:
            # In a real application, the owner_id would come from the authenticated user
            owner_id = uuid.uuid4()

            tool_config = prompt_crud.create_tool_from_prompt(
                db=db,
                vault_client=self.execution_engine.vault_client,
                owner_id=owner_id,
                **arguments,
            )
            return {
                "content": f"Tool '{tool_config.mcp_tool_name}' created successfully.",
                "isError": False,
            }
        finally:
            db.close()

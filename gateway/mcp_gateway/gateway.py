from mcp_sdk import "MCPServer, MCPConnection, Tool"
from gateway.tool_configuration.crud import get_tool_configuration, get_tool_configurations
from gateway.execution_engine.engine import ExecutionEngine
from gateway.tool_configuration.database import SessionLocal
import json

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
            return tools
        finally:
            db.close()

    def _generate_input_schema(self, parameter_mappings: dict) -> dict:
        schema = {"type": "object", "properties": {}}
        for param_type, params in parameter_mappings.items():
            if param_type == "path":
                for param in params:
                    schema["properties"][param] = {"type": "string"}
            elif param_type == "query":
                for param in params:
                    schema["properties"][param] = {"type": "string"}
            elif param_type == "body" and params == "all":
                schema["properties"]["body"] = {"type": "object"}
        return schema

# phase2/sprint2/src/orchestrator.py

class ToolOrchestrator:
    def __init__(self):
        self._tools = {}
        self._tool_schemas = []

    def register_tool(self, tool_schema: dict):
        """
        Register a tool schema.
        """
        function_name = tool_schema['function']['name']
        if function_name in self._tools:
            print(f"⚠️ Warning: Tool '{function_name}' already exists. Overriding.")
        
        self._tools[function_name] = tool_schema
        self._tool_schemas = list(self._tools.values())
        print(f"   - Successfully registered tool: {function_name}")
    
    def register_tools(self, tool_schemas: list):
        """
        Register a list of tool schemas.
        """
        for tool in tool_schemas:
            self.register_tool(tool)

    def get_all_tool_schemas(self) -> list:
        """
        Get a list of all tool schemas to pass to the LLM.
        """
        return self._tool_schemas

    def get_tool(self, name: str) -> dict:
        """
        Get a specific tool schema by name.
        """
        return self._tools.get(name)

    @property
    def available_tools_count(self) -> int:
        return len(self._tools)
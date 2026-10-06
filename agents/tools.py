class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register_tool(self, name, description, allowed_roles, function):

        self.tools[name] = {
            "description": description,
            "allowed_roles": allowed_roles,
            "function": function
        }

    def discover_tools(self):

        return self.tools

    def execute_tool(self, name, role, **kwargs):

        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found.")

        tool = self.tools[name]

        # Role-based authorization
        if role not in tool["allowed_roles"]:
            raise PermissionError(
                f"Access denied: {role} cannot use {name}"
            )

        return tool["function"](**kwargs)
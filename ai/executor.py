from ai.tools import ToolRegistry
from typing import Any

class ExecutionContext:
    """
        Creates a dictionary to store the results of each tool call as an execution context
        to be used by other tools
    """
    def __init__(self, query):
        self.data = {"query": query}
    
    def set(self, key: str, value: Any):
        self.data[key] = value
    
    def get(self, key: str):
        return self.data[key]

class Executor:
    """
        Executes the plan created by calling all the tools listed in the plan
    """
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def execute(self, query, plan):
        
        context = ExecutionContext(query=query)

        for step in plan.steps:
            # For each step in the plan we get the tool and link it to the tool in ToolRegistry
            tool = self.registry.get(step.tool)
            # For each tool we find the list of parameters needed and get the parameter values
            # from the execution context
            kwargs = {parameter: context.get(parameter) for parameter in tool.parameters}
            result = await tool.execute(**kwargs)
            for key, value in result.items():
                context.set(key, value)
        # We return the last value received as the final answer
        return value
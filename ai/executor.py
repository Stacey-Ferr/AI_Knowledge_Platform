from ai.tools import ToolRegistry
from typing import Any
from opentelemetry import trace

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
        self.tracer = trace.get_tracer("agent_executor")

    async def execute(self, query, plan):
        with self.tracer.start_as_current_span("agent.ask") as agent_span:
            context = ExecutionContext(query=query)
            agent_span.set_attribute("agent.plan_steps", len(plan.steps))
            agent_span.set_attribute("agent.plan", ", ".join(step.tool for step in plan.steps))

            for step in plan.steps:
                # For each step in the plan we get the tool and link it to the tool in ToolRegistry
                tool = self.registry.get(step.tool)
                with self.tracer.start_as_current_span(f"tool.{step.tool}") as tool_span:
                    tool_span.set_attribute("agent.step", step.tool)
                    # For each tool we find the list of parameters needed and get the parameter
                    # values from the execution context
                    kwargs = {parameter: context.get(parameter) for parameter in tool.parameters}
                    result = await tool.execute(**kwargs)
                    for key, value in result.items():
                        context.set(key, value)
                # We return the last value received as the final answer
            return value
from pydantic import BaseModel, Field

class PlanStep(BaseModel):
    tool: str

class Plan(BaseModel):
    steps: list[PlanStep]

class Planner:

    def __init__(self, ToolNames):
        self.ToolNames = ToolNames

    def plan(self) -> Plan:
        return Plan(steps=[
                            PlanStep(
                                tool=self.ToolNames.RETRIEVE,
                            ),
                            PlanStep(
                                tool=self.ToolNames.PROMPT,
                            ),
                            PlanStep(
                                tool=self.ToolNames.ANSWER,
                            )
                        ])
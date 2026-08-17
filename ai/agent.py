class Agent:
    def __init__(self, planner, executor):
        self.planner = planner
        self.executor = executor
    
    async def run(self, query: str):
        plan = self.planner.plan()
        return await self.executor.execute(query=query, plan=plan)

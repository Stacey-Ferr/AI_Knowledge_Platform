from typing import Protocol, Any

class ToolNames:
    RETRIEVE = "retrieve_documents"
    PROMPT = "build_prompt"
    ANSWER = "generate_answer"

class Tool(Protocol):
    name: str

    async def execute(self, **kwargs: Any) -> Any:
        ...

class RetrievalTool:
    """
        Used to call the retrieve method from the Retrieval Service and return relevant matches
    """
    name = ToolNames.RETRIEVE
    parameters = ["query"]
    output = ["relevant_matches"]

    def __init__(self, retrieval_service):
        self.retrieval_service = retrieval_service

    async def execute(self, query):
        relevant_matches = self.retrieval_service.retrieve(query)
        return {
                    "relevant_matches" : relevant_matches
                }

class PromptTool:
    """
        Used to call the Prompst Service to generate a prompt for the query using relevant
        matches as context
    """
    name = ToolNames.PROMPT
    parameters = ["query", "relevant_matches"]
    output = ["system_prompt", "user_prompt"]

    def __init__(self, prompt_service):
        self.prompt_service = prompt_service
    
    async def execute(self, query: str, relevant_matches):
        system_prompt, user_prompt = self.prompt_service.build_prompt(query, relevant_matches)
        return {
                    "system_prompt" : system_prompt, 
                    "user_prompt" : user_prompt
                }

class AnswerTool:
    """
        The tool will pass the prompt created to the LLM to generate an appropriate response
    """
    name = ToolNames.ANSWER
    parameters = ["system_prompt", "user_prompt"]
    output = ["response"]

    def __init__(self, openai_provider):
        self.openai_provider = openai_provider

    async def execute(self, system_prompt, user_prompt):
        response = await self.openai_provider.generate(system_prompt, user_prompt)
        return {
                    "response" : response
                }

class ToolRegistry:
    """
        This creates a dictionary of Tool names and the reference to each Tool
    """
    def __init__(self, tools: dict[str, Tool]):
        self.tools = tools
    
    def get(self, name: str) -> Tool:
        return self.tools[name]
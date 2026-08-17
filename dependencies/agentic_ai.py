from ai.tools import (RetrievalTool, PromptTool, AnswerTool, ToolRegistry, ToolNames)
from fastapi import Depends
from services.retrieval_service import RetrievalService
from dependencies.base import get_embedding_service, get_vector_service, get_bm25_service, get_reranker, get_prompt_builder, get_openai_provider
from ai.planner import Planner
from ai.executor import Executor
from ai.agent import Agent

def get_retrieval_service(
                        embedding_service = Depends(get_embedding_service),
                        vector_service = Depends(get_vector_service),
                        bm25_service = Depends(get_bm25_service),
                        reranker = Depends(get_reranker)
                    ):
    return RetrievalService(
                                embedding_service = embedding_service, vector_service = vector_service, 
                                bm25_service = bm25_service, reranker = reranker
                            )

def get_retrieval_tool(retrieval_service = Depends(get_retrieval_service)) -> RetrievalTool:
    return RetrievalTool(retrieval_service=retrieval_service)

def get_prompt_tool(prompt_service = Depends(get_prompt_builder)) -> PromptTool:
    return PromptTool(prompt_service=prompt_service)

def get_answer_tool(openai_provider = Depends(get_openai_provider)) -> AnswerTool:
    return AnswerTool(openai_provider=openai_provider)

def get_tool_registry(
                        retrieval_tool: RetrievalTool = Depends(get_retrieval_tool),
                        prompt_tool: PromptTool = Depends(get_prompt_tool),
                        answer_tool: AnswerTool = Depends(get_answer_tool)
                    ) -> ToolRegistry:
    return ToolRegistry(tools={
                                retrieval_tool.name : retrieval_tool,
                                prompt_tool.name : prompt_tool,
                                answer_tool.name : answer_tool                  
                            })

def get_planner() -> Planner:
    return Planner(ToolNames())

def get_executor(registry: ToolRegistry = Depends(get_tool_registry)) -> Executor:
    return Executor(registry=registry)

def get_agent(
                planner: Planner = Depends(get_planner), 
                executor: Executor = Depends(get_executor)
            ) -> Agent:
    return Agent(planner=planner, executor=executor)
import os
from pathlib import Path

import yaml
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.main_agent.node.decide_agent_node import decide_agent_node
from agents.main_agent.node.final_response_node import final_response_node
from agents.main_agent.node.setup_node import setup_node
from core.state import AgentState
from logger import logger


async def create_main_agent():
    """Main Agent orchestrator graph'ını oluşturur."""

    workflow = StateGraph(AgentState)

    # Node'ları ekle
    workflow.add_node("setup", setup_node)
    workflow.add_node("decide_agent", decide_agent_node)

    workflow.add_node("final_response", final_response_node)

    # Ana akış
    workflow.add_edge(START, "setup")
    workflow.add_edge("setup", "decide_agent")

    # Decide agent'ın kararına göre yönlendirme
    workflow.add_conditional_edges(
        "decide_agent",
        lambda state: state.get("next_node", "final_response"),
        {
            "decide_agent": "decide_agent",  # ReAct devam eder
            "final_response_node": "final_response",  # Tool bitti, final response
        },
    )

    # ReAct loop: tools → tekrar decide_agent
    workflow.add_edge("tools", "decide_agent")
    workflow.add_edge("final_response", END)

    # Memory
    memory = MemorySaver()

    compiled_graph = workflow.compile(checkpointer=memory)
    logger.info("Main Agent graph compiled successfully.")

    return compiled_graph

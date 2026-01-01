from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.task_manager.node.analysis_agent import analysis_agent
from core.state import AgentState
from logger import logger

task_agent = None


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and getattr(
        last_message, "tool_calls", None
    ):
        return "tools"
    return "end"


async def create_task_manager_agent(initial_state: AgentState):
    """
    Task Manager sub-agent flow.
    Burada initial_state, Main Agent setup node tarafından zaten
    config + manifest + tools_dict ile doldurulmuş olmalı.
    """

    global task_agent

    if task_agent is not None:
        logger.info(
            "Task Manager agent workflow already created. Reusing existing instance."
        )
        return task_agent

    workflow = StateGraph(AgentState)
    logger.info("Creating Task Manager agent workflow...")

    # Task Manager analiz düğümü
    workflow.add_node("analysis", analysis_agent)

    # Sadece Task Manager tool set'ini kullan
    tm_tools = initial_state["tools_dict"]["task_manager"].values()
    workflow.add_node("tools", ToolNode(tools=list(tm_tools)))
    logger.info("Added Task Manager tools to the workflow.")

    # Akış
    workflow.add_edge(START, "analysis")
    workflow.add_conditional_edges(
        "analysis",
        should_continue,
        {"tools": "tools", "end": END},
    )
    workflow.add_edge("tools", "analysis")
    logger.info("Defined workflow edges and conditions.")

    memory = MemorySaver()
    logger.info("Compiled Task Manager agent workflow with memory checkpointer.")

    compiled_graph = workflow.compile(checkpointer=memory)

    task_agent = compiled_graph

    return task_agent

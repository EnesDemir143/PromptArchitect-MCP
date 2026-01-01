import os
from typing import Any, Dict

from agents.main_agent.node.setup_node import load_tools_from_config
from core.llm_factory import get_base_llm
from core.state import AgentState
from logger import logger


async def analysis_agent(state: AgentState) -> Dict[str, Any]:
    """
    Analyzes the current project state and determines the next course of action.

    This agent examines the project manifest, recent messages, and context to
    decide if any tasks need updating or if new information is required.
    It prepares tool calls with necessary parameters if an action is needed.

    Args:
        state (AgentState): The current state of the orchestration graph.

    Returns:
        Dict[str, Any]: State updates containing the LLM response, history logs,
                        and the identity of the current agent.
    """
    logger.info("Analysis Agent: Starting state analysis...")

    tools = load_tools_from_config("task_manager")

    # temperature=0 is essential for consistent tool parameter generation
    llm = get_base_llm()

    # Bind tools natively to the model
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    try:
        response = await llm_with_tools.ainvoke(state["messages"])

        # Determine if Gemini decided to call a tool
        has_tool_calls = bool(hasattr(response, "tool_calls") and response.tool_calls)
        log_message = (
            f"Analysis Agent: Prepared {len(response.tool_calls)} tool call(s)."
            if has_tool_calls
            else "Analysis Agent: No tool call needed, proceeding to final response."
        )

        return {
            "messages": [response],  # Appends the AIMessage (with tool_calls if any)
            "current_agent": "analysis_agent",
            "history": [log_message],  # Appends to the history list via operator.add
            "error": None,
        }

    except Exception as e:
        error_msg = f"Analysis Agent Error: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "history": [f"FAILED: {error_msg}"]}

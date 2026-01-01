import json
import os

from langgraph.prebuilt import ToolNode

from core.llm_factory import get_base_llm
from core.state import AgentState
from logger import logger


async def decide_agent_node(state: AgentState) -> dict:
    """
    Decides the next steps based on the current state.

    This node evaluates the current project state, recent messages, and context
    to determine if any tasks need updating or if new information is required.
    It prepares tool calls with necessary parameters if an action is needed.

    Args:
        state (AgentState): The current state of the orchestration graph.
    """

    llm = get_base_llm()
    main_tools = state.get("tools_dict", {}).get("main_agent", {}).values()
    tools = list(main_tools) if main_tools else []

    if tools:
        llm_with_tools = llm.bind_tools(tools)
        logger.info(f"Decide Agent Node: Binding {len(tools)} tools to the LLM.")
    else:
        llm_with_tools = llm
        logger.info("Decide Agent Node: No tools to bind to the LLM.")

    updates: dict = {}

    try:
        response = await llm_with_tools.ainvoke(state["messages"])

        updates["messages"] = [response]

        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(
                f"Decide Agent Node: Prepared {len(response.tool_calls)} tool call(s)."
            )

            tool_node = ToolNode(tools=tools)

            temp_state = state.copy()
            temp_state["messages"] = list(state["messages"]) + [response]

            tool_results = await tool_node.ainvoke(temp_state)

            updates["messages"] += tool_results["messages"]

            if os.path.exists(".ai_state.json"):
                try:
                    with open(".ai_state.json", "r", encoding="utf-8") as f:
                        # updates sözlüğüne manifest'i ekliyoruz.
                        # LangGraph bunu ana state ile birleştirecek.
                        updates["manifest"] = json.load(f)
                    logger.info(
                        "Decide Node: Manifest reloaded from disk after tool execution."
                    )
                except Exception as read_err:
                    logger.error(f"Failed to reload manifest: {read_err}")

            next_node = "decide_agent"
        else:
            logger.info(
                "Decide Agent Node: No tool call needed, proceeding to final response."
            )
            next_node = "final_response_node"
        updates["history"] = [
            f"Decide Agent Node: Processed message with {len(getattr(response, 'tool_calls', []))} tool call(s)."
        ]
        updates["error"] = None
        updates["next_node"] = next_node

    except Exception as e:
        error_msg = f"Decide Agent Node Error: {str(e)}"
        logger.error(error_msg)
        updates["error"] = error_msg
        updates["history"] = [f"FAILED: {error_msg}"]
        # next_node = "error_handling_node"

    return updates

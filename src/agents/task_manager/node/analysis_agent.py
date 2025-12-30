import os
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI

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

    tools = list(state.get("tools_dict", {}).values())

    # temperature=0 is essential for consistent tool parameter generation
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-pro", temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY")
    )

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

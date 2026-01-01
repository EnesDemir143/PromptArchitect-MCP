from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from agents.task_manager.agent_flow import create_task_manager_agent
from core.state import AgentState
from logger import logger


@tool
async def task_manager_agent_tool(
    request: str, state: Annotated[AgentState, InjectedState]
) -> dict:
    """Invoke the task manager sub-agent."""
    try:
        task_tools_map = state["tools_dict"].get("task_manager", {})
        my_tools = list(task_tools_map.values())
        task_agent = await create_task_manager_agent(my_tools)

        result = await task_agent.ainvoke(state)

        last_message = result["messages"][-1]
        summary_content = (
            last_message.content
            if last_message
            else "Task Manager completed with no output."
        )

        return {
            "output": f"Task Manager Execution Result: {summary_content}",
            "error": None,
        }

    except Exception as e:
        logger.error(f"Task Manager error: {e}")
        return {"error": str(e), "history": [f"Error in sub-agent: {e}"]}

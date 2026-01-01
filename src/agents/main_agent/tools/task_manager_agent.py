from agents.task_manager.agent_flow import create_task_manager_agent
from core.state import AgentState
from logger import logger


async def task_manager_agent(state: AgentState) -> dict:
    """
    This tool is invoke the task manager.
    """
    try:
        task_agent = await create_task_manager_agent(state)
        logger.info("Starting Task Manager...")

        # Aynı state objesi modifiye olur
        await task_agent.ainvoke(state)
        logger.info("Task Manager completed.")

        return {
            "history": ["Task Manager sub-agent completed successfully."],
            "error": None,
        }
    except Exception as e:
        logger.error(f"Task Manager error: {e}")
        return {"error": str(e), "history": [f"TASK_MANAGER_ERROR: {e}"]}

from pathlib import Path

import yaml
from langchain_core.messages import SystemMessage

from core.state import AgentState
from logger import logger


async def setup_node(state: AgentState) -> AgentState:
    """Sets up the node by loading configuration from a YAML file."""

    config_path = Path("../config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    if state is None:
        state = AgentState(
            messages=[],
            tools_dict={},
            manifest={
                "project_meta": {
                    "name": "",
                    "tech_stack": [],
                    "architecture": "",
                    "root_directory": None,
                },
                "status": {
                    "current_phase": "",
                    "active_goal": "",
                    "last_update": None,
                },
                "tasks": [],
                "global_rules": [],
            },
            relevant_context=None,
            final_prompt=None,
            history=[],
            current_agent="",
            next_node="",
        )

    tm_config = config.get("task_manager", {})

    sys_config = tm_config.get("system_prompt", {})
    if sys_config.get("role") == "system":
        state["messages"].append(SystemMessage(content=sys_config.get("content", "")))
        logger.info("System prompt added to messages.")

    tools_list = tm_config.get("tools", [])
    for tool in tools_list:
        name = tool.get("name")
        desc = tool.get("description")
        state["tools_dict"][name] = desc
        logger.info(f"Tool added: {name}")

    return state

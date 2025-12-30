from pathlib import Path

import yaml
from langchain_core.messages import SystemMessage

from core.state import AgentState
from logger import logger


async def setup_node(state: AgentState) -> dict:  # Dönüş tipi dict olmalı
    """Sets up the node by returning only the necessary state updates."""

    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        return {"error": "Config file missing"}

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    updates = {}
    tm_config = config.get("task_manager", {})

    sys_config = tm_config.get("system_prompt", {})
    if sys_config.get("role") == "system":
        updates["messages"] = [SystemMessage(content=sys_config.get("content", ""))]
        logger.info("System prompt prepared for state update.")

    updates["current_agent"] = "setup_node"
    updates["history"] = ["Setup: Configuration and system prompt loaded."]

    return updates

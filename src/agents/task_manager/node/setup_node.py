import json
from pathlib import Path

import yaml
from langchain_core.messages import SystemMessage

from core.state import AgentState
from logger import logger


async def setup_node(state: AgentState) -> dict:  # Dönüş tipi dict olmalı
    """Sets up the node by returning only the necessary state updates."""

    config_path = Path(__file__).parent.parent / "config.yaml"
    manifest_path = Path(".ai_state.json")

    updates = {}

    # 1. Config ve System Prompt Yükleme
    if config_path.exists():
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        tm_config = config.get("task_manager", {})
        sys_config = tm_config.get("system_prompt", {})
        if sys_config.get("role") == "system":
            updates["messages"] = [SystemMessage(content=sys_config.get("content", ""))]

    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                updates["manifest"] = json.load(f)
            logger.info("Manifest loaded from .ai_state.json")
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")

    updates["current_agent"] = "setup_node"
    updates["history"] = ["Setup: Configuration, system prompt, and manifest loaded."]

    return updates

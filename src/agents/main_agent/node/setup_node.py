import importlib
import json
from pathlib import Path

import yaml
from langchain_core.messages import SystemMessage

from core.state import AgentState
from logger import logger


async def assign_agent_tools_to_agent_state(state: AgentState, config) -> dict:
    """Assigns the provided tools to the agent state."""

    actual_tools = {}

    for agent_key, agent_info in config.items():
        tools_metadata = agent_info.get("tools", [])
        actual_tool_instances = []

        for t in tools_metadata:
            try:
                module_str = t["import_path"].replace(".py", "").replace("/", ".")

                # Eğer bu dosya src/ altında ise:
                module_path = (
                    f"agents.{module_str}"
                    if not module_str.startswith("agents")
                    else module_str
                )

                # Dinamik import
                module = importlib.import_module(module_path)
                tool_class = getattr(module, t["class_name"])

                # Instance oluşturma
                tool_instance = tool_class(**t.get("params", {}))
                actual_tool_instances.append(tool_instance)

                logger.info(
                    f"Successfully loaded: {t['class_name']} from {module_path} for agent {agent_key}"
                )
            except Exception as e:
                logger.error(
                    f"Error loading {t.get('class_name')}: {str(e)} for agent {agent_key}"
                )

        tools_dict = {t.name: t for t in actual_tool_instances}
        actual_tools[agent_key] = tools_dict

    return actual_tools


async def setup_node(state: AgentState) -> dict:
    """Sets up the node by returning only the necessary state updates."""

    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    manifest_path = Path(".ai_state.json")

    updates: dict = {}

    # 1. Config ve system prompt
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        main_agent = config.get("main_agent", {}) or {}
        sys_cfg = main_agent.get("system_prompt", {}) or {}

        content = sys_cfg.get("content")
        if isinstance(content, str) and content.strip():
            updates["messages"] = [SystemMessage(content=content)]
            logger.info("System prompt loaded and added to messages for Main Agent.")

        # 2. Tüm agent'ların tool instance'larını üret
        tools_dict_per_agent = await assign_agent_tools_to_agent_state(state, config)
        updates["tools_dict"] = tools_dict_per_agent

    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                updates["manifest"] = json.load(f)
            logger.info("Manifest loaded from .ai_state.json")
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")

    updates["current_agent"] = "main_agent"
    updates["next_node"] = "decide_agent_node"
    updates["history"] = ["Main Agent setup completed."]

    return updates

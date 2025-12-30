import importlib
from pathlib import Path

import yaml
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.task_manager.node.analysis_agent import analysis_agent
from agents.task_manager.node.setup_node import setup_node
from core.state import AgentState
from logger import logger


def should_continue(state: AgentState) -> str:
    """
    Routing logic: Decides whether to continue to the 'tools' node
    or finish the execution by going to 'end'.
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


async def create_main_agent():
    config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        return None

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    tm_config = config.get("task_manager", {})
    actual_tool_instances = []
    tools_metadata = tm_config.get("tools", [])

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

            logger.info(f"Successfully loaded: {t['class_name']} from {module_path}")
        except Exception as e:
            logger.error(f"Error loading {t.get('class_name')}: {str(e)}")

    # 3. Graf Yapılandırması
    workflow = StateGraph(AgentState)

    # Düğümleri Ekle
    workflow.add_node("setup", setup_node)
    workflow.add_node("analysis", analysis_agent)
    # Hazır ToolNode, listeyi otomatik olarak fonksiyon isimleriyle eşleştirir
    workflow.add_node("tools", ToolNode(tools=actual_tool_instances))

    # 4. Akış Tanımı
    workflow.add_edge(START, "setup")
    workflow.add_edge("setup", "analysis")

    workflow.add_conditional_edges(
        "analysis", should_continue, {"tools": "tools", "end": END}
    )

    # ReAct döngüsü: Tool çıktısını tekrar analize gönder
    workflow.add_edge("tools", "analysis")

    # 5. Kalıcı Hafıza (Checkpointing)
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)

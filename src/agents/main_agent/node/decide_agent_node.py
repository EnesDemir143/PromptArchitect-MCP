import json
import os

from langgraph.prebuilt import ToolNode

from agents.main_agent.node.setup_node import load_tools_from_config
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
# 1. Hazırlık
    llm = get_base_llm()
    tools = load_tools_from_config("main_agent")

    # State injection (Task Manager için)
    for t in tools:
        if t.name == "route_to_task_manager":
            t.current_state = state.copy()
            logger.info("Decide Node: Injected state into RouteToTaskManager.")

    # LLM'e araçları tanıt
    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm

    updates: dict = {}

    try:
        # 2. Karar Anı (LLM Düşünüyor)
        response = await llm_with_tools.ainvoke(state["messages"])
        updates["messages"] = [response]

        # 3. Eğer Ajan "Araç Kullanacağım" dediyse
        if hasattr(response, "tool_calls") and response.tool_calls:
            logger.info(f"Decide Agent Node: Calling {len(response.tool_calls)} tools.")

            # Araçları çalıştır
            tool_node = ToolNode(tools=tools)
            temp_state = state.copy()
            temp_state["messages"] = list(state["messages"]) + [response]
            
            tool_results = await tool_node.ainvoke(temp_state)
            updates["messages"] += tool_results["messages"]

            # Manifesti güncelle (Disk -> Memory senkronizasyonu)
            manifest_path = Path(__file__).resolve().parents[4] / ".ai_state.json"
            if manifest_path.exists():
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        updates["manifest"] = json.load(f)
                except Exception as read_err:
                    logger.error(f"Manifest reload error: {read_err}")

            # KRİTİK NOKTA: Araç kullandıysa tekrar kendine dönmeli mi?
            # Sonsuz döngü sebebi burasıydı. Ama artık ContextScanner düzeldiği için
            # ajan "Tamam işim bitti" diyebilecek.
            next_node = "decide_agent"

        else:
            # 4. Ajan "Araç kullanmama gerek yok, bitti" dediyse
            logger.info("Decide Agent: Task completed, generating final response.")
            next_node = "final_response_node"

        updates["history"] = [f"Decide Node: Step executed."]
        updates["error"] = None
        updates["next_node"] = next_node

    except Exception as e:
        error_msg = f"Decide Node Error: {str(e)}"
        logger.error(error_msg)
        updates["error"] = error_msg
        updates["next_node"] = "final_response_node"

    return updates

from langchain_core.messages import AIMessage, HumanMessage

from core.llm_factory import get_base_llm
from core.state import AgentState


async def final_response_node(state: AgentState) -> dict:
    """
    ReAct loop bittikten sonra, tüm context'i LLM'ye verip
    user-facing, net bir final response üretir.

    Args:
        state (AgentState): Current state of Orchestration graph.
    """

    base_llm = get_base_llm()
    # Tool'ları bind etme, sadece temiz response için
    llm = base_llm  # bind_tools yok

    # Context: son mesajlar + manifest özeti + history
    context_prompt = f"""
    Project Status: {state["manifest"].get("status", {}).get("active_goal", "None")}
    Recent Tasks: {len(state["manifest"].get("tasks", []))} tasks
    Recent History: {state["history"][-3:]}

    Please provide a clear, user-facing summary of what was accomplished.
    """
    # This prompt is take recent 3 history and project status to give context to the LLM. But we could build enhanced memory so this content would be better.

    # Tüm conversation + context
    messages_for_final = state["messages"][-5:] + [HumanMessage(content=context_prompt)]

    try:
        final_response = await llm.ainvoke(messages_for_final)
        updates = {
            "messages": [final_response],
            "history": ["Final user-facing response generated."],
            "current_agent": "main_agent_final",
        }
    except Exception as e:
        updates = {
            "messages": [
                AIMessage(
                    content=f"An error occurred while generating the final response. ERROR DETAILS: {str(e)}"
                )
            ],
            "history": [f"Final response error: {str(e)}"],
            "error": str(e),
        }

    return updates

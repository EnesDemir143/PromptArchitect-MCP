import asyncio
import os
import sys
from mcp.server.fastmcp import FastMCP
from langchain_core.messages import HumanMessage

# Proje kök dizinini path'e ekle (Modüllerin bulunması için)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.main_agent.agent_flow import create_main_agent
from memory.json_store import JSONStore

# MCP Sunucusunu Başlat
mcp = FastMCP("PromptArchitect")

@mcp.tool()
async def architect_request(request: str) -> str:
    """
    Acts as the primary "Project Architect" and "Orchestration Engine" for this coding environment.
    
    CRITICAL: This tool MUST be the FIRST step for any coding task, feature request, or refactoring.
    Do not attempt to write code or modify files until this tool has been executed.

    This tool triggers the internal multi-agent system (LangGraph) to:
    1. Analyze the user's high-level request against the current project context.
    2. Decompose the request into specific, actionable tasks using the Task Manager.
    3. Update the persistent project manifest (.ai_state.json) with new tasks, status, and architectural rules.
    4. Generate a detailed "Architected Prompt" (implementation plan) for the Developer to follow.

    Args:
        request (str): The user's raw coding request, feature description, or bug report (e.g., "Add JWT auth", "Refactor the API").

    Returns:
        str: A summary of the architectural plan and confirmation that the project manifest (.ai_state.json) has been updated.
    """
    try:
        # 1. Main Agent'ı oluştur (Senin agent_flow.py dosyanı kullanır)
        app = await create_main_agent()
        
        # 2. Architect Prompt'u hazırla
        architect_prompt = (
            f"Please analyze the following request and generate a detailed, "
            f"architected prompt that an expert developer can use to implement it. "
            f"Focus on technical details, file structure, and best practices.\n\n"
            f"User Request: {request}"
        )

        # 3. State'i hazırla
        initial_state = {
            "messages": [HumanMessage(content=architect_prompt)],
            "manifest": JSONStore().load(), # Mevcut durumu yükle
            "history": [],
            "current_agent": "start",
        }

        # 4. Graph'ı çalıştır
        final_state = await app.ainvoke(initial_state)

        # 5. Sonucu Dön
        last_message = final_state["messages"][-1]
        return f"✅ ARCHITECTURE PLAN COMPLETE.\n\nArchitect Report:\n{last_message.content}\n\nSystem Note: The .ai_state.json manifest has been updated with new tasks. You may now proceed with implementation based on these tasks."

    except Exception as e:
        return f"❌ ARCHITECT ERROR: An error occurred during the planning phase: {str(e)}"

if __name__ == "__main__":
    mcp.run()
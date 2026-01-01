import asyncio
import os
import sys

from mcp.server.fastmcp import FastMCP
from langchain_core.messages import HumanMessage

# Add src to path to ensure imports work
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from agents.main_agent.agent_flow import create_main_agent
from memory.json_store import JSONStore

# Initialize FastMCP Server
mcp = FastMCP("PromptArchitect")

@mcp.tool()
async def architect_prompt(request: str) -> str:
    """
    Architects a highly detailed and optimized prompt based on a user's request.
    This tool analyzes the current project context and best practices to generate
    a prompt suitable for an expert coding agent.
    
    Args:
        request: The raw user request (e.g., "Create a login page with Supabase auth").
    """
    try:
        # Create the agent
        app = await create_main_agent()
        
        # Prepare the input for the agent
        # We wrap the user request to explicitly ask for an "Architected Prompt"
        architect_request = (
            f"Please analyze the following request and generate a detailed, "
            f"architected prompt that an expert developer can use to implement it. "
            f"Focus on technical details, file structure, and best practices. "
            f"\n\nUser Request: {request}"
        )
        
        initial_state = {
            "messages": [HumanMessage(content=architect_request)],
            "manifest": JSONStore().load(),
            "history": [],
            "current_agent": "start",
        }
        
        config = {"configurable": {"thread_id": "mcp_architect_request"}}
        
        final_response = ""
        
        # Run the agent
        async for event in app.astream(initial_state, config=config):
            for node_name, state_update in event.items():
                if "messages" in state_update and state_update["messages"]:
                    msg = state_update["messages"][-1]
                    if msg.content:
                        final_response = msg.content
                        
        return final_response

    except Exception as e:
        return f"Error processing request: {str(e)}"

if __name__ == "__main__":
    mcp.run()

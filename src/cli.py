import argparse
import asyncio
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from agents.main_agent.agent_flow import create_main_agent
from memory.json_store import JSONStore
from langchain_core.messages import HumanMessage

async def run_cli(request: str):
    print(f"🏗️  Architecting prompt for request: '{request}'...\n")
    
    try:
        app = await create_main_agent()
        
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
        
        config = {"configurable": {"thread_id": "cli_architect_request"}}
        
        final_response = ""
        
        async for event in app.astream(initial_state, config=config):
            for node_name, state_update in event.items():
                if "messages" in state_update and state_update["messages"]:
                    msg = state_update["messages"][-1]
                    if msg.content:
                        final_response = msg.content
                        
        print("\n" + "="*80)
        print("🏛️  ARCHITECTED PROMPT")
        print("="*80 + "\n")
        print(final_response)
        print("\n" + "="*80 + "\n")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Prompt Architect CLI")
    parser.add_argument("request", nargs="?", help="The coding request to architect")
    args = parser.parse_args()
    
    if not args.request:
        print("Usage: python src/cli.py \"Your request here\"")
        return

    asyncio.run(run_cli(args.request))

if __name__ == "__main__":
    main()

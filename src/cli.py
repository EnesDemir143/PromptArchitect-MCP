from pathlib import Path
import argparse
import asyncio
import os
import sys

# Ensure src is in path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from agents.main_agent.agent_flow import create_main_agent
from memory.json_store import JSONStore
from langchain_core.messages import HumanMessage

def get_manifest_path():
    return str(Path(__file__).resolve().parent.parent / ".ai_state.json")

async def run_cli(request: str, raw: bool = False):
    if not raw:
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
            "manifest": JSONStore(get_manifest_path()).load(),
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
        
        if raw:
            print(final_response)
        else:
            print("\n" + "="*80)
            print("🏛️  ARCHITECTED PROMPT")
            print("="*80 + "\n")
            print(final_response)
            print("\n" + "="*80 + "\n")

    except Exception as e:
        if args.raw:
             print(f"Error: {str(e)}")
        else:
             print(f"❌ Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Prompt Architect CLI")
    parser.add_argument("request", nargs="?", help="The coding request to architect")
    parser.add_argument("--raw", action="store_true", help="Output only the architected prompt")
    args = parser.parse_args()
    
    if not args.request:
        if not args.raw:
            print("Usage: python src/cli.py \"Your request here\"")
        return

    asyncio.run(run_cli(args.request, raw=args.raw))

if __name__ == "__main__":
    main()

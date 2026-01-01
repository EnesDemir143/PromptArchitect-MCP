import asyncio
import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from agents.main_agent.node.setup_node import setup_node
from langchain_core.messages import SystemMessage

async def verify():
    print("Running Context Injection Verification...")
    
    # Mock state
    state = {}
    
    # Run setup node
    updates = await setup_node(state)
    
    # Check messages
    if "messages" in updates:
        sys_msg = updates["messages"][0]
        if isinstance(sys_msg, SystemMessage):
            content = sys_msg.content
            print("\n[System Prompt Content Preview]")
            print("-" * 40)
            print(content[-500:]) # Print last 500 chars to see the injection
            print("-" * 40)
            
            if "[AUTOMATIC CONTEXT INJECTION]" in content:
                print("\n✅ Verification SUCCESS: Context injection marker found.")
            else:
                print("\n❌ Verification FAILED: Marker not found.")
                
            if "OS:" in content and "File Structure:" in content:
                print("✅ Verification SUCCESS: OS and File Structure detected.")
            else:
                print("❌ Verification FAILED: Missing OS or File Structure.")
        else:
            print("❌ Error: First message is not SystemMessage")
    else:
        print("❌ Error: No messages updated.")

if __name__ == "__main__":
    asyncio.run(verify())

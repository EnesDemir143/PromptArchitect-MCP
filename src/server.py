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
    Kullanıcının kodlama isteğini analiz eder, görevlere böler ve .ai_state.json dosyasına yazar.
    Kodlamaya başlamadan önce MUTLAKA bu aracı çalıştır.
    Args:
        request: Kullanıcının yapmak istediği iş (Örn: "Login sayfası ekle")
    """
    try:
        # 1. Main Agent'ı oluştur (Senin agent_flow.py dosyanı kullanır)
        app = await create_main_agent()
        
        # 2. Architect Prompt'u hazırla (cli.py'deki mantıkla aynı)
        architect_prompt = (
            f"Please analyze the following request and generate a detailed, "
            f"architected prompt that an expert developer can use to implement it. "
            f"Focus on technical details, file structure, and best practices.\n\n"
            f"User Request: {request}"
        )

        # 3. State'i hazırla (state.py ve json_store.py kullanır)
        initial_state = {
            "messages": [HumanMessage(content=architect_prompt)],
            "manifest": JSONStore().load(), # Mevcut durumu yükle
            "history": [],
            "current_agent": "start",
        }

        # 4. Graph'ı çalıştır
        # Not: CLI'da astream kullanmıştın, burada tek seferde sonuç almak için invoke kullanıyoruz.
        final_state = await app.ainvoke(initial_state)

        # 5. Sonucu Dön
        last_message = final_state["messages"][-1]
        return f"✅ PLANLAMA TAMAMLANDI.\n\nArchitect Raporu:\n{last_message.content}\n\n.ai_state.json güncellendi. Görevleri uygulamaya başlayabilirsin."

    except Exception as e:
        return f"❌ HATA: Architect çalışırken sorun oluştu: {str(e)}"

if __name__ == "__main__":
    mcp.run()
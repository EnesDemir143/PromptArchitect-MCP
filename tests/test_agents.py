import json
import os
import shutil
import logging # <--- EKLENDİ
import pytest
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import BaseTool

# Proje modüllerini import ediyoruz
from agents.main_agent.agent_flow import create_main_agent
from agents.main_agent.tools.route_task_manager import RouteToTaskManager
from agents.task_manager.tools.task_manager import ManageTasks
from memory.json_store import JSONStore

# --- LOGLAMA AYARLARI ---
def setup_test_logging():
    """Test çıktılarını 'test_execution.log' dosyasına yazar."""
    logging.basicConfig(
        filename="test_execution.log",
        filemode="w", # Her testte dosyayı sıfırlar
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        force=True # Önceki configleri ezer
    )
    return logging.getLogger("TestLogger")

# --- FIXTURES ---

@pytest.fixture(scope="function")
def clean_manifest():
    """Her testten önce .ai_state.json dosyasını sıfırlar."""
    manifest_path = ".ai_state.json"
    backup_path = ".ai_state.json.bak"

    if os.path.exists(manifest_path):
        shutil.copy(manifest_path, backup_path)

    store = JSONStore()
    default_data = store.load_default_template()
    store.save(default_data)

    yield

    if os.path.exists(backup_path):
        shutil.move(backup_path, manifest_path)


# --- TESTLER ---

def test_tool_class_structure():
    print("\n[Test] Tool Class Yapısı Kontrol Ediliyor...")
    tool_instance = RouteToTaskManager()
    assert isinstance(tool_instance, BaseTool), "RouteToTaskManager, BaseTool'dan türetilmemiş!"
    assert tool_instance.name == "route_to_task_manager", "Tool ismi config ile uyuşmuyor!"
    assert hasattr(tool_instance, "_arun"), "Tool'un async çalışma metodu (_arun) eksik!"
    print("✅ Tool Class yapısı doğru.")


def test_manage_tasks_tool(clean_manifest):
    print("\n[Test] ManageTasks Tool'u Test Ediliyor...")
    tool = ManageTasks()
    result = tool._run(
        action="add",
        task_id="TEST-01",
        title="Pytest Görevi",
        status="todo",
        description="Bu bir otomatik test görevidir.",
    )
    print(f"Tool Sonucu: {result}")
    with open(".ai_state.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        tasks = data.get("tasks", [])

    assert len(tasks) == 1, "Görev dosyaya eklenemedi!"
    assert tasks[0]["id"] == "TEST-01", "Görev ID'si yanlış!"
    print("✅ Görev başarıyla dosyaya yazıldı.")


@pytest.mark.asyncio
async def test_full_agent_workflow(clean_manifest):
    # 1. Logger'ı Hazırla
    logger = setup_test_logging()
    print("\n[Test] Main Agent Entegrasyon Testi Başlıyor... (Detaylar: test_execution.log)")
    logger.info("🎬 TEST BAŞLADI: Full Agent Workflow")

    # 2. Main Agent'ı oluştur
    app = await create_main_agent()

    # 3. State Hazırla
    user_input = "Lütfen 'E2E_TEST' ID'li ve 'Integration Test' başlıklı yeni bir görev ekle."
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "manifest": JSONStore().load(),
        "history": [],
        # "tools_dict": {}, # Sildik (State temizliği için)
        "current_agent": "start",
    }
    
    logger.info(f"👤 KULLANICI MESAJI: {user_input}")

    config = {"configurable": {"thread_id": "test_thread_1"}}

    # 4. Akışı Çalıştır ve Logla
    step_count = 0
    
    async for event in app.astream(initial_state, config=config):
        step_count += 1
        
        for node_name, state_update in event.items():
            print(f"--- Node Bitti: {node_name} ---")
            logger.info(f"📍 NODE TAMAMLANDI: {node_name}")
            
            # Mesajları (Düşünce Zincirini) Logla
            if "messages" in state_update and state_update["messages"]:
                last_msg = state_update["messages"][-1]
                
                if isinstance(last_msg, AIMessage):
                    content = last_msg.content
                    tool_calls = getattr(last_msg, "tool_calls", [])
                    
                    if tool_calls:
                        log_msg = f"🤖 AGENT KARARI (Tool Call): {len(tool_calls)} adet araç çağırılıyor.\n"
                        for tc in tool_calls:
                            log_msg += f"   🛠️  Tool: {tc['name']} | Args: {tc['args']}\n"
                        logger.info(log_msg)
                        print(f"   -> Agent {len(tool_calls)} araç çağırıyor...")
                    
                    if content:
                        logger.info(f"🧠 AGENT DÜŞÜNCESİ: {content}")
                
                elif isinstance(last_msg, ToolMessage):
                    logger.info(f"🔧 TOOL SONUCU ({last_msg.name}): {last_msg.content}")
                    print(f"   -> Tool sonucu alındı.")

            # Manifest Güncellemesini Logla
            if "manifest" in state_update:
                print("⚡ Manifest güncellendi sinyali alındı!")
                logger.info("💾 MANIFEST GÜNCELLENDİ: Dosya diske yazıldı.")

        if step_count > 15:
            logger.warning("⚠️ Sonsuz döngü koruması devreye girdi!")
            break

    # 5. Sonuçları Doğrula
    with open(".ai_state.json", "r", encoding="utf-8") as f:
        final_manifest = json.load(f)

    tasks = final_manifest.get("tasks", [])
    found_task = next((t for t in tasks if t["id"] == "E2E_TEST"), None)

    if found_task:
        logger.info(f"✅ TEST BAŞARILI: Görev bulundu -> {found_task}")
    else:
        logger.error("❌ TEST BAŞARISIZ: Görev bulunamadı.")

    assert found_task is not None, "Main Agent, Task Manager'ı tetikleyemedi veya görev yazılmadı!"
    assert found_task["title"] == "Integration Test", "Görev başlığı yanlış!"

    print("✅ ENTEGRASYON BAŞARILI: Log dosyasına bakabilirsiniz -> test_execution.log")
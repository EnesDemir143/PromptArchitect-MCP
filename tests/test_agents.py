import json
import os
import shutil

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool

# Proje modüllerini import ediyoruz
# Not: Bu test dosyasını çalıştırırken PYTHONPATH ayarı gerekebilir (aşağıda açıkladım)
from agents.main_agent.agent_flow import create_main_agent
from agents.main_agent.tools.route_task_manager import RouteToTaskManager
from agents.task_manager.tools.task_manager import ManageTasks
from memory.json_store import JSONStore

# --- FIXTURES (Test Ortamı Hazırlığı) ---


@pytest.fixture(scope="function")
def clean_manifest():
    """Her testten önce .ai_state.json dosyasını sıfırlar."""
    manifest_path = ".ai_state.json"
    backup_path = ".ai_state.json.bak"

    # Varsa mevcudu yedekle
    if os.path.exists(manifest_path):
        shutil.copy(manifest_path, backup_path)

    # Temiz bir başlangıç dosyası oluştur
    store = JSONStore()
    default_data = store.load_default_template()
    store.save(default_data)

    yield

    # Test bitince temizle veya yedeği geri yükle (isteğe bağlı)
    # os.remove(manifest_path)
    if os.path.exists(backup_path):
        shutil.move(backup_path, manifest_path)


# --- TESTLER ---


# 1. TEST: Config ve Class Uyumluluğu
# Bu test, setup_node.py'nin hata verip vermeyeceğini simüle eder.
def test_tool_class_structure():
    print("\n[Test] Tool Class Yapısı Kontrol Ediliyor...")

    # Tool'u initialize etmeyi dene
    tool_instance = RouteToTaskManager()

    # Kontroller
    assert isinstance(tool_instance, BaseTool), (
        "RouteToTaskManager, BaseTool'dan türetilmemiş!"
    )
    assert tool_instance.name == "route_to_task_manager", (
        "Tool ismi config ile uyuşmuyor!"
    )
    assert hasattr(tool_instance, "_arun"), (
        "Tool'un async çalışma metodu (_arun) eksik!"
    )
    print("✅ Tool Class yapısı doğru.")


# 2. TEST: Task Manager Aracı (ManageTasks) Tek Başına Çalışıyor mu?
# Bu test, veritabanı/dosya yazma işlemini kontrol eder.
def test_manage_tasks_tool(clean_manifest):
    print("\n[Test] ManageTasks Tool'u Test Ediliyor...")

    tool = ManageTasks()

    # Görev Ekleme
    result = tool._run(
        action="add",
        task_id="TEST-01",
        title="Pytest Görevi",
        status="todo",
        description="Bu bir otomatik test görevidir.",
    )

    print(f"Tool Sonucu: {result}")

    # Dosyayı oku ve doğrula
    with open(".ai_state.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        tasks = data.get("tasks", [])

    assert len(tasks) == 1, "Görev dosyaya eklenemedi!"
    assert tasks[0]["id"] == "TEST-01", "Görev ID'si yanlış!"
    print("✅ Görev başarıyla dosyaya yazıldı.")


@pytest.mark.asyncio
async def test_full_agent_workflow(clean_manifest):
    print("\n[Test] Main Agent Entegrasyon Testi Başlıyor...")

    # 1. Main Agent'ı oluştur
    app = await create_main_agent()

    # 2. State Hazırla
    initial_state = {
        "messages": [
            HumanMessage(
                content="Lütfen 'E2E_TEST' ID'li ve 'Integration Test' başlıklı yeni bir görev ekle."
            )
        ],
        "manifest": JSONStore().load(),
        "history": [],
        "tools_dict": {},
        "current_agent": "start",
    }

    # --- DÜZELTME BURADA: Thread ID için Config Hazırla ---
    config = {"configurable": {"thread_id": "test_thread_1"}}

    # 3. Akışı Çalıştır (Config parametresi eklendi)
    step_count = 0

    # app.astream içine config=config ekledik
    async for event in app.astream(initial_state, config=config):
        step_count += 1
        for node_name, state_update in event.items():
            print(f"--- Node Bitti: {node_name} ---")
            if "manifest" in state_update:
                print("⚡ Manifest güncellendi sinyali alındı!")

        if step_count > 15:
            break

    # 4. Sonuçları Doğrula
    with open(".ai_state.json", "r", encoding="utf-8") as f:
        final_manifest = json.load(f)

    tasks = final_manifest.get("tasks", [])
    found_task = next((t for t in tasks if t["id"] == "E2E_TEST"), None)

    assert found_task is not None, (
        "Main Agent, Task Manager'ı tetikleyemedi veya görev yazılmadı!"
    )
    assert found_task["title"] == "Integration Test", "Görev başlığı yanlış!"

    print("✅ ENTEGRASYON BAŞARILI: Main Agent -> Router -> Task Manager -> Disk")

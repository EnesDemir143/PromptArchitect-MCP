import importlib
import json
from pathlib import Path

import yaml
from langchain_core.messages import SystemMessage

from core.state import AgentState
from core.context_scanner import ContextScanner
from memory.json_store import JSONStore
from logger import logger


def load_tools_from_config(agent_name: str) -> list:
    """Config dosyasından belirtilen agent için tool'ları yükler."""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if not config_path.exists():
        return []

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    agent_info = config.get(agent_name, {})
    tools_metadata = agent_info.get("tools", [])

    tool_instances = []

    for t in tools_metadata:
        try:
            module_str = t["import_path"].replace(".py", "").replace("/", ".")
            module_path = (
                f"agents.{module_str}"
                if not module_str.startswith("agents")
                else module_str
            )

            module = importlib.import_module(module_path)
            tool_class = getattr(module, t["class_name"])

            # Instance oluştur
            tool_instance = tool_class(**t.get("params", {}))
            tool_instances.append(tool_instance)
        except Exception as e:
            logger.error(f"Error loading tool {t.get('class_name')}: {e}")

    return tool_instances


async def setup_node(state: AgentState) -> dict:
    """Sadece system prompt ve manifest yükler."""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    manifest_path = Path(".ai_state.json")
    updates: dict = {}

    # 1. System Prompt Yükle
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        main_agent = config.get("main_agent", {}) or {}
        sys_cfg = main_agent.get("system_prompt", {}) or {}
        content = sys_cfg.get("content")

        if isinstance(content, str) and content.strip():
            # SCANNER: Otomatik sistem ve proje taraması
            scanner = ContextScanner()
            sys_info = scanner.get_os_info()
            files = scanner.scan_directory()
            frameworks = scanner.detect_frameworks()
            languages = scanner.get_language_stats()
            
            # Context'i kaydet
            updates["system_info"] = sys_info
            updates["file_structure"] = files
            
            # Format language stats
            lang_str = ", ".join([f"{k} {v}" for k, v in languages.items()])
            
            # System Prompt'a enjekte et
            context_injection = (
                f"\n\n[AUTOMATIC CONTEXT INJECTION]\n"
                f"OS: {sys_info['os']} {sys_info['release']} ({sys_info['architecture']})\n"
                f"Shell: {sys_info['shell']}\n"
                f"Frameworks Detected: {', '.join(frameworks)}\n"
                f"Languages: {lang_str}\n"
                f"File Structure:\n{files}\n"
                f"[END CONTEXT]\n"
            )
            
            final_system_prompt = content + context_injection
            updates["messages"] = [SystemMessage(content=final_system_prompt)]
            
            logger.info("System prompt loaded with automatic context injection.")

    # 2. Manifest Yükle ve Güncelle
    json_store = JSONStore(str(manifest_path))
    manifest = json_store.load()
    
    # SCANNER (Burada da çağırıp manifest'i güncelliyoruz)
    scanner = ContextScanner()
    files = scanner.scan_directory()
    sys_info = scanner.get_os_info()
    frameworks = scanner.detect_frameworks()
    languages = scanner.get_language_stats()
    
    # Manifest'i güncelle
    manifest["project_meta"]["root_directory"] = str(Path.cwd())
    manifest["project_meta"]["tech_stack"] = frameworks
    # Architecture veya diğer alanlara da ekleyebiliriz, şimdilik bunları basalım
    
    # Context'i state'e de ekleyelim (Eğer yukarıda yapılmadıysa)
    if "system_info" not in updates:
         updates["system_info"] = sys_info
         updates["file_structure"] = files
    
    # Değişiklikleri diske yaz
    json_store.save(manifest)
    updates["manifest"] = manifest
    logger.info("Manifest loaded and updated with scanned context.")

    # Not: tools_dict ARTIK YÜKLENMİYOR.

    updates["current_agent"] = "main_agent"
    updates["next_node"] = "decide_agent"
    updates["history"] = ["Main Agent setup completed."]

    return updates

import operator
from typing import Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated


class ProjectMeta(TypedDict):
    name: str
    tech_stack: List[str]
    architecture: str
    root_directory: Optional[str]


class ProjectStatus(TypedDict):
    current_phase: str
    active_goal: str
    last_update: Optional[str]


class Task(TypedDict):
    id: str
    title: str
    status: str  # "todo", "in_progress", "completed"
    description: Optional[str]
    outcome: Optional[str]
    dependencies: Optional[List[str]]


class ProjectManifest(TypedDict):
    project_meta: ProjectMeta
    status: ProjectStatus
    tasks: List[Task]
    global_rules: List[str]


# --- LANGGRAPH STATE ---


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

    # Kalıcı hafıza artık çok daha detaylı
    manifest: ProjectManifest

    # RAG'den gelen bağlam
    relevant_context: Optional[str]

    # Nihai üretilen prompt
    final_prompt: Optional[str]

    # İşlem geçmişi (Loglar)
    history: Annotated[List[str], operator.add]

    # Akış yönetimi
    current_agent: str
    next_node: str

    # Sistem ve Proje Bağlamı (Otomatik)
    system_info: dict  # OS, Shell, etc.
    file_structure: str  # Tree view

    # Hata yönetimi
    error: Optional[str]

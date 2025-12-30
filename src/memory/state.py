import operator
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated


class ProjectManifest(TypedDict):
    project_name: str
    tech_stack: List[str]
    tasks: List[Dict[str, Any]]
    current_milestone: str


class AgentState(TypedDict):
    # Ana iletişim ve araçlar
    messages: List[BaseMessage]
    tools_dict: Dict

    # [HAFIZA] JSON'dan gelen kalıcı veriler
    manifest: ProjectManifest

    # [RAG] Vector DB'den çekilen ilgili kod parçaları veya dökümanlar
    relevant_context: Optional[str]

    # [OUTPUT] Refiner agent tarafından üretilen nihai çıktı
    final_prompt: Optional[str]

    # [LOGGING] LangGraph akışını takip etmek için adım adım geçmiş
    history: Annotated[List[str], operator.add]

    # Akış kontrolü
    current_agent: str
    next_node: str

    # Hata yönetimi
    error: Optional[str]

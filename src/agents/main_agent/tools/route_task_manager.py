from typing import Annotated, Any, Dict, List, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from agents.task_manager.agent_flow import create_task_manager_agent

# Senin projendeki importlar
from core.state import AgentState
from logger import logger
from src.agents.main_agent.node.setup_node import load_tools_from_config


# 1. LLM'in göreceği parametre şeması (Sadece request'i görür)
class RouteTaskInput(BaseModel):
    request: str = Field(
        description="A summary of what needs to be done by the Task Manager (e.g., 'Add a task', 'Update status')."
    )


# 2. Config ile uyumlu Class
class RouteToTaskManager(BaseTool):
    name: str = "route_to_task_manager"
    description: str = (
        "Delegates control to the Task Manager Agent. "
        "Use this to add, update, delete tasks or modify the project manifest."
    )
    args_schema: Type[BaseModel] = RouteTaskInput

    current_state: Optional[Dict] = None

    def _run(self, request: str) -> str:
        """Senkron çalıştırma (LangGraph async kullandığı için burası çalışmaz)."""
        return "Please use async execution."

    # 3. ASIL OLAY BURADA: Senin fonksiyon mantığını buraya taşıdık.
    async def _arun(
        self,
        request: str,
    ) -> dict:
        """
        Main Agent bu tool'u çağırdığında:
        1. Task Manager Agent'ı ayağa kaldırır.
        2. İşi yaptırır.
        3. Sonucu alıp Main Agent'a döner.
        """
        try:
            logger.info(
                f"RouteToTaskManager: Routing request '{request}' to sub-agent."
            )

            task_tools = load_tools_from_config("task_manager")
            if not task_tools:
                return {"error": "Task Manager tools could not be loaded."}

            # 2. Sub-Agent'ı oluştur (State'i değil, tool listesini veriyoruz)
            task_agent = await create_task_manager_agent(task_tools)

            # 3. Sub-Agent'ı çalıştır (State burada güncellenir ve result döner)
            # Not: Sub-agent dosyaya yazar, result ise o anki çıktıyı taşır.
            result = await task_agent.ainvoke(self.current_state)

            # 4. Sonucu işle
            # Sub-agent'ın son mesajını alıyoruz
            last_message = result["messages"][-1] if result.get("messages") else None
            summary_content = (
                last_message.content
                if last_message
                else "Task Manager completed with no output."
            )

            logger.info("RouteToTaskManager: Sub-agent execution finished.")

            # 5. Main Agent'a temiz bir çıktı dön
            return {
                "output": f"Task Manager Execution Result: {summary_content}",
                # "error": None  -> BaseTool genelde string veya dict döner, error key'i opsiyoneldir.
            }

        except Exception as e:
            logger.error(f"RouteToTaskManager Error: {e}")
            return {
                "error": str(e),
                "output": f"Failed to execute Task Manager: {str(e)}",
            }

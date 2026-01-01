from typing import Annotated, Any, List, Type

from langchain.tools import BaseTool
from langgraph.prebuilt import InjectedState
from pydantic import BaseModel, Field

from agents.task_manager.agent_flow import create_task_manager_agent

# Senin projendeki importlar
from core.state import AgentState
from logger import logger


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
    args_schema = RouteTaskInput

    def _run(self, request: str) -> str:
        """Senkron çalıştırma (LangGraph async kullandığı için burası çalışmaz)."""
        return "Please use async execution."

    # 3. ASIL OLAY BURADA: Senin fonksiyon mantığını buraya taşıdık.
    async def _arun(
        self,
        request: str,
        # DİKKAT: LangGraph bu 'Annotated' kısmını görür ve State'i buraya gizlice enjekte eder.
        state: Annotated[AgentState, InjectedState],
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

            # --- SENİN FONKSİYONUNDAKİ MANTIK ---

            # 1. Tool'ları state'den çek
            # (Hata almamak için güvenli .get kullanımı)
            all_tools = state.get("tools_dict", {})
            task_tools_map = all_tools.get("task_manager", {})

            if not task_tools_map:
                return {"error": "Task Manager tools not found in state!"}

            my_tools = list(task_tools_map.values())

            # 2. Sub-Agent'ı oluştur (State'i değil, tool listesini veriyoruz)
            task_agent = await create_task_manager_agent(my_tools)

            # 3. Sub-Agent'ı çalıştır (State burada güncellenir ve result döner)
            # Not: Sub-agent dosyaya yazar, result ise o anki çıktıyı taşır.
            result = await task_agent.ainvoke(state)

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

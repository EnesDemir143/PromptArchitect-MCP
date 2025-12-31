import json
import os
from typing import Any, Dict, List, Literal, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class TaskInput(BaseModel):
    action: Literal["add", "update", "delete"] = Field(
        description="Action to perform on tasks"
    )
    task_id: str = Field(description="Unique ID of the task (e.g., 'T1', 'setup_env')")
    title: Optional[str] = Field(None, description="Title of the task")
    status: Optional[Literal["todo", "in_progress", "completed"]] = Field(
        "todo", description="Current status of the task"
    )
    description: Optional[str] = Field(
        None, description="Detailed explanation of the task"
    )


class ManageTasks(BaseTool):
    name: str = "manage_tasks"
    description: str = "Manages the project tasks. Use this to add, update, or delete tasks in the manifest."

    args_schema = TaskInput

    filename: str = ".ai_state.json"

    def _run(
        self,
        action: str,
        task_id: str,
        title: Optional[str] = None,
        status: str = "todo",
        description: Optional[str] = None,
    ) -> str:
        msg: str = "No action performed."

        try:
            if not os.path.exists(self.filename):
                return "Error: Manifest file not found."

            with open(self.filename, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            tasks: List[Dict[str, Any]] = manifest.get("tasks", [])

            if action == "add":
                new_task = {
                    "id": task_id,
                    "title": title or "Untitled Task",
                    "status": status,
                    "description": description or "",
                }
                tasks.append(new_task)
                msg = f"Task '{task_id}' added successfully."

            elif action == "update":
                found = False
                for t in tasks:
                    if t["id"] == task_id:
                        if title is not None:
                            t["title"] = title
                        if status is not None:
                            t["status"] = status
                        if description is not None:
                            t["description"] = description
                        found = True
                        break
                msg = (
                    f"Task '{task_id}' updated."
                    if found
                    else f"Task '{task_id}' not found."
                )
            elif action == "delete":
                original_count = len(tasks)
                tasks = [t for t in tasks if t["id"] != task_id]
                if len(tasks) < original_count:
                    msg = f"Task '{task_id}' deleted successfully."
                else:
                    msg = f"Task '{task_id}' not found, nothing to delete."

            else:
                msg = f"Invalid action: {action}"

            manifest["tasks"] = tasks
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)

            return msg

        except Exception as e:
            return f"Error managing tasks: {str(e)}"

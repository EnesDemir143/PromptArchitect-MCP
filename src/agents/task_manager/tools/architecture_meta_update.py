import json
from datetime import datetime
from typing import List, Optional

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


# LLM'in hangi argümanları kullanabileceğini anlaması için şema ekledik
class ManifestUpdateInput(BaseModel):
    name: Optional[str] = Field(None, description="Project name")
    tech_stack: Optional[List[str]] = Field(None, description="Tech stack list")
    architecture: Optional[str] = Field(None, description="Project architecture")
    root_directory: Optional[str] = Field(None, description="Project root directory")
    current_phase: Optional[str] = Field(
        None, description="Current phase (e.g., Development)"
    )
    active_goal: Optional[str] = Field(None, description="Current active goal")
    global_rules: Optional[List[str]] = Field(
        None, description="Full list of global rules"
    )


class MimariMetaUpdater(BaseTool):
    name: str = "update_project_manifest"
    description: str = (
        "Updates project metadata, status, and global rules in the manifest file."
    )
    args_schema = ManifestUpdateInput
    filename: str = ".ai_state.json"

    def _run(
        self,
        name: Optional[str] = None,
        tech_stack: Optional[List[str]] = None,
        architecture: Optional[str] = None,
        root_directory: Optional[str] = None,
        current_phase: Optional[str] = None,
        active_goal: Optional[str] = None,
        global_rules: Optional[List[str]] = None,
    ) -> str:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 1. Project Meta Güncelleme
            if name:
                manifest["project_meta"]["name"] = name
            if tech_stack:
                manifest["project_meta"]["tech_stack"] = tech_stack
            if architecture:
                manifest["project_meta"]["architecture"] = architecture
            if root_directory:
                manifest["project_meta"]["root_directory"] = root_directory

            # 2. Project Status Güncelleme
            if current_phase:
                manifest["status"]["current_phase"] = current_phase
            if active_goal:
                manifest["status"]["active_goal"] = active_goal

            # Her güncellemede tarih otomatik güncellensin
            manifest["status"]["last_update"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # 3. Global Rules Güncelleme
            if global_rules is not None:
                manifest["global_rules"] = global_rules

            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)

            return "Project manifest successfully updated."
        except Exception as e:
            return f"Error updating manifest: {str(e)}"

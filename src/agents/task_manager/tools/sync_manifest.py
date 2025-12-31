import json
from datetime import datetime  # Eklendi
from typing import Any, Dict

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SyncManifestInput(BaseModel):
    manifest_data: Dict[str, Any] = Field(
        description="The complete project manifest to save."
    )


class SyncManifest(BaseTool):
    name: str = "sync_manifest"
    description: str = "Saves the current project state to a JSON file. Use this for full state persistence."
    args_schema = SyncManifestInput
    filename: str = ".ai_state.json"

    def _run(self, manifest_data: Dict[str, Any]) -> str:
        try:
            if "status" in manifest_data:
                manifest_data["status"]["last_update"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=4, ensure_ascii=False)
            return f"Successfully synchronized manifest to {self.filename}"
        except Exception as e:
            return f"Error during synchronization: {str(e)}"

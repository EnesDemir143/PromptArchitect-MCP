import json
from typing import Any, Dict

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class SyncManifestInput(BaseModel):
    manifest_data: Dict[str, Any] = Field(
        description="The complete project manifest to save."
    )


class SyncManifest(BaseTool):
    name: str = "sync_manifest"
    description: str = "Saves the current project state to a JSON file."

    args_schema = SyncManifestInput

    filename: str = ".ai_state.json"

    def _run(self, manifest_data: Dict[str, Any]) -> str:
        """Saves the manifest data to the local file system."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=4, ensure_ascii=False)
            return f"Successfully synchronized manifest to {self.filename}"
        except Exception as e:
            return f"Error during synchronization: {str(e)}"

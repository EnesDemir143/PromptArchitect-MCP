import os

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class FileInput(BaseModel):
    relative_path: str = Field(
        description="Relative path of the file from project root (e.g., 'core/state.py')"
    )


class FileReader(BaseTool):
    name: str = "read_file"
    description: str = (
        "Reads file content from the project directory to gather context."
    )
    args_schema = FileInput

    base_dir: str = os.getcwd()

    def _run(self, relative_path: str) -> str:
        """Reads a file within the base directory."""
        try:
            # Config'den gelen base_dir ile AI'dan gelen yolu birleştiriyoruz
            full_path = os.path.normpath(os.path.join(self.base_dir, relative_path))

            # Güvenlik Kontrolü: base_dir dışına çıkılmasını engelle (Path Traversal)
            if not full_path.startswith(os.path.abspath(self.base_dir)):
                return "Error: Access denied. You cannot read files outside the project root."

            if not os.path.exists(full_path):
                return f"Error: File not found at {relative_path}"

            if os.path.isdir(full_path):
                return (
                    f"Path is a directory. Contents: {', '.join(os.listdir(full_path))}"
                )

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            return f"--- Content: {relative_path} ---\n{content}\n"

        except Exception as e:
            return f"Error reading {relative_path}: {str(e)}"

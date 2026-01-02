import json
import os
import shutil
from pathlib import Path
from logger import logger


class JSONStore:    
    def __init__(
        self, filename=None, example_filename=".ai_state.json.example"
    ):
        self.root_dir: Path = Path(__file__).resolve().parents[2]
        if filename:
            self.filename = str(Path(filename).resolve())
        else:
            self.filename = str(self.root_dir / ".ai_state.json")
            
        if os.path.isabs(example_filename):
            self.example_filename = example_filename
        else:
            self.example_filename = str(self.root_dir / example_filename)
            
        self._ensure_file_exists()

    def load_default_template(self) -> dict:
        """State yapımıza tam uyumlu varsayılan şablon."""
        return {
            "project_meta": {
                "name": "New AI Project",
                "tech_stack": [],
                "architecture": "Agentic Orchestrator",
                "root_directory": str(self.root_dir),
            },
            "status": {
                "current_phase": "Initialization",
                "active_goal": "Initial setup",
                "last_update": None,
            },
            "tasks": [],
            "global_rules": ["Follow project best practices."],
        }

    def _ensure_file_exists(self):
        """Dosya yoksa example'dan kopyala veya default oluştur."""
        if not os.path.exists(self.filename):
            if os.path.exists(self.example_filename):
                shutil.copy(self.example_filename, self.filename)
            else:
                self.save(self.load_default_template())

    def load(self) -> dict:
        try:
            if not os.path.exists(self.filename):
                return self.load_default_template()
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            # Dosya bozuksa veya okunamazsa varsayılanı dön
            logger.error(f"Error loading manifest: {str(e)}")
            return self.load_default_template()

    def save(self, data: dict):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Manifest saved successfully to {self.filename}")
        except Exception as e:
            logger.error(f"Error saving manifest: {str(e)}")

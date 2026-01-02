import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class ContextScanner:
    """
    Scans the environment and project structure to provide rich context
    to the AI agent.
    """

    def __init__(self, root_dir: Optional[str] = None):
        if root_dir:
            self.root_dir = Path(root_dir).resolve()
        else:
            # src/core/context_scanner.py -> parents[2] is project root
            self.root_dir = Path(__file__).resolve().parents[2]
        self.ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".pytest_cache",
            "venv",
            "env",
            ".venv",
            ".idea",
            ".vscode",
            "dist",
            "build",
            "coverage",
        }
        self.ignore_files = {
            ".DS_Store",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "test_execution.log", # Log files
        }

    def get_os_info(self) -> Dict[str, str]:
        """Detects OS, release, and standard shell command style."""
        system = platform.system()
        release = platform.release()
        
        # Determine likely shell
        shell = "bash"
        if system == "Windows":
            shell = "powershell"
        elif "SHELL" in os.environ:
             shell_path = os.environ["SHELL"]
             if "zsh" in shell_path:
                 shell = "zsh"
             elif "bash" in shell_path:
                 shell = "bash"
             elif "fish" in shell_path:
                 shell = "fish"
        
        return {
            "os": system,
            "release": release,
            "shell": shell,
            "architecture": platform.machine()
        }

    def scan_directory(self, max_depth: int = 3) -> str:
        """Returns a string representation of the directory tree."""
        tree = []
        
        try:
            for root, dirs, files in os.walk(self.root_dir):
                # Filter directories
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
                
                # Calculate depth
                rel_path = Path(root).relative_to(self.root_dir)
                depth = len(rel_path.parts)
                
                if depth > max_depth:
                    continue
                
                indent = "  " * depth
                if str(rel_path) != ".":
                    tree.append(f"{indent}📂 {rel_path.name}/")
                else:
                    tree.append(f"📂 {self.root_dir.name}/ (ROOT)")
                
                # Add files
                sub_indent = "  " * (depth + 1)
                for f in files:
                    if f not in self.ignore_files and not f.endswith(".pyc"):
                         tree.append(f"{sub_indent}📄 {f}")
                         
        except Exception as e:
            return f"Error scanning directory: {e}"
            
        return "\n".join(tree)

    def get_language_stats(self) -> Dict[str, str]:
        """Scans all files to calculate language usage statistics."""
        extension_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript (React)",
            ".jsx": "JavaScript (React)",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".md": "Markdown",
            ".json": "JSON",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".rb": "Ruby",
            ".php": "PHP",
            ".sh": "Shell",
            ".sql": "SQL",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".toml": "TOML",
            ".xml": "XML",
        }
        
        stats = {}
        total_files = 0
        
        try:
            for root, dirs, files in os.walk(self.root_dir):
                # Filter ignore dirs in-place
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
                
                for f in files:
                    ext = Path(f).suffix.lower()
                    if ext in extension_map:
                        lang = extension_map[ext]
                        stats[lang] = stats.get(lang, 0) + 1
                        total_files += 1
                        
        except Exception:
            pass # Fail silently for stats
            
        if total_files == 0:
            return {}

        # Calculate percentages and sort
        lang_stats = {}
        sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
        
        results = {}
        for lang, count in sorted_stats:
            percent = (count / total_files) * 100
            if percent >= 1.0: # Ignore < 1%
                results[lang] = f"{percent:.1f}%"
                
        return results

    def detect_frameworks(self) -> List[str]:
        """Heuristically detects frameworks using an expanded file map."""
        frameworks = []
        
        files_map = {
            # Python
            "requirements.txt": ["Python"],
            "pyproject.toml": ["Python"],
            "Pipfile": ["Python (Pipenv)"],
            "poetry.lock": ["Python (Poetry)"],
            "manage.py": ["Django"],
            "app.py": ["Flask/Python"],
            "main.py": ["Python"],
            "uvicorn": ["FastAPI"], # If found in file content ideally, but filename for now
            
            # JavaScript / Node
            "package.json": ["Node.js"],
            "yarn.lock": ["Yarn"],
            "pnpm-lock.yaml": ["PNPM"],
            "bun.lockb": ["Bun"],
            "deno.json": ["Deno"],
            
            # Frontend Frameworks
            "next.config.js": ["Next.js"],
            "next.config.ts": ["Next.js"],
            "nuxt.config.js": ["Nuxt.js"],
            "nuxt.config.ts": ["Nuxt.js"],
            "vue.config.js": ["Vue.js"],
            "vite.config.js": ["Vite"],
            "vite.config.ts": ["Vite"],
            "angular.json": ["Angular"],
            "tailwind.config.js": ["TailwindCSS"],
            "tailwind.config.ts": ["TailwindCSS"],
            
            # Other Languages
            "go.mod": ["Go"],
            "Cargo.toml": ["Rust"],
            "Gemfile": ["Ruby on Rails"],
            "composer.json": ["PHP (Composer)"],
            "pom.xml": ["Java (Maven)"],
            "build.gradle": ["Java (Gradle)"],
            "Makefile": ["Make"],
            "Dockerfile": ["Docker"],
            "docker-compose.yml": ["Docker Compose"],
        }
        
        # Check files in root
        found_files = set(os.listdir(self.root_dir))
        
        for fname, techs in files_map.items():
            if fname in found_files:
                frameworks.extend(techs)
        
        return list(set(frameworks))

    def get_full_context(self) -> Dict:
        """Aggregates all context info."""
        return {
            "system": self.get_os_info(),
            "file_tree": self.scan_directory(),
            "frameworks": self.detect_frameworks(),
            "languages": self.get_language_stats()
        }

# 🏗️ PromptArchitect MCP Server

PromptArchitect is a high-performance **Model Context Protocol (MCP)** server designed to streamline the software development lifecycle by providing an "Architect First" approach. It uses advanced LangChain agents to analyze coding requests, break them down into actionable tasks, and maintain a structured project state.

---

## ✨ Features

- **Architect First Workflow**: Prevents "blind coding" by requiring a structured plan before implementation.
- **LangChain Integration**: Leverages powerful LLM agents (OpenAI, Gemini, Anthropic) to handle complex reasoning.
- **State Management**: Persists project structure and task progress in `.ai_state.json`.
- **Dual Interface**: Use it via **CLI** for direct interaction or as an **MCP Server** for integration with IDEs like Cursor or VS Code.
- **Flexible LLM Support**: Supports multiple providers through environment configuration.

---

## 🚀 Installation & Setup

Follow these steps to get PromptArchitect running on your local machine.

### 1. Prerequisites
- **Python 3.10+**
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/EnesDemir143/PromptArchitect-MCP.git
cd PromptArchitect-MCP
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # MacOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Open `.env` and add your API keys:
```env
LLM_PROVIDER=openai # openai, gemini, or anthropic
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

---

## 🕹 Usage

### As an MCP Server (Recommended for Cursor/VS Code)
To use PromptArchitect with an MCP-compatible IDE, add it to your `mcp` settings:

**Example Config (`.mcp.json`):**
```json
{
  "mcpServers": {
    "PromptArchitect": {
      "command": "python",
      "args": ["/path/to/PromptArchitect-MCP/src/server.py"],
      "env": {
        "OPENAI_API_KEY": "...",
        "LLM_PROVIDER": "openai"
      }
    }
  }
}
```

### Using the CLI
You can also run the architect flow directly from your terminal:
```bash
python src/cli.py "Add a login page with JWT authentication"
```

---

## 📂 Project Structure

```text
PromptArchitect-MCP/
├── src/
│   ├── agents/          # Agent definitions (Main, Refiner, Task Manager)
│   ├── memory/          # State persistence (JSON & Vector Store)
│   ├── core/            # Core logic and utilities
│   ├── server.py        # FastMCP Server implementation
│   └── cli.py           # Command-line interface
├── tests/               # Pytest suite
├── .ai_state.json       # Current project blueprints & task status
├── requirements.txt     # Python dependencies
└── pytest.ini           # Testing configuration
```

---

## 🤝 Project Workflow

1. **Request**: User sends a request (e.g., "Fix the navbar layout").
2. **Analysis**: `architect_request` tool is triggered.
3. **Planning**: Agents analyze the codebase and generate a detailed implementation plan in `.ai_state.json`.
4. **Execution**: The developer (or an automated assistant) follows the plan step-by-step.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# 🏗️ PromptArchitect MCP Server

PromptArchitect is a high-performance **Model Context Protocol (MCP)** server designed to streamline the software development lifecycle by providing an "Architect First" approach. It uses advanced LangGraph agents to analyze coding requests, break them down into actionable tasks, and maintain a structured project state.

---

## ✨ Features

- **Architect First Workflow**: Prevents "blind coding" by requiring a structured plan and task breakdown before implementation starts.
- **LangGraph Orchestration**: Uses a sophisticated graph-based multi-agent system to handle complex reasoning, task decomposition, and state management.
- **State Persistence**: Maintains a persistent project manifest in `.ai_state.json`, tracking tasks, progress, and architectural rules.
- **Dual Interface**:
  - **MCP Server**: Seamless integration with MCP-compatible IDEs like Cursor, VS Code, or Claude Desktop.
  - **CLI**: Direct interaction via terminal for standalone architectural planning.
- **Flexible LLM Support**: Supports multiple providers (OpenAI, Gemini, Anthropic) through standard environment variables.
- **Structured Memory**: Utilizes both JSON-based state storage and vector-based long-term memory for project context.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.10+** (Recommend using [Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) or [venv](https://docs.python.org/3/library/venv.html))
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
Open `.env` and configure your preferred LLM provider:
```env
# LLM Provider: openai, gemini, or anthropic
LLM_PROVIDER=openai

# API Keys
OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
```

---

## 🕹 Usage

### As an MCP Server (Recommended)

To integrate PromptArchitect with your IDE (e.g., Cursor or VS Code), add the following configuration to your MCP settings.

**Example Config (`mcp_config.json`):**
```json
{
    "mcpServers": {
        "PromptArchitect": {
            "command": "/home/jieuna1/miniconda3/envs/prompt-mcp/bin/python",
            "args": [
                "/home/jieuna1/Documents/PromptArchitect-MCP/src/server.py"
            ],
            "env": {
                "LLM_PROVIDER": "openai",
                "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY"
            }
        }
    }
}
```
> [!NOTE]
> Ensure the `command` path points to your specific Python interpreter within your virtual environment/conda environment.

### Using the CLI
Run the architect directly from your terminal to plan new features:
```bash
python src/cli.py "Design and implement a JWT-based authentication system"
```

---

## 🧪 Running Tests

The project uses `pytest` for automated testing. You can run the test suite using:
```bash
pytest
```
To see more detailed output, use:
```bash
pytest -v
```

---

## 📂 Project Structure

```text
PromptArchitect-MCP/
├── src/
│   ├── agents/          # Agent definitions (Main, Task Manager, Refiner)
│   ├── memory/          # State persistence (JSON Store, Vector Store)
│   ├── core/            # Tool definitions and core utilities
│   ├── server.py        # FastMCP Server implementation
│   ├── cli.py           # Command-line interface
│   ├── graph.py         # LangGraph orchestration logic
│   └── logger.py        # Centralized logging
├── tests/               # Pytest suite
├── .ai_state.json       # Current project blueprints & task status
├── requirements.txt     # Python dependencies
└── pytest.ini           # Testing configuration
```

---

## 🤝 Project Workflow

1. **Analysis**: When a request is made, the `architect_request` tool triggers the agentic graph.
2. **Decomposition**: The Task Manager agent breaks down the request into granular tasks.
3. **State Update**: The project manifest `.ai_state.json` is automatically updated with the new tasks and plans.
4. **Implementation**: The Developer agent (or user) follows the generated plan, updating task statuses in real-time.

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.


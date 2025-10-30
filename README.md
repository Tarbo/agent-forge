# 🤖 AgentForge

**Agentic Document Creation powered by LangGraph**

Chat with AI to generate content, then export to professional documents (Word/PDF) with intelligent formatting. Built to showcase **LangGraph 1.0** for production-ready agentic workflows - demonstrating how to build intelligent, multi-step AI systems that go beyond simple chat wrappers.

---

## ✨ Why AgentForge?

**🔒 Privacy & Control**
- Run 100% locally with Ollama - zero data leaves your infrastructure
- Perfect for sensitive/regulated industries
- No telemetry, no cloud dependencies

**💰 Zero Cost, Unlimited Scale**
- No API fees with local models
- No rate limits - process unlimited documents
- Predictable infrastructure costs

**🔌 Universal LLM Compatibility**
- Works with **any LLM provider**: OpenAI, Anthropic, Ollama, Azure, AWS, Google, or custom endpoints
- Plug in your organization's fine-tuned models
- Switch providers via config - no code changes

**🤖 True Agentic Intelligence**
- Intelligent export intent detection from natural language
- Auto-cleans LLM meta-commentary from exports
- Dynamic formatting extraction
- Extensible agent workflows with LangGraph

**📄 Export Formats**
- **Word** (`.docx`) - Formatted documents with python-docx
- **PDF** (`.pdf`) - Professional PDFs with reportlab

---

## 🎯 Perfect For

- **Enterprises** with in-house LLMs or privacy requirements
- **High-volume workflows** needing to bypass rate limits
- **Regulated industries** (healthcare, finance, legal, government)
- **Developers** building custom agentic document systems

---

## 🏗️ Architecture (LangGraph v1.0 StateGraph)

```mermaid
graph TB
    A[🔄 START] --> B[🧠 Analyzer Node<br/>Detects export intent + format]
    B --> C[🧹 Content Cleaner Node<br/>Removes meta-commentary]
    C --> D[🎨 Extract Formatting Node<br/>Extracts style preferences]
    D --> E{🔀 Router<br/>Conditional Edge}
    
    E -->|"word"| F1[📄 Word Tool Node<br/>Applies formatting]
    E -->|"pdf"| F2[📕 PDF Tool Node<br/>Applies formatting]
    
    F1 --> G[📢 Notification Node<br/>Opens file]
    F2 --> G
    
    G --> H[✅ END]
    
    style A fill:#90EE90
    style B fill:#87CEEB
    style C fill:#FFB6C1
    style D fill:#FFD700
    style E fill:#FFB6C1
    style F1 fill:#DDA0DD
    style F2 fill:#DDA0DD
    style G fill:#98FB98
    style H fill:#90EE90
```

### StateGraph Components:
- **State**: `{text: str, prompt: str, export_intent: bool, format: str, formatting: dict, file_path: str}`
- **Nodes**: 
  - `analyzer_node` - Detects export intent and desired format (Word/PDF) using structured LLM output
  - `content_cleaner_node` - Removes LLM meta-commentary and conversational fluff
  - `extract_formatting_node` - Uses LLM with structured output (Pydantic) to extract formatting preferences
  - `word_node` / `pdf_node` - Export tools with dynamic property registries
  - `notification_node` - Logs completion and opens file
- **Edges**: Sequential flow from analyzer → cleaner → formatting → router
- **Conditional Edges**: Router directs to Word or PDF tool based on detected format

---

## 📋 Prerequisites

- **Python 3.8+**
- **LLM Provider** (choose one):
  - **Ollama** (local, free) - Recommended for privacy, OR
  - **OpenAI API key** (cloud, paid), OR
  - **Anthropic API key** (cloud, paid)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Tarbo/agent-forge.git
cd agent-forge
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example env file
cp env.example .env

# Edit .env with your configuration
nano .env  # or use your favorite editor
```

**Example `.env` file:**

```env
# LLM Provider (choose one)

# Option 1: Ollama (Local, Private, No API costs)
USE_OLLAMA=true
OLLAMA_MODEL=phi3_q4:latest
OLLAMA_BASE_URL=http://localhost:11434

# Option 2: OpenAI
# OPENAI_API_KEY=sk-your-openai-key-here
# OPENAI_MODEL=gpt-3.5-turbo

# Option 3: Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Application Settings
EXPORT_DIRECTORY=~/Downloads/llm-exports
```

> **Note:** For Ollama setup instructions, see `env.example` or the Ollama section below.

---

## 🚀 Usage

### Option 1: AgentForge Chat Interface 💬

Run the ChatGPT-style web interface:

```bash
streamlit run streamlit_app.py
```

This opens at `http://localhost:8501` with:

**ChatGPT-Style Workflow:**
1. **💬 Chat** with the AI to generate content (articles, proposals, reports, etc.)
2. **📥 Export** any assistant message by:
   - Clicking the "Export as Word/PDF" button below any message
   - OR typing "export as Word/PDF" in the chat
3. **🧹 AI auto-cleans** meta-commentary ("Would you like me to...", etc.)
4. **⬇️ Download** your formatted document instantly
5. **🔄 Continue** chatting and exporting as needed!

**Features:**
- Natural conversation with LLM
- Inline export buttons for every AI response
- Intelligent export intent detection
- Automatic content cleaning
- Beautiful modern UI with dark text on light backgrounds

### Option 2: Run Tests

The best way to see the workflow in action is through the test suite:

```bash
# Run all tests
pytest tests/test_workflow.py -v

# Run specific test
pytest tests/test_workflow.py::TestWordExport::test_word_export_with_formatting -v

# Run with coverage
pytest tests/test_workflow.py --cov=src --cov-report=html --cov-report=term
```

### Option 3: Programmatic API

You can also use the workflow directly in Python:

```python
from src.agent import run_export

# Export with formatting instructions
text = """My Report Title

This is the introduction paragraph.

This is the conclusion."""

prompt = "Export as Word with Arial 14pt font, bold text, and centered title"

result = run_export(text=text, prompt=prompt)
print(f"File created: {result['file_path']}")
```

### Example Chat Workflow

**You:** "Write a project proposal for a mobile app that helps people track their fitness goals."

**AI:** *[Generates detailed proposal]* "Would you like me to add more sections or refine any part?"

**You:** *Click "Export as Word"* → Download button appears

**AI:** Removes "Would you like me to..." fluff → Creates clean Word doc

**Download:** Clean, professional proposal without conversational meta-commentary

---

**Alternative: Export via chat**

**You:** "Export the last response as PDF with Times New Roman font"

**AI:** *Auto-detects export intent* → Cleans content → Generates PDF → Shows download button

---

## 📁 Project Structure

```
llm-export-tools/
├── streamlit_app.py         # 💬 AgentForge chat interface (main entry point)
├── requirements.txt         # Dependencies
├── pytest.ini               # Test configuration
├── env.example              # Environment template
├── .env                     # Your configuration (create from env.example)
│
├── config/                  # Configuration
│   └── settings.py          # LLM provider & settings loader
│
├── src/
│   ├── agent/               # 🤖 LangGraph agentic workflow
│   │   ├── state.py         # TypedDict state definition (ExportState)
│   │   ├── data_models.py   # Pydantic models for structured LLM output
│   │   ├── nodes.py         # Node functions (analyzer, content_cleaner, formatter, tools, notification)
│   │   ├── export_graph.py  # StateGraph definition & compilation
│   │   └── __init__.py      # Exports run_export function
│   │
│   ├── tools/               # 📄 Export tool implementations
│   │   ├── word_tool.py     # Word (.docx) export with dynamic property registry
│   │   ├── pdf_tool.py      # PDF export with dynamic property registry
│   │   └── __init__.py
│   │
│   └── utils/               # 🔧 Utilities
│       ├── logger.py        # Centralized logging
│       ├── file_manager.py  # File operations & path management
│       └── __init__.py
│
├── tests/                   # ✅ Test suite
│   ├── test_workflow.py     # Integration tests for full agentic workflow
│   └── __init__.py
│
├── exports/                 # 📁 Generated files (auto-created)
│
├── visualize_graph.py       # Script to generate StateGraph visualization
├── graph_visualization.mmd  # Mermaid diagram output
└── GRAPH_VISUALIZATION.md   # Visualization documentation
```

---

## ⚙️ Configuration

Edit `.env` to customize:

### LLM Provider

**Option 1: Ollama (Local, Private, No API Costs)** ⭐ Recommended
```env
USE_OLLAMA=true
OLLAMA_MODEL=phi3_q4:latest
OLLAMA_BASE_URL=http://localhost:11434
```

Requirements:
1. Install Ollama: https://ollama.ai
2. Pull or import a model (see below)
3. Start Ollama: `ollama serve`

**Option 2: OpenAI (Cloud)**
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**Option 3: Anthropic (Cloud)**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Application Settings

```env
# Where to save exported files
EXPORT_DIRECTORY=~/Downloads/llm-exports

# Auto-open files after export (default: false)
AUTO_OPEN_FILE=false
```

### Ollama: Importing Models from HuggingFace

If you're behind a corporate firewall and can't use `ollama pull`, you can manually import models:

**Step 1: Download GGUF model from HuggingFace**
- Example: [bartowski/Llama-3.2-3B-Instruct-GGUF](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF)
- Download the `Q4_K_M` or `Q5_K_M` variant (~2GB)

**Step 2: Create a `Modelfile`**
```dockerfile
FROM ./Llama-3.2-3B-Instruct-Q4_K_M.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9

TEMPLATE """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|><|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{ .Response }}<|eot_id|>"""

SYSTEM """You are a helpful AI assistant."""
```

**Step 3: Import into Ollama**
```bash
cd ~/Downloads  # Where you saved the GGUF file
ollama create llama3.2:3b-instruct -f Modelfile
```

**Step 4: Update your `.env`**
```env
OLLAMA_MODEL=llama3.2:3b-instruct
```

---

## 🔧 Development

### Run Tests

```bash
pytest tests/
```

### Add a New Export Format

1. Add file extension to `src/utils/file_manager.py`
2. Create a new tool file in `src/tools/`
3. Use `@tool` decorator to define the tool
4. Add a node function that calls your tool
5. Register the node in `src/agent/export_graph.py`
6. Update the router conditional edge logic

**Example:**

```python
# Step 1: src/utils/file_manager.py (add extension mapping)
extensions = {
    "word": ".docx",
    "pdf": ".pdf",
    "markdown": ".md",  # ← Add this
    # ...
}

# Step 2: src/tools/markdown_tool.py
from langchain_core.tools import tool
from src.utils.file_manager import get_full_path

@tool
def export_to_markdown(text: str, formatting: dict = None) -> str:
    """Export text as a Markdown file (.md) with optional formatting"""
    file_path = get_full_path("markdown", formatting.get("custom_name") if formatting else None)
    
    # Split into title and content
    lines = text.strip().split('\n')
    title = lines[0] if lines else ""
    content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
    
    # Build markdown with heading
    markdown_content = f"# {title}\n\n{content}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(file_path)

# Step 3: src/agent/nodes.py
def markdown_node(state: ExportState) -> ExportState:
    """Node that executes markdown export"""
    file_path = export_to_markdown.invoke({
        "text": state["text"],
        "formatting": state.get("formatting", {})
    })
    return {**state, "file_path": file_path}

# Step 4: src/agent/export_graph.py (register node)
graph.add_node("markdown_tool", markdown_node)

# Step 5: src/agent/export_graph.py (add edge from markdown to notification)
graph.add_edge("markdown_tool", "notification")

# Step 6: src/agent/nodes.py (update router to include markdown)
def route_to_tool(state: ExportState) -> str:
    """Router that directs to appropriate tool based on format"""
    format_type = state["format"]
    if format_type == "word":
        return "word_tool"
    elif format_type == "pdf":
        return "pdf_tool"
    elif format_type == "markdown":
        return "markdown_tool"  # ← Add this
    else:
        return "word_tool"  # Default

# Step 7: src/agent/export_graph.py (update conditional edge mapping)
workflow.add_conditional_edges(
    "extract_formatting",
    route_to_tool,
    {
        "word_tool": "word_tool",
        "pdf_tool": "pdf_tool",
        "markdown_tool": "markdown_tool",  # ← Add this mapping
    }
)
```

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### LLM Connection Issues

- Check your API key is correct in `.env`
- Verify internet connection (for cloud LLMs)
- For Ollama, ensure it's running: `ollama serve`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 💡 Why AgentForge Was Built

This project was created to explore **LangGraph 1.0's capabilities** for building real-world agentic AI applications - systems that can autonomously plan, execute, and adapt through multi-step workflows.

### The AgentForge Advantage

**Traditional LLM Limitations:**
- ❌ "You've reached your usage limit"
- ❌ Rate limits and throttling
- ❌ Expensive API subscriptions
- ❌ Privacy concerns sending data to cloud
- ❌ Vendor lock-in

**AgentForge Solution:**
- ✅ **Unlimited** - No rate limits, no waiting
- ✅ **Private** - Run 100% locally with Ollama
- ✅ **Zero cost** - Free open-source models (phi3, mistral, llama, etc.)
- ✅ **Fast** - No network latency
- ✅ **Flexible** - Works with any LLM provider (OpenAI, Anthropic, Azure, AWS, Google, custom endpoints)
- ✅ **Enterprise-ready** - Plug in your organization's fine-tuned models

---

## 🎯 Roadmap

- [ ] Add more export formats (Excel `.xlsx`, CSV, JSON, Markdown `.md`)
- [ ] Multi-turn conversation refinement before export
- [ ] Support for images in documents
- [ ] Custom styling templates and presets
- [ ] Batch export functionality
- [ ] Export history and version tracking
- [ ] Package as standalone desktop app (no Python required)
- [ ] Docker container for easy deployment

---

## 📧 Support

Having issues? Open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using LangGraph v1.0, LangChain, and Streamlit by [@Tarbo](https://github.com/Tarbo)**

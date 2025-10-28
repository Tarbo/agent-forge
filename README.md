# 🚀 LLM Export Tools

**An agentic AI workflow that bypasses API rate limits by converting text into various file formats using LangGraph v1.0.**

Stop waiting for API limits! This tool uses a LangGraph-powered StateGraph to intelligently export your text to Word or PDF formats with customizable formatting based on natural language prompts.

---

## ✨ Features

- 🤖 **AI-Powered Format Selection** - LangGraph StateGraph intelligently routes to the right tool
- 🎨 **Dynamic Formatting** - LLM extracts styling preferences from natural language
- 📄 **Export Formats** (Current):
  - **Word** (`.docx`) - Formatted documents with python-docx
  - **PDF** (`.pdf`) - Professional PDFs with reportlab
- 🔒 **Privacy-First** - All processing happens locally (supports OpenAI, Anthropic)
- ⚡ **Bypass API Rate Limits** - Use your own API keys or Ollama (coming soon)
- 🧪 **Full Test Coverage** - Comprehensive pytest suite
- 🔧 **Extensible** - Property registry pattern for easy feature additions

**Coming Soon:**
- 🎯 GUI with global hotkey activation
- 📊 Excel, CSV, and JSON export formats

---

## 🏗️ Architecture (LangGraph v1.0 StateGraph)

```mermaid
graph TB
    A[🔄 START] --> B[🧠 Analyzer Node<br/>Detects format from prompt]
    B --> C[🎨 Extract Formatting Node<br/>Extracts style preferences]
    C --> D{🔀 Router<br/>Conditional Edge}
    
    D -->|"word"| E1[📄 Word Tool Node<br/>Applies formatting]
    D -->|"pdf"| E2[📕 PDF Tool Node<br/>Applies formatting]
    
    E1 --> F[📢 Notification Node<br/>Opens file]
    E2 --> F
    
    F --> G[✅ END]
    
    style A fill:#90EE90
    style B fill:#87CEEB
    style C fill:#FFD700
    style D fill:#FFB6C1
    style E1 fill:#DDA0DD
    style E2 fill:#DDA0DD
    style F fill:#98FB98
    style G fill:#90EE90
```

### StateGraph Components:
- **State**: `{text: str, prompt: str, format: str, formatting: dict, file_path: str}`
- **Nodes**: 
  - `analyzer_node` - Detects desired format (Word/PDF)
  - `extract_formatting_node` - Uses LLM with structured output to extract formatting preferences
  - `word_node` / `pdf_node` - Export tools with dynamic property registries
  - `notification_node` - Logs completion and opens file
- **Edges**: Sequential flow from analyzer → formatting → router
- **Conditional Edges**: Router directs to Word or PDF tool based on detected format

---

## 📋 Prerequisites

- **Python 3.8+**
- **API Key** for LLM provider:
  - OpenAI API key, OR
  - Anthropic API key

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/llm-export-tools.git
cd llm-export-tools
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
cp config/.env.example .env

# Edit .env with your API keys
nano .env  # or use your favorite editor
```

**Example `.env` file:**

```env
# LLM Provider (choose one)
OPENAI_API_KEY=sk-your-openai-key-here
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Application Settings
EXPORT_DIRECTORY=~/Downloads/llm-exports
```

> **Note:** Ollama support coming in a future PR!

---

## 🚀 Usage

### Option 1: Run Tests (Recommended)

The best way to see the workflow in action is through the test suite:

```bash
# Run all tests
pytest tests/test_workflow.py -v

# Run specific test
pytest tests/test_workflow.py::TestWordExport::test_word_export_with_formatting -v

# Run with coverage
pytest tests/test_workflow.py --cov=src --cov-report=html --cov-report=term
```

### Option 2: Programmatic API

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

### Example Prompts

| Prompt | Result |
|--------|--------|
| `"Export as Word document with Arial 14pt font, bold text, and centered title"` | `.docx` with custom formatting |
| `"Save as PDF with Times-Roman font and 1-inch margins"` | Professional PDF with layout |
| `"Export to Word"` | `.docx` with default formatting |
| `"Make it a PDF with italic text"` | PDF with italic styling |

---

## 📁 Project Structure

```
llm-export-tools/
├── requirements.txt         # Dependencies
├── pytest.ini               # Test configuration
├── .env                     # Configuration (create from config/.env.example)
│
├── config/                  # Configuration
│   ├── settings.py          # Settings loader
│   └── .env.example         # Template
│
├── src/
│   ├── agent/               # LangGraph workflow
│   │   ├── state.py         # TypedDict state definition
│   │   ├── data_models.py   # Pydantic models for structured output
│   │   ├── nodes.py         # Node functions (analyzer, formatter, tools, notification)
│   │   ├── export_graph.py  # StateGraph definition
│   │   └── __init__.py      # Exports run_export function
│   │
│   ├── tools/               # Export tools
│   │   ├── word_tool.py     # Word export with property registry
│   │   ├── pdf_tool.py      # PDF export with property registry
│   │   └── __init__.py
│   │
│   └── utils/               # Utilities
│       ├── logger.py        # Centralized logging
│       ├── file_manager.py  # File operations
│       └── __init__.py
│
├── tests/                   # Test suite
│   ├── test_workflow.py     # Integration tests
│   └── __init__.py
│
├── visualize_graph.py       # Generate StateGraph diagram
├── graph_visualization.mmd  # Mermaid diagram
└── GRAPH_VISUALIZATION.md   # Visualization documentation
```

---

## ⚙️ Configuration

Edit `.env` to customize:

### LLM Provider

**Option 1: OpenAI**
```env
OPENAI_API_KEY=sk-your-key-here
```

**Option 2: Anthropic**
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> **Coming Soon:** Ollama support for local, private LLM inference

### Application Settings

```env
# Where to save exported files
EXPORT_DIRECTORY=~/Downloads/llm-exports
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

## 💡 Why This Tool?

### The Problem
ChatGPT API has rate limits that interrupt your workflow:
- "You've reached your usage limit"
- "Please wait X minutes before trying again"
- Expensive API calls for simple exports

### The Solution
This tool runs **entirely on your machine**, bypassing all API rate limits:
- ✅ Unlimited exports
- ✅ Complete privacy (data stays local)
- ✅ Faster processing (no network latency)
- ✅ Lower cost (only pay for LLM inference, not per-export)

---

## 🎯 Roadmap

- [ ] Add more export formats (Markdown, HTML, LaTeX)
- [ ] Support for images in documents
- [ ] Batch export multiple selections
- [ ] Cloud sync integration (optional)
- [ ] Custom styling templates
- [ ] Multi-language support
- [ ] Package as standalone app (no Python required)

---

## 📧 Support

Having issues? Open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ using LangGraph v1.0 and Python**

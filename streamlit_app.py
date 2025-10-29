"""
Streamlit Web Interface for LLM Export Tools

A modern, user-friendly web interface that demonstrates the agentic AI workflow
for intelligent document export with LLM-powered formatting.
"""
import streamlit as st
from pathlib import Path
import os

from src.agent import run_export
from src.agent.nodes import analyzer_node, extract_formatting_node
from src.agent.state import ExportState
from src.utils.logger import logger


# Page config
st.set_page_config(
    page_title="LLM Export Tools",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'  # Stages: input, review, complete
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'final_result' not in st.session_state:
    st.session_state.final_result = None

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main container background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1E88E5 0%, #9C27B0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Card styling for sections */
    .stExpander {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(30, 136, 229, 0.2) !important;
        backdrop-filter: blur(10px);
    }
    
    .stExpander > div > div {
        background: white !important;
    }
    
    /* Force dark text in expanders */
    .stExpander p, .stExpander li, .stExpander span, .stExpander div {
        color: #1a1a1a !important;
    }
    
    .stExpander strong {
        color: #000 !important;
    }
    
    /* Expander header */
    .stExpander summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
    }
    
    .stExpander[open] summary {
        border-radius: 12px 12px 0 0 !important;
    }
    
    /* Button enhancements */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.1);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
    }
    
    [data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    /* Success/Info boxes */
    .stSuccess, .stInfo {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Stage indicator badges */
    .stage-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 10px 0;
    }
    
    .stage-input {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stage-review {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .stage-complete {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Section headers */
    h3 {
        color: #1E88E5;
        font-weight: 700;
        border-bottom: 3px solid #1E88E5;
        padding-bottom: 8px;
        margin-top: 20px;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1E88E5, transparent);
    }
    
    /* Download button special styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 LLM Export Tools</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Document Export with Agentic AI</div>', unsafe_allow_html=True)

# Info box
with st.expander("ℹ️ How It Works"):
    st.markdown("""
    This tool uses **LangGraph StateGraph** and **agentic AI** to:
    
    1. 🤖 **Analyze** your content and instructions using an LLM
    2. 🎨 **Extract** formatting preferences intelligently
    3. 👀 **Review** - You can see and adjust what the agent understood
    4. 📊 **Route** to the appropriate export tool (Word or PDF)
    5. ✨ **Apply** dynamic formatting based on your request
    6. 📥 **Generate** a professionally formatted document
    
    **Example prompts:**
    - "Export as Word with Arial 14pt font, bold text, and centered title"
    - "Create a PDF with 12pt Times New Roman, italics, and 1-inch margins"
    - "Make a Word doc with large headings and professional formatting"
    """)

st.markdown("---")

# ============================================================================
# STAGE 1: INPUT
# ============================================================================
if st.session_state.stage == 'input':
    st.markdown('<div class="stage-badge stage-input">📝 Stage 1: Input Content</div>', unsafe_allow_html=True)
    st.markdown("")  # Spacing
    # Text input area
    content = st.text_area(
        "📝 Enter your content:",
        height=200,
        placeholder="Paste or type the text you want to export...",
        help="The content you want to convert to a document"
    )
    
    # Prompt input
    prompt = st.text_input(
        "💬 Export prompt:",
        placeholder="e.g., 'Export as Word with bold 14pt Arial font and centered title'",
        help="Tell the AI how you want your document formatted"
    )
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze & Extract", type="primary", use_container_width=True)
    
    if analyze_button:
        if not content.strip():
            st.error("❌ Please enter some content to export")
        elif not prompt.strip():
            st.error("❌ Please provide an export prompt")
        else:
            # Run analysis and extraction
            with st.spinner("🤖 Agent is analyzing your request..."):
                try:
                    # Create initial state
                    state: ExportState = {
                        "text": content,
                        "prompt": prompt,
                        "format": "",
                        "formatting": {},
                        "file_path": ""
                    }
                    
                    # Step 1: Analyze
                    st.write("🔍 **Step 1:** Analyzing format from prompt...")
                    state = analyzer_node(state)
                    
                    # Step 2: Extract formatting
                    st.write("🎨 **Step 2:** Extracting formatting preferences...")
                    state = extract_formatting_node(state)
                    
                    # Store in session
                    st.session_state.extracted_data = {
                        "content": content,
                        "prompt": prompt,
                        "format": state["format"],
                        "formatting": state["formatting"]
                    }
                    st.session_state.stage = 'review'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    logger.error(f"Streamlit analysis error: {e}", exc_info=True)

# ============================================================================
# STAGE 2: REVIEW & ADJUST
# ============================================================================
elif st.session_state.stage == 'review':
    st.markdown('<div class="stage-badge stage-review">👀 Stage 2: Review & Adjust</div>', unsafe_allow_html=True)
    st.markdown("")  # Spacing
    st.success("✅ Agent analysis complete! Review the extracted preferences:")
    
    data = st.session_state.extracted_data
    
    # Display extracted format
    st.markdown("### 📊 Extracted Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Detected Format", data["format"].upper())
    with col2:
        st.metric("Formatting Options", len([v for v in data["formatting"].values() if v is not None]))
    
    # Show formatted extraction in an expandable box
    with st.expander("🎨 Formatting Preferences (click to expand)", expanded=True):
        if data["formatting"]:
            for key, value in data["formatting"].items():
                if value is not None:
                    st.text(f"• {key}: {value}")
        else:
            st.info("No specific formatting preferences extracted. Using defaults.")
    
    # Content preview
    with st.expander("📝 Content Preview"):
        preview_text = data["content"][:500] + ("..." if len(data["content"]) > 500 else "")
        st.text(preview_text)
    
    st.markdown("---")
    
    # Adjustment section
    st.markdown("### ⚙️ Adjust Settings (Optional)")
    
    # Allow format override
    new_format = st.selectbox(
        "Override format:",
        options=["Keep as detected", "word", "pdf"],
        index=0
    )
    
    # Allow formatting adjustments
    with st.expander("🔧 Adjust Formatting"):
        st.markdown("*Modify any extracted values below:*")
        
        adjusted_formatting = {}
        
        # Font settings
        col1, col2 = st.columns(2)
        with col1:
            font_name = st.text_input(
                "Font Name", 
                value=data["formatting"].get("name", ""),
                placeholder="e.g., Arial, Times New Roman"
            )
            if font_name:
                adjusted_formatting["name"] = font_name
            
            font_size = st.number_input(
                "Font Size (pt)", 
                min_value=8, 
                max_value=72,
                value=int(data["formatting"].get("size", 12)) if data["formatting"].get("size") else 12
            )
            adjusted_formatting["size"] = font_size
        
        with col2:
            bold = st.checkbox("Bold", value=data["formatting"].get("bold", False))
            adjusted_formatting["bold"] = bold
            
            italic = st.checkbox("Italic", value=data["formatting"].get("italic", False))
            adjusted_formatting["italic"] = italic
        
        # Title settings
        st.markdown("**Title Settings:**")
        col1, col2 = st.columns(2)
        with col1:
            title_size = st.number_input(
                "Title Font Size (pt)", 
                min_value=10, 
                max_value=72,
                value=int(data["formatting"].get("title_size", 16)) if data["formatting"].get("title_size") else 16
            )
            adjusted_formatting["title_size"] = title_size
        
        with col2:
            title_alignment = st.selectbox(
                "Title Alignment",
                options=["left", "center", "right", "justify"],
                index=["left", "center", "right", "justify"].index(data["formatting"].get("title_alignment", "center"))
            )
            adjusted_formatting["title_alignment"] = title_alignment
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.stage = 'input'
            st.session_state.extracted_data = None
            st.rerun()
    
    with col2:
        if st.button("🔍 Re-analyze", use_container_width=True):
            # Keep content/prompt but re-run extraction
            st.session_state.stage = 'input'
            st.rerun()
    
    with col3:
        # Apply adjustments to session data
        if st.button("💾 Apply Changes", use_container_width=True):
            if new_format != "Keep as detected":
                st.session_state.extracted_data["format"] = new_format
            st.session_state.extracted_data["formatting"] = adjusted_formatting
            st.success("✅ Changes applied!")
            st.rerun()
    
    with col4:
        if st.button("✅ Confirm & Export", type="primary", use_container_width=True):
            # Apply any pending adjustments
            if new_format != "Keep as detected":
                st.session_state.extracted_data["format"] = new_format
            st.session_state.extracted_data["formatting"] = adjusted_formatting
            
            # Run the export
            with st.spinner("🚀 Exporting document..."):
                try:
                    # Run full workflow with extracted data
                    result = run_export(
                        text=st.session_state.extracted_data["content"],
                        prompt=st.session_state.extracted_data["prompt"]
                    )
                    
                    st.session_state.final_result = result
                    st.session_state.stage = 'complete'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
                    logger.error(f"Streamlit export error: {e}", exc_info=True)

# ============================================================================
# STAGE 3: COMPLETE
# ============================================================================
elif st.session_state.stage == 'complete':
    st.markdown('<div class="stage-badge stage-complete">✅ Stage 3: Export Complete</div>', unsafe_allow_html=True)
    st.markdown("")  # Spacing
    
    result = st.session_state.final_result
    
    st.success("🎉 Document exported successfully!")
    
    # Display details
    st.markdown("### 📊 Export Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Format", result.get("format", "unknown").upper())
    with col2:
        file_size = Path(result["file_path"]).stat().st_size
        st.metric("File Size", f"{file_size:,} bytes")
    
    # Show formatting used
    if result.get("formatting"):
        with st.expander("🎨 Final Formatting Applied"):
            formatting = result["formatting"]
            for key, value in formatting.items():
                if value is not None:
                    st.text(f"• {key}: {value}")
    
    # Download button
    st.markdown("---")
    file_path = Path(result["file_path"])
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.download_button(
            label="📥 Download Document",
            data=file_bytes,
            file_name=file_path.name,
            mime="application/octet-stream",
            type="primary",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Export Another", use_container_width=True):
            st.session_state.stage = 'input'
            st.session_state.extracted_data = None
            st.session_state.final_result = None
            st.rerun()
    
    st.info(f"💡 File saved locally at: `{result['file_path']}`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Built with <strong>LangGraph</strong> • <strong>LangChain</strong> • <strong>Streamlit</strong></p>
    <p>Powered by Agentic AI 🤖</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # LLM provider info
    from config.settings import get_llm_config
    config = get_llm_config()
    
    st.info(f"""
    **LLM Provider:** {config['provider'].upper()}  
    **Model:** {config['model']}
    """)
    
    # Export directory
    from config.settings import get_export_dir
    export_dir = get_export_dir()
    st.text(f"Export Directory:\n{export_dir}")
    
    # Current stage indicator with emoji
    st.markdown("---")
    st.markdown("**🎯 Current Stage:**")
    stage_info = {
        'input': ("📝 Input Content", "🟣"),
        'review': ("👀 Review & Adjust", "🔴"),
        'complete': ("✅ Export Complete", "🔵")
    }
    current_stage = stage_info.get(st.session_state.stage, ("Unknown", "⚪"))
    st.info(f"{current_stage[0]} {current_stage[1]}")
    
    st.markdown("---")
    st.markdown("""
    ### 📚 Resources
    - [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
    - [LangChain Docs](https://python.langchain.com/)
    - [Streamlit Docs](https://docs.streamlit.io/)
    """)

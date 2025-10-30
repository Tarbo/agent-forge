"""
AgentForge - Agentic Document Creation

A ChatGPT-style interface powered by LangGraph agents where you can:
1. Chat with an LLM to generate content
2. Export any assistant message directly to Word/PDF with intelligent formatting
3. Continue the conversation after exporting

Built with agentic AI workflows for intelligent document transformation.
"""
import streamlit as st
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from src.agent.nodes import analyzer_node, content_cleaner_node, extract_formatting_node
from src.agent.state import ExportState
from src.agent import run_export
from config.settings import get_llm_config
from src.utils.logger import logger


# Page config
st.set_page_config(
    page_title="AgentForge - Agentic Document Creation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1E88E5 0%, #9C27B0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Ensure text in chat messages is dark and readable */
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span,
    .stChatMessage [data-testid="stMarkdownContainer"] {
        color: #1a1a1a !important;
    }
    
    /* User message background - light blue tint */
    [data-testid="stChatMessageContent"]:has([data-testid="stChatMessageUser"]) {
        background: rgba(232, 240, 254, 0.98) !important;
    }
    
    /* Assistant message background - white */
    [data-testid="stChatMessageContent"]:has([data-testid="stChatMessageAssistant"]) {
        background: rgba(255, 255, 255, 0.98) !important;
    }
    
    /* Export button styling */
    .export-button-container {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Download button special styling */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 0.95rem;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        border: none;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Info boxes */
    .stExpander {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Ensure text in expanders is readable */
    .stExpander .element-container p,
    .stExpander .element-container li,
    .stExpander .element-container strong,
    .stExpander .element-container {
        color: #1a1a1a !important;
    }
    
    .stExpander [data-testid="stMarkdownContainer"] {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'llm' not in st.session_state:
    # Initialize LLM for chat
    config = get_llm_config()
    if config["provider"] == "ollama":
        st.session_state.llm = ChatOllama(model=config["model"], base_url=config["base_url"])
    elif config["provider"] == "openai":
        st.session_state.llm = ChatOpenAI(model=config["model"])
    elif config["provider"] == "anthropic":
        st.session_state.llm = ChatAnthropic(model=config["model"])


# Header
st.markdown('<div class="main-header">🤖 AgentForge</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Agentic AI that transforms conversations into polished documents</div>', unsafe_allow_html=True)

# Info box
with st.expander("ℹ️ How to Use"):
    st.markdown("""
    **This is a ChatGPT-style interface with built-in export:**
    
    1. 💬 **Chat** with the AI to generate content (articles, proposals, reports, etc.)
    2. 📥 **Export** any assistant message by:
       - Clicking the "Export this response" button below any message
       - OR typing "export as Word/PDF" in the chat
    3. 🎨 The AI will automatically clean up meta-commentary and format your document
    4. ⬇️ Download your formatted document instantly
    5. 🔄 Continue chatting and exporting as needed!
    
    **Example workflow:**
    - You: "Write a project proposal for a mobile app"
    - AI: [Generates proposal + "Would you like me to add more details?"]
    - You: Click "Export this response" → Select format
    - AI: Removes "Would you like..." fluff → Creates clean Word/PDF
    - Download appears in chat!
    """)

st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add export button after assistant messages
            if message["role"] == "assistant":
                st.markdown('<div class="export-button-container">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    if st.button("📄 Export as Word", key=f"export_word_{idx}"):
                        # Export this message as Word
                        with st.spinner("🚀 Exporting to Word..."):
                            try:
                                # Clean content
                                temp_state: ExportState = {
                                    "text": message["content"],
                                    "prompt": "",
                                    "export_intent": True,
                                    "format": "word",
                                    "formatting": {},
                                    "file_path": ""
                                }
                                cleaned_state = content_cleaner_node(temp_state)
                                
                                # Run export workflow
                                result = run_export(
                                    text=cleaned_state["text"],
                                    prompt="Export as Word with clean formatting"
                                )
                                
                                # Show download button
                                file_path = Path(result["file_path"])
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download Word Document",
                                        data=f.read(),
                                        file_name=file_path.name,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        key=f"download_word_{idx}"
                                    )
                                st.success(f"✅ Exported to: `{file_path.name}`")
                                
                            except Exception as e:
                                st.error(f"❌ Export failed: {str(e)}")
                                logger.error(f"Export error: {e}", exc_info=True)
                
                with col2:
                    if st.button("📑 Export as PDF", key=f"export_pdf_{idx}"):
                        # Export this message as PDF
                        with st.spinner("🚀 Exporting to PDF..."):
                            try:
                                # Clean content
                                temp_state: ExportState = {
                                    "text": message["content"],
                                    "prompt": "",
                                    "export_intent": True,
                                    "format": "pdf",
                                    "formatting": {},
                                    "file_path": ""
                                }
                                cleaned_state = content_cleaner_node(temp_state)
                                
                                # Run export workflow
                                result = run_export(
                                    text=cleaned_state["text"],
                                    prompt="Export as PDF with clean formatting"
                                )
                                
                                # Show download button
                                file_path = Path(result["file_path"])
                                with open(file_path, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Download PDF Document",
                                        data=f.read(),
                                        file_name=file_path.name,
                                        mime="application/pdf",
                                        key=f"download_pdf_{idx}"
                                    )
                                st.success(f"✅ Exported to: `{file_path.name}`")
                                
                            except Exception as e:
                                st.error(f"❌ Export failed: {str(e)}")
                                logger.error(f"Export error: {e}", exc_info=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if this is an export request
    try:
        # Analyze for export intent
        analysis_state: ExportState = {
            "text": "",
            "prompt": prompt,
            "export_intent": False,
            "format": "word",
            "formatting": {},
            "file_path": ""
        }
        analyzed = analyzer_node(analysis_state)
        
        if analyzed["export_intent"]:
            # User wants to export the last assistant message
            if st.session_state.messages:
                # Find last assistant message
                last_assistant_msg = None
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "assistant":
                        last_assistant_msg = msg["content"]
                        break
                
                if last_assistant_msg:
                    with st.chat_message("assistant"):
                        with st.spinner(f"🚀 Exporting to {analyzed['format'].upper()}..."):
                            try:
                                # Clean content
                                clean_state: ExportState = {
                                    "text": last_assistant_msg,
                                    "prompt": prompt,
                                    "export_intent": True,
                                    "format": analyzed["format"],
                                    "formatting": {},
                                    "file_path": ""
                                }
                                cleaned_state = content_cleaner_node(clean_state)
                                
                                # Run export workflow
                                result = run_export(
                                    text=cleaned_state["text"],
                                    prompt=prompt
                                )
                                
                                # Show download button
                                file_path = Path(result["file_path"])
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if analyzed["format"] == "word" else "application/pdf"
                                
                                st.download_button(
                                    label=f"⬇️ Download {analyzed['format'].upper()} Document",
                                    data=file_bytes,
                                    file_name=file_path.name,
                                    mime=mime_type
                                )
                                
                                export_msg = f"✅ Exported to {analyzed['format'].upper()}: `{file_path.name}`"
                                st.success(export_msg)
                                
                                # Add to message history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": export_msg
                                })
                                
                            except Exception as e:
                                error_msg = f"❌ Export failed: {str(e)}"
                                st.error(error_msg)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": error_msg
                                })
                                logger.error(f"Export error: {e}", exc_info=True)
                else:
                    with st.chat_message("assistant"):
                        msg = "⚠️ No previous assistant message to export. Please generate some content first!"
                        st.warning(msg)
                        st.session_state.messages.append({"role": "assistant", "content": msg})
        
        else:
            # Regular chat - get LLM response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Convert message history to LangChain format
                    messages = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                    ]
                    
                    response = st.session_state.llm.invoke(messages)
                    assistant_message = response.content
                    
                    st.markdown(assistant_message)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                    # Force rerun to show export buttons
                    st.rerun()
    
    except Exception as e:
        with st.chat_message("assistant"):
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            logger.error(f"Chat error: {e}", exc_info=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # LLM provider info
    config = get_llm_config()
    st.info(f"""
    **LLM Provider:** {config['provider'].upper()}  
    **Model:** {config['model']}
    """)
    
    # Export directory
    from config.settings import get_export_dir
    export_dir = get_export_dir()
    st.text(f"Export Directory:\n{export_dir}")
    
    st.markdown("---")
    
    # Message count
    st.metric("Messages", len(st.session_state.messages))
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 💡 Tips
    - Generate content first by chatting
    - Click export buttons to save responses
    - OR type "export as Word/PDF" in chat
    - Meta-commentary is auto-removed from exports
    
    ### 📚 Resources
    - [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
    - [LangChain Docs](https://python.langchain.com/)
    - [Streamlit Docs](https://docs.streamlit.io/)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Built with <strong>LangGraph</strong> • <strong>LangChain</strong> • <strong>Streamlit</strong></p>
    <p>Powered by Agentic AI 🤖 | Created by <a href="https://github.com/Tarbo" target="_blank" style="color: #667eea; text-decoration: none;">@Tarbo</a></p>
</div>
""", unsafe_allow_html=True)

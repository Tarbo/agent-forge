"""
LangGraph nodes for the export workflow.

Each node processes the state and returns an updated state.
"""
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama

from src.agent.state import ExportState
from src.agent.data_models import FormattingPreferences, ExportIntentAnalysis
from config.settings import get_llm_config
from src.utils.logger import logger
from src.tools.word_tool import export_to_word
from src.tools.pdf_tool import export_to_pdf
from src.utils.file_manager import open_file


def get_llm():
    """Get configured LLM instance based on settings."""
    config = get_llm_config()
    
    if config["provider"] == "ollama":
        return ChatOllama(
            model=config["model"],
            base_url=config["base_url"]
        )
    elif config["provider"] == "openai":
        return ChatOpenAI(model=config["model"])
    elif config["provider"] == "anthropic":
        return ChatAnthropic(model=config["model"])
    else:
        raise ValueError(f"Unsupported LLM provider: {config['provider']}")


def extract_formatting_node(state: ExportState) -> ExportState:
    """
    Extract formatting preferences from user prompt using structured output.
    
    Leverages the detected format (from analyzer_node) to guide extraction
    toward format-specific properties (Word vs PDF).
    
    Args:
        state: Current state with user prompt and detected format
        
    Returns:
        Updated state with formatting preferences
    """
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(FormattingPreferences)
        
        detected_format = state.get("format", "word")
        
        # Tailor extraction based on detected format
        if detected_format == "word":
            format_specific_guidance = """
            This is for a Word document (.docx). Focus on:
            - name: Font name (Arial, Calibri, Times New Roman, etc.)
            - size: Font size in points
            - bold, italic, underline: Text styling
            - title_alignment: Title alignment (left, center, right)
            """
        else:  # pdf
            format_specific_guidance = """
            This is for a PDF document. Focus on:
            - fontName: PDF font name (Helvetica, Times-Roman, Courier, etc.)
            - fontSize: Font size in points
            - leftMargin, rightMargin, topMargin, bottomMargin: Page margins in points (72 = 1 inch)
            - title_alignment: Title alignment (left, center, right)
            """
        
        prompt = f"""
        Extract formatting preferences for a {detected_format.upper()} export from:
        "{state['prompt']}"
        
        {format_specific_guidance}
        
        Only include properties that are explicitly mentioned.
        Return null for properties not specified.
        """
        
        formatting_prefs = structured_llm.invoke(prompt)
        
        # Convert Pydantic model to dict, removing None values
        formatting_dict = {
            k: v for k, v in formatting_prefs.model_dump().items() 
            if v is not None
        }
        
        logger.info(f"Extracted {detected_format} formatting: {formatting_dict}")
        
        return {**state, "formatting": formatting_dict}
        
    except Exception as e:
        logger.warning(f"Failed to extract formatting: {e}. Using defaults.")
        return {**state, "formatting": {}}


def analyzer_node(state: ExportState) -> ExportState:
    """
    Analyze user message to detect export intent and desired format.
    
    Uses LLM with structured output to detect:
    1. Whether user wants to export (export_intent)
    2. What format they want (word or pdf)
    
    Args:
        state: Current state with user prompt
        
    Returns:
        Updated state with export_intent and format
    """
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ExportIntentAnalysis)
        
        prompt = f"""
        Analyze this user message to determine if they want to export content:
        "{state['prompt']}"
        
        Detect export intent by looking for keywords like:
        - "export", "save", "download", "convert", "create document"
        - "make a Word doc", "generate PDF", "save as..."
        
        If they want to export, determine the format:
        - word: for .docx, Word document, Word file, doc
        - pdf: for .pdf, PDF document, PDF file
        
        If format is not specified, default to "word".
        
        Return:
        - export_intent: true if they want to export, false otherwise
        - format: "word" or "pdf"
        - reasoning: brief explanation of your decision
        """
        
        analysis = structured_llm.invoke(prompt)
        
        # Validate format
        detected_format = analysis.format.strip().lower()
        if detected_format not in ["word", "pdf"]:
            logger.warning(f"Invalid format detected: {detected_format}. Defaulting to word.")
            detected_format = "word"
        
        logger.info(f"Export intent: {analysis.export_intent}, Format: {detected_format}")
        logger.info(f"Reasoning: {analysis.reasoning}")
        
        return {
            **state, 
            "export_intent": analysis.export_intent,
            "format": detected_format
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze export intent: {e}. Defaulting to no export.")
        return {
            **state, 
            "export_intent": False,
            "format": "word"
        }


def content_cleaner_node(state: ExportState) -> ExportState:
    """
    Clean content by removing LLM meta-commentary.
    
    Removes phrases like:
    - "Would you like me to..."
    - "Do you want..."
    - "Should I revise..."
    - "Let me know if..."
    - Other follow-up questions or meta-commentary
    
    Args:
        state: Current state with text content
        
    Returns:
        Updated state with cleaned text
    """
    try:
        llm = get_llm()
        
        prompt = f"""
        Clean this text by removing ALL meta-commentary, follow-up questions, and conversational fluff.
        
        REMOVE phrases like:
        - "Would you like me to..."
        - "Do you want..."
        - "Should I..."
        - "Let me know if..."
        - "Feel free to ask..."
        - "Is there anything else..."
        - Any questions asking for user feedback or next steps
        - Any conversational filler or pleasantries
        
        KEEP only:
        - The actual content (article, proposal, document, etc.)
        - Substantive information
        - Core message
        
        Original text:
        \"\"\"
        {state['text']}
        \"\"\"
        
        Return ONLY the cleaned content, nothing else. Do not add any commentary or explanation.
        """
        
        response = llm.invoke(prompt)
        cleaned_text = response.content.strip()
        
        logger.info(f"Content cleaned. Original length: {len(state['text'])}, Cleaned length: {len(cleaned_text)}")
        
        return {**state, "text": cleaned_text}
        
    except Exception as e:
        logger.warning(f"Failed to clean content: {e}. Using original text.")
        return state


def word_node(state: ExportState) -> ExportState:
    """
    Execute Word document export.
    
    Calls the Word export tool with text and formatting preferences.
    
    Args:
        state: Current state with text and formatting
        
    Returns:
        Updated state with file_path
    """
    try:
        logger.info("Executing Word export...")
        
        # Get formatting from state
        formatting = state.get("formatting", {})
        
        # Call Word export tool using invoke (required for LangChain tools)
        tool_input = {
            "text": state["text"],
            "formatting": formatting
        }
        file_path = export_to_word.invoke(tool_input)
        
        logger.info(f"Word export complete: {file_path}")
        
        return {**state, "file_path": file_path}
        
    except Exception as e:
        error_msg = f"Word export failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def pdf_node(state: ExportState) -> ExportState:
    """
    Execute PDF document export.
    
    Calls the PDF export tool with text and formatting preferences.
    
    Args:
        state: Current state with text and formatting
        
    Returns:
        Updated state with file_path
    """
    try:
        logger.info("Executing PDF export...")
        
        # Get formatting from state
        formatting = state.get("formatting", {})
        
        # Call PDF export tool using invoke (required for LangChain tools)
        tool_input = {
            "text": state["text"],
            "formatting": formatting
        }
        file_path = export_to_pdf.invoke(tool_input)
        
        logger.info(f"PDF export complete: {file_path}")
        
        return {**state, "file_path": file_path}
        
    except Exception as e:
        error_msg = f"PDF export failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def notification_node(state: ExportState) -> ExportState:
    """
    Final node - opens file and logs success.
    
    Args:
        state: Current state with file_path
        
    Returns:
        Final state
    """
    try:
        from config.settings import get_auto_open_file
        file_path = Path(state["file_path"])
        
        logger.info(f"✅ Export complete: {file_path}")
        logger.info(f"   Format: {state['format']}")
        logger.info(f"   Formatting applied: {state.get('formatting', {})}")
        
        # Only auto-open if enabled (disabled by default for better UX)
        if get_auto_open_file():
            if open_file(file_path):
                logger.info("File opened successfully")
        else:
            logger.info("File ready. Set AUTO_OPEN_FILE=true in .env to auto-open.")
        
        return state
        
    except Exception as e:
        logger.warning(f"File opening failed: {e}")
        return state


# Router function for conditional edges
def route_to_tool(state: ExportState) -> str:
    """
    Route to the appropriate export tool based on detected format.
    
    This is used by the StateGraph conditional edge.
    
    Args:
        state: Current state with format field
        
    Returns:
        str: Node name to route to ("word_tool" or "pdf_tool")
    """
    format_type = state.get("format", "word")
    
    if format_type == "pdf":
        logger.info("Routing to PDF tool")
        return "pdf_tool"
    else:
        logger.info("Routing to Word tool")
        return "word_tool"


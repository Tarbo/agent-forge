"""
LangGraph nodes for the export workflow.

Each node processes the state and returns an updated state.
"""
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from src.agent.state import ExportState
from src.agent.data_models import FormattingPreferences
from config.settings import get_llm_config
from src.utils.logger import logger
from src.tools.word_tool import export_to_word
from src.tools.pdf_tool import export_to_pdf
from src.utils.file_manager import open_file


def get_llm():
    """Get configured LLM instance based on settings."""
    config = get_llm_config()
    
    if config["provider"] == "openai":
        return ChatOpenAI(model=config["model"])
    elif config["provider"] == "anthropic":
        return ChatAnthropic(model=config["model"])
    else:
        raise ValueError(f"Unsupported LLM provider: {config['provider']}")


def extract_formatting_node(state: ExportState) -> ExportState:
    """
    Extract formatting preferences from user prompt using structured output.
    
    Uses LLM with structured output to parse formatting details from natural language.
    
    Args:
        state: Current state with user prompt
        
    Returns:
        Updated state with formatting preferences
    """
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(FormattingPreferences)
        
        prompt = f"""
        Extract ALL formatting preferences mentioned in this user request:
        "{state['prompt']}"
        
        Look for:
        - Font names (Arial, Calibri, Times New Roman, Helvetica, etc.)
        - Font sizes (10pt, 12pt, 14pt, etc.)
        - Text styling (bold, italic, underline)
        - Title alignment (centered, left-aligned, right-aligned)
        - Margins (wide margins, narrow margins, specific measurements)
        
        Only include properties that are explicitly mentioned.
        Return null for properties not specified.
        """
        
        formatting_prefs = structured_llm.invoke(prompt)
        
        # Convert Pydantic model to dict, removing None values
        formatting_dict = {
            k: v for k, v in formatting_prefs.items() 
            if v is not None
        }
        
        logger.info(f"Extracted formatting: {formatting_dict}")
        
        return {**state, "formatting": formatting_dict}
        
    except Exception as e:
        logger.warning(f"Failed to extract formatting: {e}. Using defaults.")
        return {**state, "formatting": {}}


def analyzer_node(state: ExportState) -> ExportState:
    """
    Analyze user prompt to determine desired export format.
    
    Uses LLM to detect if user wants Word or PDF export.
    
    Args:
        state: Current state with user prompt
        
    Returns:
        Updated state with detected format
    """
    try:
        llm = get_llm()
        
        prompt = f"""
        Analyze this user request and determine the export format they want:
        "{state['prompt']}"
        
        Choose ONE of these formats:
        - word (for .docx, Word document, Word file, doc)
        - pdf (for .pdf, PDF document, PDF file)
        
        Respond with ONLY the format name (word or pdf), nothing else.
        """
        
        response = llm.invoke(prompt)
        detected_format = response.content.strip().lower()
        
        # Validate format
        if detected_format not in ["word", "pdf"]:
            logger.warning(f"Invalid format detected: {detected_format}. Defaulting to word.")
            detected_format = "word"
        
        logger.info(f"Detected format: {detected_format}")
        
        return {**state, "format": detected_format}
        
    except Exception as e:
        logger.error(f"Failed to detect format: {e}. Defaulting to word.")
        return {**state, "format": "word"}


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
        
        # Call Word export tool
        file_path = export_to_word(
            text=state["text"],
            custom_name=None,
            **formatting
        )
        
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
        
        # Call PDF export tool
        file_path = export_to_pdf(
            text=state["text"],
            custom_name=None,
            **formatting
        )
        
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
        file_path = Path(state["file_path"])
        
        logger.info(f"✅ Export complete: {file_path}")
        logger.info(f"   Format: {state['format']}")
        logger.info(f"   Formatting applied: {state.get('formatting', {})}")
        
        # Try to open the file
        if open_file(file_path):
            logger.info("File opened successfully")
        
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


"""
Clipboard management utilities.

Handles getting text from the system clipboard using pyperclip.
"""
import pyperclip
from src.utils.logger import logger


def get_clipboard_text() -> str:
    """
    Get text from the system clipboard.
    
    Returns:
        str: Text content from clipboard, or empty string if clipboard is empty/invalid
        
    Example:
        text = get_clipboard_text()
        if text:
            print(f"Clipboard contains: {text[:50]}...")
    """
    try:
        text = pyperclip.paste()
        
        if not text or not isinstance(text, str):
            logger.warning("Clipboard is empty or contains non-text data")
            return ""
        
        logger.debug(f"Retrieved {len(text)} characters from clipboard")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Failed to access clipboard: {e}")
        return ""


def set_clipboard_text(text: str) -> bool:
    """
    Set text to the system clipboard.
    
    Args:
        text: Text to copy to clipboard
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        success = set_clipboard_text("Hello, world!")
    """
    try:
        pyperclip.copy(text)
        logger.debug(f"Copied {len(text)} characters to clipboard")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set clipboard: {e}")
        return False


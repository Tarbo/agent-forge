"""
Application settings and configuration
Loads environment variables and provides configuration values to the app
"""
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Ensure exports directory exists
EXPORTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

def get_export_directory() -> Path:
    """
    Get the export directory path from environment or use default.
    
    Returns:
        Path: Directory where exported files will be saved
    """
    custom_dir = os.getenv("EXPORT_DIRECTORY")
    
    if custom_dir:
        # Expand ~ and environment variables
        expanded_path = Path(os.path.expandvars(os.path.expanduser(custom_dir)))
        expanded_path.mkdir(parents=True, exist_ok=True)
        return expanded_path
    
    return EXPORTS_DIR


def get_hotkey() -> str:
    """Get hotkey based on OS
    Returns:
        str: Hotkey string in pynput format (e.g., '<ctrl>+<alt>+e')
    """
    default = os.getenv("HOTKEY")
    
    if default:
        return default
    
    # Auto-detect based on OS
    import platform
    if platform.system() == "Darwin":  # macOS
        return "<cmd>+<option>+e"  # ⌘⇧E
    else:  # Windows/Linux
        return "<ctrl>+<alt>+e"

# ============================================================================
# LLM CONFIGURATION
# ============================================================================

def get_llm_config() -> dict:
    """
    Auto-detect and return LLM configuration based on available settings.
    
    Priority order:
    1. Ollama (if USE_OLLAMA=true)
    2. OpenAI (if OPENAI_API_KEY exists)
    3. Anthropic (if ANTHROPIC_API_KEY exists)
    
    Returns:
        dict: {
            "provider": "ollama" | "openai" | "anthropic",
            "model": str,
            "base_url": str (optional, for Ollama)
        }
    
    Raises:
        ValueError: If no LLM provider is configured
    """
    # Check for Ollama (local LLM)
    if os.getenv("USE_OLLAMA", "false").lower() == "true":
        return {
            "provider": "ollama",
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }
    
    # Check for OpenAI
    if os.getenv("OPENAI_API_KEY"):
        return {
            "provider": "openai",
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        }
    
    # Check for Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        return {
            "provider": "anthropic",
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        }
    
    # No provider configured
    raise ValueError(
        "No LLM provider configured! Please set one of:\n"
        "  - USE_OLLAMA=true (with OLLAMA_MODEL and OLLAMA_BASE_URL)\n"
        "  - OPENAI_API_KEY\n"
        "  - ANTHROPIC_API_KEY"
    )
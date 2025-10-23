"""
File management utilities for saving and organizing export files.

Handles filename generation, path management, and file operations.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import get_export_directory
from src.utils.logger import logger


def generate_filename(format_type: str, custom_name: Optional[str] = None) -> str:
    """
    Generate a unique filename with timestamp.
    
    Args:
        format_type: Export format (word, pdf, excel, csv, json)
        custom_name: Optional custom filename (without extension)
    
    Returns:
        str: Filename with timestamp and appropriate extension
        
    Examples:
        generate_filename("word") -> "export_2024-10-23_14-30-22.docx"
        generate_filename("pdf", "report") -> "report_2024-10-23_14-30-22.pdf"
    """
    # Map format to file extension
    extensions = {
        "word": ".docx",
        "pdf": ".pdf",
        "excel": ".xlsx",
        "csv": ".csv",
        "json": ".json"
    }
    
    extension = extensions.get(format_type.lower(), ".txt")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if custom_name:
        # Remove any existing extension from custom name
        base_name = Path(custom_name).stem
        filename = f"{base_name}_{timestamp}{extension}"
    else:
        filename = f"export_{timestamp}{extension}"
    
    return filename


def get_full_path(format_type: str, custom_name: Optional[str] = None) -> Path:
    """
    Generate full file path for export file.
    
    Args:
        format_type: Export format (word, pdf, excel, csv, json)
        custom_name: Optional custom filename (without extension)
    
    Returns:
        Path: Full path to the export file
        
    Example:
        get_full_path("word") -> Path("/path/to/exports/export_2024-10-23_14-30-22.docx")
    """
    export_dir = get_export_directory()
    filename = generate_filename(format_type, custom_name)
    full_path = export_dir / filename
    
    logger.debug(f"Generated file path: {full_path}")
    
    return full_path


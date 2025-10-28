"""
State schema definition for the LangGraph StateGraph.

This defines the shape of data that flows through the graph nodes.
"""
from typing import TypedDict


class ExportState(TypedDict):
    """
    State schema for the export workflow.
    
    Attributes:
        text: The text content to be exported (from clipboard)
        prompt: User's natural language prompt describing desired export format
        format: Detected export format (word, pdf)
        formatting: Dict of formatting preferences extracted from prompt
        file_path: Full path to the generated export file
    """
    text: str
    prompt: str
    format: str
    formatting: dict
    file_path: str


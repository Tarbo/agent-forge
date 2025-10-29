"""
Pydantic models for the export workflow.

Data schemas used for structured LLM outputs and validation.
"""
from typing import Optional
from pydantic import BaseModel, Field


class ExportIntentAnalysis(BaseModel):
    """
    Structured format for detecting export intent from user message.
    
    Used by analyzer_node to determine if user wants to export
    and what format they want.
    """
    export_intent: bool = Field(
        description="True if user wants to export/save/download content, False otherwise"
    )
    format: str = Field(
        description="Export format: 'word' for Word/docx, 'pdf' for PDF. Default to 'word' if not specified."
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of why export intent was detected or not"
    )


class FormattingPreferences(BaseModel):
    """
    Structured format for LLM-extracted formatting preferences.
    
    This model is used with `with_structured_output()` to ensure
    the LLM returns properly formatted, validated data.
    """
    # Font properties (Word)
    name: Optional[str] = Field(
        None, 
        description="Font name for Word documents (e.g., Arial, Calibri, Times New Roman)"
    )
    size: Optional[int] = Field(
        None, 
        description="Font size in points for Word documents"
    )
    bold: Optional[bool] = Field(
        None, 
        description="Apply bold formatting"
    )
    italic: Optional[bool] = Field(
        None, 
        description="Apply italic formatting"
    )
    underline: Optional[bool] = Field(
        None, 
        description="Apply underline formatting"
    )
    
    # Font properties (PDF)
    fontName: Optional[str] = Field(
        None, 
        description="Font name for PDF documents (e.g., Helvetica, Times-Roman, Courier)"
    )
    fontSize: Optional[int] = Field(
        None, 
        description="Font size in points for PDF documents"
    )
    
    # Title properties
    title_alignment: Optional[str] = Field(
        None, 
        description="Title alignment: left, center, right, or justify"
    )
    title_fontSize: Optional[int] = Field(
        None, 
        description="Title font size in points"
    )
    
    # Page properties (PDF)
    leftMargin: Optional[int] = Field(
        None, 
        description="Left margin in points (72 points = 1 inch)"
    )
    rightMargin: Optional[int] = Field(
        None, 
        description="Right margin in points"
    )
    topMargin: Optional[int] = Field(
        None, 
        description="Top margin in points"
    )
    bottomMargin: Optional[int] = Field(
        None, 
        description="Bottom margin in points"
    )


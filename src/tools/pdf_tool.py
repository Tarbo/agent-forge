"""
PDF export tool.

Uses reportlab to create formatted PDF files with dynamic formatting support.
"""
from pathlib import Path
from langchain_core.tools import tool
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

from src.utils.file_manager import get_full_path
from src.utils.logger import logger


# Property registry - easily extensible as reportlab adds more features
FONT_PROPERTIES = {
    "fontName": str,        # Font name (e.g., "Helvetica", "Times-Roman")
    "fontSize": int,        # Font size in points
    "textColor": str,       # Text color (hex or name)
}

PARAGRAPH_PROPERTIES = {
    "alignment": int,       # Alignment (TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY)
    "spaceAfter": int,      # Space after paragraph in points
    "spaceBefore": int,     # Space before paragraph in points
}

TITLE_PROPERTIES = {
    "alignment": int,       # Title alignment
    "fontSize": int,        # Title font size
}

PAGE_PROPERTIES = {
    "rightMargin": int,     # Right margin in points (72 = 1 inch)
    "leftMargin": int,      # Left margin in points
    "topMargin": int,       # Top margin in points
    "bottomMargin": int,    # Bottom margin in points
}

# Default formatting values
DEFAULT_FORMATTING = {
    "fontName": "Helvetica",
    "fontSize": 12,
}

DEFAULT_TITLE_FORMATTING = {
    "alignment": TA_LEFT,
    "fontSize": 18,
}

DEFAULT_PAGE_FORMATTING = {
    "rightMargin": 72,      # 1 inch
    "leftMargin": 72,       # 1 inch
    "topMargin": 72,        # 1 inch
    "bottomMargin": 18,     # 0.25 inch
}


@tool
def export_to_pdf(text: str, custom_name: str = None, **formatting) -> str:
    """
    Export text content as a PDF document.
    
    This tool creates a formatted PDF document with the provided text.
    Accepts any formatting options via kwargs - unsupported options are gracefully ignored.
    
    Args:
        text: The text content to export to PDF
        custom_name: Optional custom filename (without extension)
        **formatting: Dynamic formatting options (see property registries)
    
    Supported formatting (extensible via registries):
        Font: fontName, fontSize, textColor
        Paragraph: alignment, spaceAfter, spaceBefore
        Title: title_alignment, title_fontSize (prefix with 'title_' for title-specific props)
        Page: rightMargin, leftMargin, topMargin, bottomMargin (in points, 72 = 1 inch)
    
    Returns:
        str: Full path to the created PDF document
        
    Example:
        export_to_pdf("My Title\\n\\nContent here", "my_report", 
                      fontName="Times-Roman", fontSize=11,
                      title_alignment=TA_CENTER,
                      leftMargin=100, rightMargin=100)
        # Returns: "/path/to/exports/my_report_2024-10-23_14-30-22.pdf"
    """
    try:
        # Generate file path
        file_path = get_full_path("pdf", custom_name)
        
        # Merge user formatting with defaults
        format_opts = {**DEFAULT_FORMATTING, **formatting}
        page_opts = {**DEFAULT_PAGE_FORMATTING, **{k: v for k, v in formatting.items() if k in PAGE_PROPERTIES}}
        
        # Create PDF document with dynamic margins
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            **page_opts
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get default styles
        styles = getSampleStyleSheet()
        
        # Parse text into title and content
        lines = text.strip().split('\n')
        if lines:
            title_text = lines[0]
            remaining_text = '\n\n'.join(lines[1:]) if len(lines) > 1 else ""
        else:
            title_text = ""
            remaining_text = text
        
        # Create and apply title style dynamically
        if title_text:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                **{**DEFAULT_TITLE_FORMATTING, **{k.replace("title_", ""): v for k, v in format_opts.items() if k.startswith("title_")}}
            )
            
            title_para = Paragraph(title_text, title_style)
            elements.append(title_para)
            elements.append(Spacer(1, 12))
        
        # Create custom paragraph style dynamically
        para_style_attrs = {**format_opts}
        # Remove title-specific props
        para_style_attrs = {k: v for k, v in para_style_attrs.items() if not k.startswith("title_")}
        
        para_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            **para_style_attrs
        )
        
        # Add content paragraphs
        if remaining_text.strip():
            paragraphs = remaining_text.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    para = Paragraph(para_text.strip().replace('\n', '<br/>'), para_style)
                    elements.append(para)
                    elements.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"PDF document created: {file_path}")
        return str(file_path)
        
    except Exception as e:
        error_msg = f"Failed to create PDF document: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


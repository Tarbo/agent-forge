"""
Test suite for the LLM Export Tools workflow.

Run individual tests:
    pytest tests/test_workflow.py::test_word_export -v

Run all tests:
    pytest tests/test_workflow.py -v

Run with coverage:
    pytest tests/test_workflow.py --cov=src --cov-report=html --cov-report=term
"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv, find_dotenv 
from src.agent import run_export
from src.utils.logger import logger

# Load environment variables
load_dotenv(find_dotenv())


@pytest.fixture(scope="session", autouse=True)
def check_api_key():
    """Verify API key is configured before running tests."""
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")


@pytest.fixture
def sample_text():
    """Sample text for testing exports."""
    return """Test Document Title
    
This is the introduction paragraph with some important content that needs to be exported.

This is the second paragraph with more details about the project and its outcomes.

Finally, this is the conclusion paragraph summarizing everything."""


@pytest.fixture
def minimal_text():
    """Minimal text for basic testing."""
    return """Quick Note
    
Just a simple export test with default formatting."""


class TestWordExport:
    """Test suite for Word document exports."""
    
    def test_word_export_with_formatting(self, sample_text):
        """Test Word export with explicit formatting preferences."""
        prompt = "Export this as a Word document with Arial 14pt font, bold text, and centered title"
        
        result = run_export(text=sample_text, prompt=prompt)
        
        # Verify result structure
        assert "file_path" in result
        assert "format" in result
        assert "formatting" in result
        
        # Verify format detection
        assert result["format"] == "word"
        
        # Verify file was created
        file_path = Path(result["file_path"])
        assert file_path.exists()
        assert file_path.suffix == ".docx"
        
        logger.info(f"✅ Word export created: {result['file_path']}")
        logger.info(f"   Formatting: {result['formatting']}")
    
    def test_word_export_minimal_prompt(self, minimal_text):
        """Test Word export with minimal prompt (no formatting details)."""
        prompt = "Export as Word"
        
        result = run_export(text=minimal_text, prompt=prompt)
        
        # Verify basic structure
        assert result["format"] == "word"
        assert Path(result["file_path"]).exists()
        
        logger.info(f"✅ Minimal Word export created: {result['file_path']}")
    
    def test_word_export_various_fonts(self, sample_text):
        """Test Word export with different font preferences."""
        prompt = "Export to Word with Calibri font and italic text"
        
        result = run_export(text=sample_text, prompt=prompt)
        
        assert result["format"] == "word"
        assert Path(result["file_path"]).exists()
        
        # Check if formatting was extracted
        formatting = result.get("formatting", {})
        logger.info(f"✅ Word with fonts created. Formatting: {formatting}")


class TestPDFExport:
    """Test suite for PDF document exports."""
    
    def test_pdf_export_with_formatting(self, sample_text):
        """Test PDF export with explicit formatting preferences."""
        prompt = "Convert to PDF with Times-Roman font, 12pt size, and 1-inch margins"
        
        result = run_export(text=sample_text, prompt=prompt)
        
        # Verify result structure
        assert "file_path" in result
        assert "format" in result
        assert "formatting" in result
        
        # Verify format detection
        assert result["format"] == "pdf"
        
        # Verify file was created
        file_path = Path(result["file_path"])
        assert file_path.exists()
        assert file_path.suffix == ".pdf"
        
        logger.info(f"✅ PDF export created: {result['file_path']}")
        logger.info(f"   Formatting: {result['formatting']}")
    
    def test_pdf_export_minimal_prompt(self, minimal_text):
        """Test PDF export with minimal prompt."""
        prompt = "Make it a PDF"
        
        result = run_export(text=minimal_text, prompt=prompt)
        
        assert result["format"] == "pdf"
        assert Path(result["file_path"]).exists()
        
        logger.info(f"✅ Minimal PDF export created: {result['file_path']}")
    
    def test_pdf_export_with_margins(self, sample_text):
        """Test PDF export with custom margins."""
        prompt = "PDF with 72pt margins on all sides"
        
        result = run_export(text=sample_text, prompt=prompt)
        
        assert result["format"] == "pdf"
        assert Path(result["file_path"]).exists()
        
        formatting = result.get("formatting", {})
        logger.info(f"✅ PDF with margins created. Formatting: {formatting}")


class TestFormatDetection:
    """Test suite for format detection logic."""
    
    def test_explicit_word_request(self, minimal_text):
        """Test explicit Word format request."""
        result = run_export(text=minimal_text, prompt="Export as Word document")
        assert result["format"] == "word"
    
    def test_explicit_pdf_request(self, minimal_text):
        """Test explicit PDF format request."""
        result = run_export(text=minimal_text, prompt="Save as PDF")
        assert result["format"] == "pdf"
    
    def test_implicit_word_request(self, minimal_text):
        """Test implicit Word format through .docx mention."""
        result = run_export(text=minimal_text, prompt="Export to docx with bold text")
        assert result["format"] == "word"
    
    def test_implicit_pdf_request(self, minimal_text):
        """Test implicit PDF format through context."""
        result = run_export(text=minimal_text, prompt="Create a PDF document")
        assert result["format"] == "pdf"


class TestFormattingExtraction:
    """Test suite for formatting preference extraction."""
    
    def test_font_extraction(self, minimal_text):
        """Test font name and size extraction."""
        result = run_export(
            text=minimal_text,
            prompt="Export to Word with Arial 16pt font"
        )
        
        formatting = result.get("formatting", {})
        # LLM should extract font preferences
        assert formatting is not None
        logger.info(f"Extracted formatting: {formatting}")
    
    def test_style_extraction(self, minimal_text):
        """Test text style extraction (bold, italic, underline)."""
        result = run_export(
            text=minimal_text,
            prompt="Make it Word with bold and italic text"
        )
        
        formatting = result.get("formatting", {})
        assert formatting is not None
        logger.info(f"Extracted styles: {formatting}")
    
    def test_alignment_extraction(self, minimal_text):
        """Test alignment preference extraction."""
        result = run_export(
            text=minimal_text,
            prompt="Word document with a centered title"
        )
        
        formatting = result.get("formatting", {})
        assert formatting is not None
        logger.info(f"Extracted alignment: {formatting}")
    
    def test_no_formatting_specified(self, minimal_text):
        """Test handling when no formatting is specified."""
        result = run_export(text=minimal_text, prompt="Export as Word")
        
        # Should still work with defaults
        assert result["format"] == "word"
        assert Path(result["file_path"]).exists()


if __name__ == "__main__":
    # Allow running directly for quick manual testing
    pytest.main([__file__, "-v", "--cov=src", "--cov-report=term"])

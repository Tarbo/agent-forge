"""
LangGraph v1.0 StateGraph definition.

This module defines the complete export workflow using StateGraph:
- Nodes: Processing steps
- Edges: Connections between nodes
- Conditional Edges: Dynamic routing based on state
"""
from langgraph.graph import StateGraph, END

from src.agent.state import ExportState
from src.agent.nodes import (
    analyzer_node,
    extract_formatting_node,
    word_node,
    pdf_node,
    notification_node,
    route_to_tool
)
from src.utils.logger import logger


def create_export_graph() -> StateGraph:
    """
    Create and return the compiled export workflow StateGraph.
    
    Workflow:
        START
          ↓
        analyzer (detect format: word/pdf)
          ↓
        extract_formatting (extract styling from prompt)
          ↓
        router (conditional) → word_node OR pdf_node
          ↓
        notification (open file, log success)
          ↓
        END
    
    Returns:
        StateGraph: Compiled graph ready for execution
    """
    logger.info("Building export StateGraph...")
    
    # Initialize StateGraph with our state schema
    workflow = StateGraph(ExportState)
    
    # Add all nodes to the graph
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("extract_formatting", extract_formatting_node)
    workflow.add_node("word_tool", word_node)
    workflow.add_node("pdf_tool", pdf_node)
    workflow.add_node("notification", notification_node)
    
    # Set entry point - where the graph starts
    workflow.set_entry_point("analyzer")
    
    # Add fixed edges (always follow this path)
    workflow.add_edge("analyzer", "extract_formatting")
    
    # Add conditional edge (router decides: word or pdf)
    workflow.add_conditional_edges(
        "extract_formatting",
        route_to_tool,
        {
            "word_tool": "word_tool",
            "pdf_tool": "pdf_tool",
        }
    )
    
    # Both tools go to notification
    workflow.add_edge("word_tool", "notification")
    workflow.add_edge("pdf_tool", "notification")
    
    # Notification leads to END
    workflow.add_edge("notification", END)
    
    # Compile the graph
    logger.info("Compiling StateGraph...")
    compiled_graph = workflow.compile()
    
    logger.info("✅ StateGraph compiled successfully")
    return compiled_graph


# Create the graph instance (singleton pattern)
export_graph = create_export_graph()


def run_export(text: str, prompt: str) -> ExportState:
    """
    Execute the export workflow.
    
    Convenience function to run the graph with initial state.
    
    Args:
        text: Text content to export
        prompt: User's natural language prompt (e.g., "Export as Word with Arial")
    
    Returns:
        ExportState: Final state with file_path and results
        
    Example:
        result = run_export(
            text="My document content",
            prompt="Export as PDF with Times New Roman"
        )
        print(f"File created: {result['file_path']}")
    """
    logger.info(f"Starting export workflow: {prompt}")
    
    # Create initial state
    initial_state: ExportState = {
        "text": text,
        "prompt": prompt,
        "format": "",
        "formatting": {},
        "file_path": ""
    }
    
    # Execute the graph
    final_state = export_graph.invoke(initial_state)
    
    logger.info(f"Export workflow complete: {final_state['file_path']}")
    return final_state


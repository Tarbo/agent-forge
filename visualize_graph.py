"""
Visualize the StateGraph workflow.

Generates a PNG image of the export workflow graph.
Requires: graphviz (brew install graphviz)
"""
from src.agent import export_graph

def visualize():
    """Generate Mermaid visualization of the StateGraph"""
    print("🎨 Generating StateGraph visualization...")
    
    try:
        # Get the graph
        graph = export_graph.get_graph()
        
        # Generate Mermaid diagram (text format - no dependencies!)
        mermaid_code = graph.draw_mermaid()
        
        output_file = "graph_visualization.mmd"
        with open(output_file, "w") as f:
            f.write(mermaid_code)
        
        print(f"✅ Visualization saved: {output_file}")
        print("\nView it at: https://mermaid.live")
        print("Or open in VS Code with Mermaid extension")
        print("\nWorkflow:")
        print("  START → analyzer → extract_formatting → [word_tool OR pdf_tool] → notification → END")
        
        # Also print to console
        print("\n" + "="*60)
        print("Mermaid Code:")
        print("="*60)
        print(mermaid_code)
        
    except Exception as e:
        print(f"❌ Failed to generate visualization: {e}")


if __name__ == "__main__":
    visualize()


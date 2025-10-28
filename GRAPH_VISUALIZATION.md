# StateGraph Visualization

This is the export workflow StateGraph:

```mermaid
%%{init: {'flowchart': {'curve': 'linear'}}}%%
graph TD;
	__start__([<p>__start__</p>]):::first
	analyzer(analyzer)
	extract_formatting(extract_formatting)
	word_tool(word_tool)
	pdf_tool(pdf_tool)
	notification(notification)
	__end__([<p>__end__</p>]):::last
	__start__ --> analyzer;
	notification --> __end__;
	extract_formatting -.-> pdf_tool;
	extract_formatting -.-> word_tool;
	word_tool --> notification;
	analyzer --> extract_formatting;
	pdf_tool --> notification;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

## Workflow Description

1. **__start__** → Entry point
2. **analyzer** → Detects format (Word or PDF)
3. **extract_formatting** → Extracts styling preferences
4. **Router** → Conditional edge to Word or PDF tool
5. **word_tool** or **pdf_tool** → Generates document
6. **notification** → Opens file and logs success
7. **__end__** → Exit point


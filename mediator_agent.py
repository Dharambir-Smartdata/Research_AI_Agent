# mediator_agent.py
"""
Mediator Agent: Dynamically classifies and routes user queries to the appropriate specialized agent:
- document_agent: handles all operations, inspections, queries, and metadata regarding uploaded/active documents.
- main_agent: handles web research, search queries, general knowledge, and executive reports.
"""
import json
import re
from langchain_core.messages import SystemMessage, HumanMessage

MEDIATOR_SYSTEM_PROMPT = """You are an intelligent routing mediator for an AI assistant.
Your job is to classify the user's query and decide which specialized agent must handle it:

1. "document_agent":
   - The query relates to an uploaded document, PDF, Word file, text file, or the active document in session.
   - Includes document operations: compressing, merging, splitting, converting, editing, signing, removing/reverting pages.
   - Includes document questions & metadata: asking for file size, page count, word count, document summary, text inspection, structure, or any detail about the active/uploaded document.

2. "main_agent":
   - The query asks for internet research, broad web search, external knowledge, scientific/academic explanations, market reports, or saving a previous research report.
   - The query does NOT ask about or target the uploaded document.

Decision Rules:
- If an active document exists and the user asks a question about it (e.g., "what is the file size of compressed pdf", "how many pages", "summarize the document") -> choose "document_agent".
- If the user attaches a document or asks to modify/inspect a file -> choose "document_agent".
- If the user asks a general or web research topic -> choose "main_agent".

Respond STRICTLY with a JSON object:
{"agent": "document_agent" | "main_agent", "reason": "<brief justification>"}
"""


async def route_query(
    llm,
    prompt: str,
    active_document: str | None = None,
    attached_files: list[str] | None = None,
    has_last_report: bool = False,
) -> str:
    """Classifies user intent using the LLM mediator agent and returns 'document_agent' or 'main_agent'."""
    prompt_clean = (prompt or "").strip()
    if not prompt_clean:
        return "main_agent"

    # Fast check: If new files are explicitly attached, route to document agent
    if attached_files and any(f for f in attached_files):
        p_lower = prompt_clean.lower()
        if not (p_lower.startswith("research on") or p_lower.startswith("search for")):
            return "document_agent"

    context_lines = []
    if active_document:
        context_lines.append(f"Active Document: {active_document}")
    if attached_files:
        context_lines.append(f"Attached Files: {', '.join(attached_files)}")
    if has_last_report:
        context_lines.append("Previous Research Report is present.")

    context_str = "\n".join(context_lines) if context_lines else "None"

    messages = [
        SystemMessage(content=MEDIATOR_SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context_str}\n\nUser Request: {prompt_clean}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
        data = json.loads(clean_json)
        agent = data.get("agent", "").strip().lower()
        if "document" in agent:
            return "document_agent"
        return "main_agent"
    except Exception as e:
        print(f"[MEDIATOR] Fallback due to: {e}")
        # Safe fallback if mediator LLM call fails
        p_lower = prompt_clean.lower()
        if active_document and any(w in p_lower for w in ["size", "compress", "page", "pdf", "file", "document", "doc", "content", "summary"]):
            return "document_agent"
        return "main_agent"

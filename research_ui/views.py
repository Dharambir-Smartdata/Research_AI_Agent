import asyncio
import json
import mimetypes
import os
import re
from pathlib import Path
from datetime import datetime

from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Import from main_agent
from main_agent import (
    initialize_agent,
    ask_gemini,
    _safe_cleanup,
    RESEARCH_DIR,
    REPORT_DIR,
    MODEL,
    UPLOAD_DIR,
    llm,
    _extract_file,
    _extract_text,
    is_document_intent,
    _get_latest_upload_file,
)

# Global singleton agent instances with asyncio lock
_agent_instance = None
_doc_agent_instance = None
_checkpointer = None
_store = None
_agent_lock = asyncio.Lock()


async def get_or_create_doc_agent():
    """Lazily initialize the Document Operations Agent."""
    global _doc_agent_instance, _checkpointer, _store
    if _doc_agent_instance is not None:
        return _doc_agent_instance

    if _checkpointer is None:
        from langgraph.checkpoint.memory import InMemorySaver
        _checkpointer = InMemorySaver()
    if _store is None:
        from langgraph.store.memory import InMemoryStore
        _store = InMemoryStore()

    from document_agent import create_document_agent
    _doc_agent_instance = create_document_agent(
        llm=llm,
        checkpointer=_checkpointer,
        store=_store,
    )
    return _doc_agent_instance

CONVERSATIONS_FILE = RESEARCH_DIR / "conversations.json"


def _load_conversations():
    """Load persistent conversation history from JSON."""
    if not CONVERSATIONS_FILE.exists():
        return {}
    try:
        with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_conversations(data):
    """Persist conversation history to JSON."""
    try:
        CONVERSATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[HISTORY] Failed to save conversations:", e)


async def get_or_create_agent():
    """Lazily initialize the agent once and keep it ready for fast requests."""
    global _agent_instance, _checkpointer, _store
    if _agent_instance is not None:
        return _agent_instance

    async with _agent_lock:
        if _agent_instance is None:
            res = await initialize_agent()
            if isinstance(res, tuple):
                _agent_instance, _checkpointer, _store = res
            else:
                _agent_instance = res
        return _agent_instance


def index(request):
    """Main dashboard page."""
    reports_count = len(_get_reports_list())
    uploads_count = 0
    if UPLOAD_DIR.exists():
        uploads_count = sum(1 for f in UPLOAD_DIR.glob("*") if f.is_file() and not f.name.startswith("."))
    vault_count = reports_count + uploads_count

    context = {
        "model_name": MODEL,
        "research_dir": str(RESEARCH_DIR),
        "upload_dir": str(UPLOAD_DIR),
        "vault_count": vault_count,
    }
    return render(request, "research_ui/index.html", context)


def test_series_view(request):
    """Test Series dashboard page."""
    reports_count = len(_get_reports_list())
    uploads_count = 0
    if UPLOAD_DIR.exists():
        uploads_count = sum(1 for f in UPLOAD_DIR.glob("*") if f.is_file() and not f.name.startswith("."))
    vault_count = reports_count + uploads_count

    context = {
        "model_name": MODEL,
        "research_dir": str(RESEARCH_DIR),
        "upload_dir": str(UPLOAD_DIR),
        "vault_count": vault_count,
    }
    return render(request, "research_ui/test_series.html", context)


def _get_reports_list():
    """Helper to list all generated research reports."""
    reports = []
    if not REPORT_DIR.exists():
        return reports

    for file_path in REPORT_DIR.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            try:
                rel = file_path.relative_to(REPORT_DIR)
                stat = file_path.stat()
                ext = file_path.suffix.lstrip(".").lower()
                topic = rel.parent.name if rel.parent.name else "general"

                # Human-friendly size
                size_bytes = stat.st_size
                if size_bytes < 1024:
                    size_human = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_human = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_human = f"{size_bytes / (1024 * 1024):.1f} MB"

                reports.append(
                    {
                        "filename": file_path.name,
                        "relpath": str(rel),
                        "topic": topic,
                        "format": ext,
                        "size_human": size_human,
                        "size_bytes": size_bytes,
                        "modified_iso": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                        "modified_formatted": datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%b %d, %Y · %H:%M"),
                    }
                )
            except Exception:
                continue

    # Sort newest first
    reports.sort(key=lambda r: r["modified_iso"], reverse=True)
    return reports


def reports_api(request):
    """Returns JSON list of all generated reports."""
    reports = _get_reports_list()
    return JsonResponse({"status": "success", "reports": reports, "count": len(reports)})


BASE_DIR = Path(__file__).resolve().parent.parent


def _find_file_safely(relpath: str) -> Path | None:
    """Safely locate a file across allowed directories (REPORT_DIR, UPLOAD_DIR, RESEARCH_DIR, BASE_DIR)."""
    if not relpath:
        return None
    relpath_clean = relpath.strip().lstrip("/\\")
    fname = Path(relpath_clean).name

    candidates = []

    # 1. Check in UPLOAD_DIR
    if relpath_clean.startswith("uploads/") or relpath_clean.startswith("uploads\\"):
        candidates.append(UPLOAD_DIR / relpath_clean[8:])
    candidates.append(UPLOAD_DIR / fname)
    candidates.append(UPLOAD_DIR / relpath_clean)

    # 2. Check in REPORT_DIR
    candidates.append(REPORT_DIR / relpath_clean)
    candidates.append(REPORT_DIR / fname)

    # 3. Check in RESEARCH_DIR
    candidates.append(RESEARCH_DIR / relpath_clean)
    candidates.append(RESEARCH_DIR / fname)

    # 4. Check relative to BASE_DIR
    candidates.append(BASE_DIR / relpath_clean)

    allowed_bases = [
        REPORT_DIR.resolve(),
        UPLOAD_DIR.resolve(),
        RESEARCH_DIR.resolve(),
        BASE_DIR.resolve(),
    ]

    for cand in candidates:
        try:
            cand_res = cand.resolve()
            if cand_res.is_file():
                if any(str(cand_res).startswith(str(base)) for base in allowed_bases):
                    return cand_res
        except Exception:
            continue
    return None


def download_report(request, relpath):
    """Safely stream a generated report or processed document for download."""
    target_path = _find_file_safely(relpath)
    if not target_path or not target_path.is_file():
        raise Http404(f"File not found or invalid path: {relpath}")

    content_type, _ = mimetypes.guess_type(str(target_path))
    if not content_type:
        content_type = "application/octet-stream"

    response = FileResponse(open(target_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{target_path.name}"'
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


def preview_report(request, relpath):
    """Safely stream report inline for preview (PDF/images) or return JSON for markdown/docx/text."""
    target_path = _find_file_safely(relpath)
    if not target_path or not target_path.is_file():
        raise Http404(f"File not found: {relpath}")

    ext = target_path.suffix.lower()
    if ext == ".pdf":
        response = FileResponse(open(target_path, "rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{target_path.name}"'
        return response
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
        content_type, _ = mimetypes.guess_type(str(target_path))
        response = FileResponse(open(target_path, "rb"), content_type=content_type or "image/png")
        response["Content-Disposition"] = f'inline; filename="{target_path.name}"'
        return response
    elif ext in [".md", ".txt", ".json", ".csv", ".py"]:
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return JsonResponse({
                "status": "success",
                "filename": target_path.name,
                "is_text": True,
                "content": content,
                "format": ext.lstrip("."),
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(target_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return JsonResponse({
                "status": "success",
                "filename": target_path.name,
                "is_text": True,
                "content": "\n\n".join(paragraphs),
                "format": "docx",
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        content_type, _ = mimetypes.guess_type(str(target_path))
        response = FileResponse(open(target_path, "rb"), content_type=content_type or "application/octet-stream")
        response["Content-Disposition"] = f'inline; filename="{target_path.name}"'
        return response


def status_api(request):
    """Returns current system and agent runtime status."""
    reports_count = len(_get_reports_list())
    is_ready = _agent_instance is not None
    return JsonResponse({
        "status": "online",
        "agent_initialized": is_ready,
        "model": MODEL,
        "reports_count": reports_count,
        "capabilities": [
            "Autonomous Web Research & Scraping",
            "Live Browser Automation (Playwright Headless)",
            "MCP Dynamic Filesystem & Graph Memory",
            "Executive Reports Exporter (PDF, DOCX, Markdown)",
            "Automated Citation & Reference Tracking",
        ],
    })


def conversations_list_api(request):
    """List all saved conversations sorted by updated_at desc."""
    data = _load_conversations()
    convs = []
    for cid, c in data.items():
        msgs = c.get("messages", [])
        last_msg = msgs[-1]["content"] if msgs else ""
        convs.append({
            "id": cid,
            "title": c.get("title", "Untitled Session"),
            "created_at": c.get("created_at"),
            "updated_at": c.get("updated_at", c.get("created_at")),
            "message_count": len(msgs),
            "preview": (last_msg[:65] + "...") if len(last_msg) > 65 else last_msg,
        })
    convs.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return JsonResponse({"status": "success", "conversations": convs, "count": len(convs)})


def conversation_detail_api(request, conv_id):
    """Get full messages for a specific conversation."""
    data = _load_conversations()
    if conv_id not in data:
        return JsonResponse({"status": "error", "message": "Conversation not found"}, status=404)
    return JsonResponse({"status": "success", "conversation": data[conv_id]})


@csrf_exempt
def conversation_delete_api(request, conv_id):
    """Delete a conversation from history."""
    if request.method not in ["DELETE", "POST"]:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    data = _load_conversations()
    if conv_id in data:
        del data[conv_id]
        _save_conversations(data)
        return JsonResponse({"status": "success", "message": "Conversation deleted"})
    return JsonResponse({"status": "error", "message": "Conversation not found"}, status=404)


@csrf_exempt
def conversations_clear_api(request):
    """Clear all conversation history."""
    if request.method not in ["DELETE", "POST"]:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    _save_conversations({})
    return JsonResponse({"status": "success", "message": "All conversations cleared"})


@csrf_exempt
def conversation_edit_message_api(request, conv_id):
    """Update a specific message's content in a saved conversation."""
    if request.method not in ["POST", "PATCH"]:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        msg_id = data.get("message_id")
        old_content = data.get("old_content")
        new_content = (data.get("content") or "").strip()
        if not new_content:
            return JsonResponse({"status": "error", "message": "Content cannot be empty"}, status=400)

        convs = _load_conversations()
        if conv_id not in convs:
            return JsonResponse({"status": "error", "message": "Conversation not found"}, status=404)

        updated = False
        for msg in convs[conv_id].get("messages", []):
            if (msg_id and msg.get("id") == msg_id) or (old_content and msg.get("content") == old_content):
                msg["content"] = new_content
                updated = True
                break

        if updated:
            convs[conv_id]["updated_at"] = datetime.now().isoformat()
            _save_conversations(convs)
            return JsonResponse({"status": "success", "message": "Message content updated"})
        return JsonResponse({"status": "error", "message": "Message not found"}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def upload_file_api(request):
    """Handle document or signature file uploads into uploads/ directory (single or multiple)."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    files = request.FILES.getlist("files") or request.FILES.getlist("file")
    if not files:
        single = request.FILES.get("file")
        if single:
            files = [single]

    if not files:
        return JsonResponse({"status": "error", "message": "No file provided"}, status=400)

    allowed = {".pdf", ".docx", ".doc", ".md", ".txt", ".png", ".jpg", ".jpeg"}
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for uploaded_file in files:
        orig_name = Path(uploaded_file.name).name
        clean_name = re.sub(r"[^\w.\-]", "_", orig_name)
        ext = Path(clean_name).suffix.lower()
        if ext not in allowed:
            continue

        target_path = UPLOAD_DIR / clean_name
        try:
            with open(target_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            stat = target_path.stat()
            size_bytes = stat.st_size
            if size_bytes < 1024:
                size_human = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_human = f"{size_bytes / 1024:.1f} KB"
            else:
                size_human = f"{size_bytes / (1024 * 1024):.1f} MB"

            saved_files.append({
                "filename": clean_name,
                "filepath": f"uploads/{clean_name}",
                "size_human": size_human,
                "format": ext.lstrip("."),
                "download_url": f"/api/uploads/download/{clean_name}",
            })
        except Exception:
            continue

    if not saved_files:
        return JsonResponse({"status": "error", "message": "No valid files uploaded"}, status=400)

    first = saved_files[0]
    return JsonResponse({
        "status": "success",
        "files": saved_files,
        "count": len(saved_files),
        "filename": first["filename"],
        "filepath": first["filepath"],
        "size_human": first["size_human"],
        "format": first["format"],
        "download_url": first["download_url"],
    })


def download_upload_file(request, relpath):
    """Safely stream a file from uploads/ or processed documents for download."""
    target_path = _find_file_safely(relpath)
    if not target_path or not target_path.is_file():
        raise Http404(f"File not found: {relpath}")

    content_type, _ = mimetypes.guess_type(str(target_path))
    if not content_type:
        content_type = "application/octet-stream"

    response = FileResponse(open(target_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{target_path.name}"'
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


def preview_upload_file(request, relpath):
    """Safely stream an upload/processed file inline for browser preview."""
    target_path = _find_file_safely(relpath)
    if not target_path or not target_path.is_file():
        raise Http404(f"File not found: {relpath}")

    ext = target_path.suffix.lower()
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(target_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return JsonResponse({
                "status": "success",
                "filename": target_path.name,
                "is_text": True,
                "content": "\n\n".join(paragraphs),
                "format": "docx",
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    elif ext in [".md", ".txt", ".json", ".csv", ".py"] and request.headers.get("accept") == "application/json":
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return JsonResponse({
                "status": "success",
                "filename": target_path.name,
                "is_text": True,
                "content": content,
                "format": ext.lstrip("."),
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    content_type, _ = mimetypes.guess_type(str(target_path))
    if not content_type:
        content_type = "application/pdf" if ext == ".pdf" else "application/octet-stream"

    response = FileResponse(open(target_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'inline; filename="{target_path.name}"'
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


def uploads_list_api(request):
    """List all uploaded / converted / signed / edited documents in uploads/."""
    files = []
    if UPLOAD_DIR.exists():
        for f in UPLOAD_DIR.glob("*"):
            if f.is_file() and not f.name.startswith("."):
                try:
                    stat = f.stat()
                    size_b = stat.st_size
                    size_h = f"{size_b} B" if size_b < 1024 else (f"{size_b/1024:.1f} KB" if size_b < 1024*1024 else f"{size_b/(1024*1024):.1f} MB")
                    files.append({
                        "filename": f.name,
                        "filepath": f"uploads/{f.name}",
                        "format": f.suffix.lstrip(".").lower(),
                        "size_human": size_h,
                        "modified_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "modified_formatted": datetime.fromtimestamp(stat.st_mtime).strftime("%b %d · %H:%M"),
                        "download_url": f"/api/uploads/download/{f.name}",
                    })
                except Exception:
                    continue
    files.sort(key=lambda x: x.get("modified_iso", ""), reverse=True)
    return JsonResponse({"status": "success", "files": files, "count": len(files)})


@csrf_exempt
async def chat_api(request):
    """Handles chat research queries, document agent operations, and persistent session history."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid JSON body"}, status=400)

    prompt = (data.get("prompt") or "").strip()
    last_report = data.get("last_report") or None
    conv_id = (data.get("conversation_id") or "").strip()
    file_paths = data.get("file_paths") or []
    file_path = _extract_file(prompt) or (data.get("file_path") or "").strip()
    if not file_path and file_paths:
        file_path = file_paths[0]

    if not prompt:
        return JsonResponse({"status": "error", "message": "Prompt cannot be empty"}, status=400)

    if not conv_id:
        conv_id = f"conv_{int(datetime.now().timestamp() * 1000)}"

    convs = _load_conversations()
    conv_record = convs.get(conv_id, {})
    active_doc = conv_record.get("active_document") or (data.get("active_document") or "").strip() or None

    target_doc = None
    if file_path:
        target_doc = file_path
    elif active_doc and _find_file_safely(active_doc):
        target_doc = active_doc
    else:
        target_doc = _get_latest_upload_file()

    is_doc_task = bool(
        file_paths
        or file_path
        or is_document_intent(prompt, bool(last_report), bool(active_doc))
    )

    try:
        if is_doc_task:
            if not target_doc:
                response_text = "No active document found in this session. Please upload a document or attach a file first to perform document operations."
            else:
                doc_agent = await get_or_create_doc_agent()
                if len(file_paths) > 1:
                    joined = ", ".join(file_paths)
                    effective_prompt = f"Target Documents: {joined}\nInstruction: {prompt}"
                else:
                    effective_prompt = prompt if (target_doc in prompt) else f"Target Document: {target_doc}\nInstruction: {prompt}"
                response = await doc_agent.ainvoke(
                    {"messages": [{"role": "user", "content": effective_prompt}]},
                    config={"configurable": {"thread_id": f"doc-{conv_id}"}},
                )
                response_text = _extract_text(response["messages"][-1].content)
        else:
            agent = await get_or_create_agent()
            response_text = await ask_gemini(
                prompt=prompt,
                agent=agent,
                last_report=last_report,
                thread_id=f"research-{conv_id}",
            )

        # Check if this was a save confirmation
        stripped = response_text.lstrip()
        is_saved = stripped.startswith("SAVED:")
        is_save_failed = stripped.startswith("SAVE_FAILED:")

        saved_path = None
        if is_saved:
            parts = stripped.split("SAVED:", 1)
            if len(parts) > 1:
                saved_path = parts[1].strip()

        # Document Operation result detection
        is_doc_result = False
        doc_action = None
        doc_path = None
        doc_filename = None
        for prefix, action_name in [
            ("EDITED:", "edit"),
            ("REMOVED:", "remove_pages"),
            ("SIGNED:", "sign"),
            ("CONVERTED:", "convert"),
            ("MERGED:", "merge"),
            ("SAVED: uploads/", "save"),
            ("SAVED:", "save"),
        ]:
            if prefix in response_text:
                parts = response_text.split(prefix, 1)
                candidate_path = parts[1].strip().splitlines()[0].strip().strip("`*\"'")
                if any(candidate_path.lower().endswith(ext) for ext in [".pdf", ".docx", ".doc", ".md", ".txt"]):
                    is_doc_result = True
                    doc_action = action_name if action_name != "save" else "edit"
                    doc_path = candidate_path
                    doc_filename = Path(doc_path).name
                    break

        is_doc_task = is_doc_result or is_document_intent(prompt, bool(last_report), bool(active_doc))

        if not is_doc_result and is_doc_task:
            found_docs = re.findall(
                r"\b(?:uploads/)?([a-zA-Z0-9_\-.]+\.(?:pdf|docx|doc|md|txt))\b",
                response_text,
                re.IGNORECASE,
            )
            for doc_name in reversed(found_docs):
                cand = UPLOAD_DIR / doc_name
                if cand.is_file():
                    is_doc_result = True
                    doc_filename = doc_name
                    doc_path = f"uploads/{doc_name}"
                    break

            if not is_doc_result:
                latest = _get_latest_upload_file()
                if latest:
                    is_doc_result = True
                    doc_path = latest
                    doc_filename = Path(latest).name

        if is_doc_result and not doc_action and doc_filename:
            prefix = doc_filename.split("_")[0].lower()
            action_map = {
                "trimmed": "remove_pages",
                "removed": "remove_pages",
                "signed": "sign",
                "converted": "convert",
                "merged": "merge",
                "split": "split",
                "reverted": "edit",
            }
            doc_action = action_map.get(prefix, "edit")

        # Save conversation history to JSON
        now_dt = datetime.now()
        now_iso = now_dt.isoformat()
        now_time = now_dt.strftime("%I:%M %p")

        if conv_id not in convs:
            clean_title = prompt.replace("\n", " ").strip()
            if len(clean_title) > 38:
                clean_title = clean_title[:38] + "..."
            convs[conv_id] = {
                "id": conv_id,
                "title": clean_title,
                "created_at": now_iso,
                "updated_at": now_iso,
                "last_report": response_text if (not is_saved and not is_doc_result) else (last_report or None),
                "active_document": None,
                "messages": [],
            }

        conv_record = convs[conv_id]
        conv_record["updated_at"] = now_iso
        if not is_saved and not is_save_failed and not is_doc_result:
            conv_record["last_report"] = response_text

        # Update active document in conversation state
        if doc_path:
            conv_record["active_document"] = doc_path
        elif is_doc_task and target_doc:
            conv_record["active_document"] = target_doc
        elif file_path:
            conv_record["active_document"] = file_path

        edit_msg_id = data.get("edit_message_id")
        is_edit = bool(data.get("is_edit") or edit_msg_id)

        replaced = False
        if is_edit:
            messages = conv_record.get("messages", [])
            target_idx = -1
            for idx, m in enumerate(messages):
                if edit_msg_id and m.get("id") == edit_msg_id:
                    target_idx = idx
                    break
            if target_idx == -1 and messages:
                for idx in range(len(messages) - 1, -1, -1):
                    if messages[idx].get("role") == "user":
                        target_idx = idx
                        break

            if target_idx != -1:
                messages[target_idx]["content"] = prompt
                messages[target_idx]["timestamp"] = now_time
                assistant_idx = target_idx + 1
                new_assistant_msg = {
                    "id": f"msg_a_{int(now_dt.timestamp()*1000)}",
                    "role": "assistant",
                    "content": response_text,
                    "is_saved": is_saved,
                    "saved_path": saved_path,
                    "is_doc_task": is_doc_task,
                    "is_document_agent": is_doc_task,
                    "is_doc_result": is_doc_result,
                    "doc_action": doc_action,
                    "doc_filename": doc_filename,
                    "download_url": f"/api/uploads/download/{doc_filename}" if doc_filename else None,
                    "timestamp": now_time,
                }
                if assistant_idx < len(messages) and messages[assistant_idx].get("role") == "assistant":
                    new_assistant_msg["id"] = messages[assistant_idx].get("id", new_assistant_msg["id"])
                    messages[assistant_idx] = new_assistant_msg
                    conv_record["messages"] = messages[: assistant_idx + 1]
                else:
                    messages.insert(assistant_idx, new_assistant_msg)
                    conv_record["messages"] = messages[: assistant_idx + 1]
                replaced = True

        if not replaced:
            conv_record["messages"].append({
                "id": f"msg_u_{int(now_dt.timestamp()*1000)}",
                "role": "user",
                "content": prompt,
                "timestamp": now_time,
            })

            conv_record["messages"].append({
                "id": f"msg_a_{int(now_dt.timestamp()*1000)}",
                "role": "assistant",
                "content": response_text,
                "is_saved": is_saved,
                "saved_path": saved_path,
                "is_doc_task": is_doc_task,
                "is_document_agent": is_doc_task,
                "is_doc_result": is_doc_result,
                "doc_action": doc_action,
                "doc_filename": doc_filename,
                "download_url": f"/api/uploads/download/{doc_filename}" if doc_filename else None,
                "timestamp": now_time,
            })

        _save_conversations(convs)

        return JsonResponse({
            "status": "success",
            "response": response_text,
            "is_saved": is_saved,
            "is_save_failed": is_save_failed,
            "saved_path": saved_path,
            "is_doc_task": is_doc_task,
            "is_document_agent": is_doc_task,
            "is_doc_result": is_doc_result,
            "doc_action": doc_action,
            "doc_path": doc_path,
            "doc_filename": doc_filename,
            "active_document": conv_record.get("active_document"),
            "download_url": f"/api/uploads/download/{doc_filename}" if doc_filename else None,
            "conversation_id": conv_id,
            "conversation_title": conv_record.get("title", ""),
        })
    except Exception as error:
        return JsonResponse({
            "status": "error",
            "message": str(error),
        }, status=500)


@csrf_exempt
def favicon_view(request):
    """Serve a 204 No Content for /favicon.ico to avoid 404 noise."""
    return HttpResponse(status=204)


@csrf_exempt
async def reset_api(request):
    """Safely cleanup and reset the agent instance for a clean state."""
    global _agent_instance, _doc_agent_instance, _checkpointer, _store
    async with _agent_lock:
        if _agent_instance is not None:
            await _safe_cleanup()
        _agent_instance = None
        _doc_agent_instance = None
        _checkpointer = None
        _store = None
    return JsonResponse({"status": "success", "message": "Agent session reset successfully."})

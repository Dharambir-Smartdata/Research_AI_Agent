# 🌐 VEDORA AI — Dual-Agent Intelligence, Autonomous Web Research & Document Code Execution

An enterprise-grade, dual-agent AI research and document automation platform powered by **LangChain**, **LangGraph**, **Google Gemini**, **Playwright**, and **MCP (Model Context Protocol)**. Equipped with an ultra-premium, modern **Django Web Interface** featuring Dark & Light mode, full Conversation History persistence, an Artifacts Vault, multi-file drag-and-drop, interactive document previews, and automated Python script generation and execution.

---

## ✨ System Architecture & Highlights

### 🤖 Dual-Agent Collaborative System

```
                      ┌───────────────────────────────────────┐
                      │        User Query / File Upload       │
                      └──────────────────┬────────────────────┘
                                         │
                         ┌───────────────▼───────────────┐
                         │   4-Tier Intent & Context     │
                         │       Router (main_agent)     │
                         └───────┬───────────────┬───────┘
                                 │               │
                 [Web Research Intent]       [Document Operation Intent]
                                 │               │
                                 ▼               ▼
         ┌───────────────────────────────┐   ┌───────────────────────────────┐
         │          Main Agent           │   │        Document Agent         │
         │      (Web Intelligence)       │   │   (Code Gen & Execution)      │
         ├───────────────────────────────┤   ├───────────────────────────────┤
         │ • DuckDuckGo Search           │   │ • Dynamic Script Generation   │
         │ • Playwright DOM Crawler      │   │ • doc_scripts/ Script Re-use  │
         │ • Perplexity-Style Citations  │   │ • Subprocess Code Execution   │
         │ • PDF / DOCX / MD Exporter    │   │ • PDF / DOCX / Text Transform │
         └───────────────────────────────┘   └───────────────────────────────┘
                                 │               │
                                 ▼               ▼
                      ┌───────────────────────────────────────┐
                      │     Django Single-Page Interface      │
                      │ • Interactive In-Modal Document Viewer│
                      │ • One-Click Download & Preview Cards  │
                      │ • Research Artifacts Vault (All/Tabs) │
                      │ • Multi-File Drag & Drop Composer     │
                      └───────────────────────────────────────┘
```

1. **Main Agent (Autonomous Web Research)**:
   - **Deep Web Crawling**: Autonomous headless browser discovery powered by Playwright and DuckDuckGo for live, un-truncated full-text extraction.
   - **Evidence Verification**: Multi-perspective fact verification, cross-referencing, and structured executive synthesis.
   - **Perplexity-Style Source Pills**: Compact source pills displaying website count, site favicons, and an expandable grid of reference cards.
   - **Executive Report Exporter**: Direct saving to **PDF**, **Microsoft Word (.docx)**, or **Markdown (.md)**.

2. **Document Agent (Code Generation & Execution)**:
   - **Autonomous Python Script Generation**: Analyzes document operation prompts, generates standalone Python code, and persists scripts into `doc_scripts/`.
   - **Intelligent Script Reuse**: Checks `doc_scripts/` first. If a pre-built or previously generated script exists (`remove_pages.py`, `revert_pages.py`, `edit_text.py`, `convert_document.py`, `add_signature.py`), it reuses it via `run_saved_script` rather than duplicating code.
   - **Multi-Document Operations**: Merging multiple PDFs, deleting/trimming pages, restoring/reverting pages from originals, text find-and-replace, format conversions, and digital signature placement.
   - **Clean Output & Zero-Path Leakage**: Automatically presents **Preview** and **Download File** cards without exposing internal filesystem paths or raw links.

---

## 🎨 Ultra-Premium Django Web Interface

- **Multi-File Upload & Drag-and-Drop**: Drag multiple files directly into the composer or use the multi-select file picker; interactive file chips display names, file sizes, and individual remove buttons.
- **In-Place Chat Context Editing**: Hover and click **Edit** on any user prompt to edit instructions in-place, dispatching an immediate in-place regeneration without cluttering thread history.
- **Interactive Full-Screen Preview Modal**: Built-in modal viewer to preview PDFs, images, and text documents natively in the browser without downloading.
- **Research Artifacts Vault**: Slide-over drawer indexing all generated research dossiers and uploaded/processed documents with format filtering tabs (**All**, **PDF**, **Word**, **Markdown**, **Uploads**) and live search.
- **Conversation History Drawer**: Persistent thread management with auto-titling, thread switching, local JSON storage, and full deletion controls.
- **Adaptive Dark / Light Themes**: Instant theme toggle with localStorage persistence and zero flash of unstyled content (FOUC).

---

## 🏗️ Project Structure

```
AI-Agent/
├── main_agent.py              # Primary research agent, intent router & CLI entrypoint
├── document_agent.py          # Document Code Generation & Execution Agent (2nd Agent)
├── browser_tools.py           # Playwright headless browser & document exporter tools
├── mcp_manager.py             # Model Context Protocol hub & dynamic filesystem tools
├── manage.py                  # Django CLI management entrypoint
├── requirements.txt           # Unified project dependencies
├── .env.example               # Environment variables template
│
├── doc_scripts/               # Persistent Python scripts for document operations
│   ├── remove_pages.py        # PDF page trimming / deletion
│   ├── revert_pages.py        # PDF page restoration / recovery from originals
│   ├── edit_text.py           # Text find-and-replace in PDF and DOCX
│   ├── convert_document.py    # Conversion between PDF, DOCX, and Markdown
│   └── add_signature.py       # Digital signature stamping
│
├── web_config/                # Django Project Configuration
│   ├── settings.py            # Django configuration, static paths, and pkgs integration
│   ├── urls.py                # Root router
│   └── wsgi.py                # WSGI application entrypoint
│
├── research_ui/               # Django Web Application & REST API
│   ├── views.py               # Chat streaming, upload handlers, preview views, vault APIs
│   ├── urls.py                # URL endpoints
│   ├── templates/
│   │   └── research_ui/
│   │       └── index.html     # Single-page application interface
│   └── static/
│       ├── css/
│       │   └── styles.css     # Quantum animations, theme variables, and responsive design
│       └── js/
│           └── app.js         # Client logic, drag-and-drop, drawers, in-place edit & marked.js
│
├── uploads/                   # User uploaded documents and processed document outputs
└── research/                  # Research storage
    ├── conversations.json     # Persisted chat threads & message histories
    └── reports/               # Generated PDF, DOCX, and Markdown research dossiers
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+**
- **Google Gemini API Key** (obtain from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation

Clone the repository and set up a virtual environment:

```bash
git clone <repository-url>
cd AI-Agent

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Environment Configuration

Copy the example environment file and configure your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Google Gemini API Key (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Gemini Model Name (e.g. gemini-2.5-flash, gemini-flash-lite-latest)
GEMINI_MODEL=demo_model_name

NEO4J_URL=demo_url
NEO4J_USERNAME=demo_username
NEO4J_PASSWORD=demo_password
```

---

## 💻 Running the Application

### Launch the Web Interface (Recommended)
```bash
python manage.py runserver
```

Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

### Running via CLI
Run the interactive CLI agent directly:
```bash
python main_agent.py
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Main Web Application UI |
| `/api/chat/` | `POST` | Dispatches research query or document code operation |
| `/api/upload/` | `POST` | Upload single or multiple files (`multipart/form-data`) |
| `/api/uploads/` | `GET` | List all uploaded and processed document artifacts |
| `/api/uploads/download/<path>` | `GET` | Download processed document from `uploads/` |
| `/api/uploads/preview/<path>` | `GET` | Stream document inline for browser/modal preview |
| `/api/reports/` | `GET` | List all generated research dossiers in the vault |
| `/api/reports/download/<path>` | `GET` | Download a generated research dossier |
| `/api/reports/preview/<path>` | `GET` | Fetch Markdown report content for previewing |
| `/api/conversations/` | `GET` | List all saved conversation sessions |
| `/api/conversations/<id>/` | `GET` | Fetch full message history for a conversation |
| `/api/conversations/<id>/delete/`| `POST` | Delete a single conversation thread |
| `/api/conversations/clear/` | `POST` | Clear all conversation history |
| `/api/conversations/<id>/message/edit/` | `POST` | Update a specific message in-place |
| `/api/status/` | `GET` | System health check and model runtime status |
| `/api/reset/` | `POST` | Reset current memory checkpoint for a clean session |

---

## 📄 Document Operations Quick Reference

You can perform any of the following operations through natural language:
- **Merge Documents**: *"Merge these 3 PDFs into a single report"* (attach or drag files).
- **Remove Pages**: *"Remove page 3 and page 5 from this PDF"*.
- **Restore / Revert Pages**: *"Revert back page 3"* (automatically restores from original).
- **Find & Replace**: *"Rename 'Old Company' to 'New Company' across the document"*.
- **Convert Formats**: *"Convert this PDF into Word format (.docx)"*.
- **Apply Signatures**: *"Stamp my uploaded signature on page 1 at the bottom right"*.
- **Custom Scripts**: *"Generate a python script to rotate all landscape pages to portrait"*.

---

## 🛡️ License

This project is licensed under the MIT License.

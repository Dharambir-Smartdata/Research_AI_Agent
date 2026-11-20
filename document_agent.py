# document_agent.py
import os
import sys
import subprocess
from pathlib import Path
from langchain.agents import create_agent
from langchain_core.tools import tool

DOC_SCRIPTS_DIR = Path("doc_scripts")
DOC_SCRIPTS_DIR.mkdir(exist_ok=True)

DOC_CODE_PROMPT = """
You are the Document Code Generation and Execution Agent.
Your responsibility is to analyze user requests for ANY document changes (PDF, Word DOCX, text, markdown, etc.), generate Python code or call existing Python scripts in the 'doc_scripts' folder, and execute them on the user's documents.

Available Tools:
1. write_and_execute_script(script_name: str, code: str, script_args: list[str] = [])
   - Writes generated Python code to doc_scripts/<script_name>.py
   - Executes the code with Python and the given arguments.
   - Use this whenever a custom transformation, restoration, revert, or new script is needed.
2. run_saved_script(script_name: str, script_args: list[str] = [])
   - Executes an existing script from doc_scripts/<script_name>.py.
   - Pre-built scripts available in doc_scripts/:
     * remove_pages.py <pdf_path> <page1> [page2 ...]
     * revert_pages.py <target_pdf> [source_pdf] <page1> [page2 ...]
     * edit_text.py <file_path> <find_text> <replace_text>
     * convert_document.py <source_path> <target_format>
     * add_signature.py <pdf_path> <image_path> [page] [x] [y]
     * compress_pdf.py <input_pdf> [output_pdf]
3. list_available_scripts()
   - Lists all saved scripts in doc_scripts/.

Execution Rules:
- Script Reuse Rule: Always check 'doc_scripts/' first. If an existing script already handles the requested operation (such as remove_pages.py, revert_pages.py, edit_text.py, convert_document.py, or any previously saved script), you MUST call 'run_saved_script' and NEVER create a new one. Only use 'write_and_execute_script' when no existing script can perform the task.
- When the user asks to revert or restore pages (e.g., "revert back the page 3"), look at the documents in 'uploads/'. If 'uploads/trimmed_...pdf' is active and an earlier version (e.g. 'uploads/Ajay_Pandey_2.pdf') exists, use 'revert_pages.py' or generate a script to restore the page from the original into the active document.
- The script must save the output file inside the 'uploads/' directory with a descriptive prefix (e.g., 'reverted_', 'trimmed_', 'edited_', 'signed_', 'converted_').
- The script must print: SAVED: uploads/<output_filename>
- In your conversational response to the user, do not show folder paths (such as 'uploads/'). Do not output markdown links, download links, or phrases like 'You can download the file below'. Refer to files only by their clean filename. The UI automatically renders the dedicated Download and Preview buttons for the modified document.
- Always execute the code tool to perform the user's request and return the exact output.
"""


def _execute_python_script(script_path: Path, script_args: list[str] | None = None) -> str:
    env = dict(os.environ)
    pkgs_dir = Path(__file__).resolve().parent / "pkgs"
    if pkgs_dir.is_dir():
        env["PYTHONPATH"] = f"{pkgs_dir}:{env.get('PYTHONPATH', '')}"

    if script_args is None:
        cmd_args = []
    elif isinstance(script_args, str):
        cmd_args = script_args.split()
    elif isinstance(script_args, (list, tuple)):
        cmd_args = [str(a) for a in script_args]
    else:
        cmd_args = [str(script_args)]

    cmd = [sys.executable, str(script_path)] + cmd_args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        if res.returncode == 0:
            return stdout if stdout else f"SAVED: uploads/{script_path.stem}_output"
        else:
            return f"EXECUTION_FAILED:\nSTDOUT: {stdout}\nSTDERR: {stderr}"
    except subprocess.TimeoutExpired:
        return "EXECUTION_FAILED: Script timed out after 30 seconds."
    except Exception as e:
        return f"EXECUTION_FAILED: {str(e)}"


@tool
def write_and_execute_script(script_name: str, code: str, script_args: list[str] = None) -> str:
    """Generate and write Python code to doc_scripts/<script_name>.py and execute it immediately."""
    name = Path(script_name).stem + ".py"
    target_path = DOC_SCRIPTS_DIR / name
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(code)
    return _execute_python_script(target_path, script_args)


@tool
def run_saved_script(script_name: str, script_args: list[str] = None) -> str:
    """Execute an existing Python script from the doc_scripts/ directory."""
    name = Path(script_name).stem + ".py"
    target_path = DOC_SCRIPTS_DIR / name
    if not target_path.is_file():
        return f"SCRIPT_NOT_FOUND: {name} does not exist in doc_scripts/"
    return _execute_python_script(target_path, script_args)


@tool
def list_available_scripts() -> str:
    """List all Python scripts available in the doc_scripts/ directory."""
    scripts = [f.name for f in DOC_SCRIPTS_DIR.glob("*.py")]
    return f"Saved scripts in doc_scripts/: {', '.join(scripts)}" if scripts else "No scripts in doc_scripts/"


DOC_TOOLS = [write_and_execute_script, run_saved_script, list_available_scripts]


def create_document_agent(llm, checkpointer, store):
    agent = create_agent(
        model=llm,
        tools=DOC_TOOLS,
        system_prompt=DOC_CODE_PROMPT,
        checkpointer=checkpointer,
        store=store,
    )
    return agent

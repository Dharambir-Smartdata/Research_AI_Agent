"""
Inspect document metadata: file size (bytes, KB, MB), page count, format.
Usage: python get_doc_info.py <file_path>
"""
import sys
import os
from pathlib import Path


def get_doc_info(path_str: str) -> None:
    p = Path(path_str)
    if not p.is_file():
        cand = Path("uploads") / p.name
        if cand.is_file():
            p = cand
        else:
            print(f"ERROR: File not found: {path_str}")
            return

    size_b = p.stat().st_size
    if size_b < 1024:
        size_h = f"{size_b} B"
    elif size_b < 1024 * 1024:
        size_h = f"{size_b / 1024:.2f} KB"
    else:
        size_h = f"{size_b / (1024 * 1024):.2f} MB"

    pages = None
    ext = p.suffix.lower()
    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(str(p))
            pages = len(doc)
            doc.close()
        except Exception:
            pass

    out = f"Filename: {p.name}\nSize: {size_h} ({size_b:,} bytes)"
    if pages is not None:
        out += f"\nPages: {pages}"
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_doc_info.py <file_path>")
        sys.exit(1)
    get_doc_info(sys.argv[1])

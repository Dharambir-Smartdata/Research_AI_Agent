#!/usr/bin/env python3
"""Remove specified pages or page ranges from a PDF or Word (DOCX/DOC) document.
Usage: python doc_scripts/remove_pages.py <file_path> <page_spec...>
Examples:
  python doc_scripts/remove_pages.py uploads/sample.pdf 3
  python doc_scripts/remove_pages.py uploads/sample.pdf 40-50
  python doc_scripts/remove_pages.py uploads/sample.pdf from 40 to 50
  python doc_scripts/remove_pages.py uploads/sample.pdf 3, 5, 8
  python doc_scripts/remove_pages.py uploads/contract.docx 2-4
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Add pkgs directory to path for dependencies
pkgs_dir = Path(__file__).resolve().parent.parent / "pkgs"
if pkgs_dir.is_dir() and str(pkgs_dir) not in sys.path:
    sys.path.insert(0, str(pkgs_dir))

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

try:
    import docx
except ImportError:
    docx = None


def parse_page_spec(args: list[str]) -> list[int]:
    """Parse flexible page specifications including single pages, discrete lists, and ranges.
    Supports: '40-50', '40..50', '40 to 50', 'from 40 to 50', '3, 5, 8', '1-5, 10'.
    """
    raw = " ".join(args).lower()
    # Normalize words like 'page', 'pages', 'pg', 'no', 'from'
    text = re.sub(r'\b(?:pages?|pgs?|p\.|no\.?|from)\b', ' ', raw)
    # Normalize ranges like '40 to 50' or '40 through 50' to '40-50'
    text = re.sub(r'\s*(?:to|through|thru|until|-|\.\.)\s*', '-', text)
    
    pages = set()
    tokens = re.split(r'[,;\s]+', text)
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        m_range = re.match(r'^(\d+)-(\d+)$', tok)
        if m_range:
            start, end = int(m_range.group(1)), int(m_range.group(2))
            pages.update(range(min(start, end), max(start, end) + 1))
            continue
        if tok.isdigit():
            pages.add(int(tok))
            continue
        for s, e in re.findall(r'(\d+)-(\d+)', tok):
            pages.update(range(min(int(s), int(e)), max(int(s), int(e)) + 1))
            
    return sorted(pages)


def resolve_file_path(file_path: str) -> Path:
    p = Path(file_path)
    if not p.is_file():
        p_up = Path("uploads") / p.name
        if p_up.is_file():
            p = p_up
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
    return p


def get_pdf_printed_page_map(doc) -> dict[int, int]:
    """Find mapping from printed page number (folio) to 1-indexed physical sheet."""
    printed_map = {}
    for idx in range(doc.page_count):
        text = doc[idx].get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3] + lines[-3:]:
            if line.isdigit() and 1 <= int(line) <= doc.page_count:
                matched = int(line)
                if matched not in printed_map:
                    printed_map[matched] = idx + 1
                break
    return printed_map


def remove_pdf_pages(p: Path, pages: list[int]) -> tuple[str, int, int, int]:
    if fitz is None:
        raise ImportError("pymupdf / fitz library is required for PDF manipulation.")

    doc = fitz.open(p)
    total = doc.page_count

    # Check if requested pages match printed folio page numbers with an offset
    pmap = get_pdf_printed_page_map(doc)
    has_offset = any(pmap.get(n) != n for n in pages if n in pmap)
    if has_offset and all(n in pmap for n in pages):
        target_sheets = [pmap[n] for n in pages]
    else:
        target_sheets = pages

    valid = [n for n in sorted(set(target_sheets), reverse=True) if 1 <= n <= total]
    if not valid:
        doc.close()
        raise ValueError(f"No valid pages to remove. Total pages: {total}")
    if len(valid) >= total:
        doc.close()
        raise ValueError(f"Cannot remove all {total} pages from document.")

    for n in valid:
        doc.delete_page(n - 1)

    out = Path("uploads") / f"trimmed_{p.name}"
    doc.save(out)
    doc.close()
    return str(out), total, len(valid), total - len(valid)


def remove_word_pages(p: Path, pages: list[int]) -> tuple[str, int, int, int]:
    # If legacy .doc format, convert to .docx first using spire.doc if available
    working_path = p
    if p.suffix.lower() == ".doc":
        try:
            import spire.doc as sp
            sp_doc = sp.Document()
            sp_doc.LoadFromFile(str(p))
            conv_path = Path("uploads") / f"temp_{p.stem}.docx"
            sp_doc.SaveToFile(str(conv_path), sp.FileFormat.Docx)
            working_path = conv_path
        except Exception as e:
            raise RuntimeError(f"Could not convert legacy .doc file: {e}")

    if docx is None:
        raise ImportError("python-docx library is required for Word document manipulation.")

    # Detect metadata page count from docProps/app.xml
    meta_pages = 1
    try:
        with zipfile.ZipFile(working_path, 'r') as z:
            if 'docProps/app.xml' in z.namelist():
                xml_data = z.read('docProps/app.xml')
                root = ET.fromstring(xml_data)
                for elem in root.iter():
                    if elem.tag.endswith('Pages'):
                        meta_pages = max(1, int(elem.text))
    except Exception:
        pass

    doc = docx.Document(working_path)
    body = doc.element.body
    children = [c for c in list(body) if not c.tag.endswith('sectPr')]

    # Check for explicit hard page breaks or soft rendered breaks
    break_indices = []
    for idx, c in enumerate(children):
        xml = c.xml
        if ('w:br' in xml and 'type="page"' in xml) or ('lastRenderedPageBreak' in xml):
            break_indices.append(idx)

    detected_pages = len(break_indices) + 1
    total_pages = max(detected_pages, meta_pages)

    element_pages = []
    if detected_pages > 1 and detected_pages >= int(total_pages * 0.8):
        # Break-based segmentation
        curr = 1
        for c in children:
            element_pages.append((c, curr))
            xml = c.xml
            if ('w:br' in xml and 'type="page"' in xml) or ('lastRenderedPageBreak' in xml):
                curr += 1
    else:
        # Paragraph & table chunk distribution across total pages
        n = max(1, len(children))
        for idx, c in enumerate(children):
            p_num = min(total_pages, int(idx * total_pages / n) + 1)
            element_pages.append((c, p_num))

    to_del = set(pages)
    valid_to_del = [n for n in to_del if 1 <= n <= total_pages]
    if not valid_to_del:
        raise ValueError(f"No valid pages to remove. Total pages: {total_pages}")
    if len(valid_to_del) >= total_pages:
        raise ValueError(f"Cannot remove all {total_pages} pages from document.")

    for c, p_num in element_pages:
        if p_num in valid_to_del:
            c.getparent().remove(c)

    out_name = f"trimmed_{p.stem}.docx"
    out = Path("uploads") / out_name
    doc.save(out)

    # Clean up temp file if created
    if working_path != p and working_path.is_file():
        try:
            working_path.unlink()
        except OSError:
            pass

    return str(out), total_pages, len(valid_to_del), total_pages - len(valid_to_del)


def remove_pages(file_path: str, pages: list[int]) -> tuple[str, int, int, int]:
    p = resolve_file_path(file_path)
    suffix = p.suffix.lower()
    if suffix in [".docx", ".doc"]:
        return remove_word_pages(p, pages)
    elif suffix == ".pdf":
        return remove_pdf_pages(p, pages)
    else:
        # Default try pdf
        return remove_pdf_pages(p, pages)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: remove_pages.py <file_path> <page_spec...>")
        print("Examples:")
        print("  remove_pages.py uploads/sample.pdf 3")
        print("  remove_pages.py uploads/sample.pdf 40-50")
        print("  remove_pages.py uploads/sample.pdf from 40 to 50")
        print("  remove_pages.py uploads/doc.docx 2-4")
        sys.exit(1)

    target = sys.argv[1]
    parsed_pages = parse_page_spec(sys.argv[2:])
    if not parsed_pages:
        print(f"ERROR: Could not parse any page numbers from: {' '.join(sys.argv[2:])}")
        sys.exit(1)

    try:
        out_file, total, removed, remaining = remove_pages(target, parsed_pages)
        if len(parsed_pages) > 5:
            pages_desc = f"{parsed_pages[0]}-{parsed_pages[-1]} ({removed} pages)"
        else:
            pages_desc = ", ".join(str(x) for x in parsed_pages)
        print(f"Original pages: {total}, Removed: {removed} (pages {pages_desc}), Remaining pages: {remaining}")
        print(f"SAVED: {out_file}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

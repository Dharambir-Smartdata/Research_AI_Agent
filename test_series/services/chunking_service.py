"""
Semantic and Structure-Aware Chunking Service for UPSC Study Material and PYQ PDFs.
"""
import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Normalize text, replace multiple spaces, smart quotes, and strange dashes."""
    if not text:
        return ""
    # Smart quotes & dashes
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("—", " - ").replace("–", " - ")
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")
    # Fix broken hyphenated linebreaks (e.g. "com-\nmunication" -> "communication")
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Collapse multiple whitespaces and excessive linebreaks
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def chunk_document(
    pages: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 80,
    metadata_base: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Structure-aware chunking that respects page boundaries, paragraph breaks, and headings.
    
    pages: list of dicts: [{"page_number": int, "text": str}]
    returns list of chunk dicts ready for embedding and vector storage.
    """
    metadata_base = metadata_base or {}
    chunks = []
    chunk_counter = 0

    for page in pages:
        p_num = page.get("page_number", 1)
        raw_text = page.get("text", "")
        cleaned = clean_text(raw_text)
        if not cleaned:
            continue

        # Split into logical paragraphs or sentences
        paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
        
        current_chunk_text = ""
        current_heading = ""
        clean_doc = re.sub(r'[^a-zA-Z0-9_]', '_', str(metadata_base.get('document_name', 'doc')))

        for para in paragraphs:
            # Check if this paragraph is a section header (e.g., "1. Preamble & Basic Structure")
            if re.match(r'^(?:\d+\.|\bSection\b|\bModule\b|\bTopic\b|\bQuestion\b|\bQ:)', para, re.IGNORECASE) and len(para) < 120:
                current_heading = para

            # If adding this paragraph exceeds chunk size, flush current chunk
            if current_chunk_text and (len(current_chunk_text) + len(para) > chunk_size):
                chunk_id = f"{metadata_base.get('subject', 'UPSC')}_{metadata_base.get('source_type', 'doc')}_{clean_doc}_{chunk_counter}"
                chunk_record = {
                    "chunk_id": chunk_id,
                    "text": current_chunk_text.strip(),
                    "page_number": p_num,
                    "section_heading": current_heading,
                    **metadata_base
                }
                chunks.append(chunk_record)
                chunk_counter += 1

                # Overlap: keep the tail of the current chunk
                overlap_text = current_chunk_text[-chunk_overlap:] if len(current_chunk_text) > chunk_overlap else ""
                current_chunk_text = (overlap_text + " " + para).strip()
            else:
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para

        # Flush any remaining text for this page
        if current_chunk_text.strip():
            chunk_id = f"{metadata_base.get('subject', 'UPSC')}_{metadata_base.get('source_type', 'doc')}_{clean_doc}_{chunk_counter}"
            chunk_record = {
                "chunk_id": chunk_id,
                "text": current_chunk_text.strip(),
                "page_number": p_num,
                "section_heading": current_heading,
                **metadata_base
            }
            chunks.append(chunk_record)
            chunk_counter += 1

    return chunks

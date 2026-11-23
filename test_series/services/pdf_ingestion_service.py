"""
PDF Ingestion Service with Strict Safety Lifecycle:
Extract -> Clean -> Chunk -> Embed -> Store -> Verify Retrieval -> Optional Cleanup of Source PDFs.
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

import fitz  # PyMuPDF from pkgs

from test_series.services.chunking_service import clean_text, chunk_document
from test_series.services.vector_store_service import (
    add_chunks_to_vector_store,
    query_vector_store,
    get_upsc_collection
)
from test_series.models import UPSC_SUBJECTS

logger = logging.getLogger(__name__)

UPSC_ROOT = Path(__file__).resolve().parent.parent / "UPSC"
MANIFEST_PATH = Path(__file__).resolve().parent.parent / "ingestion_manifest.json"


def load_manifest() -> Dict[str, Any]:
    """Load the ingestion manifest tracking processed files and timestamps."""
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"ingested_subjects": {}, "last_updated": None}


def save_manifest(manifest_data: Dict[str, Any]):
    """Save updated manifest."""
    manifest_data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write manifest: {e}")


def extract_pages_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page from PDF using PyMuPDF.
    Returns list of dicts: [{"page_number": 1, "text": "..."}]
    """
    pages = []
    if not pdf_path.is_file():
        return pages

    doc = fitz.open(str(pdf_path))
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        text = page.get_text("text")
        pages.append({
            "page_number": page_idx + 1,
            "text": text
        })
    doc.close()
    return pages


def ingest_subject_documents(
    subject: str,
    delete_after_ingest: bool = False
) -> Dict[str, Any]:
    """
    Ingest all PDFs for a UPSC subject:
    1. Study Material folder
    2. Previous Year Questions folder
    3. Verify storage & retrieval before deleting any source PDFs.
    """
    subj_dir = UPSC_ROOT / subject
    if not subj_dir.is_dir():
        return {"status": "error", "message": f"Subject directory not found: {subject}"}

    study_dir = subj_dir / "study_material"
    pyq_dir = subj_dir / "previous_year_questions"
    study_dir.mkdir(parents=True, exist_ok=True)
    pyq_dir.mkdir(parents=True, exist_ok=True)

    study_pdfs = list(study_dir.glob("*.pdf"))
    pyq_pdfs = list(pyq_dir.glob("*.pdf"))

    total_pdfs_found = len(study_pdfs) + len(pyq_pdfs)
    if total_pdfs_found == 0:
        # Check if already ingested previously in manifest
        manifest = load_manifest()
        if subject in manifest.get("ingested_subjects", {}):
            prev = manifest["ingested_subjects"][subject]
            return {
                "status": "already_indexed",
                "subject": subject,
                "message": "Subject is already indexed in Vector DB.",
                "total_chunks": prev.get("total_chunks", 0),
                "last_ingested": prev.get("ingested_at")
            }
        return {
            "status": "warning",
            "subject": subject,
            "message": "No new PDFs found in study_material or previous_year_questions."
        }

    all_chunks = []
    processed_files = []
    failed_files = []

    # 1. Process Study Material PDFs
    for pdf_path in study_pdfs:
        try:
            pages = extract_pages_from_pdf(pdf_path)
            meta_base = {
                "exam": "UPSC",
                "subject": subject,
                "source_type": "study_material",
                "document_name": pdf_path.name
            }
            chunks = chunk_document(pages, chunk_size=500, chunk_overlap=80, metadata_base=meta_base)
            all_chunks.extend(chunks)
            processed_files.append({"file": pdf_path, "type": "study_material", "chunks": len(chunks)})
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            failed_files.append({"file": str(pdf_path), "error": str(e)})

    # 2. Process PYQ PDFs
    for pdf_path in pyq_pdfs:
        try:
            pages = extract_pages_from_pdf(pdf_path)
            # Try to deduce year from filename
            year = 2024
            for yr in [2024, 2023, 2022, 2021, 2020]:
                if str(yr) in pdf_path.name:
                    year = yr
                    break

            meta_base = {
                "exam": "UPSC",
                "subject": subject,
                "source_type": "previous_year_questions",
                "document_name": pdf_path.name,
                "year": year
            }
            chunks = chunk_document(pages, chunk_size=400, chunk_overlap=60, metadata_base=meta_base)
            all_chunks.extend(chunks)
            processed_files.append({"file": pdf_path, "type": "previous_year_questions", "chunks": len(chunks)})
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            failed_files.append({"file": str(pdf_path), "error": str(e)})

    if not all_chunks:
        return {
            "status": "error",
            "subject": subject,
            "message": "No content could be extracted from PDFs.",
            "failed_files": failed_files
        }

    # 3. Store in Vector Database
    stored_count = add_chunks_to_vector_store(all_chunks)

    # 4. Rigorous Ingestion Verification (Step 7, 8, 9)
    verification_success = False
    try:
        sample_query = "UPSC Prelims Question Concept"
        test_search = query_vector_store(query_text=sample_query, subject=subject, n_results=1)
        if test_search and len(test_search) > 0 and stored_count > 0:
            verification_success = True
    except Exception as e:
        logger.error(f"Verification query failed for {subject}: {e}")
        verification_success = False

    # 5. Delete source PDFs ONLY IF verification succeeded AND flag is True
    deleted_files = []
    if verification_success and delete_after_ingest and not failed_files:
        for item in processed_files:
            file_obj: Path = item["file"]
            try:
                if file_obj.is_file():
                    file_obj.unlink()
                    deleted_files.append(file_obj.name)
            except Exception as e:
                logger.error(f"Could not delete {file_obj}: {e}")

    # 6. Update Manifest
    manifest = load_manifest()
    manifest["ingested_subjects"][subject] = {
        "subject": subject,
        "total_chunks": stored_count,
        "processed_files_count": len(processed_files),
        "failed_files_count": len(failed_files),
        "deleted_after_ingest": bool(deleted_files),
        "verified": verification_success,
        "ingested_at": datetime.utcnow().isoformat()
    }
    save_manifest(manifest)

    return {
        "status": "success" if verification_success else "partial",
        "subject": subject,
        "total_pdfs_found": total_pdfs_found,
        "processed_files": [f["file"].name for f in processed_files],
        "failed_files": failed_files,
        "total_chunks_stored": stored_count,
        "verified": verification_success,
        "source_pdfs_deleted": len(deleted_files) > 0,
        "deleted_files": deleted_files
    }


def ingest_all_upsc_subjects(delete_after_ingest: bool = False) -> Dict[str, Any]:
    """Ingest documents across all 8 UPSC subjects."""
    results = {}
    total_stored = 0
    for subj_id in UPSC_SUBJECTS.keys():
        res = ingest_subject_documents(subj_id, delete_after_ingest=delete_after_ingest)
        results[subj_id] = res
        total_stored += res.get("total_chunks_stored", 0)

    return {
        "status": "completed",
        "total_chunks_indexed": total_stored,
        "subjects": results
    }

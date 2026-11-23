"""
Django API Routes for UPSC Subject-Wise AI Test Series.
"""
import json
import asyncio
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest, Http404
from django.views.decorators.csrf import csrf_exempt

from test_series.models import UPSC_SUBJECTS
from test_series.admin_config import (
    load_admin_config,
    save_admin_config,
    verify_admin_credentials,
)
from test_series.services.vector_store_service import get_subject_stats, clear_subject_chunks
from test_series.services.pdf_ingestion_service import (
    load_manifest,
    ingest_subject_documents,
    ingest_all_upsc_subjects,
    UPSC_ROOT
)
from test_series.services.test_session_service import (
    start_test_session,
    get_or_generate_question,
    record_user_answer,
    submit_test_session,
    get_test_results,
    get_session,
    get_all_sessions_summary
)

ADMIN_COOKIE_NAME = "upsc_admin_auth"


def is_admin_authenticated(request) -> bool:
    """Check if request contains valid signed admin cookie."""
    try:
        val = request.get_signed_cookie(ADMIN_COOKIE_NAME)
        return val == "admin_1112"
    except Exception:
        return False


def admin_login_view(request):
    """
    GET: Render admin login page.
    POST: Authenticate with username 'admin_1112' and password '1112'.
    """
    if is_admin_authenticated(request):
        return redirect("/test-series/admin/")

    error_message = None
    if request.method == "POST":
        u = request.POST.get("username", "").strip()
        p = request.POST.get("password", "").strip()
        if verify_admin_credentials(u, p):
            next_url = request.GET.get("next") or "/test-series/admin/"
            resp = redirect(next_url)
            resp.set_signed_cookie(ADMIN_COOKIE_NAME, "admin_1112", max_age=86400 * 7, httponly=True)
            return resp
        else:
            error_message = "Invalid credentials. Please enter username 'admin_1112' and password '1112'."

    return render(request, "research_ui/admin_login.html", {"error": error_message})


def admin_logout_view(request):
    """Log out admin by clearing signed cookie."""
    resp = redirect("/test-series/admin/login/")
    resp.delete_cookie(ADMIN_COOKIE_NAME)
    return resp


def admin_dashboard_view(request):
    """
    GET /test-series/admin/
    Renders Admin Panel for managing PDF ingestion, vector store, and section MCQ counts.
    Protected: Requires admin login.
    """
    if not is_admin_authenticated(request):
        return redirect(f"/test-series/admin/login/?next={request.path}")

    cfg = load_admin_config()
    stats = get_subject_stats()
    manifest = load_manifest()
    sessions = get_all_sessions_summary()

    context = {
        "config": cfg,
        "subjects": UPSC_SUBJECTS,
        "stats": stats,
        "manifest": manifest,
        "sessions": sessions,
    }
    return render(request, "research_ui/admin_dashboard.html", context)


def get_config_api(request):
    """GET /api/test-series/config/ - returns public test configuration for candidates & admin."""
    cfg = load_admin_config()
    return JsonResponse({
        "status": "success",
        "config": cfg,
        "default_question_count": cfg.get("default_question_count", 10),
        "available_question_counts": cfg.get("available_question_counts", [5, 10, 15, 20, 25, 30, 50]),
        "max_questions_per_test": cfg.get("max_questions_per_test", 50),
        "upsc_marks_per_correct": cfg.get("upsc_marks_per_correct", 2.0),
        "upsc_negative_penalty": cfg.get("upsc_negative_penalty", 0.66),
        "passing_percentage": cfg.get("passing_percentage", 60.0),
        "subject_mcq_limits": cfg.get("subject_mcq_limits", {}),
        "questions_per_section": cfg.get("questions_per_section", {})
    })


@csrf_exempt
def update_config_api(request):
    """
    POST /api/test-series/admin/config/update/
    Protected API to update MCQ counts, limits, and section allocations.
    """
    if not is_admin_authenticated(request):
        return JsonResponse({"status": "error", "message": "Unauthorized. Admin login required."}, status=401)

    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    updated = save_admin_config(body)
    return JsonResponse({"status": "success", "message": "Configuration updated successfully", "config": updated})


@csrf_exempt
def upload_pdf_api(request):
    """
    POST /api/test-series/admin/upload-pdf/
    Multipart form-data: subject, category ('study_material' or 'previous_year_questions'), file
    Saves PDF file directly to target subject folder and optionally auto-ingests.
    """
    if not is_admin_authenticated(request):
        return JsonResponse({"status": "error", "message": "Unauthorized. Admin login required."}, status=401)

    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    subject = request.POST.get("subject")
    category = request.POST.get("category", "study_material")
    uploaded_file = request.FILES.get("file")

    if not subject or subject not in UPSC_SUBJECTS:
        return JsonResponse({"status": "error", "message": f"Invalid subject: '{subject}'"}, status=400)

    if category not in ["study_material", "previous_year_questions"]:
        return JsonResponse({"status": "error", "message": "Invalid category. Must be 'study_material' or 'previous_year_questions'"}, status=400)

    if not uploaded_file or not uploaded_file.name.lower().endswith(".pdf"):
        return JsonResponse({"status": "error", "message": "Only PDF files are supported"}, status=400)

    target_dir = UPSC_ROOT / subject / category
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / uploaded_file.name

    try:
        with open(target_path, "wb+") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"File save failed: {e}"}, status=500)

    auto_ingest = request.POST.get("auto_ingest", "false").lower() == "true"
    ingest_result = None
    if auto_ingest:
        ingest_result = ingest_subject_documents(subject, delete_after_ingest=False)

    return JsonResponse({
        "status": "success",
        "filename": uploaded_file.name,
        "subject": subject,
        "category": category,
        "saved_path": str(target_path.relative_to(UPSC_ROOT.parent)),
        "auto_ingested": auto_ingest,
        "ingest_result": ingest_result
    })


@csrf_exempt
def clear_subject_api(request):
    """
    POST /api/test-series/admin/clear-subject/
    Payload: {"subject": "<subject_id>"}
    Clears vector store chunks for a subject.
    """
    if not is_admin_authenticated(request):
        return JsonResponse({"status": "error", "message": "Unauthorized. Admin login required."}, status=401)

    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    subject = body.get("subject")
    if not subject or subject not in UPSC_SUBJECTS:
        return JsonResponse({"status": "error", "message": "Invalid subject"}, status=400)

    clear_subject_chunks(subject)
    return JsonResponse({"status": "success", "message": f"Cleared vector index for {subject}"})


def get_admin_sessions_api(request):
    """GET /api/test-series/admin/sessions/ - returns all candidate test sessions."""
    if not is_admin_authenticated(request):
        return JsonResponse({"status": "error", "message": "Unauthorized. Admin login required."}, status=401)
    sessions = get_all_sessions_summary()
    return JsonResponse({"status": "success", "sessions": sessions})



def get_subjects_api(request):
    """
    GET /api/test-series/upsc/subjects/
    Returns list of UPSC subjects with metadata, topics, and indexed status.
    """
    stats = get_subject_stats().get("subjects", {})
    manifest = load_manifest().get("ingested_subjects", {})

    subjects_list = []
    for sid, sinfo in UPSC_SUBJECTS.items():
        sub_stat = stats.get(sid, {})
        man_stat = manifest.get(sid, {})
        
        is_indexed = (sub_stat.get("total_chunks", 0) > 0) or man_stat.get("verified", False)
        
        subjects_list.append({
            "id": sid,
            "display_name": sinfo["display_name"],
            "icon": sinfo["icon"],
            "color": sinfo["color"],
            "description": sinfo["description"],
            "topics": sinfo["topics"],
            "is_indexed": is_indexed,
            "total_chunks": sub_stat.get("total_chunks", man_stat.get("total_chunks", 0)),
            "study_material_chunks": sub_stat.get("study_material_chunks", 0),
            "pyq_chunks": sub_stat.get("pyq_chunks", 0),
            "documents_indexed": sub_stat.get("document_count", man_stat.get("processed_files_count", 0)),
            "last_ingested": man_stat.get("ingested_at")
        })

    return JsonResponse({
        "status": "success",
        "exam": "UPSC",
        "category": "Civil Services Examination (CSE)",
        "subjects": subjects_list
    })


def get_subject_detail_api(request, subject):
    """
    GET /api/test-series/upsc/<subject>/
    Returns single subject details, study materials, topics, and ingestion status.
    """
    if subject not in UPSC_SUBJECTS:
        return JsonResponse({"status": "error", "message": f"Subject '{subject}' not found"}, status=404)

    sinfo = UPSC_SUBJECTS[subject]
    stats = get_subject_stats().get("subjects", {}).get(subject, {})
    manifest = load_manifest().get("ingested_subjects", {}).get(subject, {})

    return JsonResponse({
        "status": "success",
        "subject": {
            "id": subject,
            "display_name": sinfo["display_name"],
            "icon": sinfo["icon"],
            "color": sinfo["color"],
            "description": sinfo["description"],
            "topics": sinfo["topics"],
            "total_chunks": stats.get("total_chunks", manifest.get("total_chunks", 0)),
            "documents": stats.get("documents", []),
            "verified": manifest.get("verified", True)
        }
    })


@csrf_exempt
def start_test_api(request, subject):
    """
    POST /api/test-series/upsc/<subject>/start/
    Payload: {"user_id": ..., "difficulty": "Medium", "total_questions": 5, "topic": ...}
    Starts a new session and dynamically returns Question #1 (without correct answer).
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    if subject not in UPSC_SUBJECTS:
        return JsonResponse({"status": "error", "message": f"Invalid subject '{subject}'"}, status=400)

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    user_id = body.get("user_id", "candidate_1")
    difficulty = body.get("difficulty", "Medium")
    total_q = int(body.get("total_questions", 5))
    topic = body.get("topic")

    try:
        result = asyncio.run(start_test_session(
            user_id=user_id,
            subject=subject,
            difficulty=difficulty,
            total_questions=total_q,
            topic=topic
        ))
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def get_question_api(request, session_id, q_index):
    """
    GET /api/test-series/session/<session_id>/question/<q_index>/
    Returns question at index q_index (sanitized, no answers!). Dynamically generates if needed.
    """
    try:
        q_idx = int(q_index)
        result = asyncio.run(get_or_generate_question(session_id, q_idx))
        status_code = 200 if result.get("status") == "success" else 400
        return JsonResponse(result, status=status_code)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def next_question_api(request, session_id):
    """
    POST /api/test-series/session/<session_id>/next-question/
    Payload: {"current_index": 0} -> loads or generates question at current_index + 1
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    current_idx = int(body.get("current_index", 0))
    target_idx = current_idx + 1

    try:
        result = asyncio.run(get_or_generate_question(session_id, target_idx))
        status_code = 200 if result.get("status") == "success" else 400
        return JsonResponse(result, status=status_code)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def record_answer_api(request, session_id):
    """
    POST /api/test-series/session/<session_id>/answer/
    Payload: {"question_index": 0, "selected_option": "B"}
    Saves user's choice before submission.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    q_idx = body.get("question_index")
    opt = body.get("selected_option")

    if q_idx is None:
        return JsonResponse({"status": "error", "message": "question_index is required"}, status=400)

    result = record_user_answer(session_id, int(q_idx), opt)
    status_code = 200 if result.get("status") == "success" else 400
    return JsonResponse(result, status=status_code)


@csrf_exempt
def submit_test_api(request, session_id):
    """
    POST /api/test-series/session/<session_id>/submit/
    Payload: {"time_taken_seconds": 340}
    Evaluates test, calculates score, and returns full question-by-question review!
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    time_taken = body.get("time_taken_seconds")
    result = submit_test_session(session_id, time_taken_seconds=time_taken)
    status_code = 200 if result.get("status") == "success" else 400
    return JsonResponse(result, status=status_code)


def get_results_api(request, session_id):
    """
    GET /api/test-series/session/<session_id>/results/
    Returns full test scorecard and question review.
    """
    result = get_test_results(session_id)
    status_code = 200 if result.get("status") == "success" else 400
    return JsonResponse(result, status=status_code)


def get_ingest_status_api(request):
    """
    GET /api/test-series/ingest/status/
    Returns vector store statistics, total chunks, and manifest details.
    """
    manifest = load_manifest()
    stats = get_subject_stats()
    return JsonResponse({
        "status": "success",
        "manifest": manifest,
        "vector_store": stats
    })


@csrf_exempt
def trigger_ingest_api(request):
    """
    POST /api/test-series/ingest/run/
    Payload: {"subject": "all" | "<subject_id>", "delete_after_ingest": true | false}
    Executes ingestion pipeline with verification and optional source PDF deletion.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = {}

    target = body.get("subject", "all")
    delete_after = bool(body.get("delete_after_ingest", False))

    if target == "all":
        result = ingest_all_upsc_subjects(delete_after_ingest=delete_after)
    else:
        result = ingest_subject_documents(target, delete_after_ingest=delete_after)

    return JsonResponse(result)

"""
Test Session Management Service.
Handles session state, answer tracking, secure answer hiding, and dynamic question streaming.
"""
import json
import uuid
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from test_series.models import TestSession, MCQQuestion, UPSC_SUBJECTS
from test_series.services.mcq_generation_service import generate_upsc_mcq
from test_series.services.evaluation_service import evaluate_test_session

SESSIONS_FILE = Path(__file__).resolve().parent.parent / "sessions.json"

# In-memory sessions cache for instant response
_active_sessions: Dict[str, TestSession] = {}


def _save_sessions_to_disk():
    """Persist active sessions to disk."""
    try:
        data = {}
        for sid, sess in _active_sessions.items():
            # Include questions with correct answers on disk
            data[sid] = {
                "session_id": sess.session_id,
                "user_id": sess.user_id,
                "exam": sess.exam,
                "subject": sess.subject,
                "difficulty": sess.difficulty,
                "total_questions": sess.total_questions,
                "topic": sess.topic,
                "topic_order": getattr(sess, "topic_order", []),
                "user_answers": sess.user_answers,
                "status": sess.status,
                "created_at": sess.created_at,
                "submitted_at": sess.submitted_at,
                "time_taken_seconds": sess.time_taken_seconds,
                "evaluation": sess.evaluation,
                "questions": [q.to_dict(include_answer=True) for q in sess.questions]
            }
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        pass


def _load_sessions_from_disk():
    """Load persistent sessions from disk."""
    global _active_sessions
    if not SESSIONS_FILE.exists():
        return
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for sid, d in data.items():
            q_objs = []
            for q_data in d.get("questions", []):
                q_objs.append(MCQQuestion(
                    question_id=q_data["question_id"],
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data.get("correct_answer", "A"),
                    explanation=q_data.get("explanation", ""),
                    topic=q_data.get("topic", ""),
                    difficulty=q_data.get("difficulty", "Medium"),
                    source_references=q_data.get("source_references", []),
                    pyq_pattern_used=q_data.get("pyq_pattern_used", "UPSC Statement Based")
                ))
            sess = TestSession(
                session_id=d["session_id"],
                user_id=d.get("user_id", "default"),
                exam=d.get("exam", "UPSC"),
                subject=d["subject"],
                difficulty=d.get("difficulty", "Medium"),
                total_questions=d.get("total_questions", 5),
                topic=d.get("topic"),
                topic_order=d.get("topic_order", []),
                questions=q_objs,
                user_answers={int(k): v for k, v in d.get("user_answers", {}).items()},
                status=d.get("status", "active"),
                created_at=d.get("created_at"),
                submitted_at=d.get("submitted_at"),
                time_taken_seconds=d.get("time_taken_seconds"),
                evaluation=d.get("evaluation")
            )
            _active_sessions[sid] = sess
    except Exception:
        pass

# Initialize from disk
_load_sessions_from_disk()


async def start_test_session(
    user_id: str,
    subject: str,
    difficulty: str = "Medium",
    total_questions: int = 5,
    topic: Optional[str] = None,
    exam: str = "UPSC"
) -> Dict[str, Any]:
    """
    Start a new test session and dynamically generate the first randomized question.
    """
    exam_clean = (exam or "UPSC").replace(" ", "_")
    session_id = f"{exam_clean.lower()}_{uuid.uuid4().hex[:10]}"

    # Setup randomized topic ordering per test session
    subj_info = UPSC_SUBJECTS.get(subject, {})
    all_subj_topics = list(subj_info.get("topics", [subject.replace("_", " ")]))
    random.shuffle(all_subj_topics)
    topic_order = [topic] if topic else all_subj_topics
    first_topic = topic_order[0]
    
    session = TestSession(
        session_id=session_id,
        user_id=user_id,
        exam=exam or "UPSC",
        subject=subject,
        difficulty=difficulty,
        total_questions=total_questions,
        topic=topic,
        topic_order=topic_order,
        questions=[],
        user_answers={},
        status="active"
    )

    # Dynamically generate Question #1 via RAG pipeline
    q1 = await generate_upsc_mcq(
        subject=subject,
        topic=first_topic,
        difficulty=difficulty,
        previous_questions=[],
        q_index=0
    )
    session.questions.append(q1)

    _active_sessions[session_id] = session
    _save_sessions_to_disk()

    # SECURE RESPONSE: Return question without correct answer or explanation
    return {
        "status": "success",
        "session_id": session_id,
        "exam": session.exam,
        "subject": subject,
        "subject_name": UPSC_SUBJECTS.get(subject, {}).get("display_name", subject),
        "total_questions": total_questions,
        "current_index": 0,
        "question": q1.to_dict(include_answer=False),
        "user_answer": None
    }


def get_session(session_id: str) -> Optional[TestSession]:
    """Retrieve an active or completed session."""
    return _active_sessions.get(session_id)


async def get_or_generate_question(session_id: str, q_index: int) -> Dict[str, Any]:
    """
    Get question at q_index. If it hasn't been generated yet, dynamically generate via RAG.
    CRITICAL: Strips correct_answer and explanation for ongoing tests!
    """
    session = get_session(session_id)
    if not session:
        return {"status": "error", "message": "Test session not found."}

    if q_index >= session.total_questions:
        return {"status": "error", "message": "Question index exceeds total questions."}

    # If question already generated, return sanitized
    if q_index < len(session.questions):
        q = session.questions[q_index]
        user_ans = session.user_answers.get(q_index)
        return {
            "status": "success",
            "session_id": session_id,
            "current_index": q_index,
            "total_questions": session.total_questions,
            "question": q.to_dict(include_answer=False),
            "user_answer": user_ans,
            "is_last_question": (q_index == session.total_questions - 1)
        }

    # Dynamically generate questions sequentially up to q_index
    while len(session.questions) <= q_index and len(session.questions) < session.total_questions:
        curr_idx = len(session.questions)
        prev_stems = [item.question for item in session.questions]
        topics = session.topic_order if getattr(session, "topic_order", None) else [session.topic or session.subject.replace("_", " ")]
        target_topic = session.topic if session.topic else topics[curr_idx % len(topics)]
        new_q = await generate_upsc_mcq(
            subject=session.subject,
            topic=target_topic,
            difficulty=session.difficulty,
            previous_questions=prev_stems,
            q_index=curr_idx
        )
        session.questions.append(new_q)

    _save_sessions_to_disk()

    q = session.questions[q_index]
    user_ans = session.user_answers.get(q_index)
    return {
        "status": "success",
        "session_id": session_id,
        "current_index": q_index,
        "total_questions": session.total_questions,
        "question": q.to_dict(include_answer=False),
        "user_answer": user_ans,
        "is_last_question": (q_index == session.total_questions - 1)
    }


def record_user_answer(session_id: str, q_index: int, selected_option: Optional[str]) -> Dict[str, Any]:
    """Save or update user's answer for question at q_index."""
    session = get_session(session_id)
    if not session:
        return {"status": "error", "message": "Session not found."}

    if session.status != "active":
        return {"status": "error", "message": "Cannot modify answers for a submitted test."}

    if selected_option:
        session.user_answers[int(q_index)] = selected_option.upper().strip()
    else:
        session.user_answers.pop(int(q_index), None)

    _save_sessions_to_disk()
    return {
        "status": "success",
        "question_index": q_index,
        "saved_answer": session.user_answers.get(int(q_index)),
        "attempted_count": len(session.user_answers)
    }


def submit_test_session(session_id: str, time_taken_seconds: Optional[int] = None) -> Dict[str, Any]:
    """
    Submit test, lock answers, calculate scores, and unlock full review.
    """
    session = get_session(session_id)
    if not session:
        return {"status": "error", "message": "Session not found."}

    session.status = "submitted"
    session.submitted_at = datetime.utcnow().isoformat()
    if time_taken_seconds:
        session.time_taken_seconds = time_taken_seconds

    # Run evaluation
    evaluation = evaluate_test_session(session)
    session.evaluation = evaluation
    _save_sessions_to_disk()

    return {
        "status": "success",
        "session_id": session_id,
        "subject": session.subject,
        "evaluation": evaluation
    }


def get_test_results(session_id: str) -> Dict[str, Any]:
    """Retrieve evaluated results and review for a submitted test."""
    session = get_session(session_id)
    if not session:
        return {"status": "error", "message": "Session not found."}

    if session.status != "submitted" or not session.evaluation:
        # Evaluate now if not already evaluated
        session.evaluation = evaluate_test_session(session)
        session.status = "submitted"
        _save_sessions_to_disk()

    return {
        "status": "success",
        "session_id": session_id,
        "subject": session.subject,
        "subject_name": UPSC_SUBJECTS.get(session.subject, {}).get("display_name", session.subject),
        "difficulty": session.difficulty,
        "created_at": session.created_at,
        "submitted_at": session.submitted_at,
        "time_taken_seconds": session.time_taken_seconds,
        "evaluation": session.evaluation
    }


def get_all_sessions_summary() -> list:
    """Return a summary of all test sessions for the admin dashboard."""
    _load_sessions_from_disk()
    summary = []
    for sid, sess in _active_sessions.items():
        summary.append({
            "session_id": sid,
            "user_id": sess.user_id,
            "subject": sess.subject,
            "subject_name": UPSC_SUBJECTS.get(sess.subject, {}).get("display_name", sess.subject),
            "difficulty": sess.difficulty,
            "total_questions": sess.total_questions,
            "attempted_count": len(sess.user_answers),
            "status": sess.status,
            "created_at": sess.created_at,
            "submitted_at": sess.submitted_at,
            "score_percentage": sess.evaluation.get("score_percentage") if sess.evaluation else None,
            "upsc_marks": sess.evaluation.get("upsc_marks") if sess.evaluation else None,
        })
    summary.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return summary


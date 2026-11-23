"""
Evaluation Service for UPSC Test Series:
Computes UPSC Prelims scoring (+2 / -0.66), accuracy, topic breakdown, and comprehensive answer review.
"""
from typing import List, Dict, Any
from test_series.models import TestSession, MCQQuestion

def evaluate_test_session(session: TestSession) -> Dict[str, Any]:
    """
    Evaluate user's answers against the hidden correct answers in the session.
    """
    total_q = len(session.questions)
    attempted = 0
    correct = 0
    incorrect = 0
    unattempted = 0

    topic_stats = {}
    review_list = []

    for i, q in enumerate(session.questions):
        user_choice = session.user_answers.get(i) or session.user_answers.get(str(i))
        correct_choice = q.correct_answer.upper().strip()
        topic = q.topic or "General"

        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "correct": 0, "incorrect": 0}
        topic_stats[topic]["total"] += 1

        is_correct = False
        is_attempted = bool(user_choice)

        if is_attempted:
            attempted += 1
            if user_choice.upper().strip() == correct_choice:
                correct += 1
                is_correct = True
                topic_stats[topic]["correct"] += 1
            else:
                incorrect += 1
                topic_stats[topic]["incorrect"] += 1
        else:
            unattempted += 1

        review_item = {
            "question_index": i,
            "question_id": q.question_id,
            "question": q.question,
            "options": q.options,
            "user_answer": user_choice,
            "correct_answer": correct_choice,
            "is_correct": is_correct,
            "is_attempted": is_attempted,
            "explanation": q.explanation,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "source_references": q.source_references,
            "pyq_pattern": q.pyq_pattern_used
        }
        review_list.append(review_item)

    # UPSC CSE Prelims Standard Marking from Admin Configuration
    from test_series.admin_config import load_admin_config
    cfg = load_admin_config()
    mark_correct = float(cfg.get("upsc_marks_per_correct", 2.0))
    mark_negative = float(cfg.get("upsc_negative_penalty", 0.66))
    pass_pct = float(cfg.get("passing_percentage", 60.0))

    raw_upsc_score = round((correct * mark_correct) - (incorrect * mark_negative), 2)
    max_marks = round(total_q * mark_correct, 2)
    accuracy = round((correct / max(attempted, 1)) * 100, 1) if attempted > 0 else 0.0
    percentage = round((correct / max(total_q, 1)) * 100, 1)

    return {
        "total_questions": total_q,
        "attempted_questions": attempted,
        "correct_answers": correct,
        "incorrect_answers": incorrect,
        "unattempted_questions": unattempted,
        "accuracy_percentage": accuracy,
        "score_percentage": percentage,
        "upsc_marks": raw_upsc_score,
        "max_marks": max_marks,
        "status": "Qualified" if percentage >= pass_pct else "Needs Revision",
        "topic_breakdown": topic_stats,
        "review": review_list
    }

"""
Admin Configuration for UPSC Test Series:
Manages global MCQ counts, section allocations, passing criteria, and credentials.
"""
import json
from pathlib import Path
from typing import Dict, Any, List

CONFIG_FILE = Path(__file__).resolve().parent / "admin_config.json"

DEFAULT_CONFIG = {
    "admin_username": "admin_1112",
    "admin_password": "1112",
    "default_question_count": 10,
    "available_question_counts": [5, 10, 15, 20, 25, 30, 50],
    "max_questions_per_test": 50,
    "upsc_marks_per_correct": 2.0,
    "upsc_negative_penalty": 0.66,
    "passing_percentage": 60.0,
    "time_per_question_seconds": 120,
    "allow_dynamic_rag_fallback": True,
    "subject_mcq_limits": {
        "Indian_Polity": {"max_questions": 50, "default_questions": 10},
        "History": {"max_questions": 50, "default_questions": 10},
        "Geography": {"max_questions": 50, "default_questions": 10},
        "Economy": {"max_questions": 50, "default_questions": 10},
        "Environment": {"max_questions": 50, "default_questions": 10},
        "Science_and_Technology": {"max_questions": 50, "default_questions": 10},
        "Art_and_Culture": {"max_questions": 50, "default_questions": 10},
        "Ethics": {"max_questions": 50, "default_questions": 10}
    }
}


def load_admin_config() -> Dict[str, Any]:
    """Load config from disk or return default."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge defaults for any missing keys
                cfg = dict(DEFAULT_CONFIG)
                cfg.update(data)
                return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_admin_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Save config to disk."""
    cfg = load_admin_config()
    cfg.update(new_config)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print("[ADMIN CONFIG] Failed to save config:", e)
    return cfg


def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin login credentials (admin_1112 / 1112)."""
    cfg = load_admin_config()
    return (
        username.strip() == cfg.get("admin_username", "admin_1112") and
        password.strip() == cfg.get("admin_password", "1112")
    )

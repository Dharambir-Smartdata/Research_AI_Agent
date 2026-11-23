"""
Pydantic Schemas for API requests and responses in UPSC Test Series.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class StartTestRequest(BaseModel):
    user_id: Optional[str] = "candidate_default"
    exam: Optional[str] = "UPSC"
    subject: str
    difficulty: Optional[str] = "Medium"  # "Easy", "Medium", "Hard", "Mixed"
    total_questions: Optional[int] = Field(default=5, ge=1, le=50)
    topic: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    question_index: int = Field(ge=0)
    selected_option: Optional[str] = None  # "A", "B", "C", "D" or empty to clear

class NextQuestionRequest(BaseModel):
    current_index: Optional[int] = 0

class IngestSubjectRequest(BaseModel):
    subject: Optional[str] = "all"
    delete_after_ingest: Optional[bool] = True

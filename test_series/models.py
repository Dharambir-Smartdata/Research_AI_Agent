"""
Data models and constants for UPSC Test Series with RAG.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

# UPSC Subject Definitions
UPSC_SUBJECTS = {
    "Indian_Polity": {
        "id": "Indian_Polity",
        "display_name": "Indian Polity & Governance",
        "icon": "⚖️",
        "color": "indigo",
        "description": "Constitution, Preamble, Fundamental Rights, Parliament, Judiciary, Federalism, and Governance mechanisms.",
        "topics": ["Constitutional Framework", "Fundamental Rights", "Directive Principles", "Parliament of India", "Judicial Architecture", "Constitutional Bodies"]
    },
    "History": {
        "id": "History",
        "display_name": "History of India & National Movement",
        "icon": "🏛️",
        "color": "amber",
        "description": "Ancient India, Indus Valley, Mauryas, Guptas, Medieval Sultanates, Mughal Empire, and Modern Freedom Movement.",
        "topics": ["Indus Valley & Vedic Period", "Mauryan & Gupta Empires", "Delhi Sultanate & Mughals", "British Colonization & Drain of Wealth", "Gandhian Freedom Movements"]
    },
    "Geography": {
        "id": "Geography",
        "display_name": "Indian & World Geography",
        "icon": "🌍",
        "color": "cyan",
        "description": "Physical Geography, Geomorphology, Climatology, Monsoon dynamics, Drainage systems, Soils, and Mineral distribution.",
        "topics": ["Plate Tectonics & Continental Drift", "Atmospheric Circulation & Monsoons", "Himalayan & Peninsular Rivers", "Soil Classification & Agriculture", "Mineral Resources"]
    },
    "Economy": {
        "id": "Economy",
        "display_name": "Indian Economy & Development",
        "icon": "📈",
        "color": "emerald",
        "description": "Macroeconomics, National Accounting, Fiscal Policy, Inflation, RBI Monetary Policy, Banking reforms, and Trade.",
        "topics": ["National Income & GDP Measurement", "Fiscal Deficit & FRBM Architecture", "Monetary Policy Committee & RBI Tools", "Banking System & NPAs", "Foreign Trade & Balance of Payments"]
    },
    "Environment": {
        "id": "Environment",
        "display_name": "Environment & Ecology",
        "icon": "🌿",
        "color": "teal",
        "description": "Ecology principles, Biodiversity conservation, National Parks, Wildlife Protection Act, Climate Change treaties, and Ramsar sites.",
        "topics": ["Ecosystems & Biodiversity Hotspots", "Wildlife Protection Act & Protected Areas", "UNFCCC & Paris Agreement", "Ramsar Wetlands & Montreux Record", "Pollution Control & Renewable Energy"]
    },
    "Science_and_Technology": {
        "id": "Science_and_Technology",
        "display_name": "Science & Technology",
        "icon": "🔬",
        "color": "blue",
        "description": "Biotechnology, CRISPR gene editing, ISRO space missions, Artificial Intelligence, Quantum Computing, and Nanomaterials.",
        "topics": ["Biotechnology & Gene Editing", "ISRO Launch Vehicles & Lunar Missions", "Quantum Computing & National Quantum Mission", "Emerging Tech, AI & 5G/6G Networks", "Nanotechnology & Advanced Materials"]
    },
    "Art_and_Culture": {
        "id": "Art_and_Culture",
        "display_name": "Indian Art & Culture",
        "icon": "🎨",
        "color": "purple",
        "description": "Nagara/Dravida architecture, Rock-cut caves of Ajanta & Ellora, Classical dances, Classical music, and Miniature paintings.",
        "topics": ["Nagara, Dravida & Vesara Temple Architecture", "Ajanta, Ellora & Rock-Cut Caves", "Classical Dance Traditions of India", "Miniature Painting Schools", "UNESCO Tangible & Intangible Heritage"]
    },
    "Ethics": {
        "id": "Ethics",
        "display_name": "Ethics, Integrity & Aptitude",
        "icon": "🧭",
        "color": "rose",
        "description": "Ethics & Human Interface, Moral Thinkers, Emotional Intelligence, Nolan Principles of Public Life, and Probity in Governance.",
        "topics": ["Essence & Determinants of Ethics", "Utilitarianism vs Deontological Morality", "Emotional Intelligence in Civil Administration", "Nolan Principles & Conflict of Interest", "Probity in Governance & Whistleblowing"]
    }
}


@dataclass
class SourceReference:
    document: str
    page: int
    relevance_score: Optional[float] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class MCQQuestion:
    question_id: str
    question: str
    options: Dict[str, str]  # {"A": ..., "B": ..., "C": ..., "D": ...}
    correct_answer: str      # "A", "B", "C", or "D"
    explanation: str
    topic: str
    difficulty: str          # "Easy", "Medium", "Hard"
    source_references: List[Dict[str, Any]] = field(default_factory=list)
    pyq_pattern_used: str = "UPSC Statement Based"

    def to_dict(self, include_answer: bool = True) -> Dict[str, Any]:
        data = {
            "question_id": self.question_id,
            "question": self.question,
            "options": self.options,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "pyq_pattern_used": self.pyq_pattern_used,
        }
        if include_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"] = self.explanation
            data["source_references"] = self.source_references
        return data


@dataclass
class TestSession:
    session_id: str
    user_id: str
    exam: str  # "UPSC"
    subject: str
    difficulty: str  # "Easy", "Medium", "Hard", "Mixed"
    total_questions: int
    topic: Optional[str] = None
    questions: List[MCQQuestion] = field(default_factory=list)
    user_answers: Dict[int, str] = field(default_factory=dict)  # {0: "A", 1: "C"}
    status: str = "active"  # "active", "submitted", "abandoned"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    submitted_at: Optional[str] = None
    time_taken_seconds: Optional[int] = None
    evaluation: Optional[Dict[str, Any]] = None

    def to_dict(self, include_answers: bool = False) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "exam": self.exam,
            "subject": self.subject,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "topic": self.topic,
            "questions_count": len(self.questions),
            "questions": [q.to_dict(include_answer=include_answers) for q in self.questions],
            "user_answers": self.user_answers,
            "status": self.status,
            "created_at": self.created_at,
            "submitted_at": self.submitted_at,
            "time_taken_seconds": self.time_taken_seconds,
            "evaluation": self.evaluation,
        }

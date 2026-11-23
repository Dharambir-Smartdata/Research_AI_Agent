"""
PYQ Pattern Analysis Service for UPSC Civil Services Examination.
Extracts structural question patterns, phrasing templates, and option distributions from PYQs.
"""
from typing import List, Dict, Any
from test_series.services.vector_store_service import query_vector_store

# UPSC Question Templates & Patterns
UPSC_PATTERNS = [
    {
        "type": "Statement_Based_Multi",
        "description": "Consider the following statements... Which of the statements given above is/are correct?",
        "stem_template": "With reference to {topic}, consider the following statements:\n1. {statement_1}\n2. {statement_2}\n3. {statement_3}\nWhich of the statements given above is/are correct?",
        "option_format": ["1 only", "1 and 2 only", "2 and 3 only", "1, 2 and 3"]
    },
    {
        "type": "Pair_Matching",
        "description": "Consider the following pairs... How many of the pairs given above are correctly matched?",
        "stem_template": "Consider the following pairs:\n1. {item_1} : {desc_1}\n2. {item_2} : {desc_2}\n3. {item_3} : {desc_3}\nHow many of the pairs given above are correctly matched?",
        "option_format": ["Only one pair", "Only two pairs", "All three pairs", "None"]
    },
    {
        "type": "Conceptual_Direct",
        "description": "Which one of the following best describes the term / concept...?",
        "stem_template": "In the context of {topic}, which one of the following statements best reflects the principle of {concept}?",
        "option_format": ["Option A", "Option B", "Option C", "Option D"]
    },
    {
        "type": "Cause_and_Consequence",
        "description": "Which of the following are the likely consequences or determinants...?",
        "stem_template": "Regarding {topic}, which of the following factors directly influence {concept}?\n1. {factor_1}\n2. {factor_2}\nSelect the correct answer using the code given below:",
        "option_format": ["1 only", "2 only", "Both 1 and 2", "Neither 1 nor 2"]
    }
]


def extract_pyq_patterns_for_subject(subject: str) -> Dict[str, Any]:
    """
    Retrieve real PYQ chunks from the vector store for the subject and extract insights:
    - Sample question format
    - Elimination style options
    - Tone and difficulty guidelines
    """
    pyq_chunks = query_vector_store(
        query_text=f"UPSC Prelims Question Answer {subject}",
        subject=subject,
        source_type="previous_year_questions",
        n_results=3
    )

    pyq_samples = []
    for c in pyq_chunks:
        pyq_samples.append({
            "text": c.get("text", "")[:350],
            "document": c.get("document_name", ""),
            "page": c.get("page_number", 1)
        })

    return {
        "subject": subject,
        "supported_patterns": [p["type"] for p in UPSC_PATTERNS],
        "pattern_templates": UPSC_PATTERNS,
        "sample_pyq_excerpts": pyq_samples,
        "style_guidelines": [
            "Use formal, neutral UPSC phrasing: 'With reference to...', 'Consider the following statements...'",
            "Include statement-based questions with '1 only', '2 only', 'Both 1 and 2', 'Neither 1 nor 2' options",
            "Ensure distractors are plausible and test conceptual depth rather than trivial trivia",
            "Provide detailed rationales explaining why incorrect statements fail."
        ]
    }

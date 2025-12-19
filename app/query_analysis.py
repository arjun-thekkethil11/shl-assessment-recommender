# app/query_analysis.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class QueryProfile:
    text: str
    has_technical: bool
    has_behavioral: bool
    seniority: str  # "junior", "mid", "senior", "unknown"


TECH_KEYWORDS = [
    "java", "python", "c++", "c#", "javascript", "node", "react",
    "sql", "database", "kubernetes", "docker", "cloud", "aws", "azure",
    "data structures", "algorithms", "coding", "programming", "developer",
    "engineer", "qa", "selenium", "automation"
]

BEHAVIORAL_KEYWORDS = [
    "communication", "collaboration", "teamwork", "stakeholder",
    "leadership", "persuasion", "negotiation", "conflict", "adaptability",
    "resilience", "initiative", "ownership", "people skills"
]

JUNIOR_WORDS = ["junior", "entry level", "graduate"]
SENIOR_WORDS = ["senior", "lead", "principal", "head of"]


def analyze_query_rule_based(query: str) -> QueryProfile:
    q = query.lower()
    has_technical = any(k in q for k in TECH_KEYWORDS)
    has_behavioral = any(k in q for k in BEHAVIORAL_KEYWORDS)

    seniority = "unknown"
    if any(w in q for w in JUNIOR_WORDS):
        seniority = "junior"
    elif any(w in q for w in SENIOR_WORDS):
        seniority = "senior"
    else:
        seniority = "mid"

    return QueryProfile(
        text=query,
        has_technical=has_technical,
        has_behavioral=has_behavioral,
        seniority=seniority,
    )


# Stub for optional LLM-based analysis
def analyze_query_with_llm(query: str) -> QueryProfile:
    """
    Replace this stub with a call to an LLM if you want to strengthen the story.
    For now we just return the rule-based profile.
    """
    return analyze_query_rule_based(query)

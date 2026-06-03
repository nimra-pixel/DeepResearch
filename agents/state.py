"""
DeepResearch LangGraph State Schema
"""
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class Paper(TypedDict):
    title: str
    authors: list[str]
    year: int
    abstract: str
    source: str          # "pubmed" | "arxiv" | "semantic_scholar"
    url: str
    doi: Optional[str]
    citations: int
    keywords: list[str]
    cluster: Optional[str]


class ResearchGap(TypedDict):
    gap: str
    evidence: str
    opportunity: str
    priority: str        # "high" | "medium" | "low"


class ReviewSection(TypedDict):
    title: str
    content: str
    papers_cited: list[str]
    urdu_summary: Optional[str]


class DeepResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    session_id: str

    # Input
    topic: str
    language: str            # "english" | "bilingual"
    domain: str              # auto-detected
    max_papers: int

    # Search
    search_queries: list[str]
    raw_papers: list[Paper]
    filtered_papers: list[Paper]

    # Analysis
    clusters: dict           # {cluster_name: [paper_ids]}
    themes: list[str]
    research_gaps: list[ResearchGap]
    future_directions: list[str]
    citation_network: dict   # {paper_id: [cited_by_ids]}

    # Writing
    outline: list[str]
    sections: list[ReviewSection]
    abstract: str
    urdu_abstract: Optional[str]

    # Quality
    critic_score: float
    critic_feedback: str
    iteration: int

    # Output
    final_review: Optional[str]
    export_path: Optional[str]
    error: Optional[str]

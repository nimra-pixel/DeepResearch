"""
DeepResearch LangGraph Pipeline
START → search → analyze → write → critique → [revise loop | finalize] → END
"""
import uuid
from langgraph.graph import StateGraph, END
from agents.state import DeepResearchState
from agents.search_agent import search_agent
from agents.analyst_agent import analyst_agent
from agents.writer_agent import writer_agent
from agents.critic_agent import critic_agent, should_revise
from utils.config import get_settings


def build_graph():
    g = StateGraph(DeepResearchState)
    g.add_node("search", search_agent)
    g.add_node("analyze", analyst_agent)
    g.add_node("write", writer_agent)
    g.add_node("critique", critic_agent)

    g.set_entry_point("search")
    g.add_edge("search", "analyze")
    g.add_edge("analyze", "write")
    g.add_edge("write", "critique")
    g.add_conditional_edges("critique", should_revise, {
        "revise": "write",
        "finalize": END,
    })
    return g.compile()


deepresearch_graph = build_graph()


def run_deepresearch(
    topic: str,
    language: str = "english",
    max_papers: int = None,
    session_id: str = None,
) -> dict:
    s = get_settings()
    initial: DeepResearchState = {
        "messages": [],
        "session_id": session_id or uuid.uuid4().hex[:8],
        "topic": topic,
        "language": language,
        "domain": "",
        "max_papers": max_papers or s.MAX_PAPERS,
        "search_queries": [],
        "raw_papers": [],
        "filtered_papers": [],
        "clusters": {},
        "themes": [],
        "research_gaps": [],
        "future_directions": [],
        "citation_network": {},
        "outline": [],
        "sections": [],
        "abstract": "",
        "urdu_abstract": None,
        "critic_score": 0.0,
        "critic_feedback": "",
        "iteration": 0,
        "final_review": None,
        "export_path": None,
        "error": None,
    }
    return deepresearch_graph.invoke(initial)

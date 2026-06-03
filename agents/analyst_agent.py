"""
Analyst Agent — merged clustering + gap detection in ONE LLM call.
Saves ~1500 tokens vs separate calls.
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agents.state import DeepResearchState
from utils.llm import invoke_with_fallback

ANALYST_SYSTEM = """You are a systematic review expert. Analyze these paper abstracts.
Return ONLY valid JSON (no markdown fences):
{
  "clusters": {
    "Theme Name": ["0", "1", "3"]
  },
  "themes": ["theme1", "theme2", "theme3"],
  "research_gaps": [
    {
      "gap": "Gap description",
      "evidence": "Why this is a gap",
      "opportunity": "How to address it",
      "priority": "high"
    }
  ],
  "future_directions": ["direction1", "direction2", "direction3"]
}
Keep cluster names short (3 words max). List 3-5 clusters, 3-5 gaps, 3-5 directions."""


def analyst_agent(state: DeepResearchState) -> DeepResearchState:
    papers = state.get("filtered_papers", [])
    topic = state["topic"]

    if not papers:
        return {**state, "clusters": {}, "themes": [], "research_gaps": [],
                "future_directions": [], "citation_network": {}}

    # Compact paper summaries — 150 chars per abstract (saves tokens)
    summaries = []
    for i, p in enumerate(papers[:25]):
        summaries.append(
            f"[{i}] {p['title'][:80]} ({p['year']}, {p['source'].upper()}, "
            f"cited:{p.get('citations',0)})\n{p['abstract'][:150]}"
        )

    prompt = (
        f"Topic: {topic}\n"
        f"Domain: {state.get('domain', 'General')}\n\n"
        f"Papers:\n" + "\n\n".join(summaries) +
        "\n\nAnalyze and return JSON."
    )

    try:
        raw = invoke_with_fallback(
            [SystemMessage(content=ANALYST_SYSTEM), HumanMessage(content=prompt)],
            temperature=0.2, max_tokens=1500,
        )
        raw = re.sub(r'```(?:json)?|```', '', raw).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group() if match else raw)
        clusters = result.get("clusters", {})
        themes = result.get("themes", [topic])
        gaps = result.get("research_gaps", [])
        directions = result.get("future_directions", [])
    except Exception as e:
        print(f"[Analyst] Error: {e} — using defaults")
        clusters = {"General": [str(i) for i in range(min(len(papers), 5))]}
        themes = [topic]
        gaps = []
        directions = []

    # Tag papers with clusters
    updated = list(papers)
    for cname, indices in clusters.items():
        for idx_str in indices:
            try:
                idx = int(idx_str)
                if idx < len(updated):
                    updated[idx] = {**updated[idx], "cluster": cname}
            except (ValueError, TypeError):
                pass

    # Build keyword-overlap citation network
    network = {}
    for i, p in enumerate(updated[:20]):
        ki = set(k.lower() for k in p.get("keywords", []))
        related = [
            str(j) for j, q in enumerate(updated[:20])
            if j != i and len(ki & set(k.lower() for k in q.get("keywords", []))) >= 1
        ]
        if related:
            network[str(i)] = related[:4]

    print(f"[Analyst] Clusters:{len(clusters)} Gaps:{len(gaps)} Themes:{len(themes)}")
    return {
        **state,
        "filtered_papers": updated,
        "clusters": clusters,
        "themes": themes,
        "research_gaps": gaps,
        "future_directions": directions,
        "citation_network": network,
    }

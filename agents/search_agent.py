"""
Search Agent — 5-source robust fetcher
Sources: PubMed + ArXiv + Semantic Scholar + CrossRef + OpenAlex
All free, no API keys needed (except PubMed email)
"""
import json
import re
import concurrent.futures
from langchain_core.messages import HumanMessage, SystemMessage
from agents.state import DeepResearchState
from sources.pubmed import search_pubmed
from sources.arxiv import search_arxiv
from sources.semantic_scholar import search_semantic_scholar
from sources.crossref import search_crossref
from sources.openalex import search_openalex
from utils.llm import invoke_with_fallback

QUERY_SYSTEM = """You are a research librarian. Given a topic, generate 4 targeted search queries.
Return ONLY valid JSON (no markdown):
{
  "domain": "CS/AI | Medical | Engineering | Social Sciences | Interdisciplinary",
  "queries": ["query1", "query2", "query3", "query4"],
  "keywords": ["key1", "key2", "key3"]
}"""

SOURCES = {
    "pubmed":           search_pubmed,
    "arxiv":            search_arxiv,
    "semantic_scholar": search_semantic_scholar,
    "crossref":         search_crossref,
    "openalex":         search_openalex,
}


def _expand_queries(topic: str) -> tuple[list[str], str]:
    words = topic.strip().split()
    short = " ".join(words[:5]) if len(words) > 5 else topic
    fallback = [
        topic,
        short,
        f"{short} survey review",
        f"{short} machine learning",
    ]
    try:
        raw = invoke_with_fallback(
            [SystemMessage(content=QUERY_SYSTEM),
             HumanMessage(content=f"Research topic: {topic}")],
            temperature=0.1, max_tokens=400,
        )
        raw = re.sub(r'```(?:json)?|```', '', raw).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            queries = parsed.get("queries", fallback)
            domain = parsed.get("domain", "Interdisciplinary")
            if queries and len(queries) >= 2:
                print(f"[Search] LLM queries: {queries}")
                return queries, domain
    except Exception as e:
        print(f"[Search] LLM failed ({e}) — using fallback queries")
    return fallback, "Interdisciplinary"


def search_agent(state: DeepResearchState) -> DeepResearchState:
    topic = state["topic"]
    max_papers = state.get("max_papers", 30)
    per_source = max(8, max_papers // 4)

    queries, domain = _expand_queries(topic)
    print(f"[Search] {len(queries)} queries × {len(SOURCES)} sources × {per_source} per call")

    all_papers = []
    source_counts = {s: 0 for s in SOURCES}

    def fetch(name, fn, query, n):
        try:
            results = fn(query, n)
            print(f"[Search] {name:20s} | '{query[:35]}' → {len(results)} papers")
            return name, results
        except Exception as e:
            print(f"[Search] {name:20s} | ERROR: {e}")
            return name, []

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        futures = []
        for q in queries:
            for name, fn in SOURCES.items():
                futures.append(ex.submit(fetch, name, fn, q, per_source))
        for future in concurrent.futures.as_completed(futures):
            name, results = future.result()
            all_papers.extend(results)
            source_counts[name] += len(results)

    print(f"[Search] Totals: { {k:v for k,v in source_counts.items()} }")

    # Deduplicate by title
    seen, unique = set(), []
    for p in all_papers:
        key = p.get("title", "")[:60].lower().strip()
        if key and key not in seen and len(p.get("abstract", "")) > 50:
            seen.add(key)
            unique.append(p)

    # Sort by citations + recency
    unique.sort(
        key=lambda x: (x.get("citations", 0) * 0.4 + min(x.get("year", 2000), 2024) * 0.6),
        reverse=True
    )
    filtered = unique[:max_papers]

    print(f"[Search] {len(all_papers)} raw → {len(unique)} unique → {len(filtered)} final")

    if not filtered:
        print("[Search] WARNING: 0 papers from all 5 sources — check network connectivity")

    return {
        **state,
        "domain": domain,
        "search_queries": queries,
        "raw_papers": unique,
        "filtered_papers": filtered,
    }

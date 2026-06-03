"""Semantic Scholar source via free API"""
import requests
from utils.config import get_settings

SS_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,authors,year,abstract,citationCount,externalIds,fieldsOfStudy,url"


def search_semantic_scholar(query: str, max_results: int = 15) -> list[dict]:
    s = get_settings()
    headers = {}
    if s.SEMANTIC_SCHOLAR_API_KEY:
        headers["x-api-key"] = s.SEMANTIC_SCHOLAR_API_KEY
    try:
        r = requests.get(
            f"{SS_BASE}/paper/search",
            params={"query": query, "limit": max_results, "fields": FIELDS},
            headers=headers, timeout=15,
        )
        if r.status_code != 200:
            return []
        data = r.json().get("data", [])
        papers = []
        for p in data:
            if not p.get("title") or not p.get("abstract"):
                continue
            authors = [a.get("name", "") for a in p.get("authors", [])[:5]]
            ext = p.get("externalIds", {})
            doi = ext.get("DOI")
            url = p.get("url") or (f"https://doi.org/{doi}" if doi else "")
            papers.append({
                "title": p["title"],
                "authors": authors,
                "year": p.get("year") or 0,
                "abstract": p["abstract"][:600],
                "source": "semantic_scholar",
                "url": url,
                "doi": doi,
                "citations": p.get("citationCount") or 0,
                "keywords": p.get("fieldsOfStudy") or [],
                "cluster": None,
            })
        return papers
    except Exception as e:
        print(f"[SemanticScholar] Error: {e}")
        return []

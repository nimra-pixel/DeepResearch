"""CrossRef API — free, no key needed, works everywhere"""
import requests

CROSSREF_BASE = "https://api.crossref.org/works"


def search_crossref(query: str, max_results: int = 10) -> list[dict]:
    try:
        params = {
            "query": query,
            "rows": max_results,
            "select": "title,author,published,abstract,DOI,URL,is-referenced-by-count,subject",
            "sort": "relevance",
        }
        headers = {"User-Agent": "DeepResearch/1.0 (mailto:deepresearch@example.com)"}
        r = requests.get(CROSSREF_BASE, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        papers = []
        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else ""
            abstract = item.get("abstract", "")
            # Strip JATS XML tags from abstract
            import re
            abstract = re.sub(r'<[^>]+>', '', abstract).strip()
            if not title or len(abstract) < 30:
                continue
            authors = []
            for a in item.get("author", [])[:5]:
                name = f"{a.get('given','')} {a.get('family','')}".strip()
                if name:
                    authors.append(name)
            published = item.get("published", {})
            date_parts = published.get("date-parts", [[0]])
            year = date_parts[0][0] if date_parts and date_parts[0] else 0
            doi = item.get("DOI", "")
            url = item.get("URL", f"https://doi.org/{doi}" if doi else "")
            citations = item.get("is-referenced-by-count", 0)
            subjects = item.get("subject", [])
            papers.append({
                "title": title,
                "authors": authors,
                "year": int(year) if year else 0,
                "abstract": abstract[:600],
                "source": "crossref",
                "url": url,
                "doi": doi,
                "citations": citations,
                "keywords": subjects[:6],
                "cluster": None,
            })
        return papers
    except Exception as e:
        print(f"[CrossRef] Error: {e}")
        return []

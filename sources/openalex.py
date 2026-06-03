"""OpenAlex API — free, no key needed, 250M+ papers, best alternative to Google Scholar"""
import requests

OPENALEX_BASE = "https://api.openalex.org/works"


def search_openalex(query: str, max_results: int = 10) -> list[dict]:
    try:
        params = {
            "search": query,
            "per-page": max_results,
            "select": "title,authorships,publication_year,abstract_inverted_index,doi,cited_by_count,concepts,primary_location",
            "sort": "cited_by_count:desc",
            "mailto": "deepresearch@example.com",
        }
        r = requests.get(OPENALEX_BASE, params=params, timeout=20)
        r.raise_for_status()
        results = r.json().get("results", [])
        papers = []
        for item in results:
            title = item.get("title", "")
            if not title:
                continue
            # Reconstruct abstract from inverted index
            abstract = _reconstruct_abstract(item.get("abstract_inverted_index"))
            if len(abstract) < 30:
                continue
            authors = []
            for a in item.get("authorships", [])[:5]:
                author = a.get("author", {})
                name = author.get("display_name", "")
                if name:
                    authors.append(name)
            year = item.get("publication_year") or 0
            doi = item.get("doi", "")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi.replace("https://doi.org/", "")
            location = item.get("primary_location") or {}
            url = location.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else "")
            citations = item.get("cited_by_count", 0)
            concepts = [c.get("display_name", "") for c in item.get("concepts", [])[:6]]
            papers.append({
                "title": title,
                "authors": authors,
                "year": int(year),
                "abstract": abstract[:600],
                "source": "openalex",
                "url": url,
                "doi": doi,
                "citations": citations,
                "keywords": [c for c in concepts if c],
                "cluster": None,
            })
        return papers
    except Exception as e:
        print(f"[OpenAlex] Error: {e}")
        return []


def _reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    try:
        words = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(words[i] for i in sorted(words.keys()))
    except Exception:
        return ""

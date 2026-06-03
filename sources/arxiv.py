"""ArXiv source via public API"""
import xml.etree.ElementTree as ET
import requests

ARXIV_BASE = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv(query: str, max_results: int = 10) -> list[dict]:
    # Clean query for ArXiv
    clean_query = query.replace('"', '').replace("'", "")
    params = {
        "search_query": f"all:{clean_query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    try:
        r = requests.get(ARXIV_BASE, params=params, timeout=20)
        r.raise_for_status()
        return _parse_arxiv(r.content)
    except requests.exceptions.HTTPError as e:
        print(f"[ArXiv] HTTP error {e.response.status_code}: {e}")
        return []
    except Exception as e:
        print(f"[ArXiv] Error: {e}")
        return []


def _parse_arxiv(content: bytes) -> list[dict]:
    papers = []
    try:
        # Remove namespace declarations that cause issues
        content_str = content.decode("utf-8", errors="replace")
        content_str = content_str.replace('xmlns="http://www.w3.org/2005/Atom"', '')
        content_bytes = content_str.encode("utf-8")

        root = ET.fromstring(content_bytes)
        for entry in root.findall(".//entry"):
            title_el = entry.find("title")
            summary_el = entry.find("summary")
            id_el = entry.find("id")
            published_el = entry.find("published")

            title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""
            summary = summary_el.text.strip().replace("\n", " ") if summary_el is not None and summary_el.text else ""
            arxiv_id = id_el.text.strip().split("/")[-1] if id_el is not None and id_el.text else ""
            year = int(published_el.text[:4]) if published_el is not None and published_el.text else 0

            authors = []
            for author in entry.findall(".//author"):
                name_el = author.find("name")
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())
            authors = authors[:5]

            cats = [c.get("term", "") for c in entry.findall(".//category")]

            if title and summary and len(summary) > 50:
                papers.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "abstract": summary[:600],
                    "source": "arxiv",
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "doi": f"10.48550/arXiv.{arxiv_id}" if arxiv_id else None,
                    "citations": 0,
                    "keywords": [c for c in cats if c][:6],
                    "cluster": None,
                })
    except ET.ParseError as e:
        print(f"[ArXiv] XML parse error: {e}")
    except Exception as e:
        print(f"[ArXiv] Parse error: {e}")
    return papers

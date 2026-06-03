"""PubMed source via NCBI Entrez API"""
import xml.etree.ElementTree as ET
import requests
from utils.config import get_settings

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query: str, max_results: int = 10) -> list[dict]:
    s = get_settings()
    params = {
        "db": "pubmed", "term": query, "retmax": max_results,
        "retmode": "json", "sort": "relevance", "email": s.NCBI_EMAIL,
    }
    if s.NCBI_API_KEY:
        params["api_key"] = s.NCBI_API_KEY
    try:
        r = requests.get(f"{BASE}/esearch.fcgi", params=params, timeout=15)
        r.raise_for_status()
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return []

        fetch_p = {
            "db": "pubmed", "id": ",".join(pmids),
            "retmode": "xml", "rettype": "abstract", "email": s.NCBI_EMAIL,
        }
        if s.NCBI_API_KEY:
            fetch_p["api_key"] = s.NCBI_API_KEY
        fr = requests.get(f"{BASE}/efetch.fcgi", params=fetch_p, timeout=20)
        fr.raise_for_status()
        return _parse_pubmed_xml(fr.content)
    except requests.exceptions.HTTPError as e:
        print(f"[PubMed] HTTP {e.response.status_code}: {e}")
        return []
    except Exception as e:
        print(f"[PubMed] Error: {e}")
        return []


def _parse_pubmed_xml(content: bytes) -> list[dict]:
    papers = []
    try:
        root = ET.fromstring(content)
        for article in root.findall(".//PubmedArticle"):
            pmid = _t(article, ".//PMID")
            title = _t(article, ".//ArticleTitle")
            abstract = _t(article, ".//AbstractText")
            year_el = article.find(".//PubDate/Year")
            medline_year = article.find(".//MedlineDate")
            if year_el is not None and year_el.text:
                year = int(year_el.text)
            elif medline_year is not None and medline_year.text:
                year = int(medline_year.text[:4]) if medline_year.text else 0
            else:
                year = 0
            authors = [
                f"{_t(a, 'LastName')} {_t(a, 'ForeName')}".strip()
                for a in article.findall(".//Author")[:5]
            ]
            keywords = [k.text for k in article.findall(".//Keyword") if k.text]
            if title and abstract and len(abstract) > 50:
                papers.append({
                    "title": title, "authors": [a for a in authors if a],
                    "year": year, "abstract": abstract[:600],
                    "source": "pubmed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "doi": None, "citations": 0,
                    "keywords": keywords[:8], "cluster": None,
                })
    except Exception as e:
        print(f"[PubMed parse] Error: {e}")
    return papers


def _t(el, path: str) -> str:
    found = el.find(path)
    return found.text.strip() if found is not None and found.text else ""

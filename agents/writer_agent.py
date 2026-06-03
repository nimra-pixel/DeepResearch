"""
Writer Agent — token-efficient mode writes FULL review in 2 LLM calls instead of 8+.
Normal mode: ~12,000 tokens | Efficient mode: ~3,000 tokens
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agents.state import DeepResearchState
from utils.llm import invoke_with_fallback
from utils.config import get_settings

EFFICIENT_WRITER_SYSTEM = """You are an academic writer. Write a complete literature review.

Structure your response EXACTLY as:
## Abstract
[200 word abstract]

## Introduction and Background
[3 paragraphs academic prose]

## Theoretical Foundations
[3 paragraphs]

## Methodological Approaches
[3 paragraphs]

## Key Findings and Applications
[3 paragraphs citing specific papers as (Author, Year)]

## Research Gaps and Limitations
[2 paragraphs]

## Future Directions
[2 paragraphs]

## Conclusion
[2 paragraphs]

Rules: academic prose only (no bullets), cite papers as (Author, Year),
add disclaimer at end: "This is AI-generated decision support, not a substitute for expert review."
"""

SECTION_WRITER_SYSTEM = """Write ONE section of an academic literature review.
Return ONLY the section content as academic prose (no JSON, no bullets, no headers).
3-4 paragraphs. Cite papers as (Author, Year)."""

URDU_SYSTEM = """دیے گئے انگریزی متن کا مختصر اردو خلاصہ لکھیں (3 جملے)۔ صرف اردو میں جواب دیں۔"""


def _paper_refs(papers: list, limit: int = 15) -> str:
    return "\n".join(
        f"- {p['title'][:70]} | {', '.join(p['authors'][:2])} | {p['year']} | cited:{p.get('citations',0)}"
        for p in papers[:limit]
    )


def writer_agent(state: DeepResearchState) -> DeepResearchState:
    papers = state.get("filtered_papers", [])
    clusters = state.get("clusters", {})
    themes = state.get("themes", [])
    gaps = state.get("research_gaps", [])
    directions = state.get("future_directions", [])
    topic = state["topic"]
    language = state.get("language", "english")
    s = get_settings()
    efficient = s.EFFICIENT_MODE

    if not papers:
        return {**state, "sections": [], "abstract": "",
                "final_review": "No papers found to review.", "outline": []}

    refs = _paper_refs(papers, 20)
    gaps_str = "\n".join(f"- {g['gap']}" for g in gaps[:3])
    directions_str = "\n".join(f"- {d}" for d in directions[:3])

    if efficient:
        # EFFICIENT MODE: 1 LLM call for entire review (~2500 tokens)
        print("[Writer] Efficient mode — 1 call for full review")
        prompt = (
            f"Topic: {topic}\n"
            f"Domain: {state.get('domain','General')}\n"
            f"Key themes: {', '.join(themes[:4])}\n\n"
            f"Available papers ({len(papers)}):\n{refs}\n\n"
            f"Research gaps identified:\n{gaps_str}\n\n"
            f"Future directions:\n{directions_str}\n\n"
            "Write the complete literature review now."
        )
        try:
            full_review_text = invoke_with_fallback(
                [SystemMessage(content=EFFICIENT_WRITER_SYSTEM),
                 HumanMessage(content=prompt)],
                temperature=0.3, max_tokens=2048,
            )
        except Exception as e:
            print(f"[Writer] Error: {e}")
            full_review_text = f"# Literature Review: {topic}\n\nError generating review: {e}"

        # Parse sections from the single response
        sections = _parse_sections_from_text(full_review_text, language)
        abstract = _extract_abstract(full_review_text)

    else:
        # NORMAL MODE: separate call per section (higher quality, more tokens)
        print("[Writer] Normal mode — section-by-section writing")
        section_names = [
            "Introduction and Background",
            "Theoretical Foundations",
            "Methodological Approaches",
            "Key Findings and Applications",
            "Research Gaps and Limitations",
            "Future Directions",
            "Conclusion",
        ]
        sections = []
        for sec_name in section_names:
            prompt = (
                f"Topic: {topic} | Section: {sec_name}\n"
                f"Themes: {', '.join(themes[:3])}\n"
                f"Papers:\n{refs}"
            )
            try:
                content = invoke_with_fallback(
                    [SystemMessage(content=SECTION_WRITER_SYSTEM),
                     HumanMessage(content=prompt)],
                    temperature=0.3, max_tokens=800,
                )
            except Exception as e:
                content = f"Section could not be generated: {e}"
            sections.append({
                "title": sec_name, "content": content,
                "papers_cited": [], "urdu_summary": None,
            })
            print(f"[Writer] Section done: {sec_name}")

        # Abstract
        try:
            abstract = invoke_with_fallback(
                [SystemMessage(content="Write a 150-word academic abstract. Return only the abstract text."),
                 HumanMessage(content=f"Topic: {topic}\nThemes: {', '.join(themes)}\nGaps: {len(gaps)}")],
                temperature=0.2, max_tokens=300,
            )
        except Exception as e:
            abstract = f"Abstract unavailable: {e}"

        full_review_text = _assemble_review(topic, abstract, sections, gaps, directions)

    # Optional Urdu abstract
    urdu_abstract = None
    if language == "bilingual" and abstract:
        try:
            urdu_abstract = invoke_with_fallback(
                [SystemMessage(content=URDU_SYSTEM),
                 HumanMessage(content=abstract[:500])],
                temperature=0.1, max_tokens=200,
            )
        except Exception:
            pass

    # Final review with metadata footer
    final = full_review_text
    if urdu_abstract:
        final = final.replace("## Abstract\n", f"## Abstract\n\n**اردو خلاصہ:** {urdu_abstract}\n\n")
    final += f"\n\n---\n*Generated by DeepResearch Agent · {len(papers)} papers · Nimra Tariq, Superior University Pakistan*"

    outline = [s["title"] for s in sections] if sections else []
    print(f"[Writer] Done — {len(sections)} sections, {len(final)} chars")

    return {
        **state,
        "outline": outline,
        "sections": sections,
        "abstract": abstract,
        "urdu_abstract": urdu_abstract,
        "final_review": final,
    }


def _parse_sections_from_text(text: str, language: str) -> list[dict]:
    """Parse ## sections from a single LLM response into section dicts."""
    parts = re.split(r'\n##\s+', text)
    sections = []
    for part in parts[1:]:  # skip content before first ##
        lines = part.strip().split('\n', 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        if title and content and title.lower() != "abstract":
            sections.append({
                "title": title,
                "content": content,
                "papers_cited": [],
                "urdu_summary": None,
            })
    return sections


def _extract_abstract(text: str) -> str:
    """Extract abstract section from full review text."""
    match = re.search(r'##\s+Abstract\s*\n(.*?)(?=\n##|\Z)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text[:300]


def _assemble_review(topic, abstract, sections, gaps, directions) -> str:
    parts = [f"# Literature Review: {topic}\n\n## Abstract\n{abstract}\n"]
    for s in sections:
        parts.append(f"## {s['title']}\n{s['content']}\n")
    if gaps:
        parts.append("## Research Gaps Identified\n")
        for g in gaps:
            parts.append(f"**[{g.get('priority','medium').upper()}]** {g['gap']}\n\n> {g.get('evidence','')}\n")
    if directions:
        parts.append("## Future Research Directions\n")
        parts.extend(f"- {d}\n" for d in directions)
    return "\n".join(parts)

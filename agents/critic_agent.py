"""
Critic Agent — lightweight scoring, skipped in efficient mode.
"""
import json
import re
from langchain_core.messages import HumanMessage, SystemMessage
from agents.state import DeepResearchState
from utils.llm import invoke_with_fallback
from utils.config import get_settings

CRITIC_SYSTEM = """Rate this literature review. Return ONLY JSON:
{
  "overall_score": 7.5,
  "strengths": ["strength1"],
  "weaknesses": ["weakness1"],
  "should_revise": false
}
Score 0-10. Set should_revise=true only if score < 6."""


def critic_agent(state: DeepResearchState) -> DeepResearchState:
    s = get_settings()
    review = state.get("final_review", "")
    iteration = state.get("iteration", 0)

    # Skip critic in efficient mode or if already iterated
    if s.EFFICIENT_MODE or iteration >= 1 or not review:
        print("[Critic] Skipped (efficient mode or max iterations)")
        return {**state, "critic_score": 7.5,
                "critic_feedback": "Quality check skipped (efficient mode).",
                "iteration": iteration + 1}

    try:
        raw = invoke_with_fallback(
            [SystemMessage(content=CRITIC_SYSTEM),
             HumanMessage(content=f"Review (first 800 chars):\n{review[:800]}")],
            temperature=0.0, max_tokens=300,
        )
        raw = re.sub(r'```(?:json)?|```', '', raw).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group() if match else raw)
        score = float(result.get("overall_score", 7.0))
        feedback = (
            f"Score: {score}/10 | "
            f"Strengths: {', '.join(result.get('strengths', []))} | "
            f"Weaknesses: {', '.join(result.get('weaknesses', []))}"
        )
        should_rev = result.get("should_revise", False) and iteration < 1
    except Exception as e:
        print(f"[Critic] Error: {e}")
        score, feedback, should_rev = 7.0, "Evaluation inconclusive.", False

    print(f"[Critic] Score: {score} | Revise: {should_rev}")
    return {**state, "critic_score": score, "critic_feedback": feedback,
            "iteration": iteration + 1}


def should_revise(state: DeepResearchState) -> str:
    s = get_settings()
    if s.EFFICIENT_MODE:
        return "finalize"
    score = state.get("critic_score", 7.0)
    iteration = state.get("iteration", 0)
    if score < 6.0 and iteration < 2:
        return "revise"
    return "finalize"

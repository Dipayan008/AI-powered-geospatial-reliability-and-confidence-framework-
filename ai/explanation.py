"""
explanation.py
---------------
Generates a natural-language explanation of *why* a confidence score
came out the way it did.

Uses Gemini if GOOGLE_API_KEY is set in the environment. If it's not
set, or the API call fails (no wifi during the demo, rate limit, etc.),
falls back to a clear template-based explanation built from the same
data — so the demo never breaks on a live API call.
"""

from __future__ import annotations

import os
from typing import List

from .utils import ReliabilityLevel

_GEMINI_MODEL = "gemini-1.5-flash"


def _template_explanation(
    event: str,
    score: int,
    reliability: ReliabilityLevel,
    contributing_sources: List[str],
    conflicting_sources: List[str],
) -> str:
    event_readable = event.replace("_", " ")
    sources_readable = ", ".join(s.replace("_", " ") for s in contributing_sources) or "no confirmed sources"

    text = (
        f"Confidence is {score}% ({reliability.value}) for '{event_readable}' "
        f"because {sources_readable} "
        f"{'independently indicate' if len(contributing_sources) > 1 else 'indicates'} this event."
    )
    if conflicting_sources:
        conflict_readable = ", ".join(s.replace("_", " ") for s in conflicting_sources)
        text += f" However, {conflict_readable} reported conflicting information, which lowered the score."
    return text


def generate_explanation(
    event: str,
    score: int,
    reliability: ReliabilityLevel,
    contributing_sources: List[str],
    conflicting_sources: List[str],
) -> str:
    """
    Returns a one- or two-sentence human-readable explanation.

    Tries Gemini first (if configured), falls back to a deterministic
    template otherwise. The template alone is good enough for a demo;
    Gemini just makes the phrasing more natural.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return _template_explanation(event, score, reliability, contributing_sources, conflicting_sources)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(_GEMINI_MODEL)

        prompt = (
            "You are explaining an AI confidence score to a disaster-response "
            "official. Be factual and concise (max 2 sentences).\n\n"
            f"Event: {event.replace('_', ' ')}\n"
            f"Confidence score: {score}/100 ({reliability.value})\n"
            f"Sources that support this: {', '.join(contributing_sources) or 'none'}\n"
            f"Sources that conflict: {', '.join(conflicting_sources) or 'none'}\n\n"
            "Explain in plain language why the score is what it is."
        )
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        return text or _template_explanation(event, score, reliability, contributing_sources, conflicting_sources)

    except Exception:
        # Any failure (network, quota, bad key) — never let the demo crash.
        return _template_explanation(event, score, reliability, contributing_sources, conflicting_sources)

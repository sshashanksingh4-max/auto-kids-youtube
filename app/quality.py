from __future__ import annotations

BANNED_TERMS = {
    "gore", "blood", "weapon", "violence", "adult", "gambling",
    "drugs", "suicide", "porn",
}

def review_content(story: dict, scenes: list[dict]) -> dict:
    text = (story.get("script_hi") or "").lower()
    prompt_text = " ".join(str(s.get("prompt", "")) for s in scenes).lower()
    combined = text + " " + prompt_text
    hits = sorted(term for term in BANNED_TERMS if term in combined)

    checks = {
        "has_title": bool(story.get("title")),
        "has_story": len(story.get("script_hi", "")) >= 80,
        "has_characters": len(story.get("characters", [])) >= 2,
        "has_lesson": bool(story.get("lesson")),
        "has_scenes": len(scenes) >= 5,
        "unsafe_terms": hits,
    }
    passed = all(value is True for key, value in checks.items() if key != "unsafe_terms") and not hits

    return {
        "status": "passed" if passed else "needs_review",
        "checks": checks,
        "policy": "family_friendly_deterministic_precheck",
    }

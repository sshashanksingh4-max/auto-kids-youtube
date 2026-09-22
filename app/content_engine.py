from __future__ import annotations

import re
from datetime import datetime, timezone


SAFE_THEMES = {
    "adventure", "friendship", "kindness", "sharing", "honesty",
    "curiosity", "teamwork", "nature", "animals", "learning",
}

def normalize_topic(topic: str | None) -> str:
    raw = (topic or "").strip()
    if not raw:
        return "चिंटू और जादुई आम का पेड़"
    return raw[:120]


def make_content_plan(topic: str | None) -> dict:
    title = normalize_topic(topic)
    return {
        "title": title,
        "audience": "kids_4_10",
        "language": "hi-IN",
        "format": {"long": "5-7 minutes", "short": "30-45 seconds"},
        "theme": "friendship_and_curiosity",
        "tone": "fun, warm, educational",
        "originality": "original_story; no source-video reuse",
    }


def make_story(plan: dict) -> dict:
    title = plan["title"]
    hero = "चिंटू"
    friend = "मिन्नी"
    story = (
        f"एक दिन {hero} को {title} के बारे में एक रहस्यमयी सुराग मिला। "
        f"वह अपने दोस्त {friend} के साथ उसे खोजने निकल पड़ा। "
        "रास्ते में उन्हें छोटी-छोटी पहेलियाँ मिलीं और दोनों ने मिलकर हर पहेली हल की। "
        "अंत में उन्हें पता चला कि असली जादू किसी वस्तु में नहीं, बल्कि "
        "दोस्ती, हिम्मत और मिलकर सीखने में है। "
        "दोनों ने अपनी खोज सब दोस्तों के साथ साझा की और एक नई सीख लेकर घर लौटे।"
    )
    return {
        "title": title,
        "characters": [
            {"name": hero, "role": "curious child", "visual": "bright 3D cartoon child"},
            {"name": friend, "role": "clever friend", "visual": "friendly 3D cartoon child"},
        ],
        "lesson": "मिलकर सीखना और दूसरों के साथ खुशी बाँटना हमेशा अच्छा होता है।",
        "script_hi": story,
        "estimated_seconds": 360,
    }


def make_scene_plan(story: dict) -> list[dict]:
    title = story["title"]
    return [
        {"scene": 1, "seconds": 30, "prompt": f"3D cartoon opening for Hindi kids story: {title}, colorful village, cheerful morning, cinematic"},
        {"scene": 2, "seconds": 45, "prompt": "3D cartoon children discover a mysterious clue, expressive faces, playful camera movement"},
        {"scene": 3, "seconds": 60, "prompt": "3D cartoon adventure through a colorful garden and forest, safe playful exploration"},
        {"scene": 4, "seconds": 60, "prompt": "3D cartoon friends solve a simple puzzle together, warm educational moment"},
        {"scene": 5, "seconds": 60, "prompt": "3D cartoon magical reveal, bright friendly environment, joyful expressions"},
        {"scene": 6, "seconds": 45, "prompt": "3D cartoon friends share their discovery with other children, celebration"},
        {"scene": 7, "seconds": 60, "prompt": "3D cartoon ending with family-friendly lesson, sunset, warm happy atmosphere"},
    ]


def make_metadata(story: dict) -> dict:
    title = story["title"]
    clean = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    return {
        "youtube_title": f"{clean} | Hindi Kids Story | मज़ेदार कहानी",
        "description": (
            f"{title} की एक original Hindi kids story। "
            "यह कहानी बच्चों के लिए friendship, curiosity और learning को मज़ेदार तरीके से प्रस्तुत करती है।"
        ),
        "tags": ["Hindi kids story", "Hindi cartoon", "kids story", "बच्चों की कहानी", "Hindi cartoon story"],
        "category": "Kids & Family",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

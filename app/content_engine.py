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
    prompts = [
        f"3D cartoon opening for Hindi kids story: {title}, colorful village, cheerful morning, cinematic",
        "3D cartoon children discover a mysterious clue, expressive faces, playful camera movement",
        "3D cartoon friends travel through a colorful garden, safe playful exploration",
        "3D cartoon friends cross a tiny stream together, teamwork and gentle humor",
        "3D cartoon friends discover a glowing trail, magical but family-friendly atmosphere",
        "3D cartoon friends solve a simple puzzle together, warm educational moment",
        "3D cartoon friends help a small friendly animal, kindness and empathy",
        "3D cartoon friends reach a magical tree, bright colors and joyful expressions",
        "3D cartoon magical reveal, sparkles, cheerful reactions, cinematic camera",
        "3D cartoon children celebrate by sharing the discovery with friends",
        "3D cartoon sunset walk home, friendship and family-friendly warmth",
        "3D cartoon ending card feeling, happy children, clear positive lesson, cinematic",
    ]
    return [
        {"scene": i + 1, "seconds": 30, "prompt": prompt}
        for i, prompt in enumerate(prompts)
    ]


def make_short_scene_plan(story: dict) -> list[dict]:
    title = story["title"]
    return [
        {"scene": 1, "seconds": 10, "prompt": f"Vertical 3D cartoon hook for Hindi kids Short: {title}, exciting first moment, bright colors"},
        {"scene": 2, "seconds": 10, "prompt": "Vertical 3D cartoon mystery reveal, expressive child reactions, fast playful camera"},
        {"scene": 3, "seconds": 10, "prompt": "Vertical 3D cartoon clever solution, joyful expressions, colorful magical moment"},
        {"scene": 4, "seconds": 10, "prompt": "Vertical 3D cartoon ending with a simple positive lesson, cheerful and memorable",
        },
    ]


def make_metadata(story: dict, short: bool = False) -> dict:
    title = story["title"]
    clean = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    suffix = " | Hindi Kids Short" if short else " | Hindi Kids Story"
    return {
        "youtube_title": f"{clean}{suffix}",
        "description": (
            f"{title} की एक original Hindi kids story। "
            "बच्चों के लिए friendship, curiosity और learning को मज़ेदार तरीके से प्रस्तुत किया गया है।"
        ),
        "tags": [
            "Hindi kids story", "Hindi cartoon", "kids story",
            "बच्चों की कहानी", "Hindi cartoon story", "kids short",
        ],
        "category": "Kids & Family",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

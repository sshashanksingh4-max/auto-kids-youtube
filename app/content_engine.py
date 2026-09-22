from __future__ import annotations

import re
from datetime import datetime, timezone

from app.characters import CHARACTERS

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
        "character_universe": list(CHARACTERS),
    }


def make_story(plan: dict) -> dict:
    title = plan["title"]
    hero = CHARACTERS["chintu"]
    friend = CHARACTERS["mini"]
    squirrel = CHARACTERS["golu"]
    robot = CHARACTERS["tinku"]

    story = (
        f"एक दिन {hero['name']} को {title} के बारे में एक रहस्यमयी सुराग मिला। "
        f"वह {friend['name']}, {squirrel['name']} और {robot['name']} के साथ उसे खोजने निकल पड़ा। "
        f"रास्ते में {squirrel['name']} ने एक मज़ेदार इशारा देखा, "
        f"और {robot['name']} ने सुरागों को जोड़कर अगला रास्ता बताया। "
        f"{friend['name']} ने एक छोटी पहेली हल की और {hero['name']} ने सबको साथ लेकर आगे बढ़ाया। "
        "अंत में उन्हें समझ आया कि असली जादू किसी वस्तु में नहीं, बल्कि "
        "दोस्ती, हिम्मत, जिज्ञासा और मिलकर सीखने में है। "
        "चारों ने अपनी खोज दोस्तों के साथ साझा की और एक नई सीख लेकर खुशी-खुशी घर लौटे।"
    )

    return {
        "title": title,
        "characters": [
            {**CHARACTERS["chintu"], "visual": f"colorful 2D cartoon rig; {hero['visual']}"},
            {**CHARACTERS["mini"], "visual": f"colorful 2D cartoon rig; {friend['visual']}"},
            {**CHARACTERS["golu"], "visual": f"colorful 2D cartoon rig; {squirrel['visual']}"},
            {**CHARACTERS["tinku"], "visual": f"colorful 2D cartoon rig; {robot['visual']}"},
        ],
        "lesson": "मिलकर सीखना, दूसरों की मदद करना और खुशी बाँटना हमेशा अच्छा होता है।",
        "script_hi": story,
        "estimated_seconds": 360,
    }


def make_scene_plan(story: dict) -> list[dict]:
    title = story["title"]
    prompts = [
        f"Colorful 2D animated cartoon opening for Hindi kids story: {title}, Chintu and Mini with Golu the squirrel and Tinku the friendly robot, colorful village, cheerful morning, cinematic camera motion",
        "2D cartoon Chintu and friends discover a mysterious clue; walking, expressive faces, glances and playful camera movement",
        "2D animated friends travel through a colorful garden; visible walk cycles, Golu adds gentle humor, safe playful exploration",
        "2D cartoon friends cross a tiny stream together; Tinku points out a safe path, teamwork and gentle humor",
        "2D animated friends discover a glowing trail; curious reactions and magical but family-friendly atmosphere",
        "2D cartoon Mini solves a simple puzzle; she points to the answer while Chintu, Golu and Tinku react",
        "2D animated friends help a small friendly animal; visible hand interaction, kindness and empathy",
        "2D cartoon friends reach a magical mango tree; flowers sway, bright colors and joyful expressions",
        "2D animated magical reveal; sparkles move, characters react, cinematic camera",
        "2D cartoon children celebrate by sharing the discovery with friends; claps, smiles and gestures",
        "2D animated sunset walk home; Chintu, Mini, Golu and Tinku walk together, friendship and family-friendly warmth",
        "2D cartoon ending with a clear positive lesson; happy characters wave, cinematic closing feeling",
    ]
    return [
        {"scene": i + 1, "seconds": 30, "prompt": prompt}
        for i, prompt in enumerate(prompts)
    ]


def make_short_scene_plan(story: dict) -> list[dict]:
    title = story["title"]
    return [
        {"scene": 1, "seconds": 10, "prompt": f"Vertical 2D animated cartoon hook for Hindi kids Short: {title}, Chintu and friends see a surprising clue, visible reaction and camera movement, bright colors"},
        {"scene": 2, "seconds": 10, "prompt": "Vertical 2D cartoon mystery reveal, Mini points out the key detail, expressive child reactions, playful camera movement"},
        {"scene": 3, "seconds": 10, "prompt": "Vertical 2D animated clever solution, Golu reacts humorously, Tinku gestures to help, joyful expressions, colorful magical moment"},
        {"scene": 4, "seconds": 10, "prompt": "Vertical 2D cartoon ending with Chintu and friends sharing a simple positive lesson, cheerful and memorable"},
    ]


def make_metadata(story: dict, short: bool = False) -> dict:
    title = story["title"]
    clean = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    suffix = " | Hindi Kids Short" if short else " | Hindi Kids Story"
    return {
        "youtube_title": f"{clean}{suffix}",
        "description": (
            f"{title} की एक original Hindi kids story। "
            "बच्चों के लिए friendship, curiosity, teamwork और learning को मज़ेदार तरीके से प्रस्तुत किया गया है।"
        ),
        "tags": [
            "Hindi kids story", "Hindi cartoon", "kids story",
            "बच्चों की कहानी", "Hindi cartoon story", "kids short",
        ],
        "category": "Kids & Family",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

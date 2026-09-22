from datetime import datetime, timezone

from app.content_engine import (
    make_content_plan,
    make_metadata,
    make_scene_plan,
    make_story,
    normalize_topic,
)
from app.quality import review_content
from app.services import exa, higgsfield, youtube

PIPELINE_STAGES = [
    "trend_research", "content_plan", "story", "characters_and_world",
    "scene_plan", "video_generation", "hindi_voice", "music_and_sfx",
    "thumbnail", "quality_and_safety", "shorts_and_long_video",
    "youtube_publish", "analytics_optimization",
]


def run_pipeline(topic: str | None = None) -> dict:
    chosen_topic = normalize_topic(topic)
    plan = make_content_plan(chosen_topic)
    story = make_story(plan)
    scenes = make_scene_plan(story)
    metadata = make_metadata(story)
    quality = review_content(story, scenes)

    provider_state = {
        "research": exa.api_key is not None,
        "video_generation": higgsfield.enabled,
        "youtube_upload": youtube.enabled,
    }

    stages = []
    for stage in PIPELINE_STAGES:
        if stage in {"content_plan", "story", "characters_and_world", "scene_plan", "quality_and_safety"}:
            status = "ready" if quality["status"] == "passed" else "needs_review"
        elif stage == "trend_research":
            status = "ready" if provider_state["research"] else "waiting_for_provider"
        elif stage == "video_generation":
            status = "ready" if provider_state["video_generation"] else "waiting_for_provider"
        elif stage in {"hindi_voice", "music_and_sfx", "thumbnail", "shorts_and_long_video"}:
            status = "planned"
        elif stage == "youtube_publish":
            status = "ready" if provider_state["youtube_upload"] else "waiting_for_provider"
        else:
            status = "planned"
        stages.append({"name": stage, "status": status})

    ready_to_execute = (
        quality["status"] == "passed"
        and provider_state["video_generation"]
        and provider_state["youtube_upload"]
    )

    return {
        "status": "ready_for_generation" if ready_to_execute else "pipeline_built",
        "topic": chosen_topic,
        "language": "hi-IN",
        "channel_type": "kids",
        "animation_mode": "fully_animated",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "content_plan": plan,
        "story": story,
        "scene_plan": scenes,
        "metadata": metadata,
        "quality_review": quality,
        "stages": stages,
        "providers": provider_state,
        "next_action": (
            "Generate scenes, assemble the long video and Short, then publish."
            if ready_to_execute
            else "Connect the required provider credentials, then execute generation and publishing."
        ),
    }

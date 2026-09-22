from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.content_engine import (
    make_content_plan,
    make_metadata,
    make_scene_plan,
    make_short_scene_plan,
    make_story,
    normalize_topic,
)
from app.quality import review_content
from app.services import higgsfield


async def _submit_scenes(scenes: list[dict]) -> list[dict]:
    async def submit(scene: dict) -> dict:
        result = await higgsfield.text_to_video(
            prompt=scene["prompt"],
            duration=min(int(scene["seconds"]), 30),
            resolution="720p",
            aspect_ratio="9:16" if "Vertical" in scene["prompt"] else "16:9",
            generate_audio=True,
        )
        return {
            "scene": scene["scene"],
            "seconds_requested": min(int(scene["seconds"]), 30),
            "result": result,
        }

    return await asyncio.gather(*(submit(scene) for scene in scenes))


async def generate_scene_jobs(topic: str | None = None, short: bool = False) -> dict:
    chosen = normalize_topic(topic)
    plan = make_content_plan(chosen)
    story = make_story(plan)
    scenes = make_short_scene_plan(story) if short else make_scene_plan(story)
    quality = review_content(story, scenes)

    if quality["status"] != "passed":
        return {"status": "blocked_by_quality_review", "quality_review": quality}

    if not higgsfield.enabled:
        return {
            "status": "waiting_for_provider_keys",
            "required": ["HIGGSFIELD_API_KEY_ID", "HIGGSFIELD_API_KEY_SECRET"],
            "format": "short" if short else "long",
            "story": story,
            "scene_plan": scenes,
        }

    jobs = await _submit_scenes(scenes)
    return {
        "status": "scene_generation_submitted",
        "format": "short" if short else "long",
        "topic": chosen,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": make_metadata(story, short=short),
        "story": story,
        "quality_review": quality,
        "jobs": jobs,
        "next_step": "Poll scene jobs, assemble the finished cut, add narration/music/captions, run final QC, then upload.",
    }

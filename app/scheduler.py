from __future__ import annotations

import asyncio
import os

from app.content_engine import normalize_topic
from app.executor import generate_scene_jobs
from app.services import exa


DEFAULT_TOPICS = [
    "जादुई पेड़ और दो दोस्तों की सीख",
    "चिंटू और मिन्नी की रहस्यमयी जंगल यात्रा",
    "बोलने वाली चिड़िया और बच्चों की दोस्ती",
    "छोटा रोबोट और ईमानदारी की सीख",
]


async def choose_topics(count: int = 2) -> list[str]:
    if not exa.api_key:
        return DEFAULT_TOPICS[:count]

    result = await exa.search(
        "trending Hindi kids story themes India children animation safe educational 2026",
        num_results=8,
    )
    topics: list[str] = []
    for item in result.get("results", []):
        title = (item.get("title") or item.get("text") or "").strip()
        if title:
            topics.append(normalize_topic(title))
    return (topics + DEFAULT_TOPICS)[:count]


async def main() -> None:
    long_count = int(os.getenv("LONG_VIDEOS_PER_RUN", "1"))
    short_count = int(os.getenv("SHORT_VIDEOS_PER_RUN", "1"))
    topics = await choose_topics(max(long_count, short_count))

    if not any(topics):
        print("No topics available; exiting.")
        return

    jobs = []
    for index in range(long_count):
        topic = topics[index % len(topics)]
        jobs.append(await generate_scene_jobs(topic, short=False))

    for index in range(short_count):
        topic = topics[index % len(topics)]
        jobs.append(await generate_scene_jobs(topic, short=True))

    ready = sum(item.get("status") == "scene_generation_submitted" for item in jobs)
    waiting = sum(item.get("status") == "waiting_for_provider_keys" for item in jobs)
    print({
        "long_videos_requested": long_count,
        "short_videos_requested": short_count,
        "submitted": ready,
        "waiting_for_provider_keys": waiting,
        "topics": topics,
    })


if __name__ == "__main__":
    asyncio.run(main())

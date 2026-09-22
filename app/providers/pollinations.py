from __future__ import annotations

import httpx
from urllib.parse import quote


class PollinationsProvider:
    """Free-first media provider.

    Token-based access is documented; anonymous access may also be available
    for some endpoints. The key is optional and runtime limits are handled
    without automatic paid fallback.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    @property
    def enabled(self) -> bool:
        return True

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def generate_video(
        self,
        prompt: str,
        duration: int = 4,
        model: str = "bytedance/seedance-2.0-mini",
        aspect_ratio: str = "16:9",
    ) -> dict:
        url = f"https://gen.pollinations.ai/video/{quote(prompt, safe='')}"
        params = {"model": model, "duration": max(1, min(int(duration), 10))}
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.get(
                url,
                params=params,
                headers=self._headers(),
                follow_redirects=True,
            )
            response.raise_for_status()
            return {
                "enabled": True,
                "provider": "pollinations",
                "model": model,
                "content_type": response.headers.get("content-type"),
                "bytes": response.content,
                "aspect_ratio": aspect_ratio,
            }

    async def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
    ) -> dict:
        url = f"https://image.pollinations.ai/prompt/{quote(prompt, safe='')}"
        params = {"model": model, "width": width, "height": height}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.get(
                url,
                params=params,
                headers=self._headers(),
                follow_redirects=True,
            )
            response.raise_for_status()
            return {
                "enabled": True,
                "provider": "pollinations",
                "model": model,
                "content_type": response.headers.get("content-type"),
                "bytes": response.content,
            }

import httpx

class HiggsfieldProvider:
    def __init__(self, key_id: str | None, key_secret: str | None):
        self.key_id = key_id
        self.key_secret = key_secret

    @property
    def enabled(self) -> bool:
        return bool(self.key_id and self.key_secret)

    def headers(self) -> dict:
        return {
            "Authorization": f"Key {self.key_id}:{self.key_secret}",
            "Content-Type": "application/json",
        }

    async def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = True,
    ) -> dict:
        if not self.enabled:
            return {"enabled": False, "status": "not_configured"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.higgsfield.ai/bytedance/seedance-2.0/text-to-video",
                headers=self.headers(),
                json={
                    "prompt": prompt,
                    "resolution": resolution,
                    "generate_audio": generate_audio,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                },
            )
            response.raise_for_status()
            return response.json()

    async def request_status(self, request_id: str) -> dict:
        if not self.enabled:
            return {"enabled": False, "status": "not_configured"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://api.higgsfield.ai/requests/{request_id}/status",
                headers=self.headers(),
            )
            response.raise_for_status()
            return response.json()

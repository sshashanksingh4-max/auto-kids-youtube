import httpx

class ExaProvider:
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    async def search(self, query: str, num_results: int = 8) -> dict:
        if not self.api_key:
            return {"enabled": False, "results": []}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": self.api_key, "Content-Type": "application/json"},
                json={"query": query, "numResults": num_results, "contents": {"highlights": {"maxCharacters": 1200}}},
            )
            response.raise_for_status()
            return {"enabled": True, "results": response.json().get("results", [])}

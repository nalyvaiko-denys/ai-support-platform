from app.llm.openai_client import OpenAIClient


class EmbeddingService:
    def __init__(self, client: OpenAIClient) -> None:
        self.client = client

    async def create_embedding(self, text: str) -> list[float]:
        return await self.client.create_embedding(text)
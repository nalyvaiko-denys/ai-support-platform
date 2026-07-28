from app.llm.client import BaseLLMClient


class EmbeddingService:
    def __init__(
        self,
        client: BaseLLMClient,
    ) -> None:
        self.client = client

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        return await self.client.create_embedding(text)

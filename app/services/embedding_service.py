from app.llm.client import BaseLLMClient, EmbeddingProfile


class EmbeddingService:
    def __init__(
        self,
        client: BaseLLMClient,
    ) -> None:
        self.client = client

    @property
    def profile(self) -> EmbeddingProfile:
        return self.client.embedding_profile

    async def create_embedding(
        self,
        text: str,
    ) -> list[float]:
        embedding = await self.client.create_embedding(text)

        if len(embedding) != self.profile.dimension:
            raise ValueError(
                "Embedding dimension does not match the configured profile: "
                f"expected {self.profile.dimension}, got {len(embedding)}"
            )

        return embedding

from app.llm.openai_client import OpenAIClient


class ChatService:
    def __init__(self) -> None:
        self.client = OpenAIClient()

    async def ask(self, message: str) -> str:
        return await self.client.generate(message)
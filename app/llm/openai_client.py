from app.llm.client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    async def generate(self, prompt: str) -> str:
        return f"OpenAI response for: {prompt}"
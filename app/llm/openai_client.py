from app.llm.client import BaseLLMClient
# from openai import AsyncOpenAI
# from app.core.config import settings


class OpenAIClient(BaseLLMClient):
    # def __init__(self):
    #     self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(self, prompt: str) -> str:
        # response = await self.client.responses.create(
        #     model="gpt-4.1-mini",
        #     input=prompt,
        # )
        # return response.output_text

        return f"Mock OpenAI response: {prompt}"
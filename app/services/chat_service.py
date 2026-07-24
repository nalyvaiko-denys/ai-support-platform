from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.openai_client import OpenAIClient
from app.models.conversation import Conversation
from app.prompt.builder import PromptBuilder
from app.repositories.conversation_repository import ConversationRepository


class ChatService:
    def __init__(self, db: AsyncSession) -> None:
        self.client = OpenAIClient()
        self.repository = ConversationRepository(db)

    async def ask(
        self,
        session_id: str,
        message: str,
    ) -> str:
        history = await self.repository.get_last_messages(
            session_id=session_id,
            limit=10,
        )

        prompt = PromptBuilder.build(
            history=history,
            message=message,
        )

        print(prompt)

        response = await self.client.generate(prompt)

        conversation = Conversation(
            session_id=session_id,
            user_message=message,
            ai_response=response,
            model="gpt-4.1",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            response_time_ms=0,
        )

        await self.repository.create(conversation)

        return response
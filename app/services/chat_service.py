from app.llm.openai_client import OpenAIClient
from app.models.conversation import Conversation
from app.llm.prompt_builder import PromptBuilder
from app.repositories.conversation_repository import ConversationRepository


class ChatService:
    def __init__(
        self,
        repository: ConversationRepository,
        client: OpenAIClient,
    ) -> None:
        self.repository = repository
        self.client = client

    async def ask(self, session_id: str, message: str) -> str:
        history = await self.repository.get_last_messages(session_id)

        # ТУТ У МАЙБУТНЬОМУ БУДЕ:
        # retrieved_docs = await self.document_repository.search(message)
        # context = "\n\n".join([doc.content for doc in retrieved_docs])
        context = ""

        messages = PromptBuilder.build(
            history=history,
            message=message,
            context=context,
        )

        result = await self.client.generate(messages)

        conversation = Conversation(
            session_id=session_id,
            user_message=message,
            ai_response=result["text"],
            model=result["model"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["total_tokens"],
            response_time_ms=result["response_time_ms"],
        )

        await self.repository.create(conversation)

        return result["text"]
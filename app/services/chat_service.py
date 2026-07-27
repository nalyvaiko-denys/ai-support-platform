from app.llm.openai_client import OpenAIClient
from app.models.conversation import Conversation
from app.llm.prompt_builder import PromptBuilder
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.document_repository import DocumentRepository


class ChatService:
    def __init__(
            self,
            repository: ConversationRepository,
            document_repository: DocumentRepository,
            client: OpenAIClient,
    ) -> None:
        self.repository = repository
        self.document_repository = document_repository
        self.client = client

    async def ask(self, session_id: str, message: str) -> str:
        # 1. Отримуємо історію
        history = await self.repository.get_last_messages(session_id)

        # 2. Робимо ембединг запиту клієнта
        query_embedding = await self.client.create_embedding(message)

        # 3. Шукаємо релевантну інформацію в базі (беремо 3 найкращі збіги)
        similar_docs = await self.document_repository.search_similar(query_embedding, limit=3)

        # 4. Формуємо контекст з документів
        context = "\n\n".join([f"Джерело: {doc.source}\nІнформація: {doc.content}" for doc in similar_docs])

        # 5. Будуємо промпт
        messages = PromptBuilder.build(
            history=history,
            message=message,
            context=context,
        )

        # 6. Запитуємо LLM
        result = await self.client.generate(messages)

        # 7. Зберігаємо історію
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
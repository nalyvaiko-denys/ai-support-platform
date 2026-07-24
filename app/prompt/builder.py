from app.models.conversation import Conversation


class PromptBuilder:
    MAX_HISTORY = 10

    @classmethod
    def build(
        cls,
        history: list[Conversation],
        message: str,
    ) -> str:
        history = history[-cls.MAX_HISTORY:]

        prompt = (
            "You are a helpful AI support assistant.\n\n"
            "Conversation history:\n"
        )

        for item in history:
            prompt += (
                f"User: {item.user_message}\n"
                f"Assistant: {item.ai_response}\n"
            )

        prompt += f"\nUser: {message}\nAssistant:"

        return prompt
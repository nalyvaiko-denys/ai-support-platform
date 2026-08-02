from app.llm.prompts import build_system_prompt
from app.models.conversation import Conversation


class PromptBuilder:
    MAX_HISTORY = 5

    @classmethod
    def build(
        cls,
        history: list[Conversation],
        message: str,
        context: str = "",
    ) -> list[dict[str, str]]:

        messages = [
            {
                "role": "system",
                "content": build_system_prompt(context),
            }
        ]

        history = history[-cls.MAX_HISTORY :]

        for item in history:
            messages.append(
                {
                    "role": "user",
                    "content": item.user_message,
                }
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": item.ai_response,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )

        return messages

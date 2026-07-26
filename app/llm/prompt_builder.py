from app.models.conversation import Conversation


class PromptBuilder:
    MAX_HISTORY = 5  # 5 останніх пар повідомлень для економії токенів

    @classmethod
    def build(
            cls,
            history: list[Conversation],
            message: str,
            context: str = "",
    ) -> list[dict[str, str]]:
        system_prompt = (
            "Ти — привітний помічник служби підтримки"
            "Відповідай на запитання клієнта виключно на основі наданого контексту. "
            "Якщо інформації для відповіді немає в контексті, чесно скажи про це і запропонуй покликати людину-оператора.\n\n"
            f"Контекст бази знань:\n{context}"
        )

        messages = [{"role": "system", "content": system_prompt}]

        for item in history:
            messages.append({"role": "user", "content": item.user_message})
            messages.append({"role": "assistant", "content": item.ai_response})

        messages.append({"role": "user", "content": message})

        return messages